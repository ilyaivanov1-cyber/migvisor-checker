-- DB-010: Mart layer view definitions for Purchase data product.
-- Views are BI-facing — no raw data exposed, only joined/aggregated results.
-- Run after all fact and dimension tables are populated.

-- ── View 1: Purchase summary by supplier ──────────────────────────────────────
CREATE OR REPLACE MATERIALIZED VIEW inventory_stock.mart.v_purchase_by_supplier
COMMENT 'Aggregated purchase totals per supplier per day — primary BI view for procurement dashboards'
AS
SELECT
    d.calendar_date,
    d.calendar_year,
    d.calendar_month_number,
    s.wwi_supplier_id,
    s.supplier_name,
    s.category,
    SUM(f.ordered_outers)      AS total_ordered_outers,
    SUM(f.ordered_quantity)    AS total_ordered_quantity,
    SUM(f.received_outers)     AS total_received_outers,
    COUNT(DISTINCT f.wwi_purchase_order_id) AS distinct_purchase_orders,
    MAX(f.lineage_key)         AS lineage_key
FROM inventory_stock.silver_fact.fact_purchase f
JOIN inventory_stock.silver_dim.date          d ON f.date_key      = d.date_key
JOIN inventory_stock.silver_dim.supplier      s ON f.supplier_key  = s.supplier_key
WHERE s.is_current = TRUE
GROUP BY
    d.calendar_date,
    d.calendar_year,
    d.calendar_month_number,
    s.wwi_supplier_id,
    s.supplier_name,
    s.category;

-- ── View 2: Purchase detail per stock item ────────────────────────────────────
CREATE OR REPLACE VIEW inventory_stock.mart.v_purchase_per_stock_item
COMMENT 'Per-stock-item purchase quantities — used for inventory reconciliation and stock analytics'
AS
SELECT
    d.calendar_date,
    d.calendar_year,
    s.wwi_supplier_id,
    s.supplier_name,
    si.wwi_stock_item_id,
    si.stock_item_name,
    si.brand,
    si.color_name,
    f.wwi_purchase_order_id,
    f.ordered_outers,
    f.ordered_quantity,
    f.received_outers,
    f.package,
    f.is_order_finalized,
    f.lineage_key
FROM inventory_stock.silver_fact.fact_purchase f
JOIN inventory_stock.silver_dim.date           d  ON f.date_key       = d.date_key
JOIN inventory_stock.silver_dim.supplier       s  ON f.supplier_key   = s.supplier_key
JOIN inventory_stock.silver_dim.stock_item     si ON f.stock_item_key = si.stock_item_key
WHERE s.is_current  = TRUE
  AND si.is_current = TRUE;
