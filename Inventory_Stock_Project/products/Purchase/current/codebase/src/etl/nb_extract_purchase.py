# ============================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/etl/nb_extract_purchase.py
# Purpose  : Incremental purchase extract to bronze staging — Task 2 of nightly_etl_purchase workflow
# Rules    : FR-001, FR-006, CALC-001, CALC-005, NFR-009, CX-P001, CX-P005
# ============================================================

# =============================================================================
# SECTION 1: IMPORTS
# =============================================================================
import yaml
from pyspark.sql import functions as F
from src.common.constants import (
    PURCHASE_STAGING_TABLE, LINEAGE_RUN_TABLE
)

with open("config/environment.yaml") as f:
    cfg = yaml.safe_load(f)

# JDBC source connection — placeholder pending PD-001 platform decision
JDBC_URL = "jdbc:sqlserver://{{JDBC_HOST}}:1433;databaseName=wideworldimportersdw"
JDBC_DRIVER  = cfg["purchase"]["etl"]["jdbc_driver"]
JDBC_USER    = cfg["purchase"]["etl"]["jdbc_user"]
JDBC_PASSWORD = cfg["purchase"]["etl"]["jdbc_password"]
SOURCE_TABLE  = cfg["purchase"]["etl"]["source_table"]

# =============================================================================
# SECTION 2: LINEAGE KEY — received from nb_extract_watermark via taskValues
# =============================================================================
lineage_key    = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")
last_cutoff    = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="last_cutoff")
current_cutoff = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="current_cutoff")

# =============================================================================
# SECTION 3: ZERO-ROWS GUARD
# =============================================================================
# Count source rows within the watermark window before attempting a full extract
count_df = spark.read \
    .format("jdbc") \
    .option("url", JDBC_URL) \
    .option("driver", JDBC_DRIVER) \
    .option("user", JDBC_USER) \
    .option("password", JDBC_PASSWORD) \
    .option(
        "dbtable",
        f"(SELECT COUNT(*) AS cnt FROM {SOURCE_TABLE} "
        f"WHERE last_modified_when > '{last_cutoff}' "
        f"AND last_modified_when <= '{current_cutoff}') AS count_check"
    ) \
    .load()

source_row_count = count_df.collect()[0]["cnt"]

if source_row_count == 0:
    print("SKIPPED: zero rows in watermark window. No staging write required.")
    dbutils.notebook.exit("SKIPPED: zero rows")

# =============================================================================
# SECTION 4: MAIN ETL LOGIC — JDBC incremental extract → bronze staging
# =============================================================================
try:
    # --- Extract incremental rows from source system via JDBC ---
    raw_df = spark.read \
        .format("jdbc") \
        .option("url", JDBC_URL) \
        .option("driver", JDBC_DRIVER) \
        .option("user", JDBC_USER) \
        .option("password", JDBC_PASSWORD) \
        .option(
            "dbtable",
            f"(SELECT * FROM {SOURCE_TABLE} "
            f"WHERE last_modified_when > '{last_cutoff}' "
            f"AND last_modified_when <= '{current_cutoff}') AS incremental_extract"
        ) \
        .load()

    # --- Derive computed columns (CALC-001, CALC-005) ---
    staged_df = raw_df \
        .withColumn("date_key", F.col("order_date").cast("date")) \
        .withColumn("lineage_key", F.lit(int(lineage_key))) \
        .withColumn("_extracted_at_utc", F.current_timestamp())

    # --- Write to bronze staging in OVERWRITE mode (CX-P001) ---
    staged_df.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(PURCHASE_STAGING_TABLE)

    staged_row_count = staged_df.count()

except Exception as e:
    # Log the error; lineage will be closed (failed) by the migrate task
    print(f"ERROR in nb_extract_purchase: {e}")
    raise

# =============================================================================
# SECTION 5: CONDITIONAL OPTIMIZE — not applicable for staging table
# =============================================================================
# Staging table is overwritten each run; OPTIMIZE is not warranted here.

# =============================================================================
# SECTION 6: CLOSE LINEAGE — staging extract does not close lineage
#            (lineage closed by migrate_staged_purchase_data after MERGE completes)
# =============================================================================
print(
    f"Staging extract complete. "
    f"lineage_key={lineage_key}, "
    f"rows_staged={staged_row_count}, "
    f"watermark_window=[{last_cutoff}, {current_cutoff}]"
)
