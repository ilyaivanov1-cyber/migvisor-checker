# Data Dictionary — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `src/db/ddl/` (DDL files), `specifications/development_plan/design.md`, transformation rules
**Location:** `products/Purchase/current/codebase/docs/data-dictionary.md`
**Produced by:** `/smartbuilder_generate-etl` (TASK-026)
**Contents:** 5 tables — 11 + 15 + 9 + 3 + 10 columns = 48 total column definitions

---

## What This Spec Is

The data dictionary is the **column-level contract** for every table the Purchase product owns or manages. It is a generated codebase document — written after the DDL files exist — that adds business context, derivation logic, and rule citations to the structural information already in the SQL.

It sits at the end of the artifact chain, alongside the codebase design doc and the BI reconnection specs:

| Artifact | Question it answers |
|---|---|
| `specifications/development_plan/design.md` | How is the system designed? |
| `src/db/ddl/*.sql` | What does the database schema look like? |
| `docs/design.md` (codebase) | How does the ETL pipeline work? |
| **`docs/data-dictionary.md`** | **What does every column mean, where does it come from, and why?** |
| `docs/bi/*.md` | What must be changed in the BI layer? |

Five tables appear in it — one silver fact, one bronze staging, and three bronze control tables. Every column has seven fields: number, name, data type, nullable, description, business meaning, and derivation/source. The derivation field is what distinguishes this dictionary from a schema dump — it explains how each value is computed or extracted, not just what it holds.

---

## Why This Spec Exists

### Because DDL is structural, not semantic

A DDL file tells you the column name, type, and nullability. It does not tell you what `lineage_key` is for, why `supplier_key` can be 0, or why `_extracted_at_utc` has no legacy equivalent. A reader of `silver_fact_fact_purchase.sql` learns the schema; a reader of the data dictionary learns the schema and why each choice was made.

### Because the derivation chain is complex and non-obvious

Several columns in Purchase tables are not pass-throughs. `supplier_key` and `stock_item_key` are the result of a temporal range join with a DESC tie-breaker and a COALESCE fallback. `lineage_key` originates in `nb_extract_watermark`, travels through `taskValues`, and appears in three different tables. `_extracted_at_utc` is generated in Python at write time with no source column. Those derivations are implicit in the ETL code; the data dictionary makes them explicit and cross-references the rules that govern them.

### Because BI reports, monitoring queries, and downstream products all read these tables

The BI reconnection specs reference the data dictionary explicitly ("If the legacy report references any other columns from `fact.purchase` not listed above, consult the data dictionary"). A monitoring engineer querying `bronze.dq_rejections` needs to know what `rule_id`, `pk_column`, and `rejection_reason` contain. The data dictionary serves all of those readers without them having to reconstruct the semantics from the ETL code.

---

## Table 1 — `silver_fact.fact_purchase`

### What it contains

Eleven columns covering the grain-level purchase order line fact table. Each row represents one purchase order line identified by `purchase_key`.

### Key facts captured

**The data dictionary uses the four-column MERGE key, correcting the single-column defect in the build plan and tasks.md.**

Row 5 (`wwi_purchase_order_id`) derivation field: "Used as part of the 4-column MERGE predicate in `fact_merge.py`: `(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)`."

This is the correct MERGE key — the one that matches `to-be.md`'s composite grain specification. The build plan's Phase 2 constraint table, `design.md` §3.3, and TASK-012 all carry the single-column `wwi_purchase_order_id` MERGE defect. The data dictionary is the only document other than `to-be.md` that states the four-column key correctly. A reviewer catching this discrepancy between the data dictionary and the build plan has the data dictionary's version as the correct reference. See divergence 1 below.

**Three columns exist only in the target; none existed in the legacy fact table.**

`purchase_key` (IDENTITY surrogate PK), `is_order_finalized` (BIT → BOOLEAN, TY-015), and `lineage_key` (audit FK) are the three most structurally significant. `purchase_key` replaces the legacy's own surrogate PK by generating a new IDENTITY sequence. `is_order_finalized` is a direct type mapping. `lineage_key` has no legacy counterpart at all — it is a new audit column that the transformation rules added to support end-to-end lineage tracing.

**`supplier_key` and `stock_item_key` derivations are the most technically dense entries.**

Both cite `sk_resolver.py`, the temporal range join pattern, the DESC ROW_NUMBER tie-breaker, and the COALESCE-to-0 fallback. The derivation field explicitly cites TY-P001 (DATE vs. TIMESTAMP cast) — the cast that prevents silent off-by-one-day resolution errors when joining TIMESTAMP source data against DATE dimension validity ranges. This is one of the few places in the codebase documentation where the reason for a specific cast is recorded in a place a reader of the fact table's schema would encounter it.

**`received_outers` is the only nullable column among the measures.** The distinction between NULL (not received yet) and 0 (delivered with zero outers) is documented in the nullable and description fields. This distinction matters for fill-rate calculations in the BI layer.

---

## Table 2 — `bronze.purchase_staging`

### What it contains

Fifteen columns covering the transient staging landing zone. Surrogate keys (`supplier_key`, `stock_item_key`) are NULL at extract time and populated in-place by `sk_resolver.py`.

### Key facts captured

**Fifteen columns is the correct count — matching TASK-003's DDL and acceptance criterion.**

TASK-003's acceptance criterion requires `DESCRIBE TABLE` to return 15 columns. The data dictionary has exactly 15. `tasks-explained.md` noted that "all four column counts in the acceptance criteria are correct"; this is the staging table's corroboration.

**Two columns exist only in the staging table and are never propagated to `fact_purchase`.**

`wwi_supplier_id` and `wwi_stock_item_id` are the natural keys from the source OLTP system, retained in staging for the SK resolution join but dropped after the MERGE. A reader querying `fact_purchase` looking for the original source natural key will find `wwi_purchase_order_id` (retained in the fact table) but not `wwi_supplier_id` or `wwi_stock_item_id`. The data dictionary makes this drop explicit in the derivation field ("Not propagated to `fact_purchase`").

**`purchase_staging_key` is the partition key for `sk_resolver.py` window functions.** Its derivation field explains its unusual purpose: it is generated by Delta's IDENTITY on insert, and then used as `PARTITION BY purchase_staging_key` in the SK resolution window function. That means each staging row is partitioned by its own unique key — effectively making the ROW_NUMBER window per-row, which forces the tie-breaker to always select the most-recent dimension version per row rather than across groups. This is a subtle design decision that the DDL file (`BIGINT GENERATED ALWAYS AS IDENTITY`) does not explain.

**`_extracted_at_utc` is the latency measurement anchor.** The derivation field explains it is set to `datetime.now(timezone.utc)` at write time in `nb_extract_purchase`, with no legacy equivalent. Its purpose ("enables latency measurement: time from `last_modified_when` in source to `_extracted_at_utc` in bronze") and rule reference (OB-P002, SX-008) are stated here and nowhere in the DDL.

**The OVERWRITE load pattern is explained in the table header, not just in the design.** "Full OVERWRITE per batch run, eliminating the stale-row accumulation defect from the legacy SSIS pipeline (which truncated the wrong table `Integration.Order_Staging`)." This is the as-is defect that the migration was designed to fix — it reappears here as a note in the staging table's purpose statement, connecting the target design choice directly to the source system problem it addresses.

---

## Table 3 — `bronze.lineage_run`

### What it contains

Nine columns for the ETL run audit log. One row per pipeline execution. CDF enabled.

### Key facts captured

**The `was_successful` column has three states, not two.** NULL (run in progress), TRUE (success), FALSE (failure). This three-valued design is explained in the nullable field and the description. A monitoring query that checks `was_successful = false` will miss in-flight runs; a query that checks `was_successful IS NULL` identifies runs that are currently executing or crashed without closing. The distinction is operationally important: `was_successful = NULL` after the expected run window means the pipeline is stuck, not that it is running normally.

**`lineage_key` is defined as the primary key and the traceability anchor.** The derivation field says it replaces `NEXT VALUE FOR sequences.lineagekey` from the legacy SQL Server system. The prior-run finding F-001 (resolved in the validation report) was precisely about this column's PRIMARY KEY constraint. The data dictionary is where a reader finds the constraint noted (`CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)`) alongside the business purpose.

**`source_system_cutoff_time` is the extraction window boundary.** Its derivation field explains that it is set to the new cutoff value (not the old one) — "the `cutoff_time` read from `bronze.etl_cutoff` at the start of the run (or the new cutoff calculated for this run)." This means the column records the *upper* boundary of the window that was used, not the prior watermark. For debugging extraction window issues, this is the column to check: it tells you exactly what was extracted.

**`etl_run_id` provides global uniqueness for cross-system correlation.** UUID string generated by `str(uuid.uuid4())`. This is the column to use when matching a `lineage_run` row to a Databricks Workflow run or to an external monitoring system. `lineage_key` (the IDENTITY integer) is the internal join key; `etl_run_id` is the human-readable cross-system reference.

---

## Table 4 — `bronze.etl_cutoff`

### What it contains

Three columns for the incremental watermark control. One row per tracked table.

### Key facts captured

**This is the simplest table in the dictionary and also the most operationally sensitive.** Three columns — `table_name`, `cutoff_time`, `last_updated_utc`. But the `cutoff_time` value determines what every subsequent pipeline run extracts. If it is wrong — set too far in the past, causing re-extraction; or too far in the future, causing data gaps — the entire pipeline produces incorrect results until it is corrected. The data dictionary's description ("The high-watermark timestamp marking the upper boundary of the last successful incremental extract") makes the semantics explicit: `cutoff_time` is the upper bound, and the next run extracts `last_modified_when > cutoff_time`.

**The watermark can only be reset via `reseed_purchase_environment.py` (PD-002).** The table has one row per tracked table; that row is updated by `set_etl_cutoff()` after a successful run. There is no DELETE or explicit reset operation in the ETL code. Resetting requires running the reseed notebook, which requires scope-owner sign-off (PD-002). The data dictionary documents the column but does not document this operational constraint — the runbook does.

**`last_updated_utc` has no direct legacy equivalent.** It is a new audit column (NM-009 governs naming of such columns). In the legacy system, `integration.etl cutoff.Cutoff Time` was the only column. The new `last_updated_utc` enables detection of stalled pipelines: if `last_updated_utc` is more than 24 hours old, the watermark has not been advanced and a run likely failed.

---

## Table 5 — `bronze.dq_rejections`

### What it contains

Ten columns for the centralized DQ rejection store. Append-only; one row per column-level DQ violation per source row per ETL run.

### Key facts captured

**Ten columns is the correct count — resolving the discrepancy in NFR-007.** NFR-007 says "nine required columns" and then lists ten. TASK-004's DDL declares ten, and the data dictionary has ten. The data dictionary is correct; the requirement's count is wrong. (Noted in `tasks-explained.md` divergence noting TASK-004 "quietly corrects an error upstream.")

**The grain is column-level, not row-level.** One rejection record per violated column per source row. A staging row that fails three QA assertions on three different columns would produce three rows in `dq_rejections`. The `pk_column`/`pk_value` pair identifies the source row; `violation_column` identifies which column within that row triggered the violation. This granularity enables specific remediation — "fix this column value for this row" — rather than "this row was rejected (for an unknown reason)."

**`violation_value` is nullable, but `rejection_reason` is not.** A NULL violation value occurs when the violation is triggered by a NULL in the source column (e.g., a NOT NULL constraint violation). The reason is always provided — the derivation field says it is set to a descriptive string matching the violated rule's intent. This means `dq_rejections` is always human-readable without needing to cross-reference the rule documentation.

**The append-only insert pattern means `dq_rejections` accumulates across runs.** There is no OVERWRITE or DELETE in the ETL pipeline for this table. A row written for `lineage_key = 5` stays forever. Monitoring queries must filter by `lineage_key` to see the current run's rejections, or by date range on `detected_at`. The `lineage_key` join to `lineage_run` provides the run context (which pipeline, what cutoff window, was it successful).

---

## Divergences and Open Items

### 1. The data dictionary is the only document other than `to-be.md` that states the correct four-column MERGE key

`fact_purchase`'s column 5 (`wwi_purchase_order_id`) derivation field states "4-column MERGE predicate in `fact_merge.py`: `(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)`." The build plan's Phase 2 constraint table, TASK-012, and the codebase `docs/design.md` Section 4 all specify the single-column key `wwi_purchase_order_id`. Only `to-be.md` and this document state the four-column key.

This means the data dictionary implicitly contradicts the build plan and codebase design doc on a load-bearing design decision. **When the MERGE key defect is resolved, all four artifacts (build plan constraint table, TASK-012, codebase design.md, and `fact_merge.py`) should be reconciled to the four-column key. The data dictionary's derivation field is the correct reference.**

### 2. The `lineage_run` table in the data dictionary describes a two-tier schema that diverges from the DDL

The data dictionary's lineage_run table has nine columns: `lineage_key`, `etl_run_id`, `table_name`, `pipeline_name`, `data_load_started`, `data_load_completed`, `was_successful`, `table_row_count`, `source_system_cutoff_time`.

The codebase `docs/design.md` Section 6 describes a two-tier parent-child lineage model where `nb_extract_purchase` creates a child lineage record with a `lineage_key_parent` column. The data dictionary's lineage_run schema has no `lineage_key_parent` column.

The actual DDL at `src/db/ddl/bronze_lineage_run.sql` is the authoritative source. The nine-column flat schema in the data dictionary is likely what was generated; the parent-child model in the codebase design is a divergence in that document. **Verify against the DDL. If the actual DDL is flat (no parent-child), the codebase design.md Section 6 contains a false lineage propagation diagram that should be corrected.**

### 3. `batch_lookback_days` in `environment.yaml` is referenced in no data dictionary column

`tasks-explained.md` noted that `batch_lookback_days: 1` is "declared here but referenced by no task, calculation, or requirement in the chain." The data dictionary confirms it — no column in any table records a value derived from `batch_lookback_days`. It may be used in `nb_extract_purchase` to extend the extract window backward, but if so, the effect is not documented. **Either document which column is affected by `batch_lookback_days` (likely the extract predicate in `nb_extract_purchase`) or remove it from `environment.yaml` as an unused configuration key.**

### 4. `dq_rejections` monitoring queries in the runbook use column names not in the data dictionary

The runbook's Section 5 (Useful Queries) includes:

```sql
SELECT assertion_name, violation_type, COUNT(*) AS cnt
FROM inventory_stock.bronze.dq_rejections
WHERE lineage_key = ...
GROUP BY assertion_name, violation_type
```

The data dictionary's `dq_rejections` schema has `rule_id` (not `assertion_name`) and has no `violation_type` column. The runbook query references columns that do not exist in the table as documented.

This is either a discrepancy between the actual generated DDL and the data dictionary, or the runbook was written before the column names were finalized. **Verify the actual DDL at `src/db/ddl/bronze_dq_rejections.sql` and reconcile the runbook query with the authoritative column names.**

---

## How This Spec Is Used Downstream

| Consumer | What they take from the data dictionary |
|---|---|
| **BI developer** | Column-by-column name substitution guide (referenced explicitly in BI reconnection specs) |
| **Monitoring engineer** | Column semantics for `lineage_run` and `dq_rejections` monitoring queries |
| **Data engineer debugging** | Derivation chain for SK resolution columns; `purchase_staging_key` partitioning purpose; staging natural keys (`wwi_supplier_id`, `wwi_stock_item_id`) as join handles |
| **Downstream product** | `lineage_key` propagation pattern — any product reading `fact_purchase` can trace rows to their source runs via `lineage_key → lineage_run` |
| **Governance / compliance** | `lineage_key` on every row of every fact and staging table as the audit anchor |
| **QA / test writer** | Grain, nullable columns, and three-valued `was_successful` semantics for test case design |

---

## File Reference

| File | Location |
|---|---|
| `data-dictionary.md` | `products/Purchase/current/codebase/docs/data-dictionary.md` |
| `src/db/ddl/` | `products/Purchase/current/codebase/src/db/ddl/` — authoritative DDL for column types and constraints |
| `specifications/development_plan/design.md` | Source of the grain, load pattern, and Delta property decisions |
| `docs/design.md` (codebase) | Companion ETL design document (Section 6 lineage propagation may diverge from the data dictionary) |
| `tasks.md` TASK-026 | `products/Purchase/current/specifications/development_plan/tasks.md` — the task that generated this document |
| `validation-report.md` | `products/Purchase/current/codebase/validation-report.md` — the prior-run F-001 finding (missing PRIMARY KEY on `lineage_run`) is now RESOLVED; data dictionary's lineage_run section reflects the corrected constraint |
