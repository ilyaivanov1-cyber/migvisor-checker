---
task_id: TASK-TSK-001
skill: task-checker-tasks
participant_file: tasks.md
reference_file: tasks_final.md
product: Sales_Orders
generated: 2026-09-03
total_score: 63/100
grade: Acceptable
---

# TASK-TSK-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase (GlobalPurchase_Project)
**Participant file:** `tasks.md`
**Reference file:** `tasks_final.md`
**Generated:** 2026-09-03

---

## Score Summary

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 33 | 43/100 | 14 pts | ⚠ |
| Task Summary | 33 | 62/100 | 20 pts | ⚠ |
| Task Details | 34 | 84/100 | 29 pts | ✓ |
| **Subtotal** | | | **63 pts** | |
| Auto-deducts | | | **0 pts** | |
| **Total** | | | **63/100** | |

**Grade: Acceptable**

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No task IDs anywhere in document | −5 pts | No — all 66 tasks have TASK-GROUP-NNN IDs |
| Missing H2 reference section entirely | −5 pts each | No — participant has equivalent ## Overview and ## Task Group headings |
| No acceptance criteria anywhere | −4 pts | No — all 66 tasks have Acceptance criteria |
| More than 30% of tasks lack AC | −3 pts | No — 0/66 tasks lack AC |
| No deliverable paths on >50% of tasks | −3 pts | No — all 66 tasks have Deliverables |
| No dependency specification on any task | −3 pts | No — all 66 tasks have Depends on |
| No requirements traceability on any task | −3 pts | No — all 66 tasks have Implements |
| Any task with no description | −2 pts/task max −6 | No — all tasks have substantive descriptions |
| Missing [PENDING] markers for open items | −2 pts | No — participant marks [PENDING: CX-P04], [CX-P05], [CX-DQ-01] correctly |

---

## Section Feedback

### Header Metadata (14/33 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Content completeness (43/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product/project identification | 30% | 50/100 | Product name (Sales_Orders) present; no explicit project name field |
| Temporal metadata | 20% | 60/100 | Generation date present; no version/status field |
| Document scope | 30% | 40/100 | Pipeline stage ("tasks") present; source documents not referenced |
| Author/ownership | 20% | 0/100 | No author or team attribution |

**Structure (80/100):** H1 title and metadata block are well-formed; minor deduction for absent fields.

**Strengths:**
- Product name and generation date clearly stated in first two lines
- Pipeline stage label present (`Pipeline stage: tasks`)
- Three [PENDING] markers at document level correctly document outstanding decisions

**Gaps:**
- No project name (reference: `GlobalPurchase_Project`)
- No source documents cited (reference: `Source: design.md + requirements.md`)
- No version/status field
- No author or team attribution field

---

### Task Summary (20/33 pts)

**Criteria scored:** Content completeness (80%), Requirements Traceability (10%), Structure (10%)

**Content completeness (64/100):**
- Task groups covered: 10/11 reference groups covered (GRANT group split across DB, MART, SEC — functionally present but not as a discrete group) → 86% group coverage
- Per-task entry granularity: group-level only (11 rows vs reference's 56 per-task rows) → 25% granularity score
- Effort/counts present: Task Count + Estimated Effort columns both present → 100%

Calculation: (0.86 × 40) + (0.25 × 40) + (1.0 × 20) = 34.4 + 10.0 + 20.0 = 64/100

**Requirements traceability (0/100):**
- Reference Task Summary has a Requirements column (per-task requirement links in overview table)
- Participant Overview table columns: Task Group, Group ID, Task Count, Estimated Effort — no Requirements column
- 0/11 overview rows contain requirement references → 0/100

**Structure (100/100):**
- H2 heading present (## Overview): Yes
- Table present and well-formatted: Yes
- All 11 participant groups represented: Yes

**Strengths:**
- Group-level overview table provides useful effort planning visibility (total: 22.5 days across 11 groups)
- Task Count column allows quick progress tracking
- All task groups from participant scope are enumerated

**Gaps:**
- Overview is group-level (11 rows) — reference expects per-task index (56 rows) with one row per individual task
- No Requirements column in the overview table — reference maps each task to specific requirement IDs at a glance
- Missing a GRANT-equivalent discrete group (grants/security tasks are split across DB, MART, SEC)

---

### Task Details (29/34 pts)

**Criteria scored:** Content (20%), Acceptance Criteria (20%), Deliverable Paths (15%), Dependency Graph (15%), Requirements Traceability (10%), Design References (10%), Structure (10%)

**Content completeness (94/100):**
- Task groups covered: 10/11 reference groups have equivalent participant groups → 91%
- Task count: 66 participant vs 56 reference → min(66/56, 1.0) = 100%
- Description quality: Descriptions are implementation-specific — they name exact notebook filenames, function signatures, MERGE patterns, and idempotency requirements → 90/100

**Acceptance criteria (90/100):**
- Tasks with any AC: 66/66 → 100%
- Measurable/testable ACs (concrete commands, row counts, column assertions): ~58/66 ≈ 88%
- ACs referencing specific artifacts (tables, columns, functions): ~55/66 ≈ 83%

Examples of strong ACs: `stg.lineage has columns: lineage_key (BIGINT IDENTITY)`, `pytest step enforces --cov-fail-under=80`, `COALESCE NULL guard is present on both parameter and aggregate result`.

**Deliverable paths (100/100):**
- Tasks with deliverables: 66/66 → 100%
- Paths are specific file paths: Yes — all paths use `products/Sales_Orders/current/codebase/...` format → 100%
- Naming convention consistent: Yes — consistent prefix throughout → 100%

**Dependency graph (100/100):**
- Tasks with deps specified: 66/66 (leaf tasks use "Depends on: none") → 100%
- Deps use task IDs: Yes — all cross-task deps reference TASK-GROUP-NNN IDs → 100%
- Cross-group deps captured: Yes — e.g., FACT tasks depend on DIM tasks (TASK-DIM-008), DIM tasks depend on ING tasks (TASK-ING-004) → 100%

**Requirements traceability (74/100):**
- Tasks with req ref: 66/66 → 100% (60 pts contribution)
- Specific IDs vs category labels:
  - Category-level (FR-ING, FR-TRN, NFR-PERF, NFR-MAINT, FR-ORC, FR-LIN, FR-SRV): ~53/66 tasks → score 25%
  - Specific IDs (CON-SEC-001, DQR-AST-001..005, IFR-BI-001..009): ~13/66 tasks → score 100%
  - Weighted specificity: (13/66 × 100) + (53/66 × 25) = 19.7 + 20.1 = 40% specificity score → 40% × 40 = 16 pts

Calculation: (1.0 × 60) + (0.40 × 40) = 60 + 16 = 74/100 (14 pts out of possible 10 → 7.4 pts weighted)

**Design references (0/100):**
- Tasks with design ref: 0/66 — participant has no "Design reference" field on any task
- Reference has design section citations per task (e.g., `Data Model §2.5`, `Transformation §SCD-2 Dimension Merge Design`, `Observability §1`)
- This is the largest single gap in the Task Details section (−3.4 pts vs possible 3.4 pts)

**Structure (100/100):**
- H2 headings present per task group: Yes (## Task Group 1:, ## Task Group 2:, ...)
- Tasks organized by group: Yes
- Task IDs consistent scheme (TASK-GROUP-NNN): Yes
- Within-group H3 headings (### TASK-DB-001:): Yes

**Strengths:**
- Perfect deliverable paths coverage — all 66 tasks have specific, consistently formatted file paths
- Perfect dependency graph — all tasks specify dependencies using task IDs, including valid leaf-task "none"
- Excellent acceptance criteria coverage — 100% of tasks have ACs with strong measurability and artifact references
- Strong description quality — notebook names, function signatures, and implementation constraints are consistently specified
- Participant has 10 more tasks than reference (66 vs 56) providing broader scope coverage (ENV, SEC, ORC groups)
- [PENDING] markers on 6 tasks correctly document open decisions

**Gaps:**
- No "Design reference" field on any of the 66 tasks — reference maps every task to specific design document sections (e.g., `Data Model §2.1`, `Ingestion §4`, `Transformation §SCD-2`)
- Requirement traceability uses category-level labels (FR-ING, FR-TRN) rather than specific IDs (FR-001, FR-003) on ~80% of tasks
- ENV group (4 tasks) has no direct reference equivalent — maps loosely to COMMON + CFG groups
- SEC group (5 tasks) covers GRANT group tasks but under a different grouping scheme

---

## Improvement Items

Ordered by score impact (highest first):

1. **[Task Summary — Requirements Traceability]** Add a Requirements column to the Overview table with per-group requirement IDs → up to +3.3 pts
2. **[Task Summary — Content Completeness]** Expand the Overview table from group-level (11 rows) to per-task rows (one row per task with ID, file, description, requirements) → up to +10 pts on content granularity
3. **[Task Details — Design References]** Add a "Design reference:" field to every task pointing to specific design document sections (e.g., `Data Model §2.1`, `Ingestion §3`, `Transformation §SCD-2`) → up to +3.4 pts
4. **[Task Details — Requirements Traceability]** Replace category-level labels (FR-ING → FR-001, FR-002; NFR-PERF → NFR-001) with specific requirement IDs on all 66 tasks → up to +1.6 pts
5. **[Header — Author/Ownership]** Add author, team attribution field → up to +0.6 pts
6. **[Header — Document Scope]** Add source documents field (e.g., `Source: design.md + requirements.md`) → up to +0.6 pts
7. **[Header — Temporal Metadata]** Add version/status field → up to +0.3 pts
8. **[Header — Project Name]** Add explicit project name field → up to +0.3 pts

---

## Priority Actions

1. **Expand Overview table to per-task granularity** — Replace the 11-row group-level table with a 66-row per-task index (columns: Task ID, Group, File/Artifact, Description, Requirements). This is the single structural change that most closely mirrors the reference and recovers the most points on Task Summary. → up to +13 pts combined (granularity + req traceability)

2. **Add Design reference field to all tasks** — After the Deliverables block, add `**Design reference:** <design section(s)>` to every task. The reference design document sections include Data Model §2.x, Transformation §<pattern>, Ingestion §x, Serving §x, Observability §x. This recovers the entire design_refs criterion which currently scores 0. → up to +3.4 pts

3. **Replace category-level requirement refs with specific IDs** — Map FR-ING → FR-001/FR-002, FR-TRN → FR-003/FR-004/FR-006/FR-007, NFR-PERF → NFR-001, etc. Even a partial remap on the highest-impact tasks (DB, FACT, DIM groups) meaningfully raises specificity score. → up to +1.6 pts

4. **Add project name and source document refs to header** — Two metadata fields that bring the header in line with reference format. → up to +1.2 pts

5. **Add Requirements column to existing Overview table** — Even before expanding to per-task rows, adding a Requirements column to the current 11-row group table shows requirement coverage at the group level. → up to +3.3 pts

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing AC, deliverables, or dep graph |
| 0–44 | Incomplete | Major sections missing or tasks unidentifiable |
