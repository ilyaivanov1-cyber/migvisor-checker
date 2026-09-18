# ============================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/etl/nb_extract_watermark.py
# Purpose  : Watermark extraction — Task 1 of nightly_etl_purchase workflow
# Rules    : FR-002, FR-003, NFR-009, CX-P005, LN-P001, SX-P001
# ============================================================

# =============================================================================
# SECTION 1: IMPORTS
# =============================================================================
import yaml
from datetime import datetime, timezone
from pyspark.sql import functions as F
from src.common.constants import (
    ETL_CUTOFF_TABLE, ETL_CUTOFF_TABLE_NAME, LINEAGE_RUN_TABLE
)

with open("config/environment.yaml") as f:
    cfg = yaml.safe_load(f)

INITIAL_LOAD_DATE = cfg["purchase"]["etl"]["initial_load_date"]
PIPELINE_NAME     = "nightly_etl_purchase"

# =============================================================================
# SECTION 2: LINEAGE KEY — nb_extract_watermark GENERATES the lineage_key
#            (does not receive it via taskValues.get)
# =============================================================================
current_cutoff = datetime.now(timezone.utc)

# Read last successful cutoff — default to initial_load_date if no record
cutoff_row = spark.sql(f"""
    SELECT cutoff_time FROM {ETL_CUTOFF_TABLE}
    WHERE table_name = '{ETL_CUTOFF_TABLE_NAME}'
""").collect()

last_cutoff = cutoff_row[0]["cutoff_time"] if cutoff_row else INITIAL_LOAD_DATE

# Insert lineage record; IDENTITY column returns the new lineage_key
spark.sql(f"""
    INSERT INTO {LINEAGE_RUN_TABLE}
        (etl_run_id, table_name, pipeline_name, data_load_started, source_system_cutoff_time)
    VALUES (
        '{current_cutoff.isoformat()}',
        '{ETL_CUTOFF_TABLE_NAME}',
        '{PIPELINE_NAME}',
        current_timestamp(),
        '{current_cutoff.isoformat()}'
    )
""")

lineage_key = spark.sql(f"""
    SELECT MAX(lineage_key) AS lineage_key FROM {LINEAGE_RUN_TABLE}
    WHERE etl_run_id = '{current_cutoff.isoformat()}'
""").collect()[0]["lineage_key"]

# =============================================================================
# SECTION 3: ZERO-ROWS GUARD — not applicable for watermark notebook
# =============================================================================
# (watermark notebook extracts control data, not staging rows)

# =============================================================================
# SECTION 4: MAIN ETL LOGIC — Publish watermark values via taskValues
# =============================================================================
try:
    dbutils.jobs.taskValues.set(key="lineage_key",    value=int(lineage_key))
    dbutils.jobs.taskValues.set(key="last_cutoff",    value=str(last_cutoff))
    dbutils.jobs.taskValues.set(key="current_cutoff", value=str(current_cutoff))
except Exception as e:
    spark.sql(f"""
        UPDATE {LINEAGE_RUN_TABLE}
        SET was_successful = false, data_load_completed = current_timestamp()
        WHERE lineage_key = {lineage_key}
    """)
    raise

# =============================================================================
# SECTION 5: CONDITIONAL OPTIMIZE — not applicable for watermark notebook
# =============================================================================

# =============================================================================
# SECTION 6: CLOSE LINEAGE — watermark notebook leaves lineage open
#            (closed by migrate_staged_purchase_data after MERGE completes)
# =============================================================================
print(f"Watermark published. lineage_key={lineage_key}, last_cutoff={last_cutoff}, current_cutoff={current_cutoff}")
