# Architecture: Purchase Data Product

## Overview

The Purchase data product implements a 4-layer medallion architecture on Databricks Lakehouse with Unity Catalog. Each layer has a single, clearly bounded responsibility and writes to a dedicated schema in the `inventory_stock` catalog.

| Layer | Schema | Role |
|---|---|---|
| Bronze | `inventory_stock.bronze` | Transient landing zone for incremental extracts; pipeline control tables (watermark, lineage); DQ rejection log |
| Silver Dimension | `inventory_stock.silver_dim` | SCD Type 2 conformed dimensions (supplier, stock_item); static calendar (date) |
| Silver Fact | `inventory_stock.silver_fact` | Central purchase fact table, loaded incrementally via Delta MERGE |
| Mart | `inventory_stock.mart` | BI-facing views and materialized views; no raw data |

---

## Pipeline DAG

```
Source System (transactional database)
        │
        │ JDBC extract (watermark-bounded)
        ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Ingestion (Bronze)                            │
│                                                         │
│  nb_extract_watermark  ──► nb_extract_purchase          │
│         │                         │                     │
│         │ (task values)           │ (JDBC → staging)    │
│         ▼                         ▼                     │
│  bronze.purchase_staging ◄─── watermark-bounded         │
│  bronze.etl_cutoff       (watermark control)            │
│  bronze.lineage_run      (pipeline audit log)           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Dimensions (Silver Dim)                       │
│                                                         │
│  nb_orchestrate_dimensions                              │
│    ├─► nb_load_dim_supplier  ──► silver_dim.supplier (SCD-2) │
│    ├─► nb_load_dim_stock_item ► silver_dim.stock_item (SCD-2)│
│    └─► nb_populate_date_dim  ──► silver_dim.date        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: Fact (Silver Fact)                            │
│                                                         │
│  nb_resolve_keys (LEFT JOIN dims → surrogate keys)      │
│  nb_load_fact   ──► silver_fact.fact_purchase (MERGE)   │
│       └─► conditional OPTIMIZE (CLUSTER BY)             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 4: DQ + Mart + Commit                            │
│                                                         │
│  nb_dq_smoke_tests                                      │
│  nb_dq_assertions  ──► bronze.dq_rejections             │
│  nb_dq_rejection_report                                 │
│  nb_refresh_v_purchase_by_supplier ──► mart.v_*_supplier│
│  nb_refresh_v_purchase_per_stock_item                   │
│  nb_optimize_mart                                       │
│  nb_advance_watermark ► bronze.etl_cutoff (advance)     │
│                      ► bronze.lineage_run (was_successful)│
└─────────────────────────────────────────────────────────┘
```

---

## Delta Lake Table Properties

| Table | CDF | Liquid Clustering | Retention |
|---|---|---|---|
| `bronze.purchase_staging` | Disabled | None | 90 days |
| `bronze.etl_cutoff` | Disabled | None | 2555 days |
| `bronze.lineage_run` | Disabled | None | 2555 days |
| `bronze.dq_rejections` | Disabled | None | 90 days |
| `silver_dim.supplier` | **Enabled** | None | 2555 days |
| `silver_dim.stock_item` | **Enabled** | None | 2555 days |
| `silver_dim.date` | Disabled | None | 2555 days |
| `silver_fact.fact_purchase` | Disabled | `(date_key, supplier_key, stock_item_key)` | 2555 days |

---

## lineage_key Propagation

`lineage_key` is the central audit anchor. It is generated once per pipeline run in `bronze.lineage_run` (IDENTITY column) and propagates to every downstream table:

```
bronze.lineage_run.lineage_key (IDENTITY — source of truth)
    │
    ├─► bronze.purchase_staging.lineage_key  (constant on all rows in one extract)
    ├─► silver_dim.supplier.lineage_key       (on each SCD-2 row inserted this run)
    ├─► silver_dim.stock_item.lineage_key     (on each SCD-2 row inserted this run)
    ├─► silver_fact.fact_purchase.lineage_key (on each fact row inserted this run)
    └─► bronze.dq_rejections.lineage_key     (on each DQ violation for this run)
```

A pipeline failure before `nb_advance_watermark` leaves `bronze.lineage_run.was_successful = false` — the monitoring signal for an incomplete run.
