-- TASK-ENV-001: Provision Unity Catalog namespaces and schemas
-- Target catalog: globalsales
-- Idempotent — safe to re-run

-- Create catalog if not present
CREATE CATALOG IF NOT EXISTS globalsales
COMMENT 'GlobalSales data product catalog';

-- Set catalog owner to designated service principal
-- TODO: CX-P05 — replace placeholder with confirmed SP identity
-- ALTER CATALOG globalsales OWNER TO `{{UC_ROLE_SERVICE_PRINCIPAL}}`;

USE CATALOG globalsales;

-- Bronze staging schema
CREATE SCHEMA IF NOT EXISTS globalsales.stg
COMMENT 'Bronze staging layer — incremental landing, lineage, DQ bookkeeping';

-- Silver dimension schema
CREATE SCHEMA IF NOT EXISTS globalsales.dim
COMMENT 'Silver dimension layer — SCD2 conformed dimensions';

-- Silver fact schema
CREATE SCHEMA IF NOT EXISTS globalsales.fact
COMMENT 'Silver fact layer — sales and order fact tables';

-- Gold mart schema
CREATE SCHEMA IF NOT EXISTS globalsales.mart
COMMENT 'Gold mart layer — aggregated analytical views for BI consumption';

-- Schema ownership — [PENDING: CX-P05] finalise before production
-- ALTER SCHEMA globalsales.stg  OWNER TO `{{UC_ROLE_SERVICE_PRINCIPAL}}`;
-- ALTER SCHEMA globalsales.dim  OWNER TO `{{UC_ROLE_SERVICE_PRINCIPAL}}`;
-- ALTER SCHEMA globalsales.fact OWNER TO `{{UC_ROLE_SERVICE_PRINCIPAL}}`;
-- ALTER SCHEMA globalsales.mart OWNER TO `{{UC_ROLE_SERVICE_PRINCIPAL}}`;

-- Verify schemas exist
SHOW SCHEMAS IN globalsales;
