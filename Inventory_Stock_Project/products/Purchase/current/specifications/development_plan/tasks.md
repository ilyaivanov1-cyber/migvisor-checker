# Implementation Tasks: Purchase

_Product: Purchase | Project: Inventory_Stock_Project | Generated: 2026-09-07_
_Derived from: `design.md` + `requirements.md`_

---

## Task Summary

| Task ID | Type | Title | Depends On | Requirements | Design Reference |
|---|---|---|---|---|---|
| TASK-001 | DDL | Create `bronze.lineage_run` table | — | FR-003, NFR-007 | §7 DDL Reference |
| TASK-002 | DDL | Create `bronze.etl_cutoff` table | — | FR-002, NFR-001 | §7 DDL Reference |
| TASK-003 | DDL | Create `bronze.purchase_staging` table | TASK-001, TASK-002 | FR-001, FR-003 | §7 DDL Reference |
| TASK-004 | DDL | Create `bronze.dq_rejections` table | TASK-001 | NFR-004, NFR-005, NFR-007, DQR-008 | §7 DDL Reference |
| TASK-005 | DDL | Create `silver_fact.fact_purchase` table | TASK-001 | FR-007, NFR-001, NFR-012 | §7 DDL Reference |
| TASK-006 | DDL | Create `silver_dim.supplier_current` view | — | FR-004 | §7 DDL Reference |
| TASK-007 | DDL | Create `silver_dim.stock_item_current` view | — | FR-005 | §7 DDL Reference |
| TASK-008 | DDL | Generate GRANT statements for Unity Catalog access | TASK-001, TASK-003, TASK-004, TASK-005 | NFR-008 | §7 DDL Reference |
| TASK-009 | ETL | Write `src/common/constants.py` | TASK-001, TASK-003, TASK-005 | NFR-009, NFR-011 | §9 Configuration Management |
| TASK-010 | ETL | Write `src/common/scd2_merge.py` | — | FR-004, FR-005 | §3 SK Resolution Pattern |
| TASK-011 | ETL | Write `src/common/sk_resolver.py` | TASK-009 | FR-004, FR-005, CALC-002, CALC-003 | §3 SK Resolution Pattern |
| TASK-012 | ETL | Write `src/common/fact_merge.py` | TASK-009 | FR-007, NFR-003 | §4 MERGE INTO Pattern |
| TASK-013 | ETL | Write `src/common/udfs.py` | TASK-009 | NFR-009, NFR-011 | §9 Configuration Management |
| TASK-014 | ETL | Write `src/etl/nb_extract_watermark.py` | TASK-009, TASK-001, TASK-002 | FR-002, FR-003, NFR-009 | §2 Workflow Task Sequence, §6 Lineage Propagation |
| TASK-015 | ETL | Write `src/etl/nb_extract_purchase.py` | TASK-009, TASK-003, TASK-014 | FR-001, FR-006, CALC-001, CALC-005, NFR-009 | §2 Workflow Task Sequence |
| TASK-016 | ETL | Write `src/etl/migrate_staged_purchase_data.py` | TASK-011, TASK-012, TASK-014, TASK-015 | FR-007, FR-008, NFR-003 through NFR-007, NFR-009, DQR-001 through DQR-009 | §4 MERGE INTO Pattern, §5 QA Assertion Chain |
| TASK-017 | ETL | Write `src/init/reseed_purchase_environment.py` | TASK-001, TASK-002, TASK-003, TASK-004, TASK-005 | FR-011, NFR-002 | §7 DDL Reference |
| TASK-018 | config | Write `config/environment.yaml` | — | FR-008, FR-009, NFR-009 | §9 Configuration Management |
| TASK-019 | config | Write Databricks Workflow JSON `config/workflows/nightly_etl_purchase.json` | TASK-014, TASK-015, TASK-016 | FR-002, FR-003, NFR-001 | §2 Workflow Task Sequence |
| TASK-020 | test | Write `tests/common/test_sk_resolver.py` | TASK-011 | FR-004, FR-005, DQR-009 | §3 SK Resolution Pattern |
| TASK-021 | test | Write `tests/common/test_udfs.py` | TASK-013 | NFR-009 | §9 Configuration Management |
| TASK-022 | test | Write `tests/etl/test_migrate_staged_purchase_data.py` | TASK-016 | NFR-003, NFR-004, NFR-005, NFR-006, DQR-001 through DQR-007 | §4 MERGE INTO Pattern, §5 QA Assertion Chain |
| TASK-023 | BI | Power BI report reconnection spec: `wwidw_purchase_and_sale_per_stockitem_dynamic` | TASK-005 | FR-010 | §8 Mart Layer |
| TASK-024 | BI | Power BI report reconnection spec: `wwidw_ordered_by_supplier` | TASK-005 | FR-010 | §8 Mart Layer |
| TASK-025 | docs | Write `docs/design.md` (ETL design document) | TASK-016 | NFR-011 | §1–§9 All sections |
| TASK-026 | docs | Write `docs/data-dictionary.md` | TASK-005 | NFR-011 | §7 DDL Reference |

| TASK-027 | MART | Create mart view `v_purchase_by_supplier` | TASK-005 | FR-010 | §8 Mart Layer |
| TASK-028 | MART | Create mart view `v_purchase_per_stock_item` | TASK-005 | FR-010 | §8 Mart Layer |
| TASK-029 | MART | Write `nb_refresh_v_purchase_by_supplier.py` | TASK-027 | FR-010, NFR-001 | §8 Mart Layer |
| TASK-030 | MART | Write `nb_refresh_v_purchase_per_stock_item.py` | TASK-028 | FR-010, NFR-001 | §8 Mart Layer |
| TASK-031 | MART | Write `nb_validate_mart_views.py` | TASK-029, TASK-030 | FR-010, NFR-001 | §8 Mart Layer |
| TASK-032 | DQ | Write `src/etl/dq/dq_engine.py` | TASK-004, TASK-005 | NFR-004, NFR-005, DQR-001, DQR-002, DQR-003, DQR-006 | §5 QA Assertion Chain |
| TASK-033 | DQ | Write `src/etl/dq/nb_dq_purchase.py` | TASK-032 | DQR-001, DQR-005, DQR-006 | §5 QA Assertion Chain |
| TASK-034 | DQ | Write `src/etl/dq/nb_dq_rejection_report.py` | TASK-033 | NFR-007, DQR-004 | §5 QA Assertion Chain |

**Total: 34 tasks** | DDL: 8 | ETL: 9 | MART: 5 | DQ: 3 | Config: 2 | Test: 3 | BI: 2 | Docs: 2

---

## Task Details

---

### TASK-001 — Create `bronze.lineage_run` table

**Type:** DDL  
**Depends On:** —  
**Requirements:** FR-003, NFR-007  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/ddl/bronze_lineage_run.sql`

**Description:**
Create the `inventory_stock.bronze.lineage_run` Delta table. This table stores one row per ETL run for end-to-end auditability. The `lineage_key` column is a `BIGINT GENERATED ALWAYS AS IDENTITY` surrogate key that replaces the legacy sequence object. Change Data Feed must be enabled to support downstream lineage tracking queries.

**DDL:**
```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_lineage_run.sql
-- PURPOSE  : ETL audit log; one row per run; IDENTITY PK
-- SOURCE   : (no source object — new table)
-- TARGET   : inventory_stock.bronze.lineage_run (Databricks Delta Lake)
-- RULES    : LN-001, LN-002, OB-004, TY-017, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.bronze.lineage_run (
    lineage_key              BIGINT       GENERATED ALWAYS AS IDENTITY  NOT NULL,
    etl_run_id               STRING       NOT NULL,
    table_name               STRING       NOT NULL,
    pipeline_name            STRING       NOT NULL,
    data_load_started        TIMESTAMP    NOT NULL,
    data_load_completed      TIMESTAMP    NULL,
    was_successful           BOOLEAN      NULL,
    table_row_count          BIGINT       NULL,
    source_system_cutoff_time TIMESTAMP   NOT NULL,
    CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)
)
USING DELTA
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true'
);
```

**Acceptance:** `DESCRIBE TABLE inventory_stock.bronze.lineage_run` returns all 9 columns with correct types; `SHOW TBLPROPERTIES` returns `delta.enableChangeDataFeed = true`.

---

### TASK-002 — Create `bronze.etl_cutoff` table

**Type:** DDL  
**Depends On:** —  
**Requirements:** FR-002, NFR-001  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/ddl/bronze_etl_cutoff.sql`

**Description:**
Create the `inventory_stock.bronze.etl_cutoff` Delta table. This is the high-watermark control table. Each row tracks the latest successfully processed cutoff timestamp for a named target table. `nb_extract_watermark` reads from this table at the start of each run.

**DDL:**
```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : bronze_etl_cutoff.sql
-- PURPOSE  : Watermark control table; one row per tracked table
-- SOURCE   : (no source object — new table)
-- TARGET   : inventory_stock.bronze.etl_cutoff (Databricks Delta Lake)
-- RULES    : LN-005, OB-004, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_stock.bronze.etl_cutoff (
    table_name       STRING     NOT NULL,
    cutoff_time      TIMESTAMP  NOT NULL,
    last_updated_utc TIMESTAMP  NOT NULL
)
USING DELTA;
```

**Acceptance:** Table exists; `SELECT * FROM bronze.etl_cutoff WHERE table_name = 'fact_purchase'` after reseed returns the configured `initial_load_date` as `cutoff_time`.

---

### TASK-003 — Create `bronze.purchase_staging` table

**Type:** DDL  
**Depends On:** TASK-001, TASK-002  
**Requirements:** FR-001, FR-003  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/ddl/bronze_purchase_staging.sql`

**Description:**
Create the `inventory_stock.bronze.purchase_staging` Delta table. This is the ephemeral landing table for incremental purchase order extract data. It is written in OVERWRITE mode on every run — there is no incremental append. Includes `lineage_key` and `_extracted_at_utc` audit columns per OB-P002. `purchase_staging_key` is a Delta-managed IDENTITY PK. No liquid clustering is applied to bronze staging tables.

**DDL:**
```sql
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
    'delta.autoOptimize.autoCompact' = 'false'
);
```

**Acceptance:** Table exists with all 15 columns; after `nb_extract_purchase` runs, all rows share the same `_extracted_at_utc` timestamp for a given run.

---

### TASK-004 — Create `bronze.dq_rejections` table

**Type:** DDL  
**Depends On:** TASK-001  
**Requirements:** NFR-004, NFR-005, NFR-007, DQR-008  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/ddl/bronze_dq_rejections.sql`

**Description:**
Create the `inventory_stock.bronze.dq_rejections` Delta table. This is the centralised DQ rejection sink. Violation rows from QA-P001 through QA-P004 are appended here with `lineage_key`, `rule_id`, source table, PK, and column detail. Uses IDENTITY PK and autoOptimize.

**DDL:**
```sql
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
```

**Acceptance:** `DESCRIBE TABLE bronze.dq_rejections` returns all 10 columns with correct types and comments.

---

### TASK-005 — Create `silver_fact.fact_purchase` table

**Type:** DDL  
**Depends On:** TASK-001  
**Requirements:** FR-007, NFR-001, NFR-012  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/ddl/silver_fact_fact_purchase.sql`

**Description:**
Create the `inventory_stock.silver_fact.fact_purchase` Delta managed table. This is the central grain-level fact table. CLUSTER BY (date_key, supplier_key) for DBR 13.3+. Fallback strategy for pre-DBR 13.3: PARTITIONED BY (date_key) ZORDER BY (supplier_key, stock_item_key). AutoOptimize and autoCompact enabled. IDENTITY surrogate PK.

**DDL:**
```sql
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
    'delta.autoOptimize.autoCompact' = 'true'
);
-- Fallback for pre-DBR 13.3 (remove CLUSTER BY, use instead):
-- PARTITIONED BY (date_key)
-- ZORDER BY (supplier_key, stock_item_key) -- applied via post-DDL OPTIMIZE command
```

**Acceptance:** Table exists with all 11 columns; `DESCRIBE DETAIL` shows liquid clustering is enabled.

---

### TASK-006 — Create `silver_dim.supplier_current` view

**Type:** DDL  
**Depends On:** —  
**Requirements:** FR-004  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/ddl/silver_dim_supplier_current.sql`

**Description:**
Create `inventory_stock.silver_dim.supplier_current` as a regular (non-materialized) view that pre-filters `silver_dim.supplier` to rows where `is_current_row = TRUE`. This is a thin row-filter wrapper with no aggregation — it must NOT be created as a MATERIALIZED VIEW (per OB-P003). Any future Gold-layer analytics views that aggregate must use `CREATE OR REPLACE MATERIALIZED VIEW`.

**DDL:**
```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : silver_dim_supplier_current.sql
-- PURPOSE  : Current-version SCD-2 filter view for supplier dimension
-- SOURCE   : (new view)
-- TARGET   : inventory_stock.silver_dim.supplier_current (Databricks Delta Lake)
-- RULES    : OB-001, OB-P003, PE-004, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE OR REPLACE VIEW inventory_stock.silver_dim.supplier_current AS
SELECT *
FROM inventory_stock.silver_dim.supplier
WHERE is_current_row = TRUE;
```

**Acceptance:** `SELECT COUNT(*) FROM silver_dim.supplier_current WHERE is_current_row = FALSE` returns 0.

---

### TASK-007 — Create `silver_dim.stock_item_current` view

**Type:** DDL  
**Depends On:** —  
**Requirements:** FR-005  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/ddl/silver_dim_stock_item_current.sql`

**Description:**
Create `inventory_stock.silver_dim.stock_item_current` as a regular view pre-filtering `silver_dim.stock_item` to `is_current_row = TRUE`. Same pattern and constraints as TASK-006.

**DDL:**
```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : silver_dim_stock_item_current.sql
-- PURPOSE  : Current-version SCD-2 filter view for stock_item dimension
-- SOURCE   : (new view)
-- TARGET   : inventory_stock.silver_dim.stock_item_current (Databricks Delta Lake)
-- RULES    : OB-001, OB-P003, PE-004, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================
CREATE OR REPLACE VIEW inventory_stock.silver_dim.stock_item_current AS
SELECT *
FROM inventory_stock.silver_dim.stock_item
WHERE is_current_row = TRUE;
```

**Acceptance:** `SELECT COUNT(*) FROM silver_dim.stock_item_current WHERE is_current_row = FALSE` returns 0.

---

### TASK-008 — Generate GRANT statements for Unity Catalog access

**Type:** DDL  
**Depends On:** TASK-001, TASK-003, TASK-004, TASK-005  
**Requirements:** NFR-008  
**Design reference:** §7 DDL Reference  
**Output File:** `src/db/grants/purchase_grants.sql`

**Description:**
Generate Unity Catalog GRANT statements implementing the three-tier access model: (1) BI service principal and `data_analysts` group read access to `silver_fact.fact_purchase`, `silver_dim.supplier`, `silver_dim.stock_item`, `silver_dim.date`; (2) ETL service principal access to `bronze.*`, `silver_fact.*`; (3) `data_engineering` group read access to `bronze.dq_rejections`. Role names are placeholders — substitute actual Unity Catalog principal names before execution.

**DDL:**
```sql
-- ============================================================
-- PROJECT  : Inventory_Stock_Project
-- PRODUCT  : Purchase
-- FILE     : purchase_grants.sql
-- PURPOSE  : Unity Catalog GRANT statements for Purchase product access tiers
-- SOURCE   : (no source object)
-- TARGET   : inventory_stock catalog (Databricks Unity Catalog)
-- RULES    : SE-001, SE-002, NFR-008, NM-001, CX-P006
-- GENERATED: 2026-09-07
-- ============================================================

-- Tier 1: BI analysts — read access to silver serving layer
GRANT SELECT ON TABLE inventory_stock.silver_fact.fact_purchase TO `{{BI_SERVICE_PRINCIPAL}}`;
GRANT SELECT ON TABLE inventory_stock.silver_fact.fact_purchase TO `data_analysts`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.supplier TO `{{BI_SERVICE_PRINCIPAL}}`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.supplier TO `data_analysts`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.stock_item TO `{{BI_SERVICE_PRINCIPAL}}`;
GRANT SELECT ON TABLE inventory_stock.silver_dim.date TO `{{BI_SERVICE_PRINCIPAL}}`;

-- Tier 2: ETL service principal — full access to bronze and silver_fact
GRANT SELECT, MODIFY ON SCHEMA inventory_stock.bronze TO `{{ETL_SERVICE_PRINCIPAL}}`;
GRANT SELECT, MODIFY ON SCHEMA inventory_stock.silver_fact TO `{{ETL_SERVICE_PRINCIPAL}}`;

-- Tier 3: data engineering team — read access to DQ rejections
GRANT SELECT ON TABLE inventory_stock.bronze.dq_rejections TO `data_engineering`;
```

**Acceptance:** BI service principal can execute `SELECT COUNT(*) FROM silver_fact.fact_purchase`; same principal receives `PERMISSION_DENIED` on `bronze.purchase_staging`.

---

### TASK-009 — Write `src/common/constants.py`

**Type:** ETL  
**Depends On:** TASK-001, TASK-003, TASK-005  
**Requirements:** NFR-009, NFR-011  
**Design reference:** §9 Configuration Management  
**Output File:** `src/common/constants.py`

**Description:**
Write the Python constants module that centralises all fully-qualified table names and schema references used across Purchase ETL notebooks. This module is imported by every ETL notebook at startup to avoid hard-coded table name strings. Includes `CATALOG`, `BRONZE_SCHEMA`, `SILVER_DIM_SCHEMA`, `SILVER_FACT_SCHEMA` constants and derived table name constants.

**Content (key constants):**
```python
CATALOG = "inventory_stock"
BRONZE_SCHEMA = f"{CATALOG}.bronze"
SILVER_DIM_SCHEMA = f"{CATALOG}.silver_dim"
SILVER_FACT_SCHEMA = f"{CATALOG}.silver_fact"

PURCHASE_STAGING_TABLE = f"{BRONZE_SCHEMA}.purchase_staging"
ETL_CUTOFF_TABLE = f"{BRONZE_SCHEMA}.etl_cutoff"
LINEAGE_RUN_TABLE = f"{BRONZE_SCHEMA}.lineage_run"
DQ_REJECTIONS_TABLE = f"{BRONZE_SCHEMA}.dq_rejections"

SUPPLIER_DIM_TABLE = f"{SILVER_DIM_SCHEMA}.supplier"
STOCK_ITEM_DIM_TABLE = f"{SILVER_DIM_SCHEMA}.stock_item"
DATE_DIM_TABLE = f"{SILVER_DIM_SCHEMA}.date"
FACT_PURCHASE_TABLE = f"{SILVER_FACT_SCHEMA}.fact_purchase"

ETL_CUTOFF_TABLE_NAME = "fact_purchase"
```

**Acceptance:** `from src.common.constants import FACT_PURCHASE_TABLE` returns `"inventory_stock.silver_fact.fact_purchase"` without error.

---

### TASK-010 — Write `src/common/scd2_merge.py`

**Type:** ETL  
**Depends On:** —  
**Requirements:** FR-004, FR-005  
**Design reference:** §3 SK Resolution Pattern  
**Output File:** `src/common/scd2_merge.py`

**Description:**
Write the SCD-2 merge helper module. This module provides the `apply_scd2_merge(spark, target_table, source_df, business_key_col, natural_key_col)` function that performs the standard SCD-2 MERGE INTO pattern: close the current version of a matching business key by setting `is_current_row = FALSE`, `valid_to = current_date() - 1`, `row_expiry_date = current_date() - 1`; then insert the new version. Used by the dimension load process (externally owned for supplier and stock_item; included here as a shared helper per OB-P004).

**Acceptance:** Unit test: apply_scd2_merge on a test Delta table with a known existing row produces a new row with `is_current_row = TRUE` and the prior row with `is_current_row = FALSE`.

---

### TASK-011 — Write `src/common/sk_resolver.py`

**Type:** ETL  
**Depends On:** TASK-009  
**Requirements:** FR-004, FR-005, DQR-009  
**Design reference:** §3 SK Resolution Pattern  
**Output File:** `src/common/sk_resolver.py`

**Description:**
Write the surrogate key resolver helper. Implements `resolve_supplier_key(staging_df, supplier_dim_df)` and `resolve_stock_item_key(staging_df, stock_item_dim_df)`. Each function performs:
1. LEFT JOIN staging to dimension on business key AND temporal range predicate: `last_modified_when > CAST(valid_from AS TIMESTAMP) AND last_modified_when <= CAST(valid_to AS TIMESTAMP)`.
2. `ROW_NUMBER() OVER (PARTITION BY stg.purchase_staging_key ORDER BY dim.valid_from DESC) = 1` to select the most recent valid version when multiple versions overlap the transaction timestamp.
3. `COALESCE(dim.supplier_key, 0)` / `COALESCE(dim.stock_item_key, 0)` — returns 0 for unresolved rows.

The BROADCAST hint is applied to dimension DataFrames per PE-006.
`valid_from`/`valid_to` are DATE-typed in the dimension (per TY-P001 override); they must be explicitly cast to TIMESTAMP before the temporal range comparison.

**Acceptance:** 
- Test: staging row with `last_modified_when` within a known dimension version's validity range resolves to non-zero key.
- Test: staging row with `last_modified_when` outside all dimension version ranges resolves to key=0.
- Test: staging row with `last_modified_when` overlapping two dimension versions resolves to the most recent version (highest `valid_from`).
- Test: no staging row has NULL for `supplier_key` or `stock_item_key` after resolution.

---

### TASK-012 — Write `src/common/fact_merge.py`

**Type:** ETL  
**Depends On:** TASK-009  
**Requirements:** FR-007, NFR-003  
**Design reference:** §4 MERGE INTO Pattern  
**Output File:** `src/common/fact_merge.py`

**Description:**
Write the fact merge helper. Implements `merge_fact_purchase(spark, staging_table, fact_table)` that executes the `MERGE INTO inventory_stock.silver_fact.fact_purchase` statement keyed on `wwi_purchase_order_id`. Returns `rows_merged` (count of rows inserted or updated). The MERGE is idempotent for the same `wwi_purchase_order_id`. After MERGE, `rows_merged` is used for QA-P001 row count reconciliation.

**MERGE predicate:** `ON target.wwi_purchase_order_id = source.wwi_purchase_order_id`

**WHEN MATCHED:** UPDATE all mutable columns (date_key, supplier_key, stock_item_key, ordered_outers, ordered_quantity, received_outers, package, is_order_finalized, lineage_key)

**WHEN NOT MATCHED:** INSERT all columns except purchase_key (IDENTITY).

**Acceptance:** 
- Test: running merge twice with the same staging produces the same fact row count.
- Test: function returns the correct `rows_merged` count after MERGE.
- Test: `rows_merged` written to `bronze.lineage_run.table_row_count` for the current run.

---

### TASK-013 — Write `src/common/udfs.py`

**Type:** ETL  
**Depends On:** TASK-009  
**Requirements:** NFR-009, NFR-011  
**Design reference:** §9 Configuration Management  
**Output File:** `src/common/udfs.py`

**Description:**
Write the consolidated NULL-guarded Python UDF module. Contains UDFs consolidating duplicate scalar function patterns identified across Purchase ETL notebooks (date-format transforms, string normalisation, numeric coercion). Each UDF must: (1) return `None` on `None` input (explicit NULL guard); (2) handle empty string input; (3) include a docstring citing the function's business purpose; (4) be registered as a Spark SQL UDF if needed in SQL notebooks. All UDFs reside in this single module.

**Required UDFs (minimum):**
- `format_date_key(dt)` — converts a TIMESTAMP or DATE to ISO DATE string format for date_key derivation.
- `safe_trim(s)` — strips whitespace with None-guard; used for package name normalisation.

**Acceptance:**
- `format_date_key(None)` returns `None`.
- `safe_trim(None)` returns `None`.
- `safe_trim("")` returns `""`.
- No duplicate scalar function body exists in `src/etl/` notebooks (static scan).

---

### TASK-014 — Write `src/etl/nb_extract_watermark.py`

**Type:** ETL  
**Depends On:** TASK-009, TASK-001, TASK-002  
**Requirements:** FR-002, FR-003, NFR-009  
**Design reference:** §2 Workflow Task Sequence, §6 Lineage Propagation  
**Output File:** `src/etl/nb_extract_watermark.py`

**Description:**
Write the watermark extraction notebook. This is the first task in the Databricks Workflow.

**Skeleton (CX-P005):**
1. **IMPORTS** — `from src.common.constants import *`; `from src.common.lineage_utils import open_lineage_record`; `from src.common.etl_control import get_last_etl_cutoff_time, set_etl_cutoff`; load `config/environment.yaml`.
2. **COMPUTE EXTRACT WINDOW** — `last_cutoff = get_last_etl_cutoff_time(spark, ETL_CUTOFF_TABLE, ETL_CUTOFF_TABLE_NAME)` (default: `INITIAL_LOAD_DATE` from config if no row); `current_cutoff = CURRENT_TIMESTAMP()`.
3. **OPEN LINEAGE RECORD** — `lineage_key = open_lineage_record(spark, LINEAGE_RUN_TABLE, "fact_purchase", "nightly_etl_purchase", current_cutoff)`.
4. **PUBLISH VIA TASKVALUES** — `dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_key)`; `dbutils.jobs.taskValues.set(key="last_cutoff", value=str(last_cutoff))`; `dbutils.jobs.taskValues.set(key="current_cutoff", value=str(current_cutoff))`.

**Note:** This notebook does NOT have the zero-rows guard (it extracts the watermark, not staging data). It also does NOT receive `lineage_key` via `taskValues.get` — it generates the lineage_key.

**Acceptance:** After execution, `bronze.lineage_run` contains a new row with `was_successful = NULL` (run in progress) and `dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")` returns a non-null BIGINT.

---

### TASK-015 — Write `src/etl/nb_extract_purchase.py`

**Type:** ETL  
**Depends On:** TASK-009, TASK-003, TASK-014  
**Requirements:** FR-001, FR-006, NFR-009  
**Design reference:** §2 Workflow Task Sequence  
**Output File:** `src/etl/nb_extract_purchase.py`

**Description:**
Write the purchase extract notebook. Extracts incremental purchase order rows from the upstream source system filtered by the watermark window and writes them to `bronze.purchase_staging` in OVERWRITE mode.

**Skeleton (CX-P005):**
1. **IMPORTS** — constants, config.
2. **LINEAGE KEY** — `lineage_key = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")`.
3. **WATERMARK BOUNDS** — `last_cutoff = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="last_cutoff")`; `current_cutoff = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="current_cutoff")`.
4. **ZERO-ROWS GUARD** — Check source row count before extract; exit with `"SKIPPED: zero rows"` if empty.
5. **EXTRACT** — JDBC query with `WHERE last_modified_when > last_cutoff AND last_modified_when <= current_cutoff`; derive `date_key = CAST(order_date AS DATE)`; add `lineage_key` and `_extracted_at_utc = current_timestamp()`.
6. **WRITE STAGING** — `spark.write.format("delta").mode("overwrite").saveAsTable(PURCHASE_STAGING_TABLE)`.

**Acceptance:** After execution, `SELECT COUNT(*) FROM bronze.purchase_staging` > 0 for a non-empty batch; all rows share the same `_extracted_at_utc`; no row has `NULL` for `lineage_key`.

---

### TASK-016 — Write `src/etl/migrate_staged_purchase_data.py`

**Type:** ETL  
**Depends On:** TASK-011, TASK-012, TASK-014, TASK-015  
**Requirements:** FR-007, FR-008, NFR-003, NFR-004, NFR-005, NFR-006, NFR-007, NFR-009, DQR-001 through DQR-009  
**Design reference:** §4 MERGE INTO Pattern, §5 QA Assertion Chain  
**Output File:** `src/etl/migrate_staged_purchase_data.py`

**Description:**
Write the main ETL orchestration notebook. This is the third and final task in the Databricks Workflow.

**Skeleton (CX-P005):**
1. **IMPORTS** — constants, sk_resolver, fact_merge, lineage_utils, QA utilities; load config.
2. **LINEAGE KEY** — `lineage_key = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")`.
3. **ZERO-ROWS GUARD** — `staging_count = spark.sql(f"SELECT COUNT(*) FROM {PURCHASE_STAGING_TABLE}").collect()[0][0]`; exit `"SKIPPED: zero rows"` if 0.
4. **MAIN ETL LOGIC** — wrapped in `try/except`:
   - Load staging DataFrame and dimension DataFrames.
   - `staging_df = resolve_supplier_key(staging_df, broadcast(supplier_dim))`.
   - `staging_df = resolve_stock_item_key(staging_df, broadcast(stock_item_dim))`.
   - `rows_merged = merge_fact_purchase(spark, PURCHASE_STAGING_TABLE, FACT_PURCHASE_TABLE)`.
   - QA-P001: assert `rows_merged == staging_count` (RuntimeError on mismatch).
   - QA-P002: orphaned SK detection (supplier_key, stock_item_key) — log WARNING.
   - QA-P003: RI checks (date_key, supplier_key, stock_item_key) — write violations to dq_rejections.
   - QA-P004: business rule assertions (negative qty, out-of-window date, null package) — log WARNING.
   - QA-P005: post-run DQ rejection summary query — log to notebook output.
   - On exception: `close_lineage_record(spark, lineage_key, rows_merged=0, succeeded=False)`; raise.
5. **CONDITIONAL OPTIMIZE** — `if rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD: spark.sql(f"OPTIMIZE {FACT_PURCHASE_TABLE}")`.
6. **CLOSE LINEAGE** — `close_lineage_record(spark, lineage_key, rows_merged=rows_merged, succeeded=True)`; `set_etl_cutoff(spark, ETL_CUTOFF_TABLE, ETL_CUTOFF_TABLE_NAME, current_cutoff)`.

**Acceptance:** See DQR-001 through DQR-009 acceptance criteria. QV-001 through QV-009 must all pass.

---

### TASK-017 — Write `src/init/reseed_purchase_environment.py`

**Type:** ETL  
**Depends On:** TASK-001, TASK-002, TASK-003, TASK-004, TASK-005  
**Requirements:** FR-011, NFR-002  
**Design reference:** §7 DDL Reference  
**Output File:** `src/init/reseed_purchase_environment.py`

**Description:**
Write the environment initialisation notebook. This notebook (a) creates all required Bronze and Silver tables using `CREATE TABLE IF NOT EXISTS` (or delegates to DDL scripts); (b) inserts `key=0` sentinel rows into `silver_dim.supplier` and `silver_dim.stock_item` representing the unknown-member record; (c) resets `bronze.etl_cutoff` to `initial_load_date` from config. This notebook requires explicit scope-owner sign-off (PD-002) before execution in production.

**Sentinel row (supplier key=0):**
```python
spark.sql(f"""
INSERT INTO inventory_stock.silver_dim.supplier
(supplier_key, wwi_supplier_id, supplier, is_current_row, valid_from, valid_to,
 row_effective_date, row_expiry_date, lineage_key)
SELECT 0, 0, 'Unknown', TRUE, '1900-01-01', '9999-12-31',
       '1900-01-01', '9999-12-31', 0
WHERE NOT EXISTS (
    SELECT 1 FROM inventory_stock.silver_dim.supplier WHERE supplier_key = 0
)
""")
```

**Acceptance:** After execution: (1) all required tables exist; (2) `SELECT * FROM silver_dim.supplier WHERE supplier_key = 0` returns exactly one row; (3) `SELECT cutoff_time FROM bronze.etl_cutoff WHERE table_name = 'fact_purchase'` returns the configured `initial_load_date`.

---

### TASK-018 — Write `config/environment.yaml`

**Type:** config  
**Depends On:** —  
**Requirements:** FR-008, FR-009, NFR-009  
**Design reference:** §9 Configuration Management  
**Output File:** `config/environment.yaml`

**Description:**
Write the externalised configuration file. All date filter boundaries and business validation parameters that would otherwise be hard-coded in ETL notebooks must be defined here. ETL notebooks load this file at startup using `yaml.safe_load`.

**Required content:**
```yaml
purchase:
  etl:
    initial_load_date: "1900-01-01"
    batch_lookback_days: 1
    fact_optimize_row_threshold: 10000
  business_rules:
    # Add business factors here as they are identified during implementation
    # Each entry must have: lower_bound, upper_bound, description
```

**Acceptance:** `cfg["purchase"]["etl"]["initial_load_date"]` is not None; `cfg["purchase"]["etl"]["fact_optimize_row_threshold"]` equals 10000; no hard-coded date literals exist in `src/etl/` notebooks.

---

### TASK-019 — Write Databricks Workflow JSON `config/workflows/nightly_etl_purchase.json`

**Type:** config  
**Depends On:** TASK-014, TASK-015, TASK-016  
**Requirements:** FR-002, FR-003, NFR-001  
**Design reference:** §2 Workflow Task Sequence  
**Output File:** `config/workflows/nightly_etl_purchase.json`

**Description:**
Write the Databricks Workflow JSON definition for the nightly purchase ETL job. Three tasks with explicit dependency chain: `nb_extract_watermark` → `nb_extract_purchase` → `migrate_staged_purchase_data`. The dimension load tasks (`supplier_load`, `stock_item_load`) are declared as upstream dependencies of `migrate_staged_purchase_data` but are owned by external products — referenced by task name only.

**Key configuration:**
- Schedule: `0 2 * * *` (daily 02:00 UTC)
- Runtime: DBR 13.3 LTS or later (for Liquid Clustering)
- `max_retries: 2` on `nb_extract_watermark` and `nb_extract_purchase`; `max_retries: 0` on QA-gated task `migrate_staged_purchase_data`
- Task type: `notebook_task` for all three tasks

**Acceptance:** Workflow JSON is valid Databricks REST API v2.1 format; three tasks present in correct dependency order; schedule field is correct cron expression.

---

### TASK-020 — Write `tests/common/test_sk_resolver.py`

**Type:** test  
**Depends On:** TASK-011  
**Requirements:** FR-004, FR-005, DQR-009  
**Design reference:** §3 SK Resolution Pattern  
**Output File:** `tests/common/test_sk_resolver.py`

**Description:**
Write unit tests for `src/common/sk_resolver.py`. Tests must cover:
1. **Temporal range match** — staging row with `last_modified_when` within a known dimension version's validity range resolves to non-zero `supplier_key`.
2. **No match → key=0** — staging row with `last_modified_when` outside all dimension version ranges resolves to `supplier_key = 0`.
3. **Tie-breaker (DESC)** — staging row whose `last_modified_when` overlaps two dimension versions resolves to the most recent version (highest `valid_from`).
4. **NULL guard** — after resolution, `SELECT COUNT(*) FROM result WHERE supplier_key IS NULL` = 0.
5. Same four tests for `resolve_stock_item_key`.

Use `pyspark.sql.SparkSession` fixture with a local test schema; do not connect to a live cluster.

**Acceptance:** All 8 test cases pass; `pytest tests/common/test_sk_resolver.py` exits 0.

---

### TASK-021 — Write `tests/common/test_udfs.py`

**Type:** test  
**Depends On:** TASK-013  
**Requirements:** NFR-009  
**Design reference:** §9 Configuration Management  
**Output File:** `tests/common/test_udfs.py`

**Description:**
Write unit tests for `src/common/udfs.py`. Each UDF must be tested for:
1. `None` input → returns `None` (NULL guard).
2. Empty string input → correct return.
3. Boundary value input → correct return.
4. Representative valid input → correct return.

**Acceptance:** All UDF unit tests pass; `pytest tests/common/test_udfs.py` exits 0.

---

### TASK-022 — Write `tests/etl/test_migrate_staged_purchase_data.py`

**Type:** test  
**Depends On:** TASK-016  
**Requirements:** NFR-003, NFR-004, NFR-005, NFR-006, DQR-001 through DQR-007  
**Design reference:** §4 MERGE INTO Pattern, §5 QA Assertion Chain  
**Output File:** `tests/etl/test_migrate_staged_purchase_data.py`

**Description:**
Write integration tests for the main ETL notebook. Tests use a local SparkSession with Delta tables written to a temp directory. Required test cases:
1. **QA-P001 pass** — staging count equals merged count; no RuntimeError raised.
2. **QA-P001 fail** — injected mismatch between staging count and rows_merged raises `RuntimeError` with message `Row count mismatch: staging=N, inserted=M`.
3. **QA-P003 RI violation** — load a fact row with a supplier_key absent from the dimension; assert rejection row written to dq_rejections with `rule_id = 'QA-P003'` and correct `lineage_key`.
4. **QA-P004 negative qty** — load a row with `ordered_outers = -1`; assert WARNING log entry and pipeline succeeds.
5. **QA-P004 null package** — load a row with `package = NULL`; assert WARNING log entry and pipeline succeeds.
6. **Lineage closed on exception** — inject exception in main ETL; assert `close_lineage_record` called with `succeeded=False`.

**Acceptance:** All 6 test cases pass; `pytest tests/etl/test_migrate_staged_purchase_data.py` exits 0.

---

### TASK-023 — Power BI report reconnection spec: `wwidw_purchase_and_sale_per_stockitem_dynamic`

**Type:** BI  
**Depends On:** TASK-005  
**Requirements:** FR-010  
**Design reference:** §8 Mart Layer  
**Output File:** `docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md`

**Description:**
Produce a reconnection specification document for the `wwidw_purchase_and_sale_per_stockitem_dynamic` Power BI report. The document must specify: (1) the Databricks SQL Warehouse endpoint and connection string; (2) the table mapping from prior connection to `inventory_stock.silver_fact.fact_purchase` and `inventory_stock.silver_fact.fact_sale` (Sales_Orders product — external dependency); (3) column name mapping for all columns used by the report; (4) the coordinated cutover requirement with the Sales_Orders product. This report requires both products to be available before the Power BI reconnection is made.

**Acceptance:** Document exists; table and column mappings are complete; cross-product dependency is documented with the Sales_Orders product team.

---

### TASK-024 — Power BI report reconnection spec: `wwidw_ordered_by_supplier`

**Type:** BI  
**Depends On:** TASK-005  
**Requirements:** FR-010  
**Design reference:** §8 Mart Layer  
**Output File:** `docs/bi/wwidw_ordered_by_supplier_reconnection.md`

**Description:**
Produce a reconnection specification document for the `wwidw_ordered_by_supplier` Power BI report. Same structure as TASK-023 but for the supplier performance report. This report is self-contained within the Purchase product (no cross-product dependency). Tables: `inventory_stock.silver_fact.fact_purchase`, `inventory_stock.silver_dim.supplier`. Column name mappings must be documented.

**Acceptance:** Document exists; all column mappings are complete; no cross-product dependency noted.

---

### TASK-025 — Write `docs/design.md`

**Type:** docs  
**Depends On:** TASK-016  
**Requirements:** NFR-011  
**Design reference:** §1–§9 All sections  
**Output File:** `docs/design.md`

**Description:**
Write the ETL design document for the Purchase product. Covers: (1) architecture overview (medallion layers); (2) Workflow task sequence and dependency graph; (3) SK resolution pattern (temporal range join); (4) MERGE INTO pattern; (5) QA assertion chain; (6) lineage propagation pattern; (7) configuration management approach. References transformation rule IDs throughout.

**Acceptance:** Document exists and covers all 7 topics; all table and column names use target-system conventions.

---

### TASK-026 — Write `docs/data-dictionary.md`

**Type:** docs  
**Depends On:** TASK-005  
**Requirements:** NFR-011  
**Design reference:** §7 DDL Reference  
**Output File:** `docs/data-dictionary.md`

**Description:**
Write the column-level data dictionary for `inventory_stock.silver_fact.fact_purchase` and all Bronze control tables. For each column: name, data type, nullable, description, business meaning, and derivation source (calculated / pass-through). Include the lineage_key and _extracted_at_utc audit columns with their derivation explanations.

**Acceptance:** Document exists; all 11 columns of `fact_purchase` are documented with correct data types; lineage_key and _extracted_at_utc columns include derivation descriptions.

---

---

### TASK-027 — Create `mart.v_purchase_by_supplier` Materialized View

**Type:** MART (DDL)
**Depends On:** TASK-005
**Requirements:** FR-010, NFR-001
**Design reference:** §8 Mart Layer
**Output File:** `src/db/ddl/mart/v_purchase_by_supplier.sql`

**Description:**
Create `CREATE OR REPLACE MATERIALIZED VIEW inventory_stock.mart.v_purchase_by_supplier`. Join `silver_fact.fact_purchase` to `silver_dim.supplier` (on `supplier_key`) and `silver_dim.stock_item` (on `stock_item_key`). Aggregate: `SUM(ordered_quantity) AS total_quantity_ordered`, `COUNT(DISTINCT purchase_key) AS purchase_order_count`. GROUP BY all dimension attributes from supplier and stock_item. Add COMMENT. Serves the `wwidw_ordered_by_supplier` BI report.

**DDL (key structure):**
```sql
CREATE OR REPLACE MATERIALIZED VIEW inventory_stock.mart.v_purchase_by_supplier
COMMENT 'Aggregated purchase volume by supplier and stock item — serves wwidw_ordered_by_supplier report'
AS
SELECT
    s.wwi_supplier_id,
    s.supplier_name,
    s.supplier_category_name,
    si.wwi_stock_item_id,
    si.stock_item_name,
    si.color,
    si.unit_package_name,
    SUM(f.ordered_quantity)       AS total_quantity_ordered,
    COUNT(DISTINCT f.purchase_key) AS purchase_order_count
FROM inventory_stock.silver_fact.fact_purchase f
JOIN inventory_stock.silver_dim.supplier s
    ON f.supplier_key = s.supplier_key AND s.is_current_row = TRUE
JOIN inventory_stock.silver_dim.stock_item si
    ON f.stock_item_key = si.stock_item_key AND si.is_current_row = TRUE
GROUP BY
    s.wwi_supplier_id, s.supplier_name, s.supplier_category_name,
    si.wwi_stock_item_id, si.stock_item_name, si.color, si.unit_package_name;
```

**Acceptance:** `SELECT COUNT(*) FROM inventory_stock.mart.v_purchase_by_supplier` returns a non-negative integer after a fact load; `REFRESH MATERIALIZED VIEW` can be triggered by the ETL service principal.

---

### TASK-028 — Create `mart.v_purchase_per_stock_item` View

**Type:** MART (DDL)
**Depends On:** TASK-005
**Requirements:** FR-010, NFR-001
**Design reference:** §8 Mart Layer
**Output File:** `src/db/ddl/mart/v_purchase_per_stock_item.sql`

**Description:**
Create `CREATE OR REPLACE VIEW inventory_stock.mart.v_purchase_per_stock_item`. Join `silver_fact.fact_purchase` to `silver_dim.stock_item` and `silver_dim.supplier`. Expose all fact columns plus `stock_item_name`, `color`, `unit_package_name`, `supplier_name`. No aggregation — row-level view for the `wwidw_purchase_and_sale_per_stockitem_dynamic` BI report.

**DDL (key structure):**
```sql
CREATE OR REPLACE VIEW inventory_stock.mart.v_purchase_per_stock_item
COMMENT 'Row-level purchase detail joined to stock item and supplier — serves wwidw_purchase_and_sale_per_stockitem_dynamic report'
AS
SELECT
    f.purchase_key,
    f.date_key,
    f.wwi_purchase_order_id,
    f.ordered_outers,
    f.ordered_quantity,
    f.received_outers,
    f.package,
    f.is_order_finalized,
    f.lineage_key,
    si.wwi_stock_item_id,
    si.stock_item_name,
    si.color,
    si.unit_package_name,
    s.wwi_supplier_id,
    s.supplier_name
FROM inventory_stock.silver_fact.fact_purchase f
JOIN inventory_stock.silver_dim.stock_item si
    ON f.stock_item_key = si.stock_item_key AND si.is_current_row = TRUE
JOIN inventory_stock.silver_dim.supplier s
    ON f.supplier_key = s.supplier_key AND s.is_current_row = TRUE;
```

**Acceptance:** `DESCRIBE inventory_stock.mart.v_purchase_per_stock_item` shows all expected columns; SELECT returns rows consistent with joined tables.

---

### TASK-029 — Write `nb_refresh_v_purchase_by_supplier.py`

**Type:** MART (ETL)
**Depends On:** TASK-027
**Requirements:** FR-010, NFR-001
**Design reference:** §8 Mart Layer
**Output File:** `src/etl/mart/nb_refresh_v_purchase_by_supplier.py`

**Description:**
Implement the materialized view refresh notebook. Execute `spark.sql("REFRESH MATERIALIZED VIEW inventory_stock.mart.v_purchase_by_supplier")`. Log refresh time. Post-refresh: assert `SELECT COUNT(*) FROM inventory_stock.mart.v_purchase_by_supplier > 0`. Raise on failure to halt Workflow. Must only run after DQ gate passes (`dq_passed = TRUE` task value from nb_dq_purchase).

**Acceptance:** REFRESH executes without error; COUNT returns positive integer post-refresh; exception propagates on failure.

---

### TASK-030 — Write `nb_refresh_v_purchase_per_stock_item.py`

**Type:** MART (ETL)
**Depends On:** TASK-028
**Requirements:** FR-010, NFR-001
**Design reference:** §8 Mart Layer
**Output File:** `src/etl/mart/nb_refresh_v_purchase_per_stock_item.py`

**Description:**
Implement the view validation notebook. Since `v_purchase_per_stock_item` is a standard view (not materialized), run a COUNT validation to confirm the view is queryable after fact and dimension loads. Log row count. Raise if view returns 0 rows when `silver_fact.fact_purchase` is non-empty. Re-create view via DDL if definition is stale.

**Acceptance:** SELECT returns rows consistent with current fact layer; notebook raises if view is not queryable.

---

### TASK-031 — Write `nb_validate_mart_views.py`

**Type:** MART (ETL)
**Depends On:** TASK-029, TASK-030
**Requirements:** FR-010, NFR-001
**Design reference:** §8 Mart Layer
**Output File:** `src/etl/mart/nb_validate_mart_views.py`

**Description:**
Implement mart validation notebook. Assertions:
1. `SELECT COUNT(*) FROM mart.v_purchase_by_supplier > 0`
2. `SELECT COUNT(*) FROM mart.v_purchase_per_stock_item > 0`
3. Row count in mart consistent with `silver_fact.fact_purchase` total
4. No null FK columns in mart views (LEFT ANTI JOIN check)
Log all assertion results. Raise if any assertion fails.

**Acceptance:** All assertions pass on a clean run; mismatch raises observable exception logged with `lineage_key`.

---

### TASK-032 — Write `src/etl/dq/dq_engine.py`

**Type:** DQ
**Depends On:** TASK-004, TASK-005
**Requirements:** NFR-004, NFR-005, DQR-001, DQR-002, DQR-003, DQR-006
**Design reference:** §5 QA Assertion Chain
**Output File:** `src/etl/dq/dq_engine.py`

**Description:**
Implement the DQ rule evaluation engine. Define `evaluate_rules(spark, lineage_key, batch_id, rules_config) -> dict` function. Evaluates:
- DQR-001: row count reconciliation between `bronze.purchase_staging` and fact delta — BLOCKING
- DQR-002: FK integrity via LEFT ANTI JOIN (`supplier_key`, `stock_item_key`, `date_key`) — Informational
- DQR-003: orphaned key detection (key=0) — Informational
- DQR-006: null `lineage_key` in `silver_fact.fact_purchase` — BLOCKING
For each violation, write one row to `bronze.dq_rejections`. Return `{rule_id: {passed: bool, violation_count: int}}`.

**Acceptance:** Count mismatch returns DQR-001 failed + writes rejection rows; FK violations logged per row; clean batch returns all passed + zero rejection rows.

---

### TASK-033 — Write `src/etl/dq/nb_dq_purchase.py`

**Type:** DQ
**Depends On:** TASK-032
**Requirements:** DQR-001, DQR-005, DQR-006
**Design reference:** §5 QA Assertion Chain
**Output File:** `src/etl/dq/nb_dq_purchase.py`

**Description:**
Implement the DQ orchestrator notebook. Retrieves `lineage_key` from taskValues. Loads `config/environment.yaml` DQ config. Calls `dq_engine.evaluate_rules`. On BLOCKING rule failure: raises `DQBlockingFailure` exception to halt pipeline and prevent mart tasks from running. Informational failures logged only. Publishes `dq_passed` boolean task value.

**Acceptance:** BLOCKING failure causes raise preventing downstream mart tasks; informational-only failure allows mart promotion; `dq_passed = TRUE` only when no BLOCKING failures.

---

### TASK-034 — Write `src/etl/dq/nb_dq_rejection_report.py`

**Type:** DQ
**Depends On:** TASK-033
**Requirements:** NFR-007, DQR-004
**Design reference:** §5 QA Assertion Chain
**Output File:** `src/etl/dq/nb_dq_rejection_report.py`

**Description:**
Implement the rejection report notebook. Reads `bronze.dq_rejections` filtered to current `lineage_key`. Aggregates by `rule_id` and severity: count violations per rule. Logs formatted per-run summary table. Optionally writes summary as JSON task output. Does NOT raise on violations — reporting only artifact.

**Acceptance:** Rejection summary visible in Workflow logs; zero violations logged as "0 DQ violations for this run"; notebook does not raise on DQ violations.

---

_End of task list. Total: 34 tasks (DDL: 8 | ETL: 9 | MART: 5 | DQ: 3 | Config: 2 | Test: 3 | BI: 2 | Docs: 2)_
