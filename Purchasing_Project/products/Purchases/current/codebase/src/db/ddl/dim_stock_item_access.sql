-- TASK-003: purchasing.dim.stock_item — cross-catalog access stub
-- [PENDING: PL-008/OB-002] Cross-catalog sharing mechanism not yet decided.
-- Stubbed as an independently maintained duplicate copy under `purchasing`, mirroring
-- Design.md §1.2 Attributes for purchasing.dim.stock_item. If PL-008/OB-002 resolves to a
-- Unity Catalog cross-catalog GRANT instead, replace this CREATE TABLE with:
--   GRANT SELECT ON TABLE globalsales.dim.stock_item TO `purchasing-consumers`;
-- No downstream task (TASK-011, TASK-018) requires any change either way.
-- Requirements: FR-003

CREATE TABLE IF NOT EXISTS purchasing.dim.stock_item (
  stock_item_key    BIGINT NOT NULL,
  wwi_stock_item_id BIGINT NOT NULL,
  stock_item_name   STRING NOT NULL,
  valid_from        TIMESTAMP NOT NULL,
  valid_to          TIMESTAMP NOT NULL,
  is_current        BOOLEAN NOT NULL
)
USING DELTA
CLUSTER BY (wwi_stock_item_id, valid_from);

-- Seed the Unknown row used as the fallback surrogate key when valid-time resolution finds no match (FR-003).
MERGE INTO purchasing.dim.stock_item AS target
USING (
  SELECT
    0 AS stock_item_key,
    -1 AS wwi_stock_item_id,
    'Unknown' AS stock_item_name,
    TIMESTAMP '0001-01-01T00:00:00' AS valid_from,
    TIMESTAMP '9999-12-31T23:59:59' AS valid_to,
    true AS is_current
) AS source
ON target.stock_item_key = source.stock_item_key
WHEN NOT MATCHED THEN INSERT *;
