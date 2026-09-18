---
task_id: TASK-DE-001
skill: migvisor-task-checker-design
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/design.md
reference_file: reference/answers/module_5/development_plan/design.md
product: Purchase
generated: 2026-09-18
total_score: 73/100
grade: Acceptable
---

# TASK-DE-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Design Score: 73/100 — Acceptable**

Reference top-level sections: Data Model, Ingestion, Transformation.
Trainee top-level sections: Architecture Overview, Workflow Task Sequence, SK Resolution Pattern, MERGE INTO Pattern, QA Assertion Chain, Lineage Propagation, Configuration Management.

Different structural approach but overlapping content.

| Reference Section | Trainee Equivalent | Raw | Weight | Weighted | Status |
|---|---|---|---|---|---|
| Data Model (DDL, ER, conventions) | Architecture Overview + SK Resolution | 70 | 34 | 23.8 | ⚠ |
| Ingestion (watermark, extract, staging) | Workflow Task Sequence | 75 | 33 | 24.8 | ✓ |
| Transformation (SCD-2, MERGE, UDFs) | MERGE INTO Pattern + QA Chain | 72 | 33 | 23.8 | ⚠ |
| Auto-deducts | | | | -1 | |
| **Total** | | | | **73/100** | |

**Grade: Acceptable**

---

## Section Feedback

### Data Model — 70/100
Reference has formal DDL (`CREATE TABLE` statements), retention policy, FK constraints, mart layer. Trainee has Architecture Overview (layer responsibilities: bronze/silver/gold), SK Resolution Pattern (temporal range join, COALESCE to 0, date_key derivation). Missing: formal DDL blocks for all Delta tables, explicit FK constraints section, mart layer design, table naming conventions document. **+24 pts**

### Ingestion — 75/100
Workflow Task Sequence covers taskValues contract, notebook responsibilities. Reference has Watermark Lifecycle, Dimension Extraction Pattern, Fact Extraction Pattern (Truncate+Overwrite), Credential Management, HISTORY_ANCHOR_DATE, Audit Columns. Trainee covers the main flow but less detail on credential management and audit column design. **+25 pts**

### Transformation — 72/100
MERGE INTO Pattern section covers the Delta MERGE strategy. QA Assertion Chain section covers quality checks. Reference has SCD-2 Dimension Merge Design in detail. Trainee has good implementation-level detail on sk_resolver and MERGE pattern but lacks the formal SCD-2 design spec. **+24 pts**

---

## Auto-Deducts

| Condition | Penalty | Applied |
|---|---|---|
| Missing formal DDL blocks | −1 pt | Yes |

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add formal DDL blocks (CREATE TABLE) for all Delta tables | Data Model | +8 pts |
| 2 | Add Mart Layer section | Data Model | +4 pts |
| 3 | Add Credential Management section | Ingestion | +3 pts |
| 4 | Add formal SCD-2 Dimension Merge Design | Transformation | +3 pts |

## Priority Actions

1. **Add formal DDL blocks** — CREATE TABLE statements for bronze.purchase_staging, bronze.lineage_run, silver_fact.fact_purchase etc. Worth up to **+8 pts**.
2. **Add Mart Layer section** — design for serving layer (gold) views or tables. Worth up to **+4 pts**.
3. **Add Credential Management** — how secrets are accessed in notebooks (secrets_config pattern). Worth up to **+3 pts**.
