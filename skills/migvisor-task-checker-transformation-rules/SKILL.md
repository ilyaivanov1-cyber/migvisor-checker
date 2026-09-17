---
name: 18-migvisor-task-checker-transformation-rules
description: Evaluates a participant's transformation rules document against a reference (final) version. Works with any project or product, any number of dimensions/sections. Scores rule coverage, intent accuracy, platform correctness, and structure. Provides per-dimension comments, flags missing or incorrect rules, and surfaces a scored summary.
---

# Skill: task-checker-transformation-rules

## Identity

- **Name:** `task-checker-transformation-rules`
- **Selection signal:** Evaluates and scores a participant-submitted transformation rules document against a reference — use when a participant has drafted transformation rules and wants structured feedback.
- **Trigger phrases:**
  - "check my transformation rules"
  - "evaluate transformation rules"
  - "score transformation rules"
  - "review transformation rules"
  - "check task transformation rules"
  - "run 18-migvisor-task-checker-transformation-rules"

---

## Invocation Syntax

```
/task-checker-transformation-rules [participant_file] [reference_file] [--product <name>] [trainee=<name>]
```

All arguments are optional. Examples:
- `/task-checker-transformation-rules my-rules.md` — participant file supplied; reference auto-resolved
- `/task-checker-transformation-rules draft-rules.md reference/product-transformation-rules.md` — both supplied
- `/task-checker-transformation-rules --product Sales_Orders` — both files auto-resolved; product name overridden
- `/task-checker-transformation-rules trainee=alice` — auto-resolve participant from trainees/alice/
- `/task-checker-transformation-rules` — everything auto-resolved (single trainee folder)

---

## Preconditions

| Condition | Check | If not met |
|---|---|---|
| Participant file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1A) | Ask: "Provide the path to your transformation rules submission, e.g. `/task-checker-transformation-rules my-rules.md`" |
| Reference file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1B) | If zero: "No reference file found. Supply it as the second argument." If multiple: "Multiple reference candidates found: [list]. Which should I use?" |
| Participant file readable | File exists and is non-empty | "Cannot read submission at [path]. Check the path and try again." |
| Participant file has structure | File contains at least one `## ` or `### ` heading | "Submission does not appear to be a valid transformation rules document — no sections found. Verify the correct file." |

---

## Input Inventory

| Input | Source | Required |
|---|---|---|
| Participant's transformation rules file | Path supplied at invocation (positional arg 1) OR auto-resolved | Yes |
| Reference transformation rules file | Path supplied at invocation (positional arg 2) OR auto-resolved | Yes |
| Product/Project name | Derived from: (1) `--product` flag, (2) `# Project Transformation Rules: <Name>` or `# Product Transformation Rules: <Name>` H1 heading, (3) `product:` or `project:` YAML frontmatter, (4) parent directory name | Derived |

---

## Workflow

### Step 1 — Resolve files and product

**1A — Participant file**

If a path was supplied as argument 1, use it. Otherwise apply trainee-aware auto-detection:

1. If `trainee=<name>` flag is provided: look for `trainees/<name>/product-transformation-rules.md`, then `trainees/<name>/project-transformation-rules.md`. Use first found; if neither exists, abort: *"No participant transformation rules file found in trainees/<name>/."*
2. Otherwise: scan `trainees/` for immediate subdirectories.
   - Exactly 1 found: search `trainees/<that-name>/` for `product-transformation-rules.md` then `project-transformation-rules.md`; use first found; record `<that-name>` as the trainee name.
   - 0 found: abort with *"No trainees/ subdirectories found. Provide an explicit path."*
   - 2 or more found: abort with *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: if `trainees/` does not exist, search workspace root for `project-transformation-rules.md` then `product-transformation-rules.md`.

Record the resolved trainee name from the participant file path for output path construction in Step 8.

**1B — Reference file**

If a path was supplied as argument 2, use it. Otherwise look for `reference/product-transformation-rules.md`, then `reference/project-transformation-rules.md`. Use first found. If neither exists: abort with *"No reference file found at reference/product-transformation-rules.md. Supply an explicit reference path."*

**1C — Product/Project name**

Derive in this order:
1. `--product <name>` flag in the invocation
2. `# Project Transformation Rules: <Name>` or `# Product Transformation Rules: <Name>` H1 heading in the participant file
3. `product:` or `project:` field in YAML frontmatter of the participant file
4. Name of the immediate parent directory of the participant file
5. Fallback: `[Unknown Project]`

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

Detect scoreable sections using this priority order:

1. **Dimension sections** — all `### ` H3 headings found anywhere under a `## Rule Index`, `## Rules`, or `## Rule Set` H2 heading. Each `### ` heading = one scoreable dimension section. If no such H2 wrapper exists, treat all `### ` headings as dimension sections.

2. **Metadata section** — the first H2 heading whose text contains "Active Dimensions", "Dimensions", or "Dimension Table". Treat as one additional scored section named "Active Dimensions" (or its actual heading text).

3. **Fallback** — if neither `### ` nor a metadata `## ` heading produces a usable structure, treat every `## ` heading as one scored section (same fallback as other checkers).

For each dimension section record: heading text, dimension prefix (extracted from heading abbreviation in parentheses, e.g. `(PL)`, or inferred from the first rule ID in the section's table), all rule rows (ID + Intent), rule count.

**3B — Inventory rules per reference section**

For each reference dimension section, record:
- Total rule count
- Rule IDs (e.g., `PL-001`, `NM-002`)
- Intent text per rule

**3C — Match sections in participant file**

For each reference section, find the best match in the participant file using this priority order:

1. **Prefix match** — same dimension prefix abbreviation in the heading (e.g., `(PL)`, `PL —`, `### Platform (PL)`). Use if the abbreviation appears in both headings.
2. **Heading text match** — keyword overlap on dimension name ("Platform", "Naming", "Types", "Objects", "Syntax", "Interface", "Performance", "Lineage", "Quality", "Custom", etc.). Use best text match regardless of order.
3. **No match** — score 0 for that reference section.

| Outcome | Action |
|---|---|
| Match found (by prefix or text) | Evaluate normally — rubric + rule checks |
| Reference section with no match in participant | Score 0; note as absent |
| Participant section not matched to any reference section | Note as extra content; do not score; do not penalise |

---

### Step 4 — Calculate point weights

**4A — Check for explicit weights**

Look for a `scoring_weights` entry in the reference file's YAML frontmatter. If present and weights sum to 100: use them.

**4B — Auto-calculate weights**

If no explicit weights:
1. Count N = total scored sections (all dimension sections + the metadata section, if present).
2. Base weight = `floor(100 / N)`.
3. Distribute the remainder (100 mod N) one point at a time to sections in descending order of rule count (more rules = more complex = higher weight).
4. Minimum weight per section: 5 pts. Maximum: 35 pts.

Display calculated weights in the Score Summary table.

---

### Step 5 — Handle deferred and placeholder fields

Before scoring, identify any rule row containing `[TBD]`, `[PENDING]`, `[TODO]`, `[FILL IN]`, or `[USER INPUT REQUIRED]`.

- Treat as **intentional deferrals**, not missing content.
- If the rule ID is present but intent is deferred: award 50% of that rule's contribution to the Intent Accuracy criterion and flag as `[DEFERRED]`.
- If the rule row is entirely absent: apply normal missing-rule scoring (no special treatment).

---

### Step 6 — Score each section

Apply the **Per-Section Rubric** (below) to every matched section. Produce for each:

```
section → { weight, score, rubric_results[], deferred_fields[], improvements[] }
```

---

### Step 7 — Apply approach policy

Before finalising scores:

- Rule intent uses different wording but conveys the same constraint → **no deduction**
- Rules appear in different order within a dimension → **no deduction**
- Participant combines two reference rules into one equivalent rule → **no deduction** if combined coverage is maintained
- Participant splits one reference rule into two more specific rules → **no deduction** if all reference constraints are captured
- Extra rules beyond what the reference has → **no deduction**, note as supplementary
- Dimension prefix numbering differs (e.g., participant PL-001 corresponds to reference PL-003) → evaluate by intent coverage, not ID sequence

Deduct only for **missing or incorrect rules and intents**, not for **different numbering, ordering, or wording style**.

---

### Step 8 — Assemble the check report

Determine the output file path:
1. Extract the trainee name from the resolved participant file path: `trainees/<name>/...` → `<name>`. If participant was not under `trainees/`, use `unknown_trainee`.
2. Base name: `checks/<trainee_name>/transformation-rules/TASK-TR-001_check_report.md`
3. If it does not exist: write it.
4. If it exists: increment suffix (`_v2`, `_v3`, …) until a free path is found.
5. **Never overwrite an existing report file.**

Create the `checks/<trainee_name>/transformation-rules/` directory if it does not exist.

---

### Step 9 — Surface summary in conversation

Output the following block to the console:

```
✓ Check complete — [PROJECT_NAME] transformation rules

Score: [N] / 100   ([grade label])

  [Active Dimensions]     [N]/[weight]   [✓/⚠/✗]
  [Platform (PL)]         [N]/[weight]   [✓/⚠/✗]
  [Naming (NM)]           [N]/[weight]   [✓/⚠/✗]
  ...
  [Section N]             [N]/[weight]   [✓/⚠/✗]

Extra sections (not scored):
  - [Section heading]
  (or "None" if no extra sections)

[N] improvement items flagged. Full report: checks/[report_filename]
[If IDENTICAL_TO_REFERENCE]: ⚠ Warning: submission is byte-for-byte identical to the reference file.
```

Then immediately output a **plain-English summary** of 5–6 sentences. Rules:
- Sentence 1: overall result — score, grade, and one-line verdict.
- Sentence 2: what the submission does well — name the strongest 1–2 dimension sections and why.
- Sentence 3 (optional): if the participant includes rules or entire dimensions beyond what the reference has, name them by dimension and note they add coverage beyond what was required. If none, skip.
- Sentence 4: what needs improvement — missing rules, wrong platform targets, incorrect intents — name the specific dimension and state how many points are recoverable. If no gaps, say so in one sentence.
- Sentence 5: next step — if score ≥ 75, say "You can proceed to the next task." If score < 75, say "Address the items above and re-run the checker before moving on."
- No bullet points, no markdown headers — flowing prose only.

---

## Per-Section Rubric

### Dimension sections (Platform, Naming, Types, Objects, Syntax, Interface, etc.)

Points expressed as **percentages of that section's weight**.

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Rule coverage** | 40% | All rules present in the reference dimension are represented in the participant dimension. Match by ID first; if IDs differ, match by intent similarity. Score proportionally — e.g., 4 of 5 reference rules present = 80% of coverage points. |
| **Intent accuracy** | 25% | Each matched rule's intent description captures the same constraint as the reference. Paraphrasing is acceptable; vague, opposite, or platform-wrong intents are not. Score proportionally per rule. |
| **Technical accuracy** | 20% | Rules reference the correct source and target platforms (e.g., SQL Server → Databricks Delta Lake, not Snowflake or Azure Synapse). Correct schema layer names, correct SQL syntax target names used throughout. |
| **Metadata correctness** | 10% | Rule count for the dimension matches reference (within ±1 acceptable if explained). Dimension prefix consistent with rule IDs. |
| **Structure** | 5% | Rule table present with ID and Intent columns. IDs follow `PREFIX-NNN` convention. |

### Active Dimensions metadata section

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Dimension coverage** | 40% | All dimensions listed in the reference table appear in the participant table. Score proportionally. |
| **Count accuracy** | 30% | Rule counts per dimension match reference. Variance > ±1 with no explanation = deduct proportionally. |
| **File references** | 20% | YAML file links per dimension present and correctly named (e.g., `PL-platform.yaml`). |
| **Structure** | 10% | Table with Dimension / Prefix / File / Rule Count columns present and consistently formatted. |

**Criterion points are rounded to the nearest integer.**

---

## Auto-deducts (applied after rubric scoring)

| Condition | Deduction |
|---|---|
| Entire dimension present in reference but completely absent in participant | −5 pts (global, once per missing dimension) |
| Rules throughout a dimension consistently target wrong platform (not isolated instances) | −30% of that dimension's score |
| Rule IDs use systematically wrong prefix (e.g., all PL rules listed under NM heading) | −20% of that dimension's score |
| Active Dimensions metadata table entirely absent | −5 pts (global) |
| Rule count in Active Dimensions table is off by more than 2 for any one dimension | −2 pts (global, once per document) |

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | **Excellent** | Thorough and accurate. You can proceed to the next task. |
| 75–89 | **Good** | Minor gaps. Address flagged items; proceeding is acceptable if items are low-risk. |
| 60–74 | **Acceptable** | Several gaps. Revise before proceeding. |
| 45–59 | **Needs work** | Significant rules missing or incorrect platform targets. Substantial revision required. |
| 0–44 | **Incomplete** | Major dimensions missing or wrong platform throughout. Restart affected sections. |

---

## Check Report Template

Written to `checks/<trainee_name>/transformation-rules/TASK-TR-001_check_report.md` (or `_v2`, `_v3` … if prior reports exist):

```markdown
---
task_id: TASK-TR-001
project: [project/product name]
participant_file: [resolved path]
reference_file: [resolved path]
checked_at: [ISO 8601]
sections_evaluated: [N]
total_score: [N]/100
grade: [label]
identical_to_reference: [true|false]
---

# Task Check Report — transformation rules
_[Project name] | [timestamp]_

[If identical_to_reference: ⚠ Warning: participant file is byte-for-byte identical to the reference.]

**File resolution log:**
- Participant file: [path] — [how resolved]
- Reference file: [path] — [how resolved]
- Project: [name] — [derivation source]
- Sections in reference: [N] | Sections in participant: [N] (matched: [N], extra: [N])
- Point weights: [auto-calculated or from frontmatter]

---

## Score Summary

**The transformation rules Score: [N]**

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| [heading] | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| **Total** | | **100** | **[N]** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### [Section heading] ([score]/[weight])
_Matched to participant [heading]_

**Rule coverage:** [rules present vs. missing; list missing IDs explicitly]
**Intent accuracy:** [which rules have accurate vs. inaccurate intents; name specific IDs]
**Technical accuracy:** [correct/incorrect platform references; flag any wrong technology names]
**Metadata correctness:** [rule counts, file references, application order]
**Structure:** [table format, ID convention assessment]

**Rule inventory:**
- Reference rules: [N] | Participant rules: [N] | Missing IDs: [list]

**Deferred fields `[DEFERRED]`:** [list]

**Improvement items:**
- [ ] [Specific actionable item]

[Repeated for all evaluated sections]

---

## Extra Sections (not in reference)
[List with section heading and brief note, or "None"]

## Approach Notes
[Valid alternative approaches noted — different wording, rule splits/merges, extra rules]

---

## Priority Improvements
Top 3 items ranked by score impact:
1. [Dimension — criterion — points recoverable]
2. [Dimension — criterion — points recoverable]
3. [Dimension — criterion — points recoverable]

---

## Next Step
[score ≥ 75]: You can proceed to the next task.
[score < 75]: Address the priority improvements above and re-run the checker before moving on.
```
