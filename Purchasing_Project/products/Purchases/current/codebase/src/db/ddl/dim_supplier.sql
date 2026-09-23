-- TASK-002: purchasing.dim.supplier (SCD2)
-- Design ref: Design.md §1.2 Attributes — purchasing.dim.supplier; §1.4 Indexes and Partitioning (clustering key).
-- Requirements: FR-002

CREATE TABLE IF NOT EXISTS purchasing.dim.supplier (
  supplier_key    BIGINT NOT NULL,
  wwi_supplier_id BIGINT NOT NULL,
  supplier_name   STRING NOT NULL,
  category        STRING,
  valid_from      TIMESTAMP NOT NULL,
  valid_to        TIMESTAMP NOT NULL,
  is_current      BOOLEAN NOT NULL
)
USING DELTA
CLUSTER BY (wwi_supplier_id, valid_from);

-- Seed the Unknown row used as the fallback surrogate key when valid-time resolution finds no match (FR-002).
MERGE INTO purchasing.dim.supplier AS target
USING (
  SELECT
    0 AS supplier_key,
    -1 AS wwi_supplier_id,
    'Unknown' AS supplier_name,
    CAST(NULL AS STRING) AS category,
    TIMESTAMP '0001-01-01T00:00:00' AS valid_from,
    TIMESTAMP '9999-12-31T23:59:59' AS valid_to,
    true AS is_current
) AS source
ON target.supplier_key = source.supplier_key
WHEN NOT MATCHED THEN INSERT *;
