# Product Scope — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Base node:** `wideworldimportersdw.fact.purchase`
**Discovery mode:** hybrid — Pattern A (migVisor Explainer MCP grounded)
**Plan stage:** scope
**Objects in scope:** 19 across 6 categories | **Out-of-scope entries:** 12 | **Product-level risks:** 7

---

## What This Spec Is

The product scope is the **boundary contract** for a single data product. It answers one question with enough precision that no downstream spec has to guess: *what belongs to Purchase, and what does not?*

It is the first product-level spec in the TCP flow — produced **after** the project modernization plan and **before** the as-is analysis. It consists of 9 sections:

1. **Identity** — product name, parent project, owner, discovery mode, plan stage
2. **Description** — what the product covers and what it does not own
3. **Objects in Scope** — the complete object inventory, grouped by category
4. **Out-of-Scope Objects** — explicit exclusions with a reason for each
5. **Consumers** — who reads the product's data
6. **Calculation Surface** — where the logic lives and how heavy it is
7. **Boundaries** — temporal, organizational, and system limits (source and target)
8. **Priority and Sequencing** — where the product sits in the project order
9. **Known Migration Risks** — product-level risks with implications

Think of it as the **fence around the work**. The as-is analysis goes deep; the scope decides how wide.

---

## Why This Spec Exists

### The problem with implicit scope

Without a written scope, a migration team discovers its boundaries by colliding with them:

1. A developer migrating `fact.purchase` notices it joins `dimension.supplier` and starts migrating the supplier load procedure too — work that belongs to another product.
2. Two weeks later, the same developer realizes `sequences.lineagekey` is shared by every `migratestaged*data` procedure in the warehouse, so "just redesign it" is a project-wide decision, not a Purchase one.
3. At review time, nobody can say whether `application.configuration_reseedetl` was supposed to be migrated, because it touches Purchase objects but is mostly a test utility.
4. At cutover, the `wwidw purchase and sale per stockitem dynamic` report breaks because it also reads `fact.sale` — a table owned by a product that hasn't been migrated yet.

Every one of these is a scope question, not a technical one. The scope spec resolves them **before** any code is written.

### Ownership vs. dependency — the distinction that matters most

The single most important idea in this spec is the difference between an object Purchase **owns** and an object Purchase **reads**:

| Relationship | Example | What Purchase does |
|---|---|---|
| **Owns** | `fact.purchase`, `integration.purchase_staging`, `migratestagedpurchasedata` | Migrates the object and its logic |
| **Reads (external)** | `dimension.supplier`, `dimension.stock item` | Consumes them; does **not** migrate their load procedures |
| **Reads (shared infrastructure)** | `dimension.date`, `integration.etl cutoff`, `integration.lineage`, `sequences.lineagekey` | Consumes them; redesign decisions are coordinated project-wide |

`dimension.supplier` and `dimension.stock item` are the clearest case. The Purchase ETL cannot run without them — `migratestagedpurchasedata` performs SCD-2 surrogate key lookups against both. But their load procedures belong to other products. So Purchase scope includes **consumption** of these dimensions and excludes their **load logic**. That split appears three times in the document (§2, §3.2, §4) because getting it wrong in either direction is expensive: migrate them and you duplicate another team's work; ignore them and your fact load has no keys to resolve.

### Scope is what makes the as-is finite

The as-is analysis is a forensic examination of legacy code — and legacy warehouses have no natural stopping point. Follow the joins from `fact.purchase` far enough and you have documented the entire `wideworldimportersdw` database. The scope spec is what stops that traversal. Sections 3 and 4 together tell the as-is agent exactly which objects to examine in depth and which to note and walk away from.

---

## Section 1 — Identity

### What it contains

A 5-field table: product name, parent project, scope owner, discovery mode, and plan stage.

### The fields that carry weight

| Field | Value | Why it matters |
|---|---|---|
| Discovery mode | `hybrid — Pattern A (Explainer MCP grounded, base node: fact.purchase)` | Records **how** the scope was determined. Pattern A means the object inventory was traversed from a single base node using the migVisor Explainer MCP, not assembled by hand. A reader can re-run the traversal to verify the inventory is complete. |
| Base node | `wideworldimportersdw.fact.purchase` | The traversal root. Everything in §3 was reached by walking lineage outward from this table. If the base node is wrong, the entire inventory is wrong. |
| Plan stage | `scope` | Marks the product's position in the TCP flow. The orchestrator reads this to decide which skill runs next. |
| Scope owner | `[USER INPUT REQUIRED]` | An **unresolved placeholder**, not an omission. |

### Why the placeholders are deliberate

`[USER INPUT REQUIRED]` appears three times in this document — scope owner (§1), temporal boundary (§7), and organizational boundary (§7). These are not gaps to be quietly filled with a plausible guess. They mark decisions that need a human with authority:

- **Scope owner** determines who signs off on the boundary and who resolves the `configuration_reseedetl` drop-scope question in Risk #5.
- **Temporal boundary** determines how much history the initial load pulls — a decision with direct cost and runtime implications.
- **Organizational boundary** determines which team's on-call rotation owns the pipeline after cutover.

An invented value here looks identical to a confirmed one in every downstream document. The placeholder keeps the open question visible until someone closes it.

---

## Section 2 — Description

### What it contains

Three prose paragraphs: what the product covers, what the migration accomplishes, and the ownership carve-out for the two SCD-2 dimensions.

### Key facts captured

**The domain:** the procurement order transaction domain of the WideWorldImporters data warehouse — the core fact table, its conformed dimension read dependencies, the SSIS-orchestrated integration staging layer, and the BI reports that consume it.

**The migration:** Microsoft SQL Server 2014 → Databricks Delta Lake, replacing fragile SSIS batch logic "including a confirmed staging-truncation bug" with maintainable, observable Delta pipelines.

**The carve-out:** `dimension.supplier` and `dimension.stock item` are read dependencies only; their load procedures are owned by other products.

### Why this section matters

The description is the only part of the scope written in prose, and it is the part a new team member reads first. Two phrases in it are load-bearing:

- **"including a confirmed staging-truncation bug"** — the word *confirmed* signals this is an observed defect, not a suspicion. It escalates into Risk #1, then into the to-be design as a deliberate behavior change, then into the generated pipeline as a correct truncate. Naming it in the scope description means the fix is a scoped requirement rather than a developer's discretionary improvement.
- **"read dependencies ... but their load procedures are owned by other products"** — stated in prose here, tabulated in §3.2, and excluded explicitly in §4. Three statements of the same fact, because it is the boundary most likely to be crossed by accident.

---

## Section 3 — Objects in Scope

### What it contains

Six subsections grouping 19 objects by category, each with a role and — where relevant — an ownership note or a defect annotation.

| Subsection | Objects | What they are |
|---|---|---|
| 3.1 Core Fact Table | 1 | `fact.purchase` — the base node, with its full 11-column schema |
| 3.2 Conformed Dimensions | 3 | `supplier`, `stock item` (SCD-2 read deps), `date` (shared infrastructure) |
| 3.3 Integration Staging Layer | 7 | 3 tables + 4 stored procedures |
| 3.4 Sequences / Infrastructure | 1 | `sequences.lineagekey` |
| 3.5 SSIS Orchestration Pipeline | 5 | 1 master workflow + 4 dataflow items in the Purchase container |
| 3.6 BI Reports | 2 | Downstream consumers |

### Details worth noting

**§3.1 records the schema inline.** All 11 columns of `fact.purchase` are listed with types and roles: `PurchaseKey` (BIGINT IDENTITY PK), `Date Key`, `Supplier Key`, `Stock Item Key` (FKs), `WWI Purchase Order ID`, `Ordered Outers`, `Ordered Quantity`, `Received Outers`, `Package`, `Is Order Finalized`, `Lineage Key`. A reader can see the target table's shape without opening the as-is. Note the spaces in column names — the trigger for naming rules downstream.

**§3.3 separates owned logic from shared infrastructure.** `migratestagedpurchasedata` is flagged as "core ETL logic — must be rewritten as Databricks Delta `MERGE INTO`" and is Purchase-owned. `getlastetlcutofftime` and `getlineagekey` are marked shared infrastructure that Purchase merely calls. Same schema, different ownership.

**§3.3 scopes a procedure partially.** `application.configuration_reseedetl` is in scope for its **Purchase-domain portions only** — the `fact.purchase` TRUNCATE, the key=0 sentinel inserts into `supplier` and `stock item`, and the cutoff reset. Everything else in that procedure is excluded in §4. Partial scoping of a single object is unusual, and it is spelled out in both directions so nobody has to infer it.

**§3.5 annotates the bug at the object level.** The `truncate purchase_staging` dataflow carries an inline warning: it is coded to `DELETE FROM Integration.Order_Staging` instead of `Integration.Purchase_Staging`, so purchase staging is never truncated and stale rows accumulate across runs. The annotation appears here **and** as Risk #1, so it is visible whether a reader is scanning the inventory or the risk register.

**§3.6 flags a cross-domain consumer.** `wwidw purchase and sale per stockitem dynamic` also reads `fact.sale`, which belongs to the Sales_Orders product. This is the seed of Risk #7.

### Why this section matters

This inventory is the work list. Every table becomes a DDL artifact, every stored procedure becomes a notebook or Python module, every SSIS dataflow becomes a Workflow task, and every BI report becomes a reconnection task. Objects absent from §3 do not get built.

---

## Section 4 — Out-of-Scope Objects

### What it contains

12 entries, each pairing an excluded object (or object family) with a reason.

### The exclusion categories

| Reason type | Examples | Why excluded |
|---|---|---|
| Belongs to another product | `fact.sale`, `fact.order`, `fact.movement`, `fact.transaction`, `fact.stock holding`; `dimension.customer`, `city`, `employee`, `payment method`, `transaction type`; `analytics.*` | Owned by Sales_Orders, Inventory_Movement, or Finance_Analytics |
| Load logic for a read dependency | `migratestagedsupplierdata`, the `stock item` load procedure | Purchase reads these dimensions; another product loads them |
| Follows an out-of-scope fact | other `migratestaged*data` procedures, other `*_staging` tables, SSIS items for sale/order/movement/stockholding | Support facts that are not in this product |
| Platform-specific config | `configuration_applypolybase`, `configuration_populatelargesaletable`, `configuration_applypartitionedcolumnstoreindexing` | SQL Server–specific and unrelated to Purchase |
| Deferred decision | `sequences.reseedallsequences`, `reseedsequencebeyondtablevalues` | "Review at implementation; likely drop scope" |
| Excluded at project level | `dbo.*` | SSMS diagram objects and sample artifacts |
| Partial exclusion | `configuration_reseedetl` (non-Purchase portions) | Complements the partial inclusion in §3.3 |

### Why this section matters

An out-of-scope list with reasons behaves differently from one without. The reason is what lets a future reader **re-evaluate** the decision instead of merely obeying it.

Consider `fact.sale`. It is excluded because it belongs to Sales_Orders — not because it is irrelevant to Purchase. When Risk #7 raises the cross-domain report problem, the reason in §4 tells you the dependency is real and the exclusion is an ownership boundary, not a judgment that the table doesn't matter. An unreasoned exclusion would leave that ambiguous.

The two entries marked "review at implementation" are equally deliberate: they are not decided yet, and saying so is more useful than picking a side and hiding it.

---

## Section 5 — Consumers

### What it contains

Two BI reports with their type and the exact objects each reads.

| Consumer | Type | Reads |
|---|---|---|
| `wwidw purchase and sale per stockitem dynamic` | BI Report (Power BI / SSRS) | `fact.purchase` — cross-domain; also reads `fact.sale` |
| `wwidw-ordered-by-supplier` | BI Report (Power BI / SSRS) | `fact.purchase`, `dimension.supplier` |

### Why this section matters

Consumers determine what "done" means. A migration that lands the tables but leaves the reports pointing at SQL Server has not shipped anything a business user can see. Recording the exact object list per report makes each one a testable reconnection target: after cutover, `wwidw-ordered-by-supplier` must read `fact_purchase` and `supplier` from Databricks and return the same numbers.

The cross-domain annotation on the first report is the substantive finding. It means Purchase cannot fully cut over independently — a constraint that surfaces again in Risk #7 and drives cutover sequencing with the Sales_Orders team.

---

## Section 6 — Calculation Surface

### What it contains

A characterization — "moderately calculation-light at the analytical layer but ETL-logic-heavy in its migration procedure" — followed by five bullets locating the logic.

### Where the logic lives

| Location | What it does | Migration implication |
|---|---|---|
| `migratestagedpurchasedata` | Resolves SCD-2 surrogate keys for `supplier` and `stock item`, upserts into `fact.purchase`, injects lineage key, updates ETL cutoff | Full rewrite as Delta `MERGE INTO` with Python/SQL orchestration; idempotency semantics of the original upsert must be preserved |
| `getlastetlcutofftime` | Reads the incremental high-watermark from `integration.etl cutoff` | Re-express as a Delta control table read |
| `getlineagekey` → `sequences.lineagekey` | Generates lineage run keys | No native Databricks equivalent — redesign as `GENERATED ALWAYS AS IDENTITY` or UUID-based run ID |
| Staging truncation | Should clear purchase staging at run start; currently does not | Must be implemented correctly, fixing the legacy bug |
| Analytical layer | Nothing — no scalar UDFs, no analytics views | Both reports read `fact.purchase` directly; no intermediate calculation layer to migrate |

### Why this section matters

It sets effort expectations correctly, and the correction runs in an unintuitive direction. "Calculation-light" would normally imply a cheap migration. Here the opposite holds: there is almost nothing to migrate at the analytical layer, but the single ETL procedure concentrates SCD-2 temporal key resolution, upsert semantics, lineage injection, and watermarking into one place. That is where the difficulty sits, and this section says so before anyone estimates the work from table count alone.

The last bullet is worth reading as a positive finding: no UDFs and no views means no hidden calculation layer, and it is why the reports can be reconnected directly to the fact table rather than to a rebuilt semantic layer.

---

## Section 7 — Boundaries

### What it contains

Six boundary definitions covering temporal, organizational, source system, target system, and ETL orchestration on both sides.

| Boundary | Value |
|---|---|
| Temporal | Inherits project default — `[USER INPUT REQUIRED]` (range comes from the `integration.etl cutoff` watermark table; confirm with scope owner) |
| Organizational | `[USER INPUT REQUIRED]` — owning team within Inventory_Stock_Project |
| System (source) | `wideworldimportersdw` on SQL Server 2014 — schemas `fact`, `dimension`, `integration`, `sequences`, `application` (Purchase portions only) |
| System (target) | Databricks Delta Lake — catalog `inventory_stock`, layers bronze/silver/gold (staging → conformed dimension → fact) |
| ETL orchestration (source) | SSIS `pipeline_dailyetlmain` — Purchase container within the nightly batch |
| ETL orchestration (target) | Databricks Workflow — nightly Delta pipeline; task dependencies must enforce dimension load completion before the Purchase fact load |

### Why this section matters

The two system boundaries define the translation problem: every rule in the transformation rule set exists because something must move from the source column of this table to the target column.

The target orchestration boundary carries a requirement, not just a description: **task dependencies must enforce dimension load completion before the Purchase fact load.** In SSIS this ordering was implicit in the container graph — real, enforced, and documented nowhere. Stating it as a boundary makes it an explicit design obligation for the Workflow, and it reappears as Risk #6.

The temporal boundary shows why the placeholder convention matters in practice. The value is not simply unknown — the document records *where to find it* (the `etl cutoff` watermark table) and *who confirms it* (the scope owner). That is an actionable open item rather than a blank.

---

## Section 8 — Priority and Sequencing

### What it contains

Four fields: priority, rationale, dependencies, successor products.

| Field | Value |
|---|---|
| Priority | **PRIMARY** — first product in Inventory_Stock_Project |
| Rationale | Core procurement domain; directly feeds purchase BI reports and cross-domain stock-item analytics |
| Dependencies | `dimension.supplier` and `dimension.stock item` must be fully loaded (SCD-2 current rows present) before the Purchase ETL runs; owned by separate products, so Workflow task dependencies must enforce ordering |
| Successor products | Inventory_Movement — reuses `stock item` and `supplier` already migrated by their owning products |

### Why this section matters

Being **PRIMARY** has consequences beyond ordering. As the first product, Purchase establishes the patterns every later product inherits: the codebase layout, the SCD-2 merge helper, the surrogate key resolver, the lineage propagation mechanism, the DQ rejection store. Decisions made here are cheap to change now and expensive to change once Inventory_Movement has copied them.

The dependency entry states an uncomfortable structural fact plainly: the first product to be built depends at runtime on dimensions owned by products that have not been built. The scope does not paper over this — it names the mitigation (Workflow task dependencies) and escalates it to Risk #6.

---

## Section 9 — Known Migration Risks

### What it contains

Seven product-level risks, each with an implication that states what the migration must do about it.

| # | Risk | Implication |
|---|---|---|
| 1 | Truncate dataflow targets `Order_Staging` instead of `Purchase_Staging` — purchase staging is never cleared, stale rows accumulate | Critical correctness defect. Databricks replacement must correctly overwrite/truncate staging at the start of each incremental run. **"Do not port the bug."** |
| 2 | `dimension.supplier` and `dimension.stock item` contain **spaces** in object names | Rename to `supplier` and `stock_item` under snake_case; update all references in ETL logic and BI report queries |
| 3 | `sequences.lineagekey` — SQL Server SEQUENCE with no Databricks equivalent | Redesign as `GENERATED ALWAYS AS IDENTITY` or UUID-based run ID; coordinate with other products sharing the sequence |
| 4 | `migratestagedpurchasedata` — T-SQL MERGE with SCD-2 key resolution, lineage injection, watermarking | Full rewrite as Delta `MERGE INTO`; preserve idempotency semantics of the original upsert |
| 5 | `configuration_reseedetl` (Purchase portions) TRUNCATEs `fact.purchase` and inserts key=0 sentinels | Likely test-only — confirm drop scope with scope owner. If retained, sentinel rows must be pre-seeded at initialization |
| 6 | Supplier and stock item ETL load is **not Purchase-owned** | Hard runtime dependency. Workflow task graph must enforce that both dimension loads complete successfully before the Purchase fact load starts |
| 7 | `wwidw purchase and sale per stockitem dynamic` is **cross-domain** (`fact.purchase` + `fact.sale`) | Requires coordinated cutover with Sales_Orders; partial migration breaks the report or forces a bridging view. Align cutover timing |

### Why this section matters

This is the highest-value section in the document, and the reason is structural: **a risk written here becomes a rule, a requirement, and a line of generated code.** Each entry states not just the problem but the required response, which is what makes it traceable downstream.

Risk #1 is the clearest illustration. "Do not port the bug" is an unusual instruction — the default migration reflex is to preserve legacy behavior exactly, and a faithful port would reproduce the accumulating staging rows. Recording the bug and the instruction together converts a silent defect into a deliberate, documented behavior change that a reviewer can verify.

Risk #5 is the only entry that ends in a question rather than an answer: confirm drop scope with the scope owner. It is paired with the unresolved scope owner field in §1 — one open item blocking another, which is exactly why the §1 placeholder is not filled in with a guess.

---

## How This Spec Is Used Downstream

| Downstream spec | What it takes from the product scope |
|---|---|
| **As-is analysis** | The object inventory (§3) defines exactly what to examine; §4 stops the lineage traversal. §5 becomes as-is §2 Consumers; §6 becomes as-is §5 Calculations; §3.1 becomes as-is §3 Model. Risks #1 and #2 tell the as-is which details to verify in source code. |
| **Product transformation rules** | Risks become rules — Risk #2 (spaces in names) drives naming rules; Risk #3 (SEQUENCE) drives the identity/lineage-key rule; Risk #1 drives the staging overwrite rule; Risk #6 drives Workflow task-dependency rules |
| **To-be design** | §7 target boundaries set the platform, catalog, and bronze/silver/gold layering. §3 objects map one-to-one onto target artifacts. Risk #1's "do not port the bug" appears as an explicit intentional behavior change. |
| **Development plan — requirements** | Ownership boundaries become functional requirements (Purchase reads dimensions, does not load them). §5 consumers become report-reconnection requirements. |
| **Development plan — design** | §7 target orchestration drives the Workflow task graph, including the dimension-before-fact dependency from Risk #6 |
| **Development plan — tasks** | Every §3 object generates at least one task; the key=0 sentinel bootstrap task traces to Risk #5; report reconnection tasks trace to §5 |
| **Catalog** | Product identity (§1), description (§2), priority and sequencing (§8) |
| **Reviewers / QA** | §3 and §4 together are the **completeness checklist** — an artifact outside §3 is scope creep; a §3 object with no artifact is a gap |

---

## File Reference

| File | Location |
|---|---|
| `product-scope.md` | `products/Purchase/input/product-scope.md` |

A single markdown file containing all 9 sections — typically 150–200 lines, making it the most compact product-level spec in the TCP flow. It is deliberately short: the scope decides boundaries, and the as-is that follows supplies the depth.

Three `[USER INPUT REQUIRED]` placeholders remain open — scope owner (§1), temporal boundary (§7), and organizational boundary (§7). They should be resolved with the scope owner before the development plan is finalized, since Risk #5 depends on that sign-off.
