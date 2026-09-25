---
task_id: TASK-BI-001
skill: task-checker-bi-connections
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/bi/bi_connections.md
reference_file: reference/answers/module_5/codebase/config/bi_connections.md
product: Purchase (inventory_stock)
generated: 2026-09-25
total_score: 88/100
grade: Good
---

# TASK-BI-001 Check Report

**Product:** Purchase (inventory_stock)
**Reference:** Purchase (globalpurchase)
**Participant file:** `Inventory_Stock_Project/products/Purchase/current/codebase/docs/bi/bi_connections.md`
**Reference file:** `reference/answers/module_5/codebase/config/bi_connections.md`
**Generated:** 2026-09-25

---

## Score Summary

**BI Connections Score: 88/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 16 | 85/100 | 13.60 | ✓ |
| 1. Overview | Overview | 16 | 100/100 | 16.00 | ✓ |
| 2. Connection Details per Mart View | Connection Details per Mart View | 18 | 86/100 | 15.48 | ✓ |
| 3. Connecting BI Tools | Connecting BI Tools | 18 | 89/100 | 16.02 | ✓ |
| 4. Known Issues and Workarounds | Known Issues and Workarounds | 16 | 87/100 | 13.92 | ✓ |
| 5. Access Provisioning | Access Provisioning | 16 | 84/100 | 13.44 | ✓ |
| **Subtotal** | | | | **88.46** | |
| Auto-deducts | | | | **0** | |
| **Total** | | | | **88/100** | |

**Grade: Good**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → Connection Details (18 pts) and Connecting BI Tools (18 pts) receive +2 each from complexity ranking.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| (header block) | (header block) | exact |
| 1. Overview | 1. Overview | exact |
| 2. Connection Details per Mart View | 2. Connection Details per Mart View | exact |
| 3. Connecting BI Tools | 3. Connecting BI Tools | exact |
| 4. Known Issues and Workarounds | 4. Known Issues and Workarounds | exact |
| 5. Access Provisioning | 5. Access Provisioning | exact |

**Cross-product note:** `globalpurchase` → `inventory_stock`; all catalog/schema path substitutions are correct and non-penalised.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No per-view attribute tables anywhere | −4 pts | No — attribute tables present in Section 2 |
| No connection string block anywhere | −4 pts | No — connection string block present in Section 3 |
| No known issues section anywhere | −4 pts | No — Section 4 present with issues table |
| No access provisioning contact info | −3 pts | No — email address present in Section 5 |
| Missing H2 section | −5 pts each (max −15) | No — all 5 H2 sections present |
| GRANT SQL placeholder only | −2 pts | N/A — no GRANT SQL block in document |
| Connection string uses wrong catalog | −2 pts | No — uses inventory_stock correctly |

**Total auto-deducts: 0 pts**

---

## Section Feedback

### Header Metadata — 85/100 (weight 16 → 13.60 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Guide/product name in H1 | 35% | 100 | "CFG-012: BI Tool Reconnection Guide" ✓ |
| Task ID / traceability tag | 30% | 100 | CFG-012 present ✓ |
| Catalog / schema reference | 20% | 100 | `inventory_stock.mart` mentioned in header ✓ |
| Author / generated date | 15% | 0 | Not present (reference also omits this) |

**Strengths:**
- Clear document title with CFG task ID
- Catalog schema path correctly stated

**Gaps:**
- No author name or generated date in header block (minor — reference also omits this)

**Improvement items:**
- [ ] Optionally add `Generated: <date>` or `Author: <team>` before first `##`

---

### 1. Overview — 100/100 (weight 16 → 16.00 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 100 | Purpose, catalog path, target audience all stated ✓ |
| Structure | 10% | 100 | H2 present, paragraph format appropriate ✓ |

**Strengths:**
- Concise, accurate overview stating catalog path `inventory_stock.mart` ✓
- Explains the reconnection context clearly

---

### 2. Connection Details per Mart View — 86/100 (weight 18 → 15.48 pts)

**Criteria scored:** Content completeness (75%), Attribute Table (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 85 | 2/2 views documented; no section intro paragraph |
| Attribute Table | 15% | 100 | 5/5 attributes, concrete values ✓ |
| Structure | 10% | 75 | H2 + H3s present; no section intro paragraph before first H3 |

**Content completeness (85/100):**
- Views documented: 2/2 (v_purchase_by_supplier, v_purchase_per_stock_item) ✓
- All attribute rows present: UC path, Object type, Service principal, Minimum privilege, Refresh/Real-time ✓
- Participant adds an extra aggregate sample query for v_purchase_by_supplier (exceeds reference) ✓
- Section intro paragraph: Missing (jumps directly to H3 subsections — consistent with reference pattern)

**Attribute Table (100/100):**
- Table present ✓
- All 5 attribute rows covered ✓
- Concrete values (not placeholders) ✓

**Structure (75/100):**
- H2 + H3 present ✓
- No section intro paragraph (0%) — same as reference
- Appropriate table format ✓
- SQL in fenced code blocks ✓

**Strengths:**
- Both mart views fully documented with all required attributes
- Extra aggregate query for supplier view shows thoroughness

**Gaps:**
- No introductory paragraph before the H3 subsections (consistent with reference)

---

### 3. Connecting BI Tools — 89/100 (weight 18 → 16.02 pts)

**Criteria scored:** Content completeness (55%), Connection String (20%), BI Tool Steps (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 85 | Both connection string and BI steps present; no section intro |
| Connection String | 20% | 100 | All 5 fields, inventory_stock catalog ✓ |
| BI Tool Steps | 15% | 100 | Power BI / Tableau steps, actionable ✓ |
| Structure | 10% | 75 | H2 + sub-headings; no section intro paragraph |

**Content completeness (85/100):**
- Connection string + BI steps: both present ✓
- All 5 fields: Server hostname, HTTP path, Authentication, Catalog, Schema ✓
- Numbered steps referencing specific UI elements ✓
- Intro paragraph: Missing (goes straight to sub-section headings)

**Connection String (100/100):**
- Block present ✓, all 5 fields ✓, uses `inventory_stock` ✓

**BI Tool Steps (100/100):**
- Power BI / Tableau steps present ✓
- Actionable (references Azure Databricks connector, specific fields) ✓

**Strengths:**
- Complete connection details with all 5 required fields
- Clear 4-step BI connection procedure

**Gaps:**
- Authentication note includes "or Personal Access Token" alternative — OAuth-first is correct, PAT fallback is acceptable

---

### 4. Known Issues and Workarounds — 87/100 (weight 16 → 13.92 pts)

**Criteria scored:** Content completeness (70%), Issues Table (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 85 | 2/2 issues; concrete workarounds; no section intro |
| Issues Table | 20% | 100 | Table present, 2 issues, specific workarounds ✓ |
| Structure | 10% | 75 | H2 present; no intro paragraph |

**Content completeness (85/100):**
- Issues covered: 2/2 (stale MV data, ACCESS DENIED) ✓
- Workarounds are specific (check lineage_run, verify GRANT-004) ✓
- Extra value: participant notes the naming convention difference (`bronze.lineage_run` vs `stg.lineage`) — shows awareness of cross-product catalog differences ✓
- Section intro: Missing

**Issues Table (100/100):**
- Table present ✓, 2/2 issues covered ✓, concrete workarounds ✓

**Strengths:**
- Cross-product naming note in the stale data workaround is an excellent addition
- Both issues have specific, actionable workarounds

---

### 5. Access Provisioning — 84/100 (weight 16 → 13.44 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 85 | 3/3 provisioning topics; email present; no section intro |
| Structure | 10% | 75 | H2 present; no intro paragraph before bullet list |

**Content completeness (85/100):**
- Contact email: `data-engineering@company.com` ✓
- Three provisioning topics: onboard new SPs, grant analysts role, request manual refresh ✓
- Intro paragraph: Missing (jumps to "Contact the Data Engineering team at...")

**Strengths:**
- All three provisioning actions documented with specific contact

**Gaps:**
- The "Contact the Data Engineering team at..." line could be considered a partial intro, but a preceding context sentence would strengthen the section

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add section intro paragraph to Connection Details, Connecting BI Tools, Known Issues, and Access Provisioning | Multiple | +3 pts |
| 2 | Add author/generated date to header block | Header | +2 pts |
| 3 | Clarify authentication preference (OAuth primary, PAT fallback) with note on service principal vs user context | Connecting BI Tools | +1 pt |

---

## Priority Actions

1. **Add brief intro paragraphs** to sections 2, 3, 4, and 5 (one sentence each explaining the section's purpose) — worth up to **+3 pts**.
2. **Add `Generated:` or `Author:` metadata** to the header block before the first `##` — worth up to **+2 pts**.
3. **Clarify OAuth authentication** — add a note that the service principal uses OAuth 2.0 client credentials flow, not user-delegated auth — worth up to **+1 pt**.

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

*Report generated by skill 30-migvisor-task-checker-bi-connections on 2026-09-25*
