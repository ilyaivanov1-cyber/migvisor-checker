# Sales_Orders — Technical Design
_Generated: 2026-06-05 | Pipeline stage: design_

---

## 1. Data Model Design

### 1.1 Layer Overview

The Sales_Orders data product follows a three-layer Medallion architecture within the `globalsales` Unity Catalog:

| Layer | Schema | Purpose | Load Pattern |
|---|---|---|---|
| Bronze | `globalsales.stg` | Raw incremental extract; staging tables; lineage and DQ bookkeeping | Truncate-before-load each nightly run |
| Silver | `globalsales.dim` | Conformed, history-tracked dimensions (SCD2); reference dimension (SCD0) | MERGE INTO (upsert + close rows) |
| Silver | `globalsales.fact` | Fully attributed fact tables for sales transactions and orders | Delta MERGE INTO (incremental upsert) |
| Gold | `globalsales.mart` | Aggregated and analytical views consumed by BI tooling | Views (one materialized refresh nightly) |

History anchor: `2013-01-01`. Estimated annual volume: ~12 M rows on `globalsales.fact.sale`.

All layers reside in the `globalsales` Unity Catalog under their respective schemas. Three-part identifiers (`catalog.schema.table`) are used throughout.

---

### 1.2 Bronze / Staging Layer Schema

#### `globalsales.stg.lineage`

Tracks every ETL batch execution. A `lineage_key` is generated here and stamped on every staging and fact row (implements FR-LIN).

```sql
CREATE TABLE globalsales.stg.lineage (
  lineage_key        BIGINT  GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1)  NOT NULL,
  pipeline_run_id    STRING  NOT NULL,   -- Databricks Workflows run ID
  pipeline_name      STRING  NOT NULL,   -- e.g. 'nightly_etl_main'
  batch_start_utc    TIMESTAMP NOT NULL,
  batch_end_utc      TIMESTAMP,
  rows_extracted     BIGINT,
  rows_loaded        BIGINT,
  rows_rejected      BIGINT,
  status             STRING  NOT NULL,   -- RUNNING | SUCCESS | FAILED
  CONSTRAINT pk_lineage PRIMARY KEY (lineage_key)
)
USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'false');
```

#### `globalsales.stg.etl_cutoff`

Stores watermark values per source entity (implements FR-ING).

```sql
CREATE TABLE globalsales.stg.etl_cutoff (
  entity_name         STRING     NOT NULL,   -- e.g. 'sale', 'order', 'customer'
  last_cutoff_utc     TIMESTAMP  NOT NULL,   -- inclusive upper bound of last successful run
  updated_at_utc      TIMESTAMP  NOT NULL,
  CONSTRAINT pk_etl_cutoff PRIMARY KEY (entity_name)
)
USING DELTA;
```

#### `globalsales.stg.sale_staging`

Ephemeral staging table for raw sale rows extracted from the source in the current batch.

```sql
CREATE TABLE globalsales.stg.sale_staging (
  lineage_key              BIGINT     NOT NULL,   -- FK → stg.lineage (implements FR-LIN)
  sale_key                 BIGINT     NOT NULL,
  city_key                 INT        NOT NULL,
  customer_key             INT        NOT NULL,
  bill_to_customer_key     INT        NOT NULL,
  stock_item_key           INT        NOT NULL,
  invoice_date_key         INT        NOT NULL,
  delivery_date_key        INT,
  salesperson_key          INT        NOT NULL,
  wwi_invoice_id           INT        NOT NULL,
  description              STRING,
  package                  STRING,
  quantity                 INT        NOT NULL,
  unit_price               DECIMAL(18,2) NOT NULL,
  tax_rate                 DECIMAL(5,2)  NOT NULL,
  total_excluding_tax      DECIMAL(18,2),   -- computed on load from unit_price * quantity
  tax_amount               DECIMAL(18,2),   -- computed on load
  total_including_tax      DECIMAL(18,2),   -- computed on load
  profit                   DECIMAL(18,2),
  total_dry_items          INT,
  total_chiller_items      INT,
  last_edited_when         TIMESTAMP  NOT NULL,
  _extracted_at_utc        TIMESTAMP  NOT NULL
)
USING DELTA;
```

> Note: The staging table is truncated before each batch load. It does not accumulate history.

#### `globalsales.stg.order_staging`

Ephemeral staging table for raw order rows.

```sql
CREATE TABLE globalsales.stg.order_staging (
  lineage_key              BIGINT     NOT NULL,
  order_key                BIGINT     NOT NULL,
  city_key                 INT        NOT NULL,
  customer_key             INT        NOT NULL,
  stock_item_key           INT        NOT NULL,
  order_date_key           INT        NOT NULL,
  picked_date_key          INT,
  salesperson_key          INT        NOT NULL,
  picker_key               INT,
  wwi_order_id             INT        NOT NULL,
  wwi_backorder_id         INT,
  description              STRING,
  package                  STRING,
  quantity                 INT        NOT NULL,
  unit_price               DECIMAL(18,2) NOT NULL,
  tax_rate                 DECIMAL(5,2)  NOT NULL,
  total_excluding_tax      DECIMAL(18,2),
  tax_amount               DECIMAL(18,2),
  total_including_tax      DECIMAL(18,2),
  backorder_count          INT,         -- derived: count of rows where wwi_backorder_id IS NOT NULL
  pick_time_sla_met        BOOLEAN,     -- derived: picked_date_key - order_date_key <= SLA threshold
  is_order_finalized       BOOLEAN,
  last_edited_when         TIMESTAMP  NOT NULL,
  _extracted_at_utc        TIMESTAMP  NOT NULL
)
USING DELTA;
```

#### `globalsales.stg.dq_rejections`

Persists rows that fail DQ assertions for investigation (implements DQR).

```sql
CREATE TABLE globalsales.stg.dq_rejections (
  rejection_id       BIGINT  GENERATED ALWAYS AS IDENTITY  NOT NULL,
  lineage_key        BIGINT  NOT NULL,
  assertion_id       STRING  NOT NULL,   -- e.g. 'DQ-SALE-001'
  source_table       STRING  NOT NULL,   -- three-part name of the originating table
  source_key         BIGINT,             -- PK value of the rejected row
  rejection_reason   STRING  NOT NULL,
  rejected_at_utc    TIMESTAMP NOT NULL,
  raw_payload        STRING              -- JSON serialisation of the rejected row
)
USING DELTA
PARTITIONED BY (assertion_id);
```

---

### 1.3 Silver / Dimension Layer Schema

All SCD2 dimensions share the following bookkeeping columns appended to their natural key + attributes:

| Column | Type | Description |
|---|---|---|
| `row_effective_date` | DATE NOT NULL | Date the version became active |
| `row_expiry_date` | DATE NOT NULL | Date the version was superseded (9999-12-31 = current) |
| `is_current_row` | BOOLEAN NOT NULL | True for the active version |
| `lineage_key` | BIGINT NOT NULL | Batch that created/updated the row (implements FR-LIN) |

#### `globalsales.dim.customer`
<!-- sourceLineage: derived from source dimension table tracking customer master data -->

```sql
CREATE TABLE globalsales.dim.customer (
  customer_key         INT        GENERATED ALWAYS AS IDENTITY  NOT NULL,
  customer_id          INT        NOT NULL,   -- source natural key
  customer_name        STRING     NOT NULL,   -- PII — subject to CLS masking
  buying_group         STRING,               -- PII — subject to CLS masking
  customer_category    STRING,
  primary_contact      STRING,
  postal_code          STRING,
  phone_number         STRING,               -- PII — subject to CLS masking
  fax_number           STRING,               -- PII — subject to CLS masking
  delivery_method      STRING,
  delivery_city_key    INT,
  postal_city_key      INT,
  account_opened_date  DATE,
  credit_limit         DECIMAL(18,2),
  standard_discount_pct DECIMAL(5,2),
  is_statement_sent    BOOLEAN,
  is_on_credit_hold    BOOLEAN,
  valid_from           DATE       NOT NULL,
  valid_to             DATE       NOT NULL,
  -- SCD2 bookkeeping
  row_effective_date   DATE       NOT NULL,
  row_expiry_date      DATE       NOT NULL   DEFAULT DATE '9999-12-31',
  is_current_row       BOOLEAN    NOT NULL   DEFAULT TRUE,
  lineage_key          BIGINT     NOT NULL,
  CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key)
)
USING DELTA;
```

PII columns: `customer_name`, `phone_number`, `fax_number`, `buying_group` — governed by Unity Catalog Column Masking (see Section 6.2).

#### `globalsales.dim.city`
<!-- sourceLineage: derived from source city dimension -->

```sql
CREATE TABLE globalsales.dim.city (
  city_key             INT        GENERATED ALWAYS AS IDENTITY  NOT NULL,
  city_id              INT        NOT NULL,
  city_name            STRING     NOT NULL,
  state_province       STRING,
  country              STRING,
  continent            STRING,
  sales_territory      STRING,
  region               STRING,
  subregion            STRING,
  latest_recorded_population BIGINT,
  location_wkt         STRING,            -- WKT geometry representation
  location_lat         DOUBLE,            -- decomposed latitude (see Section 3.5)
  location_lon         DOUBLE,            -- decomposed longitude (see Section 3.5)
  -- SCD2 bookkeeping
  row_effective_date   DATE       NOT NULL,
  row_expiry_date      DATE       NOT NULL   DEFAULT DATE '9999-12-31',
  is_current_row       BOOLEAN    NOT NULL   DEFAULT TRUE,
  lineage_key          BIGINT     NOT NULL,
  CONSTRAINT pk_dim_city PRIMARY KEY (city_key)
)
USING DELTA;
```

#### `globalsales.dim.stock_item`

```sql
CREATE TABLE globalsales.dim.stock_item (
  stock_item_key              INT        GENERATED ALWAYS AS IDENTITY  NOT NULL,
  stock_item_id               INT        NOT NULL,
  stock_item_name             STRING     NOT NULL,
  color                       STRING,
  selling_package             STRING,
  buying_package              STRING,
  brand                       STRING,
  size                        STRING,
  lead_time_days              INT,
  quantity_per_outer          INT,
  is_chiller_stock            BOOLEAN,
  barcode                     STRING,
  tax_rate                    DECIMAL(5,2),
  unit_price                  DECIMAL(18,2),
  recommended_retail_price    DECIMAL(18,2),
  typical_weight_per_unit     DECIMAL(18,3),
  -- SCD2 bookkeeping
  row_effective_date          DATE       NOT NULL,
  row_expiry_date             DATE       NOT NULL   DEFAULT DATE '9999-12-31',
  is_current_row              BOOLEAN    NOT NULL   DEFAULT TRUE,
  lineage_key                 BIGINT     NOT NULL,
  CONSTRAINT pk_dim_stock_item PRIMARY KEY (stock_item_key)
)
USING DELTA;
```

#### `globalsales.dim.employee`

```sql
CREATE TABLE globalsales.dim.employee (
  employee_key         INT        GENERATED ALWAYS AS IDENTITY  NOT NULL,
  employee_id          INT        NOT NULL,
  employee_name        STRING     NOT NULL,
  preferred_name       STRING,
  is_salesperson       BOOLEAN    NOT NULL,
  photo_url            STRING,
  -- SCD2 bookkeeping
  row_effective_date   DATE       NOT NULL,
  row_expiry_date      DATE       NOT NULL   DEFAULT DATE '9999-12-31',
  is_current_row       BOOLEAN    NOT NULL   DEFAULT TRUE,
  lineage_key          BIGINT     NOT NULL,
  CONSTRAINT pk_dim_employee PRIMARY KEY (employee_key)
)
USING DELTA;
```

#### `globalsales.dim.payment_method`

```sql
CREATE TABLE globalsales.dim.payment_method (
  payment_method_key   INT        GENERATED ALWAYS AS IDENTITY  NOT NULL,
  payment_method_id    INT        NOT NULL,
  payment_method_name  STRING     NOT NULL,
  -- SCD2 bookkeeping
  row_effective_date   DATE       NOT NULL,
  row_expiry_date      DATE       NOT NULL   DEFAULT DATE '9999-12-31',
  is_current_row       BOOLEAN    NOT NULL   DEFAULT TRUE,
  lineage_key          BIGINT     NOT NULL,
  CONSTRAINT pk_dim_payment_method PRIMARY KEY (payment_method_key)
)
USING DELTA;
```

#### `globalsales.dim.transaction_type`

```sql
CREATE TABLE globalsales.dim.transaction_type (
  transaction_type_key   INT        GENERATED ALWAYS AS IDENTITY  NOT NULL,
  transaction_type_id    INT        NOT NULL,
  transaction_type_name  STRING     NOT NULL,
  -- SCD2 bookkeeping
  row_effective_date     DATE       NOT NULL,
  row_expiry_date        DATE       NOT NULL   DEFAULT DATE '9999-12-31',
  is_current_row         BOOLEAN    NOT NULL   DEFAULT TRUE,
  lineage_key            BIGINT     NOT NULL,
  CONSTRAINT pk_dim_transaction_type PRIMARY KEY (transaction_type_key)
)
USING DELTA;
```

#### `globalsales.dim.date` (SCD0 — no history tracking)

```sql
CREATE TABLE globalsales.dim.date (
  date_key             INT        NOT NULL,   -- YYYYMMDD integer surrogate
  date_value           DATE       NOT NULL,
  day_number           INT        NOT NULL,
  day_name             STRING     NOT NULL,
  month_number         INT        NOT NULL,
  month_name           STRING     NOT NULL,
  short_month          STRING     NOT NULL,
  calendar_month_number INT       NOT NULL,
  calendar_month_label STRING     NOT NULL,
  calendar_year        INT        NOT NULL,
  calendar_year_label  STRING     NOT NULL,
  fiscal_month_number  INT        NOT NULL,
  fiscal_month_label   STRING     NOT NULL,
  fiscal_year          INT        NOT NULL,
  fiscal_year_label    STRING     NOT NULL,
  iso_week_number      INT        NOT NULL,
  CONSTRAINT pk_dim_date PRIMARY KEY (date_key)
)
USING DELTA;
```

No `row_effective_date` / `row_expiry_date` — date dimension is immutable (SCD0).

---

### 1.4 Silver / Fact Layer Schema

#### `globalsales.fact.sale`

Liquid clustering on `(invoice_date_key, customer_key, stock_item_key)` for optimal BI query performance (implements NFR-PERF).

```sql
CREATE TABLE globalsales.fact.sale (
  sale_key                 BIGINT  GENERATED ALWAYS AS IDENTITY  NOT NULL,
  city_key                 INT     NOT NULL,
  customer_key             INT     NOT NULL,
  bill_to_customer_key     INT     NOT NULL,
  stock_item_key           INT     NOT NULL,
  invoice_date_key         INT     NOT NULL,
  delivery_date_key        INT,
  salesperson_key          INT     NOT NULL,
  lineage_key              BIGINT  NOT NULL,   -- implements FR-LIN
  wwi_invoice_id           INT     NOT NULL,
  description              STRING,
  package                  STRING,
  quantity                 INT     NOT NULL,
  unit_price               DECIMAL(18,2) NOT NULL,
  tax_rate                 DECIMAL(5,2)  NOT NULL,
  total_excluding_tax      DECIMAL(18,2) NOT NULL,   -- quantity * unit_price
  tax_amount               DECIMAL(18,2) NOT NULL,   -- total_excluding_tax * (tax_rate / 100)
  total_including_tax      DECIMAL(18,2) NOT NULL,   -- total_excluding_tax + tax_amount
  profit                   DECIMAL(18,2) NOT NULL,
  total_dry_items          INT,
  total_chiller_items      INT,
  last_edited_when         TIMESTAMP     NOT NULL,
  CONSTRAINT pk_fact_sale PRIMARY KEY (sale_key)
)
USING DELTA
CLUSTER BY (invoice_date_key, customer_key, stock_item_key);
```

#### `globalsales.fact.order`

Partitioned by `order_date_key`; ZORDER on `(customer_key, stock_item_key)` applied via `OPTIMIZE` job (implements NFR-PERF).

```sql
CREATE TABLE globalsales.fact.order (
  order_key                BIGINT  GENERATED ALWAYS AS IDENTITY  NOT NULL,
  city_key                 INT     NOT NULL,
  customer_key             INT     NOT NULL,
  stock_item_key           INT     NOT NULL,
  order_date_key           INT     NOT NULL,
  picked_date_key          INT,
  salesperson_key          INT     NOT NULL,
  picker_key               INT,
  lineage_key              BIGINT  NOT NULL,   -- implements FR-LIN
  wwi_order_id             INT     NOT NULL,
  wwi_backorder_id         INT,
  description              STRING,
  package                  STRING,
  quantity                 INT     NOT NULL,
  unit_price               DECIMAL(18,2) NOT NULL,
  tax_rate                 DECIMAL(5,2)  NOT NULL,
  total_excluding_tax      DECIMAL(18,2) NOT NULL,
  tax_amount               DECIMAL(18,2) NOT NULL,
  total_including_tax      DECIMAL(18,2) NOT NULL,
  backorder_count          INT,              -- number of backorder associations for this order row
  pick_time_sla_met        BOOLEAN,          -- TRUE if picked_date_key - order_date_key <= configured SLA days
  is_order_finalized       BOOLEAN,
  last_edited_when         TIMESTAMP     NOT NULL,
  CONSTRAINT pk_fact_order PRIMARY KEY (order_key)
)
USING DELTA
PARTITIONED BY (order_date_key);
```

Post-load `OPTIMIZE globalsales.fact.order ZORDER BY (customer_key, stock_item_key)` is issued within the nightly ETL task for `fact.order`.

---

### 1.5 Gold / Mart Layer Objects

All mart objects live in `globalsales.mart`. Views reference Silver layer objects using three-part names.

| Object | Type | Refresh |
|---|---|---|
| `mart.v_customer_sales_summary` | Materialized view | Nightly, post silver-facts task |
| `mart.v_order_details` | Standard view | On-read; accepts `:start_date` parameter |
| `mart.v_order_to_supply_analytics` | Standard view | On-read |
| `mart.v_order_to_year_analytics` | Standard view | On-read; `:window_days` parameter (default 100) |

Full view SQL is specified in Section 4.1.

---

### 1.6 Functions

| Function | Schema | Description |
|---|---|---|
| `fact.get_total_quantity_sold` | `globalsales.fact` | Returns total quantity sold for a given stock item, with NULL guard via COALESCE. Consolidates two legacy UDF equivalents into one (implements FR-TRN). |

Full function SQL is specified in Section 4.2.

---

## 2. Ingestion Design

### 2.1 Ingestion Strategy

The ingestion strategy uses **incremental watermark-based extraction** (implements FR-ING). On each nightly run:

1. Read the current watermark for the entity from `globalsales.stg.etl_cutoff`.
2. Extract all source rows where `last_edited_when > last_cutoff_utc`.
3. Write extracted rows to the staging table (truncate-before-load pattern).
4. After successful downstream merge, advance the watermark to `batch_start_utc`.

Source connectivity is configured via Databricks Secrets (implements NFR-SEC) — see Section 6.3.

[PENDING: CX-P04] — The OLTP-direct extraction strategy is under review. Until resolved, assume a JDBC-based incremental extract from the source OLTP system. If a CDC-based alternative is selected, the watermark column may change; the `stg.etl_cutoff` design accommodates either approach by parameterising `entity_name`.

---

### 2.2 Watermark Management

Watermark reads and advances are encapsulated in a shared Python utility module `etl_utils.watermark`:

```python
# Pseudocode — etl_utils/watermark.py

def get_cutoff(spark, entity_name: str) -> datetime:
    row = spark.table("globalsales.stg.etl_cutoff") \
               .filter(f"entity_name = '{entity_name}'") \
               .select("last_cutoff_utc") \
               .first()
    return row["last_cutoff_utc"] if row else datetime(2013, 1, 1)  # history anchor

def advance_cutoff(spark, entity_name: str, new_cutoff: datetime, run_id: str):
    spark.sql(f"""
        MERGE INTO globalsales.stg.etl_cutoff AS tgt
        USING (SELECT '{entity_name}' AS entity_name,
                      CAST('{new_cutoff}' AS TIMESTAMP) AS last_cutoff_utc,
                      current_timestamp() AS updated_at_utc) AS src
        ON tgt.entity_name = src.entity_name
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
```

Watermark advance is only executed after the downstream merge completes successfully within the same Databricks Workflows task, ensuring atomicity (implements NFR-REL).

---

### 2.3 Staging Load Pattern

Staging tables follow a **truncate-before-load** pattern within each batch (implements FR-ING):

```python
# Pseudocode — ingest task for sale entity

batch_start = current_utc()
lineage_key = create_lineage_record(spark, pipeline_name="nightly_etl_main", run_id=run_id, batch_start=batch_start)
cutoff = get_cutoff(spark, "sale")

# Extract incrementally
raw_df = (
    spark.read.format("jdbc")
         .option("url", get_secret("globalsales/source_jdbc_url"))   # NFR-SEC
         .option("dbtable", source_sale_query(cutoff))
         .load()
         .withColumn("lineage_key", lit(lineage_key))                # FR-LIN
         .withColumn("_extracted_at_utc", lit(batch_start))
)

# Truncate staging and reload
spark.sql("TRUNCATE TABLE globalsales.stg.sale_staging")
raw_df.write.mode("overwrite").saveAsTable("globalsales.stg.sale_staging")

update_lineage_rows_extracted(spark, lineage_key, raw_df.count())
```

Idempotency is guaranteed by the truncate step — re-running the bronze task always produces a clean staging table (implements NFR-REL).

---

## 3. Transformation Design

### 3.1 Dimension SCD2 Merge Pattern

All six history-tracked dimensions (`dim.customer`, `dim.city`, `dim.stock_item`, `dim.employee`, `dim.payment_method`, `dim.transaction_type`) use the following SCD2 merge pattern (implements FR-TRN).

The pattern uses a two-step MERGE:

**Step 1 — Expire changed current rows:**

```sql
MERGE INTO globalsales.dim.customer AS tgt
USING (
  SELECT src.*
  FROM   globalsales.stg.customer_staging src
  JOIN   globalsales.dim.customer cur
    ON   cur.customer_id = src.customer_id
   AND   cur.is_current_row = TRUE
  WHERE  (cur.customer_name  <> src.customer_name
       OR cur.buying_group    IS DISTINCT FROM src.buying_group
       OR cur.phone_number    IS DISTINCT FROM src.phone_number
       -- ... all tracked SCD2 columns
  )
) AS changed
ON  tgt.customer_id    = changed.customer_id
AND tgt.is_current_row = TRUE
WHEN MATCHED THEN UPDATE SET
  tgt.row_expiry_date = DATE_SUB(changed.valid_from, 1),
  tgt.is_current_row  = FALSE;
```

**Step 2 — Insert new current versions:**

```sql
MERGE INTO globalsales.dim.customer AS tgt
USING (
  SELECT src.*
  FROM   globalsales.stg.customer_staging src
  LEFT ANTI JOIN globalsales.dim.customer cur
    ON  cur.customer_id    = src.customer_id
   AND  cur.is_current_row = TRUE
   AND  (cur.customer_name = src.customer_name
     -- ... all SCD2 columns match → skip unchanged rows
   )
) AS new_or_changed
ON FALSE  -- always INSERT
WHEN NOT MATCHED THEN INSERT (
  customer_id, customer_name, buying_group, phone_number, fax_number,
  -- ... all attribute columns
  row_effective_date, row_expiry_date, is_current_row, lineage_key
) VALUES (
  new_or_changed.customer_id, new_or_changed.customer_name, ...,
  new_or_changed.valid_from, DATE '9999-12-31', TRUE, :lineage_key
);
```

The pattern is implemented as a reusable Python function `scd2_merge(spark, target_table, staging_table, natural_key_col, scd2_cols, lineage_key)` in `etl_utils/scd2.py`.

`dim.date` is loaded via a one-time batch INSERT (SCD0 — static reference table). No merge pattern applies.

---

### 3.2 Fact MERGE Pattern

`fact.sale` and `fact.order` use Delta `MERGE INTO` for idempotent incremental upserts (implements FR-TRN, NFR-REL):

```sql
-- Pattern for fact.sale (fact.order follows identical structure)
MERGE INTO globalsales.fact.sale AS tgt
USING (
  SELECT
    stg.sale_key,
    stg.city_key,
    stg.customer_key,
    stg.bill_to_customer_key,
    stg.stock_item_key,
    stg.invoice_date_key,
    stg.delivery_date_key,
    stg.salesperson_key,
    stg.lineage_key,
    stg.wwi_invoice_id,
    stg.description,
    stg.package,
    stg.quantity,
    stg.unit_price,
    stg.tax_rate,
    -- Calculated fields (implements FR-TRN calculated field spec)
    stg.quantity * stg.unit_price                                          AS total_excluding_tax,
    (stg.quantity * stg.unit_price) * (stg.tax_rate / 100.0)              AS tax_amount,
    (stg.quantity * stg.unit_price) * (1 + stg.tax_rate / 100.0)         AS total_including_tax,
    stg.profit,
    stg.total_dry_items,
    stg.total_chiller_items,
    stg.last_edited_when
  FROM globalsales.stg.sale_staging stg
) AS src
ON tgt.sale_key = src.sale_key
WHEN MATCHED AND tgt.last_edited_when < src.last_edited_when THEN
  UPDATE SET
    tgt.city_key              = src.city_key,
    tgt.customer_key          = src.customer_key,
    tgt.stock_item_key        = src.stock_item_key,
    tgt.invoice_date_key      = src.invoice_date_key,
    tgt.delivery_date_key     = src.delivery_date_key,
    tgt.salesperson_key       = src.salesperson_key,
    tgt.lineage_key           = src.lineage_key,
    tgt.quantity              = src.quantity,
    tgt.unit_price            = src.unit_price,
    tgt.tax_rate              = src.tax_rate,
    tgt.total_excluding_tax   = src.total_excluding_tax,
    tgt.tax_amount            = src.tax_amount,
    tgt.total_including_tax   = src.total_including_tax,
    tgt.profit                = src.profit,
    tgt.total_dry_items       = src.total_dry_items,
    tgt.total_chiller_items   = src.total_chiller_items,
    tgt.last_edited_when      = src.last_edited_when
WHEN NOT MATCHED THEN
  INSERT *;
```

The `WHEN MATCHED` predicate `last_edited_when < src.last_edited_when` prevents stale overwrites during reruns (implements NFR-REL).

---

### 3.3 Calculated Field Implementations

All calculated fields are computed at merge time from atomic source columns. They are stored in the fact tables (not derived at query time) to meet the BI latency NFR (implements NFR-PERF).

#### On `globalsales.fact.sale`

| Column | Expression | Notes |
|---|---|---|
| `total_excluding_tax` | `quantity * unit_price` | Base revenue before tax |
| `tax_amount` | `total_excluding_tax * (tax_rate / 100.0)` | Computed from the above |
| `total_including_tax` | `total_excluding_tax + tax_amount` | Gross revenue |
| `profit` | Sourced from source system; validated non-NULL post-DQ | Source provides cost-basis profit |
| `total_dry_items` | Sourced from source system | Count of ambient-temperature line items |
| `total_chiller_items` | Sourced from source system | Count of chilled line items |

#### On `globalsales.fact.order`

| Column | Expression | Notes |
|---|---|---|
| `total_excluding_tax` | `quantity * unit_price` | Mirrors fact.sale pattern |
| `tax_amount` | `total_excluding_tax * (tax_rate / 100.0)` | |
| `total_including_tax` | `total_excluding_tax + tax_amount` | |
| `backorder_count` | `CASE WHEN wwi_backorder_id IS NOT NULL THEN 1 ELSE 0 END` summed at row level | Incremented per backorder association |
| `pick_time_sla_met` | `CASE WHEN picked_date_key IS NOT NULL AND (picked_date_key - order_date_key) <= :sla_threshold_days THEN TRUE ELSE FALSE END` | SLA threshold externalised as config constant |

#### On `globalsales.mart.v_customer_sales_summary`

| Column | Expression | Notes |
|---|---|---|
| `profit_margin_with_factor` | `(profit / NULLIF(total_including_tax, 0)) * 100 * 1.05` | `1.05` = `PROFIT_MARGIN_FACTOR` constant (implements NFR-MAINT). The factor is externalised as a named constant; see Section 4.1. |

---

### 3.4 UDF Implementation (get_total_quantity_sold)

`fact.get_total_quantity_sold` consolidates two legacy UDF equivalents into a single Delta SQL function (implements FR-TRN). NULL input is guarded via `COALESCE`.

```sql
CREATE OR REPLACE FUNCTION globalsales.fact.get_total_quantity_sold(
  p_stock_item_key BIGINT,
  p_start_date     DATE,
  p_end_date       DATE
)
RETURNS BIGINT
LANGUAGE SQL
COMMENT 'Returns total quantity sold for a given stock item within the specified date range. Returns 0 (not NULL) when no records found or input is NULL. Date range is applied via invoice_date_key (YYYYMMDD). Consolidates legacy UDF duplicates per OB-EXTEND-001.'
RETURN
  SELECT COALESCE(SUM(s.quantity), 0)
  FROM   globalsales.fact.sale s
  WHERE  s.stock_item_key    = COALESCE(p_stock_item_key, -1)
    AND  s.invoice_date_key BETWEEN
           CAST(DATE_FORMAT(p_start_date, 'yyyyMMdd') AS INT)
       AND CAST(DATE_FORMAT(p_end_date,   'yyyyMMdd') AS INT);
-- COALESCE on the key parameter prevents full-table scans when NULL is passed
```

Usage example:

```sql
SELECT
  si.stock_item_name,
  globalsales.fact.get_total_quantity_sold(
    si.stock_item_key,
    DATE'2024-01-01',
    DATE'2024-12-31'
  ) AS total_qty_sold
FROM globalsales.dim.stock_item si
WHERE si.is_current_row = TRUE;
```

---

### 3.5 Geography Decomposition

`dim.city` stores the source geometry in `location_wkt` (WKT string) and also pre-computes `location_lat` / `location_lon` DOUBLE columns to enable direct BI latitude/longitude queries without WKT parsing at query time (implements NFR-PERF).

Decomposition is applied during the SCD2 merge transformation:

```python
# Pseudocode — city staging enrichment
from pyspark.sql.functions import col, regexp_extract

city_df = city_staging_df.withColumn(
    "location_lat",
    regexp_extract(col("location_wkt"), r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", 2).cast("double")
).withColumn(
    "location_lon",
    regexp_extract(col("location_wkt"), r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", 1).cast("double")
)
```

If `location_wkt` is NULL or unparseable, both `location_lat` and `location_lon` are set to NULL. The WKT string is preserved as-is regardless.

---

## 4. Serving Design

### 4.1 Mart View Designs

#### `globalsales.mart.v_customer_sales_summary` (Materialized)

Refreshed nightly as the final task in `nightly_etl_main` (implements FR-SRV). `PROFIT_MARGIN_FACTOR` is externalised as a Spark config key `globalsales.profit_margin_factor` defaulting to `1.05` (implements NFR-MAINT).

```sql
CREATE OR REPLACE MATERIALIZED VIEW globalsales.mart.v_customer_sales_summary AS
SELECT
  c.customer_id,
  c.customer_name,
  c.buying_group,
  c.customer_category,
  ci.city_name,
  ci.country,
  ci.sales_territory,
  d.calendar_year,
  d.calendar_month_label,
  SUM(fs.quantity)              AS total_quantity_sold,
  SUM(fs.total_excluding_tax)   AS total_revenue_ex_tax,
  SUM(fs.total_including_tax)   AS total_revenue_inc_tax,
  SUM(fs.profit)                AS total_profit,
  -- profit_margin_with_factor: PROFIT_MARGIN_FACTOR = 1.05 (externalised constant)
  (SUM(fs.profit) / NULLIF(SUM(fs.total_including_tax), 0)) * 100 * 1.05
                                AS profit_margin_with_factor
FROM       globalsales.fact.sale        fs
JOIN       globalsales.dim.customer     c   ON c.customer_key  = fs.customer_key     AND c.is_current_row  = TRUE
JOIN       globalsales.dim.city         ci  ON ci.city_key     = fs.city_key         AND ci.is_current_row = TRUE
JOIN       globalsales.dim.date         d   ON d.date_key      = fs.invoice_date_key
GROUP BY
  c.customer_id, c.customer_name, c.buying_group, c.customer_category,
  ci.city_name, ci.country, ci.sales_territory,
  d.calendar_year, d.calendar_month_label;
```

> If Databricks Photon materialized views are not available in the target workspace tier, this view is implemented as a standard Delta table refreshed via a scheduled `INSERT OVERWRITE` task. [PENDING: CX-P05] — access grants on this view depend on the role matrix.

---

#### `globalsales.mart.v_order_details`

Accepts a `:start_date` parameter to scope order history for BI tools that support parameterised views. Falls back to a static date predicate when called without the parameter.

```sql
CREATE OR REPLACE VIEW globalsales.mart.v_order_details AS
SELECT
  fo.order_key,
  fo.wwi_order_id,
  fo.wwi_backorder_id,
  c.customer_name,
  c.customer_category,
  ci.city_name,
  ci.country,
  si.stock_item_name,
  si.color,
  si.selling_package,
  d.date_value                  AS order_date,
  pd.date_value                 AS picked_date,
  fo.quantity,
  fo.unit_price,
  fo.total_excluding_tax,
  fo.total_including_tax,
  fo.backorder_count,
  fo.pick_time_sla_met,
  fo.is_order_finalized
FROM       globalsales.fact.order        fo
JOIN       globalsales.dim.customer      c   ON c.customer_key   = fo.customer_key   AND c.is_current_row  = TRUE
JOIN       globalsales.dim.city          ci  ON ci.city_key      = fo.city_key       AND ci.is_current_row = TRUE
JOIN       globalsales.dim.stock_item    si  ON si.stock_item_key = fo.stock_item_key AND si.is_current_row = TRUE
JOIN       globalsales.dim.date          d   ON d.date_key       = fo.order_date_key
LEFT JOIN  globalsales.dim.date          pd  ON pd.date_key      = fo.picked_date_key
WHERE  d.date_value >= :start_date;   -- BI parameter; supply '2013-01-01' for full history
```

---

#### `globalsales.mart.v_order_to_supply_analytics`

Analytical view joining orders with stock item supply attributes. The legacy `NOLOCK` hint has been removed — Delta ACID transactions render it unnecessary.

```sql
CREATE OR REPLACE VIEW globalsales.mart.v_order_to_supply_analytics AS
SELECT
  fo.order_key,
  fo.wwi_order_id,
  d.calendar_year,
  d.calendar_month_number,
  c.customer_name,
  c.sales_territory,
  si.stock_item_name,
  si.is_chiller_stock,
  si.lead_time_days,
  si.quantity_per_outer,
  fo.quantity                       AS ordered_quantity,
  fo.total_including_tax            AS order_value_inc_tax,
  fo.backorder_count,
  fo.pick_time_sla_met
FROM       globalsales.fact.order        fo
JOIN       globalsales.dim.customer      c   ON c.customer_key    = fo.customer_key   AND c.is_current_row  = TRUE
JOIN       globalsales.dim.stock_item    si  ON si.stock_item_key  = fo.stock_item_key AND si.is_current_row = TRUE
JOIN       globalsales.dim.city          ci  ON ci.city_key        = fo.city_key       AND ci.is_current_row = TRUE
JOIN       globalsales.dim.date          d   ON d.date_key         = fo.order_date_key;
-- Note: NOLOCK removed — Delta ACID guarantees read consistency without advisory hints
```

---

#### `globalsales.mart.v_order_to_year_analytics`

Rolling window analysis. `:window_days` parameter defaults to `100`.

```sql
CREATE OR REPLACE VIEW globalsales.mart.v_order_to_year_analytics AS
SELECT
  fo.order_key,
  fo.wwi_order_id,
  d.date_value                          AS order_date,
  d.calendar_year,
  d.fiscal_year,
  c.customer_name,
  c.customer_category,
  si.stock_item_name,
  fo.quantity,
  fo.total_including_tax,
  fo.backorder_count,
  fo.pick_time_sla_met,
  -- Rolling window sum over configurable number of days
  SUM(fo.total_including_tax) OVER (
    PARTITION BY fo.customer_key, fo.stock_item_key
    ORDER BY d.date_value
    RANGE BETWEEN INTERVAL :window_days DAYS PRECEDING AND CURRENT ROW
  )                                     AS rolling_window_revenue,
  -- Default window_days = 100 when parameter not supplied by caller
  :window_days                          AS window_days_used
FROM       globalsales.fact.order       fo
JOIN       globalsales.dim.customer     c   ON c.customer_key    = fo.customer_key   AND c.is_current_row = TRUE
JOIN       globalsales.dim.stock_item   si  ON si.stock_item_key  = fo.stock_item_key AND si.is_current_row = TRUE
JOIN       globalsales.dim.date         d   ON d.date_key        = fo.order_date_key;
```

---

### 4.2 Function Interface

#### `globalsales.fact.get_total_quantity_sold`

| Attribute | Value |
|---|---|
| Function type | Delta SQL scalar function |
| Input | `p_stock_item_key BIGINT`, `p_start_date DATE`, `p_end_date DATE` |
| Returns | `BIGINT` |
| NULL handling | COALESCE on `p_stock_item_key`; COALESCE on aggregate result — always returns 0 on NULL/missing |
| Replaces | Two legacy UDF equivalents (consolidation, implements FR-TRN) |

Full DDL is in Section 3.4.

---

### 4.3 BI Endpoint Configuration

Mart views are served via a **Databricks SQL Serverless endpoint** (implements FR-SRV).

Configuration parameters:

| Parameter | Value | Notes |
|---|---|---|
| Endpoint type | Serverless SQL Warehouse | Auto-scaling |
| Catalog binding | `globalsales` | Default catalog on connection |
| Query result cache | Enabled | Reduces repeated BI query load |
| Target query latency | ≤ 5 s p95 | NFR-PERF |
| Cluster size | Auto (start: Small) | Scale up if p95 latency breached |

Endpoint connection credentials are distributed via Databricks Secrets and injected into BI tool connection strings (implements NFR-SEC). [PENDING: CX-P05] — specific user/group role bindings on the SQL endpoint are pending the access role matrix approval.

---

## 5. Observability Design

### 5.1 Lineage Tracking

Every ETL run creates a `stg.lineage` record at the start of the batch task and closes it (status = `SUCCESS` or `FAILED`) at the end. The `lineage_key` is propagated to all rows in staging and fact tables (implements FR-LIN).

Lineage write pattern:

```python
# Pseudocode — create lineage record at task start
def create_lineage_record(spark, pipeline_name, run_id, batch_start) -> int:
    spark.sql(f"""
        INSERT INTO globalsales.stg.lineage
          (pipeline_run_id, pipeline_name, batch_start_utc, status)
        VALUES ('{run_id}', '{pipeline_name}', '{batch_start}', 'RUNNING')
    """)
    return spark.sql("SELECT MAX(lineage_key) FROM globalsales.stg.lineage").collect()[0][0]

def close_lineage_record(spark, lineage_key, rows_extracted, rows_loaded, rows_rejected, status):
    spark.sql(f"""
        UPDATE globalsales.stg.lineage SET
          batch_end_utc  = current_timestamp(),
          rows_extracted = {rows_extracted},
          rows_loaded    = {rows_loaded},
          rows_rejected  = {rows_rejected},
          status         = '{status}'
        WHERE lineage_key = {lineage_key}
    """)
```

Row-level lineage is queryable:

```sql
-- Which batch loaded a specific sale row?
SELECT l.*
FROM   globalsales.fact.sale  s
JOIN   globalsales.stg.lineage l ON l.lineage_key = s.lineage_key
WHERE  s.sale_key = :target_sale_key;
```

---

### 5.2 Data Quality Assertion Implementation

DQ assertions run post-merge, within the same task, before the watermark is advanced (implements DQR). On assertion failure, offending rows are written to `stg.dq_rejections` and the task halts (zero-tolerance pattern).

#### Assertion catalogue

| ID | Target Table | Assertion | Action on Failure |
|---|---|---|---|
| DQ-SALE-001 | `fact.sale` | `quantity > 0` for all rows in current batch | Reject rows to `stg.dq_rejections`; halt task |
| DQ-SALE-002 | `fact.sale` | `total_including_tax >= total_excluding_tax` (tax non-negative) | Reject rows; halt task |
| DQ-ORDER-001 | `fact.order` | `quantity > 0` for all rows in current batch | Reject rows; halt task |
| DQ-ORDER-RI-001 | `fact.order` | `customer_key` exists in `dim.customer` (`is_current_row = TRUE`) | Reject rows; halt task |
| DQ-ORDER-RI-002 | `fact.order` | `stock_item_key` exists in `dim.stock_item` (`is_current_row = TRUE`) | Reject rows; halt task |

[PENDING: CX-DQ-01] — Business-defined thresholds for acceptable rejection rate are under review. Currently zero-tolerance (any rejection = halt). Once approved thresholds are available, the assertion framework will be updated to apply percentage-based triggers where indicated.

#### Assertion implementation pattern

```python
# Pseudocode — DQ assertion runner
def run_dq_assertion(spark, assertion_id, source_table, predicate_sql, lineage_key):
    """
    Checks predicate_sql against source_table for the current lineage_key batch.
    Rejections are written to stg.dq_rejections. Raises AssertionError if any row fails.
    """
    rejection_df = spark.sql(f"""
        SELECT
            CAST({lineage_key}     AS BIGINT)  AS lineage_key,
            '{assertion_id}'                   AS assertion_id,
            '{source_table}'                   AS source_table,
            sale_key                           AS source_key,   -- adjust PK per table
            'Failed predicate: {predicate_sql}' AS rejection_reason,
            current_timestamp()                AS rejected_at_utc,
            to_json(struct(*))                 AS raw_payload
        FROM {source_table}
        WHERE lineage_key = {lineage_key}
          AND NOT ({predicate_sql})
    """)

    count = rejection_df.count()
    if count > 0:
        rejection_df.write.mode("append").saveAsTable("globalsales.stg.dq_rejections")
        raise AssertionError(
            f"[{assertion_id}] {count} rows failed assertion on {source_table}. "
            f"Rows written to stg.dq_rejections. Halting task."
        )
```

Zero-tolerance row count reconciliation:

```python
# Row count reconciliation — extracted vs loaded
def assert_row_count_reconciliation(extracted_count, loaded_count, rejected_count):
    expected_loaded = extracted_count - rejected_count
    if loaded_count != expected_loaded:
        raise AssertionError(
            f"Row count mismatch: extracted={extracted_count}, "
            f"rejected={rejected_count}, loaded={loaded_count}, "
            f"expected_loaded={expected_loaded}"
        )
```

---

### 5.3 ETL Monitoring and Alerting

The `nightly_etl_main` Databricks Workflow is configured with (implements FR-ORC):

| Parameter | Value |
|---|---|
| Schedule | `0 2 * * *` UTC (nightly, 02:00) |
| Retry policy | 2 retries on transient failures |
| On failure | Halt-and-alert: email + webhook notification |
| Max run duration | 4 hours (NFR-PERF SLA) |
| Alert channel | Configured via Databricks Notifications |

Task execution order within the DAG:

```
[bronze_ingest_sale]  ──┐
[bronze_ingest_order] ──┤
[bronze_ingest_dims]  ──┘
        │
        ▼
[silver_dims_scd2_merge]  (all 6 SCD2 dimensions in parallel where dependency allows)
        │
        ▼
[silver_facts_merge]      (fact.sale and fact.order — may run in parallel)
        │
        ▼
[gold_mart_refresh]       (materialized view refresh for v_customer_sales_summary)
        │
        ▼
[dq_post_validation]      (row count reconciliation, cross-table DQ summary report)
```

ETL run metrics (rows extracted/loaded/rejected, task durations) are queryable from `stg.lineage`. Long-term dashboarding against `stg.lineage` is possible via a Databricks SQL query on the Unity Catalog.

---

## 6. Security Design

### 6.1 Unity Catalog Access Control

All access control is managed through Unity Catalog RBAC (implements NFR-SEC). [PENDING: CX-P05] — the full access role matrix is pending approval; the following is the minimum design.

#### Catalog-level grants

```sql
-- Workspace service principal used by nightly_etl_main
GRANT USE CATALOG ON CATALOG globalsales TO `nightly_etl_sp`;

-- Read-only access for BI tools / analysts
GRANT USE CATALOG ON CATALOG globalsales TO `globalsales_bi_role`;
```

#### Schema-level grants

```sql
-- ETL service principal: full access to stg, dim, fact
GRANT USE SCHEMA, CREATE TABLE, MODIFY ON SCHEMA globalsales.stg  TO `nightly_etl_sp`;
GRANT USE SCHEMA, CREATE TABLE, MODIFY ON SCHEMA globalsales.dim  TO `nightly_etl_sp`;
GRANT USE SCHEMA, CREATE TABLE, MODIFY ON SCHEMA globalsales.fact TO `nightly_etl_sp`;

-- Mart access for BI role
GRANT USE SCHEMA, SELECT ON SCHEMA globalsales.mart TO `globalsales_bi_role`;

-- Analysts: read Silver (non-PII columns surfaced through masking policies)
GRANT USE SCHEMA, SELECT ON SCHEMA globalsales.dim  TO `globalsales_analyst_role`;
GRANT USE SCHEMA, SELECT ON SCHEMA globalsales.fact TO `globalsales_analyst_role`;
```

Row-level security (RLS) policies on `dim.customer` and `fact.sale` restrict data by sales territory based on the caller's group membership, using Unity Catalog Row Filters.

---

### 6.2 PII Masking Implementation

PII columns on `globalsales.dim.customer` are masked using Unity Catalog **Column Masks** (implements NFR-SEC):

Masked columns: `customer_name`, `phone_number`, `fax_number`, `buying_group`.

```sql
-- Create masking function for PII string columns
CREATE OR REPLACE FUNCTION globalsales.dim.mask_pii_string(col_value STRING)
RETURNS STRING
LANGUAGE SQL
COMMENT 'Returns full value for PII-authorised principals; masked value otherwise.'
RETURN
  CASE
    WHEN is_account_group_member('globalsales_pii_authorised')
    THEN col_value
    ELSE '****'
  END;

-- Apply mask to customer_name
ALTER TABLE globalsales.dim.customer
  ALTER COLUMN customer_name
  SET MASK globalsales.dim.mask_pii_string;

-- Apply mask to phone_number
ALTER TABLE globalsales.dim.customer
  ALTER COLUMN phone_number
  SET MASK globalsales.dim.mask_pii_string;

-- Apply mask to fax_number
ALTER TABLE globalsales.dim.customer
  ALTER COLUMN fax_number
  SET MASK globalsales.dim.mask_pii_string;

-- Apply mask to buying_group
ALTER TABLE globalsales.dim.customer
  ALTER COLUMN buying_group
  SET MASK globalsales.dim.mask_pii_string;
```

Members of the `globalsales_pii_authorised` group receive unmasked values. All other principals see `'****'`. The masking function is applied transparently at query time without changing downstream SQL.

---

### 6.3 Secrets Management

All credentials are stored in **Databricks Secrets** and accessed via `dbutils.secrets.get()` (implements NFR-SEC). No credentials are hardcoded in notebooks, configuration files, or task parameters.

| Secret scope | Key | Used for |
|---|---|---|
| `globalsales` | `source_jdbc_url` | OLTP source JDBC connection URL [PENDING: CX-P04] |
| `globalsales` | `source_jdbc_user` | OLTP source credential |
| `globalsales` | `source_jdbc_password` | OLTP source credential |
| `globalsales` | `bi_endpoint_token` | Databricks SQL endpoint PAT for BI tool connections |

Secret access pattern:

```python
# Pseudocode — secret retrieval in ETL notebook
jdbc_url      = dbutils.secrets.get(scope="globalsales", key="source_jdbc_url")
jdbc_user     = dbutils.secrets.get(scope="globalsales", key="source_jdbc_user")
jdbc_password = dbutils.secrets.get(scope="globalsales", key="source_jdbc_password")

source_df = (
    spark.read.format("jdbc")
         .option("url",      jdbc_url)
         .option("user",     jdbc_user)
         .option("password", jdbc_password)
         .option("dbtable",  extract_query)
         .load()
)
```

The `nightly_etl_sp` service principal is granted `READ` on the `globalsales` secret scope. No other principals have access.
