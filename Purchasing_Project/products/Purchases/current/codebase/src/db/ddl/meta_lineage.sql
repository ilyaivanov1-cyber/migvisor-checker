-- TASK-004: purchasing.meta.lineage
-- Design ref: Design.md §1.2 Attributes — purchasing.meta.lineage.
-- Requirements: FR-005

CREATE TABLE IF NOT EXISTS purchasing.meta.lineage (
  lineage_key BIGINT NOT NULL,
  run_id      STRING NOT NULL,
  batch_start TIMESTAMP NOT NULL,
  batch_end   TIMESTAMP,
  status      STRING NOT NULL
)
USING DELTA;

ALTER TABLE purchasing.meta.lineage
  ADD CONSTRAINT lineage_status_valid CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED'));
