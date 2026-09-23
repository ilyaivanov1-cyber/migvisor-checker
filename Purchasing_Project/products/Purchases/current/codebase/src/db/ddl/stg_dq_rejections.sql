-- TASK-008: purchasing.stg.dq_rejections
-- Design ref: Design.md §1.2 Attributes — purchasing.stg.dq_rejections.
-- Requirements: NFR-006
-- Depends on: TASK-004 (meta.lineage)

CREATE TABLE IF NOT EXISTS purchasing.stg.dq_rejections (
  rejection_id     BIGINT NOT NULL,
  lineage_key      BIGINT NOT NULL,
  assertion_id     STRING NOT NULL,
  source_table     STRING NOT NULL,
  source_key       BIGINT,
  rejection_reason STRING NOT NULL,
  rejected_at      TIMESTAMP NOT NULL
)
USING DELTA;
