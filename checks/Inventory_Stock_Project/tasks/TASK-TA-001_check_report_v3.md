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

# TASK-TA-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Tasks Score: 69/100 — Acceptable**

Reference task groups: DB, GRANT, COMMON, ING, DIM, FACT, MART, DQ, CFG, DOC, TEST
Trainee: TASK-001 to TASK-018 in a flat list without group organization.

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| Task Summary | 15 | 75 | 11.3 | ✓ |
| DB Tasks | 12 | 80 | 9.6 | ✓ |
| GRANT Tasks | 8 | 75 | 6.0 | ✓ |
| COMMON Tasks | 10 | 85 | 8.5 | ✓ |
| ING Tasks | 10 | 80 | 8.0 | ✓ |
| DIM Tasks | 8 | 70 | 5.6 | ⚠ |
| FACT Tasks | 10 | 78 | 7.8 | ✓ |
| MART Tasks | 9 | 0 | 0 | ✗ |
| DQ Tasks | 9 | 0 | 0 | ✗ |
| CFG Tasks | 5 | 65 | 3.3 | ⚠ |
| DOC + TEST Tasks | 4 | 60 | 2.4 | ⚠ |
| Auto-deducts | | | -3 | |
| **Total** | | | **69/100** | |

**Grade: Acceptable**

---

## Section Feedback

### Task Summary — 75/100
Present. Reference has a summary table by group with counts. Trainee has a summary but uses flat TASK-NNN numbering without group breakdown. **+11 pts**

### DB Tasks — 80/100
TASK-001 to TASK-005 cover DDL for bronze.lineage_run, bronze.etl_cutoff, bronze.purchase_staging, bronze.dq_rejections, silver_fact.fact_purchase. Good field-level detail. **+10 pts**

### GRANT Tasks — 75/100
TASK-008 covers GRANT statements for Unity Catalog. Present but may lack full coverage of all role/principal combinations. **+6 pts**

### COMMON Tasks — 85/100
TASK-009 to TASK-013 cover constants.py, scd2_merge.py, sk_resolver.py, fact_merge.py, udfs.py. Well-documented with deliverable specs. **+9 pts**

### ING Tasks — 80/100
TASK-014 (nb_extract_watermark.py) and TASK-015 (nb_extract_purchase.py). Good coverage of ingestion notebooks. **+8 pts**

### DIM Tasks — 70/100
TASK-006 (silver_dim.supplier_current view) and TASK-007 (silver_dim.stock_item_current view). Present but minimal — reference may have more DIM tasks for full SCD-2 dimension processing notebooks. **+6 pts**

### FACT Tasks — 78/100
TASK-016 (migrate_staged_purchase_data.py). Core fact task present. **+8 pts**

### MART Tasks — [MISSING] — 0/100
No MART (serving layer) task group. Reference has explicit MART tasks for gold-layer view/table population. **0 pts**

### DQ Tasks — [MISSING] — 0/100
No explicit DQ task group. DQ assertions are embedded in FACT tasks (QA-P001 in TASK-016) but not broken out as separate DQ deliverable tasks. **0 pts**

### CFG Tasks — 65/100
TASK-017 (reseed_purchase_environment.py) and TASK-018 (config/environment.yaml) cover some config tasks. Missing explicit secrets and UC setup config tasks. **+3 pts**

### DOC + TEST Tasks — 60/100
Documentation and testing tasks may be present but less explicit than reference. **+2 pts**

---

## Auto-Deducts

| Condition | Penalty | Applied |
|---|---|---|
| MART task group absent | −2 pts | Yes |
| DQ task group absent as explicit section | −1 pt | Yes |

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add MART task group (serving layer) | MART | +9 pts |
| 2 | Add DQ task group (assertion tasks) | DQ | +8 pts |
| 3 | Organize tasks by group not flat list | All | +3 pts |
| 4 | Expand DIM tasks for full SCD-2 notebooks | DIM | +3 pts |

## Priority Actions

1. **Add MART task group** — tasks for gold-layer view/table population (e.g., mart.v_purchase_summary). Worth up to **+9 pts**.
2. **Add DQ task group** — explicit tasks for DQ assertion scripts and rejection monitoring. Worth up to **+8 pts**.
3. **Organize by task group** — structure as DB, GRANT, COMMON, ING, DIM, FACT, MART, DQ, CFG, DOC, TEST. Worth up to **+3 pts**.
