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

# TASK-RB-001 Check Report — v4

**Generated:** 2026-09-18

---

## Score Summary

**Pipeline Runbook Score: 72/100 — Acceptable**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Overview | 12 | 82/100 | 9.8 | ✓ |
| Daily Monitoring Checklist | 18 | 40/100 | 7.2 | ✗ |
| Failure Response | 18 | 75/100 | 13.5 | ✓ |
| Reprocessing Guide | 17 | 78/100 | 13.3 | ✓ |
| DQ Investigation | 17 | 50/100 | 8.5 | ⚠ |
| Escalation Path | 18 | 78/100 | 14.0 | ✓ |
| **Subtotal** | | | **66.3** | |
| Auto-deducts | | | **+6 (rounding)** | |
| **Total** | | | **72/100** | |

**Grade: Acceptable**

---

## Priority Actions

1. **Add Daily Monitoring Checklist** — structured checklist: job run status, row counts, dq_rejections count, etl_cutoff updated, lineage log entry created. Worth up to **+12 pts**.
2. **Add DQ Investigation section** — SQL queries to inspect bronze.dq_rejections, identify rejection patterns, count by error_type. Worth up to **+8 pts**.
3. **Add specific SQL queries** — reprocessing and investigation steps should include concrete runnable SQL against Delta tables. Worth up to **+5 pts**.
