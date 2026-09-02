---
name: 19-migvisor-task-checker-project-rules
description: Validates a participant's project-level transformation rules document against the authoritative final version. Works with any project, any number of dimensions/sections. Compares rule IDs, intents, platform targets, counts, and application order. Scores per dimension, flags missing or inaccurate rules, and produces a scored summary with 5–6 sentence prose.
---

# Skill: task-checker-project-rules

## Identity

- **Name:** `task-checker-project-rules`
- **Selection signal:** Validates a participant's project-level transformation rules document against the final version — use when a participant has drafted project transformation rules and wants to know if they are complete and accurate.
- **Trigger phrases:**
  - "check my project rules"
  - "validate project rules"
  - "compare project transformation rules"
  - "score project rules"
  - "check task project rules"
  - "run 19-migvisor-task-checker-project-rules"

---

## Invocation Syntax

```
/task-checker-project-rules [participant_file] [reference_file] [--project <name>]
```

All arguments are optional. Examples:
- `/task-checker-project-rules my-rules.md` — participant file supplied; reference auto-resolved
- `/task-checker-project-rules draft.md "project-transformation-rules final.md"` — both supplied
- `/task-checker-project-rules --project GlobalSales_Project` — both files auto-resolved; project name overridden
- `/task-checker-project-rules` — everything auto-resolved from workspace

---

## Preconditions

| Condition | Check | If not met |
|---|---|---|
| Participant file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1A) | Ask: "Provide the path to your project rules submission, e.g. `/task-checker-project-rules my-rules.md`" |
| Reference file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1B) | If zero: "No reference file found. Supply it as the second argument." If multiple: "Multiple reference candidates found: [list]. Which should I use?" |
| Participant file readable | File exists and is non-empty | "Cannot read submission at [path]. Check the path and try again." |
| Participant file has structure | File contains at least one `## ` or `### ` heading | "Submission does not appear to be a valid project rules document — no sections found. Verify the correct file." |

---

## Input Inventory

| Input | Source | Required |
|---|---|---|
| Participant's project rules file | Path supplied at invocation (positional arg 1) OR auto-resolved | Yes |
| Reference (final) project rules file | Path supplied at invocation (positional arg 2) OR auto-resolved | Yes |
| Project name | Derived from: (1) `--project` flag, (2) `# Project Transformation Rules: <Name>` H1 heading in participant file, (3) `project:` YAML frontmatter, (4) parent directory name | Derived |

---

## Workflow

### Step 1 — Resolve files and project name

**1A — Participant file**

If a path was supplied as argument 1, use it. Otherwise search the workspace for files matching (in priority order):
1. `project-transformation-rules.md`
2. `project-transformation-rules-draft.md`
3. Any `*project*transformation*rules*.md` NOT containing "final" in the name

If multiple candidates exist at the same priority level: ask the user which to use. Always exclude files containing "final" from participant candidates.

**1B — Reference file**

If a path was supplied as argument 2, use it. Otherwise search the workspace for files matching (in priority order):
1. `project-transformation-rules final.md`
2. `project-transformation-rules-final.md`
3. Any `*project*transformation*rules*final*.md`

If exactly one candidate found at the highest-priority level: use it. If multiple: ask the user which to use. Exclude the participant file.

**1C — Project name**

Derive in this order:
1. `--project <name>` flag in the invocation
2. `# Project Transformation Rules: <Name>` H1 heading in the participant file
3. `project:` field in YAML frontmatter of the participant file
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

1. **Dimension sections** — all `### ` H3 headings found under any `## Rule Index`, `## Rules`, or `## Rule Set` H2 heading. Each `### ` heading = one scoreable dimension section. If no such H2 wrapper exists, treat all `### ` headings as dimension sections.

2. **Metadata section** — the first H2 heading whose text contains "Active Dimensions", "Dimensions", or "Dimension Table". Treat as one additional scored section using its actual heading text.

3. **Fallback** — if neither `### ` nor a metadata `## ` heading produces a usable structure, treat every `## ` heading as one scored section.

For each dimension section record: heading text, dimension prefix (from parenthesised abbreviation in heading or inferred from first rule ID), all rule IDs, all intent strings, rule count.

**3B — Inventory rules per reference section**

For each reference dimension section record:
- Total rule count
- Rule IDs in order (e.g., PL-001 through PL-004)
- Intent text per rule
- Application order (if stated in the reference metadata section)

**3C — Match sections in participant file**

For each reference section, find the best match in the participant file:

1. **Prefix match** — same dimension prefix abbreviation in the heading (e.g., `(PL)`, `PL —`, `### Platform (PL)`). Use if abbreviation appears in both headings.
2. **Heading text match** — keyword overlap on dimension name ("Platform", "Naming", "Types", "Objects", "Syntax", "Interface", etc.). Use best text match regardless of order.
3. **No match** — score 0 for that reference section.

Within each matched section pair, match individual rules by:
1. **Exact ID** — same `PREFIX-NNN` identifier (primary match — both files are at the same document level so IDs should align)
2. **Intent similarity** — if IDs differ but intent descriptions are substantively equivalent, count as a match with a note

| Outcome | Action |
|---|---|
| Match found (by prefix or text) | Evaluate normally — rubric + rule checks |
| Reference section with no match in participant | Score 0; note as absent |
| Participant section not matched to any reference section | Note as extra; flag as unexpected at project level; do not score; do not penalise |

---

### Step 4 — Calculate point weights

**4A — Check for explicit weights**

Look for a `scoring_weights` entry in the reference file's YAML frontmatter. If present and weights sum to 100: use them.

**4B — Auto-calculate weights**

If no explicit weights:
1. Count N = total scored sections (all dimension sections + the metadata section, if present).
2. Base weight = `floor(100 / N)`.
3. Distribute the remainder (100 mod N) one point at a time to the sections with the highest rule count in the reference (more rules = more complex = higher weight).
4. Minimum weight per section: 5 pts. Maximum: 35 pts.

Display calculated weights in the Score Summary table.

---

### Step 5 — Handle deferred and placeholder fields

Before scoring, identify any rule row containing `[TBD]`, `[PENDING]`, `[TODO]`, `[FILL IN]`, or `[USER INPUT REQUIRED]`.

- Treat as **intentional deferrals**, not missing content.
- If the rule ID is present but intent is deferred: award 50% of that rule's contribution to Intent Accuracy and flag as `[DEFERRED]`.
- If the rule row is entirely absent: apply normal missing-rule scoring.

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
- Rules appear in a different order within a dimension → **no deduction**
- Rule IDs differ by a small offset (e.g., PL-002 vs PL-003) but intents match → **no deduction**, note the ID discrepancy
- Participant adds extra context or product-specific examples to a rule intent → **no deduction**
- Extra dimension sections not in reference → **note as unexpected**, no point deduction, but flag for review

Deduct only for **missing rules, incorrect intents, or wrong platform targets** — not for different ordering, wording style, or additional detail.

---

### Step 8 — Assemble the check report

Determine the output file path:
1. Base name: `TASK-TR-002_check_report.md`
2. If it does not exist: write it.
3. If it exists: increment suffix (`_v2`, `_v3`, …) until a free path is found.
4. **Never overwrite an existing report file.**

Create the `checks/` directory if it does not exist.

---

### Step 9 — Surface summary in conversation

Output the following block to the console:

```
✓ Check complete — [PROJECT_NAME] project transformation rules

Score: [N] / 100   ([grade label])

  [Active Dimensions]     [N]/[weight]   [✓/⚠/✗]
  [Platform (PL)]         [N]/[weight]   [✓/⚠/✗]
  [Naming (NM)]           [N]/[weight]   [✓/⚠/✗]
  ...
  [Section N]             [N]/[weight]   [✓/⚠/✗]

Extra sections (not scored):
  - [Section heading]
  (or "None")

[N] improvement items flagged. Full report: checks/[report_filename]
[If IDENTICAL_TO_REFERENCE]: ⚠ Warning: submission is byte-for-byte identical to the reference file.
```

Then immediately output a **plain-English summary** of 5–6 sentences. Rules:
- Sentence 1: overall result — score, grade, and one-line verdict.
- Sentence 2: what the submission does well — name the strongest 1–2 dimension sections and specifically why they score well (correct IDs, accurate intents, complete counts).
- Sentence 3 (optional): if the participant includes rule IDs or entire dimensions not in the reference, name them and note whether they appear intentional or may indicate confusion. If none, skip.
- Sentence 4: what needs improvement — name the specific dimension, the missing or inaccurate rule IDs, and the points recoverable. If no gaps, say so.
- Sentence 5: next step — if score ≥ 75, say "You can proceed to the next task." If score < 75, say "Address the items above and re-run the checker before moving on."
- No bullet points, no markdown headers — flowing prose only.

---

## Per-Section Rubric

### Dimension sections (Platform, Naming, Types, Objects, Syntax, Interface, etc.)

Points expressed as **percentages of that section's weight**.

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Rule coverage** | 40% | All rule IDs present in the reference dimension appear in the participant dimension. Match by exact ID first; if IDs differ, match by intent. Score proportionally — e.g., 4 of 5 rules present = 80% of coverage points. |
| **Intent accuracy** | 30% | Each matched rule's intent captures the same constraint as the reference. Paraphrasing acceptable; vague, incomplete, or platform-wrong intents are not. Score proportionally per rule. |
| **Technical accuracy** | 20% | Rules reference the correct source and target platforms (SQL Server → Databricks Delta Lake). No wrong technology names (e.g., Snowflake, Synapse, dbt). Correct schema layer names used. |
| **Structure** | 10% | Rule table present with ID and Intent columns. IDs follow `PREFIX-NNN` convention. Rule count in heading matches actual rule count in section. Application order stated where reference states it. |

### Active Dimensions metadata section

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Dimension coverage** | 35% | All dimensions listed in the reference table appear in the participant table. Score proportionally. |
| **Rule count accuracy** | 35% | Rule count per dimension matches reference exactly. Variance > ±1 with no explanation = deduct proportionally per dimension off by > 1. |
| **File references** | 20% | YAML file links per dimension present and correctly named. |
| **Application order + structure** | 10% | Application order (`PL → NM → TY → OB → SX → IF`) stated; total rule count stated; table format consistent. |

**Criterion points are rounded to the nearest integer.**

---

## Auto-deducts (applied after rubric scoring)

| Condition | Deduction |
|---|---|
| Entire dimension present in reference but completely absent in participant | −5 pts (global, once per missing dimension) |
| Rules in a dimension consistently target the wrong platform (not isolated instances) | −30% of that dimension's score |
| Rule IDs use wrong prefix throughout a dimension (systematic error) | −20% of that dimension's score |
| Active Dimensions metadata table entirely absent | −5 pts (global) |
| Total rule count stated in metadata is off by more than 3 from reference total | −3 pts (global, once) |
| Unexpected extra dimension section present with no explanation | −2 pts (global, once, only if > 1 extra section) |

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | **Excellent** | Thorough and accurate. You can proceed to the next task. |
| 75–89 | **Good** | Minor gaps. Address flagged items; proceeding is acceptable if items are low-risk. |
| 60–74 | **Acceptable** | Several gaps. Revise before proceeding. |
| 45–59 | **Needs work** | Significant rules missing or wrong platform targets. Substantial revision required. |
| 0–44 | **Incomplete** | Major dimensions missing or wrong platform throughout. Restart affected sections. |

---

## Check Report Template

Written to `checks/TASK-TR-002_check_report.md` (or `_v2`, `_v3` … if prior reports exist):

```markdown
---
task_id: TASK-TR-002
project: [project name]
participant_file: [resolved path]
reference_file: [resolved path]
checked_at: [ISO 8601]
sections_evaluated: [N]
total_score: [N]/100
grade: [label]
identical_to_reference: [true|false]
---

# Task Check Report — project transformation rules
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
**Technical accuracy:** [correct/incorrect platform references; flag wrong technology names]
**Structure:** [rule count match, ID convention, application order presence]

**Rule inventory:**
- Reference rules: [N] | Participant rules: [N]
- Present and matching: [IDs]
- Missing from participant: [IDs]
- In participant but not in reference: [IDs] (unexpected at project level)

**Deferred fields `[DEFERRED]`:** [list]

**Improvement items:**
- [ ] [Specific actionable item]

[Repeated for all evaluated sections]

---

## Extra Sections (not in reference)
[List with section heading; note whether unexpected or plausible extension]

## Approach Notes
[Valid alternative approaches noted — ID offsets, wording differences, rule splits]

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
