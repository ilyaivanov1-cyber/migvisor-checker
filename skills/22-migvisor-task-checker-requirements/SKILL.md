# Skill: task-checker-requirements

## Identity

| Field | Value |
|---|---|
| Skill number | 22 |
| Skill name | task-checker-requirements |
| Task ID | TASK-REQ-001 |
| Output file | `checks/<trainee_name>/TASK-REQ-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check my requirements"
- "validate requirements"
- "compare requirements"
- "score requirements"
- "run task-checker-requirements"
- "run 22-migvisor-task-checker-requirements"
- "22"

---

## Invocation Syntax

```
/task-checker-requirements
/task-checker-requirements participant=<path> reference=<path> trainee=<name>
run task-checker-requirements
run 22-migvisor-task-checker-requirements
```

---

## Preconditions

- A participant requirements file must exist (default: `trainees/<trainee_name>/requirements.md`)
- A reference requirements file must exist (default: `reference/requirements.md`)
- The `checks/<trainee_name>/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/requirements.md` | `participant=` |
| Reference (final) | `reference/requirements.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/requirements.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/requirements.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with appropriate error (see Step 1)
3. Fallback: `requirements.md` in workspace root

Auto-detection fallback order for reference:
1. `reference/requirements.md`

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags. If `trainee=<name>` is provided and `participant=` is not, resolve participant as `trainees/<name>/requirements.md`.
2. Otherwise run auto-detection sequences above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name from the participant path (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] requirements file.
   Provide an explicit path: /task-checker-requirements participant=<path>
   ```
5. Read both files in full.
5. Extract metadata from each file header (lines before the first `##`):
   - `product:` or `# <Product Name>` — product name
   - `project:` — project name
   - `generated:` or `date:` — generation date
   - Any `[PENDING: ...]` markers at document level

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before first `##`).
2. For each `## ` H2 heading in the reference file, add a section entry.
3. Record section title exactly as written.

Result: N scored sections = 1 (Header) + count of `##` headings in reference.

**Example** — if reference has 3 H2 headings (Functional Requirements, Non-Functional Requirements, Data Quality Requirements):
- N = 4
- Section list: Header Metadata, Functional Requirements, Non-Functional Requirements, Data Quality Requirements

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

Rank sections by complexity for remainder distribution:

**Complexity ranking** (highest → lowest):
1. Data Quality Requirements (has violation handling + summary table pattern)
2. Functional Requirements (highest requirement count, most AC expected)
3. Non-Functional Requirements
4. Any extra sections (Interface Requirements, Constraints)
5. Header Metadata (lowest)

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example** (N=4, base=25, remainder=0): all sections get 25 pts.
**Example** (N=5, base=20, remainder=0): all sections get 20 pts.
**Example** (N=6, base=16, remainder=4): top 4 sections get 17 pts, bottom 2 get 16 pts.

---

### Step 4 — Classify Section Content Types

For each section in the **participant** file, detect the following boolean flags:

| Flag | True when |
|---|---|
| `has_requirement_entries` | Section contains at least one requirement ID pattern (`FR-`, `NFR-`, `DQR-`, `IFR-`, `CON-`) |
| `has_structured_tables` | Each requirement entry has a markdown table with Field/Detail or equivalent columns |
| `has_acceptance_criteria` | Requirements contain explicit acceptance criteria (AC sub-section, AC table row, or bullet list labeled "Acceptance Criteria") |
| `has_source_refs` | Requirements contain a Source field or reference to a source spec/document |
| `has_violation_handling` | Requirements contain a Violation Handling field or section (DQR-specific) |
| `has_summary_table` | Section ends with a summary/overview table listing all requirements with severity or priority |
| `has_pending_markers` | Section contains `[PENDING: ...]` markers |

Also detect at **document level**:
- `doc_has_any_ac`: any acceptance criteria anywhere in the document
- `doc_has_all_ids`: every requirement has a traceable ID
- `doc_has_pending_where_needed`: `[PENDING]` markers present for known open items

---

### Step 5 — Build Adaptive Criteria per Section

For each section, compute criterion weights using this formula:

```
content_pct = 100
  − (25 if has_acceptance_criteria else 0)
  − (15 if has_source_refs else 0)
  − (15 if has_violation_handling else 0)
  − (10 if has_summary_table else 0)
  − 10   ← structure, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Present when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Acceptance criteria | 25% | `has_acceptance_criteria` in reference section |
| Source references | 15% | `has_source_refs` in reference section |
| Violation handling | 15% | `has_violation_handling` in reference section |
| Summary table | 10% | `has_summary_table` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section's flags to evaluate how well those criteria are met.

**Section-specific examples:**

- **Header Metadata** (no code types): content=90%, structure=10%
- **Functional Requirements** (has AC + source refs in reference): content=50%, AC=25%, source=15%, structure=10%
- **Non-Functional Requirements** (has AC, no source, no violation): content=65%, AC=25%, structure=10%
- **Data Quality Requirements** (has AC + violation handling + summary table): content=40%, AC=25%, violation=15%, summary=10%, structure=10%

---

### Step 6 — Score Each Section

#### Header Metadata

Evaluate against reference header fields:

| Sub-criterion | Weight | Checks |
|---|---|---|
| Product/project identification | 30% | product name, project name present |
| Temporal metadata | 20% | generation date, version present |
| Document scope | 30% | scope statement, purpose description |
| Author/ownership | 20% | author or team attribution |

Score = weighted sum of sub-criteria, each rated 0–100%.

#### Requirement Sections (FR, NFR, DQR, IFR, CON, etc.)

**Content completeness** sub-formula:
```
score = (functional_areas_covered / total_functional_areas) × 40%
      + (topics_addressed / total_topics_in_reference) × 40%
      + (req_count_ratio_score) × 20%
```

Where:
- `functional_areas_covered`: count of distinct functional sub-domains present (e.g., ingestion, transformation, serving, data quality, orchestration, security)
- `topics_addressed`: count of reference requirement themes present in participant
- `req_count_ratio_score`: `min(participant_count / reference_count, 1.0)` — participant having more reqs than reference scores 100%

**Acceptance criteria** sub-formula (when criterion is scored):
```
score = (reqs_with_any_ac / total_reqs) × 30%
      + (ac_measurable_testable / total_reqs) × 40%
      + (ac_references_artifacts / total_reqs) × 30%
```

Where:
- `reqs_with_any_ac`: count of requirements that have at least one acceptance criterion
- `ac_measurable_testable`: count of ACs that include concrete conditions (counts, percentages, named thresholds, pass/fail behavior)
- `ac_references_artifacts`: count of ACs that reference specific tables, columns, files, or system components

**Source references** sub-formula:
```
score = (reqs_with_source / total_reqs) × 60%
      + (sources_are_consistent / total_reqs) × 40%
```

**Violation handling** sub-formula (DQR sections):
```
score = (dqrs_with_severity / total_dqrs) × 30%
      + (dqrs_with_action / total_dqrs) × 40%
      + (dqrs_with_pipeline_behavior / total_dqrs) × 30%
```

Where:
- `dqrs_with_severity`: DQRs that classify severity (BLOCKING, WARNING, Informational, Critical, etc.)
- `dqrs_with_action`: DQRs that specify what action is taken on violation (reject record, quarantine, log, alert)
- `dqrs_with_pipeline_behavior`: DQRs that describe pipeline behavior (stop, continue, retry)

**Summary table** sub-formula:
```
score = (dqrs_in_table / total_dqrs) × 40%
      + (severity_shown / total_dqrs) × 30%
      + (blocking_classification_shown / total_dqrs) × 30%
```

**Structure** sub-formula:
```
score = (h2_present) × 25%
      + (subsections_organized) × 25%
      + (requirement_ids_present) × 25%
      + (consistent_id_scheme) × 25%
```

Where:
- `h2_present`: section exists as H2 heading
- `subsections_organized`: requirements grouped into logical H3 or bold sub-groups
- `requirement_ids_present`: all or most requirements have traceable IDs
- `consistent_id_scheme`: IDs follow a pattern (FR-XXX-NNN or FR-NNN)

**Section raw score** = sum of (criterion weight × criterion score) for all criteria in section.

**Section weighted score** = (section_raw_score / 100) × section_weight.

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No requirement IDs anywhere in document | −5 pts | Untraceability; skip if all reqs have IDs |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| No acceptance criteria anywhere in document | −4 pts | Skip if `doc_has_any_ac` is true |
| More than 30% of requirements lack individual acceptance criteria | −3 pts | Count AC-less reqs / total reqs |
| Any requirement entry has no description (ID only, no text) | −2 pts | Per occurrence, max −6 pts |
| Missing `[PENDING]` markers for open items that reference doc uses | −2 pts | Compare pending items in reference vs participant |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/TASK-REQ-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-REQ-001
skill: task-checker-requirements
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-REQ-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<path>`
**Reference file:** `<path>`
**Generated:** <today's date>

---

## Score Summary

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | <W> | <S>/100 | <W×S/100 pts> | ✓/⚠/✗ |
| <Section 2> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 3> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 4> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| **Subtotal** | | | **<subtotal>** | |
| Auto-deducts | | | **<deducts>** | |
| **Total** | | | **<total>/100** | |

**Grade: <grade>**

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

---

### <Section Name> (<weighted_score>/<weight> pts)

**Criteria scored:** Content (<pct>%), Structure (10%)[, Acceptance Criteria (25%)][, Source Refs (15%)][, Violation Handling (15%)][, Summary Table (10%)]

**Content completeness (<score>/100):**
- Functional areas covered: <list>
- Missing topics: <list>
- Requirement count: participant <N> vs reference <M>

**Acceptance criteria (<score>/100):** *(if applicable)*
- Requirements with AC: <N>/<total>
- Measurable/testable ACs: <N>/<total>
- ACs referencing artifacts: <N>/<total>

**Source references (<score>/100):** *(if applicable)*
- Requirements with source: <N>/<total>

**Violation handling (<score>/100):** *(if applicable)*
- DQRs with severity: <N>/<total>
- DQRs with action: <N>/<total>
- DQRs with pipeline behavior: <N>/<total>

**Summary table (<score>/100):** *(if applicable)*
- DQRs in table: <N>/<total>

**Structure (<score>/100):**
- H2 heading present: Yes/No
- Subsections organized: Yes/No
- Requirement IDs present: Yes/No (<pct>% coverage)
- Consistent ID scheme: Yes/No

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

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
| 45–59 | Needs work | Missing AC, source refs, or violation handling |
| 0–44 | Incomplete | Major sections missing or requirements untraced |
```

Status icons: ✓ = scored ≥ 70% of weight, ⚠ = 40–69%, ✗ = < 40%.

---

### Step 10 — Surface Summary to Console

After writing the report, output to the conversation:

```
╔══════════════════════════════════════════════════════════╗
║  TASK-REQ-001  Requirements Check                        ║
║  Product : <participant product>                         ║
║  Score   : <total>/100   Grade: <grade>                  ║
║  Report  : checks/<trainee_name>/TASK-REQ-<NNN>_check_report<suffix>.md ║
╚══════════════════════════════════════════════════════════╝
```

Then write exactly 5–6 sentences of plain-English verdict following these rules:

1. **Sentence 1** — overall quality and what the participant did well (strongest section or criterion).
2. **Sentence 2** — the single most impactful gap (the criterion or section that lost the most points).
3. **Sentence 3** — format or structural observation (ID scheme, subsection organization, inline vs structured format).
4. **Sentence 4** — acceptance criteria status (present/absent, measurable/not, coverage percentage).
5. **Sentence 5** — the single highest-value fix the participant should make next.
6. **Sentence 6** *(optional)* — note any extra sections or notable extras beyond the reference scope.

Do **not** exceed 6 sentences. Do **not** use bullet points in the prose verdict.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing AC, source refs, or violation handling |
| 0–44 | Incomplete | Major sections missing or requirements untraced |

---

## Cross-Product Evaluation Note

The participant and reference may describe **different products** (e.g., participant = Sales_Orders, reference = GlobalPurchase_Project). In this case:

- **Do not** penalize for different domain entities, table names, or business rules.
- **Do** evaluate structural completeness: sections present, ID scheme, AC coverage, source refs, violation handling.
- **Do** evaluate pattern correctness: requirement format, AC format, DQR violation handling format.
- Content completeness score reflects coverage of equivalent functional areas, not identical requirement text.

---

## Notes on Participant Format Variants

Requirements documents may use different formats. Score each format against what the reference expects:

| Participant format | Reference expects | Impact |
|---|---|---|
| Inline bold `**FR-XXX** — description` | Per-requirement H3 with structured table | Structure criterion reduced; AC/source criteria likely 0% if absent |
| Per-requirement H3 with table | Per-requirement H3 with table | Full credit available for all criteria |
| Numbered list without IDs | IDs required | −5 auto-deduct for missing IDs |
| Subsection grouping (1.1, 1.2) | Flat H3 list | No penalty; subsection organization scores full structure credit |

When format differs, the AC criterion is evaluated on whether AC **exists in any form** (inline, table row, bullet list), not whether it matches the reference's exact format.
