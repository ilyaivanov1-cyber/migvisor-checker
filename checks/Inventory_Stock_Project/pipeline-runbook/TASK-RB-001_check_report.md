# Check Report: pipeline-runbook — Inventory_Stock_Project / Purchase

**Skill:** migvisor-task-checker-pipeline-runbook (#12 of 21)
**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Checked:** 2026-09-25
**Score:** 72 / 100
**Grade:** Acceptable

---

## Cross-File Reads

| File | Status | Notes |
|---|---|---|
| `codebase/docs/data-dictionary.md` | Read | dq_rejections columns: rule_id, violation_column, violation_value, rejection_reason, detected_at, assertion_name NOT a defined column |

---

## Rubric Sections (7-section adaptive rubric)

Base weight = floor(100/7) = 14; two highest-complexity sections receive +1 each (15 pts).

### Section 1 — Daily Monitoring Checklist (15 pts)

**Score: 14 / 15**

Six-item morning checklist covering: Databricks Workflow status, lineage_run.was_successful, alert inbox, dimension spot-checks, etl_cutoff advancement, fact row count. Two quick SQL queries are provided (lineage query and watermark check).

The checklist is thorough and operationally actionable. The quick lineage query uses three-part catalog names (`inventory_stock.bronze.lineage_run`).

Deduction (-1): The checklist does not specify a target completion time or an escalation threshold (e.g., "if job not succeeded by 06:00 UTC, escalate"). The reference's checklist implicitly assumes ~03:00 UTC completion; the trainee states the same but doesn't link the check to a business SLA consequence.

### Section 2 — Failure Recovery (15 pts)

**Score: 14 / 15**

The failure recovery section is the strongest in the document. Four task-specific failure sections cover every task in the `nightly_etl_purchase` workflow:
- `nb_extract_watermark` Failed (Section 2.2): checks etl_cutoff existence, reseed reference, SQL verification query
- `nb_extract_purchase` Failed (Section 2.3): JDBC diagnosis, schema change check, staging overwrite safety note, lineage_run check, re-run instruction
- `migrate_staged_purchase_data` Failed — QA-P001 (Section 2.4): staging count comparison against lineage_run, root-cause splits (zero rows vs duplicate rows)
- `migrate_staged_purchase_data` Failed — Other Errors (Section 2.5): dq_rejections query, RI check for dimension freshness, repair run instruction

This level of per-task recovery specificity matches or exceeds the reference's diagnostic table.

Deduction (-1): Section 2.5 DQ investigation query uses `assertion_name` as the GROUP BY column, but the data-dictionary.md defines `rule_id` as the column name in `bronze.dq_rejections` — `assertion_name` is not a defined column. This is an internal inconsistency. Section 5 correctly uses `rule_id`. The inconsistency indicates the Section 2.5 query was not updated after the column name was finalized.

### Section 3 — Reprocessing Guide (14 pts)

**Score: 2 / 14**

No explicit "Partial Reprocessing Guide" section is present. The reference provides a dedicated 3-step watermark reset guide with SQL and explanation. The trainee's runbook describes how to re-trigger failed runs (Repair Run / Run Now) but does not describe how to reset the watermark to reprocess a historical date range. The Cutover Checklist mentions the watermark seeding concept (PD-002: reseed) but this addresses initial environment setup, not ad-hoc reprocessing.

The nearest coverage is the recovery instruction "Run now after fixing root cause" — this addresses re-running the current window but not resetting to a historical window.

### Section 4 — DQ Investigation (14 pts)

**Score: 11 / 14**

Section 5 (DQ Investigation) contains three SQL queries:
1. All violations for a specific run (by lineage_key) using `rule_id` and `violation_column` ✓
2. Recent DQ summary across runs (JOIN to lineage_run) using `rule_id` ✓
3. All DQ rejections from most recent run (using MAX(lineage_key) subquery) ✓

A Common DQ failures table maps rule IDs (QA-P001 through QA-P004) to descriptions and recommended actions. This is functionally equivalent to the reference.

Deduction (-3): Two column-name issues:
1. Section 2.5 uses `assertion_name` (not in data-dictionary) while Section 5 uses `rule_id` — the same column, two different names in the same document. Internal inconsistency.
2. Section 6 Useful Queries includes a DQ query that uses `assertion_name` and `violation_type` — neither is defined in data-dictionary.md (`bronze.dq_rejections` has `rule_id` and `rejection_reason`, not `violation_type`). The "Useful Queries" section contains stale column references.

### Section 5 — Cutover Checklist (14 pts)

**Score: 13 / 14**

The Cutover Checklist (Section 4) provides a 9-step cutover sequence covering all four pending decisions (PD-001, PD-002, PD-003, QA-DQ-01) plus DDL execution, Dimensions team coordination, and verification steps. The checklist is presented as both a table (Pending Decisions) and an ordered sequence.

This is an excellent cutover section — the reference has a similar 9-step sequence. The trainee's sequence is well-structured and operationally complete.

Deduction (-1): Steps 1-9 are prose rather than checkboxes. The reference uses `- [ ]` checkbox format for each step, making the checklist usable as a live tracking document.

### Section 6 — Escalation Path (14 pts)

**Score: 0 / 14**

No escalation path section is present. The reference defines four escalation tiers (blocking pipeline failure, informational DQ, source unavailable, security incident) with contact channels (Slack, PagerDuty, email). The trainee's runbook has no equivalent section.

### Section 7 — Contacts (14 pts)

**Score: 0 / 14**

No contacts section is present. The reference lists three team email addresses (data-engineering, platform, security). Without a contacts section, on-call engineers cannot identify who to notify during an incident without consulting external documentation.

---

## Cross-File Consistency Checks

**data-dictionary.md alignment:**
- Section 5 DQ queries correctly use `rule_id`, `violation_column`, `violation_value`, `rejection_reason`, `detected_at` — all defined in data-dictionary.md ✓
- Section 2.5 and Section 6 queries use `assertion_name` and `violation_type` — neither column is defined in data-dictionary.md. These are stale column references that would cause SQL errors at runtime ✗
- `bronze.dq_rejections` join to `bronze.lineage_run` via `lineage_key` in Section 5 is correct ✓

**to-be.md alignment:**
- Workflow name `nightly_etl_purchase` ✓
- Run time 02:00 UTC ✓
- Halt-and-alert policy ✓
- Pending decisions (PD-001, PD-002, PD-003, QA-DQ-01) match to-be.md/build-plan ✓

---

## Auto-Deducts

| Rule | Applied | Amount | Reason |
|---|---|---|---|
| assertion_name column does not exist | Yes | -3 | Section 2.5 and Section 6 use column not defined in data-dictionary; would cause runtime SQL errors |

---

## Summary

The pipeline-runbook delivers exceptional failure recovery coverage with four task-specific recovery sections that exceed the reference's diagnostic table. The monitoring checklist and cutover checklist are thorough and operationally complete. The addition of a Surrogate Key Resolution Failure section and Useful Queries section adds operational value. The critical gaps are the missing Escalation Path and Contacts sections (both required rubric sections), the absence of a Partial Reprocessing / watermark reset guide, and stale column names (`assertion_name`, `violation_type`) in two DQ queries that contradict the data-dictionary definition. The DQ column inconsistency in Sections 2.5 and 6 would cause runtime SQL failures.

---

## Priority Actions

1. Add an Escalation Path section with severity tiers (pipeline failure, DQ violation, source unavailable), designated channels (Slack/PagerDuty), and contact references.
2. Add a Contacts section with at least data engineering lead, platform team, and security team contact details.
3. Add a Partial Reprocessing section with the watermark reset procedure: `UPDATE inventory_stock.bronze.etl_cutoff SET cutoff_time = '<target_date>' WHERE table_name = 'fact_purchase'` followed by full pipeline trigger and verification query.
4. Fix column names in Section 2.5 query and Section 6 Useful Queries: replace `assertion_name` with `rule_id` and `violation_type` with `rejection_reason` to match data-dictionary.md column definitions.
