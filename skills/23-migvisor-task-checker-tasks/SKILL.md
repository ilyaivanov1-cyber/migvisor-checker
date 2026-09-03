# Skill: task-checker-tasks

## Identity

| Field | Value |
|---|---|
| Skill number | 23 |
| Skill name | task-checker-tasks |
| Task ID | TASK-TSK-001 |
| Output file | `checks/<trainee_name>/TASK-TSK-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check my tasks"
- "validate tasks"
- "compare tasks"
- "score tasks"
- "check my work plan"
- "run task-checker-tasks"
- "run 23-migvisor-task-checker-tasks"
- "23"

---

## Invocation Syntax

```
/task-checker-tasks
/task-checker-tasks participant=<path> reference=<path> trainee=<name>
run task-checker-tasks
run 23-migvisor-task-checker-tasks
```

---

## Preconditions

- A participant tasks file must exist (default: `trainees/<trainee_name>/tasks.md`)
- A reference tasks file must exist (default: `reference/tasks.md`)
- The `checks/<trainee_name>/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/tasks.md` | `participant=` |
| Reference (final) | `reference/tasks.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/tasks.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/tasks.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with appropriate error (see Step 1)
3. Fallback: `tasks.md` in workspace root

Auto-detection fallback order for reference:
1. `reference/tasks.md`

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags. If `trainee=<name>` is provided and `participant=` is not, resolve participant as `trainees/<name>/tasks.md`.
2. Otherwise run auto-detection sequences above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name from the participant path (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] tasks file.
   Provide an explicit path: /task-checker-tasks participant=<path>
   ```
5. Read both files in full.
5. Extract metadata from each file header (lines before the first `##`):
   - Product name (H1 title or `product:` field)
   - Project name
   - Generation date
   - Source document(s) referenced
   - Any `[PENDING: ...]` markers at document level

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before first `##`).
2. For each `## ` H2 heading in the reference file, add a section entry.
3. Record section title exactly as written.

Result: N scored sections = 1 (Header) + count of `##` headings in reference.

**Example** — if reference has 2 H2 headings (Task Summary, Task Details):
- N = 3
- Section list: Header Metadata, Task Summary, Task Details

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:
1. Task Details (or equivalent detailed section — highest task field richness)
2. Task Summary / Overview (index table)
3. Header Metadata (lowest)

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example** (N=3, base=33, remainder=1): Task Details gets 34, Task Summary gets 33, Header gets 33.

---

### Step 4 — Classify Section Content Types

For each section in the **participant** file, detect the following boolean flags:

| Flag | True when |
|---|---|
| `has_task_entries` | Section contains at least one task with an ID pattern (TASK-*, DB-*, ING-*, etc.) |
| `has_overview_table` | Section has a summary/index table listing tasks or task groups |
| `has_task_ids` | Tasks have traceable ID strings |
| `has_task_types` | Tasks have a type label (etl, db, config, test, docs) |
| `has_priorities` | Tasks have a priority label (critical, high, medium, low) |
| `has_acceptance_criteria` | Tasks have per-task acceptance criteria (labeled "Acceptance criteria" or "Acceptance Criteria") |
| `has_deliverable_paths` | Tasks specify deliverable file paths |
| `has_dependency_graph` | Tasks specify predecessor task IDs ("Depends on" or "Dependencies") |
| `has_requirements_traceability` | Tasks reference which requirements they implement ("Implements" or "Requirements" field) |
| `has_design_references` | Tasks reference design document sections ("Design reference" field) |
| `has_effort_estimates` | Overview table or task entries include time/effort estimates |
| `has_pending_markers` | Section contains `[PENDING: ...]` markers |

Also detect at **document level**:
- `doc_has_any_ac`: any acceptance criteria anywhere in the document
- `doc_has_all_ids`: every task has a traceable ID

---

### Step 5 — Build Adaptive Criteria per Section

For each section, compute criterion weights using this formula:

```
content_pct = 100
  − (20 if has_acceptance_criteria else 0)
  − (15 if has_deliverable_paths else 0)
  − (15 if has_dependency_graph else 0)
  − (10 if has_requirements_traceability else 0)
  − (10 if has_design_references else 0)
  − 10   ← structure, always present
minimum content_pct = 20%
```

The resulting criteria set for a section:

| Criterion | Weight | Present when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Acceptance criteria | 20% | `has_acceptance_criteria` in reference section |
| Deliverable paths | 15% | `has_deliverable_paths` in reference section |
| Dependency graph | 15% | `has_dependency_graph` in reference section |
| Requirements traceability | 10% | `has_requirements_traceability` in reference section |
| Design references | 10% | `has_design_references` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section's flags to evaluate how well those criteria are met.

**Section-specific examples:**

- **Header Metadata** (no task fields): content=90%, structure=10%
- **Task Summary / Overview** (has overview table + req mapping in reference): content=80%, req_traceability=10%, structure=10%
- **Task Details** (has AC + deliverables + deps + req_trace + design_refs): content=20%, AC=20%, deliverables=15%, deps=15%, req_trace=10%, design_refs=10%, structure=10%

---

### Step 6 — Score Each Section

#### Header Metadata

Evaluate against reference header fields:

| Sub-criterion | Weight | Checks |
|---|---|---|
| Product/project identification | 30% | product name, project name present |
| Temporal metadata | 20% | generation date, version/status present |
| Document scope | 30% | source documents referenced, pipeline stage |
| Author/ownership | 20% | author or team attribution |

Score = weighted sum of sub-criteria, each rated 0–100%.

#### Task Summary / Overview Section

**Content completeness** sub-formula:
```
score = (task_groups_covered / total_reference_groups) × 40%
      + (per_task_entry_granularity) × 40%
      + (effort_or_counts_present) × 20%
```

Where:
- `task_groups_covered`: count of reference task groups with equivalent participant group
- `per_task_entry_granularity`: 100% if summary has one row per individual task (like reference); 25% if group-level only; 0% if absent
- `effort_or_counts_present`: 100% if task counts or effort estimates are shown in overview; 0% otherwise

**Requirements traceability** sub-formula (when criterion is scored):
```
score = (tasks_with_req_ref_in_overview / total_tasks_in_overview) × 100%
```

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (table_present) × 25%
      + (table_formatted_correctly) × 25%
      + (all_groups_represented) × 25%
```

#### Task Details Section

**Content completeness** sub-formula:
```
score = (task_groups_covered / reference_groups) × 40%
      + min(participant_task_count / reference_task_count, 1.0) × 40%
      + (description_quality) × 20%
```

Where:
- `task_groups_covered`: participant has equivalent task group for each reference group (DB, ING, DIM, FACT, MART, DQ, CFG/ORC, DOC/DOCS, TEST)
- `description_quality`: 0–100% based on: implementation specifics present (notebook names, function signatures), sufficient detail to implement, no ambiguous steps

**Acceptance criteria** sub-formula:
```
score = (tasks_with_any_ac / total_tasks) × 30%
      + (ac_measurable_testable / total_tasks) × 40%
      + (ac_references_artifacts / total_tasks) × 30%
```

Where:
- `ac_measurable_testable`: ACs with concrete verifiable conditions (specific command outputs, row counts, column values, pass/fail assertions)
- `ac_references_artifacts`: ACs that name specific tables, columns, files, functions, or catalog objects

**Deliverable paths** sub-formula:
```
score = (tasks_with_deliverable / total_tasks) × 50%
      + (paths_are_specific_file_paths / tasks_with_deliverable) × 30%
      + (naming_convention_consistent) × 20%
```

**Dependency graph** sub-formula:
```
score = (tasks_with_deps_specified / total_tasks) × 40%
      + (deps_use_task_ids / tasks_with_deps) × 40%
      + (cross_group_deps_captured) × 20%
```

Where:
- Tasks with `Depends on: none` or equivalent count as having deps specified (valid leaf tasks)
- `deps_use_task_ids`: dependencies reference specific task IDs (not just group names)
- `cross_group_deps_captured`: at least some tasks have dependencies on tasks in different groups (e.g., FACT task depends on DIM task)

**Requirements traceability** sub-formula:
```
score = (tasks_with_req_ref / total_tasks) × 60%
      + (req_refs_use_specific_ids / tasks_with_req_ref) × 40%
```

Where:
- `req_refs_use_specific_ids`: references like "FR-001, NFR-003" (specific IDs) score 100%; category-level "FR-TRN, NFR-PERF" score 25%; absent score 0%

**Design references** sub-formula:
```
score = (tasks_with_design_ref / total_tasks) × 60%
      + (design_refs_point_to_specific_sections / tasks_with_design_ref) × 40%
```

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (tasks_organized_by_group) × 25%
      + (task_ids_consistent_scheme) × 25%
      + (within_group_h3_headings) × 25%
```

**Section raw score** = sum of (criterion weight × criterion score) for all criteria in section.

**Section weighted score** = (section_raw_score / 100) × section_weight.

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No task IDs anywhere in document | −5 pts | Untraceability |
| Missing H2 reference section entirely in participant | −5 pts each | Max −10 pts |
| No acceptance criteria anywhere in document | −4 pts | Skip if `doc_has_any_ac` is true |
| More than 30% of tasks lack individual acceptance criteria | −3 pts | Count AC-less tasks / total tasks |
| No deliverable paths on more than 50% of tasks | −3 pts | Major deliverable gap |
| No dependency specification on any task | −3 pts | Unordered task set |
| No requirements traceability on any task | −3 pts | No link to requirements |
| Any task with no description (ID only) | −2 pts per task | Max −6 pts |
| Missing `[PENDING]` markers for open items in reference | −2 pts | Compare pending items |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/TASK-TSK-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-TSK-001
skill: task-checker-tasks
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-TSK-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<path>`
**Reference file:** `<path>`
**Generated:** <today's date>

---

## Score Summary

**The task plan Score: <total>/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 2> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 3> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| **Subtotal** | | | **<subtotal>** | |
| Auto-deducts | | | **<deducts>** | |
| **Total** | | | **<total>/100** | |

**Grade: <grade>**

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| <condition> | −<N> pts | <Yes/No — reason> |

---

## Section Feedback

### Header Metadata (<weighted_score>/<weight> pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

---

### <Section Name> (<weighted_score>/<weight> pts)

**Criteria scored:** Content (<pct>%)[, Acceptance Criteria (20%)][, Deliverable Paths (15%)][, Dependency Graph (15%)][, Requirements Traceability (10%)][, Design References (10%)], Structure (10%)

**Content completeness (<score>/100):**
- Task groups covered: <list>
- Missing groups: <list>
- Task count: participant <N> vs reference <M>
- Description quality: <assessment>

**Acceptance criteria (<score>/100):** *(if applicable)*
- Tasks with AC: <N>/<total>
- Measurable/testable ACs: <N>/<total>
- ACs referencing artifacts: <N>/<total>

**Deliverable paths (<score>/100):** *(if applicable)*
- Tasks with deliverables: <N>/<total>
- Paths are specific file paths: <Y/N>
- Naming convention consistent: <Y/N>

**Dependency graph (<score>/100):** *(if applicable)*
- Tasks with deps specified: <N>/<total>
- Deps use task IDs: <Y/N — pct>
- Cross-group deps captured: <Y/N>

**Requirements traceability (<score>/100):** *(if applicable)*
- Tasks with req ref: <N>/<total>
- Specific IDs vs category labels: <pct specific>

**Design references (<score>/100):** *(if applicable)*
- Tasks with design ref: <N>/<total>

**Structure (<score>/100):**
- H2 present: Yes/No
- Tasks organized by group: Yes/No
- Task IDs consistent scheme: Yes/No
- Within-group headings: Yes/No

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

---

## Improvement Items

List all identified gaps as actionable items, ordered by impact (highest first):

1. **[Section — Criterion]** <specific action> → up to +<N> pts
2. ...

---

## Priority Actions

Top 3–5 changes that will have the greatest score impact:

1. <action> → up to +<N> pts
2. ...

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing AC, deliverables, or dep graph |
| 0–44 | Incomplete | Major sections missing or tasks unidentifiable |
```

Status icons: ✓ = scored ≥ 70% of weight, ⚠ = 40–69%, ✗ = < 40%.

---

### Step 10 — Surface Summary to Console

After writing the report, output to the conversation:

```
╔══════════════════════════════════════════════════════════╗
║  TASK-TSK-001  Tasks Check                               ║
║  Product : <participant product>                         ║
║  Score   : <total>/100   Grade: <grade>                  ║
║  Report  : checks/<trainee_name>/TASK-TSK-<NNN>_check_report<suffix>.md ║
╚══════════════════════════════════════════════════════════╝
```

Then write exactly 5–6 sentences of plain-English verdict following these rules:

1. **Sentence 1** — overall quality and what the participant did well (strongest section or criterion).
2. **Sentence 2** — the single most impactful gap (the criterion or section that lost the most points).
3. **Sentence 3** — task field completeness observation (which fields are present/absent: AC, deliverables, deps, traceability, design refs).
4. **Sentence 4** — requirement traceability and design reference status (specific IDs vs categories, design doc links).
5. **Sentence 5** — the single highest-value fix the participant should make next.
6. **Sentence 6** *(optional)* — note any extra task groups or coverage beyond reference scope.

Do **not** exceed 6 sentences. Do **not** use bullet points in the prose verdict.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing AC, deliverables, or dep graph |
| 0–44 | Incomplete | Major sections missing or tasks unidentifiable |

---

## Cross-Product Evaluation Note

The participant and reference may describe **different products** (e.g., participant = Sales_Orders, reference = GlobalPurchase_Project). In this case:

- **Do not** penalize for different table names, notebook names, or domain-specific task descriptions.
- **Do** evaluate structural completeness: task groups present, task field coverage, AC coverage, dependency graph completeness.
- **Do** evaluate pattern correctness: ID scheme, deliverable path format, traceability depth.
- Content completeness score reflects coverage of equivalent functional pipeline layers, not identical task text.

---

## Notes on Participant Format Variants

Tasks documents may use different organizational formats:

| Participant format | Reference expects | Impact |
|---|---|---|
| Per-task H3 with field list | Per-task H4 with field list | Full credit available if fields present |
| Group-level H2 with task H3s | Group-level H3 with task H4s | No structural penalty; same depth |
| Overview table (group-level) | Overview table (task-level per row) | Per-task granularity criterion reduced |
| Category-level req refs (FR-TRN) | Specific ID refs (FR-003, NFR-001) | Traceability specificity criterion reduced |
| No design reference field | Design reference per task | Design references criterion = 0% |

When format differs, each criterion is evaluated on whether the **equivalent content** exists in any form, not whether it matches the reference's exact field label.
