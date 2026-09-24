# Notebook: nb_advance_watermark
# Purpose : Advance the ETL watermark to the source system cutoff time from
#           the current batch. Run after successful fact load and DQ checks.
# Rules   : FR-001, FR-002, LN-001, NFR-009

from src.common.constants import ETL_CUTOFF_TABLE, ETL_CUTOFF_TABLE_NAME

lineage_key = int(dbutils.jobs.taskValues.get(
    taskKey="nb_open_batch", key="lineage_key", debugValue=-1
))
source_system_cutoff_time = dbutils.jobs.taskValues.get(
    taskKey="nb_open_batch", key="source_system_cutoff_time", debugValue=""
)

if not source_system_cutoff_time:
    raise ValueError("source_system_cutoff_time task value is missing — cannot advance watermark.")

# ── Advance the watermark ─────────────────────────────────────────────────────
spark.sql(f"""
    UPDATE {ETL_CUTOFF_TABLE}
    SET last_cutoff_time = CAST('{source_system_cutoff_time}' AS TIMESTAMP)
    WHERE entity_name = '{ETL_CUTOFF_TABLE_NAME}'
""")

new_cutoff = spark.sql(f"""
    SELECT last_cutoff_time
    FROM {ETL_CUTOFF_TABLE}
    WHERE entity_name = '{ETL_CUTOFF_TABLE_NAME}'
""").first()["last_cutoff_time"]

print(f"Watermark advanced to: {new_cutoff} (lineage_key: {lineage_key})")
