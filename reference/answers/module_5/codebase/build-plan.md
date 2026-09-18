# Build Plan: Purchase

**Product:** Purchase · **Project:** GlobalPurchase_Project
**Generated:** 2026-08-25
**Catalog:** globalpurchase · **Workspace:** migVisor_workspace/GlobalPurchase_Project/
**Tasks:** 61 tasks across 11 groups

---

## Overview

This build plan governs the SmartBuilder code-generation execution for the **Purchase** data product — a 4-layer medallion pipeline on Databricks Lakehouse with Unity Catalog. SmartBuilder will generate SQL DDL, Python ETL notebooks, configuration files, documentation, and test stubs organized across two skills:

- `/12_migvisor_smartbuilder_generate-db` generates all database-layer artifacts: Delta Lake table DDL and Unity Catalog GRANT statements (21 tasks: DB + GRANT groups).
- `/13_migvisor_smartbuilder_generate-etl` generates all remaining artifacts: Python modules, Databricks notebooks, configuration files, documentation, and test stubs (40 tasks: COMMON, ING, DIM, FACT, MART, DQ, CFG, DOC, TEST groups).

Tasks are organized into 8 sequential build phases. Within a phase, tasks belonging to different groups may be generated in parallel by invoking `/12` and `/13` concurrently. Execution of generated artifacts (running DDL, deploying workflows) follows the phase order but is outside SmartBuilder's scope — SmartBuilder only produces source files.

---

## Build Phases

### Phase 1 — Foundation (CFG + COMMON + DB)

**Rationale:** Unity Catalog setup must exist before table DDL can execute. Configuration, constants, and base table DDL have no cross-layer dependencies. All Phase 1 artifacts can be generated in parallel across `/12` and `/13`.

**Execution order for generated artifacts (runtime):** CFG-003 → CFG-001, CFG-002, CFG-005, CFG-006, CFG-011 → DB-001–DB-008 → COMMON-001, COMMON-002

| Task ID | Group | File | Skill |
|---|---|---|---|
| CFG-001 | CFG | config/cluster_config.yml | /13 |
| CFG-002 | CFG | config/workflow_nightly_etl_main.yml | /13 |
| CFG-003 | CFG | config/uc_setup.sql | /13 |
| CFG-005 | CFG | config/dq_assertions_purchase.yaml | /13 |
| CFG-006 | CFG | config/secrets_config.py | /13 |
| CFG-007 | CFG | config/secrets_setup.md | /13 |
| CFG-008 | CFG | config/secrets_rotation_runbook.md | /13 |
| CFG-009 | CFG | config/deploy_workflow.sh | /13 |
| CFG-010 | CFG | config/ci_cd_pipeline.yml | /13 |
| CFG-011 | CFG | config/monitoring_config.yml | /13 |
| COMMON-001 | COMMON | src/common/constants.py | /13 |
| COMMON-002 | COMMON | src/common/utils.py | /13 |
| DB-001 | DB | src/db/ddl/stg_purchase_staging.sql | /12 |
| DB-002 | DB | src/db/ddl/stg_etl_cutoff.sql | /12 |
| DB-003 | DB | src/db/ddl/stg_lineage.sql | /12 |
| DB-004 | DB | src/db/ddl/stg_dq_rejections.sql | /12 |
| DB-005 | DB | src/db/ddl/dim_supplier.sql | /12 |
| DB-006 | DB | src/db/ddl/dim_stock_item.sql | /12 |
| DB-007 | DB | src/db/ddl/dim_date_populate.sql | /12 |
| DB-008 | DB | src/db/ddl/fact_purchase.sql | /12 |

---

### Phase 2 — Access Control (GRANT + mart view DDL)

**Rationale:** GRANT statements reference tables created in Phase 1. Mart view DDL (DB-009, DB-010) depends on dim and fact tables (DB-005, DB-006, DB-008) and must have grants in place before BI access is valid. CFG-004 (audit script) and CFG-012 (BI guide) reference grants and mart objects.

| Task ID | Group | File | Skill |
|---|---|---|---|
| GRANT-001 | GRANT | src/db/grants/dim_supplier_grants.sql | /12 |
| GRANT-002 | GRANT | src/db/grants/dim_stock_item_grants.sql | /12 |
| GRANT-003 | GRANT | src/db/grants/fact_rls_policies.sql | /12 |
| GRANT-004 | GRANT | src/db/grants/mart_grants.sql | /12 |
| DB-009 | DB | src/db/ddl/mart/v_purchase_by_supplier.sql | /12 |
| DB-010 | DB | src/db/ddl/mart/v_purchase_per_stock_item.sql | /12 |
| CFG-004 | CFG | config/uc_permission_audit.sql | /13 |
| CFG-012 | CFG | config/bi_connections.md | /13 |

---

### Phase 3 — Ingestion + Shared ETL Helpers (ING + DIM-001 + FACT-001 + FACT-002)

**Rationale:** Ingestion notebooks depend on COMMON-001 and COMMON-002 (Phase 1). The reusable SCD-2 merge helper (DIM-001), surrogate key resolver (FACT-001), and fact MERGE helper (FACT-002) are pure library modules — they have no dependency on other ETL notebooks and must be available before dimension and fact notebooks can reference them.

| Task ID | Group | File | Skill |
|---|---|---|---|
| ING-001 | ING | src/etl/ingestion/nb_extract_watermark.py | /13 |
| ING-002 | ING | src/etl/ingestion/nb_extract_dimensions.py | /13 |
| ING-003 | ING | src/etl/ingestion/nb_extract_purchase.py | /13 |
| ING-004 | ING | src/etl/ingestion/nb_commit_watermark.py | /13 |
| DIM-001 | DIM | src/etl/dimensions/scd2_merge.py | /13 |
| FACT-001 | FACT | src/etl/facts/sk_resolver.py | /13 |
| FACT-002 | FACT | src/etl/facts/fact_merge.py | /13 |

---

### Phase 4 — Dimension ETL (DIM notebooks)

**Rationale:** Dimension load notebooks depend on ING-001 (lineage key task values), ING-002 (dimension temp views), and DIM-001 (scd2_merge helper). All four notebooks can be generated in parallel by `/13`.

| Task ID | Group | File | Skill |
|---|---|---|---|
| DIM-002 | DIM | src/etl/dimensions/nb_load_dim_supplier.py | /13 |
| DIM-003 | DIM | src/etl/dimensions/nb_load_dim_stock_item.py | /13 |
| DIM-004 | DIM | src/etl/dimensions/nb_populate_dim_date.py | /13 |
| DIM-005 | DIM | src/etl/dimensions/nb_orchestrate_dimensions.py | /13 |

---

### Phase 5 — Fact ETL (FACT notebooks)

**Rationale:** Fact load notebooks depend on FACT-001 (sk_resolver), FACT-002 (fact_merge), and DIM-005 (dimension orchestrator, for sentinel row validation). FACT-003 and FACT-004 can be generated in parallel.

| Task ID | Group | File | Skill |
|---|---|---|---|
| FACT-003 | FACT | src/etl/facts/nb_load_fact_purchase.py | /13 |
| FACT-004 | FACT | src/etl/facts/nb_orchestrate_facts.py | /13 |

---

### Phase 6 — Data Quality (DQ)

**Rationale:** DQ engine and notebooks depend on FACT-003 (fact data available), DB-004 (dq_rejections table), and CFG-005 (DQ assertions config). DQ-001 must be generated before DQ-002 through DQ-005 which import it.

| Task ID | Group | File | Skill |
|---|---|---|---|
| DQ-001 | DQ | src/etl/dq/dq_engine.py | /13 |
| DQ-002 | DQ | src/etl/dq/nb_dq_purchase.py | /13 |
| DQ-003 | DQ | src/etl/dq/nb_dq_rejection_report.py | /13 |
| DQ-004 | DQ | src/etl/dq/nb_dq_smoke_tests.py | /13 |
| DQ-005 | DQ | src/etl/security/nb_pii_compliance_check.py | /13 |

---

### Phase 7 — Mart (MART notebooks)

**Rationale:** Mart notebooks depend on DQ-002 (dq_passed gate) and mart view DDL (DB-009, DB-010 from Phase 2). MART-001 and MART-002 can be generated in parallel; MART-003 and MART-004 follow them. MART-005 is a standalone SQL query library.

| Task ID | Group | File | Skill |
|---|---|---|---|
| MART-001 | MART | src/etl/mart/nb_refresh_v_purchase_by_supplier.py | /13 |
| MART-002 | MART | src/etl/mart/nb_refresh_v_purchase_per_stock_item.py | /13 |
| MART-003 | MART | src/etl/mart/nb_optimize_mart.py | /13 |
| MART-004 | MART | src/etl/mart/nb_validate_mart_views.py | /13 |
| MART-005 | MART | src/db/queries/bi_sample_queries.sql | /13 |

---

### Phase 8 — Documentation and Tests (DOC + TEST)

**Rationale:** Documentation and test stubs have no code dependencies — they reference specs rather than generated artifacts. All DOC and TEST tasks can be generated in parallel. TEST-001 (pytest.ini) can be generated as early as Phase 1 but is grouped here to consolidate test scaffolding.

| Task ID | Group | File | Skill |
|---|---|---|---|
| DOC-001 | DOC | docs/architecture_diagram.md | /13 |
| DOC-002 | DOC | docs/data_dictionary.md | /13 |
| DOC-003 | DOC | docs/pipeline_runbook.md | /13 |
| DOC-004 | DOC | docs/go_live_checklist.md | /13 |
| TEST-001 | TEST | config/pytest.ini | /13 |
| TEST-002 | TEST | tests/unit/test_scd2_merge.py | /13 |
| TEST-003 | TEST | tests/unit/test_sk_resolver.py | /13 |
| TEST-004 | TEST | tests/unit/test_fact_merge.py | /13 |
| TEST-005 | TEST | tests/unit/test_dq_engine.py | /13 |
| TEST-006 | TEST | tests/integration/test_pipeline_e2e.py | /13 |

---

## Task-to-Skill Mapping

| Task ID | Group | File | SmartBuilder Skill |
|---|---|---|---|
| DB-001 | DB | src/db/ddl/stg_purchase_staging.sql | /12_migvisor_smartbuilder_generate-db |
| DB-002 | DB | src/db/ddl/stg_etl_cutoff.sql | /12_migvisor_smartbuilder_generate-db |
| DB-003 | DB | src/db/ddl/stg_lineage.sql | /12_migvisor_smartbuilder_generate-db |
| DB-004 | DB | src/db/ddl/stg_dq_rejections.sql | /12_migvisor_smartbuilder_generate-db |
| DB-005 | DB | src/db/ddl/dim_supplier.sql | /12_migvisor_smartbuilder_generate-db |
| DB-006 | DB | src/db/ddl/dim_stock_item.sql | /12_migvisor_smartbuilder_generate-db |
| DB-007 | DB | src/db/ddl/dim_date_populate.sql | /12_migvisor_smartbuilder_generate-db |
| DB-008 | DB | src/db/ddl/fact_purchase.sql | /12_migvisor_smartbuilder_generate-db |
| DB-009 | DB | src/db/ddl/mart/v_purchase_by_supplier.sql | /12_migvisor_smartbuilder_generate-db |
| DB-010 | DB | src/db/ddl/mart/v_purchase_per_stock_item.sql | /12_migvisor_smartbuilder_generate-db |
| GRANT-001 | GRANT | src/db/grants/dim_supplier_grants.sql | /12_migvisor_smartbuilder_generate-db |
| GRANT-002 | GRANT | src/db/grants/dim_stock_item_grants.sql | /12_migvisor_smartbuilder_generate-db |
| GRANT-003 | GRANT | src/db/grants/fact_rls_policies.sql | /12_migvisor_smartbuilder_generate-db |
| GRANT-004 | GRANT | src/db/grants/mart_grants.sql | /12_migvisor_smartbuilder_generate-db |
| COMMON-001 | COMMON | src/common/constants.py | /13_migvisor_smartbuilder_generate-etl |
| COMMON-002 | COMMON | src/common/utils.py | /13_migvisor_smartbuilder_generate-etl |
| ING-001 | ING | src/etl/ingestion/nb_extract_watermark.py | /13_migvisor_smartbuilder_generate-etl |
| ING-002 | ING | src/etl/ingestion/nb_extract_dimensions.py | /13_migvisor_smartbuilder_generate-etl |
| ING-003 | ING | src/etl/ingestion/nb_extract_purchase.py | /13_migvisor_smartbuilder_generate-etl |
| ING-004 | ING | src/etl/ingestion/nb_commit_watermark.py | /13_migvisor_smartbuilder_generate-etl |
| DIM-001 | DIM | src/etl/dimensions/scd2_merge.py | /13_migvisor_smartbuilder_generate-etl |
| DIM-002 | DIM | src/etl/dimensions/nb_load_dim_supplier.py | /13_migvisor_smartbuilder_generate-etl |
| DIM-003 | DIM | src/etl/dimensions/nb_load_dim_stock_item.py | /13_migvisor_smartbuilder_generate-etl |
| DIM-004 | DIM | src/etl/dimensions/nb_populate_dim_date.py | /13_migvisor_smartbuilder_generate-etl |
| DIM-005 | DIM | src/etl/dimensions/nb_orchestrate_dimensions.py | /13_migvisor_smartbuilder_generate-etl |
| FACT-001 | FACT | src/etl/facts/sk_resolver.py | /13_migvisor_smartbuilder_generate-etl |
| FACT-002 | FACT | src/etl/facts/fact_merge.py | /13_migvisor_smartbuilder_generate-etl |
| FACT-003 | FACT | src/etl/facts/nb_load_fact_purchase.py | /13_migvisor_smartbuilder_generate-etl |
| FACT-004 | FACT | src/etl/facts/nb_orchestrate_facts.py | /13_migvisor_smartbuilder_generate-etl |
| MART-001 | MART | src/etl/mart/nb_refresh_v_purchase_by_supplier.py | /13_migvisor_smartbuilder_generate-etl |
| MART-002 | MART | src/etl/mart/nb_refresh_v_purchase_per_stock_item.py | /13_migvisor_smartbuilder_generate-etl |
| MART-003 | MART | src/etl/mart/nb_optimize_mart.py | /13_migvisor_smartbuilder_generate-etl |
| MART-004 | MART | src/etl/mart/nb_validate_mart_views.py | /13_migvisor_smartbuilder_generate-etl |
| MART-005 | MART | src/db/queries/bi_sample_queries.sql | /13_migvisor_smartbuilder_generate-etl |
| DQ-001 | DQ | src/etl/dq/dq_engine.py | /13_migvisor_smartbuilder_generate-etl |
| DQ-002 | DQ | src/etl/dq/nb_dq_purchase.py | /13_migvisor_smartbuilder_generate-etl |
| DQ-003 | DQ | src/etl/dq/nb_dq_rejection_report.py | /13_migvisor_smartbuilder_generate-etl |
| DQ-004 | DQ | src/etl/dq/nb_dq_smoke_tests.py | /13_migvisor_smartbuilder_generate-etl |
| DQ-005 | DQ | src/etl/security/nb_pii_compliance_check.py | /13_migvisor_smartbuilder_generate-etl |
| CFG-001 | CFG | config/cluster_config.yml | /13_migvisor_smartbuilder_generate-etl |
| CFG-002 | CFG | config/workflow_nightly_etl_main.yml | /13_migvisor_smartbuilder_generate-etl |
| CFG-003 | CFG | config/uc_setup.sql | /13_migvisor_smartbuilder_generate-etl |
| CFG-004 | CFG | config/uc_permission_audit.sql | /13_migvisor_smartbuilder_generate-etl |
| CFG-005 | CFG | config/dq_assertions_purchase.yaml | /13_migvisor_smartbuilder_generate-etl |
| CFG-006 | CFG | config/secrets_config.py | /13_migvisor_smartbuilder_generate-etl |
| CFG-007 | CFG | config/secrets_setup.md | /13_migvisor_smartbuilder_generate-etl |
| CFG-008 | CFG | config/secrets_rotation_runbook.md | /13_migvisor_smartbuilder_generate-etl |
| CFG-009 | CFG | config/deploy_workflow.sh | /13_migvisor_smartbuilder_generate-etl |
| CFG-010 | CFG | config/ci_cd_pipeline.yml | /13_migvisor_smartbuilder_generate-etl |
| CFG-011 | CFG | config/monitoring_config.yml | /13_migvisor_smartbuilder_generate-etl |
| CFG-012 | CFG | config/bi_connections.md | /13_migvisor_smartbuilder_generate-etl |
| DOC-001 | DOC | docs/architecture_diagram.md | /13_migvisor_smartbuilder_generate-etl |
| DOC-002 | DOC | docs/data_dictionary.md | /13_migvisor_smartbuilder_generate-etl |
| DOC-003 | DOC | docs/pipeline_runbook.md | /13_migvisor_smartbuilder_generate-etl |
| DOC-004 | DOC | docs/go_live_checklist.md | /13_migvisor_smartbuilder_generate-etl |
| TEST-001 | TEST | config/pytest.ini | /13_migvisor_smartbuilder_generate-etl |
| TEST-002 | TEST | tests/unit/test_scd2_merge.py | /13_migvisor_smartbuilder_generate-etl |
| TEST-003 | TEST | tests/unit/test_sk_resolver.py | /13_migvisor_smartbuilder_generate-etl |
| TEST-004 | TEST | tests/unit/test_fact_merge.py | /13_migvisor_smartbuilder_generate-etl |
| TEST-005 | TEST | tests/unit/test_dq_engine.py | /13_migvisor_smartbuilder_generate-etl |
| TEST-006 | TEST | tests/integration/test_pipeline_e2e.py | /13_migvisor_smartbuilder_generate-etl |

---

## Execution Instructions

### Prerequisites

Before invoking SmartBuilder skills, confirm:
1. `tasks.md` exists at `migVisor_workspace/GlobalPurchase_Project/products/Purchase/current/specifications/development_plan/tasks.md`
2. `design.md` exists at the same path (alongside `tasks.md`)
3. The `codebase/` directory exists at `migVisor_workspace/GlobalPurchase_Project/products/Purchase/current/codebase/`

### Using `/12_migvisor_smartbuilder_generate-db` (DB + GRANT tasks)

Invoke `/12` once per task ID. Run Phase 1 DB tasks first, then Phase 2 GRANT and mart view DDL tasks.

**Phase 1 — DB tables (invoke in any order; all can run concurrently):**
```
/12_migvisor_smartbuilder_generate-db DB-001
/12_migvisor_smartbuilder_generate-db DB-002
/12_migvisor_smartbuilder_generate-db DB-003
/12_migvisor_smartbuilder_generate-db DB-004
/12_migvisor_smartbuilder_generate-db DB-005
/12_migvisor_smartbuilder_generate-db DB-006
/12_migvisor_smartbuilder_generate-db DB-007
/12_migvisor_smartbuilder_generate-db DB-008
```

**Phase 2 — GRANTs and mart views (after Phase 1 DB tasks complete):**
```
/12_migvisor_smartbuilder_generate-db GRANT-001
/12_migvisor_smartbuilder_generate-db GRANT-002
/12_migvisor_smartbuilder_generate-db GRANT-003
/12_migvisor_smartbuilder_generate-db GRANT-004
/12_migvisor_smartbuilder_generate-db DB-009
/12_migvisor_smartbuilder_generate-db DB-010
```

### Using `/13_migvisor_smartbuilder_generate-etl` (all other tasks)

Invoke `/13` once per task ID following the phase sequence below. Within a phase, tasks with no mutual dependencies can be invoked concurrently.

**Phase 1 — CFG foundation and COMMON (invoke concurrently):**
```
/13_migvisor_smartbuilder_generate-etl CFG-001
/13_migvisor_smartbuilder_generate-etl CFG-002
/13_migvisor_smartbuilder_generate-etl CFG-003
/13_migvisor_smartbuilder_generate-etl CFG-005
/13_migvisor_smartbuilder_generate-etl CFG-006
/13_migvisor_smartbuilder_generate-etl CFG-007
/13_migvisor_smartbuilder_generate-etl CFG-008
/13_migvisor_smartbuilder_generate-etl CFG-009
/13_migvisor_smartbuilder_generate-etl CFG-010
/13_migvisor_smartbuilder_generate-etl CFG-011
/13_migvisor_smartbuilder_generate-etl COMMON-001
/13_migvisor_smartbuilder_generate-etl COMMON-002
```

**Phase 2 — Access control config (after GRANT tasks complete):**
```
/13_migvisor_smartbuilder_generate-etl CFG-004
/13_migvisor_smartbuilder_generate-etl CFG-012
```

**Phase 3 — Ingestion + shared ETL helpers (invoke concurrently):**
```
/13_migvisor_smartbuilder_generate-etl ING-001
/13_migvisor_smartbuilder_generate-etl ING-002
/13_migvisor_smartbuilder_generate-etl ING-003
/13_migvisor_smartbuilder_generate-etl ING-004
/13_migvisor_smartbuilder_generate-etl DIM-001
/13_migvisor_smartbuilder_generate-etl FACT-001
/13_migvisor_smartbuilder_generate-etl FACT-002
```

**Phase 4 — Dimension ETL notebooks (invoke concurrently):**
```
/13_migvisor_smartbuilder_generate-etl DIM-002
/13_migvisor_smartbuilder_generate-etl DIM-003
/13_migvisor_smartbuilder_generate-etl DIM-004
/13_migvisor_smartbuilder_generate-etl DIM-005
```

**Phase 5 — Fact ETL notebooks (invoke concurrently):**
```
/13_migvisor_smartbuilder_generate-etl FACT-003
/13_migvisor_smartbuilder_generate-etl FACT-004
```

**Phase 6 — DQ layer (DQ-001 first, then remaining concurrently):**
```
/13_migvisor_smartbuilder_generate-etl DQ-001
# then:
/13_migvisor_smartbuilder_generate-etl DQ-002
/13_migvisor_smartbuilder_generate-etl DQ-003
/13_migvisor_smartbuilder_generate-etl DQ-004
/13_migvisor_smartbuilder_generate-etl DQ-005
```

**Phase 7 — Mart layer (MART-001/MART-002 first, then MART-003/MART-004 concurrently):**
```
/13_migvisor_smartbuilder_generate-etl MART-001
/13_migvisor_smartbuilder_generate-etl MART-002
# then:
/13_migvisor_smartbuilder_generate-etl MART-003
/13_migvisor_smartbuilder_generate-etl MART-004
/13_migvisor_smartbuilder_generate-etl MART-005
```

**Phase 8 — Documentation and tests (invoke concurrently; no dependencies):**
```
/13_migvisor_smartbuilder_generate-etl DOC-001
/13_migvisor_smartbuilder_generate-etl DOC-002
/13_migvisor_smartbuilder_generate-etl DOC-003
/13_migvisor_smartbuilder_generate-etl DOC-004
/13_migvisor_smartbuilder_generate-etl TEST-001
/13_migvisor_smartbuilder_generate-etl TEST-002
/13_migvisor_smartbuilder_generate-etl TEST-003
/13_migvisor_smartbuilder_generate-etl TEST-004
/13_migvisor_smartbuilder_generate-etl TEST-005
/13_migvisor_smartbuilder_generate-etl TEST-006
```

### Validation

After all tasks complete, run `/14_migvisor_smartbuilder_validation` to validate all generated artifacts against `tasks.md` and `design.md`.

---

## Dependencies Graph

The graph below shows the key dependency chains. Nodes in the same column can be generated concurrently. Arrows indicate "must be generated before" for code correctness (import paths, table references).

```
Phase 1 (no dependencies)
────────────────────────────────────────────────────────────────────
CFG-001   CFG-002   CFG-003   CFG-005   CFG-006   CFG-007   CFG-008
CFG-009   CFG-010   CFG-011   COMMON-001   COMMON-002
DB-001    DB-002    DB-003    DB-004    DB-005    DB-006    DB-007
DB-008

Phase 2 (depends on Phase 1 DB + CFG-003)
────────────────────────────────────────────────────────────────────
GRANT-001 (← DB-005, CFG-003)
GRANT-002 (← DB-006, CFG-003)
GRANT-003 (← DB-008, CFG-003)
GRANT-004 (← DB-009, DB-010, CFG-003)
DB-009    (← DB-005, DB-006, DB-008)
DB-010    (← DB-005, DB-006, DB-008)
CFG-004   (← CFG-003, GRANT-001, GRANT-002, GRANT-003, GRANT-004)
CFG-012   (← DB-009, DB-010, GRANT-004)

Phase 3 (depends on COMMON-001, COMMON-002, Phase 2 DB/GRANTs)
────────────────────────────────────────────────────────────────────
ING-001   (← COMMON-001, COMMON-002, DB-002, DB-003)
ING-002   (← COMMON-001, COMMON-002, CFG-001)
ING-003   (← COMMON-001, COMMON-002, ING-001, DB-001, DB-003)
ING-004   (← COMMON-001, COMMON-002, ING-001, DB-002, DB-003)
DIM-001   (← COMMON-001, COMMON-002)
FACT-001  (← COMMON-001, COMMON-002, DB-005, DB-006)
FACT-002  (← COMMON-001, COMMON-002, DB-008)

Phase 4 (depends on DIM-001, ING-001, ING-002, Phase 1 DB tables)
────────────────────────────────────────────────────────────────────
DIM-002   (← COMMON-001, COMMON-002, DIM-001, ING-001, ING-002, DB-005)
DIM-003   (← COMMON-001, COMMON-002, DIM-001, ING-001, ING-002, DB-006)
DIM-004   (← COMMON-001, COMMON-002, DB-007)
DIM-005   (← COMMON-001, COMMON-002, DIM-002, DIM-003, DIM-004, ING-001)

Phase 5 (depends on FACT-001, FACT-002, DIM-005)
────────────────────────────────────────────────────────────────────
FACT-003  (← COMMON-001, COMMON-002, FACT-001, FACT-002, ING-001, DB-003, DB-008)
FACT-004  (← COMMON-001, COMMON-002, FACT-003, DIM-005)

Phase 6 (depends on FACT-003, DB-004, CFG-005)
────────────────────────────────────────────────────────────────────
DQ-001    (← COMMON-001, COMMON-002, DB-004, DB-008)
DQ-002    (← COMMON-001, COMMON-002, DQ-001, CFG-005, FACT-003)
DQ-003    (← COMMON-001, COMMON-002, DQ-002, DB-004)
DQ-004    (← COMMON-001, COMMON-002, DB-003, DB-004, DB-007, ING-001)
DQ-005    (← COMMON-001, COMMON-002, CFG-006)

Phase 7 (depends on DQ-002, DB-009, DB-010, GRANT-004)
────────────────────────────────────────────────────────────────────
MART-001  (← COMMON-001, COMMON-002, DB-009, GRANT-004, DQ-002)
MART-002  (← COMMON-001, COMMON-002, DB-010, GRANT-004, DQ-002)
MART-003  (← COMMON-001, COMMON-002, MART-001, MART-002)
MART-004  (← COMMON-001, COMMON-002, MART-001, MART-002, DB-008)
MART-005  (← DB-009, DB-010, GRANT-004)

Phase 8 (no code dependencies — spec-driven)
────────────────────────────────────────────────────────────────────
DOC-001   DOC-002   DOC-003   DOC-004
TEST-001  TEST-002  TEST-003  TEST-004  TEST-005  TEST-006

Cross-layer lineage_key propagation (runtime, not code-gen order):
ING-001 (writes lineage record)
  → ING-003 (reads lineage_key task value)
  → FACT-003 (reads lineage_key, updates stg.lineage.rows_loaded)
  → ING-004 (closes lineage record, advances watermark)

DAG execution order (nightly Workflow runtime):
ING-001 → ING-002 → ING-003
  → DIM-005 (DIM-002, DIM-003, DIM-004 within)
    → FACT-004 (FACT-003 within)
      → DQ-004 → DQ-002 → DQ-003
        → MART-001 → MART-002 → MART-003 → MART-004
          → ING-004 (watermark commit — final task)
```

---

*Generated by migVisor SmartBuilder plan-agent · 2026-08-25*
