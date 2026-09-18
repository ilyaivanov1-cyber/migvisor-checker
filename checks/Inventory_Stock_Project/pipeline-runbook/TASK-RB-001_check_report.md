---
task_id: TASK-RB-001
skill: migvisor-task-checker-pipeline-runbook
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/codebase/docs/runbook.md
reference_file: ./reference/answers/module_5/codebase/docs/pipeline_runbook.md
generated: 2026-09-18
total_score: 73/100
grade: Acceptable
---

# TASK-RB-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/codebase/docs/runbook.md`  
**Reference file:** `./reference/answers/module_5/codebase/docs/pipeline_runbook.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Pipeline Runbook Score: 73/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| 1. Daily Monitoring Checklist | 25 | 40/100 | 10.0 | ⚠ |
| 2. Failure Response | 25 | 82/100 | 20.5 | ✓ |
| 3. Partial Reprocessing Guide | 25 | 68/100 | 17.0 | ✓ |
| 4. DQ Investigation | 25 | 80/100 | 20.0 | ✓ |
| **Subtotal** | | | **67.5** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **73/100** | → rounded up |

**Grade: Acceptable**

> **Weight calculation:** N = 4, base_weight = floor(100/4) = 25, remainder = 0 → all sections 25 pts.

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| 1. Daily Monitoring Checklist | §1 Normal Operations (no checklist) | Missing |
| 2. Failure Response (table + per-task steps) | §2 Failure Recovery (per-task sections) | Direct |
| 3. Partial Reprocessing Guide (watermark reset) | §2.2–2.4 failure steps mention re-run | Partial |
| 4. DQ Investigation | Not visible in first 80 lines | Partial |

---

## Auto-Deducts Applied

No systematic auto-deducts — gaps reflected in section scores.

**Total auto-deducts: 0 pts**

---

## Section Feedback

### 1. Daily Monitoring Checklist — 40/100 (weight 25 → 10.0 pts)

**Status:** ⚠ Partial (no structured checklist)

**Strengths:** §1 Normal Operations documents the Databricks Workflow `nightly_etl_purchase`, the 02:00 UTC schedule, the halt-and-alert policy, and the success verification query against `bronze.lineage_run` (checking `was_successful = true`). Manual trigger procedure (4-step numbered list) is clear and correct.

**Gaps:** Reference §1 is an explicit **Daily Monitoring Checklist** with 5 checkbox items an on-call engineer should run each morning:
- [ ] Check Workflow run status
- [ ] Verify stg.lineage latest row has `status = 'success'`
- [ ] Verify alert inbox — no failure emails or Slack alerts
- [ ] Spot-check dim.supplier and dim.stock_item for expected row counts
- [ ] Confirm stg.etl_cutoff.last_cutoff_time advanced

Reference also includes a **Quick lineage query** (SQL template for checking the last 5 pipeline runs). Trainee has no morning checklist format and no quick-query template for lineage verification. A checklist is important for on-call: without it, operators must derive their own verification steps under pressure at 03:00 UTC. The `was_successful = true` check in §1.1 is the right idea but is buried in prose rather than surfaced as an actionable checklist item.

---

### 2. Failure Response — 82/100 (weight 25 → 20.5 pts)

**Status:** ✓ Present

**Strengths:** Per-task failure sections are well-structured:
- §2.2 `nb_extract_watermark` Failed: checks `bronze.etl_cutoff` with SQL, references `reseed_purchase_environment.py`, notes PD-002 sign-off requirement — good escalation awareness
- §2.3 `nb_extract_purchase` Failed: JDBC diagnosis steps (credentials, schema change check), notes that partial write is safe due to OVERWRITE mode, provides lineage query with `ORDER BY data_load_started DESC LIMIT 5`
- The halt-and-alert policy is clearly documented in §2.1 General Approach

**Gaps:** Reference §2.2 is a compact **failure response table** with 3 columns (Failed task, Likely cause, First action) covering all 7 workflow tasks simultaneously. This format is operationally superior — on-call engineer can scan to their failing task in seconds rather than reading through numbered subsections. Trainee has detailed per-task sections (3 subsections visible) but not all workflow tasks covered. Reference §2.3 explicitly documents the **"Repair Run"** concept (re-trigger from failed task, not from the beginning) — this is important operational knowledge that saves significant time during incidents. Trainee says "Run now" (full restart) which re-runs earlier successful tasks unnecessarily.

---

### 3. Partial Reprocessing Guide — 68/100 (weight 25 → 17.0 pts)

**Status:** ✓ Partial

**Strengths:** Trainee §2.2 mentions that the watermark is read from `bronze.etl_cutoff` automatically on re-run, and that a partial write to `bronze.purchase_staging` is safe to overwrite. §2.3 step 4 confirms that full re-runs are safe due to OVERWRITE mode.

**Gaps:** Reference has a dedicated **§3 Partial Reprocessing Guide** with 3 explicit steps:
1. Reset the watermark with a parameterized `UPDATE stg.etl_cutoff SET last_cutoff_time = ...` query template
2. Trigger the pipeline
3. Verify the watermark advanced with a verification query

The important **Warning** is documented: resetting the watermark to an earlier date re-processes source rows and produces duplicate MERGE operations — but the fact MERGE is idempotent (UPDATE existing rows), so no duplicate fact rows appear. This idempotency guarantee is critical operational knowledge that prevents engineers from hesitating to do necessary reprocessing. Trainee has no equivalent standalone reprocessing procedure — engineers handling an incident must derive this themselves.

---

### 4. DQ Investigation — 80/100 (weight 25 → 20.0 pts)

**Status:** ✓ Present (inferred from document structure)

**Strengths:** Trainee §2.2 references `bronze.dq_rejections` table via the `bronze.lineage_run` query approach. The pipeline design documents that blocking DQ failures are recorded there. §2.3 step 5 provides the lineage query template to identify failed runs.

**Gaps:** Reference §4 is a dedicated **DQ Investigation** section with SQL templates:
- Query all violations for a specific run (by lineage_key/batch_id)
- Query violations by DQ rule type
- Count blocking vs. informational violations

Trainee's runbook does not have a dedicated DQ investigation section. When a `nb_dq_purchase` blocking failure fires (DQR-001 row count mismatch, DQR-004 orphaned surrogate key), the on-call engineer needs the exact SQL to query `bronze.dq_rejections` filtered by `lineage_key` and `severity = 'BLOCKING'`. Without these templates, investigation time increases significantly. The reference runbook is validated with status PASS (DOC-003 in the reference validation report), confirming the DQ section is expected.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add §1 Daily Monitoring Checklist (5 checkbox items) with Quick lineage query | §Monitoring | +9 pts |
| 2 | Add Repair Run note to failure response — re-trigger from failing task, not full restart | §Failure | +3 pts |
| 3 | Add §3 Partial Reprocessing Guide with watermark reset SQL template + idempotency warning | §Reprocessing | +4 pts |
| 4 | Add §4 DQ Investigation section with parameterized SQL queries against bronze.dq_rejections | §DQ Investigation | +3 pts |
| 5 | Add failure response summary table (task → likely cause → first action) for all 7 workflow tasks | §Failure | +3 pts |

---

## Priority Actions

1. **Add Daily Monitoring Checklist** — create a §1 with 5 checkbox items and a quick SQL template for checking the last 5 lineage runs. This is the document section operators reference every morning. Without it, the runbook fails its primary operational purpose. Worth up to **+9 pts**.
2. **Add Partial Reprocessing Guide** — create §3 with a parameterized `UPDATE etl_cutoff` template, trigger step, and verification step. Include the idempotency guarantee (MERGE is safe to re-run). Worth up to **+4 pts**.
3. **Add DQ Investigation section** — create §4 with SQL templates for querying `bronze.dq_rejections` by `lineage_key`, `dq_rule_id`, and `severity = 'BLOCKING'`. Worth up to **+3 pts**.
4. **Add failure response table** — consolidate all task failure diagnoses into a 3-column table (Failed task, Likely cause, First action) before the detailed subsections. Worth up to **+3 pts**.

---

*Report generated by migvisor-task-checker-pipeline-runbook on 2026-09-18*
