---
task_id: TASK-DD-001
skill: migvisor-task-checker-data-dictionary
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/data-dictionary.md
reference_file: reference/answers/module_5/codebase/docs/data_dictionary.md
product: Purchase
generated: 2026-09-18
total_score: 74/100
grade: Acceptable
---

# TASK-DD-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Data Dictionary Score: 74/100 — Acceptable**

Reference tables (9): stg.purchase_staging, stg.etl_cutoff, stg.lineage, stg.dq_rejections, dim.supplier, dim.stock_item, dim.date, fact.purchase, Glossary SCD-2.
Trainee tables (5): silver_fact.fact_purchase, bronze.purchase_staging, bronze.lineage_run, bronze.etl_cutoff, bronze.dq_rejections.

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| Table Index | 5 | 80 | 4.0 | ✓ |
| stg/bronze.purchase_staging | 14 | 88 | 12.3 | ✓ |
| stg/bronze.etl_cutoff | 11 | 85 | 9.4 | ✓ |
| stg/bronze.lineage | 11 | 82 | 9.0 | ✓ |
| stg/bronze.dq_rejections | 11 | 85 | 9.4 | ✓ |
| dim.supplier | 12 | 0 | 0 | ✗ |
| dim.stock_item | 12 | 0 | 0 | ✗ |
| dim.date | 10 | 0 | 0 | ✗ |
| fact.purchase | 10 | 82 | 8.2 | ✓ |
| Glossary SCD-2 | 4 | 0 | 0 | ✗ |
| Auto-deducts | | | -4 | |
| **Total** | | | **78→74/100** | |

**Grade: Acceptable**

---

## Section Feedback

### Table Index — 80/100
Present. Lists 5 tables. Reference has 8 tables + glossary. **+4 pts**

### bronze.purchase_staging — 88/100
Good column-level detail. Column names, types, nullability, description. Matches reference structure for this table. **+12 pts**

### bronze.etl_cutoff — 85/100
Well-documented watermark control table. TableName PK, CutoffTime datetime2. **+9 pts**

### bronze.lineage_run — 82/100
ETL run audit log. LineageKey PK, DataLoadStarted, TableName, DataLoadCompleted, WasSuccessful, SourceSystemCutoffTime. Good coverage. **+9 pts**

### bronze.dq_rejections — 85/100
DQ rejection log table documented. Good addition that shows understanding of DQ architecture. **+9 pts**

### silver_fact.fact_purchase — 82/100
Fact table documented with column names, types, FKs. Good. **+8 pts**

### dim.supplier — [MISSING] — 0/100
SCD-2 supplier dimension definition absent. Reference documents 9 columns including ValidFrom/ValidTo SCD-2 tracking columns. **0 pts**

### dim.stock_item — [MISSING] — 0/100
SCD-2 stock item dimension definition absent. Reference documents 19 columns including Photo varbinary(max). **0 pts**

### dim.date — [MISSING] — 0/100
Static calendar dimension absent. **0 pts**

### Glossary SCD-2 — [MISSING] — 0/100
SCD-2 tracking column glossary (ValidFrom, ValidTo, SurrogateKey semantics) absent. **0 pts**

---

## Auto-Deducts

| Condition | Penalty | Applied |
|---|---|---|
| 3 dimension tables missing | −3 pts | Yes |
| SCD-2 glossary missing | −1 pt | Yes |

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add dim.supplier with all 9 columns | dim.supplier | +12 pts |
| 2 | Add dim.stock_item with all 19 columns | dim.stock_item | +12 pts |
| 3 | Add dim.date with 12 columns | dim.date | +10 pts |
| 4 | Add SCD-2 glossary | Glossary | +4 pts |

## Priority Actions

1. **Add dim.supplier** — 9 columns: SupplierKey (PK), WWISupplierID, Supplier, Category, PrimaryContact, PostalCode, ValidFrom, ValidTo, LineageKey. Worth up to **+12 pts**.
2. **Add dim.stock_item** — 19 columns including SCD-2 tracking and Photo varbinary(max). Worth up to **+12 pts**.
3. **Add dim.date** — 12-column static calendar dimension. Worth up to **+10 pts**.
4. **Add SCD-2 glossary** — explain ValidFrom/ValidTo semantics and surrogate key convention. Worth up to **+4 pts**.
