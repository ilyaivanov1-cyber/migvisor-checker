---
task_id: TASK-TB-001
skill: migvisor-task-checker-to-be
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/specifications/to-be.md
reference_file: ./reference/answers/module_4/to-be.md
generated: 2026-09-18
total_score: 81/100
grade: Good
---

# TASK-TB-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/specifications/to-be.md`  
**Reference file:** `./reference/answers/module_4/to-be.md`  
**Generated:** 2026-09-18

---

## Score Summary

**To-Be Score: 81/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| 1.1 Definition / System Identity | 17 | 88/100 | 14.96 | ✓ |
| 1.2 Metadata Table / Business Purpose | 17 | 85/100 | 14.45 | ✓ |
| Technology Stack | 17 | 80/100 | 13.6 | ✓ |
| Stakeholders | 16 | 72/100 | 11.52 | ⚠ |
| Data Domain and Subject Area | 17 | 82/100 | 13.94 | ✓ |
| Key Metrics / Transformation Summary | 16 | 78/100 | 12.48 | ✓ |
| **Subtotal** | | | **80.95** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **81/100** | |

**Grade: Good**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → +1 each to §1.1, §1.2, Technology Stack, Data Domain.

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| 1.1 System Identity | §1.1 Definition (narrative + component list) | Partial |
| 1.2 Business Purpose | §1.2 Metadata Table fields 1–7 | Partial |
| 1.3 Technology Stack | Embedded in §1.1 + §1.2 Metadata field 9 | Partial |
| 1.4 Stakeholders | Partially covered in §1.2 Metadata field 8 | Partial |
| 1.5 Data Domain and Subject Area | §1.2 Metadata fields 1–6 | Direct |
| 1.6 Key Metrics and KPIs | §1.2 Metadata field 5 + Transformation Summary | Partial |

---

## Auto-Deducts Applied

No systematic auto-deducts. Penalties embedded in section scores.

**Total auto-deducts: 0 pts**

---

## Section Feedback

### 1.1 Definition / System Identity — 88/100 (weight 17 → 14.96 pts)

**Status:** ✓ Present

**Strengths:** §1.1 narrative is outstanding — comprehensive description of the target architecture covering: catalog (`inventory_stock`), medallion schemas (bronze/silver_dim/silver_fact), all 8 target Delta tables, all 14+ named notebooks and helpers, SSIS bug correction via OVERWRITE mode, lineage key mechanism via taskValues, 5 QA checks, config externalisation. Every rule ID is referenced (LN-P001, OB-P002, CX-P001, CX-P002, QA-P001–P005). Business value paragraph clearly articulates the migration outcome.

**Gaps vs. reference:** Reference uses a concise System Identity table (catalog, schemas, grain, surrogate key, source system) which allows at-a-glance comparison of source→target attributes. Trainee's narrative is richer but lacks this structured quick-reference table. Reference uses `globalpurchase.fact.purchase` while trainee uses `inventory_stock.silver_fact.fact_purchase` — different catalog/schema names due to different project, both valid.

---

### 1.2 Metadata Table / Business Purpose — 85/100 (weight 17 → 14.45 pts)

**Status:** ✓ Present

**Strengths:** 15-field metadata table covers all required areas. Field 3 (Process Type) correctly distinguishes incremental watermark + OVERWRITE pattern. Field 11 (Calculated Fields) documents `lineage_key` via taskValues and `_extracted_at_utc` audit column. Fields 12–13 (DQ Rules) precisely map to QA rule IDs. Field 14 (Storage) lists all bronze/silver tables with Delta properties.

**Gaps:** Reference §1.2 Business Purpose lists 5 specific business questions answered by the target data product (procurement volume, order fulfilment analysis, order finalisation status, packaging profile, derived quantity integrity). Trainee's Metadata Table field 6 (Description) is concise but doesn't enumerate the business questions separately. Reference also explicitly notes "derived quantity integrity — provision of ordered_quantity as a first-class fact measure" which is a design decision that should be called out.

---

### Technology Stack — 80/100 (weight 17 → 13.6 pts)

**Status:** ✓ Present (embedded)

**Strengths:** §1.1 identifies all technology components: Databricks, Delta Lake, Unity Catalog, Databricks Workflow, Python notebooks, Databricks Secrets, Databricks Repos. Transformation Summary (embedded as HTML comments) documents all transformation rules applied to the stack.

**Gaps:** Reference has an explicit §1.3 Technology Stack table (12 rows) covering Cloud Platform, Storage Format, Metastore/Governance, Orchestration, Extract Notebook, Load Notebook, Watermark Notebook, Surrogate Key Generation, Credential Management, Dimension Views, Data Quality, Source Control. Trainee embeds these details in narrative and Metadata Table but doesn't provide a structured table. The specific Technology Stack table format makes it much easier to review and validate completeness.

---

### Stakeholders — 72/100 (weight 16 → 11.52 pts)

**Status:** ⚠ Partial

**Strengths:** Trainee §1.2 Metadata field 8 (Data Access and Restrictions) covers Unity Catalog RBAC roles for BI principals, ETL principals, and data engineering team.

**Gaps:** Reference §1.4 has a full Stakeholders table with 8 roles: Data Engineering Lead (owns Workflow configuration), Procurement Analyst (validates fact row counts), Finance/Accounts Payable (order-finalisation semantics), Warehouse/Logistics (packaging and received-quantity), Data Governance (UC Owner), Source System Owner (confirms quantity_per_outer temporality — open gate CX-P03), QA/Data Quality Engineer (DQ assertion suite), Order Product Team (Package column case-sensitivity). Trainee has no equivalent stakeholder table — the roles and their specific to-be responsibilities are not documented.

---

### Data Domain and Subject Area — 82/100 (weight 17 → 13.94 pts)

**Status:** ✓ Present

**Strengths:** §1.2 Metadata fields 1–6 cover domain, process, entities, metrics, description. Field 9 (Data Sources) lists all 6 input data sources with exact table paths. Unknown member pattern (key=0 + dq_rejections) documented with rule reference CX-P02. Field 10 (Filters Applied) documents the watermark filter logic with Python helper reference.

**Gaps:** Reference §1.5 has a structured Data Domain table including "Historical Coverage: Full history migrated from SQL Server source; incremental thereafter via last_modified_when watermark." Trainee doesn't explicitly state that full history migration is in scope vs. incremental-only.

---

### Key Metrics / Transformation Summary — 78/100 (weight 16 → 12.48 pts)

**Status:** ✓ Present

**Strengths:** Trainee §1.2 Metadata field 5 (Business Metric) lists `ordered_outers`, `ordered_quantity`, `received_outers`, `is_order_finalized`. Transformation Summary (embedded HTML comments) comprehensively maps each rule ID to the design decision it produced — PL-001 through PL-009, NM-001/002/004/009, TY-P003/P004, OB-001 through OB-P003, LN-001/002/LN-P001, QA-P001 through QA-P005, CX rules.

**Gaps:** Reference §1.6 Key Metrics and KPIs has a full table mapping each measure/attribute to its target column name, target type, and notes (type mapping rule applied). Trainee has the metric names but doesn't provide the target column name → target type mapping table, which is valuable for DDL validation.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add §1.4 Stakeholders table with all 8 roles and to-be responsibilities | Stakeholders | +5 pts |
| 2 | Add explicit Technology Stack table (12 rows) as structured section §1.3 | Technology Stack | +4 pts |
| 3 | Add Key Metrics/KPIs table with target column names and type mappings | Key Metrics | +3 pts |
| 4 | Add System Identity quick-reference table at start of §1.1 (catalog, schemas, grain, grain columns, surrogate key) | Definition | +2 pts |
| 5 | State full history migration scope explicitly in §1.5 Data Domain | Domain | +1 pt |

---

## Priority Actions

1. **Add §1.4 Stakeholders table** — 8 roles with to-be responsibilities. Include Source System Owner (CX-P03 open gate), Order Product Team (LN-P01 package column), and QA/DQ Engineer. Worth up to **+5 pts**.
2. **Add §1.3 Technology Stack table** — extract and restructure from §1.1 narrative into a 12-row table. This makes technology decisions independently reviewable. Worth up to **+4 pts**.
3. **Add Key Metrics/KPIs table** — mapping each of the 11 `fact_purchase` columns to target name, target type, and derivation note. Reference for DDL validation. Worth up to **+3 pts**.

---

*Report generated by migvisor-task-checker-to-be on 2026-09-18*
