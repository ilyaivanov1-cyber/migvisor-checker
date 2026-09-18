---
task_id: TASK-DE-001
skill: migvisor-task-checker-design
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/design.md
reference_file: ./reference/answers/module_5/development_plan/design.md
generated: 2026-09-18
total_score: 74/100
grade: Acceptable
---

# TASK-DE-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/design.md`  
**Reference file:** `./reference/answers/module_5/development_plan/design.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Design Score: 74/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| 1. Entity Overview / Architecture Schema | 25 | 80/100 | 20.0 | ✓ |
| 2. Entity-Relationship Map | 25 | 60/100 | 15.0 | ⚠ |
| 3. Attribute Tables (Column-Level Design) | 25 | 90/100 | 22.5 | ✓ |
| 4. Table DDL / Serving Layer | 25 | 58/100 | 14.5 | ⚠ |
| **Subtotal** | | | **72.0** | |
| Auto-deducts | | | **−2** | |
| **Total** | | | **74/100** | |

**Grade: Acceptable**

> **Weight calculation:** N = 4, base_weight = floor(100/4) = 25, remainder = 0 → all sections 25 pts.

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| Entity-Relationship Overview (schema table) | §1.1 Entities table | Partial |
| Logical relationship map | No Mermaid or ASCII ER diagram | Missing |
| Join keys table | Column descriptions only | Partial |
| Table DDL (`CREATE TABLE IF NOT EXISTS`) | Attribute tables (no DDL) | Partial |
| Serving layer (mart views DDL) | Not present | Missing |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No physical DDL section (CREATE TABLE statements missing) — design has column tables but no executable DDL for any of the 8 tables | −2 pts | Yes — reference provides full `CREATE TABLE IF NOT EXISTS` with COMMENTs, CLUSTER BY, TBLPROPERTIES for fact table; trainee has no DDL at all |

**Total auto-deducts: −2 pts**

---

## Section Feedback

### 1. Entity Overview / Architecture Schema — 80/100 (weight 25 → 20.0 pts)

**Status:** ✓ Present

**Strengths:** §1.1 Entities table covers all 8 required Delta tables: `silver_fact.fact_purchase`, `silver_dim.supplier`, `silver_dim.stock_item`, `silver_dim.date`, `bronze.purchase_staging`, `bronze.etl_cutoff`, `bronze.lineage_run`, `bronze.dq_rejections`. Each row has Layer, Schema, Table Name, Type, and Description columns. The medallion structure (bronze/silver_dim/silver_fact) is clearly communicated. "Externally owned" designation for the 3 dimension tables is accurate and important.

**Gaps vs reference:** Reference leads with a 4-schema table (`stg`, `dim`, `fact`, `mart`) showing each schema's role and object types — a clean architecture overview that makes the medallion structure instantly visible. Trainee mixes all entities into one flat table. Reference also includes the mart schema (serving layer with views/materialized views) — trainee has no mart layer documented in the design. The "Externally owned" flag for dimensions is a trainee-specific concept not in reference, but it creates ambiguity about who owns the DDL.

---

### 2. Entity-Relationship Map — 60/100 (weight 25 → 15.0 pts)

**Status:** ⚠ Partial

**Strengths:** The §1.1 Entities table implicitly encodes relationships via the Schema column — grouping tables by layer (bronze control, silver dimension, silver fact) conveys the data flow direction. Foreign key relationships are documented in §1.2 Attributes (e.g., `date_key` FK → `silver_dim.date.date`, `supplier_key` FK → `silver_dim.supplier.supplier_key`, `lineage_key` FK → `bronze.lineage_run.lineage_key`).

**Gaps:** Reference has an explicit ASCII logical relationship map showing data flow arrows:
```
stg.etl_cutoff ──► (controls watermark)
stg.purchase_staging ──► fact.purchase
dim.date, dim.supplier, dim.stock_item ──► fact.purchase
stg.dq_rejections ◄── ETL pipelines
mart.* ──► fact.purchase + dim.*
```
And a join keys table listing all 7 parent→child relationships with join column names. Trainee has no equivalent ER diagram or join keys table. This section is a significant structural gap — without a relationship map the design cannot be reviewed for referential integrity completeness at a glance. A reviewer must extract join keys from individual column descriptions, which is error-prone.

---

### 3. Attribute Tables (Column-Level Design) — 90/100 (weight 25 → 22.5 pts)

**Status:** ✓ Present

**Strengths:** The trainee's attribute tables are the strongest part of the design. Documented for all tables in scope:
- `silver_fact.fact_purchase`: 11 columns with Type, Nullable, Description
- `bronze.purchase_staging`: 15 columns (more than reference's staging table) including `purchase_staging_key` IDENTITY, `wwi_supplier_id`, `wwi_stock_item_id`, `last_modified_when`, `_extracted_at_utc`
- `bronze.lineage_run`: 9 columns with proper IDENTITY PK, was_successful BOOLEAN, source_system_cutoff_time
- `bronze.etl_cutoff`: `table_name` PK, `cutoff_time` — correct minimal schema
- Also includes dimension and DQ tables implied by the §1.1 listing

The attribute tables are more detailed than reference — reference provides a single CREATE TABLE DDL for fact.purchase with only 10 columns, whereas trainee documents all 8 tables at column level. This is a value-add.

**Gaps:** Reference DDL shows `date_key` as `INT NOT NULL` (YYYYMMDD integer) while trainee shows `date_key` as `DATE NOT NULL` — this is a design decision that should be explicitly documented and justified. The reference FK join from dim.date uses `date_key (YYYYMMDD integer)` while trainee uses a `DATE` type, which changes the join semantics and DDL completely.

---

### 4. Table DDL / Serving Layer — 58/100 (weight 25 → 14.5 pts)

**Status:** ⚠ Partial

**Strengths:** Trainee has column-level specifications sufficient to derive DDL. The `BIGINT GENERATED ALWAYS AS IDENTITY` pattern is documented for `purchase_key`, `purchase_staging_key`, `lineage_key`. NOT NULL / NULL constraints are specified per column.

**Gaps:**
1. **No physical DDL section** — reference provides complete `CREATE TABLE IF NOT EXISTS globalpurchase.fact.purchase (...)` with USING DELTA, CLUSTER BY, TBLPROPERTIES, and per-column COMMENTs. Trainee has no equivalent DDL for any table. This is critical for the SmartBuilder generate-db skill which needs exact DDL to produce correct SQL files.
2. **No serving layer** — reference includes mart schema objects (materialized view `v_purchase_by_supplier`, regular view `v_purchase_per_stock_item`) in the design. Trainee has no mart layer in the design at all — not even a mention that mart views are out of scope.
3. **CLUSTER BY vs PARTITIONED BY** — trainee §1.1 documents `CLUSTER BY (date_key, supplier_key)` for fact_purchase in the description field, but this is not in a DDL statement where it can be validated.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add logical ER diagram / relationship map with data-flow arrows and join keys table | §ER Map | +8 pts |
| 2 | Add Table DDL section with full `CREATE TABLE IF NOT EXISTS` for all 8 tables (USING DELTA, CLUSTER BY, TBLPROPERTIES, COMMENT per column) | §DDL | +7 pts |
| 3 | Add mart/serving layer section with DDL for at least 2 mart views (v_purchase_by_supplier, v_purchase_per_stock_item) | §Serving | +3 pts |
| 4 | Justify date_key type decision (DATE vs INT YYYYMMDD) — document explicitly | §Attribute Tables | +2 pts |
| 5 | Add schema-level architecture table (4 schemas with roles) before entity table | §Overview | +2 pts |

---

## Priority Actions

1. **Add ER relationship map** — create an ASCII diagram showing data flow from staging → fact, dimension → fact, lineage → all tables. Include join keys table with 7 parent→child relationships. Worth up to **+8 pts**.
2. **Add Table DDL section** — provide executable `CREATE TABLE IF NOT EXISTS` for at least `fact_purchase` and `purchase_staging` with USING DELTA, CLUSTER BY, TBLPROPERTIES (autoOptimize, CDF), and per-column COMMENTs. This is the primary deliverable for SmartBuilder's generate-db skill. Worth up to **+7 pts**.
3. **Add mart/serving layer** — document at minimum `v_purchase_by_supplier` (materialized view) and `v_purchase_per_stock_item` (view) in a §Serving section with DDL. Worth up to **+3 pts**.

---

*Report generated by migvisor-task-checker-design on 2026-09-18*
