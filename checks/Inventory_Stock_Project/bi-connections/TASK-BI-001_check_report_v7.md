---
task_id: TASK-BI-001
skill: migvisor-task-checker-bi-connections
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/bi/bi_connections.md
reference_file: reference/answers/module_5/codebase/config/bi_connections.md
product: Purchase
generated: 2026-09-24
total_score: 96/100
grade: Excellent
---

# TASK-BI-001 Check Report — BI Connections
_Purchase | 2026-09-24_

## Score Summary

**BI Connections Score: 96/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 16 | 88/100 | 14.1 | ✓ |
| 1. Overview | 16 | 100/100 | 16.0 | ✓ |
| 2. Connection Details per Mart View | 18 | 100/100 | 18.0 | ✓ |
| 3. Connecting BI Tools | 18 | 100/100 | 18.0 | ✓ |
| 4. Known Issues and Workarounds | 16 | 97/100 | 15.5 | ✓ |
| 5. Access Provisioning | 16 | 100/100 | 16.0 | ✓ |
| **Subtotal** | | | **97.6** | |
| Auto-deducts | | | **−2** | |
| **Total** | | | **96/100** | |

**Grade: Excellent**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | (header block, CFG-012) | exact |
| 1. Overview | 1. Overview | exact |
| 2. Connection Details per Mart View | 2. Connection Details per Mart View | exact |
| 3. Connecting BI Tools | 3. Connecting BI Tools | exact |
| 4. Known Issues and Workarounds | 4. Known Issues and Workarounds | exact |
| 5. Access Provisioning | 5. Access Provisioning | exact |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No per-view attribute tables anywhere | −4 pts | No — attribute tables present for both views |
| No connection string block anywhere | −4 pts | No — connection string block present in Section 3 |
| No known issues section anywhere | −4 pts | No — known issues table present in Section 4 |
| No access provisioning contact info | −3 pts | No — contact email `data-engineering@company.com` present |
| Missing H2 section | −5 pts each (max −15) | No — all 5 reference sections matched |
| GRANT SQL placeholder only | −2 pts | N/A — no GRANT SQL block |
| Connection string uses wrong catalog | −2 pts | No — trainee correctly uses `inventory_stock` catalog |
| Only one BI report documented | −8 pts | No — both `v_purchase_by_supplier` and `v_purchase_per_stock_item` documented |
| Cross-product dependency not documented | −4 pts | N/A — reference file does not document this either |
| Geography CLR decomposition not documented | −3 pts | N/A — reference file does not document this |
| DateKey type conversion not documented | −3 pts | N/A — reference file does not document this |

**Note:** −2 pts applied as a conservative adjustment reflecting that the header block lacks an explicit author or generated date field (both reference and participant omit this, but the rubric criterion exists).

**Total auto-deducts: −2**

---

## Section Feedback

### Header Metadata — 88/100 (weight 16 → 14 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Guide/product name in H1 | 35% | 100% | "CFG-012: BI Tool Reconnection Guide" — clear and specific |
| Task ID / traceability tag present | 30% | 80% | "CFG-012" is a valid config reference code; not TASK-* format but meaningful |
| Catalog / schema reference | 20% | 100% | "inventory_stock.mart" named in Overview section header paragraph |
| Author / generated date present | 15% | 0% | No author or generated date present (reference also lacks this) |

**Strengths:**
- H1 title is specific and matches the CFG task numbering convention.
- CFG-012 provides clear traceability.

**Gaps:**
- No author name or generated date in the header block.

**Improvement items:**
- [ ] Add `_Generated: YYYY-MM-DD_` or author attribution before the first `##` heading.

---

### 1. Overview — 100/100 (weight 16 → 16 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 100% | Purpose stated, catalog (`inventory_stock.mart`) named, audience identified |
| Structure | 10% | 100% | H2 heading, intro paragraph present |

**Strengths:**
- Overview paragraph is concise and clearly states the guide's purpose and the target catalog schema.

---

### 2. Connection Details per Mart View — 100/100 (weight 18 → 18 pts)

**Criteria scored:** Content (75%), Attribute Table (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 100% | Both views fully documented with SQL samples |
| Attribute Table | 15% | 100% | Both views have complete attribute tables with all 5 fields |
| Structure | 10% | 100% | H3 subsections, code-fenced SQL blocks |

**Content completeness:**
- Topics covered: 2/2 views (v_purchase_by_supplier MV; v_purchase_per_stock_item Standard View)
- Details specific and complete: UC paths, object types, bi-service-principal, minimum privilege, refresh/real-time flag
- Section intro paragraph present: Yes (subsection headings serve as context)

**Attribute tables:**
- Both present: Yes (35%)
- Required rows covered: 5/5 per view (UC path, Object type, Service principal, Minimum privilege, Refresh/Real-time) (35%)
- Values are concrete, not placeholder: Yes — `inventory_stock.mart.*`, `bi-service-principal`, `SELECT` (30%)

**Bonus:** Trainee includes an additional aggregate SQL sample for `v_purchase_by_supplier` (SELECT supplier_name with SUM) — exceeds the reference.

**Strengths:**
- Both mart views documented with complete attribute tables.
- Participant uses their own `inventory_stock` catalog correctly throughout.
- Additional aggregate query sample adds practical value.

---

### 3. Connecting BI Tools — 100/100 (weight 18 → 18 pts)

**Criteria scored:** Content (55%), Connection String (20%), BI Tool Steps (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100% | All connection parameters covered; BI tool steps present |
| Connection String | 20% | 100% | All 5 fields present; uses `inventory_stock` catalog |
| BI Tool Steps | 15% | 100% | 4-step numbered list; covers Power BI and Tableau |
| Structure | 10% | 100% | H2/H3 headings, fenced code block for connection string |

**Connection string:**
- Block present: Yes (code block, not fenced with language tag but clearly formatted)
- Required fields: 5/5 (Server hostname, HTTP path, Authentication, Catalog, Schema)
- Uses participant catalog (`inventory_stock`): Yes

**BI tool steps:**
- Steps present: Yes (numbered 1–4)
- Tools covered: Power BI and Tableau (2 tools matching reference)
- Steps actionable: Yes (references specific UI elements: "Select Azure Databricks as the connector")

---

### 4. Known Issues and Workarounds — 97/100 (weight 16 → 15.5 pts)

**Criteria scored:** Content (70%), Issues Table (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 100% | Both reference issues covered; trainee adds explanatory note |
| Issues Table | 20% | 100% | Table present; 2/2 issues covered; concrete workarounds |
| Structure | 10% | 85% | H2 heading present; no explicit intro paragraph before the table |

**Issues table:**
- Table present: Yes (Markdown table)
- Issues covered: 2/2 (stale MV data; ACCESS DENIED on mart view)
- Each entry has concrete workaround: Yes — both entries provide specific steps

**Bonus:** Trainee adds a cross-product note explaining that `bronze.lineage_run` corresponds to `stg.lineage` in the reference pattern — shows awareness of naming convention differences.

**Gaps:**
- No brief intro sentence before the table explaining the section's purpose.

**Improvement items:**
- [ ] Add one introductory sentence before the issues table (e.g., "The following issues have been observed during BI reconnection testing.").

---

### 5. Access Provisioning — 100/100 (weight 16 → 16 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 100% | Contact info, onboarding procedures, grant targets all present |
| Structure | 10% | 100% | H2 heading, bullet list |

**Strengths:**
- Concrete email address (`data-engineering@company.com`) present.
- Three actionable provisioning scenarios listed (onboard new SP, grant purchase-analysts, request manual refresh).

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | No author/generated date in header block | Header Metadata | +2 pts |
| 2 | No intro paragraph before Known Issues table | Known Issues | +1 pt |

---

## Priority Actions

1. **Add a generated date or author to the header block** — Insert `_Generated: YYYY-MM-DD_` before the first `##` heading. Worth up to **+2 pts**.
2. **Add one intro sentence to the Known Issues section** — Brief sentence before the table explaining the section's scope. Worth up to **+1 pt**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing per-view attribute tables, connection string, or known issues absent |
| 0–44 | Incomplete | Major sections absent or BI connection details not documented |

---

_Report generated by skill migvisor-task-checker-bi-connections on 2026-09-24_
