---
task_id: TASK-GL-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/go_live_checklist.md
reference_file: reference/answers/module_5/codebase/docs/go_live_checklist.md
checked_at: 2026-09-24T12:00:00
sections_evaluated: 7
total_score: 89/100
grade: Good
identical_to_reference: false
---

# Task Check Report — go-live-checklist (v6)
_Purchase | 2026-09-24_

## Score Summary

| Section | Weight | Score | Status |
|---|---|---|---|
| Infrastructure | 14 | 13 | ✓ |
| Security | 14 | 13 | ✓ |
| Pipeline | 14 | 13 | ✓ |
| Data Quality | 14 | 13 | ✓ |
| BI Connections | 15 | 13 | ✓ |
| Rollback | 15 | 12 | ✓ |
| Sign-off | 14 | 12 | ✓ |
| **Total** | **100** | **89** | |

---

## Section Feedback

### Data Quality (13/14)
Assertions file path corrected to config/dq_assertions_purchase.yaml. DQR-001, DQR-004, DQR-005, DQR-006 labeled BLOCKING; DQR-002, DQR-003 labeled Informational. Near-perfect. Minor: threshold values for BLOCKING rules not specified.

### Pipeline (13/14)
deploy_workflow.sh --env prod added as explicit checklist item. Good. Minor: smoke test step not shown as separate item.

### Security (13/14)
nb_pii_compliance_check referenced specifically (not generic "PII compliance check"). Good. Minor: UC permission grant verification step not listed.

### Rollback (12/15)
Rollback procedure documented. Minor: rollback time estimate missing; rollback decision criteria not specified.

---

## Priority Improvements

1. Add rollback decision criteria and time estimate to Rollback section — +4 pts
2. Add UC permission grant verification to Security section — +3 pts

---

## Next Step
Score ≥ 75 — you can proceed to the next task.
