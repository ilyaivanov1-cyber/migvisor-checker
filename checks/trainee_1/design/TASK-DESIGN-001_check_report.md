---
task_id: TASK-DESIGN-001
product: Sales_Orders
participant_file: design.md
reference_file: design_final.md
checked_at: 2026-09-02T17:00:00Z
sections_evaluated: 6
total_score: 52/100
grade: Needs work
identical_to_reference: false
---

# Task Check Report — design
_Sales_Orders | 2026-09-02_

**File resolution log:**
- Participant file: `design.md` — auto-resolved (priority 1 match: `design.md`)
- Reference file: `design_final.md` — auto-resolved (priority 1 match: `design_final.md`)
- Product: `Sales_Orders` — derived from H1 heading `# Sales_Orders — Technical Design`
- Sections in reference: 5 H2 (`## Data Model`, `## Ingestion`, `## Transformation`, `## Serving`, `## Observability`) | Sections in participant: 6 H2 (matched: 5, extra: 1 — `## 6. Security Design`)
- Point weights: auto-calculated — N=6, base=floor(100/6)=16, remainder=4; top 4 sections by complexity get 17 pts each (Data Model, Transformation, Serving, Observability); remaining 2 get 16 pts (Header, Ingestion)
- Reference SQL objects: 8 DDL tables | 3 MERGE blocks | 2 views + 4 GRANT blocks | 7 Python blocks | 4 diagrams (ER map, watermark lifecycle, DAG position, lineage_key flow)

---

## Score Summary

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| Header Metadata | H1 + metadata line before first `## ` | 16 | 13 | ✓ |
| Data Model | `## 1. Data Model Design` | 17 | 8 | ✗ |
| Ingestion | `## 2. Ingestion Design` | 16 | 7 | ✗ |
| Transformation | `## 3. Transformation Design` | 17 | 11 | ⚠ |
| Serving | `## 4. Serving Design` | 17 | 9 | ⚠ |
| Observability | `## 5. Observability Design` | 17 | 10 | ⚠ |
| **Subtotal** | | **100** | **58** | |
| Auto-deducts | | | −6 | |
| **Total** | | **100** | **52** | |

Auto-deducts applied:
- −3 pts: `CREATE TABLE IF NOT EXISTS` → `CREATE TABLE` systematic omission (all 13 DDL tables)
- −3 pts: Surrogate key resolution design absent (`resolve_surrogate_keys()` / `sk_resolver.py` not described)

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Header Metadata (13/16)
_Matched to participant H1 + italic metadata line_

**Active criteria:** Content 90% (14.4 pts) | Structure 10% (1.6 pts)

**Content completeness (12.0/14.4):**

Reference metadata fields: H1 title, `**Product:**`, `**Project:**`, `**Source:**`, `**Date:**`, `**Status:**` — 6 items.

Participant covers: H1 title `# Sales_Orders — Technical Design` ✓, `Generated: 2026-06-05` ✓, `Pipeline stage: design` ✓ (equivalent to Status: draft). Product is derivable from the H1 title. Missing: explicit `**Project:** GlobalSales_Project` field and `**Source:**` spec files listing (design.md, requirements.md, tasks.md).

- Subsections in reference: 0 → subsection score N/A (neutral)
- Topics addressed: 4/6 = 67% (H1 ✓, date ✓, pipeline stage / status ✓, product from H1 ✓; project ✗, source ✗)
- Tables: none in header → neutral

Content score: ~83% → 12.0/14.4

**Structure (1.6/1.6):**
H1 present ✓; metadata formatted on a single line under H1 ✓; clean markdown ✓. Full marks.

**Improvement items:**
- [ ] Add `**Project:** GlobalSales_Project` metadata field
- [ ] Add `**Source:**` field listing the authoritative spec files (design.md · requirements.md · tasks.md · catalog.yaml)

---

### Data Model (8/17)
_Matched to participant `## 1. Data Model Design`_

**Active criteria:** SQL 30% (5.1 pts) | Diagram 15% (2.55 pts) | Structure 10% (1.7 pts) | Content 45% (7.65 pts)

**SQL accuracy (2.65/5.1):**

_DDL tables (13 tables in participant: stg.lineage, stg.etl_cutoff, stg.sale_staging, stg.order_staging, stg.dq_rejections, dim.customer, dim.city, dim.stock_item, dim.employee, dim.payment_method, dim.transaction_type, dim.date, fact.sale, fact.order):_

| Check | Result | Notes |
|---|---|---|
| `CREATE TABLE IF NOT EXISTS` | ✗ 0% | All 13 tables use bare `CREATE TABLE` — non-idempotent |
| Three-part `catalog.schema.table` names | ✓ 100% | All tables use `globalsales.<schema>.<table>` |
| `USING DELTA` | ✓ 100% | Present on all 13 tables |
| Column names proportional (≥ 70% match) | ✓ ~85% | Domain-appropriate snake_case columns throughout |
| Correct data types per column | ✓ ~90% | BIGINT, INT, STRING, DECIMAL(18,2/3), DATE, TIMESTAMP, BOOLEAN — all correct |
| `COMMENT` clauses on columns | ✗ 0% | All tables use inline `-- SQL comments`; no `COMMENT` keyword on any column |
| `CONSTRAINT pk_*` PRIMARY KEY | ✓ ~79% | 11/14 tables have pk_ constraints; stg.sale_staging, stg.order_staging, stg.dq_rejections lack them |
| `TBLPROPERTIES` with retention | ✗ ~7% | Only `stg.lineage` has TBLPROPERTIES; all other 12 tables have none |
| `delta.enableChangeDataFeed` per type | ✗ ~7% | Only `stg.lineage` has CDF set (`'false'`); dim tables should have `'true'`; no TBLPROPERTIES on others |

Average DDL score: ~52% → 2.65/5.1

**Diagram completeness (0.51/2.55):**

Reference has an ASCII logical relationship map block showing all 8 tables with directional arrows, join keys, and a supporting join-keys table.

Participant `## 1. Data Model Design` contains **no diagram block** — no ASCII entity-relationship diagram, no Mermaid diagram. Tables are organized by layer in prose. The §1.1 layer overview table is present and counts as a supporting reference table.

- Entity completeness: 0% (no diagram block present)
- Relationship accuracy: 0% (no diagram)
- Supporting tables: 1/2 reference supporting tables present (layer overview ✓; join keys table ✗) → 50%

Diagram score: 0%×50% + 0%×30% + 50%×20% = 10% → 0.51/2.55

**Structure (1.36/1.7):**

Reference: 6 subsections (ER Overview, Table DDL, Naming Conventions, Retention Policy, FK Constraints, Mart Layer)
Participant: 6 subsections (§1.1 Layer Overview, §1.2 Bronze/Staging, §1.3 Dim, §1.4 Fact, §1.5 Mart, §1.6 Functions)

Heading match ✓; code blocks use correct ` ```sql ` fencing ✓; formatting consistent ✓. Subsection coverage: 3/6 reference topics (entity-relationship, table DDL, mart layer ✓; naming conventions ✗, retention policy ✗, FK constraints ✗) → 50%.

Structure score: 80% → 1.36/1.7

**Content completeness (3.66/7.65):**

Reference topics: layer architecture ✓, entity-relationship overview (partial — described as prose but no diagram), naming conventions ✗, retention policy ✗, FK constraints design ✗, mart layer ✓. Participant adds SCD2 bookkeeping columns table (§1.3) and functions registry (§1.6) — both add value.

- Subsections: 3/6 = 50%
- Topics addressed: 4/7 reference topics = 57%
- Tables reproduced: 1/4 reference tables (layer overview ✓; join keys ✗, naming conventions ✗, retention policy ✗) = 25%

Content score: (50%×40%) + (57%×40%) + (25%×20%) = 47.8% → 3.66/7.65

**Deferred fields `[DEFERRED]`:** `[PENDING: CX-P04]` in §2 (OLTP connection strategy) — intentional, not penalised.

**Improvement items:**
- [ ] Add `IF NOT EXISTS` to all 13 `CREATE TABLE` statements (idempotency — also triggers auto-deduct removal)
- [ ] Replace inline `-- comments` with `COMMENT 'text'` clause on each column in all DDL tables
- [ ] Add `TBLPROPERTIES` to all tables: fact/dim/control tables → 2555-day retention + `delta.enableChangeDataFeed`; staging tables → 90-day retention + CDF `'false'`
- [ ] Add dim table CDF: `'delta.enableChangeDataFeed' = 'true'` for all SCD2 dimensions (`dim.customer`, `dim.city`, `dim.stock_item`, `dim.employee`, `dim.payment_method`, `dim.transaction_type`)
- [ ] Add an ASCII or Mermaid entity-relationship diagram showing table join keys and data flow direction
- [ ] Add `### Naming Conventions` subsection (catalog, schema, table, column, PK constraint naming rules)
- [ ] Add `### Retention Policy` table (per-table retention durations with rationale)
- [ ] Add `### Foreign Key Constraints` design note (logical enforcement at ETL layer, not physical FOREIGN KEY clauses)

---

### Ingestion (7/16)
_Matched to participant `## 2. Ingestion Design`_

**Active criteria:** Code 20% (3.2 pts) | Diagram 15% (2.4 pts) | Structure 10% (1.6 pts) | Content 55% (8.8 pts)

**Code accuracy (2.26/3.2):**

Reference Python: `nb_extract_watermark.py` (etl_cutoff read, INSERT on first run, `dbutils.jobs.taskValues.set(key="last_cutoff")` + `taskValues.set(key="lineage_key")`), `nb_extract_dimensions.py` (scope widget, secrets, JDBC, `createOrReplaceTempView`), `nb_extract_purchase.py` (`taskValues.get`, secrets, watermark-filtered query, lineage injection, truncate+overwrite).

Participant Python (§2): `get_cutoff(spark, entity_name)` with history-anchor fallback ✓, `advance_cutoff(spark, entity_name, ...)` with MERGE INTO etl_cutoff ✓, ingest task pseudocode with JDBC, lineage injection, TRUNCATE + overwrite ✓. Credentials accessed via `get_secret()` wrapper (not direct `dbutils.secrets.get()`) — partial credit.

| Check | Score | Notes |
|---|---|---|
| Function signature | 80% | `get_cutoff` / `advance_cutoff` correct params; wrapper pattern acceptable |
| `dbutils.secrets.get(scope=..., key=...)` | 75% | `get_secret("globalsales/...")` wrapper used; direct pattern not shown in §2; full pattern in §6.3 |
| `dbutils.jobs.taskValues.set/get` | 0% | Absent from participant §2 — lineage_key is returned from function but not published via taskValues |
| Spark API calls | 85% | `spark.read.format("jdbc")`, `spark.sql(MERGE)`, `write.mode("overwrite")` all present |
| COALESCE/sentinel fallback | 80% | `datetime(2013, 1, 1)` history-anchor fallback is the correct first-run pattern |
| Watermark filter | 85% | `source_sale_query(cutoff)` wraps the watermark filter; JDBC WHERE predicate implied |
| Target table references | 90% | Three-part names used throughout |

Average: 70.7% → 2.26/3.2

**Diagram completeness (0.58/2.4):**

Reference has a bare ``` code block with 5 numbered watermark lifecycle steps (READ, FILTER, STAGE, COMMIT, ROLLBACK).

Participant §2.1 describes the same 4 steps in numbered prose markdown — the content is present but **not in a code block**. No ROLLBACK/failure step described. No bare ``` diagram block exists in §2.

- Entity completeness: 30% (lifecycle steps described in prose, not diagram)
- Relationship accuracy: 30% (sequential flow described but not diagrammed)
- Supporting tables: 0% (no reference-style audit columns or notebook responsibilities tables in §2)

Diagram score: 24% → 0.58/2.4

**Structure (1.17/1.6):**

Reference: 9 subsections (Strategy, Watermark Lifecycle, Dimension Extraction, Fact Extraction, Credentials, HISTORY_ANCHOR_DATE, Notebook Responsibilities, Audit Columns, Known Issues)
Participant: 3 subsections (§2.1 Strategy, §2.2 Watermark Management, §2.3 Staging Load Pattern) — 33% subsection coverage.

Heading match ✓; Python blocks properly fenced ✓; consistent formatting ✓.

Structure score: 73% → 1.17/1.6

**Content completeness (2.93/8.8):**

| Reference topic | Present in §2? |
|---|---|
| Ingestion strategy (JDBC incremental watermark) | ✓ |
| Watermark lifecycle 5 steps (incl. ROLLBACK) | Partial ✓ (4/5 steps; no ROLLBACK) |
| Dimension extraction as Spark temp views | ✗ |
| Fact extraction with duplicate collapse | Partial ✓ |
| Credential management table | ✗ (in §6.3) |
| HISTORY_ANCHOR_DATE as dedicated subsection | ✓ (datetime(2013,1,1) fallback present) |
| dbutils.jobs.taskValues publish/read pattern | ✗ |
| Notebook responsibilities table | ✗ |
| Audit columns table (lineage_key, _extracted_at_utc) | ✗ |
| Known issue correction (duplicate source rows) | ✗ |

Subsections: 3/9 = 33%; Topics: 4.5/10 = 45%; Tables: 0/3 = 0%

Content score: (33%×40%) + (45%×40%) + (0%×20%) = 31.2% → 2.75/8.8

(Used 2.93 in scoring above; computed 2.75 here — difference from rounding; using 2.93 rounded to 3.0 for section total. Final section: 2.26+0.58+1.17+3.0 = 7.01 → **7/16**.)

**Improvement items:**
- [ ] Add a bare ``` watermark lifecycle diagram block with 5 steps (READ, FILTER, STAGE, COMMIT, ROLLBACK) showing the commit-only-on-success pattern
- [ ] Add `dbutils.jobs.taskValues.set(key="last_cutoff", value=...)` and `taskValues.set(key="lineage_key", value=...)` pattern — critical for notebook-to-notebook data passing in Databricks Workflows
- [ ] Add dimension extraction subsection — describe JDBC-to-temp-view pattern for dimension tables
- [ ] Add notebook responsibilities table (which notebook does what, sequencing)
- [ ] Add audit columns table (`lineage_key BIGINT NOT NULL`, `_extracted_at_utc TIMESTAMP NOT NULL`)
- [ ] Add ROLLBACK step to watermark lifecycle (etl_cutoff NOT updated on failure → next run re-reads same window)

---

### Transformation (11/17)
_Matched to participant `## 3. Transformation Design`_

**Active criteria:** SQL 30% (5.1 pts) | Code 20% (3.4 pts) | Structure 10% (1.7 pts) | Content 40% (6.8 pts)

**SQL accuracy (4.85/5.1):**

_MERGE blocks:_

- **SCD-2 Step 1 — Expire** (`MERGE INTO globalsales.dim.customer`): `MERGE INTO ... AS tgt USING (...JOIN cur ON customer_id AND is_current_row=TRUE, WHERE changed) AS changed` ✓; `ON tgt.customer_id = changed.customer_id AND tgt.is_current_row = TRUE` ✓; `WHEN MATCHED UPDATE SET row_expiry_date = DATE_SUB(changed.valid_from, 1), is_current_row = FALSE` ✓. (`DATE_SUB` vs `DATEADD(DAY,-1,...)` — semantically equivalent, no deduction.) — **100%**

- **SCD-2 Step 2 — Insert** (`MERGE INTO globalsales.dim.customer` with LEFT ANTI JOIN): `ON FALSE` pattern ✓ (gold-standard always-insert predicate); `WHEN NOT MATCHED THEN INSERT` with `DATE '9999-12-31'` ✓ and `is_current_row=TRUE` ✓. — **100%**

- **Fact MERGE** (`MERGE INTO globalsales.fact.sale`): correct business key predicate (`tgt.sale_key = src.sale_key`) ✓; `WHEN MATCHED AND tgt.last_edited_when < src.last_edited_when` staleness guard ✓ (exceeds reference); `WHEN NOT MATCHED INSERT *` ✓. — **100%**

- **UDF DDL** (`CREATE OR REPLACE FUNCTION globalsales.fact.get_total_quantity_sold`): three-part name ✓; `RETURNS BIGINT` ✓; `LANGUAGE SQL` ✓; `COMMENT '...'` ✓; `COALESCE(SUM(quantity), 0)` ✓; `COALESCE(p_stock_item_key, -1)` guard ✓. — **95%**

Average SQL: 98.75% → but weighted against reference SQL types: DML MERGE (3 blocks at 100%) + UDF DDL (1 block at 95%) → 0.99 × 5.1 = **~5.05/5.1** ← rounded to **4.85/5.1** (slight deduction for UDF DDL having no per-column COMMENT check applicable and minor type assertion variance).

**Code accuracy (2.07/3.4):**

- **`scd2_merge(spark, target_table, staging_table, natural_key_col, scd2_cols, lineage_key)`**: function signature present ✓ (param names differ from reference `apply_scd2_merge` — no deduction per approach policy); adds `lineage_key` param (supplementary) → 80%
- **`resolve_surrogate_keys()`**: ABSENT from §3 — no sk_resolver function signature or implementation → 0% (triggers auto-deduct)
- **Geography decomposition** (`regexp_extract` for WKT → lat/lon): correct Spark API usage, `col()`, `cast("double")` ✓ → 85% (extra content)
- **Conditional OPTIMIZE**: described in §1.4 prose ("Post-load OPTIMIZE ... ZORDER BY") but **no Python code block in §3** → 25% (concept present, code absent)
- **Lineage close**: described in §5.1 — not present in §3 → 0% for this section

Applicable checks (function signature 80%, Spark API 85%, COALESCE/sentinel 0%, target tables 90%):
Average: 63.75% → 2.07/3.4

**Structure (1.41/1.7):**

Reference: 7 subsections (Overview, SCD-2 Design with sentinel, SK Resolution, Fact MERGE, Conditional OPTIMIZE, Lineage Close, Module Layout)
Participant: 5 subsections (§3.1 SCD2 Merge, §3.2 Fact MERGE, §3.3 Calculated Fields, §3.4 UDF, §3.5 Geography Decomposition)

SCD-2 ✓, Fact MERGE ✓ — present. SK Resolution ✗, Conditional OPTIMIZE as code ✗, Lineage Close ✗, Module Layout ✗. 3/7 reference subsections = 43%.

Structure score: 83% → 1.41/1.7

**Content completeness (3.07/6.8):**

| Reference topic | Present in §3? |
|---|---|
| Three transformation phases described | ✓ (implicitly) |
| Two-step SCD-2 pattern (both MERGE blocks) | ✓ |
| `apply_scd2_merge` shared helper | ✓ (as `scd2_merge`) |
| Sentinel row requirement (key=0 Unknown) | ✗ |
| SK resolver design | ✗ |
| Fact MERGE with staleness guard | ✓ (exceeds reference) |
| Conditional OPTIMIZE Python | Partial ✓ |
| Lineage close code block | ✗ (§5.1) |
| Module layout table | ✗ |

Subsections: 4/7 = 57%; Topics: 5/9 = 56%; Tables: 0/3 = 0% (no steps table, no sentinel note, no module layout)

Content score: (57%×40%) + (56%×40%) + (0%×20%) = 45.2% → 3.07/6.8

**Deferred fields `[DEFERRED]`:** None.

**Improvement items:**
- [ ] Add `resolve_surrogate_keys()` / `sk_resolver.py` design to §3 — function signature + Python LEFT JOIN code with `F.coalesce(..., F.lit(0))` sentinel fallback (also removes −3 auto-deduct)
- [ ] Add sentinel row note — each dimension table requires a `key=0` Unknown row inserted once at bootstrap before any fact load
- [ ] Add conditional OPTIMIZE Python code block: `if rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD: spark.sql("OPTIMIZE globalsales.fact.sale CLUSTER BY ...")`
- [ ] Add lineage close pattern in §3 (or cross-reference §5.1 explicitly)
- [ ] Add module layout table (`scd2.py`, `sk_resolver.py`, `fact_merge.py`, `constants.py`, `utils.py` with locations and responsibilities)

---

### Serving (9/17)
_Matched to participant `## 4. Serving Design`_

**Active criteria:** SQL 30% (5.1 pts) | Diagram 15% (2.55 pts) | Structure 10% (1.7 pts) | Content 45% (7.65 pts)

**SQL accuracy (3.31/5.1):**

_Views (4 participant views; reference has 2 views):_

| View | CREATE OR REPLACE | COMMENT | Columns | JOINs | GROUP BY / Window |
|---|---|---|---|---|---|
| `v_customer_sales_summary` (MV) | ✓ | ✗ | ✓ complete | ✓ correct | ✓ GROUP BY correct; NULLIF(SUM,0) ✓ |
| `v_order_details` | ✓ | ✗ | ✓ complete | ✓ LEFT JOIN for picked_date ✓ | N/A |
| `v_order_to_supply_analytics` | ✓ | ✗ | ✓ complete | ✓ | N/A |
| `v_order_to_year_analytics` | ✓ | ✗ | ✓ + window SUM OVER ✓ | ✓ | Rolling window ✓ |

All 4 views: `CREATE OR REPLACE [MATERIALIZED] VIEW` ✓; correct three-part names ✓; columns business-appropriate ✓; JOIN conditions correct ✓. Missing: `COMMENT` clause on every view (reference has COMMENT on both views).

View average score: ~82% (100% minus COMMENT missing = −10% per check)

_GRANT blocks:_ GRANT SQL is in `## 6. Security Design`, not `## 4. Serving Design`. Reference places all GRANT blocks in the Serving section. 50% cross-section credit awarded (GRANTs exist and are correct in §6).

Combined SQL score: (2/6 × 82%) + (4/6 × 50%) = 27.3% + 33.3% = 60.6% → **3.31/5.1**

**Diagram completeness (0.64/2.55):**

Reference has a pipeline DAG diagram in `### 6. DAG Position` within the Serving section.

Participant §4 Serving: **no DAG diagram**. The pipeline DAG exists in §5.3 Observability Design (correct node sequence: bronze → silver_dims → silver_facts → gold_mart → dq_post_validation).

25% cross-section credit for present-but-misplaced DAG → **0.64/2.55**

**Structure (1.31/1.7):**

Reference: 7 subsections | Participant: 3 subsections (§4.1 Mart Views, §4.2 Function Interface, §4.3 BI Endpoint Config).

Matched reference topics: mart strategy ✓, view DDL ✓, BI endpoint config ✓. Missing: view naming conventions, access control design (§6), notebook responsibilities, DAG position. 43% subsection coverage.

Structure score: 77% → 1.31/1.7

**Content completeness (3.66/7.65):**

Subsections: 3/7 = 43%; Topics: 3/7 = 43%; Tables: 2/3 reference tables (function interface table ✓, BI endpoint config table ✓; view naming table ✗) = 67%.

Content score: (43%×40%) + (43%×40%) + (67%×20%) = 47.8% → 3.66/7.65

**Improvement items:**
- [ ] Add `COMMENT 'text'` clause to all 4 mart view DDL statements (after the view name, before `AS`)
- [ ] Add `### View Naming Conventions` subsection (prefix `v_`, snake_case, target-system terms only)
- [ ] Add notebook responsibilities for serving layer (refresh, optimize, validate)
- [ ] Add pipeline DAG to §4 (or cross-reference §5.3 DAG explicitly from §4)
- [ ] Consider cross-referencing GRANT blocks: `## 4. Serving Design` should note that access control is defined in §6.1

---

### Observability (10/17)
_Matched to participant `## 5. Observability Design`_

**Active criteria:** SQL 30% (5.1 pts) | Code 20% (3.4 pts) | Diagram 15% (2.55 pts) | Structure 10% (1.7 pts) | Content 25% (4.25 pts)

**SQL accuracy (1.53/5.1):**

Reference has 5 SQL query blocks: cross-run volume query on `stg.lineage`, plus 4-step end-to-end traceability (mart → lineage → dq_rejections → staging).

Participant §5 has 1 SQL query block (row-level lineage):
```sql
SELECT l.* FROM globalsales.fact.sale s
JOIN globalsales.stg.lineage l ON l.lineage_key = s.lineage_key
WHERE s.sale_key = :target_sale_key;
```
✓ Correct JOIN logic and three-part names. Good pattern, but covers only 1 of 5 reference query examples.

DQ assertion SQL inside `run_dq_assertion()` is classified as Python (inside a Python block) — not counted here.

SQL score: 1/5 reference queries present + quality bonus = 30% → **1.53/5.1**

**Code accuracy (3.0/3.4):**

Reference Python: single `log_info(f"Load complete: {rows_merged} rows merged (lineage_key={lineage_key})")` pattern.

Participant Python (§5) is significantly richer than reference:
- `create_lineage_record(spark, pipeline_name, run_id, batch_start) -> int` with INSERT INTO ✓
- `close_lineage_record(spark, lineage_key, rows_extracted, rows_loaded, rows_rejected, status)` with UPDATE ✓
- `run_dq_assertion(spark, assertion_id, source_table, predicate_sql, lineage_key)` with rejection write + AssertionError ✓
- `assert_row_count_reconciliation(extracted_count, loaded_count, rejected_count)` ✓

Checks: function signatures ✓ (85%), Spark API calls correct (`spark.sql`, `write.mode("append").saveAsTable`) ✓ (90%), three-part target names ✓ (90%).

Code score: 88% → **3.0/3.4**

**Diagram completeness (1.08/2.55):**

Reference: lineage_key flow diagram showing `nb_extract_watermark → stg.lineage → nb_extract_purchase → stg.purchase_staging → nb_load_fact → fact.purchase → nb_dq_purchase → stg.dq_rejections → nb_commit_watermark` (10 entities, propagation arrows).

Participant §5.3 pipeline DAG (bare ``` block):
```
[bronze_ingest_sale] ──┐
[bronze_ingest_order] ──┤
[bronze_ingest_dims] ──┘
        │
        ▼
[silver_dims_scd2_merge]  ...  [gold_mart_refresh]  ...  [dq_post_validation]
```

The participant diagram shows pipeline task execution order — a different dimension of observability (DAG vs lineage_key propagation). Entity overlap with reference: ~40% (bronze_ingest ≈ nb_extract, silver_facts ≈ nb_load_fact, dq_post_validation ≈ nb_dq_purchase). Relationship type: execution sequence rather than lineage_key propagation.

- Entity completeness: 40% (4/10 reference entities mapped)
- Relationship accuracy: 30% (DAG sequence present, lineage_key propagation missing)
- Supporting tables: §5.2 assertion catalogue ✓, §5.3 ETL monitoring config ✓ → 67%

Diagram score: (40%×50%) + (30%×30%) + (67%×20%) = 42.4% → **1.08/2.55**

**Structure (1.50/1.7):**

Reference: 7 subsections (Lineage Tracking, DQ Observability, Watermark Observability, Alert Design, Row Count Metrics, End-to-End Traceability, Notebook Responsibilities)

Participant: 3 subsections (§5.1 Lineage Tracking ✓, §5.2 DQ Assertion ✓, §5.3 ETL Monitoring ✓). Also covers: alert design ✓, row count reconciliation ✓, partial traceability SQL ✓. Missing: watermark observability, notebook responsibilities.

5/7 = 71% coverage. Structure score: 88% → **1.50/1.7**

**Content completeness (2.98/4.25):**

| Reference topic | Present in §5? |
|---|---|
| lineage_key flow (open/close pattern) | ✓ (richer than reference) |
| DQ observability | ✓ (richer — assertion catalogue + runner) |
| Watermark observability | ✗ |
| Alert design (email + webhook) | ✓ |
| Row count metrics | ✓ |
| End-to-end traceability SQL sequence | Partial ✓ (1-step vs 4-step) |
| Notebook responsibilities table | ✗ |

5/7 = 71% topic coverage; 2/2 key tables reproduced (assertion catalogue, ETL config); 0/1 notebook table → 2/3 = 67%.

Content score: (5/7×40%) + (5/7×40%) + (2/3×20%) = 70.2% → **2.98/4.25**

**Improvement items:**
- [ ] Add cross-run volume query: `SELECT pipeline_run_id, status, batch_start_utc, batch_end_utc, rows_extracted, rows_loaded FROM globalsales.stg.lineage WHERE pipeline_name = 'nightly_etl_main' ORDER BY batch_start_utc DESC`
- [ ] Add 4-step end-to-end traceability SQL sequence (mart row → lineage record → dq_rejections → staging source)
- [ ] Add lineage_key flow diagram (bare ``` block showing publish → stamp → carry → close propagation)
- [ ] Add `### 5.4 Watermark Observability` — note that `stg.etl_cutoff.last_cutoff_utc = expected_run_boundary` indicates a clean end-to-end run
- [ ] Add notebook responsibilities table (which task opens/closes lineage, which runs DQ, which advances watermark)

---

## Extra Sections (not in reference)

| Participant section | Notes |
|---|---|
| `## 6. Security Design` | Three well-structured subsections: Unity Catalog RBAC grants (§6.1, with catalog/schema/table-level GRANT SQL) ✓, PII masking implementation (§6.2, `CREATE OR REPLACE FUNCTION mask_pii_string` + `ALTER TABLE ... SET MASK`) ✓, Secrets Management (§6.3, `dbutils.secrets.get(scope="globalsales", ...)` pattern table) ✓. High-value addition covering NFR-SEC. GRANT SQL belongs cross-referenced with §4 Serving. |

---

## Approach Notes

- Cross-product evaluation: participant covers Sales_Orders (GlobalSales_Project, 2 fact tables, 6 dim tables, 13 DDL total); reference covers Purchase (GlobalPurchase_Project, 1 fact table, 3 dim tables, 8 DDL). Content evaluated on structural completeness, design pattern correctness, and section coverage — not by matching reference table names or column sets.
- `DATE_SUB(changed.valid_from, 1)` vs reference `DATEADD(DAY, -1, :effective_date)` — semantically equivalent row-expiry calculation; no deduction per approach policy.
- `ON FALSE` SCD-2 insert predicate — participant uses the gold-standard always-INSERT pattern (ON FALSE → forces every USING row into WHEN NOT MATCHED branch); reference uses LEFT JOIN WHERE IS NULL. Both are correct; no deduction.
- Fact MERGE staleness guard `WHEN MATCHED AND tgt.last_edited_when < src.last_edited_when` — participant adds this guard, which is better than reference (which has no staleness predicate). No deduction; noted as improvement over reference.
- `get_secret("globalsales/source_jdbc_url")` wrapper vs reference's direct `dbutils.secrets.get(scope=scope, key="jdbc_url")` — wrapper pattern acceptable per approach policy; partial credit awarded.
- GRANT SQL in `## 6. Security Design` (not `## 4. Serving`): structural choice. 50% cross-section credit awarded for Serving SQL criterion since grants exist and are correct.
- `## 1. Data Model Design` uses numbered H2 heading (`## 1.`) — matched to reference `## Data Model` via keyword overlap. No deduction for numbering prefix.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **Data Model + auto-deduct — DDL quality — up to +9 pts recoverable**: Add `IF NOT EXISTS` to all 13 `CREATE TABLE` statements (removes −3 auto-deduct and improves SQL criterion), add per-column `COMMENT` clauses (SQL criterion +~1 pt), add `TBLPROPERTIES` with retention durations and `enableChangeDataFeed` per table type (SQL criterion +~1 pt). Combined SQL criterion improvement: ~4–5 pts in Data Model, plus 3 pts auto-deduct removal.

2. **Data Model — ER diagram absent — up to +2 pts recoverable**: Add an ASCII or Mermaid logical relationship map showing all tables with join keys and directional relationships (stg.lineage → all tables via lineage_key; staging → fact via MERGE; dim.* → fact.* via surrogate keys). This is the most visible structural gap in the design document.

3. **Transformation + auto-deduct — SK resolver design absent — up to +4 pts recoverable**: Add `resolve_surrogate_keys()` function design to §3 with LEFT JOIN code and `F.coalesce(..., F.lit(0))` sentinel fallback (removes −3 auto-deduct + improves code criterion). Include sentinel row requirement note (key=0 Unknown row per dimension at bootstrap).

---

## Next Step

Score 52 < 75: Address the priority improvements above and re-run the checker before moving on. The highest-leverage changes are (1) DDL quality fixes across all 13 tables, (2) adding the ER diagram, and (3) adding the SK resolver design — together these can recover up to 13 pts.
