# Product Definition — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Standard:** Open Data Product Specification (ODPS) 4.1
**Files:** `product-definition.yaml` (225 lines, authoritative) + `product-definition.md` (53 lines, `emit-md` companion)
**Derived from:** `to-be.md` + `product-transformation-rules/` + `project/current/catalog.yaml`
**Consumed by:** `development_plan/requirements.md`
**Contents:** 5 blocks — `details` | `x-inputPorts` (5 ports) | `dataAccess` (2 profiles) | `dataQuality` (5 dimensions) | `SLA` (4 dimensions)

---

## What This Spec Is

The product definition is the **machine-readable declaration** of what the Purchase data product *is*. Everything before it in the chain — the modernization plan, the as-is analysis, the transformation rules, the to-be design — is prose written for humans. This is the first artifact a program can read.

It is the first of four development-plan artifacts, and its position defines its job:

| Artifact | Question it answers |
|---|---|
| **`product-definition.yaml`** | **What is this product**, in ODPS terms? |
| `requirements.md` | What must be true when we are done? |
| `design.md` | How is that achieved? |
| `tasks.md` | In what order do we build it? |

There are two files, and only one of them counts:

| File | Role | Registered in `_manifest.yaml` |
|---|---|---|
| `product-definition.yaml` | The definition. Every downstream artifact derives from this. | Yes — `sdd.artifacts.productDefinition` |
| `product-definition.md` | A rendered companion produced by the `emit-md` step, for reading and review. | No |

The YAML has five blocks. Their sizes are wildly uneven, and the imbalance is informative:

| Block | ODPS status | Lines | What it declares | Requirements it sources |
|---|---|---|---|---|
| `details` | native | 37 | Identity, description, value proposition, taxonomy | 7 |
| `x-inputPorts` | **extension** | 49 | The five Delta tables the pipeline reads | 9 |
| `dataAccess` | native | 38 | Two consumption profiles — SQL Warehouse and Power BI | 2 |
| `dataQuality` | native | 47 | Five quality dimensions, each bound to a QA rule | **13** |
| `SLA` | native | 28 | Freshness, latency, availability, retention | 4 |

Forty-seven lines of `dataQuality` generate thirteen of the thirty-two requirements. That block is the highest-leverage text in the entire development plan.

---

## Why This Spec Exists

### Because the to-be design is prose, and prose cannot be validated

`to-be.md` is 500-plus lines of narrative describing the target architecture. It is the right form for explaining a design to a person and the wrong form for driving a build. Nothing in it can be checked for completeness, diffed between versions, or read by a code generator.

The product definition compresses that narrative into five structured blocks. The compression is lossy on purpose — it keeps exactly the facts that create downstream obligations and drops the reasoning. The reasoning still exists in `to-be.md`; the definition is the extract that the machinery consumes.

### Because ODPS is a publishing standard, not a build specification

This is the central tension in the file, and it explains most of its oddities.

ODPS 4.1 was designed to let an organisation **publish** a data product to a marketplace or catalog: here is what it contains, who may access it, what quality you can expect, what we promise about freshness. It is written from the consumer's point of view. It has a rich vocabulary for outputs (`dataAccess`) and almost nothing for inputs, because a consumer browsing a catalog does not care what the product reads from.

A build specification needs the opposite emphasis. So this file:

- adds a non-standard **`x-inputPorts`** block, using the ODPS `x-` extension prefix, because the standard has no native concept of an input dependency;
- overloads `dataQuality` — a block meant to publish *measured* quality scores — to declare the five QA rules the pipeline must *implement*;
- carries a `retentionPolicy` entry inside `SLA` that does not follow the shape of its sibling entries, because retention is a governance fact rather than a service level.

None of this is wrong. It is what happens when a publishing standard is used as a build contract, and it is exactly why `requirements.md` has to exist: the ODPS blocks declare policy, and the requirements turn each declaration into a testable obligation.

### Because one product must be describable to three different audiences

The same file is read by a data consumer deciding whether to use the product, an engineer building it, and a code generator emitting artifacts. Each block is pitched at one of them:

| Block | Primary audience |
|---|---|
| `details`, `dataAccess` | Consumer — what is this, and how do I query it? |
| `x-inputPorts`, `dataQuality` | Engineer — what do I read, and what must I assert? |
| `SLA` | Operator — what have we promised, and when do I get paged? |

The `emit-md` companion exists to serve the first audience without making them read YAML. Whether it succeeds is discussed below; it largely does not.

---

## Block 1 — `details`

### What it contains

Product identity and taxonomy, under an `en` language key (ODPS supports multilingual details; only English is populated here).

```yaml
details:
  en:
    productID: purchase
    name: Purchase
    type: analytical_data_product
    status: draft
    visibility: organisation
```

Plus a `description`, a `valueProposition`, three `categories` (`procurement`, `purchasing`, `supply_chain`), and six `tags` (`delta_lake`, `medallion`, `incremental_etl`, `scd2`, `fact_table`, `databricks`).

### Key facts captured

**The description states the grain, and it disagrees with the code that was built.** It says "Each row represents one purchase order **line**." That is the correct grain — the as-is analysis shows the legacy extract joining `Purchasing.PurchaseOrderLines`. Hold on to this sentence: it is the clearest statement anywhere in the specification chain that the fact table is at line grain, and it is the fact that makes the single-column MERGE key in FR-007, `design.md` §3.3, and TASK-012 provably wrong. The defect that runs through three downstream artifacts is contradicted by the product's own one-paragraph description.

**The description names a bug fix as a product feature.** "Corrects the legacy SSIS staging-truncation bug by writing `bronze.purchase_staging` in OVERWRITE mode on every run." A defect discovered during as-is analysis has been promoted into the product's identity, which is why it survives all the way into FR-001's acceptance criterion. Fixes recorded only in analysis documents get dropped; fixes recorded in the definition become requirements.

**`type: analytical_data_product`** distinguishes this from an operational or source-aligned product. It is why every quality strategy except one is non-blocking: analytical consumers tolerate a warning-annotated row far better than they tolerate a missing nightly load.

**`visibility: organisation`** is the reason NFR-008 exists at all. Organisation-wide visibility means the access model has to be stated rather than assumed.

**The tags are a technology assertion, not a description.** `delta_lake`, `medallion`, `databricks` are target-platform facts. A reader who knows only this block already knows the migration target, which is the point — the definition has to stand alone when read out of the workspace.

### Why this block matters

Seven requirements cite `Details` as their source — but look at what they cite alongside it:

| Requirement | Source |
|---|---|
| NFR-009 (notebook skeleton) | `Details / CX-P005` |
| NFR-010 (DDL header block) | `Details / CX-P006` |
| NFR-011 (shared modules) | `Details / CX-P004` |
| FR-009 (no inline literals) | `Details / CX-P001 + CX-P002` |

In each case the substance comes from the product transformation rule, not from `details`. The block was cited because a requirement needs a source and there was nowhere better to point. This is worth naming plainly: **the ODPS definition is not a sufficient source for about a quarter of the requirements**, and the transformation rules quietly cover the gap. That is the system working — rules and definition are complementary inputs — but it means "traced to the product definition" is a weaker claim than it sounds for those rows.

---

## Block 2 — `x-inputPorts`

### What it contains

Five Delta tables, each with `inputName`, `inputType`, `location`, `format`, `frequency`, and a `description`. All five have `inputType: delta_table` and `format: delta`.

| `inputName` | Location | Frequency | Who owns it |
|---|---|---|---|
| `purchase_staging` | `inventory_stock.bronze.purchase_staging` | daily | **This product** (TASK-003 creates, `nb_extract_purchase` writes) |
| `supplier_dimension` | `inventory_stock.silver_dim.supplier` | daily | External — another product |
| `stock_item_dimension` | `inventory_stock.silver_dim.stock_item` | daily | External — another product |
| `date_dimension` | `inventory_stock.silver_dim.date` | static | External — static reference |
| `etl_cutoff` | `inventory_stock.bronze.etl_cutoff` | daily | **This product** (TASK-002 creates, the ETL advances) |

### Key facts captured

**Two of the five "input ports" belong to this product.** The descriptions admit it — `purchase_staging` is "Populated by `nb_extract_purchase`," and `etl_cutoff` is the watermark table this pipeline reads at the start and writes at the end. These are not inputs to the *product*; they are inputs to the product's *promotion step*. The genuinely external dependencies are three: supplier, stock item, and date.

This matters because it changes what the block can be used for. Read as a list of prerequisites — which is what an input-port list is for — it overstates the external surface by two and understates the coupling to the other products by burying it in a list of five. The design catches what the definition blurs: `design.md` and the ODPS descriptions both flag supplier and stock item as "External dependency — loaded by a separate product before the Purchase ETL executes."

**`frequency: static` on `date_dimension` is a scheduling instruction.** A static reference table has no runtime load dependency, which is precisely why TASK-007 sits at the root of the build graph with no predecessors. One YAML field, one topology decision.

**The ports carry no schema.** No column lists, no types, no keys. An input port that does not state its contract cannot detect a breaking upstream change — and `supplier` and `stock_item` are SCD-2 tables owned by another team, so their validity-column types are exactly the kind of thing that can change underneath this pipeline. The SCD-2 shape those joins depend on is pinned in TY-P001 and TY-P002 instead, one layer away from the port that consumes it.

**Nine requirements source from this block** — more than any other except `dataQuality`. Each of FR-001 through FR-006 maps to a named port, giving a clean one-to-one trace from declared dependency to functional obligation.

### Why this block matters

This is where the highest-consequence structural gap in the whole specification chain originates, and the root cause is visible only here.

Every one of the five input ports is **already a Delta table in the target platform**. The SQL Server 2014 `wideworldimportersdw` database — the thing this migration exists to move away from, the actual origin of every row — is not a port. There is no `inputType: jdbc`, no connection, no credential reference, no source table.

The consequence propagates cleanly: `requirements.md` has no requirement for the inbound extract, because there was no port to derive one from; FR-002 refers vaguely to "the upstream source"; `design.md` §2.1 labels its own input "`bronze.purchase_staging` (from upstream extract)" without saying what the extract reads. The gap only becomes concrete at TASK-015, which needs a JDBC query and has no configuration to draw it from, and it is finally registered as PD-001 in `build-plan.md` — five artifacts downstream of the place where it should have been declared.

The mechanism is easy to reconstruct. The port list was populated by asking "what does the pipeline read?" and answering from the target-side data flow. Every answer was a Delta table, so every port became `delta_table`, and the legacy source fell outside the frame.

---

## Block 3 — `dataAccess` (output ports)

### What it contains

Two named consumption profiles. ODPS treats `dataAccess` as the output side, so there is no `x-outputPorts` extension — this is the native block doing its intended job.

**`default`** — the SQL Warehouse endpoint:

```yaml
default:
  outputName: fact_purchase_sql_warehouse
  outputType: sql_endpoint
  outputFormat: delta_sql
  auth: Unity Catalog RBAC (service principal or user credentials)
  url: "dbsql://{{DATABRICKS_HOST}}/sql/1.0/warehouses/{{WAREHOUSE_ID}}"
  datasets:
    primary:   [inventory_stock.silver_fact.fact_purchase]
    supporting: [supplier, stock_item, date]
```

**`bi_reports`** — the Power BI connection, listing two named reports with descriptions, one of which carries a `crossProductDependency`.

### Key facts captured

**The `spec` field on `default` resolves a type question that matters.** It states that "`date_key` is a DATE value" while `supplier_key` and `stock_item_key` are surrogate keys. This is the ODPS-level confirmation of the TY-P001 override — the decision that SCD-2 validity columns and the date key are DATE rather than integer YYYYMMDD keys or timestamps. It also explains why the SK resolution logic in `CALC-002` and `CALC-003` needs its explicit `CAST(DATE AS TIMESTAMP)`: the cast exists because this choice was made here.

**The `spec` field also gives consumers a query instruction:** "Consumers must filter on `lineage_key` or `date_key` for incremental queries." That is a partition-pruning hint pushed to the consumer, and it is the only place in the definition where the physical layout leaks into the contract — appropriately, since a consumer who ignores it will full-scan a seven-year fact table.

**`crossProductDependency` is the one field that propagates perfectly.** Declared here as `inventory_stock.silver_fact.fact_sale (Sales_Orders product)`, it reappears in `design.md` §BI as "Cross-product dependency — requires coordinated cutover with Sales_Orders," and TASK-024 makes documenting it an explicit acceptance criterion. This is the counter-example that shows the pipeline works when the definition states a fact structurally: a single YAML key became a design row and a task acceptance condition without human intervention.

**The two profiles have very different completeness.** `default` has `outputType`, `outputFormat`, `auth`, `spec`, `url`, and `datasets`. `bi_reports` has `outputType`, `outputFormat`, `auth`, `spec`, and `reports` — but no `url` and no `datasets`. The asymmetry is defensible (a BI connection's endpoint *is* the SQL Warehouse URL) but it means a program iterating the profiles cannot rely on `url` being present.

**Only two requirements source from this block** — FR-007 and FR-010 — despite it being the richest native block in the file. The output side is comparatively easy: the table exists, it is queryable, the reports connect. The obligations cluster on the input and quality sides.

### Why this block matters

`dataAccess` is the consumer-facing contract, and it is the block that survives longest. Requirements get satisfied and closed; designs get superseded; tasks get completed. The output port is what a downstream team reads in year three when they want to know what they are allowed to depend on. The `spec` fields carry that weight, which is why their content — lowercase snake_case columns, `date_key` is a DATE, filter on `lineage_key` — is disproportionately specific compared to the rest of the file.

---

## Block 4 — `dataQuality`

### What it contains

Five entries under the `default` profile, each with `dimension`, `target`, `description`, `strategy`, and `blocking`.

| ODPS dimension | QA rule | Target | Strategy | Blocking |
|---|---|---|---|---|
| `completeness` | QA-P001 — staging vs. fact row count | `fact_purchase` | `zero_tolerance` | **true** |
| `consistency` | QA-P003 — RI via LEFT ANTI JOIN per FK | `fact_purchase` | `reject_and_continue` | false |
| `accuracy` | QA-P004 — business rule assertions | `fact_purchase` | `log_and_continue` | false |
| `uniqueness` | QA-P002 — orphaned SK detection | `fact_purchase` | `log_and_continue` | false |
| `traceability` | QA-P005 — centralised rejection store | `dq_rejections` | `centralised_sink` | false |

### Key facts captured

**One blocking check, four advisory.** `blocking: true` appears exactly once, on `completeness`. This single boolean is the most consequential field in the file: it is why QA-P001 becomes a `RuntimeError` that fails the Workflow task and marks `lineage_run.was_successful = false`, while the other four produce log lines and rejection rows and let the pipeline finish. The whole failure posture of the nightly job is one YAML key.

**The `strategy` vocabulary is doing real work.** These are not synonyms:

| Strategy | Meaning |
|---|---|
| `zero_tolerance` | Any violation aborts the run |
| `reject_and_continue` | Violating rows are recorded to a sink; the load proceeds |
| `log_and_continue` | Violations are counted and logged; nothing is persisted per-row |
| `centralised_sink` | Not a check — a declaration that a sink exists for the others to write to |

The distinction between `reject_and_continue` and `log_and_continue` is exactly why QA-P003 writes to `bronze.dq_rejections` with per-row detail while QA-P002 and QA-P004 only emit counts. And `centralised_sink` is not a quality check at all; it is infrastructure declared in the quality block because there was nowhere else for it to live.

**Thirteen requirements source from these five entries** — NFR-003 through NFR-007 (one per dimension, covering the mechanism) plus DQR-001 through DQR-008 (covering the data conditions). The fan-out is roughly 1:2.6, and it is why `requirements.md` splits NFRs from DQRs at all: each dimension needs both "the check runs and behaves this way" and "this specific condition holds in the data."

**The mapping is suspiciously exactly 1:1.** Five QA rules, five ODPS dimensions, no dimension used twice and none left empty. ODPS 4.1 offers a larger dimension vocabulary; five slots being filled by exactly five rules with no remainder suggests the rules were mapped onto the standard rather than the standard being used to discover missing checks. Two of the fits are a stretch:

- QA-P003 is referential integrity. It is filed under `consistency`, which is the closest available fit, but RI is conventionally *validity*.
- QA-P002 is orphaned surrogate key detection. It is filed under **`uniqueness`**, which it is not — an orphan is a key with no parent, not a duplicate. `design.md` inherits the mislabel, tagging QV-005 and QV-006 as "Uniqueness" for the same orphan checks.

### Why this block matters

The second stretch has a real cost, and it is the second-highest-consequence finding in this document.

Because the `uniqueness` slot was spent on orphan detection, **nothing anywhere in the quality model checks that the fact table's grain is unique.** There is no duplicate check on `purchase_key`, none on `wwi_purchase_order_id`, none on the four-column business key the to-be design specifies. The word "uniqueness" appears in the definition, in the design's QV table, and in NFR-005 — and in all three places it means orphan detection.

That is precisely the check that would have caught the MERGE-key defect. A uniqueness assertion on the natural key would have flagged, on the very first run against real data, that `wwi_purchase_order_id` is not unique at line grain. Instead the fact table has five quality dimensions, four of them advisory, and no assertion about its own grain — while the block's sibling `details` description states that grain in plain English one page earlier.

---

## Block 5 — `SLA`

### What it contains

Four entries under `default`:

| Dimension | Value | Unit | Note |
|---|---|---|---|
| `updateFrequency` | `daily` | day | One batch per calendar day |
| `latency` | `4` | hours | Available by 06:00 UTC; job starts 02:00 UTC |
| `uptime` | `99.5` | percent | SQL Warehouse endpoint, business hours |
| `retentionPolicy` | — | — | `silver: 7_years`, `bronze: 90_days` |

### Key facts captured

**The latency figure is derived, not chosen.** Four hours is the gap between the 02:00 UTC job start and the 06:00 UTC availability deadline. The deadline is the real commitment; the latency number is arithmetic. NFR-001 correctly makes the *deadline* the acceptance criterion — verified against `lineage_run.data_load_completed` — rather than trying to measure a duration.

**`uptime: 99.5` is a promise about something this product does not control.** The Databricks SQL Warehouse is platform infrastructure. This is why NFR-002 is one of only six should-have requirements: the product can be complete and correct while the platform's availability is somebody else's number.

**`retentionPolicy` breaks the shape of its siblings.** The other three entries have `value` and `unit`. This one has `silver` and `bronze` keys instead, holding string values `7_years` and `90_days`. It is a two-valued governance policy wearing an SLA entry's clothes, because ODPS has no governance retention slot and `SLA` was the nearest home. Any program iterating `SLA` expecting `value`/`unit` will find nothing here — which is exactly what the Markdown companion demonstrates.

**The 90-day bronze retention silently bounds a promise made elsewhere.** DQR-008 offers batch replay via `lineage_key` — you can find every rejection for a run and reprocess it. But replay needs the staging data, and `bronze.purchase_staging` is retained for 90 days. The replay guarantee has a 90-day expiry that DQR-008 never mentions. Two blocks in the same file, one bounding the other, with no cross-reference.

### Why this block matters

The SLA block is the only part of the definition that creates *operational* rather than *build* obligations. Requirements and tasks close out when the code ships; the SLA is what someone is measured against every night afterwards. That is why it is the source for the runbook's alerting thresholds, and why the 06:00 UTC deadline is the number that appears in the incident procedure.

---

## The Markdown Companion

`product-definition.md` is produced by the development plan's `emit-md` step, which the manifest records as completed. Its purpose is to make the definition readable without opening YAML.

It does not currently achieve that, because most of its table cells are empty:

| Table in the companion | Columns rendered empty | What the YAML actually holds |
|---|---|---|
| Input Ports | **Name**, **Type** | `inputName`, `inputType` |
| Output Ports | **Type**, **URL** | `outputType`, `url` |
| Data Quality | **Measured Value** | `strategy`, `blocking` |
| SLA | **Measured Value** | `value` + `unit` (and `silver`/`bronze` for retention) |

The pattern is a field-name mismatch: the renderer looks for `name`, `type`, `measuredValue`; the YAML uses `inputName`, `inputType`, `value`. The result is that the human-readable rendering is the one place where the substance is missing. The Input Ports table shows five rows of locations with no names or types. The Data Quality table lists five dimensions and omits `blocking: true` — the single most important fact in the file. The SLA table lists four dimensions and omits every number.

Two smaller artifacts of the rendering:

- The output-port profiles are emitted alphabetically (`bi_reports` before `default`), inverting the YAML order where `default` comes first. Harmless, but it means the primary access path is listed second.
- Everything with no column in the template is dropped entirely: `categories`, `tags`, all five input-port descriptions, `auth`, `spec`, `datasets`, the report list, `crossProductDependency`, every quality `strategy` and `description`, every SLA `unit` and `description`. A 225-line definition renders as 53 lines, and the loss is not compression — it is the removal of every value.

**Practical consequence:** the companion is safe to read for orientation and unsafe to review against. Nothing downstream consumes it — `requirements.md` cites the YAML, and the manifest registers only the YAML — so the lossiness has caused no incorrect artifact. The risk is a human one: a reviewer signing off on the Markdown would be approving a document in which the retention policy, the latency target, and the blocking-check flag are all blank.

---

## Divergences and Open Items

### 1. The real source system is not an input port

All five `x-inputPorts` entries are Delta tables already inside `inventory_stock`. SQL Server 2014 / `wideworldimportersdw` — the origin of every row and the reason this project exists — has no port, no `inputType`, no connection reference.

This is the root cause of a gap that surfaces four artifacts later. `requirements.md` derives FR-001 through FR-006 from the five ports and has no requirement for the inbound extract; FR-002 says only "the upstream source"; `design.md` §2.1 labels its input "from upstream extract." The gap becomes concrete at TASK-015, which specifies a JDBC query, and is finally registered as PD-001 in `build-plan.md`.

Partially resolved downstream: `config/environment.yaml` now carries `jdbc_driver`, `jdbc_user`, `jdbc_password`, and `source_table` as `{{PLACEHOLDER}}` values pending PD-001. The configuration surface exists; the port declaration still does not. **A sixth input port with `inputType: jdbc` would put the dependency where every downstream artifact could see it.**

### 2. The `uniqueness` dimension is spent on orphan detection, so nothing checks the fact grain

`dimension: uniqueness` is bound to QA-P002, which is orphaned surrogate key detection — a referential concern, not a uniqueness one. `design.md` inherits the label in QV-005 and QV-006.

The cost is that no check anywhere asserts the fact table's grain is unique: not on `purchase_key`, not on `wwi_purchase_order_id`, not on the four-column business key. That is the assertion that would have caught the MERGE-key defect on first contact with real data. **QA-P002 should be filed under a referential dimension, and a genuine uniqueness check should be added on the fact table's business key.**

### 3. The `governance` block that NFR-008 cites does not exist

NFR-008 — Unity Catalog access control, a must-have — lists its source as `governance / Unity Catalog + PD-003`. There is no `governance` block in `product-definition.yaml`. The word appears once in the file, inside the `retentionPolicy` description ("per data governance policy"), which is unrelated.

The requirement is well-formed and its acceptance criterion is testable, so nothing is broken in practice. But the trace is dangling, and NFR-010's grep-style trace check passes on any non-empty source field. **Either add a `governance` block with the role matrix, or re-source NFR-008 to `details / visibility` plus PD-003.**

### 4. The output-port URL placeholders have no home in configuration

`dataAccess.default.url` is `dbsql://{{DATABRICKS_HOST}}/sql/1.0/warehouses/{{WAREHOUSE_ID}}`. Neither placeholder appears anywhere in `config/` — no `warehouse` key, no `databricks_host`, nothing in `environment.yaml` or the Workflow JSON.

Compare the input side, which got its placeholders wired into `environment.yaml` under `purchase.etl`. The output port's connection string was left as an unresolved template with no configuration slot to resolve into, which means the BI reconnection documents (TASK-023, TASK-024) have to state the endpoint by hand. **The warehouse host and ID belong in `environment.yaml` alongside the JDBC block.**

### 5. `status: draft` after a completed build

`details.en.status` is `draft`. The manifest records `sb.completedSteps` as `init, plan, generate-db, generate-etl, validation` — the full codebase has been generated and validated. Twenty-six of twenty-six tasks are `completed`.

The status field is the one thing a catalog consumer would check before depending on the product, and it is stale. It is a one-word edit, but it is the difference between a product a downstream team will build on and one they will wait for. Note that the `draft` status is arguably still accurate for a different reason — three pending decisions (PD-001, PD-002, PD-003) remain open — in which case the field is right and its justification simply lives nowhere in this file.

### 6. Two of five input ports are owned by this product

`purchase_staging` and `etl_cutoff` are created by TASK-003 and TASK-002 and written by this product's own notebooks. Listing them as input ports alongside three genuinely external dimensions makes the external dependency surface look larger than it is and buries the cross-product coupling that actually needs coordination.

Low consequence — the descriptions are honest about the ownership, and the design distinguishes them correctly. But an input-port list is the natural place to answer "what must exist before this product can run," and the answer here requires reading five descriptions rather than counting five rows.

### 7. The Markdown companion renders no values

Covered in detail above. Four tables have empty value columns because of a field-name mismatch between the renderer and the YAML keys. Nothing downstream consumes the file, so no generated artifact is affected — but the companion should not be used for review sign-off in its current state.

---

## How This Spec Is Used Downstream

| Consumer | What it takes from the product definition |
|---|---|
| **`requirements.md`** | Every one of the 32 requirements cites an ODPS block in its Source column — `dataQuality` sources 13, `x-inputPorts` 9, `SLA` 4, `dataAccess` 2, `details` 7 |
| **`design.md`** | `dataQuality` becomes §5.1's validation rule table; `x-inputPorts` becomes §2.1's data flow; `dataAccess.spec` fixes the `date_key` DATE decision that `CALC-002`/`CALC-003` cast around |
| **`tasks.md`** | `crossProductDependency` becomes TASK-024's acceptance criterion; `frequency: static` on the date port is why TASK-007 has no predecessors |
| **`config/environment.yaml`** | `SLA` and quality thresholds are the tunables externalised here per FR-009 |
| **`runbook.md`** | The 06:00 UTC deadline, `uptime: 99.5`, and `blocking: true` become the alerting and incident thresholds |
| **BI reconnection docs** | `dataAccess.bi_reports.reports` supplies both report names and the Sales_Orders coordination requirement |
| **`validation-report.md`** | Validates generated artifacts against the ODPS declarations, block by block |
| **`_manifest.yaml`** | Registers the YAML as `sdd.artifacts.productDefinition` — the anchor the whole SDD chain hangs from |
| **Catalog publication** | `details`, `dataAccess`, `dataQuality`, and `SLA` are the consumer-facing record if this product is published |

---

## File Reference

| File | Location |
|---|---|
| `product-definition.yaml` | `products/Purchase/current/specifications/development_plan/product-definition.yaml` |
| `product-definition.md` | same directory — the `emit-md` companion |
| `requirements.md` | same directory — the 32 obligations derived from these five blocks |
| `to-be.md` | `products/Purchase/current/specifications/to-be.md` — the narrative this YAML compresses |
| `catalog.yaml` | `project/current/catalog.yaml` — the project-level product catalog this definition registers under |
| `_manifest.yaml` | `products/Purchase/current/_manifest.yaml` — records `emit-md` as complete and registers the YAML only |

225 lines across five blocks, and the density is the opposite of what the line counts suggest. `dataAccess` is the longest native block and sources two requirements; `dataQuality` is a page of YAML and sources thirteen. One boolean — `blocking: true` — determines the failure behaviour of the entire nightly pipeline. One sentence in `details` states the grain that three downstream artifacts contradict. And the single most consequential property of the file is something it does not contain: a port for the source system this migration exists to leave.
