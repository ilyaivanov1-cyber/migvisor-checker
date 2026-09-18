-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_dq_rejections.sql
-- PURPOSE  : Centralised DQ rejection store with lineage traceability
-- SOURCE   : (new table — no source equivalent)
-- TARGET   : inventory_stock.bronze.dq_rejections (Databricks Delta Lake)
-- RULES    : QA-P005, TY-017, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.bronze.dq_rejections (
    rejection_id     BIGINT     GENERATED ALWAYS AS IDENTITY  NOT NULL,
    lineage_key      BIGINT     NOT NULL
        COMMENT 'FK to lineage_run; identifies the ETL run that produced this rejection',
    rule_id          STRING     NOT NULL
        COMMENT 'QA rule ID that detected this violation (e.g., QA-P003)',
    source_table     STRING     NOT NULL,
    pk_column        STRING     NOT NULL,
    pk_value         STRING     NOT NULL,
    violation_column STRING     NOT NULL,
    violation_value  STRING     NULL,
    rejection_reason STRING     NOT NULL,
    detected_at      TIMESTAMP  NOT NULL DEFAULT current_timestamp()
)
USING DELTA
TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true');
