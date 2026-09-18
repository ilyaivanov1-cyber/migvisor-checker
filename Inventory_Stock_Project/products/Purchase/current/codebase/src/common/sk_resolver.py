# =============================================================================
# File        : src/common/sk_resolver.py
# Product     : Purchase ETL
# Description : Surrogate key resolution utilities for supplier and stock item
#               dimensions. Applies SCD2 temporal-range joins against dimension
#               tables to resolve natural keys into surrogate keys, per rules
#               FR-004, FR-005, CALC-002, CALC-003, TY-P001, PE-006,
#               DQR-009, NM-001.
# =============================================================================
"""
sk_resolver
-----------
Provides two functions that resolve surrogate keys for the Purchase fact load:

  * resolve_supplier_key    — maps wwi_supplier_id  → supplier_key   (FR-004,
                              CALC-002)
  * resolve_stock_item_key  — maps wwi_stock_item_id → stock_item_key (FR-005,
                              CALC-003)

Both functions implement a temporal-range join so that the dimension row chosen
is the one whose validity window contains the staging record's event timestamp
(last_modified_when).  valid_from / valid_to columns are stored as DATE in the
dimension table; they are CAST to TIMESTAMP before the inequality comparison to
ensure correct semantics and avoid implicit type-coercion issues (TY-P001).

A ROW_NUMBER() de-duplication step picks the single most-recent dimension
version when multiple rows still match after the range filter — a defensive
guard against micro-overlaps that may exist in the source SCD2 data.

Unresolved rows (no matching dimension record) receive a default surrogate key
of 0 via COALESCE rather than NULL, satisfying DQR-009 (no NULL FK values in
the fact table).

A BROADCAST hint is applied to the dimension DataFrame at join time (PE-006)
because dimension tables are small relative to the staging volume and
broadcasting eliminates the shuffle on the larger side.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def resolve_supplier_key(
    staging_df: DataFrame,
    supplier_dim_df: DataFrame,
) -> DataFrame:
    """Resolve supplier surrogate keys against the supplier SCD2 dimension.

    Performs a LEFT temporal-range join between the staging DataFrame and the
    supplier dimension DataFrame, then de-duplicates using ROW_NUMBER() to
    retain only the most-recent valid dimension version for each staging row.
    Unresolved rows receive supplier_key = 0 (DQR-009).

    Rules applied:
        FR-004   — supplier FK must be resolved before fact load
        CALC-002 — temporal-range join: last_modified_when inside [valid_from,
                   valid_to)
        TY-P001  — valid_from / valid_to are DATE; cast to TIMESTAMP for
                   timestamp comparisons
        PE-006   — BROADCAST hint on the smaller dimension side
        DQR-009  — no NULL foreign keys; COALESCE to 0

    Args:
        staging_df      : Staging DataFrame that must contain columns
                          ``purchase_staging_key``, ``wwi_supplier_id``, and
                          ``last_modified_when`` (TimestampType).
        supplier_dim_df : Supplier dimension DataFrame that must contain
                          columns ``wwi_supplier_id``, ``supplier_key``,
                          ``valid_from`` (DateType), and ``valid_to``
                          (DateType).

    Returns:
        A DataFrame identical to ``staging_df`` with an additional
        ``supplier_key`` column (LongType / IntegerType, never NULL).
    """

    # ------------------------------------------------------------------
    # Step 1: Apply BROADCAST hint to the dimension side so that the
    # smaller dimension table is replicated to every executor, avoiding
    # an expensive shuffle on the (potentially large) staging side.
    # PE-006
    # ------------------------------------------------------------------
    dim_broadcast = F.broadcast(supplier_dim_df)

    # ------------------------------------------------------------------
    # Step 2: Build the temporal-range join condition.
    #
    # The dimension's valid_from and valid_to columns are stored as DATE
    # (TY-P001).  We must CAST them to TIMESTAMP before comparing against
    # last_modified_when (which is already TIMESTAMP) so that PySpark does
    # not silently coerce or truncate values.
    #
    # Semantics (CALC-002):
    #   last_modified_when >  CAST(valid_from AS TIMESTAMP)  — strictly after
    #                                                          the version start
    #   last_modified_when <= CAST(valid_to   AS TIMESTAMP)  — on or before the
    #                                                          version end
    #
    # This is equivalent to the half-open interval (valid_from, valid_to].
    # ------------------------------------------------------------------
    join_condition = (
        (staging_df["wwi_supplier_id"] == dim_broadcast["wwi_supplier_id"])
        & (
            staging_df["last_modified_when"]
            > dim_broadcast["valid_from"].cast("timestamp")
        )
        & (
            staging_df["last_modified_when"]
            <= dim_broadcast["valid_to"].cast("timestamp")
        )
    )

    # ------------------------------------------------------------------
    # Step 3: Perform the LEFT JOIN so that staging rows with no matching
    # dimension record are preserved (they will receive supplier_key = 0
    # after COALESCE in a later step).
    # ------------------------------------------------------------------
    joined_df = staging_df.join(dim_broadcast, join_condition, how="left")

    # ------------------------------------------------------------------
    # Step 4: De-duplicate with ROW_NUMBER().
    #
    # If the SCD2 data contains micro-overlapping validity windows, more
    # than one dimension row might satisfy the range condition for a given
    # staging record.  We partition by purchase_staging_key and order by
    # valid_from DESC so that the most-recently-started version wins.
    # Only rows where rn = 1 are kept.
    # ------------------------------------------------------------------
    window_spec = Window.partitionBy("purchase_staging_key").orderBy(
        dim_broadcast["valid_from"].desc()
    )

    deduped_df = (
        joined_df
        .withColumn("_rn", F.row_number().over(window_spec))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )

    # ------------------------------------------------------------------
    # Step 5: COALESCE to 0 for any unresolved (NULL) supplier_key values
    # that result from the LEFT JOIN producing no match (DQR-009).
    # The dim column is renamed to avoid ambiguity with any existing
    # supplier_key column on staging_df.
    # ------------------------------------------------------------------
    result_df = deduped_df.withColumn(
        "supplier_key",
        F.coalesce(dim_broadcast["supplier_key"], F.lit(0)),
    )

    # Drop the dimension's wwi_supplier_id column that was pulled in by
    # the join (NM-001 — keep staging schema clean; only add supplier_key).
    dim_cols_to_drop = [
        c for c in supplier_dim_df.columns
        if c != "supplier_key"
    ]
    result_df = result_df.drop(*dim_cols_to_drop)

    return result_df


def resolve_stock_item_key(
    staging_df: DataFrame,
    stock_item_dim_df: DataFrame,
) -> DataFrame:
    """Resolve stock-item surrogate keys against the stock-item SCD2 dimension.

    Mirrors the logic of :func:`resolve_supplier_key` but operates on
    ``wwi_stock_item_id`` and resolves ``stock_item_key``.

    Rules applied:
        FR-005   — stock-item FK must be resolved before fact load
        CALC-003 — temporal-range join: last_modified_when inside
                   [valid_from, valid_to)
        TY-P001  — valid_from / valid_to are DATE; cast to TIMESTAMP
        PE-006   — BROADCAST hint on the smaller dimension side
        DQR-009  — no NULL foreign keys; COALESCE to 0

    Args:
        staging_df        : Staging DataFrame that must contain columns
                            ``purchase_staging_key``, ``wwi_stock_item_id``,
                            and ``last_modified_when`` (TimestampType).
        stock_item_dim_df : Stock-item dimension DataFrame that must contain
                            columns ``wwi_stock_item_id``, ``stock_item_key``,
                            ``valid_from`` (DateType), and ``valid_to``
                            (DateType).

    Returns:
        A DataFrame identical to ``staging_df`` with an additional
        ``stock_item_key`` column (LongType / IntegerType, never NULL).
    """

    # ------------------------------------------------------------------
    # Step 1: Broadcast the dimension to avoid shuffling the staging side.
    # PE-006
    # ------------------------------------------------------------------
    dim_broadcast = F.broadcast(stock_item_dim_df)

    # ------------------------------------------------------------------
    # Step 2: Temporal-range join condition (CALC-003, TY-P001).
    #
    # Same half-open interval semantics as resolve_supplier_key:
    #   last_modified_when >  CAST(valid_from AS TIMESTAMP)
    #   last_modified_when <= CAST(valid_to   AS TIMESTAMP)
    # ------------------------------------------------------------------
    join_condition = (
        (staging_df["wwi_stock_item_id"] == dim_broadcast["wwi_stock_item_id"])
        & (
            staging_df["last_modified_when"]
            > dim_broadcast["valid_from"].cast("timestamp")
        )
        & (
            staging_df["last_modified_when"]
            <= dim_broadcast["valid_to"].cast("timestamp")
        )
    )

    # ------------------------------------------------------------------
    # Step 3: LEFT JOIN — preserve all staging rows regardless of whether
    # a dimension match exists.
    # ------------------------------------------------------------------
    joined_df = staging_df.join(dim_broadcast, join_condition, how="left")

    # ------------------------------------------------------------------
    # Step 4: ROW_NUMBER() de-duplication.
    #
    # Partition by purchase_staging_key; order by valid_from DESC so the
    # most-recent dimension version is selected when overlaps exist.
    # ------------------------------------------------------------------
    window_spec = Window.partitionBy("purchase_staging_key").orderBy(
        dim_broadcast["valid_from"].desc()
    )

    deduped_df = (
        joined_df
        .withColumn("_rn", F.row_number().over(window_spec))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )

    # ------------------------------------------------------------------
    # Step 5: COALESCE unresolved rows to stock_item_key = 0 (DQR-009).
    # ------------------------------------------------------------------
    result_df = deduped_df.withColumn(
        "stock_item_key",
        F.coalesce(dim_broadcast["stock_item_key"], F.lit(0)),
    )

    # Drop dimension columns that were pulled in by the join, keeping only
    # the resolved stock_item_key (NM-001).
    dim_cols_to_drop = [
        c for c in stock_item_dim_df.columns
        if c != "stock_item_key"
    ]
    result_df = result_df.drop(*dim_cols_to_drop)

    return result_df
