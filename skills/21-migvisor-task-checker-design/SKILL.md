---
name: 21-migvisor-task-checker-design
description: Evaluates a participant's design.md against a reference design_final.md. Works with any product, any number of top-level sections. Validates SQL DDL correctness (CREATE TABLE, MERGE, VIEW, GRANT), Python code patterns, and ASCII/Mermaid diagram completeness. Scores per section with adaptive criteria, applies auto-deducts, and produces a scored summary with 5–6 sentence prose.
---

# Skill: task-checker-design

## Identity

- **Name:** `task-checker-design`
- **Selection signal:** Evaluates and scores a participant-submitted design document against a reference final design — use when a participant has drafted a design.md and wants structured feedback on completeness, SQL accuracy, code patterns, and diagram fidelity.
- **Trigger phrases:**
  - "check my design"
  - "validate design"
  - "compare design"
  - "score design"
  - "check task design"
  - "run 21-migvisor-task-checker-design"

---

## Invocation Syntax

```
/task-checker-design [participant_file] [reference_file] [--product <name>] [trainee=<name>]
```

All arguments are optional. Examples:
- `/task-checker-design my-design.md` — participant file supplied; reference auto-resolved
- `/task-checker-design design.md reference/design.md` — both supplied
- `/task-checker-design --product Purchase` — both files auto-resolved; product name overridden
- `/task-checker-design trainee=alice` — auto-resolve participant from trainees/alice/
- `/task-checker-design` — everything auto-resolved (single trainee folder)

---

## Preconditions

| Condition | Check | If not met |
|---|---|---|
| Participant file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1A) | Ask: "Provide the path to your design submission, e.g. `/task-checker-design my-design.md`" |
| Reference file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1B) | If zero: "No reference file found. Supply it as the second argument." If multiple: "Multiple candidates found: [list]. Which should I use?" |
| Participant file readable | File exists and is non-empty | "Cannot read submission at [path]. Check the path and try again." |
| Participant file has structure | File contains at least one `## ` heading | "Submission does not appear to be a valid design document — no sections found. Verify the correct file." |

---

## Input Inventory

| Input | Source | Required |
|---|---|---|
| Participant's design file | Path supplied at invocation (positional arg 1) OR auto-resolved | Yes |
| Reference (final) design file | Path supplied at invocation (positional arg 2) OR auto-resolved | Yes |
| Product name | Derived from: (1) `--product` flag, (2) `# Design: <Name>` H1 heading, (3) `**Product:**` metadata field, (4) `product:` YAML frontmatter, (5) parent directory name | Derived |

---

## Workflow

### Step 1 — Resolve files and product

**1A — Participant file**

If a path was supplied as argument 1, use it. Otherwise apply trainee-aware auto-detection:

1. If `trainee=<name>` flag is provided: look for `trainees/<name>/design.md`. If not found, abort: *"No participant file at trainees/<name>/design.md. Verify the trainee name and file."*
2. Otherwise: scan `trainees/` for immediate subdirectories.
   - Exactly 1 found: use `trainees/<that-name>/design.md`; record `<that-name>` as the trainee name.
   - 0 found: abort with *"No trainees/ subdirectories found. Provide an explicit path."*
   - 2 or more found: abort with *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: if `trainees/` does not exist, search workspace root for `design.md`.

Record the resolved trainee name from the participant file path for output path construction in Step 9.

**1B — Reference file**

If a path was supplied as argument 2, use it. Otherwise look for `reference/design.md`. If found: use it. If not found: abort with *"No reference file found at reference/design.md. Supply an explicit reference path."*

**1C — Product name**

Derive in this order:
1. `--product <name>` flag
2. `# Design: <Name>` H1 heading in participant file
3. `**Product:**` metadata field in participant file
4. `product:` YAML frontmatter
5. Name of the immediate parent directory
6. Fallback: `[Unknown Product]`

**1D — Read files**

Read participant file and reference file in parallel.

---

### Step 2 — Check for identical files

Compute whether participant file and reference file are byte-for-byte identical.

- If identical: set `IDENTICAL_TO_REFERENCE = true`. **Do not deduct any points.** Add a warning in the report header and conversation summary.
- If not identical: proceed normally.

---

### Step 3 — Detect sections dynamically

**3A — Build section list from reference**

Detect scoreable sections:

1. **Header Metadata** — the document header (H1 + metadata fields before the first `## ` heading). Always one scored section.

2. **Top-level H2 sections** — all `## ` headings. Each `## ` heading = one scored section. The subsections within (H3, H4) are part of that section's content, not separate scored sections.

For each reference section, record:
- Heading text
- All H3 and H4 subsection headings within it
- All code blocks and their types (see Step 3B)
- All markdown tables
- Prose text

**3B — Classify code blocks within each section**

For every fenced code block in the reference section, classify as:

| Block type | Detection rule |
|---|---|
| `SQL_DDL` | Block contains `CREATE TABLE IF NOT EXISTS` or `CREATE [OR REPLACE] [MATERIALIZED] VIEW` |
| `SQL_DML` | Block contains `MERGE INTO`, `UPDATE … SET`, or `INSERT INTO` |
| `SQL_GRANT` | Block contains `GRANT ` |
| `SQL_QUERY` | Block tagged `sql` and contains `SELECT` with no DDL/DML keywords |
| `PYTHON` | Block tagged `python` |
| `DIAGRAM` | Block with no language tag (bare ```) OR tagged `mermaid` |
| `OTHER` | Everything else (shell, yaml, etc.) |

Record for each section: `has_sql_ddl`, `has_sql_dml`, `has_sql_grant`, `has_sql_query`, `has_python`, `has_diagram`.

For SQL_DDL blocks: extract table names (e.g., `catalog.schema.table`), column names, data types, constraint names, TBLPROPERTIES keys.

For SQL_DML blocks: extract target table name, ON predicate column(s), WHEN clauses.

For Python blocks: extract function names, key variable names, key method calls.

For Diagram blocks: extract entity names (words before `──`, `→`, `|`, or newlines in ASCII; node IDs in Mermaid).

**3C — Match sections in participant file**

For each reference section, find the best match in the participant file:

1. **Heading text match** — keyword overlap: "Data Model", "Ingestion", "Transformation", "Serving", "Observability", "Architecture", "Schema", "Pipeline", "Security", etc. Use best text match.
2. **No match** — score 0 for that reference section.

| Outcome | Action |
|---|---|
| Match found | Evaluate normally — adaptive rubric |
| Reference section with no match in participant | Score 0; note as absent |
| Participant section not matched to any reference section | Note as extra; do not score; do not penalise |

---

### Step 4 — Calculate point weights

**4A — Check for explicit weights**

Look for a `scoring_weights` entry in the reference file's YAML frontmatter. If present and sums to 100: use them.

**4B — Auto-calculate weights**

If no explicit weights:
1. Count N = total scored sections (Header Metadata + all H2 sections).
2. Base weight = `floor(100 / N)`.
3. Rank sections by **content complexity score** (complex section = more code block types present; more tables; more subsections). Distribute the remainder one point at a time to the highest-ranked sections.
4. Minimum weight per section: 5 pts. Maximum: 35 pts.

Display calculated weights in the Score Summary table.

---

### Step 5 — Handle placeholder and deferred fields

Before scoring, identify any code block or prose containing `[TBD]`, `[TODO]`, `[FILL IN]`, `[PENDING]`, `???`, or `<placeholder>`.

- Treat as **intentional deferrals**, not missing content.
- If a SQL DDL column definition is `[TBD]`: award 50% of that column's contribution and flag `[DEFERRED]`.
- If an entire table DDL block is absent: apply normal missing-table scoring.

---

### Step 6 — Score each section with adaptive rubric

#### Criterion weights — adaptive per section

For each reference section, compute active criterion weights based on which block types are present:

| Criterion | Active when | Base % |
|---|---|---|
| **Content completeness** | Always | See formula below |
| **SQL accuracy** | `has_sql_ddl` OR `has_sql_dml` OR `has_sql_grant` OR `has_sql_query` | 30% |
| **Code accuracy** | `has_python` | 20% |
| **Diagram completeness** | `has_diagram` | 15% |
| **Structure** | Always | 10% |

**Content completeness % formula:**
```
content_pct = 100 − (30 if any SQL else 0) − (20 if has_python else 0) − (15 if has_diagram else 0) − 10
```
Minimum content_pct = 25% (unused criterion percentages are added to content completeness, never dropped below 25%).

Examples:
- Section with SQL + Python + Diagram: content=25, sql=30, code=20, diagram=15, structure=10 → total 100
- Section with SQL only: content=60, sql=30, code=0, diagram=0, structure=10 → total 100
- Section with Python + Diagram (no SQL): content=55, sql=0, code=20, diagram=15, structure=10 → total 100
- Narrative/table only: content=90, sql=0, code=0, diagram=0, structure=10 → total 100

---

#### Per-criterion evaluation rules

**Content completeness** — `content_pct`%

- All H3 / H4 subsections from the reference section are present in the participant section. Score proportionally: (matched subsections) / (total reference subsections).
- All reference prose topics addressed (design decisions, rationale, named tables/components mentioned).
- All reference markdown tables reproduced (correct headers and substantially correct rows).
- Named design artifacts (notebook names, file paths, function names listed in reference) appear in participant section.

Score: (subsections present/total) × 40% + (topics addressed/total) × 40% + (tables reproduced/total) × 20%.

---

**SQL accuracy** — 30% (when applicable)

Evaluate every SQL code block in the participant section against the corresponding reference SQL block. Match blocks by: (1) same table/view name, (2) same MERGE target, (3) same GRANT target.

**DDL (CREATE TABLE / CREATE VIEW) checks:**

| Check | Points |
|---|---|
| `CREATE TABLE IF NOT EXISTS` (idempotency keyword present) | 10% of SQL criterion |
| Three-part `catalog.schema.table` name (not two-part) | 10% |
| `USING DELTA` present | 10% |
| All reference column names present (score proportionally: matched cols / total cols) | 20% |
| Correct data types per column (BIGINT / INT / STRING / DATE / TIMESTAMP / DECIMAL(p,s) / BOOLEAN — score per column) | 15% |
| `COMMENT` clauses present (on table and/or columns) | 10% |
| `CONSTRAINT pk_*` PRIMARY KEY clause present (if reference has one) | 10% |
| `TBLPROPERTIES` with correct retention values | 10% |
| For dimension tables: `delta.enableChangeDataFeed = 'true'`; for fact/staging: `'false'` | 5% |

Average across all DDL blocks in the section.

**MERGE (DML) checks:**

| Check | Points |
|---|---|
| `MERGE INTO … AS tgt USING … AS src` syntax present | 15% |
| `ON` predicate references correct business key column | 20% |
| `WHEN MATCHED THEN UPDATE SET` clause present | 20% |
| `WHEN NOT MATCHED [BY TARGET] THEN INSERT` clause present | 20% |
| For SCD-2 expire step: UPDATE sets `is_current_row = FALSE` and `row_expiry_date` | 15% |
| For SCD-2 insert step: INSERT sets `is_current_row = TRUE` and `row_expiry_date = DATE '9999-12-31'` | 10% |

Score proportionally per MERGE block present. If SCD-2 clauses not applicable to the block, redistribute those points to the present checks.

**VIEW / MATERIALIZED VIEW checks:**

| Check | Points |
|---|---|
| `CREATE OR REPLACE [MATERIALIZED] VIEW` with correct name | 20% |
| `COMMENT` on view present | 10% |
| All reference columns present in SELECT | 30% |
| Correct JOIN type and ON conditions | 25% |
| `GROUP BY` present if reference aggregates; correct columns | 15% |

**GRANT checks:**

| Check | Points |
|---|---|
| `GRANT` targets correct schema/table objects | 40% |
| Correct privilege types (SELECT / MODIFY / REFRESH / USE SCHEMA) per target | 40% |
| Correct role/principal targets | 20% |

Average SQL accuracy score across all SQL block types present in section.

---

**Code accuracy** — 20% (when applicable)

For each Python block in the participant section, compare to the corresponding reference Python block (matched by function name or surrounding H3 heading).

| Check | Points |
|---|---|
| Function signature matches reference: correct name, parameter names, return type annotation | 20% |
| Credential retrieval pattern: `dbutils.secrets.get(scope=…, key=…)` — no hardcoded credentials | 15% |
| Task value publish/read pattern: `dbutils.jobs.taskValues.set/get` used where reference uses it | 15% |
| Correct Spark API calls: `spark.table()`, `.filter()`, `.join()`, `F.coalesce()`, `.write.format("delta")` where reference uses them | 20% |
| COALESCE/sentinel fallback present for surrogate key joins (if reference has it) | 10% |
| Watermark filter / incremental extraction logic: WHERE clause or filter references the cutoff variable | 10% |
| Correct target table references (three-part names) | 10% |

Score proportionally across all Python blocks in the section.

---

**Diagram completeness** — 15% (when applicable)

For ASCII diagrams (bare ``` code blocks with arrow-style content) and Mermaid diagrams:

| Check | Points |
|---|---|
| All entity names from reference diagram present in participant diagram (score proportionally: matched / total) | 50% |
| Key relationships (arrows/edges) between entities reproduced directionally correctly | 30% |
| Supporting reference tables (schema role table, join keys table) present in participant section | 20% |

An entity is "present" if its name (or a recognizable abbreviation) appears in the participant's diagram block. Diagram block itself may use different box-drawing characters — style differences are not penalised.

---

**Structure** — 10%

| Check | Points |
|---|---|
| Section has the same top-level heading text or equivalent keyword match | 20% |
| H3 / H4 subsection headings are present and ordered logically (same order not required, all major topics present) | 40% |
| Code blocks use correct fencing (triple backtick with language tag for SQL/Python) | 20% |
| Consistent formatting (no broken markdown tables, consistent indentation within code blocks) | 20% |

---

### Step 7 — Apply approach policy

Before finalising scores:

- Participant uses different alias names in SQL (e.g., `AS t` vs `AS tgt`) → **no deduction**
- Participant uses `WHERE` clause in MERGE USING subquery vs JOIN-based subquery for same logic → **no deduction**
- Participant uses different ASCII characters for diagrams (different box-drawing, `-->` vs `──►`) → **no deduction**
- Participant adds extra columns to a DDL table not in the reference → **no deduction**; note as supplementary
- Participant adds extra subsections not in reference → **note as extra**, no deduction
- Participant splits a reference H3 into two H3 sections → **no deduction** if both cover the same topic
- Column data type precision differences ≤ 1 decimal place (e.g., `DECIMAL(18,2)` vs `DECIMAL(19,2)`) → **no deduction**; note as minor variance
- Participant uses Python `date_format(col, "yyyyMMdd").cast("int")` vs reference's equivalent pattern → **no deduction** if semantically equivalent

Deduct only for **missing tables, missing columns, wrong SQL syntax patterns, missing required keywords (`USING DELTA`, `CREATE TABLE IF NOT EXISTS`, `MERGE INTO`), or technically incorrect logic** — not for style, alias choice, or additional content.

---

### Step 8 — Apply auto-deducts (after rubric scoring)

| Condition | Deduction |
|---|---|
| A DDL table present in reference is entirely absent from participant | −3 pts (global, once per missing table, max −9 pts) |
| `USING DELTA` missing from ≥ 3 DDL tables (systematic omission) | −5 pts (global, once) |
| `CREATE TABLE IF NOT EXISTS` → `CREATE TABLE` (non-idempotent, systematic across ≥ 3 tables) | −3 pts (global, once) |
| SCD-2 MERGE pattern absent when reference section requires it | −4 pts (global, once) |
| A reference H2 section is entirely absent from participant | −5 pts (global, once per missing section, max −15 pts) |
| Hardcoded credential strings visible in any code block | −5 pts (global, once) |
| Surrogate key resolution (SK resolver) design absent when reference has it | −3 pts (global, once) |
| Lineage key propagation design absent (no mention of lineage_key in fact/dim DDL or code) | −3 pts (global, once) |

---

### Step 9 — Assemble the check report

Determine the output file path:
1. Extract the trainee name from the resolved participant file path: `trainees/<name>/...` → `<name>`. If participant was not under `trainees/`, use `unknown_trainee`.
2. Base name: `checks/<trainee_name>/TASK-DESIGN-001_check_report.md`
3. If it does not exist: write it.
4. If it exists: increment suffix (`_v2`, `_v3`, …) until a free path is found.
5. **Never overwrite an existing report file.**

Create the `checks/<trainee_name>/` directory if it does not exist.

---

### Step 10 — Surface summary in conversation

Output the following block to the console:

```
✓ Check complete — [PRODUCT_NAME] design

Score: [N] / 100   ([grade label])

  Header Metadata         [N]/[weight]   [✓/⚠/✗]
  [Section heading]       [N]/[weight]   [✓/⚠/✗]
  [Section heading]       [N]/[weight]   [✓/⚠/✗]
  ...

Extra sections (not scored):
  - [Section heading]
  (or "None")

[N] improvement items flagged. Full report: checks/[report_filename]
[If IDENTICAL_TO_REFERENCE]: ⚠ Warning: submission is byte-for-byte identical to the reference file.
```

Then immediately output a **plain-English summary** of 5–6 sentences. Rules:
- Sentence 1: overall result — score, grade, and one-line verdict on the design's quality.
- Sentence 2: what the design does well — name the strongest 1–2 sections and specifically why (e.g., "DDL section includes correct USING DELTA, IDENTITY PKs, COMMENT clauses, and TBLPROPERTIES on all tables"; "SCD-2 MERGE pattern correctly implements both expire and insert steps").
- Sentence 3 (optional): if the participant includes extra sections or tables not in the reference, name them and note they add coverage. If none, skip.
- Sentence 4: what needs improvement — name the specific section and gap (missing DDL table, wrong MERGE predicate, absent diagram entity, hardcoded credential), stating points recoverable. If no gaps, say so.
- Sentence 5: next step — if score ≥ 75, say "You can proceed to the next task." If score < 75, say "Address the items above and re-run the checker before moving on."
- No bullet points, no markdown headers — flowing prose only.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | **Excellent** | Thorough and technically accurate. You can proceed to the next task. |
| 75–89 | **Good** | Minor gaps. Address flagged items; proceeding is acceptable if items are low-risk. |
| 60–74 | **Acceptable** | Several gaps. Revise before proceeding. |
| 45–59 | **Needs work** | Missing tables, incorrect SQL patterns, or diagrams absent. Substantial revision required. |
| 0–44 | **Incomplete** | Major sections missing, SQL systematically wrong, or critical design patterns absent. |

---

## Check Report Template

Written to `checks/<trainee_name>/TASK-DESIGN-001_check_report.md` (or `_v2`, `_v3` … if prior reports exist):

```markdown
---
task_id: TASK-DESIGN-001
product: [product name]
participant_file: [resolved path]
reference_file: [resolved path]
checked_at: [ISO 8601]
sections_evaluated: [N]
total_score: [N]/100
grade: [label]
identical_to_reference: [true|false]
---

# Task Check Report — design
_[Product name] | [timestamp]_

[If identical_to_reference: ⚠ Warning: participant file is byte-for-byte identical to the reference.]

**File resolution log:**
- Participant file: [path] — [how resolved]
- Reference file: [path] — [how resolved]
- Product: [name] — [derivation source]
- Sections in reference: [N] | Sections in participant: [N] (matched: [N], extra: [N])
- Point weights: [auto-calculated or from frontmatter]
- Reference SQL objects: [N] DDL tables | [N] MERGE blocks | [N] views | [N] Python blocks | [N] diagrams

---

## Score Summary

**The design document Score: [N]**

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| Header Metadata | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| [H2 section] | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| **Total** | | **100** | **[N]** | |

Auto-deducts: [list applied deductions, or "None"]

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### [Section heading] ([score]/[weight])
_Matched to participant [heading]_

**Active criteria for this section:** Content [N]% | SQL [N]% (or N/A) | Code [N]% (or N/A) | Diagram [N]% (or N/A) | Structure [N]%

**Content completeness ([pts]/[max]):**
[Subsections present vs. absent; topics addressed vs. missing; tables reproduced vs. missing]

**SQL accuracy ([pts]/[max] — or N/A):**
_DDL tables:_
- [table name]: [checklist of DDL checks — present/missing per requirement]

_MERGE blocks:_
- [target table]: [ON predicate correct/wrong; WHEN clauses present/missing; SCD-2 clauses correct/wrong]

_Views:_
- [view name]: [column completeness, JOIN correctness, COMMENT present]

_Grants:_
- [grant block]: [targets correct, privileges correct, principals correct]

**Code accuracy ([pts]/[max] — or N/A):**
- [function/block name]: [signature match, credential pattern, taskValues pattern, Spark API calls, sentinel fallback]

**Diagram completeness ([pts]/[max] — or N/A):**
- Entities from reference: [list] | Found in participant: [list] | Missing: [list]
- Relationship accuracy: [specific arrows/edges correct or wrong]
- Supporting tables: [present/absent]

**Structure ([pts]/[max]):**
[Section heading match; subsections organized; code block fencing; formatting]

**Deferred fields `[DEFERRED]`:** [list]

**Improvement items:**
- [ ] [Specific actionable item]

[Repeated for all evaluated sections]

---

## Extra Sections (not in reference)
[List with section heading and brief note, or "None"]

## Approach Notes
[Valid alternatives — alias differences, style variations, equivalent logic patterns]

---

## Priority Improvements
Top 3 items ranked by score impact:
1. [Section — criterion — specific gap — points recoverable]
2. [Section — criterion — specific gap — points recoverable]
3. [Section — criterion — specific gap — points recoverable]

---

## Next Step
[score ≥ 75]: You can proceed to the next task.
[score < 75]: Address the priority improvements above and re-run the checker before moving on.
```
