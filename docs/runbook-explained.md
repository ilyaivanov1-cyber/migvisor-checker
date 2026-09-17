# Runbook — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `codebase/build-plan.md` (pending decisions), `specifications/development_plan/tasks.md` (TASK-019 retry policy), transformation rules (LN-lineage)
**Location:** `products/Purchase/current/codebase/docs/runbook.md`
**Produced by:** SmartBuilder (no task ID assigned — generated off-plan)
**Contents:** 5 sections — normal operations, failure recovery (4 subsections), SK resolution failure, cutover checklist (4 pending decisions + 9-step sequence), 5 diagnostic queries

---

## What This Spec Is

The runbook is the **operational guide for everyone who runs the Purchase ETL pipeline after go-live**. It covers day-to-day monitoring, failure recovery, and the one-time production cutover sequence.

It is the only codebase document written entirely from an *operator's* perspective. Every other artifact in the chain — specifications, build plan, validation report — is written for engineers building or reviewing the system. The runbook is written for engineers keeping the system running.

Its position in the artifact chain is unusual:

| Artifact | Audience | When used |
|---|---|---|
| `build-plan.md` | Build operator | During construction |
| `validation-report.md` | Reviewer | After construction |
| `docs/design.md` (codebase) | Maintenance engineer | When changing the system |
| **`docs/runbook.md`** | **On-call / platform engineer** | **When the system is running (or failing)** |

It is also the only artifact with no task ID. `build-plan-explained.md` documented this provenance gap: the LN transformation rules required that "the two-tier lineage model and the IDENTITY reseed procedure be documented in the runbook," but no task was created to produce that document. SmartBuilder generated it anyway — off-plan, untasked, unmanifested — because the rule obligation was visible in the spec. The result is the most operationally useful document in the codebase that no manifest tracks.

---

## Why This Spec Exists

### Because the pending decisions have operational consequences that no other artifact explains

PD-001, PD-002, PD-003, and QA-DQ-01 are registered in `build-plan.md`'s Pending Decisions table. They also appear in the specifications and task lists. But those artifacts describe the pending decisions as *blockers* — things that prevent generation or review. The runbook is the first artifact that describes them as *actions* — what specifically to do, in what order, and who does it.

Section 4's cutover checklist is the go-live procedure. It converts four abstract pending decisions into nine concrete steps with a defined sequence. That transformation — from decision registry to action sequence — exists nowhere else in the artifact chain.

### Because the halt-and-alert policy creates specific recovery paths that must be documented

`nightly_etl_purchase` uses `max_retries: 2` on the first two tasks and `max_retries: 0` on the MERGE task. When the pipeline fails, the recovery path depends on *which* task failed and *why*. An on-call engineer receiving a 02:30 UTC alert cannot read the task list or build plan to find the recovery steps. The runbook provides them, organized by the failure scenarios the retry policy creates.

### Because the LN transformation rules mandated it

The LN-lineage rule required runbook documentation of the lineage model. That obligation made its way into the generated codebase through the rule-to-task traceability chain — the generator produced a runbook because the rules said the runbook should exist. Whether the generator was right to produce it off-plan is debatable; whether the result is useful is not.

---

## Section 1 — Normal Operations

### What it contains

Two subsections: scheduled run monitoring and manual trigger steps.

### Key facts captured

**The success indicator is `was_successful = true` in `bronze.lineage_run`.** Not "the Databricks Workflows UI shows Success" — the authoritative record is the lineage table. The UI shows job status; the lineage table shows whether the ETL logic completed correctly. A run can succeed in the Databricks sense (no unhandled exception) but write `was_successful = false` to the lineage table if the pipeline logic itself caught and recorded a failure. The runbook points at the right indicator.

**Manual triggers require no parameter overrides.** The watermark is read from `bronze.etl_cutoff` automatically. A re-run after a source-side data fix simply executes the next incremental window; if the fix was applied to yesterday's data, the re-run extracts rows with `last_modified_when > last_cutoff`, which will pick up the corrected rows if they have been touched after the cutoff. If the fix predates the last cutoff, a watermark reset (section 2.2, step 3) may be needed.

---

## Section 2 — Failure Recovery

### What it contains

A general approach statement and four task-specific recovery subsections: `nb_extract_watermark` failed, `nb_extract_purchase` failed, `migrate_staged_purchase_data` failed on QA-P001, `migrate_staged_purchase_data` failed on other errors.

### Key facts captured

**The halt-and-alert policy is stated upfront: "Databricks stops all downstream tasks in the run."** This is the direct operational consequence of the retry design. If Task 1 fails, Tasks 2 and 3 do not run. If Task 2 fails after Task 1 succeeded, Task 3 does not run. There are no partial-completion states that leave the pipeline in an unknown position mid-execution.

**Section 2.2 (`nb_extract_watermark` failed) names the reseed notebook as the recovery option.** If `bronze.etl_cutoff` is missing the row for `purchase_staging`, the recovery is to run `reseed_purchase_environment.py` — but that requires PD-002 sign-off. The runbook correctly adds the dependency note ("requires PD-002 sign-off — see Pending Decisions"). A reader encountering this step during an incident knows it is not a self-service action.

**Section 2.3 (`nb_extract_purchase` failed) correctly says a partial staging write is safe to re-run.** `bronze.purchase_staging` is loaded via full OVERWRITE per run. A failed extract run that wrote partial data into staging leaves no residue — the next run overwrites it completely. This is why the staging OVERWRITE pattern (chosen to fix the legacy SSIS stale-row accumulation defect) has an operational benefit: recovery is always a clean re-run, never a manual staging cleanup.

**Section 2.3 also says the failed lineage record needs no manual cleanup.** The `nb_extract_watermark` already closed the lineage record with `was_successful = false` before the extract task even started (or `nb_extract_purchase` closes it on failure). "Do not manually modify `bronze.lineage_run`" is the explicit instruction. This is correct: manual edits to the lineage table break the audit trail and could cause the next run's watermark to behave unexpectedly.

**Section 2.4 (QA-P001 RuntimeError) is the most operationally nuanced subsection.** It distinguishes two causes: staging count of 0 (extract wrote no rows) and staging count unexpectedly high (possible duplication). The recovery for each is different:
- Count of 0: re-trigger from `nb_extract_purchase` — the watermark notebook doesn't need to re-run.
- Count high: investigate the JDBC extract predicate and the watermark, then re-run from scratch.

The section correctly says "do not manually modify `bronze.purchase_staging` or `bronze.lineage_run`." This is the key operational constraint: the pipeline's self-healing design (watermark not advanced on failure, staging overwritten on next run) only works if the lineage and cutoff tables are not manually edited.

**Section 2.5 (other errors) sends the reader to `dq_rejections` first.** The recommended query checks `assertion_name` and `violation_type` columns — but the data dictionary's `dq_rejections` schema has `rule_id`, `violation_column`, and `rejection_reason`, not `assertion_name` and `violation_type`. The query will fail with "column not found." See divergence 1.

---

## Section 3 — Surrogate Key Resolution Failure

### What it contains

The symptom (all-null `supplier_key` or `stock_item_key`), the root cause (dimension tables not loaded), and two verification queries.

### Key facts captured

**"These tables must be pre-loaded by the Dimensions team before Purchase ETL can succeed."** This is the prerequisite check from `build-plan.md` Section 8, now expressed as an operational fact rather than a pre-flight item. In the build plan, it is a pre-condition; in the runbook, it is a recovery step. If the Dimensions team's load ran late or failed, the Purchase pipeline's SK resolution will produce all-null keys, and the QA-P002 assertion will log a high orphan rate — but the pipeline will not halt on that alone (QA-P002 is a warning).

**The verification queries use the `_current` views.** `SELECT COUNT(*) FROM inventory_stock.silver_dim.supplier_current` returning 0 means the Dimensions team's SCD-2 load has not run or has not completed. The `_current` view pre-filters `is_current_row = TRUE`, so a non-zero count confirms at least some current-version rows exist. This is the correct verification — checking the base `silver_dim.supplier` would include historical versions and might return non-zero even when no current rows exist.

**"Escalate to the Dimensions team — do not proceed with Purchase ETL."** This instruction prevents the purchase pipeline from merging all-null-SK rows into `fact_purchase`, which would corrupt the fact table's analytical usefulness. Halting here is correct. The validation report's F-003 (JDBC config KeyError) would prevent reaching this step anyway, but once PD-001 resolves and the extract runs, this section becomes the most likely operational failure path in a multi-product deployment sequence.

---

## Section 4 — Cutover Checklist

### What it contains

A four-row pending decisions table (ID, action, what it blocks) and a nine-step cutover sequence.

### Key facts captured

**This is the only artifact that presents all four pending decisions as a unified go-live procedure.** `build-plan.md` registers them as blockers. The runbook converts them into a sequenced action list:

| Step | Action | Resolves |
|---|---|---|
| 1 | Update `environment.yaml`, test JDBC connectivity | PD-001 |
| 2 | Get PD-002 sign-off, run reseed notebook | PD-002 |
| 3 | Execute DDL files against target catalog | — |
| 4 | Verify prerequisites (README) | — |
| 5 | Confirm Dimensions team loaded `silver_dim.supplier` and `silver_dim.stock_item` | Build plan prerequisite check |
| 6 | Trigger `nb_extract_watermark` standalone | — |
| 7 | Trigger full pipeline; verify `lineage_run` shows success | — |
| 8 | Run `purchase_grants.sql` to grant BI access | PD-003 |
| 9 | Tune business rule thresholds in `environment.yaml` | QA-DQ-01 |

**Step 3 ("Run `scripts/deploy_ddl.sh` or execute DDL files manually") references a script that may not exist.** There is no `scripts/` directory in the workspace glob results and no TASK in the task list that generates a deployment script. The alternative ("execute DDL files manually") is the fallback. This reference to a non-existent script should not block a cutover — but an engineer who looks for `deploy_ddl.sh` and cannot find it may lose time. See divergence 2.

**Step 9 (QA-DQ-01 threshold tuning) is marked after go-live.** QA-DQ-01 "does not block generation" per the build plan. The runbook sequences it last, correctly. This means the initial production run uses provisional thresholds from `environment.yaml`. If the orphan SK rate or business rule violation rate exceeds those provisional thresholds, the QA assertions will log warnings — informational, not blocking — until step 9 is completed.

**The cutover sequence correctly places the dimension pre-load verification at step 5, before any ETL trigger.** The build plan's prerequisite checks (Section 8) include this verification but present it alongside four other checks with equal weight. The runbook's sequencing makes it the specific go/no-go gate before the first pipeline run.

---

## Section 5 — Useful Queries

### What it contains

Five SQL snippets: last 10 pipeline runs, current watermark, DQ rejection summary, and fact table row count.

### Key facts captured

**The last-10-runs query is the first thing an on-call engineer should run.** It returns `lineage_key`, `pipeline_name`, `data_load_started`, `data_load_completed`, `was_successful`, `table_row_count`, and `source_system_cutoff_time` from `bronze.lineage_run`. All seven columns are in the data dictionary; the query is immediately executable.

**The DQ rejection summary query uses wrong column names.** The query groups by `assertion_name` and `violation_type`. The data dictionary's `dq_rejections` schema has `rule_id` (maps to assertion name) and no `violation_type` column (the closest is `violation_column` — which column was violated — and `rejection_reason` — the human-readable cause). The query will fail with a column-not-found error. See divergence 1.

**The fact table row count query (`SELECT COUNT(*)`) is operationally useful but can be slow.** `silver_fact.fact_purchase` is clustered by `(date_key, supplier_key)`. A COUNT(*) without predicates scans the full table. For monitoring purposes, `lineage_run.table_row_count` (written by `close_lineage_record()` after each MERGE) is a faster proxy — it shows how many rows were merged in the last run without scanning the fact table. The runbook could supplement the COUNT(*) with "for a faster check, query `bronze.lineage_run.table_row_count` from the most recent successful run."

---

## Divergences and Open Items

### 1. The DQ rejection queries use column names not in the data dictionary

Section 2.5 and Section 5 both query `bronze.dq_rejections` with `assertion_name` and `violation_type`. The data dictionary's `dq_rejections` schema has `rule_id`, `violation_column`, and `rejection_reason`. Neither `assertion_name` nor `violation_type` appears in the dictionary.

The same discrepancy was noted in `data-dictionary-explained.md`. Either the actual generated DDL at `src/db/ddl/bronze_dq_rejections.sql` uses column names that differ from the data dictionary, or the runbook queries were written against an earlier column naming convention. **Verify the DDL and update the runbook queries to use the correct column names. The monitoring queries in Section 5 are the most visible to on-call engineers and the most likely to be run without testing first.**

### 2. Step 3 references `scripts/deploy_ddl.sh`, which does not exist in the manifest

The cutover sequence step 3 says "Run `scripts/deploy_ddl.sh` (or execute DDL files manually)." No such script appears in the codebase manifest, the task list (no DDL deployment task), or the workspace glob. The parenthetical fallback ("execute DDL files manually") is the actual viable option for a first production deployment.

**Either add a TASK-000 or similar that generates `scripts/deploy_ddl.sh`, or remove the script reference from step 3 and replace it with explicit manual DDL execution instructions (the order: run lineage/control tables first — TASK-001, TASK-002, TASK-004 — before staging and fact tables that reference them).** The ordering matters: if `silver_fact.fact_purchase` is created before `bronze.lineage_run`, the FK reference compiles but the risk of orphaned `lineage_key` values during early runs is higher.

### 3. The runbook does not document the watermark reset procedure for data corrections

Section 2.2 mentions `reseed_purchase_environment.py` as the option when `bronze.etl_cutoff` is missing its row. But a more common operational need is rewinding the watermark to re-extract data when a source-side correction predates the last cutoff — for example, a supplier record corrected three days ago when the watermark has already advanced past that point.

The reseed notebook resets `etl_cutoff` to `initial_load_date`, forcing a full re-extract. That is the nuclear option. There is no documented procedure for a targeted watermark reset (e.g., `UPDATE bronze.etl_cutoff SET cutoff_time = '2024-03-01' WHERE table_name = 'fact_purchase'`). **A targeted watermark reset procedure, including the audit implications (the lineage_run record for the re-run will show a larger `source_system_cutoff_time` than expected), should be added as Section 2.6 or an appendix.**

### 4. The runbook has no monitoring thresholds or SLA escalation guidance

NFR-001 specifies a 06:00 UTC SLA. The pipeline runs at 02:00 UTC. The four-hour window is designed to fit two retries on the extract tasks within the SLA budget. But the runbook does not state: "if the pipeline is still running at 04:30 UTC, escalate." It also does not define what constitutes a DQ anomaly worth escalating beyond the pipeline's own assertions.

A complete operational runbook would have: SLA-based escalation thresholds ("if no successful lineage_run by 05:45 UTC, escalate to the data engineering lead"), DQ anomaly thresholds by assertion ("if QA-P002 orphan count exceeds N for three consecutive runs, escalate"), and a named escalation path. **Add a Section 6 — Escalation Thresholds — covering SLA, DQ anomaly rates, and contact routing.**

### 5. The runbook is untracked and cannot be regenerated cleanly

The runbook was generated without a task ID. It does not appear in `_manifest.yaml`. The LN rules that required it do not point to a specific task. If the pipeline design changes (new task added, retry policy updated, QA assertion renamed), there is no mechanism to identify the runbook as a downstream artifact that needs regenerating.

Every other codebase artifact is owned by a task and trackable. This one is not. **Assign a TASK-027 to own the runbook, or fold the LN rules' runbook obligation into TASK-025 (the docs task). Without ownership, future regeneration will either skip the runbook (leaving stale content) or produce a second runbook alongside the first.**

---

## How This Spec Is Used Downstream

| Consumer | What they take from the runbook |
|---|---|
| **On-call engineer** | Section 2 (failure recovery by task) and Section 5 (diagnostic queries) — the primary runtime reference |
| **Platform / deployment engineer** | Section 4 (cutover checklist — pending decision resolution and 9-step sequence) |
| **Data engineering lead** | Section 3 (dimension dependency coordination with the Dimensions team) |
| **BI developer** | Section 4 step 8 (PD-003 grant execution — prerequisite for report cutover) |
| **Business analyst** | Section 4 step 9 (QA-DQ-01 threshold tuning — requires business input) |

---

## File Reference

| File | Location |
|---|---|
| `runbook.md` | `products/Purchase/current/codebase/docs/runbook.md` |
| `build-plan.md` | `products/Purchase/current/codebase/build-plan.md` — source of the pending decisions table and prerequisite checks that this runbook operationalizes |
| `config/workflows/nightly_etl_purchase.json` | `products/Purchase/current/codebase/config/workflows/nightly_etl_purchase.json` — the retry policy that determines which recovery path to follow |
| `src/init/reseed_purchase_environment.py` | `products/Purchase/current/codebase/src/init/reseed_purchase_environment.py` — the reseed notebook referenced in Section 2.2 (requires PD-002 sign-off) |
| `src/db/grants/purchase_grants.sql` | `products/Purchase/current/codebase/src/db/grants/purchase_grants.sql` — executed at cutover step 8 to resolve PD-003 |
| `config/environment.yaml` | `products/Purchase/current/codebase/config/environment.yaml` — updated at cutover steps 1 and 9 |
| `src/db/ddl/bronze_dq_rejections.sql` | `products/Purchase/current/codebase/src/db/ddl/bronze_dq_rejections.sql` — authoritative column names for the DQ rejection queries in Sections 2.5 and 5 |
| `_manifest.yaml` | `products/Purchase/current/_manifest.yaml` — does NOT list this runbook; no task produced it |
