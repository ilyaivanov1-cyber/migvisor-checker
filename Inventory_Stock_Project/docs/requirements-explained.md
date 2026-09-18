# Requirements — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `development_plan/product-definition.yaml` (ODPS 4.1)
**Implemented by:** `development_plan/design.md`
**Contents:** 3 sections | 11 functional + 12 non-functional + 9 data quality = **32 requirements**
**Priority split:** 26 must-have | 6 should-have

---

## What This Spec Is

The requirements document is the **acceptance contract**. It states what must be true when the Purchase product is finished, in a form that can be checked — each requirement is a numbered row with a testable acceptance criterion and a traceable source.

It is the second of four development-plan artifacts, and its position defines its job:

| Artifact | Question it answers |
|---|---|
| `product-definition.yaml` | What is this product, in ODPS terms? |
| **`requirements.md`** | **What** must be true when we are done? |
| `design.md` | How is that achieved? |
| `tasks.md` | In what order do we build it? |

It has 3 sections, all of them tables with the same six columns:

| Column | Purpose |
|---|---|
| **ID** | Stable identifier (`FR-nnn`, `NFR-nnn`, `DQR-nnn`) cited by design, tasks, tests, and validation |
| **Title** | One-line handle |
| **Description** | What must be true |
| **Priority** | `must-have` or `should-have` — the scope-cut instruction |
| **Acceptance Criterion** | How you would know it is true |
| **Source** | Where in the ODPS definition (or which rule) this came from |

The three sections are:

1. **Functional Requirements** (11) — what the pipeline does
2. **Non-Functional Requirements** (12) — how well it does it, and how the code must be shaped
3. **Data Quality Requirements** (9) — what must be true of the data itself

Think of it as the **test plan written before the code**. Every row is something a reviewer can pass or fail.

---

## Why This Spec Exists

### Because the ODPS definition declares policy, not tests

`product-definition.yaml` is a machine-readable product declaration. Its data quality block says, for the completeness dimension:

```yaml
- dimension: completeness
  target: inventory_stock.silver_fact.fact_purchase
  strategy: zero_tolerance
  blocking: true
```

That is a policy. It does not say what to compare against what, what error to raise, what the message should be, whether the Workflow task fails, or what happens to the lineage record. NFR-003 supplies all of it: staging count versus rows merged, a `RuntimeError` with the exact message `Row count mismatch: staging=N, inserted=M`, the task marked FAILED, and `lineage_run.was_successful = false`.

The same expansion happens across every ODPS block. `SLA / latency: 4 hours` becomes NFR-001's "complete before 06:00 UTC, verified against `lineage_run.data_load_completed`." `x-inputPorts / supplier_dimension` becomes FR-004's temporal range join. The requirements document is where declarations become obligations.

### Because acceptance criteria are where ambiguity dies

The Description column says what must be true. The Acceptance Criterion column says how you would know — and the criteria in this document are unusually strong, because many of them are written as **negative tests** rather than happy-path checks:

- NFR-003: "*Injecting a mismatch* between staging count and rows_merged causes the Workflow task to FAIL with…"
- NFR-004: "*After a load containing one invalid* `supplier_key`: a rejection row is present in…"
- NFR-005: "*After loading one fact row with a non-zero* `supplier_key` *absent from* `silver_dim.supplier`…"
- NFR-006: "*Inserting one row with* `ordered_outers = -1` produces WARNING…"
- NFR-008: "the same principal *receives* `PERMISSION_DENIED` *on* `bronze.purchase_staging`"

This is what makes the non-blocking requirements testable at all. A data quality check that is designed never to fail the pipeline is invisible when the data is clean — a check that logs a warning and a check that was never implemented look identical on a good night. By specifying the violation to inject and the exact log line to expect, the criteria turn absence-of-evidence into a real assertion. The same logic applies to NFR-008: verifying that access is *denied* matters as much as verifying it is granted, and only the negative form catches an over-broad GRANT.

### Because priority is an instruction about what to cut

Twenty-six requirements are must-have, six are should-have. The six are worth listing, because they form a coherent set:

| Should-have | Why it is not must-have |
|---|---|
| FR-008 — conditional OPTIMIZE | Performance optimization; the data is correct without it |
| NFR-002 — SQL Warehouse ≥ 99.5% uptime | Platform-level availability the product does not control |
| NFR-012 — retention (7 years / 90 days) | Governance configuration, not pipeline behaviour |
| DQR-005 — quantity non-negativity | Warning-level data condition |
| DQR-006 — date key within batch window | Warning-level data condition |
| DQR-007 — package non-null | Warning-level data condition |

Nothing that affects the **correctness or traceability** of the data is should-have. The must-have set is exactly "the pipeline produces correct, complete, lineage-stamped data"; the should-have set is "it does so efficiently, stays up, and warns about soft anomalies." That is a defensible line, and it means a scope cut under schedule pressure has an obvious first target.

One subtlety that looks like an inconsistency and is not: NFR-006 (implement the three business-rule assertions) is **must-have**, while DQR-005/006/007 (the data actually satisfying those three rules) are **should-have**. That split is deliberate. Building the check is mandatory; the data passing it cleanly is an aspiration, because the source data is not under this product's control. Confusing the two would either make the checks optional or make dirty upstream data a release blocker.

---

## Section 1 — Functional Requirements

### What it contains

Eleven requirements, presented as a flat list. They group naturally by pipeline stage:

| Stage | Requirements |
|---|---|
| Extract and run control | FR-001 staging overwrite, FR-002 watermark window, FR-003 lineage key propagation |
| Key resolution | FR-004 supplier SK, FR-005 stock item SK, FR-006 date key |
| Load | FR-007 fact MERGE, FR-008 conditional OPTIMIZE |
| Environment and delivery | FR-009 config externalisation, FR-010 SQL Warehouse delivery, FR-011 reseed notebook |

### Key facts captured

**FR-001 is a regression requirement, not a feature requirement.** It mandates that `bronze.purchase_staging` be written in OVERWRITE mode *before any transformation begins*, and its acceptance criterion tests for the **absence** of prior-run rows: "no rows from a prior run are present," verified via `_extracted_at_utc`. This is the direct remedy for the legacy SSIS defect where the truncate step cleared `Integration.Order_Staging` instead of `Purchase_Staging`, leaving stale rows to be reprocessed. Almost every other FR asserts that something new works; FR-001 asserts that something old is gone.

**FR-002 fixes the extract window bounds and is the only place the watermark advance is mandated.** The window is `last_modified_when > last_cutoff AND <= current_cutoff` — exclusive lower bound, inclusive upper. The asymmetry is what makes consecutive runs neither skip nor duplicate a row. Note carefully where the *advance* lives: the Description says only that the boundaries are **read** from `bronze.etl_cutoff` at job start. The obligation to **write** the new cutoff appears only in the Acceptance Criterion ("After each successful run, `bronze.etl_cutoff` is updated to the current run's cutoff timestamp"). That placement matters — see the divergences below.

**FR-003 names an API, which requirements usually avoid.** It specifies `dbutils.jobs.taskValues.set(key="lineage_key")` and `.get` by name. Naming a mechanism in a requirement is normally a design intrusion, but it is justified here: the lineage key is generated by an IDENTITY insert in one Workflow task and must be consumed by separate tasks running in separate processes. There is no in-band channel — no shared variable, no return value — so the transport *is* the requirement. Its acceptance criterion is a three-table invariant: the same `lineage_key` on every row in `fact_purchase`, `purchase_staging`, and `dq_rejections`, with exactly one matching record in `lineage_run`.

**FR-004 and FR-005 are deliberate twins, joined by reference.** FR-005 does not restate the join logic; it says "using the same temporal range join pattern as FR-004." That is DRY applied to specification: the two surrogate keys cannot drift apart, because there is only one description of how resolution works. Both criteria have the same three parts — (a) matched rows get a non-zero key, (b) unmatched rows get 0, (c) **no row gets NULL**. Part (c) is the one that catches a broken `COALESCE`: without it, a resolution failure could pass (a) and (b) while leaving nulls that only surface as a NOT NULL violation in the fact table.

**FR-006 settles `date_key` as a DATE.** It must match `silver_dim.date.date`, a DATE column. This is the requirement that overrides the product brief's project-wide "integer YYYYMMDD, not a DATE column" convention, and it is correct to do so — the source derives `CAST(po.OrderDate AS date)`, so the business key genuinely is a date.

**FR-007 specifies the MERGE, and contains the chain's most consequential error.** It requires a Spark SQL `MERGE INTO` "keyed on `wwi_purchase_order_id`" — a single column, at a grain the design itself describes as one row per purchase **order line**. It also defines idempotency oddly: "idempotent for the same `wwi_purchase_order_id` and `lineage_key` combination." Since `lineage_key` is new on every run, idempotency defined against it is vacuous. The usable form is in the acceptance criterion — "running the MERGE twice with the same staging input produces the same row count." Both issues are treated below.

**FR-008 externalises its own threshold.** OPTIMIZE runs only when `rows_merged > 10,000`, and the threshold must be read from `config/environment.yaml` at `purchase.etl.fact_optimize_row_threshold`. The requirement states both the value and its location, and its acceptance criterion covers both branches — OPTIMIZE runs and logs above the threshold, and is **skipped with no log entry** below it. Testing the negative branch prevents a "threshold" that is really an unconditional OPTIMIZE.

**FR-009 is the only statically checkable functional requirement.** Its criterion is a lint rule: "static scan of `src/etl/` finds zero hard-coded ISO date literals." No data, no run, no cluster — it can be evaluated on the generated source tree alone. That makes it the cheapest requirement in the document to verify and the easiest to enforce in CI.

**FR-010 carries a cross-product dependency.** Both Power BI reports must connect to the SQL Warehouse with updated target-schema references. One of them, `wwidw_purchase_and_sale_per_stockitem_dynamic`, also reads `silver_fact.fact_sale`, which belongs to the Sales_Orders product. This requirement therefore cannot be fully satisfied by the Purchase product alone — it needs a coordinated cutover, which is why it appears in the product scope as a migration risk.

**FR-011 is the only destructive requirement, and it is gated on a human decision.** `reseed_purchase_environment.py` creates tables, inserts the `key=0` sentinel rows, and **resets** `bronze.etl_cutoff` to the configured initial load date. That last action rewinds the watermark and causes a full re-extract. Accordingly, the requirement states that execution "requires explicit scope-owner sign-off (PD-002)." A requirement whose satisfaction is conditional on an approval is unusual, and correct here.

### Why this section matters

The functional requirements are the spine that `design.md` hangs structures on and `tasks.md` hangs work on. Each FR maps to design elements almost one-to-one — FR-004 becomes CALC-002, FR-002 becomes §2.2, FR-007 becomes §3.3 — which is what makes the trace auditable in both directions: every design element should answer to a requirement, and every requirement should appear in the design. Where that correspondence breaks (FR-002's watermark write), something has been lost.

---

## Section 2 — Non-Functional Requirements

### What it contains

Twelve requirements in three distinct groups, though the document does not label them:

| Group | Requirements | Derived from |
|---|---|---|
| Service levels | NFR-001 freshness, NFR-002 uptime, NFR-012 retention | ODPS `SLA` block |
| Data quality mechanism | NFR-003 – NFR-007 | ODPS `dataQuality` block |
| Governance | NFR-008 access control | (see divergences) |
| Code conformance | NFR-009 notebook skeleton, NFR-010 DDL header, NFR-011 layout | Product rules CX-P005, CX-P006, CX-P004 |

### Key facts captured

**NFR-003 through NFR-007 are the mechanism half of the data quality story.** They are classified as non-functional, but they read as behavioural specifications: what runs, when, where violations go, whether the pipeline stops, and what the log line says. Section 3 then states the same rules as *data conditions*. The relationship is worth laying out explicitly, because it is the easiest thing in this document to mistake for duplication:

| Rule | Mechanism (NFR) | Data condition (DQR) | Blocking |
|---|---|---|---|
| QA-P001 row count reconciliation | NFR-003 | DQR-001 | **Yes** |
| QA-P002 orphaned SK detection | NFR-005 | *(none)* | No |
| QA-P003 referential integrity | NFR-004 | DQR-002, DQR-003, DQR-004 | No |
| QA-P004 business rule assertions | NFR-006 | DQR-005, DQR-006, DQR-007 | No |
| QA-P005 centralised rejection store | NFR-007 | DQR-008 | No |

The asymmetry is the proof that the two sections are genuinely different views rather than a copy: **QA-P002 has an NFR but no DQR.** Orphan detection is purely informational — it counts and logs, and there is no data condition being asserted, so there is nothing for a DQR to state. If the sections were duplicates, every row would pair.

**Exactly one check blocks.** NFR-003's row count reconciliation is the only requirement in the document that can fail a run. Everything else logs, rejects, or warns. That is a deliberate and defensible design: a count mismatch means data was lost or duplicated in transit and downstream numbers would be wrong, whereas an RI violation means one dimension lookup missed — bad, but recoverable and traceable through `dq_rejections`. One blocking check is a healthy ratio; a pipeline where every check blocks does not run at night.

**NFR-009 is what makes a failed run distinguishable from a crashed run.** It requires the six-section notebook skeleton, and specifically that `close_lineage_record` appear in **both** the success path and the `except` block. Its acceptance criterion tests this by injecting an exception and verifying `close_lineage_record(spark, lineage_key, rows_merged=0, succeeded=False)` is called. This is why `lineage_run.was_successful` is three-valued — `NULL` while running, `true` on success, `false` on handled failure. Without the `except`-path close, a crash would leave `NULL` forever, and an operator could not tell a currently-running job from one that died. The three-valued column only carries information if this requirement holds.

**NFR-010's acceptance criterion is literally two shell commands.** One `grep -l` to confirm every DDL file has the header block, one `grep -c` to confirm no `RULES` field is empty. It is the most directly executable criterion in the document, and the empty-`RULES` check is the interesting half: it enforces that every generated file records *which rules produced it*, which is what keeps the rule trace intact all the way down into the emitted SQL.

**NFR-011 pins the codebase layout and the four shared modules.** `constants.py`, `scd2_merge.py`, `sk_resolver.py`, `fact_merge.py` must all exist. Naming the modules in a requirement — rather than leaving it to the design — makes the shared-code boundary non-negotiable, which is what prevents the SCD-2 and SK-resolution logic from being re-implemented inline per notebook.

**NFR-012's bronze retention silently bounds DQR-008's promise.** Bronze tables are retained 90 days; silver for 7 years. DQR-008 justifies the `lineage_key` on rejection rows as enabling "surgical investigation and **batch replay**." Replay requires the staging rows, which live in bronze. So replay is possible for 90 days, and investigation of anything older is limited to whatever the rejection rows themselves recorded. Neither requirement states this interaction; it falls out of reading them together, and it is the kind of thing worth writing into the runbook.

**NFR-001 makes the SLA measurable against a real column.** The 4-hour latency budget (02:00 start, 06:00 UTC deadline) is verified against `lineage_run.data_load_completed`, not against a monitoring dashboard. The lineage table is doing double duty as the SLA evidence store, which is only sound because NFR-009 guarantees the record always gets closed.

### Why this section matters

Three of these requirements — NFR-009, NFR-010, NFR-011 — are the only place the product's *custom* rules (CX-P004, CX-P005, CX-P006) become checkable. Transformation rules are guidance; they do not have acceptance criteria. Turning three of them into requirements with grep-able criteria is what makes the difference between a convention nobody verifies and one that fails a build.

---

## Section 3 — Data Quality Requirements

### What it contains

Nine requirements stating what must be true of the data, each traced to a `QA-P00x` product rule:

| ID | Condition | Rule | Priority |
|---|---|---|---|
| DQR-001 | Inserted count == staging count, zero tolerance | QA-P001 | must-have |
| DQR-002 | Every non-zero `supplier_key` exists in `silver_dim.supplier` | QA-P003 | must-have |
| DQR-003 | Every non-zero `stock_item_key` exists in `silver_dim.stock_item` | QA-P003 | must-have |
| DQR-004 | Every `date_key` exists in `silver_dim.date` | QA-P003 | must-have |
| DQR-005 | `ordered_outers`, `ordered_quantity` ≥ 0 | QA-P004 | should-have |
| DQR-006 | `date_key` within the batch window | QA-P004 | should-have |
| DQR-007 | `package` non-null and non-empty | QA-P004 | should-have |
| DQR-008 | Every rejection row carries its run's `lineage_key` | QA-P005 | must-have |
| DQR-009 | No NULL `supplier_key` / `stock_item_key` after resolution | FR-004 + FR-005 | must-have |

### Key facts captured

**The three RI checks are split per FK column rather than bundled.** DQR-002, DQR-003, and DQR-004 all implement QA-P003 and could have been one requirement about "all three FK columns." Splitting them means each produces its own rejection rows with its own `violation_column`, which is what makes per-column triage possible: "supplier resolution is broken tonight" is a different incident from "the calendar is missing 2027." A bundled check would report a single count and lose that distinction.

**"Non-zero" is doing essential work in DQR-002 and DQR-003.** The sentinel `key = 0` rows exist precisely to absorb unresolvable references, so a `supplier_key` of 0 is a *successful* outcome of FR-004, not an RI violation. Excluding zero from the check is what prevents the sentinel design from generating a rejection row for every unmatched source row — which would fill `dq_rejections` with expected outcomes and make it useless as a signal.

**DQR-004 checks against a different column name than it is keyed on.** `date_key` in the fact table joins to `silver_dim.date.date`. The FK column and the PK column have different names — a consequence of the naming rules applying to the fact's role-named FK and the dimension's natural PK separately. Worth noting because it is the one FK in the model where a generator cannot infer the join by matching column names.

**DQR-009 is the only requirement sourced from other requirements.** Its Source column reads `x-inputPorts / supplier_dimension + stock_item_dimension / FR-004 + FR-005`. It states a guarantee that *follows* from FR-004 and FR-005 rather than one imposed from the ODPS definition — every staging row has a non-null supplier and stock item key, because resolution either matches or defaults to 0. Restating a derived property as its own requirement is not redundancy: it is the single assertion (`COUNT(*) WHERE supplier_key IS NULL OR stock_item_key IS NULL` returns 0) that catches either twin failing, and it can be checked on `bronze.purchase_staging` *before* the MERGE, where a NOT NULL violation would otherwise be discovered late.

**DQR-006's bounds are derived, not configured.** `batch_date_min` and `batch_date_max` come from the extract watermark, so the check tightens automatically with the extract window rather than being pinned to a static range that would need maintaining. This is also the only DQ rule whose thresholds change every run.

### Why this section matters

This section is what `validation.md` and the generated test suite read. The NFRs describe code that must exist; the DQRs describe conditions a query can evaluate against loaded data. That makes them the only requirements verifiable **after deployment, against production data**, on every run — the rest are verified once, at build time.

---

## Divergences and Open Items

Five items, in descending order of consequence.

### 1. FR-007's MERGE key is one column at a multi-column grain

FR-007 requires the MERGE to be "keyed on `wwi_purchase_order_id`." The fact grain is one row per purchase **order line** — the as-is extract JOINs `Purchasing.PurchaseOrderLines`, so a single purchase order contributes one row per stock item. `wwi_purchase_order_id` is therefore not unique at the fact grain, and `to-be.md` specifies a four-column composite (`wwi_purchase_order_id`, `date_key`, `supplier_key`, `stock_item_key`).

`design.md` §3.3 carries FR-007's single-column key forward, so the requirement and the design agree with each other and disagree with the to-be. A Delta MERGE that matches multiple source rows to one target row raises an error rather than choosing one, so this fails loudly at first run — but it blocks the pipeline, and it makes FR-007's own idempotency criterion untestable.

The likely origin is the legacy pattern: `DELETE … WHERE [WWI Purchase Order ID] IN (SELECT …)` followed by a bulk insert, an *order-level* replacement where the order ID alone was the right predicate. The to-be converted that to an order-line-grain MERGE correctly; FR-007 appears to have kept the delete predicate. **The to-be's four-column key looks correct, and FR-007 and design §3.3 should both be reconciled to it before code generation.**

Related and smaller: FR-007's phrase "idempotent for the same `wwi_purchase_order_id` and `lineage_key` combination" is vacuous, because `lineage_key` is unique per run — no two runs ever share one. The acceptance criterion states the meaningful property (same staging input, same resulting row count) and should be treated as the definition.

### 2. FR-002's watermark advance exists only in its acceptance criterion

The obligation to update `bronze.etl_cutoff` after a successful run appears **only** in FR-002's Acceptance Criterion column. The Description says the boundaries are *read* at job start and stops there. `design.md` computes `current_cutoff` in §2.2 but never commits it — it is absent from §3.1's calculations and from §5.4's task description. The only place in the chain that specifies the write is `to-be.md` step 21 (`set_etl_cutoff(spark, "fact_purchase", new_cutoff)`).

This matters because of *where* the requirement lives. Acceptance criteria are read by reviewers and test authors; descriptions are read by generators. A generator working from FR-002's description and the design would build a pipeline that re-extracts the same window every night, and FR-002's criterion would fail on the second run. The watermark write should be promoted into FR-002's Description and into design §3.1.

### 3. No requirement specifies the inbound extract from SQL Server

This is the largest gap by scope, and it is structural rather than an error in any single row.

Every input in this document is already a Delta table. `product-definition.yaml` lists five `x-inputPorts` — `purchase_staging`, three `silver_dim` tables, and `etl_cutoff` — all `inputType: delta_table`. There is no SQL Server input port. FR-001 consumes `bronze.purchase_staging`; FR-002 extracts "rows from the upstream source" without naming SQL Server, JDBC, a driver, credentials, or a secret scope. `design.md` §2.1 labels its first input "`bronze.purchase_staging` (from upstream extract)" — the extract itself is a black box outside the specified boundary.

So the step that actually reads `wideworldimportersdw` is un-required and un-designed. The consequences are visible downstream: PD-001 (source JDBC connectivity) is registered as a pending decision in `codebase/build-plan.md`, not in any requirement, and the validation report records `nb_extract_purchase.py` referencing a config section that `environment.yaml` does not contain — because the notebook was generated with JDBC key references while the config was generated without a JDBC block. Neither artifact was wrong relative to the requirements; the requirements simply did not cover the seam.

Two other pending decisions, PD-002 and PD-003, *are* referenced from requirements. PD-001 — the one that gates the pipeline reading any source data at all — is not. Adding a functional requirement for the source extract, with the connection profile and secret handling named, would close this.

### 4. Two must-have requirements cannot be fully satisfied yet, and their blockers are defined downstream

FR-011 depends on PD-002 (scope-owner sign-off for the reseed notebook). NFR-008 depends on PD-003 (the Unity Catalog access role matrix). Both are must-have, and both say so plainly in their Description — which is good practice.

The trace, however, runs the wrong way. `PD-002` and `PD-003` are only *defined* in `codebase/build-plan.md`, an artifact generated later in the chain. A reader of `requirements.md` alone cannot resolve either identifier: there is no pending-decision register in `development_plan/`. The IDs are stable across the chain, which is what matters most, but the register should live at or above the level of the first document that cites it.

### 5. NFR-007's column count, and a column name that does not exist

Two small ones in the DQ requirements, both worth catching in review:

- **NFR-007** says every rejection row must include "all nine required columns," then lists ten (`rejection_id`, `lineage_key`, `rule_id`, `source_table`, `pk_column`, `pk_value`, `violation_column`, `violation_value`, `rejection_reason`, `detected_at`). The design's schema has ten. The count is wrong; the list is right.
- **NFR-004**'s acceptance criterion expects a rejection row with `fk_column = 'supplier_key'`. There is no `fk_column` in `bronze.dq_rejections` — the equivalent is `violation_column`. A test written literally from this criterion would not compile against the generated schema.

---

## How This Spec Is Used Downstream

| Consumer | What it takes from the requirements |
|---|---|
| **`design.md`** | Each FR becomes a concrete structure — FR-004 → CALC-002, FR-002 → §2.2, FR-007 → §3.3, NFR-003–007 → §5.1's nine validation rules |
| **`tasks.md`** | Requirement IDs become the per-task "satisfies" trace, so no task exists without a requirement behind it |
| **Generated tests** | Acceptance criteria become test cases directly — especially the injection-style NFR criteria and the DQR assertions |
| **SmartBuilder `generate-etl`** | NFR-009's six-section skeleton is the notebook template; FR-009 forbids inline literals |
| **SmartBuilder `generate-db`** | NFR-010's header block is prepended to every DDL file, with the RULES field populated |
| **`config/environment.yaml`** | FR-008's threshold path, FR-009's externalised date and business parameters, FR-011's `initial_load_date` |
| **`validation-report.md`** | Validates generated artifacts requirement by requirement; unresolved divergences above surface here |
| **`runbook.md`** | NFR-003's blocking failure becomes an incident procedure; the PD items become the go-live checklist |
| **Sign-off** | The 32 rows are the acceptance checklist the scope owner signs against |

---

## File Reference

| File | Location |
|---|---|
| `requirements.md` | `products/Purchase/current/specifications/development_plan/requirements.md` |
| `product-definition.yaml` | same directory — the ODPS 4.1 definition these requirements were derived from |
| `design.md` | same directory — the design that implements them |
| `tasks.md` | same directory — the build order, traced back to these IDs |
| `build-plan.md` | `products/Purchase/current/codebase/build-plan.md` — where PD-001/002/003 are defined |

61 lines and three tables. The line count is misleading: each requirement is a single dense table row, and the document is best read as 32 self-contained records rather than as prose. That structure is deliberate — a requirement that depends on its neighbours for meaning cannot be cited by ID from a design document, a task, or a test, and citation by ID is the whole point.
