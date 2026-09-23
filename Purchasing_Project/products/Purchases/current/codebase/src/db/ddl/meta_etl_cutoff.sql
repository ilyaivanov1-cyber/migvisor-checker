-- TASK-006: purchasing.meta.etl_cutoff
-- Design ref: Design.md §1.1 Entities; §1.2 Attributes — purchasing.meta.etl_cutoff.
-- Requirements: FR-001, FR-008

CREATE TABLE IF NOT EXISTS purchasing.meta.etl_cutoff (
  entity_name STRING NOT NULL,
  last_cutoff TIMESTAMP NOT NULL,
  updated_at  TIMESTAMP NOT NULL
)
USING DELTA;

-- Seed the watermark row for the purchase_staging extraction (TASK-009 reads it; TASK-015 advances it).
MERGE INTO purchasing.meta.etl_cutoff AS target
USING (
  SELECT
    'purchase_staging' AS entity_name,
    TIMESTAMP '0001-01-01T00:00:00' AS last_cutoff,
    current_timestamp() AS updated_at
) AS source
ON target.entity_name = source.entity_name
WHEN NOT MATCHED THEN INSERT *;
