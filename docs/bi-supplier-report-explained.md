# BI Reconnection Spec: Supplier Report — Explained

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Generated:** 2026-09-07
**Derived from:** `specifications/to-be.md` + transformation rules (FR-010, NM-001, TY-*)
**Location:** `products/Purchase/current/codebase/docs/bi/wwidw_ordered_by_supplier_reconnection.md`
**Produced by:** `/smartbuilder_generate-etl` (TASK-024)
**Contents:** 6 sections — report identity, connection details, table mapping (2 tables), column mapping (fact + supplier dimension), self-contained dependency statement, 17-item cutover checklist

---

## What This Spec Is

Like its companion document (`wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md`), this is a **handoff document for a BI developer** — not executable code. It translates the migVisor specification chain into the concrete changes a BI developer must make in Power BI to redirect `wwidw_ordered_by_supplier` from SQL Server 2014 to Databricks SQL Warehouse.

The two BI reconnection specs are the same type of artifact but they are structurally different in one critical way:

| Report | Tables joined | Cross-product dependency | Cutover owner |
|---|---|---|---|
| `wwidw_purchase_and_sale_per_stockitem_dynamic` | 5 (Purchase + Sales_Orders + shared dims) | Yes — Sales_Orders must be ready first | Joint: Purchase + Sales_Orders teams |
| **`wwidw_ordered_by_supplier`** | **2 (Purchase + shared supplier dim)** | **None** | **Purchase team alone** |

That difference determines the entire operational shape of the cutover. This report is self-contained and can go live as soon as the Purchase product is deployed, validated, and access-granted — with no dependency on any other product team's schedule.

It has six sections:

| Section | What it supplies |
|---|---|
| Report name and description | What the report does; explicit statement of self-containment |
| Connection details | Databricks SQL Warehouse endpoint, auth, Power BI connection steps |
| Table mapping | Two legacy tables → two Unity Catalog targets |
| Column mapping (4.1 + 4.2) | fact_purchase columns (11) + supplier dimension columns (14 + 3 new) |
| Cross-product dependency | Explicit confirmation: none |
| Cutover checklist | 17 ordered items including geography CLR expression rewrite |

---

## Why This Spec Exists

### Because FR-010 requires it and this report touches the most complex dimension mapping

FR-010 mandates a reconnection spec for every Purchase BI report. `wwidw_ordered_by_supplier` is the easier of the two reports to cut over (two tables, no cross-product dependency), but it has the most technically complex *column* mapping of the two. The supplier dimension underwent structural transformation beyond name normalization — specifically, the `DeliveryLocation geography` CLR column was decomposed into three target columns. Without Section 4.2, a BI developer working from column names alone would encounter a source column with no direct target counterpart and have no guidance on how to handle it.

### Because confirming self-containment is as important as stating dependencies

It would be easy to assume this report depends on Sales_Orders because its companion report does. Section 5 of this document makes the independence explicit. That single statement — "This report is self-contained within the Purchase product" — changes the cutover planning: no joint window, no coordination meeting, no waiting for another team's timeline. The explicit confirmation prevents a conservative project manager from unnecessarily coupling the two cutovers.

---

## Section 1 — Report Name and Description

### What it contains

Report name, legacy and new connections, description, report type (DirectQuery), and four primary use cases.

### Key facts captured

**The use cases define the fill-rate calculation as the primary measure.** "Which suppliers are filling orders in full (received vs. ordered outers)?" is the first use case. Fill rate = `received_outers / ordered_outers`. That calculation uses `received_outers`, which is nullable (NULL = not yet received). A BI developer who does not handle the NULL will produce divide-by-zero errors or wrong fill rates for open orders. Section 4.1 documents the nullability; neither the use cases nor the checklist directly calls out the fill-rate expression review.

**"Self-contained within the Purchase product" appears in the description, not just in Section 5.** This repetition is intentional — the description is the first thing a reader sees, and the independence claim is the most operationally significant fact about this report relative to its companion.

---

## Section 2 — Databricks SQL Warehouse Connection Details

### What it contains

Identical structure to the companion report's Section 2: eight connection parameters, two environment-specific placeholders, and five-step Power BI connection instructions.

### Key facts captured

**The connection details are identical to the stock-item report.** Same warehouse, same auth method, same driver. If both reports are being cut over as part of the same deployment, a BI developer configuring one will find the other already configured. This also means the BI service principal grant covers both reports — PD-003's resolution (TASK-008 with correct role names) grants access to all silver tables to `data_analysts`, covering `fact_purchase` and `silver_dim.supplier` for this report.

---

## Section 3 — Table Mapping

### What it contains

Two rows: `fact.purchase` → `silver_fact.fact_purchase`, and `dimension.supplier` → `silver_dim.supplier`.

### Key facts captured

**The mapping is the simplest of the two BI specs.** Two tables, both within or adjacent to the Purchase product boundary. A BI developer updating table references has two substitutions to make.

**The recommended target for the supplier dimension is the `_current` view, not the base table.** `silver_dim.supplier_current` pre-filters `WHERE is_current_row = TRUE`. The legacy `dimension.supplier` was a Type-1 dimension — current state only, no history — so the legacy report never needed to filter by currentness. The view makes the transition transparent: join to `supplier_current` and the behavior is equivalent to the legacy join, without adding a WHERE clause to the report query.

**The note on schema mapping (`dimension` → `silver_dim`) is explicit.** The schema name changes and the dot-notation is different. PL-002 governs this, and the mapping table makes it concrete.

---

## Section 4 — Column Name Mapping

### What it contains

Two subsections: Section 4.1 maps eleven `fact_purchase` columns; Section 4.2 maps fourteen supplier dimension columns, with notes on three new columns added in the target.

### Key facts captured

**Section 4.1 (`fact_purchase`) is identical to the companion report's Section 4.** The same eleven columns, same type changes, same notes. `date_key` type change (INT → DATE) and `received_outers` nullability are the two substantive issues, same as for the stock-item report.

**Section 4.2 (supplier dimension) is what makes this document unique.** The supplier dimension underwent three categories of change:

*Name normalization only (no structural change):* `SupplierKey`, `WWISupplierID`, `Supplier`, `Category`, `PrimaryContact`, `PostalCode`, `ValidFrom`, `ValidTo`. These are direct substitutions.

*Type changes requiring expression rewrites:* `ValidFrom` (DATETIME2 → DATE, TY-P001) and `ValidTo` (DATETIME2 → DATE, TY-P001). If the report uses `ValidFrom`/`ValidTo` in date range calculations or comparisons, those expressions must be updated for DATE vs. DATETIME2 semantics.

*Structural decomposition:* `DeliveryLocation` (SQL Server `geography` CLR type) → three columns: `delivery_location_wkt` (WKT string), `delivery_location_lat` (DOUBLE), `delivery_location_lon` (DOUBLE). This is a one-to-three mapping: one source column becomes three target columns. Any report expression that referenced `DeliveryLocation` for geographic visualization or proximity calculations must be rewritten using the three decomposed columns. TY-P004 governs this decomposition.

*New columns with no legacy equivalent:* `row_effective_date`, `row_expiry_date`, and `is_current_row` are SCD-2 control columns added by TY-P002. The report may receive these columns if it selects `*` from the base supplier table. Switching to `supplier_current` makes them irrelevant — they are pre-filtered — but if the report selects from the base table directly, these columns should be excluded from displays.

**The `LineageKey` in the supplier dimension is notable.** The legacy `dimension.supplier` did not have a lineage key. The target `silver_dim.supplier` does. Like `fact_purchase.lineage_key`, it is an audit column with no business meaning in the report and should be excluded from displays or `SELECT *` results.

---

## Section 5 — Cross-Product Dependency

### What it contains

A single affirmative statement — this report is self-contained — with a list of the two tables it joins and a paragraph confirming no dependency on Sales_Orders.

### Key facts captured

**"This report does NOT reference `fact.sale` or any other object outside the Purchase product."** The capital NOT and the explicit naming of `fact.sale` are doing work: they anticipate the assumption a project manager might make after reading the companion report and preempt a coordination requirement that does not exist.

**The self-containment claim is narrowly accurate.** The report joins `fact_purchase` (Purchase-owned) and `silver_dim.supplier` (Dimensions-owned, managed within the Purchase product scope). Strictly speaking, the supplier dimension is *managed by* the Purchase product scope (the Purchase ETL creates the `_current` view, the DDL for `silver_dim.supplier` is referenced by TASK-006/007), but the dimension load itself is performed by an external team. If the Dimensions team has not loaded `silver_dim.supplier` before cutover, the report will produce empty or wrong results even though there is no "cross-product dependency" in the SDD sense. Section 3 recommends the `_current` view; the runbook's prerequisite check (section 3 of the runbook) covers this.

---

## Section 6 — Cutover Checklist

### What it contains

Seventeen ordered items, one more than the companion report's sixteen. The extra item is about the geography CLR expression rewrite.

### Key facts captured

**Items 1–3 are pre-conditions covering both fact and dimension tables.** The checklist correctly sequences these before any BI configuration change. Items 4–11 are BI developer actions; items 12–14 are validation and sign-off; items 15–17 are publication and cleanup.

**Item 10 (geography CLR rewrite) is the most complex item in either checklist.** It requires a BI developer to: identify every expression in the report that referenced the legacy `DeliveryLocation geography` column; decide whether each expression needs the WKT string, the latitude, or the longitude; and rewrite those expressions in Power BI's DAX or M formula language. This is not a find-and-replace operation. If the report used geographic distance calculations or map visualizations based on `DeliveryLocation`, those visualizations may need to be rebuilt rather than updated.

**Item 11 is the `_current` view filter removal.** If the legacy report manually filtered `WHERE ValidTo = '9999-12-31'` (a common workaround for SCD-2 base tables where no current-record flag exists), that filter must be removed when switching to `supplier_current`, which pre-applies it. Forgetting to remove the filter does not break the report — `supplier_current` only exposes current rows, so the filter matches all rows — but it is redundant and should be cleaned up. Forgetting to add it when joining to the base table would return all historical versions.

**The 17-item checklist vs. 16-item checklist is a useful signal.** The supplier report's extra item (10: geography CLR) is not just a cosmetic difference — it documents a structural transformation that the companion report's column mapping does not face. A project manager comparing the two cutovers by checklist length will correctly infer that the supplier report requires more BI-developer effort despite its simpler data dependency.

---

## Divergences and Open Items

### 1. The filename carries a `_reconnection` suffix not in the build plan

`build-plan.md` lists `docs/bi/wwidw_ordered_by_supplier.md`. The file on disk is `docs/bi/wwidw_ordered_by_supplier_reconnection.md`. Same discrepancy as the companion report — the `_reconnection` suffix was added during generation and the build plan was not updated. The Phase 3 acceptance gate passes because it checks file existence, not exact paths. **The build plan should be corrected to the generated names.**

### 2. SCD-2 `ValidFrom`/`ValidTo` type changes (DATETIME2 → DATE) are noted but no checklist item covers them

The column mapping table in Section 4.2 notes that `ValidFrom` and `ValidTo` changed from DATETIME2 to DATE (TY-P001). If the report uses these columns in time-range calculations or date comparisons, those expressions must be updated — the same concern as the `DateKey` INT → DATE change in `fact_purchase`. Checklist item 9 covers `DateKey` filter expressions but no item addresses `ValidFrom`/`ValidTo` filter expressions. **An item should be added: "Review any expressions using `ValidFrom`/`ValidTo` dimension date columns: legacy type is DATETIME2; target type is DATE (TY-P001)."**

### 3. The `_current` view's pre-filtering of SCD-2 rows is assumed but not verified in the checklist

The checklist's item 2 says "Confirm `silver_dim.supplier` and `silver_dim.supplier_current` are fully populated; row count matches legacy `dimension.supplier` (current rows)." The row-count check compares against legacy current rows, which is correct. But the checklist does not include a step to verify that `supplier_current` returns *exactly one row per supplier* (no duplicates from overlapping SCD-2 versions). If the SCD-2 load has a bug and `is_current_row` is set for multiple versions of the same supplier, `supplier_current` would return multiple rows per supplier and the report would fan out on the join. **Item 2 should include a deduplication check: `SELECT wwi_supplier_id, COUNT(*) FROM silver_dim.supplier_current GROUP BY wwi_supplier_id HAVING COUNT(*) > 1` returns 0 rows.**

### 4. `batch_lookback_days` in `environment.yaml` is referenced by no column in this report but affects what it shows

`batch_lookback_days: 1` in `config/environment.yaml` controls how far back the incremental extract window can reach. If the pipeline runs at 02:00 UTC and the report is queried at 01:00 UTC the following night, there is a one-hour window where today's purchase data is not yet in `fact_purchase`. This is an operational reality, not a reconnection issue — the report will show yesterday's data during that window. No section of the reconnection spec mentions latency. **A brief note in Section 1 ("Report data reflects the state of `fact_purchase` as of the last successful nightly run at 02:00 UTC") would set stakeholder expectations correctly.**

---

## How This Spec Is Used Downstream

| Consumer | What they take from this document |
|---|---|
| **BI Developer** | Section 2 (connection steps), Section 3 (table references), Section 4.1+4.2 (column substitutions, including geography rewrite), Section 6 (checklist) |
| **Data Engineering** | Checklist items 1–3 (pre-condition verification before BI developer starts) |
| **Business Analyst** | Section 1 use cases (fill rate, open/closed distribution, volume ranking) — the validation baseline |
| **Project Manager** | Section 5 (confirms no joint cutover coordination needed), item 17 (completion log) |

---

## File Reference

| File | Location |
|---|---|
| This document | `products/Purchase/current/codebase/docs/bi/wwidw_ordered_by_supplier_reconnection.md` |
| Companion BI spec | `products/Purchase/current/codebase/docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md` |
| `data-dictionary.md` | `products/Purchase/current/codebase/docs/data-dictionary.md` — full column definitions for both `fact_purchase` and `silver_dim.supplier` |
| `src/db/ddl/silver_dim_supplier_current.sql` | `products/Purchase/current/codebase/src/db/ddl/silver_dim_supplier_current.sql` — the `_current` view definition |
| `tasks.md` TASK-024 | `products/Purchase/current/specifications/development_plan/tasks.md` — FR-010 obligation |
| `runbook.md` | `products/Purchase/current/codebase/docs/runbook.md` — prerequisite checks for dimension availability before cutover |
