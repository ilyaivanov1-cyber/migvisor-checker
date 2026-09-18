# Inventory_Stock_Project — Modernization Plan

## 1 Identity

| Field | Value |
|---|---|
| Project name | Inventory_Stock_Project |
| Scope owner | [USER INPUT REQUIRED] |
| Intake mode | hybrid (Pattern A — migVisor Explainer MCP grounded) |
| Plan stage | modernization-plan |

## 2 Description / Rationale

Modernize the legacy grocery-retail procurement and inventory workload onto Databricks. The legacy system runs a nightly batch that loads purchase order line items into `fact.purchase` via SSIS-orchestrated staging, resolving SCD-2 dimension surrogate keys against `dimension.supplier` and `dimension.stock item`.

The migration moves this procurement-analytics workload to a Databricks lakehouse to:

- Replace fragile SSIS batch logic (including a known staging-truncation bug) with maintainable, observable Delta pipelines.
- Gain scalability for growing purchase order volumes.
- Decouple the procurement analytical layer from the shared SQL Server DW.
- Align the purchase domain with the lakehouse conventions already established by the Sales_Orders migration.

## 3 Source Systems

| Attribute | Value |
|---|---|
| Source database platform | Microsoft SQL Server 2014 (T-SQL) |
| Source database | `wideworldimportersdw` (the WideWorldImporters sample data warehouse) |
| Access method | migVisor Explainer MCP (lineage + source retrieval) |

Schemas in scope:

| Schema | Role |
|---|---|
| `fact` | Fact table — `fact.purchase` |
| `dimension` | Conformed dimensions — `dimension.supplier`, `dimension.stock item`, `dimension.date` |
| `integration` | ETL / staging + migrate-procedure layer |
| `application` | T-SQL configuration / parameter objects (Purchase-domain portions only) |
| `sequences` | Surrogate / lineage key sequence objects |

### 3.1 Known Migration Risks / Observations (from Explainer)

| # | Observation | Implication |
|---|---|---|
| 1 | `pipeline_item_truncate purchase_staging` **bug**: the SSIS dataflow is coded to `DELETE FROM Integration.Order_Staging` instead of `Integration.Purchase_Staging`. Purchase staging is therefore never truncated before a run — stale rows can accumulate. | Critical ETL correctness defect: the Databricks replacement must implement a proper truncate/overwrite of the purchase staging table at the start of each run. |
| 2 | `dimension.supplier` and `dimension.stock item` contain **spaces** in object names. | Require quoting/renaming to `supplier` and `stock_item` under Databricks snake_case convention. |
| 3 | `sequences.lineagekey` is a SQL Server SEQUENCE object; no native Databricks equivalent. | Surrogate/lineage key generation must be redesigned (e.g., `GENERATED ALWAYS AS IDENTITY` column or UUID-based run ID). |
| 4 | `integration.migratestagedpurchasedata` resolves SCD-2 dimension keys and upserts into `fact.purchase` via T-SQL MERGE / INSERT-SELECT logic with lineage key injection and ETL cutoff watermarking. | Must be rewritten as a Databricks Delta `MERGE INTO` operation with Python/SQL orchestration. |
| 5 | `application.configuration_reseedetl` (Purchase portions): TRUNCATEs `fact.purchase` and inserts key=0 sentinel rows into `dimension.supplier` and `dimension.stock item`; resets ETL cutoff to base time. | Likely a testing/reseed-only utility — confirm drop scope with scope owner before migration; sentinel rows must be pre-seeded in the Databricks target if retained. |
| 6 | `dimension.supplier` and `dimension.stock item` are **read dependencies** of the Purchase ETL (SCD-2 lookups in `migratestagedpurchasedata`) but their load procedures are owned by other products (Inventory_Stock / Sales_Orders respectively). | ETL sequencing dependency: Purchase load must run after dimension loads complete; Databricks Workflow task dependencies must reflect this ordering. |

## 4 Target System

| Attribute | Value |
|---|---|
| Target platform | Databricks (Delta Lake lakehouse) |
| Schema naming convention | `catalog.schema.table`, lowercase_snake_case (e.g., `globalsales.<layer>.<entity>`) |

## 5 Key Entities

- Purchase order line items (`fact.purchase`)
- Supplier (`dimension.supplier`)
- Stock Item (`dimension.stock item`)
- Date (`dimension.date`)

## 6 In-Scope Objects

Confirmed present in `wideworldimportersdw` via migVisor Explainer. Grouped by schema.

### 6.1 fact

| Object | Type |
|---|---|
| `fact.purchase` | table |

### 6.2 dimension

| Object | Type | Notes |
|---|---|---|
| `dimension.supplier` | table | SCD-2 read dependency (ETL not Purchase-owned) |
| `dimension.stock item` | table | SCD-2 read dependency (ETL not Purchase-owned); name contains space |
| `dimension.date` | table | FK target for Date Key; shared infrastructure — pre-populated by shared infra layer |

### 6.3 integration

| Object | Type |
|---|---|
| `integration.purchase_staging` | table |
| `integration.etl cutoff` | table |
| `integration.lineage` | table |
| `integration.migratestagedpurchasedata` | procedure |
| `integration.getlastetlcutofftime` | procedure |
| `integration.getlineagekey` | procedure |

### 6.4 application

| Object | Type | Notes |
|---|---|---|
| `application.configuration_reseedetl` | procedure | Purchase-domain portions only: TRUNCATE `fact.purchase`; insert key=0 sentinel rows; reset ETL cutoff |

### 6.5 sequences

| Object | Type |
|---|---|
| `sequences.lineagekey` | sequence |

### 6.6 SSIS Orchestration Pipeline (Purchase container)

| Object | Type | Notes |
|---|---|---|
| `demo_ssis…pipeline_dailyetlmain` | workflow | Master daily ETL workflow (shared; Purchase container runs within it) |
| `demo_ssis…pipeline_item_set tablename to purchase` | dataflow | Sets tablename variable before the purchase load container |
| `demo_ssis…pipeline_item_truncate purchase_staging` | dataflow | **⚠ Bug:** coded to DELETE FROM `Integration.Order_Staging` — should target `Purchase_Staging` |
| `demo_ssis…pipeline_item_extract updated purchase data to staging` | dataflow | Loads purchase updates into `purchase_staging` |
| `demo_ssis…pipeline_item_migrate staged purchase data` | dataflow | Calls `migratestagedpurchasedata` |

## 7 Out-of-Scope Items

| Item | Reason |
|---|---|
| `fact.sale`, `fact.order`, `fact.movement`, `fact.transaction`, `fact.stock holding` | Belong to Sales_Orders, Inventory_Movement, or Finance_Analytics products |
| `integration.migratestaged*data` procedures other than `migratestagedpurchasedata` | Load facts not in this product scope |
| `integration.*_staging` tables other than `purchase_staging` | Staging for out-of-scope facts |
| `dimension.customer`, `dimension.city`, `dimension.employee`, `dimension.payment method`, `dimension.transaction type` | Belong to Sales_Orders product |
| `analytics.*` views and tables | Finance/Analytics domain — separate product |
| `application.configuration_applypolybase`, `configuration_populatelargesaletable`, `configuration_applypartitionedcolumnstoreindexing` | SQL Server–specific config procedures not related to Purchase domain |
| `dbo.*` | SSMS diagram objects and sample/test artifacts — excluded per project scope |
| `sequences.reseedallsequences`, `sequences.reseedsequencebeyondtablevalues` | Reseed utilities — review at implementation; likely drop scope |

## 8 Boundaries

| Boundary | Value |
|---|---|
| Temporal | [USER INPUT REQUIRED] (date range of data to migrate — confirm from `integration.etl cutoff` watermark) |
| Organizational | [USER INPUT REQUIRED] (owning team / department) |
| System | Source database `wideworldimportersdw` on Microsoft SQL Server 2014; target Databricks lakehouse. |

## 9 Data-Product Inventory

Candidate data products within Inventory_Stock_Project.

| Product | Status | Description | Sources |
|---|---|---|---|
| Purchase | PRIMARY — first product | Purchase order transaction domain over the WWI star schema. | `fact.purchase` + conformed dimensions (`supplier`, `stock item`, `date`) and the integration-layer staging/migrate procedure that loads it. |
| Inventory_Movement | Future candidate | Stock movement domain. | `fact.movement` + `dimension.stock item`, `dimension.supplier` dimensions. |

## 10 Stakeholders

| Role | Value |
|---|---|
| Project owner | [USER INPUT REQUIRED] |
| Business lead | [USER INPUT REQUIRED] |
| Technical lead | [USER INPUT REQUIRED] |
| Sign-off required | [USER INPUT REQUIRED] |

## 11 Interview Mode

| Field | Value |
|---|---|
| Mode | hybrid |
| Pattern | Pattern A — migVisor Explainer MCP grounded |
| Discovery source | migVisor Explainer MCP (lineage traversal + source retrieval over `wideworldimportersdw`) |
