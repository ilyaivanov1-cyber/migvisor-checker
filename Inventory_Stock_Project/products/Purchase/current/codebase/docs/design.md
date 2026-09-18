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
ON target.wwi_purchase_order_id = source.wwi_purchase_order_id

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

## 7. Configuration Management

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
