-- CFG-003: Unity Catalog bootstrap — catalog and schema setup.
-- Run ONCE before any table DDL (DB-001 through DB-010).
-- Idempotent: IF NOT EXISTS guards on every statement.
--
-- Schema responsibilities:
--   bronze:       raw landing zone (purchase_staging, lineage_run, etl_cutoff, dq_rejections)
--   silver_dim:   SCD-2 dimension tables (dim_supplier, dim_stock_item, dim_date)
--   silver_fact:  fact MERGE output (fact_purchase)
--   mart:         BI-facing views (v_purchase_by_supplier, v_purchase_per_stock_item)

-- Step 1: Create the catalog
CREATE CATALOG IF NOT EXISTS inventory_stock
COMMENT 'Top-level Unity Catalog for the Inventory Stock data product suite';

-- Step 2: Create the four medallion schemas
-- Execution order: bronze → silver_dim → silver_fact → mart (logical order)

CREATE SCHEMA IF NOT EXISTS inventory_stock.bronze
COMMENT 'Bronze schema: transient landing zone, watermark control, pipeline audit, and DQ rejection log';

CREATE SCHEMA IF NOT EXISTS inventory_stock.silver_dim
COMMENT 'Silver Dimension schema: SCD-2 conformed dimensions (supplier, stock_item) and static calendar (date)';

CREATE SCHEMA IF NOT EXISTS inventory_stock.silver_fact
COMMENT 'Silver Fact schema: central purchase fact table loaded incrementally via MERGE';

CREATE SCHEMA IF NOT EXISTS inventory_stock.mart
COMMENT 'Serving schema: BI-facing views and materialized views over the fact and dimension layers';

-- Verification (run after this script to confirm all four schemas are present):
SHOW SCHEMAS IN CATALOG inventory_stock;
-- Expected output: bronze, silver_dim, silver_fact, mart
