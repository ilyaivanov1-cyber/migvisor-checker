# Purchases — SmartBuilder Validation Report

| Field | Value |
|---|---|
| Product | Purchases |
| Project | Purchasing_Project |
| Validation date | 2026-09-23 |
| SDD version validated against | 4.1 (per `project/current/catalog.yaml` `schemaVersion` and `products/Purchases/current/_manifest.yaml` `sb.sddVersion`) |
| Artifacts in `sb.generated` | 24 (build-plan.md + 10 DDL + 7 ETL + 3 test + 1 config + 2 docs) |

> Note: the validation brief described the `sb.generated` list as "23 files"; the manifest's actual list (and the files present on disk) total **24** entries, all accounted for below.

---

## Results

| # | Artifact path | Status | Gaps |
|---|---|---|---|
| 1 | `products/Purchases/current/codebase/build-plan.md` | pass | none — task→deliverable→design-section mapping matches tasks.md and design.md exactly; correctly identifies TASK-022 as unmapped and TASK-016/TASK-021 as not-yet-generated. |
| 2 | `products/Purchases/current/codebase/src/db/ddl/stg_purchase_staging.sql` | pass | none — columns/types/nullability match design.md §1.2 exactly; no partitioning/clustering per §1.4; idempotent `CREATE TABLE IF NOT EXISTS`. |
| 3 | `products/Purchases/current/codebase/src/db/ddl/dim_supplier.sql` | pass | none — columns match design.md §1.2; `CLUSTER BY (wwi_supplier_id, valid_from)` matches §1.4; Unknown row (key=0, far-future window) seeded per TASK-002 acceptance criteria. |
| 4 | `products/Purchases/current/codebase/src/db/ddl/dim_stock_item_access.sql` | pass | none — column set matches design.md §1.2 `dim.stock_item`; carries the required inline `[PENDING: PL-008/OB-002]` marker; Unknown row seeded. |
| 5 | `products/Purchases/current/codebase/src/db/ddl/dim_date_access.sql` | pass | none — 2-column set (`date_key`, `date_value`) matches design.md §1.2 `dim.date`; carries the required `[PENDING: PL-008/OB-002]` marker. |
| 6 | `products/Purchases/current/codebase/src/db/ddl/meta_lineage.sql` | pass | none — columns match design.md §1.2 `meta.lineage`; `status` constrained via CHECK to RUNNING/SUCCESS/FAILED. |
| 7 | `products/Purchases/current/codebase/src/db/ddl/meta_sequence_state.sql` | pass | none — matches CALC-004's counter-table description; single seed row (`lineage_key`, 0). |
| 8 | `products/Purchases/current/codebase/src/db/ddl/meta_etl_cutoff.sql` | pass | none — matches design.md §1.2 `meta.etl_cutoff`; seeded with `purchase_staging` watermark row. |
| 9 | `products/Purchases/current/codebase/src/db/ddl/meta_v_etl_cutoff.sql` | pass | none — `SELECT * FROM purchasing.meta.etl_cutoff` matches design.md's reporting-view description. |
| 10 | `products/Purchases/current/codebase/src/db/ddl/fact_purchase.sql` | pass | none — 9 columns match design.md §1.2 `fact.purchase` exactly; `ordered_quantity` is a plain stored BIGINT with no `GENERATED ALWAYS AS` clause (correct per FR-004/CX-P01 override); partitioned by `date_key`; Z-ORDER via separate `OPTIMIZE` statement; CDF enabled. |
| 11 | `products/Purchases/current/codebase/src/db/ddl/stg_dq_rejections.sql` | pass | none — 7 columns match design.md §1.2 `stg.dq_rejections` exactly. |
| 12 | `products/Purchases/current/codebase/src/etl/extract_purchase_staging.py` | pass | Minor: the source query reads from a generic placeholder table `source.purchase_order_lines`, which does not correspond to any object named in `catalog.yaml`'s `sourceLineage`/`sourceIntegration` (e.g. `integration.purchase_staging`, `wideworldimporters.purchasing.purchaseorderlines`). Business logic (watermark filter FLT-001, `begin_batch()` called at extraction start to satisfy the NOT NULL `lineage_key`) is correct and matches the documented intentional resolution. |
| 13 | `products/Purchases/current/codebase/src/etl/resolve_supplier_key.py` | pass | Join formula matches CALC-002/FR-002 exactly (`>= valid_from AND < valid_to`, fallback to 0). Gap: produces `stg_with_supplier_key` as a Spark session-scoped temp view — see orchestration gap under item 22 (`purchase_pipeline_workflow.yml`). |
| 14 | `products/Purchases/current/codebase/src/etl/resolve_stock_item_key.py` | pass | Join formula matches CALC-003/FR-003 exactly. Same temp-view continuity gap as item 13 — consumes `stg_with_supplier_key` and produces `stg_with_keys`. |
| 15 | `products/Purchases/current/codebase/src/etl/compute_ordered_quantity.py` | pass | Formula `ordered_outers * quantity_per_outer` matches CALC-001/FR-004 exactly, computed in code (not a generated column), consistent with CX-P01. Same temp-view continuity gap as items 13–14 — consumes `stg_with_keys`, produces `stg_resolved`. |
| 16 | `products/Purchases/current/codebase/src/etl/assign_lineage_key.py` | **fail** | `begin_batch()`/`end_batch()` are each individually correct (atomic counter increment, RUNNING→SUCCESS/FAILED transition, matches CALC-004/§5.1/FR-005). However, the module's `__main__` entrypoint unconditionally calls `begin_batch()` and has **no logic that reads or dispatches on a `mode` parameter**. `end_batch()` is never invoked anywhere in the codebase. This means the orchestration config's `end_batch_lineage` task (which passes `base_parameters: mode: end_batch`, see item 22) cannot actually close the lineage record — as wired, it would just re-run `begin_batch()`, issuing a second `lineage_key`/RUNNING row instead of transitioning the batch's row to SUCCESS/FAILED. |
| 17 | `products/Purchases/current/codebase/src/etl/merge_fact_purchase.py` | pass | MERGE key (`wwi_purchase_order_id`), scoped `WHEN MATCHED/NOT MATCHED` semantics, and column list match FR-006 and fact_purchase.sql's 9 columns exactly. `date_key` derivation via `CAST(date_format(transaction_date,'yyyyMMdd') AS BIGINT)` matches the documented intentional resolution (no `stg.purchase_staging.date_key` column exists). Gap: consumes `stg_resolved`, the last link in the temp-view chain flagged under items 13–15 and 22. |
| 18 | `products/Purchases/current/codebase/src/etl/advance_etl_cutoff.py` | pass | none — updates `last_cutoff`/`updated_at` for `entity_name='purchase_staging'`; correctly documents (via docstring) that gating on TASK-014/QV-001 success is the orchestration's responsibility, consistent with FR-008 and TASK-020's design. |
| 19 | `products/Purchases/current/codebase/tests/test_qv001_row_count_reconciliation.py` | pass | none — distinct `wwi_purchase_order_id` count comparison between `stg.purchase_staging` and `fact.purchase` matches QV-001/NFR-004 exactly; raises a blocking exception on mismatch. |
| 20 | `products/Purchases/current/codebase/tests/test_qv002_unknown_key_fallback_rate.py` | pass | Fallback-rate formula (`supplier_key = 0 OR stock_item_key = 0`) matches QV-002/NFR-005; correctly non-blocking, correctly notes QA-002 threshold as pending (legitimate, matches known-pending items). Gap: reads from the same `stg_resolved` temp view flagged under items 13–15 and 22. |
| 21 | `products/Purchases/current/codebase/tests/test_qv003_referential_conformity.py` | pass | LEFT ANTI JOIN assertions against `dim.supplier`/`dim.stock_item`/`dim.date` and the `stg.dq_rejections` insert column list match QV-003/NFR-006 exactly. Minor: `assert_referential_conformity(spark, lineage_key)` requires a `lineage_key` argument, but `purchase_pipeline_workflow.yml`'s `qv003_referential_conformity` task supplies no `base_parameters` for it — the mechanism by which the running batch's `lineage_key` reaches this notebook at runtime is not specified anywhere in the codebase. |
| 22 | `products/Purchases/current/codebase/config/purchase_pipeline_workflow.yml` | **fail** | Two defects: (a) the `end_batch_lineage` task passes `base_parameters: mode: end_batch` to `assign_lineage_key.py`, but that script never reads any `mode` parameter (see item 16) — the close-out call has no effect as wired. (b) The job chain runs `extract_purchase_staging` → `resolve_supplier_key` → `resolve_stock_item_key` → `compute_ordered_quantity` → `merge_fact_purchase` as **separate `notebook_task` steps**, yet the ETL scripts for these steps (items 13–15, 17) communicate exclusively via Spark session-scoped `createOrReplaceTempView` calls (`stg_with_supplier_key`, `stg_with_keys`, `stg_resolved`). Standard Databricks Workflows execution gives each job task its own notebook/session context, so a temp view created in one task is not visible to the next task — as configured, `resolve_supplier_key` onward would fail with "table or view not found." (c) related to item 21: no `base_parameters` supply `lineage_key` to the `qv003_referential_conformity` task. Dependency ordering itself (extraction → key resolution → calculations → MERGE → QV checks → watermark advance) otherwise correctly matches TASK-020's description and the QV-001-blocks-watermark-advance requirement. |
| 23 | `products/Purchases/current/codebase/docs/data_dictionary.md` | pass | none — covers every column of `fact.purchase`, `dim.supplier`, `dim.stock_item`, and `dim.date` per design.md §1.2, matching TASK-023's scope exactly (meta.* tables correctly excluded, per task description). |
| 24 | `products/Purchases/current/codebase/docs/consumer_guide.md` | pass | none — `[PENDING: ...]` markers for TASK-016 (access profile), TASK-021 (governance), and TASK-022 (consumer validation) are legitimate: none of these three tasks has been generated/executed yet (confirmed against `_manifest.yaml`'s `sb.tasks` list, which omits TASK-016/021/022 entirely, and `build-plan.md` §4 which marks TASK-022 unmapped). Consistent with the known-pending items for this validation run. |

---

## Summary

- **Artifacts validated:** 24
- **Passed:** 22
- **Failed:** 2

### Failed artifacts and gaps

1. **`src/etl/assign_lineage_key.py`** — the `end_batch()` function is correctly implemented but never invoked; the script's `__main__` entrypoint has no `mode`-parameter dispatch, so it cannot fulfil the orchestration's "close the lineage record at batch end" call.
2. **`config/purchase_pipeline_workflow.yml`** — (a) wires an `end_batch` mode to `assign_lineage_key.py` that the script cannot act on; (b) chains `resolve_supplier_key` → `resolve_stock_item_key` → `compute_ordered_quantity` → `merge_fact_purchase` as separate Databricks Workflow tasks even though they communicate only via same-session Spark temp views, which will not survive across separate task executions; (c) does not supply the `lineage_key` parameter required by the `qv003_referential_conformity` task's underlying function.

### Non-blocking notes on otherwise-passing artifacts

- `extract_purchase_staging.py` sources from a generic placeholder table name (`source.purchase_order_lines`) not tied to any object documented in `catalog.yaml`'s source lineage.
- `resolve_supplier_key.py`, `resolve_stock_item_key.py`, `compute_ordered_quantity.py`, `merge_fact_purchase.py`, and `test_qv002_unknown_key_fallback_rate.py` are each individually correct against design.md/requirements.md, but all sit downstream of the temp-view continuity gap flagged against `purchase_pipeline_workflow.yml`.
- `test_qv003_referential_conformity.py`'s function signature expects a `lineage_key` argument that the orchestration config does not supply.

All `[PENDING: ...]` / `[OWNER INPUT REQUIRED: ...]` markers found across the artifacts (PL-008/OB-002 in the two access-stub DDL files; PL-009/OB-008, QA-002, and TASK-016/021/022 in `consumer_guide.md` and `purchase_pipeline_workflow.yml`'s email notification list) correspond to genuinely unresolved upstream/owner decisions tracked in `catalog.yaml`'s `pendingDecisions` and are not shortcuts around resolvable work.
