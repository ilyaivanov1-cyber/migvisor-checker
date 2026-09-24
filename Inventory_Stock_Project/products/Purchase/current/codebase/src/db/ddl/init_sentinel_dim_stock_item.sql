-- DB-006: Insert sentinel row into silver_dim.stock_item.
-- Sentinel row absorbs unresolved stock_item foreign keys (wwi_stock_item_id = 0).
-- Run ONCE after table creation, before any ETL pipeline run.
-- Idempotent: INSERT OR IGNORE pattern — safe to re-run.

INSERT INTO inventory_stock.silver_dim.stock_item (
    wwi_stock_item_id,
    stock_item_name,
    supplier_key,
    color_name,
    brand,
    size,
    lead_time_days,
    quantity_per_outer,
    is_chiller_stock,
    barcode,
    tax_rate,
    unit_price,
    recommended_retail_price,
    typical_weight_per_unit,
    valid_from,
    valid_to,
    is_current,
    lineage_key
)
SELECT
    0                       AS wwi_stock_item_id,
    'Unknown Stock Item'    AS stock_item_name,
    -1                      AS supplier_key,
    'Unknown'               AS color_name,
    'Unknown'               AS brand,
    NULL                    AS size,
    0                       AS lead_time_days,
    1                       AS quantity_per_outer,
    FALSE                   AS is_chiller_stock,
    NULL                    AS barcode,
    0.0                     AS tax_rate,
    0.0                     AS unit_price,
    0.0                     AS recommended_retail_price,
    0.0                     AS typical_weight_per_unit,
    '2000-01-01'::DATE      AS valid_from,
    '9999-12-31'::DATE      AS valid_to,
    TRUE                    AS is_current,
    -1                      AS lineage_key
WHERE NOT EXISTS (
    SELECT 1
    FROM inventory_stock.silver_dim.stock_item
    WHERE wwi_stock_item_id = 0
);

-- Verify:
-- SELECT * FROM inventory_stock.silver_dim.stock_item WHERE wwi_stock_item_id = 0;
-- Expected: 1 row, stock_item_name = 'Unknown Stock Item', is_current = true
