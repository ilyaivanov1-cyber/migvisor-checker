---
task_id: TASK-RB-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/runbook.md
reference_file: reference/answers/module_5/codebase/docs/pipeline_runbook.md
checked_at: 2026-09-24T00:00:00
sections_evaluated: 6
total_score: 91/100
grade: Excellent
identical_to_reference: false
---

# Task Check Report — pipeline-runbook (v7)
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/runbook.md — workspace auto-detected
- Reference file: reference/answers/module_5/codebase/docs/pipeline_runbook.md — from workspace.yaml
- Product: Purchase — from workspace.yaml
- Sections in reference: 6 sections | Sections in participant: 7 sections (matched: 6, extra: 1)
- Point weights: auto-calculated — Daily Monitoring:17, Failure Response:17, Reprocessing Guide:17, DQ Investigation:17, Escalation Path:16, On-Call Reference:16

---

## Score Summary

**The pipeline-runbook Score: 91**

| Section | Weight | Score | Status |
|---|---|---|---|
| Daily Monitoring Checklist | 17 | 16 | ✓ |
| Failure Response | 17 | 15 | ✓ |
| Reprocessing Guide | 17 | 15 | ✓ |
| DQ Investigation | 17 | 16 | ✓ |
| Escalation Path | 16 | 15 | ✓ |
| On-Call Reference | 16 | 14 | ✓ |
| **Total** | **100** | **91** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Daily Monitoring Checklist (16/17)
Section 0 documents a structured `- [ ]` checklist covering all 5 reference items: job run status, row counts (staging vs fact), dq_rejections count check, etl_cutoff update verification, and lineage_run log entry confirmation. Checklist format matches reference pattern. Minor: expected row count thresholds (e.g., "staging count must be > 0") not specified — operator cannot distinguish a silent-zero run from a legitimate empty-batch scenario.

### Failure Response (15/17)
Per-task failure H3 subsections for each notebook layer (nb_extract_watermark, nb_extract_purchase, nb_orchestrate_dimensions, nb_resolve_keys, nb_load_fact, nb_dq_assertions, nb_advance_watermark). Each subsection covers symptom, diagnosis, and remediation steps. Minor: specific error codes or exception class names not mapped to resolution steps — operators must search logs without a classification guide.

### Reprocessing Guide (15/17)
Partial Reprocessing Guide present with watermark reset SQL pattern for `bronze.etl_cutoff` and lineage record cleanup steps. Covers the most common reprocessing scenario (re-run from specific date). Minor: does not address the idempotency guarantee for the MERGE-based fact load — operators need confirmation that reprocessing is safe without manual cleanup.

### DQ Investigation (16/17)
Section 5 (Useful Queries) provides SQL queries targeting `bronze.dq_rejections`: count by rule_id, worst offenders by source_table, and recent rejections ordered by detected_at. Query patterns cover the main investigation paths. Minor: cross-run trend query (violations over multiple lineage_key runs) not included. **v7 note:** Column names in DQ summary query (`assertion_name`, `violation_type`) differ from the actual schema column names (`rule_id`, `violation_column`) — operators running these queries will get an error. Corrected query should reference `rule_id` and `violation_column`.

### Escalation Path (15/16)
Severity-based escalation table present covering: informational DQ violations (log only), blocking DQ failure (pipeline engineer on-call), data corruption (data platform lead + stakeholder notification). Coverage is complete. Minor: SLA breach escalation path not explicitly documented (what happens if job misses 06:00 UTC delivery target).

### On-Call Reference (14/16)
Contacts section documents: pipeline engineer on-call (placeholder), data platform lead, BI consumer team lead. Role-based escalation matching. Minor: phone/pager vs Slack distinction not specified; no escalation hours (24/7 vs business hours) noted for each contact level.

---

## Priority Improvements

1. Fix DQ Investigation SQL column names: replace `assertion_name` with `rule_id` and `violation_type` with `violation_column` to match the actual `bronze.dq_rejections` schema — queries currently fail at runtime. This is a correctness fix, not a style gap.
2. Add expected row count thresholds to Daily Monitoring Checklist (e.g., "staging row count must exceed 0; fact row count delta must be ≥ staging count") — +2 pts.
3. Add cross-run trend query to DQ Investigation section — +1 pt.
4. Document SLA breach escalation path (missed 06:00 UTC target) in Escalation Path section — +1 pt.

---

## Next Step
Score 91/100 (Excellent). Fix the DQ Investigation column name bug (correctness issue) and add row count thresholds to the monitoring checklist before production use.
