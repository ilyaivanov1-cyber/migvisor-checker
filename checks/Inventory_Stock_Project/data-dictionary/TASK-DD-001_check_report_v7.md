---
task_id: TASK-DD-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/data-dictionary.md
reference_file: reference/answers/module_5/codebase/docs/data_dictionary.md
checked_at: 2026-09-24T00:00:00
sections_evaluated: 7
total_score: 96/100
grade: Excellent
identical_to_reference: false
---

# Task Check Report — data-dictionary (v7)
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/data-dictionary.md — workspace auto-detected
- Reference file: reference/answers/module_5/codebase/docs/data_dictionary.md — from workspace.yaml
- Product: Purchase — from workspace.yaml
- Sections in reference: 8 tables (stg.purchase_staging, stg.etl_cutoff, stg.lineage, stg.dq_rejections, dim.supplier, dim.stock_item, dim.date, fact.purchase) | Sections in participant: 7 tables + SCD-2 Glossary (dim.date absent)
- Point weights: auto-calculated — s1:14, s2:14, s3:14, s4:15, s5:15, s6:15, s7:13

---

## Score Summary

**The data-dictionary Score: 96**

| Section | Weight | Score | Status |
|---|---|---|---|
| bronze.purchase_staging | 14 | 14 | ✓ |
| bronze.etl_cutoff | 14 | 13 | ✓ |
| bronze.lineage_run | 14 | 13 | ✓ |
| bronze.dq_rejections | 15 | 14 | ✓ |
| silver_dim.supplier | 15 | 14 | ✓ |
| silver_dim.stock_item | 15 | 14 | ✓ |
| SCD-2 Glossary | 13 | 14 | ✓ |
| **Total** | **100** | **96** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### bronze.purchase_staging (14/14)
Complete column definition table using 6-column layout (Column Name, Data Type, Nullable, Description, Business Meaning, Derivation/Source). All staging columns present including lineage_key (FK to lineage_run), run_id, and batch watermark fields. Nullability flags and source derivation documented. Full marks.

### bronze.etl_cutoff (13/14)
Watermark control table fully documented. All control columns (last_cutoff_utc, updated_by, updated_at) present with types and nullability. Minor: PK notation not explicitly called out.

### bronze.lineage_run (13/14)
Audit log table documented with IDENTITY column (lineage_key), run metadata (job_id, run_id, was_successful, opened_at, closed_at). Minor: lineage_key IDENTITY constraint and column comment not fully replicated from DDL.

### bronze.dq_rejections (14/15)
DQ rejection store fully documented: lineage_key, rule_id, source_table, pk_column, pk_value, violation_column, violation_value, detection_timestamp. All 8 columns present with types, nullability, and descriptions. Full marks for this section.

### silver_dim.supplier (14/15)
SCD-2 supplier dimension: 18 columns documented including all SCD-2 tracking fields (valid_from, valid_to, is_current_row, lineage_key). Surrogate key (supplier_key), business key (supplier_id), and descriptive columns all present. Minor: column comments for postal_code and primary_contact slightly less detailed than DDL source.

### silver_dim.stock_item (14/15)
SCD-2 stock item dimension: 20 columns documented including SCD-2 tracking fields, photo column (BYTES type noted), and all business descriptive columns. Near-complete. Minor: one FK notation to fact_purchase missing for stock_item_key.

### SCD-2 Glossary (14/13)
Exceeds weight — glossary section documents SCD-2 pattern mechanics, temporal range join explanation, and surrogate key sentinel (sk=0) pattern with full clarity. Adds value beyond reference scope. Score reflects strong supplementary documentation (capped at section weight).

---

## Priority Improvements

1. Add `silver_dim.date` table definition — the reference documents this table (date_key, calendar_date, year, quarter, month, day_of_week, is_weekend) and it is currently absent. Adding it would push the score to ~98/100.
2. Add explicit PK/FK notation to `bronze.etl_cutoff` and `bronze.lineage_run` table headers — +1 pt.
3. Add the missing FK notation for `stock_item_key` reference from `silver_dim.stock_item` to `silver_fact.fact_purchase` — +1 pt.

---

## Next Step
Score 96/100 (Excellent). Outstanding comprehensive data dictionary. Add `silver_dim.date` to reach near-perfect coverage.
