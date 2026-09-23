# Purchase — Product Brief


## Naming

Object names follow `lowercase_snake_case` throughout. A few illustrative patterns:

- `SalespersonKey` → `salesperson_key` (PascalCase → snake_case)
- `WWIInvoiceID` → `wwi_invoice_id` (acronyms lowercased, underscores inserted)
- `Dimension.Stock Item` → `dim.stock_item` (space → underscore, schema mapped)
- `getTotalQuantitySold1` → `get_total_quantity_sold` (camelCase procedure → Python function)

All generated SQL files use backtick-free identifiers. Bracket quoting (`[Column Name]`) is removed; column names are renamed to snake_case at DDL generation time. Views carry a `v_` prefix. Staging tables carry a `_staging` suffix (exception: control tables such as `etl_cutoff` do not).

---

## Column Type Rules

Only types that require a non-trivial mapping are listed. Identity mappings (e.g. `INT` → `INT`, `DATE` → `DATE`) apply without change.

| Source type | Target type | Notes |
|---|---|---|
| `NVARCHAR(n)`, `VARCHAR(n)`, `NVARCHAR(MAX)` | `STRING` | Collation dropped; Spark defaults to UTF-8 |
| `DATETIME`, `DATETIME2`, `SMALLDATETIME` | `TIMESTAMP` | Operational timestamps (e.g. `last_edited_when`); SCD-2 validity columns use `DATE` — see below |
| `BIT` | `BOOLEAN` | e.g. `Is Order Finalized`, `Is Chiller Stock` |
| `MONEY`, `SMALLMONEY` | `DECIMAL(18,2)`, `DECIMAL(10,2)` | Never use `FLOAT` for monetary values |
| `DECIMAL(p,s)` / `NUMERIC(p,s)` | `DECIMAL(p,s)` | Preserve precision and scale exactly |
| `VARBINARY` | `BINARY` | e.g. `Photo` columns on dimension tables |
| `BIGINT IDENTITY` (fact PKs) | `BIGINT GENERATED ALWAYS AS IDENTITY` | Fact surrogate keys; sequence objects retired |
| `INT IDENTITY` (dim PKs) | `INT GENERATED ALWAYS AS IDENTITY` | Dimension surrogate keys |
| `geography` | Three columns: `location_wkt STRING`, `location_lat DOUBLE`, `location_lon DOUBLE` | SQL Server CLR spatial type has no Spark equivalent; extract via `STAsText()`, `.Lat`, `.Long` at source |

SCD-2 control columns:
- `Valid From datetime2` → `valid_from DATE NOT NULL` (business effective date)
- `Valid To datetime2` → `valid_to DATE NOT NULL` (business expiry date)
- `row_effective_date DATE NOT NULL` — technical SCD-2 row open date
- `row_expiry_date DATE NOT NULL DEFAULT DATE '9999-12-31'` — technical SCD-2 row close date
- `is_current_row BOOLEAN NOT NULL DEFAULT TRUE` — active-row flag; set to `FALSE` on the expire step

---

## Calculation and Business Logic Rules

### Derived financial columns

If the source procedure computes financial aggregates (e.g. `total_excluding_tax = quantity * unit_price`, `tax_amount = total_excluding_tax * tax_rate / 100`, `total_including_tax = total_excluding_tax + tax_amount`) and stores them in the fact table, preserve this pattern in the target: compute in the ETL notebook and store as explicit columns. Do not re-derive at query time. Example in Python ETL:

```python
enriched = (
    staging_df
    .withColumn("total_excluding_tax", col("quantity") * col("unit_price"))
    .withColumn("tax_amount", col("total_excluding_tax") * (col("tax_rate") / 100.0))
    .withColumn("total_including_tax", col("total_excluding_tax") + col("tax_amount"))
)
```

### Hard-coded date filters

Analytics views may contain hard-coded date predicates (e.g. `WHERE order_date > '20230101'` or rolling windows like `GETDATE()-100`). Replace with named parameters stored in `config/environment.yaml` so the window can be changed without a code deployment. Example:

```python
# config/environment.yaml
date_filters:
  baseline_date: "20230101"      # preserves source literal; confirm with stakeholders
  rolling_window_days: 100       # preserves GETDATE()-100 behavior
```

Always add a stakeholder confirmation item when the business meaning of a hard-coded date is unclear.

### Hard-coded business factors

If a view applies an unexplained multiplier (e.g. `* 1.05` in a profit calculation), externalise it as a named constant in `config/environment.yaml`, wrap the calculation with a NULL guard (`CASE WHEN denominator = 0 THEN NULL ELSE ... END`), and add a DQ bound assertion. Record a stakeholder confirmation requirement before go-live.

### Duplicate functions

If the source contains two functionally identical scalar functions with different parameter names (e.g. `getTotalQuantitySold1(@StockItemKey)` and `getTotalQuantitySold2(@ItemKey)`), consolidate them into a single target UDF. Add a NULL guard (`COALESCE(SUM(...), 0)`) if the source lacks one. Register both source names in the migration object registry as `CONSOLIDATED → <target_name>`.

---

## Object Patterns

### SCD-2 dimension tables

Source pattern: `Valid From` / `Valid To` range + sequence-generated surrogate key. Target pattern:
- Surrogate key: `INT GENERATED ALWAYS AS IDENTITY`; sequence object retired
- Columns: `valid_from DATE`, `valid_to DATE` (business dates); `row_effective_date DATE`, `row_expiry_date DATE DEFAULT DATE '9999-12-31'`, `is_current_row BOOLEAN DEFAULT TRUE` (technical SCD-2 control)
- Loading: two-step Delta MERGE — Step 1 expires the current row (`is_current_row = FALSE`, `row_expiry_date = effective_date - 1`); Step 2 inserts the new active version. Logic lives in shared `scd2_merge.py` used by all dimension notebooks

A `key=0` "Unknown" sentinel row must be present in every SCD-2 dimension before any fact load. Create a one-time bootstrap notebook that inserts it.

### Static calendar table

No SCD-2 columns, no `lineage_key`. Primary key is `date_key INT` in `YYYYMMDD` integer format — not a DATE column. Migrate as a pre-loaded reference table. The source populates it via a day-loop procedure; replace with `nb_populate_dim_date.py` that inserts the full year range once. No daily reload.

### Staging tables

Transient `stg` Delta tables. Truncate and reload on every ETL run. Add two audit columns to every staging table:

```sql
lineage_key        BIGINT    NOT NULL,   -- FK to stg.lineage; identifies the pipeline run
_extracted_at_utc  TIMESTAMP NOT NULL    -- UTC timestamp when the row was extracted from source
```

No `OPTIMIZE`, no partitioning, short Delta log retention.

### Analytics views

SQL Server views with T-SQL syntax become Databricks mart objects. Aggregating/reporting views become **materialized views** (`CREATE OR REPLACE MATERIALIZED VIEW`); thin wrapper/alias views become regular SQL views (`CREATE OR REPLACE VIEW`). Remove `WITH (NOLOCK)` hints — Delta snapshot isolation makes them unnecessary. When a view references out-of-scope tables, stub it with a `TODO` comment and document the dependency.

### Scalar UDFs

Map to Databricks SQL UDFs registered in Unity Catalog, or to Python functions in a shared module. Always add NULL guards (`COALESCE` or `CASE WHEN`) if the source function lacks them.

---

## Syntax Transformations

| Source T-SQL | Target |
|---|---|
| `SET NOCOUNT ON`, `SET XACT_ABORT ON` | Remove — no Databricks equivalent |
| `BEGIN TRAN / COMMIT / ROLLBACK` | Remove — Delta MERGE is per-statement atomic; multi-table logic uses sequential idempotent writes with checkpoint |
| `WITH EXECUTE AS OWNER` | Remove — replaced by Databricks service principal |
| `NEXT VALUE FOR [Sequences].[...]` | Remove — IDENTITY column generates the key |
| `TOP(1)` in correlated subquery | `LIMIT 1` with `ORDER BY valid_from DESC` |
| `UPDATE staging SET key = (SELECT TOP(1) key FROM dim WHERE biz_key = ... AND valid_from <= ... AND valid_to > ...)` | Pre-join step before MERGE: `JOIN dim ON biz_key AND date BETWEEN valid_from AND valid_to` — handled by `sk_resolver.py` |
| `DELETE fact WHERE biz_key IN (SELECT ... FROM staging)` | `MERGE INTO fact ON (biz_key) WHEN MATCHED THEN DELETE` or full `MERGE` |
| `GETDATE()`, `SYSDATETIME()` | `current_timestamp()` |
| `ISNULL(x, y)` | `ifnull(x, y)` or `coalesce(x, y)` |
| `COALESCE(subquery, 0)` — Unknown member fallback | Preserve as `COALESCE(resolved_key, 0)` in Spark SQL |
| `WITH (NOLOCK)` table hints | Remove; flag any referenced out-of-scope tables for scope review |
| `CONVERT(CHAR(8), GETDATE()-N, 112)` — rolling date filter | `DATE_FORMAT(DATE_SUB(current_date(), N), 'yyyyMMdd')` |
| `[Bracket Quoted Identifier]` | Renamed to `snake_case_identifier` — no quoting needed |
| `EXEC Integration.GetLineageKey` | `lineage_key` injected from upstream task via `dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")` |
| `UPDATE Integration.Lineage SET [Data Load Completed] = ...` | `spark.sql(f"UPDATE {TBL_LINEAGE} SET rows_loaded = {rows_merged} WHERE lineage_key = {lineage_key}")` — inline after merge |

---

## Performance

Choosing between liquid clustering and partition + Z-ORDER depends on the source indexing pattern:

| Source has | Target strategy | Rationale |
|---|---|---|
| Clustered Columnstore Index (CCI) | `CLUSTER BY (date_col, fk_col_1, fk_col_2)` — liquid clustering | CCI is evidence of multi-dimensional columnar access; liquid clustering is the idiomatic replacement |
| Row-store B-tree on date column | `PARTITIONED BY (date_col)` + `ZORDER BY (fk_col_1, fk_col_2)` | Date-range partition elimination + Z-ORDER for secondary keys |

Dimension tables: no explicit `CLUSTER BY` — small tables where Delta default file layout is sufficient.

Run `OPTIMIZE` on fact tables conditionally in-notebook after merge, only when `rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD` (defined in `constants.py`). Mart views have a dedicated `nb_optimize_mart.py` task. Staging tables: no optimization.

---

## Data Quality

Assertions run after dimension/fact load, before mart promotion. Failures write to `stg.dq_rejections`:

- **Row count reconciliation** — staging count must equal the net delta in the fact table for the batch. Zero tolerance; pipeline alert on mismatch.
- **Dimension key integrity** — orphaned FK keys (key=0 or NULL where not expected) are flagged for review; do not block load.
- **Referential integrity** — all non-null FK columns in the fact must resolve in their respective dimension. Use `LEFT ANTI JOIN` per FK column.
- **Business rule assertions** — product-specific (e.g. `quantity >= received_outers`); informational only, do not block load.

DQ outcomes are traceable via `lineage_key` — the `stg.lineage` row is updated with row counts by the fact load notebook; DQ rejections written to `stg.dq_rejections` reference the same `lineage_key`.

---

## Output Structure

The codebase follows this layout. Folders map directly to Databricks Workflow task groups.

```
codebase/
│
├── config/                          # Infrastructure and operational config
│   ├── cluster_config.yml           # DBR version, node type, autoscaling
│   ├── workflow_nightly_etl_main.yml # Databricks Workflow definition (replaces SSIS)
│   ├── uc_setup.sql                 # Unity Catalog bootstrap: catalog, schemas, grants
│   ├── uc_permission_audit.sql      # Permission audit queries
│   ├── dq_assertions_<fact>.yaml    # DQ assertion definitions per fact table
│   ├── secrets_config.py            # Secret scope references only; no plain-text values
│   ├── secrets_setup.md             # How to populate the Databricks secret scope
│   ├── secrets_rotation_runbook.md  # Secret rotation procedure
│   ├── deploy_workflow.sh           # CI/CD deployment helper script
│   ├── ci_cd_pipeline.yml
│   ├── monitoring_config.yml
│   ├── pytest.ini                   # Test runner configuration
│   └── bi_connections.md            # BI tool reconnection checklist
│
├── docs/
│   ├── architecture_diagram.md      # Layer diagram: Staging → Dim/Fact → Mart
│   ├── data_dictionary.md           # Column descriptions for all target tables
│   ├── pipeline_runbook.md          # How to run, monitor, and recover the pipeline
│   └── go_live_checklist.md         # Pre-production gate: DQ sign-off, BI reconnection
│
├── src/
│   ├── common/
│   │   ├── constants.py             # Table name constants, thresholds, batch ID format
│   │   └── utils.py                 # Shared helpers: log_info, retry wrapper, row count assertion
│   │
│   ├── db/
│   │   ├── ddl/                     # CREATE TABLE / CREATE VIEW — one file per object
│   │   │   ├── dim_<name>.sql
│   │   │   ├── dim_date_populate.sql    # Date dimension bootstrap population
│   │   │   ├── fact_<name>.sql
│   │   │   ├── fact_udf_<name>.sql      # UDFs registered in the fact schema
│   │   │   ├── stg_<staging_table>.sql
│   │   │   ├── stg_etl_cutoff.sql
│   │   │   ├── stg_lineage.sql
│   │   │   └── stg_dq_rejections.sql
│   │   ├── grants/                  # Unity Catalog access control, separate from DDL
│   │   │   ├── dim_<name>_grants.sql
│   │   │   ├── fact_rls_policies.sql
│   │   │   └── mart_grants.sql
│   │   └── queries/                 # BI sample queries and smoke tests
│   │       └── bi_sample_queries.sql
│   │
│   └── etl/
│       ├── ingestion/               # Staging: extract from source to stg.*
│       │   ├── nb_extract_<entity>.py   # One notebook per fact entity
│       │   ├── nb_extract_dimensions.py # Extracts all dimensions to temp views
│       │   ├── nb_extract_watermark.py
│       │   └── nb_commit_watermark.py
│       │
│       ├── dimensions/              # Dimensions: SCD-2 and static loads
│       │   ├── nb_load_dim_<name>.py    # One notebook per SCD-2 dimension
│       │   ├── nb_populate_dim_date.py  # Static date calendar bootstrap
│       │   ├── nb_orchestrate_dimensions.py  # Runs dimensions in dependency order
│       │   └── scd2_merge.py        # Shared two-step SCD-2 MERGE helper
│       │
│       ├── facts/                   # Facts: fact table load
│       │   ├── nb_load_fact_<name>.py
│       │   ├── nb_orchestrate_facts.py
│       │   ├── sk_resolver.py       # Surrogate key pre-join (runs before MERGE)
│       │   └── fact_merge.py        # Shared MERGE pattern for fact tables
│       │
│       ├── mart/                    # Mart: view refresh and optimization
│       │   ├── nb_refresh_v_<name>.py   # One notebook per mart view
│       │   ├── nb_optimize_mart.py
│       │   └── nb_validate_mart_views.py
│       │
│       ├── dq/                      # Quality gate between facts and mart
│       │   ├── dq_engine.py         # Runs assertions, writes to stg.dq_rejections
│       │   ├── nb_dq_<fact>.py      # Product-specific assertions per fact table
│       │   ├── nb_dq_rejection_report.py  # Rejection summary report
│       │   └── nb_dq_smoke_tests.py     # End-to-end smoke assertions
│       │
│       └── security/
│           └── nb_pii_compliance_check.py
```

### SQL file conventions

Each DDL file has a standard header block:

```sql
-- =============================================================================
-- <filename>.sql
-- Catalog : <catalog>
-- Schema  : <schema>
-- Table   : <table>
-- Purpose : One-line description. Note key design decisions (clustering, CDF,
--           retention).
-- =============================================================================

CREATE TABLE IF NOT EXISTS <catalog>.<schema>.<table> (

    -- Surrogate key
    <name>_key    BIGINT  GENERATED ALWAYS AS IDENTITY  NOT NULL,

    -- Dimension foreign keys
    ...

    -- Lineage
    lineage_key   BIGINT  NOT NULL,  -- references stg.lineage

    -- Measures / attributes
    ...

    CONSTRAINT pk_<schema>_<table> PRIMARY KEY (<name>_key)
)
USING DELTA
CLUSTER BY (...)  -- facts: (date_key, fk1, fk2); dims: (surrogate_key); staging: omit
TBLPROPERTIES (
    'delta.enableChangeDataFeed'         = 'true',   -- false for fact tables
    'delta.deletedFileRetentionDuration' = 'interval 2555 days',  -- 90 days for stg
    'delta.logRetentionDuration'         = 'interval 2555 days'   -- fact/dim only
);
```

Constraints: `pk_<schema>_<table>` for primary keys, `uq_<table>_<col>` for unique constraints. FK constraints are not emitted — documented as lineage.

### Python notebook conventions

Each ETL notebook follows this structure:

```python
# Databricks notebook — TASK-<LAYER>-<N>: <description>

import sys
sys.path.insert(0, "/Workspace/<product>")

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from src.common.constants import TBL_FACT_X, TBL_STAGING, TBL_LINEAGE, FACT_OPTIMIZE_ROW_THRESHOLD
from src.common.utils import log_info
from src.etl.facts.sk_resolver import resolve_surrogate_keys  # fact notebooks only
from src.etl.facts.fact_merge import apply_fact_merge          # fact notebooks only

if __name__ == "__main__":
    spark = SparkSession.getActiveSession()

    # lineage_key injected by upstream watermark task
    try:
        lineage_key = int(dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key"))
    except Exception:
        raise RuntimeError("lineage_key not available from nb_extract_watermark task values")

    staging_df = spark.table(TBL_STAGING)
    staging_count = staging_df.count()

    if staging_count == 0:
        log_info("No staging rows — skipping merge")
    else:
        # Computed columns stored in fact (not re-derived at query time)
        enriched = staging_df.withColumn("total_excl_tax", col("qty") * col("unit_price"))

        # Surrogate key resolution — explicit join before MERGE (fact notebooks only)
        resolved = resolve_surrogate_keys(spark, enriched)

        rows_merged = apply_fact_merge(
            spark=spark,
            target_table=TBL_FACT_X,
            source_df=resolved,
            natural_key_cols=["biz_key"],
            lineage_key=lineage_key,
        )

        # Conditional OPTIMIZE — only when merge touches significant data
        if rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD:
            spark.sql(f"OPTIMIZE {TBL_FACT_X}")

        # Close lineage record
        spark.sql(f"UPDATE {TBL_LINEAGE} SET rows_loaded = {rows_merged} WHERE lineage_key = {lineage_key}")

        log_info(f"Load complete: {rows_merged} rows merged (lineage_key={lineage_key})")
```

Key points: all table names from `constants.py`; shared merge/SCD-2 logic in helper modules; `lineage_key` always from upstream task value; zero-rows guard skips merge cleanly; `sk_resolver` and `fact_merge` are fact-notebook patterns only — dim notebooks call `apply_scd2_merge` directly.
