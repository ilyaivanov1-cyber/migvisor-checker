---
name: migvisor-check-all
description: Runs all 21 MigVisor deliverable checks in sequence against the auto-detected trainee workspace and writes a summary score table with per-skill narratives. Single command — no file paths needed.
---

# Skill: migvisor-check-all

## Identity

- **Name:** `migvisor-check-all`
- **Trigger phrases:**
  - "check all"
  - "run all checks"
  - "check all deliverables"
  - "run migvisor-check-all"
  - "score all"

---

## Purpose

Run all 21 MigVisor deliverable skills in sequence against one trainee workspace.
No file paths needed — everything is resolved from `workspace.yaml`.
After every run, write `SUMMARY.md` with the score table AND a 4-5 sentence narrative for every skill.

---

## Step 1 — Resolve workspace

Read `workspace.yaml` at the project root:

```yaml
trainee_workspace: auto        # auto-detect OR explicit path
reference_workspace: ./reference/answers
product: Purchase
checks_dir: ./checks
```

**Auto-detection** (when `trainee_workspace: auto`):
- Scan the project root for any folder containing both `products/` and `project/` subdirectories.
- If exactly one found → use it. Trainee name = folder name.
- If multiple found → list them and ask: "Multiple trainee workspaces found: [list]. Run with `trainee=<name>` to select one."
- If none found → ask the user to provide the path explicitly.

---

## Step 2 — Run all checks and collect results

Run each skill below in order. **For each skill, you MUST complete ALL three sub-steps before moving to the next skill — do not skip sub-step C.**

### Per-skill procedure (repeat for all 21):

**A. Score the deliverable**
1. Read the skill's SKILL.md to get the full rubric.
2. Resolve the trainee file and reference file using the workspace paths.
3. If the trainee file is missing → score = 0/100, grade = Incomplete, go to sub-step C.
4. Score the deliverable following the rubric.
5. Write the check report to `{checks_dir}/{trainee_name}/{task-group}/` (increment suffix if file exists).

**B. Print progress line**
```
✓ [N/21] <skill-name> — <score>/100 (<grade>)
```

**C. Write the 4-5 sentence summary (MANDATORY — do not skip)**

Immediately after scoring, write the summary for this skill into your working notes using exactly this format:

```
SKILL_N_SUMMARY:
### N. <skill-name> — <score>/100 (<Grade>)
<Sentence 1: final score and grade.> <Sentence 2: what was done well — best-scoring section or strongest element.> <Sentence 3: main gap — most critical missing or weak element.> <Sentence 4: top priority fix with estimated points recoverable.> <Sentence 5: second priority fix or encouraging note.>

**Priority actions:**
1. <specific fix #1> — +N pts
2. <specific fix #2> — +N pts
```

For MISSING files use:
```
### N. <skill-name> — 0/100 (Incomplete)
This file was not submitted. Expected at `{trainee_workspace}/<relative-path>`. Reference answer is at `{reference_workspace}/<ref-path>`. Submitting this deliverable would add approximately 4.8 points to the overall average score. Create the file using the reference as a guide.
```

---

### Skill table

| # | Skill | Trainee file (relative to trainee_workspace) | Reference file (relative to reference_workspace) | Output dir |
|---|---|---|---|---|
| 1 | migvisor-task-checker-scope | `products/{product}/input/product-scope.md` | `module_2/0 product-scope.md` | `scope/` |
| 2 | migvisor-task-checker-as-is | `products/{product}/current/specifications/as-is.md` | `module_2/1 as-is.md` | `as-is/` |
| 3 | migvisor-task-checker-transformation-rules | `products/{product}/current/specifications/product-transformation-rules/product-transformation-rules.md` | `module_3/product-transformation-rules/product-transformation-rules.md` | `transformation-rules/` |
| 4 | migvisor-task-checker-project-rules | `project/current/project-transformation-rules/project-transformation-rules.md` | `module_3/project-transformation-rules/project-transformation-rules.md` | `project-rules/` |
| 5 | migvisor-task-checker-to-be | `products/{product}/current/specifications/to-be.md` | `module_4/to-be.md` | `to-be/` |
| 6 | migvisor-task-checker-design | `products/{product}/current/codebase/docs/design.md` | `module_5/development_plan/design.md` | `design/` |
| 7 | migvisor-task-checker-requirements | `products/{product}/current/specifications/development_plan/requirements.md` | `module_5/development_plan/requirements.md` | `requirements/` |
| 8 | migvisor-task-checker-tasks | `products/{product}/current/specifications/development_plan/tasks.md` | `module_5/development_plan/tasks.md` | `tasks/` |
| 9 | migvisor-task-checker-product-definition | `products/{product}/current/specifications/development_plan/product-definition.yaml` | `module_5/development_plan/product-definition.yaml` | `definition/` |
| 10 | migvisor-task-checker-build-plan | `products/{product}/current/codebase/build-plan.md` | `module_5/codebase/build-plan.md` | `build-plan/` |
| 11 | migvisor-task-checker-data-dictionary | `products/{product}/current/codebase/docs/data-dictionary.md` | `module_5/codebase/docs/data_dictionary.md` | `data-dictionary/` |
| 12 | migvisor-task-checker-pipeline-runbook | `products/{product}/current/codebase/docs/runbook.md` | `module_5/codebase/docs/pipeline_runbook.md` | `pipeline-runbook/` |
| 13 | migvisor-task-checker-validation-report | `products/{product}/current/codebase/validation-report.md` | `module_5/reports/validation/report.md` | `validation/` |
| 14 | migvisor-task-checker-architecture-diagram | `products/{product}/current/codebase/docs/architecture_diagram.md` | `module_5/codebase/docs/architecture_diagram.md` | `architecture/` |
| 15 | migvisor-task-checker-go-live-checklist | `products/{product}/current/codebase/docs/go_live_checklist.md` | `module_5/codebase/docs/go_live_checklist.md` | `go-live/` |
| 16 | migvisor-task-checker-bi-connections | `products/{product}/current/codebase/docs/bi/bi_connections.md` | `module_5/codebase/config/bi_connections.md` | `bi-connections/` |
| 17 | migvisor-task-checker-secrets-setup | `products/{product}/current/codebase/config/secrets_setup.md` | `module_5/codebase/config/secrets_setup.md` | `secrets-setup/` |
| 18 | migvisor-task-checker-secrets-rotation-runbook | `products/{product}/current/codebase/config/secrets_rotation_runbook.md` | `module_5/codebase/config/secrets_rotation_runbook.md` | `secrets-rotation/` |
| 19 | migvisor-task-checker-uc-permission-audit | `products/{product}/current/codebase/config/uc_permission_audit.sql` | `module_5/codebase/config/uc_permission_audit.sql` | `uc-permission-audit/` |
| 20 | migvisor-task-checker-uc-setup | `products/{product}/current/codebase/config/uc_setup.sql` | `module_5/codebase/config/uc_setup.sql` | `uc-setup/` |
| 21 | migvisor-task-checker-secrets-config | `products/{product}/current/codebase/config/secrets_config.py` | `module_5/codebase/config/secrets_config.py` | `secrets-config/` |

---

## Step 3 — Write SUMMARY.md

After all 21 checks are complete, write `{checks_dir}/{trainee_name}/SUMMARY.md` (overwrite if exists).

Use the scores and SKILL_N_SUMMARY notes collected in Step 2.

```markdown
---
trainee: <trainee_name>
product: <product>
generated: <YYYY-MM-DD>
---

# Check Summary — <trainee_name> / <product>

## Score Table

| # | Skill | Score | Grade |
|---|---|---|---|
| 1 | scope | .../100 | ... |
| 2 | as-is | .../100 | ... |
| 3 | transformation-rules | .../100 | ... |
| 4 | project-rules | .../100 | ... |
| 5 | to-be | .../100 | ... |
| 6 | design | .../100 | ... |
| 7 | requirements | .../100 | ... |
| 8 | tasks | .../100 | ... |
| 9 | product-definition | .../100 | ... |
| 10 | build-plan | .../100 | ... |
| 11 | data-dictionary | .../100 | ... |
| 12 | pipeline-runbook | .../100 | ... |
| 13 | validation-report | .../100 | ... |
| 14 | architecture-diagram | .../100 | ... |
| 15 | go-live-checklist | .../100 | ... |
| 16 | bi-connections | .../100 | ... |
| 17 | secrets-setup | .../100 | ... |
| 18 | secrets-rotation-runbook | .../100 | ... |
| 19 | uc-permission-audit | .../100 | ... |
| 20 | uc-setup | .../100 | ... |
| 21 | secrets-config | .../100 | ... |
| | **Average (submitted)** | **<avg>/100** | **<grade>** |
| | **Average (all 21)** | **<avg>/100** | **<grade>** |

---

## Skill Summaries

[Paste all 21 SKILL_N_SUMMARY blocks collected in Step 2 here, in order.]

---

## Priority Actions — Top Fixes Across All Skills

List the top 8 highest-impact fixes across all submitted skills, sorted by estimated points recoverable. Each row must name the skill, the specific fix, and the estimated gain.

| # | Skill | Fix | Est. gain |
|---|---|---|---|
| 1 | <skill> | <specific fix> | +N pts |
| 2 | <skill> | <specific fix> | +N pts |
| 3 | <skill> | <specific fix> | +N pts |
| 4 | <skill> | <specific fix> | +N pts |
| 5 | <skill> | <specific fix> | +N pts |
| 6 | <skill> | <specific fix> | +N pts |
| 7 | <skill> | <specific fix> | +N pts |
| 8 | <skill> | <specific fix> | +N pts |

---

## Overall Verdict

**Top 3:** <skill> (<score>), <skill> (<score>), <skill> (<score>)
**Bottom 3 (submitted):** <skill> (<score>), <skill> (<score>), <skill> (<score>)

<2-3 sentences: overall grade, most common gap, highest-impact action.>
```

---

## Step 4 — Console output

Print the score table in the conversation followed by 3-4 sentences: overall grade, strongest deliverable, weakest submitted deliverable, top priority fix.

---

## Grading scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Ready to proceed |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Major sections missing |
| 0–44 | Incomplete | Fundamental deliverables absent |
