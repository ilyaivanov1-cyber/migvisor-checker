# Codebase ETL Design — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `specifications/development_plan/design.md` + generated codebase artifacts
**Location:** `products/Purchase/current/codebase/docs/design.md`
**Produced by:** `/smartbuilder_generate-etl` (TASK-025)
**Contents:** 7 sections — architecture overview, workflow task sequence, SK resolution, MERGE INTO pattern, QA assertion chain, lineage propagation, configuration management

---

## What This Spec Is

The codebase ETL design is a **post-generation technical reference** for the people who will operate, maintain, and extend the Purchase ETL pipeline. It is written *after* the code exists and describes the system as built — not as designed in the upstream specifications.

That distinction matters because there are two `design.md` files in the Purchase product:

| File | Lives in | Written by | Purpose |
|---|---|---|---|
| `specifications/development_plan/design.md` | `specifications/` | `sdd-design-agent` | Input to code generation — describes the system to be built |
| **`codebase/docs/design.md`** | **`codebase/docs/`** | **`etl-file-generator-agent` (TASK-025)** | **Post-build reference — describes the system as built** |

The specification design drives the generator; the codebase design is what a new engineer reads to understand the running system. They should be consistent; where they diverge, the codebase design is more likely to reflect what was actually generated (since it was written after generation), but not always — see divergence 2 below.

It has seven sections:

| Section | What it supplies |
|---|---|
| Architecture Overview | Medallion lakehouse diagram, layer responsibility table |
| Workflow Task Sequence | Three-task execution chain with taskValues contract |
| SK Resolution Pattern | Temporal range join, COALESCE-to-0, date_key derivation |
| MERGE INTO Pattern | Full MERGE INTO SQL with column list |
| QA Assertion Chain | Five QA checks, blocking vs. warning behavior |
| Lineage Propagation | Insert/update lifecycle for `lineage_run`, propagation to fact rows |
| Configuration Management | `environment.yaml` structure, loading pattern in notebooks |

---

## Why This Spec Exists

### Because the specification design is written for a generator, not an operator

`specifications/development_plan/design.md` describes the system in terms of requirements, rule references, and design sections. It is organized by layer (data model, ingestion, transformation, serving, observability). An operator investigating why the nightly run failed does not want to read about FR-003 and DM-001 — they want to know what the three notebooks do and in what order.

The codebase design is organized by runtime concern: what runs first, what passes to what, what blocks and what warns.

### Because the generated code is the ground truth, not the specification

After code generation, the specification is an approximation. It describes what *should* have been built; the code is what *was* built. The codebase design, written by the generator as it emits files, captures the choices made during generation — including choices that diverge from the spec. Those choices appear in the constraint table in `build-plan.md` and as divergences in `build-plan-explained.md` and `validation-report.md`; they arrive in the codebase design as the actual patterns implemented.

### Because TASK-025 is listed as a Phase 3 deliverable required by the task list

FR-010 mandates reconnection specs. NFR-011 mandates a standard codebase layout including a docs directory. TASK-025 delivers the ETL design doc as a first-class codebase artifact alongside the BI specs and data dictionary. Its existence is required by the specification chain, not incidental.

---

## Section 1 — Architecture Overview

### What it contains

A medallion lakehouse ASCII diagram and a five-row layer responsibility table.

### Key facts captured

**The diagram uses correct, current table names.** Bronze tables shown: `purchase_staging`, `etl_cutoff`, `dq_rejections`, `lineage_run`. Silver dimensions: `silver_dim.supplier`, `silver_dim.date`. Silver fact: `silver_fact.fact_purchase`. These are all the correct generated names — consistent with the DDL files and the data dictionary.

This matters because `validation-report.md` Finding F-006 stated that `docs/design.md` used stale table names (`stg_purchase_order`, `etl_watermark_control`, `fact_purchase_order`, etc.). Either F-006 was raised against an earlier version of this file that was subsequently corrected, or the finding was resolved before this version was written. The current document's names are correct.

**The layer responsibility table cites `DM-001` and `DM-002` as the rules for the silver dimension layer.** These rule IDs do not exist in this project's transformation rule dimensions (which are PL, NM, TY, OB, SX, PE, LN at project level and QA, CX at product level). `DM-001` and `DM-002` are not referenced anywhere else in the workspace. This is a phantom rule citation — likely inherited from a template that used a different rule taxonomy. See divergence 1.

**The bronze layer groups staging and control tables together.** Both `purchase_staging` (ephemeral, OVERWRITE) and the three control tables (`etl_cutoff`, `lineage_run`, `dq_rejections`, all persistent) live in the bronze schema. The diagram correctly shows this cohabitation, and the layer responsibility table correctly distinguishes their roles: `purchase_staging` is the "staging/landing zone"; the three control tables are collectively "pipeline housekeeping." A reader who expects the bronze layer to be purely transient might be surprised to find persistent audit tables there.

---

## Section 2 — Workflow Task Sequence

### What it contains

An ASCII diagram of the three-task execution chain with a taskValues contract table.

### Key facts captured

**The execution order is absolute.** `nb_extract_watermark` → `nb_extract_purchase` → `migrate_staged_purchase_data`. The diagram shows this as a strict linear chain with no parallelism. That matches the workflow JSON's dependency configuration and the retry asymmetry (`max_retries: 2` / `max_retries: 2` / `max_retries: 0`).

**The taskValues contract table is the most useful part of this section.** Three keys are published and consumed:

| Key | Publisher | Consumer | Type |
|---|---|---|---|
| `lineage_key` | `nb_extract_watermark` | Both downstream tasks | int |
| `last_cutoff` | `nb_extract_watermark` | `nb_extract_purchase` | timestamp string |
| `current_cutoff` | `nb_extract_watermark` | Both downstream tasks | timestamp string |

This table is the only place in the codebase documentation where all three `taskValues` keys are enumerated with their types and consumers in one view. It resolves TASK-016's divergence 4 from `tasks-explained.md` (TASK-016's skeleton did not retrieve `current_cutoff` but the generator added it) by confirming that `migrate_staged_purchase_data` does consume `current_cutoff`.

**The diagram shows `lineage_key (INT)` being published by Task 1.** The data dictionary defines `lineage_key` as `BIGINT`. The taskValues contract table says `int`. BIGINT and int are different types in Python (64-bit vs. 32-bit), though in PySpark the distinction collapses for values below 2^31. For a IDENTITY column that starts at 1 and increments by 1, this is harmless in practice. But the type annotation in this document is inaccurate. See divergence 3.

---

## Section 3 — SK Resolution Pattern

### What it contains

A temporal range join SQL snippet, a COALESCE-to-0 explanation, and a `date_key` derivation snippet.

### Key facts captured

**The SQL accurately represents the three-step algorithm from TASK-011.** Temporal range predicate with asymmetric bounds (`> valid_from`, `<= valid_to`), ROW_NUMBER tie-breaker on `valid_from DESC`, and COALESCE fallback. The cast of `valid_from`/`valid_to` from DATE to TIMESTAMP is present in the query (`CAST(valid_from AS TIMESTAMP)`, `CAST(valid_to AS TIMESTAMP)`). This is TY-P001, and it is the detail that prevents off-by-one-day resolution errors when `last_modified_when` is a TIMESTAMP and the dimension validity dates are DATE. It appears in the SQL here and is where an operator debugging a "wrong supplier_key" issue would find the explanation.

**The COALESCE-to-0 section explains the unknown-member sentinel.** "Any staged row whose source key does not resolve to a dimension record receives a default SK of 0 (the 'unknown' dimension member)." It cites DM-002, which does not exist in this project's rule set — another phantom rule citation from Section 1. But the explanation is accurate: orphaned rows get SK=0, QA-P002 counts and logs them, and the MERGE proceeds without blocking.

**`date_key` derivation is described as using `format_date_key(stg.last_modified_when)`.** The data dictionary describes `date_key` as "`CAST(po.OrderDate AS DATE)` computed in `nb_extract_purchase` during OLTP JOIN" from `Purchasing.PurchaseOrders.OrderDate`. These are two different sources and two different derivation paths. The data dictionary says `OrderDate`; the codebase design says `last_modified_when`. This is a genuine discrepancy that affects what date the fact rows are filed under. See divergence 4.

---

## Section 4 — MERGE INTO Pattern

### What it contains

A complete MERGE INTO SQL statement with column list and ON predicate.

### Key facts captured

**The MERGE key is `wwi_purchase_order_id` only — the single-column defect.**

```sql
MERGE INTO inventory_stock.silver_fact.fact_purchase AS target
USING resolved_purchase_cte AS source
ON target.wwi_purchase_order_id = source.wwi_purchase_order_id
```

`to-be.md` specifies a four-column composite key. The data dictionary's derivation field states the four-column key. TASK-012, the build plan constraint table, `specifications/development_plan/design.md` §3.3, and this section all carry the single-column version. At line grain (one row per purchase order line × supplier × stock item × date), a single `wwi_purchase_order_id` matches many source rows — one per line on a multi-line order. Delta raises an error when multiple source rows match one target row, so this MERGE fails at first run against real multi-line purchase orders.

The codebase design is one of four artifacts that should be reconciled to the four-column key when the defect is fixed.

**The UPDATE clause omits `purchase_key`.** Correct — `purchase_key` is `GENERATED ALWAYS AS IDENTITY` and cannot be updated. The column list in the INSERT clause also correctly omits `purchase_key` (Delta assigns it on INSERT). A reader new to IDENTITY columns might expect to see it in both clauses; its deliberate absence is correct.

**`lineage_key` appears in both WHEN MATCHED UPDATE and WHEN NOT MATCHED INSERT.** Every MERGE operation updates `lineage_key` to the current run's key, even for rows that existed previously. This is the "refresh lineage on every touch" pattern — a row that was last merged in run 3 will show `lineage_key = 7` after run 7 re-merges it. This enables tracking of the most recent ETL run that wrote each row, but it means `lineage_key` on a fact row does not always point to the run that first created it. The data dictionary and this document both describe this correctly; the pattern's implications for historical lineage queries are not documented.

---

## Section 5 — QA Assertion Chain

### What it contains

A five-row table (ID, Name, Type, Behaviour on failure) and an ASCII diagram of the sequential QA chain.

### Key facts captured

**The blocking vs. warning distinction is the most important thing this section documents.**

QA-P001 (row count sanity) and QA-P005 (DQ rejection store write) are blocking — the pipeline halts. QA-P002 (orphaned SK count), QA-P003 (RI rejections), and QA-P004 (business rules) are warnings — they log and continue. This asymmetry is deliberate and discussed in `tasks-explained.md`: QA-P001 blocks because a row count mismatch indicates data loss or duplication; QA-P002 through QA-P004 warn because orphaned SKs and business rule violations are informational signals that should not prevent loading.

**QA-P005 blocks.** This is less obvious. QA-P005 persists all accumulated rejections to `dq_rejections` as an atomic Delta write. If that write fails, the pipeline halts. The rationale is auditability: if rejections cannot be recorded, the run's quality history cannot be trusted. Blocking on the rejection write is more conservative than blocking on the violations themselves.

**The ASCII diagram is a clean summary of the chain.** It shows the sequential flow with explicit fork-on-fail behavior for QA-P001 and QA-P005. A maintenance engineer reading this diagram can determine at a glance what data exists in what tables after a mid-chain failure: if QA-P003 wrote to `dq_rejections` and then QA-P005 failed, there may be partial rejections in the table but no completion record.

**The QA chain description does not mention `migrate_staged_purchase_data`'s `max_retries: 0` retry policy.** That policy (from TASK-019 and the workflow JSON) is the operational complement to the blocking QA assertions: the MERGE is not retried because the QA assertions that blocked it will block again on retry. The codebase design mentions the three-task chain in Section 2 but does not connect the zero-retry policy to the blocking QA behavior. The runbook Section 2.4 does.

---

## Section 6 — Lineage Propagation

### What it contains

A lifecycle diagram showing INSERT and UPDATE operations across the three tasks, with the taskValues propagation chain.

### Key facts captured

**The diagram shows a two-tier parent-child lineage model.** `nb_extract_watermark` inserts a parent lineage record and publishes `lineage_key`. `nb_extract_purchase` reads the parent `lineage_key`, inserts a *child* lineage record with `lineage_key_parent`, and publishes a new child `lineage_key`. `migrate_staged_purchase_data` reads the child `lineage_key`.

The data dictionary's `lineage_run` schema has nine columns and no `lineage_key_parent` column. A flat single-tier schema with nine columns is what the data dictionary describes and what the DDL should have been generated with (the DDL had the PRIMARY KEY as its only constraint, confirmed by the prior-run finding F-001 now RESOLVED).

If the actual generated DDL at `src/db/ddl/bronze_lineage_run.sql` has nine columns (no `lineage_key_parent`), then the two-tier model in Section 6 is a fabrication — it describes a parent-child architecture that was not implemented. The operational consequence is that monitoring queries joining on `lineage_key_parent` would fail with "column not found." See divergence 2.

**The lifecycle shows `nb_extract_purchase` writing a second INSERT.** In the flat model (as described by the data dictionary), there is only one INSERT: `nb_extract_watermark` opens the lineage record, and `migrate_staged_purchase_data` closes it. `nb_extract_purchase` does not write to `lineage_run`; it only propagates the `lineage_key` it receives. The Section 6 diagram's depiction of `nb_extract_purchase` writing its own INSERT is a divergence from the actual implementation if the DDL is flat.

**`lineage_key` propagation to `fact_purchase` is described correctly.** "The `lineage_key` value is also written into every row of `fact_purchase` (column `lineage_key`) so that individual fact rows can be traced back to the specific pipeline run that produced them." This matches the data dictionary's derivation for `fact_purchase.lineage_key` and is the correct description of the flat lineage model.

---

## Section 7 — Configuration Management

### What it contains

An `environment.yaml` structure excerpt and a Python loading pattern snippet.

### Key facts captured

**The YAML excerpt includes the JDBC keys.** The `environment.yaml` in Section 7 shows:

```yaml
    jdbc_driver:   "{{JDBC_DRIVER_CLASS}}"
    jdbc_user:     "{{JDBC_USER}}"
    jdbc_password: "{{JDBC_PASSWORD}}"
    source_table:  "{{SOURCE_TABLE_FQTN}}"
```

These are the four keys that `validation-report.md` Finding F-003 identified as missing from the actual `config/environment.yaml`. Either the codebase design was written after F-003 was resolved (showing the corrected YAML), or it was written against the intended configuration rather than the generated one. In either case, this section's YAML is the correct target state — a reader using it to update `environment.yaml` will add the right keys.

**The `business_rules` section shows four keys.** `min_ordered_quantity`, `min_ordered_outers`, `date_window_tolerance_days`, `package_required`. The actual `config/environment.yaml` generated by TASK-018 has an empty `business_rules` section ("Add business factors here as they are identified during implementation"). Section 7's YAML is either aspirational or reflects a post-generation update. A reader comparing Section 7's YAML against the actual `environment.yaml` would find the business_rules keys missing.

**The loading pattern snippet is minimal but correct.** One `yaml.safe_load()` call followed by dict-key access. No error handling, no schema validation. This is consistent with the existing notebooks: they trust the config structure and raise `KeyError` if a key is absent (the F-003 failure mode). Section 7 does not note that the JDBC keys are placeholders pending PD-001, which a reader of the config snippet would need to know before trying to run the pipeline.

---

## Divergences and Open Items

### 1. `DM-001` and `DM-002` are phantom rule citations

Section 1's layer table cites `DM-001` (silver dim, "SCD-2 managed dimension tables") and `DM-002` (silver fact, "populated via MERGE INTO after SK resolution"). No DM dimension exists in this project's transformation rules. The project has PL, NM, TY, OB, SX, PE, LN, QA, CX. The DM citations propagated from a template.

The affected rows are the silver dimension and silver fact descriptions. The actual governing rules for those layers are SX-003, TY-P001 (SK resolution), FR-003, OB-002 (fact table), and CX-P003 (dimension join pattern). **Replace `DM-001` and `DM-002` citations with the actual rule IDs from the nine dimensions used in this project.**

### 2. Section 6 describes a two-tier parent-child lineage model that likely does not match the generated DDL

The lineage propagation diagram in Section 6 shows `nb_extract_purchase` creating a child lineage record with `lineage_key_parent`. The data dictionary's `lineage_run` schema has no `lineage_key_parent` column. If the actual DDL (at `src/db/ddl/bronze_lineage_run.sql`) is flat — nine columns, no parent-child relationship — then Section 6 is describing an architecture that was not built.

The consequence for operations: any runbook or monitoring query written against the two-tier model (using `lineage_key_parent` to trace task-level lineage within a run) will fail with a column-not-found error. **Verify the actual DDL. If flat, correct Section 6 to show a single INSERT by `nb_extract_watermark` and a single UPDATE by `migrate_staged_purchase_data`, with no child record from `nb_extract_purchase`.**

### 3. `lineage_key` type annotated as `int` in taskValues contract; DDL defines it as `BIGINT`

Section 2's taskValues table types `lineage_key` as `int`. The DDL defines the column as `BIGINT GENERATED ALWAYS AS IDENTITY`. In PySpark, `dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_key)` passes whatever Python type `lineage_key` is at the call site. If the IDENTITY value is returned from a Spark SQL INSERT as a long (64-bit), it is a `long` in Python, not `int`. For values below 2^31 this is harmless; for a table used as long-term audit storage that eventually accumulates billions of rows, the type matters. **Update the taskValues contract table to type `lineage_key` as `long` (Python) / `BIGINT` (SQL).**

### 4. `date_key` derivation source diverges from the data dictionary

Section 3 says `date_key` is derived from `format_date_key(stg.last_modified_when)` — the modification timestamp of the source record. The data dictionary says `date_key` is `CAST(po.OrderDate AS DATE)` from `Purchasing.PurchaseOrders.OrderDate` — the actual order date.

These are different dates. A purchase order modified on 2024-03-20 to increase an ordered quantity might have an `OrderDate` of 2024-03-01. Section 3's derivation would file the row under March 20; the data dictionary's derivation would file it under March 1. The fact grain is "one row per purchase order line × supplier × stock item × **order date**" — which means `OrderDate` is the correct source, and the data dictionary is right.

If the generated `nb_extract_purchase.py` uses `last_modified_when` for `date_key`, that is a substantive data error: purchase orders would be misfiled by their last-edit date rather than their order date. **Verify `nb_extract_purchase.py` lines where `date_key` is computed, confirm the source column, and correct Section 3 to match.**

### 5. Section 7's YAML shows keys that may not exist in the generated `config/environment.yaml`

Section 7 shows four `business_rules` keys and four JDBC keys in the `environment.yaml` excerpt. The generated TASK-018 YAML has an empty `business_rules` block and (as of F-003) missing JDBC keys. Section 7 may be showing the intended end-state rather than the generated state.

A new engineer reading Section 7 and then opening `config/environment.yaml` would see fewer keys and might conclude that Section 7 is wrong rather than that the config needs to be updated. **Add a note to Section 7: "The JDBC keys below are placeholders; add them to `config/environment.yaml` when PD-001 resolves. Business rule keys reflect intended configuration; current values are in `config/environment.yaml`."**

---

## How This Spec Is Used Downstream

| Consumer | What they take from the codebase design |
|---|---|
| **On-call engineer** | Section 2 (task sequence and taskValues) and Section 5 (QA chain blocking vs. warning) for failure triage |
| **New data engineer** | Sections 1–3 for a system orientation in 15 minutes |
| **BI developer** | Section 3 SK resolution (understanding why `supplier_key` can be 0) |
| **Monitoring engineer** | Section 5 QA chain (which assertions write to `dq_rejections`, which halt the pipeline) |
| **Platform engineer** | Section 7 (config structure, loading pattern) |

---

## File Reference

| File | Location |
|---|---|
| `codebase/docs/design.md` (this document) | `products/Purchase/current/codebase/docs/design.md` |
| `specifications/development_plan/design.md` | `products/Purchase/current/specifications/development_plan/design.md` — the upstream spec this was derived from |
| `docs/data-dictionary.md` | `products/Purchase/current/codebase/docs/data-dictionary.md` — authoritative column-level reference; diverges from this document on `lineage_key_parent` and `date_key` derivation |
| `src/db/ddl/bronze_lineage_run.sql` | `products/Purchase/current/codebase/src/db/ddl/bronze_lineage_run.sql` — authoritative schema for the lineage table; resolves divergence 2 |
| `src/etl/nb_extract_purchase.py` | `products/Purchase/current/codebase/src/etl/nb_extract_purchase.py` — authoritative source for `date_key` derivation; resolves divergence 4 |
| `config/environment.yaml` | `products/Purchase/current/codebase/config/environment.yaml` — actual generated config; compare against Section 7's YAML |
| `validation-report.md` | `products/Purchase/current/codebase/validation-report.md` — F-006/F-007 raised against an earlier version of this document; current version has correct table names |
