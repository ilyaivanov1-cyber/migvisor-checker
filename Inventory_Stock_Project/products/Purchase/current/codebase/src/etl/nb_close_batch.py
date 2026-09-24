# Notebook: nb_close_batch
# Purpose : Mark the lineage_run row as successful and record final row count.
#           Run as the last step after all data loads and DQ checks pass.
# Rules   : LN-001, LN-002, FR-010, NFR-009

from datetime import datetime, timezone

from src.common.constants import LINEAGE_RUN_TABLE, FACT_PURCHASE_TABLE

lineage_key = int(dbutils.jobs.taskValues.get(
    taskKey="nb_open_batch", key="lineage_key", debugValue=-1
))
etl_run_id = dbutils.jobs.taskValues.get(
    taskKey="nb_open_batch", key="etl_run_id", debugValue=""
)

# ── Count fact rows for this batch ────────────────────────────────────────────
row_count = spark.sql(f"""
    SELECT COUNT(*) AS cnt
    FROM {FACT_PURCHASE_TABLE}
    WHERE lineage_key = {lineage_key}
""").first()["cnt"]

completed_at = datetime.now(timezone.utc)

# ── Update lineage_run to successful ─────────────────────────────────────────
spark.sql(f"""
    UPDATE {LINEAGE_RUN_TABLE}
    SET
        was_successful       = TRUE,
        data_load_completed  = CAST('{completed_at.isoformat()}' AS TIMESTAMP),
        table_row_count      = {row_count}
    WHERE etl_run_id = '{etl_run_id}'
""")

print(f"Batch closed. lineage_key={lineage_key}, was_successful=TRUE, row_count={row_count}")
