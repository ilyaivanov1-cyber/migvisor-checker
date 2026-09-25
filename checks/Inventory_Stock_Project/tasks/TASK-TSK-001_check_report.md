# Check Report: tasks — Inventory_Stock_Project / Purchase

**Skill:** migvisor-task-checker-tasks (#8 of 21)
**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Checked:** 2026-09-25
**Score:** 86 / 100
**Grade:** Good

---

## Cross-File Reads

| File | Status | Notes |
|---|---|---|
| `specifications/development_plan/requirements.md` | Read | 12 FR + 12 NFR + 9 DQR = 33 requirements; IDs FR-001…FR-012, NFR-001…NFR-012, DQR-001…DQR-009 |
| `codebase/docs/design.md` | Read | Correct MERGE INTO, QA assertion chain, correct column names; no "Design reference" field convention established here |

---

## Rubric Sections

### Section 1 — Task Summary Table

**Score: 16 / 20**

The trainee produces a complete Task Summary table with columns: Task ID, Type, Title, Depends On, Requirements. All 34 tasks are listed. Task IDs use the TASK-NNN convention (TASK-001 through TASK-034), which is consistent with the `inventory_stock` catalog naming and valid for this product context — the reference uses DB-NNN/GRANT-NNN/ING-NNN conventions suited to the `globalpurchase` product; neither convention is penalised.

All tasks in the summary carry at least one Requirements ID cross-referenced to FR-xxx, NFR-xxx, or DQR-xxx. Requirements traceability in the summary table is thorough.

Deduction (-4): The summary table does not include a "Design reference" column linking each task to the design.md section that constrains its implementation. The reference provides this per-task field; its absence makes it harder to verify that individual tasks were designed against the spec.

### Section 2 — Task Details (H3 per task)

**Score: 47 / 50**

Each of the 34 tasks has an H3 heading and contains all mandatory fields:
- Type (DDL/ETL/Mart/DQ/Config/Test/BI/Docs)
- Output file path
- Dependencies (prior tasks)
- Requirements traceability (FR/NFR/DQR IDs)
- Description (clear purpose paragraph)
- Acceptance criteria (concrete, verifiable)

DDL tasks (TASK-001 through TASK-008) include inline SQL DDL blocks — an above-reference addition that directly embeds the DDL specification inside the task. This is valuable.

TASK-027 through TASK-034 (Mart + DQ tasks) are extra tasks beyond the reference's 26-task scope, reflecting the trainee's more complete product scope with mart layer and extended DQ assertions. These tasks are internally consistent with the build-plan phases.

Deduction (-3): No "Design reference" field appears at the task level. The reference includes a "Design reference: §N" field in each task detail that pins the task to a specific section of design.md. Without this field, tasks cannot be audited against the design document on a per-task basis.

### Section 3 — Acceptance Criteria Quality

**Score: 23 / 30**

All 34 tasks have at least one acceptance criterion. DDL tasks have SQL-based verification criteria. ETL tasks have behavioral criteria (run success, lineage_key propagation, row counts). Test tasks have assertion-coverage criteria.

Deduction (-7): Acceptance criteria in ETL tasks (TASK-014 through TASK-016 area) reference notebook names and helper function names, but do not consistently provide the verifiable test-assertion patterns (e.g., "test that injecting exception in main ETL logic calls close_lineage_record with succeeded=False"). The reference's AC for equivalent tasks provides exact verification queries and edge-case conditions. The trainee's AC is functional but less precise.

---

## Cross-File Consistency Checks

**requirements.md alignment:** The Requirements column in both the summary table and task details references FR-xxx, NFR-xxx, DQR-xxx IDs drawn from requirements.md. Cross-checking confirms all requirement IDs cited in tasks.md are present in requirements.md. No phantom requirement IDs. Traceability is accurate.

**design.md alignment:** design.md does not define a "Design reference" column convention for tasks. The tasks.md omission is consistent with what design.md provides; however, design.md sections (§3 SK Resolution, §4 MERGE INTO, §5 QA Assertions) do correspond to specific task groups in tasks.md, and these connections are implicit rather than explicit.

---

## Auto-Deducts

| Rule | Applied | Amount | Reason |
|---|---|---|---|
| Missing design-ref field per task | Yes | -14 (across sections 1+2) | No per-task "Design reference" field linking to design.md sections |

---

## Summary

The tasks.md deliverable is strong with 34 well-structured tasks covering DDL, ETL, Mart, DQ, Config, Test, BI, and Docs phases. Inline SQL DDL in task details adds significant value over the reference. Requirements traceability is thorough with FR/NFR/DQR cross-references throughout. The primary gap is the absence of a per-task "Design reference" field that would link each task to its governing design.md section. Acceptance criteria are functional but would benefit from more precise edge-case specification, particularly for ETL notebooks where failure-path AC is underspecified.

---

## Priority Actions

1. Add a "Design reference" field to each task detail block linking to the relevant design.md section (§2 for watermark, §3 for SK resolution, §4 for MERGE, §5 for QA assertions, §7 for DDL).
2. Add the Design reference column to the Task Summary table header and populate for all 34 tasks.
3. Sharpen AC for ETL tasks TASK-014, TASK-015, TASK-016 to include failure-path assertions (close_lineage_record called on exception with succeeded=False, exact RuntimeError message format for QA-P001).
