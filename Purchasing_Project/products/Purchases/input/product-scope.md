# Purchases — Product Scope

## 1 Identity

| Field | Value |
|---|---|
| Product name | Purchases |
| Parent project | GlobalSales_Project |
| Scope owner | [USER INPUT REQUIRED] |
| Discovery mode | hybrid — Pattern A (migVisor Explainer MCP grounded, base node: `197f0cba-80b1-4837-b448-3268bdf6649c` → `wideworldimportersdw.fact.purchase`) |
| Plan stage | scope |

---

## 2 Description

Purchases is a new data product within the GlobalSales_Project migration, covering the **supplier purchase order domain** of the WideWorldImporters data warehouse: the `fact.purchase` fact table, the net-new `dimension.supplier` conformed dimension, and the SSIS-orchestrated integration staging layer that loads it.

This product reuses two conformed dimensions already migrated by Sales_Orders (`stock item`, `date`). It also has two shared downstream dependents that already exist as built artifacts of the Sales_Orders product but currently reference `fact.purchase` without that fact table being present in the target lakehouse — see §9, risk 4.

The product moves this domain from Microsoft SQL Server 2014 to the same Databricks Delta Lake lakehouse (`globalsales` catalog) established by Sales_Orders.

---

## 3 Objects in Scope

### 3.1 Core Fact Table

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.fact.purchase` | `197f0cba-80b1-4837-b448-3268bdf6649c` | table | Base node — supplier purchase order transactions (DELETE + INSERT replace-by-order-ID load pattern) |

### 3.2 Conformed Dimensions

| Object | ID | Status | Role |
|---|---|---|---|
| `wideworldimportersdw.dimension.supplier` | `97866e9f-bb34-4e79-8413-93721cda0796` | **Net new** | Migrated by this product; load proc resolves `[Supplier Key]` via `[WWI Supplier ID]` + valid-time lookup, fallback to key `0` |
| `wideworldimportersdw.dimension.stock item` | `9266888d-6063-408f-8284-e02ba1f92df3` | Reused | Already migrated by Sales_Orders; load proc resolves `[Stock Item Key]` via `[WWI Stock Item ID]` + valid-time lookup, fallback to key `0` |
| `wideworldimportersdw.dimension.date` | `83e9487a-1924-45c1-a861-6c4783b0bc93` | Reused | Already migrated by Sales_Orders; `[Date Key]` is inserted into the fact but the load proc does not itself perform the lookup — confirm at as-is whether it arrives pre-resolved from staging |

### 3.3 Integration Staging Layer

| Object | ID | Type | Role |
|---|---|---|---|
| `wideworldimportersdw.integration.purchase_staging` | `a016e5b7-ab70-4e45-af51-b70ae237c7e2` | table | Staging for purchase order data |
| `wideworldimportersdw.integration.migratestagedpurchasedata` | `b79b9b8c-99af-4d42-8e97-e9206b8d5f02` | procedure | Deletes existing rows matching `[WWI Purchase Order ID]`, then inserts from staging with dimension key lookups and `[Lineage Key]` |

Upstream source-side extract (informational — outside `wideworldimportersdw`, feeds the staging table above):
- `wideworldimporters.integration.getpurchaseupdates` (procedure)

### 3.4 SSIS Orchestration Pipeline (subset of shared `dailyetlmain`)

| Object | ID | Type | Role |
|---|---|---|---|
| `demo_ssis…pipeline_item_extract updated purchase data to staging` | `5b1ac205-a17d-4ead-83e7-14d95b112a54` | dataflow | Extracts purchase deltas |
| `demo_ssis…pipeline_item_truncate purchase_staging` | `88c761dd-8756-453e-96b2-e587e568b9e3` | dataflow | Clears purchase staging before load |
| `demo_ssis…pipeline_item_set tablename to purchase` | `e630fc7c-26b8-41a1-9701-342991f19c46` | dataflow | Parameterizes shared extract logic for the purchase source |
| `demo_ssis…pipeline_item_migrate staged purchase data` | `9492a03b-5837-41c1-bc25-f00592b94c8c` | dataflow | Calls `migratestagedpurchasedata` |

These pipeline items live inside the same master workflow (`demo_ssis.folder_ssis-project.pipeline_dailyetlmain`) already referenced by Sales_Orders and Inventory_Stock candidates — shared infrastructure, not owned by any one product.

### 3.5 Shared Downstream Dependents (Built by Sales_Orders — Not Owned Here)

| Object | ID | Type | Relationship |
|---|---|---|---|
| `wideworldimportersdw.analytics.v_ordertoyearanalytics` | `b942748e-163b-4919-92de-fd51f4ba2d52` | view | Already migrated by Sales_Orders as `globalsales.mart.v_order_to_year_analytics`; source references `Fact.Purchase` via a `Package`-keyed subquery — see §9, risk 4 |
| `wwidw purchase and sale per stockitem dynamic` | `8db5c99c-6f81-4021-95ff-5b33f9f1af5b` | report | Already claimed as a Sales_Orders consumer of `fact.sale`; by name and design also expects purchase-side data — see §9, risk 4 |

---

## 4 Out-of-Scope Objects

| Object | Reason |
|---|---|
| `fact.sale`, `fact.order`, `fact.movement`, `fact.stock holding`, `fact.transaction` | Belong to Sales_Orders (sale/order) or Inventory_Stock (movement/stock holding) |
| `dimension.customer`, `dimension.city`, `dimension.employee`, `dimension.payment method`, `dimension.transaction type` | Not joined by `fact.purchase`; owned by Sales_Orders |
| `integration.sale_staging`, `order_staging`, `movement_staging`, `stockholding_staging`, `transaction_staging`, `customer_staging`, `city_staging`, `employee_staging`, `paymentmethod_staging`, `transactiontype_staging`, `stockitem_staging` and their `migratestaged*` procedures | Load facts/dimensions not owned by this product |
| `analytics.fin_*`, `analytics.cost0`, `analytics.refx`, `analytics.pol_*`, `analytics.billtype`, `analytics.dt_service_table`, `analytics.stage_outcome`, `analytics.stgdb349`, `analytics.movementdetails` | Finance_Analytics or Inventory_Stock domains |
| `application.configuration_*` procedures | Project-level SQL Server config, not product-specific |
| `sequences.*` | Shared ETL infrastructure at project level, not re-scoped per product |
| `wideworldimporters.purchasing.*`, `wideworldimporters.webapi.purchaseorder*`, `wideworldimporters.dataloadsimulation.receivepurchaseorders`, `wideworldimporters.sequences.purchaseorderid` | Source-side OLTP/API objects upstream of the DW load path — informational only, not migrated |
| `ccentralprp8.*`, `cdssdo00.*`, `emptoris_purchase_order.*` | Separate external procurement (Emptoris) system integration — different source, not in this phase |
| `dbo.*` | SSMS diagram objects and sample/test artifacts — excluded per project scope |

---

## 5 Consumers

No purchase-exclusive BI reports were found in the lineage graph. Two existing artifacts reference `fact.purchase` but are already owned/built by Sales_Orders — treated here as **shared dependents**, not consumers this product must build for:

| Consumer | Type | Objects Consumed | Note |
|---|---|---|---|
| `analytics.v_ordertoyearanalytics` (already deployed as `globalsales.mart.v_order_to_year_analytics`) | Analytical view | `fact.purchase` (via `Package` subquery) + `fact.order`, `fact.sale` | Owned by Sales_Orders; needs re-point/refresh once `fact.purchase` lands in target |
| `wwidw purchase and sale per stockitem dynamic` | BI Report | `fact.sale` (already migrated), `fact.purchase` (pending) | Owned by Sales_Orders; report likely under-serves purchase-side data today |

---

## 6 Calculation Surface

**Pass-through** — no independent business-metric calculations found in the load path itself. Complexity is ETL-pattern rather than business-rule:

- **Full replace-by-order-ID load pattern:** `migratestagedpurchasedata` DELETEs existing rows matching `[WWI Purchase Order ID]`, then INSERTs from staging — not a true incremental MERGE. Must be redesigned as a Delta `MERGE INTO` (or delete+insert transaction) keyed on purchase order ID.
- **Valid-time dimension key resolution:** Both `[Supplier Key]` and `[Stock Item Key]` are resolved via `[Last Modified When]` against `[Valid From]`/`[Valid To]` on the respective dimension, falling back to key `0` (Unknown) — same pattern seen in the movement/stock-holding load procedures; must be reproduced faithfully in the Delta MERGE implementation.
- **Lineage key injection:** Uses `sequences.lineagekey`-derived value, same shared infrastructure risk already flagged at the project level.

---

## 7 Boundaries

| Boundary | Value |
|---|---|
| Temporal | Inherits project default — [USER INPUT REQUIRED] |
| Organizational | [USER INPUT REQUIRED] |
| System (source) | `wideworldimportersdw` on Microsoft SQL Server 2014 — schemas: `fact`, `dimension`, `integration` |
| System (target) | Databricks Delta Lake — catalog: `globalsales`, layers: bronze/silver/gold, same lakehouse as Sales_Orders |
| ETL orchestration (source) | SSIS `demo_ssis.folder_ssis-project.pipeline_dailyetlmain` — shared master workflow with Sales_Orders |
| ETL orchestration (target) | Databricks Workflow — extend or run alongside the existing `nightly_etl_main` job |

---

## 8 Priority and Sequencing

| Field | Value |
|---|---|
| Priority | Active — being scoped now, ahead of Inventory_Stock and Finance_Analytics |
| Rationale | Two artifacts already built by Sales_Orders (`v_ordertoyearanalytics`, the purchase-and-sale report) reference `fact.purchase` but currently run without it in the target lakehouse; scoping and building this product closes that gap |
| Dependencies | Requires Sales_Orders' migrated `stock item` and `date` dimensions to exist in the target before or alongside this product's load of `fact.purchase` and net-new `dimension.supplier` |
| Successor products | None identified yet; may feed a future Supplier/Procurement analytics product |

---

## 9 Known Migration Risks (Product-Level)

| # | Risk | Implication |
|---|---|---|
| 1 | `migratestagedpurchasedata` uses DELETE-then-INSERT keyed on `[WWI Purchase Order ID]`, not a true MERGE | Must be redesigned as a Delta `MERGE INTO` or an equivalent transactional delete+insert to avoid partial-write windows |
| 2 | Valid-time dimension key resolution for both `Supplier Key` and `Stock Item Key`, with fallback to key `0` | Must be ported carefully — silent Unknown-key coercion can mask upstream dimension data-quality issues if not monitored |
| 3 | No FK graph edges were returned by Explainer for `fact.purchase` — dimension joins were inferred from load-procedure source code only | Confirm the full dimensional model (including whether `Date Key` truly arrives pre-resolved) during as-is analysis |
| 4 | `analytics.v_ordertoyearanalytics` and `wwidw purchase and sale per stockitem dynamic` are already built/deployed by Sales_Orders and reference `fact.purchase`, which doesn't yet exist in the target | Cross-product coordination required: once this product ships, both shared artifacts need to be re-pointed or refreshed to pick up purchase data — flag to Sales_Orders' owning team |
| 5 | `dimension.supplier` object name and `fact.purchase` currently untouched by any shipped product | First product to actually build `dimension.supplier` — any future Inventory_Stock scoping will need to reuse this dimension rather than re-implement it |
