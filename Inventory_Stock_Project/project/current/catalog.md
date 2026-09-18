# Inventory_Stock_Project — Data Product Catalog

_Generated: 2026-09-07 | ODPS schema version: 4.1_

---

## Project

| Field | Value |
|---|---|
| **Project** | Inventory_Stock_Project |
| **Description** | Modernisation of the WideWorldImporters procurement and inventory workload onto Databricks Delta Lake Unity Catalog. Migrates the purchase order transaction domain from a legacy SSIS-orchestrated batch into a governed medallion-architecture data platform under the Unity Catalog `inventory_stock`. |
| **Source system** | Microsoft SQL Server 2014 — `wideworldimportersdw` |
| **Target system** | Databricks Delta Lake Unity Catalog — `inventory_stock` |
| **Schema convention** | lowercase_snake_case |
| **Migration mode** | hybrid |
| **Generated** | 2026-09-07 |

---

## Data Products

| # | ID | Display Name | Status | Priority | Domain | Business Process |
|---|---|---|---|---|---|---|
| 1 | Purchase | Purchase | active | primary | Procurement / Purchasing | Procure-to-Pay |
| 2 | Inventory_Movement | Inventory Movement | candidate | future | Inventory and Supply Chain | Stock Movement |

---

## 1. Purchase

**Status:** active &nbsp;|&nbsp; **Priority:** primary &nbsp;|&nbsp; **Architecture:** medallion

**Description:**
Covers the purchase order transaction domain sourced from the WideWorldImporters star schema. Implements a medallion architecture (bronze staging and control tables → silver dimensions and facts) on Databricks Delta Lake Unity Catalog. Resolves SCD-2 surrogate keys for supplier and stock item via a temporal range join helper. Corrects the legacy SSIS staging-truncation bug by replacing per-run DELETE with full OVERWRITE of the bronze staging table. Serves two Power BI reports via Databricks SQL Warehouse.

### TCP Artifacts

| Artifact | Path |
|---|---|
| As-is | `products/Purchase/current/specifications/as-is.md` |
| To-be | `products/Purchase/current/specifications/to-be.md` |
| Product transformation rules | `products/Purchase/current/specifications/product-transformation-rules/` |

### Output Datasets

**Facts**

| Table | Type | Layer | Description |
|---|---|---|---|
| `inventory_stock.silver_fact.fact_purchase` | delta_table | silver | Grain: purchase order line × supplier × stock item × date. CLUSTER BY (date_key, supplier_key). |

**Dimensions (externally owned)**

| Table | Type | Layer | SCD | Notes |
|---|---|---|---|---|
| `inventory_stock.silver_dim.supplier` | delta_table | silver | 2 | Externally owned. SCD-2 key resolution dependency. |
| `inventory_stock.silver_dim.stock_item` | delta_table | silver | 2 | Externally owned. SCD-2 key resolution dependency. |
| `inventory_stock.silver_dim.date` | delta_table | silver | none | Externally owned. Static reference. |

**Staging / Control**

| Table | Type | Layer | Description |
|---|---|---|---|
| `inventory_stock.bronze.purchase_staging` | delta_table | bronze | OVERWRITE per run. Includes `lineage_key`, `_extracted_at_utc`. |
| `inventory_stock.bronze.etl_cutoff` | delta_table | bronze | Watermark control table. |
| `inventory_stock.bronze.lineage_run` | delta_table | bronze | Lineage audit log with IDENTITY key. CDF enabled. |
| `inventory_stock.bronze.dq_rejections` | delta_table | bronze | Centralised DQ rejection sink with `lineage_key`. |

### Orchestration

| Field | Value |
|---|---|
| Platform | Databricks Workflows |
| Primary job | `nightly_etl_purchase` |
| Schedule | `0 2 * * *` (daily 02:00 UTC) |
| Strategy | incremental_nightly |

### Data Quality

| Field | Value |
|---|---|
| Assertions | 5 (QA-P001 through QA-P005) |
| Assertion targets | `silver_fact.fact_purchase`, `bronze.purchase_staging` |
| Rejection sink | `inventory_stock.bronze.dq_rejections` |
| Row count reconciliation | zero_tolerance — blocking on mismatch (QA-P001) |

### Consumers

| Type | Platform | Count | Access Endpoint |
|---|---|---|---|
| BI Reports | Power BI | 2 | Databricks SQL Warehouse |

Reports: `wwidw_purchase_and_sale_per_stockitem_dynamic`, `wwidw_ordered_by_supplier`

### SLA

| Field | Value |
|---|---|
| Data freshness | daily |
| Load completion (UTC) | 06:00 |
| Retention — silver | 7 years |
| Retention — bronze | 90 days |

### Governance

| Field | Value |
|---|---|
| Platform | Unity Catalog |
| Row-level security | false |
| Column-level security | false |
| PII masking | false |
| Access role matrix | pending |

### Pending Decisions

| ID | Description |
|---|---|
| PD-001 | Source JDBC connectivity — confirm connection profile and credentials for SQL Server 2014 incremental extract |
| PD-002 | `reseed_purchase_environment.py` scope — scope owner sign-off on drop/retain decision |
| PD-003 | Unity Catalog access role matrix — define role assignments across `inventory_stock` schemas |
| QA-DQ-01 | Business DQ thresholds — confirm acceptable failure rates for informational QA assertions before go-live |

---

## 2. Inventory_Movement

**Status:** candidate &nbsp;|&nbsp; **Priority:** future &nbsp;|&nbsp; **Architecture:** medallion

**Description:**
Covers stock movement transaction facts sourced from the WideWorldImporters inventory domain. Planned medallion architecture mirroring the Purchase product pattern. No to-be specification exists yet.

| Artifact | Path |
|---|---|
| As-is | pending |
| To-be | pending |

---

_Rendered from `project/current/catalog.yaml` (ODPS 4.1)._
