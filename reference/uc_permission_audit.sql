-- CFG-004: Unity Catalog permission audit script.
-- Read-only — lists all grants across the globalpurchase catalog.
-- Run after GRANT-001 through GRANT-004 to verify the expected privilege mapping.
-- Idempotent: SHOW GRANTS statements do not modify any state.

-- ── Catalog level ─────────────────────────────────────────────────────────────
-- Expected: etl-service-principal and bi-service-principal have USE CATALOG
SHOW GRANTS ON CATALOG globalpurchase;

-- ── Schema level ─────────────────────────────────────────────────────────────
-- stg: etl-service-principal has USE SCHEMA + SELECT + MODIFY
SHOW GRANTS ON SCHEMA globalpurchase.stg;

-- dim: etl-service-principal and bi-service-principal have USE SCHEMA
SHOW GRANTS ON SCHEMA globalpurchase.dim;

-- fact: etl-service-principal and bi-service-principal have USE SCHEMA
SHOW GRANTS ON SCHEMA globalpurchase.fact;

-- mart: etl-service-principal, bi-service-principal, purchase-analysts have USE SCHEMA
SHOW GRANTS ON SCHEMA globalpurchase.mart;

-- ── Table level ───────────────────────────────────────────────────────────────
-- stg tables
SHOW GRANTS ON TABLE globalpurchase.stg.purchase_staging;
SHOW GRANTS ON TABLE globalpurchase.stg.etl_cutoff;
SHOW GRANTS ON TABLE globalpurchase.stg.lineage;
SHOW GRANTS ON TABLE globalpurchase.stg.dq_rejections;

-- dim tables (GRANT-001, GRANT-002)
-- Expected: etl → SELECT+MODIFY; bi → SELECT
SHOW GRANTS ON TABLE globalpurchase.dim.supplier;
SHOW GRANTS ON TABLE globalpurchase.dim.stock_item;
SHOW GRANTS ON TABLE globalpurchase.dim.date;

-- fact table (GRANT-003)
-- Expected: etl → SELECT+MODIFY; bi → SELECT
SHOW GRANTS ON TABLE globalpurchase.fact.purchase;

-- ── Mart view level ───────────────────────────────────────────────────────────
-- Expected: bi + analysts → SELECT; etl → SELECT+REFRESH on materialized view
SHOW GRANTS ON MATERIALIZED VIEW globalpurchase.mart.v_purchase_by_supplier;
SHOW GRANTS ON VIEW globalpurchase.mart.v_purchase_per_stock_item;

-- ── Principal-to-privilege mapping (expected after all GRANT scripts) ─────────
--
-- Principal               | Object                              | Privileges
-- ----------------------- | ----------------------------------- | --------------------------
-- etl-service-principal   | globalpurchase.dim.supplier         | SELECT, MODIFY
-- etl-service-principal   | globalpurchase.dim.stock_item       | SELECT, MODIFY
-- etl-service-principal   | globalpurchase.fact.purchase        | SELECT, MODIFY
-- etl-service-principal   | mart.v_purchase_by_supplier (MV)   | SELECT, REFRESH
-- bi-service-principal    | globalpurchase.dim.supplier         | SELECT
-- bi-service-principal    | globalpurchase.dim.stock_item       | SELECT
-- bi-service-principal    | globalpurchase.fact.purchase        | SELECT
-- bi-service-principal    | globalpurchase.mart.*               | SELECT
-- purchase-analysts       | globalpurchase.mart.*               | SELECT
