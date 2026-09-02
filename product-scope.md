# Product Scope — Sales_Orders

**Workspace path:** `migVisor_workspace/GlobalSales_Project/products/Sales_Orders/input/product-scope.md`
**Inherits from:** `migVisor_workspace/GlobalSales_Project/project/current/modernization-plan.md`
**Written by:** `product-scope-designer-agent`
**Context source:** `input/product-scope.md` (ingested 2026-08-28)

---

## 1. Identity

| Field | Value |
|---|---|
| Product name | Sales_Orders |
| Parent project | GlobalSales_Project |
| Scope owner | Sales Analytics Team |
| Discovery mode | hybrid — Pattern A (migVisor Explainer MCP grounded, base node: `bd3cae6f-6bef-40f5-8293-e6e23b27a7f4` → `wideworldimportersdw.fact.order`) |
| Plan stage | scope |

---

## 2. Description

Sales_Orders is the primary data product for the GlobalSales_Project migration. It covers the **sales and order transaction domain** of the WideWorldImporters data warehouse: the two core fact tables (`fact.sale` and `fact.order`), their conformed dimensions, the SSIS-orchestrated integration staging layer that loads them, the analytics views that expose them, and the BI reports that consume them.

The product moves this entire domain from Microsoft SQL Server 2014 to a Databricks Delta Lake lakehouse.

---

## 3. Source System(s)

Inherited from project scope. Narrowed to the source systems relevant to this product.

| Source platform | Source system | Source schema(s) | Notes |
|---|---|---|---|
| Microsoft SQL Server 2014 (T-SQL) | `wideworldimportersdw` | `fact`, `dimension`, `integration`, `sequences`, `application` (ETL config only) | Access via migVisor Explainer MCP (lineage + source retrieval) |

### 3.1 Core Fact Tables

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.fact.order` | `bd3cae6f-6bef-40f5-8293-e6e23b27a7f4` | table | Base node — sales order line items |
| `wideworldimportersdw.fact.sale` | `3d989b9d-cfa2-472d-9092-236d64f3ca7f` | table | Completed sales transactions |

### 3.2 Conformed Dimensions

| Object | ID | Type |
|---|---|---|
| `wideworldimportersdw.dimension.customer` | `86c34861-8dc0-40a9-b0dc-19b268065b42` | table |
| `wideworldimportersdw.dimension.stock item` | `9266888d-6063-408f-8284-e02ba1f92df3` | table |
| `wideworldimportersdw.dimension.date` | `83e9487a-1924-45c1-a861-6c4783b0bc93` | table |
| `wideworldimportersdw.dimension.city` | `efc6448b-b120-4770-b712-6ef55e42f0b2` | table |
| `wideworldimportersdw.dimension.employee` | `db1847d3-0acb-42f5-a55d-e32447de1611` | table |
| `wideworldimportersdw.dimension.payment method` | `b7d72928-94bd-4f0d-a536-3b22dbc10831` | table |
| `wideworldimportersdw.dimension.transaction type` | `e39c986c-88ae-4c50-9fbf-156a2e11e7b4` | table |

### 3.3 Integration Staging Layer

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.integration.sale_staging` | `9406be0c-8da1-4933-8ef3-97cd4f74072a` | table | Staging for sale data |
| `wideworldimportersdw.integration.order_staging` | `bfcc0178-2ad7-44f2-b145-6468f3626f36` | table | Staging for order data |
| `wideworldimportersdw.integration.customer_staging` | `c853bbc5-076c-4b19-ab04-456fe521ce44` | table | Staging for customer dimension |
| `wideworldimportersdw.integration.employee_staging` | `3a053a94-0d3a-4663-acef-38c60a3da1bd` | table | Staging for employee dimension |
| `wideworldimportersdw.integration.city_staging` | `aa9dff42-8970-44cb-88b7-e641f310df75` | table | Staging for city dimension |
| `wideworldimportersdw.integration.etl cutoff` | `757aa9c0-0b80-4291-9de6-bbdba3068aaf` | table | ETL watermark / cutoff control |
| `wideworldimportersdw.integration.lineage` | `a3caa39a-a18f-4e0b-bbb7-d933f8cee8a2` | table | ETL lineage / run log |
| `wideworldimportersdw.integration.migratestagedsaledata` | `08fd5640-37cc-4ce7-a791-faf5226a26f6` | procedure | Merges sale_staging → fact.sale |
| `wideworldimportersdw.integration.migratestagedorderdata` | `2fdd0635-a8fb-492e-b00e-9419ef098286` | procedure | Merges order_staging → fact.order |
| `wideworldimportersdw.integration.migratestagedcustomerdata` | `c5bd2636-ad8a-427d-96c5-1b661c253997` | procedure | Merges customer_staging → dimension.customer |
| `wideworldimportersdw.integration.migratestagedemployeedata` | `96b10588-30ae-409e-a829-99ab6935d4fd` | procedure | Merges employee_staging → dimension.employee |
| `wideworldimportersdw.integration.migratestagedcitydata` | `7eeddd1c-e975-4001-916a-54db7a7c1737` | procedure | Merges city_staging → dimension.city |
| `wideworldimportersdw.integration.getlastetlcutofftime` | — | procedure | Reads ETL cutoff watermark |
| `wideworldimportersdw.integration.getlineagekey` | — | procedure | Calls sequences.lineagekey for run ID |
| `wideworldimportersdw.integration.populatedatedimensionforyear` | `1b01699e-9917-484e-8d87-c50b60ad5f3d` | procedure | Populates dimension.date for a given year |
| `wideworldimportersdw.integration.generatedatedimensioncolumns` | — | function | Helper for date dimension |

### 3.4 Sequences / Infrastructure

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.sequences.lineagekey` | `8fe29a7a-9e66-45a8-96d2-9ef427d7fb0a` | sequence (unknown) | Generates lineage run keys for ETL |
| `wideworldimportersdw.sequences.reseedallsequences` | — | procedure | Reseeds all sequences |
| `wideworldimportersdw.sequences.reseedsequencebeyondtablevalues` | — | procedure | Reseeds a single sequence |

### 3.5 Analytics Views (Read from Core Facts)

| Object | ID | Type | Reads |
|---|---|---|---|
| `wideworldimportersdw.analytics.customersalessummary` | `3c21bedc-aa77-4230-b969-c2c34f8a9b12` | view | `fact.sale`, `fact.order`, `dimension.customer` |
| `wideworldimportersdw.analytics.orderdetails` | `9d6e2562-d0a3-4d40-88cf-79d10fd002bf` | view | `fact.order` + dimensions |
| `wideworldimportersdw.analytics.v_ordertosupplyanalytics` | `1d9153cb-6d51-4d39-94dc-aa5c2120a4a4` | view | `fact.order`, `fact.sale` |
| `wideworldimportersdw.analytics.v_ordertoyearanalytics` | `b942748e-163b-4919-92de-fd51f4ba2d52` | view | `fact.order`, `fact.sale` |

### 3.6 Scalar Functions on Fact Tables

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.fact.gettotalquantitysold1` | `978a86ae-21a3-4ad2-a916-92cf566e3cc6` | function | Aggregate quantity from `fact.sale` |
| `wideworldimportersdw.fact.gettotalquantitysold2` | `e33adcd5-2571-4b86-8e9d-84063ca89a1d` | function | Aggregate quantity from `fact.sale` (variant) |

### 3.7 SSIS Orchestration Pipeline

| Object | ID | Type | Role |
|---|---|---|---|
| `demo_ssis…pipeline_dailyetlmain` | `2b46604a-5753-4812-9a27-c25a7132da69` | workflow | Master daily ETL workflow |
| `demo_ssis…pipeline_item_migrate staged sale data` | `43e3ecb7-7a49-4b73-b10f-517f9eef6a54` | dataflow | Calls `migratestagedsaledata` |
| `demo_ssis…pipeline_item_migrate staged order data` | `83a271bb-ff62-4137-b37f-3630ee8a5140` | dataflow | Calls `migratestagedorderdata` |
| `demo_ssis…pipeline_item_migrate staged customer data` | `544d7c06-a893-41d5-a38e-d83b4fffa4ec` | dataflow | Calls `migratestagedcustomerdata` |
| `demo_ssis…pipeline_item_migrate staged employee data` | `c26948a9-baf7-40b9-9935-e794b0f49d63` | dataflow | Calls `migratestagedemployeedata` |
| `demo_ssis…pipeline_item_migrate staged city data` | `b9618822-73eb-4fd9-b52e-6e569cad57f6` | dataflow | Calls `migratestagedcitydata` |
| `demo_ssis…pipeline_item_get lineage key` (multiple) | various | dataflow | Fetches lineage key before each migrate step |
| `demo_ssis…pipeline_item_calculate etl cutoff time backup` | `04dd9782-7194-41f9-9224-499fcf31a4a6` | dataflow | Computes ETL cutoff |
| `demo_ssis…pipeline_item_ensure date dimension includes current year` | `0e7a33c6-7089-441a-bebc-f140e819b2b7` | dataflow | Calls `populatedatedimensionforyear` |

### 3.8 BI Reports (Downstream Consumers)

| Report | ID | Reads |
|---|---|---|
| `wwidw-sales.wwidw-sales` | `72a45f7f-f759-4ad3-a827-007d28c1bebf` | `fact.sale` |
| `wwidw-sales-nofilter.wwidw-sales-nofilter` | `bf376a90-d171-4968-bcd0-83edd6752f76` | `fact.sale` |
| `wwidw dynamic of product basket per customer` | `60009440-eec5-4bc1-94cf-bce814aa9584` | `fact.sale` |
| `wwidw dynamic of product basket per customer previous year` | `5cfef993-3d0f-489c-bc01-29399cfd63f7` | `fact.sale` |
| `wwidw purchase and sale per stockitem dynamic` | `8db5c99c-6f81-4021-95ff-5b33f9f1af5b` | `fact.sale` |
| `wwidw-orderdetails.wwidw-orderdetails` | `346bd04a-640a-45c5-a1a6-bb9de9c2f770` | `fact.order` (via `dbo.orderdetails`) |
| `wwidw-orderdetails-by-employee-2024` | `397952dc-c690-4091-a6b6-079a234a472d` | `fact.order` (via `dbo.orderdetails`) |
| `wwidw-orderitemsrankings.wwidw-orderitemsrankings` | `fe9205e8-3c63-4fff-b99d-98a637de532a` | `fact.order` |
| `wwidw-total-orders-summary-march-per province` | `1a6b4ea2-e650-469d-8bf6-e32c5bd52136` | `fact.order` |

---

## 4. Target System

Inherited from project scope. May be narrowed for this product.

| Field | Value |
|---|---|
| Target platform | Databricks (Delta Lake lakehouse) |
| Target schema/dataset | `globalsales` catalog — layers: bronze / silver / gold (staging → conformed dimension → fact → analytics) |
| Naming convention | `catalog.schema.table`, lowercase_snake_case (e.g., `globalsales.<layer>.<entity>`) |

---

## 5. Key Entities

Primary business entities this data product is built around.

- Sales (`fact.sale`) — completed sales transactions
- Orders (`fact.order`) — sales order line items
- Customer (`dimension.customer`) — conformed customer dimension
- Stock Item (`dimension.stock item`) — conformed product/stock dimension
- Date (`dimension.date`) — conformed calendar dimension
- City (`dimension.city`) — conformed geography dimension
- Employee (`dimension.employee`) — conformed employee dimension
- Payment Method (`dimension.payment method`) — conformed payment method dimension
- Transaction Type (`dimension.transaction type`) — conformed transaction type dimension

---

## 6. In-Scope Objects

Database objects (tables, views, stored procedures) that belong to this product. See §3.1–§3.8 for full object tables with IDs.

| Object name | Object type | Schema | Role |
|---|---|---|---|
| `fact.order` | table | fact | Core order line item fact |
| `fact.sale` | table | fact | Core sale transaction fact |
| `fact.gettotalquantitysold1` | function | fact | Aggregate quantity from `fact.sale` |
| `fact.gettotalquantitysold2` | function | fact | Aggregate quantity from `fact.sale` (variant) |
| `dimension.customer` | table | dimension | Conformed customer dimension |
| `dimension.stock item` | table | dimension | Conformed stock/product dimension |
| `dimension.date` | table | dimension | Conformed calendar dimension |
| `dimension.city` | table | dimension | Conformed geography dimension |
| `dimension.employee` | table | dimension | Conformed employee dimension |
| `dimension.payment method` | table | dimension | Conformed payment method dimension |
| `dimension.transaction type` | table | dimension | Conformed transaction type dimension |
| `integration.sale_staging` | table | integration | Staging for sale data |
| `integration.order_staging` | table | integration | Staging for order data |
| `integration.customer_staging` | table | integration | Staging for customer dimension |
| `integration.employee_staging` | table | integration | Staging for employee dimension |
| `integration.city_staging` | table | integration | Staging for city dimension |
| `integration.etl cutoff` | table | integration | ETL watermark / cutoff control |
| `integration.lineage` | table | integration | ETL lineage / run log |
| `integration.migratestagedsaledata` | procedure | integration | Merges sale_staging → fact.sale |
| `integration.migratestagedorderdata` | procedure | integration | Merges order_staging → fact.order |
| `integration.migratestagedcustomerdata` | procedure | integration | Merges customer_staging → dimension.customer |
| `integration.migratestagedemployeedata` | procedure | integration | Merges employee_staging → dimension.employee |
| `integration.migratestagedcitydata` | procedure | integration | Merges city_staging → dimension.city |
| `integration.getlastetlcutofftime` | procedure | integration | Reads ETL cutoff watermark |
| `integration.getlineagekey` | procedure | integration | Calls sequences.lineagekey for run ID |
| `integration.populatedatedimensionforyear` | procedure | integration | Populates dimension.date for a given year |
| `integration.generatedatedimensioncolumns` | function | integration | Helper for date dimension |
| `sequences.lineagekey` | sequence | sequences | Generates lineage run keys for ETL |
| `sequences.reseedallsequences` | procedure | sequences | Reseeds all sequences |
| `sequences.reseedsequencebeyondtablevalues` | procedure | sequences | Reseeds a single sequence |
| `analytics.customersalessummary` | view | analytics | Reads `fact.sale`, `fact.order`, `dimension.customer` |
| `analytics.orderdetails` | view | analytics | Reads `fact.order` + dimensions |
| `analytics.v_ordertosupplyanalytics` | view | analytics | Reads `fact.order`, `fact.sale` |
| `analytics.v_ordertoyearanalytics` | view | analytics | Reads `fact.order`, `fact.sale` |
| `demo_ssis…pipeline_dailyetlmain` | workflow | SSIS | Master daily ETL workflow |
| `demo_ssis…pipeline_item_migrate staged sale data` | dataflow | SSIS | Calls `migratestagedsaledata` |
| `demo_ssis…pipeline_item_migrate staged order data` | dataflow | SSIS | Calls `migratestagedorderdata` |
| `demo_ssis…pipeline_item_migrate staged customer data` | dataflow | SSIS | Calls `migratestagedcustomerdata` |
| `demo_ssis…pipeline_item_migrate staged employee data` | dataflow | SSIS | Calls `migratestagedemployeedata` |
| `demo_ssis…pipeline_item_migrate staged city data` | dataflow | SSIS | Calls `migratestagedcitydata` |
| `demo_ssis…pipeline_item_get lineage key` (multiple) | dataflow | SSIS | Fetches lineage key before each migrate step |
| `demo_ssis…pipeline_item_calculate etl cutoff time backup` | dataflow | SSIS | Computes ETL cutoff |
| `demo_ssis…pipeline_item_ensure date dimension includes current year` | dataflow | SSIS | Calls `populatedatedimensionforyear` |

---

## 7. Out-of-Scope Items

Objects within the project scope that are explicitly excluded from this product, with reasons.

| Object name | Reason for exclusion |
|---|---|
| `fact.purchase`, `fact.movement`, `fact.stock holding`, `fact.transaction` | Belong to Inventory_Stock / Finance_Analytics products (future candidates) |
| `integration.migratestagedmovementdata`, `migratestagedpurchasedata`, `migratestagedstockholdingdata`, `migratestagedtransactiondata`, `migratestagedstockitemdata`, `migratestagedsupplierdata`, `migratestagedtransactiontypedata`, `migratestagedpaymentmethoddata` | Load facts not in this product scope |
| `integration.movement_staging`, `purchase_staging`, `stockholding_staging`, `transaction_staging`, `stockitem_staging`, `supplier_staging`, `transactiontype_staging`, `paymentmethod_staging` | Staging for out-of-scope facts |
| `dimension.supplier` | Feeds out-of-scope fact tables only |
| `analytics.fin_*`, `analytics.cost0`, `analytics.refx`, `analytics.pol_*`, `analytics.billtype`, `analytics.dt_service_table`, `analytics.stage_outcome`, `analytics.stgdb349` | Finance/Analytics domain — Finance_Analytics product |
| `analytics.movementdetails`, `analytics.v_ordertosupplyanalytics` (movement side), `analytics.v_cost_sync_prep`, `analytics.v_financialcoverage`, `analytics.v_location`, `analytics.locationpartition*`, `analytics.v_extrastgdb349_p`, `analytics.v_rep_*`, `analytics.v_out_date_income`, `analytics.v_virtual_car_period`, `analytics.v_stage_outcome_limit` | Out-of-scope analytics views |
| `application.configuration_populatelargesaletable`, `application.configuration_reseedetl`, `application.configuration_applypartitionedcolumnstoreindexing`, `application.configuration_applypolybase` | SQL Server–specific config procedures — dropped or re-evaluated at implementation |
| `demo_sapbo.*` universes and SAP BO tables | SAP Business Objects — separate BI platform, not in Databricks scope |
| `xe.username.customer` | Oracle source artifact, separate migration |
| `dbo.*` | SSMS diagram objects and sample/test artifacts — excluded per project scope |
| ETL pipeline items for out-of-scope facts (movement, purchase, stockholding, etc.) | Follow their respective out-of-scope facts |

---

## 8. Boundaries

Product-level boundaries within the project scope.

| Boundary type | Definition |
|---|---|
| Temporal | Full history from 2013-01-01 through current date (inherits project default; watermark managed via `integration.etl cutoff` table) |
| System (source) | `wideworldimportersdw` on Microsoft SQL Server 2014 — schemas: `fact`, `dimension`, `integration`, `sequences`, `application` (ETL config only) |
| System (target) | Databricks Delta Lake — catalog: `globalsales`, layers: bronze/silver/gold (staging → conformed dimension → fact → analytics) |
| ETL orchestration (source) | SSIS `demo_ssis.folder_ssis-project.pipeline_dailyetlmain` — nightly batch |
| ETL orchestration (target) | Databricks workflow (nightly Delta pipeline replacing SSIS) |
| Organizational | Finance & Operations team (project-level owner); Sales Analytics Team (product-level scope owner) |

---

## 9. Consumers

Teams, systems, reports, jobs, or applications that consume this product's output.

| Consumer | Consumer type | What they use it for |
|---|---|---|
| wwidw-sales / wwidw-sales-nofilter | BI Report (Power BI / SSRS) | Sales reporting over `fact.sale` |
| wwidw dynamic of product basket per customer (current + prior year) | BI Report | Product basket analysis over `fact.sale` |
| wwidw purchase and sale per stockitem dynamic | BI Report | Purchase and sale reporting by stock item over `fact.sale` |
| wwidw-orderdetails | BI Report | Order detail reporting over `fact.order` via `dbo.orderdetails` |
| wwidw-orderdetails-by-employee-2024 | BI Report | Order details by employee (2024) over `fact.order` via `dbo.orderdetails` |
| wwidw-orderitemsrankings | BI Report | Order item rankings over `fact.order` |
| wwidw-total-orders-summary-march-per province | BI Report | Monthly/provincial order summaries over `fact.order` |
| `analytics.customersalessummary` | Analytical view | Customer sales summary over `fact.sale`, `fact.order`, `dimension.customer` |
| `analytics.orderdetails` | Analytical view | Order detail analytics over `fact.order` + dimensions |
| `analytics.v_ordertosupplyanalytics` | Analytical view | Order-to-supply analytics over `fact.order`, `fact.sale` |
| `analytics.v_ordertoyearanalytics` | Analytical view | Year-over-year order analytics over `fact.order`, `fact.sale` |

---

## 10. Calculation Surface

Indicates the calculation density of this product. Drives downstream as-is and to-be agent behavior.

| Field | Value |
|---|---|
| Calculation profile | moderately calculation-heavy |
| Notes | See narrative below |

This product is **moderately calculation-heavy**:

- **Scalar functions:** `fact.gettotalquantitysold1` and `fact.gettotalquantitysold2` perform quantity aggregations over `fact.sale` — will need to be re-expressed as Databricks SQL functions or notebook utilities.
- **Staging merge procedures:** `migratestagedsaledata` and `migratestagedorderdata` contain T-SQL MERGE / INSERT-SELECT logic with lineage key injection and ETL cutoff watermarking — this logic must be reimplemented as Databricks Delta MERGE operations.
- **Date dimension population:** `populatedatedimensionforyear` / `generatedatedimensioncolumns` generate calendar rows — can be replaced by a Delta table pre-loaded from a date dimension generator.
- **Lineage key generation:** `sequences.lineagekey` (SQL Server SEQUENCE) — must be redesigned (Databricks identity column or a UUID-based run ID).
- **Analytics views:** Four views (`customersalessummary`, `orderdetails`, `v_ordertosupplyanalytics`, `v_ordertoyearanalytics`) contain multi-table joins and aggregations — will be re-implemented as Delta views or Gold-layer materialized tables.

---

## 11. Interview Mode

| Field | Value |
|---|---|
| Mode used | hybrid |
| MCP available | yes |
| Interviewer | product-scope-designer-agent |
| Interview date | 2026-08-28 |
| Discovery pattern | Pattern A — migVisor Explainer MCP grounded (base node: `bd3cae6f-6bef-40f5-8293-e6e23b27a7f4` → `wideworldimportersdw.fact.order`) |

---

## 12. Stakeholder Sign-Off

[USER INPUT REQUIRED]

| Role | Name | Sign-off status | Date |
|---|---|---|---|
| Product owner | [USER INPUT REQUIRED] | [USER INPUT REQUIRED] | [USER INPUT REQUIRED] |
| Business lead | [USER INPUT REQUIRED] | [USER INPUT REQUIRED] | [USER INPUT REQUIRED] |
| Technical lead | [USER INPUT REQUIRED] | [USER INPUT REQUIRED] | [USER INPUT REQUIRED] |

---

## 13. Priority and Sequencing

| Field | Value |
|---|---|
| Priority | PRIMARY — first product in GlobalSales_Project |
| Rationale | Core revenue domain; directly feeds all customer-facing sales BI reports |
| Dependencies | None — all required dimensions (`customer`, `stock item`, `date`, `city`, `employee`, `payment method`, `transaction type`) are owned within this product scope |
| Successor products | Inventory_Stock (reuses `stock item`, `city`, `date` dimensions already migrated here); Finance_Analytics (reuses `customer`, `date`) |

---

## 14. Known Migration Risks (Product-Level)

| # | Risk | Implication |
|---|---|---|
| 1 | `dimension.payment method`, `dimension.stock item`, `dimension.transaction type`, `fact.stock holding` — object names contain **spaces** | Must be renamed to `payment_method`, `stock_item`, `transaction_type` under Databricks snake_case convention |
| 2 | `sequences.lineagekey` — SQL Server SEQUENCE with no Databricks equivalent | Re-design as `GENERATED ALWAYS AS IDENTITY` column or UUID-based run ID in `integration.lineage` replacement |
| 3 | `integration.migratestagedsaledata` and `migratestagedorderdata` — T-SQL MERGE with lineage key injection | Must be rewritten as Databricks Delta `MERGE INTO` with Python/SQL orchestration |
| 4 | `fact.gettotalquantitysold1/2` — scalar T-SQL UDFs iterating over `fact.sale` | Likely performance anti-pattern; evaluate as Spark SQL aggregate function or Gold-layer pre-aggregation |
| 5 | `application.configuration_reseedetl` and `configuration_populatelargesaletable` modify `fact.order` and `fact.sale` directly | Review: reseed proc likely for testing only — confirm drop scope with scope owner; large-sale-population proc may be a data-generator artifact |
| 6 | SSIS pipeline `dailyetlmain` orchestrates 15+ dataflow steps with ETL cutoff watermarking | Full orchestration logic must be re-expressed as a Databricks Workflow with task dependencies and state stored in a Delta control table |
