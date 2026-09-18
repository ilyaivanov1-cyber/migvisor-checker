---
task_id: TASK-DD-001
skill: migvisor-task-checker-data-dictionary
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/codebase/docs/data-dictionary.md
reference_file: ./reference/answers/module_5/codebase/docs/data_dictionary.md
generated: 2026-09-18
total_score: 85/100
grade: Good
---

# TASK-DD-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/codebase/docs/data-dictionary.md`  
**Reference file:** `./reference/answers/module_5/codebase/docs/data_dictionary.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Data Dictionary Score: 85/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| 1. Table Index | 17 | 92/100 | 15.64 | ✓ |
| 2. fact_purchase Table Entry | 17 | 95/100 | 16.15 | ✓ |
| 3. Staging / Control Table Entries | 17 | 88/100 | 14.96 | ✓ |
| 4. Dimension Table Entries | 16 | 72/100 | 11.52 | ⚠ |
| 5. Column-Level Metadata Quality | 17 | 82/100 | 13.94 | ✓ |
| 6. Mart / DQ Rejection Table Entries | 16 | 65/100 | 10.4 | ⚠ |
| **Subtotal** | | | **82.61** | |
| Auto-deducts | | | **−2** | |
| **Total** | | | **85/100** | → rounded up |

**Grade: Good**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → +1 each to §1, §2, §3, §5.

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| stg.purchase_staging | bronze.purchase_staging | Direct |
| stg.etl_cutoff | bronze.etl_cutoff | Direct |
| stg.lineage | bronze.lineage_run | Direct |
| stg.dq_rejections | bronze.dq_rejections | Direct |
| dim.supplier | Not documented (externally owned) | Missing |
| dim.stock_item | Not documented (externally owned) | Missing |
| fact.purchase | silver_fact.fact_purchase | Direct |
| mart views | Not present | Missing |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| Missing dimension table entries (dim.supplier, dim.stock_item) — these are owned by the Purchase product and must be documented | −2 pts | Yes — reference documents both dimension tables with all SCD-2 control columns; trainee omits them entirely citing "externally owned" |

**Total auto-deducts: −2 pts**

---

## Section Feedback

### 1. Table Index — 92/100 (weight 17 → 15.64 pts)

**Status:** ✓ Present

**Strengths:** Table index covers all 5 tables in scope for trainee with Table, Schema, and Purpose columns. Hyperlinks to each section work correctly. Index communicates the medallion structure clearly via the schema column (`silver_fact` vs `bronze`). The purpose descriptions accurately capture grain and load pattern for each table.

**Gaps:** Reference does not have an explicit table index (reference uses a flat structure with section headers). Trainee's table index is actually a value-add. Minor gap: reference documents 8 tables (including 2 dim tables and mart views); trainee's index covers only 5.

---

### 2. fact_purchase Table Entry — 95/100 (weight 17 → 16.15 pts)

**Status:** ✓ Present

**Strengths:** The `silver_fact.fact_purchase` entry is the most detailed section in the document — and arguably more detailed than the reference:
- **Purpose, Grain, Load pattern, Delta properties** sections all present
- **Rules** cross-reference block lists all applicable transformation rule IDs (OB-002, TY-004, TY-010, TY-003, TY-009, TY-015, TY-017, PE-002, PE-008, PE-P001, LN-001, NM-001, NM-009, CX-P006) — excellent traceability
- **11 columns** fully documented with Column Name, Data Type, Nullable, Description, Business Meaning, and Derivation/Source — 6 sub-fields per column vs reference's 4
- `purchase_key` IDENTITY generation documented. `lineage_key` taskValues injection documented (LN-P001). `supplier_key` temporal range join pattern documented. `received_outers` NULL semantics (NULL ≠ 0) documented.
- `COALESCE(supplier_key, 0)` unknown-member sentinel documented.

**Gaps:** Very minor — `date_key` in trainee is `DATE` type while reference uses `INT` (YYYYMMDD integer format). This is an intentional design choice but should include a note explaining why `DATE` was chosen over `INT` for the FK to the date dimension.

---

### 3. Staging / Control Table Entries — 88/100 (weight 17 → 14.96 pts)

**Status:** ✓ Present

**Strengths:** `bronze.purchase_staging` entry documents 15 columns including `purchase_staging_key` IDENTITY, `wwi_supplier_id`, `wwi_stock_item_id`, `last_modified_when` (temporal probe), and `_extracted_at_utc`. Purpose documents the SSIS bug fix (OVERWRITE mode eliminates stale-row accumulation from the legacy `Integration.Order_Staging` truncation defect). Load pattern section explicitly notes that surrogate keys are NULL at extract time and populated by sk_resolver.py.

`bronze.lineage_run` is documented with 9 columns — more detailed than reference's `stg.lineage` (8 columns). `bronze.etl_cutoff` and `bronze.dq_rejections` are referenced in the table index.

**Gaps:** Reference documents `stg.etl_cutoff` with only `entity_name` (PK) and `last_cutoff_time` columns — trainee's equivalent uses `table_name` (PK) and `cutoff_time`. Minor naming difference not penalized. Reference `stg.dq_rejections` has `rejection_key`, `dq_rule_id`, `batch_id` — trainee details for `bronze.dq_rejections` are in the index only (no full column table shown in the excerpt). If the full document has the column table, this gap is resolved.

---

### 4. Dimension Table Entries — 72/100 (weight 16 → 11.52 pts)

**Status:** ⚠ Partial

**Strengths:** The trainee's `fact_purchase` entry documents the FK relationships to both dimension tables (`supplier_key` FK → `silver_dim.supplier`, `stock_item_key` FK → `silver_dim.stock_item`) and the SCD-2 join logic, so the interface contract is indirectly captured.

**Gaps:** Reference explicitly documents both dimension tables with their full column schemas:
- `dim.supplier`: business key, all attribute columns, SCD-2 control columns (`valid_from`, `valid_to`, `is_current_row`, `lineage_key`)
- `dim.stock_item`: 14+ attribute columns including DECIMAL(18,2) prices, SCD-2 control columns

Trainee data dictionary has no entries for `silver_dim.supplier` or `silver_dim.stock_item`, citing "externally owned." However, the Purchase product team is responsible for managing the SCD-2 dimension DDL (per the tasks.md and build-plan.md DDL tasks covering dim tables). The data dictionary should document the interface — even if the ETL is shared or externally co-owned. A consumer of the data dictionary cannot understand the full data model without the dimension column schemas.

---

### 5. Column-Level Metadata Quality — 82/100 (weight 17 → 13.94 pts)

**Status:** ✓ Present

**Strengths:** For every column in `silver_fact.fact_purchase`, trainee provides 6 metadata fields: Column Name, Data Type, Nullable, Description, Business Meaning, and Derivation/Source. This is significantly richer than reference's 4 fields (Column, Type, Nullable, Description). Business Meaning field explains the analytical purpose of each measure. Derivation/Source traces each column back to the specific SQL Server source table and column name. Rule cross-references in the column-level Derivation field (e.g., "Rule: TY-010", "Rules: SX-003, SX-P003, TY-P001") are excellent.

**Gaps:** Rule cross-references are present for `silver_fact.fact_purchase` but consistency across other tables in the document is not verified. The quality bar set by the fact table entry should be maintained for all tables.

---

### 6. Mart / DQ Rejection Table Entries — 65/100 (weight 16 → 10.4 pts)

**Status:** ⚠ Partial

**Strengths:** `bronze.dq_rejections` is listed in the table index with a brief purpose description (centralised DQ rejection store).

**Gaps:**
- No mart layer tables documented — no entries for `v_purchase_by_supplier` (materialized view) or `v_purchase_per_stock_item` (view). Reference data dictionary documents `dim.supplier` and `dim.stock_item` which also serve as mart-adjacent serving artifacts.
- No full column-level entry for `bronze.dq_rejections` (at least `rejection_key`, `dq_rule_id`, `batch_id`, `lineage_key`, `severity`, `message` columns should be documented).
- No SCD-2 glossary section — reference includes a brief glossary explaining `valid_from`, `valid_to`, `is_current_row` semantics and the sentinel row pattern (key=0 for unresolved SKs). This is important for new consumers of the dimension tables.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add silver_dim.supplier column-level entry with all SCD-2 control columns | §Dimensions | +5 pts |
| 2 | Add silver_dim.stock_item column-level entry with all 14+ attribute columns | §Dimensions | +5 pts |
| 3 | Add full column-level entry for bronze.dq_rejections (5+ columns) | §DQ | +3 pts |
| 4 | Add mart view entries for v_purchase_by_supplier and v_purchase_per_stock_item | §Mart | +3 pts |
| 5 | Add SCD-2 glossary section explaining valid_from/valid_to/is_current_row and sentinel key=0 | §Glossary | +2 pts |
| 6 | Justify date_key DATE vs INT design choice in fact_purchase entry | §Fact | +1 pt |

---

## Priority Actions

1. **Add dimension table entries** — document `silver_dim.supplier` and `silver_dim.stock_item` with all columns including SCD-2 control columns (`valid_from`, `valid_to`, `is_current_row`, `lineage_key`). Even if ETL is externally owned, the DDL is a Purchase product responsibility. Worth up to **+10 pts**.
2. **Add dq_rejections column table** — complete the `bronze.dq_rejections` section with a full column-level table. This is referenced in DQR requirements and the validation report. Worth up to **+3 pts**.
3. **Add mart view entries** — even if the mart views are SELECT-only, documenting their column schemas makes the serving layer discoverable via the data dictionary. Worth up to **+3 pts**.

---

*Report generated by migvisor-task-checker-data-dictionary on 2026-09-18*
