# Sales_Orders — Implementation Tasks
_Generated: 2026-06-05 | Pipeline stage: tasks_

---

## Overview

| Task Group | Group ID | Task Count | Estimated Effort |
|---|---|---|---|
| 1: Environment & Infrastructure Setup | ENV | 4 | 1.0 day |
| 2: Database Layer — Schema Creation (DDL) | DB | 12 | 2.5 days |
| 3: Ingestion Pipeline | ING | 5 | 2.0 days |
| 4: Dimension Load Pipeline | DIM | 8 | 3.5 days |
| 5: Fact Load Pipeline | FACT | 5 | 2.5 days |
| 6: Gold / Mart Layer | MART | 6 | 2.0 days |
| 7: Data Quality Framework | DQ | 5 | 2.0 days |
| 8: Orchestration & Workflow | ORC | 4 | 1.5 days |
| 9: Security & Governance | SEC | 5 | 1.5 days |
| 10: Testing & Validation | TEST | 8 | 3.0 days |
| 11: Documentation & Handoff | DOCS | 4 | 1.0 days |
| **Total** | | **66** | **22.5 days** |

---

## Task Group 1: Environment & Infrastructure Setup

### TASK-ENV-001: Provision Unity Catalog namespaces and schemas
- **ID:** TASK-ENV-001
- **Group:** 1 — Environment & Infrastructure Setup
- **Type:** config
- **Priority:** critical
- **Depends on:** none
- **Implements:** FR-ORC, CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/uc_setup.sql`
- **Description:** Create the `globalsales` catalog (if not present) and all required schemas: `stg`, `dim`, `fact`, `mart`. Apply catalog-level owner and default permissions. [PENDING: CX-P05] Unity Catalog access role matrix must be confirmed before final grants are applied.
- **Acceptance criteria:**
  - All four schemas (`stg`, `dim`, `fact`, `mart`) exist in `globalsales` catalog
  - Schema ownership is set to the designated service principal
  - Script is idempotent (re-runnable without errors)
  - No pre-existing objects are dropped by this script

---

### TASK-ENV-002: Configure Databricks Secrets for source credentials
- **ID:** TASK-ENV-002
- **Group:** 1 — Environment & Infrastructure Setup
- **Type:** config
- **Priority:** critical
- **Depends on:** none
- **Implements:** FR-ING, CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/secrets_setup.md`
  - `products/Sales_Orders/current/codebase/config/secrets_config.py`
- **Description:** Document and implement the Databricks Secrets scope and key naming conventions for source OLTP connection strings, service principal credentials, and any external API keys. The `secrets_config.py` module provides a single access point (`get_secret(scope, key)`) used by all notebooks. [PENDING: CX-P04] OLTP-direct connection strategy must be confirmed before secrets for OLTP credentials can be finalised.
- **Acceptance criteria:**
  - `secrets_config.py` module imports and returns secrets without hard-coding credentials
  - Secret scope name and key names are documented in `secrets_setup.md`
  - All notebooks reference secrets exclusively via this module
  - Secret access raises a clear error message when a key is missing

---

### TASK-ENV-003: Create shared constants and utility module
- **ID:** TASK-ENV-003
- **Group:** 1 — Environment & Infrastructure Setup
- **Type:** etl
- **Priority:** critical
- **Depends on:** none
- **Implements:** NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/common/constants.py`
  - `products/Sales_Orders/current/codebase/src/common/utils.py`
- **Description:** Define all externalised constants (`PROFIT_MARGIN_FACTOR=1.05`, catalog/schema names, watermark table references, batch size limits, date range defaults) in `constants.py`. Implement shared utility functions (logging helpers, DataFrame row-count assertions, timestamp formatters) in `utils.py`. These modules are imported by every pipeline notebook.
- **Acceptance criteria:**
  - `PROFIT_MARGIN_FACTOR` is defined as `1.05` in `constants.py`
  - Catalog and schema name constants eliminate all hard-coded strings in pipeline code
  - `utils.py` provides at minimum: `log_info()`, `assert_row_count()`, `get_current_utc_ts()`
  - Both modules have docstrings and pass `flake8` lint checks
  - Unit tests exist for every function in `utils.py`

---

### TASK-ENV-004: Initialise CI/CD pipeline configuration
- **ID:** TASK-ENV-004
- **Group:** 1 — Environment & Infrastructure Setup
- **Type:** config
- **Priority:** high
- **Depends on:** none
- **Implements:** NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/ci_cd_pipeline.yml`
  - `products/Sales_Orders/current/codebase/config/pytest.ini`
- **Description:** Define the CI/CD pipeline (GitHub Actions or Azure DevOps YAML) that runs `pytest` with 80% coverage gate, `flake8` lint, and deploys notebooks to Databricks on merge to main. `pytest.ini` configures test discovery paths, coverage source, and minimum coverage threshold.
- **Acceptance criteria:**
  - Pipeline triggers on pull request and merge-to-main
  - `pytest` step enforces `--cov-fail-under=80`
  - `flake8` step fails the build on any error
  - Databricks notebook deployment step uses service principal credentials from secrets
  - Pipeline YAML is valid and parses without errors

---

## Task Group 2: Database Layer — Schema Creation (DDL)

### TASK-DB-001: DDL — Bronze staging and control tables
- **ID:** TASK-DB-001
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** critical
- **Depends on:** TASK-ENV-001
- **Implements:** FR-ING, FR-LIN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/stg_lineage.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/stg_etl_cutoff.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/stg_sale_staging.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/stg_order_staging.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/stg_dq_rejections.sql`
- **Description:** Create all five Bronze-layer Delta tables in `globalsales.stg`. `stg.lineage` records pipeline run metadata and provides `lineage_key` stamped on every downstream row. `stg.etl_cutoff` stores the high-watermark per source table for incremental extraction. `stg.sale_staging` and `stg.order_staging` are truncate-before-load landing tables. `stg.dq_rejections` captures DQ-failed rows with rejection reason and run context.
- **Acceptance criteria:**
  - All five tables are created in `globalsales.stg` as Delta format
  - `stg.lineage` has columns: `lineage_key` (BIGINT IDENTITY), `pipeline_name`, `run_id`, `started_at`, `finished_at`, `rows_extracted`, `rows_loaded`
  - `stg.etl_cutoff` has columns: `source_table` (PK), `last_cutoff_ts`, `updated_at`
  - `stg.dq_rejections` has columns: `rejection_id` (BIGINT IDENTITY), `source_table`, `row_data` (STRING), `rejection_reason`, `assertion_id`, `lineage_key`, `rejected_at`
  - All DDL scripts are idempotent (`CREATE TABLE IF NOT EXISTS`)

---

### TASK-DB-002: DDL — dim.customer (PII masking)
- **ID:** TASK-DB-002
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** critical
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN, CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_customer.sql`
  - `products/Sales_Orders/current/codebase/src/db/grants/dim_customer_grants.sql`
- **Description:** Create `globalsales.dim.customer` as a Delta SCD2 table with `customer_key` (BIGINT IDENTITY PK), surrogate/natural key columns, SCD2 control columns (`effective_date`, `expiry_date`, `is_current`), and PII-bearing columns (`customer_name`, `postal_code`, `phone_number`) designated for Unity Catalog column masks. `dim_customer_grants.sql` applies column-mask functions and row-level security policies. [PENDING: CX-P05] Role matrix required for grant targets.
- **Acceptance criteria:**
  - Table created in `globalsales.dim` as Delta format with SCD2 control columns
  - PII columns (`customer_name`, `postal_code`, `phone_number`) have column mask function references defined
  - `is_current` flag and `expiry_date` support active-row filtering
  - DDL is idempotent
  - Grant script references [PENDING: CX-P05] roles with a clear TODO comment

---

### TASK-DB-003: DDL — dim.city
- **ID:** TASK-DB-003
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** high
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_city.sql`
- **Description:** Create `globalsales.dim.city` as a Delta SCD2 table. Implement geo decomposition columns: `city_name`, `state_province`, `country`, `sales_territory`, `region`, `subregion`, `latest_recorded_population`, `last_census_year`. Include SCD2 control columns and `city_key` (BIGINT IDENTITY PK).
- **Acceptance criteria:**
  - Table created with all geo decomposition columns
  - SCD2 control columns present (`effective_date`, `expiry_date`, `is_current`)
  - `city_key` is BIGINT IDENTITY
  - DDL is idempotent

---

### TASK-DB-004: DDL — dim.stock_item
- **ID:** TASK-DB-004
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** high
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_stock_item.sql`
- **Description:** Create `globalsales.dim.stock_item` as a Delta SCD2 table with `stock_item_key` (BIGINT IDENTITY PK), natural key `stock_item_id`, descriptive attributes (name, color, size, brand, supplier), pricing attributes, and SCD2 control columns.
- **Acceptance criteria:**
  - Table created with pricing and descriptive attribute columns
  - SCD2 control columns present
  - DDL is idempotent

---

### TASK-DB-005: DDL — dim.employee
- **ID:** TASK-DB-005
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** high
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_employee.sql`
- **Description:** Create `globalsales.dim.employee` as a Delta SCD2 table with `employee_key` (BIGINT IDENTITY PK), natural key `employee_id`, `full_name`, `preferred_name`, `is_salesperson`, `primary_sales_territory` and SCD2 control columns.
- **Acceptance criteria:**
  - Table created with all required attribute columns
  - SCD2 control columns present
  - DDL is idempotent

---

### TASK-DB-006: DDL — dim.date (SCD0)
- **ID:** TASK-DB-006
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** high
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_date.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_date_populate.sql`
- **Description:** Create `globalsales.dim.date` as a Delta SCD0 (static) table with `date_key` (INT PK, YYYYMMDD), `calendar_date`, `day_of_week`, `day_name`, `month`, `month_name`, `quarter`, `year`, `is_weekend`, `fiscal_year`, `fiscal_quarter`. Populate from 2013-01-01 to a rolling 5-year future horizon.
- **Acceptance criteria:**
  - Table created with all calendar and fiscal columns
  - No SCD2 control columns (SCD0 — no changes tracked)
  - Population script inserts dates from 2013-01-01 onward
  - `date_key` matches YYYYMMDD integer format for all rows
  - Script is idempotent (uses MERGE or INSERT WHERE NOT EXISTS)

---

### TASK-DB-007: DDL — dim.payment_method and dim.transaction_type
- **ID:** TASK-DB-007
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** medium
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_payment_method.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/dim_transaction_type.sql`
- **Description:** Create `globalsales.dim.payment_method` and `globalsales.dim.transaction_type` as Delta SCD2 tables. Each has a surrogate key (BIGINT IDENTITY PK), natural key, descriptive attributes, and SCD2 control columns.
- **Acceptance criteria:**
  - Both tables created in `globalsales.dim` as Delta format
  - SCD2 control columns present on both
  - DDL scripts are idempotent

---

### TASK-DB-008: DDL — fact.sale
- **ID:** TASK-DB-008
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** critical
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/fact_sale.sql`
- **Description:** Create `globalsales.fact.sale` as a Delta table with `sale_key` (BIGINT IDENTITY PK), all dimension foreign keys (`customer_key`, `city_key`, `stock_item_key`, `employee_key`, `invoice_date_key`, `delivery_date_key`, `payment_method_key`, `transaction_type_key`), measures (`quantity`, `unit_price`, `tax_rate`, `total_excluding_tax`, `tax_amount`, `total_including_tax`, `profit`, `total_dry_items`, `total_chiller_items`), `lineage_key`, and `last_edited_when`. Apply liquid clustering on `invoice_date_key`, `customer_key`, `stock_item_key`.
- **Acceptance criteria:**
  - Table created with all FK and measure columns
  - `sale_key` is BIGINT IDENTITY
  - Liquid clustering defined on `invoice_date_key`, `customer_key`, `stock_item_key`
  - `lineage_key` and `last_edited_when` columns present
  - DDL is idempotent

---

### TASK-DB-009: DDL — fact.order
- **ID:** TASK-DB-009
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** critical
- **Depends on:** TASK-ENV-001
- **Implements:** FR-TRN, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/fact_order.sql`
- **Description:** Create `globalsales.fact.order` as a Delta table with `order_key` (BIGINT IDENTITY PK), dimension FKs (`customer_key`, `city_key`, `stock_item_key`, `order_date_key`, `picked_date_key`, `salesperson_key`), measures (`quantity`, `unit_price`, `tax_rate`, `total_excluding_tax`, `tax_amount`, `total_including_tax`, `is_undersupply_backordered`), `lineage_key`, and `last_edited_when`. Apply PARTITION BY `order_date_key` and ZORDER BY `customer_key`, `stock_item_key`.
- **Acceptance criteria:**
  - Table created with all FK and measure columns
  - `order_key` is BIGINT IDENTITY
  - Partition and ZORDER optimizations defined in DDL
  - `lineage_key` and `last_edited_when` columns present
  - DDL is idempotent

---

### TASK-DB-010: DDL — mart views (4 views)
- **ID:** TASK-DB-010
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** high
- **Depends on:** TASK-DB-008, TASK-DB-009, TASK-DB-002, TASK-DB-003, TASK-DB-004
- **Implements:** FR-SRV, IFR-BI-001..009
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/mart_v_customer_sales_summary.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/mart_v_order_details.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/mart_v_order_to_supply_analytics.sql`
  - `products/Sales_Orders/current/codebase/src/db/ddl/mart_v_order_to_year_analytics.sql`
- **Description:** Create all four mart views in `globalsales.mart`. `v_customer_sales_summary` is a materialized view joining `fact.sale` to dimension tables and computing `profit_margin_with_factor` using `PROFIT_MARGIN_FACTOR=1.05` from `constants.py`. `v_order_details` accepts `:start_date` parameter. `v_order_to_supply_analytics` joins orders to stock supply context. `v_order_to_year_analytics` accepts `:window_days` (default 100) for rolling window aggregation.
- **Acceptance criteria:**
  - All four views created in `globalsales.mart`
  - `v_customer_sales_summary` includes `profit_margin_with_factor` column computed with factor 1.05
  - `v_order_details` filters by `:start_date` parameter
  - `v_order_to_year_analytics` defaults `:window_days` to 100 when not supplied
  - All views are queryable end-to-end with sample data

---

### TASK-DB-011: DDL — fact.get_total_quantity_sold (SQL UDF)
- **ID:** TASK-DB-011
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** medium
- **Depends on:** TASK-DB-008
- **Implements:** FR-SRV
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/fact_udf_get_total_quantity_sold.sql`
- **Description:** Create the SQL UDF `globalsales.fact.get_total_quantity_sold(p_stock_item_key BIGINT, p_start_date DATE, p_end_date DATE) RETURNS BIGINT`. The function queries `fact.sale` filtered by `stock_item_key` and invoice date range, using `COALESCE(SUM(quantity), 0)` to guard against NULL when no rows match, returning 0 rather than NULL.
- **Acceptance criteria:**
  - UDF created in `globalsales.fact` schema
  - Function signature accepts `p_stock_item_key BIGINT`, `p_start_date DATE`, `p_end_date DATE`
  - `COALESCE` NULL guard is present on both parameter and aggregate result — function returns 0 (not NULL) when no rows match
  - UDF is callable from mart views and notebooks
  - DDL is idempotent (`CREATE OR REPLACE FUNCTION`)

---

### TASK-DB-012: DDL — column mask functions for PII
- **ID:** TASK-DB-012
- **Group:** 2 — Database Layer — Schema Creation (DDL)
- **Type:** db
- **Priority:** critical
- **Depends on:** TASK-ENV-001
- **Implements:** CON-SEC-001, FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/ddl/uc_column_masks.sql`
- **Description:** Define Unity Catalog column mask functions for PII columns on `dim.customer`: `mask_customer_name()`, `mask_postal_code()`, `mask_phone_number()`. Each function returns the unmasked value for principals holding the `pii_viewer` role and a masked/redacted value for all others. [PENDING: CX-P05] Exact role names subject to access role matrix approval.
- **Acceptance criteria:**
  - Three column mask functions created in `globalsales` catalog
  - Each function checks caller's membership in the PII viewer role
  - Masked output for non-privileged callers is deterministic (e.g., `'***REDACTED***'`)
  - Functions referenced by `TASK-DB-002` grant script
  - Script is idempotent (`CREATE OR REPLACE`)

---

## Task Group 3: Ingestion Pipeline

### TASK-ING-001: Watermark extraction notebook
- **ID:** TASK-ING-001
- **Group:** 3 — Ingestion Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-DB-001, TASK-ENV-002, TASK-ENV-003
- **Implements:** FR-ING
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/ingestion/nb_extract_watermark.py`
- **Description:** Notebook that reads the current high-watermark per source table from `stg.etl_cutoff`, determines the extraction window (`last_cutoff_ts` to `current_ts`), and returns the window bounds as notebook widgets/outputs for downstream notebooks. Handles the case where no prior cutoff exists (full-load bootstrap from 2013-01-01). [PENDING: CX-P04] OLTP connection method TBD.
- **Acceptance criteria:**
  - Reads watermark from `stg.etl_cutoff` for each configured source table
  - Returns `extract_start_ts` and `extract_end_ts` as outputs
  - Bootstraps to 2013-01-01 when no prior watermark exists
  - Does not update `stg.etl_cutoff` (update handled post-load)
  - Unit-testable watermark logic is isolated to a pure Python function

---

### TASK-ING-002: Sale source extraction notebook
- **ID:** TASK-ING-002
- **Group:** 3 — Ingestion Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-ING-001, TASK-DB-001
- **Implements:** FR-ING, FR-LIN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/ingestion/nb_extract_sales.py`
- **Description:** Notebook that extracts sale records from the source system within the watermark window, truncates `stg.sale_staging`, loads extracted rows, and stamps `lineage_key` from `stg.lineage`. Implements truncate-before-load pattern for idempotency. [PENDING: CX-P04] Source connection method (JDBC OLTP-direct vs. extract file) must be confirmed before final implementation.
- **Acceptance criteria:**
  - Truncates `stg.sale_staging` before every load
  - Extracts only rows where source `last_edited_when` is within the watermark window
  - Stamps `lineage_key` on every loaded row
  - Row count written to `stg.lineage` entry
  - Handles zero-row extracts gracefully (no error, logs warning)

---

### TASK-ING-003: Order source extraction notebook
- **ID:** TASK-ING-003
- **Group:** 3 — Ingestion Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-ING-001, TASK-DB-001
- **Implements:** FR-ING, FR-LIN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/ingestion/nb_extract_orders.py`
- **Description:** Notebook that extracts order records from the source system within the watermark window, truncates `stg.order_staging`, loads extracted rows, and stamps `lineage_key`. Mirrors the pattern of `nb_extract_sales.py` for the orders domain. [PENDING: CX-P04] Source connection method must be confirmed.
- **Acceptance criteria:**
  - Truncates `stg.order_staging` before every load
  - Extracts rows within the watermark window with `lineage_key` stamped
  - Row count written to `stg.lineage`
  - Zero-row extracts handled gracefully
  - Notebook parameters are consistent with `nb_extract_sales.py` for orchestration uniformity

---

### TASK-ING-004: Dimension source extraction notebook
- **ID:** TASK-ING-004
- **Group:** 3 — Ingestion Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-ING-001, TASK-DB-001
- **Implements:** FR-ING, FR-LIN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/ingestion/nb_extract_dimensions.py`
- **Description:** Notebook that extracts changed dimension source records (customers, cities, stock items, employees, payment methods, transaction types) within the watermark window into transient staging DataFrames held in memory (or temp views). Dimension changes are small volume and do not require dedicated staging tables — they feed directly into SCD2 merge notebooks. [PENDING: CX-P04] Source connection method TBD.
- **Acceptance criteria:**
  - Extracts dimension changes for all six SCD2 sources within the watermark window
  - Creates named temp views or persists to checkpoint path for downstream SCD2 notebooks
  - Stamps `lineage_key` on each extracted DataFrame
  - Source table list is driven by configuration (not hard-coded)
  - Zero-change extracts log a warning but do not fail

---

### TASK-ING-005: Watermark commit notebook
- **ID:** TASK-ING-005
- **Group:** 3 — Ingestion Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-ING-002, TASK-ING-003, TASK-ING-004
- **Implements:** FR-ING
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/ingestion/nb_commit_watermark.py`
- **Description:** Notebook executed after all extractions succeed. Updates `stg.etl_cutoff` for each source table to the `extract_end_ts` of the current run. This is the idempotency guard — if any upstream notebook fails, the watermark is not advanced, ensuring the next run re-extracts the same window.
- **Acceptance criteria:**
  - Updates `stg.etl_cutoff.last_cutoff_ts` for each source table to `extract_end_ts`
  - Only runs when called explicitly by the orchestration workflow (not as part of extraction notebooks)
  - Update is atomic (single MERGE statement per table)
  - Previous watermark value is logged before update for auditability

---

## Task Group 4: Dimension Load Pipeline

### TASK-DIM-001: SCD2 shared merge utility
- **ID:** TASK-DIM-001
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-ENV-003
- **Implements:** FR-TRN, NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/scd2_merge.py`
- **Description:** Implement a reusable Python function `apply_scd2_merge(spark, target_table, source_df, natural_key_cols, tracked_cols, effective_date_col, lineage_key)` that encapsulates the two-step SCD2 pattern: (1) MERGE INTO to expire existing active rows where tracked columns have changed, (2) MERGE INTO to insert new active rows for changed/new records. All dimension notebooks call this function rather than duplicating MERGE logic.
- **Acceptance criteria:**
  - Function correctly expires rows by setting `expiry_date` and `is_current=False`
  - Function correctly inserts new rows with `effective_date=today`, `expiry_date=9999-12-31`, `is_current=True`
  - Function is idempotent — re-running with the same source produces no net change
  - `lineage_key` is stamped on all inserted rows
  - Unit tests cover: new record insert, changed record SCD2 split, unchanged record no-op, multi-key natural keys

---

### TASK-DIM-002: dim.customer load notebook
- **ID:** TASK-DIM-002
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-DIM-001, TASK-DB-002, TASK-ING-004
- **Implements:** FR-TRN, CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/nb_load_dim_customer.py`
- **Description:** Notebook that reads extracted customer source data, applies business transformations (name standardisation, address decomposition), and calls `apply_scd2_merge()` to load `globalsales.dim.customer`. PII columns (`customer_name`, `postal_code`, `phone_number`) are loaded as-is — masking is enforced at query time via Unity Catalog column masks (defined in TASK-DB-012).
- **Acceptance criteria:**
  - Calls `apply_scd2_merge()` with correct natural key and tracked columns
  - PII columns are present in the target table (masking applied at read, not at write)
  - `lineage_key` stamped on all inserted rows
  - Notebook is idempotent
  - At least one transformation (e.g., name standardisation) is unit-tested

---

### TASK-DIM-003: dim.city load notebook
- **ID:** TASK-DIM-003
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-DIM-001, TASK-DB-003, TASK-ING-004
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/nb_load_dim_city.py`
- **Description:** Notebook that reads extracted city source data, applies geo decomposition logic (splitting combined city/state fields into discrete columns: `city_name`, `state_province`, `country`, `sales_territory`, `region`, `subregion`), and calls `apply_scd2_merge()` to load `globalsales.dim.city`.
- **Acceptance criteria:**
  - Geo decomposition produces all six geographic attribute columns
  - `apply_scd2_merge()` called with correct keys
  - `lineage_key` stamped on all inserted rows
  - Notebook is idempotent
  - Geo decomposition logic is unit-tested

---

### TASK-DIM-004: dim.stock_item load notebook
- **ID:** TASK-DIM-004
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-DIM-001, TASK-DB-004, TASK-ING-004
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/nb_load_dim_stock_item.py`
- **Description:** Notebook that reads extracted stock item source data and calls `apply_scd2_merge()` to load `globalsales.dim.stock_item`. Handles NULL pricing attributes by substituting defaults from `constants.py`.
- **Acceptance criteria:**
  - `apply_scd2_merge()` called with correct natural key (`stock_item_id`) and tracked columns
  - NULL pricing attributes replaced with configured defaults
  - `lineage_key` stamped; notebook is idempotent

---

### TASK-DIM-005: dim.employee load notebook
- **ID:** TASK-DIM-005
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-DIM-001, TASK-DB-005, TASK-ING-004
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/nb_load_dim_employee.py`
- **Description:** Notebook that reads extracted employee source data, resolves `is_salesperson` flag, and calls `apply_scd2_merge()` to load `globalsales.dim.employee`.
- **Acceptance criteria:**
  - `apply_scd2_merge()` called with correct natural key and tracked columns
  - `is_salesperson` derived correctly from source data
  - `lineage_key` stamped; notebook is idempotent

---

### TASK-DIM-006: dim.payment_method and dim.transaction_type load notebook
- **ID:** TASK-DIM-006
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** medium
- **Depends on:** TASK-DIM-001, TASK-DB-007, TASK-ING-004
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/nb_load_dim_payment_transaction.py`
- **Description:** Single notebook that loads both `dim.payment_method` and `dim.transaction_type` by calling `apply_scd2_merge()` for each. These are low-cardinality, low-change-frequency dimensions that share a notebook for operational simplicity.
- **Acceptance criteria:**
  - Both dimensions loaded in sequence within the same notebook run
  - `apply_scd2_merge()` called independently for each dimension
  - `lineage_key` stamped on all inserted rows; notebook is idempotent

---

### TASK-DIM-007: dim.date population notebook
- **ID:** TASK-DIM-007
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-DB-006
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/nb_populate_dim_date.py`
- **Description:** Notebook that generates and inserts date dimension rows from 2013-01-01 to a rolling 5-year future horizon. SCD0 — no updates are applied, only inserts for dates not yet present. Computes all calendar and fiscal columns using vectorised PySpark date functions.
- **Acceptance criteria:**
  - Generates rows from 2013-01-01 to today + 5 years
  - Inserts only rows not already in `dim.date` (idempotent)
  - All calendar columns (`day_of_week`, `month`, `quarter`, etc.) populated correctly
  - Fiscal year/quarter computed per the configured fiscal year start month (externalised in `constants.py`)
  - `date_key` format matches YYYYMMDD integer

---

### TASK-DIM-008: Dimension load orchestration notebook
- **ID:** TASK-DIM-008
- **Group:** 4 — Dimension Load Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-DIM-002, TASK-DIM-003, TASK-DIM-004, TASK-DIM-005, TASK-DIM-006, TASK-DIM-007
- **Implements:** FR-ORC
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dimensions/nb_orchestrate_dimensions.py`
- **Description:** Orchestration notebook that invokes all dimension load notebooks in dependency order using `dbutils.notebook.run()`. Captures success/failure status for each dimension and raises an aggregate error if any dimension fails, halting the pipeline before fact loads begin.
- **Acceptance criteria:**
  - All seven dimension loads invoked in correct dependency order
  - Failure of any single dimension load halts subsequent dimension loads and fact loads
  - Per-dimension run status logged to `stg.lineage`
  - Notebook timeout per child call is configurable via `constants.py`

---

## Task Group 5: Fact Load Pipeline

### TASK-FACT-001: Fact merge shared utility
- **ID:** TASK-FACT-001
- **Group:** 5 — Fact Load Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-ENV-003
- **Implements:** FR-TRN, NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/facts/fact_merge.py`
- **Description:** Implement a reusable Python function `apply_fact_merge(spark, target_table, source_df, natural_key_cols, lineage_key, staleness_col='last_edited_when')` that performs a Delta MERGE INTO for fact tables. The merge uses a staleness guard: a source row updates the target only when `source.last_edited_when > target.last_edited_when`, preventing stale overwrites of more-recently-edited rows.
- **Acceptance criteria:**
  - Staleness guard (`last_edited_when` comparison) is applied in the MERGE condition
  - New rows (no target match) are inserted
  - Existing rows updated only when source is newer
  - `lineage_key` updated on all matched/updated rows
  - Unit tests cover: new insert, update with newer source, no-update with older source, identical timestamp no-update

---

### TASK-FACT-002: fact.sale load notebook
- **ID:** TASK-FACT-002
- **Group:** 5 — Fact Load Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-FACT-001, TASK-DB-008, TASK-DIM-008, TASK-ING-002
- **Implements:** FR-TRN, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/facts/nb_load_fact_sale.py`
- **Description:** Notebook that reads from `stg.sale_staging`, resolves dimension surrogate keys by joining to current active dimension rows (`is_current=True`), and calls `apply_fact_merge()` to load `globalsales.fact.sale`. Applies liquid clustering optimization after merge via `OPTIMIZE ... ZORDER` when the incremental row count exceeds a configurable threshold.
- **Acceptance criteria:**
  - All dimension FK lookups produce surrogate keys (no NULLs for valid source values)
  - `apply_fact_merge()` called with `last_edited_when` as staleness column
  - `lineage_key` stamped on all inserted/updated rows
  - `OPTIMIZE` triggered conditionally based on row count threshold from `constants.py`
  - Notebook completes within NFR-PERF budget (monitored via run metrics)

---

### TASK-FACT-003: fact.order load notebook
- **ID:** TASK-FACT-003
- **Group:** 5 — Fact Load Pipeline
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-FACT-001, TASK-DB-009, TASK-DIM-008, TASK-ING-003
- **Implements:** FR-TRN, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/facts/nb_load_fact_order.py`
- **Description:** Notebook that reads from `stg.order_staging`, resolves dimension surrogate keys, and calls `apply_fact_merge()` to load `globalsales.fact.order`. After merge, runs `OPTIMIZE ... ZORDER BY (customer_key, stock_item_key)` for the current partition (`order_date_key`) when row count exceeds the configured threshold.
- **Acceptance criteria:**
  - All dimension FK lookups produce surrogate keys
  - Staleness guard applied via `apply_fact_merge()`
  - Partition-scoped ZORDER executed after merge
  - `lineage_key` stamped; notebook is idempotent

---

### TASK-FACT-004: Surrogate key resolution utility
- **ID:** TASK-FACT-004
- **Group:** 5 — Fact Load Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-ENV-003
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/facts/sk_resolver.py`
- **Description:** Implement a reusable `resolve_surrogate_keys(spark, source_df, dim_table, natural_key_col, surrogate_key_col, join_type='left')` function used by fact load notebooks to look up surrogate keys from dimension tables. Returns the enriched DataFrame with surrogate key column appended and logs unresolved natural keys as warnings.
- **Acceptance criteria:**
  - Function performs `left` join by default (preserving unresolved rows as NULLs rather than dropping)
  - Unresolved rows (NULL surrogate key) are logged with count and sample natural key values
  - Function filters dimension to `is_current=True` rows before join
  - Unit tests cover: successful resolution, unresolved natural key, empty source DataFrame

---

### TASK-FACT-005: Fact load orchestration notebook
- **ID:** TASK-FACT-005
- **Group:** 5 — Fact Load Pipeline
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-FACT-002, TASK-FACT-003
- **Implements:** FR-ORC
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/facts/nb_orchestrate_facts.py`
- **Description:** Orchestration notebook that invokes `nb_load_fact_sale.py` and `nb_load_fact_order.py` (potentially in parallel using separate cluster pools if cluster policy allows), captures per-fact run status, and raises aggregate error on failure.
- **Acceptance criteria:**
  - Both fact loads invoked and monitored
  - Per-fact run status logged to `stg.lineage`
  - Aggregate error raised if either fact load fails
  - Parallel vs. sequential execution mode configurable via `constants.py`

---

## Task Group 6: Gold / Mart Layer

### TASK-MART-001: mart.v_customer_sales_summary materialized view refresh
- **ID:** TASK-MART-001
- **Group:** 6 — Gold / Mart Layer
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-DB-010, TASK-FACT-002
- **Implements:** FR-SRV, IFR-BI-001..009, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/mart/nb_refresh_v_customer_sales_summary.py`
- **Description:** Notebook that triggers refresh of the materialized view `mart.v_customer_sales_summary` post-fact-load. The view computes aggregated sales metrics per customer including `profit_margin_with_factor` (using `PROFIT_MARGIN_FACTOR=1.05` from `constants.py`). Validates that p95 query latency against the refreshed view meets the NFR-PERF ≤ 5s target using a sample benchmark query.
- **Acceptance criteria:**
  - Materialized view refresh completes without error
  - `profit_margin_with_factor` computed correctly using factor 1.05
  - Benchmark query against the view completes in ≤ 5 seconds (p95)
  - Refresh duration logged to `stg.lineage`

---

### TASK-MART-002: mart.v_order_details view validation notebook
- **ID:** TASK-MART-002
- **Group:** 6 — Gold / Mart Layer
- **Type:** etl
- **Priority:** medium
- **Depends on:** TASK-DB-010, TASK-FACT-003
- **Implements:** FR-SRV, IFR-BI-001..009
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/mart/nb_validate_mart_views.py`
- **Description:** Notebook that runs post-pipeline smoke tests against all four mart views to confirm they are queryable and return expected row counts. Tests `v_order_details` with a sample `:start_date`, `v_order_to_year_analytics` with default `:window_days=100` and a custom value, and `v_order_to_supply_analytics` with a sample filter. This notebook is also reused as part of the DQ framework (TASK-DQ-005).
- **Acceptance criteria:**
  - All four mart views queried without error
  - `v_order_details` returns rows for a supplied `:start_date`
  - `v_order_to_year_analytics` defaults to 100-day window when parameter not supplied
  - Row counts for each view are non-zero after a full pipeline run
  - Any view returning zero rows raises a warning (not a failure, as zero is valid post-bootstrap)

---

### TASK-MART-003: UDF smoke-test notebook
- **ID:** TASK-MART-003
- **Group:** 6 — Gold / Mart Layer
- **Type:** etl
- **Priority:** medium
- **Depends on:** TASK-DB-011, TASK-FACT-002
- **Implements:** FR-SRV
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/mart/nb_test_udf_qty_sold.py`
- **Description:** Notebook that exercises `fact.get_total_quantity_sold(p_stock_item_key, p_start_date, p_end_date)` with at least three test cases: (1) a known `stock_item_key` with sales in the date range returns the correct sum, (2) a non-existent `stock_item_key` returns 0 (not NULL — validating the COALESCE guard), (3) a NULL `stock_item_key` returns 0.
- **Acceptance criteria:**
  - Test case 1 returns the expected integer sum
  - Test case 2 returns `0` (not `NULL`)
  - Test case 3 returns `0` (not `NULL`)
  - All three assertions logged as pass/fail to `stg.lineage`

---

### TASK-MART-004: BI connection configuration and sample queries
- **ID:** TASK-MART-004
- **Group:** 6 — Gold / Mart Layer
- **Type:** docs
- **Priority:** medium
- **Depends on:** TASK-DB-010, TASK-DB-011
- **Implements:** IFR-BI-001..009, FR-SRV
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/bi_connections.md`
  - `products/Sales_Orders/current/codebase/src/db/queries/bi_sample_queries.sql`
- **Description:** Document Power BI connection strings (Unity Catalog SQL Warehouse endpoint), required SQL Warehouse cluster policy, and recommended Direct Query vs. Import mode for each of the 9 BI report connections (IFR-BI-001..009). Provide sample SQL for each mart view/UDF. [PENDING: CX-P05] Role matrix required for BI service account grants.
- **Acceptance criteria:**
  - All 9 BI report connections documented (IFR-BI-001..009)
  - Connection string template provided for Unity Catalog SQL Warehouse
  - Sample query provided for each of the 4 mart views and the UDF
  - NFR-PERF ≤ 5s p95 guidance noted for SQL Warehouse sizing

---

### TASK-MART-005: Grant mart layer read access
- **ID:** TASK-MART-005
- **Group:** 6 — Gold / Mart Layer
- **Type:** db
- **Priority:** high
- **Depends on:** TASK-DB-010, TASK-DB-011
- **Implements:** FR-SRV, CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/grants/mart_grants.sql`
- **Description:** Grant SELECT on all four mart views and EXECUTE on `fact.get_total_quantity_sold` to the designated BI service accounts and analyst roles. [PENDING: CX-P05] Exact role/group names subject to Unity Catalog access role matrix approval.
- **Acceptance criteria:**
  - SELECT granted on all four mart views
  - EXECUTE granted on UDF
  - Grant script is idempotent
  - [PENDING: CX-P05] placeholder clearly marked with TODO comment

---

### TASK-MART-006: Mart layer performance optimization notebook
- **ID:** TASK-MART-006
- **Group:** 6 — Gold / Mart Layer
- **Type:** etl
- **Priority:** medium
- **Depends on:** TASK-FACT-002, TASK-FACT-003
- **Implements:** NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/mart/nb_optimize_mart.py`
- **Description:** Notebook that runs post-load Delta `OPTIMIZE` and `ANALYZE` commands on `fact.sale` (liquid clustering) and `fact.order` (partition + ZORDER) to maintain query performance. Also runs `VACUUM` with the configured retention period. Scheduled as a weekly maintenance task independent of the nightly ETL.
- **Acceptance criteria:**
  - `OPTIMIZE` runs on both fact tables with correct clustering/ZORDER specifications
  - `VACUUM` runs with retention period from `constants.py` (not hard-coded)
  - `ANALYZE` runs on mart views to update statistics
  - Notebook is safe to run independently of the nightly ETL

---

## Task Group 7: Data Quality Framework

### TASK-DQ-001: DQ assertion engine
- **ID:** TASK-DQ-001
- **Group:** 7 — Data Quality Framework
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-ENV-003, TASK-DB-001
- **Implements:** DQR-AST-001..005, DQR-REJ, DQR-REC
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dq/dq_engine.py`
- **Description:** Implement the DQ assertion engine as a Python module with a class `DQEngine` that accepts a Spark DataFrame and a list of assertion configs. Runs all five standard assertions (DQR-AST-001: not-null checks, DQR-AST-002: referential integrity, DQR-AST-003: value range checks, DQR-AST-004: uniqueness checks, DQR-AST-005: format/regex checks) post-merge. Failing rows are routed to `stg.dq_rejections` (DQR-REJ). [PENDING: CX-DQ-01] Business DQ thresholds (acceptable failure rates) must be confirmed before assertions become hard failures vs. warnings.
- **Acceptance criteria:**
  - All five assertion types implemented (DQR-AST-001..005)
  - Failing rows written to `stg.dq_rejections` with `assertion_id`, `rejection_reason`, `lineage_key`
  - Passing rows returned as a clean DataFrame for downstream use
  - Assertion configs are externalised (YAML or dict) — not hard-coded in the engine
  - [PENDING: CX-DQ-01] threshold logic has a clear TODO and defaults to zero-tolerance

---

### TASK-DQ-002: DQ assertions notebook — fact.sale
- **ID:** TASK-DQ-002
- **Group:** 7 — Data Quality Framework
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-DQ-001, TASK-FACT-002
- **Implements:** DQR-AST-001..005, DQR-REC
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dq/nb_dq_fact_sale.py`
  - `products/Sales_Orders/current/codebase/config/dq_assertions_fact_sale.yaml`
- **Description:** Notebook that runs `DQEngine` against `fact.sale` post-merge with the five configured assertions. Performs zero-tolerance row count reconciliation (DQR-REC): compares row count in `stg.sale_staging` against rows successfully merged into `fact.sale` for the current `lineage_key` and raises an error if there is any discrepancy. [PENDING: CX-DQ-01] Business thresholds TBD.
- **Acceptance criteria:**
  - All five assertions run against `fact.sale` post-merge
  - Zero-tolerance reconciliation: staging count equals fact count for current `lineage_key`
  - Any reconciliation discrepancy raises a pipeline-halting error
  - Rejected rows written to `stg.dq_rejections` with full context
  - Assertion results summary written to `stg.lineage`

---

### TASK-DQ-003: DQ assertions notebook — fact.order
- **ID:** TASK-DQ-003
- **Group:** 7 — Data Quality Framework
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-DQ-001, TASK-FACT-003
- **Implements:** DQR-AST-001..005, DQR-REC
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dq/nb_dq_fact_order.py`
  - `products/Sales_Orders/current/codebase/config/dq_assertions_fact_order.yaml`
- **Description:** Notebook that runs `DQEngine` against `fact.order` post-merge and performs zero-tolerance row count reconciliation against `stg.order_staging` for the current `lineage_key`. Mirrors the pattern of `nb_dq_fact_sale.py`. [PENDING: CX-DQ-01] Business thresholds TBD.
- **Acceptance criteria:**
  - All five assertions run against `fact.order` post-merge
  - Zero-tolerance reconciliation enforced
  - Rejected rows written to `stg.dq_rejections`
  - Assertion results summary written to `stg.lineage`

---

### TASK-DQ-004: DQ rejection monitoring notebook
- **ID:** TASK-DQ-004
- **Group:** 7 — Data Quality Framework
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-DQ-002, TASK-DQ-003
- **Implements:** DQR-REJ, DQR-REC
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dq/nb_dq_rejection_report.py`
- **Description:** Notebook that queries `stg.dq_rejections` for the current pipeline run, summarises rejection counts by `assertion_id` and `source_table`, and sends an alert (via Databricks notification or webhook) if total rejections exceed the configured threshold. Produces a rejection summary written back to `stg.lineage`. [PENDING: CX-DQ-01] Alert threshold value TBD.
- **Acceptance criteria:**
  - Queries `stg.dq_rejections` filtered by current `lineage_key`
  - Summary grouped by `assertion_id` and `source_table`
  - Alert triggered when rejection count exceeds configured threshold ([PENDING: CX-DQ-01])
  - Summary written to `stg.lineage`
  - Notebook succeeds even when zero rejections exist

---

### TASK-DQ-005: DQ post-pipeline smoke-test notebook
- **ID:** TASK-DQ-005
- **Group:** 7 — Data Quality Framework
- **Type:** etl
- **Priority:** high
- **Depends on:** TASK-MART-002, TASK-DQ-002, TASK-DQ-003
- **Implements:** DQR-AST-001..005
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/dq/nb_dq_smoke_tests.py`
- **Description:** End-to-end smoke-test notebook that runs after the full pipeline completes. Validates: (1) all Silver and Gold tables are non-empty, (2) `stg.lineage` has a completed entry for the current run, (3) all mart views are queryable, (4) the UDF returns a non-NULL result. This notebook is the final gate before the workflow marks the run as successful.
- **Acceptance criteria:**
  - All Silver layer tables (`dim.*`, `fact.*`) return row count > 0
  - `stg.lineage` has a row for the current run with `finished_at` populated
  - All four mart views return at least one row for a sample query
  - UDF returns `0` (not NULL) for a customer with no matching sales
  - Notebook fails loudly (raises exception) on any check failure

---

## Task Group 8: Orchestration & Workflow

### TASK-ORC-001: Databricks Workflow YAML — nightly_etl_main
- **ID:** TASK-ORC-001
- **Group:** 8 — Orchestration & Workflow
- **Type:** config
- **Priority:** critical
- **Depends on:** TASK-ING-001, TASK-ING-005, TASK-DIM-008, TASK-FACT-005, TASK-DQ-005, TASK-MART-001
- **Implements:** FR-ORC, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/workflow_nightly_etl_main.yml`
- **Description:** Define the full Databricks Workflows YAML for `nightly_etl_main`. Schedule: `0 2 * * *` UTC (02:00 nightly). Task dependency graph: (1) `nb_extract_watermark` → (2a) `nb_extract_sales` + (2b) `nb_extract_orders` + (2c) `nb_extract_dimensions` [parallel] → (3) `nb_orchestrate_dimensions` → (4) `nb_orchestrate_facts` → (5a) `nb_dq_fact_sale` + (5b) `nb_dq_fact_order` [parallel] → (6) `nb_commit_watermark` → (7) `nb_refresh_v_customer_sales_summary` → (8) `nb_dq_smoke_tests` → (9) `nb_dq_rejection_report`. Total pipeline budget: NFR-PERF ≤ 4 hours.
- **Acceptance criteria:**
  - Workflow YAML is valid Databricks Workflows format
  - Cron schedule set to `0 2 * * *` UTC
  - All nine pipeline stages present with correct task dependencies
  - Per-task timeout values set (total must not exceed 4 hours)
  - Retry policy defined: 1 retry for transient failures, no retry for DQ gate failures
  - Cluster policy and node type configurable via cluster config block

---

### TASK-ORC-002: Workflow deployment notebook
- **ID:** TASK-ORC-002
- **Group:** 8 — Orchestration & Workflow
- **Type:** config
- **Priority:** high
- **Depends on:** TASK-ORC-001
- **Implements:** FR-ORC, NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/deploy_workflow.sh`
- **Description:** Shell script that uses the Databricks CLI (`databricks jobs create-or-update`) to deploy or update `nightly_etl_main` from `workflow_nightly_etl_main.yml`. Idempotent — detects existing workflow by name and updates rather than creating a duplicate. Intended for execution from the CI/CD pipeline.
- **Acceptance criteria:**
  - Script is idempotent (creates workflow if absent, updates if present)
  - Uses Databricks CLI with service principal credentials from environment variables
  - Exits non-zero on any Databricks API error
  - Workflow ID is printed to stdout after successful deployment

---

### TASK-ORC-003: Cluster configuration
- **ID:** TASK-ORC-003
- **Group:** 8 — Orchestration & Workflow
- **Type:** config
- **Priority:** high
- **Depends on:** TASK-ORC-001
- **Implements:** FR-ORC, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/cluster_config.yml`
- **Description:** Define Databricks cluster configuration for the `nightly_etl_main` workflow: Databricks Runtime version, node type (memory-optimised for ~12M rows/year fact volume), auto-scaling bounds, Spark configuration parameters (`spark.databricks.delta.optimizeWrite.enabled=true`, liquid clustering settings), and init scripts path.
- **Acceptance criteria:**
  - Cluster config specifies a Databricks Runtime ≥ 13.x (Delta 3.x for liquid clustering support)
  - Auto-scaling min/max nodes defined
  - `spark.databricks.delta.optimizeWrite.enabled` set to `true`
  - Config YAML is referenced by `workflow_nightly_etl_main.yml`

---

### TASK-ORC-004: Pipeline run monitoring and alerting
- **ID:** TASK-ORC-004
- **Group:** 8 — Orchestration & Workflow
- **Type:** config
- **Priority:** medium
- **Depends on:** TASK-ORC-001
- **Implements:** FR-ORC, NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/monitoring_config.yml`
- **Description:** Configure Databricks Workflows notification settings: email/webhook on pipeline failure, SLA breach alert if pipeline runtime exceeds 4 hours (NFR-PERF). Define metric collection: per-task duration, rows processed, DQ rejection counts — all pulled from `stg.lineage`. Optionally integrates with external monitoring (Datadog, PagerDuty) via webhook.
- **Acceptance criteria:**
  - Email alert configured on workflow failure
  - SLA breach alert triggered when total runtime exceeds 4 hours
  - `stg.lineage` is the single source of truth for run metrics
  - Configuration file is version-controlled and environment-parameterisable

---

## Task Group 9: Security & Governance

### TASK-SEC-001: Unity Catalog RLS policy for fact tables
- **ID:** TASK-SEC-001
- **Group:** 9 — Security & Governance
- **Type:** db
- **Priority:** critical
- **Depends on:** TASK-DB-008, TASK-DB-009
- **Implements:** CON-SEC-001, FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/grants/fact_rls_policies.sql`
- **Description:** Define and apply Unity Catalog row-level security (RLS) policies on `fact.sale` and `fact.order` to restrict data access by sales territory or business unit as appropriate. [PENDING: CX-P05] Exact RLS filter predicates depend on the Unity Catalog access role matrix. Script includes placeholder policy with clear TODO comments.
- **Acceptance criteria:**
  - RLS policy SQL created for both fact tables
  - Policy references a `current_user()` or role-based predicate
  - [PENDING: CX-P05] placeholder marked with TODO and describes what must be filled in
  - Script is idempotent (`CREATE OR REPLACE ROW FILTER`)
  - CON-SEC-001 PII compliance gate documented as a prerequisite for go-live

---

### TASK-SEC-002: Schema and table grants — Silver layer
- **ID:** TASK-SEC-002
- **Group:** 9 — Security & Governance
- **Type:** db
- **Priority:** high
- **Depends on:** TASK-DB-002, TASK-DB-003, TASK-DB-004, TASK-DB-005, TASK-DB-006, TASK-DB-007, TASK-DB-008, TASK-DB-009
- **Implements:** CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/db/grants/silver_layer_grants.sql`
- **Description:** Apply SELECT grants on all `dim.*` and `fact.*` tables to the analyst and ETL service principal roles. Apply MODIFY grants on all tables to the ETL service principal only. [PENDING: CX-P05] Role names subject to access role matrix.
- **Acceptance criteria:**
  - SELECT grants applied to all 9 Silver tables
  - MODIFY grants applied to ETL service principal only
  - Analyst roles cannot MODIFY (verified by testing with a sample analyst principal)
  - Script is idempotent and [PENDING: CX-P05] TODO clearly marked

---

### TASK-SEC-003: PII compliance validation notebook
- **ID:** TASK-SEC-003
- **Group:** 9 — Security & Governance
- **Type:** etl
- **Priority:** critical
- **Depends on:** TASK-DB-012, TASK-DIM-002
- **Implements:** CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/src/etl/security/nb_pii_compliance_check.py`
- **Description:** Notebook that validates PII column masking is correctly applied on `dim.customer`. Queries the table as a non-privileged test user (or using `AS OF` simulation) and asserts that PII column values are masked. This notebook is the CON-SEC-001 PII compliance gate and must pass before go-live approval.
- **Acceptance criteria:**
  - Queries `dim.customer` PII columns as a non-privileged principal
  - Asserts that `customer_name`, `postal_code`, `phone_number` return masked values for non-privileged users
  - Asserts that a PII-viewer-role principal receives unmasked values
  - Test result written to `stg.lineage` with assertion ID `CON-SEC-001`
  - Notebook is runnable independently of the nightly ETL

---

### TASK-SEC-004: Service principal permission audit script
- **ID:** TASK-SEC-004
- **Group:** 9 — Security & Governance
- **Type:** config
- **Priority:** medium
- **Depends on:** TASK-SEC-001, TASK-SEC-002
- **Implements:** CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/uc_permission_audit.sql`
- **Description:** SQL script that queries Unity Catalog `information_schema.object_privileges` to audit all grants on `globalsales` catalog objects and outputs a summary. Used for periodic compliance review and to verify that no unintended privileges exist. [PENDING: CX-P05] Expected role list must be confirmed.
- **Acceptance criteria:**
  - Script queries all privilege grants on `globalsales` catalog
  - Output includes: `object_name`, `privilege_type`, `grantee`, `is_grantable`
  - Script is read-only (SELECT only, no DDL or DML)
  - Output can be compared against the expected [PENDING: CX-P05] role matrix

---

### TASK-SEC-005: Secrets rotation runbook
- **ID:** TASK-SEC-005
- **Group:** 9 — Security & Governance
- **Type:** docs
- **Priority:** medium
- **Depends on:** TASK-ENV-002
- **Implements:** CON-SEC-001
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/config/secrets_rotation_runbook.md`
- **Description:** Document the procedure for rotating Databricks Secrets (source credentials, service principal keys) without pipeline downtime. Include: steps to update the secret value, verify the new credential works, and confirm the nightly pipeline picks up the new secret on next run. [PENDING: CX-P04] OLTP credential rotation procedure depends on confirmed connection strategy.
- **Acceptance criteria:**
  - Runbook covers rotation for all secret keys defined in TASK-ENV-002
  - Step-by-step procedure is unambiguous
  - [PENDING: CX-P04] OLTP section clearly marked as pending
  - Runbook references the `secrets_config.py` module for code-side impact assessment

---

## Task Group 10: Testing & Validation

### TASK-TEST-001: Unit tests — common utilities
- **ID:** TASK-TEST-001
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** critical
- **Depends on:** TASK-ENV-003
- **Implements:** NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/unit/test_utils.py`
  - `products/Sales_Orders/current/codebase/tests/unit/test_constants.py`
- **Description:** Unit tests for all functions in `utils.py` and for the contract of `constants.py` (correct types and expected values for all constants). Uses `pytest` with `unittest.mock` for Spark mocking where needed. Must achieve ≥ 80% line coverage on `src/common/`.
- **Acceptance criteria:**
  - All public functions in `utils.py` have at least one test
  - `PROFIT_MARGIN_FACTOR` asserted to equal `1.05`
  - Tests are runnable with `pytest` without a live Spark session
  - Coverage for `src/common/` ≥ 80%

---

### TASK-TEST-002: Unit tests — SCD2 merge utility
- **ID:** TASK-TEST-002
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** critical
- **Depends on:** TASK-DIM-001
- **Implements:** NFR-MAINT, FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/unit/test_scd2_merge.py`
- **Description:** Unit tests for `scd2_merge.py` using a local Spark session (`pyspark.sql.SparkSession.builder.master("local[*]")`). Test all four cases: new record insert, changed record SCD2 split (old row expired, new row inserted), unchanged record no-op, and multi-column natural key.
- **Acceptance criteria:**
  - Four test cases all pass
  - Expired row has correct `expiry_date` and `is_current=False`
  - New row has `effective_date=today`, `expiry_date=9999-12-31`, `is_current=True`
  - Unchanged record produces no net change to the target table
  - Coverage for `src/etl/dimensions/scd2_merge.py` ≥ 90%

---

### TASK-TEST-003: Unit tests — fact merge utility and SK resolver
- **ID:** TASK-TEST-003
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** critical
- **Depends on:** TASK-FACT-001, TASK-FACT-004
- **Implements:** NFR-MAINT, FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/unit/test_fact_merge.py`
  - `products/Sales_Orders/current/codebase/tests/unit/test_sk_resolver.py`
- **Description:** Unit tests for `fact_merge.py` (new insert, update-with-newer-source, no-update-with-older-source, identical-timestamp no-update) and `sk_resolver.py` (successful resolution, unresolved natural key returns NULL, empty source DataFrame).
- **Acceptance criteria:**
  - All seven test cases pass
  - Staleness guard is explicitly tested (older source does not overwrite newer target)
  - `sk_resolver.py` logs unresolved keys without raising an exception
  - Combined coverage for both modules ≥ 90%

---

### TASK-TEST-004: Unit tests — DQ engine
- **ID:** TASK-TEST-004
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** critical
- **Depends on:** TASK-DQ-001
- **Implements:** DQR-AST-001..005
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/unit/test_dq_engine.py`
- **Description:** Unit tests for all five assertion types in `dq_engine.py`. Each assertion type tested with at least two cases: one passing dataset and one failing dataset. Verifies that failing rows are correctly routed to the rejection output and passing rows are returned in the clean output.
- **Acceptance criteria:**
  - All five assertion types have passing and failing test cases
  - Failing rows appear in rejection output with correct `assertion_id` and `rejection_reason`
  - Passing rows do not appear in rejection output
  - Coverage for `src/etl/dq/dq_engine.py` ≥ 90%

---

### TASK-TEST-005: Integration test — ingestion to staging
- **ID:** TASK-TEST-005
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** high
- **Depends on:** TASK-ING-002, TASK-ING-003, TASK-ING-004
- **Implements:** FR-ING
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/integration/test_ingestion.py`
- **Description:** Integration test that runs extraction notebooks against a test fixture (small static dataset mimicking source OLTP tables) and asserts that staging tables are correctly populated. Validates watermark logic, truncate-before-load idempotency, and `lineage_key` stamping. Requires a live Databricks test environment.
- **Acceptance criteria:**
  - `stg.sale_staging`, `stg.order_staging` populated with expected row counts from fixture
  - `stg.etl_cutoff` updated after `nb_commit_watermark` runs
  - Re-running ingestion with the same watermark window yields identical staging content (idempotency)
  - `lineage_key` is non-NULL on all staging rows

---

### TASK-TEST-006: Integration test — dimension SCD2
- **ID:** TASK-TEST-006
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** high
- **Depends on:** TASK-DIM-002, TASK-DIM-003, TASK-DIM-004, TASK-DIM-005, TASK-DIM-006
- **Implements:** FR-TRN
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/integration/test_dimension_scd2.py`
- **Description:** Integration test that runs dimension load notebooks against test fixtures and validates SCD2 behaviour end-to-end: (1) initial load creates active rows, (2) second load with changed attribute creates new active row and expires old row, (3) third load with no changes produces no new rows.
- **Acceptance criteria:**
  - Initial load: all fixture records have `is_current=True`
  - Change load: changed records have one expired row and one new active row; unchanged records unchanged
  - No-change load: total row count unchanged, no new `lineage_key` entries for those records
  - Test covers at least `dim.customer` and `dim.city`

---

### TASK-TEST-007: Integration test — full pipeline end-to-end
- **ID:** TASK-TEST-007
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** high
- **Depends on:** TASK-FACT-002, TASK-FACT-003, TASK-DQ-002, TASK-DQ-003, TASK-MART-001
- **Implements:** FR-TRN, FR-SRV, DQR-REC
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/integration/test_e2e_pipeline.py`
- **Description:** End-to-end integration test that runs the full pipeline (ingestion → dimensions → facts → DQ → mart) against a deterministic test fixture with known expected outputs. Validates that final mart view results match pre-computed expected values for a small test dataset.
- **Acceptance criteria:**
  - Pipeline completes without error for the test fixture dataset
  - `fact.sale` and `fact.order` row counts match expected values
  - `v_customer_sales_summary.profit_margin_with_factor` matches expected computed values for test records
  - `stg.dq_rejections` is empty for a clean fixture dataset
  - Reconciliation counts in `stg.lineage` are correct

---

### TASK-TEST-008: Performance benchmark test
- **ID:** TASK-TEST-008
- **Group:** 10 — Testing & Validation
- **Type:** test
- **Priority:** medium
- **Depends on:** TASK-TEST-007
- **Implements:** NFR-PERF
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/tests/integration/test_performance.py`
- **Description:** Performance benchmark that runs a simulated nightly load against a scaled test dataset (minimum 1M rows in `stg.sale_staging`) and records per-stage duration. Asserts total pipeline runtime is within the 4-hour NFR budget. Also benchmarks mart view query latency (p95 ≤ 5s) by running 10 consecutive queries and computing the 95th-percentile response time.
- **Acceptance criteria:**
  - Total pipeline runtime ≤ 4 hours for a 1M+ row dataset
  - Mart view p95 query latency ≤ 5 seconds for a standard benchmark query
  - Per-stage durations logged to a benchmark output file
  - Test is repeatable and produces consistent results within ±20%

---

## Task Group 11: Documentation & Handoff

### TASK-DOCS-001: Pipeline runbook
- **ID:** TASK-DOCS-001
- **Group:** 11 — Documentation & Handoff
- **Type:** docs
- **Priority:** high
- **Depends on:** TASK-ORC-001
- **Implements:** NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/docs/pipeline_runbook.md`
- **Description:** Operational runbook covering: how to trigger a manual backfill (with watermark override), how to re-run a failed pipeline stage, how to clear and re-process `stg.dq_rejections`, how to monitor `stg.lineage` for run health, and escalation contacts. Includes a troubleshooting decision tree for the five most common failure modes.
- **Acceptance criteria:**
  - Manual backfill procedure documented with exact notebook parameter values
  - Re-run procedure for each pipeline stage documented
  - Troubleshooting decision tree covers: source extraction failure, DQ gate failure, merge timeout, watermark corruption, mart view unavailability
  - Document reviewed and signed off by the operations team before go-live

---

### TASK-DOCS-002: Data dictionary
- **ID:** TASK-DOCS-002
- **Group:** 11 — Documentation & Handoff
- **Type:** docs
- **Priority:** high
- **Depends on:** TASK-DB-001, TASK-DB-002, TASK-DB-003, TASK-DB-004, TASK-DB-005, TASK-DB-006, TASK-DB-007, TASK-DB-008, TASK-DB-009, TASK-DB-010, TASK-DB-011
- **Implements:** NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/docs/data_dictionary.md`
- **Description:** Column-level data dictionary for all 19 objects (5 staging, 7 dimensions, 2 facts, 4 mart views, 1 UDF). For each column: name, data type, description, source column/derivation, nullable, PII flag, SCD2 tracked flag. PII columns on `dim.customer` explicitly flagged and masking behaviour described.
- **Acceptance criteria:**
  - All 19 objects documented
  - Every column has: name, type, description, source derivation
  - PII columns flagged with masking behaviour described
  - SCD2 control columns documented for all SCD2 dimensions
  - Document is generated or validated against actual DDL (no column name drift)

---

### TASK-DOCS-003: Architecture and lineage diagram
- **ID:** TASK-DOCS-003
- **Group:** 11 — Documentation & Handoff
- **Type:** docs
- **Priority:** medium
- **Depends on:** TASK-ORC-001
- **Implements:** FR-LIN, NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/docs/architecture_diagram.md`
- **Description:** Markdown document containing a Mermaid diagram of the full data lineage from source OLTP tables through Bronze staging → Silver dimensions and facts → Gold mart views. Annotates each edge with transformation type (SCD2, MERGE, TRUNCATE-LOAD). Also documents the `lineage_key` propagation chain: how every target row can be traced back to a specific pipeline run via `stg.lineage`.
- **Acceptance criteria:**
  - Mermaid diagram renders correctly in GitHub/Databricks notebooks
  - All 19 target objects and their source dependencies shown
  - `lineage_key` propagation chain documented
  - Pending decision nodes annotated: [PENDING: CX-P04], [PENDING: CX-P05]

---

### TASK-DOCS-004: Go-live checklist and handoff package
- **ID:** TASK-DOCS-004
- **Group:** 11 — Documentation & Handoff
- **Type:** docs
- **Priority:** high
- **Depends on:** TASK-TEST-007, TASK-SEC-003, TASK-DOCS-001, TASK-DOCS-002
- **Implements:** CON-SEC-001, NFR-MAINT
- **Deliverables:**
  - `products/Sales_Orders/current/codebase/docs/go_live_checklist.md`
- **Description:** Pre-go-live checklist that must be completed and signed off before the pipeline is promoted to production. Items include: all integration tests passing, TASK-SEC-003 PII compliance gate passed (CON-SEC-001), [PENDING: CX-P04] OLTP connection confirmed, [PENDING: CX-P05] role matrix applied, [PENDING: CX-DQ-01] DQ thresholds confirmed and configured, performance benchmark results within NFR-PERF bounds, runbook reviewed by ops team, data dictionary reviewed by data steward.
- **Acceptance criteria:**
  - Checklist covers all three pending decisions with go/no-go gates
  - CON-SEC-001 PII compliance gate is a hard prerequisite for go-live
  - Each checklist item has an owner and sign-off field
  - Document structured for use as a formal change management artefact

---

_End of tasks.md — 66 tasks across 11 groups for Sales_Orders._
