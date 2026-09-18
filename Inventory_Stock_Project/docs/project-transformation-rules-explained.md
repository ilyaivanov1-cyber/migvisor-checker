# Project Transformation Rules — Explained

**Project:** Inventory_Stock_Project
**Source:** Microsoft SQL Server 2014 (`wideworldimportersdw`)
**Target:** Databricks Delta Lake, Unity Catalog (`inventory_stock`)
**Total rules:** 90 across 7 dimensions

---

## What This Spec Is

The project transformation rules are the **rule book** for migrating a SQL Server 2014 data warehouse to a Databricks Delta Lake lakehouse. They contain 90 rules organized into 7 dimensions — each rule is a specific, traceable instruction for how to convert one piece of the legacy system to the new platform.

Think of it as a contract: before anyone writes a single line of code, these rules define *exactly* what changes and how. Every downstream spec (as-is, to-be, development plan, generated code) references specific rule IDs from this document, creating a fully traceable chain from decision to implementation.

---

## Why This Spec Exists

Without these rules:
- One developer maps `DATETIME2` to `TIMESTAMP` while another maps it to `TIMESTAMP_NTZ`, and the SCD-2 join silently breaks.
- Someone forgets to rename the space-bearing `[stock item]` table and it fails in Databricks.
- The critical `TOP(1)` correlated subquery gets translated incorrectly and fact rows get the wrong dimension keys.
- There is no standard for naming, layer assignment, or performance tuning — every developer makes ad-hoc decisions.

The 90 rules ensure nothing is forgotten, nothing breaks silently, and every developer on the project makes the **same** translation decisions.

---

## The 7 Dimensions

### PL — Platform (10 rules)

**What it governs:** The "big picture" migration decisions — replacing the entire technology ecosystem, not just swapping databases.

**Why it's complex:** SQL Server to Databricks isn't a 1:1 swap. SSIS packages become Databricks Workflows. SQL Server sequences become IDENTITY columns. Columnstore indexes become Delta liquid clustering. Transaction blocks become Delta ACID semantics. This dimension also catches a **real bug**: SSIS was deleting from the wrong staging table (`Integration.Order_Staging` instead of `Integration.Purchase_Staging`), causing stale rows to accumulate silently across runs.

**Key rules:**

| Rule | What it does | Why it matters |
|---|---|---|
| PL-001 | Declares SQL Server 2014 to Databricks Delta Lake as the platform contract | Establishes the migration boundary — everything flows from this |
| PL-002 | Maps SQL Server schemas to Unity Catalog layers: `fact`→`silver_fact`, `dimension`→`silver_dim`, `integration`→`bronze`, `sequences`→retired | Without this, objects end up in arbitrary locations with no medallion architecture |
| PL-004 | Retires `sequences.lineagekey` SEQUENCE; replaces with `GENERATED ALWAYS AS IDENTITY` | SQL Server SEQUENCE has no native Databricks equivalent — needs a completely different approach |
| PL-005 | Migrates SSIS Purchase container (4 dataflow items) to Databricks Workflow tasks; fixes truncation bug via INSERT OVERWRITE | The SSIS pipeline is the core orchestration — replacing it wrong breaks the entire ETL |
| PL-006 | Translates `migratestagedpurchasedata` T-SQL MERGE + SCD-2 key resolution to Spark SQL MERGE INTO with Python notebooks | This is the hardest single piece to rewrite — complex procedural logic with temporal dimension lookups |
| PL-008 | Replaces columnstore indexes with Delta liquid clustering | Different storage engine, different optimization strategy — old indexes don't exist in Delta |
| PL-010 | Replaces `BEGIN TRANSACTION / COMMIT` blocks with Delta ACID write semantics; removes NOLOCK hints | Delta handles isolation differently — explicit transaction blocks would fail or be redundant |

---

### NM — Naming (9 rules)

**What it governs:** Systematic renaming of every object, column, schema, and procedure from SQL Server conventions to Databricks snake_case conventions.

**Why it's complex:** SQL Server allowed terrible naming practices — `[WWI Purchase Order ID]` with spaces, `[stock item]`, `[etl cutoff]`. Databricks uses `lowercase_snake_case`. This seems cosmetic, but wrong names break every downstream query, every Power BI report connection, and every join predicate. One missed rename and the pipeline fails at runtime.

**Key rules:**

| Rule | What it does | Why it matters |
|---|---|---|
| NM-001 | Converts all object and column names to `lowercase_snake_case`; splits camelCase and PascalCase | Establishes the universal naming convention — every other rule assumes this is done |
| NM-002 | **(TOP PRIORITY)** Renames all space-bearing objects: `dimension.stock item`→`stock_item`, `integration.etl cutoff`→`etl_cutoff`, `WWI Purchase Order ID`→`wwi_purchase_order_id` | Space-bearing identifiers are the #1 source of runtime errors in Databricks — they require backtick quoting everywhere and break most tooling |
| NM-003 | Maps source schemas to Unity Catalog layers: `fact`→`silver_fact`, `dimension`→`silver_dim`, `integration`→`bronze` | Without consistent layer mapping, objects scatter across schemas with no logical organization |
| NM-006 | Converts procedure names to notebook names: `migratestagedpurchasedata`→`migrate_staged_purchase_data` | Procedures become notebooks — naming must be consistent so orchestration references work |
| NM-007 | Does not migrate `sequences.lineagekey`; sequences schema retired entirely | Prevents someone from accidentally trying to create a sequences schema in Databricks |
| NM-008 | Names PKs as `pk_<table>_<col>`, FKs as `fk_<table>_<ref_table>`; FK constraints are informational-only in Delta | Delta doesn't enforce FKs at write time — they exist for documentation and optimizer hints only |

---

### TY — Types (26 rules)

**What it governs:** The mapping of every SQL Server data type to its Spark/Delta equivalent. This is the largest dimension because the source database uses many different types across fact, dimension, staging, and control tables.

**Why it's complex:** Most mappings seem straightforward (`INT→INT`, `VARCHAR→STRING`), but the tricky ones have subtle consequences:
- `DATETIME2` must map to `TIMESTAMP_NTZ` for SCD-2 validity tracking — using `TIMESTAMP` instead would introduce timezone-aware comparisons that break the temporal range join.
- `BIGINT IDENTITY` must become `GENERATED ALWAYS AS IDENTITY` — a different syntax that needs to be correct in every DDL file.
- `VARBINARY` must map to `BINARY` — there's a `Photo` column in `dimension.stock item` that stores binary image data.
- Collation attributes must be removed — Delta defaults to UTF-8 case-sensitive, which affects ETL TableName comparisons.

**Key rules:**

| Rule | What it does | Why it matters |
|---|---|---|
| TY-003 | `INT → INT` | Covers surrogate FK columns, order IDs, and quantity columns — the most common type in the schema |
| TY-004 | `BIGINT → BIGINT` | Covers `PurchaseKey` PK — must be exact to match IDENTITY column semantics |
| TY-005 | `DECIMAL/NUMERIC(p,s) → DECIMAL(p,s)` | Precision and scale must be preserved exactly — rounding errors in financial columns (unit price, tax rate) would corrupt analytics |
| TY-009 | `VARCHAR/NVARCHAR(n) → STRING; NVARCHAR(MAX) → STRING` | Spark STRING is unbounded — no need to carry length constraints, but the mapping must be explicit |
| TY-012 | `DATETIME2 → TIMESTAMP_NTZ` | Critical for SCD-2 `Valid From` / `Valid To` columns — using the wrong timestamp type breaks surrogate key resolution |
| TY-014 | `BINARY/VARBINARY → BINARY` | Covers the `Photo` column in `dimension.stock item` — binary data needs explicit type handling |
| TY-015 | `BIT → BOOLEAN` | Covers `Is Order Finalized`, `Is Current`, `Was Successful`, `Is Chiller Stock` — semantic clarity improvement |
| TY-017 | `BIGINT IDENTITY → GENERATED ALWAYS AS IDENTITY` | PK auto-generation syntax is completely different between SQL Server and Databricks |
| TY-019 | Remove SQL Server collation attributes | Delta defaults to UTF-8 case-sensitive; collation attributes would cause DDL errors |
| TY-022 | `integration.etl cutoff` specific type map: `NVARCHAR(50)→STRING`, `DATETIMEOFFSET(7)→TIMESTAMP` | Control tables need exact type mappings to ensure watermark comparisons work correctly |
| TY-024 | SCD-2 `Valid From` / `Valid To` → `TIMESTAMP_NTZ`; staging probe column must match | If the probe column type doesn't match the validity column type, the temporal range comparison silently produces wrong results |

---

### OB — Objects (11 rules)

**What it governs:** The migration disposition of every database object — what to migrate, what to retire, what to exclude, and what needs special handling.

**Why it's complex:** Not everything should be migrated. Some objects belong to other products. Some are testing utilities that need owner sign-off. Some are SQL Server artifacts with no Databricks equivalent. Getting this wrong means either migrating things you shouldn't (scope creep, wasted effort) or missing things you should (broken pipeline at runtime).

**Key rules:**

| Rule | What it does | Why it matters |
|---|---|---|
| OB-001 | Migrates `dimension.supplier` and `dimension.stock item` as SCD-2 Delta tables in `silver_dim`; adds `_current` suffix view; renames space-bearing names | These dimensions are read dependencies of the Purchase ETL — they must exist in the target for surrogate key resolution to work |
| OB-002 | Migrates `fact.purchase` to `silver_fact` Delta managed table; `IDENTITY PK → GENERATED ALWAYS AS IDENTITY`; `CLUSTER BY (date_key, supplier_key)` | The central fact table — clustering choice directly impacts query performance for the most common analytical access patterns |
| OB-003 | Migrates `integration.purchase_staging` to bronze Delta table with OVERWRITE mode | **Corrects the SSIS staging-truncation bug** — the most critical defect fix in the entire migration |
| OB-005 | Replaces all 3 stored procedures with Python notebooks / Databricks SQL tasks; T-SQL MERGE → Delta MERGE INTO | Stored procedures don't exist in Databricks — the entire procedural ETL layer must become notebooks |
| OB-006 | Retires `sequences.lineagekey` SEQUENCE; replaces with `GENERATED ALWAYS AS IDENTITY` on `bronze.lineage_run` | No native Databricks equivalent — needs a fundamentally different design |
| OB-007 | Replaces SSIS Purchase container with Databricks Workflow; task graph enforces dimension loads complete before fact load | Cross-team dependency: if dimensions aren't loaded first, surrogate key resolution produces all zeros |
| OB-010 | Excludes from migration: `dbo.*` (SSMS artifacts), sequences reseed utilities, non-Purchase `migratestaged*` procedures, cross-domain objects | Prevents scope creep — these objects belong to other products or are SQL Server administrative artifacts |
| OB-011 | Migrates `dimension.date` as read-only reference table — Purchase Workflow does not own its load | Clarifies ownership: Purchase depends on this table but another team is responsible for loading it |

---

### SX — Syntax (17 rules)

**What it governs:** Line-by-line translation of T-SQL constructs to their Spark SQL / Python equivalents. This is where the actual code transformation happens.

**Why it's complex:** T-SQL and Spark SQL are different languages with different idioms. Some constructs have direct equivalents (`ISNULL` → `COALESCE`). Others require fundamental restructuring — the SCD-2 `TOP(1)` correlated subquery has no equivalent in Spark SQL and must be completely reimplemented using window functions. Getting any of these wrong produces code that either fails to compile or (worse) silently produces incorrect results.

**Key rules:**

| Rule | What it does | Why it matters |
|---|---|---|
| SX-001 | Converts T-SQL MERGE upsert to Delta `MERGE INTO ... WHEN MATCHED THEN UPDATE / WHEN NOT MATCHED THEN INSERT` | The core fact load pattern — Spark SQL MERGE has different syntax and semantics than T-SQL MERGE |
| SX-003 | **(CRITICAL)** Converts `TOP(1)` correlated SCD-2 surrogate key subquery to `JOIN + ROW_NUMBER() OVER (PARTITION BY ... ORDER BY valid_from DESC) = 1` | This is the single most migration-critical syntax translation. The legacy code uses a pattern that doesn't exist in Spark SQL. Get it wrong and every fact row gets the wrong dimension key. |
| SX-005 | Converts all bracketed space-bearing identifiers (`[stock item]`, `[etl cutoff]`, `[WWI Purchase Order ID]`) to snake_case | Brackets are SQL Server syntax — Databricks uses backticks or (better) just renames to avoid special characters entirely |
| SX-007 | Converts `BEGIN TRANSACTION / COMMIT / ROLLBACK` to Python try/except with Delta write semantics | Explicit transaction management doesn't translate to Spark — Delta provides ACID at the write level |
| SX-008 | Converts `GETDATE()` / `GETUTCDATE()` / `SYSDATETIME()` to `current_timestamp()` (Spark SQL) or `datetime.now(timezone.utc)` (Python) | Date/time function names are completely different between platforms |
| SX-009 | Converts `ISNULL(expr, default)` to `COALESCE(expr, default)` | `ISNULL` is T-SQL specific; `COALESCE` is ANSI SQL and works in Spark |
| SX-010 | Converts `TOP(N)` to `LIMIT N` | Different syntax for row limiting; SCD-2 `TOP(1)` is handled separately by SX-003 |
| SX-014 | **Corrects SSIS truncation bug**: replaces `DELETE FROM Integration.Order_Staging` with `TRUNCATE TABLE inventory_stock.bronze.purchase_staging` (or OVERWRITE mode) | This is the bug fix — the legacy code targeted the wrong table; the new code must target the correct one |
| SX-016 | Converts three-part SQL Server references (`wideworldimportersdw.integration.purchase_staging`) to Unity Catalog references (`inventory_stock.bronze.purchase_staging`) | Object addressing is completely different between platforms |

---

### PE — Performance (9 rules)

**What it governs:** Replacing SQL Server performance optimizations (columnstore indexes, query hints) with Databricks-native equivalents (liquid clustering, auto-compaction, broadcast joins).

**Why it's complex:** SQL Server and Databricks optimize differently. Columnstore indexes are explicit structures in SQL Server; Delta Lake is already columnar (Parquet format) so they're unnecessary. Query hints like `NOLOCK` and `FORCESEEK` control the SQL Server optimizer; Spark has its own optimizer that ignores these. The performance rules ensure the new system is optimized for Databricks, not carrying over SQL Server-specific tuning that's either irrelevant or harmful.

**Key rules:**

| Rule | What it does | Why it matters |
|---|---|---|
| PE-001 | Drops SQL Server columnstore indexes — Delta Parquet is columnar natively | No action required in Databricks; attempting to create columnstore indexes would fail |
| PE-002 | Applies liquid clustering: `CLUSTER BY (date_key, supplier_key)` on `fact_purchase`; `CLUSTER BY (supplier_key/stock_item_key)` on SCD-2 dims | Liquid clustering is Databricks' equivalent of indexing — choosing the right clustering keys determines query performance |
| PE-003 | Schedules `OPTIMIZE` on silver tables after each nightly batch; bronze staging excluded (OVERWRITE pattern) | Delta tables accumulate small files over time from incremental writes; OPTIMIZE compacts them. Staging tables are overwritten each run so don't need it. |
| PE-004 | Creates `_current` suffix views on SCD-2 dimensions for active-row lookups | Avoids full table scans when only the current version of each dimension member is needed |
| PE-005 | Adds date-range predicate to MERGE INTO ON clause to push down to liquid clustering | Without this predicate, the MERGE scans the entire fact table; with it, liquid clustering prunes to just the relevant date range |
| PE-006 | Enables broadcast join hints (`BROADCAST`) for `dimension.supplier` and `dimension.stock_item` in SCD-2 key resolution | These dimension tables are small enough to fit in memory — broadcasting avoids expensive shuffle joins |
| PE-007 | Uses OVERWRITE mode for `bronze.purchase_staging` at run start | Corrects the SSIS truncation bug and eliminates stale rows; no OPTIMIZE needed on overwritten tables |
| PE-008 | Enables `delta.autoOptimize.optimizeWrite` and `autoCompact` on all silver tables; disables on bronze staging | Automatic file optimization for tables that receive incremental writes; disabled on staging since it's overwritten |
| PE-009 | Removes SQL Server `WITH (NOLOCK)` and `WITH (FORCESEEK)` hints | Delta ACID isolation and the Spark optimizer replace both — these hints would either fail or be ignored |

---

### LN — Lineage (8 rules)

**What it governs:** How ETL run tracking (lineage) is preserved and modernized. The source system uses a `lineage` table, a SQL Server SEQUENCE, and stored procedures to track which ETL run loaded which rows. The target must preserve this capability while replacing the implementation.

**Why it's complex:** Lineage is the audit trail — without it, you can't answer "which ETL run loaded this row?" or "did last night's run succeed?" The source uses three interconnected components (SEQUENCE, stored procedures, lineage table) that must all be replaced together. Additionally, Unity Catalog provides automatic lineage tracking for Delta reads/writes, which supplements (but doesn't replace) the explicit lineage tracking.

**Key rules:**

| Rule | What it does | Why it matters |
|---|---|---|
| LN-001 | Migrates `integration.lineage` to `inventory_stock.bronze.lineage_run` Delta table; adds `etl_run_id`, `table_row_count`, `pipeline_name`; enables Change Data Feed | The lineage table gains new columns for better observability; CDF enables downstream consumers to track changes to the lineage log itself |
| LN-002 | Retires `sequences.lineagekey` SEQUENCE; `lineage_run.lineage_key` becomes `GENERATED ALWAYS AS IDENTITY` | The SEQUENCE object has no Databricks equivalent — IDENTITY columns provide the same monotonic key generation |
| LN-003 | Replaces `integration.getlineagekey` stored procedure with Python `open_lineage_record()` / `close_lineage_record()` utility | Stored procedures don't exist in Databricks; Python utility functions provide the same capabilities with better testability |
| LN-004 | Replaces `integration.getlastetlcutofftime` with Python `get_last_etl_cutoff()` + `set_etl_cutoff()` | Same pattern — stored procedure replaced by Python functions reading from the Delta control table |
| LN-005 | Migrates `integration.[etl cutoff]` (space-in-name) to `inventory_stock.bronze.etl_cutoff`; Delta MERGE ACID writes replace transaction-protected UPDATE | Name is fixed (space removed), and the transaction protection comes from Delta ACID instead of explicit `BEGIN TRAN` blocks |
| LN-006 | Propagates `lineage_key` to `silver_fact.fact_purchase.lineage_key` and `bronze.purchase_staging.lineage_key` | Every row in every table carries the lineage key — full traceability from staging through to fact |
| LN-007 | Retires `sequences.reseedallsequences` and reseed utilities; `application.configuration_reseedetl` flagged for scope-owner sign-off | These are testing/maintenance utilities — they may or may not be needed in the new system; decision must be explicit |
| LN-008 | Unity Catalog system lineage auto-captures all Delta reads/writes via three-part naming | Free bonus: Unity Catalog automatically tracks which tables read/write to which other tables — no additional instrumentation required |

---

## How Rules Are Used Downstream

Every rule ID appears in subsequent specs:

- **Product transformation rules** — override, extend, or add to these project rules for product-specific needs
- **To-be design** — every transformation summary comment block lists the rule IDs that drove each design decision
- **Development plan tasks** — each task's DDL/code template references the rules that influenced it (e.g., `-- RULES: LN-001, LN-002, OB-004, TY-017, NM-001, CX-P006`)
- **Generated code** — DDL file headers carry a RULES field listing every rule that influenced the file

This traceability means any stakeholder can ask "why was this table clustered by (date_key, supplier_key)?" and trace back to PE-002, which traces back to the performance analysis of the source system's query patterns.

---

## File Reference

| File | Description |
|---|---|
| `project-transformation-rules.md` | Summary with rule index (all 90 rules listed with intents) |
| `PL-platform.yaml` | 10 platform rules |
| `NM-naming.yaml` | 9 naming rules |
| `TY-types.yaml` | 26 type mapping rules |
| `OB-objects.yaml` | 11 object disposition rules |
| `SX-syntax.yaml` | 17 syntax translation rules |
| `PE-performance.yaml` | 9 performance optimization rules |
| `LN-lineage.yaml` | 8 lineage tracking rules |

All files located at: `project/current/project-transformation-rules/`
