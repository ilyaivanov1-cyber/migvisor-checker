# Project Transformation Rules: GlobalSales_Project

| Field | Value |
|---|---|
| Version | 1.0.1 |
| Generated | 2026-08-28 |
| Source | Microsoft SQL Server 2014 (`wideworldimportersdw`) |
| Target | Databricks (Delta Lake lakehouse) — Unity Catalog `globalsales` |
| Active dimensions | 7 |
| Changelog | 2026-08-28 — PL: corrected catalog (`global_sales` → `globalsales`) and schema names (`bronze/silver_dim/silver_fact/gold` → `stg/dim/fact/mart`) throughout PL-002, PL-004, PL-005, PL-007, PL-008, PL-009. NM: fixed non-ODPS `quality_dimensions` values (`Correctness` → `conformity`, `Traceability` → `completeness`, capitalization normalized) across all 9 NM rules. |

---

## Dimension Table

| Dimension | Prefix | File | Rule Count |
|---|---|---|---|
| Platform | PL | [PL-platform.yaml](PL-platform.yaml) | 10 |
| Naming | NM | [NM-naming.yaml](NM-naming.yaml) | 9 |
| Types | TY | [TY-types.yaml](TY-types.yaml) | 30 |
| Objects | OB | [OB-objects.yaml](OB-objects.yaml) | 11 |
| Syntax | SX | [SX-syntax.yaml](SX-syntax.yaml) | 17 |
| Performance | PE | [PE-performance.yaml](PE-performance.yaml) | 8 |
| Lineage | LN | [LN-lineage.yaml](LN-lineage.yaml) | 7 |

**Total rules: 92**

---

## Rule Index

### PL — Platform (10 rules)

| Rule ID | Intent |
|---|---|
| PL-001 | Establish the authoritative mapping between SQL Server 2014 (source engine) and Databricks with Delta Lake (target engine), capturing all engine-level capability differences that downstream rules must respect. |
| PL-002 | Map every SQL Server schema to its corresponding Databricks Unity Catalog three-part name, enforcing lowercase_snake_case naming and a consistent medallion-layer assignment. |
| PL-003 | Convert all SQL Server heap, row-store B-tree, and columnstore tables to Delta Lake format, enabling ACID transactions, time travel, schema enforcement, and unified batch/streaming support. |
| PL-004 | Eliminate all SQL Server SEQUENCE objects (primarily `sequences.lineagekey`) and replace them with Databricks-native surrogate key generation patterns that are idempotent, scalable, and compatible with distributed execution. |
| PL-005 | Replace the SQL Server ETL pattern (staging tables + `migratestaged*` stored procedures) with Databricks-native Delta Lake MERGE operations executed from Python/SQL notebooks orchestrated by Databricks Workflows. |
| PL-006 | Replace SQL Server columnstore indexes and partition functions/schemes with Delta Lake Z-ordering and liquid clustering to achieve equivalent or better query performance on analytical workloads. |
| PL-007 | Formally evaluate every stored procedure in `application.*` and assign a disposition of DROP, RE-IMPLEMENT, or DEFER so that no SQL Server application-layer procedure is silently omitted from the migration record. |
| PL-008 | Address the fundamental difference between SQL Server's pessimistic lock-based ACID transaction model and Delta Lake's optimistic concurrency control, ensuring multi-statement transaction logic is redesigned for correctness. |
| PL-009 | Assign every SQL Server star-schema object to the correct Databricks Delta Lake layer (`integration.* → globalsales.stg`, `dimension.* → globalsales.dim`, `fact.* → globalsales.fact`, `analytics.* → globalsales.mart`), ensuring clean separation of raw ingestion, curated business objects, and analytical aggregations. |
| PL-010 | Replace all SQL Server Agent job schedules and step sequences with equivalent Databricks Workflows, preserving scheduling, error handling, notifications, and retry logic. |

---

### NM — Naming (9 rules)

| Rule ID | Intent |
|---|---|
| NM-001 | Convert all SQL Server object names using PascalCase, camelCase, or mixed case into lowercase_snake_case for Databricks. |
| NM-002 | Rename SQL Server table and object names that contain literal space characters to valid Databricks snake_case identifiers (covers `payment method`, `stock item`, `transaction type`, `stock holding`, `etl cutoff`). |
| NM-003 | Map each SQL Server schema to the corresponding Databricks Unity Catalog identifier (`dimension → globalsales.dim`, `fact → globalsales.fact`, `integration → globalsales.stg`, `analytics → globalsales.mart`, `application → globalsales.app`, `sequences → retired`). |
| NM-004 | Standardise view naming in Databricks by preserving the `v_` prefix convention already in use in the source `analytics` schema. |
| NM-005 | Preserve and standardise the `_staging` suffix convention used in the SQL Server integration schema for all staging (landing zone) tables in Databricks. |
| NM-006 | Map SQL Server stored procedures and user-defined functions to their Databricks equivalents — notebooks or Python module functions — using consistent lowercase_snake_case naming. |
| NM-007 | Declare that SQL Server SEQUENCE objects residing in the `sequences` schema are not migrated to Databricks. Delta Lake uses IDENTITY columns or Python-managed counters as replacements. |
| NM-008 | Establish a consistent naming convention for constraints (`pk_`, `uq_`, `chk_` prefixes) in Databricks Delta Lake DDL. FKs and indexes are not migrated. |
| NM-009 | Define a naming convention for temporary, work, or intermediate tables created during ETL processing in Databricks (`tmp_` prefix for SQL temp views, `df_` prefix for Python DataFrames). |

---

### TY — Types (30 rules)

| Rule ID | Intent |
|---|---|
| TY-001 | Convert SQL Server TINYINT (0–255) to Spark SQL BYTE, preserving the smallest integer footprint. |
| TY-002 | Preserve SMALLINT as the identical Spark SQL type. |
| TY-003 | Preserve SQL Server INT as Spark SQL INT. |
| TY-004 | Preserve SQL Server BIGINT as Spark SQL BIGINT — required for surrogate keys and large fact-table row counts. |
| TY-005 | Convert SQL Server DECIMAL(p,s) / NUMERIC(p,s) to Spark SQL DECIMAL(p,s), preserving precision and scale. |
| TY-006 | Convert SQL Server MONEY to DECIMAL(19,4) in Spark SQL. |
| TY-007 | Convert SQL Server SMALLMONEY to DECIMAL(10,4) in Spark SQL. |
| TY-008 | Convert SQL Server FLOAT to Spark SQL DOUBLE (IEEE 754 double precision). |
| TY-009 | Convert SQL Server REAL / FLOAT(n ≤ 24) to Spark SQL FLOAT (single precision). |
| TY-010 | Convert CHAR(n) and NCHAR(n) to Spark SQL STRING, eliminating padding semantics. |
| TY-011 | Convert VARCHAR(n), VARCHAR(MAX), NVARCHAR(n), NVARCHAR(MAX) to Spark SQL STRING. |
| TY-012 | Preserve SQL Server DATE as Spark SQL DATE (direct semantic equivalent). |
| TY-013 | Convert SQL Server TIME(n) to STRING in Spark SQL (ISO 8601 format). |
| TY-014 | Convert SQL Server DATETIME to Spark SQL TIMESTAMP (UTC-normalised). |
| TY-015 | Convert SQL Server DATETIME2(n) to Spark SQL TIMESTAMP_NTZ. |
| TY-016 | Convert SQL Server SMALLDATETIME to Spark SQL TIMESTAMP. |
| TY-017 | Convert SQL Server DATETIMEOFFSET(n) to Spark SQL TIMESTAMP (UTC-normalised) with companion offset column. |
| TY-018 | Convert SQL Server BINARY(n) / VARBINARY(n) / VARBINARY(MAX) to Spark SQL BINARY. |
| TY-019 | Convert the deprecated SQL Server IMAGE type to Spark SQL BINARY. |
| TY-020 | Convert SQL Server BIT (0/1/NULL) to Spark SQL BOOLEAN. |
| TY-021 | Faithfully replicate SQL Server NOT NULL / NULL column constraints in Delta Lake DDL. |
| TY-022 | Convert SQL Server UNIQUEIDENTIFIER (GUID) to Spark SQL STRING (UUID format). |
| TY-023 | Replace SQL Server IDENTITY(seed, increment) with Delta Lake GENERATED ALWAYS AS IDENTITY. |
| TY-024 | Replace SQL Server SEQUENCE objects (specifically `sequences.lineagekey`) with Databricks-native counter mechanisms. |
| TY-025 | Convert SQL Server XML type to Spark SQL STRING, preserving the XML document as a raw string. |
| TY-026 | Convert SQL Server SQL_VARIANT to Spark SQL STRING with type-prefix serialisation. |
| TY-027 | Remove SQL Server column-level and database-level collation specifications; default to Spark UTF-8. |
| TY-028 | Determine the DDL type of the `application.*` objects identified as having "unknown" DDL type, then classify and map to appropriate Databricks alternatives. |
| TY-029 | Convert SQL Server DEFAULT constraint expressions (GETDATE(), NEWID(), literals) to Spark SQL equivalents. |
| TY-030 | Replace SQL Server computed column definitions (`col AS <expr>`) with Delta Lake GENERATED ALWAYS AS (`<expr>`). |

---

### OB — Objects (11 rules)

| Rule ID | Intent |
|---|---|
| OB-001 | Migrate all 8 SQL Server conformed dimension tables to Delta Lake managed tables in `globalsales.dim`. |
| OB-002 | Migrate all 6 SQL Server fact tables to Delta Lake managed tables in `globalsales.fact` with date partitioning and Z-ORDER or liquid clustering. |
| OB-003 | Migrate all 15 SQL Server integration staging tables to transient Delta Lake managed tables in `globalsales.stg`. |
| OB-004 | Migrate all 16 SQL Server analytics schema tables to Delta Lake managed tables in `globalsales.mart`. |
| OB-005 | Migrate all SQL Server views (1 integration + 14 analytics) to Databricks SQL views or materialized views with translated T-SQL syntax. |
| OB-006 | Migrate all 4 SQL Server scalar functions to Databricks SQL UDFs or Python UDFs registered in Unity Catalog. |
| OB-007 | Migrate all 16 integration ETL stored procedures + 2 sequences procedures to Python tasks in Databricks Workflows executing Delta MERGE operations. |
| OB-008 | Replace the SQL Server SEQUENCE object (`sequences.lineagekey`) and all IDENTITY columns with Delta Lake IDENTITY columns or Python-managed surrogate keys in `globalsales.meta`. |
| OB-009 | Formally retire all SQL Server application-specific stored procedures (PolyBase config, large sale table, ETL re-seed) — DROP, no Databricks migration target. |
| OB-010 | Migrate all 6 `application.*` config/parameter objects of unknown DDL type to Databricks Secrets, YAML config, or `globalsales.meta` Delta tables. |
| OB-011 | Explicitly exclude all out-of-scope objects (`dbo.*`, `grocery_inventory`, `testdb.bidef`, `snowflake`) from migration scope, enforced via `config/exclusions.yaml`. |

---

### SX — Syntax (17 rules)

| Rule ID | Intent |
|---|---|
| SX-001 | Convert T-SQL MERGE statements in `integration.*` ETL procedures to Databricks Delta Lake MERGE INTO syntax. |
| SX-002 | Remove T-SQL procedure-level directives SET NOCOUNT ON and SET XACT_ABORT ON (no Databricks equivalent). |
| SX-003 | Convert T-SQL explicit transaction control (BEGIN TRANSACTION / COMMIT / ROLLBACK) to Delta Lake transactional patterns and Python try/except wrappers. |
| SX-004 | Replace T-SQL global system variables @@ROWCOUNT, @@ERROR, @@IDENTITY with Databricks-idiomatic equivalents (Delta metrics, exception handling, sequence utilities). |
| SX-005 | Map T-SQL date/time functions GETDATE(), SYSDATETIME(), GETUTCDATE() to Spark SQL equivalents (`current_timestamp()`, etc.). |
| SX-006 | Map T-SQL ISNULL() to Spark SQL `ifnull()` / `coalesce()`. |
| SX-007 | Replace T-SQL TOP N / TOP N WITH TIES with Spark SQL LIMIT N and QUALIFY window equivalents. |
| SX-008 | Remove T-SQL table hints (NOLOCK, UPDLOCK, HOLDLOCK) — Delta Lake snapshot isolation satisfies read-blocking concerns. |
| SX-009 | Replace T-SQL PRINT statements with Python logging calls or Databricks notebook output for ETL observability. |
| SX-010 | Remove T-SQL EXECUTE AS / WITH EXECUTE AS clauses — Databricks uses Unity Catalog service principals instead. |
| SX-011 | Convert T-SQL OBJECT_ID() existence checks and IF OBJECT_ID(...) IS NOT NULL guards to Spark SQL catalog API patterns. |
| SX-012 | Normalize T-SQL window function syntax (ROW_NUMBER, RANK, LAG, LEAD, SUM OVER) to Spark SQL window function syntax. |
| SX-013 | Replace T-SQL IDENTITY(1,1) definitions and NEXT VALUE FOR sequence references with Databricks GENERATED IDENTITY or Python-generated surrogate key patterns. |
| SX-014 | Convert T-SQL two-part `schema.object` references to Databricks Unity Catalog three-part `catalog.schema.table` naming. |
| SX-015 | Remove T-SQL `[bracket]` identifier quoting; replace with backtick quoting only where Spark SQL reserved words require it, or rename per naming conventions. |
| SX-016 | Map T-SQL CAST / CONVERT / TRY_CAST / TRY_CONVERT to Spark SQL equivalents, preserving safe-cast semantics and CONVERT format codes. |
| SX-017 | Replace the T-SQL STUFF(... FOR XML PATH('')) string aggregation pattern with Spark SQL COLLECT_LIST + ARRAY_JOIN or STRING_AGG. |

---

### PE — Performance (8 rules)

| Rule ID | Intent |
|---|---|
| PE-001 | Retire SQL Server columnstore index DDL (no migration action needed) — Delta Lake is columnar by default; retire `application.configuration_applypartitionedcolumnstoreindexing`. |
| PE-002 | Map SQL Server table partition functions/schemes on fact tables to Delta Lake PARTITIONED BY on date columns for partition elimination on range queries. |
| PE-003 | Apply Delta Lake Z-ORDER on fact tables to co-locate data by dimension key columns, enabling data skipping on analytical queries. |
| PE-004 | Apply Delta Lake liquid clustering on large fact tables (Databricks Runtime 13.3+) as an alternative to static PARTITIONED BY + ZORDER for flexible, online re-clustering. |
| PE-005 | Integrate Delta OPTIMIZE (and ZORDER where applicable) into the nightly ETL pipeline as a post-load step for all non-staging tables to prevent small-file accumulation. |
| PE-006 | Apply broadcast join hints for small dimension tables (customer, city, stock_item, employee, supplier, payment_method, transaction_type, date) to avoid shuffle-based joins against large fact tables. |
| PE-007 | Classify `integration.*` staging tables as transient (write-once-read-once per ETL run) — no OPTIMIZE, ZORDER, or liquid clustering applied; short Delta log retention. |
| PE-008 | Enable Databricks auto-optimization features (auto-compaction and optimized writes) on all silver and gold Delta tables to reduce manual maintenance overhead. |

---

### LN — Lineage (7 rules)

| Rule ID | Intent |
|---|---|
| LN-001 | Recreate the SQL Server `integration.lineage` table as a managed Delta Lake table `globalsales.stg.lineage`, preserving the ETL run tracking contract with enhanced metadata columns. |
| LN-002 | Replace the SQL Server SEQUENCE object `sequences.lineagekey` with a Delta Lake IDENTITY column on `globalsales.stg.lineage` or a Python-managed UUID-based run identifier. |
| LN-003 | Replace the SQL Server stored procedure `integration.getlineagekey` with a Python utility function (`open_lineage_record()` / `close_lineage_record()`) in `shared/utils/lineage_utils.py`. |
| LN-004 | Ensure that every migrated fact table retains a `lineage_key` BIGINT NOT NULL column referencing `globalsales.stg.lineage`, preserving the FK tracking pattern with DQ assertions. |
| LN-005 | Retire SQL Server SEQUENCE reseed procedures (`sequences.reseedallsequences`, `sequences.reseedsequencebeyondtablevalues`) — no Databricks equivalent needed; Delta IDENTITY is self-managing. |
| LN-006 | Configure Databricks Unity Catalog system-level lineage (table-to-table and column-to-column lineage) as a complement to application-level lineage in `globalsales.stg.lineage`. |
| LN-007 | Capture a consistent set of ETL run operational metadata in each lineage record: run ID, pipeline name, notebook path, cluster ID, row count, start/end time, and success status. |
