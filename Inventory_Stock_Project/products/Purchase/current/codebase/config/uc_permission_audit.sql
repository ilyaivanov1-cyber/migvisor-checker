-- CFG-004: Unity Catalog permission audit script.
-- Read-only — lists all grants across the inventory_stock catalog.
-- Run after GRANT-001 through GRANT-004 to verify the expected privilege mapping.
-- Idempotent: SHOW GRANTS statements do not modify any state.

-- ── Catalog level ─────────────────────────────────────────────────────────────
-- Expected: etl-service-principal and bi-service-principal have USE CATALOG
SHOW GRANTS ON CATALOG inventory_stock;

-- ── Schema level ─────────────────────────────────────────────────────────────
-- bronze: etl-service-principal has USE SCHEMA + SELECT + MODIFY
SHOW GRANTS ON SCHEMA inventory_stock.bronze;

-- silver_dim: etl-service-principal and bi-service-principal have USE SCHEMA
SHOW GRANTS ON SCHEMA inventory_stock.silver_dim;

-- silver_fact: etl-service-principal and bi-service-principal have USE SCHEMA
SHOW GRANTS ON SCHEMA inventory_stock.silver_fact;

-- mart: etl-service-principal, bi-service-principal, purchase-analysts have USE SCHEMA
SHOW GRANTS ON SCHEMA inventory_stock.mart;

-- ── Table level ───────────────────────────────────────────────────────────────
-- bronze tables
SHOW GRANTS ON TABLE inventory_stock.bronze.purchase_staging;
SHOW GRANTS ON TABLE inventory_stock.bronze.etl_cutoff;
SHOW GRANTS ON TABLE inventory_stock.bronze.lineage_run;
SHOW GRANTS ON TABLE inventory_stock.bronze.dq_rejections;

-- silver_dim tables (GRANT-001, GRANT-002)
-- Expected: etl → SELECT+MODIFY; bi → SELECT
SHOW GRANTS ON TABLE inventory_stock.silver_dim.supplier;
SHOW GRANTS ON TABLE inventory_stock.silver_dim.stock_item;
SHOW GRANTS ON TABLE inventory_stock.silver_dim.date;

-- silver_fact table (GRANT-003)
-- Expected: etl → SELECT+MODIFY; bi → SELECT
SHOW GRANTS ON TABLE inventory_stock.silver_fact.fact_purchase;

-- ── Mart view level ───────────────────────────────────────────────────────────
-- Expected: bi + analysts → SELECT; etl → SELECT+REFRESH on materialized view
SHOW GRANTS ON MATERIALIZED VIEW inventory_stock.mart.v_purchase_by_supplier;
SHOW GRANTS ON VIEW inventory_stock.mart.v_purchase_per_stock_item;

-- ── Principal-to-privilege mapping (expected after all GRANT scripts) ─────────
--
-- Principal               | Object                                          | Privileges
-- ----------------------- | ----------------------------------------------- | --------------------------
-- etl-service-principal   | inventory_stock.silver_dim.supplier             | SELECT, MODIFY
-- etl-service-principal   | inventory_stock.silver_dim.stock_item           | SELECT, MODIFY
-- etl-service-principal   | inventory_stock.silver_fact.fact_purchase       | SELECT, MODIFY
-- etl-service-principal   | mart.v_purchase_by_supplier (MV)                | SELECT, REFRESH
-- bi-service-principal    | inventory_stock.silver_dim.supplier             | SELECT
-- bi-service-principal    | inventory_stock.silver_dim.stock_item           | SELECT
-- bi-service-principal    | inventory_stock.silver_fact.fact_purchase       | SELECT
-- bi-service-principal    | inventory_stock.mart.*                          | SELECT
-- purchase-analysts       | inventory_stock.mart.*                          | SELECT
