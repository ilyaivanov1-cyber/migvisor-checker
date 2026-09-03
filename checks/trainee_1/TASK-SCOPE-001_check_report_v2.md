---
task_id: TASK-SCOPE-001
product: Sales_Orders
participant_file: product-scope.md
reference_file: 0 product-scope.md
checked_at: 2026-09-02T11:00:00Z
sections_evaluated: 9
total_score: 100/100
grade: Excellent
identical_to_reference: false
---

# Task Check Report — product-scope
_Sales_Orders | 2026-09-02_

**File resolution log:**
- Participant file: `product-scope.md` — supplied explicitly by user
- Reference file: `0 product-scope.md` — auto-resolved (highest-priority candidate)
- Product: `Sales_Orders` — derived from H1 heading `# Product Scope — Sales_Orders`
- Sections in reference: 9 | Sections in participant: 14 (9 matched by heading text, 5 extra — not scored)
- Point weights: auto-calculated — floor(100/9)=11 base; +1 distributed to 2 longest sections (§3 Objects in Scope → §6, §4 Out-of-Scope Objects → §7)

---

## Score Summary

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| 1. Identity | §1 Identity | 11 | 11 | ✓ |
| 2. Description | §2 Description | 11 | 11 | ✓ |
| 3. Objects in Scope | §6 In-Scope Objects | 12 | 12 | ✓ |
| 4. Out-of-Scope Objects | §7 Out-of-Scope Items | 12 | 12 | ✓ |
| 5. Consumers | §9 Consumers | 11 | 11 | ✓ |
| 6. Calculation Surface | §10 Calculation Surface | 11 | 11 | ✓ |
| 7. Boundaries | §8 Boundaries | 11 | 11 | ✓ |
| 8. Priority and Sequencing | §13 Priority and Sequencing | 11 | 11 | ✓ |
| 9. Known Migration Risks | §14 Known Migration Risks | 10 | 10 | ✓ |
| **Total** | | **100** | **100** | |

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Section 1 — Identity (11/11)
_Matched to participant §1 Identity_

**Coverage (4/4):** All five identity fields present — product name (`Sales_Orders`), parent project (`GlobalSales_Project`), scope owner (`Sales Analytics Team`), discovery mode (hybrid Pattern A with base node UUID), and plan stage (`scope`).

**Specificity (3/3):** Base node UUID and MCP path documented (`bd3cae6f → wideworldimportersdw.fact.order`). Named scope owner rather than a placeholder.

**Technical accuracy (2/2):** Source system correctly identified in discovery mode.

**Issues/gaps flagged (1/1):** Scope owner populated — no gap.

**Structure (1/1):** Standard identity table, consistent with reference.

No deductions. Full marks.

---

### Section 2 — Description (11/11)
_Matched to participant §2 Description_

**Coverage (4/4):** Domain stated, core objects named (fact.sale, fact.order, dimensions, SSIS layer, analytics views, BI reports), source-to-target migration direction stated.

**Specificity (3/3):** Specific system names, database names, and technology stack stated.

**Technical accuracy (2/2):** Source system (`wideworldimportersdw`) correctly described, not the target.

**Issues/gaps flagged (1/1):** Content is complete; no gaps required for a description section.

**Structure (1/1):** Narrative format consistent with reference.

No deductions. Full marks.

---

### Section 3 — Objects in Scope (12/12)
_Matched to participant §6 In-Scope Objects_

**Coverage (5/5):** All object layers present — fact tables, dimensions, staging tables, procedures, sequences, analytics views, scalar functions, SSIS pipeline items, BI reports. Full object table with schema, type, and role per entry.

**Specificity (3/3):** Schema-qualified names used throughout, role descriptions per object. Object IDs available in §3 subsections of participant file and cross-referenced here.

**Technical accuracy (2/2):** Source system objects described. No target-system substitution.

**Issues/gaps flagged (1/1):** SSIS bug noted in §3.6 (participant file) — `pipeline_item_truncate purchase_staging` targets wrong table. Proactive risk flag within scope section.

**Structure (1/1):** Consistent table format (Object name / Object type / Schema / Role).

No deductions. Full marks.

---

### Section 4 — Out-of-Scope Objects (12/12)
_Matched to participant §7 Out-of-Scope Items_

**Coverage (5/5):** All exclusion categories present — other fact tables and their staging/procedures, unrelated dimensions, out-of-scope analytics views, SQL Server config procedures, SAP BO, Oracle artifacts, dbo.* test objects, out-of-scope ETL items.

**Specificity (3/3):** Named object lists per exclusion row, reasons explicitly stated per category.

**Technical accuracy (2/2):** Exclusions correctly attributed to other products or platforms.

**Issues/gaps flagged (1/1):** Cross-domain view coordination note included.

**Structure (1/1):** Table with Object name / Reason for exclusion.

No deductions. Full marks.

---

### Section 5 — Consumers (11/11)
_Matched to participant §9 Consumers_

**Coverage (4/4):** 11 consumers documented — 7 BI reports + 4 analytics views, each with consumer type and purpose.

**Specificity (3/3):** Named reports with exact titles, consumption paths stated.

**Technical accuracy (2/2):** Consumers correctly identified against the in-scope object list.

**Issues/gaps flagged (1/1):** Consumer list is complete per scope; no gaps to flag.

**Structure (1/1):** Table with Consumer / Consumer type / What they use it for.

No deductions. Full marks.

---

### Section 6 — Calculation Surface (11/11)
_Matched to participant §10 Calculation Surface_

**Coverage (4/4):** Calculation profile stated (`moderately calculation-heavy`), five calculation categories documented with migration implications.

**Specificity (3/3):** Named functions, procedures, sequences, and views with migration action per item.

**Technical accuracy (2/2):** All calculation objects reference the correct source layer.

**Issues/gaps flagged (1/1):** Scalar UDF performance risk noted.

**Structure (1/1):** Profile table + narrative with per-item bullet points.

No deductions. Full marks.

---

### Section 7 — Boundaries (11/11)
_Matched to participant §8 Boundaries_

**Coverage (4/4):** All boundary types present — temporal, system source, system target, ETL orchestration source, ETL orchestration target, organizational.

**Specificity (3/3):** Exact date range, catalog name (`globalsales`), layer convention, SSIS pipeline path.

**Technical accuracy (2/2):** Source and target systems correctly separated.

**Issues/gaps flagged (1/1):** All fields populated — no boundary ambiguities.

**Structure (1/1):** Table with Boundary type / Definition.

No deductions. Full marks.

---

### Section 8 — Priority and Sequencing (11/11)
_Matched to participant §13 Priority and Sequencing_

**Coverage (4/4):** Priority (PRIMARY), rationale, dependencies, and successor products all present.

**Specificity (3/3):** Named successor products with specific shared dimension dependencies stated.

**Technical accuracy (2/2):** Dependencies correctly attributed.

**Issues/gaps flagged (1/1):** All fields populated.

**Structure (1/1):** Table with Field / Value.

No deductions. Full marks.

---

### Section 9 — Known Migration Risks (10/10)
_Matched to participant §14 Known Migration Risks_

**Coverage (4/4):** 6 risks documented — space-in-name convention, SEQUENCE objects, T-SQL MERGE rewrites, scalar UDF performance, config procedure scope, SSIS orchestration complexity.

**Specificity (3/3):** Each risk names specific objects, describes the implication, and states the required migration action.

**Technical accuracy (2/2):** All risks correctly attributed to source-system characteristics.

**Issues/gaps flagged (1/1):** Implication column explicitly states consequences for each risk.

**Structure (1/1):** Numbered table with # / Risk / Implication columns.

No deductions. Full marks.

---

## Extra Sections (not in reference)

| Participant section | Notes |
|---|---|
| §3 Source System(s) | Source system detail with sub-sections for each object layer — supplementary to §6 In-Scope Objects |
| §4 Target System | Explicit target platform table (catalog, naming convention) |
| §5 Key Entities | Bulleted list of primary business entities |
| §11 Interview Mode | Discovery metadata (MCP availability, interviewer, date, pattern) |
| §12 Stakeholder Sign-Off | Sign-off table with `[USER INPUT REQUIRED]` placeholders |

---

## Approach Notes

- Participant uses a different section numbering than the reference — sections matched by heading text similarity, not by number. All 9 reference sections found and matched correctly.
- Participant has 5 extra sections beyond the reference — noted above, not penalised.
- Stakeholder sign-off table (§12) contains `[USER INPUT REQUIRED]` — treated as intentional deferral; section is supplementary to scored reference sections.

---

## Priority Improvements

No score-impacting gaps found. Optional enhancements:

1. **§12 Stakeholder Sign-Off — fill deferred fields:** Complete product owner, business lead, and technical lead rows when sign-off occurs.
2. **§9 Consumers — add owner/contact:** No owner column present — adding a team or role per consumer improves traceability.
3. **§1 Identity — scope owner detail:** `Sales Analytics Team` is sufficient, but a named contact would strengthen accountability.

---

## Next Step

Score 100 ≥ 75: You can proceed to the next task.
