# Skill: task-checker-build-plan

## Identity

| Field | Value |
|---|---|
| Skill number | 25 |
| Skill name | task-checker-build-plan |
| Task ID | TASK-BP-001 |
| Output file | `checks/<trainee_name>/build-plan/TASK-BP-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check build plan"
- "validate build plan"
- "score build plan"
- "compare build plan"
- "check my build plan"
- "run task-checker-build-plan"
- "run 25-migvisor-task-checker-build-plan"
- "25"

---

## Invocation Syntax

```
/task-checker-build-plan
/task-checker-build-plan participant=<path> reference=<path> trainee=<name>
run task-checker-build-plan
run 25-migvisor-task-checker-build-plan
```

---

## Preconditions

- A participant `build-plan.md` file must exist (default: `trainees/<trainee_name>/build-plan.md`)
- A reference `build-plan.md` file must exist (default: `reference/build-plan.md`)
- The `checks/<trainee_name>/build-plan/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/build-plan.md` | `participant=` |
| Reference (final) | `reference/build-plan.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/build-plan.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/build-plan.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `build-plan.md` in workspace root

Auto-detection fallback order for reference:
1. `reference/build-plan.md`

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags. If `trainee=<name>` is provided and `participant=` is not, resolve participant as `trainees/<name>/build-plan.md`.
2. Otherwise run auto-detection sequences above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] build-plan.md.
   Provide an explicit path: /task-checker-build-plan participant=<path>
   ```
5. Read both files in full.
6. Extract header metadata from each file (lines before the first `##`):
   - Product name (H1 title or `**Product:**` field)
   - Project name
   - Generated date
   - Total task count and group count
   - Target catalog/workspace
   - SmartBuilder skills referenced (`/12`, `/13`, etc.)
   - Any `[PENDING]` or blocker references at document level

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — if reference has 5 H2 headings (Overview, Build Phases, Task-to-Skill Mapping, Execution Instructions, Dependencies Graph):
- N = 6
- Section list: Header Metadata, Overview, Build Phases, Task-to-Skill Mapping, Execution Instructions, Dependencies Graph

**Cross-product section matching** — the participant may use different H2 titles for equivalent functional areas. Match by semantic equivalence:

| Reference section | Participant equivalent examples |
|---|---|
| Overview | Build Overview, Summary, Introduction, Plan Summary |
| Build Phases | Build Phases, Execution Phases, Phase Plan, Phases |
| Task-to-Skill Mapping | File Manifest, Task Manifest, Artifact Map, Task List, Task Index |
| Execution Instructions | Generation Instructions, Running SmartBuilder, How to Generate, Invocation Guide |
| Dependencies Graph | Dependency Graph, DAG, Dependency Diagram, Execution Graph |
| Pending Decision Blockers | Pending Decisions, Blockers, Open Items, Decision Log |

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. Build Phases — most complex: per-phase rationale, task lists, execution ordering, cross-phase dependencies, blocker documentation
2. Task-to-Skill Mapping / File Manifest — largest table: all task IDs, file paths, group assignments, skill assignments
3. Execution Instructions / Generation Instructions — invocation examples, per-phase sequencing, parallel execution guidance, blocked task handling
4. Dependencies Graph — diagram completeness, critical path, parallel-task identification
5. Overview / Build Overview — scope, metrics, product summary
6. Header Metadata — simplest
7. Any additional participant-only sections (extra content; noted but not scored)

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example** (N=6, base=16, remainder=4):
- Build Phases → 17 pts
- Task-to-Skill Mapping → 17 pts
- Execution Instructions → 17 pts
- Dependencies Graph → 17 pts
- Overview → 16 pts
- Header Metadata → 16 pts

---

### Step 4 — Classify Section Content Types

For each section in the **reference** and **participant** files, detect:

| Flag | True when |
|---|---|
| `has_task_table` | Section contains a table with task IDs and file paths |
| `has_skill_assignments` | Tasks are mapped to a SmartBuilder skill (`/12`, `/13`, or named skill) |
| `has_phase_rationale` | Phases include a goal statement, rationale, or purpose description |
| `has_execution_order` | Section specifies which tasks run sequentially vs. in parallel within a phase |
| `has_dependency_diagram` | Section contains a visual or textual dependency graph (ASCII, Mermaid, table) |
| `has_invocation_examples` | Section contains code blocks showing how to invoke SmartBuilder skills per task |
| `has_pending_markers` | Section references [PENDING], blocked tasks, open decisions |
| `has_blocker_mitigation` | Blocked tasks have a documented mitigation strategy (placeholder tokens, partial generation) |
| `has_deliverable_counts` | Section states expected file counts, type breakdowns, or deliverable totals |

Also detect at **document level**:
- `doc_has_task_ids`: any tasks carry traceable IDs (TASK-*, DB-*, ING-*, CFG-*, etc.)
- `doc_has_file_paths`: any section lists specific output file paths
- `doc_has_skill_refs`: any section references SmartBuilder skills by name or number
- `doc_has_phases`: any section organizes work into sequential build phases
- `doc_has_dep_info`: any section contains dependency or ordering information

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (20 if has_task_table else 0)
  − (10 if has_skill_assignments else 0)
  − (15 if has_invocation_examples else 0)
  − (15 if has_dependency_diagram else 0)
  − (10 if has_blocker_mitigation else 0)
  − 10   ← structure/conventions, always present
minimum content_pct = 20%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Task table | 20% | `has_task_table` in reference section |
| Skill assignments | 10% | `has_skill_assignments` in reference section |
| Invocation examples | 15% | `has_invocation_examples` in reference section |
| Dependency diagram | 15% | `has_dependency_diagram` in reference section |
| Blocker mitigation | 10% | `has_blocker_mitigation` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**

- **Header Metadata** — content 90%, structure 10%
- **Overview / Build Overview** — content 90%, structure 10%
- **Build Phases** (has task_table + execution_order, no dep diagram, no invocation, no mitigation in reference) — content 70%, task table 20%, structure 10%
- **Task-to-Skill Mapping** (has task_table + skill_assignments) — content 70%, task table 20%, skill assignments 10%, structure 10% → wait, content = 100-20-10-0-0-0-10 = 60%; so: content 60%, task table 20%, skill assignments 10%, structure 10%
- **Execution Instructions** (has invocation_examples) — content 75%, invocation examples 15%, structure 10%
- **Dependencies Graph** (has dep diagram) — content 75%, dep diagram 15%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

Evaluate against the reference header fields:

| Sub-criterion | Weight | Checks |
|---|---|---|
| Product/project identification | 30% | Product name, project name present |
| Temporal metadata | 20% | Generated date, pipeline stage present |
| Plan scope | 30% | Total task count, group count, catalog/workspace reference |
| SmartBuilder skill references | 20% | Skills used (`/12`, `/13`, etc.) identified in header or intro |

Score = weighted sum of sub-criteria, each rated 0–100%.
`[PENDING]` or `TBD` values score 50% on affected sub-criteria.

#### Overview / Build Overview Section

**Content completeness** sub-formula:
```
score = (product_context_present) × 30%
      + (plan_scope_described) × 30%
      + (skill_split_described) × 20%
      + (phase_count_stated) × 20%
```

Where:
- `product_context_present`: product name, pipeline type (medallion/etc.), and target platform identified
- `plan_scope_described`: SmartBuilder scope described (which artifacts will be generated); total files or task count stated
- `skill_split_described`: which tasks go to which SmartBuilder skill (e.g., DB tasks → /12, ETL tasks → /13) is explained
- `phase_count_stated`: number of build phases declared with their names or purposes

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (intro_narrative_or_table_present) × 25%
      + (content_organized_logically) × 25%
      + (no_orphaned_content) × 25%
```

#### Build Phases Section

**Content completeness** sub-formula:
```
score = (phases_present / reference_phase_count) × 40%
      + (phases_have_goal_or_rationale) × 30%
      + (execution_order_within_phase) × 30%
```

Where:
- `phases_present`: count of participant build phases matched to reference phases (by semantic layer: foundation/env, pipeline/etl, mart/serving, security, testing/docs), capped at 1.0
- `phases_have_goal_or_rationale`: percentage of phases that include a goal statement, rationale, or purpose description (0–100%)
- `execution_order_within_phase`: percentage of phases that specify the ordering or parallelism of tasks within the phase (sequential → parallel → sequential, or explicit lists)

**Task table** sub-formula (when criterion is scored):
```
score = (phases_with_task_table / total_phases) × 40%
      + (task_ids_in_table / total_tasks_in_phases) × 30%
      + (file_paths_in_table / total_tasks_in_phases) × 30%
```

Where:
- `phases_with_task_table`: phases that include a table or list of tasks with IDs
- `task_ids_in_table`: tasks in phase tables that carry traceable IDs
- `file_paths_in_table`: tasks in phase tables that include a specific output file path

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (phases_use_h3_headings) × 25%
      + (phase_names_descriptive) × 25%
      + (phases_sequential_ordered) × 25%
```

#### Task-to-Skill Mapping / File Manifest Section

**Content completeness** sub-formula:
```
score = (task_groups_covered / reference_group_count) × 40%
      + min(participant_task_count / reference_task_count, 1.0) × 40%
      + (file_type_labels_present) × 20%
```

Where:
- `task_groups_covered`: count of participant task groups with equivalent reference groups (DB, GRANT, COMMON, ING, DIM, FACT, MART, DQ, CFG, DOC, TEST or equivalent)
- `participant_task_count`: total task entries in the manifest
- `file_type_labels_present`: tasks have a type/category label (db, etl, config, test, docs or equivalent)

**Task table** sub-formula (when criterion is scored):
```
score = (tasks_with_id / total_tasks) × 40%
      + (tasks_with_file_path / total_tasks) × 40%
      + (paths_are_specific_not_generic / tasks_with_file_path) × 20%
```

Where:
- `tasks_with_id`: tasks that carry a traceable ID (TASK-DB-01, DB-001, etc.)
- `tasks_with_file_path`: tasks that specify a concrete output file path
- `paths_are_specific_not_generic`: paths name a specific file (e.g., `src/db/create_dim_customer.sql`) vs. a directory only

**Skill assignments** sub-formula (when criterion is scored):
```
score = (tasks_with_skill_ref / total_tasks) × 60%
      + (skill_refs_are_specific / tasks_with_skill_ref) × 40%
```

Where:
- `tasks_with_skill_ref`: tasks mapped to a SmartBuilder skill (`/12`, `/13`, `/12_migvisor_smartbuilder_generate-db`, etc.)
- `skill_refs_are_specific`: skill references name the exact skill (not just "SmartBuilder" generically)

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (tasks_grouped_by_group_or_type) × 25%
      + (table_format_consistent) × 25%
      + (all_groups_represented) × 25%
```

#### Execution Instructions / Generation Instructions Section

**Content completeness** sub-formula:
```
score = (skills_covered / reference_skill_count) × 30%
      + (phase_sequence_described) × 30%
      + (parallel_execution_guidance) × 20%
      + (validation_step_mentioned) × 20%
```

Where:
- `skills_covered`: SmartBuilder skills with dedicated invocation instructions (participant has instructions for all skills used)
- `phase_sequence_described`: instructions follow the phase order or provide a sequenced task list
- `parallel_execution_guidance`: document explains which tasks can run concurrently
- `validation_step_mentioned`: a post-generation validation step is referenced (`/14` or equivalent)

**Invocation examples** sub-formula (when criterion is scored):
```
score = (skills_with_code_examples / total_skills) × 50%
      + (examples_per_phase_provided) × 30%
      + (blocked_task_handling_documented) × 20%
```

Where:
- `skills_with_code_examples`: each SmartBuilder skill has at least one code block showing the invocation syntax
- `examples_per_phase_provided`: code examples are organized by phase or task sequence (not just a random list)
- `blocked_task_handling_documented`: instructions state how to handle blocked tasks (placeholder tokens, skip/defer guidance)

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (per_skill_subsections_present) × 25%
      + (code_blocks_formatted) × 25%
      + (prerequisite_check_mentioned) × 25%
```

#### Dependencies Graph Section

**Content completeness** sub-formula:
```
score = (all_task_groups_in_graph / reference_group_count) × 40%
      + (inter_group_dependencies_shown) × 30%
      + (critical_path_identifiable) × 30%
```

Where:
- `all_task_groups_in_graph`: count of task groups represented in the dependency diagram vs. reference
- `inter_group_dependencies_shown`: diagram shows which groups depend on which (e.g., DIM depends on ING, FACT depends on DIM)
- `critical_path_identifiable`: the main execution path (longest chain of dependencies) can be traced from the diagram

**Dependency diagram** sub-formula (when criterion is scored):
```
score = (diagram_present) × 30%
      + (diagram_is_readable) × 30%
      + (intra_phase_parallelism_shown) × 20%
      + (runtime_dag_or_lineage_documented) × 20%
```

Where:
- `diagram_present`: any visual representation of dependencies exists (ASCII art, Mermaid, table with arrows)
- `diagram_is_readable`: diagram has node labels (not just letters), directional arrows, and phase grouping
- `intra_phase_parallelism_shown`: diagram or legend indicates which tasks within a phase can run in parallel
- `runtime_dag_or_lineage_documented`: execution-time ordering (nightly job DAG or lineage_key propagation path) is documented separately from code-generation order

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (diagram_syntax_valid) × 25%
      + (phase_labels_present) × 25%
      + (legend_or_color_coding_present) × 25%
```

#### Pending Decision Blockers Section (participant-only or extra reference section)

If the reference file has a Pending Decision Blockers section (H2), score it as a regular section with:

**Content completeness** sub-formula:
```
score = (pending_items_documented / reference_pending_count) × 40%
      + (impacted_tasks_listed_per_item) × 30%
      + (owner_and_target_date_present) × 30%
```

**Blocker mitigation** sub-formula (when criterion is scored):
```
score = (items_with_mitigation / total_pending_items) × 50%
      + (mitigation_uses_placeholder_tokens / items_with_mitigation) × 30%
      + (partial_generation_guidance_present) × 20%
```

#### Generic Section Fallback (any reference section not matching named types above)

```
content_pct = (sub_sections_present / reference_sub_sections) × 60%
            + (content_non_empty / sub_sections_present) × 40%
```

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No task IDs anywhere in document | −5 pts | Skip if `doc_has_task_ids` is true |
| No file paths/deliverables anywhere in document | −4 pts | Skip if `doc_has_file_paths` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| No SmartBuilder skill reference anywhere | −3 pts | Skip if `doc_has_skill_refs` is true |
| No dependency or phase ordering information anywhere | −3 pts | Skip if `doc_has_dep_info` is true |
| No build phases defined anywhere | −3 pts | Skip if `doc_has_phases` is true |
| Pending decisions referenced in phases but not documented anywhere | −2 pts | Check if PENDING items mentioned in phases have a documentation section |
| Any task entry has no file path (ID only) | −2 pts per occurrence | Max −6 pts total |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/build-plan/TASK-BP-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/build-plan/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-BP-001
skill: task-checker-build-plan
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-BP-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<path>`
**Reference file:** `<path>`
**Generated:** <today's date>

---

## Score Summary

**The build plan Score: <total>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header) | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 2> | <ref title> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 3> | <ref title> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| ... | | | | | |
| **Subtotal** | | | | **<subtotal>** | |
| Auto-deducts | | | | **<deducts>** | |
| **Total** | | | | **<total>/100** | |

**Grade: <grade>**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| <ref title> | <participant title> or [MISSING] | exact / semantic / missing |

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

**Improvement items:**
- [ ] <specific action>

---

### <Reference Section> → participant: <matched title> (<weighted_score>/<weight> pts)

**Criteria scored:** Content (<pct>%)[, Task Table (20%)][, Skill Assignments (10%)][, Invocation Examples (15%)][, Dependency Diagram (15%)][, Blocker Mitigation (10%)], Structure (10%)

**Content completeness (<score>/100):**
- <key sub-criteria with values>

**Task table (<score>/100):** *(if applicable)*
- Tasks with ID: <N>/<total>
- Tasks with file path: <N>/<total>
- Paths are specific: <pct>

**Skill assignments (<score>/100):** *(if applicable)*
- Tasks with skill ref: <N>/<total>
- Skill refs are specific: <pct>

**Invocation examples (<score>/100):** *(if applicable)*
- Skills with code examples: <N>/<total>
- Examples per phase: Yes/No
- Blocked task handling documented: Yes/No

**Dependency diagram (<score>/100):** *(if applicable)*
- Diagram present: Yes/No
- Readable with labels: Yes/No
- Parallelism shown: Yes/No
- Runtime DAG documented: Yes/No

**Blocker mitigation (<score>/100):** *(if applicable)*
- Items with mitigation: <N>/<total>
- Placeholder tokens used: Yes/No

**Structure (<score>/100):**
- H2 heading present: Yes/No
- <structure detail>

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

**Improvement items:**
- [ ] <specific action>

---

## Extra Sections (participant-only, not in reference)

- **<section title>** — <brief description>. No score impact.

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
| 45–59 | Needs work | Missing task manifest, phases, or skill assignments |
| 0–44 | Incomplete | Major sections absent or no task identifiers |
```

Status icons: ✓ = scored ≥ 70% of weight, ⚠ = 40–69%, ✗ = < 40%.

---

### Step 10 — Surface Summary to Console

After writing the report, output to the conversation:

```
╔══════════════════════════════════════════════════════════╗
║  TASK-BP-001  Build Plan Check                           ║
║  Product : <participant product>                         ║
║  Score   : <total>/100   Grade: <grade>                  ║
║  Report  : checks/<trainee_name>/build-plan/TASK-BP-001_check_report<suffix>.md ║
╚══════════════════════════════════════════════════════════╝
```

Then write exactly 5–6 sentences of plain-English verdict following these rules:

1. **Sentence 1** — overall quality and what the participant did well (strongest section or criterion).
2. **Sentence 2** — the single most impactful gap (the section or criterion that lost the most points).
3. **Sentence 3** — structural observation: how well the participant's sections map to the reference, any naming differences, and whether extra sections add value.
4. **Sentence 4** — state the final score explicitly: "The build plan scores **<total>/100** (<grade>)" and identify the next most important fix.
5. **Sentence 5** — the single highest-value actionable change the participant should make before resubmitting.
6. **Sentence 6** *(optional)* — note any extra sections or content depth that goes beyond the reference scope and adds meaningful value.

Do **not** exceed 6 sentences. Do **not** use bullet points in the prose verdict. The final score **must appear as a number** in sentence 4.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing task manifest, phases, or skill assignments |
| 0–44 | Incomplete | Major sections absent or no task identifiers |

---

## Cross-Product Evaluation Note

The participant and reference describe **different products** (e.g., participant = Sales_Orders, reference = GlobalPurchase_Project). In this case:

- **Do not** penalize for different table names, notebook names, task IDs, or product-specific file paths.
- **Do** evaluate structural completeness: required sections present, task IDs exist, file paths specific, phases defined, skill assignments present.
- **Do** evaluate pattern correctness: ID scheme, file path format, phase rationale format, invocation code block format, dependency diagram format.
- **Do not** penalize for a different number of phases — score phase coverage by functional layer equivalence (foundation/env, pipeline, mart/serving, security, testing/docs) not by count match.
- **Do not** penalize for pending decision items that differ between products — each product has its own open decisions; score the format and completeness of the documentation, not the decisions themselves.
- Content completeness reflects coverage of equivalent functional pipeline layers, not identical task text or identical SmartBuilder skill numbers.

---

## Notes on Participant Format Variants

Build plan documents may use different organizational formats:

| Participant format | Reference expects | Impact |
|---|---|---|
| Numbered H2 headings (`## 1. Build Overview`) | Unnumbered H2 headings (`## Overview`) | No penalty — semantic match applies |
| Flat task list instead of grouped tables | Per-group tables in manifest section | Task table criterion reduced if groups not distinguishable |
| Mermaid diagram | ASCII art dependency graph | Full credit for dependency diagram criterion — format does not matter |
| Separate Pending Decisions section | Inline PENDING markers within phases | If pending items are documented somewhere, no auto-deduct; score in whichever section they appear |
| Per-phase deliverable count instead of flat manifest | Flat Task-to-Skill Mapping table | Score file manifest / task table criteria based on wherever file paths and task IDs appear — may be across multiple sections |
| `{{PLACEHOLDER}}` tokens in blocked tasks | `[PENDING]` markers | Equivalent — both indicate acknowledged deferrals |
| Skill numbers (`/12`, `/13`) | Full skill names (`/12_migvisor_smartbuilder_generate-db`) | No penalty — shorthand references score full credit |
