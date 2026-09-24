---
task_id: TASK-SCOPE-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/input/product-scope.md
reference_file: reference/answers/module_2/0 product-scope.md
checked_at: 2026-09-24T12:00:00
sections_evaluated: 9
total_score: 87/100
grade: Good
identical_to_reference: false
---

# Task Check Report — product-scope (v6)
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: Inventory_Stock_Project/products/Purchase/input/product-scope.md — auto-detected
- Reference file: reference/answers/module_2/0 product-scope.md — workspace.yaml
- Product: Purchase — workspace.yaml
- Sections in reference: 9 | Sections in participant: 9 (matched: 9)
- Point weights: auto-calculated — §1:11, §2:11, §3:12, §4:11, §5:11, §6:11, §7:11, §8:11, §9:11

---

## Score Summary

| Section | Weight | Score | Status |
|---|---|---|---|
| 1 Identity | 11 | 11 | ✓ |
| 2 Description | 11 | 10 | ✓ |
| 3 Objects in Scope | 12 | 10 | ✓ |
| 4 Out-of-Scope Objects | 11 | 10 | ✓ |
| 5 Consumers | 11 | 11 | ✓ |
| 6 Calculation Surface | 11 | 10 | ✓ |
| 7 Boundaries | 11 | 10 | ⚠ |
| 8 Priority and Sequencing | 11 | 11 | ✓ |
| 9 Known Migration Risks | 11 | 9 | ⚠ |
| **Total** | **100** | **87** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### §5 Consumers (11/11)
analytics.v_ordertoyearanalytics now included with cross-domain coordination note and correlated subquery detail. All 3 consumers present. Full credit.

### §7 Boundaries (10/11)
Temporal and Organizational boundaries carry [USER INPUT REQUIRED] placeholders — treated as intentional deferrals per rubric. System source/target and ETL orchestration entries are fully specified. Minor deduction for deferred fields with no supplementary estimate.

### §9 Known Migration Risks (9/11)
7 of 8 reference risks documented. Missing: the SCD-2 UPDATE+INSERT pattern for supplier/stock-item dimension procedures (reference risk #5). analytics.v_ordertoyearanalytics cross-domain risk is in Consumers (§5) but not in the risks table itself.

### §3 Objects in Scope (10/12)
No dedicated §3.5 Analytics Views section (present in reference). The analytics view is documented in §5 Consumers. Minor structural gap.

---

## Priority Improvements

1. Add risk #5 to Known Migration Risks table: SCD-2 UPDATE+INSERT pattern for dimension procedures — +2 pts
2. Add dedicated §3.5 Analytics Views section or reference note for analytics.v_ordertoyearanalytics — +1 pt

---

## Next Step
Score ≥ 75 — you can proceed to the next task.
