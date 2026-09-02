---
task_id: TASK-AS-IS-001
product: Sales_Orders
participant_file: as-is-task2.md
reference_file: as-is-reference.md
checked_at: 2026-09-01T16:10:00Z
total_score: 95/100
grade: Excellent
identical_to_reference: true
---

# Task Check Report — as-is
_Sales_Orders | 2026-09-01_

> ⚠ **Warning:** Participant file (`as-is-task2.md`) is byte-for-byte identical to the reference file (`as-is-reference.md`). Score reflects content quality; no deduction applied for identity. Verify this is expected (e.g., document produced via the as-is agent pipeline) rather than a manual copy of the reference.

**File resolution log:**
- Participant file: `as-is-task2.md` — supplied implicitly (only candidate in workspace)
- Reference file: `as-is-reference.md` — auto-resolved (highest-priority candidate)
- Product: `Sales_Orders` — derived from H1 heading `# As-Is Analysis — Sales_Orders`
- Scope file: not found (searched up to 3 levels from `as-is-task2.md`)
- Sections matched: `## 1` through `## 6` — all six present in both files

---

## Score Summary

| Section | Max | Score | Status |
|---|---|---|---|
| 1. Analytical Data Product Description | 20 | 19 | ✓ |
| 2. Consumers and Use Cases | 15 | 12 | ⚠ |
| 3. Model Analytical Data Product | 25 | 24 | ✓ |
| 4. Column-Level Lineage | 20 | 20 | ✓ |
| 5. Calculation Logic | 10 | 10 | ✓ |
| 6. Data Sources | 10 | 10 | ✓ |
| **Total** | **100** | **95** | |

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Section 1 — Analytical Data Product Description (19/20)

**What was covered well:**
- Product name (`Sales_Orders`) and domain (`Sales and Order Management`) stated explicitly.
- Technology stack precisely identified: Microsoft SQL Server 2014, `wideworldimportersdw`, on-prem.
- Volume and scale excellent: ~12M rows/year on `Fact.Sale`, history baseline 2013-01-01.
- Business context and stakeholders thorough: sales management, finance, supply chain, regional management all named.
- Calculated fields (row 11), filters (row 10), and data sources (row 9) fully described.

**What was missing or imprecise:**
- Scope boundaries (criterion: IN scope and OUT OF scope explicitly listed) are implied by the product narrative and component listing but never stated as an explicit IN/OUT block. −1 pt.

**Deferred fields `[DEFERRED]`:**
- Row 3 — Process Type: `[USER INPUT REQUIRED]` — intentional deferral, not evaluated
- Row 8 — Data Access and Restrictions: `[USER INPUT REQUIRED]` — intentional deferral, not evaluated
- Row 12 — Business DQ Rules: `[USER INPUT REQUIRED]` — intentional deferral, not evaluated
- Row 13 — Technical DQ Rules: `[USER INPUT REQUIRED]` — intentional deferral, not evaluated

**Improvement items:**
- [ ] Add an explicit IN-scope / OUT-of-scope block in §1.1 — e.g., "IN scope: `Fact.Sale`, `Fact.Order`, seven dimensions, SSIS ETL pipeline. OUT OF scope: `Fact.Purchase`, GL schema, OLTP transaction tables."
- [ ] Fill in the four deferred metadata rows when information becomes available.

---

### Section 2 — Consumers and Use Cases (12/15)

**What was covered well:**
- All 15 consumers listed and cross-referenced: 9 Power BI reports, 4 analytics views, 1 ETL procedure, 1 OLTP-direct report.
- Consumption method named precisely per consumer (Power BI direct, via view, SQL view, stored procedure, OLTP-direct bypass).
- Dependency type clear: all BI consumers are read-only; ETL procedure is an internal operational dependency.

**What was missing or imprecise:**
- **Owner/contact (0/2):** The consumer table has no owner column — no team name, role, email, "TBD", or "Unknown" for any entry. Completely absent → 0 pts.
- **Frequency/SLA (2/3):** The ETL pipeline documents "nightly batch". BI reports and SQL views have no stated SLA or access frequency (e.g., "on-demand interactive", "daily scheduled refresh"). −1 pt.

**Improvement items:**
- [ ] Add an `Owner / Contact` column to the consumer table — even "TBD" or "Unknown – investigate" per row satisfies the criterion.
- [ ] Add a `Frequency / SLA` column — e.g., "on-demand", "daily refresh", "nightly batch" per consumer.

---

### Section 3 — Model Analytical Data Product (24/25)

**What was covered well:**
- All primary entities documented across all layers: 2 facts, 7 dimensions, 5 staging tables, 4 analytics views, 2 scalar UDFs.
- Mermaid ER diagram present with full cardinality (1:N, nullable PickerKey noted) — accepted as full substitute for relationships table per rubric.
- Key columns with data types listed in ER diagram; IDENTITY PK, SEQUENCE surrogate keys, columnstore index, `ValidFrom`/`ValidTo` SCD2 pattern all noted.
- Structural anomalies called out: `Dimension.Payment Method` and `Dimension.Transaction Type` unbound to facts; `Sale_Staging` lacks LineageKey vs. `Order_Staging`; `dbo.OrderDetails` is a decommission candidate.

**What was missing or imprecise:**
- **Known DQ issues (2/3):** Structural and schema issues are well documented. Operational DQ indicators (NULL rates, orphaned FK row counts, known data inconsistencies from production) are not present — likely requires live system access. −1 pt.

**Improvement items:**
- [ ] Add at least one operational DQ observation: e.g., "PickerKey is nullable — approximately X% of `Fact.Order` rows have no picker assignment" or known NULL rates from a profiling run.

---

### Section 4 — Column-Level Lineage (20/20)

**What was covered well:**
- Upstream sources fully named with system, database, and schema identifiers.
- Ingestion methods documented per source: SSIS `dailyetlmain`, `GetSaleUpdates`, `GetOrderUpdates`, PolyBase for Azure Blob.
- 14-step transformation table covers the full ETL lifecycle: orchestration → truncate → extract → key resolution → fact load → ETL metadata → analytics layer, with SQL logic and business meaning per step.
- All 15 downstream consumers mapped to the tables they read (Section 4.5).
- Lineage traceability fully documented: `Integration.Lineage` per-run audit, `Integration.ETL Cutoff` watermark, `Sequences.LineageKey`.
- Known gaps explicitly flagged: undocumented 1.05 factor, OLTP-direct bypass, Azure Blob ad-hoc exclusion, no Power BI consumer for supply/year analytics views.

No deductions. Full marks.

---

### Section 5 — Calculation Logic (10/10)

**What was covered well:**
- All seven calculations documented with business purpose, mathematical formula, input tables/columns, SQL code, step-by-step walkthrough, and threshold categorization.
- Sale vs. Order path differences explicitly distinguished for `Total Excluding Tax`, `Tax Amount`, `Total Including Tax`.
- `ProfitMarginWithFactor` correctly identified as a view-layer calculation; undocumented 1.05 factor flagged as a business-rule gap.
- Edge cases documented: NULL return without COALESCE guard in UDF variants; ±0.01 rounding difference from independently rounded Order components.
- UDF duplication (`getTotalQuantitySold1` / `getTotalQuantitySold2`) identified and explained.

No deductions. Full marks.

---

### Section 6 — Data Sources (10/10)

**What was covered well:**
- 19 source objects listed across three platforms with platform, system, schema, object type, description, and key fields.
- Connection methods documented: SSIS (daily batch), PolyBase (ad-hoc external table), OLTP-direct (`WebApi.SalesOrders`).
- Refresh schedule stated per source: daily incremental, ad-hoc, and "not part of daily ETL" explicitly called out for Azure Blob.
- Source DQ characteristics present: temporal tables with `_Archive` variants, OLTP-direct bypass noted, `LastEditedWhen` watermark approach documented.
- Output tables (§6.2) comprehensively listed with object type, storage format, and architectural notes.

No deductions. Full marks.

---

## Approach Notes

- Section 3 uses a Mermaid `erDiagram` block — accepted as full substitute for a relationships table. Cardinality correctly expressed.
- Section 4 uses canonical top-down lineage (source → staging → fact → analytics → BI) — no deduction.
- Section 2 consumer table format used throughout — preferred format per rubric.
- Four metadata rows with `[USER INPUT REQUIRED]` in Section 1 treated as intentional deferrals (not scored as missing content).

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **Section 2 — Owner/contact per consumer — 2 points recoverable:** Add any identifier (team name, role, "TBD") per consumer row. Currently completely absent.
2. **Section 2 — Frequency/SLA per consumer — 1 point recoverable:** Add frequency category (on-demand, daily refresh, nightly batch) per BI report and SQL view.
3. **Section 1 — Scope boundaries — 1 point recoverable:** Add an explicit IN/OUT scope block in §1.1.

---

## Next Step

Score 95 ≥ 75: Proceed to `/project-transformation-rules` or `/product-transformation-rules`.
