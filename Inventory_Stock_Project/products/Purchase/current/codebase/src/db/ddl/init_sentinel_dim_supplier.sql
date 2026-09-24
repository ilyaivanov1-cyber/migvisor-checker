-- DB-005: Insert sentinel row into silver_dim.supplier.
-- Sentinel row absorbs unresolved supplier foreign keys (wwi_supplier_id = 0).
-- Run ONCE after table creation, before any ETL pipeline run.
-- Idempotent: INSERT OR IGNORE pattern — safe to re-run.

INSERT INTO inventory_stock.silver_dim.supplier (
    wwi_supplier_id,
    supplier_name,
    category,
    primary_contact,
    supplier_reference,
    payment_days,
    valid_from,
    valid_to,
    is_current,
    lineage_key
)
SELECT
    0                       AS wwi_supplier_id,
    'Unknown Supplier'      AS supplier_name,
    'Unknown'               AS category,
    'Unknown'               AS primary_contact,
    'SENTINEL'              AS supplier_reference,
    0                       AS payment_days,
    '2000-01-01'::DATE      AS valid_from,
    '9999-12-31'::DATE      AS valid_to,
    TRUE                    AS is_current,
    -1                      AS lineage_key
WHERE NOT EXISTS (
    SELECT 1
    FROM inventory_stock.silver_dim.supplier
    WHERE wwi_supplier_id = 0
);

-- Verify:
-- SELECT * FROM inventory_stock.silver_dim.supplier WHERE wwi_supplier_id = 0;
-- Expected: 1 row, supplier_name = 'Unknown Supplier', is_current = true
