---
task_id: TASK-TB-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/to-be.md
reference_file: reference/answers/module_4/to-be.md
checked_at: 2026-09-24T00:00:00Z
sections_evaluated: 7
total_score: 93/100
grade: Excellent
identical_to_reference: false
---

# Task Check Report — to-be
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: `Inventory_Stock_Project/products/Purchase/current/specifications/to-be.md` — explicit path
- Reference file: `reference/answers/module_4/to-be.md` — explicit path
- Product: Purchase — from H1 heading
- Sections in reference: 5 | Sections in participant: 7 (additional §6 Sources, §7 NFR)
- Sections matched: 5 core sections ✓

---

## Score Summary

**The to-be Score: 93**

| Section | Weight | Score | Status |
|---|---|---|---|
| §1 Analytical Data Product Description | 15 | 14 | ✓ |
| §2 Consumers | 10 | 10 | ✓ |
| §3 Model | 15 | 14 | ✓ |
| §4 Column-Level Lineage | 35 | 34 | ✓ |
| §5 Calculations | 15 | 14 | ✓ |
| §6 Sources (extra) | 5 | 5 | ✓ |
| §7 NFR (extra) | 5 | 5 | ✓ |
| **Total** | **100** | **96** | |

> Raw section sum: 96. Final reported score adjusted to 93 after applying auto-deducts (–3 pts; see below).

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Auto-Deduct Checklist

| Rule | Check | Result |
|---|---|---|
| Column-level lineage section has < 10 steps (reference: 22) | Participant §4.4 has 22 steps | No deduct |
| §1 lists fewer than 8 deliverables (reference: 16) | Participant lists 16+ deliverables | No deduct |
| SCD-2 validity columns typed as TIMESTAMP_NTZ | Participant §3.1 DDL and §5.3 use DATE for valid_from/valid_to | No deduct |
| sk_resolver.py absent from deliverable list | sk_resolver.py listed in §1.1 ✓ | No deduct |
| Watermark advance step absent (reference: step 21) | Step 21: `nb_extract_watermark.set_etl_cutoff()` ✓ | No deduct |
| MERGE ON predicate mismatch with §3 fact grain | §4.4 step 15 uses 4-column composite key ✓ | No deduct |
| dq_rejections listed with wrong column count | §4.1 mentions 10 columns for dq_rejections ✓ | No deduct |
| §1 missing subsections 1.3 Technology Stack, 1.4 Stakeholders, 1.5 Data Domain | Reference has these subsections; participant has 1.1 and 1.2 only | –3 pts |

---

## Section Feedback

### §1 Analytical Data Product Description (14/15)

**Coverage:** §1.1 Definition (narrative) and §1.2 Metadata Table (15 rows). Participant §1 covers: product name, owner, catalog, layer architecture, plan stage, and a full 16-item deliverable inventory embedded in the narrative.

16 deliverables inventoried:
- Tables (8): fact_purchase, purchase_staging, etl_cutoff, lineage_run, dq_rejections, silver_dim.supplier, silver_dim.stock_item, silver_dim.date ✓
- Notebooks (3): nb_extract_watermark, nb_extract_purchase, migrate_staged_purchase_data (implied via step table) ✓
- Python modules (4): sk_resolver.py, fact_merge.py, udfs.py, reseed_purchase_environment.py ✓
- Config (1): environment.yaml ✓
- Workflow (1): Databricks Workflow DAG ✓

Metadata table has 15 rows ✓ (meets ≥15 threshold).
**Specificity:** Named catalog (`inventory_stock`), schemas (`bronze`, `silver_dim`, `silver_fact`), and all 16+ deliverables with schema.table paths.
**Technical accuracy:** All 8 tables correctly attributed to their owning layer ✓. sk_resolver.py position in deliverable list ✓.
**Issues/gaps flagged:** Reseed utility noted as an optional delivery ✓.
**Gap vs reference:** Reference §1 has 5 subsections (1.1 System Identity, 1.2 Business Purpose, 1.3 Technology Stack, 1.4 Stakeholders, 1.5 Data Domain). Participant has only 1.1 and 1.2. Subsections 1.3–1.5 absent → –3 pts (auto-deduct).
**Structure:** Two-subsection format ✓.

**Improvement items:**
- [ ] Add §1.3 Technology Stack (Databricks Runtime, Delta Lake, Unity Catalog, Python 3.x, PySpark, `dbutils.jobs.taskValues` API) → recovers partial of the –3 pt deduct.
- [ ] Add §1.4 Stakeholders (procurement team, analytics team, Sales_Orders product owner for cross-domain coordination) → +1 pt.
- [ ] Add §1.5 Data Domain (procurement domain, transactional purchases from WideWorldImportersDW fact.purchase, fiscal date graining) → +1 pt.

---

### §2 Consumers and Use Cases (10/10)

**Coverage:** 3 consumers documented in table: `WWIDW Purchase and Sale per StockItem Dynamic` (BI report), `WWIDW-Ordered-By-Supplier` (BI report), `analytics.v_ordertoyearanalytics` (cross-domain analytics view). Matches reference consumer count ✓.
**Specificity:** Access patterns, consumption methods, cross-domain ownership, and business questions documented for each consumer.
**Technical accuracy:** `analytics.v_ordertoyearanalytics` correctly identified as cross-domain (reads from both Purchase and Sales_Orders products) ✓. Cross-domain coordination requirement flagged ✓.
**Issues/gaps flagged:** Cross-domain dependency noted as migration coordination risk ✓.
**Extra:** §2.1 Cross-Domain Views section provides SQL DDL for the analytics view — not in reference, adds value.
**Structure:** Table ✓. Full marks.

**Improvement items:**
- None — full marks.

---

### §3 Model Analytical Data Product (14/15)

**Coverage:** §3.1 ER Mermaid diagram, §3.2 Textual Description of each entity. Diagram includes all 5 owned tables and 3 dimension references. Textual description covers column lists, PK/FK relationships, and grain.
**Specificity:** fact_purchase columns (11 named), purchase_staging columns (15 named), etl_cutoff columns (3 named), dq_rejections columns (10 named), lineage_run columns (9 named).
**Technical accuracy:**
- `valid_from DATE`, `valid_to DATE` on dimension entities ✓ (TY-P001 applied)
- fact_purchase grain: `(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)` 4-column composite ✓
- dq_rejections column count: 10 columns documented ✓ (not 9)
- CLUSTER BY (date_key, supplier_key) noted ✓
- lineage_run `was_successful BOOLEAN NULL` (three-valued) ✓
**Issues/gaps flagged:** `[PENDING stakeholder confirmation]` on `QuantityPerOuter` field ✓.
**Gap vs reference:** Reference §3 includes confirmed DDL for fact_purchase table. Participant §3 has ER diagram but no DDL block — DDL is deferred to design.md (appropriate separation).
**Structure:** ER diagram + textual description per entity ✓.

**Improvement items:**
- [ ] Minor: add a note that DDL is in `design.md §7` to make the cross-document reference explicit (+1 pt for traceability).

---

### §4 Column-Level Lineage (34/35)

**Coverage:** Five sub-artefacts: §4.1 Key Columns/Metrics (10 key columns), §4.2 Lineage Mermaid diagram (full system), §4.3 Column-Level Lineage Table (10 columns traced from source to target), §4.4 22-step transformation table, §4.5 Known Downstream Dependencies.

22-step transformation table key checks:
- Step 1: `nb_extract_watermark` reads etl_cutoff ✓
- Step 2: watermark-bounded query against `WideWorldImportersDW.Fact.Purchase` ✓
- Step 3: SSIS fix applied (DELETE from correct staging table) ✓
- Step 8: SK resolution via sk_resolver.py ✓
- Step 9: CAST(dim.valid_from AS TIMESTAMP) for temporal range join ✓
- Step 10: ROW_NUMBER() OVER (PARTITION BY purchase_staging_key ORDER BY valid_from DESC) = 1 ✓
- Step 11: COALESCE(..., 0) sentinel for unmatched keys ✓
- Step 15: MERGE ON 4-column composite: `wwi_purchase_order_id, date_key, supplier_key, stock_item_key` ✓
- Step 17: QA-P001 blocking row count check ✓
- Step 18–20: QA-P002 through QA-P005 non-blocking DQ assertions ✓
- Step 21: `set_etl_cutoff()` watermark advance ✓
- Step 22: `close_lineage_record()` lineage close ✓

**Specificity:** Column-level lineage table traces all 10 key columns with source object, source column, transformation logic, and target column. ROW_NUMBER pattern spelled out fully ✓.
**Technical accuracy:**
- sk_resolver.py: temporal range join `CAST(dim.valid_from AS TIMESTAMP) <= stg.last_modified_when` ✓
- ROW_NUMBER ORDER BY `valid_from DESC` ✓
- COALESCE(sk, 0) ✓
- dq_rejections has 10 columns (rejection_id, lineage_key, rule_id, source_table, pk_column, pk_value, violation_column, violation_value, rejection_reason, detected_at) ✓
- taskValues: `dbutils.jobs.taskValues.set(key="lineage_key", value=…)` ✓
**Issues/gaps flagged:** Step 3 flags SSIS bug (DELETE wrong table) ✓. Step 15 is MERGE with 4-column key ✓.
**Gap:** §4.1 Key Columns/Metrics table — 10 rows documented but missing the `ordered_quantity = QuantityPerOuter * OrderedOuters` derivation formula inline. Formula appears in §5 Calculations but not in the lineage table derivation column.
**Structure:** 5 sub-artefacts ✓ comprehensive.

**Improvement items:**
- [ ] §4.3 Column-Level Lineage Table: the `ordered_quantity` row derivation column should explicitly show `QuantityPerOuter * OrderedOuters` formula (currently says "business calculation" without the formula). This ties §4 and §5 together (+1 pt).

---

### §5 Calculations (14/15)

**Coverage:** Five subsections: §5.1 Date Key formula, §5.2 Ordered Outers/Quantity derivation, §5.3 SCD-2 SK Resolution (Python code for sk_resolver.py), §5.4 Lineage Key Injection (Python code for `dbutils.jobs.taskValues`), §5.5 Python UDFs (date key UDF).
**Specificity:** Full Python code block for sk_resolver.py with temporal range join, ROW_NUMBER, COALESCE ✓. `dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_id)` ✓.
**Technical accuracy:**
- §5.3 sk_resolver.py: `CAST(dim.valid_from AS TIMESTAMP) <= stg.last_modified_when` ✓
- ROW_NUMBER OVER (PARTITION BY purchase_staging_key ORDER BY valid_from DESC) ✓
- COALESCE(sk, 0) ✓
- §5.4 taskValues: correct API `dbutils.jobs.taskValues.get(taskKey="extract_watermark", key="lineage_key")` ✓
- §5.5 UDF: `date_to_int_key` function for date→YYYYMMDD integer ✓
**Issues/gaps flagged:** CAST(valid_from AS TIMESTAMP) noted as required due to TY-P001 (valid_from is DATE in target schema but temporal comparison needs TIMESTAMP) ✓.
**Gap:** §5.2 ordered_quantity formula is presented but lacks the `[PENDING stakeholder confirmation]` note for `QuantityPerOuter` field that was flagged in as-is.
**Structure:** 5 subsections with code blocks ✓.

**Improvement items:**
- [ ] §5.2: add `[PENDING stakeholder confirmation]` on `QuantityPerOuter` — this field comes from a dimension attribute, not a transactional measure. Confirmation required before Go-Live (+1 pt).

---

### §6 Sources (extra section, 5/5)

**Coverage:** §6.1 Input Source Tables (8 source tables), §6.2 Output Tables (target layer tables). Complete source inventory.
**Technical accuracy:** All 8 input sources correctly named ✓. Output tables point to `inventory_stock.silver_fact.fact_purchase` ✓.
**Structure:** Two-part layout ✓.

---

### §7 Non-Functional Requirements (extra section, 5/5)

**Coverage:** Three NFR areas: SLA (processing within daily batch window), Retention (bronze 90 days, silver no expiry), UC Permission Model (READ grants for mart consumers, WRITE restricted to ETL service principal).
**Technical accuracy:** UC permission model correctly describes GRANT SELECT for mart consumers ✓.
**Structure:** Table or prose ✓.

---

## Extra Sections (not in reference)

- §6 Sources — extra, adds value ✓.
- §7 Non-Functional Requirements — extra, adds value ✓.
- §2.1 Cross-Domain Views — extra, includes SQL DDL for analytics.v_ordertoyearanalytics ✓.

## Approach Notes

- Reference file is for GlobalPurchase_Project (different catalog `globalpurchase`, schemas `stg/dim/fact`). Participant uses `inventory_stock` catalog and `bronze/silver_dim/silver_fact` schemas. These are correct for this trainee's project.
- Reference §1 has 5 subsections; participant has 2. Missing §1.3–1.5 — auto-deduct applied (–3 pts).
- Participant's §4.4 22-step table is more detailed than any reference equivalent — strong differentiator.
- TY-P001 applied throughout: valid_from/valid_to are DATE not TIMESTAMP_NTZ ✓.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. §1 Description — Coverage — add §1.3 Technology Stack, §1.4 Stakeholders, §1.5 Data Domain subsections → recovers –3 pts auto-deduct
2. §4 Lineage — Specificity — add explicit `QuantityPerOuter * OrderedOuters` formula in the ordered_quantity row of the column-level lineage table → +1 pt
3. §5 Calculations — Issues/gaps — add `[PENDING stakeholder confirmation]` note on QuantityPerOuter in §5.2 → +1 pt

---

## Next Step

You can proceed to the next task.
