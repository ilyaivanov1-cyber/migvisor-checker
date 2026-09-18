# =============================================================================
# File        : src/common/fact_merge.py
# Product     : Purchase ETL
# Description : Delta Lake MERGE (upsert) for the fact_purchase table.
#               Implements idempotent, incremental loads via a MERGE INTO
#               statement, then returns the number of rows affected for
#               lineage and audit purposes.
#               Rules applied: FR-007, NFR-003, CALC-006, NM-001.
# =============================================================================
"""
fact_merge
----------
Provides a single public function:

  * merge_fact_purchase(spark, staging_table, fact_table)
        Execute a MERGE INTO upsert from a staging view/table into the
        Delta Lake fact_purchase table, then return the row count that
        was affected (inserted + updated) as reported by Delta's
        DESCRIBE HISTORY command.

Design decisions
~~~~~~~~~~~~~~~~
FR-007   — The fact table must support incremental / idempotent loads.
           MERGE INTO (Delta Lake) is the prescribed mechanism: it
           updates existing rows matched on the business key
           (wwi_purchase_order_id) and inserts new rows for unmatched
           sources.

NFR-003  — The implementation uses spark.sql() so the MERGE statement is
           executed as a single atomic Delta transaction, guaranteeing
           ACID semantics and avoiding partial-load states.

CALC-006 — rows_merged is derived from Delta's operation metrics after
           the MERGE completes.  DESCRIBE HISTORY LIMIT 1 returns the
           most-recent operation; the numTargetRowsInserted and
           numTargetRowsUpdated metrics are summed to produce the total
           rows_merged count returned to the caller.

NM-001   — Column names in the MERGE statement use snake_case and match
           the canonical schema defined in the to-be design document.
"""

from pyspark.sql import SparkSession


def merge_fact_purchase(
    spark: SparkSession,
    staging_table: str,
    fact_table: str,
) -> int:
    """Upsert rows from a staging table into the fact_purchase Delta table.

    Executes a MERGE INTO statement that:
      - Updates existing fact rows when the business key
        (wwi_purchase_order_id) matches a staging row.
      - Inserts new fact rows for staging rows with no existing match.

    After the MERGE completes, the function queries Delta's DESCRIBE
    HISTORY to extract the number of rows inserted and updated, sums
    them, and returns the total as ``rows_merged`` (CALC-006).

    Args:
        spark          : Active SparkSession with Delta Lake extensions
                         enabled.
        staging_table  : Fully-qualified name (or temporary view name) of
                         the staging table/view that provides the source
                         rows for the MERGE.  Must expose all columns
                         referenced in the MERGE statement.
        fact_table     : Fully-qualified Delta table name for the target
                         fact_purchase table (e.g.
                         ``"gold.fact_purchase"``).

    Returns:
        rows_merged (int): Total number of rows inserted or updated in
        the target table during this MERGE operation.  Returns 0 if the
        metrics cannot be read from Delta history.

    Raises:
        AnalysisException: If either ``staging_table`` or ``fact_table``
                           does not exist or is inaccessible.
        Exception        : Re-raised for any other Spark execution error.
    """

    # ------------------------------------------------------------------
    # Step 1: Build and execute the MERGE INTO statement (FR-007, NFR-003).
    #
    # MATCHED clause — update all mutable fact columns for rows where the
    # natural business key (wwi_purchase_order_id) already exists in the
    # fact table.  The surrogate key columns (date_key, supplier_key,
    # stock_item_key) are refreshed to reflect the latest resolved values,
    # allowing late-arriving dimension records to back-fill correctly.
    #
    # NOT MATCHED clause — insert a full row for net-new purchase orders
    # that have not yet been loaded into the fact table.
    #
    # lineage_key is included in both clauses to link every fact row to
    # the ETL run that created or last modified it.
    # ------------------------------------------------------------------
    merge_sql = f"""
        MERGE INTO {fact_table} AS target
        USING {staging_table} AS source
        ON target.wwi_purchase_order_id = source.wwi_purchase_order_id
        WHEN MATCHED THEN UPDATE SET
            target.date_key              = source.date_key,
            target.supplier_key          = source.supplier_key,
            target.stock_item_key        = source.stock_item_key,
            target.ordered_outers        = source.ordered_outers,
            target.ordered_quantity      = source.ordered_quantity,
            target.received_outers       = source.received_outers,
            target.package               = source.package,
            target.is_order_finalized    = source.is_order_finalized,
            target.lineage_key           = source.lineage_key
        WHEN NOT MATCHED THEN INSERT (
            date_key,
            supplier_key,
            stock_item_key,
            wwi_purchase_order_id,
            ordered_outers,
            ordered_quantity,
            received_outers,
            package,
            is_order_finalized,
            lineage_key
        ) VALUES (
            source.date_key,
            source.supplier_key,
            source.stock_item_key,
            source.wwi_purchase_order_id,
            source.ordered_outers,
            source.ordered_quantity,
            source.received_outers,
            source.package,
            source.is_order_finalized,
            source.lineage_key
        )
    """

    spark.sql(merge_sql)

    # ------------------------------------------------------------------
    # Step 2: Extract rows_merged from Delta operation metrics (CALC-006).
    #
    # DESCRIBE HISTORY <table> LIMIT 1 returns a single row representing
    # the most-recently committed Delta transaction.  The ``operationMetrics``
    # column is a MAP<STRING, STRING> that contains (among others):
    #
    #   numTargetRowsInserted  — rows written by the NOT MATCHED branch
    #   numTargetRowsUpdated   — rows written by the MATCHED branch
    #
    # Both values are cast to INTEGER before summing.  If either key is
    # absent (e.g. zero rows were affected by that branch) the MERGE still
    # succeeds and we default the missing metric to 0.
    # ------------------------------------------------------------------
    history_df = spark.sql(
        f"DESCRIBE HISTORY {fact_table} LIMIT 1"
    )

    metrics_row = history_df.select("operationMetrics").first()

    rows_merged: int = 0

    if metrics_row and metrics_row["operationMetrics"] is not None:
        metrics: dict = metrics_row["operationMetrics"]

        # numTargetRowsInserted and numTargetRowsUpdated are string values
        # in the metrics map — convert to int before arithmetic.
        rows_inserted = int(metrics.get("numTargetRowsInserted", 0))
        rows_updated  = int(metrics.get("numTargetRowsUpdated",  0))

        rows_merged = rows_inserted + rows_updated

    return rows_merged
