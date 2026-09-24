# Purchase — Product Scope

## 1 Identity

| Field | Value |
|---|---|
| Product name | Purchase |
| Parent project | Inventory_Stock_Project |
| Scope owner | [USER INPUT REQUIRED] |
| Discovery mode | hybrid — Pattern A (migVisor Explainer MCP grounded, base node: `wideworldimportersdw.fact.purchase`) |
| Plan stage | scope |

---

## 2 Description

Purchase is the primary data product for the Inventory_Stock_Project migration. It covers the **procurement order transaction domain** of the WideWorldImporters data warehouse: the core fact table (`fact.purchase`), its conformed dimension read dependencies (`dimension.supplier`, `dimension.stock item`, `dimension.date`), the SSIS-orchestrated integration staging layer that loads it, and the BI reports that consume it.

The product moves this entire procurement domain from Microsoft SQL Server 2014 to a Databricks Delta Lake lakehouse, replacing fragile SSIS batch logic — including a confirmed staging-truncation bug — with maintainable, observable Delta pipelines.

`dimension.supplier` and `dimension.stock item` are **read dependencies** of the Purchase ETL (SCD-2 surrogate key lookups in `migratestagedpurchasedata`) but their load procedures are owned by other products. The Purchase product scope covers consumption of these dimensions only; it does not own or migrate their load logic.

---

## 3 Objects in Scope

### 3.1 Core Fact Table

| Object | Type | Role |
|---|---|---|
| `wideworldimportersdw.fact.purchase` | table | Base node — purchase order line items |

Known schema: `PurchaseKey` (BIGINT IDENTITY PK), `Date Key` (date FK), `Supplier Key` (int FK), `Stock Item Key` (int FK), `WWI Purchase Order ID` (int), `Ordered Outers` (int), `Ordered Quantity` (int), `Received Outers` (int), `Package` (nvarchar), `Is Order Finalized` (bit), `Lineage Key` (int).

### 3.2 Conformed Dimensions

| Object | Type | Ownership | Notes |
|---|---|---|---|
| `wideworldimportersdw.dimension.supplier` | table | External (not Purchase-owned) | SCD-2 read dependency — used for surrogate key lookup in `migratestagedpurchasedata`; ETL load owned by separate product |
| `wideworldimportersdw.dimension.stock item` | table | External (not Purchase-owned) | SCD-2 read dependency — used for surrogate key lookup in `migratestagedpurchasedata`; ETL load owned by separate product; object name contains a space |
| `wideworldimportersdw.dimension.date` | table | Shared infrastructure | FK target for `Date Key`; pre-populated by shared infrastructure layer; not Purchase-owned |

### 3.3 Integration Staging Layer

| Object | Type | Role | Notes |
|---|---|---|---|
| `wideworldimportersdw.integration.purchase_staging` | table | Staging area for purchase data before fact insert | Never correctly truncated before a run due to SSIS bug (see Risk #1) |
| `wideworldimportersdw.integration.etl cutoff` | table | ETL watermark / cutoff control | Shared infrastructure; consumed by Purchase |
| `wideworldimportersdw.integration.lineage` | table | ETL run log | Shared infrastructure; consumed by Purchase |
| `wideworldimportersdw.integration.migratestagedpurchasedata` | stored procedure | Resolves SCD-2 surrogate keys for `supplier` and `stock item`, upserts into `fact.purchase`, updates `lineage` and `etl cutoff` | Core ETL logic — must be rewritten as Databricks Delta `MERGE INTO` |
| `wideworldimportersdw.integration.getlastetlcutofftime` | stored procedure | Reads ETL cutoff watermark | Shared infrastructure; called by Purchase pipeline |
| `wideworldimportersdw.integration.getlineagekey` | stored procedure | Generates lineage run key via `sequences.lineagekey` | Shared infrastructure; called by Purchase pipeline |
| `wideworldimportersdw.application.configuration_reseedetl` | stored procedure | Purchase-domain portions only: TRUNCATEs `fact.purchase`; inserts key=0 sentinel rows into `dimension.supplier` and `dimension.stock item`; resets ETL cutoff to base time | Testing/reseed utility — confirm drop scope with scope owner before migration; if retained, sentinel rows must be pre-seeded in Databricks target |

### 3.4 Sequences / Infrastructure

| Object | Type | Role | Notes |
|---|---|---|---|
| `wideworldimportersdw.sequences.lineagekey` | sequence | Generates lineage run keys for all ETL migrate procedures | Shared infrastructure; SQL Server SEQUENCE object — no native Databricks equivalent; must be redesigned |

### 3.5 SSIS Orchestration Pipeline (Purchase container)

| Object | Type | Role | Notes |
|---|---|---|---|
| `demo_ssis…pipeline_dailyetlmain` | workflow | Master daily ETL workflow | Shared pipeline; Purchase container runs within it |
| `demo_ssis…pipeline_item_set tablename to purchase` | dataflow | Sets the `tablename` variable before the purchase load container executes | |
| `demo_ssis…pipeline_item_truncate purchase_staging` | dataflow | Intended to truncate `integration.purchase_staging` before load | **⚠ Bug:** dataflow is coded to `DELETE FROM Integration.Order_Staging` instead of `Integration.Purchase_Staging` — stale purchase staging rows accumulate across runs; Databricks replacement must implement correct overwrite/truncate |
| `demo_ssis…pipeline_item_extract updated purchase data to staging` | dataflow | Loads incremental purchase updates from source into `purchase_staging` | |
| `demo_ssis…pipeline_item_migrate staged purchase data` | dataflow | Calls `integration.migratestagedpurchasedata` to resolve keys and upsert into `fact.purchase` | |

### 3.6 BI Reports (Downstream Consumers)

| Report | Reads | Notes |
|---|---|---|
| `wwidw purchase and sale per stockitem dynamic` | `fact.purchase` | Cross-domain report; also reads `fact.sale` (Sales_Orders product) |
| `wwidw-ordered-by-supplier` | `fact.purchase`, `dimension.supplier` | Purchase-specific supplier report |

---

## 4 Out-of-Scope Objects

| Object | Reason |
|---|---|
| `fact.sale`, `fact.order`, `fact.movement`, `fact.transaction`, `fact.stock holding` | Belong to Sales_Orders, Inventory_Movement, or Finance_Analytics products |
| `integration.migratestaged*data` procedures other than `migratestagedpurchasedata` | Load facts not in this product scope |
| `integration.*_staging` tables other than `purchase_staging` | Staging for out-of-scope facts |
| `dimension.supplier` ETL load procedure (`migratestagedsupplierdata`) | ETL load owned by separate product — Purchase only reads this dimension |
| `dimension.stock item` ETL load procedure | ETL load owned by separate product — Purchase only reads this dimension |
| `dimension.customer`, `dimension.city`, `dimension.employee`, `dimension.payment method`, `dimension.transaction type` | Belong to Sales_Orders product; not referenced by Purchase ETL |
| `analytics.*` views and tables | Finance/Analytics domain — separate product |
| `application.configuration_reseedetl` (non-Purchase portions) | Only the Purchase-domain portions (TRUNCATE `fact.purchase`, supplier/stock item key=0 sentinel rows, cutoff reset) are in scope — all other domain reseeds are excluded |
| `application.configuration_applypolybase`, `configuration_populatelargesaletable`, `configuration_applypartitionedcolumnstoreindexing` | SQL Server–specific config procedures not related to Purchase domain |
| `sequences.reseedallsequences`, `sequences.reseedsequencebeyondtablevalues` | Reseed utilities — review at implementation; likely drop scope |
| `dbo.*` | SSMS diagram objects and sample/test artifacts — excluded per project scope |
| SSIS pipeline items for out-of-scope facts (sale, order, movement, stockholding, etc.) | Follow their respective out-of-scope facts |

---

## 5 Consumers

| Consumer | Type | Objects Consumed | Notes |
|---|---|---|---|
| `wwidw purchase and sale per stockitem dynamic` | BI Report (Power BI / SSRS) | `fact.purchase` (cross-domain; also reads `fact.sale`) | Cross-domain; requires coordinated cutover with Sales_Orders product |
| `wwidw-ordered-by-supplier` | BI Report (Power BI / SSRS) | `fact.purchase`, `dimension.supplier` | Purchase-specific; no cross-domain dependency |
| `analytics.v_ordertoyearanalytics` | Analytical View (SQL Server) | `fact.purchase` via correlated subquery on `Package` column | **Cross-domain — out-of-scope for Purchase.** Driven by `fact.order`; cannot be rebuilt by this product alone. Coordination with Order product team required before migration. If `Package` column is renamed, this view's predicate must be updated. |

---

## 6 Calculation Surface

This product is **moderately calculation-light** at the analytical layer but **ETL-logic-heavy** in its migration procedure:

- **Staging merge procedure:** `integration.migratestagedpurchasedata` contains T-SQL MERGE / INSERT-SELECT logic that (a) resolves SCD-2 surrogate keys for `dimension.supplier` and `dimension.stock item`, (b) upserts rows into `fact.purchase`, (c) injects a lineage key, and (d) updates the ETL cutoff watermark. This logic must be fully reimplemented as a Databricks Delta `MERGE INTO` operation with Python/SQL orchestration.
- **ETL cutoff watermarking:** `integration.getlastetlcutofftime` reads the incremental high-watermark from `integration.etl cutoff` — must be re-expressed as a Delta control table read in the Databricks pipeline.
- **Lineage key generation:** `integration.getlineagekey` calls `sequences.lineagekey` (SQL Server SEQUENCE) — must be redesigned as a `GENERATED ALWAYS AS IDENTITY` column or UUID-based run ID in the Databricks lineage replacement table.
- **Staging truncation:** the Purchase pipeline must implement an explicit overwrite/truncate of the purchase staging area at the start of each run, correcting the legacy SSIS bug.
- No scalar UDFs or analytics views are owned by this product. The two BI reports read `fact.purchase` directly; no intermediate calculation layer exists on the purchase side.

---

## 7 Boundaries

| Boundary | Value |
|---|---|
| Temporal | Inherits project default — [USER INPUT REQUIRED] (date range from `integration.etl cutoff` watermark table; confirm with scope owner) |
| Organizational | [USER INPUT REQUIRED] (owning team within Inventory_Stock_Project) |
| System (source) | `wideworldimportersdw` on Microsoft SQL Server 2014 — schemas: `fact`, `dimension`, `integration`, `sequences`, `application` (Purchase-domain portions only) |
| System (target) | Databricks Delta Lake — catalog: `inventory_stock` (or project-aligned catalog name), layers: bronze/silver/gold (staging → conformed dimension → fact) |
| ETL orchestration (source) | SSIS `demo_ssis…pipeline_dailyetlmain` — Purchase container within nightly batch |
| ETL orchestration (target) | Databricks Workflow — nightly Delta pipeline replacing SSIS Purchase container; task dependencies must enforce dimension load completion before Purchase fact load |

---

## 8 Priority and Sequencing

| Field | Value |
|---|---|
| Priority | PRIMARY — first product in Inventory_Stock_Project |
| Rationale | Core procurement domain; directly feeds purchase BI reports and cross-domain stock-item analytics |
| Dependencies | `dimension.supplier` and `dimension.stock item` must be fully loaded (SCD-2 current rows present) before the Purchase ETL runs; these dimensions are owned by separate products — Databricks Workflow task dependencies must enforce this ordering |
| Successor products | Inventory_Movement (reuses `dimension.stock item` and `dimension.supplier` already migrated by their respective owning products) |

---

## 9 Known Migration Risks (Product-Level)

| # | Risk | Implication |
|---|---|---|
| 1 | `demo_ssis…pipeline_item_truncate purchase_staging` **bug**: dataflow is coded to `DELETE FROM Integration.Order_Staging` instead of `Integration.Purchase_Staging` — purchase staging is never truncated before a run; stale rows accumulate | Critical ETL correctness defect. The Databricks replacement must implement a correct overwrite/truncate of the purchase staging Delta table at the start of each incremental run. Do not port the bug. |
| 2 | `dimension.supplier` and `dimension.stock item` contain **spaces** in object names | Must be renamed to `supplier` and `stock_item` under Databricks snake_case convention. All downstream references in `migratestagedpurchasedata` logic and BI report queries must be updated accordingly. |
| 3 | `sequences.lineagekey` — SQL Server SEQUENCE object with no native Databricks equivalent | Redesign as a `GENERATED ALWAYS AS IDENTITY` column in the Databricks lineage control table, or use a UUID-based ETL run ID. Coordinate with other products sharing this sequence. |
| 4 | `integration.migratestagedpurchasedata` — T-SQL MERGE with SCD-2 key resolution, lineage key injection, and ETL cutoff watermarking | Must be fully rewritten as a Databricks Delta `MERGE INTO` operation with Python/SQL orchestration. Preserve idempotency semantics of the original upsert logic. |
| 5 | `application.configuration_reseedetl` (Purchase portions) — TRUNCATEs `fact.purchase` and inserts key=0 sentinel rows | Likely a testing/reseed utility only — confirm drop scope with scope owner before migration. If retained, sentinel rows must be pre-seeded in the Databricks `fact_purchase` Delta table at initialization. |
| 6 | `dimension.supplier` and `dimension.stock item` ETL load is **not Purchase-owned** | Purchase ETL has a hard runtime dependency on these dimensions being current. Databricks Workflow task graph must enforce that dimension load tasks for both `supplier` and `stock_item` complete successfully before the Purchase fact load task begins. |
| 7 | `wwidw purchase and sale per stockitem dynamic` is a **cross-domain BI report** reading both `fact.purchase` (Purchase) and `fact.sale` (Sales_Orders) | Report migration requires coordinated cutover of both products; partial migration will break or require a bridging view across SQL Server and Databricks. Align cutover timing with Sales_Orders product team. |
