# Data Product: Purchase

**Product ID:** purchase  
**Type:** analytical_data_product  
**Status:** draft  
**Visibility:** organisation  

## Description

Grain-level Delta Lake fact table for procurement transactions on Databricks. Each row represents one purchase order line identified by purchase_key (IDENTITY), associated with a supplier, stock item, and order date via resolved SCD-2 surrogate keys. Includes five post-load data quality assertions (row count reconciliation, orphaned SK detection, RI checks, business rule assertions, and centralised DQ rejection tracking) and full end-to-end lineage via lineage_key propagation from nb_extract_watermark to fact_purchase. Corrects the legacy SSIS staging-truncation bug by writing bronze.purchase_staging in OVERWRITE mode on every run.


## Value Proposition

Provides reliable, auditable, and queryable procurement analytics on a modern cloud-native Databricks platform. Eliminates the stale-row defect that caused silent data quality issues in the predecessor pipeline. Enables the wwidw_purchase_and_sale_per_stockitem_dynamic and wwidw_ordered_by_supplier Power BI reports through Databricks SQL Warehouse, and establishes the observability foundation (lineage, DQ rejection store, watermark control) required for production operations.


## Input Ports

| Name | Type | Location | Format | Frequency |
| --- | --- | --- | --- | --- |
|  |  | inventory_stock.bronze.purchase_staging | delta | daily |
|  |  | inventory_stock.silver_dim.supplier | delta | daily |
|  |  | inventory_stock.silver_dim.stock_item | delta | daily |
|  |  | inventory_stock.silver_dim.date | delta | static |
|  |  | inventory_stock.bronze.etl_cutoff | delta | daily |

## Output Ports

| Profile | Type | URL |
| --- | --- | --- |
| bi_reports |  |  |
| default |  |  |

## Data Quality

| Profile | Dimension | Measured Value |
| --- | --- | --- |
| default | completeness |  |
| default | consistency |  |
| default | accuracy |  |
| default | uniqueness |  |
| default | traceability |  |

## SLA

| Profile | Dimension | Measured Value |
| --- | --- | --- |
| default | updateFrequency |  |
| default | latency |  |
| default | uptime |  |
| default | retentionPolicy |  |
