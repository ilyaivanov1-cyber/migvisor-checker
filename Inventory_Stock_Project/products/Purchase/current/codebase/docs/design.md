# Purchase ETL — Technical Design

**Project:** Inventory_Stock_Project
**Product:** Purchase
**Layer scope:** Bronze (staging/control) → Silver (dim + fact)
**Last updated:** 2026-09-07

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Workflow Task Sequence](#2-workflow-task-sequence)
3. [SK Resolution Pattern](#3-sk-resolution-pattern)
4. [MERGE INTO Pattern](#4-merge-into-pattern)
5. [QA Assertion Chain](#5-qa-assertion-chain)
6. [Lineage Propagation](#6-lineage-propagation)
7. [Configuration Management](#7-configuration-management)

---

## 1. Architecture Overview

The Purchase ETL pipeline follows the **medallion lakehouse** pattern with three active layers:

```
 ┌─────────────────────────────────────────────────────────────┐
 │  BRONZE                                                     │
 │  ┌──────────────────────────┐  ┌──────────────────────────┐ │
 │  │ purchase_staging         │  │ etl_cutoff               │ │
 │  │ (append-only staging)    │  │ (high-watermark store)   │ │
 │  └──────────────────────────┘  └──────────────────────────┘ │
 │  ┌──────────────────────────┐  ┌──────────────────────────┐ │
 │  │ dq_rejections            │  │ lineage_run              │ │
 │  │ (DQ rejection log)       │  │ (lineage audit log)      │ │
 │  └──────────────────────────┘  └──────────────────────────┘ │
 └─────────────────────────────────────────────────────────────┘
               │                          │
               ▼                          ▼
 ┌─────────────────────────┐  ┌─────────────────────────────┐
 │  SILVER — DIM           │  │  SILVER — FACT              │
 │  silver_dim.supplier    │  │  silver_fact.fact_purchase  │
 │  silver_dim.date        │  │                             │
 └─────────────────────────┘  └─────────────────────────────┘
```

### Layer responsibilities

| Layer | Table(s) | Responsibility |
|---|---|---|
| Bronze staging | `purchase_staging` | Append-only incremental landing zone for raw source rows. No transformations beyond type coercion. Rule: **FR-002**. |
| Bronze control | `etl_cutoff`, `lineage_run`, `dq_rejections` | Pipeline housekeeping: watermark tracking, lineage audit, DQ rejection storage. |
| Silver dim | `silver_dim.supplier`, `silver_dim.date` | SCD-2 managed dimension tables. The SK resolution step reads from these tables. Rule: **DM-001**, **DM-002**. |
| Silver fact | `fact_purchase` | Final consumption-ready fact table. Populated via MERGE INTO after SK resolution and QA assertion chain. Rule: **FR-003**. |

All table and column names follow target-system snake_case conventions as required by rule **NM-001**.

---

## 2. Workflow Task Sequence

The nightly job (`nightly_etl_purchase`) runs three notebook tasks in strict linear dependency order. Each task communicates with the next via Databricks `taskValues`.

```
 ┌────────────────────────────┐
 │  nb_extract_watermark      │  Task 1 — no dependencies
 │                            │
 │  Reads etl_cutoff,         │
 │  publishes:                │
 │    • last_cutoff           │
 │    • current_cutoff        │
 │    • lineage_key (INT)     │
 └────────────┬───────────────┘
              │  taskValues
              ▼
 ┌────────────────────────────┐
 │  nb_extract_purchase       │  Task 2 — depends on Task 1
 │                            │
 │  Reads source using        │
 │  last/current cutoff,      │
 │  appends to purchase_      │
 │  staging.                  │
 │  Passes lineage_key        │
 │  forward via taskValues.   │
 └────────────┬───────────────┘
              │  taskValues
              ▼
 ┌────────────────────────────┐
 │  migrate_staged_purchase_  │  Task 3 — depends on Task 2
 │  data                      │
 │                            │
 │  SK resolution →           │
 │  QA assertions →           │
 │  MERGE INTO fact table →   │
 │  close lineage_run record  │
 └────────────────────────────┘
```

### taskValues contract

| Key | Publisher | Consumer(s) | Type | Rule |
|---|---|---|---|---|
| `lineage_key` | `nb_extract_watermark` | `nb_extract_purchase`, `migrate_staged_purchase_data` | `int` | **NFR-007** |
| `last_cutoff` | `nb_extract_watermark` | `nb_extract_purchase` | `timestamp string` | **FR-002** |
| `current_cutoff` | `nb_extract_watermark` | `nb_extract_purchase`, `migrate_staged_purchase_data` | `timestamp string` | **FR-002** |

---

## 3. SK Resolution Pattern

Before rows can be promoted to `fact_purchase`, each staged row must be enriched with surrogate keys (SKs) from the silver dimension tables. The resolution uses a **temporal range join** to find the dimension version that was current at the time of the source event (`last_modified_when`).

### Temporal range join

```sql
-- supplier_key resolution (same pattern applies to date_key)
SELECT
    stg.wwi_purchase_order_id,
    stg.last_modified_when,
    COALESCE(dim.supplier_key, 0)   AS supplier_key,
    ...
FROM purchase_staging stg
LEFT JOIN (
    SELECT
        supplier_key,
        wwi_supplier_id,
        valid_from,
        valid_to,
        ROW_NUMBER() OVER (
            PARTITION BY wwi_supplier_id
            ORDER BY valid_from DESC          -- tie-breaker: most-recent version wins
        ) AS rn
    FROM silver_dim.supplier
    WHERE stg.last_modified_when  >  CAST(valid_from AS TIMESTAMP)
      AND stg.last_modified_when  <= CAST(valid_to   AS TIMESTAMP)
) dim
    ON  stg.wwi_supplier_id = dim.wwi_supplier_id
    AND dim.rn = 1
```

Rules applied: **CX-P003** (SK derivation from `last_modified_when`), **DM-001** (SCD-2 join condition).

### COALESCE to 0

Any staged row whose source key does not resolve to a dimension record receives a default SK of `0` (the "unknown" dimension member). This prevents fact-load failures while making orphaned rows visible to QA-P002. Rule: **DM-002**.

```sql
COALESCE(dim.supplier_key, 0) AS supplier_key
```

### date_key derivation

`date_key` is derived using the `format_date_key` UDF (see `src/common/udfs.py`) applied to `last_modified_when`. The resulting ISO string is then joined to `silver_dim.date.date_key`. Rule: **CX-P003**.

```sql
format_date_key(stg.last_modified_when) AS date_key
```

---

## 4. MERGE INTO Pattern

The resolved and QA-passed rows are upserted into `silver_fact.fact_purchase` using a single atomic `MERGE INTO` statement keyed on `wwi_purchase_order_id`.

```sql
MERGE INTO inventory_stock.silver_fact.fact_purchase AS target
USING resolved_purchase_cte AS source
ON  target.wwi_purchase_order_id = source.wwi_purchase_order_id
AND target.date_key               = source.date_key
AND target.supplier_key           = source.supplier_key
AND target.stock_item_key         = source.stock_item_key

WHEN MATCHED THEN
    UPDATE SET
        target.date_key             = source.date_key,
        target.supplier_key         = source.supplier_key,
        target.stock_item_key       = source.stock_item_key,
        target.ordered_outers       = source.ordered_outers,
        target.ordered_quantity     = source.ordered_quantity,
        target.received_outers      = source.received_outers,
        target.package              = source.package,
        target.is_order_finalized   = source.is_order_finalized,
        target.lineage_key          = source.lineage_key

WHEN NOT MATCHED THEN
    INSERT (
        date_key, supplier_key, stock_item_key,
        wwi_purchase_order_id, ordered_outers, ordered_quantity,
        received_outers, package, is_order_finalized, lineage_key
    )
    VALUES (
        source.date_key, source.supplier_key, source.stock_item_key,
        source.wwi_purchase_order_id, source.ordered_outers, source.ordered_quantity,
        source.received_outers, source.package, source.is_order_finalized, source.lineage_key
    )
;
```

Rules applied: **FR-003** (upsert pattern), **NM-001** (column naming), **NFR-007** (lineage_key propagated into every merged row).

---

## 5. QA Assertion Chain

Quality gates are executed sequentially inside `migrate_staged_purchase_data` after SK resolution and before the MERGE INTO. Each assertion produces a named result that is logged to `lineage_run` and, where applicable, to `dq_rejections`.

| ID | Name | Type | Behaviour on failure |
|---|---|---|---|
| **QA-P001** | Row count sanity | **Blocking** | Raises exception; pipeline halts before MERGE. Compares the resolved CTE row count against the source extract. A mismatch indicates a data-loss or duplication event during resolution. |
| **QA-P002** | Orphaned SK check | **Warning** | Logs count of rows where any SK equals `0` (unresolved dimension). Does not block MERGE; rows are loaded with SK=0 so they appear in `dim_unknown`. Triggers an alert if orphan rate exceeds the threshold defined in `environment.yaml`. |
| **QA-P003** | Referential integrity rejections | **Warning** | Identifies rows violating FK constraints (e.g., `stock_item_key` not present in the reference table). Rejected rows are written to `dq_rejections` with `rejection_reason = 'RI_VIOLATION'`. MERGE proceeds on non-rejected rows only. |
| **QA-P004** | Business rule validation | **Warning** | Checks domain-specific rules (e.g., `ordered_quantity >= 0`, `ordered_outers >= 0`, `is_order_finalized IN (true, false)`). Violations are logged to `lineage_run`; rows are not blocked from the MERGE. |
| **QA-P005** | DQ rejection store write | **Blocking** | Persists all accumulated rejections (from QA-P003 and QA-P004 rejections) to `dq_rejections` as an atomic Delta write. Failure here is blocking to ensure auditability. |

```
nb_extract_purchase
      │
      │  taskValues: lineage_key
      ▼
migrate_staged_purchase_data
  ├── SK resolution CTE
  ├── QA-P001  ──── FAIL ──►  pipeline.abort()
  ├── QA-P002  ──── WARN ──►  log to lineage_run (orphan_sk_count)
  ├── QA-P003  ──── WARN ──►  write RI rejections to dq_rejections
  ├── QA-P004  ──── WARN ──►  log violations to lineage_run
  ├── QA-P005  ──── FAIL ──►  pipeline.abort() (rejection write failure)
  └── MERGE INTO fact_purchase
```

---

## 6. Lineage Propagation

End-to-end lineage is tracked via the `lineage_run` table. A single `lineage_key` (IDENTITY integer) is created at the start of each job run and propagated through all three tasks.

### Lifecycle

```
nb_extract_watermark
  └── INSERT INTO bronze.lineage_run
          (run_ts, job_name, task_name, status)
        VALUES (CURRENT_TIMESTAMP(), 'nightly_etl_purchase', 'nb_extract_watermark', 'RUNNING')
      → returns lineage_key (IDENTITY)
  └── dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_key)

nb_extract_purchase
  └── lineage_key = dbutils.jobs.taskValues.get(
            taskKey="nb_extract_watermark", key="lineage_key")
  └── INSERT INTO bronze.lineage_run
          (lineage_key_parent, run_ts, job_name, task_name, status)
        VALUES (lineage_key, CURRENT_TIMESTAMP(), ..., 'RUNNING')
  └── dbutils.jobs.taskValues.set(key="lineage_key", value=child_lineage_key)

migrate_staged_purchase_data
  └── lineage_key = dbutils.jobs.taskValues.get(
            taskKey="nb_extract_purchase", key="lineage_key")
  └── [SK resolution + QA assertions + MERGE]
  └── UPDATE bronze.lineage_run
        SET status = 'SUCCESS', end_ts = CURRENT_TIMESTAMP(),
            rows_inserted = :rows_inserted, rows_updated = :rows_updated
      WHERE lineage_key = :lineage_key
      -- on any exception:
  └── UPDATE bronze.lineage_run
        SET status = 'FAILED', end_ts = CURRENT_TIMESTAMP(),
            error_message = :error_message
      WHERE lineage_key = :lineage_key
```

The `lineage_key` value is also written into every row of `fact_purchase` (column `lineage_key`) so that individual fact rows can be traced back to the specific pipeline run that produced them. Rule: **NFR-007**.

---

## 7. DDL Reference

Complete `CREATE TABLE IF NOT EXISTS` DDL for all Bronze and Silver tables owned by the Purchase product. All tables use `USING DELTA` and Unity Catalog three-part naming.

### bronze.lineage_run

```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_lineage_run.sql
-- PURPOSE  : ETL audit log; one row per run; IDENTITY PK
-- TARGET   : inventory_stock.bronze.lineage_run
-- RULES    : LN-001, LN-002, OB-004, TY-017, NM-001
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.bronze.lineage_run (
    lineage_key               BIGINT     GENERATED ALWAYS AS IDENTITY  NOT NULL
        COMMENT 'Surrogate PK; IDENTITY auto-incremented; propagated to all downstream tables',
    etl_run_id                STRING     NOT NULL
        COMMENT 'UUID string uniquely identifying this pipeline execution',
    table_name                STRING     NOT NULL
        COMMENT 'Name of the target table being loaded (e.g. fact_purchase)',
    pipeline_name             STRING     NOT NULL
        COMMENT 'Name of the Databricks Workflow executing this run',
    data_load_started         TIMESTAMP  NOT NULL
        COMMENT 'UTC timestamp when the pipeline run was initiated',
    data_load_completed       TIMESTAMP  NULL
        COMMENT 'UTC timestamp when run completed; NULL while in progress',
    was_successful            BOOLEAN    NULL
        COMMENT 'NULL while running; TRUE on success; FALSE on failure',
    table_row_count           BIGINT     NULL
        COMMENT 'Row count merged into target fact table; NULL while running',
    source_system_cutoff_time TIMESTAMP  NOT NULL
        COMMENT 'Upper boundary of incremental extract window used for this run',
    CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)
)
USING DELTA
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true'
);
```

### bronze.purchase_staging

```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_purchase_staging.sql
-- PURPOSE  : Bronze landing table; OVERWRITE mode per run
-- TARGET   : inventory_stock.bronze.purchase_staging
-- RULES    : OB-003, OB-P002, TY-017, TY-015, TY-010, LN-001, NM-001
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.bronze.purchase_staging (
    purchase_staging_key  BIGINT     GENERATED ALWAYS AS IDENTITY  NOT NULL
        COMMENT 'Surrogate PK; used as PARTITION BY key in sk_resolver window functions',
    date_key              DATE       NOT NULL
        COMMENT 'Order date derived from source OrderDate; FK to silver_dim.date',
    supplier_key          BIGINT     NULL
        COMMENT 'NULL at extract time; populated by sk_resolver.py before fact MERGE',
    stock_item_key        BIGINT     NULL
        COMMENT 'NULL at extract time; populated by sk_resolver.py before fact MERGE',
    wwi_purchase_order_id INT        NOT NULL
        COMMENT 'Source system natural key; MERGE predicate for fact_purchase',
    ordered_outers        INT        NOT NULL
        COMMENT 'Number of outer packaging units ordered',
    ordered_quantity      INT        NOT NULL
        COMMENT 'Total individual units ordered',
    received_outers       INT        NULL
        COMMENT 'Outer units received; NULL = not yet received',
    package               STRING     NOT NULL
        COMMENT 'Package type name (e.g. Each, Carton)',
    is_order_finalized    BOOLEAN    NOT NULL
        COMMENT 'TRUE when purchase order is fully confirmed',
    wwi_supplier_id       INT        NOT NULL
        COMMENT 'Source supplier ID; used by sk_resolver for temporal range join',
    wwi_stock_item_id     INT        NOT NULL
        COMMENT 'Source stock item ID; used by sk_resolver for temporal range join',
    last_modified_when    TIMESTAMP  NOT NULL
        COMMENT 'Source last-edit timestamp; watermark and SK resolution probe column',
    lineage_key           BIGINT     NOT NULL
        COMMENT 'FK to bronze.lineage_run; set at extract time',
    _extracted_at_utc     TIMESTAMP  NOT NULL
        COMMENT 'UTC timestamp when row was written to bronze by nb_extract_purchase'
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'false',
    'delta.autoOptimize.autoCompact' = 'false'
);
```

### silver_fact.fact_purchase

```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : silver_fact_fact_purchase.sql
-- PURPOSE  : Grain-level purchase order line fact table
-- TARGET   : inventory_stock.silver_fact.fact_purchase
-- RULES    : OB-002, TY-004, TY-010, TY-003, TY-009, TY-015, TY-017,
--            PE-002, PE-008, PE-P001, LN-001, NM-001, NM-009
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.silver_fact.fact_purchase (
    purchase_key          BIGINT     GENERATED ALWAYS AS IDENTITY  NOT NULL
        COMMENT 'Surrogate PK; IDENTITY auto-incremented; no business meaning',
    date_key              DATE       NOT NULL
        COMMENT 'Order date; FK to silver_dim.date',
    supplier_key          BIGINT     NOT NULL
        COMMENT 'SCD-2 surrogate FK to silver_dim.supplier (current version at order time)',
    stock_item_key        BIGINT     NOT NULL
        COMMENT 'SCD-2 surrogate FK to silver_dim.stock_item (current version at order time)',
    wwi_purchase_order_id INT        NOT NULL
        COMMENT 'Source natural key; MERGE predicate',
    ordered_outers        INT        NOT NULL
        COMMENT 'Number of outer packaging units ordered',
    ordered_quantity      INT        NOT NULL
        COMMENT 'Total individual units ordered',
    received_outers       INT        NULL
        COMMENT 'Outer units received; NULL = not yet received',
    package               STRING     NOT NULL
        COMMENT 'Package type name',
    is_order_finalized    BOOLEAN    NOT NULL
        COMMENT 'TRUE when purchase order is fully confirmed',
    lineage_key           BIGINT     NOT NULL
        COMMENT 'FK to bronze.lineage_run; identifies ETL run that loaded this row'
)
USING DELTA
CLUSTER BY (date_key, supplier_key)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
-- Fallback for pre-DBR 13.3 (remove CLUSTER BY, use instead):
-- PARTITIONED BY (date_key)
-- Post-DDL: OPTIMIZE inventory_stock.silver_fact.fact_purchase ZORDER BY (supplier_key, stock_item_key)
```

---

## 8. Mart Layer

The serving (gold) layer exposes aggregated and row-level views of the purchase data for BI consumption. Mart views are built on top of `silver_fact.fact_purchase` joined to the current-version SCD-2 dimension records (`is_current_row = TRUE`).

### mart.v_purchase_by_supplier — Materialized View

Aggregated purchase volume by supplier and stock item. Serves the `wwidw_ordered_by_supplier` Power BI report. Refreshed by `nb_refresh_v_purchase_by_supplier.py` after each successful fact load and DQ gate pass.

```sql
CREATE OR REPLACE MATERIALIZED VIEW inventory_stock.mart.v_purchase_by_supplier
COMMENT 'Aggregated purchase volume by supplier and stock item — refreshed nightly'
AS
SELECT
    s.wwi_supplier_id,
    s.supplier,
    s.category,
    si.wwi_stock_item_id,
    si.stock_item,
    si.color,
    si.unit_package_name,
    SUM(f.ordered_quantity)        AS total_quantity_ordered,
    COUNT(DISTINCT f.purchase_key) AS purchase_order_count
FROM inventory_stock.silver_fact.fact_purchase f
JOIN inventory_stock.silver_dim.supplier s
    ON f.supplier_key = s.supplier_key AND s.is_current_row = TRUE
JOIN inventory_stock.silver_dim.stock_item si
    ON f.stock_item_key = si.stock_item_key AND si.is_current_row = TRUE
GROUP BY
    s.wwi_supplier_id, s.supplier, s.category,
    si.wwi_stock_item_id, si.stock_item, si.color, si.unit_package_name;
```

**Refresh:** `REFRESH MATERIALIZED VIEW inventory_stock.mart.v_purchase_by_supplier` — executed by `nb_refresh_v_purchase_by_supplier.py` after DQ gate.

### mart.v_purchase_per_stock_item — Regular View

Row-level purchase detail joined to stock item and supplier. Serves the `wwidw_purchase_and_sale_per_stockitem_dynamic` Power BI report. No aggregation — row-level view.

```sql
CREATE OR REPLACE VIEW inventory_stock.mart.v_purchase_per_stock_item
COMMENT 'Row-level purchase detail with stock item and supplier attributes — serves wwidw_purchase_and_sale_per_stockitem_dynamic report'
AS
SELECT
    f.purchase_key,
    f.date_key,
    f.wwi_purchase_order_id,
    f.ordered_outers,
    f.ordered_quantity,
    f.received_outers,
    f.package,
    f.is_order_finalized,
    f.lineage_key,
    si.wwi_stock_item_id,
    si.stock_item,
    si.color,
    si.unit_package_name,
    s.wwi_supplier_id,
    s.supplier
FROM inventory_stock.silver_fact.fact_purchase f
JOIN inventory_stock.silver_dim.stock_item si
    ON f.stock_item_key = si.stock_item_key AND si.is_current_row = TRUE
JOIN inventory_stock.silver_dim.supplier s
    ON f.supplier_key = s.supplier_key AND s.is_current_row = TRUE;
```

### Mart Validation

After each mart refresh, `nb_validate_mart_views.py` asserts:
1. Both views return non-empty result sets
2. Mart row counts are consistent with `silver_fact.fact_purchase` totals
3. No null FK columns in either view

Mart validation failure raises an exception and is logged with `lineage_key` for full traceability.

---

## 9. Configuration Management

All environment-specific literals are externalised to `config/environment.yaml`. No hard-coded connection strings, table names, thresholds, or cluster parameters appear in `src/etl/` notebooks.

### environment.yaml structure (excerpt)

```yaml
purchase:
  etl:
    initial_load_date: "1900-01-01"
    batch_lookback_days: 1
    fact_optimize_row_threshold: 10000
    jdbc_driver:   "{{JDBC_DRIVER_CLASS}}"
    jdbc_user:     "{{JDBC_USER}}"
    jdbc_password: "{{JDBC_PASSWORD}}"
    source_table:  "{{SOURCE_TABLE_FQTN}}"
  business_rules:
    min_ordered_quantity: 0
    min_ordered_outers: 0
    date_window_tolerance_days: 0
    package_required: true
```

### Loading pattern in notebooks

```python
import yaml
with open("config/environment.yaml") as f:
    cfg = yaml.safe_load(f)
initial_load_date = cfg["purchase"]["etl"]["initial_load_date"]
```

Rule references: **NFR-009** (no hard-coded literals), **NFR-011** (deterministic, environment-portable pipelines).
