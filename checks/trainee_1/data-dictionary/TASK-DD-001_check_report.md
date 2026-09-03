---
task_id: TASK-DD-001
skill: task-checker-data-dictionary
participant_file: trainees/trainee_1/data_dictionary.md
reference_file: reference/data_dictionary.md
product: Sales_Orders
generated: 2026-09-03
total_score: 45/100
grade: Needs Work
---

# TASK-DD-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase Data Product
**Participant file:** `trainees/trainee_1/data_dictionary.md`
**Reference file:** `reference/data_dictionary.md`
**Generated:** 2026-09-03

---

## Score Summary

**The data dictionary Score: 45/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 10 | 91/100 | 9.1 | ✓ Pass |
| stg.purchase_staging | stg.purchase_staging | 10 | 71/100 | 7.1 | ✓ Pass |
| stg.etl_cutoff | stg.etl_cutoff | 10 | 86/100 | 8.6 | ✓ Pass |
| stg.lineage | stg.lineage | 10 | 78/100 | 7.8 | ✓ Pass |
| stg.dq_rejections | stg.dq_rejections | 10 | 76/100 | 7.6 | ✓ Pass |
| dim.supplier (SCD-2) | dim.supplier | 10 | 39/100 | 3.9 | ✗ Below threshold |
| dim.stock_item (SCD-2) | dim.stock_item | 10 | 32/100 | 3.2 | ✗ Below threshold |
| dim.date | dim.date | 10 | 0/100 | 0.0 | ✗ Missing |
| fact.purchase | fact.purchase | 10 | 79/100 | 7.9 | ✓ Pass |
| Glossary: SCD-2 Tracking Columns | Glossary | 10 | 0/100 | 0.0 | ✗ Missing |
| **Subtotal** | | | | **55.2** | |
| Auto-deducts | | | | **−10.0** | |
| **Total** | | | | **45/100** | |

**Grade: Needs Work**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | H1 "Data Dictionary — Sales_Orders" + preamble | exact |
| stg.purchase_staging | `### globalsales.stg.sale_staging` (H3 under Bronze layer H2) | semantic — equivalent staging table |
| stg.etl_cutoff | `### globalsales.stg.etl_cutoff` | exact (H3 structural difference noted) |
| stg.lineage | `### globalsales.stg.lineage` | exact (H3 structural difference noted) |
| stg.dq_rejections | `### globalsales.stg.dq_rejections` | exact (H3 structural difference noted) |
| dim.supplier (SCD-2) | `### globalsales.dim.customer (SCD2)` | semantic — primary SCD-2 dimension |
| dim.stock_item (SCD-2) | `### globalsales.dim.city (SCD2)` | semantic — second SCD-2 dimension |
| dim.date | [MISSING] | missing |
| fact.purchase | `### globalsales.fact.sale` | semantic — central fact table |
| Glossary: SCD-2 Tracking Columns | [MISSING] | missing |
| *(not in reference)* | `### globalsales.mart.v_customer_sales_summary` | extra |

**Structural note:** The reference uses `##` H2 headings per table; the participant uses `##` H2 for layer groupings (Bronze/Staging Layer, Silver/Dimension Layer) and `###` H3 for individual tables. Tables that ARE present as H3 are scored normally; no missing-H2 deduct is applied for them. Only sections with no content at all (dim.date, Glossary) receive the missing-H2 deduct.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No column tables anywhere | −5 pts | **No** — column tables present in all table sections |
| Missing H2 section present in reference but absent in participant | −5 pts each (max −15) | **Yes — dim.date: −5 pts; Glossary: −5 pts = −10 pts** |
| No Type column anywhere | −4 pts | **No** — Type column present throughout |
| No Nullable column anywhere | −3 pts | **No** — Nullable present in staging and fact sections |
| No Description column anywhere | −3 pts | **No** — Description column present throughout |
| No lineage_key anywhere in document | −3 pts | **No** — lineage_key present in stg.lineage and fact.sale sections |
| SCD-2 columns absent from dim tables with no shared table | −2 pts/table (max −4) | **No** — shared SCD-2 columns table IS present at Silver layer intro |

**Total auto-deducts: −10 pts**

---

## Section Feedback

### Header Metadata — 91/100 (weight 10 → 9.1 pts)

**Criteria scored:** Content (90%), Structure (10%)

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product / document name | 35% | 100 | "Sales_Orders" clear in H1 |
| Task ID / traceability tag | 35% | 100 | "TASK-DOCS-002" present in preamble |
| Catalog / platform reference | 20% | 100 | "globalsales Unity Catalog" explicit |
| Version / generation date | 10% | 0 | Absent |

**Strengths:**
- All three primary metadata elements (product name, task ID, catalog) present and clear
- Preamble format `_TASK-DOCS-002 | globalsales Unity Catalog_` provides clean traceability

**Gaps:**
- No generation date or version tag

**Improvement items:**
- [ ] Add a generation date or version line: `_Generated: 2026-09-03 | v1_`

---

### stg.purchase_staging → `### globalsales.stg.sale_staging` — 71/100 (weight 10 → 7.1 pts)

**Criteria scored:** Content (40%), Column Completeness (20%), Nullability (15%), FK References (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 40% | 62/100 | Topic coverage ~75%; descriptions ~70%; no table paragraph |
| Column Completeness | 20% | 75/100 | 9/12 equivalent topics covered; packaging/delivery cols purchase-specific |
| Nullability | 15% | 80/100 | Nullable column present; most values accurate |
| FK References | 15% | 80/100 | `FK → stg.lineage` present on lineage_key |
| Structure | 10% | 70/100 | H3 (not H2); column table present; no intro paragraph |

**Strengths:**
- Source column is an excellent addition (documents extraction origin per column)
- `_extracted_at_utc` and `lineage_key` FK correctly documented
- Watermark column (`last_edited_when`) noted with purpose

**Gaps:**
- No paragraph description before the column table (reference has "Truncated and overwritten on each pipeline run…")
- purchase_order equivalent (`sale_key`) description could clarify it is the source invoice line PK more explicitly

**Improvement items:**
- [ ] Add a one-line paragraph above each table: table purpose, load pattern, and key invariants (e.g., "Truncated and reloaded on each pipeline run; all rows share a constant `lineage_key`")

---

### stg.etl_cutoff → `### globalsales.stg.etl_cutoff` — 86/100 (weight 10 → 8.6 pts)

**Criteria scored:** Content (55%), Column Completeness (20%), Nullability (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 81/100 | 2/2 ref topics covered; descriptions clear; no table paragraph |
| Column Completeness | 20% | 100/100 | Both reference topics present; extra `updated_at_utc` is additive |
| Nullability | 15% | 95/100 | All columns correctly marked N |
| Structure | 10% | 70/100 | H3 (not H2); no intro paragraph |

**Strengths:**
- `updated_at_utc` addition is operationally useful and correctly typed
- `entity_name` description ("PK — e.g. sale, order, customer") is precise and product-adapted

**Gaps:**
- No table description paragraph (reference: "One row per monitored entity. Controls incremental extract boundaries.")

**Improvement items:**
- [ ] Add one-sentence table description above the column table

---

### stg.lineage → `### globalsales.stg.lineage` — 78/100 (weight 10 → 7.8 pts)

**Criteria scored:** Content (55%), Column Completeness (20%), Nullability (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 74/100 | ~88% topic coverage; descriptions present; no table paragraph |
| Column Completeness | 20% | 88/100 | 7/8 reference topics covered; `entity_name` replaced by `pipeline_name` |
| Nullability | 15% | 85/100 | batch_end_utc (Y) correctly nullable; status marked N (ref: YES — minor deviation) |
| Structure | 10% | 70/100 | H3; no intro paragraph |

**Strengths:**
- Status enum `RUNNING | SUCCESS | FAILED` clearly documented
- `rows_rejected` addition provides useful operational signal
- `pipeline_run_id` description "Databricks Workflows run ID" is precise

**Gaps:**
- `entity_name` (logical entity being loaded, e.g., `sale`) is absent — replaced by `pipeline_name` which is a different concept
- No table paragraph description

**Improvement items:**
- [ ] Consider adding `entity_name` to track which logical entity (sale, order, customer) is being processed — enables per-entity monitoring
- [ ] Add one-sentence table description: "One row per pipeline execution. Primary lineage anchor for all target tables."

---

### stg.dq_rejections → `### globalsales.stg.dq_rejections` — 76/100 (weight 10 → 7.6 pts)

**Criteria scored:** Content (40%), Column Completeness (20%), Nullability (15%), FK References (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 40% | 71/100 | ~80% topic coverage; descriptions ~90%; no table paragraph |
| Column Completeness | 20% | 78/100 | 7/9 ref topics; `severity` absent, `batch_id` covered via lineage_key |
| Nullability | 15% | 80/100 | Nullable present; `lineage_key` marked N (ref: YES — design difference) |
| FK References | 15% | 85/100 | `FK → stg.lineage` present |
| Structure | 10% | 70/100 | H3; no intro paragraph; extra PII annotation column |

**Strengths:**
- `raw_payload` column with PII annotation is an excellent operational addition
- `assertion_id` naming (e.g., `DQ-SALE-001`) is more specific than reference's `dq_rule_id`
- `source_table` (three-part table name) adds traceability absent from reference

**Gaps:**
- `severity` column absent — reference documents `WARNING | ERROR | CRITICAL` severity levels
- `lineage_key` is NOT NULL in participant but reference allows NULL for "pre-lineage violations" — this is a deliberate but undocumented design choice

**Improvement items:**
- [ ] Add `severity` column: `STRING | N | Violation severity: WARNING \| ERROR \| CRITICAL`
- [ ] Add table paragraph description

---

### dim.supplier → `### globalsales.dim.customer (SCD2)` — 39/100 (weight 10 → 3.9 pts)

**Criteria scored:** Content (40%), Column Completeness (20%), Nullability (15%), FK References (15%), Structure (10%)
**SCD-2 raw penalty applied: −5 pts** (3/5 SCD-2 cols present via shared table; valid_from + valid_to absent)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 40% | 54/100 | ~67% topic coverage; 7/13 descriptions meaningful; no table paragraph |
| Column Completeness | 20% | 67/100 | 12/18 reference topics covered structurally |
| Nullability | 15% | **0/100** | **Nullable column ABSENT from dim.customer table** |
| FK References | 15% | 20/100 | No FK → notation in table; lineage_key FK only in shared SCD-2 table |
| Structure | 10% | 60/100 | H3; PII column replaces Nullable; no intro paragraph |

**Raw before SCD-2 penalty:** 43.9/100 — **After −5 penalty:** 38.9/100 → **39/100**

**Strengths:**
- PII column with "Masked via UC Column Mask" is an important security annotation
- Surrogate PK (`customer_key`) and source natural key (`customer_id`) correctly identified

**Gaps:**
- **Nullable column completely absent** — replaced by PII column, making nullability unreadable
- **No FK → notation** in the table itself (lineage_key FK is only in shared table)
- 6/13 descriptions are empty (customer_category, delivery_method, credit_limit, standard_discount_pct, is_statement_sent, is_on_credit_hold)
- SCD-2 tracking columns not in dim.customer table; shared table missing `valid_from` and `valid_to`
- No table paragraph description

**Improvement items:**
- [ ] Add Nullable column to dim.customer table (keep PII column if needed — use 5 columns: Column | Type | Nullable | PII | Description)
- [ ] Add FK → notation to lineage_key row: `FK → stg.lineage.lineage_key`
- [ ] Fill empty descriptions for at least: customer_category, delivery_method, credit_limit, is_on_credit_hold
- [ ] Add `valid_from` and `valid_to` to the shared SCD-2 columns table at the Silver layer

---

### dim.stock_item → `### globalsales.dim.city (SCD2)` — 32/100 (weight 10 → 3.2 pts)

**Criteria scored:** Content (40%), Column Completeness (20%), Nullability (15%), FK References (15%), Structure (10%)
**SCD-2 raw penalty applied: −5 pts** (3/5 SCD-2 cols present via shared table; valid_from + valid_to absent)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 40% | 50/100 | ~60% topic coverage; 5/9 descriptions; no table paragraph |
| Column Completeness | 20% | 50/100 | Cross-product coverage ~50% of structural dimension topics |
| Nullability | 15% | **0/100** | **Nullable column ABSENT from dim.city table** |
| FK References | 15% | 15/100 | No FK → notation; TY-EXTEND-001 task ref present (good) |
| Structure | 10% | 50/100 | H3; **non-standard merged-cell syntax** in column name column |

**Raw before SCD-2 penalty:** 37.3/100 — **After −5 penalty:** 32.3/100 → **32/100**

**Strengths:**
- `location_lat` and `location_lon` decomposition from WKT with task reference (TY-EXTEND-001) is excellent design documentation
- `location_wkt` preservation note ("Source WKT geometry (preserved as-is)") adds clarity

**Gaps:**
- **Non-standard merged-cell syntax**: `state_province, country, continent | STRING |` — this represents 3 columns in one table row, which is not valid Markdown table format and will render incorrectly
- **Nullable column absent** — same issue as dim.customer
- 4/9 descriptions are empty (city_name, state_province/country/continent, sales_territory/region/subregion, latest_recorded_population)
- No FK → notation anywhere in the table

**Improvement items:**
- [ ] Split merged cells: each column on its own row (`state_province`, `country`, `continent` as separate rows)
- [ ] Add Nullable column (with Nullable | PII | Description if PII annotations needed)
- [ ] Add FK → notation to lineage_key row
- [ ] Fill empty descriptions for all columns

---

### dim.date → [MISSING] — 0/100 (weight 10 → 0.0 pts)

No date or calendar dimension section exists in the participant document. The reference defines a 14-column static calendar dimension (2000-01-01 to 2030-12-31) with date_key, year, quarter, month, day, fiscal_year, and other calendar attributes.

`fact.sale` references `invoice_date_key` with `FK → dim.date (YYYYMMDD)`, confirming the dimension is part of the product — it is just undocumented.

**Gaps:**
- Entire dimension section absent
- `dim.date.date_key` used as FK target in `fact.sale` but dimension itself not described

**Improvement items:**
- [ ] Add `## globalsales.dim.date — Static Calendar Dimension` section with at minimum: date_key (INT IDENTITY PK), calendar_date, year, month, day, day_of_week, is_weekend, is_public_holiday columns — adapt from the reference dim.date structure

---

### fact.purchase → `### globalsales.fact.sale` — 79/100 (weight 10 → 7.9 pts)

**Criteria scored:** Content (40%), Column Completeness (20%), Nullability (15%), FK References (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 40% | 69/100 | ~82% topic coverage; 13/16 descriptions meaningful; no table paragraph |
| Column Completeness | 20% | 82/100 | 9/11 ref topics covered; more columns than reference (computed cols added) |
| Nullability | 15% | 85/100 | Nullable present; most values accurate |
| FK References | 15% | 98/100 | All 6 FK relationships explicitly documented with target table |
| Structure | 10% | 75/100 | H3; column table with clustering note; no intro paragraph |

**Strengths:**
- All FK relationships explicitly documented: `FK → dim.date (YYYYMMDD)`, `FK → dim.customer`, `FK → dim.stock_item`, `FK → dim.city`, `FK → dim.employee`, `FK → stg.lineage`
- Computed column formulas documented: `total_excluding_tax = quantity × unit_price`, etc.
- DQ rule cross-reference: "From source; DQ-SALE-004 asserts non-NULL" on profit
- Clustering key documented at bottom of section

**Gaps:**
- `quantity`, `unit_price`, `tax_rate` descriptions empty — these are high-traffic fact columns
- No intro paragraph (reference: "One row per purchase order line. Loaded incrementally via MERGE on…")

**Improvement items:**
- [ ] Add one-line table description above the column table: load pattern, grain, MERGE predicate
- [ ] Fill descriptions for quantity, unit_price, tax_rate

---

### Glossary: SCD-2 Tracking Columns → [MISSING] — 0/100 (weight 10 → 0.0 pts)

No Glossary section in the participant document. The reference defines the meaning of all 5 SCD-2 columns (valid_from, valid_to, row_effective_date, row_expiry_date, is_current_row) with "Applies to" and "Meaning" columns.

The participant's Silver layer intro table partially serves this function but:
- Lacks `valid_from` and `valid_to` entries
- Lacks the "Applies to" column
- Has no footnote on FK logical vs physical constraint enforcement

**Improvement items:**
- [ ] Add `## Glossary: SCD-2 Tracking Columns` section with a 3-column table (Column | Applies to | Meaning) covering all 5 SCD-2 columns
- [ ] Add footnote: "FK relationships are logical — Delta Lake does not enforce physical constraints. Referential integrity enforced at ETL layer (sk_resolver + DQ rules)."

---

## Extra Section

**`### globalsales.mart.v_customer_sales_summary`** — 11-column mart view with computed `profit_margin_with_factor` referencing `PROFIT_MARGIN_FACTOR` (NFR-MNT-002, CX-P01). Good operational documentation. No score impact.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add `## dim.date` section (14 cols: date_key, calendar_date, year, quarter, month, day, weekday, is_weekend, is_public_holiday + fiscal cols) | dim.date | +9 pts |
| 2 | Add `## Glossary: SCD-2 Tracking Columns` section with all 5 SCD-2 columns + FK footnote | Glossary | +9 pts |
| 3 | Add Nullable column to dim.customer and dim.city; add valid_from + valid_to to shared SCD-2 table | dim.customer, dim.city | +8 pts |
| 4 | Fix dim.city non-standard merged-cell syntax (one column per row) | dim.city | +2 pts |
| 5 | Add FK → notation within dim.customer and dim.city tables | dim.customer, dim.city | +2 pts |
| 6 | Fill empty descriptions in dim.customer (6 cols) and dim.city (4 cols) | dim.customer, dim.city | +2 pts |
| 7 | Add one-sentence table description paragraph above each table | All table sections | +3 pts |

Addressing items 1–3 alone would push the score to approximately **71/100 (Acceptable approaching Good)**.

---

## Priority Actions

1. **Add `## globalsales.dim.date` section** — static calendar dimension; include at minimum date_key (INT IDENTITY PK YYYYMMDD), calendar_date, year, quarter, month, day, day_of_week, is_weekend, is_public_holiday, fiscal_year, fiscal_quarter. This is the FK target for `fact.sale.invoice_date_key` so its absence is a documentation gap. Worth up to **+9 pts**.

2. **Add `## Glossary: SCD-2 Tracking Columns`** — 3-column table (Column | Applies to | Meaning) covering valid_from, valid_to, row_effective_date, row_expiry_date, is_current_row, plus add valid_from and valid_to to the shared Silver layer intro table. Worth up to **+9 pts**.

3. **Fix dim.customer and dim.city Nullable column** — add a Nullable column to both tables. If PII annotations are needed, use a 5-column format: Column | Type | Nullable | PII | Description. Also extend the shared SCD-2 table with valid_from and valid_to rows. Combined worth up to **+8 pts**.

4. **Fix dim.city merged-cell syntax** — split `state_province, country, continent` and `sales_territory, region, subregion` into separate rows, one column per row. Prevents rendering breakage. Worth up to **+2 pts**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing tables, SCD-2 columns absent, or structural issues |
| 0–44 | Incomplete | Major sections missing or column tables absent |

---

*Report generated by skill 28-migvisor-task-checker-data-dictionary on 2026-09-03*
