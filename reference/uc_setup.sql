-- CFG-003: Unity Catalog bootstrap — catalog and schema setup.
-- Run ONCE before any table DDL (DB-001 through DB-010).
-- Idempotent: IF NOT EXISTS guards on every statement.

-- Step 1: Create the catalog
CREATE CATALOG IF NOT EXISTS globalpurchase
COMMENT 'Top-level Unity Catalog for the GlobalPurchase data product suite';

-- Step 2: Create the four medallion schemas
-- Execution order: stg → dim → fact → mart (no dependency, but logical order)

CREATE SCHEMA IF NOT EXISTS globalpurchase.stg
COMMENT 'Staging schema: transient landing zone, watermark control, pipeline audit, and DQ rejection log';

CREATE SCHEMA IF NOT EXISTS globalpurchase.dim
COMMENT 'Dimension schema: SCD-2 conformed dimensions (supplier, stock_item) and static calendar (date)';

CREATE SCHEMA IF NOT EXISTS globalpurchase.fact
COMMENT 'Fact schema: central purchase fact table loaded incrementally via MERGE';

CREATE SCHEMA IF NOT EXISTS globalpurchase.mart
COMMENT 'Serving schema: BI-facing views and materialized views over the fact and dimension layers';

-- Verification query (run after this script):
-- SHOW SCHEMAS IN globalpurchase;
-- Expected: stg, dim, fact, mart
