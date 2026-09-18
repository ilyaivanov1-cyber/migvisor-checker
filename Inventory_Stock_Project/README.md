# Inventory Stock Project — Purchase Data Product

## Overview

This repository contains the fully generated SmartBuilder codebase for the **Purchase** data product, migrated from Microsoft SQL Server 2014 (WideWorldImportersDW) to **Databricks Delta Lake** on Unity Catalog (`inventory_stock`).

The migration was produced using the **migVisor SmartBuilder 4.1** pipeline:

```
TCP Phase  →  SDD Specifications  →  SmartBuilder Code Generation  →  Validation
```

---

## Architecture

The product follows a **Bronze → Silver** medallion architecture:

```
SQL Server 2014                      Databricks Delta Lake (inventory_stock)
────────────────────────             ──────────────────────────────────────
integration.purchase_staging    →    bronze.purchase_staging
integration.lineage             →    bronze.lineage_run
integration.etl_cutoff          →    bronze.etl_cutoff
integration.dq_rejections       →    bronze.dq_rejections
fact.purchase                   →    silver_fact.fact_purchase
dimension.supplier              →    silver_dim.supplier_current  (view)
dimension.stock_item            →    silver_dim.stock_item_current (view)
```

The nightly ETL pipeline runs at **02:00 UTC** as a Databricks Workflow with a halt-and-alert policy.

---

## Repository Structure

```
products/Purchase/current/codebase/
├── config/
│   ├── environment.yaml                          # ETL parameters, DQ thresholds, JDBC config
│   └── workflows/
│       └── nightly_etl_purchase.json             # Databricks Workflow definition
├── docs/
│   ├── design.md                                 # Technical design document
│   ├── data-dictionary.md                        # Full data dictionary
│   └── bi/
│       ├── wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md
│       └── wwidw_ordered_by_supplier_reconnection.md
├── src/
│   ├── common/
│   │   ├── constants.py                          # Catalog, schema, table name constants
│   │   ├── scd2_merge.py                         # SCD-2 merge framework
│   │   ├── sk_resolver.py                        # Surrogate key resolution (temporal range join)
│   │   ├── fact_merge.py                         # MERGE INTO helper for fact_purchase
│   │   └── udfs.py                               # Reusable Python UDFs
│   ├── db/
│   │   ├── ddl/
│   │   │   ├── bronze_lineage_run.sql
│   │   │   ├── bronze_etl_cutoff.sql
│   │   │   ├── bronze_purchase_staging.sql
│   │   │   ├── bronze_dq_rejections.sql
│   │   │   ├── silver_fact_fact_purchase.sql
│   │   │   ├── silver_dim_supplier_current.sql
│   │   │   └── silver_dim_stock_item_current.sql
│   │   └── grants/
│   │       └── purchase_grants.sql               # Unity Catalog GRANT statements
│   ├── etl/
│   │   ├── nb_extract_watermark.py               # Watermark read from bronze.etl_cutoff
│   │   ├── nb_extract_purchase.py                # Incremental extract from SQL Server source
│   │   └── migrate_staged_purchase_data.py       # SK resolution → DQ assertions → MERGE INTO
│   └── init/
│       └── reseed_purchase_environment.py        # One-time environment seed (requires sign-off)
└── tests/
    ├── common/
    │   ├── test_sk_resolver.py
    │   └── test_udfs.py
    └── etl/
        └── test_migrate_staged_purchase_data.py
```

---

## ETL Pipeline

The nightly workflow consists of three sequential Databricks notebook tasks:

```
nb_extract_watermark  →  nb_extract_purchase  →  migrate_staged_purchase_data
```

| Notebook | Purpose |
|---|---|
| `nb_extract_watermark` | Reads the high-watermark from `bronze.etl_cutoff`; publishes `last_cutoff` and `current_cutoff` via `dbutils.jobs.taskValues` |
| `nb_extract_purchase` | Incremental JDBC extract from SQL Server; writes raw rows to `bronze.purchase_staging`; opens a `bronze.lineage_run` record |
| `migrate_staged_purchase_data` | Resolves surrogate keys (supplier, stock item); runs 5-step QA assertion chain; executes `MERGE INTO silver_fact.fact_purchase`; closes lineage record; runs conditional OPTIMIZE |

### QA Assertion Chain

| Step | Rule | Behaviour |
|---|---|---|
| QA-P001 | Row count reconciliation — staging vs. fact | **Blocking** — raises `RuntimeError` on mismatch |
| QA-P002 | Orphaned surrogate key detection | Informational — logged, non-blocking |
| QA-P003 | Referential integrity checks per FK column | Violations written to `bronze.dq_rejections` |
| QA-P004 | Business rule assertions (quantities, date window, package non-null) | Informational — non-blocking |
| QA-P005 | DQ rejection store write + post-run summary | Always executed |

---

## Database Objects

### Bronze Layer (`inventory_stock.bronze`)

| Table | Description |
|---|---|
| `lineage_run` | One row per ETL run; tracks start/end time, row counts, success flag |
| `etl_cutoff` | High-watermark control table; one row per source table |
| `purchase_staging` | Incremental raw extract from SQL Server; overwritten each run |
| `dq_rejections` | Failed DQ assertion rows with `lineage_key` for traceability |

### Silver Fact Layer (`inventory_stock.silver_fact`)

| Table | Description |
|---|---|
| `fact_purchase` | Purchase order line grain; BIGINT IDENTITY PK; liquid clustering on `(date_key, supplier_key)` |

### Silver Dim Layer (`inventory_stock.silver_dim`)

| View | Description |
|---|---|
| `supplier_current` | Active-row view over SCD-2 `supplier` table |
| `stock_item_current` | Active-row view over SCD-2 `stock_item` table |

---

## Configuration

All runtime parameters are externalised to `config/environment.yaml`:

| Key | Default | Purpose |
|---|---|---|
| `purchase.etl.initial_load_date` | `1900-01-01` | Safe sentinel for full-history load lower boundary |
| `purchase.etl.batch_lookback_days` | `1` | Incremental batch window width |
| `purchase.etl.fact_optimize_row_threshold` | `10000` | Minimum merged rows to trigger Delta OPTIMIZE |
| `purchase.etl.jdbc_driver` | `{{JDBC_DRIVER_CLASS}}` | Pending PD-001 resolution |
| `purchase.business_rules.*` | See file | DQ assertion thresholds |

---

## Pending Decisions

| ID | Status | Blocks | Description |
|---|---|---|---|
| PD-001 | Open | `nb_extract_purchase.py`, `nightly_etl_purchase.json` | SQL Server 2014 JDBC connection profile — confirm driver class, credentials, secret scope |
| PD-002 | Open | `reseed_purchase_environment.py` | Scope owner sign-off required before execution in any environment |
| PD-003 | Open | `purchase_grants.sql` | Unity Catalog access role matrix — role names must be confirmed before GRANT execution |
| QA-DQ-01 | Open | `migrate_staged_purchase_data.py`, tests | Business DQ threshold values — acceptable informational assertion failure rates |

---

## Prerequisites

Before executing Phase 1 DDL, verify:

```bash
databricks configure --check
databricks catalogs get inventory_stock
# Must return: bronze, silver_dim, silver_fact
SHOW SCHEMAS IN inventory_stock
# External dependency — must return rows > 0
SELECT COUNT(*) FROM inventory_stock.silver_dim.supplier
```

> **Note:** `silver_dim.supplier` and `silver_dim.stock_item` must be pre-loaded by the Dimensions team before the Purchase ETL can resolve surrogate keys.

---

## Transformation Rules Applied

The generated code applies **26 product-specific transformation rules** across 9 dimensions on top of 7 inherited project-level dimensions:

| Dimension | Key rules applied |
|---|---|
| Naming (NM) | PascalCase → `lowercase_snake_case`; space-bearing names explicitly mapped; schema → Unity Catalog layer mapping |
| Types (TY) | `BIT → BOOLEAN`; `IDENTITY → BIGINT GENERATED ALWAYS AS IDENTITY`; SCD-2 validity columns → `DATE` (TY-P001 override) |
| Syntax (SX) | T-SQL `MERGE` → `MERGE INTO`; `TOP(1)` SK subquery → `sk_resolver.py`; `NEXT VALUE FOR` → `open_lineage_record()` |
| Lineage (LN) | `lineage_run` IDENTITY PK; `lineage_key` propagated to staging and fact; `taskValues` injection pattern |
| Quality (QA) | 5-step QA assertion chain (QA-P001 blocking, QA-P002–P005 informational) |
| Custom (CX) | Standard notebook skeleton (CX-P005); standard DDL header block (CX-P006); all date literals externalised to `environment.yaml` (CX-P001) |

---

## Validation

SmartBuilder validation was run against all 26 generated tasks. All 8 validation findings were identified and resolved. See `products/Purchase/current/codebase/validation-report.md` for the full per-artifact report.

---

## Project Details

| Attribute | Value |
|---|---|
| Project | Inventory_Stock_Project |
| Product | Purchase |
| Source system | Microsoft SQL Server 2014 — WideWorldImportersDW |
| Target platform | Databricks Delta Lake — Unity Catalog `inventory_stock` |
| SmartBuilder version | 4.1 |
| Generated | 2026-09-07 |
| Total tasks | 26 |
| Generated files | 28 |
