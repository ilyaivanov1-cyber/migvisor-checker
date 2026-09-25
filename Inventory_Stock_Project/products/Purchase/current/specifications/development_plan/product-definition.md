# Data Product: Purchase

**Product ID:** purchase  
**Type:** analytical_data_product  
**Status:** draft  
**Visibility:** organisation  
**Domain:** Procurement / Purchasing  
**Categories:** procurement, supply-chain, inventory  
**Tags:** purchase-orders, delta-lake, databricks, scd-2, incremental-etl  

---

## Description

Grain-level Delta Lake fact table for procurement transactions on Databricks. Each row represents one purchase order line identified by purchase_key (IDENTITY), associated with a supplier, stock item, and order date via resolved SCD-2 surrogate keys. Includes nine post-load data quality assertions (row count reconciliation, RI completeness per FK, quantity non-negativity, date window validation, package non-null, DQ rejection traceability, and SK default coverage) and full end-to-end lineage via lineage_key propagation from nb_extract_watermark to fact_purchase. Corrects the legacy SSIS staging-truncation bug by writing bronze.purchase_staging in OVERWRITE mode on every run.

## Value Proposition

Provides reliable, auditable, and queryable procurement analytics on a modern cloud-native Databricks platform. Eliminates the stale-row defect that caused silent data quality issues in the predecessor pipeline. Enables the wwidw_purchase_and_sale_per_stockitem_dynamic and wwidw_ordered_by_supplier Power BI reports through Databricks SQL Warehouse, and establishes the observability foundation (lineage, DQ rejection store, watermark control) required for production operations.

---

## Input Ports

| Name | Type | Location | Format | Frequency | Description |
| --- | --- | --- | --- | --- | --- |
| source_purchase_jdbc | jdbc | wideworldimportersdw — SQL Server 2014 (`Purchasing.PurchaseOrders`, `Purchasing.PurchaseOrderLines`, `Purchasing.Suppliers`, `Warehouse.StockItems`, `Warehouse.PackageTypes`) | jdbc/sql-server | daily | Watermark-bounded JDBC extract from the transactional source system. Connection details in `config/environment.yaml` (PD-001 pending). Driver: `com.microsoft.sqlserver.jdbc.SQLServerDriver`. |
| purchase_staging | delta | inventory_stock.bronze.purchase_staging | delta | daily | Bronze staging table populated by nb_extract_purchase; OVERWRITE per run; surrogate keys NULL at load time, resolved by sk_resolver.py before MERGE. |
| supplier_dimension | delta | inventory_stock.silver_dim.supplier | delta | daily | SCD-2 supplier dimension; loaded by Dimensions team (external dependency). Purchase ETL reads via `supplier_current` view (is_current_row = TRUE). |
| stock_item_dimension | delta | inventory_stock.silver_dim.stock_item | delta | daily | SCD-2 stock item dimension; loaded by Dimensions team (external dependency). Purchase ETL reads via `stock_item_current` view. |
| date_dimension | delta | inventory_stock.silver_dim.date | delta | static | Static calendar dimension; externally owned (OB-011); Purchase has FK dependency via fact_purchase.date_key. |
| etl_cutoff | delta | inventory_stock.bronze.etl_cutoff | delta | daily | High-watermark control table; one row per tracked table; read at run start by nb_extract_watermark. |

---

## Output Ports

### default — `inventory_stock.silver_fact.fact_purchase`

| # | Field | Type | Nullable | Description |
| --- | --- | --- | --- | --- |
| 1 | purchase_key | BIGINT | No | Surrogate PK; GENERATED ALWAYS AS IDENTITY |
| 2 | date_key | DATE | No | Order date; FK → silver_dim.date.date |
| 3 | supplier_key | BIGINT | No | SCD-2 FK → silver_dim.supplier.supplier_key |
| 4 | stock_item_key | BIGINT | No | SCD-2 FK → silver_dim.stock_item.stock_item_key |
| 5 | wwi_purchase_order_id | INT | No | Source natural key; part of 4-column MERGE predicate |
| 6 | ordered_outers | INT | No | Outer packaging units ordered |
| 7 | ordered_quantity | INT | No | Total individual units ordered |
| 8 | received_outers | INT | Yes | Outer units received; NULL = not yet received |
| 9 | package | STRING | No | Package type name (e.g. Each, Carton) |
| 10 | is_order_finalized | BOOLEAN | No | TRUE when purchase order is confirmed |
| 11 | lineage_key | BIGINT | No | FK → bronze.lineage_run.lineage_key; ETL run traceability |

### bi_reports — Mart Views

| Report | View | Type | Refresh |
| --- | --- | --- | --- |
| wwidw_ordered_by_supplier | inventory_stock.mart.v_purchase_by_supplier | MATERIALIZED VIEW | After each successful fact load + DQ gate |
| wwidw_purchase_and_sale_per_stockitem_dynamic | inventory_stock.mart.v_purchase_per_stock_item | VIEW | Live (no refresh needed) |

---

## Pipeline

| Property | Value |
| --- | --- |
| orchestration | nightly_etl_purchase |
| schedule | 02:00 UTC daily |
| platform | Databricks Workflows |
| halt_policy | halt-and-alert on any task failure |
| lineage_key | propagated via taskValues from nb_extract_watermark to all downstream tables |

### Layers

| Layer | Notebooks | dependsOn | Description |
| --- | --- | --- | --- |
| ingestion | nb_extract_watermark, nb_extract_purchase | — | Read watermark from etl_cutoff; JDBC extract to purchase_staging; open lineage_run record |
| dimensions | nb_load_dim_supplier, nb_load_dim_stock_item, nb_populate_date_dim | ingestion | SCD-2 dimension refresh (external team); date dim coverage check; must complete before facts |
| facts | migrate_staged_purchase_data | ingestion, dimensions | SK resolution → QA assertion chain → MERGE INTO fact_purchase → close lineage_run; advance etl_cutoff |
| mart_dq | nb_dq_purchase, nb_refresh_v_purchase_by_supplier, nb_refresh_v_purchase_per_stock_item, nb_validate_mart_views | facts | Standalone DQ engine; mart materialized view refresh; mart validation gate |

### Assertions

| Assertion | QA Rule | DQR ID | Severity | Rejection Table |
| --- | --- | --- | --- | --- |
| Row count reconciliation | QA-P001 | DQR-001 | BLOCKING | — |
| RI completeness — supplier_key | QA-P003 | DQR-002 | informational | inventory_stock.bronze.dq_rejections |
| RI completeness — stock_item_key | QA-P003 | DQR-003 | informational | inventory_stock.bronze.dq_rejections |
| RI completeness — date_key | QA-P003 | DQR-004 | informational | inventory_stock.bronze.dq_rejections |
| Quantity non-negativity | QA-P004 | DQR-005 | informational | inventory_stock.bronze.dq_rejections |
| Date key within batch window | QA-P004 | DQR-006 | informational | inventory_stock.bronze.dq_rejections |
| Package non-null | QA-P004 | DQR-007 | informational | inventory_stock.bronze.dq_rejections |
| DQ rejection store write | QA-P005 | DQR-008 | BLOCKING | inventory_stock.bronze.dq_rejections |
| Surrogate key default coverage | sk_resolver + QA-P002 | DQR-009 | informational | — |

---

## Data Quality

| Profile | Dimension | QA Rule | DQR ID | Measured Value | Blocking |
| --- | --- | --- | --- | --- | --- |
| default | completeness | QA-P001 | DQR-001 | Zero-tolerance row count reconciliation: staging rows = fact rows merged per run | true |
| default | consistency | QA-P003 | DQR-002, DQR-003, DQR-004 | RI completeness: all FK columns (supplier_key, stock_item_key, date_key) resolve to dimension records; violations logged to dq_rejections | false |
| default | accuracy | QA-P004 | DQR-005, DQR-006, DQR-007 | Business rule assertions: ordered_outers ≥ 0, ordered_quantity ≥ 0, date_key within batch window, package IS NOT NULL | false |
| default | uniqueness | sk_resolver | DQR-009 | COALESCE(key, 0) ensures no NULL surrogate keys; sentinel key=0 row pre-seeded per OB-P001 | false |
| default | traceability | QA-P005, LN-001 | DQR-008 | Every row in fact_purchase and dq_rejections carries lineage_key FK to bronze.lineage_run | true |

---

## SLA

| Profile | Dimension | Measured Value |
| --- | --- | --- |
| default | updateFrequency | Daily — nightly_etl_purchase runs at 02:00 UTC; expected completion by 03:00 UTC |
| default | latency | < 1 hour from source commit (last_modified_when) to fact_purchase row available in Databricks SQL |
| default | uptime | Pipeline halt-and-alert policy; no silent failures; was_successful flag monitored each morning |
| default | retentionPolicy | silver_fact.fact_purchase: 2555 days; bronze staging: 90 days; bronze.lineage_run: 2555 days |

---

## Migration

This product migrates the WideWorldImporters DW Purchase domain from SQL Server 2014 (`wideworldimportersdw`) to Databricks Delta Lake Unity Catalog (`inventory_stock`).

### Source Object Mapping

| Source Object | Source Schema | Target Object | Target Schema | Migration Notes |
| --- | --- | --- | --- | --- |
| purchase_staging | integration | purchase_staging | inventory_stock.bronze | OVERWRITE mode per run (fixes SSIS truncation bug); lineage_key and _extracted_at_utc audit columns added |
| [etl cutoff] | integration | etl_cutoff | inventory_stock.bronze | Space in name resolved (NM-002); DATETIMEOFFSET → TIMESTAMP (TY-022); Delta ACID replaces BEGIN TRAN |
| lineage | integration | lineage_run | inventory_stock.bronze | Renamed; CDF enabled; IDENTITY PK replaces sequences.lineagekey; metadata columns added (etl_run_id, pipeline_name, table_row_count) |
| lineagekey (SEQUENCE) | sequences | (retired) | — | Replaced by GENERATED ALWAYS AS IDENTITY on lineage_run.lineage_key (LN-002); sequences schema retired |
| supplier | dimension | supplier | inventory_stock.silver_dim | SCD-2; Purchase ETL reads only (external load); is_current_row view pattern added |
| [stock item] | dimension | stock_item | inventory_stock.silver_dim | Space fixed (NM-002); SCD-2; external load; is_current_row view added |
| date | dimension | date | inventory_stock.silver_dim | Read-only reference table; Purchase Workflow does not own load (OB-011) |
| purchase | fact | fact_purchase | inventory_stock.silver_fact | Grain-level fact; MERGE INTO; CLUSTER BY (date_key, supplier_key); IDENTITY PK; lineage_key propagated |
| configuration_reseedetl | application | reseed_purchase_environment.py | src/init/ | Purchase portions only; requires scope-owner sign-off (PD-002) before execution in each environment |

### Migration Risks

| Risk ID | Description | Mitigation |
| --- | --- | --- |
| PD-001 | JDBC connectivity to SQL Server 2014 source not confirmed; driver class and credentials unknown | Confirm driver class, credentials, Databricks Secret Scope name; update config/environment.yaml before TASK-015 |
| PD-002 | reseed_purchase_environment.py requires scope-owner sign-off before executing in dev/staging/prod | Obtain sign-off; execute sequentially per environment under change management |
| PD-003 | Unity Catalog role names not yet defined; GRANT statements in purchase_grants.sql are placeholders | Confirm role names with platform team; review purchase_grants.sql (TASK-008) before execution |
| QA-DQ-01 | DQ threshold values (min_ordered_quantity, date_window_tolerance_days, package_required) need business stakeholder agreement | Agree thresholds with business owner before go-live; update config/environment.yaml |
| — | sequences.lineagekey retirement may affect cross-product lineage consumers outside Purchase | Audit all consumers of sequences.lineagekey across projects; coordinate retirement with platform team |
