# Tasks: Purchase

**Product:** Purchase · **Project:** GlobalPurchase_Project
**Source:** design.md + requirements.md · **Date:** 2026-08-25

---

## Task Summary

| Task ID | Group | File / Artifact | Description | Requirements |
|---|---|---|---|---|
| DB-001 | DB | src/db/ddl/stg_purchase_staging.sql | CREATE TABLE for transient staging table | FR-001, FR-010, NFR-008 |
| DB-002 | DB | src/db/ddl/stg_etl_cutoff.sql | CREATE TABLE for watermark control table | FR-002, NFR-008 |
| DB-003 | DB | src/db/ddl/stg_lineage.sql | CREATE TABLE for pipeline lineage registry | FR-008, NFR-007, NFR-008 |
| DB-004 | DB | src/db/ddl/stg_dq_rejections.sql | CREATE TABLE for DQ rejection log | FR-009, DQR-004, NFR-008 |
| DB-005 | DB | src/db/ddl/dim_supplier.sql | CREATE TABLE for SCD-2 supplier dimension | FR-003, FR-011, NFR-008 |
| DB-006 | DB | src/db/ddl/dim_stock_item.sql | CREATE TABLE for SCD-2 stock item dimension | FR-004, FR-011, NFR-008 |
| DB-007 | DB | src/db/ddl/dim_date_populate.sql | CREATE TABLE + seed script for static date calendar | FR-005, FR-011, NFR-008 |
| DB-008 | DB | src/db/ddl/fact_purchase.sql | CREATE TABLE for central purchase fact table | FR-006, NFR-001, NFR-008 |
| DB-009 | DB | src/db/ddl/mart/v_purchase_by_supplier.sql | CREATE MATERIALIZED VIEW for supplier purchase summary | FR-012, NFR-001 |
| DB-010 | DB | src/db/ddl/mart/v_purchase_per_stock_item.sql | CREATE VIEW for per-stock-item purchase detail | FR-012, NFR-001 |
| GRANT-001 | GRANT | src/db/grants/dim_supplier_grants.sql | Unity Catalog GRANT statements for dim.supplier | NFR-003 |
| GRANT-002 | GRANT | src/db/grants/dim_stock_item_grants.sql | Unity Catalog GRANT statements for dim.stock_item | NFR-003 |
| GRANT-003 | GRANT | src/db/grants/fact_rls_policies.sql | Unity Catalog GRANT statements for fact.purchase | NFR-003 |
| GRANT-004 | GRANT | src/db/grants/mart_grants.sql | Unity Catalog GRANT statements for mart schema | NFR-003 |
| COMMON-001 | COMMON | src/common/constants.py | Shared table-name, schema-name, and threshold constants | NFR-006 |
| COMMON-002 | COMMON | src/common/utils.py | Shared log_info / log_error helper functions | NFR-006, NFR-007 |
| ING-001 | ING | src/etl/ingestion/nb_extract_watermark.py | Read watermark from etl_cutoff; open lineage record; publish task values | FR-002, FR-008, FR-011 |
| ING-002 | ING | src/etl/ingestion/nb_extract_dimensions.py | Extract source dimension tables via JDBC into Spark temp views | FR-003, FR-004, NFR-003 |
| ING-003 | ING | src/etl/ingestion/nb_extract_purchase.py | Bounded JDBC extract of purchase data; truncate+overwrite stg.purchase_staging | FR-001, FR-010, NFR-005 |
| ING-004 | ING | src/etl/ingestion/nb_commit_watermark.py | Advance etl_cutoff watermark and close lineage record after successful run | FR-002, FR-008, NFR-005 |
| DIM-001 | DIM | src/etl/dimensions/scd2_merge.py | Reusable two-step SCD-2 MERGE helper (expire + insert) | FR-003, FR-004, NFR-005 |
| DIM-002 | DIM | src/etl/dimensions/nb_load_dim_supplier.py | Notebook: invoke scd2_merge for dim.supplier; log metrics | FR-003, NFR-007 |
| DIM-003 | DIM | src/etl/dimensions/nb_load_dim_stock_item.py | Notebook: invoke scd2_merge for dim.stock_item; log metrics | FR-004, NFR-007 |
| DIM-004 | DIM | src/etl/dimensions/nb_populate_dim_date.py | Bootstrap and guard script for static dim.date calendar population | FR-005, FR-011, NFR-005 |
| DIM-005 | DIM | src/etl/dimensions/nb_orchestrate_dimensions.py | Orchestrator notebook: sequence dimension loads; pass task values | FR-003, FR-004, FR-005 |
| FACT-001 | FACT | src/etl/facts/sk_resolver.py | Surrogate key resolution helper; left-join + COALESCE sentinel fallback | FR-006, FR-007 |
| FACT-002 | FACT | src/etl/facts/fact_merge.py | Delta MERGE helper for fact.purchase; returns rows_merged metric | FR-006, NFR-005 |
| FACT-003 | FACT | src/etl/facts/nb_load_fact_purchase.py | Fact load notebook: resolve SKs, run fact MERGE, conditional OPTIMIZE, close lineage | FR-006, FR-007, FR-008, NFR-001 |
| FACT-004 | FACT | src/etl/facts/nb_orchestrate_facts.py | Orchestrator notebook: sequence sk_resolver + fact load; pass task values | FR-006, NFR-005 |
| MART-001 | MART | src/etl/mart/nb_refresh_v_purchase_by_supplier.py | Notebook: REFRESH MATERIALIZED VIEW for v_purchase_by_supplier | FR-012, NFR-001 |
| MART-002 | MART | src/etl/mart/nb_refresh_v_purchase_per_stock_item.py | Notebook: refresh v_purchase_per_stock_item view | FR-012, NFR-001 |
| MART-003 | MART | src/etl/mart/nb_optimize_mart.py | Notebook: OPTIMIZE and VACUUM mart-layer Delta tables | NFR-001, NFR-004 |
| MART-004 | MART | src/etl/mart/nb_validate_mart_views.py | Notebook: row-count and null-key assertions comparing mart to fact | FR-012, DQR-005, NFR-007 |
| MART-005 | MART | src/db/queries/bi_sample_queries.sql | Sample Unity Catalog queries for BI tool validation | FR-012, NFR-006 |
| DQ-001 | DQ | src/etl/dq/dq_engine.py | DQ rule evaluator: evaluate configured rules; write stg.dq_rejections rows | FR-009, DQR-001, DQR-002, DQR-003, DQR-004 |
| DQ-002 | DQ | src/etl/dq/nb_dq_purchase.py | DQ orchestrator notebook: invoke dq_engine; enforce blocking rules | FR-009, DQR-001, DQR-005, DQR-006 |
| DQ-003 | DQ | src/etl/dq/nb_dq_rejection_report.py | Aggregate stg.dq_rejections by lineage_key; log per-run summary | FR-009, DQR-004, NFR-007 |
| DQ-004 | DQ | src/etl/dq/nb_dq_smoke_tests.py | Fast-fail pre-DQ checks (dim.date non-empty, staging non-null lineage_key) | FR-005, DQR-006, NFR-007 |
| DQ-005 | DQ | src/etl/security/nb_pii_compliance_check.py | PII scan notebook: assert zero hardcoded credentials in all notebooks | NFR-003 |
| CFG-001 | CFG | config/cluster_config.yml | Databricks cluster policy: instance types, autoscaling, Spark configs | NFR-001, NFR-003 |
| CFG-002 | CFG | config/workflow_nightly_etl_main.yml | Databricks Workflow DAG: 4-layer task graph, schedules, alerts | FR-001, NFR-002 |
| CFG-003 | CFG | config/uc_setup.sql | Unity Catalog setup: CREATE CATALOG, CREATE SCHEMA for all four schemas | NFR-003, NFR-006 |
| CFG-004 | CFG | config/uc_permission_audit.sql | Audit query: show all grants across globalpurchase catalog | NFR-003 |
| CFG-005 | CFG | config/dq_assertions_purchase.yaml | DQ assertion config: rule definitions, thresholds, severity mappings | FR-009, DQR-001, DQR-002, DQR-003 |
| CFG-006 | CFG | config/secrets_config.py | Secrets bootstrap script: create Databricks Secrets scopes and keys | NFR-003 |
| CFG-007 | CFG | config/secrets_setup.md | Secrets setup runbook: step-by-step guide for initializing scopes | NFR-003, NFR-006 |
| CFG-008 | CFG | config/secrets_rotation_runbook.md | Credential rotation runbook: steps to rotate JDBC credentials | NFR-003, NFR-006 |
| CFG-009 | CFG | config/deploy_workflow.sh | Deployment shell script: upload notebooks and create/update Workflow | NFR-002, NFR-006 |
| CFG-010 | CFG | config/ci_cd_pipeline.yml | CI/CD pipeline definition: lint, test, deploy stages | NFR-006 |
| CFG-011 | CFG | config/monitoring_config.yml | Alert configuration: recipient lists, webhook URLs, 15-min SLA window | NFR-002, NFR-007 |
| CFG-012 | CFG | config/bi_connections.md | BI tool reconnection guide: Unity Catalog endpoint details per mart view | FR-012, NFR-006 |
| DOC-001 | DOC | docs/architecture_diagram.md | Architecture narrative and ASCII/Mermaid diagram of 4-layer pipeline | NFR-006 |
| DOC-002 | DOC | docs/data_dictionary.md | Column-level data dictionary for all managed tables | NFR-006, NFR-007 |
| DOC-003 | DOC | docs/pipeline_runbook.md | Operational runbook: monitoring, failure recovery, reprocessing steps | NFR-002, NFR-006 |
| DOC-004 | DOC | docs/go_live_checklist.md | Pre-production checklist: all acceptance criteria in verifiable checkbox form | NFR-006 |
| TEST-001 | TEST | config/pytest.ini | pytest configuration: test paths, markers, coverage thresholds | NFR-006 |
| TEST-002 | TEST | tests/unit/test_scd2_merge.py | Unit test stubs for scd2_merge.apply_scd2_merge | FR-003, FR-004, NFR-005 |
| TEST-003 | TEST | tests/unit/test_sk_resolver.py | Unit test stubs for sk_resolver.resolve_surrogate_keys | FR-006, FR-007 |
| TEST-004 | TEST | tests/unit/test_fact_merge.py | Unit test stubs for fact_merge.apply_fact_merge | FR-006, NFR-005 |
| TEST-005 | TEST | tests/unit/test_dq_engine.py | Unit test stubs for dq_engine rule evaluation and rejection writing | FR-009, DQR-001, DQR-004 |
| TEST-006 | TEST | tests/integration/test_pipeline_e2e.py | Integration test stubs: full pipeline run against a test catalog | FR-001, FR-002, FR-006, NFR-005 |

---

## Task Details

### DB Tasks (Database Layer)

#### DB-001 — Create stg.purchase_staging Table

**File:** `src/db/ddl/stg_purchase_staging.sql`
**Description:** Implement the DDL for `globalpurchase.stg.purchase_staging`. The table must use `USING DELTA`, carry `lineage_key BIGINT NOT NULL` and `_extracted_at_utc TIMESTAMP NOT NULL` audit columns, and set `delta.deletedFileRetentionDuration` and `delta.logRetentionDuration` to `interval 90 days`. Include `CREATE TABLE IF NOT EXISTS`. No clustering. No CDF. The full column list is defined in Data Model §2.5. Add `COMMENT` clauses on all columns.
**Design reference:** Data Model §2.5, Data Model §4
**Requirements:** FR-001, FR-010, NFR-008
**Acceptance criteria:** (1) `CREATE TABLE IF NOT EXISTS` executes without error on a clean catalog. (2) `DESCRIBE DETAIL` confirms both retention properties are `90 days`. (3) The table is present in `globalpurchase.stg` schema after execution. (4) Re-running the script produces no error.
**Dependencies:** CFG-003

---

#### DB-002 — Create stg.etl_cutoff Table

**File:** `src/db/ddl/stg_etl_cutoff.sql`
**Description:** Implement the DDL for `globalpurchase.stg.etl_cutoff`. Columns: `entity_name STRING NOT NULL` (PK), `last_cutoff_time TIMESTAMP NOT NULL`. `USING DELTA`. Retention: `interval 2555 days` for both log and file retention (control table, retained with fact/dim history). Primary key constraint `pk_stg_etl_cutoff`. `CREATE TABLE IF NOT EXISTS`. Full column spec in Data Model §2.6.
**Design reference:** Data Model §2.6, Data Model §4, Ingestion §2
**Requirements:** FR-002, NFR-008
**Acceptance criteria:** (1) Table creates successfully and `entity_name` is the primary key. (2) `DESCRIBE DETAIL` confirms 2555-day retention. (3) An INSERT for `entity_name = 'purchase'` with a non-null timestamp succeeds. (4) A duplicate INSERT on `entity_name` fails with a constraint violation.
**Dependencies:** CFG-003

---

#### DB-003 — Create stg.lineage Table

**File:** `src/db/ddl/stg_lineage.sql`
**Description:** Implement the DDL for `globalpurchase.stg.lineage`. `lineage_key` must be `BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL` (surrogate PK). Include: `pipeline_run_id STRING NOT NULL`, `entity_name STRING NOT NULL`, `started_at TIMESTAMP NOT NULL`, `completed_at TIMESTAMP`, `status STRING`, `source_row_count BIGINT`, `rows_loaded BIGINT`. `USING DELTA`. Retention: `interval 2555 days`. Full spec in Data Model §2.7.
**Design reference:** Data Model §2.7, Data Model §4, Observability §1
**Requirements:** FR-008, NFR-007, NFR-008
**Acceptance criteria:** (1) `lineage_key` auto-increments on INSERT without explicit value. (2) `DESCRIBE DETAIL` confirms 2555-day retention. (3) An INSERT with only `pipeline_run_id`, `entity_name`, and `started_at` populated succeeds. (4) The table exists in `globalpurchase.stg`.
**Dependencies:** CFG-003

---

#### DB-004 — Create stg.dq_rejections Table

**File:** `src/db/ddl/stg_dq_rejections.sql`
**Description:** Implement the DDL for `globalpurchase.stg.dq_rejections`. `rejection_key` must be `BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL` (surrogate PK). Include all rejection record attributes: `dq_rule_id STRING NOT NULL`, `batch_id STRING NOT NULL`, `lineage_key BIGINT`, `affected_column STRING`, `observed_value STRING`, `expected_condition STRING`, `severity STRING NOT NULL`, `recorded_at TIMESTAMP NOT NULL`. `USING DELTA`. Retention: `interval 90 days`. Full spec in Data Model §2.8.
**Design reference:** Data Model §2.8, Data Model §4, DQR-004
**Requirements:** FR-009, DQR-004, NFR-008
**Acceptance criteria:** (1) `rejection_key` auto-increments on INSERT. (2) `DESCRIBE DETAIL` confirms 90-day retention. (3) An INSERT with a null `lineage_key` succeeds (nullable). (4) An INSERT with a null `severity` fails.
**Dependencies:** CFG-003

---

#### DB-005 — Create dim.supplier Table

**File:** `src/db/ddl/dim_supplier.sql`
**Description:** Implement the DDL for `globalpurchase.dim.supplier`. `supplier_key` must be `INT GENERATED ALWAYS AS IDENTITY NOT NULL` (surrogate PK). Include all SCD-2 tracking columns: `valid_from DATE NOT NULL`, `valid_to DATE NOT NULL`, `row_effective_date DATE NOT NULL`, `row_expiry_date DATE NOT NULL DEFAULT DATE '9999-12-31'`, `is_current_row BOOLEAN NOT NULL DEFAULT TRUE`. CDF must be enabled: `'delta.enableChangeDataFeed' = 'true'`. Retention: `interval 2555 days`. Add `lineage_key BIGINT NOT NULL`. Full column list in Data Model §2.2.
**Design reference:** Data Model §2.2, Data Model §3, Data Model §4, Transformation §SCD-2 Dimension Merge Design
**Requirements:** FR-003, FR-011, NFR-008
**Acceptance criteria:** (1) `supplier_key` auto-increments. (2) CDF is enabled — `DESCRIBE DETAIL` confirms `enableChangeDataFeed = true`. (3) Retention is 2555 days. (4) A sentinel INSERT (`supplier_key` override not possible via IDENTITY — insert a row with `wwi_supplier_id = 0` and verify it becomes the sentinel). (5) `is_current_row` defaults to `TRUE`.
**Dependencies:** CFG-003

---

#### DB-006 — Create dim.stock_item Table

**File:** `src/db/ddl/dim_stock_item.sql`
**Description:** Implement the DDL for `globalpurchase.dim.stock_item`. Same structural pattern as DB-005: `stock_item_key INT GENERATED ALWAYS AS IDENTITY NOT NULL` (PK), all SCD-2 tracking columns, `lineage_key BIGINT NOT NULL`, CDF enabled, retention 2555 days. Include product-specific columns: `wwi_stock_item_id`, `stock_item_name`, `color`, `size`, `unit_package_name`, `outer_package_name`, `brand`, `description`, `unit_price DECIMAL(18,2)`, `recommended_retail_price DECIMAL(18,2)`, `typical_weight_per_unit DECIMAL(18,3)`, `is_chiller_stock BOOLEAN`, `tax_rate DECIMAL(18,3)`. Full column list in Data Model §2.3.
**Design reference:** Data Model §2.3, Data Model §3, Data Model §4
**Requirements:** FR-004, FR-011, NFR-008
**Acceptance criteria:** (1) Same structural checks as DB-005 applied to `dim.stock_item`. (2) CDF enabled. (3) Retention 2555 days. (4) DECIMAL columns accept 18,2 and 18,3 precision values. (5) `is_current_row` defaults to `TRUE`.
**Dependencies:** CFG-003

---

#### DB-007 — Create and Seed dim.date Table

**File:** `src/db/ddl/dim_date_populate.sql`
**Description:** Implement two SQL blocks in one file: (1) `CREATE TABLE IF NOT EXISTS globalpurchase.dim.date` with `date_key INT NOT NULL` (PK, YYYYMMDD format), `calendar_date DATE NOT NULL`, and all calendar attribute columns (`year`, `quarter`, `month`, `month_name`, `day`, `day_of_week`, `day_of_week_num`, `week_of_year`, `is_weekend`, `is_public_holiday`, `fiscal_year`, `fiscal_quarter`). `USING DELTA`. Retention: `interval 2555 days`. (2) A Spark SQL `INSERT INTO ... SELECT` block that generates the full calendar using a range expression (e.g., `SEQUENCE(DATE '2000-01-01', DATE '2030-12-31', INTERVAL 1 DAY)`). The seed block must be guarded with `IF (SELECT COUNT(*) FROM globalpurchase.dim.date) = 0` or equivalent idempotency guard so re-running does not duplicate rows. Full column list in Data Model §2.4.
**Design reference:** Data Model §2.4, Data Model §4, Ingestion §6, FR-005
**Requirements:** FR-005, FR-011, NFR-008
**Acceptance criteria:** (1) After execution, `dim.date` contains one row per calendar day with no gaps. (2) `date_key` equals the YYYYMMDD integer of each date (e.g., 2024-01-15 → 20240115). (3) Re-running the script produces no additional rows. (4) `DESCRIBE DETAIL` confirms 2555-day retention.
**Dependencies:** CFG-003

---

#### DB-008 — Create fact.purchase Table

**File:** `src/db/ddl/fact_purchase.sql`
**Description:** Implement the DDL for `globalpurchase.fact.purchase`. `purchase_key` must be `BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL` (surrogate PK). FK columns: `date_key INT NOT NULL`, `supplier_key INT NOT NULL`, `stock_item_key INT NOT NULL`. Natural key: `wwi_purchase_order_id INT` (MERGE predicate). Measure columns: `ordered_outers INT`, `ordered_quantity INT`, `received_outers INT`, `package STRING`, `is_order_finalized BOOLEAN`. Audit: `lineage_key BIGINT NOT NULL`. Table properties: `'delta.enableChangeDataFeed' = 'false'`, both retention properties `= 'interval 2555 days'`. Liquid clustering: `CLUSTER BY (date_key, supplier_key, stock_item_key)`. Full spec in Data Model §2.1.
**Design reference:** Data Model §2.1, Data Model §4, Data Model §5, NFR-001
**Requirements:** FR-006, NFR-001, NFR-008
**Acceptance criteria:** (1) `CLUSTER BY` clause is present and references all three FK columns. (2) CDF is `false`. (3) Retention is 2555 days. (4) `lineage_key` is NOT NULL. (5) `purchase_key` auto-increments. (6) `DESCRIBE DETAIL` confirms all properties.
**Dependencies:** CFG-003

---

#### DB-009 — Create mart.v_purchase_by_supplier Materialized View

**File:** `src/db/ddl/mart/v_purchase_by_supplier.sql`
**Description:** Implement `CREATE OR REPLACE MATERIALIZED VIEW globalpurchase.mart.v_purchase_by_supplier`. The view joins `fact.purchase` to `dim.supplier` (on `supplier_key`) and `dim.stock_item` (on `stock_item_key`). Aggregate: `SUM(ordered_quantity) AS total_quantity_ordered`, `COUNT(DISTINCT purchase_key) AS purchase_order_count`. GROUP BY all non-aggregate dimension columns. Add a COMMENT. Use only target-system column names — no source aliases. Serving §3 contains the full DDL pattern.
**Design reference:** Serving §2, Serving §3, Data Model §6
**Requirements:** FR-012, NFR-001
**Acceptance criteria:** (1) `CREATE OR REPLACE MATERIALIZED VIEW` executes without error. (2) A `SELECT COUNT(*) FROM globalpurchase.mart.v_purchase_by_supplier` returns a non-negative integer after a fact load. (3) Column names match the design (no source system names). (4) A `REFRESH` can be triggered by the ETL service principal.
**Dependencies:** DB-005, DB-006, DB-008, GRANT-004

---

#### DB-010 — Create mart.v_purchase_per_stock_item View

**File:** `src/db/ddl/mart/v_purchase_per_stock_item.sql`
**Description:** Implement `CREATE OR REPLACE VIEW globalpurchase.mart.v_purchase_per_stock_item`. The view joins `fact.purchase` to `dim.stock_item` (on `stock_item_key`) and `dim.supplier` (on `supplier_key`). Expose fact columns (`purchase_key`, `date_key`, `supplier_key`, `stock_item_key`, `ordered_outers`, `ordered_quantity`, `received_outers`, `package`, `is_order_finalized`) plus `dim.stock_item.stock_item_name`, `dim.stock_item.color`, `dim.stock_item.unit_package_name`, and `dim.supplier.supplier_name`. No aggregation. Serving §3 contains the full DDL pattern.
**Design reference:** Serving §2, Serving §3, Data Model §6
**Requirements:** FR-012, NFR-001
**Acceptance criteria:** (1) `CREATE OR REPLACE VIEW` executes without error. (2) `DESCRIBE globalpurchase.mart.v_purchase_per_stock_item` shows all expected columns. (3) A SELECT against the view returns rows consistent with the joined tables. (4) `bi-service-principal` can SELECT on this view after GRANT-004 is applied.
**Dependencies:** DB-005, DB-006, DB-008, GRANT-004

---

### GRANT Tasks (Unity Catalog Access Control)

#### GRANT-001 — dim.supplier Unity Catalog Grants

**File:** `src/db/grants/dim_supplier_grants.sql`
**Description:** Implement GRANT statements for `globalpurchase.dim.supplier`. Grant `USE SCHEMA` on `globalpurchase.dim` to `etl-service-principal` and `bi-service-principal`. Grant `SELECT, MODIFY` on `globalpurchase.dim.supplier` to `etl-service-principal`. Grant `SELECT` on `globalpurchase.dim.supplier` to `bi-service-principal`. Use Unity Catalog syntax (`GRANT ... ON TABLE ... TO ...`). Reference: Serving §4.
**Design reference:** Serving §4, NFR-003
**Requirements:** NFR-003
**Acceptance criteria:** (1) After execution, `SHOW GRANTS ON TABLE globalpurchase.dim.supplier` lists both principals with correct privileges. (2) `bi-service-principal` can SELECT but not MODIFY the table. (3) `etl-service-principal` can SELECT and MODIFY. (4) Script is idempotent — re-running produces no error.
**Dependencies:** CFG-003, DB-005

---

#### GRANT-002 — dim.stock_item Unity Catalog Grants

**File:** `src/db/grants/dim_stock_item_grants.sql`
**Description:** Implement GRANT statements for `globalpurchase.dim.stock_item` following the same pattern as GRANT-001. Grant `SELECT, MODIFY` to `etl-service-principal` and `SELECT` to `bi-service-principal`. Reference: Serving §4.
**Design reference:** Serving §4, NFR-003
**Requirements:** NFR-003
**Acceptance criteria:** Same acceptance criteria as GRANT-001 applied to `dim.stock_item`. `SHOW GRANTS` confirms both principals with correct privileges.
**Dependencies:** CFG-003, DB-006

---

#### GRANT-003 — fact.purchase Unity Catalog Grants and RLS Policies

**File:** `src/db/grants/fact_rls_policies.sql`
**Description:** Implement GRANT statements for `globalpurchase.fact.purchase`. Grant `USE SCHEMA` on `globalpurchase.fact` to `etl-service-principal` and `bi-service-principal`. Grant `SELECT, MODIFY` to `etl-service-principal`. Grant `SELECT` to `bi-service-principal`. If row-level security is required by the design, add `CREATE ROW FILTER` or `ALTER TABLE SET ROW FILTER` statements here. Reference: Serving §4.
**Design reference:** Serving §4, NFR-003
**Requirements:** NFR-003
**Acceptance criteria:** (1) `SHOW GRANTS ON TABLE globalpurchase.fact.purchase` lists both principals. (2) `bi-service-principal` cannot MODIFY the fact table. (3) `etl-service-principal` can SELECT and MODIFY. (4) Script is idempotent.
**Dependencies:** CFG-003, DB-008

---

#### GRANT-004 — mart Schema Unity Catalog Grants

**File:** `src/db/grants/mart_grants.sql`
**Description:** Implement GRANT statements for `globalpurchase.mart`. Grant `USE SCHEMA` to `etl-service-principal`, `bi-service-principal`, and `purchase-analysts`. Grant `SELECT` on all views in `globalpurchase.mart` to `bi-service-principal` and `purchase-analysts`. Grant `SELECT, REFRESH` on the materialized view `globalpurchase.mart.v_purchase_by_supplier` to `etl-service-principal`. Reference: Serving §4.
**Design reference:** Serving §4, NFR-003
**Requirements:** NFR-003
**Acceptance criteria:** (1) `purchase-analysts` principal can SELECT mart views. (2) `etl-service-principal` can REFRESH the materialized view. (3) `bi-service-principal` cannot REFRESH or MODIFY. (4) `SHOW GRANTS ON SCHEMA globalpurchase.mart` confirms all principals.
**Dependencies:** CFG-003, DB-009, DB-010

---

### COMMON Tasks (Shared Python Modules)

#### COMMON-001 — constants.py: Table Names and Thresholds

**File:** `src/common/constants.py`
**Description:** Implement the shared constants module. Define fully qualified table name strings for every managed table: `TBL_STG_PURCHASE_STAGING`, `TBL_STG_ETL_CUTOFF`, `TBL_STG_LINEAGE`, `TBL_STG_DQ_REJECTIONS`, `TBL_DIM_SUPPLIER`, `TBL_DIM_STOCK_ITEM`, `TBL_DIM_DATE`, `TBL_FACT_PURCHASE`, `VIEW_MART_BY_SUPPLIER`, `VIEW_MART_PER_STOCK_ITEM`. Define schema-name constants: `CATALOG`, `SCHEMA_STG`, `SCHEMA_DIM`, `SCHEMA_FACT`, `SCHEMA_MART`. Define pipeline threshold constants: `FACT_OPTIMIZE_ROW_THRESHOLD` (integer; default 10000). Define `ENTITY_NAME_PURCHASE = 'purchase'` and `HISTORY_ANCHOR_DATE_KEY = 'spark.globalpurchase.history_anchor_date'`. All names must be strings composed from the catalog/schema constants, not hardcoded strings scattered across ETL code.
**Design reference:** Transformation §Module Layout, NFR-006
**Requirements:** NFR-006
**Acceptance criteria:** (1) `from src.common.constants import TBL_FACT_PURCHASE` resolves to `'globalpurchase.fact.purchase'`. (2) A grep for hardcoded schema-qualified names in `src/etl/` returns zero hits — all references go through constants. (3) `flake8` and `black` pass on this file. (4) Module has no side effects on import.
**Dependencies:** none

---

#### COMMON-002 — utils.py: Shared Logging Helpers

**File:** `src/common/utils.py`
**Description:** Implement `log_info(msg: str) -> None` and `log_error(msg: str) -> None` helpers that emit structured log lines including a UTC timestamp and the calling context. Both functions must accept format-string style messages with a `lineage_key` keyword argument (e.g., `log_info("Merged %d rows", rows, lineage_key=key)`). Optionally add a `get_spark_conf(spark, key: str, default: str = None) -> str` helper that wraps `spark.conf.get` with a default fallback. All helpers must be importable without a live Spark session (for unit testing).
**Design reference:** Observability §5, Transformation §Module Layout, NFR-006
**Requirements:** NFR-006, NFR-007
**Acceptance criteria:** (1) `log_info` and `log_error` execute without error when called with a message string. (2) Output includes a UTC timestamp. (3) Both functions are importable in a non-Spark Python environment. (4) `flake8` and `black` pass.
**Dependencies:** none

---

### ING Tasks (Ingestion Layer)

#### ING-001 — nb_extract_watermark: Watermark Read and Lineage Open

**File:** `src/etl/ingestion/nb_extract_watermark.py`
**Description:** Implement the watermark-read notebook. Logic: (1) Read `entity_name = 'purchase'` from `globalpurchase.stg.etl_cutoff`. (2) If no row exists, use `HISTORY_ANCHOR_DATE` from `spark.conf.get(HISTORY_ANCHOR_DATE_KEY)` and INSERT the initial row. (3) INSERT a new lineage record into `globalpurchase.stg.lineage` with `status = 'running'`, `entity_name = ENTITY_NAME_PURCHASE`, `started_at = CURRENT_TIMESTAMP()`. (4) Publish `last_cutoff` and `lineage_key` as Databricks task values via `dbutils.jobs.taskValues.set`. Retrieve `env_scope` via `dbutils.widgets.get`. All table names must come from `constants.py`. Logging via `utils.log_info`. Design pattern in Ingestion §2.
**Design reference:** Ingestion §2, Ingestion §7, Ingestion §8, Observability §1
**Requirements:** FR-002, FR-008, FR-011
**Acceptance criteria:** (1) After execution, `stg.lineage` has a new row with `status = 'running'` and a valid `lineage_key`. (2) `dbutils.jobs.taskValues.get(taskKey='nb_extract_watermark', key='lineage_key')` returns a non-null integer. (3) `dbutils.jobs.taskValues.get(taskKey='nb_extract_watermark', key='last_cutoff')` returns a valid timestamp string. (4) On first run with no etl_cutoff row, `HISTORY_ANCHOR_DATE` is used and a row is inserted. (5) No hardcoded credentials or table names.
**Dependencies:** COMMON-001, COMMON-002, DB-002, DB-003

---

#### ING-002 — nb_extract_dimensions: JDBC Dimension Extraction

**File:** `src/etl/ingestion/nb_extract_dimensions.py`
**Description:** Implement the dimension extraction notebook. (1) Retrieve JDBC credentials from Databricks Secrets using `env_scope` widget: `dbutils.secrets.get(scope, key='jdbc_url')`, `jdbc_username`, `jdbc_password`. (2) Read the source `Purchasing.Suppliers` table via `spark.read.format('jdbc')` and register as Spark temp view `src_suppliers`. (3) Read `Warehouse.StockItems` via JDBC and register as temp view `src_stock_items`. (4) The JDBC driver class is read from Spark config, never hardcoded. (5) Log row counts for each extracted view using `utils.log_info`. Temp views are session-scoped only — do not write to persistent storage. Design pattern in Ingestion §3.
**Design reference:** Ingestion §3, Ingestion §5, Ingestion §7
**Requirements:** FR-003, FR-004, NFR-003
**Acceptance criteria:** (1) After execution, `spark.catalog.tableExists('src_suppliers')` is `True` (as temp view). (2) `src_suppliers` row count equals source `Purchasing.Suppliers` row count. (3) No JDBC credentials appear in the notebook source. (4) The notebook runs cleanly on a cluster with the JDBC driver installed. (5) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, CFG-001

---

#### ING-003 — nb_extract_purchase: Bounded JDBC Extract and Staging Overwrite

**File:** `src/etl/ingestion/nb_extract_purchase.py`
**Description:** Implement the purchase extraction notebook. (1) Retrieve `last_cutoff` and `lineage_key` from task values published by ING-001. (2) Retrieve JDBC credentials from Databricks Secrets. (3) Issue a JDBC pushdown query that filters `WHERE po.LastEditedWhen > CAST('<last_cutoff>' AS DATETIME2)` and collapses duplicate order IDs using `MAX(LastEditedWhen) GROUP BY` (correcting the known source duplicate defect; see Ingestion §9 and FR-010). (4) Inject `lineage_key` (cast to BIGINT) and `_extracted_at_utc` (UTC now) as columns on every row. (5) Write to `globalpurchase.stg.purchase_staging` using `mode('overwrite')` with `overwriteSchema=False`. Log source row count to `stg.lineage.source_row_count`. Design pattern in Ingestion §4.
**Design reference:** Ingestion §4, Ingestion §5, Ingestion §7, Ingestion §8, Ingestion §9
**Requirements:** FR-001, FR-010, NFR-003, NFR-005
**Acceptance criteria:** (1) After execution, `stg.purchase_staging` contains only rows from the bounded JDBC query. (2) All rows carry the same non-null `lineage_key`. (3) No row has `purchase_order_id` duplicated (GROUP BY de-duplicates). (4) A run with no new source rows produces an empty staging table and does not raise an error. (5) `_extracted_at_utc` is non-null on every row. (6) `stg.lineage.source_row_count` is updated with the staging row count.
**Dependencies:** COMMON-001, COMMON-002, ING-001, DB-001, DB-003

---

#### ING-004 — nb_commit_watermark: Watermark Advance and Lineage Close

**File:** `src/etl/ingestion/nb_commit_watermark.py`
**Description:** Implement the watermark commit notebook — executed as the final task in the Workflow DAG, after all layers succeed. (1) Retrieve `lineage_key` from task values. (2) Compute the new watermark as `MAX(_extracted_at_utc)` from `stg.purchase_staging` for the current `lineage_key`. (3) UPDATE `stg.etl_cutoff SET last_cutoff_time = <new_watermark> WHERE entity_name = ENTITY_NAME_PURCHASE`. (4) UPDATE `stg.lineage SET status = 'success', completed_at = CURRENT_TIMESTAMP() WHERE lineage_key = <lineage_key>`. This notebook must NOT run if any upstream task failed — enforced by the Workflow DAG dependencies defined in CFG-002. Observability §3 and §1 describe the commit lifecycle.
**Design reference:** Ingestion §2, Observability §1, Observability §3, Observability §7
**Requirements:** FR-002, FR-008, NFR-005
**Acceptance criteria:** (1) After execution, `stg.etl_cutoff.last_cutoff_time` for `'purchase'` is strictly greater than the value before the run. (2) `stg.lineage` row for the run has `status = 'success'` and a non-null `completed_at`. (3) If the notebook is not executed (simulated upstream failure), `etl_cutoff` remains unchanged. (4) Re-running for the same batch does not create duplicate lineage rows.
**Dependencies:** COMMON-001, COMMON-002, ING-001, DB-002, DB-003

---

### DIM Tasks (Dimension Layer)

#### DIM-001 — scd2_merge.py: Two-Step SCD-2 MERGE Helper

**File:** `src/etl/dimensions/scd2_merge.py`
**Description:** Implement `apply_scd2_merge(spark, target_table, staging_df, business_key, effective_date, attribute_columns) -> int`. The function executes two sequential Spark SQL MERGE operations: (1) Expire step — MERGE on `business_key AND is_current_row = TRUE`, WHEN MATCHED AND attributes changed, SET `is_current_row = FALSE, row_expiry_date = effective_date - 1 day`. (2) Insert step — MERGE on `business_key AND is_current_row = TRUE`, WHEN NOT MATCHED BY TARGET, INSERT new active row with `is_current_row = TRUE, row_effective_date = effective_date, row_expiry_date = DATE '9999-12-31'`. Return total rows affected (expired + inserted). The expire step must complete before the insert step. Design SQL patterns in Transformation §SCD-2 Dimension Merge Design. The function must be parameterizable so it works for both `dim.supplier` and `dim.stock_item`.
**Design reference:** Transformation §SCD-2 Dimension Merge Design, Transformation §Module Layout
**Requirements:** FR-003, FR-004, NFR-005
**Acceptance criteria:** (1) A changed attribute produces exactly one expired row and one new active row for that business key. (2) An unchanged attribute produces zero additional rows. (3) A new business key produces one new active row. (4) No active row has `valid_to` other than `DATE '9999-12-31'`. (5) `flake8` and `black` pass. (6) Function is importable without a live Spark session for unit testing purposes (Spark dependency injected, not imported at module level).
**Dependencies:** COMMON-001, COMMON-002

---

#### DIM-002 — nb_load_dim_supplier: Supplier SCD-2 Load Notebook

**File:** `src/etl/dimensions/nb_load_dim_supplier.py`
**Description:** Implement the supplier dimension load notebook. (1) Retrieve `lineage_key` from task values (set by ING-001). (2) Read `src_suppliers` temp view (created by ING-002 in the same Workflow run). (3) Map source columns to `dim.supplier` attribute columns (apply any name normalizations defined in the product transformation rules). (4) Call `scd2_merge.apply_scd2_merge(spark, TBL_DIM_SUPPLIER, supplier_df, business_key='wwi_supplier_id', effective_date=today, attribute_columns=[...])`. (5) Log rows merged via `utils.log_info`. Do not re-read from the JDBC source — consume the session temp view from ING-002.
**Design reference:** Transformation §SCD-2 Dimension Merge Design, Ingestion §3, Observability §7
**Requirements:** FR-003, NFR-007
**Acceptance criteria:** (1) After execution, `dim.supplier` has SCD-2 rows reflecting the current batch. (2) Changed supplier attributes produce exactly two rows (one expired, one active). (3) The `lineage_key` column on new rows matches the run's lineage key. (4) The sentinel row (`wwi_supplier_id = 0`) is never expired or duplicated. (5) Log output contains row count.
**Dependencies:** COMMON-001, COMMON-002, DIM-001, ING-001, ING-002, DB-005

---

#### DIM-003 — nb_load_dim_stock_item: Stock Item SCD-2 Load Notebook

**File:** `src/etl/dimensions/nb_load_dim_stock_item.py`
**Description:** Implement the stock item dimension load notebook following the same pattern as DIM-002. (1) Read `src_stock_items` temp view from ING-002. (2) Map source columns to `dim.stock_item` attributes. (3) Call `scd2_merge.apply_scd2_merge` with `business_key='wwi_stock_item_id'`. (4) Log metrics. Sentinel row (`wwi_stock_item_id = 0`) must not be overwritten.
**Design reference:** Transformation §SCD-2 Dimension Merge Design, Ingestion §3, Data Model §2.3
**Requirements:** FR-004, NFR-007
**Acceptance criteria:** All acceptance criteria from DIM-002 applied to `dim.stock_item`. `stock_item_key = 0` sentinel is preserved after each run.
**Dependencies:** COMMON-001, COMMON-002, DIM-001, ING-001, ING-002, DB-006

---

#### DIM-004 — nb_populate_dim_date: Date Calendar Bootstrap Guard

**File:** `src/etl/dimensions/nb_populate_dim_date.py`
**Description:** Implement the date dimension bootstrap guard notebook. (1) Check `SELECT COUNT(*) FROM globalpurchase.dim.date` — if zero, trigger the calendar population SQL from DB-007. (2) If non-zero, skip population and log "dim.date already populated — skipping". (3) Always assert that `dim.date` is non-empty at the end; if empty after the population attempt, raise an exception to abort the pipeline. This notebook is safe to run on every pipeline execution (idempotent guard) but only populates on the first run. The actual calendar SQL lives in DB-007; this notebook calls it or embeds the population logic.
**Design reference:** Data Model §2.4, FR-005, Ingestion §7
**Requirements:** FR-005, FR-011, NFR-005
**Acceptance criteria:** (1) On a fresh catalog, execution populates `dim.date` with one row per calendar day. (2) On subsequent runs, `dim.date` row count is unchanged. (3) If `dim.date` is empty after the bootstrap attempt, the notebook raises and the pipeline aborts. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DB-007

---

#### DIM-005 — nb_orchestrate_dimensions: Dimension Layer Orchestrator

**File:** `src/etl/dimensions/nb_orchestrate_dimensions.py`
**Description:** Implement the dimension orchestration notebook that acts as the entry point for the dimension Workflow task. Sequence: (1) Call `nb_populate_dim_date` guard (or replicate its check inline). (2) Call `nb_load_dim_supplier`. (3) Call `nb_load_dim_stock_item`. Alternatively, this notebook can be a thin wrapper that confirms task dependencies (using `dbutils.jobs.taskValues.get` to validate that `lineage_key` is available) and logs the dimension layer summary. If the Workflow DAG handles sequencing via task dependencies, this notebook may simply validate preconditions and emit a dimension-layer completion task value.
**Design reference:** Serving §6 (DAG diagram), Ingestion §7, Observability §7
**Requirements:** FR-003, FR-004, FR-005
**Acceptance criteria:** (1) After execution, all three dimension loads have been invoked. (2) A failed dimension sub-load causes this orchestrator to report failure (propagates exception). (3) No dimension task runs before `lineage_key` is validated. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DIM-002, DIM-003, DIM-004, ING-001

---

### FACT Tasks (Fact Layer)

#### FACT-001 — sk_resolver.py: Surrogate Key Resolution Helper

**File:** `src/etl/facts/sk_resolver.py`
**Description:** Implement `resolve_surrogate_keys(spark, staging_df, load_date) -> DataFrame`. The function: (1) Reads `dim.supplier` filtered to `is_current_row = TRUE`; left-joins on `wwi_supplier_id`; adds `supplier_key = COALESCE(dim.supplier_key, 0)`. (2) Reads `dim.stock_item` filtered to `is_current_row = TRUE`; left-joins on `wwi_stock_item_id`; adds `stock_item_key = COALESCE(dim.stock_item_key, 0)`. (3) Derives `date_key = CAST(DATE_FORMAT(order_date, 'yyyyMMdd') AS INT)`. Returns a DataFrame with `supplier_key`, `stock_item_key`, and `date_key` added. Unresolved keys MUST default to `0` (sentinel fallback), never NULL. Code pattern in Transformation §Surrogate Key Resolution Design.
**Design reference:** Transformation §Surrogate Key Resolution Design, FR-007
**Requirements:** FR-006, FR-007
**Acceptance criteria:** (1) A staged row with an unresolvable `wwi_supplier_id` yields `supplier_key = 0`. (2) A staged row with an unresolvable `wwi_stock_item_id` yields `stock_item_key = 0`. (3) `date_key` equals the YYYYMMDD integer of `order_date` for every row. (4) No row has a NULL value in `supplier_key`, `stock_item_key`, or `date_key` after resolution. (5) Function is importable without a live Spark session for unit testing (Spark injected). (6) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DB-005, DB-006

---

#### FACT-002 — fact_merge.py: Fact Delta MERGE Helper

**File:** `src/etl/facts/fact_merge.py`
**Description:** Implement `apply_fact_merge(spark, resolved_df, lineage_key) -> int`. The function executes a Spark SQL MERGE INTO `globalpurchase.fact.purchase` using `wwi_purchase_order_id` as the match predicate. WHEN MATCHED: update all non-key columns. WHEN NOT MATCHED BY TARGET: insert all columns including `lineage_key`. Return `rows_merged` extracted from the Delta operation metrics (`operationMetrics['numTargetRowsInserted'] + numTargetRowsUpdated`). Do not call OPTIMIZE — that is handled in FACT-003. Full MERGE SQL in Transformation §Fact MERGE Design.
**Design reference:** Transformation §Fact MERGE Design, Transformation §Module Layout
**Requirements:** FR-006, NFR-005
**Acceptance criteria:** (1) A new `wwi_purchase_order_id` results in an INSERT into `fact.purchase`. (2) An existing `wwi_purchase_order_id` results in an UPDATE (idempotent). (3) `rows_merged` is a positive integer equal to the number of rows in the resolved DataFrame. (4) `lineage_key` is non-null on every inserted row. (5) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DB-008

---

#### FACT-003 — nb_load_fact_purchase: Fact Load Notebook

**File:** `src/etl/facts/nb_load_fact_purchase.py`
**Description:** Implement the fact load notebook. (1) Retrieve `lineage_key` and `last_cutoff` from task values. (2) Call `sk_resolver.resolve_surrogate_keys` on `stg.purchase_staging`. (3) Call `fact_merge.apply_fact_merge` with the resolved DataFrame and `lineage_key`. (4) Apply conditional OPTIMIZE: `if rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD: spark.sql(f"OPTIMIZE {TBL_FACT_PURCHASE} ZORDER BY (date_key, supplier_key)")`. (5) Update `stg.lineage SET rows_loaded = rows_merged, status = 'running' WHERE lineage_key = <key>`. (6) Log all metrics. The watermark commit (ING-004) is a downstream Workflow task, not called here.
**Design reference:** Transformation §Fact MERGE Design, Transformation §Conditional OPTIMIZE, Transformation §Lineage Close, Observability §1
**Requirements:** FR-006, FR-007, FR-008, NFR-001
**Acceptance criteria:** (1) After execution, `fact.purchase` contains all rows from `stg.purchase_staging` for the current batch. (2) `lineage_key` is non-null on every fact row. (3) OPTIMIZE is triggered only when `rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD`; the skip case is logged. (4) `stg.lineage.rows_loaded` is updated. (5) No hardcoded table names or credentials.
**Dependencies:** COMMON-001, COMMON-002, FACT-001, FACT-002, ING-001, DB-003, DB-008

---

#### FACT-004 — nb_orchestrate_facts: Fact Layer Orchestrator

**File:** `src/etl/facts/nb_orchestrate_facts.py`
**Description:** Implement the fact orchestration notebook. Validates that `lineage_key` is available from task values, confirms dimension layer completion (check that `dim.supplier` and `dim.stock_item` have sentinel rows), then calls or sequences `nb_load_fact_purchase`. If the Workflow DAG handles sequencing via task dependencies, this notebook may serve as a thin precondition validator that asserts sentinel rows exist in both dimension tables before fact load begins (`SELECT COUNT(*) FROM globalpurchase.dim.supplier WHERE supplier_key = 0 MUST = 1`).
**Design reference:** Serving §6, FR-007, FR-011
**Requirements:** FR-006, NFR-005
**Acceptance criteria:** (1) If the sentinel row is missing from `dim.supplier` or `dim.stock_item`, execution raises before the fact MERGE begins. (2) After a clean run, the fact layer completes and logs row counts. (3) Task value `lineage_key` is available before any fact write. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, FACT-003, DIM-005

---

### MART Tasks (Serving Layer)

#### MART-001 — nb_refresh_v_purchase_by_supplier: Materialized View Refresh

**File:** `src/etl/mart/nb_refresh_v_purchase_by_supplier.py`
**Description:** Implement the materialized view refresh notebook. Execute `spark.sql(f"REFRESH MATERIALIZED VIEW {VIEW_MART_BY_SUPPLIER}")`. Log the refresh time and verify the view returns at least one row post-refresh via a COUNT query. The notebook must only run after the DQ assertion suite completes (enforced by DAG; see CFG-002). If the REFRESH raises an exception, the notebook must not swallow it — propagate to the Workflow for alerting.
**Design reference:** Serving §5, Serving §6
**Requirements:** FR-012, NFR-001
**Acceptance criteria:** (1) `REFRESH MATERIALIZED VIEW` executes without error. (2) `SELECT COUNT(*) FROM globalpurchase.mart.v_purchase_by_supplier` returns a positive integer after the refresh. (3) The notebook raises if the refresh fails. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DB-009, GRANT-004, DQ-002

---

#### MART-002 — nb_refresh_v_purchase_per_stock_item: View Refresh

**File:** `src/etl/mart/nb_refresh_v_purchase_per_stock_item.py`
**Description:** Implement the view refresh notebook for `v_purchase_per_stock_item`. Since this is a standard view (not materialized), the notebook may instead run a validation SELECT to confirm the view is queryable after the fact and dimension loads complete. Log the row count returned from the view. If the view has stale definitions, trigger a `CREATE OR REPLACE VIEW` using the DDL from DB-010.
**Design reference:** Serving §3, Serving §5, Serving §6
**Requirements:** FR-012, NFR-001
**Acceptance criteria:** (1) A SELECT against the view returns rows consistent with the current fact layer. (2) Notebook logs the view row count. (3) The notebook raises if the view is not queryable. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DB-010, GRANT-004, DQ-002

---

#### MART-003 — nb_optimize_mart: Mart OPTIMIZE and VACUUM

**File:** `src/etl/mart/nb_optimize_mart.py`
**Description:** Implement the mart optimization notebook. (1) Run `OPTIMIZE` on any Delta-backed mart tables (materialized views stored as Delta tables). (2) Run `VACUUM` with a retention period consistent with the 90-day staging retention or as configured. (3) Log before/after file counts. This notebook runs after mart view refreshes in the DAG. Skip OPTIMIZE/VACUUM on plain views (non-Delta). Conditionally skip if no rows were merged in the fact layer this run (read `rows_loaded` from `stg.lineage` for the current run).
**Design reference:** Serving §5, Serving §6, NFR-001, NFR-004
**Requirements:** NFR-001, NFR-004
**Acceptance criteria:** (1) `OPTIMIZE` is executed on Delta-backed mart tables. (2) `VACUUM` runs without error. (3) Notebook is idempotent — runs safely on an already-optimized table. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, MART-001, MART-002

---

#### MART-004 — nb_validate_mart_views: Mart Validation Assertions

**File:** `src/etl/mart/nb_validate_mart_views.py`
**Description:** Implement the mart validation notebook. Assertions: (1) `SELECT COUNT(*) FROM globalpurchase.mart.v_purchase_by_supplier` > 0. (2) `SELECT COUNT(*) FROM globalpurchase.mart.v_purchase_per_stock_item` > 0. (3) Row count in mart view is consistent with `fact.purchase` (total counts should align). (4) No null FK columns in the mart views (LEFT ANTI JOIN to detect unresolved keys). Log all assertion results. Raise if any assertion fails so the Workflow alerts. Reference: Observability §2, DQR-005.
**Design reference:** Serving §5, Observability §2, DQR-005
**Requirements:** FR-012, DQR-005, NFR-007
**Acceptance criteria:** (1) All assertions pass on a clean run. (2) A mismatch between mart and fact row counts raises an observable exception. (3) Assertion results are logged with `lineage_key`. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, MART-001, MART-002, DB-008

---

#### MART-005 — bi_sample_queries.sql: BI Validation Queries

**File:** `src/db/queries/bi_sample_queries.sql`
**Description:** Implement a library of 5–8 sample queries against the mart layer for use by BI developers and QA validation. Include: (1) Total ordered quantity by supplier and month. (2) Top 10 stock items by ordered quantity. (3) Purchase orders with sentinel keys (`supplier_key = 0` OR `stock_item_key = 0`). (4) End-to-end lineage trace for a given `purchase_key`. (5) Count of DQ rejections by rule per run. All queries must use `globalpurchase.mart.*` or `globalpurchase.stg.*` — no direct access to `fact.*` or `dim.*` except for the lineage trace. Use `-- Query N: <title>` comment headers.
**Design reference:** Serving §3, Serving §7, Observability §6
**Requirements:** FR-012, NFR-006
**Acceptance criteria:** (1) Each query executes without syntax error on the target catalog. (2) Results are consistent with known test data. (3) No hardcoded catalog names — use `globalpurchase` as prefix throughout.
**Dependencies:** DB-009, DB-010, GRANT-004

---

### DQ Tasks (Data Quality Layer)

#### DQ-001 — dq_engine.py: DQ Rule Evaluation Engine

**File:** `src/etl/dq/dq_engine.py`
**Description:** Implement the DQ engine module. Define a `DQEngine` class or `evaluate_rules(spark, lineage_key, batch_id, rules_config) -> dict` function. The engine must: (1) Evaluate DQR-001 (row count reconciliation between `stg.purchase_staging` and the fact delta for `lineage_key`) — BLOCKING. (2) Evaluate DQR-002 (FK integrity via LEFT ANTI JOIN for `supplier_key`, `stock_item_key`, `date_key`) — Informational. (3) Evaluate DQR-003 (orphaned key: key = 0 or NULL on any FK column) — Informational. (4) Evaluate DQR-006 (null `lineage_key` in `fact.purchase` for current batch) — BLOCKING. For each violation, write one row to `stg.dq_rejections` with all required attributes (DQR-004). Return a summary dict with `{rule_id: {passed: bool, violation_count: int}}`. A write failure to `stg.dq_rejections` must itself raise a blocking error (DQR-004 mechanism).
**Design reference:** Observability §2, DQR-001, DQR-002, DQR-003, DQR-004, DQR-006
**Requirements:** FR-009, DQR-001, DQR-002, DQR-003, DQR-004
**Acceptance criteria:** (1) A staging/fact count mismatch returns `{DQR-001: {passed: False, ...}}` and writes to `stg.dq_rejections`. (2) FK violations are logged per offending row per FK column. (3) Rows with `supplier_key = 0` are flagged under DQR-003. (4) A clean batch returns all rules as `passed: True` and zero rejection rows for that `lineage_key`. (5) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DB-004, DB-008

---

#### DQ-002 — nb_dq_purchase: DQ Orchestrator Notebook

**File:** `src/etl/dq/nb_dq_purchase.py`
**Description:** Implement the DQ orchestrator notebook. (1) Retrieve `lineage_key` and `batch_id` from task values. (2) Load the rules config from `config/dq_assertions_purchase.yaml` (CFG-005). (3) Call `dq_engine.evaluate_rules(spark, lineage_key, batch_id, rules_config)`. (4) Check the returned summary: if any BLOCKING rule failed, raise a `DQBlockingFailure` exception to halt the pipeline. Informational failures are logged but do not raise. (5) Publish a `dq_passed` boolean task value. The exception must propagate to the Workflow so that mart tasks are not scheduled (DQR-005).
**Design reference:** Observability §2, Observability §7, DQR-001, DQR-005, DQR-006
**Requirements:** FR-009, DQR-001, DQR-005, DQR-006
**Acceptance criteria:** (1) A BLOCKING DQ failure causes the notebook to raise, preventing downstream mart tasks. (2) An informational-only failure allows mart promotion. (3) `dq_passed` task value is set to `True` only when no BLOCKING failures occur. (4) All DQ results are logged with `lineage_key`. (5) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DQ-001, CFG-005, FACT-003

---

#### DQ-003 — nb_dq_rejection_report: Rejection Report Notebook

**File:** `src/etl/dq/nb_dq_rejection_report.py`
**Description:** Implement the rejection report notebook. (1) Read `stg.dq_rejections` filtered to the current `lineage_key`. (2) Aggregate by `dq_rule_id` and `severity`: count violations per rule. (3) Log a formatted per-run summary table using `utils.log_info`. (4) Optionally write the summary as a JSON task output value for downstream consumers. This notebook does not raise on violations — it is a reporting-only artifact. It runs after `nb_dq_purchase` in the DAG.
**Design reference:** Observability §2, Observability §7, DQR-004
**Requirements:** FR-009, DQR-004, NFR-007
**Acceptance criteria:** (1) After execution, a formatted rejection summary is visible in Workflow logs. (2) If zero violations exist for the current `lineage_key`, the report logs "0 DQ violations for this run". (3) The notebook does not raise on DQ violations. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DQ-002, DB-004

---

#### DQ-004 — nb_dq_smoke_tests: Pre-DQ Fast-Fail Checks

**File:** `src/etl/dq/nb_dq_smoke_tests.py`
**Description:** Implement fast-fail smoke test notebook that runs before the main DQ suite. Checks: (1) `dim.date` is non-empty — abort if empty (FR-005). (2) `stg.purchase_staging` rows all have non-null `lineage_key` — abort if any null (DQR-006 pre-check). (3) `stg.lineage` has a `'running'` record for the current `lineage_key` — abort if not found. Each check raises immediately on failure with a descriptive error message. This notebook does NOT write to `stg.dq_rejections` (smoke tests are pre-pipeline guards, not DQ events).
**Design reference:** Observability §7, FR-005, DQR-006
**Requirements:** FR-005, DQR-006, NFR-007
**Acceptance criteria:** (1) An empty `dim.date` causes immediate abort with a clear error message. (2) A null `lineage_key` in staging causes abort. (3) A missing lineage record causes abort. (4) A clean state produces no errors and logs all checks as passed. (5) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, DB-003, DB-004, DB-007, ING-001

---

#### DQ-005 — nb_pii_compliance_check: PII and Credentials Scan

**File:** `src/etl/security/nb_pii_compliance_check.py`
**Description:** Implement the PII compliance check notebook. (1) Use `dbutils.fs.ls` or equivalent to list all notebook source paths in the product codebase directory. (2) Read each file and scan for patterns indicating hardcoded credentials: password=, jdbc_password=, secret=, literal IP addresses in connection strings, or any string matching common credential patterns. (3) Assert zero matches — raise if any are found. (4) Additionally assert that all `dbutils.secrets.get` calls specify a scope variable (not a hardcoded scope string other than the constant names). Log each scanned file and result. This notebook is run as a CI step or on-demand, not in the nightly DAG.
**Design reference:** Ingestion §5, NFR-003
**Requirements:** NFR-003
**Acceptance criteria:** (1) A scan of the clean codebase returns zero credential matches. (2) A scan of a file containing a hardcoded password raises with a clear message identifying the file and line. (3) All source files in `src/` are scanned. (4) `flake8` and `black` pass.
**Dependencies:** COMMON-001, COMMON-002, CFG-006

---

### CFG Tasks (Configuration)

#### CFG-001 — cluster_config.yml: Databricks Cluster Policy

**File:** `config/cluster_config.yml`
**Description:** Define the Databricks cluster configuration for the nightly ETL job. Include: instance type, autoscaling min/max workers, Spark configuration keys (`spark.databricks.delta.optimizeWrite.enabled = true`, JDBC driver class as `spark.driver.extraClassPath` or equivalent, `spark.globalpurchase.history_anchor_date`), cluster tags for cost attribution, and the cluster policy ID. No credential values in this file — all secrets referenced by scope and key name only.
**Design reference:** Ingestion §5, NFR-001, NFR-003
**Requirements:** NFR-001, NFR-003
**Acceptance criteria:** (1) The YAML is valid (parseable by PyYAML). (2) No credential values are present — a grep for password/secret returns zero results. (3) The cluster config is consumable by CFG-002 (Workflow YAML references the cluster policy). (4) `spark.globalpurchase.history_anchor_date` is defined with a placeholder value.
**Dependencies:** none

---

#### CFG-002 — workflow_nightly_etl_main.yml: Databricks Workflow DAG

**File:** `config/workflow_nightly_etl_main.yml`
**Description:** Define the complete Databricks Workflow YAML for the nightly ETL run. The DAG must have exactly four layers with correct task dependencies: Layer 1 — `nb_extract_watermark` → `nb_extract_dimensions` → `nb_extract_purchase` (sequential ingestion). Layer 2 — `nb_orchestrate_dimensions` (depends on Layer 1). Layer 3 — `nb_orchestrate_facts` (depends on Layer 2). Layer 4 — `nb_dq_smoke_tests` → `nb_dq_purchase` → `nb_dq_rejection_report` → `nb_refresh_v_purchase_by_supplier` → `nb_refresh_v_purchase_per_stock_item` → `nb_optimize_mart` → `nb_validate_mart_views` → `nb_commit_watermark` (depends on Layer 3). Include the nightly schedule cron expression, email alert on failure (referencing `monitoring_config.yml`), and the `env_scope` widget parameter.
**Design reference:** Serving §6, Ingestion §7, Observability §4, NFR-002
**Requirements:** FR-001, NFR-002
**Acceptance criteria:** (1) The YAML is valid Databricks Workflow format. (2) Each downstream task has explicit `depends_on` entries. (3) `nb_commit_watermark` is the last task in the DAG. (4) The schedule is defined. (5) Alert configuration references `monitoring_config.yml` recipients.
**Dependencies:** CFG-001, CFG-011, COMMON-001

---

#### CFG-003 — uc_setup.sql: Unity Catalog Schema Setup

**File:** `config/uc_setup.sql`
**Description:** Implement the Unity Catalog bootstrap SQL. Execute: `CREATE CATALOG IF NOT EXISTS globalpurchase`. Create the four schemas: `CREATE SCHEMA IF NOT EXISTS globalpurchase.stg`, `globalpurchase.dim`, `globalpurchase.fact`, `globalpurchase.mart`. Add `COMMENT` clauses on each schema describing its role. This script is run once before any table DDL. Include a header comment explaining the execution order (this script before DB-001 through DB-010).
**Design reference:** Data Model §1, Data Model §3, NFR-003
**Requirements:** NFR-003, NFR-006
**Acceptance criteria:** (1) `CREATE CATALOG IF NOT EXISTS` executes without error. (2) All four schemas exist after execution. (3) Re-running produces no errors. (4) A `SHOW SCHEMAS IN globalpurchase` lists all four schemas.
**Dependencies:** none

---

#### CFG-004 — uc_permission_audit.sql: Unity Catalog Permission Audit

**File:** `config/uc_permission_audit.sql`
**Description:** Implement a SQL audit script that queries all grants across the `globalpurchase` catalog. Include: `SHOW GRANTS ON CATALOG globalpurchase`, `SHOW GRANTS ON SCHEMA globalpurchase.stg`, `SHOW GRANTS ON SCHEMA globalpurchase.dim`, `SHOW GRANTS ON SCHEMA globalpurchase.fact`, `SHOW GRANTS ON SCHEMA globalpurchase.mart`, and `SHOW GRANTS ON TABLE` for each managed table. Add comments explaining each block and the expected principal-to-privilege mapping. Used by security auditors post-deploy.
**Design reference:** Serving §4, NFR-003
**Requirements:** NFR-003
**Acceptance criteria:** (1) All `SHOW GRANTS` statements execute without error on the target catalog. (2) Output after running GRANT-001 through GRANT-004 lists the expected principals and privileges. (3) Script is idempotent (read-only).
**Dependencies:** CFG-003, GRANT-001, GRANT-002, GRANT-003, GRANT-004

---

#### CFG-005 — dq_assertions_purchase.yaml: DQ Rules Configuration

**File:** `config/dq_assertions_purchase.yaml`
**Description:** Define the DQ rule configuration consumed by `dq_engine.py` (DQ-001). Include one entry per rule: `rule_id` (DQR-001 through DQR-006), `description`, `severity` (`BLOCKING` or `Informational`), `enabled` (boolean), and `parameters` (e.g., tolerance thresholds for count reconciliation). The YAML structure must match what `dq_engine.evaluate_rules` expects. Include all six DQRs defined in the requirements.
**Design reference:** Observability §2, DQR-001 through DQR-006
**Requirements:** FR-009, DQR-001, DQR-002, DQR-003
**Acceptance criteria:** (1) The YAML is valid (parseable by PyYAML). (2) All six DQRs are defined. (3) DQR-001, DQR-004, DQR-005, DQR-006 have `severity: BLOCKING`. (4) DQR-002 and DQR-003 have `severity: Informational`. (5) `dq_engine.py` can load and iterate the rules without error.
**Dependencies:** none

---

#### CFG-006 — secrets_config.py: Secrets Bootstrap Script

**File:** `config/secrets_config.py`
**Description:** Implement a one-time secrets setup script that creates the Databricks Secrets scopes `globalpurchase-dev` and `globalpurchase-prod` and registers the required keys: `jdbc_url`, `jdbc_username`, `jdbc_password`. The script must use the Databricks CLI or Secrets API — no hardcoded secret values. Actual secret values are supplied at runtime via environment variables or interactive prompts. Include idempotency guards (`if scope not exists: create`). Add clear docstrings explaining which keys must be populated before the ETL pipeline can run.
**Design reference:** Ingestion §5, NFR-003
**Requirements:** NFR-003
**Acceptance criteria:** (1) Running the script creates both scopes without error. (2) Secret values are never printed or logged. (3) A grep for literal password values in this file returns zero hits. (4) `flake8` and `black` pass.
**Dependencies:** none

---

#### CFG-007 — secrets_setup.md: Secrets Initialization Runbook

**File:** `config/secrets_setup.md`
**Description:** Write the step-by-step secrets setup runbook. Sections: (1) Prerequisites (Databricks CLI installed, workspace URL). (2) Creating the dev scope (`globalpurchase-dev`). (3) Creating the prod scope (`globalpurchase-prod`). (4) Registering each required key (`jdbc_url`, `jdbc_username`, `jdbc_password`) with the correct Databricks CLI commands. (5) Verifying that `dbutils.secrets.list(scope='globalpurchase-dev')` lists all keys (without revealing values). (6) Rotating secrets pointer to `secrets_rotation_runbook.md`.
**Design reference:** Ingestion §5, NFR-003, NFR-006
**Requirements:** NFR-003, NFR-006
**Acceptance criteria:** (1) Following the runbook on a fresh workspace results in both scopes existing with all keys registered. (2) No secret values appear in the document. (3) The runbook references the Databricks Secrets documentation for context.
**Dependencies:** CFG-006

---

#### CFG-008 — secrets_rotation_runbook.md: Credential Rotation Runbook

**File:** `config/secrets_rotation_runbook.md`
**Description:** Write the credential rotation runbook for JDBC credentials. Sections: (1) Trigger conditions (scheduled rotation, security incident). (2) Step-by-step rotation procedure using Databricks CLI `secrets put`. (3) Verification steps (run `nb_pii_compliance_check`, confirm pipeline connects successfully). (4) Rollback procedure if new credentials fail. (5) Notification checklist (who to inform). (6) Rotation log table (date, rotated by, scope, key). Document both `globalpurchase-dev` and `globalpurchase-prod` rotation paths.
**Design reference:** Ingestion §5, NFR-003
**Requirements:** NFR-003, NFR-006
**Acceptance criteria:** (1) Following the runbook successfully rotates credentials in both scopes. (2) The runbook covers rollback. (3) No actual credential values are present in the document.
**Dependencies:** CFG-007

---

#### CFG-009 — deploy_workflow.sh: Deployment Shell Script

**File:** `config/deploy_workflow.sh`
**Description:** Implement the deployment shell script that: (1) Exports notebooks from `src/etl/` to the Databricks workspace using the Databricks CLI (`databricks workspace import`). (2) Creates or updates the Workflow from `workflow_nightly_etl_main.yml` using `databricks jobs create` or `databricks jobs update`. (3) Accepts `--env dev|prod` flag to select the target workspace and cluster policy. (4) Exits non-zero on any error. Validate required CLI version at start. Reference `DATABRICKS_HOST` and `DATABRICKS_TOKEN` from environment variables — never hardcoded.
**Design reference:** NFR-002, NFR-006
**Requirements:** NFR-002, NFR-006
**Acceptance criteria:** (1) Running `./deploy_workflow.sh --env dev` uploads all notebooks and creates/updates the Workflow. (2) Script exits non-zero if `DATABRICKS_HOST` is unset. (3) Script exits non-zero if the Databricks CLI is not found. (4) Re-running the script with the same artifacts produces no duplicate jobs.
**Dependencies:** CFG-001, CFG-002

---

#### CFG-010 — ci_cd_pipeline.yml: CI/CD Pipeline Definition

**File:** `config/ci_cd_pipeline.yml`
**Description:** Define the CI/CD pipeline (GitHub Actions, Azure DevOps, or GitLab CI format — align with project standard). Stages: (1) `lint` — run `flake8` and `black --check` on all Python files in `src/`. (2) `test` — run `pytest` using `config/pytest.ini`. (3) `deploy-dev` — run `deploy_workflow.sh --env dev` on merge to main. (4) `deploy-prod` — manual trigger with approval gate. Reference `DATABRICKS_HOST` and `DATABRICKS_TOKEN` as CI secrets. No credentials in the file.
**Design reference:** NFR-006
**Requirements:** NFR-006
**Acceptance criteria:** (1) The YAML is valid for the chosen CI system. (2) The lint stage catches a `flake8` violation if introduced. (3) The test stage runs `pytest` and fails on test failures. (4) No credential values in the pipeline file.
**Dependencies:** CFG-009, TEST-001

---

#### CFG-011 — monitoring_config.yml: Alert Configuration

**File:** `config/monitoring_config.yml`
**Description:** Define the monitoring and alerting configuration. Include: (1) Recipient email addresses (as placeholder strings, e.g., `data-engineering@company.com`). (2) Webhook URLs (placeholder). (3) Alert SLA: 15 minutes from failure detection. (4) Alert trigger condition: any Workflow task failure. (5) Suppression windows (list format for planned maintenance). (6) Severity levels that trigger alerts. This file is referenced by `workflow_nightly_etl_main.yml` (CFG-002). No credential values.
**Design reference:** Observability §4, NFR-002
**Requirements:** NFR-002, NFR-007
**Acceptance criteria:** (1) The YAML is valid. (2) Alert SLA is documented as 15 minutes. (3) Webhook and email recipient fields are present (with placeholder values). (4) The file is consumable by CFG-002 without modification (field names align).
**Dependencies:** none

---

#### CFG-012 — bi_connections.md: BI Tool Reconnection Guide

**File:** `config/bi_connections.md`
**Description:** Write the BI tool reconnection guide. Sections: (1) Overview: migration from the legacy source to Unity Catalog endpoints. (2) For each BI consumer (`v_purchase_by_supplier`, `v_purchase_per_stock_item`): target Unity Catalog connection string format, required service principal, minimum required privilege. (3) Testing the connection: sample query to verify access. (4) Known issues and workarounds. (5) Contact for access provisioning. Serving §7 defines the BI-to-view mapping.
**Design reference:** Serving §7, NFR-006
**Requirements:** FR-012, NFR-006
**Acceptance criteria:** (1) A BI developer following the guide can connect to both mart views. (2) The guide specifies the Unity Catalog SQL warehouse endpoint format. (3) No service principal credentials appear in the document.
**Dependencies:** DB-009, DB-010, GRANT-004

---

### DOC Tasks (Documentation)

#### DOC-001 — architecture_diagram.md: Architecture Narrative and Diagram

**File:** `docs/architecture_diagram.md`
**Description:** Write the architecture document. Include: (1) A paragraph overview of the 4-layer medallion architecture (stg → dim → fact → mart). (2) An ASCII or Mermaid diagram showing the pipeline DAG from ingestion through mart refresh. (3) A table describing each layer's role, schema, and Delta Lake table properties. (4) A description of the lineage flow (`lineage_key` propagation from `stg.lineage` through all target tables). (5) A reference to the Serving §6 DAG sequence. Use only target-system terms.
**Design reference:** Data Model §1, Serving §6, Observability §1
**Requirements:** NFR-006
**Acceptance criteria:** (1) The diagram accurately reflects the 4-layer architecture and task dependencies. (2) All four schemas are described. (3) The document renders correctly in a Markdown viewer. (4) Zero source-system-specific terms (no SQL Server, SSIS references).
**Dependencies:** none

---

#### DOC-002 — data_dictionary.md: Column-Level Data Dictionary

**File:** `docs/data_dictionary.md`
**Description:** Write the column-level data dictionary covering all managed tables: `stg.purchase_staging`, `stg.etl_cutoff`, `stg.lineage`, `stg.dq_rejections`, `dim.supplier`, `dim.stock_item`, `dim.date`, `fact.purchase`. For each table: table description, one row per column with column name, data type, nullable, description, and notes (FK relationships, SCD-2 role, audit purpose). The COMMENT clauses in the DDL files are the authoritative source for descriptions. Include a glossary section for SCD-2 tracking columns.
**Design reference:** Data Model §2.1–2.8, Data Model §3
**Requirements:** NFR-006, NFR-007
**Acceptance criteria:** (1) Every column in every managed table is documented. (2) SCD-2 tracking columns are explained in the glossary. (3) FK relationships are documented (with the caveat that they are logical, not physical). (4) The document is consistent with the DDL COMMENT clauses.
**Dependencies:** DB-001, DB-002, DB-003, DB-004, DB-005, DB-006, DB-007, DB-008

---

#### DOC-003 — pipeline_runbook.md: Operational Runbook

**File:** `docs/pipeline_runbook.md`
**Description:** Write the operational runbook. Sections: (1) Daily monitoring checklist (check Workflow run status, `stg.lineage` latest row, alert inbox). (2) Failure response: how to identify the failed task, read logs, determine whether to re-trigger or investigate. (3) Partial reprocessing guide: how to reset the watermark in `stg.etl_cutoff` and re-run the pipeline for a specific date range. (4) DQ investigation: how to query `stg.dq_rejections` for a given run. (5) Escalation path. (6) Contacts. Include the SQL queries from Observability §6 for end-to-end lineage tracing.
**Design reference:** Observability §1–6, NFR-002, NFR-006
**Requirements:** NFR-002, NFR-006
**Acceptance criteria:** (1) The runbook covers all standard failure scenarios. (2) The watermark reset procedure is accurate and safe (no data loss). (3) SQL queries in the runbook execute without error on the target catalog. (4) No source-system-specific terms.
**Dependencies:** none

---

#### DOC-004 — go_live_checklist.md: Pre-Production Checklist

**File:** `docs/go_live_checklist.md`
**Description:** Write the go-live checklist as a Markdown checkbox list organized by category: (1) Infrastructure — Unity Catalog setup complete, cluster policies applied, secrets scopes created. (2) Data — sentinel rows present, `dim.date` populated, `stg.etl_cutoff` initialized. (3) Security — GRANT statements applied, `nb_pii_compliance_check` passed, dev/prod scope isolation confirmed. (4) Pipeline — Workflow deployed, nightly schedule active, alert recipients confirmed. (5) DQ — `dq_assertions_purchase.yaml` loaded, all six DQR rules enabled. (6) BI — mart views queryable, BI connections guide distributed to consumers. (7) Documentation — all docs complete and accessible. Each item maps to an acceptance criterion from requirements.md.
**Design reference:** All sections of design.md and requirements.md
**Requirements:** NFR-006
**Acceptance criteria:** (1) Every functional and non-functional acceptance criterion from requirements.md appears as a checkbox item. (2) The checklist is structured so that a team member can work through it sequentially. (3) Completing all items is sufficient evidence for production readiness. (4) No items reference source-system-specific components.
**Dependencies:** none

---

### TEST Tasks (Testing)

#### TEST-001 — pytest.ini: pytest Configuration

**File:** `config/pytest.ini`
**Description:** Configure pytest for the Purchase product test suite. Settings: `testpaths = tests`, `python_files = test_*.py`, `python_classes = Test*`, `python_functions = test_*`. Define markers: `unit` (no Spark required), `integration` (requires Databricks cluster or local Spark). Set `addopts = --strict-markers -v --tb=short`. Set `filterwarnings` to suppress known Spark deprecation warnings. Configure `log_cli = true` and `log_level = INFO`.
**Design reference:** NFR-006
**Requirements:** NFR-006
**Acceptance criteria:** (1) `pytest --collect-only` discovers test files in `tests/`. (2) Running `pytest -m unit` selects only unit-marked tests. (3) Running `pytest -m integration` selects only integration-marked tests. (4) The ini file is valid pytest configuration (no parse errors).
**Dependencies:** none

---

#### TEST-002 — test_scd2_merge.py: Unit Tests for SCD-2 Merge Helper

**File:** `tests/unit/test_scd2_merge.py`
**Description:** Implement unit test stubs for `src/etl/dimensions/scd2_merge.py`. Use `pyspark.testing` or a local Spark fixture. Test cases: (1) `test_expire_on_attribute_change` — verify that a changed attribute produces one expired row. (2) `test_insert_new_active_on_change` — verify a new active row is inserted. (3) `test_skip_unchanged` — verify no rows created for unchanged attributes. (4) `test_new_business_key_inserts_active_row` — verify new key results in one active row. (5) `test_sentinel_row_not_touched` — verify business key `0` sentinel row survives the merge. Mark all tests `@pytest.mark.unit`.
**Design reference:** Transformation §SCD-2 Dimension Merge Design, FR-003, FR-004
**Requirements:** FR-003, FR-004, NFR-005
**Acceptance criteria:** (1) All five test functions are implemented as stubs with at least one assertion each. (2) Tests can be collected by pytest with `--collect-only`. (3) Tests pass on a local Spark session. (4) `flake8` and `black` pass.
**Dependencies:** TEST-001, DIM-001

---

#### TEST-003 — test_sk_resolver.py: Unit Tests for Surrogate Key Resolution

**File:** `tests/unit/test_sk_resolver.py`
**Description:** Implement unit test stubs for `src/etl/facts/sk_resolver.py`. Test cases: (1) `test_resolved_supplier_key` — matched supplier produces correct `supplier_key`. (2) `test_unresolved_supplier_falls_back_to_sentinel` — unmatched supplier yields `supplier_key = 0`. (3) `test_resolved_stock_item_key` — matched stock item produces correct key. (4) `test_unresolved_stock_item_falls_back_to_sentinel` — unmatched stock item yields key `0`. (5) `test_date_key_format` — `date_key` equals YYYYMMDD integer of `order_date`. (6) `test_no_null_keys_in_output` — asserts zero null values across all three FK columns. Mark all tests `@pytest.mark.unit`.
**Design reference:** Transformation §Surrogate Key Resolution Design, FR-006, FR-007
**Requirements:** FR-006, FR-007
**Acceptance criteria:** (1) All six test functions are implemented with at least one assertion each. (2) Tests pass on a local Spark session. (3) `flake8` and `black` pass.
**Dependencies:** TEST-001, FACT-001

---

#### TEST-004 — test_fact_merge.py: Unit Tests for Fact MERGE Helper

**File:** `tests/unit/test_fact_merge.py`
**Description:** Implement unit test stubs for `src/etl/facts/fact_merge.py`. Test cases: (1) `test_new_order_inserted` — new `wwi_purchase_order_id` produces one INSERT. (2) `test_existing_order_updated` — existing `wwi_purchase_order_id` produces one UPDATE, no duplicate row. (3) `test_rows_merged_count_returned` — return value equals expected rows. (4) `test_lineage_key_on_inserted_row` — inserted row carries the supplied `lineage_key`. (5) `test_idempotent_double_run` — running twice for the same data produces the same row count. Mark all tests `@pytest.mark.unit`.
**Design reference:** Transformation §Fact MERGE Design, FR-006, NFR-005
**Requirements:** FR-006, NFR-005
**Acceptance criteria:** (1) All five test functions are implemented with at least one assertion each. (2) Tests pass on a local Spark session. (3) `flake8` and `black` pass.
**Dependencies:** TEST-001, FACT-002

---

#### TEST-005 — test_dq_engine.py: Unit Tests for DQ Engine

**File:** `tests/unit/test_dq_engine.py`
**Description:** Implement unit test stubs for `src/etl/dq/dq_engine.py`. Test cases: (1) `test_dqr001_passes_on_matching_counts` — equal staging and fact counts return passed. (2) `test_dqr001_fails_on_count_mismatch` — mismatched counts return failed and write rejection row. (3) `test_dqr002_detects_fk_violation` — a fact row with no dim match is flagged. (4) `test_dqr003_flags_sentinel_key` — `supplier_key = 0` is flagged as orphaned key. (5) `test_dqr006_fails_on_null_lineage_key` — null `lineage_key` in fact returns failed. (6) `test_rejection_row_written_on_violation` — every violation writes to `stg.dq_rejections`. Mark all tests `@pytest.mark.unit`.
**Design reference:** Observability §2, DQR-001, DQR-002, DQR-003, DQR-006
**Requirements:** FR-009, DQR-001, DQR-004
**Acceptance criteria:** (1) All six test functions implemented with at least one assertion each. (2) Tests pass on a local Spark session with a mock `stg.dq_rejections` table. (3) `flake8` and `black` pass.
**Dependencies:** TEST-001, DQ-001

---

#### TEST-006 — test_pipeline_e2e.py: Integration Test Stubs

**File:** `tests/integration/test_pipeline_e2e.py`
**Description:** Implement integration test stubs that validate the end-to-end pipeline against a test catalog (`globalpurchase_test`). Test cases: (1) `test_watermark_initialized_on_first_run` — after first run, `stg.etl_cutoff` has a non-null row. (2) `test_staging_populated_after_ingestion` — `stg.purchase_staging` is non-empty after ingestion. (3) `test_fact_rows_match_staging_count` — fact row delta equals staging count (DQR-001). (4) `test_lineage_key_non_null_on_all_fact_rows` — zero null `lineage_key` values in `fact.purchase`. (5) `test_watermark_advanced_after_successful_run` — `etl_cutoff.last_cutoff_time` is greater after run. (6) `test_watermark_unchanged_after_failed_run` — simulate failure before commit, confirm watermark unchanged. Mark all tests `@pytest.mark.integration`.
**Design reference:** FR-001, FR-002, FR-006, FR-008, NFR-005
**Requirements:** FR-001, FR-002, FR-006, NFR-005
**Acceptance criteria:** (1) All six test functions are implemented as stubs with at least one assertion each. (2) Tests are marked `@pytest.mark.integration`. (3) Tests can be collected without a live Databricks connection. (4) `flake8` and `black` pass.
**Dependencies:** TEST-001, ING-001, ING-003, ING-004, FACT-003

---

*Generated by migVisor SmartBuilder · 2026-08-25*
