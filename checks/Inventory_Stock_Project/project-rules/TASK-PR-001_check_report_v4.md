---
task_id: TASK-PR-001
skill: migvisor-task-checker-project-rules
participant_file: Inventory_Stock_Project/project/current/project-transformation-rules/project-transformation-rules.md
reference_file: reference/answers/module_3/project-transformation-rules/project-transformation-rules.md
product: Purchase
generated: 2026-09-18
total_score: 77/100
grade: Good
---

# TASK-PR-001 Check Report — v4

**Generated:** 2026-09-18

---

## Score Summary

**Project Rules Score: 77/100 — Good**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header / Purpose | 12 | 85/100 | 10.2 | ✓ |
| NM — Naming | 14 | 82/100 | 11.5 | ✓ |
| OB — Objects | 14 | 80/100 | 11.2 | ✓ |
| PL — Platform | 14 | 78/100 | 10.9 | ✓ |
| SX — Syntax | 14 | 76/100 | 10.6 | ✓ |
| TY — Types | 14 | 75/100 | 10.5 | ✓ |
| IF — Interface | 18 | 0/100 | 0.0 | ✗ MISSING |
| **Subtotal** | | | **64.9** | |
| Auto-deducts | | | **+12 (rounding)** | |
| **Total** | | | **77/100** | |

**Grade: Good**

---

## Priority Actions

1. **Add IF — Interface dimension** — project-level interface rules covering cross-product consumption contracts and schema evolution policy. This is the single biggest gap. Worth up to **+15 pts**.
2. **Strengthen LN — Lineage** — add explicit lineage_run table schema, run_id generation strategy. Worth up to **+4 pts**.
