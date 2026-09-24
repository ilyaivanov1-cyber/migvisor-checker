---
trainee: Inventory_Stock_Project
product: Purchase
generated: 2026-09-24
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
| 14 | architecture-diagram | 77/100 | Good |
| 15 | go-live-checklist | 78/100 | Good |
| 16 | bi-connections | 87/100 | Good |
| 17 | secrets-setup | 91/100 | Excellent |
| 18 | secrets-rotation-runbook | 94/100 | Excellent |
| 19 | uc-permission-audit | 88/100 | Good |
| 20 | uc-setup | 92/100 | Excellent |
| 21 | secrets-config | 95/100 | Excellent |
| | **Average (all 21)** | **79/100** | **Good** |

---

## Skill Summaries

### 1. scope — 81/100 (Good)
The product scope document scored 81/100 (Good), with strong coverage across Identity, Description, Objects in Scope, and Calculation Surface sections. The Consumers section is the main weak point — analytics.v_ordertoyearanalytics is missing, which reads fact.purchase via correlated subquery and is a key downstream consumer. The Priority and Sequencing section also lacks detail compared to the reference. The top fix is to add analytics.v_ordertoyearanalytics to Consumers with a coordination note, worth up to +4 pts. Filling the [USER INPUT REQUIRED] placeholders in the Boundaries section recovers another +2 pts.

**Priority actions:**
1. Add analytics.v_ordertoyearanalytics to Consumers section with cross-domain coordination note — +4 pts
2. Fill [USER INPUT REQUIRED] placeholders in Boundaries section — +2 pts

### 2. as-is — 68/100 (Acceptable)
The as-is document scored 68/100 (Acceptable), with the Definition and Model/ER Diagram sections performing well. The Consumers section is significantly weak — it misses analytics.v_ordertoyearanalytics and lacks consumption patterns and migration impact detail. The Data Flow section does not include a Bronze to Silver to Gold layer diagram with Delta table names, which is a core as-is requirement. The top priority fix is to expand the Data Flow section with a layer diagram, worth up to +4 pts. Adding the analytical views sub-section to Consumers is equally important at +4 pts.

**Priority actions:**
1. Expand Data Flow section with Bronze to Silver to Gold layer diagram and Delta table names — +4 pts
2. Add analytics.v_ordertoyearanalytics as cross-domain consumer to Consumers section — +4 pts

### 3. transformation-rules — 70/100 (Acceptable)
The product transformation rules scored 70/100 (Acceptable), with solid coverage of NM (Naming), OB (Objects), and LN (Lineage) dimensions. The critical gap is the completely missing IF (Interface) dimension, which defines data contracts and connector types and is worth up to +10 pts. The PL (Platform) and QA (Quality) sections need explicit Unity Catalog, DLT, and Liquid Clustering references and DQ assertion patterns. Adding the IF dimension is the single highest-impact action. A secondary fix is to list the YAML action files in an Action Files section, worth +6 pts.

**Priority actions:**
1. Add the IF (Interface) dimension covering data contracts and connector types — +10 pts
2. List YAML action files (CX-custom.yaml, LN-lineage.yaml) in an Action Files section — +6 pts

### 4. project-rules — 77/100 (Good)
The project transformation rules scored 77/100 (Good), with all six submitted dimensions (NM, OB, PL, SX, TY, Header) scoring 75 to 85. The sole critical gap is the missing IF (Interface) dimension, which covers cross-product consumption contracts and schema evolution policy — worth up to +15 pts. Adding the IF dimension is the only action needed to push this score into the Excellent range. A secondary improvement is strengthening the LN (Lineage) dimension with explicit lineage_run table schema and run_id generation strategy, worth +4 pts.

**Priority actions:**
1. Add the IF (Interface) dimension with cross-product consumption contracts and schema evolution policy — +15 pts
2. Strengthen LN dimension with lineage_run table schema and run_id generation strategy — +4 pts

### 5. to-be — 80/100 (Good)
The to-be design document scored 80/100 (Good), with consistent performance across all six sections — Overview, Target Architecture, Data Model, ETL Pipeline Design, and Migration Strategy all scored 76 to 88. The Non-Functional Requirements section is the weakest, lacking SLA targets, data retention policy, and UC permission model. The cross-domain view analytics.v_ordertoyearanalytics is not documented as a consumer of the target fact table. Priority fixes: add the Cross-Domain Views subsection (+3 pts) and expand the NFR section with SLA and retention policy (+3 pts).

**Priority actions:**
1. Add Cross-Domain Views subsection documenting analytics.v_ordertoyearanalytics — +3 pts
2. Expand NFR section with SLA targets, data retention policy, and UC permission model — +3 pts

### 6. design — 73/100 (Acceptable)
The technical design document scored 73/100 (Acceptable), with the Overview, MERGE/ETL Logic, Python Notebooks, and Architecture Diagram sections scoring well. The Bronze and Silver DDL sections are below standard — formal CREATE TABLE statements with all column types, constraints, and COMMENT strings are missing. The Mart/Serving Layer section scored only 30/100, indicating the gold-layer design is largely absent. The top fix is adding complete DDL blocks for bronze.purchase_staging, bronze.lineage_run, and silver_fact.fact_purchase, worth up to +8 pts.

**Priority actions:**
1. Add complete DDL blocks for bronze.purchase_staging, bronze.lineage_run, and silver_fact.fact_purchase — +8 pts
2. Add Mart Layer section with view definitions for mart.v_purchase_by_supplier and v_purchase_per_stock_item — +4 pts

### 7. requirements — 82/100 (Good)
The requirements document scored 82/100 (Good) — the strongest submitted deliverable among skills 1-13. All five sections (FR, NFR, DQR, Acceptance Criteria, Source References) scored 75 to 85, indicating comprehensive and well-structured coverage. The main gap is traceability: DQR items are not linked to specific Acceptance Criteria rows. Two functional requirements may be incomplete: FR-011 (Bootstrap Initialization) and FR-012 (Mart Layer Population for BI). Adding DQR-to-AC traceability recovers +2 pts; verifying and completing FR-011 and FR-012 is worth +3 pts each.

**Priority actions:**
1. Add DQR-to-Acceptance-Criteria traceability cross-references — +2 pts
2. Verify and complete FR-011 (Bootstrap Initialization) and FR-012 (Mart Layer Population) — +3 pts each

### 8. tasks — 69/100 (Acceptable)
The task list scored 69/100 (Acceptable), with Bronze, Silver, and Dependencies/Traceability sections performing solidly. Two entire task groups are completely missing: MART tasks (gold-layer view/table population) and DQ tasks (assertion scripts and rejection monitoring), each worth approximately 8 to 9 pts when added. The DIM task group is partial — surrogate key resolver and SCD-2 merge tasks are absent. Adding the MART task group is the highest-impact action at +9 pts, followed by the DQ task group at +8 pts.

**Priority actions:**
1. Add MART task group with gold-layer view/materialized view population tasks — +9 pts
2. Add DQ task group with assertion scripts and dq_rejections monitoring tasks — +8 pts

### 9. product-definition — 75/100 (Good)
The product-definition YAML scored 75/100 (Good), with Header/Identity, Source, and Target sections scoring 78 to 82. The Pipeline and Consumers sections are the weaker areas at 68/100 each — the pipeline section is missing DQ assertions list and lineage_key traceability, while the consumers section lacks connection method, view name, and access role per BI consumer. Adding explicit status, domain, and owner fields to the header is the top fix at +6 pts. Adding pipeline.assertions and traceability is worth +5 pts.

**Priority actions:**
1. Add status, domain, and owner fields to the header/identity section — +6 pts
2. Add pipeline.assertions list and lineage_key traceability to the pipeline section — +5 pts

### 10. build-plan — 63/100 (Acceptable)
The build plan scored 63/100 (Acceptable) — the lowest score among all submitted deliverables. The MART phase is completely absent, and the Task-to-Skill Mapping section scored only 20/100 because the mapping between task IDs and SmartBuilder skills is largely missing. The DIM phase is also weak, lacking the SK resolver build step and SCD-2 merge task. The two highest-priority fixes are adding the Task-to-Skill Mapping (+8 pts) and adding the MART phase with serving layer build steps (+8 pts). Expanding the DIM phase with SK resolver and SCD-2 merge recovers another +4 pts.

**Priority actions:**
1. Add Task-to-Skill Mapping section linking task IDs to SmartBuilder skills — +8 pts
2. Add MART phase with serving layer build steps (v_purchase_by_supplier MV, v_purchase_per_stock_item view) — +8 pts

### 11. data-dictionary — 74/100 (Acceptable)
The data dictionary scored 74/100 (Acceptable), with the four Bronze/Silver tables (purchase_staging, etl_cutoff, lineage_run, fact_purchase) and the SCD-2 Glossary all scoring 75 to 82. The critical gap is two completely missing dimension table definitions: dim.supplier (9 columns) and dim.stock_item (19 columns including SCD-2 tracking fields), each worth approximately 12 pts. Nullability flags and FK notation are also absent across all table definitions. Adding these two dimension tables together recovers up to +24 pts and would push this score into the Excellent range.

**Priority actions:**
1. Add dim.supplier table definition (9 columns with SCD-2 tracking fields) — +12 pts
2. Add dim.stock_item table definition (19 columns including SCD-2 tracking fields) — +12 pts

### 12. pipeline-runbook — 72/100 (Acceptable)
The pipeline runbook scored 72/100 (Acceptable), with Failure Response, Reprocessing Guide, and Escalation Path sections performing well (75 to 82). The Daily Monitoring Checklist section is the biggest gap at only 40/100 — it lacks a structured checklist covering job run status, row counts, dq_rejections count, etl_cutoff update check, and lineage log entry verification. The DQ Investigation section is also weak at 50/100, missing SQL queries to inspect bronze.dq_rejections. Adding a complete Daily Monitoring Checklist is the top fix at +12 pts; adding the DQ Investigation SQL queries is second at +8 pts.

**Priority actions:**
1. Add complete Daily Monitoring Checklist with job status, row counts, dq_rejections count, etl_cutoff update, and lineage log verification — +12 pts
2. Add DQ Investigation SQL queries for inspecting bronze.dq_rejections — +8 pts

### 13. validation-report — 70/100 (Acceptable)
The validation report scored 70/100 (Acceptable), with Header/Run Context, SmartBuilder Skills Executed, Build Results, Validation Findings, and Sign-off all scoring 72 to 85. The critical gap is the DQR Coverage section at only 45/100 — the report does not map which Data Quality Requirements from requirements.md were validated, which passed, and which were deferred. Adding a DQR Coverage table with pass/fail/deferred status per DQR item is the top fix, worth up to +14 pts. Adding per-skill build output detail is the second priority at +5 pts.

**Priority actions:**
1. Add DQR Coverage table mapping each DQR item to pass/fail/deferred status — +14 pts
2. Add per-skill build output detail (rows processed, tables created, execution time) — +5 pts

### 14. architecture-diagram — 77/100 (Good)
The architecture diagram scored 77/100 (Good), covering all four sections (Overview, Pipeline DAG, Delta Lake Table Properties, lineage_key Propagation) with solid content. The Pipeline DAG section is the primary gap: several notebooks present in the reference are absent, including nb_extract_dimensions, nb_orchestrate_dimensions, nb_dq_smoke_tests, nb_dq_rejection_report, and mart optimization steps. The Delta Lake Table Properties table uses only a two-column clustering key for fact_purchase, missing stock_item_key from the three-column reference key. The lineage_key propagation chain is well-executed and semantically correct.

**Priority actions:**
1. Expand Pipeline DAG with missing orchestrator and DQ notebooks (nb_orchestrate_dimensions, nb_dq_smoke_tests, nb_dq_rejection_report, nb_optimize_mart) — +8 pts
2. Add stock_item_key to the Liquid Clustering key for silver_fact.fact_purchase — +4 pts

### 15. go-live-checklist — 78/100 (Good)
The go-live checklist scored 78/100 (Good), covering all seven section categories with actionable checkbox items. The Data Quality section is the weakest at 65/100 because the DQ assertions file path is tests/dq_assertions_purchase.yaml instead of the expected config/ path, and specific DQR rule IDs with blocking/informational severity labels are not listed. The Pipeline section is missing the deploy_workflow.sh step as an explicit item. The Security section references a generic PII check instead of the specific nb_pii_compliance_check notebook.

**Priority actions:**
1. Fix DQ section: move assertions file to config/ path and enumerate DQR-001/004/005/006 (BLOCKING) and DQR-002/003 (Informational) — +7 pts
2. Add deploy_workflow.sh --env prod as an explicit Pipeline checklist item — +5 pts

### 16. bi-connections — 87/100 (Good)
The BI connections document scored 87/100 (Good) — the strongest of the module-5 codebase config deliverables. All five sections are complete: Overview, Connection Details per both mart views, SQL Warehouse endpoint, Known Issues, and Access Provisioning. The document is correctly adapted using the inventory_stock catalog throughout. The Known Issues section accurately references bronze.lineage_run.was_successful = true as the monitoring signal. The Access Provisioning section is essentially perfect, and this document is production-ready.

**Priority actions:**
1. Add explanatory note clarifying that bronze.lineage_run corresponds to stg.lineage in the GlobalPurchase reference pattern — +5 pts
2. Add sample aggregate query for v_purchase_by_supplier symmetric to the v_purchase_per_stock_item query — +4 pts

### 17. secrets-setup — 91/100 (Excellent)
The secrets setup runbook scored 91/100 (Excellent) — one of the top-scoring deliverables in this run. All eight steps are present with correct Databricks CLI commands, Python verification code, and cross-references to the rotation runbook. The scope names (inventory-stock-dev/prod) are the correct adaptation for this product. The document is well-structured and ready for ops use. Only minor gaps remain in the Reference section wording and missing inline verification reminders after key registration steps.

**Priority actions:**
1. Standardize the env_scope widget values in the Reference section to match ETL notebook widget format exactly — +3 pts
2. Add inline verification reminder after key registration steps 3 and 4 — +3 pts

### 18. secrets-rotation-runbook — 94/100 (Excellent)
The secrets rotation runbook scored 94/100 (Excellent) — the highest score among all markdown/doc deliverables in this run. All six sections are present: Trigger Conditions, Rotation Procedure, Verification Steps, Rollback Procedure, Notification Checklist, and Rotation Log. The trigger conditions and notification checklist are identical to the reference. The only gaps are in the Verification section: nb_extract_dimensions is omitted from the notebook list, and nb_pii_compliance_check is referenced generically as a PII compliance check. This document is production-ready as-is.

**Priority actions:**
1. Add nb_extract_dimensions to Verification Step 1 alongside nb_extract_purchase and nb_extract_watermark — +5 pts
2. Replace generic PII compliance check reference with specific notebook name nb_pii_compliance_check — +3 pts

### 19. uc-permission-audit — 88/100 (Good)
The UC permission audit SQL scored 88/100 (Good) with comprehensive SHOW GRANTS coverage across all four audit levels (catalog, schema, table, mart views). The principal-to-privilege mapping comment table is complete with all expected grants for etl-service-principal, bi-service-principal, and purchase-analysts. The schema naming (bronze/silver_dim/silver_fact/mart) is the correct product adaptation. The only notable gap is the lineage table audited as bronze.lineage_run, which must be consistent with the actual DDL throughout the codebase.

**Priority actions:**
1. Verify that bronze.lineage_run name is consistent with DDL and all other references throughout the codebase — +5 pts
2. Add explanatory comment on the catalog-level section noting expected USE CATALOG principal grants — +4 pts

### 20. uc-setup — 92/100 (Excellent)
The UC setup SQL scored 92/100 (Excellent) — a near-perfect bootstrap script for the inventory_stock catalog. All four schemas are created with IF NOT EXISTS guards and meaningful COMMENT strings. The execution order note in the header accurately reflects the schema dependency order. The verification query comment matches the actual schemas created. Only cosmetic improvements remain possible: more detailed header comments and making the verification query an executable statement rather than a comment.

**Priority actions:**
1. Add schema-to-responsibility mapping in the header (bronze: raw landing; silver_dim: SCD-2 dims; silver_fact: fact MERGE; mart: BI views) — +4 pts
2. Convert the verification SHOW SCHEMAS comment to an executable statement at the end of the file — +4 pts

### 21. secrets-config — 95/100 (Excellent)
The secrets config Python script scored 95/100 (Excellent) — the highest score in the entire v5 check run. The SCOPES dict, REQUIRED_KEYS, all four helper functions (_run, scope_exists, create_scope, register_key), and the argparse entry point are all present and functionally correct. The scope names are correctly adapted to inventory-stock-dev/prod. The getpass usage for secure credential input matches the reference exactly. This is production-ready code requiring only minor cosmetic improvements.

**Priority actions:**
1. Move import getpass from inside register_key() to the module-level imports block — +2 pts
2. Add --dry-run flag to argparse to preview scope/key registration without executing — +2 pts

---

## Priority Actions — Top Fixes Across All Skills

| # | Skill | Fix | Est. gain |
|---|---|---|---|
| 1 | data-dictionary | Add dim.supplier and dim.stock_item table definitions | +24 pts |
| 2 | pipeline-runbook | Add Daily Monitoring Checklist and DQ Investigation SQL queries | +20 pts |
| 3 | tasks | Add MART task group and DQ task group | +17 pts |
| 4 | build-plan | Add Task-to-Skill Mapping section and MART phase | +16 pts |
| 5 | transformation-rules | Add IF (Interface) dimension and Action Files section | +16 pts |
| 6 | project-rules | Add IF (Interface) dimension | +15 pts |
| 7 | validation-report | Add DQR Coverage table with pass/fail/deferred per DQR item | +14 pts |
| 8 | design | Add complete DDL blocks and Mart Layer section | +12 pts |

---

## Overall Verdict

**Top 3:** secrets-config (95), secrets-rotation-runbook (94), uc-setup (92)
**Bottom 3 (submitted):** build-plan (63), as-is (68), tasks (69)

All 21 deliverables are now submitted, raising the overall average from 45/100 (Needs Work) to **79/100 (Good)** — a significant improvement driven by the 8 newly added module-5 codebase deliverables which averaged 88/100. The most common gap across the specification deliverables is missing or incomplete MART/gold-layer content: build-plan, tasks, design, and validation-report all lack serving-layer definitions. The highest-impact single fixes are completing the data dictionary (dim.supplier + dim.stock_item, +24 pts to that skill) and adding the Daily Monitoring Checklist to the pipeline-runbook (+20 pts); addressing these two would push the overall average above 81/100.
