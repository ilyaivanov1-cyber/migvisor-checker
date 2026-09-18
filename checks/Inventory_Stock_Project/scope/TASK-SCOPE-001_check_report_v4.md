---
task_id: TASK-SCOPE-001
skill: migvisor-task-checker-scope
participant_file: Inventory_Stock_Project/products/Purchase/input/product-scope.md
reference_file: reference/answers/module_2/0 product-scope.md
product: Purchase
generated: 2026-09-18
total_score: 81/100
grade: Good
---

# TASK-SCOPE-001 Check Report — v4

**Product:** Purchase  
**Participant file:** `Inventory_Stock_Project/products/Purchase/input/product-scope.md`  
**Reference file:** `reference/answers/module_2/0 product-scope.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Scope Score: 81/100 — Good**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Identity | 14 | 90/100 | 12.6 | ✓ |
| Description | 14 | 85/100 | 11.9 | ✓ |
| Objects in Scope | 15 | 82/100 | 12.3 | ✓ |
| Out-of-Scope Objects | 14 | 80/100 | 11.2 | ✓ |
| Consumers | 14 | 75/100 | 10.5 | ⚠ |
| Calculation Surface | 15 | 85/100 | 12.8 | ✓ |
| Boundaries | 7 | 80/100 | 5.6 | ✓ |
| Priority and Sequencing | 7 | 75/100 | 5.3 | ⚠ |
| **Subtotal** | | | **82.2** | |
| Auto-deducts | | | **−1** | |
| **Total** | | | **81/100** | |

**Grade: Good**

---

## Priority Actions

1. **Add analytics.v_ordertoyearanalytics to §5 Consumers** — cross-domain view that reads fact.purchase via correlated subquery; needs coordination note. Worth up to **+4 pts**.
2. **Add §3.5 Analytics Views subsection** — reference explicitly states no analytics views are owned by Purchase but documents the cross-domain dependency. Worth up to **+3 pts**.
3. **Fill [USER INPUT REQUIRED] boundary fields** — temporal boundary and organizational owner are placeholders. Worth up to **+2 pts**.
