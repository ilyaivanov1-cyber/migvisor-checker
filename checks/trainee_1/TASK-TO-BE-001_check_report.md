---
task_id: TASK-TO-BE-001
product: Sales_Orders
participant_file: to-be my.md
reference_file: to-be.md
checked_at: 2026-09-01T10:00:00Z
sections_evaluated: 6
total_score: 76/100
grade: Good
identical_to_reference: false
---

# Task Check Report — to-be
_Sales_Orders | 2026-09-01_

**File resolution log:**
- Participant file: `to-be my.md` — supplied explicitly by user
- Reference file: `to-be.md` — auto-resolved (highest-priority candidate `to-be.md`)
- Product: `Sales_Orders` — derived from H1 heading `# To-Be Design: Sales_Orders`
- Sections in reference: 6 | Sections in participant: 6 (matched: 6, extra: 0)
- Point weights: auto-calculated — floor(100/6)=16 base; +1 distributed to 4 longest sections (§1 Definition, §2 Consumers, §3 Model, §4 Lineage → 17 pts each; §5 and §6 → 16 pts each)

---

## Score Summary

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| 1. Definition | §1 Analytical Data Product Description | 17 | 16 | ✓ |
| 2. Consumers | §2 Consumers and Use Cases | 17 | 14 | ✓ |
| 3. Model | §3 Model Analytical Data Product | 17 | 9 | ⚠ |
| 4. Lineage | §4 Column-Level Lineage | 17 | 12 | ⚠ |
| 5. Calculations | §5 Calculation Logic | 16 | 14 | ✓ |
| 6. Sources | §6 Data Sources | 16 | 11 | ⚠ |
| **Total** | | **100** | **76** | |

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Section 1 — Definition (16/17)
_Matched to participant §1 Analytical Data Product Description_

**Coverage (5/6):** Product identity (medallion architecture, `globalsales` catalog, all four schema layers), business purpose (order-to-cash), technology stack (Databricks, Delta Lake, Unity Catalog, Workflow `nightly_etl_main`), data domain, key metrics with formulas, DQ rules, and storage strategy all present in §1.1 narrative and §1.2 metadata table. **Missing:** no explicit stakeholder roles table (reference includes Data Engineering Lead, Procurement Analyst, Finance/AP, Data Governance roles etc. with responsibilities). Operational context (schedule, watermark, credential management details) is partially covered in the metadata table but lacks a dedicated subsection.

**Specificity (4/4):** Named tables with `globalsales.*` three-part catalog paths, 9 named Power BI reports, formula for `profit_margin_with_factor` with named constant `PROFIT_MARGIN_FACTOR = 1.05`, DQ assertion names (QA-P01 through QA-P03), CX-rule IDs — all present. Excellent specificity.

**Technical accuracy (3/3):** All content describes the Databricks/Delta Lake target. `globalsales` catalog, liquid clustering, `GENERATED ALWAYS AS IDENTITY`, snake_case naming — all correct. No T-SQL.

**Issues/gaps flagged (2/2):** `[PENDING DECISION per CX-P04]` (OLTP-direct BI report), `[PENDING SIGN-OFF]` for DQ thresholds, `[PENDING DECISION]` for role-to-permission matrix — all explicitly flagged with rule IDs.

**Structure (1/1):** §1.1 definition narrative + §1.2 metadata table — clean and consistent.

**Code / Diagram quality (1/1):** No code blocks or Mermaid diagrams in reference §1 — criterion not applicable; full score.

**Code/Diagram inventory:**
- SQL blocks: 0 in reference → 0 in participant
- Python blocks: 0 in reference → 0 in participant
- Mermaid diagrams: 0 in reference → 0 in participant

**Improvement items:**
- [ ] Add a stakeholder roles table (Data Engineering Lead, Business Analyst, Data Governance etc.) with responsibilities in the target state — recovers up to 1 pt.

---

### Section 2 — Consumers (14/17)
_Matched to participant §2 Consumers and Use Cases_

**Coverage (3/6):** Consumer inventory is thorough — 15 consumers documented with business questions and consumption method. `[PENDING DECISION per CX-P04]` called out for the OLTP-direct consumer. However, three key reference subsections are absent: (1) **source→target object mapping per consumer** (which source objects each consumer read and which target objects they should reconnect to), (2) **migration actions per consumer** (step-by-step reconnection instructions, connection parameters), (3) **consumer priority and sequencing** (which consumers can be reconnected immediately vs. which are blocked on other products). Cross-domain views from other products that depend on Sales_Orders data are not explicitly catalogued.

**Specificity (4/4):** Named reports with exact titles, named target objects (`globalsales.fact.sale`, `globalsales.mart.v_order_details`, etc.), rule IDs (CX-P03, CX-P04), consumption paths explicitly stated.

**Technical accuracy (3/3):** All consumers correctly connected to Databricks SQL endpoint and named target objects. CX-P03 consolidation and dbo.OrderDetails decommission correctly reflected.

**Issues/gaps flagged (2/2):** CX-P04 PENDING DECISION explicitly called out for the OLTP-direct BI report. CX-P03 decommission of `dbo.OrderDetails` and consolidation to `v_order_details` noted.

**Structure (1/1):** Single comprehensive consumer table with 4 columns — compact but covers all consumers consistently.

**Code / Diagram quality (1/1):** Reference §2 has only a trivial single-line SQL comment snippet (not a substantive code block) — no deduction for absence.

**Code/Diagram inventory:**
- SQL blocks: ~0 in reference → 0 in participant (reference has one inline SQL comment, not a fenced block)
- Python blocks: 0 in reference → 0 in participant
- Mermaid diagrams: 0 in reference → 0 in participant

**Improvement items:**
- [ ] Add source→target object mapping per consumer (which source tables each consumer read → which target `globalsales.*` objects they should use) — recovers ~1 pt.
- [ ] Add migration actions per consumer (connection update steps, column rename requirements, parallel-run validation approach) — recovers ~1 pt.
- [ ] Add consumer priority/sequencing table (which consumers unblock on Sales_Orders cutover vs. which require cross-product coordination) — recovers ~1 pt.

---

### Section 3 — Model (9/17)
_Matched to participant §3 Model Analytical Data Product_

**Coverage (2/6):** The participant provides an excellent and detailed Mermaid `erDiagram` (§3.1) covering all 15+ entities across STG/FACT/DIM/MART layers with column names, data types, and FK relationships. The textual description table (§3.2) covers all four layers with purpose and key objects. However, the reference §3 is primarily a **DDL-specification section** — all fact, dimension, and staging table DDL (`CREATE TABLE ... USING DELTA`) with full column definitions, constraints, and `TBLPROPERTIES` are absent from the participant file. Also absent: key design decisions (composite PK elimination, IDENTITY/SEQUENCE replacement rationale, SCD-2 is_current flag addition, decimal precision preservation, sentinel row seeding), and a source-to-target column mapping table.

**Specificity (3/4):** Entity names are `globalsales.*` catalog-qualified in the description table. ER diagram uses entity names (STG_SALE_STAGING, FACT_SALE, DIM_CUSTOMER, etc.) and FK relationship labels. Column types are present in the ER diagram but use shorthand notation (DECIMAL_18_2 instead of DECIMAL(18,2)). Missing the precise DDL column definitions, NOT NULL constraints, and TBLPROPERTIES.

**Technical accuracy (3/3):** Target platform entities correctly named, `USING DELTA` references correct, liquid clustering and partitioning correctly described in §3.2 textual description. No T-SQL.

**Issues/gaps flagged (2/2):** Transformation summary comment block present with comprehensive rule references. `dbo.OrderDetails` decommission (CX-P03) noted. Lineage asymmetry correction (LN-EXTEND-001) documented.

**Structure (1/1):** Clean §3.1 ER diagram + §3.2 textual description.

**Code / Diagram quality (1/1):** Mermaid `erDiagram` is syntactically valid, covers all 15 entities with attributes and relationships. Entity coverage ≥ 80% for the Sales_Orders product ✓. Relationship directions (source→target FK) correct.

**Code/Diagram inventory:**
- SQL blocks: 6+ CREATE TABLE DDL blocks in reference → 0 in participant (**−3 pts auto-deduct applied**)
- Python blocks: 0 in reference → 0 in participant
- Mermaid diagrams: 1 erDiagram in reference → 1 erDiagram in participant ✓

**Auto-deduct applied:** SQL block present in reference but completely absent in participant → **−3 pts**

**Improvement items:**
- [ ] Add `CREATE TABLE ... USING DELTA` DDL for `globalsales.fact.sale` and `globalsales.fact.order` with full column list, data types, NOT NULL constraints, `GENERATED ALWAYS AS IDENTITY`, `TBLPROPERTIES`, and clustering/partitioning declarations — this alone recovers the −3 pts auto-deduct plus Coverage improvement.
- [ ] Add DDL for at least the key dimension tables (`globalsales.dim.customer`, `globalsales.dim.city`) and staging tables (`globalsales.stg.sale_staging`, `globalsales.stg.lineage`).
- [ ] Add a key design decisions subsection covering composite PK elimination, SCD-2 `is_current` flag rationale, IDENTITY/SEQUENCE replacement, and sentinel row seeding.
- [ ] Add a source-to-target column mapping table for `globalsales.fact.sale`.

---

### Section 4 — Lineage (12/17)
_Matched to participant §4 Column-Level Lineage_

**Coverage (4/6):** The participant provides strong column-level lineage: §4.1 key columns/metrics table (18 rows with derivation logic), §4.2 Mermaid flowchart (end-to-end data flow from Bronze to PBI), §4.3 column-level lineage table (source→intermediate→target per column), §4.4 step-by-step transformation table (14 steps with SQL logic), §4.5 downstream dependencies. This is excellent column-level coverage. However, the reference §4 focuses on **pipeline-level lineage**: ETL step-by-step with `dbutils.jobs.taskValues` propagation, Python notebook pseudocode for lineage key tracking, watermark commit protocol, SSIS-to-Workflow mapping, and cross-product dependency declarations with explicit `depends_on` blocks. The Python lineage traceability code (`open_lineage_record()` / `close_lineage_record()` implementations) is described in §4.4 text but not shown as a Python code block.

**Specificity (4/4):** Named ETL tasks (`get_sale_updates`, `migrate_staged_sale_data`, etc.), named rule IDs (SX-007, SX-016, CX-P01, LN-EXTEND-001), named target columns with three-part catalog paths, SCD2 ROW_NUMBER() pattern documented.

**Technical accuracy (3/3):** All lineage paths correctly describe Databricks target objects. MERGE INTO pattern, `open_lineage_record()` / `close_lineage_record()` functions referenced correctly. No T-SQL.

**Issues/gaps flagged (2/2):** CX-P04 PENDING DECISION on OLTP-direct consumer, SX-EXTEND-001 for `v_order_to_supply_analytics` auxiliary table scope, cross-domain dependencies noted in §4.5.

**Structure (1/1):** Five clear subsections 4.1–4.5 covering different aspects of lineage.

**Code / Diagram quality (1/1):** Mermaid `graph TD` flowchart in §4.2 is syntactically valid with color-coded class definitions. All major pipeline nodes present (Bronze → Staging → ETL tasks → Fact → Mart → PBI). Relationship directions correct.

**Code/Diagram inventory:**
- SQL blocks: 0 in reference → 0 in participant
- Python blocks: 1 in reference (§4.8 `dbutils.jobs.taskValues` code) → 0 in participant (**−3 pts auto-deduct applied**)
- Mermaid diagrams: 0 in reference → 1 in participant (bonus — not penalised)

**Auto-deduct applied:** Python/PySpark block present in reference but completely absent in participant → **−3 pts**

**Approach note:** The participant chose a column-level lineage approach (column derivation table + step transformation table) where the reference uses a pipeline-level approach (ETL task sequence + Python code). Both are valid representations. The column-level coverage is excellent; the pipeline mechanics Python code is missing.

**Improvement items:**
- [ ] Add a Python code block showing `open_lineage_record()` / `close_lineage_record()` call pattern for the nightly ETL tasks, including `dbutils.jobs.taskValues` propagation — this recovers the −3 pts auto-deduct.
- [ ] Add cross-product dependency declarations (which Databricks Workflow tasks depend on other product's dimension loads).

---

### Section 5 — Calculation Logic (14/16)
_Matched to participant §5 Calculation Logic_

**Coverage (4/6):** Seven metrics documented with complete coverage: `total_excluding_tax`, `tax_amount`, `total_including_tax`, `total_dry_items`, `total_chiller_items`, `profit_margin_with_factor`, and `get_total_quantity_sold` UDF. Each has Business Purpose, Mathematical Formula, Input Columns table, SQL Code block, Step-by-Step Calculation, and Thresholds table — an excellent per-metric format. The reference §5, however, is ETL-mechanics oriented: SCD-2 key resolution (Python/PySpark broadcast join pattern), fact MERGE pattern, unknown-member fallback, lineage/watermark management, and DQ assertions. These ETL-level calculation types are addressed partially in §4.4 (step table) but are not present as code implementations in §5 specifically. The reference also has a Python-based overview table of 10 calculation areas with as-is→to-be mapping; the participant doesn't have an equivalent overview.

**Specificity (4/4):** Named formulas with `globalsales.*` tables, DQ rule IDs (CX-P01, QA-P02), named constants (`PROFIT_MARGIN_FACTOR = 1.05`), `config/environment.yaml` reference, business-owner placeholder noted for sign-off. Very specific throughout.

**Technical accuracy (2/3):** All SQL uses Databricks SQL syntax — no T-SQL, correct `INSERT INTO ... SELECT` pattern, valid `CASE WHEN is_chiller_stock = false` BOOLEAN semantics, correct `NULLIF`/`COALESCE` guards, `CREATE OR REPLACE VIEW/FUNCTION` syntax. **One issue:** §5.6 SQL references `dc.ww_i_customer_id` (with `_i_`) — this appears to be a typo for `dc.wwi_customer_id` (standard snake_case form used elsewhere in the file). This also appears in `GROUP BY o.customer_key, dc.ww_i_customer_id, dc.customer` — should be `wwi_customer_id`.

**Issues/gaps flagged (2/2):** `[BUSINESS_OWNER] on [DATE]` placeholder for CX-P01 confirmation; CX-P01 named constant governance note; DQ sanity bound > 200 flagged in §5.6 threshold table.

**Structure (1/1):** Consistent 6-part structure per subsection: Business Purpose → Formula → Inputs → SQL Code → Steps → Thresholds. Excellent layout.

**Code / Diagram quality (1/1):** Seven SQL blocks all syntactically valid Databricks SQL. Complete (not truncated). No T-SQL. Minor typo (`ww_i_customer_id`) noted above but does not affect block validity.

**Code/Diagram inventory:**
- SQL blocks: SQL blocks present in reference (Python-based reference uses different code types) → 7 SQL blocks in participant (**approach note:** participant uses SQL where reference uses Python; logic is equivalent — no auto-deduct per approach policy)
- Python blocks: 2 in reference → 0 in participant (approach difference — SQL equivalents provided)
- Mermaid diagrams: 0 in reference → 0 in participant

**Improvement items:**
- [ ] Fix typo `dc.ww_i_customer_id` → `dc.wwi_customer_id` in §5.6 SQL block and GROUP BY clause (Technical accuracy improvement).
- [ ] Consider adding a calculations overview table (listing all 7 metrics with as-is location, to-be location, complexity) to match reference §5.1 structure.

---

### Section 6 — Data Sources (11/16)
_Matched to participant §6 Data Sources_

**Coverage (3/6):** The participant §6.1 provides a comprehensive 18-row input source table listing all Delta tables read by the ETL pipeline (stg.*, dim.date, control tables) with key fields — and a lineage traceability table mapping each back to the original OLTP source. §6.2 documents all 14 target output objects (facts, dims, staging, mart). This is excellent for target-state documentation. However, the reference §6 is primarily about **how the pipeline connects to and reads from the source** — OLTP source system inventory, direct JDBC read mechanics, JDBC extraction notebook pseudocode, watermark commit protocol, and incremental load pattern. The extraction mechanics, JDBC connection details (dbutils.secrets usage, JDBC URL), and the watermark two-phase commit protocol are absent from the participant file.

**Specificity (4/4):** Named OLTP source tables with schemas (e.g., `wideworldimporters.Sales.Invoices`), all target objects with `globalsales.*` three-part names, transformation rule IDs per row (LN-EXTEND-001, TY-EXTEND-001, CX-P03), key fields listed per table.

**Technical accuracy (3/3):** Target objects correctly named, lineage paths accurate, `[PENDING DECISION per CX-P04]` correctly flagged for OLTP-direct view, SEQUENCE retirement (LN-002) documented.

**Issues/gaps flagged (2/2):** CX-P04 PENDING flagged for `mart.v_sales_orders_realtime`. SSIS `dailyetlmain` retirement documented. LN-EXTEND-001 source asymmetry correction noted.

**Structure (1/1):** §6.1 Input + Lineage Traceability + §6.2 Output — logical structure.

**Code / Diagram quality (1/1):** No code blocks present in either reference or participant for the "quality" criterion. Python extraction code is a coverage issue, not a quality issue for code present.

**Code/Diagram inventory:**
- SQL blocks: 0 in reference → 0 in participant
- Python blocks: 1 in reference (§6.3 extraction notebook pseudocode) → 0 in participant (**−3 pts auto-deduct applied**)
- Mermaid diagrams: 0 in reference → 0 in participant

**Auto-deduct applied:** Python/PySpark block present in reference but completely absent in participant → **−3 pts**

**Improvement items:**
- [ ] Add §6.3 Extraction Method describing the JDBC read approach, connection details (Databricks Secrets pattern), and a Python pseudocode block for the extraction notebook — recovers −3 pts auto-deduct.
- [ ] Add §6.4 Incremental Load Pattern describing the watermark tables (`stg.etl_cutoff`, `stg.lineage`), the two-phase commit protocol, and what happens if the pipeline fails mid-run.

---

## Extra Sections (not in reference)

None. Both files have exactly 6 sections; all matched.

## Approach Notes

- Participant file is for **Sales_Orders** product; reference is for **Purchase** product. Products have different schemas, consumer landscapes, and ETL topologies. All scoring evaluated by information coverage relative to the reference section structure, not by identical product content.
- Section matching done by heading-text keyword overlap — all 6 reference sections matched correctly despite heading text differences.
- Participant §4 takes a column-level lineage approach (column derivation tables, step-by-step SQL transformation table) whereas reference §4 is pipeline-level lineage (ETL task sequence, Python code). Both are valid representations; coverage gap noted, no extra deduction beyond the missing Python block auto-deduct.
- Participant §5 uses SQL code blocks for metric implementations; reference §5 uses Python/PySpark for ETL-level calculations. Per approach policy, SQL implementations of equivalent logic are accepted — no auto-deduct for Python absence in §5.
- Participant §6 documents target data objects comprehensively; reference §6 focuses on extraction mechanics. Both are valid approaches; extraction mechanics are missing and scored accordingly.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **§3 Model — add SQL DDL for fact and dimension tables** — missing `CREATE TABLE ... USING DELTA` blocks trigger −3 pts auto-deduct plus Coverage loss; adding DDL for `fact.sale`, `fact.order`, and key dimensions recovers up to **5–6 pts**
2. **§4 Lineage + §6 Sources — add Python code blocks** — both sections have a −3 pts auto-deduct each for missing Python blocks; adding `open_lineage_record()` / `close_lineage_record()` in §4 and extraction notebook pseudocode in §6 recovers **6 pts** combined
3. **§2 Consumers — add source→target mapping and migration actions** — adding per-consumer source→target object table and migration steps recovers **2–3 pts**

---

## Next Step

Score 76 ≥ 75: You can proceed to the next task.
