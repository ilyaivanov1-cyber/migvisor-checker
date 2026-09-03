# Skill: task-checker-architecture-diagram

## Identity

| Field | Value |
|---|---|
| Skill number | 26 |
| Skill name | task-checker-architecture-diagram |
| Task ID | TASK-ARCH-001 |
| Output file | `checks/<trainee_name>/TASK-ARCH-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check architecture diagram"
- "validate architecture diagram"
- "score architecture diagram"
- "compare architecture diagram"
- "check my architecture diagram"
- "check arch diagram"
- "run task-checker-architecture-diagram"
- "run 26-migvisor-task-checker-architecture-diagram"
- "26"

---

## Invocation Syntax

```
/task-checker-architecture-diagram
/task-checker-architecture-diagram participant=<path> reference=<path> trainee=<name>
run task-checker-architecture-diagram
run 26-migvisor-task-checker-architecture-diagram
```

---

## Preconditions

- A participant `architecture_diagram.md` file must exist (default: `trainees/<trainee_name>/architecture_diagram.md`)
- A reference `architecture_diagram.md` file must exist (default: `reference/architecture_diagram.md`)
- The `checks/<trainee_name>/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/architecture_diagram.md` | `participant=` |
| Reference | `reference/architecture_diagram.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/architecture_diagram.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/architecture_diagram.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `architecture_diagram.md` in workspace root

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags.
2. Otherwise run auto-detection sequences above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] architecture_diagram.md.
   Provide an explicit path: /task-checker-architecture-diagram participant=<path>
   ```
5. Read both files in full.
6. Extract header metadata from each file (lines before the first `##`):
   - Product/architecture name (H1 title)
   - Architecture pattern (medallion, lakehouse, etc.)
   - Target catalog and platform
   - Number of layers/schemas described

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — if reference has 4 H2 headings (Overview, Pipeline DAG, Delta Lake Table Properties, lineage_key Propagation):
- N = 5
- Section list: Header Metadata, Overview, Pipeline DAG, Delta Lake Table Properties, lineage_key Propagation

**Cross-product section matching** — the participant may use different H2 titles for equivalent functional areas. Match by semantic equivalence:

| Reference section | Participant equivalent examples |
|---|---|
| Overview | Architecture Overview, Summary, Data Architecture, Medallion Layers, Layer Summary |
| Pipeline DAG | Pipeline Flow, Data Flow Diagram, DAG, ETL Flow, Workflow Diagram, Pipeline Architecture |
| Delta Lake Table Properties | Table Properties, Storage Configuration, Delta Properties, Table Config, Lake Properties |
| lineage_key Propagation | Lineage Propagation, Audit Key, lineage_key Chain, Lineage Flow, Audit Trail, Run Key |
| (any other reference H2) | Semantic match by topic |

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. Pipeline DAG — most complex: visual representation of the entire pipeline flow, layer boundaries, notebook/task names, data flow arrows, parallelism
2. lineage_key Propagation — audit chain completeness, FK propagation across all tables, failure mode signal
3. Delta Lake Table Properties — storage configuration table: CDF flags, clustering keys, retention policies, coverage of all tables
4. Overview — layer summary table, architecture description, schema mapping
5. Header Metadata — simplest: product title, architecture type label, catalog reference

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example** (N=5, base=20, remainder=0): all sections get 20 pts each.
**Example** (N=6, base=16, remainder=4): Pipeline DAG=17, lineage_key=17, Delta Table Properties=17, Overview=17, Header=16, 6th section=16.

---

### Step 4 — Classify Section Content Types

For each section in the **reference** and **participant** files, detect:

| Flag | True when |
|---|---|
| `has_layer_table` | Section contains a table listing architecture layers/schemas with roles |
| `has_pipeline_diagram` | Section contains a visual diagram (ASCII art or Mermaid) showing pipeline flow |
| `has_notebook_references` | Section names specific notebooks, tasks, or pipeline steps (e.g., `nb_extract_watermark`) |
| `has_schema_references` | Section uses fully qualified `catalog.schema.table` naming |
| `has_table_config_table` | Section contains a table with storage/Delta properties (CDF, clustering, retention) |
| `has_lineage_chain` | Section contains a propagation chain diagram showing lineage_key or audit key flow |
| `has_scd_notation` | Section explicitly documents SCD-2 or slowly-changing dimension loading pattern |
| `has_failure_modes` | Section documents a failure/monitoring signal (e.g., stuck lineage status, incomplete run) |
| `has_layer_boundaries` | Diagram uses box/block notation to separate layers visually |
| `has_data_flow_arrows` | Diagram includes directional arrows (→, ►, │, ▼, or Mermaid edges) |

Also detect at **document level**:
- `doc_has_any_diagram`: any ASCII art or Mermaid block exists
- `doc_has_schema_refs`: any `catalog.schema` or `schema.table` references exist
- `doc_has_layer_structure`: any section describes a layered or medallion architecture
- `doc_has_lineage_info`: any section covers lineage, audit, or run tracking
- `doc_has_notebook_names`: any specific notebook or task names are mentioned

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (20 if has_pipeline_diagram else 0)
  − (15 if has_layer_table else 0)
  − (15 if has_table_config_table else 0)
  − (15 if has_lineage_chain else 0)
  − 10   ← structure/conventions, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Pipeline diagram | 20% | `has_pipeline_diagram` in reference section |
| Layer table | 15% | `has_layer_table` in reference section |
| Table config table | 15% | `has_table_config_table` in reference section |
| Lineage chain | 15% | `has_lineage_chain` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**

- **Header Metadata** — content 90%, structure 10%
- **Overview** (has layer_table) — content 75%, layer table 15%, structure 10%
- **Pipeline DAG** (has pipeline_diagram) — content 70%, pipeline diagram 20%, structure 10%
- **Delta Lake Table Properties** (has table_config_table) — content 75%, table config 15%, structure 10%
- **lineage_key Propagation** (has lineage_chain) — content 75%, lineage chain 15%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

Evaluate against the reference header fields:

| Sub-criterion | Weight | Checks |
|---|---|---|
| Product / architecture name | 30% | H1 title present; product or system named |
| Architecture pattern stated | 30% | Medallion, lakehouse, Unity Catalog, Delta Lake, or equivalent explicitly named |
| Catalog / platform reference | 20% | Target catalog name and compute platform (e.g., Databricks) stated |
| Layer count or schema list | 20% | Number of layers or schema names referenced in header or preamble |

Score = weighted sum of sub-criteria, each rated 0–100%.
`[PENDING]` or `TBD` values score 50% on affected sub-criteria.

---

#### Overview Section

**Content completeness** sub-formula:
```
score = (architecture_pattern_described) × 30%
      + (layer_role_descriptions_present) × 30%
      + (schema_names_listed) × 20%
      + (data_flow_direction_stated) × 20%
```

Where:
- `architecture_pattern_described`: medallion / multi-layer / Delta Lake pattern is named and its purpose explained
- `layer_role_descriptions_present`: each layer has a stated role or responsibility (not just a name)
- `schema_names_listed`: specific schema or catalog.schema names appear in the overview
- `data_flow_direction_stated`: document states or implies the direction of data flow (source → staging → dim → fact → mart or equivalent)

**Layer table** sub-formula (when criterion is scored):
```
score = (table_present) × 30%
      + (layer_count_matches_or_exceeds_reference_layer_count) × 20%
      + (each_row_has_schema_name) × 25%
      + (each_row_has_role_description) × 25%
```

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (intro_narrative_present) × 25%
      + (table_or_list_present) × 25%
      + (content_logically_organized) × 25%
```

---

#### Pipeline DAG Section

**Content completeness** sub-formula:
```
score = (layers_represented / reference_layer_count) × 40%
      + (notebook_or_task_names_present) × 30%
      + (inter_layer_data_flow_shown) × 30%
```

Where:
- `layers_represented`: count of pipeline layers (ingestion, dimensions, facts, mart/DQ) visually or textually represented vs. reference layer count
- `notebook_or_task_names_present`: specific notebook or task names appear in the diagram (not just layer labels)
- `inter_layer_data_flow_shown`: diagram shows how data flows between layers (arrows or text connectors between layer boxes)

**Pipeline diagram** sub-formula (when criterion is scored):
```
score = (diagram_present) × 30%
      + (layer_boundaries_shown) × 25%
      + (data_flow_arrows_present) × 25%
      + (output_tables_labeled) × 20%
```

Where:
- `diagram_present`: any visual diagram exists (ASCII art code block, Mermaid, or equivalent)
- `layer_boundaries_shown`: layers are visually separated (box notation, section dividers, or Mermaid subgraph)
- `data_flow_arrows_present`: directional arrows or edge connectors link layers or tasks
- `output_tables_labeled`: target tables (`schema.table`) appear in the diagram at their write points

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (diagram_in_code_block_or_mermaid) × 25%
      + (layer_labels_readable) × 25%
      + (source_system_entry_point_shown) × 25%
```

---

#### Delta Lake Table Properties Section (or equivalent)

**Content completeness** sub-formula:
```
score = (tables_covered / reference_table_count) × 40%
      + (property_types_match_reference_columns) × 30%
      + (values_are_specific_not_placeholder) × 30%
```

Where:
- `tables_covered`: count of tables with property rows vs. reference table count (participant may have different table names — score by proportion)
- `property_types_match_reference_columns`: participant table has equivalent property columns (CDF / change data feed, clustering key or ZORDER, retention / vacuum policy, or equivalents)
- `values_are_specific_not_placeholder`: actual values present (Enabled/Disabled, specific key names, integer retention days) rather than TBD or blanks

**Table config table** sub-formula (when criterion is scored):
```
score = (table_present) × 30%
      + (all_schemas_represented) × 25%
      + (cdf_column_present) × 20%
      + (retention_or_vacuum_column_present) × 25%
```

Where:
- `all_schemas_represented`: rows exist for tables from every schema layer (stg, dim, fact, mart or equivalents)
- `cdf_column_present`: Change Data Feed / CDC enablement flag column is present
- `retention_or_vacuum_column_present`: retention policy or vacuum duration column is present

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (markdown_table_format) × 25%
      + (column_headers_clear) × 25%
      + (rows_ordered_by_layer) × 25%
```

---

#### lineage_key Propagation Section (or equivalent audit key section)

**Content completeness** sub-formula:
```
score = (audit_key_purpose_explained) × 30%
      + (downstream_tables_covered / reference_downstream_count) × 40%
      + (failure_mode_documented) × 30%
```

Where:
- `audit_key_purpose_explained`: the audit/lineage key's role (one value per pipeline run, FK in all downstream tables, monitoring anchor) is stated
- `downstream_tables_covered`: count of downstream tables shown receiving the lineage key vs. reference count
- `failure_mode_documented`: a failure or monitoring signal is documented (e.g., `status = 'running'` means incomplete run, or equivalent)

**Lineage chain** sub-formula (when criterion is scored):
```
score = (chain_diagram_present) × 30%
      + (source_of_truth_identified) × 25%
      + (all_downstream_branches_shown) × 25%
      + (failure_mode_in_diagram_or_notes) × 20%
```

Where:
- `chain_diagram_present`: any visual or textual chain representation exists (ASCII tree, Mermaid, or indented list with arrows)
- `source_of_truth_identified`: the originating table/column that generates the key is explicitly labeled
- `all_downstream_branches_shown`: every table that stores the lineage key appears in the chain
- `failure_mode_in_diagram_or_notes`: failure/incomplete-run detection is described

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (chain_in_code_block_or_indented_block) × 25%
      + (source_node_at_top_or_clearly_labeled) × 25%
      + (narrative_explanation_accompanies_chain) × 25%
```

---

#### Generic Section Fallback (any reference H2 not matching named types above)

```
content_score = (sub_sections_present / reference_sub_sections) × 60%
              + (content_non_empty / sub_sections_present) × 40%

structure_score = (h2_present) × 50%
                + (content_organized) × 50%
```

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No visual diagram anywhere in document | −5 pts | Skip if `doc_has_any_diagram` is true |
| No schema or table references anywhere | −4 pts | Skip if `doc_has_schema_refs` is true |
| No layer or medallion structure described | −4 pts | Skip if `doc_has_layer_structure` is true |
| No lineage or audit key information anywhere | −3 pts | Skip if `doc_has_lineage_info` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| No notebook or task names anywhere in document | −3 pts | Skip if `doc_has_notebook_names` is true |
| Table properties section present but CDF and retention columns both absent | −2 pts | Only when table config section exists |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/TASK-ARCH-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-ARCH-001
skill: task-checker-architecture-diagram
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-ARCH-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<path>`
**Reference file:** `<path>`
**Generated:** <today's date>

---

## Score Summary

**The architecture diagram Score: <total>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header) | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 2> | <ref title> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 3> | <ref title> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| ... | | | | | |
| **Subtotal** | | | | **<subtotal>** | |
| Auto-deducts | | | | **<deducts>** | |
| **Total** | | | | **<total>/100** | |

**Grade: <grade>**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| <ref title> | <participant title> or [MISSING] | exact / semantic / missing |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| <condition> | −<N> pts | <Yes/No — reason> |

---

## Section Feedback

### Header Metadata (<weighted_score>/<weight> pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

**Improvement items:**
- [ ] <specific action>

---

### <Reference Section> → participant: <matched title> (<weighted_score>/<weight> pts)

**Criteria scored:** Content (<pct>%)[, Pipeline Diagram (20%)][, Layer Table (15%)][, Table Config (15%)][, Lineage Chain (15%)], Structure (10%)

**Content completeness (<score>/100):**
- <key sub-criteria with values>

**Pipeline diagram (<score>/100):** *(if applicable)*
- Diagram present: Yes/No
- Layer boundaries shown: Yes/No
- Data flow arrows present: Yes/No
- Output tables labeled: Yes/No

**Layer table (<score>/100):** *(if applicable)*
- Table present: Yes/No
- Layer count vs. reference: <N>/<ref_N>
- Each row has schema name: Yes/No
- Each row has role description: Yes/No

**Table config table (<score>/100):** *(if applicable)*
- Table present: Yes/No
- All schemas represented: Yes/No
- CDF column present: Yes/No
- Retention/vacuum column present: Yes/No

**Lineage chain (<score>/100):** *(if applicable)*
- Chain diagram present: Yes/No
- Source of truth identified: Yes/No
- All downstream branches shown: Yes/No
- Failure mode documented: Yes/No

**Structure (<score>/100):**
- H2 heading present: Yes/No
- <structure detail>

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

**Improvement items:**
- [ ] <specific action>

---

## Extra Sections (participant-only, not in reference)

- **<section title>** — <brief description>. No score impact.

---

## Improvement Items

List all identified gaps as actionable items, ordered by impact (highest first):

1. **[Section — Criterion]** <specific action> → up to +<N> pts
2. ...

---

## Priority Actions

Top 3–5 changes that will have the greatest score impact:

1. <action> → up to +<N> pts
2. ...

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing diagrams, table properties, or lineage chain |
| 0–44 | Incomplete | Major sections absent or no visual representation |
```

Status icons: ✓ = scored ≥ 70% of weight, ⚠ = 40–69%, ✗ = < 40%.

---

### Step 10 — Surface Summary to Console

After writing the report, output to the conversation:

```
╔══════════════════════════════════════════════════════════╗
║  TASK-ARCH-001  Architecture Diagram Check               ║
║  Product : <participant product>                         ║
║  Score   : <total>/100   Grade: <grade>                  ║
║  Report  : checks/<trainee_name>/TASK-ARCH-001_check_report<suffix>.md ║
╚══════════════════════════════════════════════════════════╝
```

Then write exactly 5–6 sentences of plain-English verdict following these rules:

1. **Sentence 1** — overall quality and what the participant did well (strongest section or criterion).
2. **Sentence 2** — the single most impactful gap (the section or criterion that lost the most points).
3. **Sentence 3** — structural observation: how well the participant's sections map to the reference, any naming differences, and whether extra sections add value.
4. **Sentence 4** — state the final score explicitly: "The architecture diagram scores **<total>/100** (<grade>)" and identify the next most important fix.
5. **Sentence 5** — the single highest-value actionable change the participant should make before resubmitting.
6. **Sentence 6** *(optional)* — note any extra sections or content depth that goes beyond the reference scope and adds meaningful value.

Do **not** exceed 6 sentences. Do **not** use bullet points in the prose verdict. The final score **must appear as a number** in sentence 4.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing diagrams, table properties, or lineage chain |
| 0–44 | Incomplete | Major sections absent or no visual representation |

---

## Cross-Product Evaluation Note

The participant and reference describe **different products** (e.g., participant = Sales_Orders, reference = Purchase). In this case:

- **Do not** penalize for different table names, notebook names, catalog names, or product-specific schema paths.
- **Do** evaluate structural completeness: required sections present, layer structure defined, diagrams exist, table properties covered.
- **Do** evaluate pattern correctness: medallion layer pattern, SCD-2 notation for dimensions, audit key propagation chain format, Delta Lake property table format.
- **Do not** penalize for a different number of layers — score layer coverage by functional equivalence (staging/landing, dimensions, facts, mart/serving or equivalent).
- **Do not** penalize for different property values (e.g., different retention days) — score whether the property columns exist and values are specific.
- Content completeness reflects coverage of equivalent architectural concepts, not identical table names or identical notebook paths.

---

## Notes on Participant Format Variants

Architecture diagram documents may use different organizational formats:

| Participant format | Reference expects | Impact |
|---|---|---|
| Mermaid diagram | ASCII art pipeline DAG | Full credit for pipeline diagram criterion — format does not matter |
| `flowchart TD` Mermaid | Box-and-arrow ASCII | Equivalent — any directed graph format accepted |
| `audit_run_id` instead of `lineage_key` | `lineage_key` column | Semantic equivalent — score lineage chain criterion normally |
| Separate sections for each layer | Single Pipeline DAG section | If all layers are covered across sections, score content completeness at full credit |
| No dedicated table properties section but properties inline in narrative | Separate table properties section | −5 pts missing H2 deduct applies; inline property details scored under the section where they appear |
| `run_id`, `batch_key`, `etl_key` | `lineage_key` | Semantic equivalents — score lineage chain normally |
| Numbered H2 headings | Unnumbered H2 headings | No penalty — semantic match applies |
