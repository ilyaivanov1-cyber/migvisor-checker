# Purchases — Technical Design
_Generated: 2026-09-22 | Pipeline stage: design_

---

## 1. Data Model

### 1.1 Entities

| Entity | Layer | Description |
|---|---|---|
| `purchasing.stg.purchase_staging` | Bronze | Incremental landing table for extracted purchase order line records, bounded by the current watermark. |
| `purchasing.dim.supplier` | Silver | Conformed supplier dimension, SCD Type 2 (valid-time history). |
| `purchasing.dim.stock_item` | Silver | Conformed stock item dimension, SCD Type 2 (valid-time history). Cross-catalog reused. |
| `purchasing.dim.date` | Silver | Static calendar dimension. Referenced only as a declarative FK target; no active load-time lookup. |
| `purchasing.fact.purchase` | Silver | Purchase order line fact. Grain: one row per purchase order line as of the current load window. |
| `purchasing.stg.dq_rejections` | Bronze | Data quality rejection sink for row-count reconciliation and referential-integrity failures. |
| `purchasing.meta.lineage` | Bronze | Batch/run bookkeeping — one record per ETL run. |
| `purchasing.meta.sequence_state` | Bronze | Delta counter table backing `lineage_key` issuance. |
| `purchasing.meta.etl_cutoff` | Bronze | High-watermark control table for incremental extraction. |
| `purchasing.meta.v_etl_cutoff` | Bronze | Reporting view over `purchasing.meta.etl_cutoff`. |

### 1.2 Attributes

#### `purchasing.stg.purchase_staging`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `wwi_purchase_order_id` | INT64 | No | Business key identifying the purchase order line; used as the MERGE key into `fact.purchase`. |
| `wwi_supplier_id` | INT64 | No | Business key used to resolve `supplier_key` via valid-time lookup. |
| `wwi_stock_item_id` | INT64 | No | Business key used to resolve `stock_item_key` via valid-time lookup. |
| `transaction_date` | DATE | No | Date of the purchase order line; used both for dimension key resolution and as the FK value for `date_key`. |
| `ordered_outers` | INT64 | No | Quantity of outers ordered. |
| `quantity_per_outer` | INT64 | No | Units per outer, used to compute `ordered_quantity`. |
| `received_outers` | INT64 | Yes | Quantity of outers received against the order line, if known at extraction time. |
| `last_modified_when` | TIMESTAMP | No | Source modification timestamp; drives the incremental watermark filter (FLT-001). |
| `lineage_key` | INT64 | No | FK → `purchasing.meta.lineage.lineage_key`. |

#### `purchasing.dim.supplier`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `supplier_key` | INT64 | No | Surrogate primary key. |
| `wwi_supplier_id` | INT64 | No | Business/natural key. |
| `supplier_name` | STRING | No | Supplier display name. |
| `category` | STRING | Yes | Supplier category classification. |
| `valid_from` | TIMESTAMP | No | Start of the version's effective window (valid-time). |
| `valid_to` | TIMESTAMP | No | End of the version's effective window; open-ended current row uses a far-future sentinel. |
| `is_current` | BOOLEAN | No | True for the active version. |

#### `purchasing.dim.stock_item`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `stock_item_key` | INT64 | No | Surrogate primary key. |
| `wwi_stock_item_id` | INT64 | No | Business/natural key. |
| `stock_item_name` | STRING | No | Stock item display name. |
| `valid_from` | TIMESTAMP | No | Start of the version's effective window (valid-time). |
| `valid_to` | TIMESTAMP | No | End of the version's effective window. |
| `is_current` | BOOLEAN | No | True for the active version. |

#### `purchasing.dim.date`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date_key` | INT64 | No | Surrogate primary key (calendar date). |
| `date_value` | DATE | No | Calendar date value. |

#### `purchasing.fact.purchase`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `wwi_purchase_order_id` | INT64 | No | MERGE key (FR-006); one row per purchase order line. |
| `supplier_key` | INT64 | No | FK → `dim.supplier.supplier_key`. Resolved via valid-time lookup; `0` (Unknown) on no match (FR-002). |
| `stock_item_key` | INT64 | No | FK → `dim.stock_item.stock_item_key`. Resolved via valid-time lookup; `0` (Unknown) on no match (FR-003). |
| `date_key` | INT64 | No | FK → `dim.date.date_key`. Declarative reference only; no active load-time lookup. |
| `ordered_outers` | INT64 | No | Pass-through from staging. |
| `quantity_per_outer` | INT64 | No | Pass-through from staging. |
| `ordered_quantity` | INT64 | No | Stored (not generated) column: `ordered_outers * quantity_per_outer` (FR-004, CALC-001). |
| `received_outers` | INT64 | Yes | Pass-through from staging. |
| `lineage_key` | INT64 | No | FK → `purchasing.meta.lineage.lineage_key` (FR-005). |

#### `purchasing.stg.dq_rejections`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `rejection_id` | INT64 | No | Surrogate primary key. |
| `lineage_key` | INT64 | No | FK → `purchasing.meta.lineage.lineage_key`. |
| `assertion_id` | STRING | No | Identifier of the failed quality assertion (e.g. `QA-003`). |
| `source_table` | STRING | No | Three-part name of the originating table. |
| `source_key` | INT64 | Yes | Primary/business key of the rejected row. |
| `rejection_reason` | STRING | No | Human-readable failure description. |
| `rejected_at` | TIMESTAMP | No | Rejection timestamp. |

#### `purchasing.meta.lineage`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `lineage_key` | INT64 | No | Surrogate primary key, issued from `meta.sequence_state`. |
| `run_id` | STRING | No | Orchestration run identifier. |
| `batch_start` | TIMESTAMP | No | Start of the processed batch window. |
| `batch_end` | TIMESTAMP | Yes | End of the processed batch window. |
| `status` | STRING | No | `RUNNING` \| `SUCCESS` \| `FAILED`. |

#### `purchasing.meta.etl_cutoff`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `entity_name` | STRING | No | Name of the entity the watermark applies to. |
| `last_cutoff` | TIMESTAMP | No | Inclusive upper bound of the last successful run. |
| `updated_at` | TIMESTAMP | No | Timestamp of the last watermark advance. |

### 1.3 Relationships

| From | To | Type | Join Condition |
|---|---|---|---|
| `fact.purchase` | `dim.supplier` | many-to-one | `fact.purchase.supplier_key = dim.supplier.supplier_key` |
| `fact.purchase` | `dim.stock_item` | many-to-one | `fact.purchase.stock_item_key = dim.stock_item.stock_item_key` |
| `fact.purchase` | `dim.date` | many-to-one | `fact.purchase.date_key = dim.date.date_key` |
| `fact.purchase` | `meta.lineage` | many-to-one | `fact.purchase.lineage_key = meta.lineage.lineage_key` |
| `stg.dq_rejections` | `meta.lineage` | many-to-one | `stg.dq_rejections.lineage_key = meta.lineage.lineage_key` |
| `stg.purchase_staging` | `dim.supplier` | many-to-one (resolution-time only) | `dim.supplier.wwi_supplier_id = stg.purchase_staging.wwi_supplier_id AND stg.purchase_staging.transaction_date >= dim.supplier.valid_from AND stg.purchase_staging.transaction_date < dim.supplier.valid_to` |
| `stg.purchase_staging` | `dim.stock_item` | many-to-one (resolution-time only) | `dim.stock_item.wwi_stock_item_id = stg.purchase_staging.wwi_stock_item_id AND stg.purchase_staging.transaction_date >= dim.stock_item.valid_from AND stg.purchase_staging.transaction_date < dim.stock_item.valid_to` |

### 1.4 Indexes and Partitioning

| Entity | Index Type | Definition |
|---|---|---|
| `purchasing.fact.purchase` | Partition Key | `date_key` |
| `purchasing.fact.purchase` | Clustering Key (ZORDER) | `(supplier_key, stock_item_key)` |
| `purchasing.fact.purchase` | Change Data Feed | Enabled — supports downstream incremental consumption. |
| `purchasing.dim.supplier` | Clustering Key | `(wwi_supplier_id, valid_from)` — supports valid-time range-join lookups. |
| `purchasing.dim.stock_item` | Clustering Key | `(wwi_stock_item_id, valid_from)` — supports valid-time range-join lookups. |
| `purchasing.stg.purchase_staging` | None | Transient, write-once-read-once staging table; no persistent optimization applied. |

---

## 2. Ingestion

| # | Input Port | Pattern | Error Handling |
|---|---|---|---|
| 1 | `purchase_staging` | Batch, incremental — extraction bounded by `purchasing.meta.etl_cutoff`; only records modified since the prior watermark are pulled. | Retry the extraction task on transient failure; halt-and-alert on repeated failure. Watermark advances only after the run's Delta MERGE and quality assertions succeed (FR-008). |
| 2 | `supplier_dimension` | On-demand valid-time range-join lookup at transformation time, not a separate extraction. | Falls back to Unknown key `0` when no matching valid-time window is found; no run failure on fallback (FR-002). |
| 3 | `stock_item_dimension` | On-demand valid-time range-join lookup at transformation time. Physical cross-catalog access mechanism is `[OWNER INPUT REQUIRED — pending PL-008/OB-002]`. | Falls back to Unknown key `0` when unresolved; no run failure on fallback (FR-003). |
| 4 | `date_dimension` | Declarative FK target only — `date_key` arrives pre-resolved with staging; no active load-time lookup is performed. | N/A |

---

## 3. Transformation

### 3.1 Calculations

| ID | Calculation | Formula | Input → Output |
|---|---|---|---|
| CALC-001 | Ordered quantity | `ordered_outers * quantity_per_outer` | `stg.purchase_staging.ordered_outers`, `stg.purchase_staging.quantity_per_outer` → `fact.purchase.ordered_quantity` (FR-004) |
| CALC-002 | Supplier key resolution | Valid-time range-join: select the `dim.supplier` row where `wwi_supplier_id` matches and `transaction_date` falls within `[valid_from, valid_to)`; else `0`. | `stg.purchase_staging.wwi_supplier_id`, `stg.purchase_staging.transaction_date` → `fact.purchase.supplier_key` (FR-002) |
| CALC-003 | Stock item key resolution | Valid-time range-join: select the `dim.stock_item` row where `wwi_stock_item_id` matches and `transaction_date` falls within `[valid_from, valid_to)`; else `0`. | `stg.purchase_staging.wwi_stock_item_id`, `stg.purchase_staging.transaction_date` → `fact.purchase.stock_item_key` (FR-003) |
| CALC-004 | Lineage key assignment | Next value issued from `meta.sequence_state` counter, stamped on every row of the batch. | (system-generated) → `fact.purchase.lineage_key` (FR-005) |

### 3.2 Filters

| ID | Filter | Condition |
|---|---|---|
| FLT-001 | Incremental watermark filter | `last_modified_when > :prior_cutoff AND last_modified_when <= :new_cutoff`, applied during extraction into `stg.purchase_staging` (FR-001). |

---

## 4. Serving

| # | Output Port | Implementation | Notes |
|---|---|---|---|
| 1 | `dataAccess.default` (`purchasing.fact.purchase`) | `[OWNER INPUT REQUIRED — cross-catalog exposure mechanism pending PL-009/OB-008: Unity Catalog cross-catalog GRANT SELECT vs. federated/replicated read-only copy]` | Serves the three known cross-catalog consumers (FR-007). No purchase-exclusive mart view is owned by this product. |

---

## 5. Observability

### 5.1 Lineage Tracking

Every run creates a `purchasing.meta.lineage` record at batch start (`status = RUNNING`) and closes it (`status = SUCCESS` or `FAILED`) at batch end. `lineage_key` is stamped on every row written to `purchasing.fact.purchase` and any row routed to `purchasing.stg.dq_rejections`, giving row-level traceability back to the loading run (FR-005).

### 5.2 Validation Rules (Quality Implementation)

| ID | Dimension | Rule | Threshold | Failure Action |
|---|---|---|---|---|
| QV-001 | Consistency | Count of distinct `wwi_purchase_order_id` in the staged batch must equal the count reflected in `fact.purchase` post-load. | Zero-tolerance | Block the run; raise an alert before the watermark advances (QA-001). |
| QV-002 | Accuracy | Rate of `supplier_key`/`stock_item_key` resolving to Unknown (`0`) is tracked against a rolling historical baseline. | `[OWNER INPUT REQUIRED — pending QA-002]` | Non-blocking monitoring alert only. |
| QV-003 | Conformity | Every `supplier_key`, `stock_item_key`, and `date_key` on `fact.purchase` must resolve to an existing dimension row. | Zero silent orphans | Route the offending row to `purchasing.stg.dq_rejections`; non-blocking (QA-003). |

### 5.3 Monitoring and Alerting

Run metrics (rows extracted, rows loaded, rows rejected, run status) are queryable from `purchasing.meta.lineage`. A run halts and raises an alert before advancing `purchasing.meta.etl_cutoff` whenever QV-001 fails; QV-002 and QV-003 emit non-blocking alerts and route affected rows to `purchasing.stg.dq_rejections` without halting the run.
