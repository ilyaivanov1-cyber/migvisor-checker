# Product Transformation Rules: Purchase

| Field | Value |
|---|---|
| Product | Purchase |
| Project | Inventory_Stock_Project |
| Inherits from | Inventory_Stock_Project project rules v1.0 (2026-09-04) |
| Generated | 2026-09-07 |
| Source | Microsoft SQL Server 2014 (T-SQL), `wideworldimportersdw` |
| Target | Databricks Delta Lake lakehouse, Unity Catalog (`inventory_stock`) |
| Active dimensions | 9 |
| Inherited project dimensions | 7 (PL, NM, TY, OB, SX, PE, LN) |
| Product-only dimensions | 2 (QA, CX) |

---

## Customization Summary

| Type | Count | Rule IDs |
|---|---|---|
| Overrides | 1 | TY-P001 |
| Extensions | 13 | TY-P002, TY-P003, TY-P004, OB-P001, OB-P002, OB-P003, OB-P004, PE-P001, PE-P002, LN-P001, SX-P001, SX-P002, SX-P003 |
| Deactivations | 0 | — |
| New rules | 12 | SX-P004, QA-P001, QA-P002, QA-P003, QA-P004, QA-P005, CX-P001, CX-P002, CX-P003, CX-P004, CX-P005, CX-P006 |
| **Total customizations** | **26** | |

---

## Dimension Table

| Dimension | Prefix | File | Rule Count | Customizations Applied |
|---|---|---|---|---|
| Platform | PL | [PL-platform.yaml](PL-platform.yaml) | 10 | None — fully inherited |
| Naming | NM | [NM-naming.yaml](NM-naming.yaml) | 9 | None — fully inherited |
| Types | TY | [TY-types.yaml](TY-types.yaml) | 30 | 1 override (TY-P001), 3 extensions (TY-P002, TY-P003, TY-P004) |
| Objects | OB | [OB-objects.yaml](OB-objects.yaml) | 15 | 4 extensions (OB-P001, OB-P002, OB-P003, OB-P004) |
| Syntax | SX | [SX-syntax.yaml](SX-syntax.yaml) | 21 | 3 extensions (SX-P001, SX-P002, SX-P003), 1 new (SX-P004) |
| Performance | PE | [PE-performance.yaml](PE-performance.yaml) | 11 | 2 extensions (PE-P001, PE-P002) |
| Lineage | LN | [LN-lineage.yaml](LN-lineage.yaml) | 9 | 1 extension (LN-P001) |
| Quality | QA | [QA-quality.yaml](QA-quality.yaml) | 5 | Product-only dimension — 5 new rules |
| Custom | CX | [CX-custom.yaml](CX-custom.yaml) | 6 | Product-only dimension — 6 new rules |

---

## Rule Index

### PL — Platform (10 rules, 0 customizations)

| ID | Intent | Tag |
|---|---|---|
| PL-001 | Declare SQL Server 2014 → Databricks Delta Lake as the platform contract; SSIS staging-truncation bug must be corrected in replacement pipeline | |
| PL-002 | Map SQL Server schemas to Unity Catalog `inventory_stock` layers (fact→silver_fact, dimension→silver_dim, integration→bronze, sequences→retire); resolve space-bearing object names | |
| PL-003 | Migrate all SQL Server heap/clustered tables to Delta Parquet managed tables; confirm VARBINARY columns (e.g. Photo in stock_item) map to BINARY | |
| PL-004 | Retire `sequences.lineagekey` SEQUENCE; replace with `GENERATED ALWAYS AS IDENTITY` on lineage control table or Python UUID-based run counter | |
| PL-005 | Migrate SSIS Purchase container (4 dataflow items) to Databricks Workflow tasks; enforce dimension load → fact load dependency ordering; fix truncation bug via INSERT OVERWRITE | |
| PL-006 | Translate `migratestagedpurchasedata` T-SQL MERGE + SCD-2 key resolution to Spark SQL `MERGE INTO` with Python notebook orchestration | |
| PL-007 | Confirm drop scope with scope owner for `application.configuration_reseedetl` (Purchase portions); pre-seed key=0 sentinel rows if retained | |
| PL-008 | Replace SQL Server columnstore indexes with Delta liquid clustering; CLUSTER BY (date_key, supplier_key) for fact.purchase; CLUSTER BY (supplier_key/stock_item_key) for SCD-2 dims | |
| PL-009 | Assign procurement objects to medallion layers: bronze=integration.*/sequences control, silver_dim=dimension.*, silver_fact=fact.purchase, gold=future analytics | |
| PL-010 | Replace multi-statement `BEGIN TRANSACTION / COMMIT` blocks with Delta ACID write semantics; remove NOLOCK hints; add Python retry wrapper | |

### NM — Naming (9 rules, 0 customizations)

| ID | Intent | Tag |
|---|---|---|
| NM-001 | Convert all object and column names to lowercase_snake_case; split camelCase and PascalCase identifiers | |
| NM-002 | (TOP PRIORITY) Rename all space-bearing objects and columns: `dimension.stock item`→`stock_item`, `integration.etl cutoff`→`etl_cutoff`, `WWI Purchase Order ID`→`wwi_purchase_order_id`, etc. | |
| NM-003 | Map source schemas to `inventory_stock` Unity Catalog layers; fact→silver_fact, dimension→silver_dim, integration→bronze, application→bronze, sequences→retired | |
| NM-004 | Retain `_staging` suffix on staging tables; `etl_cutoff` and `lineage_run` are control tables — no suffix | |
| NM-005 | Apply `v_` prefix to all Gold-layer presentation views; Purchase currently has no source views | |
| NM-006 | Convert procedure names to snake_case notebook names: `migratestagedpurchasedata`→`migrate_staged_purchase_data`, `getlastetlcutofftime`→`get_last_etl_cutoff_time`, `getlineagekey`→`get_lineage_key` | |
| NM-007 | Do not migrate `sequences.lineagekey`; sequences schema retired; replacement handled by LN dimension rules | |
| NM-008 | Name PKs as `pk_<table>_<col>`, FKs as `fk_<table>_<ref_table>`; FK constraints are informational-only in Delta | |
| NM-009 | Prefix in-notebook temporary DataFrames with `tmp_` or `df_`; no persistent temp tables in Delta | |

### TY — Types (26 inherited + 4 product = 30 rules)

| ID | Intent | Tag |
|---|---|---|
| TY-001 | TINYINT → TINYINT (promote to SMALLINT if values exceed 255) | |
| TY-002 | SMALLINT → SMALLINT | |
| TY-003 | INT → INT (covers surrogate FK columns, order IDs, quantity columns) | |
| TY-004 | BIGINT → BIGINT (covers PurchaseKey PK) | |
| TY-005 | DECIMAL/NUMERIC(p,s) → DECIMAL(p,s) (preserve precision and scale exactly) | EXTENDED by TY-P003 |
| TY-006 | FLOAT → DOUBLE | |
| TY-007 | REAL / FLOAT(n≤24) → FLOAT | |
| TY-008 | CHAR/NCHAR(n) → STRING (remove padding semantics) | |
| TY-009 | VARCHAR/NVARCHAR(n) → STRING; NVARCHAR(MAX) → STRING | EXTENDED by TY-P004 |
| TY-010 | DATE → DATE (covers Date Key FK column) | |
| TY-011 | DATETIME → TIMESTAMP | |
| TY-012 | DATETIME2 → TIMESTAMP_NTZ (SCD-2 Valid From / Valid To columns) | OVERRIDDEN by TY-P001; EXTENDED by TY-P002 |
| TY-013 | DATETIMEOFFSET → TIMESTAMP with optional companion offset INT column | |
| TY-014 | BINARY/VARBINARY → BINARY (covers Photo column in dimension.stock item) | |
| TY-015 | BIT → BOOLEAN (covers Is Order Finalized, Is Current, Was Successful, Is Chiller Stock) | |
| TY-016 | Preserve NOT NULL / NULL constraints in Delta DDL | |
| TY-017 | BIGINT IDENTITY → `GENERATED ALWAYS AS IDENTITY` (PurchaseKey, PurchaseStagingKey) | |
| TY-018 | SQL Server SEQUENCE (`sequences.lineagekey`) → retired; replaced by IDENTITY column or Python UUID counter | |
| TY-019 | Remove SQL Server collation attributes; Delta defaults to UTF-8 case-sensitive; note ETL TableName comparisons | |
| TY-020 | Translate DEFAULT constraint values to Spark SQL DDL DEFAULT (verify Delta Runtime support) | |
| TY-021 | Computed columns → persisted literal columns or Gold-layer view expressions | |
| TY-022 | `integration.etl cutoff` type map: NVARCHAR(50) table_name, DATETIMEOFFSET(7) cutoff_time → STRING, TIMESTAMP | |
| TY-023 | `integration.lineage` type map: INT/BIGINT keys, NVARCHAR labels, DATETIME timestamps → INT/BIGINT, STRING, TIMESTAMP | |
| TY-024 | SCD-2 Valid From / Valid To → TIMESTAMP_NTZ; staging probe column must match to ensure correct surrogate key resolution in MERGE | |
| TY-025 | Dimension DECIMAL columns (unit price, tax rate) → DECIMAL(18,2) or as specified in source DDL | |
| TY-026 | dimension.date: DATE → DATE, NVARCHAR month/day labels → STRING, INT fiscal keys → INT | |
| TY-P001 | SCD-2 validity columns (valid_from, valid_to) on Purchase SCD-2 dimension tables → DATE (not TIMESTAMP_NTZ) | OVERRIDE |
| TY-P002 | Define the full 5-column SCD-2 control block pattern for Purchase dimension tables (valid_from, valid_to, row_effective_date, row_expiry_date, is_current_row) | EXTENSION |
| TY-P003 | Map SQL Server MONEY → DECIMAL(18,2) and SMALLMONEY → DECIMAL(10,2) — not covered by project TY rules | EXTENSION |
| TY-P004 | Map SQL Server geography CLR type → three target columns (_wkt STRING, _lat DOUBLE, _lon DOUBLE) | EXTENSION |

### OB — Objects (11 inherited + 4 product = 15 rules)

| ID | Intent | Tag |
|---|---|---|
| OB-001 | Migrate dimension.supplier and dimension.stock item as SCD-2 Delta tables in silver_dim; add `_current` suffix view; rename space-bearing names | EXTENDED by OB-P001 |
| OB-002 | Migrate fact.purchase to silver_fact Delta managed table; IDENTITY PK → GENERATED ALWAYS AS IDENTITY; CLUSTER BY (date_key, supplier_key) | |
| OB-003 | Migrate integration.purchase_staging to bronze Delta table with OVERWRITE mode; corrects SSIS staging-truncation bug; no OPTIMIZE on staging | EXTENDED by OB-P002 |
| OB-004 | Migrate integration.etl_cutoff and integration.lineage to bronze control Delta tables; Delta ACID replaces SQL Server BEGIN TRAN blocks | |
| OB-005 | Replace migratestagedpurchasedata, getlastetlcutofftime, getlineagekey with Python notebooks / Databricks SQL tasks; T-SQL MERGE → Delta MERGE INTO | EXTENDED by OB-P004 |
| OB-006 | Retire sequences.lineagekey SEQUENCE; replace with GENERATED ALWAYS AS IDENTITY on bronze.lineage_run | |
| OB-007 | Replace SSIS Purchase container with Databricks Workflow; task graph enforces dimension loads complete before Purchase fact load | |
| OB-008 | Reconnect Power BI / SSRS reports to Databricks SQL Warehouse; update object references for renamed space-bearing tables and columns | EXTENDED by OB-P003 |
| OB-009 | Confirm drop scope for application.configuration_reseedetl (Purchase portions); if retained, pre-seed key=0 sentinel rows at init | |
| OB-010 | Exclude from migration: dbo.* (SSMS artifacts), sequences reseed utilities, non-Purchase integration.migratestaged* procedures, cross-domain fact/analytics objects | |
| OB-011 | Migrate dimension.date as read-only reference table in silver_dim; Purchase Workflow does not own its load; shared infrastructure responsibility | |
| OB-P001 | Require a key=0 'Unknown' sentinel row bootstrap notebook for every SCD-2 dimension table; MERGE-based upsert; INIT_ONLY tag | EXTENSION |
| OB-P002 | Add lineage_key BIGINT and _extracted_at_utc TIMESTAMP audit columns to purchase_staging beyond project DDL pattern | EXTENSION |
| OB-P003 | Classify analytics views: aggregating/reporting views → MATERIALIZED VIEW; thin wrapper/alias views → regular VIEW | EXTENSION |
| OB-P004 | Promote scd2_merge.py, sk_resolver.py, fact_merge.py as explicit named shared helper modules under src/common/ | EXTENSION |

### SX — Syntax (17 inherited + 4 product = 21 rules)

| ID | Intent | Tag |
|---|---|---|
| SX-001 | Convert T-SQL MERGE upsert in migratestagedpurchasedata to Delta `MERGE INTO ... WHEN MATCHED THEN UPDATE / WHEN NOT MATCHED THEN INSERT` | |
| SX-002 | Convert DELETE + INSERT-SELECT purchase reload pattern to Delta MERGE or explicit delete + append | |
| SX-003 | (CRITICAL) Convert TOP(1) correlated SCD-2 surrogate key subquery to `JOIN + ROW_NUMBER() OVER (PARTITION BY ... ORDER BY valid_from ASC) = 1` | EXTENDED by SX-P003 |
| SX-004 | Convert `NEXT VALUE FOR sequences.lineagekey` to Python `open_lineage_record()` returning IDENTITY-generated lineage_key | EXTENDED by SX-P001 |
| SX-005 | Convert all bracketed space-bearing identifiers ([stock item], [etl cutoff], [WWI Purchase Order ID], etc.) to backtick-quoted or snake_case renamed | |
| SX-006 | Remove SET NOCOUNT ON / SET XACT_ABORT ON procedure headers; no equivalent in Databricks notebooks | |
| SX-007 | Convert BEGIN TRANSACTION / COMMIT / ROLLBACK to Python try/except with Delta write semantics | |
| SX-008 | Convert GETDATE() / GETUTCDATE() / SYSDATETIME() to `current_timestamp()` (Spark SQL) or `datetime.now(timezone.utc)` (Python) | |
| SX-009 | Convert ISNULL(expr, default) to COALESCE(expr, default) or `ifnull()` | |
| SX-010 | Convert TOP(N) / SELECT TOP 1 in watermark reads to `LIMIT N`; SCD-2 TOP(1) handled by SX-003 | |
| SX-011 | Convert PRINT statements to Python `logging` calls | |
| SX-012 | Remove EXECUTE AS OWNER; replace with Unity Catalog service principal permissions | |
| SX-013 | Convert IF OBJECT_ID(...) IS NOT NULL / IF EXISTS checks to `IF NOT EXISTS` DDL or `spark.catalog.tableExists()` | |
| SX-014 | Correct SSIS truncation bug: replace `DELETE FROM Integration.Order_Staging` with `TRUNCATE TABLE inventory_stock.bronze.purchase_staging` (or OVERWRITE mode) | |
| SX-015 | Convert BIGINT IDENTITY to `GENERATED ALWAYS AS IDENTITY` in Delta DDL; INT upgraded to BIGINT for PK columns | |
| SX-016 | Convert `wideworldimportersdw.integration.purchase_staging` three-part SQL Server references to Unity Catalog `inventory_stock.bronze.purchase_staging` | |
| SX-017 | Convert CAST/CONVERT to Spark SQL `CAST(x AS type)`; use `TO_DATE` / `TO_TIMESTAMP` for date string conversions | EXTENDED by SX-P002 |
| SX-P001 | Specify exact dbutils.jobs.taskValues injection pattern as canonical replacement for EXEC Integration.GetLineageKey in Purchase ETL notebooks | EXTENSION |
| SX-P002 | Add CONVERT(CHAR(8), GETDATE()-N, 112) → DATE_FORMAT(DATE_SUB(current_date(), N), 'yyyyMMdd') mapping not covered by SX-017 | EXTENSION |
| SX-P003 | Replace inline UPDATE staging SET key = (SELECT TOP(1)...) pattern with pre-join call to sk_resolver.py before the MERGE step | EXTENSION |
| SX-P004 | Convert UPDATE Integration.Lineage SET [Data Load Completed] = ... inline lineage-close pattern to spark.sql UPDATE with Python variable injection | NEW |

### PE — Performance (9 inherited + 2 product = 11 rules)

| ID | Intent | Tag |
|---|---|---|
| PE-001 | Drop SQL Server columnstore indexes; Delta Parquet is columnar natively — no action required | |
| PE-002 | Apply liquid clustering to fact and dimension tables: CLUSTER BY (date_key, supplier_key) on fact_purchase; CLUSTER BY (supplier_key/stock_item_key) on SCD-2 dims | EXTENDED by PE-P001 |
| PE-003 | Schedule OPTIMIZE on silver_dim and silver_fact after each nightly batch; bronze staging excluded (OVERWRITE pattern) | EXTENDED by PE-P002 |
| PE-004 | Create `_current` suffix views on SCD-2 dimensions for active-row lookups; liquid clustering enables efficient surrogate key joins | |
| PE-005 | Add date-range predicate to MERGE INTO ON clause to push down to liquid clustering on date_key; keep staging table small via incremental load | |
| PE-006 | Enable broadcast join hints (`BROADCAST`) for dimension.supplier and dimension.stock_item in SCD-2 key resolution queries (tables are small) | |
| PE-007 | Use OVERWRITE mode for bronze.purchase_staging at run start; corrects SSIS truncation bug; no CLUSTER BY / OPTIMIZE on staging tables | |
| PE-008 | Enable `delta.autoOptimize.optimizeWrite` and `autoCompact` on all silver tables; disable on bronze staging | |
| PE-009 | Remove SQL Server WITH (NOLOCK) and WITH (FORCESEEK) hints; Delta ACID isolation and Spark optimizer replace both | |
| PE-P001 | Alternative layout for pre-DBR 13.3 runtimes: PARTITIONED BY (date_col) + ZORDER BY (supplier_key, stock_item_key) — mutually exclusive with CLUSTER BY | EXTENSION |
| PE-P002 | Conditional OPTIMIZE: run only when rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD (10,000); threshold externalised to config/environment.yaml | EXTENSION |

### LN — Lineage (8 inherited + 1 product = 9 rules)

| ID | Intent | Tag |
|---|---|---|
| LN-001 | Migrate integration.lineage to `inventory_stock.bronze.lineage_run` Delta table; retain all metadata columns; add etl_run_id, table_row_count, pipeline_name; enable CDF | |
| LN-002 | Retire sequences.lineagekey SEQUENCE; `lineage_run.lineage_key` becomes GENERATED ALWAYS AS IDENTITY; Python retrieves key via etl_run_id UUID | |
| LN-003 | Replace integration.getlineagekey with Python `open_lineage_record()` / `close_lineage_record()` utility in shared/utils/lineage_utils.py | EXTENDED by LN-P001 |
| LN-004 | Replace integration.getlastetlcutofftime with Python `get_last_etl_cutoff()` + `set_etl_cutoff()` reading from `inventory_stock.bronze.etl_cutoff` Delta table | |
| LN-005 | Migrate integration.[etl cutoff] (space-in-name) to `inventory_stock.bronze.etl_cutoff`; Delta MERGE ACID writes replace transaction-protected UPDATE | |
| LN-006 | Propagate lineage_key to `silver_fact.fact_purchase.lineage_key` and `bronze.purchase_staging.lineage_key`; set from open_lineage_record() at run start | |
| LN-007 | Retire sequences.reseedallsequences and sequences.reseedsequencebeyondtablevalues; application.configuration_reseedetl (Purchase portions) flagged for scope-owner sign-off | |
| LN-008 | Unity Catalog system lineage auto-captures all Delta reads/writes via three-part naming; no additional instrumentation required | |
| LN-P001 | Specify dbutils.jobs.taskValues as the Purchase lineage_key injection mechanism: nb_extract_watermark publishes via taskValues.set; all downstream tasks consume via taskValues.get | EXTENSION |

### QA — Quality (product-only dimension — 5 new rules)

| ID | Intent | Tag |
|---|---|---|
| QA-P001 | Row count reconciliation between purchase_staging and fact_purchase after each ETL run — blocking failure on mismatch | NEW |
| QA-P002 | Orphaned surrogate key detection in fact_purchase via LEFT ANTI JOIN on supplier_key and stock_item_key — informational, non-blocking | NEW |
| QA-P003 | RI checks via LEFT ANTI JOIN per FK column (supplier_key, stock_item_key, date_key); violations written to inventory_stock.bronze.dq_rejections | NEW |
| QA-P004 | Business rule assertions: negative quantities, out-of-window date_key, null/empty package — informational, non-blocking | NEW |
| QA-P005 | Centralised DQ rejection store (inventory_stock.bronze.dq_rejections) with lineage_key for traceability; post-run summary query logged per run | NEW |

### CX — Custom (product-only dimension — 6 new rules)

| ID | Intent | Tag |
|---|---|---|
| CX-P001 | Externalise hard-coded date filters to config/environment.yaml under purchase.etl | NEW |
| CX-P002 | Externalise hard-coded business factors to config/environment.yaml under purchase.business_rules; add NULL guards and DQ bound assertions | NEW |
| CX-P003 | Consolidate duplicate scalar functions into NULL-guarded Python UDFs in src/common/udfs.py | NEW |
| CX-P004 | Enforce standard Purchase codebase layout (config/, docs/, src/common/, src/db/, src/etl/, src/init/, tests/) | NEW |
| CX-P005 | Enforce standard ETL notebook skeleton: constants import → lineage_key via taskValues → zero-rows guard → main ETL → conditional OPTIMIZE → close lineage | NEW |
| CX-P006 | Enforce standard SQL DDL file header block listing PROJECT, PRODUCT, FILE, PURPOSE, SOURCE, TARGET, RULES, GENERATED fields | NEW |
