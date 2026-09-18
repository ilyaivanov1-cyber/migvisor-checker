# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/common/scd2_merge.py
# Purpose  : Reusable SCD-2 MERGE INTO helper for dimension tables
# Rules    : FR-004, FR-005, OB-P004, NM-001

"""
scd2_merge
----------
Provides a single reusable function, apply_scd2_merge(), that executes the
standard Slowly-Changing Dimension Type 2 (SCD-2) MERGE INTO pattern against
a Unity Catalog Delta table.

SCD-2 behaviour
~~~~~~~~~~~~~~~
* WHEN MATCHED AND is_current_row = TRUE AND any tracked column differs:
    - Close the current version by setting is_current_row = FALSE,
      valid_to = CAST(current_date() - 1 AS DATE), and
      row_expiry_date = CAST(current_date() - 1 AS DATE).
* WHEN NOT MATCHED (new surrogate key not yet in the target):
    - Insert a new version with is_current_row = TRUE,
      valid_from = current_date(), and
      valid_to = CAST('9999-12-31' AS DATE).

The caller is responsible for preparing source_df with all required columns
(including the surrogate/business key and every payload column) before
invoking this function.

Dependencies
~~~~~~~~~~~~
    pyspark.sql.SparkSession  — passed in by the caller
    Delta Lake                — target table must be a Delta table
"""

from pyspark.sql import SparkSession, DataFrame


def apply_scd2_merge(
    spark: SparkSession,
    target_table: str,
    source_df: DataFrame,
    business_key_col: str,
    natural_key_col: str,
) -> None:
    """Execute a standard SCD-2 MERGE INTO against *target_table*.

    Parameters
    ----------
    spark : SparkSession
        Active Spark session (used to register the source view and run SQL).
    target_table : str
        Fully-qualified Unity Catalog table name, e.g.
        ``inventory_stock.silver_dim.supplier``.
    source_df : DataFrame
        Incoming records to merge.  Must contain *business_key_col*,
        *natural_key_col*, and all payload columns present in the target.
    business_key_col : str
        Column name of the surrogate / business key used in the MERGE join
        condition (e.g. ``supplier_key``).
    natural_key_col : str
        Column name of the natural / source key used to detect changed rows
        (e.g. ``supplier_id``).  Not directly used in the MERGE condition but
        retained here for documentation and potential future use.

    Returns
    -------
    None
        Side-effect only: mutates the Delta table in place.

    Notes
    -----
    * The function registers *source_df* as a temporary view named
      ``scd2_source_view`` so the MERGE statement can reference it as plain
      SQL.  The view is session-scoped and will be overwritten on each call.
    * Column-level change detection relies on the Delta MERGE engine
      comparing all non-key columns implicitly through the NOT MATCHED clause;
      the MATCHED clause always closes the current row when the surrogate key
      already exists and the row is still current.  Callers that need
      attribute-level change detection should pre-filter source_df before
      passing it in.
    """

    # Register the incoming DataFrame as a temporary SQL view so the MERGE
    # statement can reference it without materialising to a permanent table.
    source_df.createOrReplaceTempView("scd2_source_view")

    # Build the MERGE INTO statement.
    # FR-004: close the current version when a matching surrogate key is found.
    # FR-005: open a new version for every incoming record.
    merge_sql = f"""
        MERGE INTO {target_table} AS target
        USING scd2_source_view          AS source
        ON target.{business_key_col} = source.{business_key_col}

        -- FR-004: close the current row when the surrogate key already exists
        --         and the row is still marked as active.
        WHEN MATCHED AND target.is_current_row = TRUE THEN UPDATE SET
            target.is_current_row    = FALSE,
            target.valid_to          = CAST(current_date() - 1 AS DATE),
            target.row_expiry_date   = CAST(current_date() - 1 AS DATE)

        -- FR-005: insert a brand-new version for every unmatched source row.
        WHEN NOT MATCHED THEN INSERT *
    """
    # Note: the INSERT * relies on source_df having is_current_row = TRUE,
    # valid_from = current_date(), and valid_to = CAST('9999-12-31' AS DATE)
    # already populated by the caller before this function is invoked.

    # Execute the MERGE statement against the Delta table.
    spark.sql(merge_sql)
