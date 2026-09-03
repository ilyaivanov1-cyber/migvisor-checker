---
name: 15-migvisor-task-checker-as-is
description: Evaluates a participant's as-is submission against a reference file. Works with any product, any file names, any workspace structure, and any number of sections. Scores all sections found in the reference (0–100 total), provides per-section comments, flags improvement areas, and acknowledges valid alternative approaches.
---

# Skill: task-checker-as-is

## Identity

- **Name:** `task-checker-as-is`
- **Selection signal:** Evaluates and scores a participant-submitted as-is document against a reference — use when a participant has completed the as-is analysis task and wants structured feedback.
- **Trigger phrases:**
  - "check my as-is"
  - "evaluate as-is submission"
  - "score as-is"
  - "review as-is task"
  - "check task as-is"
  - "run 15-migvisor-task-checker"

---

## Invocation Syntax

```
/task-checker-as-is [participant_file] [reference_file] [--product <name>] [trainee=<name>]
```

All arguments are optional. Examples:
- `/task-checker-as-is my-submission.md` — participant file supplied; reference auto-resolved
- `/task-checker-as-is submissions/alice.md reference/as-is.md` — both supplied
- `/task-checker-as-is --product Inventory` — both files auto-resolved; product name overridden
- `/task-checker-as-is trainee=alice` — auto-resolve participant from trainees/alice/
- `/task-checker-as-is` — everything auto-resolved (single trainee folder)

---

## Preconditions

| Condition | Check | If not met |
|---|---|---|
| Participant file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1A) | Ask: "Provide the path to your as-is submission, e.g. `/task-checker-as-is path/to/submission.md`" |
| Reference file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1B) | If zero candidates: "No reference file found. Supply it as the second argument." If multiple: "Multiple reference candidates found: [list]. Which should I use?" |
| Participant file readable | File exists and is non-empty | "Cannot read submission at [path]. Check the path and try again." |
| Participant file has structure | File contains at least one `## ` heading | "Submission does not appear to be a valid as-is document — no H2 sections found. Verify the correct file." |

---

## Input Inventory

| Input | Source | Required |
|---|---|---|
| Participant's as-is file | Path supplied at invocation (positional arg 1) OR auto-resolved | Yes |
| Reference as-is file | Path supplied at invocation (positional arg 2) OR auto-resolved | Yes |
| Product name | Derived from: (1) `--product` flag, (2) `# As-Is Analysis — <Product>` H1 heading in participant file, (3) `product:` field in YAML frontmatter, (4) parent directory name | Derived |
| `product-scope.md` | Searched relative to participant file's directory and its parents (max 3 levels up) | Optional |

---

## Workflow

### Step 1 — Resolve files and product

**1A — Participant file**

If a path was supplied as argument 1, use it. Otherwise apply trainee-aware auto-detection:

1. If `trainee=<name>` flag is provided: look for `trainees/<name>/as-is.md`. If not found, abort: *"No participant file at trainees/<name>/as-is.md. Verify the trainee name and file."*
2. Otherwise: scan `trainees/` for immediate subdirectories.
   - Exactly 1 found: use `trainees/<that-name>/as-is.md`; record `<that-name>` as the trainee name.
   - 0 found: abort with *"No trainees/ subdirectories found. Provide an explicit path or create trainees/<name>/."*
   - 2 or more found: abort with *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: if `trainees/` does not exist, search the workspace root for `as-is.md`.

Record the resolved trainee name from the participant file path for output path construction in Step 8.

**1B — Reference file**

If a path was supplied as argument 2, use it. Otherwise look for `reference/as-is.md`. If found: use it. If not found: abort with *"No reference file found at reference/as-is.md. Supply an explicit reference path."*

**1C — Product name**

Derive in this order:
1. `--product <name>` flag in the invocation
2. `# As-Is Analysis — <Name>` H1 heading in the participant file
3. `product:` field in YAML frontmatter of the participant file
4. Name of the immediate parent directory of the participant file
5. Fallback: `[Unknown Product]`

**1D — Scope file**

Search for `product-scope.md` starting from the participant file's directory, then each parent directory up to 3 levels. Use the first match found; skip silently if not found.

If found, use it in scoring as follows:
- **Consumer section:** cross-check the participant's consumer list against consumers named in the scope file; missing consumers lose coverage points proportionally.
- **Definition section:** check whether the participant's IN/OUT scope statement is consistent with the scope file boundaries.

**1E — Read files**

Read participant file, reference file, and scope file (if found) in parallel.

---

### Step 2 — Check for identical files

Compute whether participant file and reference file are byte-for-byte identical.

- If identical: set `IDENTICAL_TO_REFERENCE = true`. **Do not deduct any points.** Add a warning in the report header and conversation summary.
- If not identical: proceed normally.

---

### Step 3 — Detect sections dynamically

**3A — Build section list from reference**

Scan the reference file for all headings matching `## <N>` where N is a number, immediately followed by a space, dot, or end-of-token. This is the canonical section list for this evaluation.

Example matches: `## 1`, `## 1.`, `## 2 Consumers`, `## 7. New Section Title`

Record for each section: its number, its full heading text, and its content.

**3B — Match sections in participant file**

For each section number found in the reference, look for the corresponding `## <N>` heading in the participant file.

| Outcome | Action |
|---|---|
| Section present in both | Evaluate normally |
| Section in reference but missing from participant | Score 0 for that section; note as absent |
| Section in participant but not in reference | Note as extra content; do not score; do not penalise |

---

### Step 4 — Calculate point weights

**4A — Check for explicit weights**

Look for a `scoring_weights` entry in the reference file's YAML frontmatter, e.g.:
```yaml
scoring_weights:
  1: 20
  2: 15
  3: 25
  4: 20
  5: 10
  6: 10
```

If present and weights sum to 100: use them.

**4B — Auto-calculate weights**

If no explicit weights are defined:
1. Count N = total sections found in the reference.
2. Base weight per section = `floor(100 / N)`.
3. Distribute the remainder (100 mod N) one point at a time to sections in descending order of their content length in the reference (longer sections are typically more complex).
4. Minimum weight per section: 5 pts. Maximum: 35 pts.

Example: 6 sections → floor(100/6) = 16 pts each, remainder 4 distributed to the 4 longest sections → weights like 20, 18, 18, 16, 16, 12.

Display the calculated weights in the report's Score Summary table so the participant can see how points were allocated.

---

### Step 5 — Handle `[USER INPUT REQUIRED]` fields

Before scoring, identify any field or row containing `[USER INPUT REQUIRED]`, `TBD`, `TODO`, or `[FILL IN]`.

- Treat as **intentional deferrals**, not missing content.
- For the affected criterion: if other non-deferred content in the same criterion provides sufficient coverage, award full points. If the deferred field is the only evidence for that criterion, award 50% and note as pending.
- Flag each deferred field in section feedback with the label `[DEFERRED]`.

---

### Step 6 — Score each section

Apply the **Generic Per-Section Rubric** (below) to every section detected in Step 3. Produce for each:

```
section → { weight, score, criteria_results[], deferred_fields[], improvements[], approach_notes[] }
```

---

### Step 7 — Apply approach policy

Before finalising scores:

- Different structure but same information covered → **no deduction**, note in `approach_notes`
- Bottom-up vs. top-down presentation → **no deduction**
- Subsection omitted but content covered elsewhere in the same section → evaluate coverage before deducting
- Owner/contact stated as "TBD", "Unknown", team name, role, or email → **award full points**; only completely blank scores 0

Deduct only for **missing information**, not for **different presentation**.

---

### Step 8 — Assemble the check report

Determine the output file path:
1. Extract the trainee name from the resolved participant file path: `trainees/<name>/...` → `<name>`. If participant was not under `trainees/`, use `unknown_trainee`.
2. Base name: `checks/<trainee_name>/TASK-AS-IS-001_check_report.md`
3. If it does not exist: write it.
4. If it exists: increment suffix (`_v2`, `_v3`, …) until a free path is found.
5. **Never overwrite an existing report file.**

Create the `checks/<trainee_name>/` directory if it does not exist.

---

### Step 9 — Surface summary in conversation

Output the following block to the console:

```
✓ Check complete — [PRODUCT_NAME] as-is

Score: [N] / 100   ([grade label])

  [Section 1 heading]   [N]/[weight]   [✓/⚠/✗]
  [Section 2 heading]   [N]/[weight]   [✓/⚠/✗]
  ...
  [Section N heading]   [N]/[weight]   [✓/⚠/✗]

[N] improvement items flagged. Full report: checks/[report_filename]
[If IDENTICAL_TO_REFERENCE]: ⚠ Warning: submission is byte-for-byte identical to the reference file.
```

Then immediately output a **plain-English summary** of 5–6 sentences. Rules:
- Sentence 1: overall result — score, grade, and one-line verdict ("strong submission", "needs revision", etc.)
- Sentence 2: what the submission does well — name the strongest 1–2 sections and why.
- Sentence 3–4: what needs improvement — state each gap in plain language, name the section, and say how many points are recoverable.
- Sentence 5: the single highest-priority action the participant should take next.
- Sentence 6 (optional): next step — if score ≥ 75, say "You can proceed to the next task." If score < 75, say "Address the items above and re-run the checker before moving on." Do not mention transformation rules or specific command names — the trainee is not yet familiar with that step.
- No bullet points, no markdown headers — flowing prose only.
- Do not repeat the score table; the summary is a human-readable complement to it.

---

## Generic Per-Section Rubric

Applied to every section regardless of its heading or domain. Points below are expressed as **percentages of that section's weight** — they scale automatically with whatever weight was assigned in Step 4.

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Coverage** | 40% | Key topics, entities, and subsections present in the reference section are addressed in the participant section. Score proportionally — e.g., 8 of 10 reference topics covered = 80% of coverage points. |
| **Specificity** | 25% | Information uses named objects, values, identifiers, and system names rather than vague descriptions. "SQL Server 2014, `wideworldimportersdw`" scores higher than "a SQL database". |
| **Technical accuracy** | 20% | No direction error (source system vs. target); correct layer described; facts consistent with reference. Full deduct if the section describes the wrong system. |
| **Issues and gaps flagged** | 10% | Known limitations, data quality issues, undocumented rules, or broken dependencies are called out explicitly. Absence of any such note scores 0. |
| **Structure** | 5% | Required subsections or format elements (tables, diagrams, lists) are present and consistent with the reference layout. |

**Criterion points are rounded to the nearest integer.**

---

### Auto-deducts (apply after rubric scoring)

| Condition | Deduction |
|---|---|
| Section describes the **target/future** system instead of the **current/source** system | −50% of section score |
| Model-type section: fewer than 3 entities documented when reference has > 10 | −5 pts |
| Lineage-type section: consumer listed as a source (direction reversed) | −4 pts |
| Calculations-type section: section present but empty with no "no calculations" statement | −3 pts |

A section is identified as "model-type", "lineage-type", or "calculations-type" by its heading text — look for keywords like "model", "lineage", "calculation", "sources", "consumers", "definition" in the heading. When ambiguous, apply only the direction-error auto-deduct.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | **Excellent** | Thorough and accurate. Proceed to transformation rules. |
| 75–89 | **Good** | Minor gaps. Address flagged items; proceeding is acceptable if items are low-risk. |
| 60–74 | **Acceptable** | Several gaps. Revise before running transformation rules. |
| 45–59 | **Needs work** | Significant sections incomplete or inaccurate. Substantial revision required. |
| 0–44 | **Incomplete** | Major sections missing or direction error. Restart affected sections. |

---

## Check Report Template

Written to `checks/<trainee_name>/TASK-AS-IS-001_check_report.md` (or `_v2`, `_v3` … if prior reports exist):

```markdown
---
task_id: TASK-AS-IS-001
product: [product name]
participant_file: [resolved path]
reference_file: [resolved path]
checked_at: [ISO 8601]
sections_evaluated: [N]
total_score: [N]/100
grade: [label]
identical_to_reference: [true|false]
---

# Task Check Report — as-is
_[Product name] | [timestamp]_

[If identical_to_reference: ⚠ Warning: participant file is byte-for-byte identical to the reference.
Score reflects content quality; no deduction applied for identity.]

**File resolution log:**
- Participant file: [path] — [how resolved]
- Reference file: [path] — [how resolved]
- Product: [name] — [derivation source]
- Scope file: [path or "not found"]
- Sections in reference: [N] | Sections in participant: [N]
- Point weights: [auto-calculated or from frontmatter] — [s1:N, s2:N, ...]

---

## Score Summary

**The as-is document Score: [N]**

| Section | Weight | Score | Status |
|---|---|---|---|
| [heading text] | [N] | [N] | ✓ / ⚠ / ✗ |
| ... | | | |
| **Total** | **100** | **[N]** | |

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### [Section N heading] ([score]/[weight])

**Coverage:** [what topics from the reference were addressed; what was missing]
**Specificity:** [were named objects, values, identifiers used]
**Technical accuracy:** [any direction errors or inconsistencies]
**Issues/gaps flagged:** [what was called out; what was absent]
**Structure:** [subsections and format assessment]

**Deferred fields `[DEFERRED]`:** [list placeholder entries and their criterion impact]

**Improvement items:**
- [ ] [Specific actionable item]

[Repeated for all evaluated sections]

---

## Extra Sections (not in reference)
[List any sections found in participant file that have no counterpart in the reference]

## Approach Notes
[Explicitly state if participant used a different but valid approach]

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
