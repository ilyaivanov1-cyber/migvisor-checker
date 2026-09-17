# MigVisor As-Is Checker

A set of Claude Code skills for evaluating and scoring MigVisor pipeline deliverables against reference files. Each skill covers one task type, detects sections dynamically, applies an adaptive rubric, and writes a structured check report to `checks/`.

---

## Skills

| Skill | Trigger | Evaluates |
|---|---|---|
| `migvisor-task-checker-as-is` | "check my as-is" | As-is analysis document vs reference |
| `migvisor-task-checker-scope` | "check my scope" | Product scope document vs reference |
| `migvisor-task-checker-to-be` | "check my to-be" | To-be design document vs reference (SQL + Mermaid + Python) |
| `migvisor-task-checker-transformation-rules` | "check my transformation rules" | Product-level transformation rules vs reference |
| `migvisor-task-checker-project-rules` | "check my project rules" | Project-level transformation rules vs reference |
| `migvisor-task-checker-validation-report` | "check my validation report" | SmartBuilder validation report vs reference |
| `migvisor-task-checker-design` | "check my design" | Technical design document vs reference (DDL + MERGE + Python + diagrams) |
| `migvisor-task-checker-requirements` | "check my requirements" | Requirements document vs reference (FR + NFR + DQR + AC + source refs) |
| `migvisor-task-checker-tasks` | "check my tasks" | Task list vs reference (task fields, AC, deliverables, dependencies, traceability) |
| `migvisor-task-checker-product-definition` | "check product definition" | Product definition YAML vs reference (ODPS 4.1, N-section YAML-key adaptive scoring) |
| `migvisor-task-checker-build-plan` | "check build plan" | Build plan Markdown vs reference (N-section H2-heading adaptive scoring, SmartBuilder skills) |
| `migvisor-task-checker-architecture-diagram` | "check architecture diagram" | Architecture diagram Markdown vs reference (N-section, pipeline DAG, table properties, lineage chain) |
| `migvisor-task-checker-go-live-checklist` | "check go live checklist" | Go-live checklist vs reference (N-section, checkbox format, task refs, verification steps, principal checks) |
| `migvisor-task-checker-data-dictionary` | "check data dictionary" | Data dictionary Markdown vs reference (N-section per table, column completeness, nullability, FK notation, SCD-2 check) |
| `migvisor-task-checker-pipeline-runbook` | "check pipeline runbook" | Pipeline runbook vs reference (N-section, monitoring checklist, failure response, SQL queries, escalation path) |
| `migvisor-task-checker-bi-connections` | "check bi connections" | BI connections document vs reference (N-section, per-view attribute tables, connection string, BI tool steps, known issues) |
| `migvisor-task-checker-secrets-setup` | "check secrets setup" | Secrets setup runbook vs reference (N-section, scope creation, key registration, verification step, dev/prod separation) |
| `migvisor-task-checker-secrets-rotation-runbook` | "check secrets rotation runbook" | Secrets rotation runbook vs reference (N-section, trigger conditions, rotation procedure, verification, rollback, notification checklist, rotation log) |
| `migvisor-task-checker-uc-permission-audit` | "check uc permission audit" | UC permission audit SQL vs reference (N-section, SHOW GRANTS vs information_schema, catalog/schema/table/view coverage, principal-to-privilege mapping) |
| `migvisor-task-checker-uc-setup` | "check uc setup" | UC bootstrap SQL vs reference (N-section, IF NOT EXISTS guards, catalog + 4 schemas, COMMENT strings, verification step) |
| `migvisor-task-checker-secrets-config` | "check secrets config" | Secrets config Python vs reference (N-section, CLI bootstrap vs accessor module detection, SCOPES dict, scope creation, key registration with getpass, argparse entry point) |

Each skill also accepts `run <skill-name>` as a trigger.

---

## Folder Structure

```
migvisor-as-is-checker/
├── reference/                          # Authoritative reference files (read-only)
│   ├── as-is.md
│   ├── product-scope.md
│   ├── to-be.md
│   ├── product-transformation-rules.md
│   ├── project-transformation-rules.md
│   ├── validation-report.md
│   ├── design.md
│   ├── requirements.md
│   ├── tasks.md
│   ├── product-definition.yaml
│   ├── build-plan.md
│   ├── architecture_diagram.md
│   ├── go_live_checklist.md
│   ├── data_dictionary.md
│   ├── pipeline_runbook.md
│   ├── bi_connections.md
│   ├── secrets_setup.md
│   └── secrets_rotation_runbook.md
├── trainees/                           # One subfolder per trainee
│   └── <trainee_name>/                 # e.g. trainee_1, alice, bob
│       ├── product-scope.md
│       ├── to-be.md
│       ├── product-transformation-rules.md
│       ├── project-transformation-rules.md
│       ├── validation-report.md
│       ├── design.md
│       ├── requirements.md
│       ├── tasks.md
│       ├── product-definition.yaml
│       ├── build-plan.md
│       ├── architecture_diagram.md
│       ├── go_live_checklist.md
│       ├── data_dictionary.md
│       ├── pipeline_runbook.md
│       ├── bi_connections.md
│       ├── secrets_setup.md
│       └── secrets_rotation_runbook.md
├── checks/                             # One subfolder per trainee
│   └── <trainee_name>/
│       └── <task-group>/               # e.g. as-is, scope, tasks, design …
│           └── TASK-*_check_report.md
└── skills/
    └── migvisor-<skill-name>/
        └── SKILL.md
```

Skills auto-detect the trainee name from `trainees/` subdirectories. If a single subfolder exists it is used automatically; if multiple exist, pass `trainee=<name>` at invocation.

## Reference Files

| File | Task |
|---|---|
| `reference/as-is.md` | As-is analysis |
| `reference/product-scope.md` | Product scope |
| `reference/to-be.md` | To-be design |
| `reference/product-transformation-rules.md` | Product transformation rules |
| `reference/project-transformation-rules.md` | Project transformation rules |
| `reference/validation-report.md` | Validation report |
| `reference/design.md` | Technical design |
| `reference/requirements.md` | Requirements |
| `reference/tasks.md` | Task list |
| `reference/product-definition.yaml` | Product definition (ODPS 4.1) |
| `reference/build-plan.md` | SmartBuilder build plan |
| `reference/architecture_diagram.md` | Architecture diagram (pipeline DAG, Delta Lake properties, lineage chain) |
| `reference/go_live_checklist.md` | Go-live checklist (infrastructure, data, security, pipeline, DQ, BI, docs) |
| `reference/data_dictionary.md` | Data dictionary (8 table definitions + SCD-2 glossary) |
| `reference/pipeline_runbook.md` | Pipeline runbook (monitoring checklist, failure response, reprocessing guide, DQ investigation, escalation) |
| `reference/bi_connections.md` | BI connections (per-view attribute tables, SQL Warehouse endpoint, BI tool steps, known issues, access provisioning) |
| `reference/secrets_setup.md` | Secrets setup runbook (scope creation, key registration, verification, dev/prod separation, credential rotation) |
| `reference/secrets_rotation_runbook.md` | Secrets rotation runbook (trigger conditions, rotation procedure, verification steps, rollback, notification checklist, rotation log) |
| `reference/uc_permission_audit.sql` | UC permission audit (SHOW GRANTS per object, schema/table/view coverage, principal-to-privilege mapping) |
| `reference/uc_setup.sql` | UC bootstrap (catalog creation, 4 medallion schemas, IF NOT EXISTS guards, COMMENT strings, verification) |
| `reference/secrets_config.py` | Secrets bootstrap CLI (SCOPES dict, REQUIRED_KEYS, scope creation, getpass key registration, argparse --env) |

---

## Check Reports

All reports are written to `checks/<trainee_name>/<task-group>/` as `TASK-<ID>-001_check_report.md`. If a report already exists the skill increments the suffix (`_v2`, `_v3`, …) and never overwrites.

The `checks/trainee_1/` directory structure is preserved and ready for new submissions. No reports have been generated yet.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing tables, incorrect SQL, or diagrams absent |
| 0–44 | Incomplete | Major sections missing or SQL systematically wrong |

---

## How Skills Work

Every skill follows the same workflow:

1. **Resolve files** — auto-detects participant and reference files from the workspace, or accepts explicit paths.
2. **Detect sections** — builds a scored section list from the reference: Header Metadata + all `##` H2 headings.
3. **Classify code blocks** — tags each block as `SQL_DDL`, `SQL_DML`, `SQL_GRANT`, `SQL_QUERY`, `PYTHON`, `DIAGRAM`, or `OTHER`.
4. **Calculate weights** — N sections, `floor(100/N)` base weight, remainder distributed to highest-complexity sections.
5. **Adaptive rubric** — criterion weights shift per section based on which block types are present (SQL 30%, Python 20%, Diagram 15%, Structure 10%, Content remainder ≥ 25%).
6. **Apply auto-deducts** — global penalties for systematic omissions (missing `IF NOT EXISTS`, absent SK resolver, hardcoded credentials, etc.).
7. **Write report** — `checks/TASK-*_check_report.md` with score table, per-section feedback, improvement items, and priority actions.
8. **Surface summary** — score block + 5–6 sentence plain-English verdict in the conversation.

---

## Repository

[https://github.com/ilyaivanov1-cyber/migvisor-checker](https://github.com/ilyaivanov1-cyber/migvisor-checker)
