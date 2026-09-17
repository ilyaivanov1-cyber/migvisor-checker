# To-Be Design — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Target:** Databricks Delta Lake, Unity Catalog (`inventory_stock`)
**Pipeline stage:** to-be
**Generated:** 2026-09-07

---

## What This Spec Is

The to-be design is the **complete target-state specification** — what the Purchase product looks like on Databricks after migration. It is the last major TCP document produced before the handoff to SmartBuilder code generation.

It mirrors the as-is analysis section-by-section (6 sections, same structure) but describes the **future state** instead of the current state. Every transformation is annotated with the rule IDs that drove the decision, creating a fully traceable chain: as-is behavior → transformation rule → to-be design.

Think of it as the **architectural blueprint** — if the as-is is the autopsy of the old system, the to-be is the construction plan for the new one.

---

## Why This Spec Exists

### The bridge between analysis and code

The to-be occupies a specific position in the flow:

```
as-is (what exists) → transformation rules (how to convert) → to-be (what to build)
```

Without the to-be:
- SmartBuilder would have to interpret the as-is and rules simultaneously, guessing how to combine them.
- Reviewers couldn't verify that rules were applied correctly — they'd have to mentally apply 90+ rules to the as-is to determine what the target should look like.
- Developers would disagree about design decisions that the rules leave ambiguous (e.g., "the rule says replace TOP(1) with ROW_NUMBER — but what window spec? what ordering? what tie-breaker?").

The to-be resolves all ambiguity. It contains the exact target table schemas, the exact Python code for critical functions, the exact MERGE predicates, and the exact QA assertion logic.

### The diff against the as-is

Every section in the to-be is a **diff** against the corresponding as-is section. Each section ends with a `<!-- TRANSFORMATION SUMMARY -->` comment block listing every rule ID that was applied. A reviewer can:

1. Read an as-is section (e.g., "the legacy SCD-2 resolution uses a correlated TOP(1) subquery")
2. Find the corresponding to-be section (e.g., "the target uses sk_resolver.py with a temporal range JOIN + ROW_NUMBER")
3. Check the transformation summary to verify the correct rules were applied (SX-003, SX-P003, TY-P001)

This traceability makes the to-be **auditable** — every design decision can be traced back to a specific rule, which traces back to a specific source system observation.

---

## Section-by-Section Breakdown

---

## Section 1 — Analytical Data Product Description

### What it contains

**Section 1.1 — Definition:** A comprehensive narrative of the modernized product — what it delivers, how it works, what components it has, and what business value it provides. Much longer than the as-is definition because it must describe not just what exists but how every piece was transformed and why.

**Section 1.2 — Metadata table:** A 15-field structured table mirroring the as-is metadata table, with every field updated to reflect the target state.

### What changed from the as-is

The to-be definition describes a fundamentally different system that preserves the same business semantics:

| Aspect | As-Is | To-Be | Driving rules |
|---|---|---|---|
| **Central fact table** | `wideworldimportersdw.fact.purchase` (SQL Server rowstore) | `inventory_stock.silver_fact.fact_purchase` (Delta managed, CLUSTER BY date_key, supplier_key) | PL-002, OB-002, PE-002 |
| **Staging** | `integration.purchase_staging` — never correctly truncated (SSIS bug) | `bronze.purchase_staging` — OVERWRITE mode per run, with `lineage_key` and `_extracted_at_utc` audit columns | OB-003, OB-P002, SX-014, PE-007 |
| **SCD-2 resolution** | Correlated `TOP(1)` subquery UPDATE on staging table | `sk_resolver.py` — temporal range JOIN + `ROW_NUMBER() OVER (... ORDER BY valid_from DESC) = 1` | SX-003, SX-P003 |
| **Lineage** | `sequences.lineagekey` SEQUENCE + stored procedures | `bronze.lineage_run` with IDENTITY key + Python utilities + `taskValues` propagation | LN-001, LN-002, LN-003, LN-P001 |
| **Orchestration** | SSIS Purchase container within `pipeline_dailyetlmain` | Databricks Workflow `nightly_etl_purchase` with explicit task dependencies | PL-005, OB-007 |
| **Data quality** | No structured DQ checks — problems invisible until BI users notice | 5 QA assertions (1 blocking, 4 informational) + centralized `dq_rejections` table | QA-P001 through QA-P005 |
| **Configuration** | Hard-coded date filters and business factors in T-SQL | Externalized to `config/environment.yaml` under `purchase.etl` and `purchase.business_rules` | CX-P001, CX-P002 |
| **Naming** | Space-bearing names (`[stock item]`, `[etl cutoff]`, `[WWI Purchase Order ID]`) | `lowercase_snake_case` throughout (`stock_item`, `etl_cutoff`, `wwi_purchase_order_id`) | NM-001, NM-002 |

### Key components listed in the to-be

The to-be definition enumerates **every deliverable** — 8 tables, 3 notebooks, 4 Python modules, 1 config file, 1 Workflow:

| Component | Type | New vs. Migrated |
|---|---|---|
| `silver_fact.fact_purchase` | Delta managed table | Migrated from `fact.purchase` |
| `bronze.purchase_staging` | Delta managed table | Migrated from `integration.purchase_staging` (bug fixed) |
| `bronze.etl_cutoff` | Delta managed table | Migrated from `integration.etl cutoff` |
| `bronze.lineage_run` | Delta managed table | Migrated from `integration.lineage` + `sequences.lineagekey` |
| `bronze.dq_rejections` | Delta managed table | **New** — didn't exist in legacy |
| `silver_dim.supplier` | Delta SCD-2 table + `_current` view | Migrated from `dimension.supplier` (externally owned) |
| `silver_dim.stock_item` | Delta SCD-2 table + `_current` view | Migrated from `dimension.stock item` (externally owned, space removed) |
| `silver_dim.date` | Delta table | Migrated from `dimension.date` (externally owned, static) |
| `nb_extract_watermark` | Python notebook | Replaces SSIS watermark + lineage registration steps |
| `nb_extract_purchase` | Python notebook | Replaces SSIS extract dataflow |
| `migrate_staged_purchase_data` | Python notebook | Replaces `migratestagedpurchasedata` stored procedure |
| `sk_resolver.py` | Python module | **New** — replaces inline correlated subquery pattern |
| `fact_merge.py` | Python module | **New** — replaces inline T-SQL MERGE pattern |
| `src/common/udfs.py` | Python module | **New** — consolidates duplicate scalar functions (CX-P003) |
| `src/common/lineage_utils.py` | Python module | **New** — replaces `getlineagekey` and `getlastetlcutofftime` procedures |
| `config/environment.yaml` | YAML config | **New** — externalizes hard-coded values (CX-P001, CX-P002) |
| `nightly_etl_purchase` | Databricks Workflow | Replaces SSIS Purchase container |

### The metadata table — field-by-field changes

| # | Field | Key change from as-is | Why |
|---|---|---|---|
| 3 | Process Type | "full OVERWRITE of bronze staging per run to eliminate legacy stale-row accumulation" added | Documents the bug fix as part of the process definition |
| 8 | Data Access | Unity Catalog RBAC specified: silver readable by BI + analysts, bronze restricted to ETL principals | Legacy had no structured access control; target has explicit RBAC |
| 9 | Data Sources | All references changed to `inventory_stock.*` three-part names | Source references updated from SQL Server to Databricks |
| 10 | Filters Applied | "date filter parameters externalised to `config/environment.yaml`" added | CX-P001 — no more hard-coded date literals |
| 11 | Calculated Fields | `lineage_key` via `open_lineage_record()` + `taskValues.set`; `_extracted_at_utc` audit column added | LN-P001, OB-P002 — new observability columns |
| 12 | Business DQ Rules | QA-P001 through QA-P004 specified with blocking/informational classification | Legacy had no formal DQ rules; target has 5 assertions |
| 13 | Technical DQ Rules | "OVERWRITE mode eliminates stale-row accumulation from legacy SSIS truncation bug" | The bug fix is now a documented technical DQ rule |

### Why this section matters

Section 1 is the **executive summary** of the entire to-be design. A stakeholder who reads only this section understands:
- What's being delivered (8 tables, 3 notebooks, 4 modules, 1 Workflow)
- What's new that didn't exist before (DQ framework, config externalization, UDF consolidation)
- What bugs are being fixed (staging truncation)
- What the business value is (reliable, auditable procurement analytics on a modern platform)

---

## Section 2 — Consumers and Use Cases

### What it contains

The same 3 consumers from the as-is, updated to reflect the target state:

| Consumer | As-Is | To-Be | Key change |
|---|---|---|---|
| `wwidw_purchase_and_sale_per_stockitem_dynamic` | Direct SQL Server connection to `fact.purchase` + `fact.sale` | Databricks SQL Warehouse; references updated to `inventory_stock.silver_fact.fact_purchase` + `inventory_stock.silver_fact.fact_sale` | Table names, column names (snake_case), connection endpoint all changed. **Still requires coordinated cutover with Sales_Orders.** |
| `wwidw_ordered_by_supplier` | Direct SQL Server connection to `fact.purchase` + `dimension.supplier` | Databricks SQL Warehouse; references updated to `inventory_stock.silver_fact.fact_purchase` + `inventory_stock.silver_dim.supplier` | Same changes. Self-contained within Purchase domain. |
| `integration.migratestagedpurchasedata` (internal ETL) | Stored procedure reading `integration.etl cutoff` | Python notebook `migrate_staged_purchase_data.py` as Databricks Workflow task | Entire consumption mechanism replaced — stored procedure → notebook |

### The transformation summary for this section

The to-be documents three specific changes:

1. **Power BI reports reconnected** — from direct SQL Server connections to Databricks SQL Warehouse. Object references updated from legacy schema-qualified names to `inventory_stock.*` Unity Catalog names. All space-bearing column names normalized to snake_case per NM-002.

2. **Internal ETL consumer replaced** — `integration.migratestagedpurchasedata` stored procedure replaced by `migrate_staged_purchase_data.py` Python notebook, per OB-007 and PL-006. No stored-procedure dependency exists in the target.

3. **Cross-domain cutover constraint preserved** — the `wwidw_purchase_and_sale_per_stockitem_dynamic` report still depends on Sales_Orders data. The to-be explicitly states that coordinated cutover is required.

### Why this section matters

Consumer reconnection is one of the most commonly overlooked migration tasks. The reports work fine in testing (where you might mock the data) but fail in production because:
- The connection string still points to SQL Server
- The column names still have spaces
- The schema references are still `fact.purchase` instead of `silver_fact.fact_purchase`

By specifying the exact changes per consumer, the to-be ensures nothing is missed during cutover.

---

## Section 3 — Model (Analytical Data Product)

### What it contains

**Section 3.1 — Target ER diagram:** A full Mermaid entity-relationship diagram showing all target Delta tables with their exact column definitions, types, constraints, and relationships. This is the **physical data model** of the target system.

**Section 3.2 — Textual description:** A layer-by-layer narrative describing each table group in the medallion architecture: Bronze Staging, Bronze Control, Bronze DQ, Silver Dim, and Silver Fact.

### What changed from the as-is model

The target model has significant structural differences from the source:

**New tables (didn't exist in legacy):**

| Table | Why it's new |
|---|---|
| `bronze.dq_rejections` | Centralized DQ rejection sink — 10 columns including `lineage_key`, `rule_id`, `violation_column`, `violation_value`, `rejection_reason` (QA-P005) |

**Modified tables (structural changes):**

| Table | Key structural changes | Driving rules |
|---|---|---|
| `silver_fact.fact_purchase` | `purchase_key` → `BIGINT GENERATED ALWAYS AS IDENTITY`; all column names snake_cased; `CLUSTER BY (date_key, supplier_key)` | TY-017, NM-001, PE-002 |
| `bronze.purchase_staging` | Added `lineage_key BIGINT` and `_extracted_at_utc TIMESTAMP` audit columns; `supplier_key`/`stock_item_key` now BIGINT (was INT) and nullable (populated by sk_resolver after extract) | OB-P002, TY-003 |
| `bronze.lineage_run` | Replaces both `integration.lineage` AND `sequences.lineagekey`; new columns: `etl_run_id`, `table_row_count`, `pipeline_name`; CDF enabled | LN-001, LN-002 |
| `silver_dim.supplier` | 5-column SCD-2 control block (`valid_from DATE`, `valid_to DATE`, `row_effective_date`, `row_expiry_date`, `is_current_row`); geography CLR → 3 columns (`delivery_location_wkt STRING`, `delivery_location_lat DOUBLE`, `delivery_location_lon DOUBLE`) | TY-P001, TY-P002, TY-P004 |
| `silver_dim.stock_item` | Space removed from name; MONEY columns (`unit_price`, `recommended_retail_price`) → `DECIMAL(18,2)`; `Photo varbinary` → `BINARY`; same 5-column SCD-2 control block | NM-002, TY-P003, TY-014, TY-P001, TY-P002 |

**Type changes across all tables:**

| SQL Server Type | Delta Type | Columns affected | Rule |
|---|---|---|---|
| `BIGINT IDENTITY` | `BIGINT GENERATED ALWAYS AS IDENTITY` | `purchase_key`, `purchase_staging_key`, `lineage_key`, `rejection_id` | TY-017 |
| `BIT` | `BOOLEAN` | `is_order_finalized`, `was_successful`, `is_current_row`, `is_chiller_stock` | TY-015 |
| `DATETIME2` | `TIMESTAMP` (control tables) or `DATE` (SCD-2 validity, per TY-P001 override) | timestamps in lineage_run/etl_cutoff; valid_from/valid_to in dimensions | TY-012, TY-P001 |
| `NVARCHAR(n)` | `STRING` | All string columns | TY-009 |
| `VARBINARY(MAX)` | `BINARY` | `photo` in stock_item | TY-014 |
| `MONEY` | `DECIMAL(18,2)` | `unit_price`, `recommended_retail_price` in stock_item | TY-P003 |
| `geography CLR` | `STRING` + `DOUBLE` + `DOUBLE` (3-column decomposition) | `delivery_location` in supplier | TY-P004 |

### The layer-by-layer description

| Layer | Tables | Key design decisions |
|---|---|---|
| **Bronze Staging** | `purchase_staging` | OVERWRITE mode per run (bug fix); no liquid clustering (ephemeral data); autoOptimize disabled; `supplier_key`/`stock_item_key` nullable at extract time (populated by sk_resolver later) |
| **Bronze Control** | `etl_cutoff`, `lineage_run` | `lineage_run` has IDENTITY PK replacing SEQUENCE; CDF enabled for downstream change tracking; Delta ACID replaces explicit transaction blocks |
| **Bronze DQ** | `dq_rejections` | New table; row-level rejection store linked to pipeline runs via `lineage_key`; enables investigation without blocking the load |
| **Silver Dim** | `supplier`, `stock_item`, `date` | 5-column SCD-2 control block (TY-P002); `valid_from`/`valid_to` as `DATE` not `TIMESTAMP_NTZ` (TY-P001 override); `_current` views classified as regular VIEW not MATERIALIZED (OB-P003); key=0 sentinel rows must be bootstrapped (OB-P001); externally owned |
| **Silver Fact** | `fact_purchase` | `CLUSTER BY (date_key, supplier_key)` for analytical query patterns; autoOptimize + autoCompact enabled; fallback for pre-DBR 13.3: `PARTITIONED BY (date_key) ZORDER BY (supplier_key, stock_item_key)` per PE-P001 |

### Why this section matters

The ER diagram is the **source of truth for DDL generation**. SmartBuilder reads these column definitions to produce the `CREATE TABLE` statements. Every column name, type, nullability constraint, and clustering key comes from this section.

The layer-by-layer description captures design decisions that aren't visible in the ER diagram alone — why autoOptimize is disabled on staging, why `_current` views are regular VIEWs not MATERIALIZED, why the SCD-2 validity columns are DATE instead of TIMESTAMP_NTZ. These decisions are annotated with rule IDs so they're traceable.

---

## Section 4 — Column-Level Lineage

### What it contains

The **largest section** of the to-be — and the most detailed. It mirrors the as-is lineage section but documents the target pipeline with all transformations applied.

**Section 4.1 — Key Columns/Metrics:** 10 columns documented (vs. 9 in the as-is — `wwi_purchase_order_id` is now explicitly documented as the MERGE predicate column).

**Section 4.2 — Lineage Diagram:** A full Mermaid flow diagram with 7 subgraphs (OLTP Source, Task 1 nb_extract_watermark, Task 2 nb_extract_purchase, Task 3 migrate_staged_purchase_data, Silver Dimensions, Target Fact, BI Consumers). Color-coded by role: green=source, red=control, yellow=calculation, purple=aggregation, blue=target.

**Section 4.3 — Column-Level Lineage Table:** Every target column mapped from source through intermediate with exact transformation logic and rule IDs. **19 rows** (vs. 9 in the as-is) because the target tracks more columns — audit columns, DQ rejection columns, geography decomposition columns, and lineage propagation columns.

**Section 4.4 — Step-by-Step Transformation Table:** A **22-step table** (vs. 11 in the as-is) documenting every ETL step in the target pipeline.

**Section 4.5 — Known Downstream Dependencies:** 10 dependent objects (vs. 8 in the as-is) — includes new internal dependencies (Python modules) not present in the legacy system.

### The 22-step target pipeline

The target pipeline has twice as many steps as the legacy because it adds DQ validation, conditional optimization, and separates concerns that were tangled together in the stored procedure:

| Step | Task | What happens | Key difference from as-is | Rules |
|---|---|---|---|---|
| 1 | nb_extract_watermark | Read last ETL cutoff | Python `get_last_etl_cutoff()` replaces stored procedure | LN-004, LN-005 |
| 2 | nb_extract_watermark | Open lineage record | `open_lineage_record()` with IDENTITY key replaces SEQUENCE | LN-002, LN-003 |
| 3 | nb_extract_watermark | Publish watermark + lineage key via taskValues | **New** — `taskValues.set` propagation mechanism didn't exist in SSIS | LN-P001, SX-P001 |
| 4 | nb_extract_purchase | Consume task values | **New** — `taskValues.get` to receive lineage_key | LN-P001 |
| 5 | nb_extract_purchase | Incremental OLTP JOIN + filter | Same 5-table JOIN; `GETDATE()` → `current_timestamp()` | SX-008 |
| 6 | nb_extract_purchase | Date derivation | `CAST(po.OrderDate AS DATE)` — same logic, Spark SQL syntax | SX-017 |
| 7 | nb_extract_purchase | Boolean coercion | `IsOrderFinalized BIT → BOOLEAN` — **new** explicit type conversion | TY-015 |
| 8 | nb_extract_purchase | String normalization | `NVARCHAR → STRING` — automatic in Spark | TY-009 |
| 9 | nb_extract_purchase | Watermark metadata injection | `current_timestamp() AS _extracted_at_utc` — **new** audit column | OB-P002, SX-008 |
| 10 | nb_extract_purchase | Staging overwrite | `mode("overwrite")` — **fixes the SSIS bug** | SX-014 |
| 11 | migrate_staged_purchase_data | Consume lineage key | `taskValues.get` — binds to the same lineage record | LN-P001 |
| 12 | migrate_staged_purchase_data | Zero-rows guard | **New** — if staging is empty, close lineage cleanly and exit | CX-P005 |
| 13 | sk_resolver.py | Supplier SCD-2 key resolution | Temporal range JOIN + `ROW_NUMBER() DESC = 1` + `COALESCE(..., 0)` + BROADCAST hint — **completely reimplemented** | SX-003, SX-P003, TY-P001, PE-006 |
| 14 | sk_resolver.py | Stock item SCD-2 key resolution | Same pattern as step 13 | SX-003, SX-P003 |
| 15 | fact_merge.py | Fact MERGE INTO | `MERGE INTO ... ON (wwi_purchase_order_id, date_key, supplier_key, stock_item_key) WHEN MATCHED THEN UPDATE WHEN NOT MATCHED THEN INSERT` — replaces DELETE + INSERT pattern | SX-001, SX-002 |
| 16 | migrate_staged_purchase_data | Row count reconciliation | **New** — `assert staging_count == rows_merged` (blocking) | QA-P001 |
| 17 | migrate_staged_purchase_data | Orphaned SK detection | **New** — LEFT ANTI JOIN for key=0 counts (informational) | QA-P002 |
| 18 | migrate_staged_purchase_data | RI checks → dq_rejections | **New** — LEFT ANTI JOIN per FK column; violations written to `dq_rejections` | QA-P003 |
| 19 | migrate_staged_purchase_data | Business rule assertions | **New** — negative quantities, out-of-window dates, null package (informational) | QA-P004 |
| 20 | migrate_staged_purchase_data | Conditional OPTIMIZE | **New** — only if `rows_merged > 10,000` (threshold from `environment.yaml`) | PE-P002 |
| 21 | migrate_staged_purchase_data | Advance ETL watermark | `set_etl_cutoff()` — same semantics as legacy, Python implementation | LN-004, LN-005 |
| 22 | migrate_staged_purchase_data | Close lineage record | `close_lineage_record()` — same semantics, Python implementation | SX-P004, LN-003 |

**Steps that are entirely new (didn't exist in legacy):** 3, 4, 7, 9, 12, 16, 17, 18, 19, 20 — ten new steps, all adding observability, quality, or operational improvements.

**Steps that were fundamentally reimplemented:** 2 (SEQUENCE → IDENTITY), 10 (bug fix), 13-14 (TOP(1) → ROW_NUMBER), 15 (DELETE+INSERT → MERGE INTO).

**Steps that are direct translations:** 1, 5, 6, 8, 11, 21, 22 — same logic, different syntax.

### The SCD-2 resolution — as-is vs. to-be

This is the most critical transformation in the entire migration. The to-be includes the **actual Python code** for `sk_resolver.py`:

```python
def resolve_supplier_key(staging_df, supplier_dim_df):
    w = Window.partitionBy("stg.purchase_staging_key").orderBy(F.col("dim.valid_from").desc())
    resolved = (
        staging_df.alias("stg")
        .join(
            F.broadcast(supplier_dim_df).alias("dim"),
            (F.col("stg.wwi_supplier_id") == F.col("dim.wwi_supplier_id"))
            & (F.col("stg.last_modified_when") > F.col("dim.valid_from").cast("timestamp"))
            & (F.col("stg.last_modified_when") <= F.col("dim.valid_to").cast("timestamp")),
            "left"
        )
        .withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .withColumn("supplier_key", F.coalesce(F.col("dim.supplier_key"), F.lit(0)))
        .drop("rn")
    )
    return resolved
```

**What changed from the as-is correlated subquery:**

| Aspect | As-Is (T-SQL) | To-Be (PySpark) | Why it changed |
|---|---|---|---|
| Pattern | `UPDATE staging SET key = (SELECT TOP(1) ... correlated subquery)` | LEFT JOIN + `ROW_NUMBER() OVER (... ORDER BY valid_from DESC) = 1` | Correlated `TOP(1)` subquery doesn't exist in Spark SQL (SX-003) |
| Execution | Row-by-row correlated subquery UPDATE on the staging table | Vectorized join across all staging rows at once | Spark operates on DataFrames, not row-by-row updates |
| Sort order | `ORDER BY valid_from ASC` (earliest matching version) | `ORDER BY valid_from DESC` (most recent matching version), `rn = 1` | Both select the same row when exactly one version matches. The DESC + rn=1 pattern is the Spark idiom for "latest match" (SX-P003) |
| Type handling | Homogeneous — both sides are `datetime2` | Heterogeneous — `valid_from` is DATE (TY-P001 override), `last_modified_when` is TIMESTAMP | Requires explicit `CAST(valid_from AS TIMESTAMP)` to prevent implicit promotion errors |
| Join strategy | Correlated subquery (nested loop) | `BROADCAST` hint on dimension table (PE-006) | Dimension tables are small; broadcasting avoids expensive shuffle join |
| Fallback | `COALESCE(..., 0)` | `F.coalesce(F.col("dim.supplier_key"), F.lit(0))` | Same semantics, PySpark syntax |

### The column-level lineage table — 19 rows

The to-be column-level lineage is significantly more detailed than the as-is (19 rows vs. 9):

**New rows not in the as-is:**

| Target Column | Why it's new |
|---|---|
| `purchase_key` | `GENERATED ALWAYS AS IDENTITY` — auto-assigned on MERGE INSERT |
| `wwi_supplier_id` (on fact) | Retained on fact table for SK resolution lineage traceability |
| `wwi_stock_item_id` (on fact) | Same — retained for traceability |
| `last_modified_when` (on fact) | Retained as watermark high-water reference |
| `_extracted_at_utc` (on staging) | New audit column — `datetime.now(timezone.utc)` injected at extract time |
| `lineage_key` (on staging) | Propagated from `nb_extract_watermark` via taskValues |
| `cutoff_time` (on etl_cutoff) | Written by `set_etl_cutoff()` after successful MERGE |
| `data_load_completed` / `was_successful` (on lineage_run) | Written by `close_lineage_record()` |
| `dq_rejections.*` | RI check failures from QA-P003 |
| `delivery_location_wkt/lat/lon` (on supplier) | Geography CLR decomposition (TY-P004) |

### Why this section matters

Section 4 is where the to-be proves it has accounted for every legacy behavior. A reviewer can:

1. Compare the 11 as-is steps against the 22 to-be steps and verify that every legacy step has a target equivalent
2. Check that the 10 new steps add value (DQ, observability, bug fixes) without changing business semantics
3. Verify that the SCD-2 resolution preserves the exact boundary semantics (`>` exclusive, `<=` inclusive)
4. Confirm that every column-level transformation references the correct rule IDs

---

## Section 5 — Calculations

### What it contains

Five calculations (vs. 3 in the as-is) — the same 3 legacy calculations updated for the target, plus 2 new ones:

| Calculation | As-Is | To-Be | Status |
|---|---|---|---|
| 5.1 Date Key Derivation | `CAST(OrderDate AS date)` in SSIS | `CAST(po.OrderDate AS DATE)` in Spark SQL (nb_extract_purchase) | **Direct translation** — same logic, different syntax (SX-017) |
| 5.2 Ordered Outers / Ordered Quantity | Pass-throughs, no arithmetic | Pass-throughs + QA-P004 non-negativity assertion (informational) | **Enhanced** — same data flow, new quality check added |
| 5.3 SCD-2 Surrogate Key Resolution | Correlated `TOP(1)` subquery | `sk_resolver.py` temporal range JOIN + ROW_NUMBER | **Completely reimplemented** — same semantics, different pattern |
| 5.4 Lineage Key Injection | `NEXT VALUE FOR sequences.lineagekey` | `open_lineage_record()` + IDENTITY + taskValues | **Completely reimplemented** — new mechanism |
| 5.5 Consolidated Python UDFs | N/A (inline duplicated logic) | `src/common/udfs.py` with NULL guards | **New** — consolidates scattered patterns (CX-P003) |

### Calculation 5.3 — SCD-2 resolution (the critical reimplementation)

The to-be provides the **complete Python implementation** with annotations explaining every design decision:

| Design decision | Choice made | Rule | Why |
|---|---|---|---|
| Join strategy | LEFT JOIN (not INNER) | SX-003 | Unmatched staging rows must receive key=0, not be dropped |
| Window ordering | `ORDER BY valid_from DESC` | SX-P003 | Most recent matching version wins (equivalent to as-is `TOP(1) ORDER BY ASC` when exactly one version matches) |
| Type cast | `F.col("dim.valid_from").cast("timestamp")` | TY-P001 | `valid_from` is DATE (product override); `last_modified_when` is TIMESTAMP; explicit cast prevents implicit promotion errors |
| Broadcast hint | `F.broadcast(supplier_dim_df)` | PE-006 | Dimension tables are small enough for in-memory broadcast — avoids shuffle |
| Fallback | `F.coalesce(F.col("dim.supplier_key"), F.lit(0))` | SX-003 | Preserves as-is fallback-to-0 behavior for unresolved rows |

### Calculation 5.4 — Lineage key injection (new mechanism)

The to-be documents the complete taskValues propagation chain:

```
nb_extract_watermark:
  1. open_lineage_record(spark, etl_run_id, pipeline_name) → returns lineage_key (IDENTITY)
  2. dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_key)

nb_extract_purchase / migrate_staged_purchase_data:
  3. lineage_key = dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")
```

This is entirely new — SSIS used a `@LineageKey` variable passed between dataflow steps. Databricks Workflows use `taskValues` to pass data between notebook tasks. The to-be specifies the exact `taskKey` and `key` names so there's no ambiguity during implementation.

### Calculation 5.5 — Consolidated UDFs (new)

The to-be documents the UDF consolidation pattern:

- Identify inline scalar expressions appearing in 2+ stored procedures
- Implement each as a `@udf`-decorated function with NULL guard as the first statement
- Register with `spark.udf.register()` for Spark SQL usage
- Replace all inline occurrences with UDF calls
- Add unit tests covering: `None` input, empty string, boundary values, valid input

### Why this section matters

Section 5 provides the **algorithmic specification** for every computation. For the SCD-2 resolution, the actual Python code is included — not pseudocode, not a description, but the implementation that `sk_resolver.py` will contain. This means:

- SmartBuilder has a code template to generate from
- Reviewers can verify the logic against the as-is SQL
- Developers don't need to invent the implementation — it's specified

---

## Section 6 — Sources

### What it contains

**Section 6.1 — Input Source Tables (Target Platform):** 6 target-platform tables documented with their roles, key fields, and descriptions. These are the tables the Purchase pipeline **reads** at runtime.

**Lineage Traceability sub-table:** Maps every target table back to its SQL Server source object with the transformation rules applied.

**Section 6.2 — Output Tables (Target Platform):** 4 target-platform tables documented — the tables the Purchase pipeline **writes** at runtime.

### Input sources — what the target pipeline reads

| Target Table | Role | Key difference from as-is |
|---|---|---|
| `bronze.purchase_staging` | Primary source (populated by nb_extract_purchase) | OVERWRITE mode; audit columns added |
| `bronze.etl_cutoff` | Watermark control | Renamed from `integration.etl cutoff` (space removed) |
| `bronze.lineage_run` | Lineage context | New table combining `integration.lineage` + `sequences.lineagekey` |
| `silver_dim.supplier` | SCD-2 lookup | Geography CLR decomposed; SCD-2 validity → DATE; externally owned |
| `silver_dim.stock_item` | SCD-2 lookup | Space removed from name; MONEY → DECIMAL; Photo → BINARY; externally owned |
| `silver_dim.date` | Date dimension FK reference | Read-only; Purchase doesn't own its load (OB-011) |

### Output tables — what the target pipeline writes

| Target Table | Key difference from as-is |
|---|---|
| `silver_fact.fact_purchase` | CLUSTER BY; loaded via MERGE INTO (not DELETE+INSERT); lineage_key stamped per row |
| `bronze.dq_rejections` | **New** — RI violations written here by QA-P003 |
| `bronze.lineage_run` | Updated by `close_lineage_record()` at run end |
| `bronze.etl_cutoff` | Updated by `set_etl_cutoff()` after successful run |

### The lineage traceability table

This sub-table creates the full traceability chain from target → source → rules:

| Target Table | Source Object | Key rules applied |
|---|---|---|
| `bronze.purchase_staging` | `integration.purchase_staging` | NM-002 (space-bearing columns renamed) |
| `bronze.etl_cutoff` | `integration.etl cutoff` | NM-002 (space in name resolved); TY-022 (DATETIMEOFFSET → TIMESTAMP) |
| `bronze.lineage_run` | `integration.lineage` + `sequences.lineagekey` | LN-002 (SEQUENCE retired); OB-006 (IDENTITY replacement) |
| `silver_dim.supplier` | `dimension.supplier` | TY-P001 (validity → DATE); TY-P002 (5-col SCD-2 block); TY-P004 (geography CLR decomposed) |
| `silver_dim.stock_item` | `dimension.stock item` | NM-002 (space removed); TY-014 (VARBINARY → BINARY); TY-P003 (MONEY → DECIMAL) |
| `silver_dim.date` | `dimension.date` | OB-011 (read-only reference, not owned by Purchase) |

### The transformation summary

The final transformation summary block lists **every rule applied** across Section 6, including:
- PE-P001 (fallback partitioning for pre-DBR 13.3 runtimes)
- CX-P003 (UDF consolidation)
- CX-P006 (DDL header block standard)
- OB-P003 (`_current` views as regular VIEW; Gold analytics views as MATERIALIZED VIEW)

### Why this section matters

Section 6 closes the traceability loop. A reviewer can start from any target table, trace it back to its source object, and verify that every transformation rule in between was applied correctly. The lineage traceability table is essentially the **audit evidence** that the migration was executed according to the rules.

---

## The Transformation Summary Comment Blocks

Every section in the to-be ends with a `<!-- TRANSFORMATION SUMMARY -->` HTML comment block listing every rule ID applied in that section. These blocks are not visible in rendered Markdown but are critical for automated verification.

Example from Section 1:
```
<!-- TRANSFORMATION SUMMARY — rules applied to produce this section
Platform / Layer:
  PL-001  SQL Server 2014 → Databricks Delta Lake
  PL-002  Schema mapping: fact → silver_fact, dimension → silver_dim, integration → bronze
  PL-005  SSIS → Databricks Workflow
  ...
Naming:
  NM-001  All names → lowercase_snake_case
  NM-002  Space-bearing names resolved
  ...
-->
```

**Why they exist:** A future automated tool can parse these blocks to verify rule coverage — ensuring that every rule in the project and product rule sets was applied somewhere in the to-be. If a rule is missing from all transformation summaries, it may have been forgotten.

---

## How This Spec Is Used Downstream

| Downstream spec | What it takes from the to-be |
|---|---|
| **Development plan — product-definition.yaml** | Table schemas (§3 ER diagram), orchestration config (§1), DQ assertions (§1 metadata table), input/output ports (§6) |
| **Development plan — requirements.md** | Functional requirements derived from to-be behavior (e.g., FR-007 "Fact table upsert via MERGE INTO" comes from §4.4 step 15) |
| **Development plan — design.md** | Entity attributes (§3), Python module signatures (§5), Workflow task graph (§4.2 diagram) |
| **Development plan — tasks.md** | Each task implements a specific to-be component (e.g., TASK-011 "Write sk_resolver.py" implements §5.3) |
| **SmartBuilder `/smartbuilder_generate-db`** | DDL from §3 ER diagram column definitions |
| **SmartBuilder `/smartbuilder_generate-etl`** | ETL logic from §4.4 step-by-step table and §5 calculation code |
| **Runbook** | Failure recovery procedures derived from §4.4 pipeline steps (e.g., "what to do when step 15 MERGE fails") |
| **Catalog** | Product description, output datasets, orchestration, DQ, consumers, SLA, governance — all populated from to-be sections |

---

## File Reference

| File | Location |
|---|---|
| `to-be.md` | `products/Purchase/current/specifications/to-be.md` |

This is a single markdown file containing all 6 sections. It is typically the largest spec in the TCP flow — 800-900 lines — because it includes actual Python code, full ER diagrams, 22-step transformation tables, and detailed transformation summaries with rule annotations.
