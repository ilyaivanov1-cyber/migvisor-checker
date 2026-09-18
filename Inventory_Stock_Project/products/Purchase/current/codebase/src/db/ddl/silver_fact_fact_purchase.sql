-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : silver_fact_fact_purchase.sql
-- PURPOSE  : Grain-level purchase order line fact table
-- SOURCE   : (new table)
-- TARGET   : inventory_stock.silver_fact.fact_purchase (Databricks Delta Lake)
-- RULES    : OB-002, TY-004, TY-010, TY-003, TY-009, TY-015, TY-017,
--            PE-002, PE-008, PE-P001, LN-001, NM-001, NM-009, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.silver_fact.fact_purchase (
    purchase_key          BIGINT     GENERATED ALWAYS AS IDENTITY  NOT NULL,
    date_key              DATE       NOT NULL,
    supplier_key          BIGINT     NOT NULL,
    stock_item_key        BIGINT     NOT NULL,
    wwi_purchase_order_id INT        NOT NULL,
    ordered_outers        INT        NOT NULL,
    ordered_quantity      INT        NOT NULL,
    received_outers       INT        NULL,
    package               STRING     NOT NULL,
    is_order_finalized    BOOLEAN    NOT NULL,
    lineage_key           BIGINT     NOT NULL
        COMMENT 'FK to bronze.lineage_run; identifies ETL run that loaded this row'
)
USING DELTA
CLUSTER BY (date_key, supplier_key)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact'   = 'true'
);
-- Fallback for pre-DBR 13.3 (remove CLUSTER BY above, use instead):
-- PARTITIONED BY (date_key)
-- ZORDER applied via post-DDL: OPTIMIZE fact_purchase ZORDER BY (supplier_key, stock_item_key)
