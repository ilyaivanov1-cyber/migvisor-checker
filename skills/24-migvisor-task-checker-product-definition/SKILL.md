# Skill: task-checker-product-definition

## Identity

| Field | Value |
|---|---|
| Skill number | 24 |
| Skill name | task-checker-product-definition |
| Task ID | TASK-DEF-001 |
| Output file | `checks/<trainee_name>/TASK-DEF-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check product definition"
- "validate product definition"
- "score product definition"
- "compare product definition"
- "check product-definition yaml"
- "validate product-definition yaml"
- "run task-checker-product-definition"
- "run 24-migvisor-task-checker-product-definition"
- "24"

---

## Invocation Syntax

```
/task-checker-product-definition
/task-checker-product-definition participant=<path> reference=<path> trainee=<name>
run task-checker-product-definition
run 24-migvisor-task-checker-product-definition
```

---

## Preconditions

- A participant `product-definition.yaml` file must exist (default: `trainees/<trainee_name>/product-definition.yaml`)
- A reference `product-definition.yaml` file must exist (default: `reference/product-definition.yaml`)
- The `checks/<trainee_name>/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/product-definition.yaml` | `participant=` |
| Reference (final) | `reference/product-definition.yaml` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/product-definition.yaml`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/product-definition.yaml`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with appropriate error (see Step 1)
3. Fallback: `product-definition.yaml` in workspace root

Auto-detection fallback order for reference:
1. `reference/product-definition.yaml`

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags. If `trainee=<name>` is provided and `participant=` is not, resolve participant as `trainees/<name>/product-definition.yaml`.
2. Otherwise run auto-detection sequences above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name from the participant path (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] product-definition.yaml.
   Provide an explicit path: /task-checker-product-definition participant=<path>
   ```
5. Read both files in full.
6. Extract top-level metadata from the reference file:
   - `schema:` — ODPS schema URL (indicates ODPS compliance)
   - `version:` — ODPS specification version
   - Product identifier (under any top-level key, e.g., `product.id`, `product.name`, or equivalent)
   - Product status (draft, published, deprecated)
7. Extract equivalent metadata from participant file.

---

### Step 2 — Detect Sections

Build the scored section list using **YAML top-level key detection**:

**YAML metadata keys to exclude from section list** (these are ODPS file-level declarations, not content sections):
- `schema:` — ODPS schema URL declaration
- `version:` — ODPS spec version declaration (when it appears at file root, not inside a section)

**Section detection algorithm:**

1. Always add **Document Metadata** as section 0. This section covers:
   - ODPS `schema:` declaration presence and correctness
   - ODPS `version:` declaration
   - Top-level product identification fields visible at file root

2. For each top-level YAML key in the **reference** file (excluding `schema:` and `version:` metadata keys), add a section entry. Record the key name exactly as written.

3. Result: N scored sections = 1 (Document Metadata) + count of content top-level YAML keys in reference.

**Example** — if reference has top-level keys `schema`, `version`, `product`, `inputPorts`, `outputPorts`, `pipeline`, `dataQuality`, `migration`:
- Content keys = `product`, `inputPorts`, `outputPorts`, `pipeline`, `dataQuality`, `migration` → 6 keys
- N = 7 (Document Metadata + 6 content sections)
- Section list: Document Metadata, product, inputPorts, outputPorts, pipeline, dataQuality, migration

**Cross-product section matching** — participant file may use different top-level key names for equivalent functional areas. Match participant sections to reference sections by **semantic equivalence**:

| Reference key | Participant equivalent examples |
|---|---|
| `product` | `productIdentity`, `identity`, `product` |
| `inputPorts` | `sources`, `ingestion`, `inputPorts`, `sourceConnections` |
| `outputPorts` | `outputs`, `datasets`, `outputPorts`, `dataOutputs` |
| `pipeline` | `orchestration`, `workflow`, `pipeline`, `etl` |
| `dataQuality` | `dq`, `quality`, `dataQuality`, `assertions` |
| `migration` | `sourceLineage`, `migration`, `legacyMapping`, `sourceMapping` |
| `governance` | `security`, `governance`, `access` |
| `consumers` | `consumers`, `reports`, `subscribers` |
| `sla` | `sla`, `serviceLevel`, `freshness` |
| `calculatedFields` | `calculatedFields`, `derivedFields`, `transformations` |

Record both the reference section name and the matched participant section name (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. `outputPorts` / output datasets section — deepest nesting (field-level schemas, output port definitions)
2. `pipeline` / orchestration section — task dependency chains, layer ordering
3. `dataQuality` / DQ section — assertions, severity, rejection handling, blocking classification
4. `product` / identity section — nested schemas/tables, domain metadata, tags
5. `migration` / source lineage section — multi-object mapping table, known risks
6. `inputPorts` / source connection section — simpler flat structure
7. Any additional participant-only sections (extra content, no penalty)
8. `Document Metadata` — simplest (lowest)

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example** (N=7, base=14, remainder=2):
- outputPorts → 15 pts
- pipeline → 15 pts
- dataQuality → 14 pts
- product → 14 pts
- migration → 14 pts
- inputPorts → 14 pts
- Document Metadata → 14 pts

---

### Step 4 — Classify Section Content Types

For each section in **both** reference and participant files, detect these boolean flags:

| Flag | True when |
|---|---|
| `has_nested_objects` | Section contains nested YAML mappings (objects within objects, e.g., fields, schemas, tables) |
| `has_arrays` | Section contains YAML sequences (lists of ports, tasks, assertions, fields) |
| `has_field_schemas` | Section defines field-level schema (field name, type, nullable, description) |
| `has_task_list` | Section lists pipeline tasks or notebook names |
| `has_dependency_chain` | Section specifies task or layer ordering / `dependsOn` / `runOrder` |
| `has_severity_labels` | Section classifies items by severity (blocking, informational, critical, warning) |
| `has_source_mapping` | Section maps source objects to target objects |
| `has_known_risks` | Section documents known risks, bugs, or migration caveats |
| `has_authentication` | Section documents auth method, secrets, or credential references |
| `has_pending_markers` | Section contains `[USER INPUT REQUIRED]`, `[TBD]`, `[PENDING]`, or `PENDING_DECISION` |
| `has_cross_references` | Section references identifiers defined elsewhere in the document |

Also detect at **document level**:
- `doc_has_product_id`: any top-level section contains a product identifier (id, name, or displayName)
- `doc_has_output_schemas`: any section defines field-level output schemas
- `doc_has_pipeline_spec`: any section specifies orchestration tasks or workflow
- `doc_has_dq_assertions`: any section contains data quality assertions
- `doc_has_platform_declaration`: any section explicitly names the target compute/storage platform

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (20 if has_field_schemas else 0)
  − (15 if has_dependency_chain else 0)
  − (15 if has_severity_labels else 0)
  − (10 if has_source_mapping else 0)
  − (10 if has_authentication else 0)
  − 10   ← structure/conventions, always present
minimum content_pct = 20%
```

The resulting criteria set for a section:

| Criterion | Weight | Present when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure/conventions | 10% | Always |
| Field schemas | 20% | `has_field_schemas` in reference section |
| Dependency chain | 15% | `has_dependency_chain` in reference section |
| Severity/handling | 15% | `has_severity_labels` in reference section |
| Source mapping | 10% | `has_source_mapping` in reference section |
| Authentication spec | 10% | `has_authentication` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section's flags to evaluate how well those criteria are met.

**Section-specific examples:**

- **Document Metadata** (no nested content types): content=90%, structure=10%
- **product / identity** (has nested objects + arrays, no schemas): content=80%, structure=10% + tech accuracy embedded in content scoring
- **inputPorts** (has authentication + arrays): content=80%, auth=10%, structure=10%
- **outputPorts** (has field schemas + arrays): content=70%, schemas=20%, structure=10%
- **pipeline** (has task list + dependency chain): content=75%, deps=15%, structure=10%
- **dataQuality** (has arrays + severity labels): content=70%, severity=15% + source mapping=0%, structure=15% → adjust to 75% content, 15% severity, 10% structure
- **migration** (has source mapping + known risks): content=80%, source mapping=10%, structure=10%

---

### Step 6 — Score Each Section

#### Document Metadata

Evaluate against reference ODPS file-level metadata:

| Sub-criterion | Weight | Checks |
|---|---|---|
| ODPS schema declaration | 30% | `schema:` key present with valid ODPS URL or equivalent spec reference |
| ODPS version | 20% | `version:` key present with valid version number |
| Product identification | 30% | Product id, name, or displayName present somewhere in document |
| Product status | 20% | Status field present (draft, published, deprecated, or equivalent) |

Score = weighted sum of sub-criteria, each rated 0–100%.

**Tolerance**: `[USER INPUT REQUIRED]` or `TBD` values in required fields score 50% (intentional deferral acknowledged, but incomplete).

#### Identity / Product Section (product, productIdentity, or equivalent)

**Content completeness** sub-formula:
```
score = (identity_fields_present / total_reference_identity_fields) × 40%
      + (domain_metadata_present) × 20%
      + (nested_details_present) × 40%
```

Where:
- `identity_fields_present`: count of id/name/description/version/status/domain/owner fields that have values (non-null, non-placeholder)
- `domain_metadata_present`: domain, tags, or equivalent classification fields present
- `nested_details_present`: if reference has nested schemas/tables/details under identity, participant provides equivalent structural details (schemas listed, catalog specified, layers documented)

**Technical accuracy** (embedded in content score):
- Catalog/schema names follow the product's naming convention
- Status values use valid ODPS vocabulary (draft, published, deprecated, retired)
- Domain classification is specific (not generic)

#### Input Ports Section (inputPorts, sources, or equivalent)

**Content completeness** sub-formula:
```
score = (ports_present / reference_port_count) × 40%
      + (connection_details_present) × 30%
      + (extraction_pattern_documented) × 30%
```

Where:
- `ports_present`: participant has at least one input port definition for each reference input port (matched by type: jdbc, file, api, stream)
- `connection_details_present`: port type, protocol, and location fields present (placeholders acceptable with acknowledgment)
- `extraction_pattern_documented`: update frequency, extraction mode (full/incremental), or watermark pattern specified

**Authentication spec** sub-formula (when criterion is scored):
```
score = (ports_with_auth_method / total_ports) × 50%
      + (credential_reference_documented / total_ports) × 50%
```

Where:
- `ports_with_auth_method`: ports that specify authenticationMethod or equivalent
- `credential_reference_documented`: ports that document where credentials are stored (secrets, vault, config key)

#### Output Ports Section (outputPorts, datasets, outputs, or equivalent)

**Content completeness** sub-formula:
```
score = (output_ports_present / reference_output_port_count) × 40%
      + (port_metadata_present) × 30%
      + (location_and_format_present) × 30%
```

Where:
- `output_ports_present`: participant defines equivalent output ports by type (fact table, dimension table, view, mart)
- `port_metadata_present`: id, name, description, type, updateFrequency present per port
- `location_and_format_present`: catalog.schema.table location and format (delta, parquet, etc.) specified

**Field schemas** sub-formula (when criterion is scored):
```
score = (ports_with_schema / total_output_ports) × 40%
      + (field_coverage_ratio) × 30%
      + (field_metadata_completeness) × 30%
```

Where:
- `ports_with_schema`: output ports that have a schema/fields definition
- `field_coverage_ratio`: average (participant field count / reference field count) across ports that have schemas, capped at 1.0; for cross-product evaluation, measure structural equivalence (same field categories: surrogate keys, FKs, measures, metadata) rather than identical field names
- `field_metadata_completeness`: for fields that exist, percentage with name + type + nullable + description all present

#### Pipeline / Orchestration Section (pipeline, orchestration, or equivalent)

**Content completeness** sub-formula:
```
score = (orchestration_platform_specified) × 20%
      + (schedule_specified) × 20%
      + (pipeline_layers_defined / reference_layer_count) × 30%
      + (tasks_named / reference_task_count) × 30%
```

Where:
- `orchestration_platform_specified`: explicit orchestration tool named (Databricks Workflows, Airflow, dbt, SSIS, etc.)
- `schedule_specified`: schedule expressed (nightly, cron expression, frequency)
- `pipeline_layers_defined`: count of participant pipeline layers matched to reference layers (ingestion/staging, dimension, fact, mart/DQ, etc.)
- `tasks_named`: count of individual notebook/task/job names specified vs reference count, capped at 1.0

**Dependency chain** sub-formula (when criterion is scored):
```
score = (layers_with_dependsOn / total_layers) × 50%
      + (dependency_ordering_correct) × 50%
```

Where:
- `layers_with_dependsOn`: layers that explicitly state which prior layers they depend on (or are leaf layers)
- `dependency_ordering_correct`: the ordering respects ETL logical sequence (ingestion before dimensions, dimensions before facts, facts before mart/DQ)

#### Data Quality Section (dataQuality, dq, quality, or equivalent)

**Content completeness** sub-formula:
```
score = (assertions_defined / reference_assertion_count) × 40%
      + (rejection_sink_documented) × 20%
      + (traceability_field_referenced) × 20%
      + (reconciliation_pattern_present) × 20%
```

Where:
- `assertions_defined`: participant defines at least as many DQ assertions as reference (capped at 1.0); for cross-product, count assertion categories: row-count, FK integrity, null check, business rule, orphan key
- `rejection_sink_documented`: a table or location for DQ rejections is specified
- `traceability_field_referenced`: a lineage or batch key field is referenced for DQ tracing
- `reconciliation_pattern_present`: row count reconciliation between staging and fact is described

**Severity/handling** sub-formula (when criterion is scored):
```
score = (assertions_with_severity / total_assertions) × 40%
      + (assertions_with_blocking_classification / total_assertions) × 40%
      + (pipeline_behavior_on_violation / total_assertions) × 20%
```

Where:
- `assertions_with_severity`: assertions labeled blocking, informational, critical, warning, or equivalent
- `assertions_with_blocking_classification`: assertions state whether they block the pipeline load
- `pipeline_behavior_on_violation`: description of pipeline response (alert, halt, continue, quarantine)

#### Migration / Source Lineage Section (migration, sourceLineage, or equivalent)

**Content completeness** sub-formula:
```
score = (source_system_identified) × 20%
      + (mappings_present / reference_mapping_count) × 50%
      + (known_risks_documented / reference_risk_count) × 30%
```

Where:
- `source_system_identified`: legacy source system named (SQL Server, Oracle, SSIS, etc.)
- `mappings_present`: count of source-to-target object mappings provided; cross-product: count mapping categories (fact, dimension, staging, control, stored-procedure, orchestration)
- `known_risks_documented`: number of risks/caveats documented vs reference count, capped at 1.0

**Source mapping** sub-formula (when criterion is scored):
```
score = (mappings_with_source_and_target / total_mappings) × 50%
      + (mappings_with_type_label / total_mappings) × 30%
      + (mappings_with_notes_where_needed / total_mappings) × 20%
```

Where:
- `mappings_with_source_and_target`: mappings that specify both source and target locations
- `mappings_with_type_label`: mappings labeled by type (fact table, dimension, staging table, stored procedure, orchestration)
- `mappings_with_notes_where_needed`: mappings for renamed objects, procedure replacements, or architectural changes include explanatory notes

#### Additional / Extra Sections (participant-only sections with no reference equivalent)

These sections are not scored — they are noted in the report as extra content beyond reference scope. No score impact (positive or negative).

Document them in the report under **Extra Sections**.

#### Generic Section Fallback (any reference section not matching a named type above)

**Content completeness** sub-formula:
```
score = (sub_keys_present / reference_sub_key_count) × 60%
      + (values_non_empty / sub_keys_present) × 40%
```

**Structure** sub-formula:
```
score = (section_key_present) × 50%
      + (nested_structure_matches_reference_depth) × 50%
```

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No product identifier anywhere (id, name, displayName) | −5 pts | Document cannot be identified |
| Missing section with reference equivalent (output ports absent) | −5 pts | Critical structure gap |
| No output port schema/fields defined anywhere in document | −4 pts | Skip if `doc_has_output_schemas` is true |
| No pipeline / orchestration specification anywhere | −3 pts | Skip if `doc_has_pipeline_spec` is true |
| No DQ assertions anywhere in document | −3 pts | Skip if `doc_has_dq_assertions` is true |
| Platform target inconsistent within document (e.g., Snowflake in one section, Databricks in another) | −3 pts | Internal contradiction |
| Input port location uses hardcoded connection string (not secrets/config reference) | −2 pts | Security concern; secrets pattern expected |
| More than 40% of output port fields missing type declarations | −2 pts | Schema incomplete |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/TASK-DEF-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-DEF-001
skill: task-checker-product-definition
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-DEF-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<path>`
**Reference file:** `<path>`
**Generated:** <today's date>

---

## Score Summary

**The product definition Score: <total>/100**

| Section | Reference Key | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Document Metadata | (file root) | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 2> | <reference_key> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 3> | <reference_key> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| ... | | | | | |
| **Subtotal** | | | | **<subtotal>** | |
| Auto-deducts | | | | **<deducts>** | |
| **Total** | | | | **<total>/100** | |

**Grade: <grade>**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| <ref_key> | <participant_key> or [MISSING] | exact / semantic / missing |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| <condition> | −<N> pts | <Yes/No — reason> |

---

## Section Feedback

### Document Metadata (<weighted_score>/<weight> pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**ODPS compliance:**
- Schema declaration: <present/absent — value if present>
- Version: <present/absent — value if present>

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

---

### <Reference Section Name> → participant: <matched_key> (<weighted_score>/<weight> pts)

**Criteria scored:** Content (<pct>%)[, Field Schemas (20%)][, Dependency Chain (15%)][, Severity/Handling (15%)][, Source Mapping (10%)][, Authentication (10%)], Structure (10%)

**Content completeness (<score>/100):**
- <key sub-criteria with values>

**Field schemas (<score>/100):** *(if applicable)*
- Ports/tables with schema: <N>/<total>
- Field coverage ratio: <pct>
- Field metadata completeness: <pct>

**Dependency chain (<score>/100):** *(if applicable)*
- Layers with dependency spec: <N>/<total>
- Ordering correct: Yes/No

**Severity/handling (<score>/100):** *(if applicable)*
- Assertions with severity: <N>/<total>
- Assertions with blocking classification: <N>/<total>
- Pipeline behavior documented: <N>/<total>

**Source mapping (<score>/100):** *(if applicable)*
- Mappings with source + target: <N>/<total>
- Type labels present: <N>/<total>
- Notes where needed: <N>/<total>

**Authentication spec (<score>/100):** *(if applicable)*
- Ports with auth method: <N>/<total>
- Credential reference documented: <N>/<total>

**Structure (<score>/100):**
- Section key present: Yes/No
- Nested depth matches reference: Yes/No

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

**Improvement items:**
- [ ] <specific actionable fix>

---

## Extra Sections (participant-only, not in reference)

- **<section_key>** — <brief description of content and scope>. No score impact.

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
| 45–59 | Needs work | Missing schemas, DQ spec, or pipeline definition |
| 0–44 | Incomplete | Critical sections absent or product unidentifiable |
```

Status icons: ✓ = scored ≥ 70% of weight, ⚠ = 40–69%, ✗ = < 40%.

---

### Step 10 — Surface Summary to Console

After writing the report, output to the conversation:

```
╔══════════════════════════════════════════════════════════╗
║  TASK-DEF-001  Product Definition Check                  ║
║  Product : <participant product>                         ║
║  Score   : <total>/100   Grade: <grade>                  ║
║  Report  : checks/<trainee_name>/TASK-DEF-001_check_report<suffix>.md ║
╚══════════════════════════════════════════════════════════╝
```

Then write exactly 5–6 sentences of plain-English verdict following these rules:

1. **Sentence 1** — overall quality and what the participant did well (strongest section or highest-scoring area).
2. **Sentence 2** — the single most impactful gap (the section or criterion that lost the most points).
3. **Sentence 3** — structural observation: how well the participant's YAML sections map to the reference (section coverage, naming differences, ODPS compliance).
4. **Sentence 4** — state the final score explicitly: "The document scores **<total>/100** (<grade>)" and name the next most important fix.
5. **Sentence 5** — the single highest-value actionable change to make before resubmitting.
6. **Sentence 6** *(optional)* — note any extra sections or depth beyond reference scope that adds value.

Do **not** exceed 6 sentences. Do **not** use bullet points in the prose verdict. The final score **must appear as a number** in sentence 4.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing schemas, DQ spec, or pipeline definition |
| 0–44 | Incomplete | Critical sections absent or product unidentifiable |

---

## Cross-Product Evaluation Note

The participant and reference describe **different products** (e.g., participant = Sales_Orders, reference = GlobalPurchase_Project). In this case:

- **Do not** penalize for different domain entities, catalog names, table names, or business-specific field names.
- **Do** evaluate structural completeness: all reference section types present, nested depth equivalent, required fields populated.
- **Do** evaluate pattern correctness: ODPS conventions followed, field metadata format (name/type/nullable/description), pipeline layer pattern, DQ assertion format, source mapping format.
- **Do not** penalize `[USER INPUT REQUIRED]` or `TBD` placeholders — treat as intentional deferrals scoring 50% on affected sub-criteria.
- Content completeness reflects coverage of equivalent functional domain areas (identity, ingestion, output schemas, orchestration, DQ, migration), not identical YAML text.

**Section semantic matching guidance:**
- A participant `productIdentity:` section is semantically equivalent to a reference `product:` section — evaluate for identity, domain, metadata completeness.
- A participant `datasets:` section that contains both facts and dimensions is semantically equivalent to reference `outputPorts:` — evaluate for schema/field coverage.
- A participant `orchestration:` section is semantically equivalent to reference `pipeline:` — evaluate for task list, schedule, dependency chain.
- A participant `sourceLineage:` section is semantically equivalent to reference `migration:` — evaluate for source mappings and risk documentation.
- When a participant section combines multiple reference sections (e.g., one `datasets:` section covering all output ports), do not double-penalize — evaluate all combined content against all matched reference sections.

---

## Notes on Participant YAML Structure Variants

Product definition YAML files may use different structural styles:

| Participant structure | Reference expects | Impact |
|---|---|---|
| 12 top-level keys (verbose style) | 6 top-level keys (compact style) | No penalty; extra keys are extra content. Match semantically. |
| Single `datasets:` block for all outputs | Per-port `outputPorts:` array | Score field coverage across all entries in `datasets:` against all reference outputPorts |
| Comment-delimited sections (`# ─── N. SECTION ───`) | Top-level YAML keys | Treat comment-delimited blocks as YAML sections for matching purposes |
| Inline `[USER INPUT REQUIRED]` strings | Resolved values | Score 50% for sub-criteria affected; note as intentional deferrals |
| `PENDING_DECISION` values | Resolved values | Treat same as `[USER INPUT REQUIRED]` — 50% credit, note pending |
| camelCase key names | snake_case key names | No penalty; semantic match only |

When the participant's YAML is significantly more detailed than the reference (e.g., 12 sections vs 6), extra sections beyond the reference scope are noted in the report but do not affect the score negatively or positively.
