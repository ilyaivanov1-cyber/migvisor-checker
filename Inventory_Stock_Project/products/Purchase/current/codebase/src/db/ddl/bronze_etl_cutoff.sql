-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_etl_cutoff.sql
-- PURPOSE  : Watermark control table; one row per tracked table
-- SOURCE   : (no source object — new table)
-- TARGET   : inventory_stock.bronze.etl_cutoff (Databricks Delta Lake)
-- RULES    : LN-005, OB-004, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.bronze.etl_cutoff (
    table_name       STRING     NOT NULL,
    cutoff_time      TIMESTAMP  NOT NULL,
    last_updated_utc TIMESTAMP  NOT NULL
)
USING DELTA;
