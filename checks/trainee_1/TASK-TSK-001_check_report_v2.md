---
task_id: TASK-TSK-001
skill: task-checker-tasks
participant_file: trainees/trainee_1/tasks.md
reference_file: reference/tasks.md
product: Sales_Orders
generated: 2026-09-03
total_score: 63/100
grade: Acceptable
---

# TASK-TSK-001 Check Report

**Product:** Sales_Orders  
**Reference product:** Purchase (GlobalPurchase_Project)  
**Participant file:** `trainees/trainee_1/tasks.md`  
**Reference file:** `reference/tasks.md`  
**Generated:** 2026-09-03

> ℹ Cross-product evaluation: participant and reference describe different products. Structural completeness, task field coverage, AC quality, dependency graph, and traceability depth are scored. Product-specific table/notebook names are not penalised.

---

## Score Summary

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 33 | 53/100 | 18 | ⚠ |
| Task Summary (Overview) | 33 | 51/100 | 17 | ⚠ |
| Task Details | 34 | 83/100 | 28 | ✓ |
| **Subtotal** | | | **63** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **63/100** | |

**Grade: Acceptable** — Several gaps; revise before proceeding.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No task IDs anywhere | −5 pts | No — all 66 tasks have TASK-XXX-NNN IDs |
| Missing H2 reference section | −5 pts each | No — Overview and task group H2s present |
| No acceptance criteria anywhere | −4 pts | No — all 66 tasks have AC blocks |
| >30% tasks lack individual AC | −3 pts | No — 0/66 tasks missing ACs |
| No deliverable paths on >50% tasks | −3 pts | No — all 66 tasks have deliverable paths |
| No dependency specification on any task | −3 pts | No — all 66 tasks have Depends on field |
| No requirements traceability on any task | −3 pts | No — all 66 tasks have Implements field |
| Any task with no description | −2 pts per task | No — all 66 tasks have descriptions |
| Missing [PENDING] markers for reference open items | −2 pts | No — reference has no pending markers to compare |

---

## Section Feedback

### Header Metadata (18/33 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Content completeness (53/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product/project identification | 30% | 70% | "Sales_Orders" clear from title; no separate project name (reference has explicit "Project: GlobalPurchase_Project") |
| Temporal metadata | 20% | 60% | Generation date (2026-06-05) present; no version or status field |
| Document scope | 30% | 50% | Pipeline stage "tasks" noted; source documents not referenced (reference cites "design.md + requirements.md") |
| Author/ownership | 20% | 0% | No author, team, or ownership attribution |

**Structure (100/100):** H1 heading and metadata line both present.

**Strengths:**
- Generation date and pipeline stage clearly stated in the subtitle line
- Product name immediately identifiable from H1

**Gaps:**
- No project name — the header only identifies the product, not the project context
- Source documents that informed the task list are not cited
- No author or team field — unclear who produced and owns this document

---

### Task Summary / Overview (17/33 pts)

**Criteria scored:** Content (65%), Deliverable Paths (15%), Requirements Traceability (10%), Structure (10%)

**Content completeness (63/100):**
- Task groups covered: 9/11 reference groups matched — DB, ING, DIM, FACT, MART, DQ, TEST, DOCS (= DOC) are exact; ENV covers COMMON (contains constants.py and utils.py); SEC covers GRANT; ORC partially covers CFG (Workflow YAML, cluster, CI/CD, monitoring). BI sample queries and secrets config are not represented as a group in the overview.
- Per-task entry granularity: **Group-level only (25%)** — overview has one row per task group, not one row per individual task as in the reference. The reference overview table has one row per task (Task ID, Group, File, Description, Requirements). The participant's overview collapses 66 tasks into 11 group rows.
- Effort/counts present: **100%** — both task counts and effort estimates (in days) are shown.

**Deliverable paths (0/100):** Overview table has no file/artifact column. The reference includes a File/Artifact column per task row in the summary table. Participant deliverables only appear in the Task Details section.

**Requirements traceability (0/100):** Overview table has no Requirements column. The reference includes a Requirements column per task row. Participant requirement references only appear at task level in the **Implements:** field.

**Structure (100/100):** H2 present, table present, correctly formatted, all 11 groups represented.

**Strengths:**
- Effort estimates per group and a grand total (22.5 days across 66 tasks) provide actionable planning data absent from the reference
- Clean table layout with consistent group IDs

**Gaps:**
- Overview is group-level summary only; each individual task's ID, file path, and requirement reference are not visible at the summary level
- No file/artifact column — cannot see deliverable list without scanning all task groups
- No requirements column — cannot cross-check which requirements each task satisfies from the overview

---

### Task Details (28/34 pts)

**Criteria scored:** Content (20%), Acceptance Criteria (20%), Deliverable Paths (15%), Dependency Graph (15%), Requirements Traceability (10%), Design References (10%), Structure (10%)

**Content completeness (91/100):**
- Task groups covered: 9/11 reference functional layers present (DB, ING, DIM, FACT, MART, DQ, TEST, DOCS, plus ENV+SEC+ORC covering COMMON+GRANT+CFG). GRANT-type tasks (SQL GRANT statements) are partially embedded in SEC tasks; CFG-type config tasks (12 in reference) are spread across ENV, ORC, and DB groups in the participant (fewer standalone config tasks).
- Task count: participant 66 vs reference 61 — participant exceeds reference scope ✓
- Description quality: **90%** — descriptions include specific notebook names, function signatures (`apply_scd2_merge`, `resolve_surrogate_keys`, `apply_fact_merge`), specific column names, Delta table properties, and implementation constraints. All descriptions are actionable. Minor: a handful of ORC/SEC tasks have shorter descriptions.

**Acceptance criteria (91/100):**
- Tasks with AC: 66/66 (100%)
- Measurable/testable ACs: ~59/66 (89%) — most ACs specify verifiable conditions such as column names, specific values (`PROFIT_MARGIN_FACTOR = 1.05`), SQL outputs (`DESCRIBE DETAIL` checks), and pass/fail assertions. A few ACs in ORC and DOCS groups are more subjective ("document reviewed and signed off").
- ACs referencing artifacts: ~56/66 (85%) — most ACs name specific tables, columns, files, or function return values.

**Deliverable paths (100/100):**
- 66/66 tasks specify deliverable file paths
- All paths are explicit (`products/Sales_Orders/current/codebase/src/db/ddl/dim_customer.sql`)
- Naming convention is consistent throughout: `products/<Product>/current/codebase/<layer>/`

**Dependency graph (100/100):**
- 66/66 tasks have **Depends on:** field (leaf tasks correctly carry "none")
- All non-leaf dependencies reference specific task IDs (e.g., "TASK-DB-001, TASK-ENV-002, TASK-ENV-003")
- Cross-group dependencies present: e.g., TASK-FACT-002 depends on TASK-DIM-008; TASK-DB-010 depends on multiple TASK-DB-* tasks

**Requirements traceability (70/100):**
- 66/66 tasks have **Implements:** field
- Requirement references use **category-level IDs** (FR-ORC, FR-ING, FR-TRN, NFR-MAINT, CON-SEC-001, DQR-AST-001..005) rather than **specific numeric IDs** (FR-001, NFR-003). Per rubric: category-level scores 25%.
- Score: (66/66)×60% + 0.25×40% = 60+10 = 70%

**Design references (0/100):**
- 0/66 tasks have a **Design reference:** field.
- The reference document includes a Design reference field on every task (e.g., "Data Model §2.5, Data Model §4" or "Transformation §SCD-2 Dimension Merge Design").
- This is the largest single gap in Task Details.

**Structure (100/100):**
- H2 task group headings present for all 11 groups
- Tasks organized within each group
- Task IDs follow a consistent pattern (TASK-{GROUP}-{NNN})
- H3 heading per individual task throughout

**Strengths:**
- Perfect dependency graph — all 66 tasks traceable with specific task ID references and cross-group chains
- Perfect deliverable coverage — every task has a specific file path in a consistent naming convention
- Acceptance criteria quality is high: measurable, testable, with artifact references

**Gaps:**
- No design reference field on any task — readers cannot navigate from task to the relevant design document section
- Requirement traceability is category-level only — requirements doc links are not traceable to specific requirement IDs

---

## Improvement Items

Ordered by score impact (highest first):

1. **[Task Summary — Deliverable Paths]** Add a File/Artifact column to the Overview table with the primary deliverable path per task → up to +5 pts
2. **[Task Summary — Content + Req Traceability]** Expand overview from group-level rows to one row per individual task, add a Requirements column → up to +4 pts
3. **[Task Details — Design References]** Add a **Design reference:** field to each task pointing to the relevant design document section (e.g., "Design §3.2 — Dimension Load") → up to +3.4 pts
4. **[Header — Content]** Add project name, source document references (design.md, requirements.md), and author/team attribution to the header → up to +3 pts
5. **[Task Details — Requirements Traceability]** Replace category-level requirement codes (FR-ORC, NFR-MAINT) with specific numeric IDs (FR-001, NFR-003) matching the requirements document → up to +1 pt

---

## Priority Actions

1. **Add design reference field** to all task entries in the Task Details section — point to the relevant design document section for each task. This is the single largest gap (10% criterion, currently 0%) and adds no structural overhead since a short "Design §X.Y" annotation suffices. → up to +3.4 pts

2. **Expand Overview table to per-task level** — add one row per individual task (as in the reference) with columns: Task ID, Group, Primary Deliverable Path, Requirements. This closes both the deliverables (15%) and req traceability (10%) gaps in the Task Summary section. → up to +9 pts combined if fully done

3. **Add project name and source document references** to the document header — one line: `**Project:** Sales_Orders_Project · **Source:** design.md + requirements.md` → up to +3 pts

4. **Replace category-level requirement codes with specific IDs** — reference the requirements document and map FR-ORC → FR-xxx numeric IDs. → up to +1 pt

5. **Add author/owner field** to document header. → minor recovery on header score

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing AC, deliverables, or dep graph |
| 0–44 | Incomplete | Major sections missing or tasks unidentifiable |
