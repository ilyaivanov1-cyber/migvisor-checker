---
task_id: TASK-TSK-001
skill: task-checker-tasks
participant_file: trainees/trainee_1/tasks.md
reference_file: reference/tasks.md
product: Sales_Orders
generated: 2026-09-03
total_score: 60/100
grade: Acceptable
---

# TASK-TSK-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase (GlobalPurchase_Project)
**Participant file:** `trainees/trainee_1/tasks.md`
**Reference file:** `reference/tasks.md`
**Generated:** 2026-09-03

---

## Score Summary

**The task plan Score: 60/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 33 | 39/100 | 12.9 | ✗ |
| Task Summary | 33 | 55/100 | 18.3 | ⚠ |
| Task Details | 34 | 85/100 | 28.8 | ✓ |
| **Subtotal** | | | **60.0** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **60/100** | |

**Grade: Acceptable**

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No task IDs anywhere | −5 pts | No — all tasks carry TASK-{GROUP}-{NNN} IDs |
| Missing H2 reference section | −5 pts each | No — both sections present (Overview ≈ Task Summary, Task Groups ≈ Task Details) |
| No acceptance criteria anywhere | −4 pts | No — every task has Acceptance criteria |
| >30% tasks lack individual AC | −3 pts | No — all 66 tasks have AC |
| >50% tasks lack deliverable paths | −3 pts | No — all 66 tasks have Deliverables |
| No dependency specification on any task | −3 pts | No — all tasks have Depends on field |
| No requirements traceability on any task | −3 pts | No — all tasks have Implements field |
| Task with no description (ID only) | −2 pts/task | No — all tasks have descriptions |
| Missing PENDING markers vs reference | −2 pts | No — reference has no pending items |

---

## Section Feedback

### Header Metadata (12.9/33 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Sub-criteria breakdown (raw 39/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product/project identification | 30% | 50/100 | Product name "Sales_Orders" present; project name absent |
| Temporal metadata | 20% | 75/100 | Generation date present; pipeline stage present; no version field |
| Document scope | 30% | 30/100 | Pipeline stage present; source documents not referenced |
| Author/ownership | 20% | 0/100 | No author or team attribution |

**Strengths:**
- Product name clear in H1 title
- Generation date present (2026-06-05)
- Pipeline stage labelled

**Gaps:**
- Project name absent (reference has `Project: GlobalPurchase_Project`)
- Source documents not referenced (reference lists `Source: design.md + requirements.md`)
- No author or team attribution

---

### Task Summary (18.3/33 pts)

**Criteria scored:** Content (65%), Deliverable Paths (15%), Requirements Traceability (10%), Structure (10%)

**Content completeness (70/100):**
- Task groups covered: 11/11 — all reference pipeline layers present
- Per-task entry granularity: 25% — Overview is group-level (11 rows); reference has one row per task (57 rows)
- Effort/counts present: 100% — Task Count and Estimated Effort columns both present
- Score: (11/11)×40% + 25%×40% + 100%×20% = **70/100**

**Deliverable paths (0/100):**
- Reference Task Summary has a File/Artifact column with specific paths per task
- Participant Overview has no file paths column
- Score: 0/100

**Requirements traceability (0/100):**
- Reference Task Summary has a Requirements column per task row
- Participant Overview has no requirements column
- Score: 0/100

**Structure (100/100):**
- H2 present: Yes (## Overview)
- Table present and formatted correctly: Yes
- All groups represented: Yes (all 11 groups)

**Strengths:**
- All 11 pipeline layers covered
- Effort estimates (Task Count + Estimated Effort) add planning value
- Clean table structure

**Gaps:**
- Group-level only; reference expects one row per individual task
- No File/Artifact column — deliverable paths missing from summary
- No Requirements column — traceability missing from summary

---

### Task Details (28.8/34 pts)

**Criteria scored:** Content (20%), Acceptance Criteria (20%), Deliverable Paths (15%), Dependency Graph (15%), Requirements Traceability (10%), Design References (10%), Structure (10%)

**Content completeness (98/100):**
- Task groups covered: 11/11
- Task count: 66 participant vs 57 reference — capped at 100%
- Description quality: 95/100 — notebook names, function signatures, column lists, constants, idempotency patterns all present

**Acceptance criteria (91/100):**
- Tasks with AC: 66/66 = 100%
- Measurable/testable ACs: ~90% — specific commands, row counts, coverage thresholds
- ACs referencing artifacts: ~85% — most name specific tables, columns, or files

**Deliverable paths (100/100):**
- Tasks with deliverables: 66/66 = 100%
- Paths are specific file paths: Yes — uniform `products/Sales_Orders/current/codebase/<type>/<path>` pattern
- Naming convention consistent: Yes

**Dependency graph (100/100):**
- Tasks with deps specified: 66/66 = 100% (leaf tasks use "Depends on: none")
- Deps use task IDs: 100% — all reference specific TASK-XXX-NNN identifiers
- Cross-group deps captured: Yes — e.g., TASK-FACT-002 depends on TASK-DIM-008, TASK-ING-002

**Requirements traceability (70/100):**
- Tasks with req ref: 66/66 = 100%
- Specific IDs vs category labels: category-level only (FR-TRN, NFR-MAINT vs FR-001, NFR-008) → 25% specificity
- Score: (66/66)×60% + 25%×40% = **70/100**

**Design references (0/100):**
- No task has a Design reference field
- Reference has Design reference per task (e.g., "Data Model §2.5", "Transformation §SCD-2 Dimension Merge Design")
- Score: 0/100

**Structure (100/100):**
- H2 present: Yes (## Task Group 1 … ## Task Group 11)
- Tasks organized by group: Yes
- Task IDs consistent scheme: Yes — TASK-{GROUP}-{NNN} throughout
- Within-group H3 headings: Yes

**Strengths:**
- 66 tasks with full field coverage across all pipeline layers
- Every task has deliverable paths, dependency IDs, and acceptance criteria
- Dependency graph exemplary: specific IDs, "none" for leaf nodes, rich cross-group links
- ACs are concrete and testable throughout
- [PENDING] markers correctly used for open decisions (CX-P04, CX-P05, CX-DQ-01)

**Gaps:**
- Design reference field entirely absent — no task links to a design document section
- Requirements use category-level codes instead of specific numeric IDs

---

## Improvement Items

1. **[Task Summary — Deliverable Paths]** Add File/Artifact column to Overview table → up to +5.0 pts
2. **[Task Summary — Per-Task Granularity]** Expand Overview from 11 group rows to one row per individual task → up to +3.3 pts
3. **[Task Summary — Requirements Traceability]** Add Requirements column to Overview table → up to +3.3 pts
4. **[Header — Document Scope]** Add source documents reference to header → up to +3.0 pts
5. **[Header — Project Identification]** Add project name field to header → up to +2.5 pts
6. **[Header — Author/Ownership]** Add author or team attribution → up to +2.0 pts
7. **[Task Details — Design References]** Add `Design reference:` field to each task pointing to the relevant design document section → up to +3.4 pts
8. **[Task Details — Requirements Traceability]** Replace category codes (FR-TRN) with specific numeric IDs (FR-001) → up to +1.0 pt

---

## Priority Actions

1. **Expand Overview to per-task rows with File/Artifact and Requirements columns** → up to +8.3 pts combined
2. **Add Design reference field to all task details** → up to +3.4 pts
3. **Complete header metadata** (project name, source docs, author) → up to +7.5 pts
4. **Replace category requirement codes with specific numeric IDs** → up to +1.0 pt

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| **60–74** | **Acceptable** | **Several gaps; revise before proceeding** |
| 45–59 | Needs work | Missing AC, deliverables, or dep graph |
| 0–44 | Incomplete | Major sections missing or tasks unidentifiable |
