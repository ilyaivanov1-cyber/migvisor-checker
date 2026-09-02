---
task_id: TASK-AS-IS-001
product: Sales_Orders
participant_file: as-is-task2.md
reference_file: as-is-reference.md
checked_at: 2026-09-01T18:30:00Z
sections_evaluated: 6
total_score: 94/100
grade: Excellent
identical_to_reference: true
---

# Task Check Report — as-is
_Sales_Orders | 2026-09-01_

> ⚠ **Warning:** Participant file (`as-is-task2.md`) is byte-for-byte identical to the reference file (`as-is-reference.md`). Score reflects content quality against the generic rubric; no deduction applied for identity. Verify this is expected (e.g., agent-generated output) rather than a manual copy.

**File resolution log:**
- Participant file: `as-is-task2.md` — supplied explicitly by user
- Reference file: `as-is-reference.md` — auto-resolved (highest-priority candidate)
- Product: `Sales_Orders` — derived from H1 heading `# As-Is Analysis — Sales_Orders`
- Scope file: not found (searched up to 3 levels from participant file directory)
- Sections in reference: 6 (`## 1` through `## 6`) | Sections in participant: 6 (all matched)
- Point weights: auto-calculated — floor(100/6)=16 base; +1 distributed to 4 longest sections

---

## Score Summary

| Section | Weight | Score | Status |
|---|---|---|---|
| 1. Analytical Data Product Description | 16 | 15 | ✓ |
| 2. Consumers and Use Cases | 16 | 12 | ⚠ |
| 3. Model Analytical Data Product | 17 | 16 | ✓ |
| 4. Column-Level Lineage | 17 | 17 | ✓ |
| 5. Calculation Logic | 17 | 17 | ✓ |
| 6. Data Sources | 17 | 17 | ✓ |
| **Total** | **100** | **94** | |

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Section 1 — Analytical Data Product Description (15/16)

**Coverage (6/6):** All key topics present — product name, domain, technology stack, business value, key components (facts, dimensions, staging, analytics, UDFs, BI reports), stakeholders, volume/scale indicators, data sources, filters, and calculated fields all documented.

**Specificity (4/4):** Excellent. SQL Server 2014 version named, `wideworldimportersdw` database identified, specific table and procedure names used throughout, precise volume (~12M rows/year, 2013-01-01 baseline).

**Technical accuracy (3/3):** Source system (`wideworldimportersdw`) correctly described, not the target/migration platform.

**Issues/gaps flagged (1/2):** Deferred metadata rows are marked `[USER INPUT REQUIRED]` which signals their pending state. However, no explicit OUT-of-scope statement exists — the boundary of what this product does NOT cover is never stated.

**Structure (1/1):** Two clear subsections — §1.1 Definition (narrative) and §1.2 Metadata Table (structured). Consistent with reference.

**Deferred fields `[DEFERRED]`:**
- Row 3 — Process Type: `[USER INPUT REQUIRED]` — other fields sufficiently cover business context; no penalty.
- Row 8 — Data Access and Restrictions: `[USER INPUT REQUIRED]` — access scope pending.
- Row 12 — Business DQ Rules: `[USER INPUT REQUIRED]` — DQ observations present in Section 3; supplementary here.
- Row 13 — Technical DQ Rules: `[USER INPUT REQUIRED]` — same as row 12.

**Improvement items:**
- [ ] Add an explicit OUT-of-scope statement in §1.1 — e.g., "OUT OF scope: `Fact.Purchase`, GL schema, OLTP transactional tables, Finance reporting."
- [ ] Fill in deferred metadata rows (3, 8, 12, 13) when information becomes available.

---

### Section 2 — Consumers and Use Cases (12/16)

**Coverage (4/6):** 15 consumers documented with use cases, business questions answered, and consumption method — 3 of 5 expected attribute types present. Owner/contact column and access frequency/SLA column are completely absent across all 15 entries, reducing coverage to ~60%.

**Specificity (4/4):** Consumer names are specific, consumption methods precisely named (Power BI direct, via `Analytics.OrderDetails`, OLTP-direct via `WebApi.SalesOrders`, stored procedure call). Named view and report paths used.

**Technical accuracy (3/3):** Consumers correctly identified; consumption relationships accurate; OLTP-direct bypass correctly distinguished from DW consumers.

**Issues/gaps flagged (0/2):** No consumer-side gaps flagged — missing SLA commitments, undocumented consumer owners, or potential zombie consumers are not called out anywhere in the section.

**Structure (1/1):** Clean table format with consistent columns throughout.

**Improvement items:**
- [ ] Add `Owner / Contact` column — team name, role, email, or "TBD" per row. Currently completely absent.
- [ ] Add `Frequency / SLA` column — "on-demand", "daily scheduled refresh", "nightly batch" per consumer.
- [ ] Flag at least one known consumer-side gap or SLA uncertainty in a note below the table.

---

### Section 3 — Model Analytical Data Product (16/17)

**Coverage (7/7):** All layers documented — 2 fact tables, 7 dimensions, 5 staging tables + migrate procedures, 4 analytics views, 2 scalar UDFs. Both ER diagram and textual description present and consistent.

**Specificity (4/4):** Column names, data types, PK/FK markers, index types (columnstore, B-tree), SCD2 pattern (ValidFrom/ValidTo), SEQUENCE-generated keys, geography column — all named explicitly.

**Technical accuracy (3/3):** Source system (SQL Server `wideworldimportersdw`) tables described. No target-system substitution detected.

**Issues/gaps flagged (1/2):** Structural anomalies called out: `Sale_Staging` lacks LineageKey vs. `Order_Staging`; `Dimension.Payment Method` and `Dimension.Transaction Type` have no FK bindings to either fact; `dbo.OrderDetails` flagged as decommission candidate. Operational DQ indicators (NULL rates, orphaned FK counts from profiling) absent.

**Structure (1/1):** §3.1 ER Diagram (Mermaid) + §3.2 Textual Description (layered table). Mermaid diagram accepted as full substitute for relationships table — cardinality correctly expressed.

**Improvement items:**
- [ ] Add at least one operational DQ observation — e.g., "PickerKey nullable in `Fact.Order`; estimated X% of rows have no picker assignment" from a profiling run.

---

### Section 4 — Column-Level Lineage (17/17)

**Coverage (7/7):** Complete pipeline documented end-to-end: OLTP sources → extract procedures → staging → SCD2 key resolution → fact load → ETL metadata → analytics layer → BI reports.

**Specificity (4/4):** SQL logic snippets per step, specific procedure names (`GetSaleUpdates`, `MigrateStagedSaleData`), column-level source/target/intermediate mapping, SCD2 range lookup logic, watermark SQL shown.

**Technical accuracy (3/3):** Top-down flow direction correct. OLTP-direct report correctly distinguished as bypassing the DW ETL pipeline.

**Issues/gaps flagged (2/2):** Undocumented 1.05 business factor flagged, OLTP-direct bypass noted as a lineage gap, Azure Blob ad-hoc exclusion stated, no Power BI consumer for `v_OrderToSupplyAnalytics` and `v_OrderToYearAnalytics`.

**Structure (1/1):** Five clearly delineated subsections (§4.1–§4.5).

No deductions. Full marks.

---

### Section 5 — Calculation Logic (17/17)

**Coverage (7/7):** All seven calculations documented — Total Excluding Tax, Tax Amount, Total Including Tax, Total Dry Items, Total Chiller Items, ProfitMarginWithFactor, GetTotalQuantitySold UDF.

**Specificity (4/4):** Exact SQL expressions shown, Sale vs. Order path differences explicitly distinguished, UDF parameter names noted.

**Technical accuracy (3/3):** All calculations reference the correct source layer. Sale and Order monetary differences accurately described.

**Issues/gaps flagged (2/2):** Undocumented 1.05 uplift factor flagged; NULL return without COALESCE guard noted; ±0.01 rounding discrepancy documented.

**Structure (1/1):** Seven subsections (§5.1–§5.7) each with identical internal structure.

No deductions. Full marks.

---

### Section 6 — Data Sources (17/17)

**Coverage (7/7):** 19 source objects across three platforms + 15 output objects. Platform, system, schema, object type, description, and key fields populated for each entry.

**Specificity (4/4):** Connection methods named per source (SSIS, PolyBase, OLTP-direct), temporal table variants noted, Azure Blob URL and format documented.

**Technical accuracy (3/3):** Input sources (§6.1) and output targets (§6.2) correctly separated.

**Issues/gaps flagged (2/2):** Azure Blob PolyBase excluded from daily ETL marked ad-hoc. OLTP-direct bypass documented. `Sale_Staging` LineageKey asymmetry noted.

**Structure (1/1):** §6.1 Input Source Tables + §6.2 Output Tables. Consistent column layout.

No deductions. Full marks.

---

## Approach Notes

- Section 3 uses a Mermaid `erDiagram` — accepted as full substitute for a relationships table.
- Section 4 uses canonical top-down lineage direction — no deduction.
- Four `[USER INPUT REQUIRED]` metadata rows in Section 1 treated as intentional deferrals; no auto-deduction applied.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **Section 2 — Coverage: owner/contact and frequency/SLA absent — 4 pts recoverable:** Adding both columns brings Section 2 coverage from 4/6 to 6/6.
2. **Section 2 — Issues/gaps flagged — 2 pts recoverable:** Add a note flagging at least one known consumer-side uncertainty.
3. **Section 1 — Issues/gaps flagged — 1 pt recoverable:** Add an explicit OUT-of-scope statement.

---

## Next Step

Score 94 ≥ 75: Proceed to `/project-transformation-rules` or `/product-transformation-rules`.
