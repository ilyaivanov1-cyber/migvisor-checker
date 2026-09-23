-- TASK-003: purchasing.dim.date — cross-catalog access stub
-- [PENDING: PL-008/OB-002] Cross-catalog sharing mechanism not yet decided.
-- Stubbed as an independently maintained duplicate copy under `purchasing`, mirroring
-- Design.md §1.2 Attributes for purchasing.dim.date (static calendar spine, declarative
-- FK target only — no active load-time lookup). If PL-008/OB-002 resolves to a Unity
-- Catalog cross-catalog GRANT instead, replace this CREATE TABLE with:
--   GRANT SELECT ON TABLE globalsales.dim.date TO `purchasing-consumers`;
-- Requirements: FR-003

CREATE TABLE IF NOT EXISTS purchasing.dim.date (
  date_key   BIGINT NOT NULL,
  date_value DATE NOT NULL
)
USING DELTA;
