---
task_id: TASK-TB-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/to-be.md
reference_file: reference/answers/module_4/to-be.md
checked_at: 2026-09-24T12:00:00
sections_evaluated: 6
total_score: 86/100
grade: Good
identical_to_reference: false
---

# Task Check Report — to-be (v6)
_Purchase | 2026-09-24_

## Score Summary

| Section | Weight | Score | Status |
|---|---|---|---|
| Overview | 17 | 15 | ✓ |
| Target Architecture | 17 | 15 | ✓ |
| Data Model | 17 | 15 | ✓ |
| ETL Pipeline Design | 17 | 14 | ✓ |
| Non-Functional Requirements | 16 | 14 | ✓ |
| Migration Strategy | 16 | 13 | ✓ |
| **Total** | **100** | **86** | |

---

## Section Feedback

### Non-Functional Requirements (14/16)
NFR section now expanded with SLA targets (daily pipeline must complete within 2h), data retention policy (90 days bronze, indefinite silver/gold), and Unity Catalog RBAC model (service principals + roles). Strong improvement. Minor: no explicit RTO/RPO targets.

### ETL Pipeline Design (14/17)
Cross-Domain Views subsection added documenting analytics.v_ordertoyearanalytics access pattern. Comprehensive pipeline design. Minor: mart optimization step not explicitly covered.

### Migration Strategy (13/16)
Covers phased migration approach. Minor: cutover validation steps could be more detailed.

---

## Priority Improvements

1. Add RTO/RPO targets to NFR section — +2 pts
2. Expand Migration Strategy with cutover validation steps — +3 pts

---

## Next Step
Score ≥ 75 — you can proceed to the next task.
