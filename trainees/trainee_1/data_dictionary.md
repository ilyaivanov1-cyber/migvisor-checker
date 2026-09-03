# Data Dictionary — Sales_Orders
_TASK-DOCS-002 | globalsales Unity Catalog_

---

## Bronze / Staging Layer

### globalsales.stg.lineage

| Column | Type | Nullable | Description |
|---|---|---|---|
| lineage_key | BIGINT IDENTITY | N | Surrogate PK — propagated to all downstream rows |
| pipeline_run_id | STRING | N | Databricks Workflows run ID |
| pipeline_name | STRING | N | e.g. `nightly_etl_main` |
| batch_start_utc | TIMESTAMP | N | UTC start of the batch window |
| batch_end_utc | TIMESTAMP | Y | UTC end; NULL while running |
| rows_extracted | BIGINT | Y | Source rows extracted |
| rows_loaded | BIGINT | Y | Rows merged to Silver |
| rows_rejected | BIGINT | Y | Rows sent to stg.dq_rejections |
| status | STRING | N | RUNNING \| SUCCESS \| FAILED |

### globalsales.stg.etl_cutoff

| Column | Type | Nullable | Description |
|---|---|---|---|
| entity_name | STRING | N | PK — e.g. `sale`, `order`, `customer` |
| last_cutoff_utc | TIMESTAMP | N | Inclusive upper bound of last successful batch |
| updated_at_utc | TIMESTAMP | N | When this row was last updated |

### globalsales.stg.sale_staging

| Column | Type | Nullable | Description | Source |
|---|---|---|---|---|
| lineage_key | BIGINT | N | FK → stg.lineage | Stamped at extraction |
| sale_key | BIGINT | N | Source invoice line PK | Sales.InvoiceLines |
| customer_key | INT | N | Source customer FK | Sales.Invoices |
| stock_item_key | INT | N | Source stock item FK | Sales.InvoiceLines |
| invoice_date_key | INT | N | YYYYMMDD | Derived |
| quantity | INT | N | Line quantity | Sales.InvoiceLines |
| unit_price | DECIMAL(18,2) | N | Unit price | Sales.InvoiceLines |
| tax_rate | DECIMAL(5,2) | N | Tax rate % | Sales.InvoiceLines |
| profit | DECIMAL(18,2) | Y | Line profit from source | Sales.InvoiceLines |
| last_edited_when | TIMESTAMP | N | Source watermark column | Sales.Invoices |
| _extracted_at_utc | TIMESTAMP | N | Extraction timestamp | Added at ingest |

### globalsales.stg.dq_rejections

| Column | Type | Nullable | Description | PII |
|---|---|---|---|---|
| rejection_id | BIGINT IDENTITY | N | Surrogate PK | — |
| lineage_key | BIGINT | N | FK → stg.lineage | — |
| assertion_id | STRING | N | e.g. `DQ-SALE-001` | — |
| source_table | STRING | N | Three-part table name | — |
| source_key | BIGINT | Y | PK of rejected row | — |
| rejection_reason | STRING | N | Human-readable reason | — |
| rejected_at_utc | TIMESTAMP | N | Rejection timestamp | — |
| raw_payload | STRING | Y | JSON of rejected row | May contain PII |

---

## Silver / Dimension Layer

All SCD2 dimensions share these bookkeeping columns:

| Column | Type | Description | SCD2 tracked |
|---|---|---|---|
| row_effective_date | DATE | Version activation date | — |
| row_expiry_date | DATE | Version expiry (9999-12-31 = current) | — |
| is_current_row | BOOLEAN | TRUE for active version | — |
| lineage_key | BIGINT | Batch that created/updated this row | — |

### globalsales.dim.customer (SCD2)

| Column | Type | PII | Description |
|---|---|---|---|
| customer_key | INT IDENTITY | — | Surrogate PK |
| customer_id | INT | — | Source natural key |
| customer_name | STRING | **YES** | Masked via UC Column Mask |
| buying_group | STRING | **YES** | Masked via UC Column Mask |
| customer_category | STRING | — | |
| postal_code | STRING | **YES** | Masked |
| phone_number | STRING | **YES** | Masked |
| fax_number | STRING | **YES** | Masked |
| delivery_method | STRING | — | |
| credit_limit | DECIMAL(18,2) | — | |
| standard_discount_pct | DECIMAL(5,2) | — | |
| is_statement_sent | BOOLEAN | — | |
| is_on_credit_hold | BOOLEAN | — | |

### globalsales.dim.city (SCD2)

| Column | Type | Description |
|---|---|---|
| city_key | INT IDENTITY | Surrogate PK |
| city_id | INT | Source natural key |
| city_name | STRING | |
| state_province, country, continent | STRING | |
| sales_territory, region, subregion | STRING | |
| latest_recorded_population | BIGINT | |
| location_wkt | STRING | Source WKT geometry (preserved as-is) |
| location_lat | DOUBLE | Decomposed latitude (TY-EXTEND-001) |
| location_lon | DOUBLE | Decomposed longitude (TY-EXTEND-001) |

### globalsales.fact.sale

| Column | Type | Nullable | Description |
|---|---|---|---|
| sale_key | BIGINT IDENTITY | N | Surrogate PK |
| invoice_date_key | INT | N | FK → dim.date (YYYYMMDD) |
| customer_key | INT | N | FK → dim.customer |
| stock_item_key | INT | N | FK → dim.stock_item |
| city_key | INT | N | FK → dim.city |
| salesperson_key | INT | N | FK → dim.employee |
| lineage_key | BIGINT | N | FK → stg.lineage |
| quantity | INT | N | |
| unit_price | DECIMAL(18,2) | N | |
| tax_rate | DECIMAL(5,2) | N | |
| total_excluding_tax | DECIMAL(18,2) | N | quantity × unit_price |
| tax_amount | DECIMAL(18,2) | N | total_excluding_tax × (tax_rate / 100) |
| total_including_tax | DECIMAL(18,2) | N | total_excluding_tax + tax_amount |
| profit | DECIMAL(18,2) | N | From source; DQ-SALE-004 asserts non-NULL |
| total_dry_items | INT | Y | Ambient-temperature line items |
| total_chiller_items | INT | Y | Chilled line items |
| last_edited_when | TIMESTAMP | N | Source staleness column (MERGE guard) |

**Clustering:** CLUSTER BY (invoice_date_key, customer_key, stock_item_key)

### globalsales.mart.v_customer_sales_summary

| Column | Type | Description |
|---|---|---|
| customer_id | INT | Source natural key |
| customer_name | STRING | PII — masked for non-authorised callers |
| buying_group | STRING | PII — masked |
| customer_category, city_name, country, sales_territory | STRING | |
| calendar_year, calendar_month_label | INT / STRING | |
| total_quantity_sold | BIGINT | SUM(quantity) |
| total_revenue_ex_tax | DECIMAL | SUM(total_excluding_tax) |
| total_revenue_inc_tax | DECIMAL | SUM(total_including_tax) |
| total_profit | DECIMAL | SUM(profit) |
| profit_margin_with_factor | DOUBLE | (total_profit / total_revenue_inc_tax) × 100 × 1.05 |

**profit_margin_with_factor:** The factor 1.05 is `PROFIT_MARGIN_FACTOR` (NFR-MNT-002, CX-P01).
