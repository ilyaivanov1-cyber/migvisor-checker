# Purchases — Data Dictionary

_TASK-023 | Design ref: design.md §1.2 Attributes | Requirements: FR-007_

---

## `purchasing.fact.purchase`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `wwi_purchase_order_id` | BIGINT | No | MERGE key (FR-006); one row per purchase order line. |
| `supplier_key` | BIGINT | No | FK → `dim.supplier.supplier_key`. Resolved via valid-time lookup; `0` (Unknown) on no match (FR-002). |
| `stock_item_key` | BIGINT | No | FK → `dim.stock_item.stock_item_key`. Resolved via valid-time lookup; `0` (Unknown) on no match (FR-003). |
| `date_key` | BIGINT | No | FK → `dim.date.date_key`. Declarative reference only; derived deterministically from `transaction_date`. |
| `ordered_outers` | BIGINT | No | Pass-through from staging. |
| `quantity_per_outer` | BIGINT | No | Pass-through from staging. |
| `ordered_quantity` | BIGINT | No | Stored (not generated) column: `ordered_outers * quantity_per_outer` (FR-004). |
| `received_outers` | BIGINT | Yes | Pass-through from staging. |
| `lineage_key` | BIGINT | No | FK → `meta.lineage.lineage_key` (FR-005). |

## `purchasing.dim.supplier`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `supplier_key` | BIGINT | No | Surrogate primary key. `0` reserved for the Unknown row. |
| `wwi_supplier_id` | BIGINT | No | Business/natural key. |
| `supplier_name` | STRING | No | Supplier display name. |
| `category` | STRING | Yes | Supplier category classification. |
| `valid_from` | TIMESTAMP | No | Start of the version's effective window (valid-time). |
| `valid_to` | TIMESTAMP | No | End of the version's effective window. |
| `is_current` | BOOLEAN | No | True for the active version. |

## `purchasing.dim.stock_item`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `stock_item_key` | BIGINT | No | Surrogate primary key. `0` reserved for the Unknown row. |
| `wwi_stock_item_id` | BIGINT | No | Business/natural key. |
| `stock_item_name` | STRING | No | Stock item display name. |
| `valid_from` | TIMESTAMP | No | Start of the version's effective window (valid-time). |
| `valid_to` | TIMESTAMP | No | End of the version's effective window. |
| `is_current` | BOOLEAN | No | True for the active version. |

`[PENDING: PL-008/OB-002]` — cross-catalog sharing mechanism for this table not yet decided; column set is stable regardless of outcome.

## `purchasing.dim.date`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date_key` | BIGINT | No | Surrogate primary key (calendar date). |
| `date_value` | DATE | No | Calendar date value. |

`[PENDING: PL-008/OB-002]` — cross-catalog sharing mechanism for this table not yet decided; column set is stable regardless of outcome.
