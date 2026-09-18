# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/common/constants.py
# Purpose  : Centralised fully-qualified table name constants for Purchase ETL
# Rules    : NFR-009, NFR-011, CX-P004, NM-001

CATALOG            = "inventory_stock"
BRONZE_SCHEMA      = f"{CATALOG}.bronze"
SILVER_DIM_SCHEMA  = f"{CATALOG}.silver_dim"
SILVER_FACT_SCHEMA = f"{CATALOG}.silver_fact"

PURCHASE_STAGING_TABLE = f"{BRONZE_SCHEMA}.purchase_staging"
ETL_CUTOFF_TABLE       = f"{BRONZE_SCHEMA}.etl_cutoff"
LINEAGE_RUN_TABLE      = f"{BRONZE_SCHEMA}.lineage_run"
DQ_REJECTIONS_TABLE    = f"{BRONZE_SCHEMA}.dq_rejections"

SUPPLIER_DIM_TABLE    = f"{SILVER_DIM_SCHEMA}.supplier"
STOCK_ITEM_DIM_TABLE  = f"{SILVER_DIM_SCHEMA}.stock_item"
DATE_DIM_TABLE        = f"{SILVER_DIM_SCHEMA}.date"
FACT_PURCHASE_TABLE   = f"{SILVER_FACT_SCHEMA}.fact_purchase"

ETL_CUTOFF_TABLE_NAME = "fact_purchase"
