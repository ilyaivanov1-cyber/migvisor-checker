# Project Transformation Rules: GlobalPurchase_Project
# Rule Set Level: project
# Active Dimensions: PL, NM, TY, OB, SX, IF
# Date: 2026-08-25
# Source Platform: Microsoft SQL Server 2014 (wideworldimportersdw)
# Target Platform: Databricks Delta Lake, Unity Catalog (globalpurchase)

---

## Active Dimensions

| Dimension | Prefix | File | Rule Count |
|---|---|---|---|
| Platform | PL | [PL-platform.yaml](PL-platform.yaml) | 4 |
| Naming | NM | [NM-naming.yaml](NM-naming.yaml) | 6 |
| Types | TY | [TY-types.yaml](TY-types.yaml) | 6 |
| Objects | OB | [OB-objects.yaml](OB-objects.yaml) | 5 |
| Syntax | SX | [SX-syntax.yaml](SX-syntax.yaml) | 5 |
| Interface | IF | [IF-interface.yaml](IF-interface.yaml) | 4 |

**Total: 30 rules across 6 dimensions**

Application order: PL → NM → TY → OB → SX → IF

---

## Rule Index

### Platform (PL)

| ID | Intent |
|---|---|
| PL-001 | Every table created in the target Databricks environment must use the Delta Lake storage format by including the USING DELTA clause in its DDL. |
| PL-002 | All SSIS packages and their scheduling logic must be replaced by Databricks Workflow jobs that enforce the Staging → Dimensions/Facts → Mart task dependency ordering. |
| PL-003 | The target Unity Catalog must be organized into three schema layers — stg, dim/fact, and mart — mapping to the source system's raw, integration, and presentation zones respectively. |
| PL-004 | All SQL Server SEQUENCE objects and NEXT VALUE FOR calls used to generate surrogate keys must be eliminated and replaced with Delta Lake column-level GENERATED ALWAYS AS IDENTITY definitions. |

### Naming (NM)

| ID | Intent |
|---|---|
| NM-001 | All source object names (tables, columns, views, stored procedures) must be converted to lowercase_snake_case in the target Databricks Unity Catalog. |
| NM-002 | Any spaces embedded in source object or schema-qualified names must be replaced with underscores before the name is applied in the target system. |
| NM-003 | Every view created in the target Databricks Unity Catalog must carry the prefix v_ to distinguish views from base tables at a glance. |
| NM-004 | All staging (bronze/stg-layer) tables must carry the _staging suffix so they are unambiguously identified as transient landing objects, with the single exception of the etl_cutoff control table. |
| NM-005 | Each source SQL Server schema must be translated to the corresponding target Unity Catalog schema that reflects the target data architecture layer (integration→stg, dimension→dim, fact→fact, analytics→mart). |
| NM-006 | Table names must not be prefixed with the name of the schema layer they reside in — the three-part Unity Catalog name already conveys the layer (e.g. globalpurchase.fact.purchase, not globalpurchase.fact.fact_purchase). |

### Types (TY)

| ID | Intent |
|---|---|
| TY-001 | Convert INT, SMALLINT, TINYINT to INT and BIGINT to BIGINT in all Delta Lake table definitions. |
| TY-002 | Convert DECIMAL, NUMERIC, FLOAT, and REAL SQL Server types to DECIMAL(p,s) or DOUBLE in Databricks, preserving precision and scale where applicable. |
| TY-003 | Consolidate all SQL Server character and text types (VARCHAR, NVARCHAR, CHAR, NCHAR, TEXT, NTEXT) into the Databricks STRING type. |
| TY-004 | Convert SQL Server temporal types (DATE, DATETIME, DATETIME2, SMALLDATETIME, TIME) to DATE, TIMESTAMP, or STRING as appropriate; TIME maps to STRING due to no native type in Databricks. |
| TY-005 | Convert SQL Server BIT to BOOLEAN, UNIQUEIDENTIFIER to STRING, and VARBINARY/BINARY to BINARY in all Delta Lake table definitions. |
| TY-006 | Migrate SQL Server auto-increment IDENTITY columns to the Delta Lake native GENERATED ALWAYS AS IDENTITY syntax to maintain surrogate key generation on the target platform. |

### Objects (OB)

| ID | Intent |
|---|---|
| OB-001 | All tables in the fact, dimension, and integration schemas are recreated in Databricks as Delta Lake tables under the globalpurchase Unity Catalog. |
| OB-002 | All in-scope SQL Server stored procedures (migratestaged* family) are replaced by equivalent Python functions with snake_case names matching the original procedure names. |
| OB-003 | SQL Server SEQUENCE objects in the sequences schema are not migrated; all references to NEXT VALUE FOR are replaced by GENERATED ALWAYS AS IDENTITY columns for surrogate keys or Python-managed counters for lineage keys. |
| OB-004 | Objects in the application schema are excluded from object migration; any relevant behavior they encode is re-expressed as idempotent Databricks bootstrap scripts run at environment initialisation. |
| OB-005 | All in-scope SQL Server views are recreated in Databricks with a v_ name prefix; views explicitly listed as out of scope (e.g. analytics.v_ordertoyearanalytics) are not migrated. |

### Syntax (SX)

| ID | Intent |
|---|---|
| SX-001 | Eliminate BEGIN TRAN / COMMIT / ROLLBACK constructs because Delta Lake provides per-statement atomicity that makes explicit transaction wrapping unnecessary. |
| SX-002 | Replace the SQL Server pattern of loading data into a staging table and then calling a migratestaged* stored procedure with an equivalent Delta MERGE INTO operation in a Python or SQL notebook. |
| SX-003 | Convert the SQL Server SCD Type-2 pattern of UPDATE Valid To + INSERT into a single atomic Delta MERGE INTO statement with active/history logic and an is_current BOOLEAN flag. |
| SX-004 | Convert the SQL Server fact table refresh pattern of DELETE + INSERT into a single idempotent Delta MERGE INTO statement keyed on the business key. |
| SX-005 | Translate T-SQL-specific functions, operators, data types, and DML constructs to their Spark SQL or Python equivalents so that all generated code executes correctly on Databricks. |

### Interface (IF)

| ID | Intent |
|---|---|
| IF-001 | Migrate the legacy SSIS daily ETL orchestration to a Databricks Workflow with explicit task dependencies enforcing Staging → Dimensions/Facts → Mart execution order. |
| IF-002 | Replace full SSIS extracts with JDBC incremental reads filtered by LastEditedWhen, committing the watermark to etl_cutoff only after all downstream loads succeed to guarantee exactly-once processing semantics. |
| IF-003 | Eliminate hard-coded SQL Server credentials by storing the JDBC URL, username, and password in Databricks Secrets and requiring the environment-specific JDBC driver class to be configured before pipeline execution. |
| IF-004 | Standardise the staging strategy so dimension data is held only in transient in-memory temp views consumed within the same Workflow run, while fact data is written to globalpurchase.stg.* tables via truncate+overwrite to ensure idempotency. |

---

*Generated by migVisor Transformation Co-Pilot · 2026-08-25 · Initial pass (no as-is files available)*
