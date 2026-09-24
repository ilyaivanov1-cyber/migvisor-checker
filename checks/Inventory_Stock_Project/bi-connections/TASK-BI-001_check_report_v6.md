---
task_id: TASK-BI-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/bi/bi_connections.md
reference_file: reference/answers/module_5/codebase/config/bi_connections.md
checked_at: 2026-09-24T12:00:00
sections_evaluated: 5
total_score: 94/100
grade: Excellent
identical_to_reference: false
---

# Task Check Report — bi-connections (v6)
_Purchase | 2026-09-24_

## Score Summary

| Section | Weight | Score | Status |
|---|---|---|---|
| Overview | 20 | 19 | ✓ |
| Connection Details (v_purchase_by_supplier) | 20 | 19 | ✓ |
| Connection Details (v_purchase_per_stock_item) | 20 | 19 | ✓ |
| Known Issues | 20 | 19 | ✓ |
| Access Provisioning | 20 | 18 | ✓ |
| **Total** | **100** | **94** | |

---

## Section Feedback

### Connection Details (19/20 each)
Sample aggregate query added for v_purchase_by_supplier. Both views now have sample queries. Minor: connection string doesn't include cluster size recommendation.

### Known Issues (19/20)
Explanatory note added: bronze.lineage_run corresponds to stg.lineage in GlobalPurchase reference pattern. Good. Near-perfect.

### Access Provisioning (18/20)
Comprehensive. Minor: role assignment command example not included.

---

## Priority Improvements

1. Add cluster size recommendation to connection string — +2 pts
2. Add role assignment command example to Access Provisioning — +2 pts

---

## Next Step
Score ≥ 90 — Excellent. You can proceed to the next task.
