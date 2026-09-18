---
task_id: TASK-TR-001
skill: migvisor-task-checker-transformation-rules
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md
reference_file: reference/answers/module_3/product-transformation-rules/product-transformation-rules.md
product: Purchase
generated: 2026-09-18
total_score: 70/100
grade: Acceptable
---

# TASK-TR-001 Check Report — v4

**Generated:** 2026-09-18

---

## Score Summary

**Transformation Rules Score: 70/100 — Acceptable**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header / Purpose | 12 | 80/100 | 9.6 | ✓ |
| NM — Naming | 12 | 82/100 | 9.8 | ✓ |
| OB — Objects | 12 | 78/100 | 9.4 | ✓ |
| LN — Lineage | 12 | 75/100 | 9.0 | ✓ |
| PL — Platform | 12 | 70/100 | 8.4 | ⚠ |
| QA — Quality | 12 | 68/100 | 8.2 | ⚠ |
| SX — Syntax | 12 | 70/100 | 8.4 | ⚠ |
| TY — Types | 12 | 72/100 | 8.6 | ✓ |
| IF — Interface | 12 | 0/100 | 0.0 | ✗ MISSING |
| **Subtotal** | | | **71.4** | |
| Auto-deducts | | | **−1** | |
| **Total** | | | **70/100** | |

**Grade: Acceptable**

---

## Priority Actions

1. **Add IF — Interface dimension** — reference has 4 project + 1 product extension rules covering data contract, connector type, API shape. Worth up to **+10 pts**.
2. **Add Action Files section** — list the YAML files comprising the rule set (CX-custom.yaml, LN-lineage.yaml, etc.). Worth up to **+6 pts**.
3. **Strengthen PL and QA sections** — platform rules should reference Unity Catalog, DLT, and LC; quality rules should cover DQ assertion patterns. Worth up to **+4 pts**.
