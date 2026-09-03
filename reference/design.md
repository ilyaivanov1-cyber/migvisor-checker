# Design: Purchase

**Product:** Purchase · **Project:** GlobalPurchase_Project
**Source:** product-definition.yaml + requirements.md · **Date:** 2026-08-25
**Status:** draft

---

## Data Model

### 1. Entity-Relationship Overview

The `globalpurchase` catalog is organized into four schemas that form a medallion-style layered architecture. Each schema has a single, clearly bounded responsibility.

| Schema | Role | Object types |
|---|---|---|
| `globalpurchase.stg` | Transient staging, pipeline control, audit | Delta tables (transient or persistent) |
| `globalpurchase.dim` | Conformed dimensions (SCD-2 where noted, static calendar) | Delta tables |
| `globalpurchase.fact` | Central fact table for purchase activity | Delta table |
| `globalpurchase.mart` | Serving layer for BI and analytical consumption | Views / materialized views (defined in Serving section) |

#### Logical relationship map

```
stg.etl_cutoff ──────────────────────────────────────────────►  (controls incremental watermark)

stg.purchase_staging ─────────────────────────────────────────►  fact.purchase
                                                                  │
                                                            ┌─────┴─────────────────┐
                                                            │                       │
                                                          dim.date           dim.supplier
                                                          dim.stock_item     stg.lineage

dim.supplier    ──► stg.lineage  (lineage_key)
dim.stock_item  ──► stg.lineage  (lineage_key)

stg.dq_rejections ◄── ETL pipelines (records failed DQ checks per batch)

mart.*          ──► fact.purchase + dim.* (read-only; defined in Serving section)
```

**Join keys between objects:**

| Parent table | Child table | Join key |
|---|---|---|
| `dim.date` | `fact.purchase` | `date_key` (YYYYMMDD integer) |
| `dim.supplier` | `fact.purchase` | `supplier_key` (surrogate) |
| `dim.stock_item` | `fact.purchase` | `stock_item_key` (surrogate) |
| `stg.lineage` | `fact.purchase` | `lineage_key` |
| `stg.lineage` | `dim.supplier` | `lineage_key` |
| `stg.lineage` | `dim.stock_item` | `lineage_key` |
| `stg.lineage` | `stg.dq_rejections` | `lineage_key` |

All relationships are logical. Physical `FOREIGN KEY` constraints are not emitted in Delta Lake DDL; referential integrity is enforced at the ETL layer (see Section 1.5).

---

### 2. Table DDL

All tables reside in the `globalpurchase` catalog. DDL uses Spark SQL syntax with Delta Lake table format.

---

#### 2.1 `globalpurchase.fact.purchase`

Central fact table. One row per purchase order line. Loaded incrementally via MERGE using `wwi_purchase_order_id` as the natural key. Change Data Feed is disabled because downstream consumers query snapshots, not change streams.

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.fact.purchase (
    purchase_key          BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL
                              COMMENT 'Surrogate primary key, system-assigned',
    date_key              INT NOT NULL
                              COMMENT 'FK → dim.date.date_key (YYYYMMDD); identifies the order date',
    supplier_key          INT NOT NULL
                              COMMENT 'FK → dim.supplier.supplier_key (current SCD-2 row)',
    stock_item_key        INT NOT NULL
                              COMMENT 'FK → dim.stock_item.stock_item_key (current SCD-2 row)',
    wwi_purchase_order_id INT
                              COMMENT 'Source system natural/business key; used as MERGE predicate',
    ordered_outers        INT
                              COMMENT 'Number of outer packages ordered',
    ordered_quantity      INT
                              COMMENT 'Total individual units ordered',
    received_outers       INT
                              COMMENT 'Number of outer packages actually received',
    package               STRING
                              COMMENT 'Package type description (e.g. Each, Carton)',
    is_order_finalized    BOOLEAN
                              COMMENT 'True when the purchase order has been fully confirmed',
    lineage_key           BIGINT NOT NULL
                              COMMENT 'FK → stg.lineage.lineage_key; links row to pipeline run',
    CONSTRAINT pk_fact_purchase PRIMARY KEY (purchase_key)
)
USING DELTA
CLUSTER BY (date_key, supplier_key, stock_item_key)
COMMENT 'Fact table: purchase order lines from the source purchasing domain'
TBLPROPERTIES (
    'delta.enableChangeDataFeed'          = 'false',
    'delta.deletedFileRetentionDuration'  = 'interval 2555 days',
    'delta.logRetentionDuration'          = 'interval 2555 days'
);
```

---

#### 2.2 `globalpurchase.dim.supplier` (SCD Type 2)

Supplier conformed dimension. Tracks historical changes to supplier attributes using SCD Type 2. Change Data Feed is enabled to support downstream incremental dimension lookups.

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.dim.supplier (
    supplier_key            INT GENERATED ALWAYS AS IDENTITY NOT NULL
                                COMMENT 'Surrogate primary key, system-assigned',
    wwi_supplier_id         INT NOT NULL
                                COMMENT 'Source system supplier identifier; used as SCD-2 lookup key',
    supplier_name           STRING NOT NULL
                                COMMENT 'Full legal or trading name of the supplier',
    supplier_category_name  STRING
                                COMMENT 'Supplier category as defined in the source system',
    primary_contact         STRING
                                COMMENT 'Name of the primary contact person at the supplier',
    phone_number            STRING
                                COMMENT 'Main telephone number',
    fax_number              STRING
                                COMMENT 'Fax number, if applicable',
    website_url             STRING
                                COMMENT 'Supplier website URL',
    delivery_city_name      STRING
                                COMMENT 'City used for delivery address',
    delivery_postal_code    STRING
                                COMMENT 'Postal code for delivery address',
    delivery_country_name   STRING
                                COMMENT 'Country for delivery address',
    payment_days            INT
                                COMMENT 'Standard payment terms in days',
    valid_from              DATE NOT NULL
                                COMMENT 'Inclusive start date of this version (source effective date)',
    valid_to                DATE NOT NULL
                                COMMENT 'Inclusive end date of this version; 9999-12-31 = current',
    row_effective_date      DATE NOT NULL
                                COMMENT 'Date this row was inserted into the dimension',
    row_expiry_date         DATE NOT NULL DEFAULT DATE '9999-12-31'
                                COMMENT 'Date this row was logically closed; 9999-12-31 = open',
    is_current_row          BOOLEAN NOT NULL DEFAULT TRUE
                                COMMENT 'True for the single active version of each supplier',
    lineage_key             BIGINT NOT NULL
                                COMMENT 'FK → stg.lineage.lineage_key; links row to pipeline run',
    CONSTRAINT pk_dim_supplier PRIMARY KEY (supplier_key)
)
USING DELTA
COMMENT 'SCD Type 2 supplier dimension; tracks full attribute history'
TBLPROPERTIES (
    'delta.enableChangeDataFeed'          = 'true',
    'delta.deletedFileRetentionDuration'  = 'interval 2555 days',
    'delta.logRetentionDuration'          = 'interval 2555 days'
);
```

---

#### 2.3 `globalpurchase.dim.stock_item` (SCD Type 2)

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.dim.stock_item (
    stock_item_key              INT GENERATED ALWAYS AS IDENTITY NOT NULL
                                    COMMENT 'Surrogate primary key, system-assigned',
    wwi_stock_item_id           INT NOT NULL
                                    COMMENT 'Source system stock item identifier; used as SCD-2 lookup key',
    stock_item_name             STRING NOT NULL
                                    COMMENT 'Full descriptive name of the stock item',
    color                       STRING
                                    COMMENT 'Color of the item, if applicable',
    size                        STRING
                                    COMMENT 'Size descriptor of the item, if applicable',
    unit_package_name           STRING
                                    COMMENT 'Packaging type for individual units (e.g. Each)',
    outer_package_name          STRING
                                    COMMENT 'Packaging type for outer containers (e.g. Carton)',
    brand                       STRING
                                    COMMENT 'Brand name of the item',
    description                 STRING
                                    COMMENT 'Long-form product description',
    unit_price                  DECIMAL(18, 2)
                                    COMMENT 'Standard unit price in source currency',
    recommended_retail_price    DECIMAL(18, 2)
                                    COMMENT 'Recommended retail price, if set',
    typical_weight_per_unit     DECIMAL(18, 3)
                                    COMMENT 'Typical weight per unit in kilograms',
    is_chiller_stock            BOOLEAN
                                    COMMENT 'True if item requires cold-chain storage',
    tax_rate                    DECIMAL(18, 3)
                                    COMMENT 'Applicable tax rate percentage',
    valid_from                  DATE NOT NULL
                                    COMMENT 'Inclusive start date of this version',
    valid_to                    DATE NOT NULL
                                    COMMENT 'Inclusive end date of this version; 9999-12-31 = current',
    row_effective_date          DATE NOT NULL
                                    COMMENT 'Date this row was inserted into the dimension',
    row_expiry_date             DATE NOT NULL DEFAULT DATE '9999-12-31'
                                    COMMENT 'Date this row was logically closed; 9999-12-31 = open',
    is_current_row              BOOLEAN NOT NULL DEFAULT TRUE
                                    COMMENT 'True for the single active version of each stock item',
    lineage_key                 BIGINT NOT NULL
                                    COMMENT 'FK → stg.lineage.lineage_key; links row to pipeline run',
    CONSTRAINT pk_dim_stock_item PRIMARY KEY (stock_item_key)
)
USING DELTA
COMMENT 'SCD Type 2 stock item dimension; tracks full attribute history'
TBLPROPERTIES (
    'delta.enableChangeDataFeed'          = 'true',
    'delta.deletedFileRetentionDuration'  = 'interval 2555 days',
    'delta.logRetentionDuration'          = 'interval 2555 days'
);
```

---

#### 2.4 `globalpurchase.dim.date` (Static Calendar)

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.dim.date (
    date_key          INT NOT NULL
                          COMMENT 'Primary key in YYYYMMDD format; matches fact.purchase.date_key',
    calendar_date     DATE NOT NULL
                          COMMENT 'Full calendar date value',
    year              INT NOT NULL,
    quarter           INT NOT NULL,
    month             INT NOT NULL,
    month_name        STRING NOT NULL,
    day               INT NOT NULL,
    day_of_week       STRING NOT NULL,
    day_of_week_num   INT NOT NULL
                          COMMENT 'Weekday number: 1 = Monday, 7 = Sunday (ISO-8601)',
    week_of_year      INT NOT NULL,
    is_weekend        BOOLEAN NOT NULL,
    is_public_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    fiscal_year       INT,
    fiscal_quarter    INT,
    CONSTRAINT pk_dim_date PRIMARY KEY (date_key)
)
USING DELTA
COMMENT 'Static calendar dimension; one row per calendar date; no SCD-2 tracking'
TBLPROPERTIES (
    'delta.deletedFileRetentionDuration'  = 'interval 2555 days',
    'delta.logRetentionDuration'          = 'interval 2555 days'
);
```

---

#### 2.5 `globalpurchase.stg.purchase_staging` (Transient Staging)

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.stg.purchase_staging (
    purchase_order_id       INT       COMMENT 'Source purchase order identifier',
    supplier_id             INT       COMMENT 'Source supplier identifier; resolved to supplier_key in dim load',
    stock_item_id           INT       COMMENT 'Source stock item identifier; resolved to stock_item_key in dim load',
    order_date              DATE      COMMENT 'Date the purchase order was placed',
    expected_delivery_date  DATE      COMMENT 'Expected delivery date from supplier',
    ordered_outers          INT,
    ordered_quantity        INT,
    received_outers         INT,
    package                 STRING,
    is_order_finalized      BOOLEAN,
    lineage_key             BIGINT    NOT NULL COMMENT 'FK → stg.lineage.lineage_key',
    _extracted_at_utc       TIMESTAMP NOT NULL COMMENT 'UTC timestamp at extraction time'
)
USING DELTA
COMMENT 'Transient staging table for purchase order extracts; truncated on each pipeline run'
TBLPROPERTIES (
    'delta.deletedFileRetentionDuration'  = 'interval 90 days',
    'delta.logRetentionDuration'          = 'interval 90 days'
);
```

---

#### 2.6 `globalpurchase.stg.etl_cutoff`

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.stg.etl_cutoff (
    entity_name      STRING    NOT NULL COMMENT 'Logical entity name (e.g. purchase)',
    last_cutoff_time TIMESTAMP NOT NULL COMMENT 'UTC timestamp of the latest successfully processed source record',
    CONSTRAINT pk_stg_etl_cutoff PRIMARY KEY (entity_name)
)
USING DELTA
COMMENT 'Incremental watermark control table; one row per monitored entity'
TBLPROPERTIES (
    'delta.deletedFileRetentionDuration'  = 'interval 2555 days',
    'delta.logRetentionDuration'          = 'interval 2555 days'
);
```

---

#### 2.7 `globalpurchase.stg.lineage`

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.stg.lineage (
    lineage_key      BIGINT    GENERATED ALWAYS AS IDENTITY NOT NULL COMMENT 'Surrogate PK; referenced by all target tables',
    pipeline_run_id  STRING    NOT NULL COMMENT 'Databricks Workflow run ID',
    entity_name      STRING    NOT NULL COMMENT 'Logical entity being loaded',
    started_at       TIMESTAMP NOT NULL,
    completed_at     TIMESTAMP,
    status           STRING    COMMENT 'running | success | failed',
    source_row_count BIGINT,
    rows_loaded      BIGINT,
    CONSTRAINT pk_stg_lineage PRIMARY KEY (lineage_key)
)
USING DELTA
COMMENT 'Pipeline run audit log; primary lineage anchor for all target tables'
TBLPROPERTIES (
    'delta.deletedFileRetentionDuration'  = 'interval 2555 days',
    'delta.logRetentionDuration'          = 'interval 2555 days'
);
```

---

#### 2.8 `globalpurchase.stg.dq_rejections`

```sql
CREATE TABLE IF NOT EXISTS globalpurchase.stg.dq_rejections (
    rejection_key      BIGINT    GENERATED ALWAYS AS IDENTITY NOT NULL,
    dq_rule_id         STRING    NOT NULL,
    batch_id           STRING    NOT NULL,
    lineage_key        BIGINT,
    affected_column    STRING,
    observed_value     STRING,
    expected_condition STRING,
    severity           STRING    NOT NULL COMMENT 'WARNING | ERROR | CRITICAL',
    recorded_at        TIMESTAMP NOT NULL,
    CONSTRAINT pk_stg_dq_rejections PRIMARY KEY (rejection_key)
)
USING DELTA
COMMENT 'Data quality rejection log; one row per DQ rule failure per pipeline run'
TBLPROPERTIES (
    'delta.deletedFileRetentionDuration'  = 'interval 90 days',
    'delta.logRetentionDuration'          = 'interval 90 days'
);
```

---

### 3. Table Naming Conventions

| Convention | Rule applied |
|---|---|
| **Catalog** | Single catalog `globalpurchase`; scopes all product objects |
| **Schema** | Functional layer: `stg`, `dim`, `fact`, `mart` |
| **Table name** | Singular noun, snake_case, no abbreviations except well-known (`dq`, `etl`) |
| **Column name** | snake_case; boolean columns prefixed with `is_` |
| **Primary key constraint** | `pk_<schema>_<table>` |
| **Surrogate key column** | `<table_singular>_key` |
| **Natural/business key** | Prefixed `wwi_` to signal source system provenance |
| **SCD-2 tracking columns** | `valid_from`, `valid_to`, `row_effective_date`, `row_expiry_date`, `is_current_row` |
| **Pipeline audit columns** | `lineage_key`, `_extracted_at_utc` |

---

### 4. Retention Policy (NFR-008)

| Table | `deletedFileRetentionDuration` | `logRetentionDuration` | Rationale |
|---|---|---|---|
| `fact.purchase` | 2555 days | 2555 days | Regulatory requirement for financial transaction history |
| `dim.supplier` | 2555 days | 2555 days | SCD-2 history must be co-retained with fact |
| `dim.stock_item` | 2555 days | 2555 days | SCD-2 history must be co-retained with fact |
| `dim.date` | 2555 days | 2555 days | Stable reference data; retained for audit traceability |
| `stg.etl_cutoff` | 2555 days | 2555 days | Control table; small and persistent |
| `stg.lineage` | 2555 days | 2555 days | Audit trail must match fact/dim retention |
| `stg.purchase_staging` | 90 days | 90 days | Transient landing zone |
| `stg.dq_rejections` | 90 days | 90 days | Operational audit log |

---

### 5. Foreign Key Constraints

Delta Lake does not enforce physical foreign key constraints. Relationships are logical and enforced at the ETL layer:
- MERGE / lookup logic ensures every fact row carries valid FK values before the MERGE executes.
- Referential integrity checks are implemented as DQ rules logged to `stg.dq_rejections`.
- No `FOREIGN KEY` clauses appear in any DDL. All FK relationships are documented via `COMMENT` clauses only.

---

### 6. Mart Layer

Objects in `globalpurchase.mart` are defined in the **Serving** section below. They read from `fact.purchase` joined with dimensions and expose business-facing column names for BI consumption. Mart objects do not carry lineage keys, SCD-2 tracking columns, or pipeline control columns.

---

## Ingestion

### 1. Ingestion Strategy Overview

The Purchase product uses a **JDBC incremental ingestion strategy** driven by a persistent watermark. Each pipeline run extracts only the rows modified since the previous successful run.

Ingestion is split into three notebooks executed as sequential tasks within a single Databricks Workflow run:

| Notebook | Role |
|---|---|
| `nb_extract_watermark` | Reads or initialises the watermark; emits `lineage_key` as a task value |
| `nb_extract_dimensions` | Extracts dimension tables from the source into in-memory Spark temp views |
| `nb_extract_purchase` | Extracts the purchase fact dataset into `globalpurchase.stg.purchase_staging` via truncate+overwrite |

---

### 2. Watermark Lifecycle

```
1. READ    nb_extract_watermark reads last_cutoff_time from globalpurchase.stg.etl_cutoff
            (entity_name = 'purchase')
           If no row exists → use HISTORY_ANCHOR_DATE (first-run fallback)
2. FILTER  nb_extract_purchase issues a JDBC query: WHERE LastEditedWhen > <last_cutoff_time>
3. STAGE   Extracted rows are written to stg.purchase_staging (truncate+overwrite)
4. COMMIT  After all downstream loads succeed, nb_commit_watermark updates etl_cutoff.last_cutoff_time
5. ROLLBACK If any downstream task fails, etl_cutoff is NOT updated; next run re-reads same window
```

```python
# nb_extract_watermark.py — watermark read pattern
from pyspark.sql import functions as F

ENTITY = "purchase"
ANCHOR_DATE = spark.conf.get("spark.globalpurchase.history_anchor_date")

cutoff_df = spark.table("globalpurchase.stg.etl_cutoff").filter(
    F.col("entity_name") == ENTITY
)

if cutoff_df.count() == 0:
    last_cutoff = ANCHOR_DATE
    spark.sql(f"""
        INSERT INTO globalpurchase.stg.etl_cutoff (entity_name, last_cutoff_time)
        VALUES ('{ENTITY}', CAST('{ANCHOR_DATE}' AS TIMESTAMP))
    """)
else:
    last_cutoff = cutoff_df.collect()[0]["last_cutoff_time"]

dbutils.jobs.taskValues.set(key="last_cutoff",  value=str(last_cutoff))
dbutils.jobs.taskValues.set(key="lineage_key",  value=lineage_key)
```

---

### 3. Dimension Extraction Pattern — In-Memory Temp Views

Dimension tables are extracted from the source via JDBC and materialised as **Spark temporary views** within the current Spark session. They are never written to persistent storage during the ingestion phase — consumed directly by SCD-2 MERGE notebooks in the same Workflow run.

```python
# nb_extract_dimensions.py
scope = dbutils.widgets.get("env_scope")
jdbc_url      = dbutils.secrets.get(scope=scope, key="jdbc_url")
jdbc_username = dbutils.secrets.get(scope=scope, key="jdbc_username")
jdbc_password = dbutils.secrets.get(scope=scope, key="jdbc_password")

jdbc_options = {"url": jdbc_url, "user": jdbc_username, "password": jdbc_password}

supplier_df = spark.read.format("jdbc").options(**jdbc_options).option("dbtable", "Purchasing.Suppliers").load()
supplier_df.createOrReplaceTempView("src_suppliers")

stock_item_df = spark.read.format("jdbc").options(**jdbc_options).option("dbtable", "Warehouse.StockItems").load()
stock_item_df.createOrReplaceTempView("src_stock_items")
```

The JDBC driver class is externalised as a cluster-level Spark configuration key and is never hardcoded in notebooks.

---

### 4. Fact Extraction Pattern — Truncate+Overwrite

```python
# nb_extract_purchase.py
scope       = dbutils.widgets.get("env_scope")
last_cutoff = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="last_cutoff")
lineage_key = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")

jdbc_url      = dbutils.secrets.get(scope=scope, key="jdbc_url")
jdbc_username = dbutils.secrets.get(scope=scope, key="jdbc_username")
jdbc_password = dbutils.secrets.get(scope=scope, key="jdbc_password")

source_query = f"""
    (SELECT po.PurchaseOrderID, po.SupplierID, pol.StockItemID,
            pol.OrderedOuters, pol.ReceivedOuters, pol.UnitPackageID,
            MAX(po.LastEditedWhen) AS LastEditedWhen
     FROM Purchasing.PurchaseOrders po
     JOIN Purchasing.PurchaseOrderLines pol ON pol.PurchaseOrderID = po.PurchaseOrderID
     WHERE po.LastEditedWhen > CAST('{last_cutoff}' AS DATETIME2)
     GROUP BY po.PurchaseOrderID, po.SupplierID, pol.StockItemID,
              pol.OrderedOuters, pol.ReceivedOuters, pol.UnitPackageID) t
"""

from pyspark.sql import functions as F
from datetime import datetime, timezone

purchase_df = spark.read.format("jdbc").option("url", jdbc_url).option("user", jdbc_username) \
    .option("password", jdbc_password).option("dbtable", source_query).load()

purchase_df = purchase_df \
    .withColumn("lineage_key", F.lit(lineage_key).cast("bigint")) \
    .withColumn("_extracted_at_utc", F.lit(datetime.now(timezone.utc)).cast("timestamp"))

purchase_df.write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "false").saveAsTable("globalpurchase.stg.purchase_staging")
```

---

### 5. Credential Management

All credentials stored in Databricks Secrets. Retrieved at runtime via `dbutils.secrets.get`. No hardcoded values.

| Secret key | Description |
|---|---|
| `jdbc_url` | Full JDBC connection string |
| `jdbc_username` | Service-account username |
| `jdbc_password` | Service-account password |

Scopes: `globalpurchase-dev` (dev/test) and `globalpurchase-prod` (production). Active scope passed via Widget `env_scope`.

---

### 6. HISTORY_ANCHOR_DATE

First-run fallback watermark. Configured as a Workflow parameter or cluster Spark config (`spark.globalpurchase.history_anchor_date`). Never hardcoded. On first run: read anchor → insert etl_cutoff row → proceed. On subsequent runs: read existing etl_cutoff row.

---

### 7. Notebook Responsibilities

| Notebook | Responsibility |
|---|---|
| `nb_extract_watermark.py` | Reads etl_cutoff; falls back to HISTORY_ANCHOR_DATE; opens lineage record; publishes `last_cutoff` and `lineage_key` as task values |
| `nb_extract_dimensions.py` | Reads supplier and stock_item via JDBC; registers as temp views; does not write to persistent storage |
| `nb_extract_purchase.py` | Reads purchase data with watermark filter + duplicate collapse; injects audit columns; truncate+overwrites purchase_staging |

---

### 8. Audit Columns on Staging Rows

| Column | Type | Population |
|---|---|---|
| `lineage_key` | `BIGINT NOT NULL` | Injected from `nb_extract_watermark` task values; constant within a run |
| `_extracted_at_utc` | `TIMESTAMP NOT NULL` | Set to `datetime.now(timezone.utc)` at extract time; constant within a run |

---

### 9. Known Issue Correction — Duplicate Source Rows

The source system can produce multiple rows per `PurchaseOrderID` with different `LastEditedWhen` timestamps. Corrected at extraction time using `MAX(LastEditedWhen) GROUP BY` in the JDBC pushdown query, ensuring at most one row per `PurchaseOrderID` enters staging.

---

## Transformation

### Overview

Three phases, strictly sequenced in the Databricks job:
1. **SCD-2 dimension merge** — `dim.supplier` and `dim.stock_item` updated with incoming changes
2. **Surrogate key resolution** — staging rows pre-joined to dimensions to resolve `supplier_key`, `stock_item_key`, `date_key`
3. **Fact MERGE** — resolved rows merged into `fact.purchase`; conditional OPTIMIZE; lineage close

---

### SCD-2 Dimension Merge Design

#### Two-step expire-then-insert pattern

| Step | Operation | Effect |
|---|---|---|
| 1 — Expire | MERGE on business_key AND is_current_row = TRUE, WHEN MATCHED (changed attrs) | Sets `is_current_row = FALSE`, `row_expiry_date = effective_date - 1` |
| 2 — Insert | MERGE on business_key AND is_current_row = TRUE, WHEN NOT MATCHED BY TARGET | Inserts new row with `is_current_row = TRUE`, `row_effective_date = today`, `row_expiry_date = 9999-12-31` |

Expire runs before insert so Step 2's `NOT MATCHED BY TARGET` guard correctly sees the expired row.

#### Shared helper: `src/etl/dimensions/scd2_merge.py`

```python
def apply_scd2_merge(
    spark: SparkSession,
    target_table: str,
    staging_df: DataFrame,
    business_key: str,
    effective_date: date,
    attribute_columns: list[str],
) -> int:
    """Two-step SCD-2 MERGE. Returns rows affected (expired + inserted)."""
```

#### Step 1 — Expire (Spark SQL)

```sql
MERGE INTO globalpurchase.dim.supplier AS tgt
USING (
    SELECT s.* FROM globalpurchase.stg.supplier s
    JOIN globalpurchase.dim.supplier d
      ON s.supplier_business_key = d.supplier_business_key AND d.is_current_row = TRUE
    WHERE s.supplier_name <> d.supplier_name OR s.payment_days <> d.payment_days
) AS src
ON tgt.supplier_business_key = src.supplier_business_key AND tgt.is_current_row = TRUE
WHEN MATCHED THEN UPDATE SET
    tgt.is_current_row  = FALSE,
    tgt.row_expiry_date = DATEADD(DAY, -1, :effective_date)
```

#### Step 2 — Insert new active version

```sql
MERGE INTO globalpurchase.dim.supplier AS tgt
USING (
    SELECT s.* FROM globalpurchase.stg.supplier s
    LEFT JOIN globalpurchase.dim.supplier d
      ON s.supplier_business_key = d.supplier_business_key AND d.is_current_row = TRUE
    WHERE d.supplier_key IS NULL
) AS src
ON tgt.supplier_business_key = src.supplier_business_key AND tgt.is_current_row = TRUE
WHEN NOT MATCHED BY TARGET THEN INSERT (
    supplier_business_key, supplier_name, payment_days,
    is_current_row, row_effective_date, row_expiry_date
) VALUES (
    src.supplier_business_key, src.supplier_name, src.payment_days,
    TRUE, :effective_date, DATE '9999-12-31'
)
```

Same pattern applied to `dim.stock_item`.

#### Sentinel row requirement

Both dimension tables must contain a `key = 0` Unknown sentinel row before any fact load. Created once during bootstrap; never touched by incremental loads.

---

### Surrogate Key Resolution Design

#### `src/etl/facts/sk_resolver.py`

```python
def resolve_surrogate_keys(
    spark: SparkSession,
    staging_df: DataFrame,
    load_date: date,
) -> DataFrame:
    """Left-joins staging to each dimension on business key + is_current_row = TRUE.
    Returns DataFrame with supplier_key, stock_item_key, date_key added.
    Unresolved → COALESCE(..., 0) sentinel fallback."""
```

```python
from pyspark.sql import functions as F

supplier_dim = spark.table("globalpurchase.dim.supplier").filter("is_current_row = TRUE")
resolved = staging_df.join(
    supplier_dim.select("supplier_business_key", "supplier_key"), on="supplier_business_key", how="left"
).withColumn("supplier_key", F.coalesce(F.col("supplier_key"), F.lit(0)))

stock_item_dim = spark.table("globalpurchase.dim.stock_item").filter("is_current_row = TRUE")
resolved = resolved.join(
    stock_item_dim.select("stock_item_business_key", "stock_item_key"), on="stock_item_business_key", how="left"
).withColumn("stock_item_key", F.coalesce(F.col("stock_item_key"), F.lit(0)))

# date_key: direct YYYYMMDD cast — no join required
resolved = resolved.withColumn("date_key", F.date_format(F.col("order_date"), "yyyyMMdd").cast("int"))
```

---

### Fact MERGE Design

```sql
MERGE INTO globalpurchase.fact.purchase AS tgt
USING (
    SELECT wwi_purchase_order_id, supplier_key, stock_item_key, date_key,
           ordered_quantity, received_outers, is_order_finalized, order_date
    FROM globalpurchase.stg.purchase_resolved
) AS src
ON tgt.wwi_purchase_order_id = src.wwi_purchase_order_id
WHEN MATCHED THEN UPDATE SET
    tgt.supplier_key = src.supplier_key, tgt.stock_item_key = src.stock_item_key,
    tgt.date_key = src.date_key, tgt.ordered_quantity = src.ordered_quantity,
    tgt.received_outers = src.received_outers, tgt.is_order_finalized = src.is_order_finalized
WHEN NOT MATCHED BY TARGET THEN INSERT (
    wwi_purchase_order_id, supplier_key, stock_item_key, date_key,
    ordered_quantity, received_outers, is_order_finalized, order_date
) VALUES (
    src.wwi_purchase_order_id, src.supplier_key, src.stock_item_key, src.date_key,
    src.ordered_quantity, src.received_outers, src.is_order_finalized, src.order_date
)
```

Shared helper: `src/etl/facts/fact_merge.py` → `apply_fact_merge()` returns `rows_merged` from Delta operation metrics.

---

### Conditional OPTIMIZE

```python
if rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD:
    spark.sql(f"OPTIMIZE {TBL_FACT_PURCHASE} ZORDER BY (date_key, supplier_key)")
```

`FACT_OPTIMIZE_ROW_THRESHOLD` defined in `constants.py`. Z-order on `date_key, supplier_key` aligns with analytical query patterns.

---

### Lineage Close

```python
spark.sql(f"""
    UPDATE {TBL_LINEAGE}
    SET rows_loaded = {rows_merged}, load_end_ts = CURRENT_TIMESTAMP(), status = 'COMPLETED'
    WHERE lineage_key = {lineage_key}
""")
```

If the notebook raises before reaching this step, `status` remains `RUNNING` — detected by pipeline monitoring.

---

### Module Layout

| Module | Location | Responsibility |
|---|---|---|
| `scd2_merge.py` | `src/etl/dimensions/` | Two-step SCD-2 MERGE; parameterized; reusable across products |
| `sk_resolver.py` | `src/etl/facts/` | Dimension key pre-join; COALESCE fallback to sentinel 0 |
| `fact_merge.py` | `src/etl/facts/` | Standard Delta MERGE; returns `rows_merged` |
| `constants.py` | `src/common/` | Table name strings and numeric thresholds |
| `utils.py` | `src/common/` | Shared `log_info` / `log_error` helpers |

---

## Serving

### 1. Mart Layer Strategy

All mart objects reside in `globalpurchase.mart`. Two types:

| Object type | When used |
|---|---|
| `CREATE OR REPLACE MATERIALIZED VIEW` | Aggregating/reporting views with high query-time join cost |
| `CREATE OR REPLACE VIEW` | Thin wrappers with no aggregation |

No query hints applied; Delta snapshot isolation handles read consistency.

---

### 2. View Naming Conventions

- **Prefix:** `v_` on every view and materialized view
- **Case:** `snake_case`
- **Language:** Target-system terms only

| BI Consumer | Mart object |
|---|---|
| Purchase and sale per stock item (dynamic) | `globalpurchase.mart.v_purchase_per_stock_item` |
| Ordered by supplier | `globalpurchase.mart.v_purchase_by_supplier` |

---

### 3. Example Mart View DDL

```sql
-- src/db/ddl/v_purchase_by_supplier.sql
CREATE OR REPLACE MATERIALIZED VIEW globalpurchase.mart.v_purchase_by_supplier
COMMENT 'Purchase summary per stock item and supplier for BI consumers'
AS
SELECT
    fp.purchase_date,
    ds.supplier_key, ds.supplier_name, ds.supplier_category, ds.delivery_country_name,
    dsi.stock_item_key, dsi.stock_item_name, dsi.color, dsi.unit_package_name,
    SUM(fp.ordered_quantity)        AS total_quantity_ordered,
    COUNT(DISTINCT fp.purchase_key) AS purchase_order_count
FROM globalpurchase.fact.purchase        AS fp
INNER JOIN globalpurchase.dim.supplier   AS ds  ON fp.supplier_key   = ds.supplier_key
INNER JOIN globalpurchase.dim.stock_item AS dsi ON fp.stock_item_key = dsi.stock_item_key
GROUP BY
    fp.purchase_date,
    ds.supplier_key, ds.supplier_name, ds.supplier_category, ds.delivery_country_name,
    dsi.stock_item_key, dsi.stock_item_name, dsi.color, dsi.unit_package_name;
```

```sql
-- src/db/ddl/v_purchase_per_stock_item.sql
CREATE OR REPLACE VIEW globalpurchase.mart.v_purchase_per_stock_item
COMMENT 'Per-stock-item purchase detail for dynamic BI reporting'
AS
SELECT
    fp.purchase_key, fp.date_key, fp.supplier_key, fp.stock_item_key,
    fp.ordered_outers, fp.ordered_quantity, fp.received_outers,
    fp.package, fp.is_order_finalized,
    dsi.stock_item_name, dsi.color, dsi.unit_package_name,
    ds.supplier_name
FROM globalpurchase.fact.purchase        AS fp
INNER JOIN globalpurchase.dim.stock_item AS dsi ON fp.stock_item_key = dsi.stock_item_key
INNER JOIN globalpurchase.dim.supplier   AS ds  ON fp.supplier_key   = ds.supplier_key;
```

---

### 4. Access Control Design

```sql
-- src/db/grants/stg_grants.sql
GRANT USE SCHEMA ON SCHEMA globalpurchase.stg TO `etl-service-principal`;
GRANT SELECT, MODIFY ON ALL TABLES IN SCHEMA globalpurchase.stg TO `etl-service-principal`;

-- src/db/grants/dim_supplier_grants.sql
GRANT USE SCHEMA ON SCHEMA globalpurchase.dim TO `etl-service-principal`, `bi-service-principal`;
GRANT SELECT, MODIFY ON TABLE globalpurchase.dim.supplier TO `etl-service-principal`;
GRANT SELECT ON TABLE globalpurchase.dim.supplier TO `bi-service-principal`;
-- Repeat for dim.stock_item (dim_stock_item_grants.sql)

-- src/db/grants/fact_rls_policies.sql
GRANT USE SCHEMA ON SCHEMA globalpurchase.fact TO `etl-service-principal`, `bi-service-principal`;
GRANT SELECT, MODIFY ON TABLE globalpurchase.fact.purchase TO `etl-service-principal`;
GRANT SELECT ON TABLE globalpurchase.fact.purchase TO `bi-service-principal`;

-- src/db/grants/mart_grants.sql
GRANT USE SCHEMA ON SCHEMA globalpurchase.mart TO `etl-service-principal`, `bi-service-principal`, `purchase-analysts`;
GRANT SELECT ON ALL VIEWS IN SCHEMA globalpurchase.mart TO `bi-service-principal`, `purchase-analysts`;
GRANT SELECT, REFRESH ON MATERIALIZED VIEW globalpurchase.mart.v_purchase_by_supplier TO `etl-service-principal`;
```

---

### 5. Notebook Responsibilities

| Notebook | Responsibility |
|---|---|
| `nb_refresh_v_purchase_by_supplier.py` | `REFRESH MATERIALIZED VIEW` for v_purchase_by_supplier |
| `nb_optimize_mart.py` | `OPTIMIZE` + `VACUUM` on mart-layer Delta tables |
| `nb_validate_mart_views.py` | Row-count and null-key assertions against mart views; compares to fact layer |

---

### 6. DAG Position

```
[stg ingestion]
      |
[dim loads: supplier, stock_item]
      |
[fact load: fact.purchase]
      |
[DQ assertions: nb_dq_purchase]
      |
[mart refresh: nb_refresh_v_*]
      |
[mart optimize: nb_optimize_mart]
      |
[mart validate + watermark commit]  ← pipeline terminal node
```

---

### 7. BI Reconnection

After migration, BI tools must update connection strings to Unity Catalog endpoints. See `docs/bi_connections.md`.

| BI consumer | Target mart view |
|---|---|
| Purchase and sale per stock item (dynamic) | `globalpurchase.mart.v_purchase_per_stock_item` |
| Ordered by supplier | `globalpurchase.mart.v_purchase_by_supplier` |

---

## Observability

### 1. Lineage Tracking Design

`stg.lineage` is the central lineage registry. Every pipeline run creates one lineage record; its `lineage_key` propagates to every downstream table.

#### lineage_key Flow

```
nb_extract_watermark  → inserts stg.lineage (status='RUNNING') → publishes lineage_key via task values
nb_extract_purchase   → stamps every row in stg.purchase_staging with lineage_key
nb_load_fact          → carries lineage_key into fact.purchase; UPDATEs stg.lineage.rows_loaded after MERGE
nb_dq_purchase        → reads lineage_key; writes to stg.dq_rejections with lineage_key
nb_commit_watermark   → closes stg.lineage (status='SUCCESS', completed_at)
```

If the pipeline fails before `nb_commit_watermark`, `status` remains `RUNNING` — a monitoring indicator of failure.

---

### 2. DQ Observability

DQ evaluation runs after fact merge, before mart promotion. `dq_engine.py` evaluates each configured rule and writes one row to `stg.dq_rejections` per violation. `ERROR`-severity rejections halt mart promotion; `WARNING`-severity are logged and mart proceeds.

After evaluation, `nb_dq_rejection_report.py` aggregates results by `lineage_key` and logs a per-run summary.

---

### 3. Watermark Observability

`stg.etl_cutoff` row for `entity_name = 'purchase'` with `last_cutoff_time` matching the expected run boundary is a reliable indicator of a clean end-to-end run. `nb_commit_watermark.py` advances this row as the final write in the pipeline.

---

### 4. Alert Design

Failures trigger Databricks Workflow alerts (email + webhook) within 15 minutes. Configuration in `config/monitoring_config.yml`:
- Recipient email addresses and webhook URLs
- Alert window (15-minute SLA)
- Severity level that triggers an alert
- Suppression windows for planned maintenance

---

### 5. Row Count Metrics

Consistent `log_info` pattern per notebook:

```python
log_info(f"Load complete: {rows_merged} rows merged (lineage_key={lineage_key})")
```

Cross-run volume query from `stg.lineage`:

```sql
SELECT pipeline_run_id, entity_name, started_at, completed_at, status,
       source_row_count, rows_loaded, rows_loaded - source_row_count AS delta
FROM stg.lineage
WHERE entity_name = 'purchase'
ORDER BY started_at DESC;
```

---

### 6. End-to-End Traceability Example

```sql
-- Step 1: Identify mart row and lineage_key
SELECT purchase_key, lineage_key FROM globalpurchase.mart.v_purchase_by_supplier LIMIT 1;

-- Step 2: Pipeline run metadata
SELECT * FROM globalpurchase.stg.lineage WHERE lineage_key = <key>;

-- Step 3: DQ status for that run
SELECT * FROM globalpurchase.stg.dq_rejections WHERE lineage_key = <key>;

-- Step 4: Source staging record
SELECT * FROM globalpurchase.stg.purchase_staging WHERE lineage_key = <key>;
```

---

### 7. Notebook Responsibilities

| Notebook | Observability role |
|---|---|
| `nb_extract_watermark` | Opens stg.lineage record; publishes lineage_key |
| `nb_load_fact` | Updates stg.lineage.rows_loaded after MERGE |
| `nb_dq_purchase` | Orchestrates DQ; calls dq_engine; triggers rejection report |
| `dq_engine.py` | Evaluates rules; writes stg.dq_rejections rows |
| `nb_dq_rejection_report.py` | Aggregates rejections; logs per-run summary |
| `nb_dq_smoke_tests.py` | Fast-fail checks before DQ; does not write to dq_rejections |
| `nb_commit_watermark` | Advances etl_cutoff; closes lineage record |

---

*Generated by migVisor SmartBuilder · 2026-08-25*
