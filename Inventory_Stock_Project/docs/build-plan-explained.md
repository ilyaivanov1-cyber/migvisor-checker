# Build Plan — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `specifications/development_plan/design.md` + `specifications/development_plan/tasks.md`
**Location:** `products/Purchase/current/codebase/build-plan.md` — inside the codebase, not the specifications
**Produced by:** `/smartbuilder_development-plan plan Purchase` (the `plan` step)
**Contents:** 26 tasks → 3 phases → 10 explicit batches, plus 5 prerequisite checks and 4 pending decisions

---

## What This Spec Is

The build plan is the **execution schedule**. It takes the 26 tasks and answers a question none of the upstream artifacts answer: in what concrete batches do we actually run the generators, and what has to be true before we start?

Its location is the most informative thing about it. Every artifact before it lives under `specifications/`; this one lives under `codebase/`. It is the last document written for a human reader and the first thing written into the directory that will hold the code:

| Artifact | Lives in | Written by | Audience |
|---|---|---|---|
| `product-definition.yaml` | `specifications/development_plan/` | `define` | Consumer + generator |
| `requirements.md` | `specifications/development_plan/` | `requirements` | Reviewer |
| `design.md` | `specifications/development_plan/` | `design` | Engineer |
| `tasks.md` | `specifications/development_plan/` | `tasks` | Engineer + generator |
| **`build-plan.md`** | **`codebase/`** | **`plan`** | **The build operator** |
| `validation-report.md` | `codebase/` | `validation` | Reviewer, after the fact |

That crossing of the boundary is why the build plan is the only artifact that talks about Databricks CLI commands, catalog accessibility, and credentials. It is the first document that assumes a real environment exists.

It has nine sections:

| Section | What it supplies |
|---|---|
| Overview | Task counts by type, phase count, which skill runs which phase |
| Codebase Layout | The target file tree, annotated task-by-task |
| Phase 1 — DDL | 8 tasks, 3 batches, acceptance gate |
| Phase 2 — ETL + Config | 11 tasks, 7 batches, a design-constraint table, acceptance gate |
| Phase 3 — Tests + BI + Docs | 7 tasks, mostly parallel, acceptance gate |
| Full Task Dependency Graph | ASCII rendering of the whole graph across phases |
| SDD Spec Cross-Reference | Design section → tasks → rules |
| Prerequisite Checks | 5 environment conditions with verification commands |
| Pending Decisions | 4 unresolved items with the tasks they block |

---

## Why This Spec Exists

### Because `tasks.md` gives a partial order, and a build needs a schedule

The task list states dependencies per task — TASK-016 depends on TASK-011, TASK-012, TASK-014, TASK-015. That is a directed graph, and a graph is not a schedule. Someone still has to decide how to walk it: what runs together, what waits, where the safe stopping points are.

The build plan does that walk once and writes it down as ten named batches. The value is not that the batching is clever — it is a topological sort, and any correct sort would do — but that it is **fixed**. A recorded batch order means two operators building the same product produce the same artifacts in the same sequence, and a failure at "Phase 2, Batch 5" is a reproducible coordinate rather than a description of where someone happened to be.

### Because the build has preconditions the task list cannot express

`tasks.md` is written entirely in terms of other tasks. It has no vocabulary for "the Unity Catalog has to exist," "the supplier dimension has to be loaded by another team," or "we do not yet have the source credentials." Those are facts about the world, not about the work.

The Prerequisite Checks section is where they finally appear, and it is the only place in the entire specification chain where they do. Three of the five checks describe conditions no task creates and no requirement mentions.

### Because the generator needs somewhere to record decisions the specifications left open

This is the build plan's least advertised and most consequential function. When the specifications are ambiguous or self-contradictory, something has to choose before code can be emitted. The build plan is where that choice gets recorded — in the Phase 2 design-constraint table, and in the Pending Decisions table for the choices that were deferred instead.

That makes the build plan the most honest document in the chain about what is actually unresolved. It also makes it the place where a specification defect can be quietly converted into an implementation decision, which is exactly what happened to the lineage-close mechanism.

---

## Section 1 — Overview

### What it contains

A six-row field table (product, project, target catalog, 26 tasks, 3 phases, which skills run) and a task-breakdown table mapping the six task types to phases.

### Key facts captured

**The type-to-phase mapping is one-way.** Each of the six types belongs to exactly one phase, so "phase" is not an independent concept — it is a grouping of types. DDL → Phase 1, ETL and Config → Phase 2, Test and BI and Docs → Phase 3. The phases exist because the *skills* differ: `/smartbuilder_generate-db` handles Phase 1, `/smartbuilder_generate-etl` handles Phases 2 and 3.

**"DDL 8" counts tasks, not DDL files.** Seven tasks emit files into `src/db/ddl/`; TASK-008 emits a grants file into `src/db/grants/`. The Phase 1 acceptance gate is precise about this — "7 DDL files exist under `src/db/ddl/`; grants file exists at `src/db/grants/purchase_grants.sql`" — so the apparent discrepancy between 8 and 7 is a type/file distinction, not an error.

**The type vocabulary drifts from the manifest.** The build plan says DDL / ETL / Config / Test / BI / Docs. `_manifest.yaml` records the same tasks as `db` / `etl` / `config` / `test` / `docs`, collapsing BI and Docs into a single `docs: 4`. Both are internally consistent; a tool joining them on type would not be.

### Why this section matters

It is the reconciliation point for the count that everything else is checked against. Twenty-six appears in the manifest's task list, in the tasks document's summary table, in the validation report, and here. Any drift between them is a signal that a task was added or dropped without the chain being regenerated.

---

## Section 2 — Codebase Layout

### What it contains

The full target directory tree with a trailing comment on every file naming the task that produces it.

### Key facts captured

**The annotation direction is the useful one.** `tasks.md` reads task → file. This tree reads file → task, which is the direction you need when you are looking at a file in the repository and want to know what specified it. Twenty-two of the twenty-six tasks appear as a leaf here; the tree is effectively a reverse index.

**The tree encodes CX-P004's layout rule as a picture.** `src/common/`, `src/db/ddl/`, `src/db/grants/`, `src/etl/`, `src/init/`, `config/`, `config/workflows/`, `tests/common/`, `tests/etl/`, `docs/`. NFR-011 states this layout in prose; the tree is the version a generator can be checked against, and the validation step does exactly that.

**Three things are missing from the tree.** `docs/bi/` is relegated to a footnote below the diagram rather than drawn in it. `build-plan.md` and `validation-report.md` — both of which live in `codebase/` — do not appear at all, presumably because no task produces them. And `docs/runbook.md`, which does exist on disk, appears nowhere in the tree, in the task list, or in the manifest's generated-artifact list.

### Why this section matters

This tree is the acceptance surface for the entire build. Every phase gate is phrased as "these files exist at these paths," and this is where the paths are declared. That is also why the two path errors it contains matter more than they would in a prose document — see divergence 4.

---

## Section 3 — Phase 1 (Database Layer)

### What it contains

A parallelism note, three named batches, an eight-row task table with dependencies, and an acceptance gate.

```
Batch 1 (parallel): TASK-001, TASK-002, TASK-006, TASK-007
Batch 2 (parallel): TASK-003, TASK-004, TASK-005   ← after TASK-001 + TASK-002
Batch 3 (sequential): TASK-008                      ← after Batch 2
```

### Key facts captured

**Batch 1 is the four tasks with no dependencies**, which matches the roots of the task graph exactly: the two control tables (`lineage_run`, `etl_cutoff`) and the two SCD-2 current views. The views have no dependencies because their base tables are owned by another product — an ownership gap the task list leaves implicit and the prerequisite checks later make explicit.

**Batch 2 over-serializes, harmlessly.** TASK-004 and TASK-005 depend only on TASK-001 per the task table, but the batch is gated on "after TASK-001 + TASK-002." Only TASK-003 needs TASK-002. Since Batch 1 runs all four in parallel anyway, the cost is zero — but it means the batch annotation is a simplification of the table above it rather than a derivation from it.

**The acceptance gate is mechanically checkable, and that is unusual.** `grep -c '-- RULES    : $' src/db/ddl/*.sql` returns 0 — a shell command that verifies NFR-010's requirement that every DDL header's RULES field be populated. Most gates in this chain are prose; this one can be run.

It is also the weakest possible version of that check. It confirms the field is non-empty, not that its contents are valid. TASK-008's header cites `SE-001, SE-002` — identifiers belonging to a rule dimension that does not exist in this project — and this gate passes it without complaint.

### Why this section matters

Phase 1 is the only phase whose output is pure DDL, which means it is the only phase where the generated artifacts can be reviewed against the design's data model column by column with no runtime behaviour involved. The gate reflects that: it checks existence and headers, because correctness here is structural.

---

## Section 4 — Phase 2 (ETL Pipeline + Configuration)

### What it contains

Seven batches, an eleven-row task table, an eight-row **design-constraint table**, and an acceptance gate.

```
Batch 1 (parallel):   TASK-009, TASK-010, TASK-018
Batch 2 (parallel):   TASK-011, TASK-012, TASK-013   ← after TASK-009
Batch 3 (sequential): TASK-014                       ← after TASK-009
Batch 4 (sequential): TASK-015                       ← after TASK-014
Batch 5 (sequential): TASK-016                       ← after TASK-011, TASK-012, TASK-014, TASK-015
Batch 6 (sequential): TASK-017                       ← after TASK-016 (optional; init notebook)
Batch 7 (sequential): TASK-019                       ← after TASK-014, TASK-015, TASK-016
```

### Key facts captured

**The batch count tells you where the risk is.** Phase 1 needed three batches for eight tasks; Phase 2 needs seven for eleven. Batches 3 through 7 are all single-task, because the three notebooks form a strict chain — watermark, then extract, then promote — and the workflow config can only be written once all three exist. Phase 2 is where the build stops being parallelisable.

**Batch 6 is marked "optional."** TASK-017 is the reseed notebook, and PD-002 requires scope-owner sign-off before it is *executed*. The build plan correctly separates generating the artifact from running it, but "optional" is doing double duty: the file is not optional, its execution is.

**The design-constraint table is the most important eight rows in the file.** It is a list of specification decisions the generator must honour, each with its rule and the tasks that enforce it:

| Constraint | Rule cited | Enforced in |
|---|---|---|
| Standard notebook skeleton (6 sections in order) | NFR-009, CX-P005 | TASK-014, 015, 016, 017 |
| **Lineage-close via direct `spark.sql UPDATE` in except block** | **NFR-009** | TASK-014, TASK-016 |
| No hard-coded date literals | FR-009, CX-P001 | TASK-014, 015, 016 |
| SK resolution: temporal range join + DESC tie-breaker + COALESCE to 0 | FR-004/005, CALC-002/003 | TASK-011 |
| **MERGE INTO keyed on `wwi_purchase_order_id`** | **FR-007** | TASK-012, TASK-016 |
| OPTIMIZE conditional on `rows_merged > 10,000` | FR-008, PE-P002 | TASK-016 |
| Row count reconciliation raises RuntimeError | NFR-003, DQR-001 | TASK-016 |
| DQ rejections written to `bronze.dq_rejections` with `lineage_key` | NFR-004, NFR-007 | TASK-016 |

Six of the eight rows are faithful restatements of the specifications. The two in bold are not, and they are the two highest-consequence findings in this document — the second row silently reverses NFR-009, and the fifth carries the MERGE-key defect into its fourth artifact.

**The acceptance gate names one config key by path.** "`config/environment.yaml` contains `purchase.etl.fact_optimize_row_threshold`." A single key is checked out of the dozen the config file ends up holding — the one FR-008 depends on. The JDBC keys that TASK-015 needs are not checked, which is consistent with them being blocked on PD-001, but it means the gate would pass a config file that cannot run the extract.

### Why this section matters

This is where the specifications stop being descriptive and become instructions to a generator. Every row of the constraint table becomes a property of emitted code. That is a good design — a single table the generator can be diffed against — and it is precisely why an incorrect row in it propagates directly into the codebase rather than being caught.

---

## Section 5 — Phase 3 (Tests, BI Specs, Documentation)

### What it contains

A parallelism note, a seven-row task table, and an acceptance gate. No batch diagram — six of the seven tasks run in parallel and TASK-022 waits for TASK-016.

### Key facts captured

**Phase 3 is where the plan stops constraining.** There is no constraint table, no batch sequence, and the dependencies are all backward-looking (TASK-020 after TASK-011, TASK-023 after TASK-005). Once Phase 2 is complete, everything remaining is independently generable.

**The acceptance gate is the only place test *content* is specified at the plan level.** It requires that TASK-020 cover all three SK resolution scenarios — match yields a non-zero key, no match yields 0, multiple versions yield the most recent — and that TASK-022 cover the `RuntimeError` injection path.

Those three SK scenarios are exactly the three branches of `CALC-002`, so the gate is a genuine coverage assertion rather than a file-existence check. It is the strongest gate in the document.

**The same gate contradicts the Phase 2 constraint table.** It requires verifying that `close_lineage_record(succeeded=False)` is called. Forty lines earlier, Phase 2 instructed the generator to implement lineage-close as a direct `spark.sql UPDATE` instead of that function. Both statements are in the same file, about the same behaviour, and only one of them can be satisfied.

**TASK-023 and TASK-024 depend only on TASK-005.** They need the fact table's column names to write the report column mappings, which is correct. But TASK-024's own acceptance criterion in `tasks.md` requires documenting the coordinated cutover with the Sales_Orders product — a dependency on another product entirely, which no task-level dependency can express and which the prerequisite checks do not cover either.

### Why this section matters

Phase 3 is the deliverable-completion phase, and its gate is the last automated check before validation. Everything it does not assert becomes something the validation step has to catch by reading.

---

## Section 6 — Full Task Dependency Graph

### What it contains

An ASCII diagram of all 26 tasks arranged in three boxed phases with arrows between them.

### Key facts captured

**It is a redundant rendering, and that is fine.** Every edge in the diagram already exists in the three phase tables. The diagram adds no information; it adds *shape* — you can see at a glance that TASK-009 fans out to four tasks, that TASK-016 is the convergence point, and that three tasks (TASK-006, TASK-007, TASK-010) hang off the graph with no connections in either direction.

**TASK-010 is visibly isolated.** The diagram labels it "(independent)" with no incoming and no outgoing edges. That is the clearest available statement of a real problem: `scd2_merge.py` is generated, has no importer among the notebooks, and has no test task. The diagram makes dead code visually obvious in a way the tables do not.

**Two of the arrows are drawn with a different glyph.** `TASK-016 → TASK-019` uses a plain arrow where every other edge uses `──►`. Cosmetic, but it hints the diagram was hand-assembled rather than rendered from the dependency data — which means it can drift from the tables without anything detecting it.

### Why this section matters

For a 26-task build this diagram is a convenience. For a larger product it would be the only practical way to see that a task has no dependents, and "has no dependents" is the signature of an artifact nobody uses.

---

## Section 7 — SDD Spec Cross-Reference

### What it contains

Five rows mapping each design section to its tasks and the rules that govern them.

| Design section | Tasks | Rule count cited |
|---|---|---|
| §1 Data Model | TASK-001–008 | 9 |
| §2 Ingestion | TASK-014, 015, 018 | 7 |
| §3 Transformation | TASK-010, 011, 012, 016 | 12 |
| §4 Serving | TASK-008, 019, 023, 024 | 4 |
| §5 Observability | TASK-016, 004, 022 | ~20 (ranges) |

### Key facts captured

**This table closes the traceability loop in the coarse direction.** `tasks.md` traces each task to requirements and rules; this traces each *design section* to tasks. Together they let a reviewer start from any of the three and reach the other two.

**TASK-016 appears in three of the five rows.** Transformation, Observability, and — through the workflow config — Serving. That concentration is real: `migrate_staged_purchase_data.py` is the only artifact that performs the MERGE, runs all five QA assertions, closes the lineage record, and advances the watermark. It is a 415-line file doing the work of four design sections.

**§4 Serving cites `SE-001`.** There is no SE dimension in this project. The nine dimensions are PL, NM, TY, OB, SX, PE, LN at project level plus QA and CX at product level. `SE-001` and `SE-002` appear only in `tasks.md` (TASK-008's header) and here — the same phantom identifier propagating from the task list into the build plan without either document being able to detect it.

### Why this section matters

It is the last chance to notice that a design section has no tasks behind it. All five sections have tasks here, so the coverage claim holds — but the check is existence-only, and a design section could be represented by a single tangential task and still appear covered.

---

## Section 8 — Prerequisite Checks

### What it contains

Five environment conditions, each paired with a verification command.

| Check | Command |
|---|---|
| Databricks CLI configured | `databricks configure --check` |
| Unity Catalog `inventory_stock` accessible | `databricks catalogs get inventory_stock` |
| Target schemas exist | `SHOW SCHEMAS IN inventory_stock` returns `bronze`, `silver_dim`, `silver_fact` |
| SCD-2 dimension tables pre-loaded | `SELECT COUNT(*) FROM inventory_stock.silver_dim.supplier` returns > 0 |
| Source JDBC connectivity (PD-001 pending) | Confirm connection profile before TASK-015 |

### Key facts captured

**Three of these five conditions are met by nothing in the build.** No task creates the catalog. No task creates the schemas — there is no `CREATE SCHEMA` statement anywhere in the generated codebase. No task loads the supplier or stock item dimensions. They are all genuine external preconditions, and this table is the only artifact in the chain that states them.

**The schema check is the sharpest of the three.** Every DDL file the build emits writes into `inventory_stock.bronze`, `inventory_stock.silver_dim`, or `inventory_stock.silver_fact`. If those schemas do not exist, all eight Phase 1 tasks fail at execution. The design's data model assumes them, the tasks assume them, and the assumption becomes visible for the first and only time here — as a manual check.

**The dimension pre-load check names only `supplier`.** `stock_item` is equally required by the SK resolution logic and equally externally owned; `silver_dim.date` is required by the fact table's `date_key` FK. Only one of the three is checked. The others are covered by the same class of dependency and would produce the same class of failure.

**The JDBC row is not a check.** "Confirm connection profile before TASK-015 extract is run" is a note that something is unresolved. It is the honest entry in the table, and it points at PD-001.

### Why this section matters

This is the build plan's most distinctive contribution. Every other artifact in the chain reasons about the product; this section reasons about the platform. The three unowned preconditions it names are exactly the failures that would otherwise be discovered by running Phase 1 and watching it fail.

---

## Section 9 — Pending Decisions

### What it contains

Four unresolved items, each with the tasks it blocks.

| ID | Blocks | Nature |
|---|---|---|
| PD-001 | TASK-015, TASK-019 | Source JDBC connectivity — connection profile and credentials for SQL Server 2014 |
| PD-002 | TASK-017 | Reseed notebook scope — requires scope-owner sign-off before execution |
| PD-003 | TASK-008 | Unity Catalog access role matrix — GRANT statements must be reviewed after it resolves |
| QA-DQ-01 | TASK-016, TASK-022 | Business DQ thresholds — affects test expectations, does not block generation |

### Key facts captured

**These are the four places the specification chain admits it is incomplete**, and each has a different shape. PD-001 is a missing fact. PD-002 is a missing approval. PD-003 is a missing policy. QA-DQ-01 is a missing agreement with the business, explicitly marked as not blocking code generation.

**The blocking distinction is well drawn.** PD-003 does not prevent TASK-008 from generating GRANT statements; it means they must be reviewed afterwards. QA-DQ-01 does not prevent TASK-016 from implementing QA-P004; it means the threshold values in `config/environment.yaml` are provisional. Only PD-001 blocks an artifact from being *correct* rather than merely unreviewed — which is why it produced the one real defect the validation step caught.

**The section header says "from SDD," and half of it is not.** PD-002 and PD-003 do appear in the specifications — PD-002 in FR-011 and TASK-017, PD-003 in NFR-008. PD-001 and QA-DQ-01 appear nowhere in `specifications/`. They originate here.

That is not a flaw in the decisions; both are real and both are correctly identified. It is a mislabelled provenance, and it matters because it hides the more interesting fact: **the build plan discovered two unresolved items that four upstream artifacts missed.** PD-001 in particular is the moment the missing source-system input port finally became a named blocker.

### Why this section matters

This table is the go-live checklist. The runbook picks all four up, and QA-DQ-01 appears there as step 9 of the deployment sequence — the only trace either of the two build-plan-originated decisions has outside this file.

---

## Divergences and Open Items

### 1. The lineage-close mechanism was reversed here, credited to the requirement it contradicts, and contradicted again in the same file

NFR-009 is explicit:

> The `close_lineage_record` call must appear in both the success path and the `except` block.

Its acceptance criterion is a test verifying that `close_lineage_record(spark, lineage_key, rows_merged=0, succeeded=False)` is called. `tasks.md` TASK-016 step 6 calls the function by name.

The build plan's Phase 2 constraint table says:

> Lineage-close via direct `spark.sql UPDATE` in except block — **NFR-009** — TASK-014, TASK-016

This is the opposite instruction, attributed to the requirement that forbids it. Then the Phase 3 acceptance gate requires "`close_lineage_record(succeeded=False)` call verification" — so the file instructs the generator to inline the UPDATE and then gates on the function call being present.

The generated code followed Phase 2. `migrate_staged_purchase_data.py` closes the lineage record with a `spark.sql` UPDATE in the `except` block and another at the end of the success path. `src/common/lineage_helpers.py` was created containing `open_lineage_record` and `close_lineage_record`, and no notebook imports it.

The outcome is functionally correct — the lineage record is closed on both paths, which is what NFR-009 is *for*. But the requirement's letter is unsatisfied, its acceptance test cannot pass as written, and a module of dead code exists because the plan and the gate disagreed. **This is the root cause of the missing-shared-module finding recorded in `tasks-explained.md`, and it is resolvable by picking one mechanism and correcting NFR-009, the constraint row, and the Phase 3 gate to match.**

### 2. No task creates the target schemas

The Prerequisite Checks section requires `bronze`, `silver_dim`, and `silver_fact` to exist. Nothing in the build creates them — there is no `CREATE SCHEMA` in any generated file — and no requirement, design section, or task mentions schema creation.

For a training or greenfield environment this is a hard stop: all eight Phase 1 tasks fail on the first statement. **Either a TASK-000 should create the three schemas, or the prerequisite should be promoted from a table row to an explicit, signed-off environment provisioning step.** The build plan is the right place for this to surface; a manual check buried in the eighth section is the wrong weight for a precondition that blocks every artifact.

### 3. Two of the four "Pending Decisions (from SDD)" are not from the SDD

PD-002 and PD-003 are traceable to FR-011, TASK-017, and NFR-008. PD-001 and QA-DQ-01 appear nowhere under `specifications/` — they were identified during planning.

Low direct consequence, but it inverts the reading. The header implies the build plan is relaying decisions the specifications raised; in fact it raised two of them itself, including the most consequential one. **The table should distinguish inherited items from plan-discovered items, and PD-001 should be back-propagated into `requirements.md` as the missing source-extract requirement.**

### 4. The BI output filenames do not match what was generated

The Phase 3 table specifies:

- `docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic.md`
- `docs/bi/wwidw_ordered_by_supplier.md`

The files on disk, and in the manifest's generated list, are:

- `docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md`
- `docs/bi/wwidw_ordered_by_supplier_reconnection.md`

A `_reconnection` suffix was added during generation. The Phase 3 acceptance gate is phrased as "all 7 test/BI/docs files exist," which passes either way — but a gate that checked the declared paths literally would fail on both. Since the Output File column is the build plan's contract with the generator, and every phase gate is a path-existence assertion, **the plan should be corrected to the generated names or the generator to the planned ones.**

### 5. `docs/runbook.md` exists but is in no plan, no task, and no manifest

The file is on disk at `codebase/docs/runbook.md`. It is not in the Codebase Layout tree, not among the 26 tasks, and not in `_manifest.yaml`'s `generated:` list. It is a substantive document — it carries the PD-001/002/003 and QA-DQ-01 resolution steps and the deployment sequence.

Its motivation is traceable: `product-transformation-rules/LN-lineage.yaml` requires that the two-tier lineage model and the IDENTITY reseed procedure be documented "in the runbook," and one of its acceptance criteria is "the project runbook documents the two-tier lineage model." So a rule mandated a deliverable, no task was created to produce it, and the generator produced it anyway — off-plan.

The artifact is welcome; its provenance is not auditable. **A TASK-027 should own it, or the LN rules' runbook obligation should be folded into TASK-025.** As it stands, the only artifact recording the go-live checklist is the one artifact nothing tracks.

### 6. The MERGE key defect reaches its fourth artifact

"MERGE INTO keyed on `wwi_purchase_order_id` — FR-007 — TASK-012, TASK-016" now joins FR-007, `design.md` §3.3, and TASK-012.

`to-be.md:512` specifies a four-column composite key. The product definition's own description states the grain as "one purchase order **line**." At line grain a single order ID matches many source rows, so Delta will raise "multiple source rows matched" on the first run against real data — and TASK-012's own first acceptance case would fail.

Appearing in the build plan's constraint table is the worst place for it, because that table is the generator's instruction set. **All four — FR-007, design §3.3, TASK-012, and this row — should be reconciled to the four-column key.**

### 7. `SE-001` propagates into the cross-reference

§4 Serving cites `SE-001` among its key rules. No SE dimension exists in this project. The identifier appears only in TASK-008's DDL header and here, having been copied forward from the task list.

Harmless to execution, but it demonstrates the limit of the traceability checks: NFR-010's gate verifies the RULES field is non-empty, and this cross-reference table is never validated against the rule inventory at all. **A check that rule IDs resolve to the nine actual dimensions would catch this and the TASK-008 header in one pass.**

### 8. Phase 1 Batch 2 gates on a dependency two of its tasks do not have

TASK-004 and TASK-005 depend only on TASK-001 per the task table, but Batch 2 is annotated "after TASK-001 + TASK-002." Since Batch 1 runs both in parallel, there is no scheduling cost.

Noted only because it shows the batch annotations are summaries written alongside the tables rather than derived from them — the same authorship pattern as the hand-drawn dependency graph, and the same exposure to silent drift.

---

## How This Spec Is Used Downstream

| Consumer | What it takes from the build plan |
|---|---|
| **`/smartbuilder_generate-db`** | Phase 1's batches, output paths, and the CX-P006 header gate |
| **`/smartbuilder_generate-etl`** | Phase 2 and 3 batches, and the eight-row design-constraint table as its instruction set |
| **`_manifest.yaml`** | The 26 task IDs and types become the `sb.tasks` list with per-task status; the layout tree becomes the `generated:` list |
| **`validation-report.md`** | The three phase acceptance gates are the checks it runs; the Output File column supplies the paths it verifies |
| **`docs/runbook.md`** | All four pending decisions become resolution steps; QA-DQ-01 becomes step 9 of the deployment sequence |
| **The build operator** | The Prerequisite Checks section, run before Phase 1 — the only pre-flight list in the chain |
| **Anyone resuming the build** | "Phase 2, Batch 5" is a resumable coordinate; the manifest's per-task status says which batches are done |

---

## File Reference

| File | Location |
|---|---|
| `build-plan.md` | `products/Purchase/current/codebase/build-plan.md` |
| `tasks.md` | `products/Purchase/current/specifications/development_plan/tasks.md` — the 26 tasks this schedules |
| `design.md` | same directory — the five sections the cross-reference maps |
| `requirements.md` | same directory — NFR-009, whose reversal is divergence 1 |
| `validation-report.md` | `products/Purchase/current/codebase/validation-report.md` — runs the three phase gates |
| `docs/runbook.md` | `products/Purchase/current/codebase/docs/runbook.md` — the unplanned artifact that inherits the pending decisions |
| `_manifest.yaml` | `products/Purchase/current/_manifest.yaml` — per-task status and the generated-artifact list |

262 lines, and the density is at the two ends. The middle — layout tree, phase tables, dependency graph — is a rearrangement of `tasks.md` into an executable order, valuable but derivative. The value that exists nowhere else is concentrated in eight rows of the Phase 2 constraint table, five rows of prerequisite checks, and four rows of pending decisions. Those seventeen rows are where the build plan stops summarising the specifications and starts making decisions about them: two of the constraints are wrong, three of the prerequisites are owned by nobody, and two of the pending decisions were discovered here rather than inherited. A document that is 90% restatement and 10% original judgement is worth reading for the 10%.
