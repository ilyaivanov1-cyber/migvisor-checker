# Technical Design: Purchase

_Product: Purchase | Project: Inventory_Stock_Project | Generated: 2026-09-07_
_Implements requirements: `products/Purchase/current/specifications/development_plan/requirements.md`_

---

## 1. Data Model

### 1.1 Entities

| Entity | Layer | Schema | Table Name | Type | Description |
|---|---|---|---|---|---|
| Fact: Purchase Order Line | silver | `silver_fact` | `fact_purchase` | Delta managed table | Central grain-level fact table. One row per purchase order line. CLUSTER BY (date_key, supplier_key). |
| Dim: Supplier | silver | `silver_dim` | `supplier` | Delta managed table | SCD-2 supplier dimension. Externally owned. CLUSTER BY (supplier_key). |
| Dim: Stock Item | silver | `silver_dim` | `stock_item` | Delta managed table | SCD-2 stock item dimension. Externally owned. CLUSTER BY (stock_item_key). |
| Dim: Date | silver | `silver_dim` | `date` | Delta managed table | Static date reference. Externally owned. PK is `date` (DATE). |
| Staging: Purchase | bronze | `bronze` | `purchase_staging` | Delta managed table | OVERWRITE mode per run. Landing table for incremental extract. |
| Control: ETL Cutoff | bronze | `bronze` | `etl_cutoff` | Delta managed table | Watermark control — one row per tracked table. |
| Control: Lineage Run | bronze | `bronze` | `lineage_run` | Delta managed table | Audit log — one row per ETL run. IDENTITY PK. CDF enabled. |
| DQ: Rejections | bronze | `bronze` | `dq_rejections` | Delta managed table | Centralised DQ rejection sink. IDENTITY PK. autoOptimize enabled. |

### 1.2 Attributes

**`inventory_stock.silver_fact.fact_purchase`**

| Column | Type | Nullable | Description |
|---|---|---|---|
| `purchase_key` | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | Surrogate PK. Delta-managed IDENTITY column. |
| `date_key` | DATE | NOT NULL | FK → silver_dim.date.date. Derived from order date. |
| `supplier_key` | BIGINT | NOT NULL | FK → silver_dim.supplier.supplier_key. Resolved via sk_resolver.py. |
| `stock_item_key` | BIGINT | NOT NULL | FK → silver_dim.stock_item.stock_item_key. Resolved via sk_resolver.py. |
| `wwi_purchase_order_id` | INT | NOT NULL | Business natural key. MERGE predicate column. |
| `ordered_outers` | INT | NOT NULL | Ordered quantity in outer packaging units. |
| `ordered_quantity` | INT | NOT NULL | Ordered quantity in individual units. |
| `received_outers` | INT | NULL | Received quantity in outer packaging units. |
| `package` | STRING | NOT NULL | Packaging type name. |
| `is_order_finalized` | BOOLEAN | NOT NULL | True when order has been finalized. |
| `lineage_key` | BIGINT | NOT NULL | FK → bronze.lineage_run.lineage_key. ETL run identifier. |

**`inventory_stock.bronze.purchase_staging`**

| Column | Type | Nullable | Description |
|---|---|---|---|
| `purchase_staging_key` | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | Surrogate PK. |
| `date_key` | DATE | NOT NULL | Derived order date. |
| `supplier_key` | BIGINT | NULL | Populated by sk_resolver.py after extract. |
| `stock_item_key` | BIGINT | NULL | Populated by sk_resolver.py after extract. |
| `wwi_purchase_order_id` | INT | NOT NULL | Business natural key. |
| `ordered_outers` | INT | NOT NULL | Ordered outer quantity. |
| `ordered_quantity` | INT | NOT NULL | Ordered unit quantity. |
| `received_outers` | INT | NULL | Received outer quantity. |
| `package` | STRING | NOT NULL | Packaging type name. |
| `is_order_finalized` | BOOLEAN | NOT NULL | Order finalization flag. |
| `wwi_supplier_id` | INT | NOT NULL | Business FK to supplier — used by sk_resolver.py for dimension join. |
| `wwi_stock_item_id` | INT | NOT NULL | Business FK to stock item — used by sk_resolver.py for dimension join. |
| `last_modified_when` | TIMESTAMP | NOT NULL | Row modification timestamp from source — used as temporal probe in SCD-2 key resolution. |
| `lineage_key` | BIGINT | NOT NULL | FK → bronze.lineage_run.lineage_key. |
| `_extracted_at_utc` | TIMESTAMP | NOT NULL | UTC timestamp of the bronze extraction run. |

**`inventory_stock.bronze.lineage_run`**

| Column | Type | Nullable | Description |
|---|---|---|---|
| `lineage_key` | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | PK. Identity surrogate for each ETL run. |
| `etl_run_id` | STRING | NOT NULL | Unique run identifier (UUID or Workflow run ID). |
| `table_name` | STRING | NOT NULL | Target table being loaded (e.g., `fact_purchase`). |
| `pipeline_name` | STRING | NOT NULL | Workflow name. |
| `data_load_started` | TIMESTAMP | NOT NULL | UTC timestamp when the run began. |
| `data_load_completed` | TIMESTAMP | NULL | UTC timestamp when the run closed. NULL until closed. |
| `was_successful` | BOOLEAN | NULL | True on successful close; False on failure close; NULL while running. |
| `table_row_count` | BIGINT | NULL | Count of rows merged into the fact table. |
| `source_system_cutoff_time` | TIMESTAMP | NOT NULL | Upper bound of the extract window for this run. |

**`inventory_stock.bronze.etl_cutoff`**

| Column | Type | Nullable | Description |
|---|---|---|---|
| `table_name` | STRING | NOT NULL | PK. Target table name (e.g., `fact_purchase`). |
| `cutoff_time` | TIMESTAMP | NOT NULL | Most recent successfully processed cutoff timestamp. |
| `last_updated_utc` | TIMESTAMP | NOT NULL | Timestamp of the last successful update. |

**`inventory_stock.bronze.dq_rejections`**

| Column | Type | Nullable | Description |
|---|---|---|---|
| `rejection_id` | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | Surrogate PK. |
| `lineage_key` | BIGINT | NOT NULL | FK to lineage_run — identifies the ETL run. |
| `rule_id` | STRING | NOT NULL | QA rule ID that detected the violation (e.g., `QA-P003`). |
| `source_table` | STRING | NOT NULL | Target table where the violation was detected. |
| `pk_column` | STRING | NOT NULL | Name of the PK column in the source table. |
| `pk_value` | STRING | NOT NULL | Value of the PK for the offending row. |
| `violation_column` | STRING | NOT NULL | Column containing the violation. |
| `violation_value` | STRING | NULL | Value that triggered the violation rule. |
| `rejection_reason` | STRING | NOT NULL | Human-readable description of the violation. |
| `detected_at` | TIMESTAMP | NOT NULL | UTC timestamp when the violation was detected. |

### 1.3 Relationships

| From | To | Join Columns | Type | Notes |
|---|---|---|---|---|
| `silver_fact.fact_purchase` | `silver_dim.supplier` | `supplier_key = supplier_key` | many-to-one | Non-nullable FK; key=0 sentinel handles unresolved rows |
| `silver_fact.fact_purchase` | `silver_dim.stock_item` | `stock_item_key = stock_item_key` | many-to-one | Non-nullable FK; key=0 sentinel handles unresolved rows |
| `silver_fact.fact_purchase` | `silver_dim.date` | `date_key = date` | many-to-one | FK to DATE-typed PK column named `date` in silver_dim.date |
| `silver_fact.fact_purchase` | `bronze.lineage_run` | `lineage_key = lineage_key` | many-to-one | Every fact row traceable to its ETL run |
| `bronze.purchase_staging` | `bronze.lineage_run` | `lineage_key = lineage_key` | many-to-one | Staging rows carry the run's lineage_key |
| `bronze.dq_rejections` | `bronze.lineage_run` | `lineage_key = lineage_key` | many-to-one | DQ violations traceable to their originating run |

### 1.4 Indexes and Partitioning

| Entity | Strategy | Columns | Applicability | Notes |
|---|---|---|---|---|
| `silver_fact.fact_purchase` | CLUSTER BY (Liquid Clustering) | `date_key`, `supplier_key` | DBR 13.3+ | AutoOptimize and AutoCompact enabled |
| `silver_fact.fact_purchase` | PARTITIONED BY + ZORDER (fallback) | PARTITIONED BY (date_key); ZORDER BY (supplier_key, stock_item_key) | Pre-DBR 13.3 | PE-P001 fallback |
| `silver_dim.supplier` | CLUSTER BY (Liquid Clustering) | `supplier_key` | DBR 13.3+ | Optimises point-lookup joins from fact |
| `silver_dim.stock_item` | CLUSTER BY (Liquid Clustering) | `stock_item_key` | DBR 13.3+ | Optimises point-lookup joins from fact |
| `bronze.purchase_staging` | None | N/A | All runtimes | Ephemeral; no clustering applied |

---

## 2. Ingestion

### 2.1 Ingestion Patterns

| Input Source | Pattern | Frequency | Write Mode | Error Handling |
|---|---|---|---|---|
| `bronze.purchase_staging` (from upstream extract) | Batch — full OVERWRITE per run | Daily | OVERWRITE | If extract fails, Workflow task is FAILED; staging is left empty and the MERGE step is skipped via zero-rows guard |
| `silver_dim.supplier` (runtime SCD-2 join) | Read-only dimension join during sk_resolver.py | Per run | N/A (read only) | If dimension table is empty or unavailable, sk_resolver.py raises an exception; Workflow task is FAILED |
| `silver_dim.stock_item` (runtime SCD-2 join) | Read-only dimension join during sk_resolver.py | Per run | N/A (read only) | Same as supplier — exception on unavailability |
| `silver_dim.date` (FK lookup) | Read-only reference join during extract | Per run | N/A (read only) | date_key derived in extract notebook; missing date FK violations captured by QA-P003 post-merge |
| `bronze.etl_cutoff` (watermark read) | Point lookup at job start | Per run | N/A (read only) | If record missing, nb_extract_watermark uses `initial_load_date` from `config/environment.yaml` as default |

### 2.2 Extract Window Computation

**Notebook:** `nb_extract_watermark`

```
last_cutoff  ← SELECT cutoff_time FROM bronze.etl_cutoff WHERE table_name = 'fact_purchase'
               (default: config.purchase.etl.initial_load_date if no record exists)

current_cutoff ← CURRENT_TIMESTAMP() (upper bound for this run)

Rows extracted ← WHERE last_modified_when > last_cutoff
                   AND last_modified_when <= current_cutoff
```

The `lineage_key` is obtained by inserting a new record into `bronze.lineage_run` and reading the generated IDENTITY value. It is published via `dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_key)`.

### 2.3 Zero-Rows Guard

Every ETL notebook in `src/etl/` evaluates `staging_count = SELECT COUNT(*) FROM bronze.purchase_staging`. If `staging_count == 0`, the notebook exits immediately via `dbutils.notebook.exit("SKIPPED: zero rows")` without performing any write operations.

---

## 3. Transformation Logic

### 3.1 Calculations

| ID | Name | Formula | Input Columns | Output Column | Notes |
|---|---|---|---|---|---|
| CALC-001 | date_key derivation | `CAST(order_date AS DATE)` | `order_date` (TIMESTAMP from source extract) | `purchase_staging.date_key` | Performed in `nb_extract_purchase` during the OLTP extract JOIN |
| CALC-002 | supplier_key resolution | Temporal range join: `wwi_supplier_id == dim.wwi_supplier_id AND last_modified_when > CAST(dim.valid_from AS TIMESTAMP) AND last_modified_when <= CAST(dim.valid_to AS TIMESTAMP)`; `ROW_NUMBER() OVER (PARTITION BY purchase_staging_key ORDER BY dim.valid_from DESC) = 1`; `COALESCE(dim.supplier_key, 0)` | `purchase_staging.wwi_supplier_id`, `purchase_staging.last_modified_when`, `silver_dim.supplier.supplier_key`, `valid_from`, `valid_to` | `purchase_staging.supplier_key` | Executed in `sk_resolver.py`. valid_from/valid_to are DATE; cast to TIMESTAMP for comparison. |
| CALC-003 | stock_item_key resolution | Same temporal range join pattern as CALC-002, joining on `wwi_stock_item_id` against `silver_dim.stock_item` | `purchase_staging.wwi_stock_item_id`, `purchase_staging.last_modified_when`, `silver_dim.stock_item.stock_item_key`, `valid_from`, `valid_to` | `purchase_staging.stock_item_key` | Executed in `sk_resolver.py`. Same CAST and COALESCE pattern. |
| CALC-004 | lineage_key injection | INSERT INTO `bronze.lineage_run` (...); `lineage_key = lineage_run.lineage_key` (IDENTITY-generated) | N/A (generated) | `lineage_run.lineage_key` (propagated to all staging and fact rows) | Executed in `nb_extract_watermark`; propagated via `dbutils.jobs.taskValues`. |
| CALC-005 | _extracted_at_utc audit stamp | `current_timestamp()` | N/A | `purchase_staging._extracted_at_utc` | Written by `nb_extract_purchase` at staging insert time. |
| CALC-006 | rows_merged count | MERGE INTO `silver_fact.fact_purchase` using `bronze.purchase_staging` → `rows_merged = spark.sql("SELECT COUNT(*) FROM fact_purchase WHERE lineage_key = ...")` | `bronze.purchase_staging`, `silver_fact.fact_purchase` | `lineage_run.table_row_count` | Captured by `fact_merge.py` after MERGE; used in QA-P001 reconciliation. |

### 3.2 Filters

| ID | Name | Condition | Applied At | Notes |
|---|---|---|---|---|
| FLT-001 | Incremental watermark filter | `last_modified_when > last_etl_cutoff AND last_modified_when <= current_cutoff` | `nb_extract_purchase` (extract query) | Cutoff values from `bronze.etl_cutoff`; bounds externalised to `config/environment.yaml`. |
| FLT-002 | SK resolution temporal range | `last_modified_when > CAST(dim.valid_from AS TIMESTAMP) AND last_modified_when <= CAST(dim.valid_to AS TIMESTAMP)` | `sk_resolver.py` (dimension join predicate) | Per SCD-2 temporal range pattern. DATE columns cast to TIMESTAMP for probe comparison. |
| FLT-003 | SK resolution tie-breaker | `ROW_NUMBER() OVER (PARTITION BY purchase_staging_key ORDER BY dim.valid_from DESC) = 1` | `sk_resolver.py` (window filter) | Selects most recent valid dimension version when multiple versions overlap the transaction timestamp. |
| FLT-004 | OPTIMIZE threshold | `rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD` (10,000) | `migrate_staged_purchase_data.py` (post-MERGE) | Threshold read from `config/environment.yaml` under `purchase.etl.fact_optimize_row_threshold`. |

### 3.3 MERGE Logic

**MERGE INTO `silver_fact.fact_purchase`**

```sql
MERGE INTO inventory_stock.silver_fact.fact_purchase AS target
USING inventory_stock.bronze.purchase_staging AS source
  ON target.wwi_purchase_order_id = source.wwi_purchase_order_id
WHEN MATCHED THEN UPDATE SET
  target.date_key            = source.date_key,
  target.supplier_key        = source.supplier_key,
  target.stock_item_key      = source.stock_item_key,
  target.ordered_outers      = source.ordered_outers,
  target.ordered_quantity    = source.ordered_quantity,
  target.received_outers     = source.received_outers,
  target.package             = source.package,
  target.is_order_finalized  = source.is_order_finalized,
  target.lineage_key         = source.lineage_key
WHEN NOT MATCHED THEN INSERT (
  date_key, supplier_key, stock_item_key, wwi_purchase_order_id,
  ordered_outers, ordered_quantity, received_outers, package,
  is_order_finalized, lineage_key
) VALUES (
  source.date_key, source.supplier_key, source.stock_item_key,
  source.wwi_purchase_order_id, source.ordered_outers,
  source.ordered_quantity, source.received_outers, source.package,
  source.is_order_finalized, source.lineage_key
)
```

---

## 4. Serving

### 4.1 Output Ports

| Output Port | Type | Primary Dataset | Access Pattern | Refresh |
|---|---|---|---|---|
| `fact_purchase_sql_warehouse` | Databricks SQL Warehouse | `inventory_stock.silver_fact.fact_purchase` | SQL SELECT via JDBC or HTTP connector; Unity Catalog RBAC | Daily; available by 06:00 UTC |
| `power_bi_purchase_reports` | Power BI semantic model | `inventory_stock.silver_fact.fact_purchase`, `silver_dim.supplier`, `silver_dim.stock_item` | DirectQuery or Import via Databricks SQL Warehouse connector | Daily; reconnected from SQL Server connection |

### 4.2 Report Connectivity

| Report Name | Access Method | Primary Tables | Notes |
|---|---|---|---|
| `wwidw_purchase_and_sale_per_stockitem_dynamic` | Power BI → Databricks SQL Warehouse | `silver_fact.fact_purchase`, `silver_fact.fact_sale` (Sales_Orders product) | Cross-product dependency — requires coordinated cutover with Sales_Orders |
| `wwidw_ordered_by_supplier` | Power BI → Databricks SQL Warehouse | `silver_fact.fact_purchase`, `silver_dim.supplier` | Self-contained within Purchase product |

### 4.3 Views

| View | Type | Schema | Based On | Purpose |
|---|---|---|---|---|
| `supplier_current` | CREATE OR REPLACE VIEW | `silver_dim` | `silver_dim.supplier WHERE is_current_row = TRUE` | Pre-filter to current supplier versions for simplified joins |
| `stock_item_current` | CREATE OR REPLACE VIEW | `silver_dim` | `silver_dim.stock_item WHERE is_current_row = TRUE` | Pre-filter to current stock item versions for simplified joins |

_Note: These are thin row-filter views with no aggregation — they are NOT materialized views. Any future Gold-layer analytics views that aggregate data must use `CREATE OR REPLACE MATERIALIZED VIEW`._

---

## 5. Observability

### 5.1 Validation Rules

| ID | Dimension | Rule | Target | Threshold | Failure Action |
|---|---|---|---|---|---|
| QV-001 | Completeness | `inserted_count == staging_count` (QA-P001 row count reconciliation) | `silver_fact.fact_purchase` vs `bronze.purchase_staging` | Zero tolerance — any mismatch | `RuntimeError` → Workflow task FAILED; `lineage_run.was_successful = false` |
| QV-002 | Consistency | LEFT ANTI JOIN `fact_purchase.supplier_key` against `silver_dim.supplier.supplier_key` (QA-P003 RI check) | `silver_fact.fact_purchase.supplier_key` | 0 violations expected; non-zero written to `dq_rejections` | Log at ERROR; write to `dq_rejections`; pipeline continues |
| QV-003 | Consistency | LEFT ANTI JOIN `fact_purchase.stock_item_key` against `silver_dim.stock_item.stock_item_key` (QA-P003 RI check) | `silver_fact.fact_purchase.stock_item_key` | 0 violations expected; non-zero written to `dq_rejections` | Log at ERROR; write to `dq_rejections`; pipeline continues |
| QV-004 | Consistency | LEFT ANTI JOIN `fact_purchase.date_key` against `silver_dim.date.date` (QA-P003 RI check) | `silver_fact.fact_purchase.date_key` | 0 violations expected; non-zero written to `dq_rejections` | Log at ERROR; write to `dq_rejections`; pipeline continues |
| QV-005 | Uniqueness | LEFT ANTI JOIN `fact_purchase.supplier_key` against any row in `silver_dim.supplier` (excl. key=0) — orphan detection (QA-P002) | `silver_fact.fact_purchase.supplier_key` | 0 orphans expected; non-zero logged | Log at WARNING; pipeline continues |
| QV-006 | Uniqueness | LEFT ANTI JOIN `fact_purchase.stock_item_key` against any row in `silver_dim.stock_item` (excl. key=0) — orphan detection (QA-P002) | `silver_fact.fact_purchase.stock_item_key` | 0 orphans expected; non-zero logged | Log at WARNING; pipeline continues |
| QV-007 | Accuracy | `ordered_outers >= 0 AND ordered_quantity >= 0` (QA-P004 business rule) | `silver_fact.fact_purchase` | 0 violations expected | Log at WARNING; pipeline continues |
| QV-008 | Accuracy | `date_key BETWEEN batch_date_min AND batch_date_max` (QA-P004 business rule) | `silver_fact.fact_purchase` | 0 out-of-window rows expected | Log at WARNING; pipeline continues |
| QV-009 | Accuracy | `package IS NOT NULL AND TRIM(package) != ''` (QA-P004 business rule) | `silver_fact.fact_purchase` | 0 null/empty rows expected | Log at WARNING; pipeline continues |

### 5.2 Lineage and Auditability

| Component | Implementation | Purpose |
|---|---|---|
| `bronze.lineage_run` | IDENTITY-keyed Delta table; CDF enabled | One record per ETL run; tracks start/end, success, row count, source cutoff |
| `lineage_key` propagation | `dbutils.jobs.taskValues.set/get` in Databricks Workflow | Every staging and fact row traceable to the ETL run that produced it |
| `bronze.dq_rejections` | append-only Delta table | All QA violations persisted with `lineage_key`, `rule_id`, column detail |
| Post-run DQ summary | `spark.sql("SELECT rule_id, COUNT(*) FROM dq_rejections WHERE lineage_key = X GROUP BY rule_id").show()` | Logged at end of every ETL run for operational monitoring |

### 5.3 Alerting

| Condition | Alerting Mechanism | Severity |
|---|---|---|
| Workflow task FAILED (QA-P001 row count mismatch) | Databricks Workflow task failure notification | CRITICAL |
| Workflow task FAILED (unhandled exception in main ETL) | Databricks Workflow task failure notification | CRITICAL |
| RI violations present in `dq_rejections` (QA-P003) | Post-run DQ summary log; operator review required | WARNING |
| Business rule violations present (QA-P004) | Post-run DQ summary log; operator review | INFO |
| Orphaned SK count > 0 (QA-P002) | Post-run DQ summary log | INFO |

### 5.4 Workflow Task Structure

| Task ID | Notebook | Dependencies | Purpose |
|---|---|---|---|
| `nb_extract_watermark` | `src/etl/nb_extract_watermark.py` | None (entry task) | Open lineage record; compute extract window; publish lineage_key via taskValues |
| `nb_extract_purchase` | `src/etl/nb_extract_purchase.py` | `nb_extract_watermark` | Extract incremental rows → bronze.purchase_staging (OVERWRITE) |
| `migrate_staged_purchase_data` | `src/etl/migrate_staged_purchase_data.py` (orchestrates sk_resolver.py + fact_merge.py) | `nb_extract_purchase` + dimension load tasks (external) | SK resolution; MERGE INTO fact_purchase; QA checks; close lineage |
