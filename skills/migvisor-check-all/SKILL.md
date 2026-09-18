---
name: migvisor-check-all
description: Runs all 13 MigVisor deliverable checks in sequence against the auto-detected trainee workspace and writes a summary score table. Single command — no file paths needed.
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

Run all 13 MigVisor deliverable skills in sequence against one trainee workspace.
No file paths needed — everything is resolved from `workspace.yaml`.
At the end, print a single summary score table.

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

## Step 2 — Run all checks in sequence

Run each skill below in order. For each:
1. Read the skill's SKILL.md to get the full rubric.
2. Resolve the trainee file and reference file using the workspace paths.
3. Score the deliverable.
4. Write the check report to `{checks_dir}/{trainee_name}/{task-group}/`.
5. Print a one-line progress update: `✓ [N/13] <skill-name> — <score>/100 (<grade>)`

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

If a trainee file is missing, mark that check as **[MISSING] — 0/100** and continue to the next.

---

## Step 3 — Write summary report

After all 13 checks, write a summary file to:
`{checks_dir}/{trainee_name}/SUMMARY.md`

```markdown
---
trainee: <trainee_name>
product: <product>
generated: <YYYY-MM-DD>
total_score: <avg>/100
grade: <grade>
---

# Check Summary — <trainee_name> / <product>

| # | Skill | Task ID | Score | Grade |
|---|---|---|---|---|
| 1 | scope | TASK-SC-001 | .../100 | ... |
| 2 | as-is | TASK-AI-001 | .../100 | ... |
| 3 | transformation-rules | TASK-TR-001 | .../100 | ... |
| 4 | project-rules | TASK-PR-001 | .../100 | ... |
| 5 | to-be | TASK-TB-001 | .../100 | ... |
| 6 | design | TASK-DE-001 | .../100 | ... |
| 7 | requirements | TASK-RE-001 | .../100 | ... |
| 8 | tasks | TASK-TA-001 | .../100 | ... |
| 9 | product-definition | TASK-PD-001 | .../100 | ... |
| 10 | build-plan | TASK-BP-001 | .../100 | ... |
| 11 | data-dictionary | TASK-DD-001 | .../100 | ... |
| 12 | pipeline-runbook | TASK-RB-001 | .../100 | ... |
| 13 | validation-report | TASK-VR-001 | .../100 | ... |
| | **Average** | | **<avg>/100** | **<grade>** |

## Top scores
<list top 3>

## Lowest scores
<list bottom 3>

## Main gaps
<2-3 sentences on the most common issues across all checks>
```

---

## Step 4 — Console summary

Print the final score table in the conversation:

```
╔══════════════════════════════════════════════════════════════════╗
║  migvisor-check-all · <trainee_name> · <product> · <date>        ║
╠══════════════════════════════════════════════════════════════════╣
║  Score: <avg>/100 · Grade: <grade>                               ║
╚══════════════════════════════════════════════════════════════════╝

| # | Skill                  | Score    | Grade      |
|---|------------------------|----------|------------|
| 1 | scope                  | .../100  | ...        |
...
|   | Average                | .../100  | ...        |
```

Follow with 3–4 sentences: overall grade, strongest deliverable, weakest deliverable, top priority fix.

---

## Grading scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Ready to proceed |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Major sections missing |
| 0–44 | Incomplete | Fundamental deliverables absent |
