---
trainee: Inventory_Stock_Project
product: Purchase
generated: 2026-09-18
---

# Check Summary — Inventory_Stock_Project / Purchase

## Score Table

| # | Skill | Score | Grade |
|---|---|---|---|
| 1 | scope | 81/100 | Good |
| 2 | as-is | 68/100 | Acceptable |
| 3 | transformation-rules | 70/100 | Acceptable |
| 4 | project-rules | 77/100 | Good |
| 5 | to-be | 80/100 | Good |
| 6 | design | 73/100 | Acceptable |
| 7 | requirements | 82/100 | Good |
| 8 | tasks | 69/100 | Acceptable |
| 9 | product-definition | 75/100 | Good |
| 10 | build-plan | 63/100 | Acceptable |
| 11 | data-dictionary | 74/100 | Acceptable |
| 12 | pipeline-runbook | 72/100 | Acceptable |
| 13 | validation-report | 70/100 | Acceptable |
| 14 | architecture-diagram | 0/100 | Incomplete - not submitted |
| 15 | go-live-checklist | 0/100 | Incomplete - not submitted |
| 16 | bi-connections | 0/100 | Incomplete - not submitted |
| 17 | secrets-setup | 0/100 | Incomplete - not submitted |
| 18 | secrets-rotation-runbook | 0/100 | Incomplete - not submitted |
| 19 | uc-permission-audit | 0/100 | Incomplete - not submitted |
| 20 | uc-setup | 0/100 | Incomplete - not submitted |
| 21 | secrets-config | 0/100 | Incomplete - not submitted |
| | **Average (submitted 13)** | **73/100** | **Acceptable** |
| | **Average (all 21)** | **45/100** | **Needs Work** |

---

## Skill Summaries

### 1. scope — 81/100 (Good)
The product scope document scored 81/100 (Good), with strong coverage across Identity, Description, Objects in Scope, and Calculation Surface sections. The Consumers section is the main weak point — the cross-domain view analytics.v_ordertoyearanalytics is missing, which is a key downstream consumer that reads fact.purchase via correlated subquery. The Priority and Sequencing section also lacks detail compared to the reference. The top fix is to add analytics.v_ordertoyearanalytics to the Consumers section with a coordination note, worth up to +4 pts. Additionally, filling the [USER INPUT REQUIRED] placeholder fields in the Boundaries section would recover another +2 pts.

### 2. as-is — 68/100 (Acceptable)
The as-is document scored 68/100 (Acceptable), with the Definition and Model/ER Diagram sections performing well. The Consumers section is significantly weak — it misses analytics.v_ordertoyearanalytics as a cross-domain consumer and lacks consumption patterns and migration impact detail. The Data Flow section does not include a Bronze to Silver to Gold layer diagram with Delta table names, which is a core as-is requirement. The top priority fix is to expand the Data Flow section with a layer diagram, worth up to +4 pts. Adding the analytical views sub-section to Consumers is equally important at +4 pts.

### 3. transformation-rules — 70/100 (Acceptable)
The product transformation rules scored 70/100 (Acceptable), with solid coverage of NM (Naming), OB (Objects), and LN (Lineage) dimensions. The critical gap is the completely missing IF (Interface) dimension, which defines data contracts and connector types and is worth up to +10 pts on its own. The PL (Platform) and QA (Quality) sections are also below reference quality — they need explicit Unity Catalog, DLT, and Liquid Clustering references and DQ assertion patterns. Adding the IF dimension is the single highest-impact action. A secondary fix is to list the YAML action files (CX-custom.yaml, LN-lineage.yaml, etc.) in an Action Files section, worth +6 pts.

### 4. project-rules — 77/100 (Good)
The project transformation rules scored 77/100 (Good), with all six submitted dimensions (NM, OB, PL, SX, TY, Header) scoring 75 to 85. The sole critical gap is the missing IF (Interface) dimension, which covers cross-product consumption contracts and schema evolution policy — it carries an 18-point weight and its absence costs the full amount. Adding the IF dimension is the only action needed to push this score into the Excellent range, worth up to +15 pts. A secondary improvement is strengthening the LN (Lineage) dimension with explicit lineage_run table schema and run_id generation strategy, worth +4 pts.

### 5. to-be — 80/100 (Good)
The to-be design document scored 80/100 (Good), with consistent performance across all six sections — Overview, Target Architecture, Data Model, ETL Pipeline Design, and Migration Strategy all scored 76 to 88. The Non-Functional Requirements section is the weakest, lacking SLA targets, data retention policy, and UC permission model. The cross-domain view analytics.v_ordertoyearanalytics is not documented as a consumer of the target fact table. Priority fixes: add the Cross-Domain Views subsection (+3 pts) and expand the NFR section with SLA and retention policy (+3 pts). Adding a Technology Stack subsection with explicit Databricks, Delta, and UC versions recovers another +2 pts.

### 6. design — 73/100 (Acceptable)
The technical design document scored 73/100 (Acceptable), with the Overview, MERGE/ETL Logic, Python Notebooks, and Architecture Diagram sections scoring well. The Bronze and Silver DDL sections are below standard — formal CREATE TABLE statements with all column types, constraints, and COMMENT strings are missing. The Mart/Serving Layer section scored only 30/100, indicating the gold-layer design is largely absent. The top fix is adding complete DDL blocks for bronze.purchase_staging, bronze.lineage_run, and silver_fact.fact_purchase, worth up to +8 pts. Adding the Mart Layer section for downstream BI views is the second priority at +4 pts.

### 7. requirements — 82/100 (Good)
The requirements document scored 82/100 (Good) — the strongest submitted deliverable. All five sections (FR, NFR, DQR, Acceptance Criteria, Source References) scored 75 to 85, indicating comprehensive and well-structured coverage. The main gap is traceability: DQR items are not linked to specific Acceptance Criteria rows. Two functional requirements may be incomplete: FR-011 (Bootstrap Initialization) and FR-012 (Mart Layer Population for BI). Adding DQR-to-AC traceability recovers +2 pts; verifying and completing FR-011 and FR-012 is worth +3 pts each.

### 8. tasks — 69/100 (Acceptable)
The task list scored 69/100 (Acceptable), with Bronze, Silver, and Dependencies/Traceability sections performing solidly. Two entire task groups are completely missing: MART tasks (gold-layer view/table population) and DQ tasks (assertion scripts and rejection monitoring), each worth approximately 8 to 9 pts when added. The DIM task group is partial — surrogate key resolver and SCD-2 merge tasks are absent. Adding the MART task group is the highest-impact action at +9 pts, followed by the DQ task group at +8 pts. Expanding DIM tasks with SK resolver and SCD-2 merge entries recovers an additional +4 pts.

### 9. product-definition — 75/100 (Good)
The product-definition YAML scored 75/100 (Good), with Header/Identity, Source, and Target sections scoring 78 to 82. The Pipeline and Consumers sections are the weaker areas at 68/100 each — the pipeline section is missing DQ assertions list and lineage_key traceability, while the consumers section lacks connection method, view name, and access role per BI consumer. Adding explicit status, domain, and owner fields to the header is the top fix at +6 pts. Adding pipeline.assertions and traceability is worth +5 pts, and expanding the consumers section is worth +4 pts.

### 10. build-plan — 63/100 (Acceptable)
The build plan scored 63/100 (Acceptable) — the lowest score among submitted deliverables. The MART phase is completely absent (0/100), and the Task-to-Skill Mapping section scored only 20/100 because the mapping between task IDs and SmartBuilder skills is largely missing. The DIM phase is also weak, lacking the SK resolver build step and SCD-2 merge task. The two highest-priority fixes are adding the Task-to-Skill Mapping (+8 pts) and adding the MART phase with serving layer build steps (+8 pts). Expanding the DIM phase with SK resolver and SCD-2 merge recovers another +4 pts.

### 11. data-dictionary — 74/100 (Acceptable)
The data dictionary scored 74/100 (Acceptable), with the four Bronze/Silver tables (purchase_staging, etl_cutoff, lineage_run, fact_purchase) and the SCD-2 Glossary all scoring 75 to 82. The critical gap is two completely missing dimension table definitions: dim.supplier (9 columns) and dim.stock_item (19 columns including SCD-2 tracking fields), each worth approximately 12 pts. Nullability flags and FK notation are also absent across all table definitions. Adding dim.supplier and dim.stock_item are the top two priorities, together worth up to +24 pts and would push this score into the Excellent range.

### 12. pipeline-runbook — 72/100 (Acceptable)
The pipeline runbook scored 72/100 (Acceptable), with Failure Response, Reprocessing Guide, and Escalation Path sections performing well (75 to 82). The Daily Monitoring Checklist section is the biggest gap at only 40/100 — it lacks a structured checklist covering job run status, row counts, dq_rejections count, etl_cutoff update check, and lineage log entry verification. The DQ Investigation section is also weak at 50/100, missing SQL queries to inspect bronze.dq_rejections. Adding a complete Daily Monitoring Checklist is the top fix at +12 pts; adding the DQ Investigation SQL queries is second at +8 pts.

### 13. validation-report — 70/100 (Acceptable)
The validation report scored 70/100 (Acceptable), with Header/Run Context, SmartBuilder Skills Executed, Build Results, Validation Findings, and Sign-off all scoring 72 to 85. The critical gap is the DQR Coverage section at only 45/100 — the report does not map which Data Quality Requirements from requirements.md were validated, which passed, and which were deferred. Adding a DQR Coverage table with pass/fail/deferred status per DQR item is the top fix, worth up to +14 pts. Adding per-skill build output detail is the second priority at +5 pts.

### 14. architecture-diagram — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/docs/architecture_diagram.md. Reference: reference/answers/module_5/codebase/docs/architecture_diagram.md. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

### 15. go-live-checklist — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/docs/go_live_checklist.md. Reference: reference/answers/module_5/codebase/docs/go_live_checklist.md. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

### 16. bi-connections — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/docs/bi/bi_connections.md. Reference: reference/answers/module_5/codebase/config/bi_connections.md. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

### 17. secrets-setup — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/config/secrets_setup.md. Reference: reference/answers/module_5/codebase/config/secrets_setup.md. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

### 18. secrets-rotation-runbook — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/config/secrets_rotation_runbook.md. Reference: reference/answers/module_5/codebase/config/secrets_rotation_runbook.md. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

### 19. uc-permission-audit — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/config/uc_permission_audit.sql. Reference: reference/answers/module_5/codebase/config/uc_permission_audit.sql. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

### 20. uc-setup — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/config/uc_setup.sql. Reference: reference/answers/module_5/codebase/config/uc_setup.sql. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

### 21. secrets-config — 0/100 (Incomplete)
File not submitted. Expected at products/Purchase/current/codebase/config/secrets_config.py. Reference: reference/answers/module_5/codebase/config/secrets_config.py. Submitting this file would add approximately 3.8 pts to the overall 21-skill average.

---

## Overall Verdict

**Top 3:** requirements (82), scope (81), to-be (80)
**Bottom 3 (submitted):** build-plan (63), as-is (68), tasks (69)

The 13 submitted deliverables average 73/100 (Acceptable), showing solid foundational work across all modules. The most common gap is missing task groups and phases for the MART (gold) layer and DQ assertions — this pattern appears in tasks, build-plan, and validation-report simultaneously, suggesting the serving layer was not fully designed. The highest-impact single action is submitting the 8 missing module-5 codebase deliverables; within the submitted files, adding the IF (Interface) dimension to both transformation rule sets and the MART/DQ task groups to tasks.md and build-plan.md would recover the most points.
