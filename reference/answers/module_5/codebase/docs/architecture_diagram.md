# Architecture: Purchase Data Product

## Overview

The Purchase data product implements a 4-layer medallion architecture on Databricks Lakehouse with Unity Catalog. Each layer has a single, clearly bounded responsibility and writes to a dedicated schema in the `globalpurchase` catalog.

| Layer | Schema | Role |
|---|---|---|
| Staging | `globalpurchase.stg` | Transient landing zone for incremental extracts; pipeline control tables (watermark, lineage); DQ rejection log |
| Dimension | `globalpurchase.dim` | SCD Type 2 conformed dimensions (supplier, stock_item); static calendar (date) |
| Fact | `globalpurchase.fact` | Central purchase fact table, loaded incrementally via Delta MERGE |
| Mart | `globalpurchase.mart` | BI-facing views and materialized views; no raw data |

---

## Pipeline DAG

```
Source System (transactional database)
        │
        │ JDBC extract (watermark-bounded)
        ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Ingestion                                     │
│                                                         │
│  nb_extract_watermark  ──► nb_extract_dimensions        │
│         │                         │                     │
│         │ (task values)           │ (temp views)        │
│         ▼                         ▼                     │
│  nb_extract_purchase  ──► stg.purchase_staging          │
│                               stg.etl_cutoff            │
│                               stg.lineage               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Dimensions                                    │
│                                                         │
│  nb_orchestrate_dimensions                              │
│    ├─► nb_populate_dim_date  ──► dim.date               │
│    ├─► nb_load_dim_supplier  ──► dim.supplier (SCD-2)   │
│    └─► nb_load_dim_stock_item ► dim.stock_item (SCD-2)  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: Fact                                          │
│                                                         │
│  nb_orchestrate_facts                                   │
│    └─► sk_resolver (LEFT JOIN dims)                     │
│    └─► fact_merge  ──► fact.purchase (MERGE)            │
│         └─► conditional OPTIMIZE (ZORDER)               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 4: DQ + Mart + Commit                            │
│                                                         │
│  nb_dq_smoke_tests                                      │
│  nb_dq_purchase  ──► stg.dq_rejections                  │
│  nb_dq_rejection_report                                 │
│  nb_refresh_v_purchase_by_supplier ──► mart.v_*_supplier│
│  nb_refresh_v_purchase_per_stock_item                   │
│  nb_optimize_mart                                       │
│  nb_validate_mart_views                                 │
│  nb_commit_watermark ──► stg.etl_cutoff (advance)       │
│                      ──► stg.lineage (status=success)   │
└─────────────────────────────────────────────────────────┘
```

---

## Delta Lake Table Properties

| Table | CDF | Liquid Clustering | Retention |
|---|---|---|---|
| `stg.purchase_staging` | Disabled | None | 90 days |
| `stg.etl_cutoff` | Disabled | None | 2555 days |
| `stg.lineage` | Disabled | None | 2555 days |
| `stg.dq_rejections` | Disabled | None | 90 days |
| `dim.supplier` | **Enabled** | None | 2555 days |
| `dim.stock_item` | **Enabled** | None | 2555 days |
| `dim.date` | Disabled | None | 2555 days |
| `fact.purchase` | Disabled | `(date_key, supplier_key, stock_item_key)` | 2555 days |

---

## lineage_key Propagation

`lineage_key` is the central audit anchor. It is generated once per pipeline run in `stg.lineage` (IDENTITY column) and propagates to every downstream table:

```
stg.lineage.lineage_key (IDENTITY — source of truth)
    │
    ├─► stg.purchase_staging.lineage_key  (constant on all rows in one extract)
    ├─► dim.supplier.lineage_key           (on each SCD-2 row inserted this run)
    ├─► dim.stock_item.lineage_key         (on each SCD-2 row inserted this run)
    ├─► fact.purchase.lineage_key          (on each fact row inserted this run)
    └─► stg.dq_rejections.lineage_key     (on each DQ violation for this run)
```

A pipeline failure before `nb_commit_watermark` leaves `stg.lineage.status = 'running'` — the monitoring signal for an incomplete run.
