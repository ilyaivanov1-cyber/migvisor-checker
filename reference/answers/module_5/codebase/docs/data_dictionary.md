# Data Dictionary: Purchase Data Product

## stg.purchase_staging — Transient Staging Table

Truncated and overwritten on each pipeline run. Rows carry a constant `lineage_key` within a run.

| Column | Type | Nullable | Description |
|---|---|---|---|
| purchase_order_id | INT | YES | Source purchase order identifier |
| supplier_id | INT | YES | Source supplier identifier; resolved to `supplier_key` in dim load |
| stock_item_id | INT | YES | Source stock item identifier; resolved to `stock_item_key` in dim load |
| order_date | DATE | YES | Date the purchase order was placed |
| expected_delivery_date | DATE | YES | Expected delivery date from supplier |
| ordered_outers | INT | YES | Number of outer packages ordered |
| ordered_quantity | INT | YES | Total individual units ordered |
| received_outers | INT | YES | Number of outer packages actually received |
| package | STRING | YES | Package type description (e.g. Each, Carton) |
| is_order_finalized | BOOLEAN | YES | True when the purchase order has been fully confirmed |
| lineage_key | BIGINT | **NO** | FK → stg.lineage.lineage_key; constant within a pipeline run |
| _extracted_at_utc | TIMESTAMP | **NO** | UTC timestamp at extraction time; constant within a pipeline run |

---

## stg.etl_cutoff — Watermark Control Table

One row per monitored entity. Controls incremental extract boundaries.

| Column | Type | Nullable | Description |
|---|---|---|---|
| entity_name | STRING | **NO** | Logical entity name (e.g. `purchase`); primary key |
| last_cutoff_time | TIMESTAMP | **NO** | UTC timestamp of the latest successfully processed source record |

---

## stg.lineage — Pipeline Run Audit Log

One row per pipeline execution. Primary lineage anchor for all target tables.

| Column | Type | Nullable | Description |
|---|---|---|---|
| lineage_key | BIGINT | **NO** | Surrogate PK; IDENTITY auto-incremented |
| pipeline_run_id | STRING | **NO** | Databricks Workflow run ID |
| entity_name | STRING | **NO** | Logical entity being loaded (e.g. `purchase`) |
| started_at | TIMESTAMP | **NO** | UTC timestamp when the pipeline run began |
| completed_at | TIMESTAMP | YES | UTC timestamp when the run finished; NULL while running |
| status | STRING | YES | Pipeline run state: `running` \| `success` \| `failed` |
| source_row_count | BIGINT | YES | Row count extracted from the source system |
| rows_loaded | BIGINT | YES | Row count merged into the fact table |

---

## stg.dq_rejections — Data Quality Rejection Log

One row per DQ rule violation per pipeline run.

| Column | Type | Nullable | Description |
|---|---|---|---|
| rejection_key | BIGINT | **NO** | Surrogate PK; IDENTITY auto-incremented |
| dq_rule_id | STRING | **NO** | DQ rule identifier (e.g. DQR-001) |
| batch_id | STRING | **NO** | Workflow run batch identifier |
| lineage_key | BIGINT | YES | FK → stg.lineage.lineage_key; nullable for pre-lineage violations |
| affected_column | STRING | YES | Column name that triggered the rejection |
| observed_value | STRING | YES | Actual value observed at time of rejection |
| expected_condition | STRING | YES | Rule condition that was violated |
| severity | STRING | **NO** | Violation severity: `WARNING` \| `ERROR` \| `CRITICAL` |
| recorded_at | TIMESTAMP | **NO** | UTC timestamp when the rejection was recorded |

---

## dim.supplier — SCD Type 2 Supplier Dimension

Tracks full attribute history. Change Data Feed enabled.

| Column | Type | Nullable | Description |
|---|---|---|---|
| supplier_key | INT | **NO** | Surrogate PK; IDENTITY auto-incremented |
| wwi_supplier_id | INT | **NO** | Source system supplier identifier; SCD-2 lookup key |
| supplier_name | STRING | **NO** | Full legal or trading name of the supplier |
| supplier_category_name | STRING | YES | Supplier category as defined in the source system |
| primary_contact | STRING | YES | Name of the primary contact person |
| phone_number | STRING | YES | Main telephone number |
| fax_number | STRING | YES | Fax number, if applicable |
| website_url | STRING | YES | Supplier website URL |
| delivery_city_name | STRING | YES | City used for delivery address |
| delivery_postal_code | STRING | YES | Postal code for delivery address |
| delivery_country_name | STRING | YES | Country for delivery address |
| payment_days | INT | YES | Standard payment terms in days |
| valid_from | DATE | **NO** | Inclusive start date of this version (source effective date) |
| valid_to | DATE | **NO** | Inclusive end date; `9999-12-31` = current version |
| row_effective_date | DATE | **NO** | Date this row was inserted into the dimension |
| row_expiry_date | DATE | **NO** | Date this row was logically closed; `9999-12-31` = open |
| is_current_row | BOOLEAN | **NO** | True for the single active version of each supplier |
| lineage_key | BIGINT | **NO** | FK → stg.lineage.lineage_key; links row to pipeline run |

---

## dim.stock_item — SCD Type 2 Stock Item Dimension

Tracks full attribute history. Change Data Feed enabled.

| Column | Type | Nullable | Description |
|---|---|---|---|
| stock_item_key | INT | **NO** | Surrogate PK; IDENTITY auto-incremented |
| wwi_stock_item_id | INT | **NO** | Source system stock item identifier; SCD-2 lookup key |
| stock_item_name | STRING | **NO** | Full descriptive name of the stock item |
| color | STRING | YES | Color of the item |
| size | STRING | YES | Size descriptor |
| unit_package_name | STRING | YES | Packaging type for individual units |
| outer_package_name | STRING | YES | Packaging type for outer containers |
| brand | STRING | YES | Brand name |
| description | STRING | YES | Long-form product description |
| unit_price | DECIMAL(18,2) | YES | Standard unit price in source currency |
| recommended_retail_price | DECIMAL(18,2) | YES | Recommended retail price |
| typical_weight_per_unit | DECIMAL(18,3) | YES | Typical weight per unit in kilograms |
| is_chiller_stock | BOOLEAN | YES | True if item requires cold-chain storage |
| tax_rate | DECIMAL(18,3) | YES | Applicable tax rate percentage |
| valid_from | DATE | **NO** | Inclusive start date of this version |
| valid_to | DATE | **NO** | Inclusive end date; `9999-12-31` = current |
| row_effective_date | DATE | **NO** | Date this row was inserted |
| row_expiry_date | DATE | **NO** | Date this row was logically closed; `9999-12-31` = open |
| is_current_row | BOOLEAN | **NO** | True for the single active version of each stock item |
| lineage_key | BIGINT | **NO** | FK → stg.lineage.lineage_key |

---

## dim.date — Static Calendar Dimension

One row per calendar day (2000-01-01 to 2030-12-31). No SCD-2 tracking.

| Column | Type | Nullable | Description |
|---|---|---|---|
| date_key | INT | **NO** | PK in YYYYMMDD format; matches fact.purchase.date_key |
| calendar_date | DATE | **NO** | Full calendar date value |
| year | INT | **NO** | Calendar year |
| quarter | INT | **NO** | Calendar quarter: 1–4 |
| month | INT | **NO** | Calendar month: 1–12 |
| month_name | STRING | **NO** | Full month name (e.g. January) |
| day | INT | **NO** | Day of month: 1–31 |
| day_of_week | STRING | **NO** | Full weekday name (e.g. Monday) |
| day_of_week_num | INT | **NO** | ISO-8601 weekday: 1=Monday, 7=Sunday |
| week_of_year | INT | **NO** | ISO week number: 1–53 |
| is_weekend | BOOLEAN | **NO** | True for Saturday and Sunday |
| is_public_holiday | BOOLEAN | **NO** | True if public holiday; populated externally |
| fiscal_year | INT | YES | Fiscal year; NULL if not applicable |
| fiscal_quarter | INT | YES | Fiscal quarter: 1–4; NULL if not applicable |

---

## fact.purchase — Central Purchase Fact Table

One row per purchase order line. Loaded incrementally via MERGE on `wwi_purchase_order_id`.

| Column | Type | Nullable | Description |
|---|---|---|---|
| purchase_key | BIGINT | **NO** | Surrogate PK; IDENTITY auto-incremented |
| date_key | INT | **NO** | FK → dim.date.date_key (YYYYMMDD) |
| supplier_key | INT | **NO** | FK → dim.supplier.supplier_key (current SCD-2 row) |
| stock_item_key | INT | **NO** | FK → dim.stock_item.stock_item_key (current SCD-2 row) |
| wwi_purchase_order_id | INT | YES | Source system natural key; MERGE predicate |
| ordered_outers | INT | YES | Number of outer packages ordered |
| ordered_quantity | INT | YES | Total individual units ordered |
| received_outers | INT | YES | Number of outer packages received |
| package | STRING | YES | Package type description |
| is_order_finalized | BOOLEAN | YES | True when fully confirmed |
| lineage_key | BIGINT | **NO** | FK → stg.lineage.lineage_key |

---

## Glossary: SCD-2 Tracking Columns

| Column | Applies to | Meaning |
|---|---|---|
| `valid_from` | dim.supplier, dim.stock_item | Inclusive start date of this attribute version (source-system effective date) |
| `valid_to` | dim.supplier, dim.stock_item | Inclusive end date; `9999-12-31` means this is the current version |
| `row_effective_date` | dim.supplier, dim.stock_item | Date this row was physically inserted into the dimension |
| `row_expiry_date` | dim.supplier, dim.stock_item | Date this row was logically closed; `9999-12-31` means still open |
| `is_current_row` | dim.supplier, dim.stock_item | Boolean flag; exactly one row per business key has `is_current_row = TRUE` |

FK relationships are logical — Delta Lake does not enforce physical constraints. Referential integrity is enforced at the ETL layer (sk_resolver + DQ rules DQR-002/DQR-003).
