# Technical Design — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Implements:** `development_plan/requirements.md` (32 requirements)
**Target catalog:** `inventory_stock` — schemas `bronze`, `silver_dim`, `silver_fact`
**Contents:** 5 sections | 8 entities | 6 calculations | 4 filters | 9 validation rules | 3 Workflow tasks

---

## What This Spec Is

The technical design is the **build specification**. It states, concretely enough to generate code from, what tables exist, what columns they have, how data moves between them, what the MERGE statement is, what gets validated, and what the Workflow task graph looks like.

It is the third of four development-plan artifacts, and its position defines its job:

| Artifact | Question it answers |
|---|---|
| `product-definition.yaml` | What is this product, in ODPS terms? |
| `requirements.md` | **What** must be true when we are done? (32 numbered, testable requirements) |
| **`design.md`** | **How** is that achieved? (concrete schemas, formulas, statements) |
| `tasks.md` | In what **order** do we build it? |

It has 5 sections:

1. **Data Model** — entities, full column-level attributes, relationships, clustering strategy
2. **Ingestion** — input patterns, the extract window computation, the zero-rows guard
3. **Transformation Logic** — 6 numbered calculations, 4 numbered filters, the MERGE statement
4. **Serving** — output ports, BI report connectivity, views
5. **Observability** — 9 validation rules, lineage/audit design, alerting, the Workflow task graph

Think of it as the **blueprint**. The to-be design explains what changes and why; this explains what to build.

---

## Why This Spec Exists

### It is where the specs stop justifying and start specifying

The to-be design and the technical design describe the same target system, and it is easy to mistake one for a longer version of the other. They differ in purpose:

| | To-be design | Technical design |
|---|---|---|
| Organized by | The as-is sections it mirrors | The layers you build |
| Cites | Rule IDs (SX-001, TY-P001, LN-004) | Requirement IDs (FR-007, NFR-003) |
| Shows a MERGE as | A 22-step pipeline entry with rule justification | An executable SQL statement |
| Answers | "Why is it built this way?" | "What exactly do I create?" |
| Reader | A reviewer verifying nothing was lost | A generator emitting DDL |

The to-be is a **diff against the legacy system**. The technical design has no legacy system in it at all — no T-SQL, no SSIS, no source object names except as business keys. That absence is deliberate: at this point the translation argument is settled, and carrying it further would invite re-litigating decisions instead of building.

### It converts requirements into structures

Requirements are written to be *testable*, which makes them deliberately implementation-agnostic. FR-004 says supplier keys must resolve via a temporal range join with `valid_from DESC` tie-breaking and a 0 fallback. That is verifiable but not buildable — it does not say which table, which column names, which cast, or which module.

The design closes that gap. FR-004 becomes CALC-002, with the full join predicate, the exact `ROW_NUMBER() OVER (PARTITION BY purchase_staging_key ORDER BY dim.valid_from DESC) = 1` window, the `COALESCE(dim.supplier_key, 0)` fallback, the named input columns, the named output column, and the module it lives in (`sk_resolver.py`). A generator can write that; it could not have written FR-004.

### It is the last document before code

Everything upstream can be revised cheaply. Once code generation runs against this design, its choices are embodied in DDL files, notebooks, tests, and a Workflow definition. An error here propagates into every generated artifact — which is why the divergence section below matters more than it would in an earlier spec.

---

## Section 1 — Data Model

### 1.1 Entities

Eight tables across two layers, all Delta managed:

| Layer / Schema | Table | Role |
|---|---|---|
| silver / `silver_fact` | `fact_purchase` | The central fact. One row per purchase order line. CLUSTER BY (date_key, supplier_key). |
| silver / `silver_dim` | `supplier` | SCD-2. **Externally owned.** CLUSTER BY (supplier_key). |
| silver / `silver_dim` | `stock_item` | SCD-2. **Externally owned.** CLUSTER BY (stock_item_key). |
| silver / `silver_dim` | `date` | Static reference. **Externally owned.** PK is `date` (DATE). |
| bronze / `bronze` | `purchase_staging` | OVERWRITE per run. Landing table for the incremental extract. |
| bronze / `bronze` | `etl_cutoff` | Watermark control — one row per tracked table. |
| bronze / `bronze` | `lineage_run` | Audit log — one row per ETL run. IDENTITY PK, CDF enabled. |
| bronze / `bronze` | `dq_rejections` | DQ rejection sink. IDENTITY PK, autoOptimize enabled. |

**The layer split resolves an open question from the earlier specs.** The product brief used `dim.` / `stg.` / `mart.` schemas; the product scope's target boundary specified bronze/silver/gold. The design settles on **bronze + silver, with silver split into `silver_dim` and `silver_fact`, and no gold layer** — consistent with the scope's finding that Purchase owns no analytics views. `stg.lineage` became `bronze.lineage_run`; `stg.dq_rejections` became `bronze.dq_rejections`.

**Three of eight entities are marked "Externally owned."** This is the product scope's ownership boundary carried into the data model. Purchase's DDL generation covers the five bronze and silver_fact tables; the three dimensions are declared so that FKs, joins, and RI checks can reference them, not so they get created here.

### 1.2 Attributes

Full column-level definitions for the five Purchase-owned tables — 11 columns on `fact_purchase`, 15 on `purchase_staging`, 9 on `lineage_run`, 3 on `etl_cutoff`, 10 on `dq_rejections`. Every column has a type, a nullability, and a description that names its purpose.

**Staging carries four columns the fact does not**, and each earns its place:

| Staging-only column | Why it exists |
|---|---|
| `wwi_supplier_id INT NOT NULL` | The **business** FK. `sk_resolver.py` joins on this to find the surrogate key. |
| `wwi_stock_item_id INT NOT NULL` | Same, for stock item. |
| `last_modified_when TIMESTAMP NOT NULL` | The **temporal probe** — the timestamp compared against `valid_from`/`valid_to` to pick the right SCD-2 version. |
| `_extracted_at_utc TIMESTAMP NOT NULL` | Extraction wall-clock time, for freshness auditing independent of the watermark (OB-P002). |

This is the SCD-2 resolution pattern made visible in the schema. Staging arrives with business keys and a timestamp; `sk_resolver.py` converts them to surrogate keys; the fact stores only the surrogate keys plus `wwi_purchase_order_id` retained as the MERGE predicate. The business keys and the probe timestamp are deliberately *not* propagated to the fact — they were inputs to resolution, not attributes of the grain.

**Nullability encodes the pipeline order.** `supplier_key` and `stock_item_key` are `NULL`-able in staging but `NOT NULL` in the fact. Staging is written by the extract before resolution has run; the fact is written after. The transition from NULL to NOT NULL is enforced by DQR-009: after `sk_resolver.py`, no staging row may have a null key — unresolved rows get 0, never NULL.

**`lineage_run.was_successful` is three-valued on purpose.** `NULL` while running, `true` on success close, `false` on failure close. A two-valued flag could not distinguish "still running" from "failed," which is exactly the distinction an operator needs when a job is hung.

### 1.3 Relationships

Six many-to-one relationships. Three are the expected dimensional FKs (`supplier_key`, `stock_item_key`, `date_key`); the other three all point at `bronze.lineage_run` — from `fact_purchase`, from `purchase_staging`, and from `dq_rejections`.

That second group is the audit spine. Every row of data and every quality violation joins back to the run that produced it, which is what makes `WHERE lineage_key = X` a complete slice of one execution. It is also what DQR-008 requires for "surgical investigation and batch replay."

Note the `date_key = date` join: the fact's column is `date_key` and the dimension's PK column is `date`. The names differ, so the design states the join columns explicitly rather than relying on a name match.

### 1.4 Indexes and Partitioning

| Entity | Strategy | Applicability |
|---|---|---|
| `fact_purchase` | CLUSTER BY (`date_key`, `supplier_key`) — liquid clustering | DBR 13.3+ |
| `fact_purchase` | PARTITIONED BY (`date_key`) + ZORDER BY (`supplier_key`, `stock_item_key`) | Pre-DBR 13.3 — the PE-P001 fallback |
| `supplier`, `stock_item` | CLUSTER BY (surrogate key) | DBR 13.3+ — optimises point-lookup joins from the fact |
| `purchase_staging` | None | Ephemeral |

**Two mutually exclusive fact strategies, selected by runtime version.** A table gets one or the other, never both. Liquid clustering is the default; partition + Z-ORDER is the fallback when the runtime is older than DBR 13.3.

This is worth comparing against the product brief, which selected the strategy from the **source index type** — CCI → liquid clustering, rowstore date B-tree → partition + Z-ORDER. The product scope records `fact.purchase` as **rowstore**, so the brief's rule points at partition + Z-ORDER. The design instead makes liquid clustering the default and demotes partition + Z-ORDER to a runtime fallback, matching PE-P001 as the product rules state it. The selection criterion changed from *source evidence* to *target runtime capability*. Both are defensible; the design and the product rules agree, so the design governs. It is simply not what the brief's rule alone would produce.

The dimension clustering is also a departure — the brief said dimension tables get no explicit `CLUSTER BY` because Delta's default layout suffices for small tables. The design clusters both on their surrogate keys, justified by the point-lookup join from the fact.

---

## Section 2 — Ingestion

### 2.1 Ingestion Patterns

Five inputs, each with a write mode and — importantly — an **error-handling policy**:

| Input | Pattern | On failure |
|---|---|---|
| `purchase_staging` | Batch, full OVERWRITE per run | Task FAILED; staging left empty; MERGE skipped by the zero-rows guard |
| `silver_dim.supplier` | Read-only SCD-2 join in `sk_resolver.py` | `sk_resolver.py` raises; task FAILED |
| `silver_dim.stock_item` | Read-only SCD-2 join | Same |
| `silver_dim.date` | Read-only reference join at extract | `date_key` derived in extract; missing FKs caught post-merge by QA-P003 |
| `bronze.etl_cutoff` | Point lookup at job start | Falls back to `initial_load_date` from `config/environment.yaml` |

**OVERWRITE is the bug fix.** Risk #1 in the product scope is the SSIS dataflow that truncates the wrong table, so purchase staging accumulates stale rows. Here staging is written in OVERWRITE mode, which makes stale-row carry-forward structurally impossible rather than dependent on a truncate step running correctly. FR-001's acceptance criterion tests exactly this: after each run, staging contains only rows from the current extraction.

**The dimensions fail loudly; the date dimension does not.** An empty or unavailable `supplier`/`stock_item` raises and fails the task, because resolution against a missing dimension would silently assign key=0 to every row — a full batch of unresolved keys that looks like valid output. A missing *date* FK, by contrast, is handled post-merge by QA-P003 as a non-blocking rejection. The asymmetry is deliberate: one condition corrupts the whole batch, the other affects individual rows.

**The cutoff has a documented cold-start path.** No `etl_cutoff` record means first run, and the design names the fallback (`initial_load_date` from config) rather than leaving the query to return NULL and the window to become undefined.

### 2.2 Extract Window Computation

```
last_cutoff    ← SELECT cutoff_time FROM bronze.etl_cutoff WHERE table_name = 'fact_purchase'
                 (default: config.purchase.etl.initial_load_date if no record exists)
current_cutoff ← CURRENT_TIMESTAMP()
Rows extracted ← WHERE last_modified_when >  last_cutoff
                   AND last_modified_when <= current_cutoff
```

**The bounds are asymmetric and that is the point.** Lower bound exclusive (`>`), upper bound inclusive (`<=`). Consecutive windows therefore abut exactly: no row is extracted twice, no row falls between two runs. Getting both bounds inclusive duplicates boundary rows; both exclusive drops them. Writing the operators out means a generator cannot guess.

**`current_cutoff` is captured once, at the start.** Pinning the upper bound before extraction means rows modified *during* the run are excluded from this window and picked up by the next one. If the upper bound were evaluated later, or per-query, rows arriving mid-run would land in a window whose recorded cutoff does not cover them — and would never be re-extracted.

**The lineage key is created by insert-then-read.** A row goes into `bronze.lineage_run`, the generated IDENTITY value is read back, and it is published via `dbutils.jobs.taskValues.set(key="lineage_key", ...)`. This is the concrete replacement for `sequences.lineagekey` (Risk #3 in the product scope): the Delta IDENTITY column supplies the number, and the audit row's existence is what allocates it.

### 2.3 Zero-Rows Guard

Every notebook in `src/etl/` counts `bronze.purchase_staging` and, if the count is 0, exits via `dbutils.notebook.exit("SKIPPED: zero rows")` before any write.

Purchase's nightly volume is variable — some nights nothing changes. Without the guard, an empty batch still runs a MERGE, still triggers the OPTIMIZE evaluation, and still runs nine QA assertions against nothing. Worse, the row-count reconciliation compares 0 to 0 and passes, so an empty run is indistinguishable from a successful one in the logs. The explicit `SKIPPED` exit makes "nothing to do" a visible, distinct outcome.

---

## Section 3 — Transformation Logic

### 3.1 Calculations

Six numbered calculations, each with a formula, named input columns, a named output column, and the module that executes it.

| ID | What | Where |
|---|---|---|
| CALC-001 | `date_key` = `CAST(order_date AS DATE)` | `nb_extract_purchase`, during the OLTP extract JOIN |
| CALC-002 | `supplier_key` resolution — temporal range join + `ROW_NUMBER` tie-break + `COALESCE(…, 0)` | `sk_resolver.py` |
| CALC-003 | `stock_item_key` resolution — same pattern on `wwi_stock_item_id` | `sk_resolver.py` |
| CALC-004 | `lineage_key` — INSERT into `lineage_run`, read IDENTITY | `nb_extract_watermark` |
| CALC-005 | `_extracted_at_utc` = `current_timestamp()` | `nb_extract_purchase` |
| CALC-006 | `rows_merged` count → `lineage_run.table_row_count` | `fact_merge.py`, after MERGE |

**CALC-002 is the heart of the product**, and the design spells out all three of its parts:

```
wwi_supplier_id == dim.wwi_supplier_id
  AND last_modified_when >  CAST(dim.valid_from AS TIMESTAMP)
  AND last_modified_when <= CAST(dim.valid_to   AS TIMESTAMP)
ROW_NUMBER() OVER (PARTITION BY purchase_staging_key ORDER BY dim.valid_from DESC) = 1
COALESCE(dim.supplier_key, 0)
```

Three details each guard against a specific failure:

- **The explicit `CAST(… AS TIMESTAMP)`** is the visible consequence of override TY-P001. `valid_from`/`valid_to` are DATE (day-granularity business validity); `last_modified_when` is a TIMESTAMP. The cast is written out so the granularity mismatch is auditable rather than left to implicit coercion.
- **The same asymmetric bounds as the extract window** — `>` on `valid_from`, `<=` on `valid_to`. Adjacent SCD-2 versions therefore cannot both match a probe timestamp on their shared boundary.
- **`ROW_NUMBER` with `valid_from DESC`** picks the most recent version when ranges overlap anyway, and `COALESCE(…, 0)` routes anything unmatched to the sentinel row. Together they guarantee exactly one non-null key per staging row, which is what DQR-009 asserts.

**CALC-006 counts by lineage key, not by MERGE metrics.** `rows_merged` comes from `SELECT COUNT(*) FROM fact_purchase WHERE lineage_key = …`. Because the MERGE's UPDATE branch also sets `lineage_key = source.lineage_key`, both inserted and updated rows carry the current run's key — so the count covers the full merged set, not just inserts. This is the number QA-P001 reconciles against the staging count and the number written to `lineage_run.table_row_count`.

### 3.2 Filters

Four numbered filters, each with a condition and an application point: FLT-001 the incremental watermark window, FLT-002 the SK temporal range, FLT-003 the `ROW_NUMBER` tie-breaker, FLT-004 the OPTIMIZE threshold (`rows_merged > 10,000`, read from `config/environment.yaml` under `purchase.etl.fact_optimize_row_threshold`).

FLT-002 and FLT-003 restate parts of CALC-002/003 — intentional redundancy so a reader looking for "what filters run and where" finds them without reverse-engineering the calculation formulas.

FLT-004 resolves the divergence I flagged in the product brief: the brief put the threshold in `constants.py`, but PE-P002 and CX-P001 externalize tunable values to `environment.yaml`. The design follows the rules, with the exact config path.

### 3.3 MERGE Logic

An executable statement: `MERGE INTO inventory_stock.silver_fact.fact_purchase AS target USING inventory_stock.bronze.purchase_staging AS source ON target.wwi_purchase_order_id = source.wwi_purchase_order_id`, with a MATCHED branch updating nine columns and a NOT MATCHED branch inserting ten.

**`purchase_key` appears in neither branch.** It is `GENERATED ALWAYS AS IDENTITY`, so Delta assigns it. Listing it in the INSERT column list would fail.

**`lineage_key` is updated on matched rows.** That is what makes CALC-006's count-by-lineage-key work, and it means the fact records the *most recent* run that touched each row rather than the run that first created it.

This single statement replaces the legacy pattern of `DELETE FROM Fact.Purchase WHERE [WWI Purchase Order ID] IN (SELECT … FROM staging)` followed by a bulk `INSERT` — an order-level full-replacement. The MERGE is the idempotent equivalent, and FR-007's acceptance criterion tests exactly that: running it twice with the same input yields the same row count.

**But see the MERGE predicate issue below.** The `ON` clause here is narrower than the to-be design specifies, and the difference matters.

---

## Section 4 — Serving

### 4.1 and 4.2 — Output Ports and Reports

Two output ports: a **Databricks SQL Warehouse** over `fact_purchase` (JDBC/HTTP, Unity Catalog RBAC, available by 06:00 UTC) and a **Power BI semantic model** over the fact plus both dimensions (DirectQuery or Import).

Both reports from the product scope reappear with their access method and table lists: `wwidw_ordered_by_supplier` is self-contained within Purchase; `wwidw_purchase_and_sale_per_stockitem_dynamic` also reads `silver_fact.fact_sale` from the Sales_Orders product and is annotated as requiring coordinated cutover.

**The cross-product dependency survives every spec unchanged** — product scope §3.6 and §5, Risk #7, and now the serving layer. It is a constraint no amount of Purchase-side design can remove, and carrying it to the last spec before code keeps it from being discovered at cutover.

### 4.3 Views

Two thin views, `supplier_current` and `stock_item_current`, both `CREATE OR REPLACE VIEW` over `WHERE is_current_row = TRUE`.

The section closes with an explicit note: these are row-filter views with no aggregation and are **NOT** materialized; any future gold-layer aggregating view must use `CREATE OR REPLACE MATERIALIZED VIEW`. That is OB-P003 applied and its unused half recorded — materializing a `WHERE is_current_row = TRUE` filter would spend compute to duplicate a predicate Delta evaluates cheaply. The note exists because "materialized is faster" is the intuitive and wrong default.

---

## Section 5 — Observability

### 5.1 Validation Rules

Nine rules, QV-001 through QV-009, each mapped to its QA rule, its target, its threshold, and its failure action.

| Group | Rules | Failure action |
|---|---|---|
| Completeness | QV-001 (QA-P001 row count) | **`RuntimeError` → task FAILED; `lineage_run.was_successful = false`** |
| Consistency | QV-002/003/004 (QA-P003 RI on the three FKs) | Log ERROR; write to `dq_rejections`; **continue** |
| Uniqueness | QV-005/006 (QA-P002 orphan detection, excl. key=0) | Log WARNING; continue |
| Accuracy | QV-007/008/009 (QA-P004 business rules) | Log WARNING; continue |

**One blocking rule out of nine.** QV-001 blocks because a staging/fact count mismatch means rows were silently lost, and allowing the watermark to advance on top of that loss makes the gap permanent — the next run's window starts after the rows that never landed. The other eight surface conditions that mostly originate upstream, outside Purchase's control; failing nightly on them would produce outages for defects Purchase cannot fix.

**The 4 brief assertions became 9 concrete rules** by expansion along the columns they apply to: one RI assertion became three (one per FK), one orphan check became two (one per SCD-2 dimension), one business-rule assertion became three (quantities, date window, package). Each is separately implementable and separately testable.

**Orphan detection excludes key=0 explicitly.** The sentinel row is the *expected* destination for unresolved lookups. Without the exclusion, every legitimately unresolved row would be reported as an orphan, and the check would fire constantly on correct behavior.

### 5.2 Lineage and Auditability

Four components: `bronze.lineage_run` (IDENTITY PK, CDF enabled) as one record per run; `lineage_key` propagation via `taskValues.set/get`; `bronze.dq_rejections` as an append-only sink; and a **post-run DQ summary** — `SELECT rule_id, COUNT(*) FROM dq_rejections WHERE lineage_key = X GROUP BY rule_id` — logged at the end of every run.

The summary is the piece that makes eight non-blocking assertions operationally real. Non-blocking checks that only write rows produce a table nobody queries. Aggregating them by rule at the end of the run puts the count in the job log where an operator already looks, while the detail rows stay in `dq_rejections` for investigation.

### 5.3 Alerting

Five conditions across three severities: CRITICAL for both task-failure paths (QA-P001 mismatch, unhandled exception), WARNING for RI violations, INFO for business-rule violations and orphan counts.

The severities line up with the blocking policy in §5.1 — the two things that stop the pipeline page someone; the rest are reviewed. Both CRITICAL rows route to the same Databricks Workflow task-failure notification, since from an operator's perspective a failed task is a failed task; the distinction is for triage after the page.

### 5.4 Workflow Task Structure

Three tasks:

| Task | Depends on | Does |
|---|---|---|
| `nb_extract_watermark` | none (entry) | Open lineage record; compute the extract window; publish `lineage_key` |
| `nb_extract_purchase` | `nb_extract_watermark` | Extract incremental rows → `purchase_staging` (OVERWRITE) |
| `migrate_staged_purchase_data` | `nb_extract_purchase` **+ dimension load tasks (external)** | SK resolution; MERGE; QA checks; close lineage |

**The external dependency is the design's answer to Risk #6.** The Purchase fact load cannot start until the supplier and stock item dimension loads have succeeded — an ordering that was implicit in the SSIS container graph and documented nowhere. Here it is an edge in the task graph, enforced by the scheduler rather than by convention.

**Exactly one task opens the lineage record.** `nb_extract_watermark` is the only producer of `lineage_key`; the other two consume it via `taskValues.get`. This is LN-P001, and it is why `taskValues` was chosen over each task reading the control table — a shared read would let two tasks allocate two keys for one run.

---

## Divergences and Open Items

An explained doc should not smooth over inconsistencies. Four are worth knowing about, in descending order of consequence.

### 1. The MERGE predicate is narrower than the to-be specifies — verify before generating

| Spec | MERGE `ON` clause |
|---|---|
| **to-be.md** (steps 15, and the lineage diagram) | `wwi_purchase_order_id` **AND** `date_key` **AND** `supplier_key` **AND** `stock_item_key` — described as "idempotent upsert at the order-line grain" |
| **design.md §3.3** and **FR-007** | `wwi_purchase_order_id` **only** |

The fact grain is stated in §1.1 as "one row per purchase order line," and the as-is confirms it: the extract JOINs `Purchasing.PurchaseOrderLines`, so one purchase order contributes one row **per stock item line**. `wwi_purchase_order_id` is therefore not unique at the fact grain.

A Delta `MERGE` whose `ON` clause matches multiple source rows to one target row raises an error rather than picking one, so this would surface at first run rather than corrupt data silently — but it would block the pipeline, and it would also make FR-007's idempotency criterion untestable as written.

The likely origin is the legacy pattern: the source used `DELETE … WHERE [WWI Purchase Order ID] IN (SELECT …)` followed by a bulk INSERT, an *order-level* replacement where the order ID alone was the correct predicate. The to-be converted that to an order-line-grain MERGE with the 4-column composite key; the design and FR-007 appear to have carried the legacy delete predicate forward instead. **The to-be's 4-column key looks correct and the design's should be reconciled to it before code generation.**

### 2. The watermark advance is missing from the design

FR-002 requires `bronze.etl_cutoff` to be updated to the current cutoff after each successful run, and its acceptance criterion tests it. The to-be assigns this to step 21 — `set_etl_cutoff(spark, "fact_purchase", new_cutoff)` inside `migrate_staged_purchase_data.py`.

The design computes `current_cutoff` in §2.2 but never says it is committed. §3.1's calculations do not include it, and §5.4's purpose line for `migrate_staged_purchase_data` lists "SK resolution; MERGE INTO fact_purchase; QA checks; close lineage" — no watermark commit. A generator working only from this design would omit the step, and the pipeline would silently re-extract the same window every night.

The to-be supplies the missing detail, so this is an omission rather than a contradiction — but it is an omission in the document the generator reads.

### 3. The brief's calendar-key convention correctly did not apply

The product brief §4 specified that the static calendar's PK is `date_key INT` in YYYYMMDD format, "not a DATE column." The design uses `date_key DATE`, joining to a `date` DATE column.

This is not a defect. The as-is shows the source deriving `CAST(po.OrderDate AS date) AS [Date Key]` — the source key is genuinely DATE-typed. The brief's integer convention was written for warehouses that use integer date keys and, being generic project-wide guidance, correctly did not fire here. It is worth noting only because the brief states it emphatically, and a reader moving between the two documents will notice the contradiction.

### 4. Minor cross-document naming inconsistencies

Three small ones, none blocking, all worth catching in review:

- **NFR-007** says `dq_rejections` has "nine required columns" and then lists ten. The design's schema has ten. The design is right.
- **NFR-004**'s acceptance criterion references `fk_column = 'supplier_key'`, but the `dq_rejections` schema has no `fk_column` — the equivalent is `violation_column`.
- **to-be step 21** writes `WHERE product_name = 'fact_purchase'` on `etl_cutoff`, but the design's `etl_cutoff` PK is `table_name`. The design is self-consistent (§1.2 and §2.2 both use `table_name`).
- **Layout**: the brief's tree nested ETL code in six task-group subfolders (`ingestion/`, `dimensions/`, `facts/`, `mart/`, `dq/`, `security/`); §5.4 places notebooks flat in `src/etl/`, matching NFR-011's shorter required layout. Purchase's 3-task pipeline does not need six groups, so the flattening is reasonable — but generators reading the brief and generators reading NFR-011 would disagree.

---

## How This Spec Is Used Downstream

| Consumer | What it takes from the design |
|---|---|
| **`tasks.md`** | Every entity in §1.1 becomes a DDL task; every calculation in §3.1 becomes an implementation task; §5.4's three tasks become the Workflow definition task |
| **SmartBuilder `generate-db`** | §1.2 column tables become `CREATE TABLE` statements; §1.4 supplies `CLUSTER BY` / `PARTITIONED BY`; §1.1 supplies TBLPROPERTIES (CDF, autoOptimize) |
| **SmartBuilder `generate-etl`** | §2.2 becomes `nb_extract_watermark`; §3.1 CALC-002/003 become `sk_resolver.py`; §3.3 becomes `fact_merge.py`; §5.1 becomes the DQ notebook |
| **Generated tests** | §5.1's thresholds and failure actions become assertions; §3.1's formulas become unit-test expectations |
| **`config/environment.yaml`** | FLT-004's threshold path, §2.1's `initial_load_date` fallback |
| **Workflow definition YAML** | §5.4's task graph, including the external dimension-load dependency |
| **`validation.md`** | Validates generated artifacts against §1.2 schemas and §5.1 rules |
| **Runbook** | §5.3 alert conditions become response procedures; §2.3's SKIPPED exit becomes an expected non-error state |

---

## File Reference

| File | Location |
|---|---|
| `design.md` | `products/Purchase/current/specifications/development_plan/design.md` |
| `requirements.md` | same directory — the 32 requirements this design implements |
| `product-definition.yaml` | same directory — the ODPS definition requirements were derived from |
| `tasks.md` | same directory — the build order derived from this design |

277 lines, generated 2026-09-07. It is the shortest of the three narrative development-plan documents and the densest: almost every line is a schema row, a formula, or a rule, with little prose. That density is the point — it is written to be read by a code generator, and the justifications live upstream in `to-be.md`.
