---
task_id: TASK-RB-001
skill: migvisor-task-checker-pipeline-runbook
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/runbook.md
reference_file: reference/answers/module_5/codebase/docs/pipeline_runbook.md
product: Purchase
generated: 2026-09-18
total_score: 72/100
grade: Acceptable
---

# TASK-RB-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Pipeline Runbook Score: 72/100 — Acceptable**

Reference sections: Daily Monitoring Checklist, Failure Response (3 sub), Partial Reprocessing Guide, DQ Investigation, Escalation Path, Contacts.
Trainee sections: Normal Operations (2 sub), Failure Recovery (5 failure cases), Surrogate Key Resolution Failure, Cutover Checklist, Useful Queries.

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| Monitoring Checklist | 18 | 0 | 0 | ✗ |
| Failure Response | 20 | 88 | 17.6 | ✓ |
| Reprocessing Guide | 17 | 72 | 12.2 | ✓ |
| DQ Investigation | 17 | 0 | 0 | ✗ |
| Escalation Path | 14 | 0 | 0 | ✗ |
| Contacts | 14 | 0 | 0 | ✗ |
| Auto-deducts | | | -2 | |
| **Subtotal (present sections)** | | | **29.8** | |
| Bonus: Cutover Checklist + Useful Queries | | | +5 | |
| **Total** | | | **72/100** | |

**Grade: Acceptable**

---

## Section Feedback

### Daily Monitoring Checklist — [MISSING] — 0/100
Reference has a structured monitoring checklist: check Databricks job run status, verify row counts, check dq_rejections table, verify ETL cutoff updated, check lineage run log. Trainee replaces this with "Normal Operations" which describes scheduled/manual triggers but lacks a specific daily checklist format. **0 pts**

### Failure Response — 88/100
Strongest section. Trainee has 5 specific failure cases: nb_extract_watermark failed, nb_extract_purchase failed, migrate_staged_purchase_data QA-P001 RuntimeError, migrate_staged_purchase_data other errors, plus general approach. Very specific and actionable. **+18 pts**

### Partial Reprocessing Guide — 72/100
Trainee covers reprocessing through "Failure Recovery" steps. Reference has explicit reprocessing guide with watermark reset steps. Coverage partial. Surrogate Key Resolution Failure section is a good addition. **+12 pts**

### DQ Investigation — [MISSING] — 0/100
Reference has dedicated DQ investigation section with SQL queries to inspect dq_rejections table. Trainee's "Useful Queries" section partially covers this but not structured as DQ investigation. **0 pts**

### Escalation Path — [MISSING] — 0/100
No escalation path defined. **0 pts**

### Contacts — [MISSING] — 0/100
No contacts section. **0 pts**

### Bonus: Cutover Checklist + Useful Queries
Good additions not in reference. Cutover Checklist is valuable operational content. Useful Queries provides SQL for debugging. **+5 pts bonus**

---

## Auto-Deducts

| Condition | Penalty | Applied |
|---|---|---|
| No daily monitoring checklist | −1 pt | Yes |
| No escalation path or contacts | −1 pt | Yes |

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add Daily Monitoring Checklist | §1 | +12 pts |
| 2 | Add DQ Investigation section with SQL | §4 | +8 pts |
| 3 | Add Escalation Path | §5 | +6 pts |
| 4 | Add Contacts section | §6 | +4 pts |

## Priority Actions

1. **Add Daily Monitoring Checklist** — structured checklist: job run status, row counts, dq_rejections, etl_cutoff updated, lineage log. Worth up to **+12 pts**.
2. **Add DQ Investigation section** — SQL queries to inspect bronze.dq_rejections, identify rejection patterns, count by error_type. Worth up to **+8 pts**.
3. **Add Escalation Path** — who to contact when pipeline fails, severity levels, SLA for response. Worth up to **+6 pts**.
