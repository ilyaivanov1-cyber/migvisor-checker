---
trainee: Inventory_Stock_Project
product: Purchase
generated: 2026-09-25
---

# Check Summary — Inventory_Stock_Project / Purchase

## Score Table

| # | Skill | Score | Grade |
|---|---|---|---|
| 1 | scope | 90/100 | Excellent |
| 2 | as-is | 96/100 | Excellent |
| 3 | transformation-rules | 93/100 | Excellent |
| 4 | project-rules | 95/100 | Excellent |
| 5 | to-be | 94/100 | Excellent |
| 6 | design | 87/100 | Good |
| 7 | requirements | 88/100 | Good |
| 8 | tasks | 86/100 | Good |
| 9 | product-definition | 58/100 | Needs work |
| 10 | build-plan | 67/100 | Acceptable |
| 11 | data-dictionary | 85/100 | Good |
| 12 | pipeline-runbook | 72/100 | Acceptable |
| 13 | validation-report | 84/100 | Good |
| 14 | architecture-diagram | 82/100 | Good |
| 15 | go-live-checklist | 95/100 | Excellent |
| 16 | bi-connections | 88/100 | Good |
| 17 | secrets-setup | 91/100 | Excellent |
| 18 | secrets-rotation-runbook | 94/100 | Excellent |
| 19 | uc-permission-audit | 100/100 | Excellent |
| 20 | uc-setup | 100/100 | Excellent |
| 21 | secrets-config | 100/100 | Excellent |
| | **Average (submitted)** | **88/100** | **Good** |
| | **Average (all 21)** | **88/100** | **Good** |

---

## Skill Summaries

### 1. scope — 90/100 (Excellent)
The scope document covers all 9 required sections with precise identifiers: 19 objects across 6 categories (exact match), all 7 SKILL.md migration risks documented, catalog target inventory_stock correctly stated, and 3 consumers identified. Three [USER INPUT REQUIRED] placeholders for scope owner and boundaries are legitimate deferrals matching the reference. Minor gaps: getpurchaseupdates is not named explicitly in the out-of-scope objects list, and the analytics.v_ordertoyearanalytics dependency is documented in §5 Consumers but not elevated to a distinct entry in §9 Migration Risks as the reference does.

**Priority actions:**
1. Add getpurchaseupdates by name to the out-of-scope objects list with disposition: replaced by direct JDBC incremental extract (rule OB-002) — +2 pts
2. Add a distinct migration risk entry for analytics.v_ordertoyearanalytics cross-domain dependency referencing the Order product team ownership and case-sensitivity risk — +1 pt

---

### 2. as-is — 96/100 (Excellent)
Exceptional as-is document with all 6 sections fully populated including a 15-field metadata table (exceeds threshold), correct SCD-2 boundary semantics (> Valid From exclusive, <= Valid To inclusive), ORDER BY [Valid From] ASC tie-breaker, COALESCE(...,0) fallback, and the SSIS truncation bug documented with the specific wrong table name. Both Mermaid diagrams (ER and lineage) are column-level complete. The 11-step transformation table is more detailed than the reference's 8-step version. The only notable issue is a staging column count of 14 vs the reference's 13, reflecting a different interpretation of whether LineageKey is part of the extract-time staging schema.

**Priority actions:**
1. Clarify the staging column count discrepancy (14 vs 13) with an explicit note explaining that LineageKey is counted as a staging column written by the SSIS procedure before the fact MERGE — +2 pts
2. Group §6.2 Output Objects into categorical subsections (staging, fact, control, views) to match the reference's output organisation granularity — +1 pt

---

### 3. transformation-rules — 93/100 (Excellent)
All 10 product dimensions present (PL, NM, TY, OB, SX, IF, PE, LN, QA, CX) — the three mandatory auto-deduct elements all pass: QA dimension with QA-P001 through QA-P005, CX dimension with CX-P001 through CX-P006, and TY-P001 override (valid_from/valid_to → DATE). Customisation count of 26 (1 override, 13 extensions, 12 new) aligns with SKILL.md expectations. Primary concern: the TY dimension at 30 rules includes all 26 inherited project TY rules restated in the product file, creating duplication with project-transformation-rules.md and blurring the project-vs-product boundary.

**Priority actions:**
1. Refactor TY dimension in product-transformation-rules.md to list only the 4 product-specific TY rules (TY-P001 through TY-P004), with a reference pointer to project-transformation-rules.md for the 26 inherited TY rules — +4 pts
2. Add explicit cross-references in the Active Dimensions metadata table linking each product rule to the inherited project rule it overrides or extends — +2 pts

---

### 4. project-rules — 95/100 (Excellent)
Project-rules document is exemplary: all 7 expected dimensions present with counts matching SKILL.md exactly (PL:10, NM:9, TY:26, OB:11, SX:17, PE:9, LN:8 = 90 total). All mandatory rule verifications pass — TY-012 (DATETIME2→TIMESTAMP_NTZ), SX-003 (SCD-2 correlated subquery replacement), LN-001 (lineage_run migration with CDF). The IF dimension bonus adds 5 interface contract rules. Application order table and Active Dimensions metadata are complete. Minor improvements needed: TY-012 should cross-reference the TY-P001 product override for validity columns, and several TY rules need expanded intent descriptions beyond the bare type mapping.

**Priority actions:**
1. Add a cross-reference note to TY-012 stating that TY-P001 product override takes precedence for SCD-2 valid_from/valid_to columns (mapping to DATE rather than TIMESTAMP_NTZ) — +2 pts
2. Expand TY-017 through TY-026 rule descriptions to include the migration implication and any ETL-time action required — +1 pt

---

### 5. to-be — 94/100 (Excellent)
Comprehensive to-be specification covering all 7 sections. The 22-step transformation table is complete and correct. The sk_resolver.py code correctly implements temporal range join with DATE-typed validity columns, ROW_NUMBER DESC tie-breaker, and COALESCE(0) fallback. The MERGE INTO in §4.4 step 15 correctly uses a 4-column composite key matching the fact grain. All 3 main consumers are present plus the cross-domain view dependency is thoroughly documented with case-sensitivity risk. Minor issues: date dimension PK naming inconsistency (date vs date_key) between the ER diagram and lineage text, and scd2_merge.py is missing from §1 Key Components list despite being listed in OB-P004.

**Priority actions:**
1. Resolve date dimension PK naming inconsistency: standardise on one name (date or date_key) across ER diagram, §4.1 key columns, §4.3 lineage table, and §6.1 input sources — +3 pts
2. Add scd2_merge.py explicitly to §1 Key Components list alongside sk_resolver.py and fact_merge.py — +1 pt

---

### 6. design — 87/100 (Good)
The design document covers the ETL architecture comprehensively in most areas: SK resolution temporal range join, QA assertion chain with correct blocking/warning classification, lineage propagation, and accurate DDL for 3 of 5 owned Purchase tables (lineage_run 9 cols, purchase_staging 15 cols, fact_purchase 11 cols — all with correct column counts and CLUSTER BY). Key gaps: DDL for etl_cutoff and dq_rejections is absent (40% of owned table DDL missing); mart view SQL uses non-existent column names (supplier_name, stock_item_name); the MERGE key uses a single column inconsistent with to-be; and §6 lineage propagation introduces a parent-child lineage_key hierarchy contradicting the single-key model in to-be.

**Priority actions:**
1. Add CREATE TABLE DDL blocks for bronze.etl_cutoff (3 cols) and bronze.dq_rejections (10 cols) with CX-P006 standard header blocks — +5 pts
2. Correct mart view column names to match actual Silver dimension columns: supplier (not supplier_name), category (not supplier_category_name), stock_item (not stock_item_name) — +3 pts
3. Fix the MERGE key to 4-column composite matching to-be §4.4 step 15 — +3 pts

---

### 7. requirements — 88/100 (Good)
Requirements document contains 33 well-structured requirements (12 FR + 12 NFR + 9 DQR) with specific measurable acceptance criteria, correct blocking/warning classification, and a bonus DQR-to-AC traceability table. All three auto-deduct checks pass (≥25 requirements, priority split present, all three types present). Two known errors identified: FR-007 uses a single-column MERGE key (wwi_purchase_order_id) inconsistent with the 4-column composite key in to-be §4.4; and NFR-004 acceptance criterion uses fk_column where the actual dq_rejections schema has violation_column.

**Priority actions:**
1. Correct FR-007 MERGE key to 4-column composite (wwi_purchase_order_id, date_key, supplier_key, stock_item_key) matching to-be §4.4 step 15 — +5 pts
2. Correct NFR-004 acceptance criterion: replace fk_column with violation_column to match the actual bronze.dq_rejections schema column name — +3 pts

---

### 8. tasks — 86/100 (Good)
Strong 34-task deliverable with inline SQL DDL in task details, thorough FR/NFR/DQR traceability, and concrete acceptance criteria. All tasks carry mandatory fields (type, output file, dependencies, requirements, description, AC). Extra MART and DQ tasks (TASK-027 through TASK-034) reflect a more complete product scope than the reference. The primary gap is the absence of a per-task 'Design reference' field linking each task to its governing design.md section, which is present in the reference and required by the rubric. Acceptance criteria for ETL notebooks lack failure-path edge cases.

**Priority actions:**
1. Add 'Design reference: §N' field to each task detail block and to the Task Summary table — +6 pts
2. Sharpen AC for TASK-014, TASK-015, TASK-016 with failure-path assertions: RuntimeError message format for QA-P001, close_lineage_record called on exception — +3 pts

---

### 9. product-definition — 58/100 (Needs work)
The ODPS 4.1 product-definition.yaml has a strong details block, solid dataAccess with both consumers named, and a dataQuality block with correct BLOCKING flag on completeness. However three critical gaps significantly reduce the score: (1) the migration section is entirely absent — ODPS 4.1 requires it for any platform migration product and to-be.md confirms the SQL Server 2014 migration context; (2) the JDBC source input port is missing from x-inputPorts — to-be.md explicitly describes a JDBC watermark-bounded extract from the transactional source; (3) the pipeline block is flat with no named layers or dependsOn chains. No port carries field-level schemas.

**Priority actions:**
1. Add migration section: map 9 source objects from SQL Server 2014 to target Delta Lake equivalents with 4 known risks (PD-001, PD-002, PD-003, QA-DQ-01) — +15 pts
2. Add JDBC SQL Server input port to x-inputPorts with host, driver, schema, and credential reference fields — +8 pts
3. Restructure pipeline block into 4 named layers (ingestion, dimensions, facts, mart_dq) with dependsOn relationships — +7 pts
4. Add field-level schemas to the fact_purchase output port (11 columns with name, type, nullable flags) — +5 pts

---

### 10. build-plan — 67/100 (Acceptable)
The build-plan covers all 34 tasks in 4 logical phases consistent with tasks.md, and adds value with a Codebase Layout tree, SDD Spec Cross-Reference, and Prerequisite Checks section. The Full Task Dependency Graph in ASCII art is present and correct. The critical gap is the missing Execution Instructions section — a required rubric section containing per-phase CLI code blocks for SmartBuilder invocations. Shortened skill names (/smartbuilder_generate-db) are used instead of canonical names (/12_migvisor_smartbuilder_generate-db). Pending Decisions (PD-001 through QA-DQ-01) lack owner and target date, making them untrackable.

**Priority actions:**
1. Add a dedicated Execution Instructions section with per-phase CLI code blocks using full canonical skill names: /12_migvisor_smartbuilder_generate-db and /13_migvisor_smartbuilder_generate-etl — +12 pts
2. Add Owner and Target Date columns to the Pending Decisions table — +5 pts
3. Fix TASK-008 output path in Codebase Layout tree: src/db/grants/purchase_grants.sql (not src/db/ddl/grants.sql) — +2 pts

---

### 11. data-dictionary — 85/100 (Good)
Excellent 7-table data dictionary with a richer 6-column format (adding Business Meaning and Derivation/Source beyond the reference's 4 columns). All 5 SCD-2 tracking columns are present and correctly typed as DATE in both dimension tables, consistent with TY-P001. FK references are precise at the table.column level. Column names in dq_rejections (rule_id, violation_column) are consistent with the to-be.md ER diagram. The only deduction is the absent silver_dim.date section; to-be.md classifies it as externally owned but the Purchase product has a FK dependency on it that should be documented.

**Priority actions:**
1. Add a silver_dim.date section documenting its columns (date PK, date_key, calendar_year, etc.) with a note that it is externally owned and not loaded by the Purchase workflow — +8 pts
2. Strengthen Derivation/Source entries for etl_cutoff and lineage_run: specify generating helper functions (open_lineage_record(), set_etl_cutoff()) — +4 pts

---

### 12. pipeline-runbook — 72/100 (Acceptable)
The runbook excels in failure recovery with four task-specific recovery sections (one per workflow task) that exceed the reference's diagnostic table. The 9-step cutover checklist is thorough and covers all pending decisions. The monitoring checklist and DQ investigation queries are strong. The critical gaps are two entirely missing rubric sections (Escalation Path and Contacts) and the absent Partial Reprocessing / watermark reset guide. Stale column names (assertion_name, violation_type) in Section 2.5 and Section 6 queries contradict the data-dictionary column definitions (rule_id, rejection_reason) and would cause SQL runtime errors.

**Priority actions:**
1. Add Escalation Path section with severity tiers and contact channels — +7 pts
2. Add Contacts section with data engineering, platform team, and security team contact details — +5 pts
3. Add Partial Reprocessing section with watermark reset SQL and verification query — +5 pts
4. Fix Section 2.5 and Section 6 queries: replace assertion_name with rule_id and violation_type with rejection_reason — +3 pts

---

### 13. validation-report — 84/100 (Good)
Exceptionally strong validation report covering 27 artifacts with correct 19 PASS / 8 FAIL split. Eight findings are documented with root cause, impact, resolution, and code snippets — with F-003 (CRITICAL JDBC config missing, pipeline-blocking) correctly prioritized. The unique Build Output Detail section provides per-notebook execution metrics from an actual pipeline run, demonstrating genuine end-to-end validation. The primary gaps are: DQR IDs in the coverage table do not align with requirements.md DQR-001 through DQR-009, three DQRs from requirements.md (DQR-005, DQR-006, DQR-007) are not covered, and the dual-use of F-001 ID creates ambiguity.

**Priority actions:**
1. Align DQR Coverage table IDs with requirements.md DQR-001 through DQR-009; add a mapping column from assertion names (QA-P001 etc.) to DQR IDs — +8 pts
2. Add coverage rows for DQR-005 (quantity non-negativity), DQR-006 (date key window), DQR-007 (package non-null) covered by QA-P004 — +5 pts
3. Rename prior-run finding to F-001-PRIOR-RUN to disambiguate from the new F-001 — +1 pt

---

### 14. architecture-diagram — 82/100 (Good)
Well-structured 4-section architecture document with a comprehensive ASCII Pipeline DAG, complete Delta Lake Table Properties table, and accurate lineage_key Propagation diagram. The expanded DAG with dimension orchestration, DQ, and mart notebooks is confirmed by the validation report's Build Output Detail and is a strength. Cross-file checks revealed two material inconsistencies: (1) the fact_purchase clustering key count is 3 in the architecture table but 2 in design.md DDL and to-be.md; (2) CDF for bronze.lineage_run is shown as Disabled but to-be.md explicitly enables it per LN-001. Two unspecified notebooks (nb_preflight_dim_check, nb_preflight_date_check) in the DAG have no corresponding tasks in tasks.md.

**Priority actions:**
1. Resolve clustering key inconsistency: align architecture table with design.md DDL — CLUSTER BY (date_key, supplier_key) if 2 columns is correct, or update design.md DDL if 3 columns is intended — +5 pts
2. Update bronze.lineage_run CDF to Enabled in the Delta Lake Table Properties table, consistent with LN-001 (to-be.md) — +4 pts
3. Add TASK-NNN entries in tasks.md for nb_preflight_dim_check and nb_preflight_date_check, or remove these notebooks from the DAG — +3 pts

---

### 15. go-live-checklist — 95/100 (Excellent)
All 7 reference sections present with full checkbox coverage and a strong closing readiness statement. The checklist is a well-adapted product-specific version using inventory_stock/bronze/silver_dim/silver_fact naming throughout. Security section correctly names both service principals with permission scopes and a negative permission check (bi-SP cannot MODIFY). Minor score reductions come from Security task ID refs being limited to item 1 only (GRANT-001–004) while items 2–6 lack refs, and the DQ rejection-table item using 'writable' rather than the more precise 'MODIFY' privilege. The Pipeline section lacks a synthetic failure test item for end-to-end error detection.

**Priority actions:**
1. Add GRANT-* and CFG-* task refs to Security items 2–6 (scope creation, key registration, SP verification) — +1.5 pts
2. Replace 'writable by etl-service-principal' with 'etl-service-principal has MODIFY on bronze.dq_rejections (GRANT-003)' — +0.7 pts
3. Add a synthetic pipeline failure test item (inject JDBC error, verify alert fires) — +0.5 pts

---

### 16. bi-connections — 88/100 (Good)
Both mart views are fully documented with all 5 required attribute table rows, correct UC paths, service principal references, and privilege statements. The connection string block covers all 5 required fields using the correct inventory_stock catalog. The participant adds an extra aggregate sample query for the supplier view and a cross-product naming note in the Known Issues section that shows strong operational awareness. The consistent deduction across 4 sections is the absence of introductory paragraphs before the first list/table/code block. The header lacks an author/date field.

**Priority actions:**
1. Add one introductory sentence to each of sections 2, 3, 4, and 5 before the first table/list/code block — +3 pts
2. Add Generated: or Author: metadata to the header block before the first ## — +2 pts
3. Clarify OAuth 2.0 service-principal authentication as primary (not 'or PAT') — +1 pt

---

### 17. secrets-setup — 91/100 (Excellent)
All 8 reference steps present with correct scope name adaptations (inventory-stock-dev/prod). The Step 5 verification correctly uses dbutils.secrets.list() — non-revealing — and shows expected key names. The participant adds post-step get() verification blocks at Steps 3 and 4 for extra confidence, and enriches the Reference section with a critical operational note about the env_scope widget requiring exact scope name matches. The only scoring gaps are the absence of per-key purpose documentation in the key inventory and missing introductory sentences in a few sections.

**Priority actions:**
1. Add one-line purpose descriptions per key (jdbc_url — source DB connection URL, etc.) in Steps 3, 4 and Reference — +2 pts
2. Add intro sentences to Step 2, Step 6, and Reference sections before the first code block or link — +2 pts

---

### 18. secrets-rotation-runbook — 94/100 (Excellent)
All 6 reference sections present with exact section titles. Trigger Conditions lists all 4 triggers including the 90-day schedule policy. Rotation Procedure has correct H3 sub-sections (Prepare/Dev/Prod) with the critical 'do not revoke old credentials' guidance. Rollback Procedure uses inventory-stock-&lt;env&gt; placeholder correctly. Notification Checklist uses checkbox format with all 3 stakeholder roles including the conditional on-call note. The only scoring reductions are the absence of intro sentences in Verification Steps and Rotation Log, and the missing header author/date field.

**Priority actions:**
1. Add one introductory sentence to Section 3 (Verification Steps) and Section 6 (Rotation Log) — +2 pts
2. Add author or generated date to the header block — +2 pts

---

### 19. uc-permission-audit — 100/100 (Excellent)
A perfect adaptation of the reference permission audit script. All 5 content sections are present: catalog-level SHOW GRANTS, all 4 schema-level SHOW GRANTS (bronze/silver_dim/silver_fact/mart), 8 table-level SHOW GRANTS covering all product tables, both MATERIALIZED VIEW and VIEW audit statements, and a complete 9-row principal-to-privilege comment table. The participant adds operational commentary beyond the reference (downstream failure warning at catalog level, inline expected-grant comments per schema/table). All section separator comments present, idempotency noted, CFG-004 task ID present, no DML statements, no hardcoded values.

**Priority actions:**
1. No priority actions required — script is production-ready

---

### 20. uc-setup — 100/100 (Excellent)
A complete and idempotent UC bootstrap script that exceeds the reference in two measurable ways. The header includes a schema responsibility table documenting which tables live in each of the 4 schemas (not present in reference). The verification step is executable (SHOW SCHEMAS IN CATALOG inventory_stock;) rather than commented-out as in the reference, which the rubric explicitly rewards with bonus credit. All 4 schemas present with IF NOT EXISTS guards, descriptive COMMENT strings, and correct catalog prefix. No destructive statements, no hardcoded values, no unresolved placeholders.

**Priority actions:**
1. No priority actions required — script is production-ready

---

### 21. secrets-config — 100/100 (Excellent)
A Type A bootstrap script that matches the reference intent and adds a meaningful --dry-run mode not present in the reference. All 5 sections are complete: CFG-006 header with Usage/Prerequisites docstring, SCOPES dict and REQUIRED_KEYS list correctly adapted to inventory-stock-dev/prod, idempotent scope_exists() + create_scope() with _run() error handler, register_key() using getpass imported at module level (cleaner than reference's inline import), and a main() with argparse --env required argument and __main__ guard. No hardcoded values, no input() calls, no missing bootstrap elements.

**Priority actions:**
1. No priority actions required — script is production-ready
2. Optional: document --dry-run in the module docstring Usage: block

---

## Priority Actions — Top Fixes Across All Skills

| # | Skill | Fix | Est. gain |
|---|---|---|---|
| 1 | product-definition | Add migration section mapping 9 source SQL Server objects with 4 risks | +15 pts |
| 2 | product-definition | Add JDBC SQL Server input port to x-inputPorts with host, driver, schema, credential | +8 pts |
| 3 | pipeline-runbook | Add Escalation Path and Contacts sections with severity tiers and contact channels | +12 pts |
| 4 | product-definition | Restructure pipeline block into 4 named layers with dependsOn relationships | +7 pts |
| 5 | build-plan | Add Execution Instructions section with per-phase CLI code blocks for SmartBuilder | +12 pts |
| 6 | tasks | Add Design reference field to every task block and Task Summary table | +6 pts |
| 7 | design | Add CREATE TABLE DDL for bronze.etl_cutoff and bronze.dq_rejections (2 missing tables) | +5 pts |
| 8 | pipeline-runbook | Fix SQL column names: assertion_name → rule_id, violation_type → rejection_reason | +3 pts |

---

## Overall Verdict

**Top 3:** uc-permission-audit (100), uc-setup (100), secrets-config (100)
**Bottom 3 (submitted):** product-definition (58), build-plan (67), pipeline-runbook (72)

The overall score of 88/100 (Good) reflects strong specification and infrastructure work — 11 of 21 skills reached Excellent — but is dragged down by three operational deliverables (product-definition, build-plan, pipeline-runbook) that have significant structural gaps: a missing migration section, missing Execution Instructions, and two absent runbook sections. The most common gap across all skills is missing required sections rather than poor content quality — content where present is generally accurate and detailed. The highest-impact fix is completing the product-definition.yaml migration block, which alone could move that score from 58 to ~88 and lift the overall average by ~1.5 points.
