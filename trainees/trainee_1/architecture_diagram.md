# Architecture & Lineage Diagram — Sales_Orders
_TASK-DOCS-003_

## Data flow overview

Source OLTP → Bronze Staging → Silver Dimensions + Facts → Gold Mart → BI

```mermaid
flowchart TD
    SRC["Source OLTP\n[PENDING: CX-P04]\nJDBC / CDC TBD"]

    subgraph Bronze ["Bronze — globalsales.stg"]
        STG_SALE["stg.sale_staging\nTRUNCATE-LOAD"]
        STG_ORD["stg.order_staging\nTRUNCATE-LOAD"]
        LINEAGE["stg.lineage\nlineage_key propagation"]
        CUTOFF["stg.etl_cutoff\nwatermark control"]
        REJECTIONS["stg.dq_rejections\nDQ rejection sink"]
    end

    subgraph Silver_Dim ["Silver — globalsales.dim"]
        DIM_CUST["dim.customer\nSCD2 | PII masked"]
        DIM_CITY["dim.city\nSCD2 | geo decomposed"]
        DIM_STOCK["dim.stock_item\nSCD2"]
        DIM_EMP["dim.employee\nSCD2"]
        DIM_PAY["dim.payment_method\nSCD2"]
        DIM_TXN["dim.transaction_type\nSCD2"]
        DIM_DATE["dim.date\nSCD0 — static"]
    end

    subgraph Silver_Fact ["Silver — globalsales.fact"]
        FACT_SALE["fact.sale\nDelta MERGE\nliquid clustering"]
        FACT_ORD["fact.order\nDelta MERGE\npartition + ZORDER"]
        UDF["fact.get_total_quantity_sold\nSQL UDF"]
    end

    subgraph Gold ["Gold — globalsales.mart"]
        MART_SUMM["mart.v_customer_sales_summary\nMaterialized | nightly refresh"]
        MART_ORD["mart.v_order_details\n:start_date param"]
        MART_SUPPLY["mart.v_order_to_supply_analytics\nNOLOCK removed"]
        MART_YEAR["mart.v_order_to_year_analytics\n:window_days param (default 100)"]
    end

    BI["Power BI (9 reports)\nDatabricks SQL Warehouse\n[PENDING: CX-P05]"]

    SRC -->|"JDBC extract\nlast_edited_when > cutoff"| STG_SALE
    SRC -->|"JDBC extract"| STG_ORD
    SRC -->|"dim changes"| DIM_CUST
    SRC -->|"dim changes"| DIM_CITY
    SRC -->|"dim changes"| DIM_STOCK
    SRC -->|"dim changes"| DIM_EMP
    SRC -->|"dim changes"| DIM_PAY
    SRC -->|"dim changes"| DIM_TXN

    LINEAGE -->|"lineage_key"| STG_SALE
    LINEAGE -->|"lineage_key"| STG_ORD
    CUTOFF -->|"watermark bounds"| SRC

    STG_SALE -->|"MERGE INTO"| FACT_SALE
    STG_ORD  -->|"MERGE INTO"| FACT_ORD

    DIM_CUST & DIM_CITY & DIM_STOCK & DIM_EMP & DIM_DATE --> FACT_SALE
    DIM_CUST & DIM_CITY & DIM_STOCK & DIM_EMP & DIM_DATE --> FACT_ORD

    FACT_SALE --> MART_SUMM
    FACT_ORD  --> MART_ORD
    FACT_ORD  --> MART_SUPPLY
    FACT_ORD  --> MART_YEAR
    FACT_SALE --> UDF

    FACT_SALE -->|"DQ assertions"| REJECTIONS
    FACT_ORD  -->|"DQ assertions"| REJECTIONS

    MART_SUMM & MART_ORD & MART_SUPPLY & MART_YEAR & UDF --> BI
```

## lineage_key propagation chain

Every row in every table can be traced to its source pipeline run:

```
stg.lineage (lineage_key=42, pipeline_run_id=..., batch_start=2024-01-15T02:00Z)
  ↓ stamped at extract
stg.sale_staging (lineage_key=42)
  ↓ propagated at MERGE
fact.sale (lineage_key=42)
  ↓ aggregated via mart view
mart.v_customer_sales_summary (references fact.sale)
```

Query: which batch loaded a specific sale row?

```sql
SELECT l.*
FROM   globalsales.fact.sale  s
JOIN   globalsales.stg.lineage l ON l.lineage_key = s.lineage_key
WHERE  s.sale_key = :target_sale_key;
```

## Pending decision nodes

| Node | Pending | Impact |
|---|---|---|
| Source OLTP connection | CX-P04 — connection strategy TBD | Ingestion notebooks have `{{SOURCE_JDBC_URL}}` placeholders |
| BI grants | CX-P05 — UC role matrix TBD | Grant scripts have `{{UC_ROLE_*}}` placeholders |
| DQ thresholds | CX-DQ-01 — business thresholds TBD | Zero-tolerance active; `dq_threshold_config.yaml` has placeholder structure |
