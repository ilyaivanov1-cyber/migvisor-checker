# Notebook: nb_load_dim_supplier
# Purpose : Load supplier dimension using SCD-2 MERGE from staging data.
# Rules   : FR-004, FR-005, LN-001, NFR-009

from pyspark.sql import functions as F

from src.common.constants import PURCHASE_STAGING_TABLE, SUPPLIER_DIM_TABLE
from src.common.scd2_merge import apply_scd2_merge

# ── Widgets ───────────────────────────────────────────────────────────────────
dbutils.widgets.text("env_scope", "inventory-stock-dev")

lineage_key = int(dbutils.jobs.taskValues.get(
    taskKey="nb_open_batch", key="lineage_key", debugValue=-1
))

# ── Extract distinct suppliers from staging ───────────────────────────────────
source_df = spark.sql(f"""
    SELECT DISTINCT
        supplier_id                     AS wwi_supplier_id,
        supplier_name,
        supplier_category_name          AS category,
        primary_contact,
        supplier_reference,
        payment_days,
        CAST(current_date() AS DATE)    AS valid_from,
        CAST('9999-12-31' AS DATE)      AS valid_to,
        TRUE                            AS is_current,
        TRUE                            AS is_current_row,
        CAST(current_date() AS DATE)    AS row_effective_date,
        CAST('9999-12-31' AS DATE)      AS row_expiry_date,
        {lineage_key}                   AS lineage_key
    FROM {PURCHASE_STAGING_TABLE}
    WHERE lineage_key = {lineage_key}
""")

# ── Apply SCD-2 MERGE ─────────────────────────────────────────────────────────
apply_scd2_merge(
    spark=spark,
    target_table=SUPPLIER_DIM_TABLE,
    source_df=source_df,
    business_key_col="wwi_supplier_id",
    natural_key_col="wwi_supplier_id",
)

loaded_count = source_df.count()
print(f"nb_load_dim_supplier complete. Rows processed: {loaded_count}, lineage_key: {lineage_key}")
