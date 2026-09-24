# Notebook: nb_open_batch
# Purpose : Open a new ETL batch by inserting a lineage_run row and broadcasting
#           the lineage_key to downstream notebooks via Databricks task values.
# Rules   : LN-001, LN-002, NFR-009

import uuid
from datetime import datetime, timezone

from src.common.constants import LINEAGE_RUN_TABLE, ETL_CUTOFF_TABLE, ETL_CUTOFF_TABLE_NAME

# ── Widgets ───────────────────────────────────────────────────────────────────
dbutils.widgets.text("env_scope", "inventory-stock-dev")
dbutils.widgets.text("pipeline_name", "purchase_etl")

env_scope     = dbutils.widgets.get("env_scope")
pipeline_name = dbutils.widgets.get("pipeline_name")

# ── Read current watermark (cutoff) ──────────────────────────────────────────
cutoff_row = spark.sql(f"""
    SELECT last_cutoff_time
    FROM {ETL_CUTOFF_TABLE}
    WHERE entity_name = '{ETL_CUTOFF_TABLE_NAME}'
""").first()

if cutoff_row is None:
    raise ValueError(
        f"No watermark row found for entity '{ETL_CUTOFF_TABLE_NAME}'. "
        "Run src/db/ddl/seed_watermark.sql first."
    )

source_system_cutoff_time = cutoff_row["last_cutoff_time"]

# ── Open lineage row ──────────────────────────────────────────────────────────
etl_run_id   = str(uuid.uuid4())
started_at   = datetime.now(timezone.utc)

spark.sql(f"""
    INSERT INTO {LINEAGE_RUN_TABLE} (
        etl_run_id,
        table_name,
        pipeline_name,
        data_load_started,
        data_load_completed,
        was_successful,
        table_row_count,
        source_system_cutoff_time
    ) VALUES (
        '{etl_run_id}',
        'fact_purchase',
        '{pipeline_name}',
        CAST('{started_at.isoformat()}' AS TIMESTAMP),
        NULL,
        FALSE,
        0,
        CAST('{source_system_cutoff_time}' AS TIMESTAMP)
    )
""")

lineage_key = spark.sql(f"""
    SELECT lineage_key
    FROM {LINEAGE_RUN_TABLE}
    WHERE etl_run_id = '{etl_run_id}'
""").first()["lineage_key"]

# ── Broadcast to downstream tasks ────────────────────────────────────────────
dbutils.jobs.taskValues.set(key="lineage_key",               value=lineage_key)
dbutils.jobs.taskValues.set(key="etl_run_id",                value=etl_run_id)
dbutils.jobs.taskValues.set(key="source_system_cutoff_time", value=str(source_system_cutoff_time))

print(f"Batch opened. lineage_key={lineage_key}, etl_run_id={etl_run_id}")
print(f"Source cutoff: {source_system_cutoff_time}")
