-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : purchase_grants.sql
-- PURPOSE  : Unity Catalog GRANT statements for Purchase product access tiers
-- SOURCE   : (no source object)
-- TARGET   : inventory_stock catalog (Databricks Unity Catalog)
-- RULES    : SE-001, SE-002, NFR-008, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
-- NOTE: Replace {{BI_SERVICE_PRINCIPAL}} and {{ETL_SERVICE_PRINCIPAL}}
--       with actual Unity Catalog principal names before execution (PD-003 pending).

-- Tier 1: BI analysts — read access to silver serving layer
GRANT SELECT ON TABLE inventory_stock.silver_fact.fact_purchase    TO `{{BI_SERVICE_PRINCIPAL}}`;
GRANT SELECT ON TABLE inventory_stock.silver_fact.fact_purchase    TO `data_analysts`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.supplier          TO `{{BI_SERVICE_PRINCIPAL}}`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.supplier          TO `data_analysts`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.stock_item        TO `{{BI_SERVICE_PRINCIPAL}}`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.stock_item        TO `data_analysts`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.date              TO `{{BI_SERVICE_PRINCIPAL}}`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.date              TO `data_analysts`;

-- Tier 2: ETL service principal — full access to bronze and silver_fact
GRANT SELECT, MODIFY ON SCHEMA inventory_stock.bronze              TO `{{ETL_SERVICE_PRINCIPAL}}`;
GRANT SELECT, MODIFY ON SCHEMA inventory_stock.silver_fact         TO `{{ETL_SERVICE_PRINCIPAL}}`;

-- Tier 3: data engineering team — read access to DQ rejections
GRANT SELECT ON TABLE inventory_stock.bronze.dq_rejections         TO `data_engineering`;
