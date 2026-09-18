---
trainee: Inventory_Stock_Project
product: Purchase
generated: 2026-09-18
checks_run: 21
total_score: 45/100
grade: Needs Work
existing_score: 73/100
existing_grade: Acceptable
---

# Check Summary — Inventory_Stock_Project / Purchase

**Run:** v3 — all 21 skills  
**Generated:** 2026-09-18

---

## Score Table

| # | Skill | Task ID | Score | Grade |
|---|---|---|---|---|
| 1 | scope | TASK-SCOPE-001 | **81/100** | Good |
| 2 | as-is | TASK-AI-001 | **68/100** | Acceptable |
| 3 | transformation-rules | TASK-TR-001 | **70/100** | Acceptable |
| 4 | project-rules | TASK-PR-001 | **77/100** | Good |
| 5 | to-be | TASK-TB-001 | **80/100** | Good |
| 6 | design | TASK-DE-001 | **73/100** | Acceptable |
| 7 | requirements | TASK-RE-001 | **82/100** | Good |
| 8 | tasks | TASK-TA-001 | **69/100** | Acceptable |
| 9 | product-definition | TASK-PD-001 | **75/100** | Good |
| 10 | build-plan | TASK-BP-001 | **63/100** | Acceptable |
| 11 | data-dictionary | TASK-DD-001 | **74/100** | Acceptable |
| 12 | pipeline-runbook | TASK-RB-001 | **72/100** | Acceptable |
| 13 | validation-report | TASK-VR-001 | **70/100** | Acceptable |
| 14 | architecture-diagram | TASK-AD-001 | **0/100** | Incomplete — file not submitted |
| 15 | go-live-checklist | TASK-GL-001 | **0/100** | Incomplete — file not submitted |
| 16 | bi-connections | TASK-BI-001 | **0/100** | Incomplete — file not submitted |
| 17 | secrets-setup | TASK-SS-001 | **0/100** | Incomplete — file not submitted |
| 18 | secrets-rotation-runbook | TASK-SR-001 | **0/100** | Incomplete — file not submitted |
| 19 | uc-permission-audit | TASK-UC-001 | **0/100** | Incomplete — file not submitted |
| 20 | uc-setup | TASK-UC-002 | **0/100** | Incomplete — file not submitted |
| 21 | secrets-config | TASK-SC-001 | **0/100** | Incomplete — file not submitted |
| | **Average (all 21)** | | **45/100** | **Needs Work** |
| | **Average (submitted 13)** | | **73/100** | **Acceptable** |

---

## Top Scores (submitted files)

1. requirements — 82/100 (Good)
2. scope — 81/100 (Good)
3. to-be — 80/100 (Good)

## Lowest Scores (submitted files)

1. build-plan — 63/100 (Acceptable)
2. as-is — 68/100 (Acceptable)
3. tasks — 69/100 (Acceptable)

## Not Submitted (0/100)

8 deliverables from module 5 codebase/config and codebase/docs are missing:
- architecture_diagram.md
- go_live_checklist.md
- bi_connections.md
- secrets_setup.md
- secrets_rotation_runbook.md
- uc_permission_audit.sql
- uc_setup.sql
- secrets_config.py

---

## Main Gaps

1. IF (Interface) dimension missing from both transformation rule sets
2. MART and DQ task groups absent from tasks.md and build-plan.md
3. Dimension tables (dim.supplier, dim.stock_item, dim.date) missing from data-dictionary
4. Daily Monitoring Checklist missing from pipeline runbook
5. analytics.v_ordertoyearanalytics missing as consumer across scope/as-is/to-be
