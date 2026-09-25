# Check Report: build-plan — Inventory_Stock_Project / Purchase

**Skill:** migvisor-task-checker-build-plan (#10 of 21)
**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Checked:** 2026-09-25
**Score:** 67 / 100
**Grade:** Acceptable

---

## Cross-File Reads

| File | Status | Notes |
|---|---|---|
| `specifications/development_plan/tasks.md` | Read | 34 tasks across 4 phases; TASK-001 through TASK-034; build-plan phases match tasks.md structure |
| `codebase/docs/design.md` | Read | Correct architecture, QA chain, MERGE INTO pattern; build-plan constraint tables partially reference design.md |

---

## Rubric Sections

### Section 1 — Build Phases (Overview + Phase structure)

**Score: 22 / 25**

The build-plan defines 4 phases:
- Phase 1: DDL (8 tasks: TASK-001 through TASK-008)
- Phase 2: ETL + Config (9 tasks: TASK-009 through TASK-019)
- Phase 3: Tests / BI / Docs (7 tasks: TASK-020 through TASK-026)
- Phase 4: Mart + DQ (8 tasks: TASK-027 through TASK-034)

All 34 tasks from tasks.md are accounted for. Each phase has an acceptance gate (prerequisite checklist). The phase structure is logical and follows the medallion architecture build order (DDL before ETL before Tests before Mart).

Cross-file check: task counts per phase are consistent with tasks.md groupings.

Deduction (-3): Phase 4 (Mart + DQ) appears as an appendix to the main plan rather than a fully integrated phase with the same detail level as Phases 1-3. The acceptance gate for Phase 4 is less developed than for Phases 1-3.

### Section 2 — Task-to-Skill Mapping

**Score: 14 / 15**

The Task-to-Skill Mapping table assigns each task to its generating SmartBuilder skill. All 34 tasks are mapped.

Deduction (-1): The skill names used are the shortened forms (`/smartbuilder_generate-db`, `/smartbuilder_generate-etl`) rather than the full canonical SmartBuilder skill names (`/12_migvisor_smartbuilder_generate-db`, `/13_migvisor_smartbuilder_generate-etl`). The rubric expects the full skill invocation names as they appear in the SmartBuilder skill registry. While the shortened names are recognizable, they would not be directly usable as CLI commands.

### Section 3 — Dependency Graph

**Score: 13 / 15**

The Full Task Dependency Graph (ASCII art) is present and covers all 34 tasks with correct dependency arrows. The graph shows DDL tasks in parallel where applicable and linear dependencies for ETL tasks. TASK-016 correctly depends on TASK-015 (staging must be populated before migrate).

Deduction (-2): The dependency graph uses ASCII art that represents parallel branches well but does not distinguish between hard dependencies (must complete before) and soft dependencies (should complete before). The reference's graph is more explicit about dependency types.

### Section 4 — Prerequisite Checklist

**Score: 12 / 15**

A Prerequisite Checks section contains 5 verification commands (Databricks CLI + SQL) that confirm the environment is ready before execution. These cover: Unity Catalog access, schema existence, etl_cutoff seeding, lineage_run table, and JDBC connectivity check placeholder.

Deduction (-3): The checklist commands reference specific CLI tools and SQL patterns correctly, but several commands use catalog-unqualified table names that would fail if the active catalog is not set to `inventory_stock`. All queries should use three-part names (`inventory_stock.bronze.etl_cutoff`) for portability.

### Section 5 — Execution Instructions (MISSING)

**Score: 0 / 20**

The Execution Instructions section — which the rubric requires to contain per-phase CLI invocation code blocks for triggering the SmartBuilder skill for each task — is entirely absent. The reference provides a dedicated "Execution Instructions" section with one CLI code block per phase showing the exact command to execute: e.g.:
```
/12_migvisor_smartbuilder_generate-db --task TASK-001 --product Purchase
```

The trainee's build-plan has a Task-to-Skill Mapping table and a Dependency Graph, but no section containing executable CLI commands that an engineer could copy and run to regenerate each task's output. This is the most significant gap.

### Section 6 — Pending Decisions

**Score: 6 / 10**

Four pending decisions are documented (PD-001, PD-002, PD-003, QA-DQ-01) with descriptions of what needs to be decided and which artifacts are blocked.

Deduction (-4): None of the four pending decisions has an assigned owner or target resolution date. The reference's Pending Decisions section includes Owner and Target Date columns for each item. Without these fields, the pending decisions are informational only and cannot be tracked to resolution.

---

## Cross-File Consistency Checks

**tasks.md alignment:** All 34 tasks from tasks.md appear in the build-plan. Phase groupings are consistent (DDL tasks in Phase 1, ETL in Phase 2, etc.). Task IDs match exactly between the two documents.

**design.md alignment:** The build-plan references design.md constraints for the ETL notebook skeleton (CX-P005) and config management (CX-P001, CX-P002). These references are consistent with design.md §7 (Configuration Management). The Phase 2 constraint table mentions `close_lineage_record` in success AND except block — consistent with design.md §6 Lineage Propagation. However, one finding from the validation report (F-008) notes a path mismatch for TASK-008 output in the build-plan codebase layout tree; this is a known inconsistency.

**Codebase Layout section:** The trainee includes a Codebase Layout tree (not in reference) — this is an additional useful section that shows the full directory structure. The layout is consistent with to-be.md's CX-P004 standard layout.

---

## Auto-Deducts

| Rule | Applied | Amount | Reason |
|---|---|---|---|
| Missing Execution Instructions section | Yes | -5 | No per-phase CLI code blocks for SmartBuilder invocations |
| Pending Decisions lack owner/date | Yes | -2 | PD-001 through QA-DQ-01 have no assignee or target date |

---

## Summary

The build-plan provides solid phase coverage with 34 tasks correctly organized across 4 phases, consistent with tasks.md. The Task-to-Skill Mapping table, Full Dependency Graph, and Prerequisite Checklist are meaningful additions. The extra Codebase Layout and SDD Spec Cross-Reference sections add value beyond the reference. The critical gap is the missing Execution Instructions section, which is a required rubric section containing per-phase CLI commands. The shortened skill names and missing owner/date on pending decisions are secondary gaps. With the Execution Instructions section added, this build-plan would score significantly higher.

---

## Priority Actions

1. Add a dedicated "Execution Instructions" section with one CLI code block per phase, using full canonical skill names: `/12_migvisor_smartbuilder_generate-db` and `/13_migvisor_smartbuilder_generate-etl`.
2. Update Task-to-Skill Mapping table to use full skill names (`/12_migvisor_smartbuilder_generate-db`, `/13_migvisor_smartbuilder_generate-etl`) instead of shortened aliases.
3. Add Owner and Target Date columns to the Pending Decisions table (PD-001, PD-002, PD-003, QA-DQ-01).
4. Fix the TASK-008 output path in the Codebase Layout tree: `src/db/grants/purchase_grants.sql` (not `src/db/ddl/grants.sql`).
