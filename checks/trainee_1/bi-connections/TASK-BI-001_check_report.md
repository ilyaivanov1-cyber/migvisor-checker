---
task_id: TASK-BI-001
skill: task-checker-bi-connections
participant_file: trainees/trainee_1/bi_connections.md
reference_file: reference/bi_connections.md
product: Sales_Orders
generated: 2026-09-03
total_score: 13/100
grade: Incomplete
---

# TASK-BI-001 Check Report

**Product:** Sales_Orders  
**Reference:** Purchase (globalpurchase)  
**Participant file:** `trainees/trainee_1/bi_connections.md`  
**Reference file:** `reference/bi_connections.md`  
**Generated:** 2026-09-03

---

## Score Summary

**BI Connections Score: 13/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 16 | 65/100 | 10.4 | ⚠ |
| 1. Overview | ## 1. Overview | 16 | 0/100 | 0.0 | ✗ |
| 2. Connection Details per Mart View | ## Connection Details per Mart View | 18 | 41/100 | 7.4 | ⚠ |
| 3. Connecting BI Tools | ## Connecting BI Tools | 18 | 64/100 | 11.5 | ⚠ |
| 4. Known Issues and Workarounds | ## Known Issues and Workarounds | 16 | 0/100 | 0.0 | ✗ |
| 5. Access Provisioning | ## Access Provisioning | 16 | 43/100 | 6.9 | ⚠ |
| **Subtotal** | | | | **36.2** | |
| Auto-deducts | | | | **−23** | |
| **Total** | | | | **13/100** | |

**Grade: Incomplete**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4. Top 2 sections (Connection Details, Connecting BI Tools) each receive +2 → 18 pts each.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | Lines 1–2 before first `##` | Direct match |
| 1. Overview | [MISSING] | Missing |
| 2. Connection Details per Mart View | `## BI report connections (IFR-BI-001..009)` | Partial — report manifest (not attribute tables) |
| 3. Connecting BI Tools | `## SQL Warehouse connection string` | Partial — connection string present, BI tool steps absent |
| 4. Known Issues and Workarounds | [MISSING] | Missing |
| 5. Access Provisioning | `## Grant targets — [PENDING: CX-P05]` | Partial — GRANT SQL with placeholder only |

**Extra participant section (unscored):** `## Performance guidance (NFR-PERF ≤ 5s p95)` — no reference equivalent.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No per-view attribute tables anywhere | −4 pts | **Yes** — participant has a report manifest table (Report/Primary asset/Mode/Notes) but no per-view config table with UC path, Object type, Service principal, Minimum privilege, or Refresh fields |
| No connection string block anywhere | −4 pts | **No** — `## SQL Warehouse connection string` code block present with all 5 required fields |
| No known issues section anywhere | −4 pts | **Yes** — no Known Issues, Workarounds, or Troubleshooting section anywhere in the document |
| No access provisioning contact info | −3 pts | **Yes** — no email address, team name, or contact channel anywhere in the document |
| Missing H2 section | −5 pts each (max −15) | **Yes** — `## 1. Overview` (−5), `## 4. Known Issues and Workarounds` (−5) → **−10 pts total** |
| GRANT SQL placeholder only | −2 pts | **Yes** — `{{UC_ROLE_BI_SERVICE_PRINCIPAL}}` is an unresolved template variable; comment confirms TODO |
| Connection string uses wrong catalog | −2 pts | **No** — Catalog = `globalsales`, Schema = `mart` (participant's own, correct) |

**Total auto-deducts: −23 pts**

---

## Section Feedback

### Header Metadata — 65/100 (weight 16 → 10.4 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Guide / product name in H1 | 35% | 100/100 | "BI Connections — Sales_Orders" clearly names the product |
| Task ID / traceability tag | 30% | 100/100 | `_TASK-MART-004 \| [PENDING: CX-P05] BI service account grants_` — clear task ID and PENDING flag |
| Catalog / schema reference | 20% | 0/100 | Header block itself contains no catalog name; `globalsales` first appears inside the connection string section |
| Author / generated date | 15% | 0/100 | No author, created date, or version tag in the header |

**Strengths:**
- Product name and task ID both clearly stated.

**Gaps:**
- No catalog reference in header block.
- No generated date or author.

**Improvement items:**
- [ ] Add `Catalog: globalsales.mart` or a catalog note before the first `##` heading.
- [ ] Add a generated date or version line (e.g., `_Last updated: 2026-09-03_`).

---

### 1. Overview — 0/100 (weight 16 → 0.0 pts)

**[MISSING]** — Participant document has no Overview section. The reference Overview explains that all BI access goes through the `mart` schema and sets context for BI developers reconnecting after migration.

**Improvement items:**
- [ ] Add an `## Overview` section (2–4 sentences) explaining: the migration context, that all BI access goes through `globalsales.mart`, and which two mart views are the primary BI assets.

---

### 2. Connection Details per Mart View — 41/100 (weight 18 → 7.4 pts)

**Criteria scored:** Content completeness (75%), Attribute Table (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 40/100 | Report manifest covers view/asset names and connection mode; missing UC paths, object types, service principal, minimum privilege, refresh cadence, and SQL samples |
| Attribute Table | 15% | 26/100 | Table present (Report / Primary asset / Mode / Notes) but columns are a report manifest, not per-view config attributes (no UC path, Object type, SP, Privilege, Refresh rows) |
| Structure | 10% | 70/100 | H2 heading present; Markdown table correctly formatted; no intro paragraph |

**Strengths:**
- 9-report connection manifest provides a useful asset inventory for BI developers.
- `mart.v_customer_sales_summary`, `mart.v_order_details`, and other mart assets are specifically named.
- Mode column (`DirectQuery`) and Notes column add operational context.

**Gaps:**
- No per-view attribute table: UC path (`globalsales.mart.<view>`), Object type (Materialized View / Standard View), Service principal, Minimum privilege, and Refresh/availability are all absent.
- No SQL sample query for any mart view.
- No intro paragraph explaining the section.

**Improvement items:**
- [ ] For each key mart view (`v_customer_sales_summary`, `v_order_details`), add an H3 subsection with an attribute table containing: Unity Catalog path, Object type, Service principal, Minimum privilege, Real-time/Refresh.
- [ ] Add a sample SQL connection query per view.
- [ ] Add a one-sentence intro above the report manifest explaining its purpose.

---

### 3. Connecting BI Tools — 64/100 (weight 18 → 11.5 pts)

**Criteria scored:** Content completeness (55%), Connection String (20%), BI Tool Steps (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 63/100 | Server, HTTP path, authentication, catalog, schema all present; Power BI / Tableau numbered steps entirely absent |
| Connection String | 20% | 100/100 | All 5 required fields present (Server, HTTP Path, Authentication, Catalog, Schema); catalog correctly set to `globalsales` / `mart` |
| BI Tool Steps | 15% | 11/100 | No numbered steps for Power BI or Tableau; Power BI mentioned only in auth credential note |
| Structure | 10% | 76/100 | H2 heading present; connection string in fenced code block; minimal auth context after block; no formal intro |

**Strengths:**
- Connection string block is complete and uses the participant's own catalog (`globalsales`/`mart`).
- Authentication options (PAT and SP OAuth) are correctly stated.
- Security note ("never in the report file") adds operational value.

**Gaps:**
- No numbered step-by-step guide for connecting Power BI or Tableau.
- No mention of which connector to select in Power BI or Tableau UI.
- Auth note is placed after the code block with no intro context.

**Improvement items:**
- [ ] Add a "Power BI" subsection with numbered steps: (1) Select Azure Databricks connector, (2) Enter Server hostname + HTTP path, (3) Set Catalog = `globalsales` and Schema = `mart`, (4) Select the target view.
- [ ] Add a similar "Tableau" section or note if applicable.
- [ ] Add a brief intro sentence above the connection string block.

---

### 4. Known Issues and Workarounds — 0/100 (weight 16 → 0.0 pts)

**[MISSING]** — No known issues, troubleshooting, or caveats section in the participant document. The reference covers: stale Materialized View data (check `stg.lineage` / trigger ETL REFRESH) and ACCESS DENIED (confirm service principal grants).

**Improvement items:**
- [ ] Add a `## Known Issues and Workarounds` section with an Issue | Workaround table.
- [ ] Include at minimum: stale view data workaround (check `stg.lineage` for latest `status='success'` run) and ACCESS DENIED workaround (verify `globalsales.mart` GRANT for the BI service principal).

---

### 5. Access Provisioning — 43/100 (weight 16 → 6.9 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 40/100 | GRANT SELECT on schema + GRANT EXECUTE on function cover SP access; no contact info, no refresh request path, no user onboarding instructions; SP name is an unresolved placeholder |
| Structure | 10% | 73/100 | H2 heading present; SQL in fenced block with `sql` tag; no intro paragraph; PENDING flag in heading |

**Strengths:**
- GRANT SELECT on `globalsales.mart` correctly scoped to schema level.
- GRANT EXECUTE on function is a useful addition.
- PENDING flag and task reference (`CX-P05`) signal that this is a known incomplete item.

**Gaps:**
- SP name `{{UC_ROLE_BI_SERVICE_PRINCIPAL}}` is an unresolved template placeholder — GRANT is not executable.
- No contact information (email, Slack channel, or team name) for access requests.
- No instructions for onboarding new BI service principals or granting the `purchase-analysts` / sales-analysts role to end users.
- No path for requesting a manual mart refresh.

**Improvement items:**
- [ ] Resolve `{{UC_ROLE_BI_SERVICE_PRINCIPAL}}` to the actual service principal name once CX-P05 is confirmed.
- [ ] Add a contact line: team name, email address, or Slack channel for access requests.
- [ ] Add bullet points for: onboarding new BI service principals, granting analyst role to end users, requesting manual mart refresh.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add `## Overview` section (2–4 sentences on migration context and mart access) | Overview | +14 pts |
| 2 | Add `## Known Issues and Workarounds` table (stale MV, ACCESS DENIED) | Known Issues | +14 pts |
| 3 | Add per-view attribute tables (UC path, Object type, SP, Min privilege, Refresh) with SQL samples | Connection Details | +8 pts |
| 4 | Resolve SP name placeholder and add contact/provisioning info | Access Provisioning | +5 pts |
| 5 | Add numbered Power BI / Tableau connection steps | Connecting BI Tools | +4 pts |
| 6 | Add catalog reference and date to header block | Header Metadata | +2 pts |

---

## Priority Actions

1. **Add `## Overview` and `## Known Issues and Workarounds` sections** — both are entirely missing and together account for 32 pts of possible weight plus a −10 auto-deduct for the two missing H2s. These two additions alone are worth up to **+24 pts**.
2. **Replace the report manifest with per-view attribute tables** — add H3 subsections for each key mart view (`v_customer_sales_summary`, `v_order_details`) with UC path, Object type, Service principal, Minimum privilege, Refresh, and a SQL sample. This addresses the −4 attribute table auto-deduct and recovers up to **+8 pts** in the Connection Details section.
3. **Resolve the GRANT SQL placeholder** — once CX-P05 is confirmed, replace `{{UC_ROLE_BI_SERVICE_PRINCIPAL}}` with the actual SP name and add a contact email/Slack channel. Removes the −2 GRANT placeholder auto-deduct and improves Access Provisioning content score. Worth up to **+5 pts**.
4. **Add Power BI / Tableau numbered steps** — the connection string is perfect; adding the BI tool steps below it completes the "Connecting BI Tools" section and recovers up to **+4 pts**.

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

*Report generated by skill 30-migvisor-task-checker-bi-connections on 2026-09-03*
