# Notebook: nb_resolve_keys
# Purpose : Resolve surrogate keys (supplier_key, stock_item_key, date_key)
#           from staging data using sk_resolver utilities.
#           Writes resolved staging to a temp view for downstream fact load.
# Rules   : FR-004, FR-005, CALC-002, CALC-003, DQR-009, NFR-009

from src.common.constants import (
    PURCHASE_STAGING_TABLE,
    SUPPLIER_DIM_TABLE,
    STOCK_ITEM_DIM_TABLE,
    DATE_DIM_TABLE,
)
from src.common.sk_resolver import resolve_supplier_key, resolve_stock_item_key

lineage_key = int(dbutils.jobs.taskValues.get(
    taskKey="nb_open_batch", key="lineage_key", debugValue=-1
))

# ── Load staging for this batch ───────────────────────────────────────────────
staging_df = spark.sql(f"""
    SELECT * FROM {PURCHASE_STAGING_TABLE}
    WHERE lineage_key = {lineage_key}
""")

# ── Load dimension tables ─────────────────────────────────────────────────────
supplier_dim_df    = spark.table(SUPPLIER_DIM_TABLE).filter("is_current = TRUE")
stock_item_dim_df  = spark.table(STOCK_ITEM_DIM_TABLE).filter("is_current = TRUE")
date_dim_df        = spark.table(DATE_DIM_TABLE).select("date_key", "calendar_date")

# ── Resolve supplier and stock item keys ──────────────────────────────────────
resolved_df = resolve_supplier_key(staging_df, supplier_dim_df)
resolved_df = resolve_stock_item_key(resolved_df, stock_item_dim_df)

# ── Resolve date_key via join on calendar_date ────────────────────────────────
from pyspark.sql import functions as F

resolved_df = (
    resolved_df
    .join(date_dim_df,
          resolved_df["order_date"].cast("date") == date_dim_df["calendar_date"],
          how="left")
    .withColumn("date_key", F.coalesce(F.col("date_key"), F.lit(0)))
    .drop("calendar_date")
)

# ── Expose as temp view for nb_load_fact ─────────────────────────────────────
resolved_df.createOrReplaceTempView("resolved_staging")

row_count = resolved_df.count()
null_supplier   = resolved_df.filter("supplier_key = 0").count()
null_stock_item = resolved_df.filter("stock_item_key = 0").count()
null_date       = resolved_df.filter("date_key = 0").count()

print(f"nb_resolve_keys complete. Rows: {row_count}")
print(f"  Unresolved supplier_key (sentinel 0): {null_supplier}")
print(f"  Unresolved stock_item_key (sentinel 0): {null_stock_item}")
print(f"  Unresolved date_key (sentinel 0): {null_date}")
