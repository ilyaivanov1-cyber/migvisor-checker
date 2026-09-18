-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : silver_dim_stock_item_current.sql
-- PURPOSE  : Current-version SCD-2 filter view for stock_item dimension
-- SOURCE   : (new view)
-- TARGET   : inventory_stock.silver_dim.stock_item_current (Databricks Delta Lake)
-- RULES    : OB-001, OB-P003, PE-004, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE OR REPLACE VIEW inventory_stock.silver_dim.stock_item_current AS
SELECT *
FROM   inventory_stock.silver_dim.stock_item
WHERE  is_current_row = TRUE;
