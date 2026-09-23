-- TASK-006: purchasing.meta.v_etl_cutoff
-- Design ref: Design.md §1.1 Entities (reporting view over purchasing.meta.etl_cutoff).
-- Requirements: FR-001, FR-008
-- Depends on: purchasing.meta.etl_cutoff (this task, meta_etl_cutoff.sql)

CREATE OR REPLACE VIEW purchasing.meta.v_etl_cutoff AS
SELECT * FROM purchasing.meta.etl_cutoff;
