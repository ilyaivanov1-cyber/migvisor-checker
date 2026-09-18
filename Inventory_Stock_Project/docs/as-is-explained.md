# As-Is Analysis — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Source:** Microsoft SQL Server 2014 (`wideworldimportersdw`)
**Fact table:** `fact.purchase` (11 columns, rowstore, IDENTITY PK)
**ETL engine:** SSIS — `pipeline_dailyetlmain` (daily batch), Purchase container

---

## What This Spec Is

The as-is analysis is a **deep forensic examination** of the legacy system *as it exists today* — including its bugs, implicit assumptions, undocumented dependencies, and subtle behavioral details. It is produced **after** the product scope is defined and **before** the product transformation rules and to-be design are written.

It consists of 6 sections, each examining the legacy system from a different angle:

1. **Definition** — what the product is and what business purpose it serves
2. **Consumers** — who reads the data and what questions they answer
3. **Model** — the physical data model (ER diagram, table schemas, relationships)
4. **Lineage** — end-to-end data flow from OLTP source through ETL to BI consumption
5. **Calculations** — every derivation, transformation, and computation in the ETL
6. **Sources** — complete inventory of input and output tables with key fields

Think of it as the **autopsy report** of the legacy system. You can't design a replacement without understanding exactly what the current system does — including the parts nobody documented, the bugs nobody fixed, and the dependencies nobody remembers.

---

## Why This Spec Exists

### The problem with "just rewrite it"

Without a thorough as-is analysis, the typical migration failure mode is:

1. A developer reads the stored procedure, translates the SQL syntax, and declares it done.
2. Three weeks later, someone notices the SCD-2 surrogate key resolution produces different results because the temporal range comparison has different boundary semantics (`>` vs. `>=`) in the new implementation.
3. Two months later, the team discovers the fact load depends on dimensions being loaded first — a dependency that was encoded in SSIS task ordering but never documented anywhere.
4. At go-live, the Power BI reports break because they were connected via direct SQL Server connections that no longer exist.

The as-is analysis prevents all of these by documenting:
- The **exact** SQL code for every transformation (not paraphrased, not summarized — the actual T-SQL)
- The **exact** boundary semantics of every comparison (exclusive lower bound, inclusive upper bound on SCD-2 ranges)
- Every **runtime dependency** (dimensions must load before facts)
- Every **downstream consumer** with their exact consumption method

### The as-is enables the to-be

The to-be design is written as a **diff against the as-is**. Every section in the to-be mirrors the corresponding as-is section and documents what changed and why. Without the as-is as a baseline, the to-be would have to describe the entire system from scratch, making it impossible to verify that nothing was lost in translation.

---

## Section 1 — Definition

### What it contains

**Section 1.1 — Narrative definition:** A comprehensive description of what the Purchase data product is, what business purpose it serves, and what its key components are. Written in prose, not tables — designed to give a reader who has never seen the system a complete understanding in one read.

**Section 1.2 — Metadata table:** A structured 15-field table covering domain, business process, entities, metrics, DQ rules, storage, consumers, and data sources.

### Key facts captured

**The product's business purpose:**
- Provides reliable, queryable procurement data for downstream BI reporting
- Answers questions like: which suppliers are fulfilling orders in full? How do ordered quantities compare against received quantities per stock item? Which purchase orders remain open?

**The 5 key components:**

| Component | What it is | Why it matters |
|---|---|---|
| `fact.purchase` | Core fact table — 11 columns, one row per purchase order line | The central analytical artifact. Everything else exists to feed this table. |
| Conformed dimensions | `dimension.supplier` (SCD-2), `dimension.stock item` (SCD-2), `dimension.date` (static) | **Read dependencies** — Purchase doesn't own their loads but can't run without them |
| Integration staging layer | `purchase_staging`, `etl cutoff`, `lineage`, `migratestagedpurchasedata` procedure | The ETL engine — staging, watermarking, lineage tracking, and the core MERGE procedure |
| SSIS pipeline | Purchase container within `pipeline_dailyetlmain` | The orchestration layer — runs nightly, contains the confirmed staging-truncation bug |
| Shared infrastructure | `sequences.lineagekey`, `getlastetlcutofftime`, `getlineagekey` | Supporting objects — sequence for lineage keys, stored procedures for watermark and key generation |

**The metadata table captures structured details:**

| # | Field | What it captures | Why it's important |
|---|---|---|---|
| 1 | Domain Name | Procurement / Purchasing | Classifies the product within the business domain taxonomy |
| 3 | Process Type | Transactional (incremental daily batch load; append and upsert via MERGE) | Determines the ETL strategy — incremental, not full reload |
| 5 | Business Metric | Ordered Outers, Ordered Quantity, Received Outers, Order Finalization Rate | These are the measures that appear in BI reports — they must be preserved exactly |
| 10 | Filters Applied | Incremental load filtered by ETL high-watermark from `integration.etl cutoff` | The watermark mechanism must be replicated in the target |
| 12 | Business DQ Rules | Ordered Quantity > 0; Received Outers <= Ordered Outers for finalized orders | These rules don't exist as code in the legacy system — they're implicit business expectations that the target should enforce explicitly |
| 13 | Technical DQ Rules | Stale staging rows from prior runs must not be re-processed — **legacy SSIS bug violates this rule** | The as-is documents that the current system *fails* its own DQ rules due to the bug |

### Why this section matters

The definition establishes the **contract** between the data product and its consumers. The measures (`ordered_outers`, `ordered_quantity`, `received_outers`) and their semantics (pass-throughs from source, not calculated in ETL) must be preserved exactly in the target. If the to-be design accidentally adds a transformation to one of these columns, a reviewer can catch it by comparing against this section.

The `[USER INPUT REQUIRED]` placeholders (data access restrictions, additional consumers, table size) flag decisions that require human input — the MCP can discover code structure but can't determine security policies or confirm undocumented consumers.

---

## Section 2 — Consumers

### What it contains

A table of every downstream consumer of the Purchase data product, with four columns: Consumer Name, Use Cases, Business Questions Answered, and Consumption Method.

### The three consumers

**Consumer 1: `wwidw purchase and sale per stockitem dynamic`**

| Aspect | Detail |
|---|---|
| What it is | Cross-domain procurement-vs-sales comparison report |
| Who uses it | Procurement and inventory analysts |
| What it reads | `fact.purchase` directly; cross-domain join with `fact.sale` (Sales_Orders product) on stock item |
| Business questions | Which stock items are ordered in volumes matching sales demand? How do receipt quantities compare to sales per stock item? |
| Consumption method | **Direct table read** — no intermediate view or procedure |
| Migration risk | **High** — cross-domain join with `fact.sale` means both Purchase and Sales_Orders must be cut over together |

**Consumer 2: `wwidw-ordered-by-supplier`**

| Aspect | Detail |
|---|---|
| What it is | Supplier performance and order fill rate report |
| Who uses it | Procurement teams |
| What it reads | `fact.purchase` and `dimension.supplier` directly |
| Business questions | Which suppliers are filling orders in full? What is the open vs. finalized order distribution per supplier? |
| Consumption method | **Direct table read** — joins on `Supplier Key` (SCD-2 surrogate key) |
| Migration risk | **Low** — self-contained within Purchase domain |

**Consumer 3: `integration.migratestagedpurchasedata` (internal)**

| Aspect | Detail |
|---|---|
| What it is | The ETL procedure itself — it reads the watermark to determine what to extract |
| What it reads | `integration.etl cutoff` (watermark table) |
| Consumption method | Indirect dependency — reads the watermark last written by itself |
| Migration risk | **None** — replaced entirely by Python notebooks |

### Why this section matters

The consumer analysis reveals two critical facts:

1. **Both Power BI reports use direct table reads** — no intermediate views or stored procedures. This means the reports contain hardcoded SQL Server table references (`fact.purchase`, `dimension.supplier`) that must be updated to Databricks references (`inventory_stock.silver_fact.fact_purchase`, `inventory_stock.silver_dim.supplier`). Every column name with spaces must be updated to snake_case.

2. **The cross-domain report creates a cutover constraint** — `wwidw_purchase_and_sale_per_stockitem_dynamic` joins Purchase and Sales data. You can't migrate Purchase to Databricks while Sales is still on SQL Server — the report would have to query two different platforms simultaneously. This forces a coordinated cutover with the Sales_Orders product.

---

## Section 3 — Model

### What it contains

**Section 3.1 — ER diagram:** A full Mermaid entity-relationship diagram showing every table in the Purchase product's scope with all columns, types, PKs, FKs, and relationships. Includes the source fact table, staging table, control tables (ETL cutoff, lineage), and all three dimensions.

**Section 3.2 — Textual description:** A layer-by-layer narrative describing each table group: Primary Source, Fact Table, Dimension/Dictionary, and Processing.

### Key details captured in the ER diagram

The diagram documents **every column and its type** for 8 tables:

| Table | Columns | Key details |
|---|---|---|
| `fact.purchase` | 11 | `PurchaseKey` BIGINT IDENTITY PK; surrogate FKs to all 3 dimensions + lineage |
| `integration.purchase_staging` | 14 | 3 extra columns vs. fact: `WWISupplierID`, `WWIStockItemID`, `LastModifiedWhen` — these are the natural keys and temporal probe used for SCD-2 resolution |
| `dimension.supplier` | 9 | SCD-2 with `ValidFrom`/`ValidTo` datetime2; `WWISupplierID` natural key |
| `dimension.stock item` | 19 | SCD-2; includes `Photo varbinary(max)` — binary image data that needs special type handling |
| `dimension.date` | 12 | Static calendar; no SCD-2; both `Date` (DATE PK) and `DateKey` (INT) columns exist |
| `integration.etl cutoff` | 2 | `TableName` PK + `CutoffTime` — simple watermark store |
| `integration.lineage` | 6 | `LineageKey` PK, start/end timestamps, success flag, cutoff time |

### The relationships diagram reveals the data flow

```
Source fact.purchase → (watermark extract) → Purchase_Staging
Purchase_Staging → (SCD-2 lookup) → Dimension.Supplier
Purchase_Staging → (SCD-2 lookup) → Dimension.Stock Item
Purchase_Staging → (MERGE upsert) → Fact.Purchase
Fact.Purchase → Dimension.Supplier (FK: SupplierKey)
Fact.Purchase → Dimension.Stock Item (FK: StockItemKey)
Fact.Purchase → Dimension.Date (FK: DateKey)
Fact.Purchase → Integration.Lineage (FK: LineageKey)
ETL Cutoff → (watermark read) → Purchase_Staging
```

### Why this section matters

The ER diagram is the **physical truth** of the source system. It reveals details that prose descriptions miss:

- **Staging has 14 columns but the fact has 11** — the 3 extra columns (`WWISupplierID`, `WWIStockItemID`, `LastModifiedWhen`) exist only for SCD-2 key resolution and are dropped after the MERGE. The target must preserve this pattern.
- **`dimension.stock item` has 19 columns including `Photo varbinary(max)`** — this binary column needs `VARBINARY → BINARY` type handling (TY-014), which wouldn't be obvious from a text description.
- **`dimension.date` has both `Date` (DATE) and `DateKey` (INT)** — the fact table uses `DateKey` as its FK. The target must decide which column to use as the join key.
- **Staging carries both resolved surrogate keys AND original natural keys** — `SupplierKey` (resolved) and `WWISupplierID` (natural) coexist in the same table. The resolution UPDATE writes the surrogate key; the natural key is used as the lookup input.

---

## Section 4 — Lineage

### What it contains

This is the **longest and most detailed section** of the as-is analysis — and for good reason. It documents the complete end-to-end data flow from OLTP source through ETL to BI consumption.

**Section 4.1 — Key Columns/Metrics:** 9 columns documented with their exact derivation logic (pass-through vs. derived, source table, transformation applied).

**Section 4.2 — Lineage Diagram:** A full Mermaid flow diagram with 6 subgraphs (OLTP, Extract, Staging, Key Resolution, Fact Load, BI Reports) showing every data transformation step, color-coded by layer.

**Section 4.3 — Column-Level Lineage Table:** Every target column mapped back to its source column, through its intermediate table, with the exact transformation logic.

**Section 4.4 — Step-by-Step Transformation Table:** An **11-step table** documenting every ETL step with the actual T-SQL code, business meaning, and layer classification.

**Section 4.5 — Known Downstream Dependencies:** 8 dependent objects documented with their relationship type and migration implications.

### The 11 ETL steps (the core of the as-is)

| Step | What happens | Why it's important for migration |
|---|---|---|
| **1. Watermark read** | `SELECT TOP(1) [Cutoff Time] FROM Integration.[ETL Cutoff] WHERE [Table Name] = 'fact.purchase'` → bounds the extract window | The watermark mechanism must be replicated exactly. Note: `TOP(1)` becomes `LIMIT 1` in Spark; `[Table Name]` (space in column name) must be renamed. |
| **2. Staging truncation** | **BUG** — `DELETE FROM Integration.Order_Staging` (wrong table!) — `Purchase_Staging` is **never truncated** | The most critical finding. Stale rows accumulate indefinitely. The target MUST fix this with OVERWRITE mode. |
| **3. Lineage registration** | `INSERT INTO Integration.Lineage` + `NEXT VALUE FOR Sequences.LineageKey` → generates run ID | SEQUENCE doesn't exist in Databricks. Must be replaced with IDENTITY column + Python utility function. |
| **4. Extract** | 5-table OLTP JOIN filtered by `LastEditedWhen` window; computes `DateKey = CAST(OrderDate AS date)` | The only derived column at extract time. All others are pass-throughs. The JOIN involves 5 tables — must be replicated as a JDBC query or Spark DataFrame join. |
| **5. Staging load** | SSIS OLE DB Destination bulk insert into `Purchase_Staging` | `SupplierKey` and `StockItemKey` are initially NULL — they get populated in steps 6-7. |
| **6. Supplier key resolution** | `UPDATE stg SET stg.[Supplier Key] = COALESCE((SELECT TOP(1) s.[Supplier Key] FROM Dimension.Supplier s WHERE s.[WWI Supplier ID] = stg.[WWI Supplier ID] AND stg.[Last Modified When] > s.[Valid From] AND stg.[Last Modified When] <= s.[Valid To] ORDER BY s.[Valid From]), 0)` | **The hardest step to migrate.** Correlated `TOP(1)` subquery doesn't exist in Spark SQL. Must become a temporal range JOIN + `ROW_NUMBER() OVER (...) = 1`. The boundary semantics (`>` exclusive, `<=` inclusive) must be preserved exactly. |
| **7. Stock item key resolution** | Same pattern as step 6, applied to `Dimension.[Stock Item]` | Identical logic, different dimension table. Same migration challenge. |
| **8. Fact delete** | `DELETE FROM Fact.Purchase WHERE [WWI Purchase Order ID] IN (SELECT [WWI Purchase Order ID] FROM Integration.Purchase_Staging)` | Order-level full-replacement pattern — any update to a purchase order causes ALL lines for that order to be deleted and re-inserted. The target's MERGE must replicate this idempotent behavior. |
| **9. Fact insert** | `INSERT INTO Fact.Purchase SELECT ..., @LineageKey FROM Integration.Purchase_Staging` | The `@LineageKey` constant binds all rows in this run together. The target must inject `lineage_key` the same way. |
| **10. Lineage completion** | `UPDATE Integration.Lineage SET [Data Load Completed] = SYSDATETIME(), [Was Successful] = 1` | Closes the audit trail. The target must call `close_lineage_record()` in both the success path AND the error handler. |
| **11. Watermark advance** | `UPDATE Integration.[ETL Cutoff] SET [Cutoff Time] = @NewCutoff WHERE [Table Name] = 'fact.purchase'` | Moves the incremental boundary forward. Must only happen after successful load — if it advances after a failed load, data is lost. |

### Column-level lineage details

The column-level lineage table (§4.3) maps every target column to its source, through its intermediate, with the exact transformation:

| Target Column | Transformation | Migration note |
|---|---|---|
| `Date Key` | `CAST(OrderDate AS date)` in SSIS extract | Direct equivalent in Spark: `CAST(order_date AS DATE)` |
| `Supplier Key` | `COALESCE(TOP(1) SCD-2 match..., 0)` | Must be completely reimplemented as temporal range JOIN + ROW_NUMBER |
| `Stock Item Key` | Same pattern as Supplier Key | Same reimplementation needed |
| `Lineage Key` | `NEXT VALUE FOR Sequences.LineageKey` | SEQUENCE retired; replaced by IDENTITY column + Python utility |
| `Package` | Pass-through from `PackageTypes.PackageTypeName` via buying-package FK join | The FK join happens at extract time in the 5-table OLTP JOIN |
| All quantity columns | Pass-through — no transformation | Must be preserved exactly; no accidental arithmetic |

### Why this section matters

Section 4 is where the as-is analysis pays for itself. Without it:

- **Step 2 (the bug)** would be invisible. No one would know to fix it because the bug is in the SSIS dataflow metadata, not in any SQL code.
- **Steps 6-7 (SCD-2 resolution)** would be translated incorrectly. The boundary semantics (`> Valid From` exclusive, `<= Valid To` inclusive) and the `ORDER BY Valid From` (not DESC) tie-breaker are subtle details that determine whether the correct historical dimension version is selected.
- **Step 8 (fact delete)** would be missed. Many developers would translate the MERGE without realizing there's a preceding DELETE that implements order-level full-replacement.
- **Step 11 (watermark advance)** would be placed in the wrong location. If the watermark advances before the MERGE completes, and the MERGE fails, the next run skips the failed data — a silent data loss.

---

## Section 5 — Calculations

### What it contains

Three calculations documented with full detail: business purpose, mathematical formula, input columns, actual SQL code, step-by-step calculation logic, and thresholds/categorization.

### Calculation 5.1 — Date Key Derivation

| Aspect | Detail |
|---|---|
| Formula | `Date Key = CAST(OrderDate AS date)` |
| Where it happens | SSIS extract dataflow (not in the stored procedure) |
| What it does | Strips time-of-day from `datetime`/`datetime2` to produce a plain `date` for FK to `dimension.date` |
| Pass-through after extract? | Yes — `migratestagedpurchasedata` reads it from staging and writes it unchanged to the fact |

**Why it matters:** This is the **only derived column** at extract time. All other columns are pass-throughs. If a developer adds an accidental transformation to `date_key` during migration, it breaks the FK relationship with `dimension.date`.

### Calculation 5.2 — Ordered Outers and Ordered Quantity

| Aspect | Detail |
|---|---|
| Formula | Both are **pass-throughs** — no arithmetic in the DW ETL |
| Relationship | `Ordered Quantity = Ordered Outers × Quantity Per Outer` — but this is computed in the **OLTP source**, not the DW |
| `Received Outers` | Also a pass-through; receipt completeness ratio (`Received / Ordered`) is computed at the **BI layer**, not ETL |

**Why it matters:** Documenting that these are pass-throughs prevents a developer from accidentally "improving" the ETL by adding calculations that already exist elsewhere. The relationship between outers and quantity is governed by the dimension attribute `Quantity Per Outer`, not by ETL logic.

### Calculation 5.3 — SCD-2 Surrogate Key Resolution (the critical one)

This is the most detailed calculation in the as-is — and it's the **most migration-critical logic** in the entire product.

**The problem it solves:** `fact.purchase` references two SCD-2 dimensions via integer surrogate keys. The source system uses natural keys (`WWI Supplier ID`, `WWI Stock Item ID`). Because both dimensions are Type-2 (they maintain version history with `Valid From` / `Valid To` ranges), a simple lookup by natural key isn't enough — you need the surrogate key that was active **at the time the purchase order was last modified**.

**The formula:**
```sql
Supplier Key = COALESCE(
    (SELECT TOP(1) s.[Supplier Key]
     FROM Dimension.Supplier s
     WHERE s.[WWI Supplier ID] = stg.[WWI Supplier ID]
       AND stg.[Last Modified When] > s.[Valid From]      -- exclusive
       AND stg.[Last Modified When] <= s.[Valid To]        -- inclusive
     ORDER BY s.[Valid From]),                              -- earliest match
    0)                                                      -- fallback: unknown
```

**Three critical subtleties documented:**

| Subtlety | Detail | What goes wrong if missed |
|---|---|---|
| **Boundary semantics** | `> Valid From` (exclusive) and `<= Valid To` (inclusive) | Using `>=` instead of `>` can select the previous SCD-2 version when the modification timestamp exactly equals a version boundary — the fact row gets the wrong supplier attributes |
| **ORDER BY direction** | `ORDER BY Valid From ASC` (earliest matching version) | In a well-formed SCD-2, only one version matches. But if overlapping rows exist (a dimension DQ defect), `ASC` selects the earliest — `DESC` would select a different row. The target must match this behavior. |
| **Fallback to key 0** | `COALESCE(..., 0)` — unresolved rows get surrogate key 0 ("Unknown") | Key 0 is a **sentinel row** that must be pre-seeded in the dimension table. If it doesn't exist, FK checks fail. If the fallback is changed to `NULL` instead of `0`, any `NOT NULL` constraint on the FK column causes the load to fail. |

**Pre-condition:** Both dimension tables must be fully loaded before this code runs. If either dimension is empty, **every row** resolves to key 0 — silently. No error is raised. This is the cross-team dependency (Risk #6 from the modernization plan) in its most dangerous form.

### Why this section matters

The calculations section captures the **exact behavioral contract** of the ETL. For pass-throughs, it documents "this column must not be transformed." For derivations, it documents the exact formula, boundary conditions, and edge cases. The SCD-2 resolution logic alone has 3 subtleties that would be easy to get wrong without this documentation — and any of them would cause silent data corruption in the fact table.

---

## Section 6 — Sources

### What it contains

**Section 6.1 — Input Source Tables:** 8 source objects documented with platform, schema, object type, description, and key fields used. Covers both the OLTP source tables (in `wideworldimporters`) and the DW control/staging tables (in `wideworldimportersdw`).

**Section 6.2 — Output Tables:** 7 output objects documented with target system, object type, and description.

### Input sources — what feeds the Purchase ETL

| Source | Database | Type | Key detail |
|---|---|---|---|
| `Purchasing.PurchaseOrders` | wideworldimporters (OLTP) | Table | Header records — `OrderDate`, `IsOrderFinalized`, `SupplierID` |
| `Purchasing.PurchaseOrderLines` | wideworldimporters (OLTP) | Table | Line items — `OrderedOuters`, `OrderedQuantity`, `ReceivedOuters`, `LastEditedWhen` (watermark filter column) |
| `Warehouse.StockItems` | wideworldimporters (OLTP) | Table | Stock item master — temporal table with `_Archive` variant |
| `Warehouse.PackageTypes` | wideworldimporters (OLTP) | Table | Packaging type lookup — `PackageTypeName` (buying package) |
| `Purchasing.Suppliers` | wideworldimporters (OLTP) | Table | Supplier master — temporal table with `_Archive` variant |
| `Integration.ETL Cutoff` | wideworldimportersdw (DW) | Control table | Per-entity watermark — `Table Name` PK, `Cutoff Time` |
| `Integration.Lineage` | wideworldimportersdw (DW) | Control table | Run audit log — `Lineage Key` PK, timestamps, success flag |
| `Sequences.LineageKey` | wideworldimportersdw (DW) | Sequence object | `NEXT VALUE FOR` generates monotonic lineage keys |

**Important distinction:** The OLTP tables are in the `wideworldimporters` database (the transactional system). The DW control tables are in `wideworldimportersdw` (the analytical system). The SSIS extract crosses this database boundary — the Databricks replacement must use JDBC to reach the OLTP source.

### Output tables — what the Purchase ETL writes

| Output | Type | Key detail |
|---|---|---|
| `Fact.Purchase` | Fact table | The primary output — 11 columns, IDENTITY PK |
| `Dimension.Supplier` | SCD-2 dimension | **Read dependency only** — Purchase reads it for key resolution but doesn't write to it |
| `Dimension.Stock Item` | SCD-2 dimension | **Read dependency only** — same as supplier; name contains space |
| `Dimension.Date` | Static dimension | **Read dependency only** — FK target, pre-populated |
| `Integration.Purchase_Staging` | Staging table | **Never correctly truncated** — the SSIS bug leaves stale rows |
| `Integration.ETL Cutoff` | Control table | Updated at end of each successful run to advance the watermark |
| `Integration.Lineage` | Control table | Row inserted at run start; updated at run end with completion time and success flag |

### Why this section matters

Section 6 completes the forensic inventory by cataloging every table the Purchase ETL touches — both reads and writes. Two important details:

1. **Dimension tables appear in both input AND output sections** — as read dependencies in the output section (because `migratestagedpurchasedata` reads them for SCD-2 lookups) and as source objects in the input section (because they originate from the OLTP `Purchasing.Suppliers` and `Warehouse.StockItems` tables). This dual listing makes it unambiguous that Purchase **reads** dimensions but does **not load** them.

2. **The staging table is listed as an output with the bug annotation** — `Integration.Purchase_Staging` is documented as "never correctly truncated due to the SSIS bug." This ensures the bug is visible in every section of the as-is, not just the lineage section.

---

## How This Spec Is Used Downstream

| Downstream spec | What it takes from the as-is |
|---|---|
| **Product transformation rules** | Specific override/extension needs discovered from the as-is detail (e.g., TY-P001 override for SCD-2 validity columns emerged from the §5.3 calculation analysis showing `Valid From`/`Valid To` boundary semantics) |
| **To-be design** | **Direct section-by-section mirror.** Every to-be section references its as-is counterpart. §1 Definition → modernized definition. §2 Consumers → reconnected consumers. §3 Model → target ER diagram. §4 Lineage → 22-step target pipeline (vs. 11 steps in as-is). §5 Calculations → target implementations with rule IDs. §6 Sources → target platform tables. |
| **Development plan requirements** | Functional requirements derived from as-is behavior (e.g., FR-004 "SCD-2 supplier key resolution" is directly derived from as-is §5.3) |
| **Development plan tasks** | Implementation tasks trace to specific as-is sections (e.g., TASK-011 "Write sk_resolver.py" implements the target equivalent of as-is §5.3) |
| **Runbook** | Failure recovery procedures reference as-is lineage steps (e.g., the watermark recovery procedure in the runbook traces back to as-is §4.4 steps 1 and 11) |
| **Reviewers / QA** | The as-is is the **acceptance baseline** — reviewers compare the to-be and generated code against the as-is to verify that all legacy behavior is preserved (or explicitly changed with rule justification) |

---

## File Reference

| File | Location |
|---|---|
| `as-is.md` | `products/Purchase/current/specifications/as-is.md` |

This is a single markdown file containing all 6 sections. It is the largest spec in the TCP flow — typically 500-900 lines — because it captures every detail of the legacy system including actual SQL code, full ER diagrams, and step-by-step transformation tables.
