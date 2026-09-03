---
name: 17-migvisor-task-checker-to-be
description: Evaluates a participant's to-be design document against a reference. Works with any product, any file names, any workspace structure, and any number of sections. Scores all sections found in the reference (0–100 total), with dedicated checks for SQL code blocks, Mermaid diagrams, and Python code. Provides per-section comments, flags improvement areas, and acknowledges valid alternative approaches.
---

# Skill: task-checker-to-be

## Identity

- **Name:** `task-checker-to-be`
- **Selection signal:** Evaluates and scores a participant-submitted to-be design document against a reference — use when a participant has completed the to-be design task and wants structured feedback.
- **Trigger phrases:**
  - "check my to-be"
  - "evaluate to-be submission"
  - "score to-be"
  - "review to-be task"
  - "check task to-be"
  - "run 17-migvisor-task-checker-to-be"

---

## Invocation Syntax

```
/task-checker-to-be [participant_file] [reference_file] [--product <name>] [trainee=<name>]
```

All arguments are optional. Examples:
- `/task-checker-to-be my-to-be.md` — participant file supplied; reference auto-resolved
- `/task-checker-to-be submissions/alice.md reference/to-be.md` — both supplied
- `/task-checker-to-be --product Sales_Orders` — both files auto-resolved; product name overridden
- `/task-checker-to-be trainee=alice` — auto-resolve participant from trainees/alice/
- `/task-checker-to-be` — everything auto-resolved (single trainee folder)

---

## Preconditions

| Condition | Check | If not met |
|---|---|---|
| Participant file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1A) | Ask: "Provide the path to your to-be submission, e.g. `/task-checker-to-be my-to-be.md`" |
| Reference file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1B) | If zero: "No reference file found. Supply it as the second argument." If multiple: "Multiple reference candidates found: [list]. Which should I use?" |
| Participant file readable | File exists and is non-empty | "Cannot read submission at [path]. Check the path and try again." |
| Participant file has structure | File contains at least one `## ` heading | "Submission does not appear to be a valid to-be document — no H2 sections found. Verify the correct file." |

---

## Input Inventory

| Input | Source | Required |
|---|---|---|
| Participant's to-be file | Path supplied at invocation (positional arg 1) OR auto-resolved | Yes |
| Reference to-be file | Path supplied at invocation (positional arg 2) OR auto-resolved | Yes |
| Product name | Derived from: (1) `--product` flag, (2) `# To-Be Design: <Name>` H1 heading, (3) `product:` YAML frontmatter, (4) parent directory name | Derived |

---

## Workflow

### Step 1 — Resolve files and product

**1A — Participant file**

If a path was supplied as argument 1, use it. Otherwise apply trainee-aware auto-detection:

1. If `trainee=<name>` flag is provided: look for `trainees/<name>/to-be.md`. If not found, abort: *"No participant file at trainees/<name>/to-be.md. Verify the trainee name and file."*
2. Otherwise: scan `trainees/` for immediate subdirectories.
   - Exactly 1 found: use `trainees/<that-name>/to-be.md`; record `<that-name>` as the trainee name.
   - 0 found: abort with *"No trainees/ subdirectories found. Provide an explicit path or create trainees/<name>/."*
   - 2 or more found: abort with *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: if `trainees/` does not exist, search the workspace root for `to-be.md`.

Record the resolved trainee name from the participant file path for output path construction in Step 8.

**1B — Reference file**

If a path was supplied as argument 2, use it. Otherwise look for `reference/to-be.md`. If found: use it. If not found: abort with *"No reference file found at reference/to-be.md. Supply an explicit reference path."*

**1C — Product name**

Derive in this order:
1. `--product <name>` flag
2. `# To-Be Design: <Name>` H1 heading in the participant file
3. `product:` field in YAML frontmatter
4. Name of the immediate parent directory
5. Fallback: `[Unknown Product]`

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

Scan the reference file for all headings matching `## <N>` where N is a number, immediately followed by a space, dot, or end-of-token. This is the canonical section list for this evaluation.

Record for each section: its number, its full heading text, its content, its code blocks (SQL/Python/PySpark), and its diagrams (Mermaid).

**3B — Inventory code blocks and diagrams per reference section**

For each reference section, record:
- **SQL blocks:** count and content of all ` ```sql ` fenced blocks
- **Python / PySpark blocks:** count and content of all ` ```python ` fenced blocks
- **Mermaid diagrams:** count and type (`erDiagram`, `flowchart`, `sequenceDiagram`, etc.) of all ` ```mermaid ` blocks

This inventory defines what code and diagram evidence is expected in the participant's corresponding section.

**3C — Match sections in participant file**

For each reference section, find the best match in the participant file using this priority order:

1. **Exact number match** — same `## N` number AND heading keywords overlap. Use if headings are similar.
2. **Heading text match** — search all participant sections for the one whose heading text most closely matches the reference heading by keyword overlap ("definition", "consumer", "model", "lineage", "calculation", "source", "data", etc.). Use the best text match regardless of its number.
3. **No match** — score 0 for that reference section.

Any participant section not claimed by a reference section match is treated as extra content.

| Outcome | Action |
|---|---|
| Match found (by number or text) | Evaluate normally — rubric + code/diagram checks |
| Reference section with no match in participant | Score 0; note as absent |
| Participant section not matched to any reference section | Note as extra content; do not score; do not penalise |

---

### Step 4 — Calculate point weights

**4A — Check for explicit weights**

Look for a `scoring_weights` entry in the reference file's YAML frontmatter. If present and weights sum to 100: use them.

**4B — Auto-calculate weights**

If no explicit weights:
1. Count N = total sections in the reference.
2. Base weight = `floor(100 / N)`.
3. Distribute remainder one point at a time to sections in descending order of content length.
4. Minimum weight: 5 pts. Maximum: 35 pts.

Display calculated weights in the Score Summary table.

---

### Step 5 — Handle `[USER INPUT REQUIRED]` and `[PENDING DECISION]` fields

Before scoring, identify any field or row containing `[USER INPUT REQUIRED]`, `[PENDING DECISION]`, `TBD`, `TODO`, or `[FILL IN]`.

- Treat as **intentional deferrals**, not missing content.
- If other non-deferred content in the same criterion provides sufficient coverage: award full points.
- If the deferred field is the only evidence for that criterion: award 50% and note as pending.
- Flag each deferred field with the label `[DEFERRED]`.

---

### Step 6 — Score each section

Apply the **Generic Per-Section Rubric** plus **Code and Diagram Checks** to every matched section.

```
section → { weight, score, rubric_results[], code_check_results[], diagram_check_results[], deferred_fields[], improvements[] }
```

---

### Step 7 — Apply approach policy

Before finalising scores:

- Different structure but same information covered → **no deduction**
- Participant uses PySpark where reference uses SQL for the same logic → **no deduction** if the logic is equivalent
- Participant uses a different diagram type but conveys the same relationships → **no deduction**
- Extra code blocks or diagrams beyond what reference has → **no deduction**, note as supplementary

Deduct only for **missing or incorrect information**, not for **different presentation**.

---

### Step 8 — Assemble the check report

Determine the output file path:
1. Extract the trainee name from the resolved participant file path: `trainees/<name>/...` → `<name>`. If participant was not under `trainees/`, use `unknown_trainee`.
2. Base name: `checks/<trainee_name>/TASK-TO-BE-001_check_report.md`
3. If it does not exist: write it.
4. If it exists: increment suffix (`_v2`, `_v3`, …) until a free path is found.
5. **Never overwrite an existing report file.**

Create the `checks/<trainee_name>/` directory if it does not exist.

---

### Step 9 — Surface summary in conversation

Output the following block to the console:

```
✓ Check complete — [PRODUCT_NAME] to-be

Score: [N] / 100   ([grade label])

  [Section 1 heading]   [N]/[weight]   [✓/⚠/✗]
  [Section 2 heading]   [N]/[weight]   [✓/⚠/✗]
  ...
  [Section N heading]   [N]/[weight]   [✓/⚠/✗]

Extra sections (not scored):
  - [Section heading]
  (or "None" if no extra sections)

[N] improvement items flagged. Full report: checks/[report_filename]
[If IDENTICAL_TO_REFERENCE]: ⚠ Warning: submission is byte-for-byte identical to the reference file.
```

Then immediately output a **plain-English summary** of 5–7 sentences. Rules:
- Sentence 1: overall result — score, grade, and one-line verdict.
- Sentence 2: what the submission does well — name the strongest 1–2 sections and why.
- Sentence 3 (optional): if the participant includes code blocks or diagrams that go beyond what the reference has (e.g., a Mermaid diagram where the reference has only ASCII art, extra SQL blocks, additional Python code), name them by section and artifact type and note they add value beyond what was required. If no supplementary artifacts exist, skip this sentence.
- Sentence 4: if participant has extra sections not in the reference, name them. If none, skip.
- Sentence 5–6: what needs improvement — gaps, missing SQL/diagrams, wrong platform syntax — name the section and points recoverable.
- Sentence 7: next step — if score ≥ 75, say "You can proceed to the next task." If score < 75, say "Address the items above and re-run the checker before moving on."
- No bullet points, no markdown headers — flowing prose only.

---

## Generic Per-Section Rubric

Applied to every section. Points expressed as **percentages of that section's weight**.

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Coverage** | 35% | Key topics, entities, subsections, and code/diagram types present in the reference section are addressed in the participant section. If reference has SQL blocks, participant must have SQL or equivalent code. If reference has diagrams, participant must have diagrams. Score proportionally. |
| **Specificity** | 25% | Information uses named objects, target column names, data types, catalog paths, notebook names, and rule IDs rather than vague descriptions. Code uses actual table/column names, not placeholders. |
| **Technical accuracy** | 20% | Code and content targets the correct platform (Databricks/Delta Lake, not SQL Server). No T-SQL syntax (e.g. `TOP`, `NOLOCK`, `IDENTITY` without `GENERATED ALWAYS AS`) in target SQL. Transformation rules applied correctly. |
| **Issues and gaps flagged** | 10% | Known limitations, open decisions (`[PENDING DECISION]`), DQ rules, migration risks, or deferred items are called out explicitly. |
| **Structure** | 5% | Required subsections, tables, code blocks, and diagrams are present and consistently formatted. |
| **Code / Diagram quality** | 5% | Applied only when reference section contains code or diagrams. SQL/Python is syntactically plausible and complete (not truncated or placeholder-only). Diagrams render correctly (valid Mermaid syntax, correct entity relationships). |

**Criterion points are rounded to the nearest integer.**

---

## Code and Diagram Checks

Applied in addition to the rubric when the reference section contains code blocks or diagrams.

### SQL checks

For each SQL block in the participant section:

| Check | Pass condition | Fail action |
|---|---|---|
| Platform syntax | No SQL Server–specific syntax: no `TOP N`, `NOLOCK`, `WITH (...)` table hints, `IDENTITY(1,1)` (without `GENERATED ALWAYS AS`), `NVARCHAR`, `DATETIME`, `GETDATE()`, `ISNULL()` (flag if used as NULL check vs. COALESCE) | Deduct from Technical accuracy |
| Target naming | Table names use Unity Catalog three-part path (`catalog.schema.table`) or documented shorthand; no source schema names (`Fact.*`, `Dimension.*`, `Integration.*`) | Deduct from Specificity |
| Key SQL elements | DDL sections include `USING DELTA`; MERGE sections use `MERGE INTO ... WHEN MATCHED / NOT MATCHED`; DQ sections include assertion logic | Deduct from Coverage proportionally |
| Completeness | SQL block is not truncated mid-statement or filled with `...` placeholders | Deduct from Code/Diagram quality |

### Python / PySpark checks

| Check | Pass condition | Fail action |
|---|---|---|
| Framework | Uses PySpark DataFrame API or Databricks SQL; no raw T-SQL execution against source tables | Deduct from Technical accuracy |
| Key patterns | Watermark read, staging write, MERGE or equivalent upsert present where reference has them | Deduct from Coverage |
| Completeness | Code block is not a stub or placeholder | Deduct from Code/Diagram quality |

### Mermaid diagram checks

| Check | Pass condition | Fail action |
|---|---|---|
| Diagram present | If reference has `erDiagram`, participant must have `erDiagram` or equivalent relationship diagram | −3 pts auto-deduct |
| Entity coverage | Diagram covers at least 80% of entities present in the reference diagram | Deduct from Coverage proportionally |
| Relationship direction | No reversed relationships (source → target direction correct) | Deduct from Technical accuracy |
| Syntax validity | Diagram block uses valid Mermaid keywords; no obvious syntax errors | Deduct from Code/Diagram quality |

---

## Auto-deducts (applied after rubric scoring)

| Condition | Deduction |
|---|---|
| Section describes the **source/legacy** system instead of the **target** platform | −50% of section score |
| SQL uses SQL Server–specific syntax throughout (not isolated instances) | −30% of section score |
| Mermaid diagram present in reference but completely absent in participant | −3 pts |
| SQL block present in reference but completely absent in participant | −3 pts |
| Python/PySpark block present in reference but completely absent in participant | −3 pts |
| Calculations section: formulas present but no SQL or code implementation shown | −4 pts |

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | **Excellent** | Thorough and accurate. You can proceed to the next task. |
| 75–89 | **Good** | Minor gaps. Address flagged items; proceeding is acceptable if items are low-risk. |
| 60–74 | **Acceptable** | Several gaps. Revise before proceeding. |
| 45–59 | **Needs work** | Significant sections incomplete or inaccurate. Substantial revision required. |
| 0–44 | **Incomplete** | Major sections missing, wrong platform, or no code where required. Restart affected sections. |

---

## Check Report Template

Written to `checks/<trainee_name>/TASK-TO-BE-001_check_report.md` (or `_v2`, `_v3` … if prior reports exist):

```markdown
---
task_id: TASK-TO-BE-001
product: [product name]
participant_file: [resolved path]
reference_file: [resolved path]
checked_at: [ISO 8601]
sections_evaluated: [N]
total_score: [N]/100
grade: [label]
identical_to_reference: [true|false]
---

# Task Check Report — to-be
_[Product name] | [timestamp]_

[If identical_to_reference: ⚠ Warning: participant file is byte-for-byte identical to the reference.]

**File resolution log:**
- Participant file: [path] — [how resolved]
- Reference file: [path] — [how resolved]
- Product: [name] — [derivation source]
- Sections in reference: [N] | Sections in participant: [N] (matched: [N], extra: [N])
- Point weights: [auto-calculated or from frontmatter]

---

## Score Summary

**The to-be document Score: [N]**

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| [heading] | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| **Total** | | **100** | **[N]** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Section N — [heading] ([score]/[weight])
_Matched to participant [§N heading]_

**Coverage:** [topics and code/diagram types covered vs. missing]
**Specificity:** [named objects, types, catalog paths, rule IDs used]
**Technical accuracy:** [platform correctness; SQL syntax issues]
**Issues/gaps flagged:** [open decisions, DQ rules, risks called out]
**Structure:** [subsections, tables, code blocks, diagrams present]
**Code / Diagram quality:** [SQL completeness, diagram validity, Python patterns]

**Code/Diagram inventory:**
- SQL blocks: [N in reference → N in participant]
- Python blocks: [N in reference → N in participant]
- Mermaid diagrams: [N in reference → N in participant]

**Deferred fields `[DEFERRED]`:** [list]

**Improvement items:**
- [ ] [Specific actionable item]

[Repeated for all evaluated sections]

---

## Extra Sections (not in reference)
[List with section heading and brief note]

## Approach Notes
[Valid alternative approaches noted]

---

## Priority Improvements
Top 3 items ranked by score impact:
1. [Section — criterion — points recoverable]
2. [Section — criterion — points recoverable]
3. [Section — criterion — points recoverable]

---

## Next Step
[score ≥ 75]: You can proceed to the next task.
[score < 75]: Address the priority improvements above and re-run the checker before moving on.
```
