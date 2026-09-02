---
name: 16-migvisor-task-checker-scope
description: Evaluates a participant's product-scope file against a reference scope file. Works with any product, any file names, any workspace structure, and any number of sections. Scores all sections found in the reference (0–100 total), provides per-section comments, flags improvement areas, and acknowledges valid alternative approaches.
---

# Skill: task-checker-scope

## Identity

- **Name:** `task-checker-scope`
- **Selection signal:** Evaluates and scores a participant-submitted product-scope document against a reference — use when a participant has completed the product scope task and wants structured feedback.
- **Trigger phrases:**
  - "check my scope"
  - "evaluate scope submission"
  - "score scope"
  - "review scope task"
  - "check task scope"
  - "run 16-migvisor-task-checker-scope"

---

## Invocation Syntax

```
/task-checker-scope [participant_file] [reference_file] [--product <name>]
```

All arguments are optional. Examples:
- `/task-checker-scope my-scope.md` — participant file supplied; reference auto-resolved
- `/task-checker-scope submissions/alice-scope.md reference/0 product-scope.md` — both supplied
- `/task-checker-scope --product Purchase` — both files auto-resolved; product name overridden
- `/task-checker-scope` — everything auto-resolved from workspace

---

## Preconditions

| Condition | Check | If not met |
|---|---|---|
| Participant file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1A) | Ask: "Provide the path to your product-scope submission, e.g. `/task-checker-scope path/to/my-scope.md`" |
| Reference file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1B) | If zero candidates: "No reference file found. Supply it as the second argument." If multiple: "Multiple reference candidates found: [list]. Which should I use?" |
| Participant file readable | File exists and is non-empty | "Cannot read submission at [path]. Check the path and try again." |
| Participant file has structure | File contains at least one `## ` heading | "Submission does not appear to be a valid product-scope document — no H2 sections found. Verify the correct file." |

---

## Input Inventory

| Input | Source | Required |
|---|---|---|
| Participant's product-scope file | Path supplied at invocation (positional arg 1) OR auto-resolved | Yes |
| Reference product-scope file | Path supplied at invocation (positional arg 2) OR auto-resolved | Yes |
| Product name | Derived from: (1) `--product` flag, (2) `# Product Scope — <Name>` or `# <Name> — Product Scope` H1 heading, (3) `product:` field in YAML frontmatter, (4) parent directory name | Derived |

---

## Workflow

### Step 1 — Resolve files and product

**1A — Participant file**

If a path was supplied as argument 1, use it. Otherwise prompt: *"Provide the path to your product-scope file, e.g. `/task-checker-scope my-scope.md`"*. Do not guess from filename patterns — require an explicit path when not supplied.

**1B — Reference file**

If a path was supplied as argument 2, use it. Otherwise search the workspace for files matching (in priority order):
1. `0 product-scope.md` (space in name is intentional — matches the template convention)
2. `0-product-scope.md`
3. `product-scope-reference.md`
4. `scope-reference.md`

If exactly one candidate is found at the highest-priority level: use it. If multiple candidates exist: ask the user which to use. Exclude the participant file from reference candidates.

**1C — Product name**

Derive in this order:
1. `--product <name>` flag in the invocation
2. `# Product Scope — <Name>` or `# <Name> — Product Scope` H1 heading in the participant file
3. `product:` field in YAML frontmatter of the participant file
4. Name of the immediate parent directory of the participant file
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

Example matches: `## 1`, `## 1.`, `## 2 Description`, `## 7. Boundaries`

Record for each section: its number, its full heading text, and its content.

**3B — Match sections in participant file**

For each reference section, find the best match in the participant file using this priority order:

1. **Exact number match** — same `## N` number AND heading keywords overlap (e.g., reference `## 3 Objects in Scope` matches participant `## 3 Objects in Scope`). Use this if headings are similar.
2. **Heading text match** — if the number matches but headings differ significantly, search all participant sections for the one whose heading text most closely matches the reference heading (keyword overlap: "scope", "risk", "consumer", "boundary", "calculation", etc.). Use the best text match regardless of its number.
3. **No match** — if no participant section has meaningfully overlapping heading keywords, score 0 for that reference section.

Any participant section not claimed by a reference section match is treated as extra content.

| Outcome | Action |
|---|---|
| Match found (by number or text) | Evaluate normally |
| Reference section with no match in participant | Score 0; note as absent |
| Participant section not matched to any reference section | Note as extra content; do not score; do not penalise |

---

### Step 4 — Calculate point weights

**4A — Check for explicit weights**

Look for a `scoring_weights` entry in the reference file's YAML frontmatter, e.g.:
```yaml
scoring_weights:
  1: 15
  2: 10
  3: 20
  ...
```

If present and weights sum to 100: use them.

**4B — Auto-calculate weights**

If no explicit weights are defined:
1. Count N = total sections found in the reference.
2. Base weight per section = `floor(100 / N)`.
3. Distribute the remainder (100 mod N) one point at a time to sections in descending order of their content length in the reference (longer sections are typically more complex).
4. Minimum weight per section: 5 pts. Maximum: 35 pts.

Display the calculated weights in the report's Score Summary table.

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
- More subsections than reference but all reference content covered → **no deduction**
- Owner/contact stated as "TBD", "Unknown", team name, role, or email → **award full points**; only completely blank scores 0
- Extra sections in participant file not present in reference → noted but not penalised

Deduct only for **missing information**, not for **different presentation**.

---

### Step 8 — Assemble the check report

Determine the output file path:
1. Base name: `TASK-SCOPE-001_check_report.md`
2. If it does not exist: write it.
3. If it exists: increment suffix (`_v2`, `_v3`, …) until a free path is found.
4. **Never overwrite an existing report file.**

Create the `checks/` directory if it does not exist.

---

### Step 9 — Surface summary in conversation

Output the following block to the console:

```
✓ Check complete — [PRODUCT_NAME] product-scope

Score: [N] / 100   ([grade label])

  [Section 1 heading]   [N]/[weight]   [✓/⚠/✗]
  [Section 2 heading]   [N]/[weight]   [✓/⚠/✗]
  ...
  [Section N heading]   [N]/[weight]   [✓/⚠/✗]

Extra sections (not scored):
  - [Section heading]
  - [Section heading]
  (or "None" if participant has no extra sections)

[N] improvement items flagged. Full report: checks/[report_filename]
[If IDENTICAL_TO_REFERENCE]: ⚠ Warning: submission is byte-for-byte identical to the reference file.
```

Then immediately output a **plain-English summary** of 5–6 sentences. Rules:
- Sentence 1: overall result — score, grade, and one-line verdict ("strong submission", "needs revision", etc.)
- Sentence 2: what the submission does well — name the strongest 1–2 sections and why.
- Sentence 3: if the participant has extra sections, name them and note they were not scored but add value — e.g., "The submission also includes X, Y, and Z beyond the required sections." If no extra sections, skip this sentence.
- Sentence 4–5: what needs improvement — state each gap in plain language, name the section, and say how many points are recoverable. If no gaps, say so in one sentence.
- Sentence 6: the single highest-priority action the participant should take next (or the top optional enhancement if score is perfect).
- Sentence 7 (optional): next step — if score ≥ 75, say "You can proceed to the next task." If score < 75, say "Address the items above and re-run the checker before moving on." Do not mention transformation rules or specific command names.
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
| **Issues and gaps flagged** | 10% | Known limitations, risks, undocumented rules, or out-of-scope boundary ambiguities are called out explicitly. Absence of any such note scores 0. |
| **Structure** | 5% | Required subsections or format elements (tables, diagrams, lists) are present and consistent with the reference layout. |

**Criterion points are rounded to the nearest integer.**

---

### Auto-deducts (apply after rubric scoring)

| Condition | Deduction |
|---|---|
| Section describes the **target/future** system instead of the **source/current** system where source is expected | −50% of section score |
| Scope section (objects in scope): fewer than 3 objects documented when reference has > 10 | −5 pts |
| Out-of-scope section: no entries at all when reference has > 5 | −4 pts |
| Risks section: section present but empty with no "no known risks" statement | −3 pts |

A section is identified as "scope-type", "out-of-scope-type", or "risks-type" by its heading text — look for keywords like "scope", "objects", "out-of-scope", "risk", "boundaries", "consumers", "calculation" in the heading.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | **Excellent** | Thorough and accurate. You can proceed to the next task. |
| 75–89 | **Good** | Minor gaps. Address flagged items; proceeding is acceptable if items are low-risk. |
| 60–74 | **Acceptable** | Several gaps. Revise before proceeding. |
| 45–59 | **Needs work** | Significant sections incomplete or inaccurate. Substantial revision required. |
| 0–44 | **Incomplete** | Major sections missing or direction error. Restart affected sections. |

---

## Check Report Template

Written to `checks/TASK-SCOPE-001_check_report.md` (or `_v2`, `_v3` … if prior reports exist):

```markdown
---
task_id: TASK-SCOPE-001
product: [product name]
participant_file: [resolved path]
reference_file: [resolved path]
checked_at: [ISO 8601]
sections_evaluated: [N]
total_score: [N]/100
grade: [label]
identical_to_reference: [true|false]
---

# Task Check Report — product-scope
_[Product name] | [timestamp]_

[If identical_to_reference: ⚠ Warning: participant file is byte-for-byte identical to the reference.]

**File resolution log:**
- Participant file: [path] — [how resolved]
- Reference file: [path] — [how resolved]
- Product: [name] — [derivation source]
- Sections in reference: [N] | Sections in participant: [N] (matched: [N])
- Point weights: [auto-calculated or from frontmatter] — [s1:N, s2:N, ...]

---

## Score Summary

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
