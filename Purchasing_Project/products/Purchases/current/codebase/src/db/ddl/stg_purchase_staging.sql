-- TASK-001: purchasing.stg.purchase_staging
-- Transient, write-once-read-once landing table for incremental purchase order line extraction.
-- Design ref: Design.md §1.2 Attributes — purchasing.stg.purchase_staging; §1.4 Indexes and Partitioning (none applied).
-- Requirements: FR-001

CREATE TABLE IF NOT EXISTS purchasing.stg.purchase_staging (
  wwi_purchase_order_id BIGINT NOT NULL,
  wwi_supplier_id       BIGINT NOT NULL,
  wwi_stock_item_id     BIGINT NOT NULL,
  transaction_date      DATE NOT NULL,
  ordered_outers        BIGINT NOT NULL,
  quantity_per_outer    BIGINT NOT NULL,
  received_outers       BIGINT,
  last_modified_when    TIMESTAMP NOT NULL,
  lineage_key           BIGINT NOT NULL
)
USING DELTA;
