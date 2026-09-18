# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/init/reseed_purchase_environment.py
# Purpose  : Environment initialisation notebook.
#            Creates all required Bronze and Silver tables if they do not
#            exist, inserts sentinel (key=0) rows into the dimension tables,
#            and resets the ETL watermark to initial_load_date from config.
# Rules    : FR-011, OB-P001
#
# WARNING  : ################################################################
#            REQUIRES EXPLICIT SCOPE-OWNER SIGN-OFF (PD-002) BEFORE
#            EXECUTION IN PRODUCTION.  Running this notebook against a live
#            production environment will reset the ETL watermark and may
#            cause duplicate or re-processed loads.  Always obtain written
#            approval from the designated scope owner and execute only in a
#            controlled change-management window.
#            ################################################################
# =============================================================================

import yaml
import logging

with open("config/environment.yaml") as f:
    cfg = yaml.safe_load(f)

INITIAL_LOAD_DATE = cfg["purchase"]["etl"]["initial_load_date"]

logger = logging.getLogger(__name__)
logger.info("reseed_purchase_environment started")

# =============================================================================
# STEP 1: CREATE BRONZE TABLES (FR-011, OB-P001)
# All DDL uses CREATE TABLE IF NOT EXISTS / CREATE OR REPLACE VIEW so the
# notebook is safely re-runnable without risk of overwriting existing data.
# =============================================================================

# --- bronze.purchase_staging -------------------------------------------------
spark.sql("""
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
    )
""")
logger.info("Ensured table: inventory_stock.bronze.purchase_staging")

# --- bronze.lineage_run ------------------------------------------------------
spark.sql("""
    CREATE TABLE IF NOT EXISTS inventory_stock.bronze.lineage_run (
        lineage_key               BIGINT    GENERATED ALWAYS AS IDENTITY  NOT NULL,
        etl_run_id                STRING                                   NOT NULL,
        table_name                STRING                                   NOT NULL,
        pipeline_name             STRING                                   NOT NULL,
        data_load_started         TIMESTAMP                                NOT NULL,
        data_load_completed       TIMESTAMP                                NULL,
        was_successful            BOOLEAN                                  NULL,
        table_row_count           BIGINT                                   NULL,
        source_system_cutoff_time TIMESTAMP                                NOT NULL,
        CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)
    )
    USING DELTA
    TBLPROPERTIES (
        'delta.enableChangeDataFeed'       = 'true',
        'delta.autoOptimize.optimizeWrite' = 'true'
    )
""")
logger.info("Ensured table: inventory_stock.bronze.lineage_run")

# --- bronze.etl_cutoff -------------------------------------------------------
spark.sql("""
    CREATE TABLE IF NOT EXISTS inventory_stock.bronze.etl_cutoff (
        table_name       STRING     NOT NULL,
        cutoff_time      TIMESTAMP  NOT NULL,
        last_updated_utc TIMESTAMP  NOT NULL
    )
    USING DELTA
""")
logger.info("Ensured table: inventory_stock.bronze.etl_cutoff")

# --- bronze.dq_rejections ----------------------------------------------------
spark.sql("""
    CREATE TABLE IF NOT EXISTS inventory_stock.bronze.dq_rejections (
        rejection_id     BIGINT     GENERATED ALWAYS AS IDENTITY  NOT NULL,
        lineage_key      BIGINT     NOT NULL,
        rule_id          STRING     NOT NULL,
        source_table     STRING     NOT NULL,
        pk_column        STRING     NOT NULL,
        pk_value         STRING     NOT NULL,
        violation_column STRING     NOT NULL,
        violation_value  STRING     NULL,
        rejection_reason STRING     NOT NULL,
        detected_at      TIMESTAMP  NOT NULL DEFAULT current_timestamp()
    )
    USING DELTA
    TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true')
""")
logger.info("Ensured table: inventory_stock.bronze.dq_rejections")

# =============================================================================
# STEP 2: CREATE SILVER DIMENSION AND FACT TABLES (FR-011, OB-P001)
# =============================================================================

# --- silver_dim.supplier -----------------------------------------------------
spark.sql("""
    CREATE TABLE IF NOT EXISTS inventory_stock.silver_dim.supplier (
        supplier_key      BIGINT   GENERATED ALWAYS AS IDENTITY  NOT NULL,
        wwi_supplier_id   INT                                     NOT NULL,
        supplier          STRING                                  NOT NULL,
        is_current_row    BOOLEAN                                 NOT NULL,
        valid_from        DATE                                    NOT NULL,
        valid_to          DATE                                    NOT NULL,
        row_effective_date DATE                                   NOT NULL,
        row_expiry_date   DATE                                    NOT NULL,
        lineage_key       BIGINT                                  NOT NULL
    )
    USING DELTA
    TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true')
""")
logger.info("Ensured table: inventory_stock.silver_dim.supplier")

# --- silver_dim.supplier_current (view) --------------------------------------
spark.sql("""
    CREATE OR REPLACE VIEW inventory_stock.silver_dim.supplier_current AS
    SELECT *
    FROM   inventory_stock.silver_dim.supplier
    WHERE  is_current_row = TRUE
""")
logger.info("Ensured view: inventory_stock.silver_dim.supplier_current")

# --- silver_dim.stock_item ---------------------------------------------------
spark.sql("""
    CREATE TABLE IF NOT EXISTS inventory_stock.silver_dim.stock_item (
        stock_item_key    BIGINT   GENERATED ALWAYS AS IDENTITY  NOT NULL,
        wwi_stock_item_id INT                                     NOT NULL,
        stock_item        STRING                                  NOT NULL,
        is_current_row    BOOLEAN                                 NOT NULL,
        valid_from        DATE                                    NOT NULL,
        valid_to          DATE                                    NOT NULL,
        row_effective_date DATE                                   NOT NULL,
        row_expiry_date   DATE                                    NOT NULL,
        lineage_key       BIGINT                                  NOT NULL
    )
    USING DELTA
    TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true')
""")
logger.info("Ensured table: inventory_stock.silver_dim.stock_item")

# --- silver_dim.stock_item_current (view) ------------------------------------
spark.sql("""
    CREATE OR REPLACE VIEW inventory_stock.silver_dim.stock_item_current AS
    SELECT *
    FROM   inventory_stock.silver_dim.stock_item
    WHERE  is_current_row = TRUE
""")
logger.info("Ensured view: inventory_stock.silver_dim.stock_item_current")

# --- silver_fact.fact_purchase -----------------------------------------------
spark.sql("""
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
    )
    USING DELTA
    CLUSTER BY (date_key, supplier_key)
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact'   = 'true'
    )
""")
logger.info("Ensured table: inventory_stock.silver_fact.fact_purchase")

# =============================================================================
# STEP 3: INSERT SENTINEL ROW — silver_dim.supplier (key=0)
# (OB-P001, DQR-009)
# Inserts the unknown/unresolved sentinel row (supplier_key=0) only when it
# does not already exist, making this block safely idempotent.
# =============================================================================
spark.sql("""
    INSERT INTO inventory_stock.silver_dim.supplier
        (supplier_key, wwi_supplier_id, supplier, is_current_row, valid_from, valid_to,
         row_effective_date, row_expiry_date, lineage_key)
    SELECT 0, 0, 'Unknown', TRUE,
           CAST('1900-01-01' AS DATE), CAST('9999-12-31' AS DATE),
           CAST('1900-01-01' AS DATE), CAST('9999-12-31' AS DATE), 0
    WHERE NOT EXISTS (
        SELECT 1 FROM inventory_stock.silver_dim.supplier WHERE supplier_key = 0
    )
""")
logger.info("Sentinel row (supplier_key=0) ensured in silver_dim.supplier")

# =============================================================================
# STEP 4: INSERT SENTINEL ROW — silver_dim.stock_item (key=0)
# (OB-P001, DQR-009)
# =============================================================================
spark.sql("""
    INSERT INTO inventory_stock.silver_dim.stock_item
        (stock_item_key, wwi_stock_item_id, stock_item, is_current_row, valid_from, valid_to,
         row_effective_date, row_expiry_date, lineage_key)
    SELECT 0, 0, 'Unknown', TRUE,
           CAST('1900-01-01' AS DATE), CAST('9999-12-31' AS DATE),
           CAST('1900-01-01' AS DATE), CAST('9999-12-31' AS DATE), 0
    WHERE NOT EXISTS (
        SELECT 1 FROM inventory_stock.silver_dim.stock_item WHERE stock_item_key = 0
    )
""")
logger.info("Sentinel row (stock_item_key=0) ensured in silver_dim.stock_item")

# =============================================================================
# STEP 5: RESET ETL CUTOFF TO initial_load_date (FR-011, OB-P001)
# Overwrites (or inserts) the watermark row for fact_purchase so the next
# pipeline run performs a full-history reload from initial_load_date.
# =============================================================================
spark.sql(f"""
    MERGE INTO inventory_stock.bronze.etl_cutoff AS t
    USING (
        SELECT
            'fact_purchase'                         AS table_name,
            CAST('{INITIAL_LOAD_DATE}' AS TIMESTAMP) AS cutoff_time,
            current_timestamp()                      AS last_updated_utc
    ) AS s
    ON t.table_name = s.table_name
    WHEN MATCHED THEN UPDATE SET
        t.cutoff_time      = s.cutoff_time,
        t.last_updated_utc = s.last_updated_utc
    WHEN NOT MATCHED THEN INSERT *
""")
logger.info(
    f"ETL cutoff for 'fact_purchase' reset to initial_load_date='{INITIAL_LOAD_DATE}'"
)

logger.info("reseed_purchase_environment completed successfully")
print(
    f"Environment seeded. "
    f"All tables created (IF NOT EXISTS). "
    f"Sentinel rows inserted (if absent). "
    f"ETL cutoff reset to '{INITIAL_LOAD_DATE}'."
)
