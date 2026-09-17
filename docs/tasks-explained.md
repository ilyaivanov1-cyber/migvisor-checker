# Implementation Tasks — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `development_plan/design.md` + `development_plan/requirements.md`
**Contents:** 26 tasks — DDL 8 | ETL 9 | Config 2 | Test 3 | BI 2 | Docs 2
**Output:** 26 files across `src/db/`, `src/common/`, `src/etl/`, `src/init/`, `config/`, `tests/`, `docs/`

---

## What This Spec Is

The task list is the **work order**. It converts the design into a numbered, dependency-ordered set of units of work, each producing exactly one file, each traced back to the requirements it satisfies.

It is the last of four development-plan artifacts, and it is the handoff point to SmartBuilder:

| Artifact | Question it answers |
|---|---|
| `product-definition.yaml` | What is this product, in ODPS terms? |
| `requirements.md` | What must be true when we are done? |
| `design.md` | How is that achieved? |
| **`tasks.md`** | In what **order** do we build it, and **what files** come out? |

It has two parts:

1. **Task Summary** — one table, 26 rows: `Task ID`, `Type`, `Title`, `Depends On`, `Requirements`. This is the dependency graph in tabular form.
2. **Task Details** — 26 sections, each with Type, Depends On, Requirements, **Output File**, Description, an inline artifact (DDL, Python constants, or a numbered skeleton), and an Acceptance criterion.

Think of it as the **bill of materials plus the build order**. The design says what the system is; this says what gets typed, in what sequence, and how you know each piece is done.

---

## Why This Spec Exists

### Because a design is not a sequence

`design.md` describes a finished system: eight tables, six calculations, three Workflow tasks. It is organized by layer, which is the right way to *understand* a system and the wrong way to *build* one. Nothing in the design says that `bronze.lineage_run` must exist before `bronze.purchase_staging` can be created, or that `constants.py` must be settled before any notebook is written.

The task list supplies that ordering, and it supplies it as data rather than prose — a `Depends On` column that can be topologically sorted. That is what lets work be parallelised safely and what lets a generator emit files in an order where each one's references already exist.

### Because it is where the spec becomes files

Every task names exactly one **Output File**. Twenty-six tasks, twenty-six paths. This one-to-one mapping is the contract with SmartBuilder: `generate-db` and `generate-etl` take a task ID and produce the named file, and nothing else. No task produces two files; no file comes from two tasks.

That constraint is what makes generation auditable. `validation-report.md` can walk the 26 rows and check each path, because the task list already decided what the tree looks like. A task list that said "implement the ETL layer" would leave the file boundaries to the generator and there would be nothing to validate against.

### Because acceptance moves from the abstract to the concrete

Requirements have acceptance criteria written against behaviour ("no staging row has a null `supplier_key`"). Task acceptance criteria are written against artifacts:

- TASK-001: `DESCRIBE TABLE … returns all 9 columns`; `SHOW TBLPROPERTIES` returns CDF enabled
- TASK-009: `from src.common.constants import FACT_PURCHASE_TABLE` returns the expected string
- TASK-020: `pytest tests/common/test_sk_resolver.py` exits 0

These are checks you can run against a file the moment it is written, without a cluster, a dataset, or a full pipeline run. That is what makes the build incremental — each task can be closed on its own evidence rather than waiting for an end-to-end run.

### Because several DDL tasks carry their own artifact inline

Five DDL tasks (TASK-001 – TASK-005) and one grants task (TASK-008) include the **complete SQL**, header block and all. TASK-009 includes the constants. TASK-017 includes the sentinel INSERT. TASK-018 includes the YAML.

This is unusual — a task list that contains its own deliverable blurs the line between plan and implementation. It is justified here because these artifacts are short, entirely determined by the design's schema tables, and load-bearing for everything downstream. Writing them out at plan time means the column list is reviewed once, in one place, before nine notebooks and three test files are generated against it.

---

## Part 1 — The Task Summary and the Dependency Graph

### What it contains

Twenty-six rows across six types. The distribution is worth reading as a statement about where the work is:

| Type | Count | What it produces |
|---|---|---|
| DDL | 8 | 5 tables, 2 views, 1 grants script |
| ETL | 9 | 5 shared modules, 3 notebooks, 1 init notebook |
| Config | 2 | `environment.yaml`, the Workflow JSON |
| Test | 3 | Two unit suites, one integration suite |
| BI | 2 | Two report reconnection specs |
| Docs | 2 | ETL design doc, data dictionary |

The stated totals are correct: TASK-001–008 DDL, 009–017 ETL, 018–019 config, 020–022 test, 023–024 BI, 025–026 docs.

### Key facts captured

**Six tasks have no dependencies and form the first parallel wave.** TASK-001 (`lineage_run`), TASK-002 (`etl_cutoff`), TASK-006 and TASK-007 (the two `_current` views), TASK-010 (`scd2_merge.py`), and TASK-018 (`environment.yaml`). Everything else waits on at least one of them.

**The graph converges hard on TASK-016.** `migrate_staged_purchase_data.py` depends on TASK-011, TASK-012, TASK-014, and TASK-015 — and transitively on almost the entire DDL and shared-module set. It also carries the largest requirement list in the document: FR-007, FR-008, NFR-003 through NFR-007, NFR-009, and DQR-001 through DQR-009. Three other tasks depend on it in turn (TASK-019, TASK-022, TASK-025). It is the keystone: nothing meaningful can be integration-tested until it exists, and it is the single riskiest unit of work in the plan.

**None of the DDL dependencies are technically necessary, and that is the point.** Delta Lake does not enforce foreign keys — `PRIMARY KEY` in TASK-001 is a declarative hint, not a constraint. So `bronze.purchase_staging` (TASK-003) would create successfully whether or not `bronze.lineage_run` exists, despite its `lineage_key` column. The dependency edges therefore encode **review order** rather than execution order: settle the audit table's key before declaring columns that reference it. That is a legitimate use of the graph, but it means the graph cannot be trusted as a statement about what would fail if run out of order.

One edge looks spurious even on that reading: TASK-003 depends on TASK-002 (`etl_cutoff`), but `purchase_staging` has no column, comment, or reference touching the watermark table. TASK-001 explains itself through `lineage_key`; TASK-002 does not.

**TASK-006 and TASK-007 have no dependencies because their base tables are not ours.** Both views select from `silver_dim.supplier` / `silver_dim.stock_item`, which the product scope designates as **externally owned** — loaded by a separate product. You cannot declare a dependency on a task that does not exist in your own plan, so the edge is simply absent. The consequence is a real hole: `CREATE OR REPLACE VIEW` will fail if the external dimension has not been created yet, and nothing in the build graph warns you.

The runtime graph handles this better. TASK-019's Workflow JSON declares `supplier_load` and `stock_item_load` as upstream dependencies of `migrate_staged_purchase_data`, "referenced by task name only." So the external dependency is expressed where the job runs but not where the code is built — a reasonable split, as long as whoever executes the DDL knows to sequence behind the dimension owner.

### Why this section matters

The summary table is what a build coordinator reads. It answers "what can six people start on Monday" (the six root tasks), "what is the critical path" (TASK-001 → 009 → 011/012 → 016 → 019/022), and "what is safe to defer" (the BI and docs tasks, which depend only on TASK-005 and TASK-016 and block nothing).

---

## Part 2 — Task Details

### DDL tasks (TASK-001 – TASK-008)

**All four column counts in the acceptance criteria are correct** — `lineage_run` 9, `purchase_staging` 15, `dq_rejections` 10, `fact_purchase` 11. Worth checking because the counts are the cheapest thing to get wrong and the easiest thing to test.

Notably, **TASK-004 quietly corrects an error upstream.** NFR-007 says `dq_rejections` has "nine required columns" and then lists ten. TASK-004's DDL declares ten and its acceptance criterion says ten. The task list is right and the requirement's count is wrong; nothing in the document flags the discrepancy, so the correction is invisible unless you compare them.

**Every DDL file carries the CX-P006 header block with a populated RULES field.** This is what NFR-010 demands, and it is the mechanism that keeps the rule trace alive inside emitted SQL — `fact_purchase` records that PE-002, PE-008, PE-P001, TY-004, NM-009 and nine others shaped it. A reader of the generated file can reconstruct why every choice was made without leaving the file.

**TASK-005 expresses the PE-P001 clustering fallback as a comment, and the actual decision is made in a different task.** The DDL uses `CLUSTER BY (date_key, supplier_key)`, with the pre-DBR-13.3 alternative (`PARTITIONED BY (date_key)` + post-DDL `ZORDER`) commented out below. That means the fallback is not executable — taking it requires a manual edit. What resolves the ambiguity is TASK-019, which pins the runtime to "DBR 13.3 LTS or later (for Liquid Clustering)." So the branch is decided by the Workflow config, four tasks away from the DDL that carries it. The comment is then dead weight, and worth removing once the runtime is confirmed.

**TASK-006 and TASK-007 spend most of their description saying what *not* to build.** Both must be plain `CREATE OR REPLACE VIEW`, explicitly **not** `MATERIALIZED VIEW`, per OB-P003 — because they are thin row filters (`WHERE is_current_row = TRUE`) with no aggregation, and materializing them would add refresh cost and staleness for no scan benefit. The rule reserves materialized views for future Gold-layer aggregations. Their acceptance criteria are elegantly minimal: `SELECT COUNT(*) … WHERE is_current_row = FALSE` returns 0.

**TASK-008 is a plan for GRANTs, not executable GRANTs.** It defines three access tiers — BI/analysts read the silver serving layer, the ETL principal gets `SELECT, MODIFY` on whole bronze and `silver_fact` schemas, data engineering reads `dq_rejections` — but the principal names are `{{BI_SERVICE_PRINCIPAL}}` and `{{ETL_SERVICE_PRINCIPAL}}` placeholders. The description says so plainly: "substitute actual Unity Catalog principal names before execution." This is the correct handling of PD-003 (the pending role matrix): generate the structure, defer the identities, and make the deferral visible in the file rather than blocking the task.

The schema-level grant for ETL is the right granularity choice — new bronze tables inherit access automatically instead of requiring a grants change per table.

### Shared module tasks (TASK-009 – TASK-013)

**TASK-009 settles a split that earlier specs left ambiguous.** `constants.py` contains **table identifiers only** — catalog, three schemas, eight fully-qualified table names, and `ETL_CUTOFF_TABLE_NAME = "fact_purchase"`. It contains no thresholds, no dates, no business factors. Those live in `config/environment.yaml` (TASK-018) per FR-009. The product brief's mention of both files as homes for constants had left this unclear; the task list resolves it cleanly: **identifiers are code, tunables are config.** That is the right line — a table name changing is a code change, a threshold changing is not.

**TASK-011 is the most technically detailed task in the document**, and it needs to be. The SK resolver's three-step algorithm is spelled out: the temporal range predicate with its asymmetric bounds (`> valid_from`, `<= valid_to`), the `ROW_NUMBER() … ORDER BY dim.valid_from DESC = 1` tie-breaker for overlapping versions, and the `COALESCE(…, 0)` sentinel fallback. Two rule-driven details are called out that a generator would otherwise miss:

- `BROADCAST` hint on the dimension DataFrames, per PE-006 — dimensions are small, the staging batch is not, and a broadcast join avoids shuffling the fact-sized side.
- The **explicit cast** of `valid_from` / `valid_to` from DATE to TIMESTAMP before comparison, because TY-P001 (the single product-level override) made them DATE while `last_modified_when` is a TIMESTAMP. Silent type coercion across that boundary is exactly the kind of thing that produces off-by-one-day resolution errors, so making the cast explicit in the task is well judged.

Its four acceptance cases map one-to-one onto the failure modes: in-range match, no match, overlapping versions, and no NULLs.

**TASK-010 builds a module this product does not use.** `scd2_merge.py` implements the standard SCD-2 close-and-insert pattern, and the description concedes its position: "Used by the dimension load process (**externally owned** for supplier and stock_item; included here as a shared helper per OB-P004)."

Three things follow. Nothing in the task graph depends on TASK-010. No notebook task imports it. And no test task covers it — despite TASK-010's own acceptance criterion describing a unit test ("apply_scd2_merge on a test Delta table…") that TASK-020, TASK-021, and TASK-022 do not include. So it is a task whose output is, within this product's boundary, unreferenced code with an unwritten test. Whether that is correct depends on whether the Purchase product is meant to *own* the shared SCD-2 helper for the project. If so, the plan should say so and add the test task; if not, the task belongs to the dimension product.

**TASK-013 is a consolidation task masquerading as a creation task.** `udfs.py` exists to collect "duplicate scalar function patterns identified across Purchase ETL notebooks" into one module, with three mandatory properties per UDF: an explicit `None` guard, empty-string handling, and a docstring stating business purpose. Its most interesting acceptance criterion is the last one — "no duplicate scalar function body exists in `src/etl/` notebooks (static scan)" — which is a check on *other* tasks' output. It only passes if TASK-014 through TASK-017 all import rather than reimplement.

Note that `udfs.py` is a fifth `src/common/` module, while NFR-011 names only four as required. The requirement's list is a floor, not a ceiling, but the mismatch is worth knowing when reading NFR-011's acceptance criterion literally.

### Notebook tasks (TASK-014 – TASK-017)

**Each notebook task is written as a numbered CX-P005 skeleton**, which is what makes NFR-009's six-section conformance requirement checkable. More useful than the conformance itself is that the tasks **document their own deviations**:

TASK-014 states plainly that `nb_extract_watermark` has **no zero-rows guard** (it extracts a watermark, not data) and does **not** receive `lineage_key` via `taskValues.get` — it *generates* it. Without that note, a validator checking six-section conformance would flag the notebook as non-compliant, and a generator following the template blindly would insert a `taskValues.get` call for a value that does not yet exist. Documenting a justified exception is more valuable than a template that pretends there are none.

Its acceptance criterion is precise about the in-flight state: `bronze.lineage_run` contains a new row with `was_successful = NULL` — run in progress. That NULL is the whole reason the column is three-valued, and testing for it here is what makes "running" distinguishable from "crashed" later.

**TASK-015 is the only task that touches the source system, and it does so in one clause.** Step 5: "JDBC query with `WHERE last_modified_when > last_cutoff AND last_modified_when <= current_cutoff`." No driver, no connection profile, no credential source, no secret scope. This is where the requirements' silence on the inbound extract lands — see divergence 3.

**TASK-016 repairs a gap that both upstream specs had.** The watermark advance — `set_etl_cutoff(spark, ETL_CUTOFF_TABLE, ETL_CUTOFF_TABLE_NAME, current_cutoff)` — appears in step 6, alongside `close_lineage_record`. `design.md` computed `current_cutoff` and never committed it; `requirements.md` mandated the commit only inside FR-002's acceptance criterion. The task list is the first development-plan artifact to place the write in the sequence where a generator will read it. That is the chain self-correcting, and it is worth noticing because it means the earlier gap was less dangerous than it looked.

The ordering within step 6 also matters and is correct: the cutoff advances **after** the QA chain and **after** the lineage record closes successfully. Combined with the `except` branch — which closes lineage with `succeeded=False` and re-raises without touching the cutoff — this makes the pipeline self-healing. A failed run leaves the watermark where it was, so the next night re-extracts the same window plus anything new.

**TASK-017 is the only destructive task, and its DDL is defensive.** The sentinel insert uses `SELECT … WHERE NOT EXISTS (SELECT 1 … WHERE supplier_key = 0)` rather than a bare `INSERT`, so re-running it cannot create a duplicate key-0 row. Given that the notebook also **resets** `bronze.etl_cutoff` to `initial_load_date` — rewinding the watermark and forcing a full re-extract — the idempotent sentinel is the right instinct, and the PD-002 sign-off gate is the right control.

The sentinel row's values are worth reading: `valid_from '1900-01-01'`, `valid_to '9999-12-31'`, `is_current_row TRUE`, `lineage_key 0`. The open-ended validity range is what guarantees the temporal range join in TASK-011 can always match the sentinel if it needs to, and `lineage_key = 0` is a self-reference that avoids an FK to a lineage run that never happened.

### Config tasks (TASK-018, TASK-019)

**TASK-019's retry asymmetry is the sharpest operational decision in the plan.** `max_retries: 2` on `nb_extract_watermark` and `nb_extract_purchase`; `max_retries: 0` on `migrate_staged_purchase_data`, described as the "QA-gated task."

The reasoning holds up. The extract tasks fail for transient reasons — cluster startup, JDBC timeouts — and retrying is free because the watermark has not advanced. The main task fails for one non-transient reason: the QA-P001 row count assertion raised a `RuntimeError`. Retrying that re-runs the MERGE against unchanged staging and reaches the same mismatch, so a retry converts one failure into three and delays the alert. Worse, a retry after a partially applied MERGE risks changing the count on the second attempt and masking the original defect. Zero retries is correct.

**The schedule and the SLA are consistent.** `0 2 * * *` (02:00 UTC) against NFR-001's 06:00 UTC deadline gives a four-hour budget, matching the ODPS `SLA / latency: 4 hours`. Two retries on the extract tasks fit inside that window; a third would not necessarily.

**TASK-018's `business_rules` block is empty.** The required YAML content has `purchase.etl` fully populated (`initial_load_date`, `batch_lookback_days`, `fact_optimize_row_threshold`) and `purchase.business_rules` as two comment lines: "Add business factors here as they are identified during implementation." FR-009's acceptance criterion requires `environment.yaml` to contain "all externalised values under `purchase.etl` **and** `purchase.business_rules`" — which an empty block either trivially satisfies or cannot satisfy, depending on how the check is written. The honest reading is that Purchase has no identified business factors yet, and the placeholder is a hook rather than a value. It should be stated that way, so a validator does not fail on an empty map.

Also note `batch_lookback_days: 1` is declared here but referenced by no task, calculation, or requirement in the chain.

### Test tasks (TASK-020 – TASK-022)

Three suites: the SK resolver (8 cases — four scenarios × two dimensions), the UDFs (four properties per UDF), and the main notebook (6 integration cases).

**TASK-020 and TASK-022 both require local execution.** "Use `pyspark.sql.SparkSession` fixture with a local test schema; do not connect to a live cluster"; "local SparkSession with Delta tables written to a temp directory." This makes the suites runnable in CI without Databricks, which is what makes them worth generating at all — a test that needs a cluster and a service principal does not run on every commit.

**TASK-022's case list is the best part of the plan.** Six cases, and four of them are failure injections: a forced count mismatch expecting the exact `RuntimeError` message, an RI violation expecting a `dq_rejections` row with the right `rule_id` and `lineage_key`, a negative quantity expecting a WARNING and a *succeeding* pipeline, and an injected exception expecting `close_lineage_record(succeeded=False)`. Those last two are the only way to verify non-blocking behaviour and the `except`-path lineage close, both of which are invisible on a clean run.

### BI and docs tasks (TASK-023 – TASK-026)

**TASK-023 and TASK-024 produce specifications, not connections.** Both output a Markdown reconnection spec — endpoint, table mapping, column mapping — rather than a reconfigured report, because the reports live in Power BI and cannot be generated. The distinction between the two is the point: TASK-024's report is self-contained within Purchase, while TASK-023's reads `silver_fact.fact_sale` from the Sales_Orders product and therefore carries a **coordinated cutover requirement**. That is the cross-product risk from the product scope, arriving in the task list as an explicit deliverable rather than a footnote.

**TASK-025 creates a second `design.md`.** Its output is `docs/design.md` inside the codebase — an ETL design document covering seven topics, distinct from `development_plan/design.md` which specified this build. Anyone navigating the workspace should know both exist: the development-plan one is the input to code generation, the codebase one is documentation written after the fact for operators.

---

## Divergences and Open Items

Six items, in descending order of consequence.

### 1. Two shared modules are imported but no task creates them

TASK-014's skeleton opens with:

```python
from src.common.lineage_utils import open_lineage_record
from src.common.etl_control import get_last_etl_cutoff_time, set_etl_cutoff
```

TASK-016 uses `close_lineage_record` and `set_etl_cutoff` from the same modules. But the five ETL module tasks produce `constants.py`, `scd2_merge.py`, `sk_resolver.py`, `fact_merge.py`, and `udfs.py`. **There is no task for `lineage_utils.py` and no task for `etl_control.py`** — and NFR-011 does not name them either, listing only four required modules. TASK-016 additionally imports unnamed "QA utilities" with no module and no task at all.

These are not incidental helpers. `open_lineage_record` creates the run record that FR-003's entire lineage chain hangs from; `close_lineage_record` is what NFR-009 requires in both the success and `except` paths; `set_etl_cutoff` is FR-002's watermark advance. Four load-bearing functions have no owner in a 26-task plan.

The consequence is visible in the generated code. SmartBuilder improvised: it created `src/common/lineage_helpers.py` — a name no spec uses — containing `open_lineage_record` and `close_lineage_record` but not the cutoff functions. Then, because the import paths in the task skeletons did not match anything real, the notebooks **inlined the logic instead**. `migrate_staged_purchase_data.py` closes the lineage record and advances the watermark with two direct `spark.sql` statements, and `lineage_helpers.py` is never imported by any notebook — it is dead code.

The outcome happens to be functionally correct, and the inlined `MERGE INTO etl_cutoff` is a sound implementation. But NFR-009's requirement that `close_lineage_record` be *called* in both paths is now satisfied only in spirit, a test written against the named function would fail, and the shared-module boundary that NFR-011 exists to protect was decided by the generator rather than the plan. **Two tasks should be added, or the four functions folded into an existing module with the import paths corrected.**

### 2. The single-column MERGE key reaches its third artifact

TASK-012 specifies `merge_fact_purchase` with **MERGE predicate:** `ON target.wwi_purchase_order_id = source.wwi_purchase_order_id`, and states "the MERGE is idempotent for the same `wwi_purchase_order_id`."

The fact grain is one row per purchase order **line** — a single order contributes one row per stock item — so this column is not unique at the fact grain. `to-be.md` specifies a four-column composite (`wwi_purchase_order_id`, `date_key`, `supplier_key`, `stock_item_key`). FR-007 narrowed it to one column, `design.md` §3.3 carried that forward, and TASK-012 is now the third artifact to repeat it.

Nothing in the DDL guards the grain either: `fact_purchase`'s only key is the IDENTITY `purchase_key`, and there is no uniqueness constraint on the business composite — nor could there be one that Delta enforces.

Delta raises an error when a MERGE matches multiple source rows to one target row, so this fails at first run rather than corrupting silently. TASK-012's own first acceptance case ("running merge twice with the same staging produces the same fact row count") would fail immediately. That is the right failure mode, but discovering it as a red test after generation is more expensive than fixing three lines of spec now. **All three — FR-007, design §3.3, TASK-012 — should be reconciled to the to-be's four-column key.**

### 3. TASK-015 requires a JDBC extract that TASK-018's config does not provide

TASK-015 step 5 specifies a "JDBC query" against the upstream source. TASK-018's required `environment.yaml` content has `purchase.etl` and `purchase.business_rules` — and no JDBC section: no host, driver, credential reference, or secret scope.

The two tasks are internally consistent with their own instructions and inconsistent with each other, and both were generated exactly as specified. The result, recorded in `validation-report.md`, is a notebook referencing config keys that the config file does not contain — a `KeyError` before the pipeline reaches the source at all.

The root cause is upstream: no requirement covers the inbound extract, because all five ODPS `x-inputPorts` are already Delta tables. PD-001 (source JDBC connectivity) is registered as a pending decision in `codebase/build-plan.md` — downstream of the plan that needed it. **TASK-018 should include a JDBC block with `{{PLACEHOLDER}}` values so the config loads before PD-001 resolves**, which is exactly what the validation report recommends.

### 4. TASK-016's skeleton uses a value it never retrieves

Step 2 of TASK-016 retrieves one task value: `lineage_key`. Step 6 then calls `set_etl_cutoff(spark, ETL_CUTOFF_TABLE, ETL_CUTOFF_TABLE_NAME, current_cutoff)` — and `current_cutoff` is never bound. TASK-015 retrieves both `last_cutoff` and `current_cutoff` in its step 3; TASK-016 retrieves neither.

Followed literally, this is a `NameError` in the final step of the nightly pipeline, after the MERGE has already committed. The generator noticed and added the missing line (`current_cutoff = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="current_cutoff")`), so the shipped code is correct. But a plan that depends on the generator catching an unbound variable is relying on luck. **Add the `current_cutoff` retrieval to TASK-016 step 2.**

### 5. Three broken or inconsistent traceability references

The `Requirements` column is the audit spine of this document, and three entries do not resolve:

- **TASK-008's RULES header cites `SE-001, SE-002`.** This project has nine rule dimensions — PL, NM, TY, OB, SX, PE, LN at project level, plus QA and CX added by Purchase. **There is no SE dimension.** `SE-001` and `SE-002` appear nowhere except this header and the build plan that inherited it. The same header also lists `NFR-008`, which is a requirement, not a transformation rule. NFR-010's grep-based check would pass — the RULES field is non-empty — while two of its five IDs are unresolvable. This is the failure mode of a non-empty-string check.
- **TASK-017 cites `NFR-002`.** NFR-002 is SQL Warehouse uptime ≥ 99.5%, which has nothing to do with an environment reseed notebook. Given TASK-017's content, the intended reference is almost certainly NFR-011 (codebase layout) or nothing beyond FR-011.
- **The summary table and the details disagree on two tasks.** TASK-011's summary row lists `FR-004, FR-005, CALC-002, CALC-003`; its detail section lists `FR-004, FR-005, DQR-009`. TASK-015's summary row includes `CALC-001, CALC-005`; its detail drops them. The summary is mixing design calculation IDs into a Requirements column, and the two views of the same trace are not reconcilable. One convention should win — citing both requirement and calculation IDs is defensible, but only if both places do it.

### 6. Test coverage is narrower than the traces claim

TASK-022 lists `NFR-003, NFR-004, NFR-005, NFR-006, DQR-001 through DQR-007` in its Requirements, but its six enumerated cases cover QA-P001 (pass and fail), QA-P003 RI, QA-P004 negative quantity, QA-P004 null package, and the exception-path lineage close. Not covered by any case: **DQR-006** (out-of-window `date_key`), **QA-P002 / NFR-005** (orphaned SK detection), and **QA-P005** (the post-run rejection summary). The trace overstates what the suite verifies.

Separately, `scd2_merge.py` (TASK-010) has an acceptance criterion phrased as a unit test but no test task writes one, and `fact_merge.py` (TASK-012) has three acceptance tests with no dedicated suite — they are only reachable through TASK-022's integration tests. Neither is fatal, but a validator matching test tasks to source modules will report both.

---

## How This Spec Is Used Downstream

| Consumer | What it takes from the task list |
|---|---|
| **SmartBuilder `generate-db`** | TASK-001 – TASK-008: emits each Output File, using the inline DDL and header block verbatim |
| **SmartBuilder `generate-etl`** | TASK-009 – TASK-022: the numbered skeletons become module and notebook structure; the acceptance cases become tests |
| **`build-plan.md`** | Reorders the 26 tasks into execution waves, adds the PD-001/002/003 register, and records per-task status |
| **`validation-report.md`** | Walks the 26 rows one by one — each Output File is checked for existence, header conformance, and acceptance |
| **`config/workflows/nightly_etl_purchase.json`** | TASK-019's schedule, retry policy, runtime version, and three-task dependency chain |
| **`runbook.md`** | TASK-019's retry policy becomes the on-call escalation rule; TASK-017 becomes the seeding procedure behind PD-002 |
| **`docs/data-dictionary.md`** | TASK-005's and TASK-003's column lists are the source of record |
| **Build coordination** | The `Depends On` column is the parallelisation plan and the critical path |

---

## File Reference

| File | Location |
|---|---|
| `tasks.md` | `products/Purchase/current/specifications/development_plan/tasks.md` |
| `design.md` | same directory — the design these tasks implement |
| `requirements.md` | same directory — the 32 requirements each task traces to |
| `product-definition.yaml` | same directory — the ODPS definition at the head of the chain |
| `build-plan.md` | `products/Purchase/current/codebase/build-plan.md` — execution waves and the PD register |
| `validation-report.md` | `products/Purchase/current/codebase/validation-report.md` — per-task verification of generated output |

763 lines, the longest artifact in the development plan. Its length comes from carrying six complete SQL files, a constants module, a sentinel INSERT, a YAML file, and four numbered notebook skeletons inline. That front-loading is deliberate: every schema and every import path is reviewed once here, before nine notebooks and three test suites are generated against them — which is exactly why the two missing module tasks in divergence 1 were expensive, and why they were the one thing this document did not front-load.
