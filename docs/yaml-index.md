# YAML Rules Index — Inventory_Stock_Project

**Project:** Inventory_Stock_Project
**Product:** Purchase
**Last updated:** 2026-09-15

All transformation rule YAML files live in the `rules/` directories. Project-level rules apply to every product; product-level rules override, extend, or add to them for the Purchase product specifically.

---

## Project-Level Rules (`project/current/project-transformation-rules/`)

| File | Rules | Summary |
|---|---|---|
| `PL-platform.yaml` | 10 | Establishes the SQL Server 2014 → Databricks engine contract: covers schema namespace mapping, Delta storage format, SEQUENCE/IDENTITY replacement, SSIS → Databricks Workflow migration, stored procedure → Python notebook conversion, columnstore → liquid clustering, medallion layer assignment, and optimistic concurrency. |
| `NM-naming.yaml` | 9 | Defines all identifier renaming conventions: PascalCase/camelCase → lowercase_snake_case, space-in-name resolution, schema → Unity Catalog three-part name mapping, view/staging/constraint naming suffixes, and stored procedure → Python function name conversion. |
| `TY-types.yaml` | 26 | Maps every SQL Server type to its Spark equivalent — integers, decimal (DECIMAL/NUMERIC), all string variants, date/time (DATETIME2 → TIMESTAMP_NTZ), binary, boolean (BIT → BOOLEAN), NULL constraints, IDENTITY, SEQUENCE, collation, defaults, and computed columns — plus domain-specific rules for ETL control tables, SCD-2 dimension validity columns, pricing decimals, and the date calendar table. |
| `OB-objects.yaml` | 11 | Assigns each procurement source object to its medallion layer and migration decision: SCD-2 dimensions → silver_dim with _current views, fact.purchase → silver_fact with liquid clustering, staging → bronze (OVERWRITE), control tables → bronze, ETL stored procedures → Python notebooks, SEQUENCE → IDENTITY, SSIS → Workflow DAG, BI reports → Databricks SQL Warehouse DirectQuery, and reseed utilities → conditional DROP. |
| `SX-syntax.yaml` | 17 | Converts T-SQL syntax patterns to Spark SQL / Python: MERGE → MERGE INTO, SCD-2 correlated TOP(1) subquery → ROW_NUMBER() + COALESCE, NEXT VALUE FOR → IDENTITY, bracket quoting removal, BEGIN TRAN → Python try/except, date functions, ISNULL → COALESCE, TOP → LIMIT, PRINT → logger, schema → Unity Catalog three-part names, and CAST/CONVERT rewrites. |
| `PE-performance.yaml` | 9 | Defines all performance optimisation strategies: drop columnstore indexes (Delta is columnar by default), liquid clustering on fact/dim tables, OPTIMIZE schedule after nightly batch, SCD-2 _current view for fast lookups, MERGE predicate pushdown for data skipping, broadcast join hints, bronze staging lifecycle (OVERWRITE, no clustering), autoOptimize settings for silver tables, and NOLOCK/FORCESEEK hint removal. |
| `LN-lineage.yaml` | 8 | Governs ETL audit and lineage tracking: migration of integration.lineage → bronze.lineage_run Delta table, SEQUENCE → IDENTITY replacement for lineagekey, getlineagekey → open_lineage_record() Python utility, get_last_etl_cutoff() / set_etl_cutoff() watermark control, lineage_key propagation to fact and staging tables, retirement of reseed procedures, and two-tier Unity Catalog system + application lineage model. |

---

## Product-Level Rules (`products/Purchase/current/specifications/product-transformation-rules/`)

### Rule-set meta-files

| File | Summary |
|---|---|
| `override.yaml` | Contains one override (TY-P001): SCD-2 validity columns `valid_from`/`valid_to` on Purchase-scope dimension tables map to DATE instead of TIMESTAMP_NTZ, because the Purchase product treats SCD-2 boundaries as calendar dates with no intraday component. |
| `extensions.yaml` | Contains 12 extensions across TY, OB, PE, LN, and SX dimensions: the five-column SCD-2 control block (TY-P002), MONEY/SMALLMONEY → DECIMAL mappings (TY-P003), geography CLR → three-column decomposition (TY-P004), key=0 sentinel bootstrap notebooks (OB-P001), audit columns on purchase_staging (OB-P002), materialized vs. regular view classification (OB-P003), shared helper modules (OB-P004), pre-DBR-13.3 alternative partitioning (PE-P001), conditional OPTIMIZE threshold (PE-P002), taskValues lineage_key injection (LN-P001 / SX-P001), CONVERT style 112 date arithmetic (SX-P002), and sk_resolver.py pre-join pattern (SX-P003). |
| `new-rules.yaml` | Contains 11 entirely new product rules across SX, QA, and CX dimensions: the inline lineage-close UPDATE pattern (SX-P004), five data quality rules (QA-P001 row count reconciliation through QA-P005 DQ rejection store), and six custom/convention rules (CX-P001 config externalisation through CX-P006 DDL header standard). |
| `deactivations.yaml` | Empty — no project-level rules are deactivated for the Purchase product; all project rules remain active. |

### Per-dimension files (inherited project rules + product-specific rules)

| File | Rules | Summary |
|---|---|---|
| `PL-platform.yaml` | 10 inherited | All 10 project Platform rules are inherited without modification; the SSIS staging-truncation bug correction (PL-005) and medallion layer assignments (PL-009) are directly relevant to Purchase and carried forward unchanged. |
| `NM-naming.yaml` | 9 inherited | All 9 project Naming rules are inherited without modification; NM-002 (space-in-name resolution) is of particular importance because `dimension.[stock item]` → `inventory_stock.silver_dim.stock_item` and all space-bearing Purchase column names must follow the explicit column_mapping table. |
| `TY-types.yaml` | 26 inherited + 4 product | Reproduces all 26 project Type rules and adds 4 Purchase rules: TY-P001 overrides DATETIME2 → DATE for SCD-2 validity columns, TY-P002 defines the full five-column SCD-2 control block, TY-P003 adds MONEY/SMALLMONEY → DECIMAL mappings, and TY-P004 adds geography CLR → three-column decomposition. |
| `OB-objects.yaml` | 11 inherited + 4 product | Reproduces all 11 project Object rules and adds 4 Purchase rules: OB-P001 mandates key=0 sentinel bootstrap notebooks per SCD-2 dimension, OB-P002 adds lineage_key and _extracted_at_utc audit columns to purchase_staging, OB-P003 classifies analytics views as materialized or regular, and OB-P004 promotes scd2_merge.py / sk_resolver.py / fact_merge.py as first-class shared helper modules. |
| `SX-syntax.yaml` | 17 inherited + 4 product | Reproduces all 17 project Syntax rules and adds 4 Purchase rules: SX-P001 specifies the dbutils.jobs.taskValues lineage_key injection pattern, SX-P002 adds the CONVERT style 112 date-arithmetic rewrite, SX-P003 defines the sk_resolver.py pre-join step as the canonical surrogate key resolution replacement, and SX-P004 specifies the inline lineage-close UPDATE conversion. |
| `PE-performance.yaml` | 9 inherited + 2 product | Reproduces all 9 project Performance rules and adds 2 Purchase rules: PE-P001 defines an alternative PARTITIONED BY + ZORDER strategy for runtimes earlier than DBR 13.3, and PE-P002 makes the OPTIMIZE step conditional on a configurable row-count threshold (default 10,000) to avoid wasted compute on low-volume nights. |
| `LN-lineage.yaml` | 8 inherited + 1 product | Reproduces all 8 project Lineage rules and adds 1 Purchase rule: LN-P001 specifies that lineage_key is obtained via dbutils.jobs.taskValues.get from the upstream nb_extract_watermark task — not by calling open_lineage_record() directly — making taskValues the canonical lineage_key propagation mechanism for all downstream Purchase ETL notebooks. |
| `QA-quality.yaml` | 5 new (product-only) | Defines 5 new data quality rules with no project-level equivalents: QA-P001 row count reconciliation between staging and fact (blocking), QA-P002 orphaned surrogate key detection (non-blocking warning), QA-P003 referential integrity checks via LEFT ANTI JOIN writing violations to bronze.dq_rejections (non-blocking), QA-P004 business rule assertions on loaded rows (non-blocking warning), and QA-P005 the centralised DQ rejection store DDL and append pattern. |
| `CX-custom.yaml` | 6 new (product-only) | Defines 6 new custom/convention rules with no project-level equivalents: CX-P001 externalises hard-coded date filters to config/environment.yaml, CX-P002 externalises business factors with NULL guards and bound assertions, CX-P003 consolidates duplicate scalar functions into NULL-guarded Python UDFs in src/common/udfs.py, CX-P004 enforces the standard Purchase codebase directory layout, CX-P005 mandates the standard Python ETL notebook skeleton (imports → lineage_key → zero-rows guard → try/except → conditional OPTIMIZE → close lineage), and CX-P006 requires a standard SQL DDL file header block in every generated DDL file. |
