# MigVisor As-Is Checker

A set of Claude Code skills for evaluating and scoring MigVisor pipeline deliverables against reference answer files. Drop any trainee's migVisor workspace into this directory, say **"check all"**, and get a full score report across all deliverables.

---

## Quick Start

1. Drop the trainee's migVisor project folder into this directory (any folder with `products/` + `project/` structure is auto-detected)
2. Say **"check all"**
3. Get individual reports in `checks/<trainee_name>/` and a `SUMMARY.md`

To check a specific deliverable only, use the individual skill trigger (e.g. "check my as-is").

---

## Master Skill

| Skill | Trigger | What it does |
|---|---|---|
| `migvisor-check-all` | "check all" | Runs all 13 checks in sequence, writes SUMMARY.md |

---

## Individual Skills

| Skill | Trigger | Evaluates |
|---|---|---|
| `migvisor-task-checker-scope` | "check my scope" | Product scope document vs reference |
| `migvisor-task-checker-as-is` | "check my as-is" | As-is analysis document vs reference |
| `migvisor-task-checker-transformation-rules` | "check my transformation rules" | Product-level transformation rules vs reference |
| `migvisor-task-checker-project-rules` | "check my project rules" | Project-level transformation rules vs reference |
| `migvisor-task-checker-to-be` | "check my to-be" | To-be design document vs reference (SQL + Mermaid + Python) |
| `migvisor-task-checker-design` | "check my design" | Technical design document vs reference (DDL + MERGE + Python + diagrams) |
| `migvisor-task-checker-requirements` | "check my requirements" | Requirements document vs reference (FR + NFR + DQR + AC + source refs) |
| `migvisor-task-checker-tasks` | "check my tasks" | Task list vs reference (task fields, AC, deliverables, dependencies, traceability) |
| `migvisor-task-checker-product-definition` | "check product definition" | Product definition YAML vs reference (ODPS 4.1, N-section YAML-key adaptive scoring) |
| `migvisor-task-checker-build-plan` | "check build plan" | Build plan Markdown vs reference (N-section H2-heading adaptive scoring, SmartBuilder skills) |
| `migvisor-task-checker-data-dictionary` | "check data dictionary" | Data dictionary Markdown vs reference (N-section per table, column completeness, nullability, FK notation, SCD-2 check) |
| `migvisor-task-checker-pipeline-runbook` | "check pipeline runbook" | Pipeline runbook vs reference (N-section, monitoring checklist, failure response, SQL queries, escalation path) |
| `migvisor-task-checker-validation-report` | "check validation report" | SmartBuilder validation report vs reference |
| `migvisor-task-checker-architecture-diagram` | "check architecture diagram" | Architecture diagram Markdown vs reference (N-section, pipeline DAG, table properties, lineage chain) |
| `migvisor-task-checker-go-live-checklist` | "check go live checklist" | Go-live checklist vs reference (N-section, checkbox format, task refs, verification steps) |
| `migvisor-task-checker-bi-connections` | "check bi connections" | BI connections document vs reference (N-section, per-view attribute tables, connection string, BI tool steps) |
| `migvisor-task-checker-secrets-setup` | "check secrets setup" | Secrets setup runbook vs reference (N-section, scope creation, key registration, dev/prod separation) |
| `migvisor-task-checker-secrets-rotation-runbook` | "check secrets rotation runbook" | Secrets rotation runbook vs reference (trigger conditions, rotation procedure, rollback, notification checklist) |
| `migvisor-task-checker-uc-permission-audit` | "check uc permission audit" | UC permission audit SQL vs reference (SHOW GRANTS, catalog/schema/table/view coverage) |
| `migvisor-task-checker-uc-setup` | "check uc setup" | UC bootstrap SQL vs reference (IF NOT EXISTS guards, catalog + 4 schemas, COMMENT strings) |
| `migvisor-task-checker-secrets-config` | "check secrets config" | Secrets config Python vs reference (SCOPES dict, scope creation, key registration, argparse entry point) |

---

## Folder Structure

```
migvisor-as-is-checker/
├── workspace.yaml                      # Points to trainee workspace and reference answers
├── <TraineeProject>/                   # Any trainee's migVisor workspace (auto-detected)
│   ├── products/<Product>/
│   │   ├── input/product-scope.md
│   │   └── current/
│   │       ├── specifications/
│   │       │   ├── as-is.md
│   │       │   ├── to-be.md
│   │       │   ├── product-transformation-rules/
│   │       │   └── development_plan/
│   │       └── codebase/
│   │           ├── build-plan.md
│   │           ├── validation-report.md
│   │           └── docs/
│   └── project/current/project-transformation-rules/
├── reference/
│   └── answers/
│       ├── module_2/       # scope, as-is
│       ├── module_3/       # transformation rules
│       ├── module_4/       # to-be
│       └── module_5/       # design, requirements, tasks, build-plan, data-dictionary, ...
├── checks/
│   └── <trainee_name>/
│       ├── SUMMARY.md      # Overall score table (written by migvisor-check-all)
│       ├── scope/
│       ├── as-is/
│       ├── to-be/
│       └── ...             # One subfolder per skill
└── skills/
    ├── migvisor-check-all/         # Master skill — runs all 13
    └── migvisor-task-checker-*/    # Individual skills
```

---

## workspace.yaml

```yaml
trainee_workspace: auto        # auto = scan root for any folder with products/ + project/
reference_workspace: ./reference/answers
product: Purchase
checks_dir: ./checks
```

Set `trainee_workspace: auto` to auto-detect any trainee folder. Set it to an explicit path (e.g. `./Inventory_Stock_Project`) to pin a specific trainee.

---

## How Skills Work

Every skill follows the same workflow:

1. **Resolve files** — reads `workspace.yaml`, auto-detects trainee folder, resolves trainee and reference file paths.
2. **Detect sections** — builds a scored section list from the reference: all `##` H2 headings.
3. **Classify code blocks** — tags each block as `SQL_DDL`, `SQL_DML`, `SQL_GRANT`, `SQL_QUERY`, `PYTHON`, `DIAGRAM`, or `OTHER`.
4. **Calculate weights** — N sections, `floor(100/N)` base weight, remainder distributed to highest-complexity sections.
5. **Adaptive rubric** — criterion weights shift per section based on which block types are present.
6. **Apply auto-deducts** — global penalties for systematic omissions.
7. **Write report** — `checks/<trainee_name>/<task-group>/TASK-*_check_report.md`.
8. **Surface summary** — score + 5–6 sentence plain-English verdict.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing tables, incorrect SQL, or diagrams absent |
| 0–44 | Incomplete | Major sections missing or SQL systematically wrong |
