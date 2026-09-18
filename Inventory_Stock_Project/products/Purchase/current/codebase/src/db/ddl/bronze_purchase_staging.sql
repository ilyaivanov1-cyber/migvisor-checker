-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_purchase_staging.sql
-- PURPOSE  : Bronze landing table; OVERWRITE mode per run
-- SOURCE   : (new table — replaces ephemeral staging pattern)
-- TARGET   : inventory_stock.bronze.purchase_staging (Databricks Delta Lake)
-- RULES    : OB-003, OB-P002, TY-017, TY-015, TY-010, TY-004, TY-003,
--            TY-009, LN-001, NM-001, NM-002, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.bronze.purchase_staging (
    purchase_staging_key  BIGINT     GENERATED ALWAYS AS IDENTITY  NOT NULL,
    date_key              DATE       NOT NULL,
    supplier_key          BIGINT     NULL,
    stock_item_key        BIGINT     NULL,
    wwi_purchase_order_id INT        NOT NULL,
    ordered_outers        INT        NOT NULL,
    ordered_quantity      INT        NOT NULL,
    received_outers       INT        NULL,
    package               STRING     NOT NULL,
    is_order_finalized    BOOLEAN    NOT NULL,
    wwi_supplier_id       INT        NOT NULL,
    wwi_stock_item_id     INT        NOT NULL,
    last_modified_when    TIMESTAMP  NOT NULL,
    lineage_key           BIGINT     NOT NULL,
    _extracted_at_utc     TIMESTAMP  NOT NULL
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'false',
    'delta.autoOptimize.autoCompact'   = 'false'
);
