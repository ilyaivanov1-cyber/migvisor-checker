# Modernization Plan — Explained

**Project:** Inventory_Stock_Project
**Source:** Microsoft SQL Server 2014 (`wideworldimportersdw`)
**Target:** Databricks Delta Lake, Unity Catalog (`inventory_stock`)
**Intake mode:** Hybrid (Pattern A — migVisor Explainer MCP grounded)

---

## What This Spec Is

The modernization plan is the **very first document produced** in the entire TCP (Transformation Co-Pilot) flow. It is the project intake — the result of an interactive Q&A session combined with automated source-code discovery via the migVisor Explainer MCP.

Before any transformation rules are written, before any code is designed, before any product-level analysis begins, this document captures four things:

1. **What** we're migrating (which database, which schemas, which objects)
2. **Where from** and **where to** (SQL Server 2014 → Databricks Delta Lake)
3. **Why** we're migrating (business rationale, not just "because we can")
4. **What's dangerous** (known risks, bugs, cross-team dependencies discovered from actual source code analysis)

Think of it as the project charter for the migration — everything downstream depends on the decisions made here.

---

## Why This Spec Exists

Without this document:

- The team discovers the SSIS staging-truncation bug 3 weeks into development, forcing rework.
- Developers argue about which objects are in scope vs. out of scope.
- Someone accidentally migrates `fact.sale` (which belongs to the Sales_Orders product) and wastes a sprint.
- The cross-team dimension dependency is forgotten until the first production run fails because dimensions weren't loaded first.
- The reseed utility gets migrated without owner sign-off, then breaks production data.
- Nobody documents *why* the migration is happening, so when priorities shift, there's no rationale to defend the project.

The modernization plan forces all of these discoveries **up front**, when they're cheap to address — not mid-implementation, when they're expensive.

---

## Section-by-Section Breakdown

### Section 1 — Identity

```
| Field        | Value                                                    |
| Project name | Inventory_Stock_Project                                  |
| Scope owner  | [USER INPUT REQUIRED]                                    |
| Intake mode  | hybrid (Pattern A — migVisor Explainer MCP grounded)     |
| Plan stage   | modernization-plan                                       |
```

**What it is:** The project's ID card — name, ownership, and how the intake was conducted.

**Why it matters:** The intake mode (`hybrid`) means this plan was built from both human answers and automated MCP discovery. This is important because it tells downstream readers that the risk observations and object inventories were **machine-verified against the actual source code**, not just reported from memory or documentation that might be stale.

**The `[USER INPUT REQUIRED]` placeholder** for scope owner is intentional — it forces someone to explicitly claim ownership before the project proceeds. A migration without a named owner has no one accountable for decisions like "do we keep the reseed utility?"

---

### Section 2 — Description / Rationale

**What it is:** The business case for the migration in plain language.

**What it says:** Modernize the legacy grocery-retail procurement and inventory workload onto Databricks. The legacy system runs a nightly batch that loads purchase order line items into `fact.purchase` via SSIS-orchestrated staging, resolving SCD-2 dimension surrogate keys against `dimension.supplier` and `dimension.stock item`.

**Four concrete reasons to migrate:**

| # | Reason | Why it's important |
|---|---|---|
| 1 | Replace fragile SSIS batch logic (including a **known staging-truncation bug**) with maintainable, observable Delta pipelines | The bug is real and actively causing data quality issues — this isn't a theoretical improvement |
| 2 | Gain scalability for growing purchase order volumes | The legacy SQL Server DW has a ceiling; Databricks scales horizontally |
| 3 | Decouple the procurement analytical layer from the shared SQL Server DW | Other teams share this DW — procurement changes risk breaking their workloads |
| 4 | Align the purchase domain with the lakehouse conventions already established by the Sales_Orders migration | Another team has already migrated Sales_Orders to Databricks — Purchase should follow the same patterns for consistency |

**Why it matters:** Every migration needs a rationale that isn't "the old thing is old." These four reasons are specific, measurable, and defensible. When someone asks "why are we spending 3 months on this?" — this section answers it. Reason #1 alone (fixing a known bug that silently corrupts data) justifies the project.

---

### Section 3 — Source Systems

**What it is:** The precise identification of what we're migrating from — platform, database, access method, and schemas in scope.

**Source identification:**

| Attribute | Value |
|---|---|
| Platform | Microsoft SQL Server 2014 (T-SQL) |
| Database | `wideworldimportersdw` (the WideWorldImporters sample data warehouse) |
| Access method | migVisor Explainer MCP (lineage + source retrieval) |

**Schemas in scope:**

| Schema | Role | Why it's in scope |
|---|---|---|
| `fact` | Fact table — `fact.purchase` | The core analytical output of the Purchase product |
| `dimension` | Conformed dimensions — `supplier`, `stock item`, `date` | Read dependencies for SCD-2 surrogate key resolution |
| `integration` | ETL / staging + migrate-procedure layer | The entire staging and transformation pipeline lives here |
| `application` | T-SQL configuration / parameter objects (Purchase-domain portions only) | Contains the reseed utility that may or may not be migrated |
| `sequences` | Surrogate / lineage key sequence objects | Contains `lineagekey` SEQUENCE — must be replaced, not migrated |

**Why it matters:** Naming the exact platform version (SQL Server **2014**) matters because it determines which T-SQL features are available in the source code. Naming the exact database matters because there could be multiple databases on the server. Listing schemas explicitly prevents someone from accidentally pulling in schemas that don't belong to this project.

---

### Section 3.1 — Known Migration Risks (the most valuable part)

**What it is:** Six specific risks discovered by the migVisor Explainer MCP by analyzing the actual source code — not guessed, not theoretical, not from documentation.

This is arguably the **most valuable section** in the entire modernization plan. These risks were found by machine analysis of the source system's lineage, stored procedures, and SSIS packages.

| # | Risk | Severity | What happens if missed |
|---|---|---|---|
| **1** | **SSIS staging-truncation bug**: the SSIS dataflow deletes from `Integration.Order_Staging` instead of `Integration.Purchase_Staging`. Purchase staging is **never truncated** — stale rows accumulate indefinitely. | **Critical** | If the Databricks replacement doesn't fix this bug, it inherits the same silent data corruption. Stale rows from prior runs get re-merged into the fact table, producing duplicate or outdated purchase records. Every downstream report shows incorrect numbers. |
| **2** | `dimension.supplier` and `dimension.stock item` contain **spaces** in object names. | High | Spaces in Delta table names require backtick quoting everywhere and break most tooling, notebooks, and automated processes. If not renamed during migration, every SQL query and Python script must handle the quoting — a maintenance nightmare. |
| **3** | `sequences.lineagekey` is a SQL Server SEQUENCE object; **no native Databricks equivalent**. | High | If someone tries to create a SEQUENCE in Databricks, it simply doesn't exist. The lineage key generation mechanism must be completely redesigned — not translated. |
| **4** | `integration.migratestagedpurchasedata` resolves SCD-2 dimension keys and upserts into `fact.purchase` via T-SQL MERGE with lineage key injection and ETL cutoff watermarking. | High | This is the most complex stored procedure in scope. It combines SCD-2 temporal lookups, MERGE upsert, lineage tracking, and watermark management in a single procedure. A naive translation will miss subtle semantics (e.g., the exclusive/inclusive bounds on the temporal range lookup). |
| **5** | `application.configuration_reseedetl` TRUNCATEs `fact.purchase` and inserts key=0 sentinel rows; resets ETL cutoff to base time. | Medium | This is likely a testing/reseed utility. If migrated without sign-off, someone could accidentally run it in production and wipe the fact table. If dropped without sign-off, the team loses their ability to reset the environment for testing. |
| **6** | `dimension.supplier` and `dimension.stock item` are **read dependencies** owned by other products. Purchase ETL must run after dimension loads complete. | High | If the Databricks Workflow doesn't enforce this ordering, the Purchase pipeline runs before dimensions are loaded, and every surrogate key resolves to 0 (unknown). The fact table fills with meaningless dimension references. No error is raised — it's a silent data quality failure. |

**Why it matters:** These six risks represent the difference between a successful migration and a disaster. Risk #1 is a **production bug** in the current system. Risk #6 is a **cross-team dependency** that must be encoded in the Databricks Workflow task graph. Risk #4 is the **hardest piece of code** to rewrite. Finding all of these before writing a single line of code saves weeks of debugging.

---

### Section 4 — Target System

**What it is:** A concise declaration of the target platform and naming conventions.

| Attribute | Value |
|---|---|
| Target platform | Databricks (Delta Lake lakehouse) |
| Schema naming convention | `catalog.schema.table`, `lowercase_snake_case` |

**Why it matters:** This establishes two fundamental contracts:
1. **Three-part naming**: every object reference in the target is `inventory_stock.<schema>.<table>` — not two-part, not four-part.
2. **lowercase_snake_case**: every name in the target follows this convention — no exceptions. This drives the entire NM (Naming) dimension of the transformation rules.

---

### Section 5 — Key Entities

**What it is:** The four business entities that define the Purchase domain.

- Purchase order line items (`fact.purchase`)
- Supplier (`dimension.supplier`)
- Stock Item (`dimension.stock item`)
- Date (`dimension.date`)

**Why it matters:** This is the star schema in one sentence. The fact table at the center, three dimension tables around it. Every subsequent spec — as-is, to-be, development plan — revolves around these four entities.

---

### Section 6 — In-Scope Objects

**What it is:** A complete, verified inventory of every object that **will** be migrated — 17 objects across 5 schemas plus 4 SSIS pipeline items. Each object was confirmed present in the source database via the migVisor Explainer MCP.

**6.1 — fact schema (1 object)**

| Object | Type |
|---|---|
| `fact.purchase` | table |

The core fact table. One object, but it's the most important one.

**6.2 — dimension schema (3 objects)**

| Object | Type | Notes |
|---|---|---|
| `dimension.supplier` | table | SCD-2 read dependency (ETL not Purchase-owned) |
| `dimension.stock item` | table | SCD-2 read dependency; **name contains space** |
| `dimension.date` | table | FK target; shared infrastructure — pre-populated |

All three are **read dependencies** — Purchase doesn't load them, but it can't run without them. This distinction (own vs. depend) is critical for Workflow task ordering.

**6.3 — integration schema (6 objects)**

| Object | Type |
|---|---|
| `integration.purchase_staging` | table |
| `integration.etl cutoff` | table |
| `integration.lineage` | table |
| `integration.migratestagedpurchasedata` | procedure |
| `integration.getlastetlcutofftime` | procedure |
| `integration.getlineagekey` | procedure |

This is the ETL engine — 3 tables and 3 stored procedures. All six must be replaced in the target.

**6.4 — application schema (1 object)**

| Object | Type | Notes |
|---|---|---|
| `application.configuration_reseedetl` | procedure | Purchase-domain portions only — needs scope-owner sign-off |

The controversial reseed utility. Included in scope but flagged for a decision.

**6.5 — sequences schema (1 object)**

| Object | Type |
|---|---|
| `sequences.lineagekey` | sequence |

The SQL Server SEQUENCE that has no Databricks equivalent. Included so it's explicitly tracked as "must be replaced, not migrated."

**6.6 — SSIS Orchestration Pipeline (4 items)**

| Object | Notes |
|---|---|
| `pipeline_dailyetlmain` | Master daily ETL workflow (shared; Purchase container runs within it) |
| `pipeline_item_set tablename to purchase` | Sets variable before the purchase load container |
| `pipeline_item_truncate purchase_staging` | **BUG:** coded to DELETE FROM `Integration.Order_Staging` — wrong table |
| `pipeline_item_extract updated purchase data to staging` | Loads purchase updates into staging |
| `pipeline_item_migrate staged purchase data` | Calls `migratestagedpurchasedata` |

The SSIS pipeline is documented here because it **is** the orchestration layer. The bug in item #3 is flagged inline so it's impossible to miss.

**Why it matters:** This inventory is the **scope boundary**. If an object isn't listed here, it's not in scope. Period. This prevents scope creep and ensures the team knows exactly what they're responsible for.

---

### Section 7 — Out-of-Scope Items

**What it is:** An explicit list of everything that will **not** be migrated, with reasons.

| Item | Reason |
|---|---|
| `fact.sale`, `fact.order`, `fact.movement`, `fact.transaction`, `fact.stock holding` | Belong to Sales_Orders, Inventory_Movement, or Finance_Analytics products |
| `integration.migratestaged*data` procedures (other than Purchase) | Load facts not in this product scope |
| `integration.*_staging` tables (other than purchase) | Staging for out-of-scope facts |
| `dimension.customer`, `dimension.city`, `dimension.employee`, `dimension.payment method`, `dimension.transaction type` | Belong to Sales_Orders product |
| `analytics.*` views and tables | Finance/Analytics domain — separate product |
| `application.configuration_applypolybase`, `configuration_populatelargesaletable`, `configuration_applypartitionedcolumnstoreindexing` | SQL Server-specific config not related to Purchase |
| `dbo.*` | SSMS diagram objects and sample/test artifacts |
| `sequences.reseedallsequences`, `sequences.reseedsequencebeyondtablevalues` | Reseed utilities — review at implementation; likely drop |

**Why it matters:** The out-of-scope list is as important as the in-scope list. Without it:
- A developer sees `fact.sale` in the same database and wonders "should I migrate this too?"
- Someone notices `dimension.customer` and adds it to the DDL scripts "just in case."
- The reseed utilities get migrated without review.

Explicit exclusion eliminates ambiguity.

---

### Section 8 — Boundaries

**What it is:** The temporal, organizational, and system boundaries of the migration.

| Boundary | Value |
|---|---|
| Temporal | `[USER INPUT REQUIRED]` — date range of data to migrate |
| Organizational | `[USER INPUT REQUIRED]` — owning team / department |
| System | Source: `wideworldimportersdw` on SQL Server 2014; Target: Databricks lakehouse |

**Why it matters:** The `[USER INPUT REQUIRED]` placeholders are deliberate. The temporal boundary (how much historical data to migrate) is a business decision with cost implications — migrating 10 years of data takes much longer than migrating 1 year. The organizational boundary defines who is responsible. These can't be guessed by automation — they require human decisions.

---

### Section 9 — Data-Product Inventory

**What it is:** The list of candidate data products within the project.

| Product | Status | Description |
|---|---|---|
| **Purchase** | PRIMARY — first product | Purchase order transaction domain. `fact.purchase` + conformed dimensions + integration-layer staging/migrate procedure |
| **Inventory_Movement** | Future candidate | Stock movement domain. `fact.movement` + dimensions |

**Why it matters:** This scoping decision drives the entire workflow. Purchase is built first because it's the primary product. Inventory_Movement is identified early so the project knows what's coming next, but no work begins on it until Purchase is complete. This prevents the team from trying to boil the ocean.

---

### Section 10 — Stakeholders

**What it is:** The four key roles that must be filled before the project proceeds.

| Role | Value |
|---|---|
| Project owner | `[USER INPUT REQUIRED]` |
| Business lead | `[USER INPUT REQUIRED]` |
| Technical lead | `[USER INPUT REQUIRED]` |
| Sign-off required | `[USER INPUT REQUIRED]` |

**Why it matters:** Every `[USER INPUT REQUIRED]` is a forcing function. The project cannot proceed to implementation without named individuals in these roles. The "Sign-off required" field is especially important for pending decisions like PD-002 (should the reseed utility be migrated?).

---

### Section 11 — Interview Mode

**What it is:** Metadata about how the plan was created.

| Field | Value |
|---|---|
| Mode | hybrid |
| Pattern | Pattern A — migVisor Explainer MCP grounded |
| Discovery source | migVisor Explainer MCP (lineage traversal + source retrieval) |

**Why it matters:** This tells future readers that the object inventories, risk observations, and lineage analysis in this plan were **machine-verified** by traversing the actual source code and SSIS packages — not hand-written from memory. This gives the plan a higher confidence level than a purely manual intake.

---

## How This Spec Is Used Downstream

The modernization plan feeds directly into every subsequent spec:

| Downstream spec | What it takes from the modernization plan |
|---|---|
| **Project transformation rules** | Source/target platforms (§3, §4), schemas in scope (§3), known risks (§3.1) — risks become specific rules (e.g., Risk #1 → SX-014, PE-007, OB-003) |
| **Product scope** | Data product inventory (§9), in-scope objects (§6), key entities (§5) |
| **As-is analysis** | Source system details (§3), object inventory (§6), SSIS pipeline documentation (§6.6), known bugs (§3.1) |
| **Product transformation rules** | Risk observations that need product-specific handling (e.g., Risk #6 → Workflow task dependency rules) |
| **To-be design** | Target platform (§4), naming conventions (§4), rationale for bug fixes (§2, §3.1) |
| **Development plan** | Pending decisions become task prerequisites; stakeholder sign-offs gate specific tasks (PD-002 → TASK-017) |
| **Catalog** | Project description (§2), source/target systems (§3, §4), product inventory (§9) |

---

## File Reference

| File | Location |
|---|---|
| `modernization-plan.md` | `project/current/modernization-plan.md` |

This is a single file — there are no per-dimension YAML files for the modernization plan. All content is in one markdown document.
