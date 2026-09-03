# Skill: task-checker-data-dictionary

## Identity

| Field | Value |
|---|---|
| Skill number | 28 |
| Skill name | task-checker-data-dictionary |
| Task ID | TASK-DD-001 |
| Output file | `checks/<trainee_name>/data-dictionary/TASK-DD-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check data dictionary"
- "validate data dictionary"
- "score data dictionary"
- "compare data dictionary"
- "check my data dictionary"
- "run task-checker-data-dictionary"
- "run 28-migvisor-task-checker-data-dictionary"
- "28"

---

## Invocation Syntax

```
/task-checker-data-dictionary
/task-checker-data-dictionary participant=<path> reference=<path> trainee=<name>
run task-checker-data-dictionary
run 28-migvisor-task-checker-data-dictionary
```

---

## Preconditions

- A participant `data_dictionary.md` file must exist (default: `trainees/<trainee_name>/data_dictionary.md`)
- A reference `data_dictionary.md` file must exist (default: `reference/data_dictionary.md`)
- The `checks/<trainee_name>/data-dictionary/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/data_dictionary.md` | `participant=` |
| Reference | `reference/data_dictionary.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/data_dictionary.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/data_dictionary.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `data_dictionary.md` in workspace root

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags.
2. Otherwise run auto-detection above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] data_dictionary.md.
   Provide an explicit path: /task-checker-data-dictionary participant=<path>
   ```
5. Read both files in full.
6. Extract document metadata from each file (lines before the first `##`):
   - Product name (H1 title)
   - Total table count (count of `##` headings that describe a table)
   - Whether a Glossary or cross-table reference section is present

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — if reference has 9 H2 headings (8 table definitions + 1 Glossary):
- N = 10
- Section list: Header Metadata, stg.purchase_staging, stg.etl_cutoff, stg.lineage, stg.dq_rejections, dim.supplier, dim.stock_item, dim.date, fact.purchase, Glossary: SCD-2 Tracking Columns

**Cross-product section matching** — the participant uses different product-specific table names. Match by functional role:

| Reference section | Participant equivalent examples |
|---|---|
| stg.purchase_staging (staging table) | stg.sale_staging, stg.order_staging, stg.\<entity\>_staging |
| stg.etl_cutoff (watermark table) | stg.etl_cutoff, stg.watermark, stg.cutoff_control |
| stg.lineage (audit log) | stg.lineage, stg.pipeline_log, stg.run_log, stg.audit_log |
| stg.dq_rejections (DQ violation log) | stg.dq_rejections, stg.dq_violations, stg.dq_errors |
| dim.supplier (SCD-2 dimension) | dim.\<entity\> where entity is a supplier, customer, city, employee, or any SCD-2 dim |
| dim.stock_item (SCD-2 dimension) | dim.\<entity\> where entity is a product, item, stock, or similar SCD-2 dim |
| dim.date (static dimension) | dim.date, dim.calendar, dim.time — the static calendar/date dimension |
| fact.\<entity\> (central fact table) | fact.sale, fact.order, fact.transaction, or the primary fact table |
| Glossary (cross-table reference) | Glossary, Data Types, Conventions, SCD columns, Reference section |

**Multiple staging/dimension tables:** If the participant has more staging tables or dimensions than the reference, score each one against its closest reference equivalent. Extra tables not in the reference are treated as extra sections (noted, not penalized). For N-calculation, use the reference section count only.

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. SCD-2 dimensions (e.g., dim.supplier, dim.stock_item) — most columns, SCD-2 tracking columns, CDF notation, FK references, lineage_key
2. Central fact table — FK references to all dimensions, surrogate key, MERGE key, lineage_key
3. DQ rejection log — severity enum, FK to lineage, IDENTITY PK, multiple nullable/non-null distinctions
4. Audit/lineage log — status enum, IDENTITY PK, run metadata columns
5. Staging table(s) — source columns, lineage_key FK, extraction metadata
6. Static dimension (dim.date) — many columns but no SCD-2, no FK complexity
7. Glossary / cross-table reference section — no column table, conceptual content
8. Simple control tables (stg.etl_cutoff — 2 columns)
9. Header Metadata — simplest

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

---

### Step 4 — Classify Section Content Types

For each `##` section in the **reference** and **participant** files, detect:

| Flag | True when |
|---|---|
| `has_column_table` | Section contains a markdown table with column definitions |
| `has_type_column` | Column table includes a Type column |
| `has_nullable_column` | Column table includes a Nullable column (YES / NO / **NO** / NOT NULL) |
| `has_description_column` | Column table includes a Description column |
| `has_table_description` | Section has a prose paragraph above the column table |
| `has_fk_references` | One or more Description cells reference another table (FK →, references, foreign key) |
| `has_scd2_columns` | Table contains SCD-2 tracking columns: valid_from, valid_to, is_current_row, row_effective_date, row_expiry_date (or equivalents) |
| `has_identity_notation` | Surrogate key column description mentions IDENTITY, auto-increment, or generated |
| `has_lineage_key` | Table has a lineage_key or equivalent audit-key column |
| `has_enum_values` | A column description lists allowed values (e.g., `running` \| `success` \| `failed`) |
| `has_nullability_emphasis` | NOT NULL columns are visually distinguished (bold **NO**, backtick `NOT NULL`, or equivalent) |

Also detect at **document level**:
- `doc_has_column_tables`: any column definition table exists
- `doc_has_type_column`: type column present in at least one table
- `doc_has_nullable_column`: nullable column present in at least one table
- `doc_has_description_column`: description column present in at least one table
- `doc_has_lineage_key`: lineage_key or equivalent audit key present in at least one table
- `doc_has_glossary`: a Glossary or cross-table reference section is present

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (20 if has_column_table else 0)
  − (15 if has_nullable_column else 0)
  − (15 if has_fk_references else 0)
  − 10   ← structure/conventions, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Column completeness | 20% | `has_column_table` in reference section |
| Nullability | 15% | `has_nullable_column` in reference section |
| FK references | 15% | `has_fk_references` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**

- **Header Metadata** — content 90%, structure 10%
- **stg.etl_cutoff** (has column_table, has nullable, no FK) — content 55%, column completeness 20%, nullability 15%, structure 10%
- **stg.lineage** (has column_table, has nullable, no FK) — content 55%, column completeness 20%, nullability 15%, structure 10%
- **stg.dq_rejections** (has column_table, has nullable, has FK) — content 40%, column completeness 20%, nullability 15%, FK references 15%, structure 10%
- **dim.supplier** (has column_table, has nullable, has FK) — content 40%, column completeness 20%, nullability 15%, FK references 15%, structure 10%
- **fact.purchase** (has column_table, has nullable, has FK) — content 40%, column completeness 20%, nullability 15%, FK references 15%, structure 10%
- **Glossary** — content 90%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

| Sub-criterion | Weight | Checks |
|---|---|---|
| Product name in H1 | 40% | H1 title present and names the product |
| Table count stated or derivable | 30% | Total table count clear from document structure |
| Schema coverage stated | 30% | All schemas (stg, dim, fact, or equivalents) represented in header or introduction |

---

#### Content Completeness Sub-Formula (table definition sections)

For each table section, content completeness measures **column functional coverage**:

```
score = (columns_covering_equivalent_topics / reference_column_count) × 60%
      + (descriptions_are_meaningful / total_columns) × 25%
      + (table_description_paragraph_present) × 15%
```

Where:
- `columns_covering_equivalent_topics`: count of participant columns that map to the same functional role as a reference column (cross-product: different column names OK, same role required — e.g., `customer_key` ≡ `supplier_key` as a surrogate PK; `order_date` ≡ `order_date` as the event date)
- `descriptions_are_meaningful`: columns have descriptions that are more than the column name reworded; descriptions explain purpose, constraints, or FK targets
- `table_description_paragraph_present`: a prose paragraph above the column table describes the table's purpose, loading pattern, or key invariant

---

#### Column Completeness Sub-Formula (when criterion is scored)

```
score = (participant_column_count / reference_column_count) × 40%    (capped at 1.0)
      + (columns_have_type / participant_column_count) × 30%
      + (columns_have_description / participant_column_count) × 30%
```

Where:
- `participant_column_count`: number of columns in the participant's table definition
- `columns_have_type`: columns that carry a non-empty data type
- `columns_have_description`: columns that have a non-empty description cell

---

#### Nullability Sub-Formula (when criterion is scored)

```
score = (nullable_column_present_in_table) × 40%
      + (not_null_columns_marked / reference_not_null_count) × 40%
      + (nullability_values_are_explicit) × 20%
```

Where:
- `nullable_column_present_in_table`: the column table includes a Nullable column (any heading: Nullable, Null, Required, etc.)
- `not_null_columns_marked`: participant marks NOT NULL columns explicitly (bold, backtick, or `NO`) vs just leaving blank
- `nullability_values_are_explicit`: values in the Nullable column are YES/NO (or equivalent), not blank/absent

---

#### FK References Sub-Formula (when criterion is scored)

```
score = (fk_columns_documented / reference_fk_count) × 60%
      + (fk_targets_are_specific / fk_columns_documented) × 40%
```

Where:
- `fk_columns_documented`: participant columns that include a FK notation or cross-table reference in their description (cross-product: target table name will differ)
- `fk_targets_are_specific`: FK descriptions name the target table and column (e.g., FK → stg.lineage.lineage_key or equivalent), not just "foreign key"

---

#### Structure Sub-Formula (table sections)

```
score = (h2_present) × 25%
      + (column_table_present_and_formatted) × 35%
      + (column_headers_match_convention) × 20%
      + (table_description_above_columns) × 20%
```

Where:
- `h2_present`: section has a `##` heading with table name and short role description
- `column_table_present_and_formatted`: a markdown table with ≥ 3 columns exists in the section
- `column_headers_match_convention`: table headers include Column (or Name), Type, and at least one of Nullable / Description
- `table_description_above_columns`: a sentence or paragraph above the table describes the table's purpose

---

#### SCD-2 Dimension Additional Check

For sections matched to SCD-2 dimension tables (dim.\* with valid_from/valid_to in reference):

Apply a **SCD-2 completeness bonus/penalty** after the standard criteria:
- All 5 SCD-2 tracking columns present (valid_from, valid_to, row_effective_date, row_expiry_date, is_current_row or equivalents): no adjustment
- 3–4 of 5 present: −5 raw points on the section score
- 1–2 of 5 present: −10 raw points
- 0 of 5 present: −15 raw points (SCD-2 columns completely absent from a SCD-2 dim)

This is applied after the weighted section score is calculated (subtract from section weighted score, floor at 0).

---

#### Glossary / Cross-Table Reference Section

**Content completeness** sub-formula:
```
score = (glossary_terms_covered / reference_term_count) × 70%
      + (each_term_has_definition) × 30%
```

Where:
- `glossary_terms_covered`: count of participant glossary terms addressing the same concept as reference terms (cross-product: different table names in the definition are OK)
- `each_term_has_definition`: all documented terms have a non-empty definition

If the participant has no Glossary section, score 0/100 raw. This triggers the missing-H2 auto-deduct.

If the participant has a glossary with different terms (e.g., covers lineage conventions instead of SCD-2), score by semantic coverage of the same cross-table concepts.

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No column definition table anywhere in document | −5 pts | Skip if `doc_has_column_tables` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| No Type column in any table | −4 pts | Skip if `doc_has_type_column` is true |
| No Nullable column in any table | −3 pts | Skip if `doc_has_nullable_column` is true |
| No Description column in any table | −3 pts | Skip if `doc_has_description_column` is true |
| No lineage_key or audit-key column in any fact or dimension table | −3 pts | Skip if `doc_has_lineage_key` is true |
| SCD-2 tracking columns entirely absent from a matched SCD-2 dimension table | −2 pts per table | Max −4 pts total (in addition to section scoring penalty above) |

Compute:
```
subtotal     = sum of all section weighted scores (after SCD-2 adjustments)
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/data-dictionary/TASK-DD-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/data-dictionary/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-DD-001
skill: task-checker-data-dictionary
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-DD-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<path>`
**Reference file:** `<path>`
**Generated:** <today's date>

---

## Score Summary

**The data dictionary Score: <total>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header) | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 2> | <ref title> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| ... | | | | | |
| **Subtotal** | | | | **<subtotal>** | |
| Auto-deducts | | | | **<deducts>** | |
| **Total** | | | | **<total>/100** | |

**Grade: <grade>**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type | Columns (ref / participant) |
|---|---|---|---|
| <ref title> | <participant title> or [MISSING] | exact / semantic / missing | <N> / <M> |

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

### <Reference Table> → participant: <matched title> (<weighted_score>/<weight> pts)

**Criteria scored:** Content (<pct>%)[, Column Completeness (20%)][, Nullability (15%)][, FK References (15%)], Structure (10%)

**Content completeness (<score>/100):**
- Columns covering equivalent topics: <N>/<ref_count>
- Descriptions are meaningful: <pct>%
- Table description paragraph present: Yes/No

**Column completeness (<score>/100):** *(if applicable)*
- Participant column count: <N> (reference: <M>)
- Columns with type: <N>/<total> (<pct>%)
- Columns with description: <N>/<total> (<pct>%)

**Nullability (<score>/100):** *(if applicable)*
- Nullable column present: Yes/No
- NOT NULL columns marked: <N>/<ref_not_null_count>
- Values are explicit YES/NO: Yes/No

**FK references (<score>/100):** *(if applicable)*
- FK columns documented: <N>/<ref_fk_count>
- FK targets are specific: Yes/No

**SCD-2 columns:** *(for SCD-2 dimension sections only)*
- valid_from: Present/Absent
- valid_to: Present/Absent
- row_effective_date: Present/Absent
- row_expiry_date: Present/Absent
- is_current_row: Present/Absent
- Score adjustment: <0 / −5 / −10 / −15> raw pts

**Structure (<score>/100):**
- H2 heading present: Yes/No
- Column table formatted: Yes/No
- Column headers include Type + Nullable/Description: Yes/No
- Table description above column table: Yes/No

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

**Improvement items:**
- [ ] <specific action>

---

## Extra Sections (participant-only, not in reference)

- **<section title>** — <brief description of the extra table>. No score impact.

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
| 45–59 | Needs work | Missing tables, incomplete columns, or no type/nullable info |
| 0–44 | Incomplete | Major tables absent or no column definitions |
```

Status icons: ✓ = scored ≥ 70% of weight, ⚠ = 40–69%, ✗ = < 40%.

---

### Step 10 — Surface Summary to Console

After writing the report, output to the conversation:

```
╔══════════════════════════════════════════════════════════╗
║  TASK-DD-001  Data Dictionary Check                      ║
║  Product : <participant product>                         ║
║  Score   : <total>/100   Grade: <grade>                  ║
║  Report  : checks/<trainee_name>/data-dictionary/TASK-DD-001_check_report<suffix>.md ║
╚══════════════════════════════════════════════════════════╝
```

Then write exactly 5–6 sentences of plain-English verdict following these rules:

1. **Sentence 1** — overall quality and what the participant did well (strongest section or criterion).
2. **Sentence 2** — the single most impactful gap (the section or criterion that lost the most points).
3. **Sentence 3** — structural observation: column table format consistency, nullability marking, FK notation quality, and whether extra tables add value.
4. **Sentence 4** — state the final score explicitly: "The data dictionary scores **<total>/100** (<grade>)" and identify the next most important fix.
5. **Sentence 5** — the single highest-value actionable change the participant should make before resubmitting.
6. **Sentence 6** *(optional)* — note any extra tables or depth beyond the reference scope that adds meaningful value.

Do **not** exceed 6 sentences. Do **not** use bullet points in the prose verdict. The final score **must appear as a number** in sentence 4.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing tables, incomplete columns, or no type/nullable info |
| 0–44 | Incomplete | Major tables absent or no column definitions |

---

## Cross-Product Evaluation Note

The participant and reference describe **different products** (e.g., participant = Sales_Orders, reference = Purchase). In this case:

- **Do not** penalize for different table names, column names, or data values (e.g., `customer_key` instead of `supplier_key`).
- **Do** evaluate structural completeness: all required table sections present, column tables formatted correctly, all four standard columns present (Column, Type, Nullable, Description).
- **Do** evaluate pattern correctness: surrogate key with IDENTITY notation, SCD-2 tracking columns for SCD-2 dimensions, lineage_key FK notation, enum values documented for status/severity columns.
- **Do not** penalize for a different number of columns per table — score column completeness as a proportion relative to the equivalent reference table's column count, capped at 100%.
- **Do not** penalize for more columns than the reference — additional columns are extra content (bonus).
- **Do not** penalize for different FK target names — score FK notation by presence and specificity of the cross-table reference pattern, not by exact table name match.
- **Do not** penalize for different SCD-2 column naming conventions (e.g., `eff_start_date` instead of `valid_from`) — score by functional equivalence (start date, end date, current flag, insert date, expiry date).

---

## Notes on Participant Format Variants

Data dictionary documents may use different organizational formats:

| Participant format | Reference expects | Impact |
|---|---|---|
| Separate H2 per staging table (e.g., stg.sale_staging AND stg.order_staging) | Single staging table section | Both are scored; extra staging table noted as extra section, no penalty |
| `NOT NULL` text instead of bold `**NO**` | Bold `**NO**` for NOT NULL | Equivalent — any explicit NOT NULL marking scores full nullability credit |
| `REQUIRED` / `OPTIONAL` instead of `YES` / `NO` | `YES` / `NO` | Equivalent |
| `PK` / `FK` notation in a separate column | FK in description cell | Equivalent — score FK criterion from wherever the FK info appears |
| SCD-2 columns named `eff_start_date`, `eff_end_date`, `current_flag` | `valid_from`, `valid_to`, `is_current_row` | Semantic equivalents — score SCD-2 completeness by functional role |
| `run_id`, `batch_key`, `audit_key` instead of `lineage_key` | `lineage_key` | Semantic equivalents |
| Glossary covers lineage or Delta Lake conventions instead of SCD-2 | SCD-2 glossary | Score glossary by cross-table concept coverage, not topic identity |
| Tables defined in numbered H2 headings (`## 1. stg.sale_staging`) | Unnumbered H2 headings | No penalty — semantic match applies |
| Column name and type in the same cell (`sale_key BIGINT`) | Separate Column and Type columns | Type criterion partially satisfied; note the format deviation |
