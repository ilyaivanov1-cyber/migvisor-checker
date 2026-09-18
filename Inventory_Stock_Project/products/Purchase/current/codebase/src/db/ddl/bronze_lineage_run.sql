-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_lineage_run.sql
-- PURPOSE  : Create the bronze.lineage_run Delta table to store one row per ETL run for end-to-end auditability
-- SOURCE   : (no source object — new table)
-- TARGET   : inventory_stock.bronze.lineage_run
-- RULES    : LN-001, LN-002, OB-004, TY-017, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================

CREATE TABLE IF NOT EXISTS inventory_stock.bronze.lineage_run (
    lineage_key             BIGINT GENERATED ALWAYS AS IDENTITY  NOT NULL,
    etl_run_id              STRING                               NOT NULL,
    table_name              STRING                               NOT NULL,
    pipeline_name           STRING                               NOT NULL,
    data_load_started       TIMESTAMP                            NOT NULL,
    data_load_completed     TIMESTAMP                            NULL,
    was_successful          BOOLEAN                              NULL,
    table_row_count         BIGINT                               NULL,
    source_system_cutoff_time TIMESTAMP                          NOT NULL,

    CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)
)
USING DELTA
TBLPROPERTIES (
    'delta.enableChangeDataFeed'          = 'true',
    'delta.autoOptimize.optimizeWrite'    = 'true'
);
