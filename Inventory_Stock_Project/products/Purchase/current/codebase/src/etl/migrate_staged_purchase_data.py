# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/etl/migrate_staged_purchase_data.py
# Purpose  : Main ETL notebook — SK resolution, QA assertion chain
#            (QA-P001 through QA-P005), and MERGE INTO from bronze staging
#            to silver_fact.fact_purchase.  Closes the lineage_run record
#            on success or failure.
# Rules    : FR-007, FR-008, NFR-003, NFR-004, NFR-005, NFR-006, NFR-007,
#            NFR-009, DQR-001, DQR-002, DQR-003, DQR-004, DQR-005, DQR-006,
#            DQR-007, DQR-008, DQR-009, CX-P005, QA-P001, QA-P002, QA-P003,
#            QA-P004, QA-P005
# Workflow : nightly_etl_purchase — Task 3 (migrate_staged_purchase_data)
# =============================================================================

# =============================================================================
# SECTION 1: IMPORTS
# =============================================================================
import yaml
import logging
from pyspark.sql import functions as F
from src.common.constants import (
    PURCHASE_STAGING_TABLE,
    FACT_PURCHASE_TABLE,
    SUPPLIER_DIM_TABLE,
    STOCK_ITEM_DIM_TABLE,
    DATE_DIM_TABLE,
    LINEAGE_RUN_TABLE,
    DQ_REJECTIONS_TABLE,
    ETL_CUTOFF_TABLE,
    ETL_CUTOFF_TABLE_NAME,
)
from src.common.sk_resolver import resolve_supplier_key, resolve_stock_item_key
from src.common.fact_merge import merge_fact_purchase

with open("config/environment.yaml") as f:
    cfg = yaml.safe_load(f)

FACT_OPTIMIZE_THRESHOLD = cfg["purchase"]["etl"]["fact_optimize_row_threshold"]

# Business-rule thresholds (QA-P004 / DQR-005, DQR-006, DQR-007)
MIN_ORDERED_QUANTITY    = cfg["purchase"]["business_rules"]["min_ordered_quantity"]
MIN_ORDERED_OUTERS      = cfg["purchase"]["business_rules"]["min_ordered_outers"]
DATE_WINDOW_TOLERANCE   = cfg["purchase"]["business_rules"]["date_window_tolerance_days"]

logger = logging.getLogger(__name__)

# =============================================================================
# SECTION 2: LINEAGE KEY
# Retrieve the lineage_key and current_cutoff published by nb_extract_watermark
# via Databricks taskValues (CX-P005).
# =============================================================================
lineage_key    = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")
current_cutoff = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="current_cutoff")

logger.info(f"migrate_staged_purchase_data started. lineage_key={lineage_key}, current_cutoff={current_cutoff}")

# =============================================================================
# SECTION 3: ZERO-ROWS GUARD
# If the staging table is empty there is nothing to merge.  Update the
# lineage record as a successful (but skipped) run and exit early (NFR-006).
# =============================================================================
staging_count = spark.sql(
    f"SELECT COUNT(*) AS cnt FROM {PURCHASE_STAGING_TABLE}"
).collect()[0]["cnt"]

if staging_count == 0:
    spark.sql(f"""
        UPDATE {LINEAGE_RUN_TABLE}
        SET was_successful        = true,
            data_load_completed   = current_timestamp(),
            table_row_count       = 0
        WHERE lineage_key = {lineage_key}
    """)
    logger.info(f"SKIPPED: zero rows in {PURCHASE_STAGING_TABLE} for lineage_key={lineage_key}")
    dbutils.notebook.exit("SKIPPED: zero rows in staging")

# =============================================================================
# SECTION 4: MAIN ETL LOGIC
# Steps:
#   1. Load staging and dimension DataFrames
#   2. Resolve supplier_key via temporal SCD-2 join (FR-004, CALC-002)
#   3. Resolve stock_item_key via temporal SCD-2 join (FR-005, CALC-003)
#   4. Write resolved staging back to the staging table
#   5. Execute MERGE INTO fact_purchase (FR-007, NFR-003)
#   6. QA-P001 BLOCKING row-count assertion
#   7. QA-P002 non-blocking orphaned-SK warning
#   8. QA-P003 non-blocking RI violation capture
#   9. QA-P004 non-blocking business-rule warnings
#  10. QA-P005 DQ rejection summary
# =============================================================================
try:
    # -------------------------------------------------------------------------
    # Step 1: Load DataFrames
    # -------------------------------------------------------------------------
    staging_df       = spark.table(PURCHASE_STAGING_TABLE)
    supplier_dim_df  = spark.table(SUPPLIER_DIM_TABLE)
    stock_item_dim_df = spark.table(STOCK_ITEM_DIM_TABLE)

    # -------------------------------------------------------------------------
    # Step 2: Resolve supplier_key (FR-004, CALC-002, PE-006, DQR-009)
    # The BROADCAST hint is applied inside resolve_supplier_key.
    # -------------------------------------------------------------------------
    staging_df = resolve_supplier_key(staging_df, F.broadcast(supplier_dim_df))
    logger.info("supplier_key resolution complete")

    # -------------------------------------------------------------------------
    # Step 3: Resolve stock_item_key (FR-005, CALC-003, PE-006, DQR-009)
    # The BROADCAST hint is applied inside resolve_stock_item_key.
    # -------------------------------------------------------------------------
    staging_df = resolve_stock_item_key(staging_df, F.broadcast(stock_item_dim_df))
    logger.info("stock_item_key resolution complete")

    # -------------------------------------------------------------------------
    # Step 4: Write the resolved staging DataFrame back to the staging table
    # so that the MERGE statement (which reads from the table by name) sees
    # the resolved surrogate keys (NFR-003).
    # -------------------------------------------------------------------------
    (
        staging_df
        .write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "false")
        .saveAsTable(PURCHASE_STAGING_TABLE)
    )
    logger.info(f"Resolved staging written back to {PURCHASE_STAGING_TABLE}")

    # -------------------------------------------------------------------------
    # Step 5: Execute MERGE INTO fact_purchase (FR-007, NFR-003, CALC-006)
    # -------------------------------------------------------------------------
    rows_merged = merge_fact_purchase(spark, PURCHASE_STAGING_TABLE, FACT_PURCHASE_TABLE)
    logger.info(f"merge_fact_purchase complete: rows_merged={rows_merged}")

    # -------------------------------------------------------------------------
    # Step 6: QA-P001 — BLOCKING row-count assertion (DQR-001)
    # Every row that was in staging must have been inserted or updated in the
    # fact table.  A discrepancy indicates a silent data-loss scenario and
    # must abort the pipeline immediately.
    # -------------------------------------------------------------------------
    if rows_merged != staging_count:
        raise RuntimeError(
            f"QA-P001 FAILED — Row count mismatch: "
            f"staging={staging_count}, inserted/updated={rows_merged}"
        )
    logger.info(f"QA-P001 PASSED: staging_count={staging_count} == rows_merged={rows_merged}")

    # -------------------------------------------------------------------------
    # Step 7: QA-P002 — Non-blocking orphaned-SK detection (DQR-009)
    # Rows where supplier_key = 0 or stock_item_key = 0 indicate that no
    # matching dimension record was found during resolution.  These rows are
    # loaded with the sentinel key (DQR-009) but the count is logged as a
    # WARNING so that data stewards can investigate the source data.
    # Key = 0 is the sentinel value and is excluded from the "orphaned" count
    # only when it appeared in source because the dimension itself starts at 0;
    # here we flag all rows where the key was coalesced to 0 from NULL.
    # -------------------------------------------------------------------------
    resolved_staging_df = spark.table(PURCHASE_STAGING_TABLE)

    orphaned_supplier = (
        resolved_staging_df
        .join(
            spark.table(SUPPLIER_DIM_TABLE),
            resolved_staging_df["supplier_key"] == spark.table(SUPPLIER_DIM_TABLE)["supplier_key"],
            how="left_anti",
        )
        .filter(F.col("supplier_key") != F.lit(0))
        .count()
    )

    orphaned_stock_item = (
        resolved_staging_df
        .join(
            spark.table(STOCK_ITEM_DIM_TABLE),
            resolved_staging_df["stock_item_key"] == spark.table(STOCK_ITEM_DIM_TABLE)["stock_item_key"],
            how="left_anti",
        )
        .filter(F.col("stock_item_key") != F.lit(0))
        .count()
    )

    if orphaned_supplier > 0:
        logger.warning(
            f"QA-P002: {orphaned_supplier} staging row(s) have supplier_key not found in "
            f"{SUPPLIER_DIM_TABLE} (excluding sentinel key=0)"
        )
    else:
        logger.info("QA-P002 PASSED: no orphaned supplier_key values")

    if orphaned_stock_item > 0:
        logger.warning(
            f"QA-P002: {orphaned_stock_item} staging row(s) have stock_item_key not found in "
            f"{STOCK_ITEM_DIM_TABLE} (excluding sentinel key=0)"
        )
    else:
        logger.info("QA-P002 PASSED: no orphaned stock_item_key values")

    # -------------------------------------------------------------------------
    # Step 8: QA-P003 — Non-blocking RI check (DQR-002, DQR-003, DQR-004)
    # Verify that every FK in the loaded fact rows resolves to a dimension row.
    # Violations are written to the DQ rejections table for triage.
    # -------------------------------------------------------------------------
    fact_df      = spark.table(FACT_PURCHASE_TABLE).filter(F.col("lineage_key") == lineage_key)
    supplier_dim = spark.table(SUPPLIER_DIM_TABLE).select("supplier_key").distinct()
    stock_item_dim = spark.table(STOCK_ITEM_DIM_TABLE).select("stock_item_key").distinct()
    date_dim     = spark.table(DATE_DIM_TABLE).select("date_key").distinct()

    # date_key RI violations
    date_violations = (
        fact_df
        .join(date_dim, fact_df["date_key"] == date_dim["date_key"], how="left_anti")
        .select(
            F.lit(lineage_key).cast("bigint").alias("lineage_key"),
            F.lit("QA-P003").alias("rule_id"),
            F.lit(FACT_PURCHASE_TABLE).alias("source_table"),
            F.lit("purchase_key").alias("pk_column"),
            F.col("purchase_key").cast("string").alias("pk_value"),
            F.lit("date_key").alias("violation_column"),
            F.col("date_key").cast("string").alias("violation_value"),
            F.lit("date_key not found in silver_dim.date").alias("rejection_reason"),
        )
    )

    # supplier_key RI violations
    supplier_violations = (
        fact_df
        .join(supplier_dim, fact_df["supplier_key"] == supplier_dim["supplier_key"], how="left_anti")
        .select(
            F.lit(lineage_key).cast("bigint").alias("lineage_key"),
            F.lit("QA-P003").alias("rule_id"),
            F.lit(FACT_PURCHASE_TABLE).alias("source_table"),
            F.lit("purchase_key").alias("pk_column"),
            F.col("purchase_key").cast("string").alias("pk_value"),
            F.lit("supplier_key").alias("violation_column"),
            F.col("supplier_key").cast("string").alias("violation_value"),
            F.lit("supplier_key not found in silver_dim.supplier").alias("rejection_reason"),
        )
    )

    # stock_item_key RI violations
    stock_item_violations = (
        fact_df
        .join(stock_item_dim, fact_df["stock_item_key"] == stock_item_dim["stock_item_key"], how="left_anti")
        .select(
            F.lit(lineage_key).cast("bigint").alias("lineage_key"),
            F.lit("QA-P003").alias("rule_id"),
            F.lit(FACT_PURCHASE_TABLE).alias("source_table"),
            F.lit("purchase_key").alias("pk_column"),
            F.col("purchase_key").cast("string").alias("pk_value"),
            F.lit("stock_item_key").alias("violation_column"),
            F.col("stock_item_key").cast("string").alias("violation_value"),
            F.lit("stock_item_key not found in silver_dim.stock_item").alias("rejection_reason"),
        )
    )

    # Union all RI violations and write to DQ rejections table
    all_ri_violations = date_violations.union(supplier_violations).union(stock_item_violations)
    ri_violation_count = all_ri_violations.count()

    if ri_violation_count > 0:
        (
            all_ri_violations
            .write
            .format("delta")
            .mode("append")
            .saveAsTable(DQ_REJECTIONS_TABLE)
        )
        logger.warning(
            f"QA-P003: {ri_violation_count} RI violation(s) written to {DQ_REJECTIONS_TABLE} "
            f"(lineage_key={lineage_key})"
        )
    else:
        logger.info("QA-P003 PASSED: no RI violations detected")

    # -------------------------------------------------------------------------
    # Step 9: QA-P004 — Non-blocking business-rule assertions
    # (DQR-005: negative quantities, DQR-006: out-of-window date_key,
    #  DQR-007: null/empty package)
    # -------------------------------------------------------------------------

    # Derive batch window boundaries from config (DQR-006)
    from datetime import datetime, timezone, timedelta
    run_dt       = datetime.now(timezone.utc).date()
    lookback_days = cfg["purchase"]["etl"]["batch_lookback_days"]
    tolerance     = DATE_WINDOW_TOLERANCE
    batch_date_min = run_dt - timedelta(days=lookback_days + tolerance)
    batch_date_max = run_dt + timedelta(days=tolerance)

    # DQR-005: negative ordered_outers or ordered_quantity
    negative_qty_count = (
        resolved_staging_df
        .filter(
            (F.col("ordered_outers") < MIN_ORDERED_OUTERS)
            | (F.col("ordered_quantity") < MIN_ORDERED_QUANTITY)
        )
        .count()
    )
    if negative_qty_count > 0:
        logger.warning(
            f"QA-P004 (DQR-005): {negative_qty_count} row(s) have ordered_outers < "
            f"{MIN_ORDERED_OUTERS} or ordered_quantity < {MIN_ORDERED_QUANTITY}"
        )
    else:
        logger.info("QA-P004 (DQR-005) PASSED: all quantity values within expected range")

    # DQR-006: date_key outside batch window
    out_of_window_count = (
        resolved_staging_df
        .filter(
            (F.col("date_key") < F.lit(str(batch_date_min)).cast("date"))
            | (F.col("date_key") > F.lit(str(batch_date_max)).cast("date"))
        )
        .count()
    )
    if out_of_window_count > 0:
        logger.warning(
            f"QA-P004 (DQR-006): {out_of_window_count} row(s) have date_key outside "
            f"batch window [{batch_date_min}, {batch_date_max}]"
        )
    else:
        logger.info(f"QA-P004 (DQR-006) PASSED: all date_key values within batch window [{batch_date_min}, {batch_date_max}]")

    # DQR-007: null or empty package
    if cfg["purchase"]["business_rules"]["package_required"]:
        null_package_count = (
            resolved_staging_df
            .filter(
                F.col("package").isNull()
                | (F.trim(F.col("package")) == F.lit(""))
            )
            .count()
        )
        if null_package_count > 0:
            logger.warning(
                f"QA-P004 (DQR-007): {null_package_count} row(s) have null or empty 'package' value"
            )
        else:
            logger.info("QA-P004 (DQR-007) PASSED: all package values are non-null and non-empty")

    # -------------------------------------------------------------------------
    # Step 10: QA-P005 — DQ rejection summary count
    # Log the total number of DQ rejections written for this lineage_key
    # across all QA rules (QA-P005).
    # -------------------------------------------------------------------------
    dq_rejection_total = spark.sql(f"""
        SELECT COUNT(*) AS cnt
        FROM {DQ_REJECTIONS_TABLE}
        WHERE lineage_key = {lineage_key}
    """).collect()[0]["cnt"]

    logger.info(
        f"QA-P005 DQ rejection summary: {dq_rejection_total} total rejection(s) "
        f"recorded in {DQ_REJECTIONS_TABLE} for lineage_key={lineage_key}"
    )

except Exception as e:
    # -------------------------------------------------------------------------
    # Error handler: mark the lineage run as failed and re-raise so Databricks
    # workflow marks the task as failed and optionally triggers an alert.
    # (NFR-004, NFR-005)
    # -------------------------------------------------------------------------
    spark.sql(f"""
        UPDATE {LINEAGE_RUN_TABLE}
        SET was_successful      = false,
            data_load_completed = current_timestamp(),
            table_row_count     = 0
        WHERE lineage_key = {lineage_key}
    """)
    logger.error(f"migrate_staged_purchase_data FAILED for lineage_key={lineage_key}: {e}")
    raise

# =============================================================================
# SECTION 5: CONDITIONAL OPTIMIZE
# Run OPTIMIZE only when the merged row count exceeds the configured threshold
# to avoid unnecessary compaction overhead on small incremental loads (FR-008).
# =============================================================================
if rows_merged > FACT_OPTIMIZE_THRESHOLD:
    spark.sql(f"OPTIMIZE {FACT_PURCHASE_TABLE}")
    logger.info(
        f"OPTIMIZE executed on {FACT_PURCHASE_TABLE} after {rows_merged} rows merged"
    )

# =============================================================================
# SECTION 6: CLOSE LINEAGE
# Mark the lineage_run record as successful and advance the ETL cutoff
# watermark so the next run starts from where this one ended (FR-003, LN-001).
# =============================================================================
spark.sql(f"""
    UPDATE {LINEAGE_RUN_TABLE}
    SET was_successful      = true,
        data_load_completed = current_timestamp(),
        table_row_count     = {rows_merged}
    WHERE lineage_key = {lineage_key}
""")

spark.sql(f"""
    MERGE INTO {ETL_CUTOFF_TABLE} AS t
    USING (
        SELECT
            '{ETL_CUTOFF_TABLE_NAME}'              AS table_name,
            CAST('{current_cutoff}' AS TIMESTAMP)  AS cutoff_time,
            current_timestamp()                    AS last_updated_utc
    ) AS s
    ON t.table_name = s.table_name
    WHEN MATCHED THEN UPDATE SET
        t.cutoff_time      = s.cutoff_time,
        t.last_updated_utc = s.last_updated_utc
    WHEN NOT MATCHED THEN INSERT *
""")

logger.info(
    f"migrate_staged_purchase_data completed successfully. "
    f"lineage_key={lineage_key}, rows_merged={rows_merged}, cutoff advanced to {current_cutoff}"
)
