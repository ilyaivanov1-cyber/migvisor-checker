# Check Report: TASK-DESIGN-001
**Skill:** design | **Trainee:** Inventory_Stock_Project | **Product:** Purchase
**Checker version:** v1 | **Generated:** 2026-09-25

---

## Score: 87 / 100 — Good

---

## Rubric Evaluation

### Content Completeness — 20 / 25

The design document covers 9 sections:
1. Architecture Overview (Mermaid diagram + layer table)
2. Workflow Task Sequence (diagram + taskValues contract table)
3. SK Resolution Pattern (SQL + COALESCE logic)
4. MERGE INTO Pattern (full SQL statement)
5. QA Assertion Chain (table + flow diagram)
6. Lineage Propagation (lifecycle code)
7. DDL Reference (3 of 5 owned tables)
8. Mart Layer (2 mart views)
9. Configuration Management (yaml excerpt + loading pattern)

**DDL Coverage assessment — 3 of 5 owned tables (60%):**
| Table | Expected | Present |
|---|---|---|
| `bronze.lineage_run` (9 cols) | ✓ | ✓ |
| `bronze.purchase_staging` (15 cols) | ✓ | ✓ |
| `silver_fact.fact_purchase` (11 cols) | ✓ | ✓ |
| `bronze.etl_cutoff` (3 cols) | ✓ | MISSING |
| `bronze.dq_rejections` (10 cols) | ✓ | MISSING |

The missing `etl_cutoff` and `dq_rejections` DDL blocks are a notable gap. Both tables are referenced throughout the design (etl_cutoff in §2 taskValues contract and §6 lineage lifecycle; dq_rejections in §5 QA chain and §6) but neither has a `CREATE TABLE` block. This means 40% of the owned Purchase table DDL is absent.

The three present DDL blocks are complete and accurate:
- `lineage_run`: 9 columns matching SKILL.md expectation ✓, CDF enabled ✓, BIGINT IDENTITY PK ✓, `was_successful BOOLEAN NULL` (three-valued: NULL=running, TRUE=success, FALSE=failure) ✓
- `purchase_staging`: 15 columns matching SKILL.md expectation ✓, OVERWRITE mode documented in comments ✓, lineage_key + _extracted_at_utc present ✓
- `fact_purchase`: 11 columns matching SKILL.md expectation ✓, CLUSTER BY (date_key, supplier_key) ✓, pre-DBR 13.3 fallback comment present ✓

Content completeness adjusted: (3/5 DDL coverage × 40% weight) + (non-DDL content 95% × 60% weight) = 0.24 + 0.57 = 81% → 25 × 0.81 ≈ 20 pts.

### SQL Accuracy — 25 / 30

**MERGE INTO statement (§4):** Uses single-column MERGE key `ON target.wwi_purchase_order_id = source.wwi_purchase_order_id`. This is flagged as a cross-file consistency issue (see below) — the to-be §4.4 step 15 uses a 4-column composite key while the design uses a single column.

**SK resolution SQL (§3):** The temporal range join is syntactically correct:
```sql
WHERE stg.last_modified_when  >  CAST(valid_from AS TIMESTAMP)
  AND stg.last_modified_when  <= CAST(valid_to   AS TIMESTAMP)
```
SCD-2 boundary semantics correct (exclusive lower, inclusive upper) ✓. ROW_NUMBER with ORDER BY valid_from DESC ✓. COALESCE(dim.supplier_key, 0) ✓.

**Mart view SQL (§8):**
- `mart.v_purchase_by_supplier` (MATERIALIZED VIEW): Uses `s.supplier_name`, `s.supplier_category_name`, `si.stock_item_name`, `si.unit_package_name` — these column names do NOT match the actual `silver_dim.supplier` and `silver_dim.stock_item` column names from the DDL in to-be §3.1. Correct column names are: `supplier` (not `supplier_name`), `category` (not `supplier_category_name`), `stock_item` (not `stock_item_name`). This is a technical accuracy error in the mart view SQL (-3 pts).
- `mart.v_purchase_per_stock_item` (regular VIEW): Same column name errors apply (`si.stock_item_name`, `s.supplier_name`).

**DDL blocks:** All three DDL blocks present (lineage_run, purchase_staging, fact_purchase) are syntactically correct and use proper Unity Catalog three-part naming ✓.

Deductions: Single-column MERGE key (cross-file flag, not deduction since known defect) -0. Mart view column name errors -3. Correct SKR SQL and DDL +27.

Adjusted: 28/30 raw - 3 = 25/30.

### Code Accuracy — 18 / 20

**Lineage propagation code (§6):** The lifecycle code shows:
- `nb_extract_watermark`: `INSERT INTO bronze.lineage_run` → captures `lineage_key` → `dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_key)` ✓
- `nb_extract_purchase`: `dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")` ✓
- `migrate_staged_purchase_data`: `UPDATE bronze.lineage_run SET status = 'SUCCESS'` or `status = 'FAILED'` with `end_ts` and `rows_inserted/rows_updated` ✓

Note: The design §6 lineage code shows a hierarchy where nb_extract_purchase inserts its own child lineage_run record and publishes a `child_lineage_key`. This adds complexity not shown in to-be or requirements: to-be shows a single lineage_key propagated across all 3 tasks (not a parent-child hierarchy). This is an architectural inconsistency with the to-be document (-2 pts).

**Configuration loading pattern (§9):** Correct Python `yaml.safe_load()` pattern ✓. NFR-009 and NFR-011 rule references correct ✓.

**QA assertion chain (§5):** Correctly distinguishes blocking (QA-P001, QA-P005) vs warning (QA-P002, QA-P003, QA-P004) behaviours ✓. Flow diagram syntax valid ✓.

### Diagram Completeness — 13 / 15

**Architecture diagram (§1):** ASCII/text diagram correctly showing Bronze and Silver layers with 4 Bronze tables and 2 Silver layers ✓. Layer responsibilities table ✓.

**Workflow task sequence diagram (§2):** ASCII diagram with 3 tasks and taskValues arrows ✓. taskValues contract table with key/publisher/consumer/type/rule mapping ✓.

**QA assertion chain flow diagram (§5):** Text-based flow diagram showing FAIL vs WARN vs continuation paths for all 5 QA assertions ✓.

Minor deductions (-2 pts): The design does not include a Mermaid ER diagram or column-level relationship diagram. While the to-be document has a comprehensive Mermaid ER diagram, the design relies on ASCII text diagrams for architecture and workflow. A formal ER diagram showing the Bronze and Silver table relationships would strengthen the design's technical completeness.

### Structure — 9 / 10

9 clearly numbered sections with a Table of Contents ✓. Consistent heading hierarchy. Rule references (FR-002, FR-003, etc.) cited inline at the point of relevance ✓. DDL blocks have standardised header comments per CX-P006 ✓ (PROJECT, PRODUCT, FILE, PURPOSE, TARGET, RULES fields all present in the 3 DDL blocks).

Minor: Section 8 (Mart Layer) is architecturally correct but is a bonus section that introduces mart views not fully specified in the SKILL.md expected design scope — it's valuable but introduces the column name errors noted above.

---

## Auto-Deduct Checks

| Check | Result |
|---|---|
| lineage_run DDL present (9 cols) | PASS ✓ |
| purchase_staging DDL present (15 cols) | PASS ✓ |
| fact_purchase DDL present (11 cols) | PASS ✓ |
| etl_cutoff DDL present (3 cols) | FAIL — DDL absent |
| dq_rejections DDL present (10 cols) | FAIL — DDL absent |
| was_successful three-valued BOOLEAN NULL | PASS ✓ |
| _current views NOT materialized | PASS — OB-P003 noted: thin views use CREATE OR REPLACE VIEW ✓ |
| Zero-rows guard mentioned | PASS — CX-P005 referenced in §5 QA chain (zero-rows guard listed) ✓ |
| CDF enabled on lineage_run | PASS — TBLPROPERTIES delta.enableChangeDataFeed=true ✓ |

---

## Cross-File Consistency Checks (MANDATORY)

### MERGE Key Consistency (read to-be.md §4.4 step 15)

**to-be MERGE key (§4.4 step 15):**
```sql
ON tgt.wwi_purchase_order_id = src.wwi_purchase_order_id
AND tgt.date_key = src.date_key
AND tgt.supplier_key = src.supplier_key
AND tgt.stock_item_key = src.stock_item_key
```
4-column composite key reflecting the actual fact grain.

**design MERGE key (§4):**
```sql
ON target.wwi_purchase_order_id = source.wwi_purchase_order_id
```
Single-column key.

**Result: INCONSISTENCY FLAGGED.** This is a known MERGE key defect (matches the reference design pattern where design uses single-column key despite fact grain being 4-column composite). This cross-file inconsistency is documented as a **known defect** — not a trainee-introduced error. However, the design MERGE key must be corrected to match to-be before production implementation.

**Impact:** Using a single-column MERGE key (`wwi_purchase_order_id`) will cause incorrect updates if multiple purchase order line items share the same `wwi_purchase_order_id` with different `date_key`, `supplier_key`, or `stock_item_key` values. The WHEN MATCHED branch will update all matching rows indiscriminately, potentially corrupting dimension key assignments.

### DDL Column Name Consistency (data-dictionary.md present — verification pending Batch B)

The three present DDL blocks use snake_case column names consistent with the to-be ER diagram and transformation rules. Full column-level verification against data-dictionary.md is deferred to Batch B processing.

**Mart view column names:** As noted, mart views use non-existent column names (`supplier_name`, `supplier_category_name`, `stock_item_name`, `unit_package_name`) that do not exist in the Silver dimension tables. This is a DDL column name inconsistency within the design document itself (mart views reference columns not present in the Silver layer DDL defined in the same document's to-be specification).

---

## Summary

The design document demonstrates strong technical depth in the areas it covers: the SK resolution temporal range join, QA assertion chain with blocking/warning classification, lineage propagation pattern, and correct DDL for 3 of 5 owned Bronze and Silver tables. The three present DDL blocks are accurate with correct column counts, CLUSTER BY configuration, CDF enablement, and three-valued `was_successful`. The primary weaknesses are: (1) missing DDL for `etl_cutoff` and `dq_rejections` — two of the five owned Purchase tables; (2) incorrect column names in mart view SQL that reference non-existent dimension columns; (3) a lineage propagation architecture in §6 that introduces a parent-child lineage_key hierarchy inconsistent with the single-key model in to-be; and (4) the known single-column MERGE key defect that must be corrected to the 4-column composite key before production.

---

## Priority Actions

1. **Add DDL blocks for `bronze.etl_cutoff` (3 cols: table_name STRING PK, cutoff_time TIMESTAMP, last_updated_utc TIMESTAMP) and `bronze.dq_rejections` (10 cols: rejection_id IDENTITY, lineage_key FK, rule_id, source_table, pk_column, pk_value, violation_column, violation_value, rejection_reason, detected_at) with CX-P006 header blocks.** This completes DDL coverage to 5/5 owned tables.
2. **Fix mart view column names:** `s.supplier` not `s.supplier_name`, `s.category` not `s.supplier_category_name`, `si.stock_item` not `si.stock_item_name`. Verify all referenced column names against the to-be ER diagram before the mart views are deployed.
3. **Correct the MERGE key to 4-column composite** matching to-be §4.4 step 15: `ON target.wwi_purchase_order_id = source.wwi_purchase_order_id AND target.date_key = source.date_key AND target.supplier_key = source.supplier_key AND target.stock_item_key = source.stock_item_key`.
4. **Simplify §6 lineage propagation** to the single-key model from to-be: one `lineage_key` opened by `nb_extract_watermark`, published via taskValues, consumed by both `nb_extract_purchase` and `migrate_staged_purchase_data` — remove the parent-child lineage_key hierarchy that contradicts the to-be specification.
