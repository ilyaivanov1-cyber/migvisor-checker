# Purchases — SmartBuilder Build Plan
_Generated: 2026-09-23 | Pipeline stage: plan_

---

## 1. Build Overview

| Metric | Value |
|---|---|
| Data product | Purchases |
| Project | Purchasing_Project |
| SDD version | 4.1 |
| Total tasks (tasks.md) | 23 |
| Mapped components | 22 |
| Unmapped tasks | 1 |
| Generating skills used | `generate-db`, `generate-etl` |
| Execution phases | 2 |

### Component breakdown by generating skill

| Generating skill | Task count | Task IDs |
|---|---|---|
| `generate-db` | 10 | TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-016, TASK-021 |
| `generate-etl` | 12 | TASK-009, TASK-010, TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-017, TASK-018, TASK-019, TASK-020, TASK-023 |
| Unmapped | 1 | TASK-022 |

`generate-etl` covers ETL pipeline, test, config, and documentation code per the deployed-skills scope, so `test`-type (TASK-017–019), `config`-type (TASK-020), and `docs`-type (TASK-023) tasks route to it alongside the `ETL`-type tasks. TASK-016 and TASK-021 are grouped under `generate-db` despite their `API`/`config` task types because both deliverables are Unity Catalog SQL scripts (a grant/access profile and a governance/grant script) directly analogous to the DDL objects `generate-db` already produces, and both depend directly on a DDL component (TASK-007).

### Execution phase summary

| Phase | Generating skill | Components | Purpose |
|---|---|---|---|
| Phase 1 | `generate-db` | TASK-001–008, TASK-016, TASK-021 | All schema DDL, plus the SQL-based access and governance scripts that sit directly on top of the DDL layer |
| Phase 2 | `generate-etl` | TASK-009–015, TASK-017–020, TASK-023 | Extraction, key resolution, calculation, MERGE load, watermark advance, quality assertions, orchestration config, and documentation |

---

## 2. Platform Components

| Task ID | Deliverable | Generating Skill | Depends On | Design Source Section |
|---|---|---|---|---|
| TASK-001 | `src/db/ddl/stg_purchase_staging.sql` | `generate-db` | none | §1.2 Attributes — `stg.purchase_staging`; §1.4 Indexes and Partitioning |
| TASK-002 | `src/db/ddl/dim_supplier.sql` | `generate-db` | none | §1.2 Attributes — `dim.supplier`; §1.4 Indexes and Partitioning |
| TASK-003 | `src/db/ddl/dim_stock_item_access.sql`, `src/db/ddl/dim_date_access.sql` | `generate-db` | none | §2 Ingestion, rows 3–4 |
| TASK-004 | `src/db/ddl/meta_lineage.sql` | `generate-db` | none | §1.2 Attributes — `meta.lineage` |
| TASK-005 | `src/db/ddl/meta_sequence_state.sql` | `generate-db` | none | §3.1 Calculations — CALC-004 |
| TASK-006 | `src/db/ddl/meta_etl_cutoff.sql`, `src/db/ddl/meta_v_etl_cutoff.sql` | `generate-db` | none | §1.1 Entities; §1.2 Attributes — `meta.etl_cutoff` |
| TASK-007 | `src/db/ddl/fact_purchase.sql` | `generate-db` | TASK-002, TASK-003, TASK-004 | §1.2 Attributes — `fact.purchase`; §1.4 Indexes and Partitioning |
| TASK-008 | `src/db/ddl/stg_dq_rejections.sql` | `generate-db` | TASK-004 | §1.2 Attributes — `stg.dq_rejections` |
| TASK-016 | `src/api/fact_purchase_access_profile.sql` | `generate-db` | TASK-007 | §4 Serving |
| TASK-021 | `config/fact_purchase_governance.sql` | `generate-db` | TASK-007, TASK-016 | §4 Serving |
| TASK-009 | `src/etl/extract_purchase_staging.py` | `generate-etl` | TASK-001, TASK-006 | §2 Ingestion, row 1; §3.2 Filters — FLT-001 |
| TASK-010 | `src/etl/resolve_supplier_key.py` | `generate-etl` | TASK-002, TASK-009 | §3.1 Calculations — CALC-002 |
| TASK-011 | `src/etl/resolve_stock_item_key.py` | `generate-etl` | TASK-003, TASK-009 | §3.1 Calculations — CALC-003 |
| TASK-012 | `src/etl/compute_ordered_quantity.py` | `generate-etl` | TASK-009 | §3.1 Calculations — CALC-001 |
| TASK-013 | `src/etl/assign_lineage_key.py` | `generate-etl` | TASK-004, TASK-005, TASK-009 | §3.1 Calculations — CALC-004; §5.1 Lineage Tracking |
| TASK-014 | `src/etl/merge_fact_purchase.py` | `generate-etl` | TASK-007, TASK-010, TASK-011, TASK-012, TASK-013 | §1.2/§3.1 |
| TASK-015 | `src/etl/advance_etl_cutoff.py` | `generate-etl` | TASK-006, TASK-014 | §5.3 Monitoring and Alerting |
| TASK-017 | `tests/test_qv001_row_count_reconciliation.py` | `generate-etl` | TASK-014 | §5.2 Validation Rules — QV-001 |
| TASK-018 | `tests/test_qv002_unknown_key_fallback_rate.py` | `generate-etl` | TASK-010, TASK-011 | §5.2 Validation Rules — QV-002 |
| TASK-019 | `tests/test_qv003_referential_conformity.py` | `generate-etl` | TASK-008, TASK-014 | §5.2 Validation Rules — QV-003 |
| TASK-020 | `config/purchase_pipeline_workflow.yml` | `generate-etl` | TASK-009, TASK-010, TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-017, TASK-018, TASK-019 | §5.3 Monitoring and Alerting |
| TASK-023 | `docs/data_dictionary.md`, `docs/consumer_guide.md` | `generate-etl` | TASK-007, TASK-016, TASK-022 | §1.2 Attributes; §4 Serving |

---

## 3. Sequencing Notes

Every `generate-etl` component in this plan traces back through its `Depends On` column to at least one `generate-db` component, because every design section under Ingestion, Transformation, Serving, and Observability references entity names first defined under Data Model. Phase 1 (`generate-db`) must therefore complete in full before Phase 2 (`generate-etl`) is dispatched. Within Phase 1, TASK-007 (`fact.purchase`) must follow TASK-002/TASK-003/TASK-004, and TASK-016/TASK-021 must follow TASK-007 — but all of Phase 1 still resolves to the single `generate-db` skill, so no cross-skill ordering is required inside the phase. Within Phase 2, the dependency chain TASK-009 → {TASK-010, TASK-011, TASK-012, TASK-013} → TASK-014 → {TASK-015, TASK-017, TASK-018, TASK-019} → TASK-020 governs execution order inside the ETL generation pass.

TASK-023 (`docs`) lists TASK-022 in its `Depends On` column, but TASK-022 is unmapped (see §4) — the data dictionary and consumer guide can be generated once TASK-007/TASK-016 are complete, but the consumer-access confirmation content within it cannot be finalized until TASK-022 is completed manually.

---

## 4. Unmapped Tasks

| Task ID | Type | Title | Reason |
|---|---|---|---|
| TASK-022 | BI | Validate cross-catalog consumer access to `fact.purchase` | `[CANNOT MAP: no BI-report/consumer-access-validation generation skill is deployed in this package — deployed SmartBuilder generation skills are limited to generate-db and generate-etl. This task requires manual execution of a representative query under the consumer role.]` |

---

## 5. Traceability

Every mapped component above traces to exactly one `tasks.md` Task ID and at least one `design.md` section. No component was invented outside of `tasks.md`'s 23 tasks. TASK-022 is the only task without a generating-skill mapping.
