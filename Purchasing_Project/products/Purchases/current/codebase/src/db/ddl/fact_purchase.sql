-- TASK-007: purchasing.fact.purchase
-- Design ref: Design.md §1.2 Attributes — purchasing.fact.purchase; §1.4 Indexes and Partitioning.
-- Requirements: FR-004, FR-005, FR-006
-- Depends on: TASK-002 (dim.supplier), TASK-003 (dim.stock_item / dim.date), TASK-004 (meta.lineage)

CREATE TABLE IF NOT EXISTS purchasing.fact.purchase (
  wwi_purchase_order_id BIGINT NOT NULL,
  supplier_key          BIGINT NOT NULL,
  stock_item_key        BIGINT NOT NULL,
  date_key              BIGINT NOT NULL,
  ordered_outers        BIGINT NOT NULL,
  quantity_per_outer    BIGINT NOT NULL,
  ordered_quantity      BIGINT NOT NULL,
  received_outers       BIGINT,
  lineage_key           BIGINT NOT NULL
)
USING DELTA
PARTITIONED BY (date_key)
TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- ordered_quantity is deliberately a stored column with no GENERATED ALWAYS AS clause (FR-004);
-- it is populated by TASK-012's transformation logic, not by a DDL-level computed expression.

OPTIMIZE purchasing.fact.purchase ZORDER BY (supplier_key, stock_item_key);
