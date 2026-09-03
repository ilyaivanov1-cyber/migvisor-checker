---
task_id: TASK-ARCH-001
skill: task-checker-architecture-diagram
participant_file: trainees/trainee_1/architecture_diagram.md
reference_file: reference/architecture_diagram.md
product: Sales_Orders
generated: 2026-09-03
total_score: 46/100
grade: Needs Work
---

# TASK-ARCH-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase Data Product
**Participant file:** `trainees/trainee_1/architecture_diagram.md`
**Reference file:** `reference/architecture_diagram.md`
**Generated:** 2026-09-03

---

## Score Summary

**The architecture diagram Score: 46/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 20 | 45/100 | 9.0 | ✗ Below threshold |
| Overview | Overview | 20 | 80/100 | 16.0 | ✓ Pass |
| Pipeline DAG | Pipeline DAG | 20 | 85/100 | 17.0 | ✓ Pass |
| Delta Lake Table Properties | Delta Lake Table Properties | 20 | 10/100 | 2.0 | ✗ Missing |
| lineage_key Propagation | lineage_key Propagation | 20 | 50/100 | 10.0 | ⚠ Partial |
| **Subtotal** | | | | **54.0** | |
| Auto-deducts | | | | **−8.0** | |
| **Total** | | | | **46/100** | |

**Grade: Needs Work**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | H1 + `_TASK-DOCS-003_` tag | exact |
| Overview | `## Data flow overview` (text + Mermaid) | semantic |
| Pipeline DAG | `## Data flow overview` (Mermaid diagram portion) | semantic — combined with Overview |
| Delta Lake Table Properties | [MISSING] | missing |
| lineage_key Propagation | `## lineage_key propagation chain` | semantic (near-exact title) |
| *(not in reference)* | `## Pending decision nodes` | extra |

**Note:** The participant merged the reference's Overview and Pipeline DAG into a single `## Data flow overview` section. The combined section is rich and both reference sections are scored against it. No missing-H2 deduct is applied for Pipeline DAG since the content is present.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No visual diagram anywhere in document | −5 pts | **No** — Mermaid flowchart present |
| No schema/table references anywhere | −4 pts | **No** — `globalsales.stg`, `globalsales.dim`, etc. present |
| No layer/medallion structure described | −4 pts | **No** — Bronze/Silver/Gold subgraphs present |
| No lineage/audit key information anywhere | −3 pts | **No** — dedicated lineage section present |
| Missing H2 section present in reference but absent in participant | −5 pts each (max −15) | **Yes — Delta Lake Table Properties: −5 pts** |
| No notebook or task names anywhere in document | −3 pts | **Yes — no nb_* names anywhere: −3 pts** |
| Table config section present but CDF and retention columns both absent | −2 pts | **No** — section is fully absent (deduct above already applied) |

**Total auto-deducts: −8 pts**

---

## Section Feedback

### Header Metadata — 45/100 (weight 20 → 9.0 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product / architecture name | 30% | 90 | "Sales_Orders" clear; architecture title present |
| Architecture pattern stated | 30% | 60 | Title says "Architecture & Lineage Diagram" — implies pattern but does not explicitly name medallion / Delta Lake / Databricks |
| Catalog / platform reference | 20% | 0 | `globalsales` catalog and Databricks not mentioned in header lines |
| Layer count or schema list | 20% | 0 | Not stated in header |

**Strengths:**
- Product name `Sales_Orders` is immediately clear from the H1 title
- `_TASK-DOCS-003_` task tag is useful for traceability

**Gaps:**
- No mention of platform (Databricks), architecture pattern (medallion / Delta Lake), or catalog name (`globalsales`) in the header block
- No layer count or schema summary in the header

**Improvement items:**
- [ ] Add a short subtitle or metadata block stating: platform (Databricks), architecture pattern (medallion / Delta Lake), target catalog (`globalsales`), and layer count (4)

---

### Overview → participant: `## Data flow overview` — 80/100 (weight 20 → 16.0 pts)

**Criteria scored:** Content (75%), Layer Table (15%), Structure (10%)

**Content completeness (82/100):**
- Architecture pattern described (30%): Bronze/Silver/Gold Mermaid subgraph names make the medallion pattern immediately clear — 90/100
- Layer role descriptions present (30%): Subgraph labels show schema names (`globalsales.stg`) but role narratives are absent (no "Transient landing zone for incremental extracts…" equivalent) — 50/100
- Schema names listed (20%): `globalsales.stg`, `globalsales.dim`, `globalsales.fact`, `globalsales.mart` all present — 100/100
- Data flow direction stated (20%): "Source OLTP → Bronze Staging → Silver Dimensions + Facts → Gold Mart → BI" explicitly states direction — 100/100

**Layer table (65/100):**
- Table present (30%): No separate markdown table; Mermaid subgraph labels serve the same purpose — partial credit 40/100
- Layer count vs. reference (20%): 4 participant layers match 4 reference layers — 100/100
- Each row has schema name (25%): Subgraph label format includes `globalsales.<schema>` — 90/100
- Each row has role description (25%): Subgraph names only; no narrative role description per layer — 40/100

**Structure (90/100):**
- H2 present: Yes — 100
- Intro narrative present: Yes (single-line data flow summary) — 70
- Diagram/table present: Yes (Mermaid flowchart) — 100
- Logically organized: Yes — 90

**Strengths:**
- Mermaid subgraphs with catalog+schema labels effectively communicate the medallion architecture at a glance
- One-line data flow summary is crisp and accurate

**Gaps:**
- No standalone markdown table listing Layer | Schema | Role for quick reference
- Layer role descriptions absent — reader must infer roles from table names inside subgraphs

**Improvement items:**
- [ ] Add a markdown table after the intro line: Layer | Schema | Role — mirrors the reference Overview table format

---

### Pipeline DAG → participant: `## Data flow overview` (Mermaid portion) — 85/100 (weight 20 → 17.0 pts)

**Criteria scored:** Content (70%), Pipeline Diagram (20%), Structure (10%)

**Content completeness (79/100):**
- Layers represented / reference layer count (40%): All 4 reference functional layers covered (Ingestion/Bronze, Dimensions/Silver-Dim, Fact/Silver-Fact, DQ+Mart/Gold) — 100/100
- Notebook or task names present (30%): Participant diagram uses **table names** as nodes (`stg.sale_staging`, `dim.customer`, `fact.sale`) not notebook/process names (`nb_extract_watermark` etc.). Process steps are implied by edge labels ("JDBC extract", "MERGE INTO", "DQ assertions") — partial credit 30/100
- Inter-layer data flow shown (30%): Mermaid edges with labels clearly connect SRC → stg → fact/dim → mart → BI — 100/100

**Pipeline diagram (100/100):**
- Diagram present: Yes (Mermaid `flowchart TD`) — 100
- Layer boundaries shown: Yes (Mermaid `subgraph` blocks per layer) — 100
- Data flow arrows present: Yes (`-->` edges with edge labels) — 100
- Output tables labeled: Yes (fully qualified `schema.table` node labels) — 100

**Structure (100/100):**
- H2 present: Yes — 100
- Diagram in Mermaid code block: Yes — 100
- Layer labels readable: Yes (Bronze/Silver/Gold with catalog.schema) — 100
- Source system entry point shown: Yes (`SRC["Source OLTP\n[PENDING: CX-P04]"]`) — 100

**Strengths:**
- Mermaid `flowchart TD` with `subgraph` notation is clean, readable, and correctly structured
- All table nodes carry fully-qualified `catalog.schema.table` names
- Edge labels describe the operation type ("JDBC extract", "MERGE INTO", "DQ assertions")
- PENDING blockers (CX-P04, CX-P05) correctly annotated on the affected nodes

**Gaps:**
- Diagram is **data-flow focused** (shows tables) rather than **process-flow focused** (shows notebooks/tasks). The reference shows `nb_extract_watermark`, `nb_load_dim_supplier`, etc. as nodes; the participant shows `stg.sale_staging`, `dim.customer` etc.
- No notebook/pipeline step names anywhere in the document — only table names

**Improvement items:**
- [ ] Add a parallel process view or annotate the Mermaid nodes with notebook/job names alongside table names (e.g., `nb_extract_sale → stg.sale_staging`)

---

### Delta Lake Table Properties → [MISSING] — 10/100 (weight 20 → 2.0 pts)

**Criteria scored:** Content (75%), Table Config (15%), Structure (10%)

No dedicated section exists in the participant document. Some inline table properties appear within Mermaid node labels:
- `fact.sale` — "liquid clustering" noted
- `fact.order` — "partition + ZORDER" noted
- Dimension tables — "SCD2" / "SCD0" noted

No CDF (Change Data Feed) column, no retention/vacuum policy, no separate markdown table.

**Content completeness (17/100):**
- Tables covered / reference table count (40%): No table rows; 2 tables have inline clustering notes in Mermaid — 10/100
- Property types match reference columns (30%): Clustering mentioned for 2 tables; CDF not mentioned anywhere; retention not mentioned anywhere — 15/100
- Values are specific not placeholder (30%): "liquid clustering" and "ZORDER" are specific; CDF and retention absent — 20/100

**Table config table (0/100):**
- Table present: No — 0
- All schemas represented: No — 0
- CDF column present: No — 0
- Retention/vacuum column present: No — 0

**Structure (0/100):**
- H2 present: No — 0

**Gaps:**
- No dedicated section at all
- CDF flag not documented for any table
- Retention policy not documented for any table
- Clustering keys only noted inline for 2 tables, not systematically for all tables

**Improvement items:**
- [ ] Add `## Delta Lake Table Properties` section with a markdown table: Table | CDF Enabled | Liquid Clustering / ZORDER Key | Retention (days)
- [ ] Cover all tables: stg.* (4 tables), dim.* (7 tables), fact.* (2 tables), mart views
- [ ] Document CDF: Enabled on dimension tables (SCD-2), Disabled on staging/fact/mart
- [ ] Document retention: short for staging (e.g., 90 days), long for dimensions/fact (e.g., 2555 days)

---

### lineage_key Propagation → `## lineage_key propagation chain` — 50/100 (weight 20 → 10.0 pts)

**Criteria scored:** Content (75%), Lineage Chain (15%), Structure (10%)

**Content completeness (42/100):**
- Audit key purpose explained (30%): "Every row in every table can be traced to its source pipeline run" — clear, accurate — 100/100
- Downstream tables covered / reference downstream count (40%): Reference documents propagation to 5 downstream tables (stg.purchase_staging, dim.supplier, dim.stock_item, fact.purchase, stg.dq_rejections). Participant's chain section shows only: stg.sale_staging → fact.sale → mart.v_customer_sales_summary — approximately 3 of ~10 downstream tables for Sales_Orders product — 25/100
- Failure mode documented (30%): **Absent.** No mention of `status = 'running'` as incomplete-run signal or any equivalent monitoring anchor — 0/100

**Lineage chain (59/100):**
- Chain diagram present (30%): Yes — ASCII tree with ↓ arrows and example values (`lineage_key=42`) — 100/100
- Source of truth identified (25%): Yes — `stg.lineage (lineage_key=42, pipeline_run_id=..., batch_start=...)` clearly at root — 100/100
- All downstream branches shown (25%): No — chain shows only one fact path (sale); missing stg.order_staging, all 7 dimension tables, fact.order, stg.dq_rejections — 15/100
- Failure mode in diagram or notes (20%): Absent — 0/100

**Structure (100/100):**
- H2 present: Yes — 100
- Chain in code block with arrows: Yes — 100
- Source node at top: Yes — 100
- Narrative explanation accompanies chain: Yes — 100

**Strengths:**
- Section exists with a clear, readable ASCII propagation chain
- Concrete `lineage_key=42` example with real field values makes the concept tangible
- SQL tracing query is an excellent addition not present in the reference
- lineage_key purpose statement is precise

**Gaps:**
- Propagation chain shows only one path (sale_staging → fact.sale → mart view). Missing: stg.order_staging, dim.customer, dim.city, dim.stock_item, dim.employee, dim.payment_method, dim.transaction_type, dim.date, fact.order, stg.dq_rejections
- No failure mode documented: when a pipeline fails before committing the watermark, `stg.lineage.status` remains in a non-success state — this monitoring signal is absent
- The Mermaid diagram (## Data flow overview) shows `LINEAGE → STG_SALE` and `LINEAGE → STG_ORD` edges, but these are not reflected in the propagation chain section

**Improvement items:**
- [ ] Expand the propagation chain to show ALL downstream tables: stg.order_staging, dim.* (7 tables), fact.order, stg.dq_rejections
- [ ] Add failure mode documentation: when pipeline halts before watermark commit, `stg.lineage.status = 'running'` is the incomplete-run signal
- [ ] Reconcile the chain section with the Mermaid diagram — both should show the same downstream tables receiving lineage_key

---

## Extra Section

**`## Pending decision nodes`** — table documenting 3 open blockers (CX-P04 source connection, CX-P05 BI grants, CX-DQ-01 DQ thresholds) with impact and placeholder token strategy. Excellent operational content. No score impact.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add `## Delta Lake Table Properties` section with CDF / clustering / retention table covering all tables | Delta Lake Table Properties | +21 pts (18 scoring + 5 deduct removal) |
| 2 | Expand lineage chain to all downstream tables + document failure mode signal | lineage_key Propagation | +8 pts |
| 3 | Add catalog name, platform (Databricks), architecture pattern, and layer count to header | Header Metadata | +6 pts |
| 4 | Add notebook/process step names to pipeline diagram alongside table names | Pipeline DAG | +3 pts |
| 5 | Remove notebook-names auto-deduct by adding at least one `nb_*` process reference anywhere | doc-level | +3 pts |
| 6 | Add markdown layer table (Layer \| Schema \| Role) to Overview section | Overview | +2 pts |

Addressing items 1–2 alone would push the score to approximately **75/100 (Good)**.

---

## Priority Actions

1. **Add `## Delta Lake Table Properties` section** — create a markdown table with all tables from stg, dim, fact, mart layers; columns: Table | CDF Enabled | Clustering Key | Retention (days). This single addition is worth up to **+21 pts**.

2. **Expand `## lineage_key propagation chain`** — add all downstream tables (stg.order_staging, all 7 dim tables, fact.order, stg.dq_rejections) and document the failure-mode signal (`stg.lineage.status = 'running'` on incomplete run). Worth up to **+8 pts**.

3. **Improve header metadata** — add a one-line subtitle: `Platform: Databricks | Architecture: Medallion Delta Lake | Catalog: globalsales | Layers: 4`. Worth up to **+6 pts**.

4. **Add notebook names to the pipeline diagram** — annotate process nodes with `nb_*` names or add a separate process-flow table. Also removes the −3 auto-deduct for missing notebook references. Worth up to **+6 pts combined**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing diagrams, table properties, or lineage chain |
| 0–44 | Incomplete | Major sections absent or no visual representation |

---

*Report generated by skill 26-migvisor-task-checker-architecture-diagram on 2026-09-03*
