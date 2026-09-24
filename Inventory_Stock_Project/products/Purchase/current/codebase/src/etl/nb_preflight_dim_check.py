# Notebook: nb_preflight_dim_check
# Purpose : Verify that required dimension tables are populated and contain
#           at least the sentinel row before the main ETL runs.
# Rules   : FR-011, NFR-003, DQR-006

from src.common.constants import SUPPLIER_DIM_TABLE, STOCK_ITEM_DIM_TABLE

# ── Supplier dimension check ──────────────────────────────────────────────────
supplier_count = spark.sql(f"""
    SELECT COUNT(*) AS cnt FROM {SUPPLIER_DIM_TABLE} WHERE is_current = TRUE
""").first()["cnt"]

if supplier_count == 0:
    raise ValueError(
        f"{SUPPLIER_DIM_TABLE} has no current rows. "
        "Run src/db/ddl/init_sentinel_dim_supplier.sql and reload dimensions first."
    )

# ── Stock item dimension check ────────────────────────────────────────────────
stock_item_count = spark.sql(f"""
    SELECT COUNT(*) AS cnt FROM {STOCK_ITEM_DIM_TABLE} WHERE is_current = TRUE
""").first()["cnt"]

if stock_item_count == 0:
    raise ValueError(
        f"{STOCK_ITEM_DIM_TABLE} has no current rows. "
        "Run src/db/ddl/init_sentinel_dim_stock_item.sql and reload dimensions first."
    )

print(f"Preflight OK. Supplier current rows: {supplier_count}, Stock item current rows: {stock_item_count}")
