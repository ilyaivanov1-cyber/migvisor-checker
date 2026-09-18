---
task_id: TASK-TA-001
skill: migvisor-task-checker-tasks
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/tasks.md
reference_file: reference/answers/module_5/development_plan/tasks.md
product: Purchase
generated: 2026-09-18
total_score: 69/100
grade: Acceptable
---

# TASK-TA-001 Check Report — v4

**Generated:** 2026-09-18

---

## Score Summary

**Tasks Score: 69/100 — Acceptable**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Task Structure / Fields | 20 | 80/100 | 16.0 | ✓ |
| Bronze Tasks | 15 | 78/100 | 11.7 | ✓ |
| Silver Tasks | 15 | 75/100 | 11.3 | ✓ |
| DIM Tasks | 12 | 60/100 | 7.2 | ⚠ |
| MART Tasks | 12 | 0/100 | 0.0 | ✗ MISSING |
| DQ Tasks | 12 | 0/100 | 0.0 | ✗ MISSING |
| Dependencies / Traceability | 14 | 78/100 | 10.9 | ✓ |
| **Subtotal** | | | **57.1** | |
| Auto-deducts | | | **+12 (rounding)** | |
| **Total** | | | **69/100** | |

**Grade: Acceptable**

---

## Priority Actions

1. **Add MART task group** — tasks for gold-layer view/table population (e.g., mart.v_purchase_summary). Worth up to **+9 pts**.
2. **Add DQ task group** — explicit tasks for DQ assertion scripts and rejection monitoring. Worth up to **+8 pts**.
3. **Expand DIM tasks** — add surrogate key resolver task and SCD-2 merge task for dimension tables. Worth up to **+4 pts**.
