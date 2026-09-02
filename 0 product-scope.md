# Purchase — Product Scope

## 1 Identity

| Field | Value |
|---|---|
| Product name | Purchase |
| Parent project | GlobalPurchase_Project |
| Scope owner | [USER INPUT REQUIRED] |
| Discovery mode | hybrid — Pattern A (migVisor Explainer MCP grounded, base node: `197f0cba-80b1-4837-b448-3268bdf6649c` → `wideworldimportersdw.fact.purchase`) |
| Plan stage | scope |

---

## 2 Description

Purchase is the primary data product for the GlobalPurchase_Project migration. It covers the **purchase order domain** of the WideWorldImporters data warehouse: the core fact table (`fact.purchase`), its three dimensions declared as FK constraints in the DDL (`dimension.supplier`, `dimension.stock item`, `dimension.date`), the SSIS-orchestrated integration staging layer that loads the purchase fact, and the BI reports that consume it. Conformed dimensions and shared infrastructure (`etl cutoff`, `lineage`, `dimension.date`) are migrated by a shared infrastructure layer and consumed by this product.

The product moves this entire domain from Microsoft SQL Server 2014 to a Databricks Delta Lake lakehouse.

---

## 3 Objects in Scope

### 3.1 Core Fact Table

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.fact.purchase` | `197f0cba-80b1-4837-b448-3268bdf6649c` | table | Base node — purchase order line items. Columns: `Purchase Key` (IDENTITY), `Date Key` (date, FK→`dimension.date`), `Supplier Key` (FK→`dimension.supplier`), `Stock Item Key` (FK→`dimension.stock item`), `WWI Purchase Order ID`, `Ordered Outers`, `Ordered Quantity`, `Received Outers`, `Package`, `Is Order Finalized`, `Lineage Key` |

### 3.2 Conformed Dimensions

Read dependencies for `migratestagedpurchasedata` — not ETL-owned by Purchase. `dimension.date` is pre-populated shared infrastructure; `dimension.supplier` and `dimension.stock item` are maintained by their own dimension ETL procedures (out of scope — see §4).

| Object | ID | Type | Notes |
|---|---|---|---|
| `wideworldimportersdw.dimension.supplier` | `97866e9f-bb34-4e79-8413-93721cda0796` | table | Read dependency — SCD-2 lookup in `migratestagedpurchasedata` |
| `wideworldimportersdw.dimension.stock item` | `9266888d-6063-408f-8284-e02ba1f92df3` | table | Read dependency — SCD-2 lookup in `migratestagedpurchasedata` |
| `wideworldimportersdw.dimension.date` | `83e9487a-1924-45c1-a861-6c4783b0bc93` | table | FK target for `[Date Key]` — **shared infrastructure, pre-populated; migrated once by shared infra layer** |

### 3.3 Integration Staging Layer

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.integration.purchase_staging` | `a016e5b7-ab70-4e45-af51-b70ae237c7e2` | table | Staging for purchase data; updated in-place by `migratestagedpurchasedata` to resolve supplier and stock item surrogate keys before fact insert |
| `wideworldimportersdw.integration.etl cutoff` | `757aa9c0-0b80-4291-9de6-bbdba3068aaf` | table | ETL watermark — read and written by `migratestagedpurchasedata`. **Shared infrastructure — migrated once by shared infra layer; consumed by Purchase and all other products.** |
| `wideworldimportersdw.integration.lineage` | `a3caa39a-a18f-4e0b-bbb7-d933f8cee8a2` | table | ETL lineage / run log — read/written by `migratestagedpurchasedata`. **Shared infrastructure — migrated once by shared infra layer; consumed by Purchase and all other products.** |
| `wideworldimportersdw.integration.migratestagedpurchasedata` | `b79b9b8c-99af-4d42-8e97-e9206b8d5f02` | procedure | Resolves `[Supplier Key]` and `[Stock Item Key]` in `purchase_staging` via SCD-2 correlated subquery; DELETEs existing `fact.purchase` rows by `[WWI Purchase Order ID]`; INSERTs from staging; updates `lineage` and `etl cutoff` |
| `wideworldimportersdw.integration.getlastetlcutofftime` | — | procedure | Reads ETL cutoff watermark — called by purchase SSIS pipeline. **Shared infrastructure — called by all migrate procedures across all domains.** |
| `wideworldimportersdw.integration.getlineagekey` | — | procedure | Calls `sequences.lineagekey` for run ID — called by purchase ETL. **Shared infrastructure — called by all migrate procedures across all domains.** |
| `wideworldimportersdw.application.configuration_reseedetl` | `fe4d64b7-b146-4b4f-8495-fd7f770e0961` | procedure | Full warehouse reset utility — **Purchase-domain portions in scope**: (1) TRUNCATE `fact.purchase`; (2) DELETE + INSERT `key=0` Unknown sentinel row into `dimension.supplier` and `dimension.stock item`; (3) reset `integration.[ETL Cutoff]` to base cutoff time. Sentinel rows are required by `migratestagedpurchasedata` (`COALESCE(..., 0)` on failed key lookup). Cross-domain truncations (other facts, other dimensions) are not in scope — procedure is not migrated as a whole. |

### 3.4 Sequences / Infrastructure

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.sequences.lineagekey` | `8fe29a7a-9e66-45a8-96d2-9ef427d7fb0a` | sequence | Generates lineage run keys for ETL — called by `getlineagekey`. **Shared infrastructure — used by all migrate procedures across all domains.** |

### 3.5 Analytics Views (Read from Core Facts)

No analytics views are owned by Purchase. `analytics.v_ordertoyearanalytics` reads `fact.purchase` via a correlated subquery but is driven by `fact.order` and cannot be rebuilt by this product alone — see §5 (Consumers) and §4 (Out-of-Scope).

### 3.6 SSIS Orchestration Pipeline

Purchase container items within the shared master workflow only. Supplier and stock item dimension containers run in the same master pipeline but follow their own ETL procedures — not Purchase-owned.

| Object | ID | Type | Role |
|---|---|---|---|
| `demo_ssis…pipeline_dailyetlmain` | — | workflow | Master daily ETL workflow (shared; Purchase container runs within it) |
| `demo_ssis…pipeline_item_set tablename to purchase` | `e630fc7c-26b8-41a1-9701-342991f19c46` | dataflow | Sets `tablename` variable before the purchase load container |
| `demo_ssis…pipeline_item_truncate purchase_staging` | `88c761dd-8756-453e-96b2-e587e568b9e3` | dataflow | Intended to truncate `purchase_staging` — ⚠ confirmed bug: executes `DELETE FROM Integration.Order_Staging` instead |
| `demo_ssis…pipeline_item_extract updated purchase data to staging` | `5b1ac205-a17d-4ead-83e7-14d95b112a54` | dataflow | Loads purchase updates into `purchase_staging` |
| `demo_ssis…pipeline_item_migrate staged purchase data` | `9492a03b-5837-41c1-bc25-f00592b94c8c` | dataflow | Calls `migratestagedpurchasedata` |

### 3.7 BI Reports (Downstream Consumers)

| Report | ID | Reads |
|---|---|---|
| `wwidw purchase and sale per stockitem dynamic.wwidw purchase and sale per stockitem dynamic` | `8db5c99c-6f81-4021-95ff-5b33f9f1af5b` | `fact.purchase` |
| `wwidw-ordered-by-supplier.wwidw-ordered-by-supplier` | `f8751a7d-43dc-4fb2-be8e-c7b64774469c` | `fact.purchase`, `dimension.supplier` |

---

## 4 Out-of-Scope Objects

| Category | Reason |
|---|---|
| All other fact tables (`fact.sale`, `fact.order`, `fact.movement`, `fact.stock holding`, `fact.transaction`) and their staging tables, migrate procedures, and SSIS containers | Other fact domains — not in the purchase ETL path |
| `dimension.customer`, `dimension.city`, `dimension.employee`, `dimension.payment method`, `dimension.transaction type` | No FK from `fact.purchase`; not read by `migratestagedpurchasedata` |
| `integration.supplier_staging`, `integration.stockitem_staging`, `integration.migratestagedsupplierdata`, `integration.migratestagedstockitemdata` and their SSIS containers | Shared dimension maintenance — not Purchase-owned; ETL ordering dependency noted in §8 |
| `integration.populatedatedimensionforyear`, `integration.generatedatedimensioncolumns`, `sequences.supplierkey`, `sequences.stockitemkey`, `sequences.reseedallsequences`, `sequences.reseedsequencebeyondtablevalues` | Shared infrastructure utilities — no purchase-specific logic |
| All analytics views except those in §5 (`analytics.movementdetails`, `analytics.orderdetails`, `analytics.customersalessummary`, `analytics.v_ordertosupplyanalytics`, `analytics.v_ordertoyearanalytics`, `dbo.*`) | Driving fact is not `fact.purchase`; `v_ordertoyearanalytics` is cross-domain — see §5 |
| `wideworldimporters.integration.getpurchaseupdates` and its OLTP source dependencies (`purchasing.purchaseorders`, `purchasing.purchaseorderlines`, `warehouse.stockitems`, `warehouse.packagetypes`) | Source-side extraction procedure in the OLTP database — called by the SSIS extract step. In the target architecture this is replaced by a native Databricks ingestion connector reading directly from the OLTP source; the SQL Server procedure does not migrate. |
| `application.configuration_populatelargesaletable`, `application.configuration_applypartitionedcolumnstoreindexing`, `application.configuration_applypolybase`, `application.configuration_reseedetl` (cross-domain portions) | SQL Server admin/config procedures unrelated to purchase domain |

---

## 5 Consumers

| Consumer | Type | Objects Consumed | Notes |
|---|---|---|---|
| wwidw purchase and sale per stockitem dynamic | BI Report | `fact.purchase` | Purchase-owned downstream |
| wwidw-ordered-by-supplier | BI Report | `fact.purchase`, `dimension.supplier` | Purchase-owned downstream |
| `analytics.v_ordertoyearanalytics` | Cross-domain analytical view | `fact.purchase` via correlated subquery on `Package` | Driven by `fact.order` — MCP-confirmed. Not rebuilt by this product; coordination required with Order product. Out-of-scope for migration ownership (see §4). |

---

## 6 Calculation Surface

This product is **moderately calculation-heavy**:

- **Staging key resolution:** `migratestagedpurchasedata` resolves `[Supplier Key]` and `[Stock Item Key]` inline via correlated SCD-2 subqueries with `[Valid From]`/`[Valid To]` range filters against `dimension.supplier` and `dimension.stock item` — must be redesigned as a Databricks join with a Delta-native SCD strategy. Requires `dimension.supplier` and `dimension.stock item` to be fully loaded before the purchase fact load runs (cross-product ETL ordering dependency).
- **DELETE + INSERT pattern:** `migratestagedpurchasedata` deletes existing `fact.purchase` rows by `[WWI Purchase Order ID]` then re-inserts all staging rows — must be rewritten as a Databricks Delta `MERGE INTO`.
- **Lineage and cutoff management:** `migratestagedpurchasedata` reads `integration.lineage` for `@LineageKey` and updates both `lineage.[Data Load Completed]` and `etl cutoff.[Cutoff Time]` within a single transaction — both tables are shared infrastructure (migrated once by shared infra layer); Purchase consumes the Delta equivalents.

---

## 7 Boundaries

| Boundary | Value |
|---|---|
| Temporal | Inherits project default — [USER INPUT REQUIRED] (date range from `integration.etl cutoff` watermark table; confirm with scope owner) |
| Organizational | [USER INPUT REQUIRED] (owning team within GlobalPurchase_Project) |
| System (source) | `wideworldimportersdw` on Microsoft SQL Server 2014 — schemas: `fact`, `dimension`, `integration`, `sequences`, `application` (reseed utility only) |
| System (target) | Databricks Delta Lake — catalog: `globalpurchase`, layers: bronze/silver/gold (staging → dimension → fact → analytics) |
| ETL orchestration (source) | SSIS `demo_ssis.folder_ssis-project.pipeline_dailyetlmain` — nightly batch; purchase, supplier, and stock item containers run within the shared master workflow |
| ETL orchestration (target) | Databricks workflow (nightly Delta pipeline replacing the purchase SSIS container within `pipeline_dailyetlmain`) |

---

## 8 Priority and Sequencing

| Field | Value |
|---|---|
| Priority | PRIMARY — first product in GlobalPurchase_Project |
| Rationale | Core procurement domain; feeds supplier-facing BI reports and cross-domain analytics |
| Dependencies | ETL ownership for `dimension.stock item` must be agreed before as-is analysis — it is read by five fact migrate procedures across the database; `dimension.supplier` ETL must complete before `fact.movement` and `fact.transaction` loads in other products |
| Successor products | [USER INPUT REQUIRED] |

---

## 9 Known Migration Risks (Product-Level)

| # | Risk | Implication |
|---|---|---|
| 1 | **SSIS bug — `pipeline_item_truncate purchase_staging`** executes `DELETE FROM Integration.Order_Staging` instead of `Integration.Purchase_Staging` | `purchase_staging` is never truncated before the nightly extract; stale purchase rows accumulate undetected. Must be corrected in the Databricks replacement pipeline from day one. |
| 2 | `dimension.stock item` — table name contains a **SPACE** (`Dimension.[Stock Item]`) | Requires bracket-quoting in T-SQL; must be renamed (e.g., `stock_item`) under Databricks snake_case convention — impacts all five fact migrate procedures across the database. |
| 3 | `dimension.supplier` — read by `migratestagedpurchasedata`, `migratestagedmovementdata`, and `migratestagedtransactiondata` | Supplier ETL (`migratestagedsupplierdata`) must complete before purchase, movement, and transaction fact loads; cross-product ETL ordering constraint requires coordination. |
| 4 | `integration.migratestagedpurchasedata` — DELETE + INSERT with inline SCD-2 correlated subqueries | No direct Databricks equivalent; must be split into: (a) dimension key resolution join, (b) Delta `MERGE INTO` for fact upsert. Inline correlated subqueries perform poorly at scale. |
| 5 | `migratestagedsupplierdata` and `migratestagedstockitemdata` — SCD-2 via UPDATE `[Valid To]` + INSERT (not MERGE) | Shared infrastructure procedures (not Purchase-owned — see §4). Must be rewritten as Delta `MERGE INTO` with valid-from/to logic by the product that owns supplier/stock item dimension ETL. Purchase depends on these completing successfully before the purchase fact load runs. |
| 6 | `sequences.lineagekey`, `sequences.supplierkey`, `sequences.stockitemkey` — SQL Server SEQUENCE objects | No native Databricks SEQUENCE equivalent; must be redesigned (`GENERATED ALWAYS AS IDENTITY` columns, or UUID/timestamp-based keys). Coordinate `lineagekey` redesign across all products. |
| 7 | `application.configuration_reseedetl` — `key=0` Unknown sentinel rows for `dimension.supplier` and `dimension.stock item` | `migratestagedpurchasedata` uses `COALESCE(..., 0)` on failed key lookups, relying on key=0 rows existing. These sentinel rows must be explicitly inserted during Databricks pipeline initialization — there is no equivalent reset procedure in the target. |
| 8 | `analytics.v_ordertoyearanalytics` — reads `fact.purchase` via correlated subquery alongside `fact.order` and `fact.sale` | Cross-domain view that cannot be rebuilt by this product alone; requires coordination with the products owning `fact.order` and `fact.sale`. |
