---
task_id: TASK-AS-IS-001
product: Sales_Orders
participant_file: as-is-task2.md
reference_file: as-is-reference.md
checked_at: 2026-09-01T15:55:00Z
total_score: 95/100
grade: Excellent
---

# Task Check Report — as-is.md
_Sales_Orders | 2026-09-01_

> **Note:** The participant file (`as-is-task2.md`) is byte-for-byte identical to the reference file (`as-is-reference.md`). The evaluation below scores the content on its merits against the rubric — but this identity should be confirmed as expected (e.g., participant produced the output via the as-is agent pipeline) rather than a manual copy.

---

## Score Summary

| Section | Max | Score | Status |
|---|---|---|---|
| 1. Definition | 20 | 19 | ✓ |
| 2. Consumers | 15 | 12 | ⚠ |
| 3. Model | 25 | 24 | ✓ |
| 4. Lineage | 20 | 20 | ✓ |
| 5. Calculations | 10 | 10 | ✓ |
| 6. Sources | 10 | 10 | ✓ |
| **Total** | **100** | **95** | |

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Section 1 — Definition (19/20)

**What was covered well:**
- Product name (`Sales_Orders`) and domain (`Sales and Order Management`) stated explicitly.
- Technology stack is precisely identified: Microsoft SQL Server 2014, `wideworldimportersdw` database, on-prem deployment implied by hosting model.
- Volume and scale are excellent: 12 million rows/year on `Fact.Sale`, history baseline from 2013-01-01.
- Business context and value are thoroughly explained — orders, invoices, profitability, supply chain, regional reporting all addressed.
- All stakeholder groups named (sales management, finance, supply chain, regional management).

**What was missing or imprecise:**
- Scope boundaries (criterion: "IN scope and OUT OF scope both stated explicitly") are implied by the product description and metadata rows but never explicitly enumerated. Row 8 (`Data Access and Restrictions`) and row 3 (`Process Type`) remain as `[USER INPUT REQUIRED]` placeholders, leaving access control scope undefined.

**Improvement items:**
- [ ] Add an explicit IN-scope / OUT-of-scope block — e.g., "IN scope: `Fact.Sale`, `Fact.Order`, seven conformed dimensions, ETL pipeline. OUT OF scope: `Fact.Purchase`, OLTP transaction tables, Finance.GL."
- [ ] Fill in row 3 (Process Type) and row 8 (Data Access and Restrictions) — these are required metadata fields.

---

### Section 2 — Consumers (12/15)

**What was covered well:**
- All 15 consumers (9 Power BI reports + 4 analytics views + 1 ETL process + 1 OLTP-direct report) are listed and cross-referenced against the product scope.
- Consumption method is named precisely per consumer (direct Power BI, via view, SQL view, stored procedure call, OLTP-direct).
- Dependency type is clear: all BI reports are read-only; the ETL procedure is an internal operational dependency.

**What was missing or imprecise:**
- **Owner/contact per consumer (0/2):** No team name, role, or email is provided for any consumer. This is a full miss on the criterion.
- **Access frequency/SLA (2/3):** The ETL pipeline (`nightly`) is documented. BI reports have no stated SLA or access frequency (e.g., interactive/on-demand, daily scheduled refresh). The four SQL views and two scalar functions also lack any frequency indicator.

**Improvement items:**
- [ ] Add an owner/contact column (team name or role) to the consumer table — even "Finance Team", "Sales Ops", or "Unknown – investigate" is sufficient.
- [ ] Add a frequency/SLA column: e.g., "on-demand (interactive)", "daily scheduled refresh", "nightly batch" per consumer.

---

### Section 3 — Model (24/25)

**What was covered well:**
- All primary entities documented: 2 fact tables, 7 dimensions, 5 staging tables, 4 analytics views, 2 scalar UDFs — all present in both the ER diagram and textual description.
- Key columns identified with data types and PK/FK marking in the Mermaid ER diagram.
- Relationships fully documented with cardinality (1:N, nullable FK for PickerKey) — the ER diagram satisfies the "valid substitute" criterion in full.
- Entity purpose is described for every layer in the textual description table.
- Constraints noted: IDENTITY PK, SEQUENCE surrogate keys, columnstore index (`CCX_Fact_Sale`), `ValidFrom`/`ValidTo` SCD2 pattern, geography column, `[USER INPUT REQUIRED]` gaps are consistent with reference scope.

**What was missing or imprecise:**
- **Known data quality issues (2/3):** Structural issues are identified (Sale_Staging lacks LineageKey vs. Order_Staging; `Dimension.Payment Method` and `Dimension.Transaction Type` have no FK bindings to either fact; `dbo.OrderDetails` is a duplicate decommission candidate). However, no NULL rates, actual orphaned FK counts, or known data inconsistencies from production are documented — these would require access to the live system, which may be intentionally deferred.

**Improvement items:**
- [ ] Supplement the DQ section with any known NULL rates or orphaned FK observations from the source system (e.g., "PickerKey is nullable in `Fact.Order` — approximately X% of rows have no picker assignment").

---

### Section 4 — Lineage (20/20)

**What was covered well:**
- Upstream sources named with full system, database, and schema identifiers (`wideworldimporters`, `wideworldimportersdw`, `sqldwdatasets.blob.core.windows.net`).
- Ingestion method documented precisely per source: SSIS `dailyetlmain`, `Integration.GetSaleUpdates`, `Integration.GetOrderUpdates`, PolyBase for Azure Blob.
- Transformation steps are outstanding: 14-step transformation table with SQL logic and business meaning per step, covering orchestration → truncate → extract → key resolution → fact load → ETL metadata → analytics layer.
- All downstream consumers mapped to source tables in Section 4.5.
- Lineage traceability fully documented: `Integration.Lineage` (per-run audit), `Integration.ETL Cutoff` (watermark), `Sequences.LineageKey` (run identifier).
- Known gaps explicitly flagged: undocumented 1.05 factor, OLTP-direct bypass bypassing ETL, Azure Blob ad-hoc (not in daily ETL), no Power BI consumer captured for supply/year analytics views.

No deductions.

---

### Section 5 — Calculations (10/10)

**What was covered well:**
- All seven calculations documented with business purpose, mathematical formula, input tables/columns, SQL code, step-by-step walkthrough, and threshold categorization.
- Sale vs. Order path differences explicitly called out for `Total Excluding Tax`, `Tax Amount`, `Total Including Tax`.
- `ProfitMarginWithFactor` correctly identified as a view-layer (not fact-layer) calculation; 1.05 factor flagged as undocumented business rule.
- Edge cases documented: NULL return with no COALESCE guard in both UDF variants, ±0.01 rounding difference from independently rounded components in Order path.
- Scalar UDF duplication (`getTotalQuantitySold1` / `getTotalQuantitySold2`) identified and explained.

No deductions. Full marks.

---

### Section 6 — Sources (10/10)

**What was covered well:**
- 19 source objects listed across three platforms (SQL Server `wideworldimporters`, SQL Server `wideworldimportersdw` control objects, Azure Blob via PolyBase) with platform, system, schema, object type, and key fields.
- Connection method documented per source type: SSIS (daily batch), PolyBase (ad-hoc), OLTP-direct (`WebApi.SalesOrders` view).
- Refresh schedule stated per source: daily incremental (ETL window), ad-hoc (Azure Blob), not part of daily ETL explicitly noted.
- Source data quality characteristics present: temporal tables with `_Archive` variants noted, ad-hoc PolyBase gap flagged, OLTP-direct bypass documented, `LastEditedWhen` watermark approach documented.
- Output tables (Section 6.2) comprehensively listed with object type, storage format, and key architectural notes.

No deductions. Full marks.

---

## Approach Notes

- Section 3 ER diagram uses a Mermaid `erDiagram` block — accepted as a full substitute for a relationships table per the rubric. Cardinality is correctly expressed.
- Section 4 uses top-down lineage (source → staging → fact → analytics → BI) — canonical direction, no deduction.
- Section 2 table format is used throughout — preferred format per rubric.
- Metadata rows with `[USER INPUT REQUIRED]` in Section 1 (rows 3, 8, 12, 13) are present in the reference too and represent intentional scope boundaries for the agent-generated document. No auto-deduct applied as these are not "target system described instead of source" errors.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **Section 2 — Owner/contact per consumer — 2 points recoverable:** Add a team name or role for each of the 15 consumers. Even a "TBD / investigate" is better than blank.
2. **Section 2 — Access frequency/SLA per consumer — 1 point recoverable:** Add a frequency category (on-demand, daily refresh, nightly batch) per BI report and SQL view consumer.
3. **Section 1 — Scope boundaries — 1 point recoverable:** Add an explicit IN/OUT scope block to §1.1 and fill in metadata rows 3 and 8.

---

## Next Step

Score 95 ≥ 75: Proceed to `/project-transformation-rules` or `/product-transformation-rules`.
