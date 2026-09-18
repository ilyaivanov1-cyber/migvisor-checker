---
task_id: TASK-TA-001
skill: migvisor-task-checker-tasks
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/tasks.md
reference_file: ./reference/answers/module_5/development_plan/tasks.md
generated: 2026-09-18
total_score: 70/100
grade: Acceptable
---

# TASK-TA-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/tasks.md`  
**Reference file:** `./reference/answers/module_5/development_plan/tasks.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Tasks Score: 70/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Task Summary Table | 25 | 80/100 | 20.0 | ✓ |
| DDL Tasks (DB group) | 25 | 75/100 | 18.75 | ⚠ |
| ETL Tasks (ING/DIM/FACT groups) | 25 | 78/100 | 19.5 | ✓ |
| Config / CFG Tasks | 25 | 45/100 | 11.25 | ✗ |
| **Subtotal** | | | **69.5** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **70/100** | |

**Grade: Acceptable**

> **Weight calculation:** N = 4, base_weight = floor(100/4) = 25, remainder = 0 → all sections 25 pts.

---

## Section Matching Log

| Reference Group | Matched in Trainee | Match Type |
|---|---|---|
| DB (DDL tasks) | TASK-001–008 (8 DDL tasks) | Direct |
| GRANT (access tasks) | TASK-008 (GRANTs combined) | Partial |
| COMMON (shared modules) | TASK-009–013 | Direct |
| ING (ingestion notebooks) | TASK-014–015 | Direct |
| DIM (dimension ETL) | Not present — external responsibility | Missing |
| FACT (fact ETL) | TASK-016 (fact migrate + sk_resolver + fact_merge) | Direct |
| MART (serving layer) | Not present | Missing |
| DQ (DQ engine tasks) | Embedded in TASK-016 | Partial |
| CFG (config artifacts) | TASK-018–019 only | Partial |

---

## Auto-Deducts Applied

No systematic auto-deducts — gaps reflected in section scores.

**Total auto-deducts: 0 pts**

---

## Section Feedback

### Task Summary Table — 80/100 (weight 25 → 20.0 pts)

**Status:** ✓ Present

**Strengths:** 26 tasks with Task ID, Type, Title, Depends On, Requirements columns. Task dependency graph is clear — TASK-001/002 (control tables) before TASK-003 (staging), TASK-011/012 before TASK-016. Requirements traceability present for all tasks. Type column distinguishes DDL/ETL/Config/Test/BI/Docs.

**Gaps vs reference:** Reference has 50+ tasks across 9 groups (DB, GRANT, COMMON, ING, DIM, FACT, MART, DQ, CFG) — trainee has 26 across 6 types. Key missing groups: DIM (dimension ETL notebooks — 5 tasks), MART (serving layer — 5 tasks), DQ (DQ engine tasks — 5 tasks), partial CFG (10 tasks vs 2 in trainee). Reference task group structure is more granular and better reflects the DAG complexity. Trainee has Test tasks (TASK-020/021/022) that reference lacks — this is a value-add.

---

### DDL Tasks — 75/100 (weight 25 → 18.75 pts)

**Status:** ⚠ Partial

**Strengths:** TASK-001 through TASK-008 cover all required Delta tables: `bronze.lineage_run`, `bronze.etl_cutoff`, `bronze.purchase_staging`, `bronze.dq_rejections`, `silver_fact.fact_purchase`, `silver_dim.supplier_current` view, `silver_dim.stock_item_current` view, GRANT statements. Full DDL included in task descriptions (TASK-001 shown with complete `CREATE TABLE IF NOT EXISTS` with COMMENT strings, CDF enabled, TBLPROPERTIES).

**Gaps:** Reference has separate DDL tasks for `dim.supplier` and `dim.stock_item` tables themselves (DB-005, DB-006) plus `dim_date_populate.sql` (DB-007) and mart layer views (DB-009, DB-010). Trainee TASK-006/007 create only the `_current` views, not the underlying SCD-2 dimension tables (these are treated as externally owned but the DDL file should still be produced). Missing mart-layer DDL tasks entirely.

---

### ETL Tasks — 78/100 (weight 25 → 19.5 pts)

**Status:** ✓ Present

**Strengths:** Core ETL tasks well covered. TASK-009 (constants.py), TASK-010 (scd2_merge.py), TASK-011 (sk_resolver.py), TASK-012 (fact_merge.py), TASK-013 (udfs.py) cover the shared common module layer. TASK-014 (nb_extract_watermark), TASK-015 (nb_extract_purchase), TASK-016 (migrate_staged_purchase_data) cover ingestion and fact load. Test tasks TASK-020, 021, 022 cover sk_resolver, udfs, and migrate_staged_purchase_data — good TDD coverage.

**Gaps:** Reference has 5 separate dimension ETL tasks (DIM-001 through DIM-005): scd2_merge.py, nb_load_dim_supplier.py, nb_load_dim_stock_item.py, nb_populate_dim_date.py, nb_orchestrate_dimensions.py. Trainee has no DIM group tasks — dimension loading is treated as external but should at minimum reference interface tasks. Reference FACT group has 4 tasks (sk_resolver.py, fact_merge.py, nb_load_fact_purchase.py, nb_orchestrate_facts.py) — trainee collapses these into TASK-011/012/016.

---

### Config / CFG Tasks — 45/100 (weight 25 → 11.25 pts)

**Status:** ✗ Incomplete

**Strengths:** TASK-018 (config/environment.yaml) and TASK-019 (Databricks Workflow JSON) are present.

**Gaps:** Reference has 10 CFG tasks that are entirely absent or only partially covered in trainee:
- CFG-001: `config/cluster_config.yml` (Databricks cluster policy) — missing
- CFG-003: `config/uc_setup.sql` (Unity Catalog setup — CREATE CATALOG/SCHEMA) — missing
- CFG-004: `config/uc_permission_audit.sql` (audit query for grants) — missing
- CFG-005: `config/dq_assertions_purchase.yaml` (DQ assertion config) — missing
- CFG-006: `config/secrets_config.py` (Secrets bootstrap script) — missing
- CFG-007: `config/secrets_setup.md` (Secrets setup runbook) — missing
- CFG-008: `config/secrets_rotation_runbook.md` (credential rotation runbook) — missing
- CFG-009: `config/deploy_workflow.sh` (deployment script) — missing
- CFG-010: `config/ci_cd_pipeline.yml` (CI/CD pipeline definition) — missing

These config artifacts are critical for production deployment and security. The secrets and UC setup tasks are particularly important for the security review and go-live readiness.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add CFG tasks: uc_setup.sql, uc_permission_audit.sql, secrets_config.py, secrets_setup.md, secrets_rotation_runbook.md, deploy_workflow.sh, ci_cd_pipeline.yml | CFG | +12 pts |
| 2 | Add DIM group tasks: scd2_merge.py, nb_load_dim_supplier.py, nb_load_dim_stock_item.py, nb_populate_dim_date.py | DIM | +5 pts |
| 3 | Add MART group tasks: materialized view DDL and mart refresh notebooks | MART | +4 pts |
| 4 | Add DQ group tasks: dq_engine.py, nb_dq_purchase.py, nb_dq_rejection_report.py | DQ | +3 pts |

---

## Priority Actions

1. **Add CFG tasks** — create tasks for all 9 missing config artifacts. The secrets_config.py, uc_setup.sql, and ci_cd_pipeline.yml tasks are particularly important for security and deployment readiness. Worth up to **+12 pts**.
2. **Add DIM group tasks** — even if dimension ETL is externally owned, the DDL files for `silver_dim.supplier` and `silver_dim.stock_item` must be produced by the Purchase product team, and the interface contract (task dependency in Workflow) must be documented. Worth up to **+5 pts**.
3. **Add MART group tasks** — mart-layer materialized views and refresh notebooks complete the serving-layer architecture. Worth up to **+4 pts**.

---

*Report generated by migvisor-task-checker-tasks on 2026-09-18*
