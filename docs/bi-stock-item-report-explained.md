# BI Reconnection Spec: Stock-Item Report — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `specifications/to-be.md` + transformation rules (FR-010, NM-001, TY-*)
**Location:** `products/Purchase/current/codebase/docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md`
**Produced by:** `/smartbuilder_generate-etl` (TASK-023)
**Contents:** 6 sections — report identity, connection details, table mapping (5 tables), column mapping (11 columns), cross-product dependency, 16-item cutover checklist

---

## What This Spec Is

The BI reconnection spec is a **handoff document for a BI developer**, not executable code. It bridges two worlds: the migVisor specification chain that describes what the data platform now looks like, and the Power BI report that was pointing at a SQL Server 2014 database and must be redirected to a Databricks SQL Warehouse.

It sits at the end of the artifact chain alongside the other Phase 3 deliverables:

| Artifact | Lives in | Purpose |
|---|---|---|
| `specifications/to-be.md` | specifications/ | Designed the target data model and migration rules |
| `specifications/development_plan/tasks.md` | specifications/ | Described TASK-023 and its FR-010 obligation |
| `src/db/ddl/silver_fact_fact_purchase.sql` | codebase/src/ | Defines the actual target table schema |
| `docs/data-dictionary.md` | codebase/docs/ | Defines every column in every table |
| **`docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md`** | **codebase/docs/bi/** | **Tells the BI developer exactly what to change in the report** |

It is the only artifact in the chain written for an audience outside the data engineering team — the BI developer reconnecting the report, and the business analyst validating it. Its sections map directly to the actions those two roles perform.

It has six sections:

| Section | What it supplies |
|---|---|
| Report name and description | What the report does, why it requires a coordinated cutover |
| Connection details | Databricks SQL Warehouse endpoint, auth method, step-by-step Power BI instructions |
| Table mapping | Five legacy SQL Server tables → five Unity Catalog targets |
| Column mapping | Eleven `fact_purchase` columns, PascalCase → snake_case, with type change notes |
| Cross-product dependency | Joint cutover requirement with the Sales_Orders product |
| Cutover checklist | 16 ordered actions with owner assignments |

---

## Why This Spec Exists

### Because FR-010 requires it for every report that joins Purchase data

FR-010 mandates a reconnection specification for every Power BI report that reads from the migrated tables. This report reads `fact_purchase` plus two tables outside the Purchase product boundary (`fact_sale` from Sales_Orders and `silver_dim.date`), so it carries the most complex reconnection of the two Purchase BI reports.

### Because the report cannot be reconfigured without knowing what changed

The legacy report connected to SQL Server as a DirectQuery source. The target is Databricks SQL Warehouse — a different connector, a different auth mechanism, a different catalog structure, and different column names on every table it reads. Without a document that translates each legacy object to its target equivalent, a BI developer reconnecting the report would have to reconstruct the mapping from the data dictionary, the as-is analysis, and the transformation rules separately.

This document does that reconstruction once.

### Because the cross-product dependency has nowhere else to surface

The `wwidw_purchase_and_sale_per_stockitem_dynamic` report joins `fact_purchase` with `fact_sale` — a table owned by the Sales_Orders product. That join is what makes this the harder of the two reports to cut over. The product scope document notes the cross-product dependency; the task list (TASK-024) lists the coordinated cutover as a requirement; but neither document provides the coordination checklist — the actions, owners, and sequence. Section 5 and the cutover checklist are the first and only place those appear in procedural form.

---

## Section 1 — Report Name and Description

### What it contains

A six-row metadata table: report name, legacy connection, new connection, description, report type, and primary use cases.

### Key facts captured

**The description names the join that makes this report the harder cutover.** The report joins `silver_fact.fact_purchase` (Purchase product) with `silver_fact.fact_sale` (Sales_Orders product) and `silver_dim.stock_item`. Two of the three tables are owned by other products, and one of them — `fact_sale` — must be deployed before this report can go live. That structural dependency is stated in the description, not just in Section 5.

**The three primary use cases define what a valid test looks like.** Open purchase orders relative to sales activity, volumes vs. demand per stock item, receipt vs. sales comparison. A BI developer validating the reconnected report has a business-readable checklist of what should be answerable: if any of these three questions returns no data or wrong data, the reconnection is incomplete.

**"DirectQuery" is load-bearing.** Import mode would cache data in Power BI; DirectQuery queries the warehouse on every render. The choice was made in `to-be.md` (OB-P004: DirectQuery recommended for reporting layers with SLA requirements) and carried here. It means the SQL Warehouse must be running when the report is opened, and every row-level filter in the report becomes a live SQL query against `fact_purchase` and `fact_sale`. Latency and warehouse sizing matter in a way they would not for an Import-mode report.

---

## Section 2 — Databricks SQL Warehouse Connection Details

### What it contains

Eight connection parameters, two placeholders to fill in, and step-by-step Power BI Desktop connection instructions.

### Key facts captured

**Both placeholders are environment-specific and documented as such.** `{{DATABRICKS_HOST}}` and `{{WAREHOUSE_ID}}` require values that differ between dev, staging, and production environments. The note makes this explicit with an example hostname format. A template with undocumented placeholders is a support ticket waiting to happen; a template with the example format (`adb-1234567890.1.azuredatabricks.net`) makes the substitution unambiguous.

**OAuth 2.0 client credentials flow is the auth pattern.** The report authenticates as a service principal, not as the BI developer's user account. That is the right pattern for a scheduled report that runs unattended — user credentials expire, service principal credentials are managed by the platform team. But it requires the platform team to have provisioned the service principal and granted it SELECT on the target tables (PD-003) before the BI developer can complete step 4 of the connection instructions.

**The driver note covers both Simba and Databricks ODBC v2.x.** Two drivers are listed because organizations that already have the Simba driver installed need not upgrade; those installing fresh may prefer the Databricks driver. Both work with DirectQuery against a SQL Warehouse.

---

## Section 3 — Table Mapping

### What it contains

Five rows mapping legacy SQL Server `wideworldimportersdw` tables to Unity Catalog targets, with notes on schema mapping and SCD-2 view usage.

### Key facts captured

**Three of the five tables are outside the Purchase product boundary.** `fact_sale` is Sales_Orders' table. `silver_dim.date` is shared infrastructure. `silver_dim.stock_item` is owned by the Dimensions team. The Purchase product only *owns* `fact_purchase`. A BI developer updating table references must resolve five targets but can only verify three of them from the Purchase product documentation.

**The SCD-2 `_current` views are the recommended join target for dimension tables.** The mapping notes point the report to `silver_dim.supplier_current` and `silver_dim.stock_item_current` rather than the base dimension tables. Those views pre-filter `WHERE is_current_row = TRUE`, which eliminates the need for a WHERE clause in every report query that joins to a dimension. The report's legacy queries almost certainly had no such filter — they joined to a Type-1 or current-row-only SQL Server dimension without needing it. The view handles the translation transparently.

**The space-in-name resolution is captured as a note.** `dimension.stock item` (with a space) becomes `silver_dim.stock_item` (underscore). NM-002 governs this, and the mapping table row makes it explicit. Without that note, a BI developer searching for the report's legacy table name in the Unity Catalog would find nothing and assume the table does not exist.

**The `fact_sale` row carries no column mapping.** Section 4 maps only `fact_purchase` columns. Columns from `fact_sale` and the dimension tables are not mapped here. For a report that joins five tables, that is a gap — a BI developer updating the `fact_sale` reference would need the Sales_Orders product's own reconnection spec for its column mapping.

---

## Section 4 — Column Name Mapping

### What it contains

Eleven rows, one per `fact_purchase` column. Each row gives the legacy PascalCase name, the target snake_case name, the data type, and a notes field covering derivation or type changes.

### Key facts captured

**Seven of eleven columns are pass-throughs with only a name change.** `OrderedOuters`, `OrderedQuantity`, `ReceivedOuters`, `Package`, `IsOrderFinalized`, `WWIPurchaseOrderID`, and `LineageKey` carry the same data with different names. A BI developer updating those references needs only the name substitution.

**Four columns carry substantive changes that require expression rewrites.**

`DateKey` is the most significant. Legacy: `INT` in YYYYMMDD format (e.g. `20240315`). Target: `DATE` value (e.g. `2024-03-15`). Any report filter written as `DateKey >= 20240101 AND DateKey <= 20240131` will not work against a DATE column without rewriting. The notes field flags this explicitly (TY-010). A BI developer who misses this change will produce either an error or a silently wrong date filter.

`SupplierKey` and `StockItemKey` are SCD-2 surrogate keys resolved by `sk_resolver.py`. The legacy keys were direct join references; the target keys are version-specific surrogates. For the report, the practical implication is that joining on these keys must use the `_current` views (already captured in Section 3), not ad-hoc WHERE filters on the base table.

`LineageKey` is a new column with no business meaning in the report. It exists in the fact table for audit purposes. Report queries that select `*` from `fact_purchase` will now include this column and should exclude it from displays.

**`received_outers` is the only nullable column flagged explicitly.** The notes field says "NULL = not received yet; 0 = delivered with zero outers." In SQL Server, the legacy column was also nullable, but reports using it in calculations may not have handled NULL vs. 0 distinctly. Any fill-rate measure (`received_outers / ordered_outers`) needs a `COALESCE(received_outers, 0)` or a conditional, because NULL propagates through division.

---

## Section 5 — Cross-Product Dependency

### What it contains

A dependency table (three rows: Purchase product, Sales_Orders product, shared dimensions), a risk statement, and four coordination actions.

### Key facts captured

**This section is what separates this report from `wwidw_ordered_by_supplier`.** The supplier report is self-contained and can be cut over by the Purchase team alone. This report requires the Sales_Orders product to be deployed, validated, and available in Databricks before a cutover is possible. Section 5 is where that constraint is stated most clearly.

**The risk statement names the only viable interim state.** If Purchase is ready and Sales_Orders is not, the report stays on SQL Server. There is no safe partial cutover — redirecting the report to Databricks while `fact_sale` is still on SQL Server would require a multi-source hybrid connection, which Power BI supports but which is operationally complex and fragile. The risk statement implicitly recommends against it.

**The four coordination actions are procedural, not just informational.** Each is an action (schedule a joint window, validate row counts, test in Power BI Desktop, confirm dimension access). A reviewer reading this section can assign those four actions to owners and track them as a pre-cutover checklist without having to derive the steps from the risk statement.

**`silver_dim.stock_item` and `silver_dim.date` are mentioned here but not in the BI grants (TASK-008).** TASK-008 grants SELECT on `silver_fact.fact_purchase` and the Purchase-owned silver tables to `data_analysts`. It does not grant on `fact_sale` (Sales_Orders' table), `silver_dim.stock_item`, or `silver_dim.date`. The shared dimensions are presumably granted by whoever owns them; `fact_sale` is the Sales_Orders team's grant to make. Section 5 identifies the dependency but the grant coordination is not explicitly tracked anywhere.

---

## Section 6 — Cutover Checklist

### What it contains

Sixteen ordered items with action, owner, and a status checkbox. Owners span Data Engineering, Sales_Orders Data Engineering, BI Developer, Business Analyst, and Project Manager.

### Key facts captured

**Items 1–5 are pre-conditions, not actions.** They verify that the data exists and is accessible before any BI configuration is touched. This ordering is correct — a BI developer who updates the report connection before the data exists will see a connection error that could be mistaken for a configuration problem.

**Item 10 is the one that will trip up a BI developer who reads too quickly.** "Update `DateKey` filter expressions: legacy `DateKey` is INT (YYYYMMDD); target `date_key` is DATE — update any date filter logic accordingly." Date filters in Power BI reports are often embedded in measures, in row-level security filters, and in slicers — not just in the main query. Finding all of them requires a report audit, not just a table-reference update.

**The checklist is 16 items where `wwidw_ordered_by_supplier` is 17 items.** The supplier report has one extra step (item 10: rewrite geography CLR expressions). This report does not join the supplier dimension for its geographic columns, so that step is absent. The different checklist lengths are structurally correct, not an error.

**Item 13 (business stakeholder sign-off) is the gate between testing and publication.** Items 14–16 (publish to Power BI Service, decommission legacy connection, log completion) cannot happen until the business analyst confirms the report output is correct. That gate is easy to skip under deadline pressure — having it as a named checklist item with an owner makes it harder to overlook.

**The status checkboxes are blank.** The document was generated as a template to be completed at cutover time, not as a record of completion. That is the correct state for an artifact produced before the cutover has occurred.

---

## Divergences and Open Items

### 1. The filename carries a `_reconnection` suffix not in the build plan or task list

`build-plan.md` Phase 3 table names the output file as `docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic.md`. The file on disk is `docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md`. This discrepancy is F-004 in `validation-report.md` (named there as F-004 for the workflow JSON, but the same `_reconnection` suffix mismatch appears for both BI files as the build plan path error discussed in the validation report's F-001/F-008 context).

The content of the document is correct; the naming is a gap in the build plan's path specification. The Phase 3 acceptance gate checks "all 7 test/BI/docs files exist" without checking exact paths, so the gate passes. **The build plan should be corrected to the generated names.**

### 2. Column mapping covers only `fact_purchase`; four other tables are unmapped

The report joins five tables. Section 4 maps eleven columns from `fact_purchase`. The column mappings for `fact_sale`, `silver_dim.stock_item`, `silver_dim.supplier`, and `silver_dim.date` are absent. A BI developer updating table references will reach those tables and find no column-level guidance in this document.

For `fact_sale` and `silver_dim.stock_item`, the Sales_Orders product's own BI reconnection spec should supply the mapping. For `silver_dim.supplier`, `wwidw_ordered_by_supplier_reconnection.md` Section 4.2 has it. For `silver_dim.date`, no reconnection spec exists in the Purchase workspace. **A note in Section 4 pointing to the companion documents would close this gap without expanding the document significantly.**

### 3. The BI service principal grant for cross-product tables is untracked

Section 5 says to "confirm the BI read-only service principal has `SELECT` grants on `silver_fact.fact_purchase`, `silver_fact.fact_sale`, `silver_dim.stock_item`, `silver_dim.supplier`, `silver_dim.date`." Checklist item 6 assigns this to "Data Engineering / DBA." But PD-003 (the pending decisions register) only covers the Purchase product's grants — it does not address the grants on `fact_sale` or the shared dimensions.

There is no artifact in the Purchase workspace that tracks who is responsible for granting the BI service principal access to Sales_Orders and Dimensions tables. **This coordination gap should be added to the runbook's cutover checklist as a named action with a named owner from each product team.**

### 4. `received_outers` NULL semantics require a report-side decision not flagged by the checklist

The column mapping notes correctly say `received_outers` is nullable. The cutover checklist has no item asking the BI developer to audit fill-rate measures for NULL handling. A fill-rate calculation (`received_outers / ordered_outers`) that worked on SQL Server by treating NULL as 0 will behave differently in Power BI/DAX if NULL is propagated rather than coalesced.

This is not a data engineering issue — the column is correctly nullable in both source and target. It is a report logic issue that the reconnection process should surface. **Checklist item 10 (currently about DateKey) should be accompanied by an item about reviewing any measure that divides `received_outers` or references it in a comparison.**

---

## How This Spec Is Used Downstream

| Consumer | What they take from this document |
|---|---|
| **BI Developer** | Section 2 (connection steps), Section 3 (table references to update), Section 4 (column names to replace), Section 6 (ordered checklist) |
| **Data Engineering** | Section 5 coordination actions and checklist items 1–6 (pre-condition verification) |
| **Sales_Orders Product Team** | Section 5 joint cutover requirement — triggers their own cutover readiness assessment |
| **Business Analyst** | Section 1 use cases (what to validate), checklist item 12 (output validation), item 13 (sign-off) |
| **Project Manager** | Checklist item 16 (completion log) |

---

## File Reference

| File | Location |
|---|---|
| This document | `products/Purchase/current/codebase/docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md` |
| Companion BI spec | `products/Purchase/current/codebase/docs/bi/wwidw_ordered_by_supplier_reconnection.md` |
| `data-dictionary.md` | `products/Purchase/current/codebase/docs/data-dictionary.md` — full column definitions for `fact_purchase` |
| `src/db/ddl/silver_fact_fact_purchase.sql` | `products/Purchase/current/codebase/src/db/ddl/silver_fact_fact_purchase.sql` — authoritative DDL for column types |
| `tasks.md` TASK-023 | `products/Purchase/current/specifications/development_plan/tasks.md` — FR-010 obligation and cross-product cutover requirement |
| `runbook.md` | `products/Purchase/current/codebase/docs/runbook.md` — PD-001/002/003 resolution steps that must precede the cutover checklist |
