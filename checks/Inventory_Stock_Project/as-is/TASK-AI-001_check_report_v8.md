---
task_id: TASK-AI-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md
reference_file: reference/answers/module_2/1 as-is.md
checked_at: 2026-09-24T00:00:00Z
sections_evaluated: 6
total_score: 94/100
grade: Excellent
identical_to_reference: false
note: v7 already existed; this report uses v8 suffix per no-overwrite rule.
---

# Task Check Report — as-is
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: `Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md` — explicit path
- Reference file: `reference/answers/module_2/1 as-is.md` — explicit path
- Product: Purchase — from H1 heading
- Sections in reference: 6 | Sections in participant: 6 (matched: 6)
- Point weights: auto-calculated — §1:10, §2:10, §3:20, §4:30, §5:20, §6:10

---

## Score Summary

**The as-is Score: 94**

| Section | Weight | Score | Status |
|---|---|---|---|
| §1 Definition | 10 | 9 | ✓ |
| §2 Consumers | 10 | 10 | ✓ |
| §3 Model | 20 | 19 | ✓ |
| §4 Lineage | 30 | 28 | ✓ |
| §5 Calculations | 20 | 19 | ✓ |
| §6 Sources | 10 | 9 | ✓ |
| **Total** | **100** | **94** | |

Auto-deducts applied: none.

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Auto-Deduct Checklist

| Rule | Check | Result |
|---|---|---|
| Metadata table < 10 fields (≥15 required) | Participant has 15 fields | No deduct |
| SSIS truncation bug absent from lineage | Participant names `Integration.Order_Staging` bug in steps 8, 11 | No deduct |
| COALESCE(…, 0) fallback omitted from SCD-2 | Participant includes `COALESCE(s.[Supplier Key], 0)` | No deduct |
| Fewer than 3 entities when reference has > 10 | Participant documents 6 entity types | No deduct |
| SCD-2 tie-breaker direction error | Participant uses `ORDER BY [Valid From]` (ASC default, matches reference) | No deduct |
| Section direction inverted (documents target as source) | Participant correctly describes WideWorldImportersDW as the source | No deduct |

---

## Section Feedback

### §1 Definition (9/10)

**Coverage:** Two subsections — §1.1 narrative definition and §1.2 Metadata Table with 15 rows. Covers domain, system identity, discovery plan stage, and data product classification.
**Specificity:** Names `WideWorldImportersDW`, SQL Server 2014, Databricks Delta Lake, `inventory_stock` catalog, `wwi_purchase_order_id` as natural key.
**Technical accuracy:** Source system and technology stack correctly identified. Discovery mode and plan stage correct. 15-field metadata table meets the ≥15 threshold.
**Issues/gaps flagged:** Scope owner marked `[USER INPUT REQUIRED]` — consistent with scope document ✓.
**Structure:** §1.1 narrative + §1.2 table pattern ✓. Reference uses 1.1 System Identity / 1.2 Business Purpose / 1.3 Technology Stack; participant's structure is different but equivalent.

**Improvement items:**
- [ ] Minor: reference explicitly calls out the composite PK `(Purchase Key, Date Key)` in the definition metadata. Participant can add this to the §1.2 metadata table as "Natural key columns" → (+1 pt).

---

### §2 Consumers (10/10)

**Coverage:** 4 consumers documented: 2 BI reports, 1 cross-domain analytics view, 1 ETL consumer (`migratestagedpurchasedata`). Reference documents 3 downstream consumers.
**Specificity:** Named with access patterns, business questions answered, downstream schema paths.
**Technical accuracy:** Cross-domain analytics dependency correctly characterised. ETL consumer correctly identified as write-then-read pattern.
**Issues/gaps flagged:** Cross-domain coordination requirement noted ✓.
**Structure:** Table with Consumer, Access Pattern, Business Question columns ✓.

**Improvement items:**
- None — full marks (extra ETL consumer is additive value).

---

### §3 Model (19/20)

**Coverage:** §3.1 ER Mermaid diagram with all 6 entities (Purchase, Supplier, StockItem, Date, PurchaseStagingTable, Lineage). §3.2 Textual description for each entity with column lists, relationships, and ownership model.
**Specificity:** Column lists for `fact.purchase` (11 columns), `integration.purchase_staging` (11 columns), dimension keys named. Composite PK pattern documented.
**Technical accuracy:** Cardinalities in ER diagram match the fact-to-dimension grain. `Integration.Supplier` has `[Supplier Key]` (IDENTITY PK) ✓.
**Issues/gaps flagged:** Space-bearing column names in source documented with brackets ✓.
**Structure:** ER diagram + textual description per entity ✓.

**Improvement items:**
- [ ] Reference explicitly shows the confirmed DDL with `CONSTRAINT pk_fact_purchase PRIMARY KEY NONCLUSTERED (Purchase Key, Date Key)`. Add the composite PK DDL notation or note in §3 model to complete the entity model (+1 pt).

---

### §4 Lineage (28/30)

**Coverage:** Four lineage artefacts: ASCII target data flow diagram, key columns/metrics table, Mermaid lineage diagram, column-level lineage table, 11-step transformation table, downstream dependencies. All major lineage requirements present.
**Specificity:** 11 ETL steps documented with source objects, target objects, logic, and notes. Column-level lineage traces 10 key columns from source through transformation to target.
**Technical accuracy:**
- SSIS bug documented in steps 8 and 11: `DELETE FROM Integration.Order_Staging` should be `Integration.Purchase_Staging` ✓
- SCD-2 boundary semantics: `stg.[Last Modified When] > s.[Valid From]` (exclusive) AND `stg.[Last Modified When] <= s.[Valid To]` (inclusive) ✓
- Tie-breaker: `ORDER BY [Valid From]` (ASC default in T-SQL) matches expected ascending order ✓
- COALESCE fallback: `COALESCE(s.[Supplier Key], 0)` ✓ and stock item similarly ✓
- 8 input source tables documented (Supplier, StockItem, Date, City, Customer, Transaction, Employee + Purchase fact) ✓
**Issues/gaps flagged:** SSIS truncation bug called out in both step notes column and as a separate findings note ✓. Downstream downstream dependencies table present ✓.
**Structure:** Lineage section is the richest section with 5 sub-artefacts. Full ✓.

**Improvement items:**
- [ ] §4.3 Column-level lineage table: `supplier_key` derivation could explicitly note that COALESCE to 0 is the fallback when no dimension row matches (currently only in §5.3 Calculations). Duplicating the fallback logic in the lineage table column would tie both artefacts together (+1 pt).
- [ ] §4.4 Transformation table: step 10 (the INSERT from staging) is listed as the core load step but the ETL step table doesn't note the affected row count pattern (`@@ROWCOUNT` or equivalent). Reference mentions row reconciliation count as a lineage metric (+1 pt).

---

### §5 Calculations (19/20)

**Coverage:** Three calculation subsections — §5.1 Date Key (`CONVERT(int, CONVERT(varchar(8), [Invoice Date Key], 112))`), §5.2 Ordered Outers/Quantity (`QuantityPerOuter * OrderedOuters`), §5.3 SCD-2 SK Resolution with full T-SQL code block.
**Specificity:** Full T-SQL for SCD-2 resolution showing boundary predicates, `ORDER BY`, and `COALESCE` fallback. Date key formula is concrete and reproducible.
**Technical accuracy:**
- Date key formula: `CONVERT(int, CONVERT(varchar(8), [Invoice Date Key], 112))` — correct ISO format 112 → YYYYMMDD integer ✓
- SCD-2 boundary: `> [Valid From]`, `<= [Valid To]` ✓
- Tie-breaker: `ORDER BY [Valid From]` (T-SQL `TOP(1)` pattern) ✓
- `COALESCE(s.[Supplier Key], 0)`: fallback to sentinel 0 ✓
**Issues/gaps flagged:** T-SQL `TOP(1)` correlated sub-query noted as requiring migration to `JOIN + ROW_NUMBER()` per SX-003 ✓.
**Structure:** Three subsections with SQL code blocks ✓.

**Improvement items:**
- [ ] §5.2 `QuantityPerOuter * OrderedOuters`: reference notes that the `QuantityPerOuter` field requires confirmation from a business stakeholder because its source is a dimension attribute rather than a transactional measure. Add a `[PENDING stakeholder confirmation]` marker or note (+1 pt).

---

### §6 Sources (9/10)

**Coverage:** §6.1 Input source tables (8 source tables with schema, column, data types, and scope notes). §6.2 Output tables (target DDL reference). Complete source inventory.
**Specificity:** Named input tables with schema paths (`WideWorldImportersDW.Dimension.Supplier` etc.), key columns identified, scope notes per table.
**Technical accuracy:** All 8 input sources correctly identified ✓. Output table references `silver_fact.fact_purchase` (target layer) ✓.
**Issues/gaps flagged:** `Dimension.Transaction` out-of-scope note ✓. `WideWorldImportersDW.Fact.Purchase` as primary source noted ✓.
**Structure:** Two-part layout with input and output tables ✓.

**Improvement items:**
- [ ] Minor: output table §6.2 could include a mini-DDL showing column types (even abbreviated) rather than just naming columns. Reference includes confirmed DDL for the fact table (+1 pt).

---

## Extra Content (not in reference)

- §2 includes ETL consumer (`migratestagedpurchasedata`) not in reference — extra value, not penalised.
- §4 includes both ASCII data-flow and Mermaid lineage diagrams — more than reference minimum, not penalised.
- §4 includes §4.5 Known Downstream Dependencies (extra section) — additive.

## Approach Notes

- Reference uses subsection titles "System Identity / Business Purpose / Technology Stack"; participant uses "Definition / Metadata Table". Different structure, same content — no deduction per approach policy.
- Reference uses `globalpurchase` catalog; participant uses `inventory_stock`. Different project name — not penalised.
- T-SQL `ORDER BY [Valid From]` without explicit `ASC`/`DESC` is ascending by default — matches expected tie-breaker direction.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. §4 Lineage — Coverage — add COALESCE fallback note explicitly in the column-level lineage table (column derivation) to link §4 and §5 artefacts → +1 pt
2. §3 Model — Specificity — add composite PK DDL notation to the entity model → +1 pt
3. §5 Calculations — Issues/gaps — add `[PENDING stakeholder confirmation]` marker on QuantityPerOuter source → +1 pt

---

## Next Step

You can proceed to the next task.
