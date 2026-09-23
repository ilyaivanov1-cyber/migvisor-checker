-- TASK-005: purchasing.meta.sequence_state
-- Design ref: Design.md §3.1 Calculations — CALC-004 (lineage_key issuance counter).
-- Requirements: FR-005

CREATE TABLE IF NOT EXISTS purchasing.meta.sequence_state (
  sequence_name STRING NOT NULL,
  current_value BIGINT NOT NULL
)
USING DELTA;

-- Seed the single counter row backing lineage_key issuance (TASK-013 increments it via
-- conditional MERGE to avoid concurrent-run duplicate values).
MERGE INTO purchasing.meta.sequence_state AS target
USING (SELECT 'lineage_key' AS sequence_name, 0 AS current_value) AS source
ON target.sequence_name = source.sequence_name
WHEN NOT MATCHED THEN INSERT *;
