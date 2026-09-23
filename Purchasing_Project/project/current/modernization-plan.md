# Purchasing_Project — Modernization Plan

## 1 Identity

| Field | Value |
|---|---|
| Project name | Purchasing_Project |
| Scope owner | [USER INPUT REQUIRED] |
| Intake mode | derived (project split from GlobalSales_Project) |
| Plan stage | modernization-plan |

## 2 Description / Rationale

Purchasing_Project is a new standalone project created by splitting the supplier-purchasing domain (the `Purchases` data product) out of `GlobalSales_Project`.

The team originally intended to scope and migrate Purchases as its own independent project from the start, but work began inside `GlobalSales_Project` by mistake, alongside the Sales/Orders, Inventory/Stock, and Finance Analytics domains. This project corrects that: it gives Purchases its own project-level scope, transformation rules, and pipeline, fully decoupled from the other GlobalSales_Project domains.

Purchases originates from the same source database as GlobalSales_Project (`wideworldimportersdw`, Microsoft SQL Server 2014) and moves to the same target platform family (Databricks Delta Lake), but under a **new, independent Unity Catalog** (`purchasing`) rather than continuing to share the `globalsales` catalog.

## 3 Source Systems

| Attribute | Value |
|---|---|
| Source database platform | Microsoft SQL Server 2014 (T-SQL) |
| Source database | `wideworldimportersdw` (the WideWorldImporters sample data warehouse) |
| Access method | Derived from GlobalSales_Project's prior migVisor Explainer MCP-grounded analysis (`product-scope.md`, `as-is.md` for the Purchases product) — no fresh MCP interview run for this split |

Schemas in scope (Purchases domain only):

| Schema | Role |
|---|---|
| `dimension` | Conformed dimensions used by `fact.purchase` (`supplier`, `stock item`, `date`) |
| `fact` | `fact.purchase` |
| `integration` | ETL / staging + migrate-procedure layer for Purchases, plus shared lineage/cutoff infrastructure |
| `sequences` | Surrogate / lineage key sequence objects (shared infrastructure) |

Upstream (informational, outside `wideworldimportersdw`, not itself migrated — feeds the staging layer above): `wideworldimporters` OLTP schemas `purchasing` and `warehouse`, and `wideworldimporters.integration.getpurchaseupdates`.

### 3.1 Known Migration Risks / Observations

| # | Observation | Implication |
|---|---|---|
| 1 | **Conformed dimension duplication risk.** `dimension.supplier` and `dimension.stock item` are conformed dimensions also used by other GlobalSales_Project domains — in particular the "Inventory_Stock" future candidate product, which uses both `stock item` and `supplier`. Splitting Purchases into its own project means these dimensions may now need to be independently maintained/duplicated under `purchasing.dim`, or a cross-project dimension-sharing strategy must be decided. | **Open architectural question, not yet resolved.** Must be decided before build: (a) duplicate/independently maintain `supplier` and `stock item` inside `purchasing`, or (b) design a cross-project/cross-catalog dimension-sharing mechanism with GlobalSales_Project (and any future Inventory_Stock product). Affects both this project and GlobalSales_Project's future Inventory_Stock scoping. |
| 2 | **Cross-project downstream dependency.** `analytics.v_ordertoyearanalytics` (owned by GlobalSales_Project's Sales_Orders product, deployed as `globalsales.mart.v_order_to_year_analytics`) reads `fact.purchase` directly (via a `Package`-keyed correlated subquery). Once Purchases moves to Purchasing_Project, this becomes a **cross-project** dependency (not merely cross-product): a view living in `globalsales` would depend on a fact table that no longer lives in the same project/catalog. | **Unresolved architectural/sequencing risk requiring a decision** — e.g., expose `purchasing.fact.purchase` to GlobalSales_Project via Unity Catalog cross-catalog grants, or replicate/federate the table back into `globalsales`. Must be resolved and communicated to the GlobalSales_Project/Sales_Orders owning team before this view is repointed at the target lakehouse. |
| 3 | Two further GlobalSales_Project/Sales_Orders-owned artifacts also read `fact.purchase` and/or the reused dimensions and will inherit the same cross-project dependency as risk #2: `wwidw purchase and sale per stockitem dynamic` (BI report; reads `fact.purchase`, `fact.sale`, `dimension.stock item`, `dimension.date`) and `wwidw-ordered-by-supplier` (BI report, discovered during Purchases' as-is lineage traversal; reads `fact.purchase`, `dimension.supplier`, `dimension.date`). | Same resolution path as risk #2 applies to all three artifacts; treat as one coordinated cross-project decision rather than three separate ones. |
| 4 | `integration.migratestagedpurchasedata` loads `fact.purchase` via a full DELETE-then-INSERT keyed on `[WWI Purchase Order ID]`, not a true incremental MERGE. | Must be redesigned as a Delta `MERGE INTO` (or an equivalent atomic delete+insert transaction) to avoid partial-write windows on the target lakehouse. |
| 5 | `Supplier Key` and `Stock Item Key` are resolved via valid-time (SCD2) lookups against `dimension.supplier` / `dimension.stock item`, falling back to key `0` (Unknown) when unresolved; `Date Key` arrives pre-resolved from staging with no active load-time lookup against `dimension.date`. | Valid-time lookup and Unknown-key fallback logic must be reproduced faithfully in the Delta implementation; silent fallback can mask upstream dimension data-quality issues if not monitored. |

## 4 Target System

| Attribute | Value |
|---|---|
| Target platform | Databricks (Delta Lake lakehouse) |
| Schema naming convention | `catalog.schema.table`, lowercase_snake_case, under a new independent Unity Catalog `purchasing` (e.g., `purchasing.<layer>.<entity>`) — distinct from GlobalSales_Project's `globalsales` catalog |

## 5 Key Entities

- Purchases (`fact.purchase`)

Conformed dimensions: Supplier (net-new to this domain), Stock Item (reused — previously migrated by GlobalSales_Project/Sales_Orders), Date (reused — previously migrated by GlobalSales_Project/Sales_Orders; FK target only, no active load-time lookup).

## 6 In-Scope Objects

Derived from the Purchases product's `product-scope.md` and `as-is.md` (authored under GlobalSales_Project) and restricted to the Purchases domain plus the shared cross-cutting infrastructure it depends on.

### 6.1 dimension

| Object | Type | Note |
|---|---|---|
| `dimension.supplier` | table | Net new — first migrated by the Purchases product; SCD2 (valid-time) dimension |
| `dimension.stock item` | table | Reused — already migrated by GlobalSales_Project/Sales_Orders; SCD2 (valid-time) dimension. Conformed — see §3.1 risk 1 |
| `dimension.date` | table | Reused — already migrated by GlobalSales_Project/Sales_Orders; declarative FK target for `fact.purchase.[Date Key]` only, no active load-time lookup |

### 6.2 fact

| Object | Type |
|---|---|
| `fact.purchase` | table |

### 6.3 integration

| Object | Type | Note |
|---|---|---|
| `integration.purchase_staging` | table | Staging for purchase order data |
| `integration.migratestagedpurchasedata` | procedure | Delete-then-insert load of `fact.purchase`, dimension key resolution (see §3.1 risk 4/5) |
| `integration.lineage` | table | Shared cross-cutting ETL infrastructure (lineage/batch bookkeeping) |
| `integration.getlineagekey` | procedure | Shared cross-cutting ETL infrastructure (lineage key issuance) |
| `integration.etl cutoff` | table | Shared cross-cutting ETL infrastructure — incremental-extraction watermark referenced by the Purchases load path |
| `integration.etl_cutoff_view2024` | view | Shared cross-cutting ETL infrastructure — cutoff/watermark reporting view |

### 6.4 sequences

| Object | Type |
|---|---|
| `sequences.lineagekey` | sequence |

### 6.5 Upstream source objects (informational — outside `wideworldimportersdw`, not migrated)

| Object | Type |
|---|---|
| `wideworldimporters.purchasing.purchaseorders` | table |
| `wideworldimporters.purchasing.purchaseorderlines` | table |
| `wideworldimporters.warehouse.stockitems` | table |
| `wideworldimporters.warehouse.packagetypes` | table |
| `wideworldimporters.integration.getpurchaseupdates` | procedure |

## 7 Out-of-Scope Items

| Item | Reason |
|---|---|
| Sales, Orders, Inventory/Stock, and Finance Analytics domains and all their dimension/fact/analytics objects (e.g., `fact.sale`, `fact.order`, `fact.movement`, `fact.stock holding`, `fact.transaction`, `dimension.customer`, `dimension.city`, `dimension.employee`, `dimension.payment method`, `dimension.transaction type`, the `analytics.*` reporting schema, `application.*` config procedures not consumed by Purchases) | Remain owned by `GlobalSales_Project`, which is the project of record for those domains. This split moves only the Purchases domain out. |
| `wideworldimporters.purchasing.*`, `.webapi.purchaseorder*`, `.dataloadsimulation.receivepurchaseorders`, `.sequences.purchaseorderid` (beyond the informational OLTP tables listed in §6.5) | Source-side OLTP/API objects upstream of the DW load path — informational only, not migrated. |
| `ccentralprp8.*`, `cdssdo00.*`, `emptoris_purchase_order.*` | Separate external procurement (Emptoris) system integration — different source, not in this phase. |
| `dbo.*` | SSMS diagram objects and sample/test artifacts — excluded per (inherited) project scope. |

## 8 Boundaries

| Boundary | Value |
|---|---|
| Temporal | [USER INPUT REQUIRED] (date range of data to migrate — GlobalSales_Project's own project-level temporal boundary was also left unresolved) |
| Organizational | [USER INPUT REQUIRED] (owning team / department) |
| System (source) | `wideworldimportersdw` on Microsoft SQL Server 2014 — schemas: `fact`, `dimension`, `integration`, `sequences` (Purchases subset only); upstream OLTP source `wideworldimporters` (informational, §6.5) |
| System (target) | Databricks Delta Lake lakehouse, new independent Unity Catalog `purchasing` |

## 9 Data-Product Inventory

Purchasing_Project has exactly one data product for now.

| Product | Status | Description | Sources |
|---|---|---|---|
| Purchases | Active — migrating (re-parented from GlobalSales_Project; scope, as-is, and product-transformation-rules already completed in its prior home) | Supplier purchase order domain: `fact.purchase`, the `dimension.supplier` conformed dimension, and the integration staging/load layer that feeds it. | `fact.purchase` + `supplier` / `stock item` / `date` dimensions and the integration-layer staging/migrate procedure and shared lineage/cutoff infrastructure that load it. |

No other candidate products are currently identified within Purchasing_Project.

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
| Mode | derived |
| Pattern | Derived — project split from GlobalSales_Project |
| Discovery source | GlobalSales_Project's existing Purchases product artifacts (`products/Purchases/input/product-scope.md`, `products/Purchases/current/specifications/as-is.md`) and GlobalSales_Project's own `project/current/modernization-plan.md`, reconciled into a new standalone project scope. No fresh migVisor Explainer MCP interview was run for this split. |
