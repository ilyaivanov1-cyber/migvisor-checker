# Validation Report — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `codebase/` artifacts vs. `specifications/development_plan/` + transformation rules
**Location:** `products/Purchase/current/codebase/validation-report.md` — inside the codebase, after generation
**Produced by:** `/smartbuilder_validation` (the `validation` step)
**Contents:** 27 artifacts checked → 19 PASS / 8 FAIL → 7 unique findings (F-001 through F-008; one prior finding RESOLVED)

---

## What This Spec Is

The validation report is the **post-build audit**. It walks every generated artifact and checks it against the specifications, transformation rules, and phase acceptance gates — then records what passed, what failed, and what to do about each failure.

It is the last document in the chain, and the only one written *after* the code exists:

| Artifact | Lives in | Written by | Audience |
|---|---|---|---|
| `product-definition.yaml` | `specifications/development_plan/` | `define` | Consumer + generator |
| `requirements.md` | `specifications/development_plan/` | `requirements` | Reviewer |
| `design.md` | `specifications/development_plan/` | `design` | Engineer |
| `tasks.md` | `specifications/development_plan/` | `tasks` | Engineer + generator |
| `build-plan.md` | `codebase/` | `plan` | Build operator |
| **`validation-report.md`** | **`codebase/`** | **`validation`** | **Reviewer, after the fact** |

Like `build-plan.md`, it lives in `codebase/` rather than `specifications/`. That placement is meaningful: it is a statement about the real code, not an upstream design. It can describe a path that does not match the plan, a test that fails, or a key that is missing — things no specification can know before generation.

It has four sections:

| Section | What it supplies |
|---|---|
| Results Table | One row per artifact — Status and Findings at a glance |
| Prior-Run Finding Status | Resolution check for findings from the previous validation run |
| Detailed Findings | Root cause, impact, and resolution for each FAIL |
| Summary | Severity breakdown, artifact-category pass rates, prioritised remediation order |

---

## Why This Spec Exists

### Because generation is not verification

SmartBuilder generates code from the task list's skeletons, constraint table, and inline DDL. It follows instructions; it does not check them. If an instruction is wrong — a constraint table row that inverts a requirement, a config key that a notebook references but the YAML omits — the generator produces a file that satisfies the task and violates the specification simultaneously, and nothing in the build pipeline detects it.

The validation step exists to make that class of error visible. It reads the generated file and the originating specification in the same pass, finds the discrepancy, and records it with enough detail that the fix is unambiguous.

### Because the build plan's acceptance gates are necessary but insufficient

Each phase ends with a gate — existence checks and structural assertions. The Phase 1 gate checks file count and header population; the Phase 3 gate checks test coverage scenarios. Those gates are mechanically executable against the codebase as soon as the phase completes. But they are gates, not reviews. They do not verify that a header's RULES field resolves to real dimensions, that a test's regex matches the notebook it is supposed to exercise, or that a config file contains the keys its notebook requires.

The validation report does those deeper checks, artifact by artifact, against the full specification chain.

### Because prior-run findings need a status update

The report treats iteration as first-class. F-001 from a prior validation run is tracked explicitly — it was a missing PRIMARY KEY in `bronze_lineage_run.sql`, it was fixed, and this report confirms it RESOLVED. That pattern matters because a validation report that does not distinguish new findings from carried-over ones creates noise for anyone who ran a previous round.

---

## Section 1 — Results Table

### What it contains

Twenty-seven rows: artifact path, generating task, Status (PASS or FAIL), and a one-line Findings note for anything that failed.

### Key facts captured

**The failure rate is 30% by row count, but the severity is uneven.** Eight rows are FAIL, but they represent two distinct problems: three are documentation-only inconsistencies (F-001, F-004, F-008), and one (F-003) is a runtime blocker that prevents the pipeline from executing at all.

**DDL is clean; notebooks and config are not.** Seven DDL files and one grants file all pass. Five shared-module Python files all pass. Of the three ETL notebooks, one (TASK-014) fails on a pattern deviation and one (TASK-015) fails on a missing config section. The config artifacts have a 0% pass rate — both fail, and their failures are the same underlying issue (F-003).

**The results table is a quick triage surface.** Looking at the Findings column, the words "stale" and "placeholder" appear repeatedly — signalling that several failures originate from the same root: artifacts generated from older templates or deferred sections. That pattern is more legible from the table than from the detailed findings.

**TASK-010 passes but its result is noted as unused elsewhere.** `src/common/scd2_merge.py` is marked PASS — the file exists, is well-formed, and matches its task description. The validation report does not flag unused modules. That gap is documented in `tasks-explained.md` (divergence 1) but is outside the scope of artifact-level validation.

**The row count of 27 does not match the 26 tasks.** `build-plan.md` itself is validated as row 27, with no task associated. That is the correct accounting — the build plan is a codebase artifact that can contain path errors, and this one does (F-001, F-008). Validating the planner against the plan's own output is what catches the grants-file path mismatch.

### Why this section matters

It is the entry point for anyone who wants to know the build's health before reading anything else. Status PASS or FAIL is the first thing a reviewer, a build coordinator, or an automated check reads. The detailed findings are for understanding; this table is for deciding.

---

## Section 2 — Prior-Run Finding Status

### What it contains

One entry: F-001 from a prior run, confirmed RESOLVED. `bronze_lineage_run.sql` was missing `CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)`. The current run finds the constraint present at line 23 and links it to Design §1.2.

### Key facts captured

**The finding was substantive, not cosmetic.** A missing PRIMARY KEY in a lineage table is not a style violation — `lineage_key` is the identity surrogate that all nine QA assertions write back to `bronze.dq_rejections`, and that TASK-016's lineage-close UPDATE uses as a predicate. Without it, the row is findable but the column carries no uniqueness guarantee at the database level. Delta does not enforce it, but the declaration is the spec's contract with Unity Catalog.

**Confirmation is explicit and specific.** The report does not just say "constraint added." It cites line 23 and quotes the constraint name (`pk_lineage_run`) against the design's intent. That level of detail is what separates a tracked resolution from a checkbox.

**This is the only entry in this section.** Prior runs produced one finding; the current run inherits one prior finding. In a longer iteration history, this section accumulates a resolution ledger — each row a proof that the validation loop is closing issues rather than accumulating them.

### Why this section matters

It establishes that the report is part of a sequence, not a one-shot snapshot. A reviewer who sees "CONFIRMED RESOLVED" on a prior finding knows that someone ran validation, fixed the issue, and re-ran — which is different from "we think it's fixed." The prior-run section is what makes the report auditable across iterations.

---

## Section 3 — Detailed Findings

### What it contains

Eight finding blocks, each with artifact path, severity, rule citation, finding description, root cause, impact, and resolution.

### Key facts captured

**F-001 (LOW) and F-008 (LOW) are the same defect expressed twice.**

Both concern the grants file. F-001 says the codebase layout tree in `build-plan.md` lists `src/db/ddl/grants.sql` when the actual file is `src/db/grants/purchase_grants.sql`. F-008 says the same thing in more detail, with both path errors identified: wrong directory (`ddl/` vs. `grants/`) and wrong filename (`grants.sql` vs. `purchase_grants.sql`). The two findings exist because the validator encountered the discrepancy in two places — the layout tree and the Phase 1 acceptance gate — and recorded each encounter separately. The fix is a single edit to `build-plan.md`, and both findings resolve together.

**F-002 (MEDIUM) is the runtime consequence of the build plan's most significant divergence.**

The build plan's Phase 2 constraint table instructed the generator to implement lineage-close as `spark.sql UPDATE` in the `except` block. NFR-009 requires a `close_lineage_record` helper call. The validator finds `nb_extract_watermark.py` using the direct UPDATE — consistent with the constraint table, contrary to the requirement. `src/common/lineage_helpers.py` exists and contains `close_lineage_record`, but no notebook imports it.

The finding is marked MEDIUM rather than HIGH because the functional outcome is correct: the lineage record is closed on both paths. What is wrong is the implementation pattern — it creates dead code, fails the named-function acceptance criterion, and makes a future change to the close mechanism require editing multiple notebooks instead of one module. The resolution offers a genuine choice: promote the inline pattern to the official one (low effort, no functional impact) or wire up the helper (higher effort, better maintainability). The report correctly presents both options rather than mandating either.

**F-003 (HIGH/CRITICAL) is the only finding that blocks the pipeline from running.**

`nb_extract_purchase.py` reads four JDBC config keys (`jdbc_driver`, `jdbc_user`, `jdbc_password`, `source_table`) from `config/environment.yaml`. Those keys do not exist in the config file. The notebook raises `KeyError: 'jdbc_driver'` before reaching any ETL logic.

The root cause is a coordination failure between two tasks. TASK-018 generated `environment.yaml` without a JDBC section because PD-001 (source JDBC connectivity) was pending. TASK-015 generated `nb_extract_purchase.py` with config key references to a section that was never written. Neither task was inconsistent with its own instructions, and neither detected the mismatch with the other.

The resolution is precise: add four placeholder keys under `purchase.etl` with `{{PLACEHOLDER}}` values. This unblocks the config load without resolving PD-001 — the notebook will still fail at the JDBC `.load()` call, but the failure will be the expected JDBC connectivity error rather than a Python `KeyError` on startup. The distinction matters: a `KeyError` before any ETL logic is a configuration gap; a JDBC connection error is the known pending decision.

**F-004 (LOW) is purely cosmetic, but its root cause is revealing.**

`nightly_etl_purchase.json` uses `silver_fact.fact_purchase_order` in a task description string. The correct name is `silver_fact.fact_purchase`. No functional behavior is affected — the description is shown in the Databricks Jobs UI but not parsed by the workflow engine. The root cause is a carry-forward from an earlier draft or template.

The same stale name appears across F-004, F-006, and F-007. Its persistence across three artifacts (workflow JSON, codebase design doc, MERGE example) suggests it was present in the source template for `docs/design.md` and was never systematically replaced — which is consistent with F-006's finding that `docs/design.md` was generated from an entirely wrong version of the schema.

**F-005 (MEDIUM) is a false-confidence finding: the test passes but does not validate the right artifact.**

`test_migrate_staged_purchase_data.py` contains a `run_qa_p001` helper that raises `RuntimeError("Row count mismatch: staging={n}, inserted={n}")`. The test asserts against that message with regex `inserted=\d+`. The test passes.

The actual notebook, `migrate_staged_purchase_data.py`, raises `RuntimeError("QA-P001 FAILED — Row count mismatch: staging={n}, inserted/updated={n}")`. The regex `inserted=\d+` does not match `inserted/updated=\d+` because of the forward slash.

Two independent things are wrong. First, the regex is too narrow — `inserted=` does not match `inserted/updated=`. Second, the test is asserting against its own local helper, not the notebook. Both failures are hidden because the local helper's simpler message happens to satisfy the simpler regex. A reviewer running the test sees a green result and incorrect confidence.

The fix is a two-line change: update the helper's message to match the notebook, and update the regex to match the notebook's format. The Phase 3 acceptance gate ("TASK-022 covers the RuntimeError injection path") passes either way, because the gate checks that a case exists — not that the case exercises the right code.

**F-006 (MEDIUM) and F-007 (MEDIUM) share a root cause and a resolution.**

`docs/design.md` — the codebase design document generated by TASK-025 — was generated from a template describing a different version of the Purchase product. Its architecture diagram, layer responsibility table, and MERGE INTO example use eight table names, none of which match the actual DDL. `stg_purchase_order` instead of `purchase_staging`; `fact_purchase_order` instead of `fact_purchase`; `dim_package` and `dim_date`, which do not exist as Purchase product tables at all.

F-007 is the MERGE INTO example specifically: it references columns that do not exist in `silver_fact.fact_purchase` and omits six columns that do. The finding is split from F-006 because the column-level error requires its own evidence (the DDL vs. the MERGE example column by column), but the resolution is the same: regenerate `docs/design.md` using the finalized DDL artifacts as the naming source.

Both findings are MEDIUM rather than HIGH because `docs/design.md` is documentation, not executable code. Nothing in the pipeline reads it. But a wrong architecture diagram is actively harmful — an engineer using it as a reference for queries against `silver_fact.fact_purchase` will fail on every column reference.

### Why this section matters

The detailed findings section is where validation earns its place in the chain. The results table flags failures; this section explains them. The distinction between F-003 (blocks the pipeline) and F-004 (cosmetic string in a JSON comment) is not in the results table. The resolution for F-002 is not "fix the code" but "decide which mechanism is canonical." Those judgements live here.

---

## Section 4 — Summary

### What it contains

Three subsections: a severity breakdown table, an artifact-category pass/fail table, and a prioritised remediation order.

### Key facts captured

**The severity breakdown reveals the distribution clearly.** One CRITICAL/HIGH (F-003), three MEDIUM (F-002, F-005, F-006+F-007 counted together), two LOW (F-001+F-008, F-004). The CRITICAL finding is singular and unambiguous: it blocks execution. The MEDIUM findings all require a decision: which lineage-close pattern is canonical, which test message format is authoritative, how to regenerate a stale document. The LOW findings are documentation corrections with no functional impact.

**The artifact-category table shows a clean DDL/grants/shared-module block.** Eight artifacts (7 DDL + 1 grants), five shared modules (constants, scd2_merge, sk_resolver, fact_merge, udfs): all 13 pass. The failures cluster in the notebook/config interface and in the generated documentation. DDL is the most mechanically specified layer — inline SQL in the task list, column-for-column acceptance checks — and it shows. The notebook and config layers have the most specification gaps (PD-001, the missing module tasks) and they fail.

**The prioritised remediation order is actionable and correctly ranked.** F-003 is first because it is the only finding that prevents end-to-end execution. F-006+F-007 are second because a wrong architecture document is a reliability hazard for anyone operating the system. F-005 is third because false-green tests erode the value of the test suite. F-002 is fourth — no functional risk, but unresolved pattern drift. F-004 and F-001+F-008 are last: cosmetic, no execution impact.

The report correctly bundles F-001 and F-008 in the same remediation step and F-006 and F-007 in the same step. Both pairs are single-location fixes: one `build-plan.md` edit, one `docs/design.md` regeneration.

**The prior-run finding table closes the loop.** F-001 (prior run) — missing PRIMARY KEY — RESOLVED PASS. It appears here as confirmation that the most recent fix cycle closed what it was supposed to close. With F-001 resolved and F-003 as the new top priority, the remediation roadmap for the next cycle is clear.

### Why this section matters

The summary is the go-to-meeting artifact. The detailed findings section requires reading the full report; the summary section provides the brief. Severity breakdown, pass rate by category, and a numbered remediation order are enough to scope a fix sprint, assign ownership by artifact type, and set the agenda for a status review.

---

## Divergences and Open Items

### 1. F-003 was discoverable from the specifications and was not caught before generation

PD-001 is registered in `build-plan.md` as a pending decision blocking TASK-015. The build plan's prerequisite check table includes "Source JDBC connectivity (PD-001 pending) — Confirm connection profile before TASK-015 extract is run." Despite this, TASK-018 was generated without a JDBC section and TASK-015 was generated referencing config keys that TASK-018 does not define.

The validation step is the first artifact that treats this as a defect rather than a pending item. The distinction is consequential: PD-001 is a pending *decision* (which driver, which credentials), but the config structure is not pending — a JDBC section with placeholder values could have been generated immediately, as the remediation confirms. The build plan identified the right gap (PD-001) and drew the wrong boundary around it, treating the entire JDBC section as blocked when only the credential values were unknown. **The resolution requires updating both TASK-018's required YAML content and `build-plan.md`'s pending-decision description to distinguish configuration structure (generatable now) from configuration values (pending PD-001).**

### 2. The validator does not check whether passing artifacts are used

`src/common/scd2_merge.py` (TASK-010) is PASS. `src/common/lineage_helpers.py` — generated by SmartBuilder beyond the task list — is not in the results table at all (no task produced it). Neither artifact is imported by any notebook in the codebase. The validator checks whether an artifact matches its specification; it does not check whether any other artifact references it.

This is a reasonable scope boundary for a per-artifact validator. But the consequence is that dead code — `scd2_merge.py`, `lineage_helpers.py` — passes validation and accumulates without signal. The gap is documented in `tasks-explained.md` (divergence 1) and `build-plan-explained.md` (dependency graph section). **A cross-artifact reference check — "which modules are imported by which notebooks" — would catch this class of issue and belongs either in the validator or in a separate static analysis step.**

### 3. F-005 exposes a gap in the Phase 3 acceptance gate

The Phase 3 gate requires that TASK-022 "cover the `RuntimeError` injection path." TASK-022 does contain a test case that raises a `RuntimeError`. The gate passes. But the test's regex does not match the notebook it is testing.

The gate is checking *existence* of a test case, not *correctness* of the test. A gate that checked "the test case imports `migrate_staged_purchase_data` and invokes it" rather than "a test case exists" would have caught F-005 at the gate level, before validation. **Phase 3's gate could be strengthened with one import-check assertion without adding significant complexity.**

### 4. F-006 and F-007 reveal that the codebase design doc is a second-class artifact

`docs/design.md` (TASK-025) failed completely — eight wrong table names, wrong columns in the MERGE example, a phantom dimension. The root cause is that it was generated from a stale template. But the deeper structural issue is that TASK-025 generates a document *about* the codebase rather than generating codebase code, and its input is described in the task skeleton rather than derived from the DDL artifacts that were already generated by the time TASK-025 runs.

In Phase 3, the DDL, shared modules, notebooks, and config are all complete. TASK-025 could read those artifacts and derive the correct table names, column lists, and MERGE example directly. Instead, it relies on the task description's references to `design.md` and `requirements.md` upstream specs. When those upstream specs carry a stale name (F-004 shows `fact_purchase_order` propagating from the source template), the codebase doc inherits the error. **TASK-025 should be generated last in Phase 3 and should explicitly reference the DDL files and ETL modules as its source of truth for names, not the upstream design spec.**

### 5. Two findings (F-002, F-005) point at the same unresolved mechanism question

F-002 is about the lineage-close pattern: `spark.sql UPDATE` inline vs. `close_lineage_record` helper. F-005 is about the test for that same mechanism: the Phase 3 gate checks for `close_lineage_record(succeeded=False)` call verification, but the code uses inline SQL.

Both findings are symptoms of the same unresolved decision that `build-plan-explained.md` identified as its first and most consequential divergence: the Phase 2 constraint table instructed the generator to inline the SQL, the Phase 3 gate checked for the function call, and neither document detected the contradiction. The validation report surfaces both consequences separately, but resolving them requires a single upstream fix: choose one mechanism, update NFR-009 and the Phase 2 constraint table to agree, and re-run the Phase 3 gate. As long as the constraint table and the gate disagree, F-002 and F-005 will reappear in every validation cycle. **These two findings should be treated as one resolution item, not two.**

---

## How This Report Is Used Downstream

| Consumer | What it takes from the validation report |
|---|---|
| **Build operator** | The prioritised remediation order — what to fix first and why |
| **`build-plan.md`** | F-001 and F-008 identify path corrections; the report is the evidence for that update |
| **`config/environment.yaml`** | F-003's resolution adds four JDBC placeholder keys |
| **`tests/etl/test_migrate_staged_purchase_data.py`** | F-005's resolution fixes the `run_qa_p001` helper and the regex |
| **`docs/design.md`** | F-006 and F-007 require regeneration from correct DDL source |
| **Next validation run** | Current findings F-002 through F-008 become prior-run findings; each must appear in the Prior-Run Finding Status section with RESOLVED or CARRIED OVER |
| **Project retrospective** | F-003 and the TASK-010 dead-code gap feed back to `tasks.md` as missing tasks (JDBC placeholder task, deletion of spurious SCD-2 module task) |

---

## File Reference

| File | Location |
|---|---|
| `validation-report.md` | `products/Purchase/current/codebase/validation-report.md` |
| `build-plan.md` | `products/Purchase/current/codebase/build-plan.md` — the artifact validated as row 27; contains the path errors in F-001 and F-008 |
| `tasks.md` | `products/Purchase/current/specifications/development_plan/tasks.md` — the 26-task list whose output this report checks |
| `design.md` (spec) | `products/Purchase/current/specifications/development_plan/design.md` — the authoritative naming source for F-006 and F-007 |
| `docs/design.md` (codebase) | `products/Purchase/current/codebase/docs/design.md` — the stale document in F-006 and F-007 |
| `config/environment.yaml` | `products/Purchase/current/codebase/config/environment.yaml` — the config file missing the JDBC section in F-003 |
| `src/etl/nb_extract_purchase.py` | `products/Purchase/current/codebase/src/etl/nb_extract_purchase.py` — the notebook with broken config references in F-003 |
| `src/etl/nb_extract_watermark.py` | `products/Purchase/current/codebase/src/etl/nb_extract_watermark.py` — the notebook with the inline lineage-close pattern in F-002 |
| `tests/etl/test_migrate_staged_purchase_data.py` | `products/Purchase/current/codebase/tests/etl/test_migrate_staged_purchase_data.py` — the test file with the false-green regex in F-005 |
| `_manifest.yaml` | `products/Purchase/current/_manifest.yaml` — per-task status; the generated-artifact list confirms the grants file path that F-001 and F-008 correct |

The report is 397 lines across four sections. Its length is determined almost entirely by Section 3 — the eight detailed findings — which runs to roughly 300 lines because each finding reproduces enough evidence (code blocks, column lists, line numbers) to make the defect unambiguous and the fix unambiguous. A validation report that named the problem without showing it would require a reader to re-examine the artifacts themselves. Here, the report is the examination.
