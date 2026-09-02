---
task_id: TASK-AS-IS-001
product: Sales_Orders
participant_file: as-is-task2.md
reference_file: as-is-reference.md
checked_at: 2026-09-01T16:30:00Z
total_score: 95/100
grade: Excellent
identical_to_reference: true
---

# Task Check Report — as-is
_Sales_Orders | 2026-09-01_

> ⚠ **Warning:** Participant file (`as-is-task2.md`) is byte-for-byte identical to the reference file (`as-is-reference.md`). Score reflects content quality; no deduction applied for identity. Verify this is expected (e.g., document produced via the as-is agent pipeline) rather than a manual copy of the reference.

**File resolution log:**
- Participant file: `as-is-task2.md` — auto-resolved (`*task*.md` match; `as-is-reference.md` excluded as reference candidate)
- Reference file: `as-is-reference.md` — auto-resolved (highest-priority candidate)
- Product: `Sales_Orders` — derived from H1 heading `# As-Is Analysis — Sales_Orders`
- Scope file: not found (searched up to 3 levels from participant file directory)
- Sections matched by number: all six present (`## 1` through `## 6`)

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
- Product name (`Sales_Orders`) and domain (`Sales and Order Management`) stated explicitly. ✓
- Technology stack precisely identified: Microsoft SQL Server 2014, `wideworldimportersdw`, on-prem. ✓
- Volume and scale: ~12M rows/year on `Fact.Sale`, history baseline 2013-01-01. ✓
- Business context thorough: sales management, finance, supply chain, and regional management all named as stakeholder groups. ✓
- Calculated fields (row 11), filters (row 10), data sources (row 9), internal consumers (row 15), and storage (row 14) all populated with precise information. ✓

**What was missing or imprecise:**
- **Scope boundaries (−1 pt):** IN scope is implied by the component listing in §1.1, but no explicit OUT-of-scope statement exists anywhere in the section. The `Dimension.Payment Method` and `Dimension.Transaction Type` gap (no FK bindings) and `Fact.Purchase` references hint at what is out of scope, but they are never stated as such.

**Deferred fields `[DEFERRED]` — intentional, not penalised:**
- Row 3 — Process Type: `[USER INPUT REQUIRED]`. Other fields sufficiently cover business context; full points awarded for that criterion.
- Row 8 — Data Access and Restrictions: `[USER INPUT REQUIRED]`. Affects access scope only; scope boundaries criterion scored on the non-deferred content.
- Row 12 — Business DQ Rules: `[USER INPUT REQUIRED]`. DQ observations are present in Section 3; this row is supplementary.
- Row 13 — Technical DQ Rules: `[USER INPUT REQUIRED]`. Same reasoning as row 12.

**Improvement items:**
- [ ] Add an explicit IN/OUT scope block in §1.1 — e.g., "IN scope: `Fact.Sale`, `Fact.Order`, seven conformed dimensions, SSIS ETL pipeline. OUT OF scope: `Fact.Purchase`, GL schema, OLTP transactional tables."
- [ ] Fill in deferred metadata rows (3, 8, 12, 13) when information becomes available.

---

### Section 2 — Consumers and Use Cases (12/15)

**What was covered well:**
- All 15 consumers documented: 9 Power BI reports, 4 analytics views, 1 ETL procedure, 1 OLTP-direct report. ✓
- Consumption method named per consumer (Power BI direct, via view, SQL view, stored procedure call, OLTP-direct bypass). ✓
- Dependency type clear: all BI consumers are read-only; ETL procedure is an internal operational dependency. ✓

**What was missing or imprecise:**
- **Owner/contact (0/2):** No owner column present — no team name, role, email, "TBD", or "Unknown" for any consumer. Completely absent.
- **Frequency/SLA (2/3):** ETL pipeline correctly documented as nightly batch. BI reports and SQL views carry no frequency or SLA indicator (e.g., "on-demand", "daily scheduled refresh").

**Note:** No `product-scope.md` was found; consumer completeness was cross-checked against the reference only.

**Improvement items:**
- [ ] Add an `Owner / Contact` column — any value including "TBD" or "Unknown – investigate" satisfies the criterion.
- [ ] Add a `Frequency / SLA` column — "on-demand", "daily refresh", or "nightly batch" per consumer.

---

### Section 3 — Model Analytical Data Product (24/25)

**What was covered well:**
- All layers documented: 2 fact tables, 7 dimensions, 5 staging tables, 4 analytics views, 2 scalar UDFs. ✓
- Mermaid ER diagram with full cardinality (1:N, nullable `PickerKey`) — accepted as full substitute for a relationships table. ✓
- Key columns with data types in ER diagram; IDENTITY PK, SEQUENCE surrogate keys, columnstore index, `ValidFrom`/`ValidTo` SCD2 pattern all noted. ✓
- Structural anomalies called out: `Dimension.Payment Method` and `Dimension.Transaction Type` unbound to facts; `Sale_Staging` lacks `LineageKey` vs. `Order_Staging`; `dbo.OrderDetails` is a decommission candidate. ✓

**What was missing or imprecise:**
- **Known DQ issues (2/3):** Structural issues are well documented. Operational DQ indicators (NULL rates, orphaned FK row counts from a profiling run) are absent — likely requires live system access.

**Improvement items:**
- [ ] Add at least one operational DQ observation — e.g., "PickerKey is nullable; ~X% of `Fact.Order` rows have no picker assignment" or a known NULL rate from profiling.

---

### Section 4 — Column-Level Lineage (20/20)

**What was covered well:**
- Upstream sources fully named with system, database, and schema identifiers (including Azure Blob via PolyBase). ✓
- Ingestion methods documented per source: SSIS `dailyetlmain`, `GetSaleUpdates`, `GetOrderUpdates`, PolyBase. ✓
- 14-step transformation table covers orchestration → truncate → extract → key resolution → fact load → ETL metadata → analytics layer, with SQL logic and business meaning per step. ✓
- All 15 downstream consumers mapped to the tables they read (§4.5). ✓
- Lineage traceability: `Integration.Lineage` per-run audit, `Integration.ETL Cutoff` watermark, `Sequences.LineageKey`. ✓
- Known gaps flagged: undocumented 1.05 factor, OLTP-direct bypass, Azure Blob ad-hoc exclusion, no Power BI consumer for supply/year analytics views. ✓

No deductions. Full marks.

---

### Section 5 — Calculation Logic (10/10)

**What was covered well:**
- All seven calculations documented with business purpose, formula, input tables, SQL code, step-by-step walkthrough, and threshold table. ✓
- Sale vs. Order path differences explicitly distinguished for `Total Excluding Tax`, `Tax Amount`, `Total Including Tax`. ✓
- `ProfitMarginWithFactor` correctly identified as a view-layer calculation; undocumented 1.05 factor flagged. ✓
- Edge cases: NULL return without COALESCE guard in both UDF variants; ±0.01 rounding difference in Order path. ✓
- UDF duplication (`getTotalQuantitySold1` / `getTotalQuantitySold2`) identified and explained. ✓

No deductions. Full marks.

---

### Section 6 — Data Sources (10/10)

**What was covered well:**
- 19 source objects across three platforms with platform, system, schema, object type, description, and key fields all populated. ✓
- Connection methods: SSIS (daily batch), PolyBase (ad-hoc external table), OLTP-direct (`WebApi.SalesOrders`). ✓
- Refresh schedule: daily incremental, ad-hoc, and "not part of daily ETL" explicitly stated per source. ✓
- Source DQ characteristics: temporal tables with `_Archive` variants noted, OLTP-direct bypass documented, `LastEditedWhen` watermark approach noted. ✓
- Output tables (§6.2) fully listed with storage format and architectural notes. ✓

No deductions. Full marks.

---

## Approach Notes

- Section 3 uses a Mermaid `erDiagram` — accepted as full substitute for a relationships table; cardinality correctly expressed.
- Section 4 uses canonical top-down lineage direction — no deduction.
- Section 2 consumer table format — preferred format per rubric.
- Four `[USER INPUT REQUIRED]` metadata rows in Section 1 treated as intentional deferrals per updated skill rules; no auto-deduction applied.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **Section 2 — Owner/contact per consumer — 2 pts recoverable:** Add any identifier (team name, role, "TBD") per consumer row. Currently completely absent.
2. **Section 2 — Frequency/SLA per consumer — 1 pt recoverable:** Add frequency category per BI report and SQL view.
3. **Section 1 — Scope boundaries — 1 pt recoverable:** Add an explicit OUT-of-scope statement in §1.1.

---

## Next Step

Score 95 ≥ 75: Proceed to `/project-transformation-rules` or `/product-transformation-rules`.
