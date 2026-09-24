-- Validation queries for Purchase ETL pipeline.
-- Run manually or in nb_dq_assertions to verify pipeline state.
-- All queries are read-only — safe to run in any environment.

-- ── 1. Row count checks ───────────────────────────────────────────────────────

-- Staging row count for the latest batch
SELECT
    lineage_key,
    COUNT(*) AS row_count,
    MIN(last_edited_when) AS min_edit_date,
    MAX(last_edited_when) AS max_edit_date
FROM inventory_stock.bronze.purchase_staging
GROUP BY lineage_key
ORDER BY lineage_key DESC
LIMIT 5;

-- Fact table total row count
SELECT COUNT(*) AS fact_purchase_total_rows
FROM inventory_stock.silver_fact.fact_purchase;

-- ── 2. Lineage run status ─────────────────────────────────────────────────────

SELECT
    lineage_key,
    etl_run_id,
    pipeline_name,
    data_load_started,
    data_load_completed,
    was_successful,
    table_row_count,
    source_system_cutoff_time
FROM inventory_stock.bronze.lineage_run
ORDER BY data_load_started DESC
LIMIT 10;

-- ── 3. Watermark state ────────────────────────────────────────────────────────

SELECT entity_name, last_cutoff_time
FROM inventory_stock.bronze.etl_cutoff
ORDER BY entity_name;

-- ── 4. DQ rejections for the last run ────────────────────────────────────────

SELECT
    lineage_key,
    rule_id,
    severity,
    COUNT(*) AS violation_count
FROM inventory_stock.bronze.dq_rejections
WHERE lineage_key = (SELECT MAX(lineage_key) FROM inventory_stock.bronze.lineage_run WHERE was_successful = TRUE)
GROUP BY lineage_key, rule_id, severity
ORDER BY lineage_key DESC, rule_id;

-- ── 5. Dimension completeness ─────────────────────────────────────────────────

-- Supplier current rows
SELECT COUNT(*) AS current_supplier_count
FROM inventory_stock.silver_dim.supplier
WHERE is_current = TRUE;

-- Stock item current rows
SELECT COUNT(*) AS current_stock_item_count
FROM inventory_stock.silver_dim.stock_item
WHERE is_current = TRUE;

-- ── 6. Fact referential integrity spot-check ──────────────────────────────────

-- Unresolved supplier keys (should be 0 or only sentinel -1)
SELECT supplier_key, COUNT(*) AS row_count
FROM inventory_stock.silver_fact.fact_purchase f
WHERE NOT EXISTS (
    SELECT 1 FROM inventory_stock.silver_dim.supplier s
    WHERE s.supplier_key = f.supplier_key
)
GROUP BY supplier_key;

-- Unresolved stock_item keys
SELECT stock_item_key, COUNT(*) AS row_count
FROM inventory_stock.silver_fact.fact_purchase f
WHERE NOT EXISTS (
    SELECT 1 FROM inventory_stock.silver_dim.stock_item si
    WHERE si.stock_item_key = f.stock_item_key
)
GROUP BY stock_item_key;

-- ── 7. Mart view sanity check ─────────────────────────────────────────────────

SELECT COUNT(*) AS mart_supplier_rows
FROM inventory_stock.mart.v_purchase_by_supplier;

SELECT COUNT(*) AS mart_stock_item_rows
FROM inventory_stock.mart.v_purchase_per_stock_item;
