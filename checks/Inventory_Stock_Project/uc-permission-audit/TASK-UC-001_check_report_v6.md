---
task_id: TASK-UC-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/uc_permission_audit.sql
reference_file: reference/answers/module_5/codebase/config/uc_permission_audit.sql
checked_at: 2026-09-24T12:00:00
sections_evaluated: 4
total_score: 95/100
grade: Excellent
identical_to_reference: false
---

# Task Check Report — uc-permission-audit (v6)
_Purchase | 2026-09-24_

## Score Summary

| Section | Weight | Score | Status |
|---|---|---|---|
| Catalog-level SHOW GRANTS | 25 | 24 | ✓ |
| Schema-level SHOW GRANTS | 25 | 24 | ✓ |
| Table-level SHOW GRANTS | 25 | 24 | ✓ |
| Mart Views SHOW GRANTS | 25 | 23 | ✓ |
| **Total** | **100** | **95** | |

---

## Section Feedback

### Catalog-level SHOW GRANTS (24/25)
Comment block added noting expected USE CATALOG principal grants: etl-service-principal (CREATE TABLE, CREATE SCHEMA), bi-service-principal (SELECT). Troubleshooting note included. Near-perfect. Minor: REVOKE example not included.

### All SHOW GRANTS sections
bronze.lineage_run name is consistent throughout (not stg.lineage or other variants). Correct. Principal-to-privilege mapping complete for all principals.

---

## Priority Improvements

1. Add REVOKE example to catalog-level section for audit completeness — +2 pts
2. Add note on INFORMATION_SCHEMA.TABLE_PRIVILEGES as alternative audit method — +2 pts

---

## Next Step
Score ≥ 90 — Excellent. You can proceed to the next task.
