# Product Transformation Rules — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Inherits from:** Inventory_Stock_Project project rules v1.0 (90 rules, 7 dimensions)
**Product customizations:** 26 (1 override, 13 extensions, 0 deactivations, 12 new rules)
**Active dimensions:** 9 (7 inherited + 2 product-only: QA, CX)

---

## What This Spec Is

The product transformation rules are **Purchase-specific customizations** layered on top of the 90 project-level rules. They handle situations where the project rules are too generic, too broad, or don't cover something the Purchase product needs.

The spec uses four mechanisms:

| Mechanism | What it does | Count |
|---|---|---|
| **Override** | Replaces a project rule's behavior for this product | 1 |
| **Extension** | Adds product-specific detail to a project rule without replacing it | 13 |
| **Deactivation** | Turns off a project rule that doesn't apply to this product | 0 |
| **New rule** | Adds a rule in a dimension that has no project-level equivalent | 12 |

The result is a product-level rule set of **116 effective rules** (90 inherited + 26 customizations) across 9 dimensions.

---

## Why This Spec Exists

### The problem with one-size-fits-all project rules

Project rules are deliberately generic — they apply to every product in the project. But products have specific needs:

- **Project rule TY-012** says "map DATETIME2 to TIMESTAMP_NTZ." But Purchase's SCD-2 dimensions use date-granularity validity periods — `TIMESTAMP_NTZ` introduces spurious sub-second comparison issues. Purchase needs `DATE` instead.
- **Project rule PE-003** says "run OPTIMIZE after every nightly batch." But Purchase has variable nightly volumes — some nights only a handful of orders change. Running OPTIMIZE on 5 rows wastes compute.
- **Project rules have no QA dimension at all.** Purchase needs 5 specific data quality assertions with blocking/informational classification.
- **Project rules don't specify codebase layout.** Purchase needs a standard directory structure so code generators produce files in the right places.

Product rules solve all of these without modifying the project rules that other products (like Inventory_Movement) will inherit unchanged.

### The inheritance model

```
Project rules (90 rules, 7 dimensions)
    ├── Purchase product rules (26 customizations, 2 new dimensions)
    │     = 116 effective rules across 9 dimensions
    └── Inventory_Movement product rules (future — will inherit the same 90 project rules)
```

This model means:
- Changing a project rule automatically affects all products
- Changing a product rule only affects that product
- A product can override a project rule without breaking other products
- A product can add entirely new dimensions (QA, CX) that don't exist at project level

---

## The Four YAML Files

The product rules are stored in four structured YAML files plus per-dimension YAML files and a summary markdown:

| File | Purpose | Contents |
|---|---|---|
| `override.yaml` | Rules that replace project rule behavior | 1 override (TY-P001) |
| `extensions.yaml` | Rules that add detail to existing project rules | 13 extensions |
| `new-rules.yaml` | Rules in dimensions with no project-level equivalent | 12 new rules (1 SX, 5 QA, 6 CX) |
| `deactivations.yaml` | Rules turned off for this product | Empty — no deactivations |
| `PL-platform.yaml` through `LN-lineage.yaml` | Per-dimension merged rule sets (inherited + customized) | 7 inherited dimension files |
| `QA-quality.yaml`, `CX-custom.yaml` | Product-only dimension files | 2 new dimension files |
| `product-transformation-rules.md` | Human-readable summary with rule index | All 116 rules listed |

---

## The Override — TY-P001

### What it overrides

**Project rule TY-012:** "Map DATETIME2(n) to TIMESTAMP_NTZ to preserve wall-clock semantics."

### What TY-P001 says instead

Map SCD-2 validity columns (`valid_from`, `valid_to`) from DATETIME2 to **DATE** (not TIMESTAMP_NTZ) on Purchase-scope dimension tables.

### Why the override is needed

The project rule is correct for general DATETIME2 columns (timestamps in lineage tables, cutoff times, last-modified-when columns). But Purchase's SCD-2 dimensions treat validity boundaries as **calendar dates**, not sub-day timestamps. Storing them as TIMESTAMP_NTZ introduces problems:

| Problem | What goes wrong |
|---|---|
| Spurious sub-second comparison issues | If `valid_from` is `2024-03-15T00:00:00.000` and `last_modified_when` is `2024-03-15T00:00:00.001`, the `>` comparison evaluates differently than if both were `DATE '2024-03-15'` |
| Misleading precision | The SCD-2 validity window has day granularity — storing it with nanosecond precision implies a precision that doesn't exist |
| Temporal range predicate complexity | The sk_resolver.py join must cast DATE to TIMESTAMP for comparison with `last_modified_when` — this cast is explicit and auditable, vs. implicit TIMESTAMP_NTZ comparisons that hide the granularity mismatch |

### Scope limitation

The override applies **only** to SCD-2 validity columns (`valid_from`, `valid_to`) on Purchase-scope dimension tables (`supplier`, `stock_item`). All other DATETIME2 columns — `data_load_started`, `cutoff_time`, `last_modified_when`, `source_system_cutoff_time` — continue to map to TIMESTAMP_NTZ per the unchanged project rule TY-012.

This scope limitation is critical. Without it, the override would affect lineage timestamps and watermark columns, which genuinely need sub-second precision.

---

## The 13 Extensions

Extensions add product-specific detail to existing project rules without replacing them. Each extension has an `extension_id` (e.g., TY-P002) that becomes a new rule in the product rule set.

### TY Extensions (3 rules)

**TY-P002 — 5-column SCD-2 control block** (extends TY-012)

| What it adds | Why |
|---|---|
| Defines the complete SCD-2 control column pattern: `valid_from DATE`, `valid_to DATE`, `row_effective_date DATE`, `row_expiry_date DATE DEFAULT '9999-12-31'`, `is_current_row BOOLEAN DEFAULT TRUE` | Project rule TY-012 maps types but doesn't specify the full SCD-2 column set. Purchase needs exactly these 5 columns on every SCD-2 dimension, in this exact order, with these exact defaults. Code generators must emit this block as a unit. |

**TY-P003 — MONEY/SMALLMONEY mapping** (extends TY-005)

| What it adds | Why |
|---|---|
| `MONEY → DECIMAL(18,2)`, `SMALLMONEY → DECIMAL(10,2)` | Project rule TY-005 covers `DECIMAL/NUMERIC` but doesn't address SQL Server's currency types. Purchase dimension tables (`stock_item`) have `unit_price` and `recommended_retail_price` columns typed as MONEY. Without this rule, these columns have no defined mapping and code generators would fail or guess. |

**TY-P004 — Geography CLR decomposition** (extends TY-009)

| What it adds | Why |
|---|---|
| `geography CLR` → 3 columns: `<col>_wkt STRING` (WKT), `<col>_lat DOUBLE`, `<col>_lon DOUBLE` | Project rules cover standard SQL types but not CLR user-defined types. The `supplier` dimension has a `DeliveryLocation` geography column. Spark has no geography type — it must be decomposed into queryable primitives. The extraction uses `.ToString()` for WKT, `.Lat` for latitude, `.Long` for longitude. |

### OB Extensions (4 rules)

**OB-P001 — Key=0 sentinel bootstrap** (extends OB-001)

| What it adds | Why |
|---|---|
| Every SCD-2 dimension must have a bootstrap notebook that MERGE-upserts a key=0 "Unknown" sentinel row | The SCD-2 resolution uses `COALESCE(..., 0)` for unresolved rows. If key=0 doesn't exist in the dimension, FK checks fail and reports show broken dimension references. The bootstrap must be INIT_ONLY (not in the nightly Workflow), idempotent (MERGE not INSERT), and assert key=0 exists after execution. |

**OB-P002 — Staging audit columns** (extends OB-003)

| What it adds | Why |
|---|---|
| `lineage_key BIGINT NOT NULL` and `_extracted_at_utc TIMESTAMP NOT NULL` added to `purchase_staging` | `lineage_key` propagates the ETL run ID to every staging row (LN-006). `_extracted_at_utc` records the exact extraction wall-clock time, enabling freshness auditing independent of the watermark. Neither existed in the legacy staging table. |

**OB-P003 — View materialization classification** (extends OB-008)

| What it adds | Why |
|---|---|
| Aggregating views → MATERIALIZED VIEW; thin wrappers → regular VIEW | `_current` views on SCD-2 dims are thin filters (`WHERE is_current_row = TRUE`) — materializing them wastes compute. Gold analytics views that aggregate should be materialized for performance. The project rule doesn't distinguish between view types. |

**OB-P004 — Named shared helper modules** (extends OB-005)

| What it adds | Why |
|---|---|
| `scd2_merge.py`, `sk_resolver.py`, `fact_merge.py` promoted to explicit migration targets under `src/common/` | The project rule says "replace stored procedures with notebooks" but doesn't prescribe the modular decomposition. Purchase explicitly designates 3 shared helpers as first-class artifacts with defined interfaces, unit tests, and module-level docstrings. This ensures they're tracked, tested, and reusable. |

### SX Extensions (3 rules)

**SX-P001 — taskValues lineage injection** (extends SX-004)

| What it adds | Why |
|---|---|
| Specifies `dbutils.jobs.taskValues.set/get` as the exact mechanism for passing `lineage_key` between Workflow tasks | Project rule SX-004 says "replace SEQUENCE with Python utility" but doesn't specify the inter-task communication channel. Purchase's 3-task Workflow needs `taskValues` — not a shared file, not a database read, not a widget parameter. The exact `taskKey` and `key` names are specified so code generators produce consistent references. |

**SX-P002 — CONVERT style 112 date arithmetic** (extends SX-017)

| What it adds | Why |
|---|---|
| `CONVERT(CHAR(8), GETDATE()-N, 112)` → `DATE_FORMAT(DATE_SUB(current_date(), N), 'yyyyMMdd')` | Project rule SX-017 covers general CAST/CONVERT but not the specific style-112-with-date-arithmetic pattern used in Purchase source code for generating YYYYMMDD date strings. Without this extension, a developer would have to figure out the Spark equivalent from scratch. |

**SX-P003 — sk_resolver.py pre-join pattern** (extends SX-003)

| What it adds | Why |
|---|---|
| Specifies `sk_resolver.py` as a pre-join step before the MERGE, replacing the inline `UPDATE staging SET key = (SELECT TOP(1)...)` pattern | Project rule SX-003 says "convert TOP(1) to ROW_NUMBER" but implies the resolution happens inline in a SQL UPDATE. Purchase moves it to a separate Python module that is called before the MERGE, producing a resolved staging DataFrame. This separation makes the resolution testable, debuggable, and reusable. The extension includes the full calling pattern with function signature. |

### PE Extensions (2 rules)

**PE-P001 — Fallback partitioning for pre-DBR 13.3** (extends PE-002)

| What it adds | Why |
|---|---|
| `PARTITIONED BY (date_key) ZORDER BY (supplier_key, stock_item_key)` as alternative to `CLUSTER BY` | Liquid Clustering requires DBR 13.3+. If the runtime is older, this fallback provides equivalent data layout optimization. The strategies are **mutually exclusive** — a table uses one or the other, never both. The default is CLUSTER BY; fallback is only used when the runtime constraint is confirmed. |

**PE-P002 — Conditional OPTIMIZE threshold** (extends PE-003)

| What it adds | Why |
|---|---|
| OPTIMIZE only when `rows_merged > 10,000`; threshold externalized to `environment.yaml` | Project rule PE-003 says "OPTIMIZE after every batch." Purchase has variable nightly volumes — some nights only 5 orders change. Unconditional OPTIMIZE on 5 rows wastes cluster compute. The threshold (10,000) is externalized so it can be tuned per environment without code changes. |

### LN Extension (1 rule)

**LN-P001 — taskValues as lineage propagation mechanism** (extends LN-003)

| What it adds | Why |
|---|---|
| `nb_extract_watermark` opens the lineage record and publishes `lineage_key` via `taskValues.set`; all downstream tasks consume via `taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")` | Project rule LN-003 says "replace getlineagekey with Python open_lineage_record()." But it doesn't specify how the lineage key crosses task boundaries in a multi-task Workflow. Purchase uses taskValues — the native Databricks mechanism for inter-task data passing. Only `nb_extract_watermark` calls `open_lineage_record()`; no other task opens its own lineage record. |

---

## The 12 New Rules

New rules exist in dimensions that have no project-level equivalent. Purchase introduces 2 entirely new dimensions: **QA (Quality)** and **CX (Custom)**.

### SX-P004 — Lineage close UPDATE (1 new syntax rule)

| What it specifies | Why it's needed |
|---|---|
| Converts the inline `UPDATE Integration.Lineage SET [Data Load Completed] = SYSDATETIME() WHERE [Lineage Key] = @LineageKey` to a `spark.sql(f"UPDATE bronze.lineage_run SET ... WHERE lineage_key = {lineage_key}")` call | No project SX rule covers this specific inline UPDATE pattern. The to-be design needs an explicit specification for the lineage-close statement, including the `rows_merged` count injection and the requirement that the `was_successful = false` variant appears in the exception handler. |

### QA Dimension — 5 New Rules

The QA dimension is **entirely new** — the legacy system had no structured data quality checks. Problems were invisible until a business user noticed incorrect numbers in a report. Purchase introduces 5 assertions:

**QA-P001 — Row count reconciliation (BLOCKING)**

| What it checks | Behavior on failure |
|---|---|
| `staging_count == rows_merged` after each MERGE | **Raises RuntimeError** — marks the Workflow task as FAILED, prevents watermark advance, prevents lineage record from closing as successful |

This is the only **blocking** assertion. If the staging table has 1,000 rows but the MERGE only touched 950, something silently dropped 50 rows. This must never pass silently.

**QA-P002 — Orphaned surrogate key detection (INFORMATIONAL)**

| What it checks | Behavior on failure |
|---|---|
| LEFT ANTI JOIN `fact_purchase` against `supplier` and `stock_item` dimensions (excluding key=0) to find non-zero surrogate keys that don't exist in any dimension version | **Logs WARNING** — does not block the pipeline |

Orphaned keys (non-zero keys with no matching dimension row) indicate either a dimension load timing issue or a DQ defect in the dimension data. Key=0 rows are excluded because they're the expected fallback for unresolved lookups.

**QA-P003 — Referential integrity checks (INFORMATIONAL, writes to dq_rejections)**

| What it checks | Behavior on failure |
|---|---|
| LEFT ANTI JOIN per FK column (`supplier_key`, `stock_item_key`, `date_key`) against their respective dimension tables | **Writes violation rows to `bronze.dq_rejections`** with `lineage_key`, `rule_id`, column name, and offending value. Logs at ERROR level. Does not block. |

This is the most operationally important QA rule. The `dq_rejections` table provides a queryable, persistent record of every RI violation, linked to the specific ETL run that produced it. Operations teams can query this table to investigate data quality issues without reading notebook logs.

**QA-P004 — Business rule assertions (INFORMATIONAL)**

| What it checks | Behavior on failure |
|---|---|
| Three business invariants: (1) `ordered_outers >= 0` and `ordered_quantity >= 0`, (2) `date_key` within expected batch window, (3) `package` is not null or empty | **Logs WARNING** — does not block |

These are domain-specific rules that the legacy system didn't enforce. Negative quantities, out-of-window dates, and null packages are all symptoms of upstream data problems. Logging them creates visibility; blocking on them would cause unnecessary pipeline failures for problems that aren't the Purchase ETL's fault.

**QA-P005 — Centralized DQ rejection store**

| What it specifies | Why |
|---|---|
| The DDL for `bronze.dq_rejections` (10 columns: `rejection_id` IDENTITY, `lineage_key`, `rule_id`, `source_table`, `pk_column`, `pk_value`, `violation_column`, `violation_value`, `rejection_reason`, `detected_at`) and the requirement that all QA checks write to it | Without a centralized store, DQ violations are scattered across notebook logs. The rejection table makes them queryable, filterable by `lineage_key` or `rule_id`, and available for dashboards and SLA reporting. |

### CX Dimension — 6 New Rules

The CX (Custom) dimension captures **engineering standards** specific to the Purchase product — codebase layout, notebook conventions, configuration patterns, and DDL formatting.

**CX-P001 — Date filter externalization**

| What it specifies | Why |
|---|---|
| All hard-coded date literals in ETL code must be moved to `config/environment.yaml` under `purchase.etl` (e.g., `initial_load_date`, `batch_lookback_days`, `fact_optimize_row_threshold`) | Hard-coded dates are brittle — they break when you need to re-run with a different window, or when you deploy to a different environment (dev vs. prod). Externalization enables environment-specific overrides and re-runs without code changes. |

**CX-P002 — Business factor externalization with NULL guards**

| What it specifies | Why |
|---|---|
| All hard-coded business factors (multipliers, thresholds, rates) must be externalized to `config/environment.yaml` under `purchase.business_rules`, with NULL guards (`if val is None: raise ValueError`) and bound assertions (`assert lower <= val <= upper`) | A missing config value produces a silent `None` that propagates through calculations. The NULL guard catches this immediately. The bound assertion catches unreasonable values (e.g., a threshold of -1 or 999999) before they corrupt downstream data. |

**CX-P003 — UDF consolidation**

| What it specifies | Why |
|---|---|
| Duplicate scalar function patterns across Purchase stored procedures must be consolidated into `src/common/udfs.py` with NULL guards, Spark SQL registration, and unit tests | Copy-pasted scalar functions diverge over time. One copy gets a bug fix; the others don't. Consolidation ensures one implementation, one set of tests, one place to fix bugs. The NULL guard (`if val is None: return None`) is mandatory on every UDF. |

**CX-P004 — Codebase layout**

| What it specifies | Why |
|---|---|
| The canonical directory structure: `config/`, `docs/`, `src/common/`, `src/db/ddl/`, `src/db/grants/`, `src/etl/`, `src/init/`, `tests/common/`, `tests/etl/` | Without a standard layout, code generators put files in random locations, import paths break, CI pipelines can't find artifacts, and documentation generators miss files. This rule is the contract between code generators and all downstream tooling. |

**CX-P005 — ETL notebook skeleton**

| What it specifies | Why |
|---|---|
| Every ETL notebook must follow a 6-section skeleton: (1) imports, (2) lineage_key via taskValues, (3) zero-rows guard, (4) main ETL in try/except, (5) conditional OPTIMIZE, (6) close lineage | Without a standard skeleton: some notebooks forget the zero-rows guard and process empty batches (wasted compute); some forget the exception handler and leave lineage records open on failure; some forget conditional OPTIMIZE and compact 5-row batches. The skeleton ensures consistency. |

**CX-P006 — DDL file header block**

| What it specifies | Why |
|---|---|
| Every `.sql` file in `src/db/ddl/` must begin with a header block containing PROJECT, PRODUCT, FILE, PURPOSE, SOURCE, TARGET, RULES, and GENERATED fields. The RULES field must list every rule ID that influenced the file. | The header is the **audit trail** for generated code. A reviewer can look at any DDL file and immediately see which source object it replaces, which target object it creates, and which transformation rules were applied. The RULES field is especially important — it closes the traceability loop from project rule → product rule → generated code. |

---

## What's NOT Customized

Two project dimensions have **zero customizations** at the product level:

| Dimension | Rules | Why no changes |
|---|---|---|
| **PL — Platform** (10 rules) | Fully inherited | Platform decisions (SQL Server → Databricks, SSIS → Workflows, SEQUENCE → IDENTITY) are project-wide and apply equally to Purchase |
| **NM — Naming** (9 rules) | Fully inherited | Naming conventions (snake_case, space removal, schema mapping) are project-wide and apply equally to Purchase |

This is significant — it means the naming and platform rules are stable across all products. If Inventory_Movement is built next, it inherits the same PL and NM rules without modification.

---

## How Product Rules Interact with Project Rules

The inheritance model has specific precedence rules:

| Scenario | What happens |
|---|---|
| Project rule exists, no product customization | Project rule applies as-is |
| Project rule exists, product **extends** it | Both apply — extension adds detail but doesn't change the base rule |
| Project rule exists, product **overrides** it | Product rule replaces the project rule for this product only (other products still use the project rule) |
| Project rule exists, product **deactivates** it | Project rule is turned off for this product (Purchase has 0 deactivations) |
| No project rule exists, product adds **new rule** | New rule applies only to this product (QA and CX dimensions) |

---

## How This Spec Is Used Downstream

| Downstream spec | What it takes from product rules |
|---|---|
| **To-be design** | Every transformation summary references product rule IDs (e.g., "SCD-2 validity → DATE per TY-P001"; "conditional OPTIMIZE per PE-P002"). The to-be cannot be written without product rules. |
| **Development plan — requirements** | Product rules generate functional requirements (e.g., QA-P001 → NFR-003 "row count reconciliation blocking on mismatch") |
| **Development plan — design** | Product rules define interfaces (e.g., OB-P004 → sk_resolver.py function signature; CX-P004 → directory structure) |
| **Development plan — tasks** | Product rules generate tasks (e.g., QA-P005 → TASK-004 "Create dq_rejections table"; CX-P005 → structural validation of every notebook) |
| **SmartBuilder code generation** | DDL generators read TY-P001/TY-P002 for SCD-2 column types; ETL generators read SX-P001/SX-P003 for lineage injection and SK resolution patterns; all generators read CX-P006 for header block format |
| **Generated DDL files** | The RULES field in every DDL header (CX-P006) lists the product rule IDs that influenced that file |

---

## File Reference

| File | Location | Purpose |
|---|---|---|
| `override.yaml` | `products/Purchase/current/specifications/product-transformation-rules/` | 1 override (TY-P001) |
| `extensions.yaml` | same | 13 extensions with full rationale and behavior specs |
| `new-rules.yaml` | same | 12 new rules (SX-P004, QA-P001–P005, CX-P001–P006) |
| `deactivations.yaml` | same | Empty — no deactivations |
| `PL-platform.yaml` | same | 10 rules (fully inherited) |
| `NM-naming.yaml` | same | 9 rules (fully inherited) |
| `TY-types.yaml` | same | 30 rules (26 inherited + 4 product) |
| `OB-objects.yaml` | same | 15 rules (11 inherited + 4 product) |
| `SX-syntax.yaml` | same | 21 rules (17 inherited + 4 product) |
| `PE-performance.yaml` | same | 11 rules (9 inherited + 2 product) |
| `LN-lineage.yaml` | same | 9 rules (8 inherited + 1 product) |
| `QA-quality.yaml` | same | 5 rules (product-only dimension) |
| `CX-custom.yaml` | same | 6 rules (product-only dimension) |
| `product-transformation-rules.md` | same | Human-readable summary with full rule index |
