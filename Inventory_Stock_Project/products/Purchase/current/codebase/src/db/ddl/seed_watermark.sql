-- DB-009: Initialize watermark control table for Purchase ETL.
-- Sets the history anchor date (first valid extract boundary).
-- Run ONCE before the first pipeline execution.
-- Idempotent: INSERT OR IGNORE pattern — safe to re-run.

-- HISTORY_ANCHOR_DATE: set to the earliest date in the source system purchase data.
-- Adjust this value to match the actual source system history start date.
DECLARE OR REPLACE VARIABLE HISTORY_ANCHOR_DATE DATE DEFAULT DATE '2013-01-01';

INSERT INTO inventory_stock.bronze.etl_cutoff (entity_name, last_cutoff_time)
SELECT
    'fact_purchase'                          AS entity_name,
    CAST(HISTORY_ANCHOR_DATE AS TIMESTAMP)   AS last_cutoff_time
WHERE NOT EXISTS (
    SELECT 1
    FROM inventory_stock.bronze.etl_cutoff
    WHERE entity_name = 'fact_purchase'
);

-- Verify:
-- SELECT * FROM inventory_stock.bronze.etl_cutoff WHERE entity_name = 'fact_purchase';
-- Expected: 1 row, last_cutoff_time = 2013-01-01 00:00:00
