---
name: 20-migvisor-task-checker-validation-report
description: Evaluates a participant's validation report against a reference final report. Works with any product, any number of artifact categories/sections. Scores completeness, verdict documentation, finding quality, metrics accuracy, and structure. Provides per-section comments and a scored summary with 5–6 sentence prose.
---

# Skill: task-checker-validation-report

## Identity

- **Name:** `task-checker-validation-report`
- **Selection signal:** Evaluates and scores a participant-submitted validation report against a reference — use when a participant has completed a validation report and wants structured feedback on its quality, completeness, and accuracy.
- **Trigger phrases:**
  - "check my validation report"
  - "evaluate validation report"
  - "score validation report"
  - "review validation report"
  - "check task validation report"
  - "run 20-migvisor-task-checker-validation-report"

---

## Invocation Syntax

```
/task-checker-validation-report [participant_file] [reference_file] [--product <name>]
```

All arguments are optional. Examples:
- `/task-checker-validation-report my-report.md` — participant file supplied; reference auto-resolved
- `/task-checker-validation-report validation-report.md report_final.md` — both supplied
- `/task-checker-validation-report --product Sales_Orders` — both files auto-resolved; product name overridden
- `/task-checker-validation-report` — everything auto-resolved from workspace

---

## Preconditions

| Condition | Check | If not met |
|---|---|---|
| Participant file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1A) | Ask: "Provide the path to your validation report, e.g. `/task-checker-validation-report my-report.md`" |
| Reference file resolvable | Path supplied OR exactly one candidate found in workspace (see Step 1B) | If zero: "No reference file found. Supply it as the second argument." If multiple: "Multiple candidates found: [list]. Which should I use?" |
| Participant file readable | File exists and is non-empty | "Cannot read submission at [path]. Check the path and try again." |
| Participant file has structure | File contains at least one `## ` heading | "Submission does not appear to be a valid validation report — no sections found. Verify the correct file." |

---

## Input Inventory

| Input | Source | Required |
|---|---|---|
| Participant's validation report | Path supplied at invocation (positional arg 1) OR auto-resolved | Yes |
| Reference (final) validation report | Path supplied at invocation (positional arg 2) OR auto-resolved | Yes |
| Product name | Derived from: (1) `--product` flag, (2) H1 heading (e.g., `# SmartBuilder Validation Report — <Name>`), (3) `**Product:**` metadata field, (4) `product:` YAML frontmatter, (5) parent directory name | Derived |

---

## Workflow

### Step 1 — Resolve files and product

**1A — Participant file**

If a path was supplied as argument 1, use it. Otherwise search the workspace for files matching (in priority order):
1. `validation-report.md`
2. `validation_report.md`
3. Any `*validation*report*.md` NOT containing "final" in the name

If multiple candidates exist at the same level: ask the user which to use.

**1B — Reference file**

If a path was supplied as argument 2, use it. Otherwise search the workspace for files matching (in priority order):
1. `report_final.md`
2. `report-final.md`
3. Any `*report*final*.md` or `*final*report*.md`

If exactly one candidate found: use it. If multiple: ask the user. Exclude the participant file.

**1C — Product name**

Derive in this order:
1. `--product <name>` flag
2. `# SmartBuilder Validation Report — <Name>` or `# Validation Report: <Name>` H1 heading in participant file
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

Detect scoreable sections using this priority order:

1. **Summary section** — the first `## ` H2 heading whose text contains "Summary", "Executive Summary", or "Overview". Treat as one scored section.

2. **Results/artifact category sections** — all `### ` H3 headings found under any `## Results`, `## Results Table`, or `## Validation Results` H2 heading. Each `### ` heading = one scored artifact category section. If the reference uses a flat `## Results` table with no H3 subsections, treat the entire `## Results` section as one scored section.

3. **Findings section** — the first `## ` H2 heading whose text contains "Finding", "Failure", "Issues", or "Defects". Treat as one scored section.

4. **Additional H2 sections** — any remaining `## ` headings not matched above (e.g., `## DQR Coverage Note`, `## Architecture Notes`). Each = one additional scored section.

5. **Metadata section** — treat the document header (H1 + metadata fields before the first `## `) as one scored section named "Header Metadata".

For each section record: heading text, artifact rows (for results categories), failure entries (for findings), summary metrics (for summary section).

**3B — Inventory key elements per reference section**

For each reference section record:
- **Results category sections**: artifact count, PASS count, FAIL count, WARN count, column names in table
- **Summary section**: total artifact count, PASS count, FAIL count, WARN count, PASS rate, narrative present
- **Findings section**: number of failures documented, whether each failure has file path + root cause + spec reference
- **Additional sections**: headings and whether content addresses a specific concern

**3C — Match sections in participant file**

For each reference section, find the best match in the participant file:

1. **Heading text match** — keyword overlap: "summary", "executive summary", "results", "findings", "failure", "warning", "DQR", "architecture", "docs", "tests", "config", "ETL", "DB", etc. Use best text match.
2. **Category type match** — if reference has `### DB — DDL`, match to participant section with "DB" or "DDL" keywords; `### Tests` matches any participant section with "Test".
3. **No match** — score 0 for that reference section.

| Outcome | Action |
|---|---|
| Match found | Evaluate normally — rubric |
| Reference section with no match in participant | Score 0; note as absent |
| Participant section not matched to any reference section | Note as extra; do not score; do not penalise |

---

### Step 4 — Calculate point weights

**4A — Check for explicit weights**

Look for a `scoring_weights` entry in the reference file's YAML frontmatter. If present and sums to 100: use them.

**4B — Auto-calculate weights**

If no explicit weights:
1. Count N = total scored sections detected.
2. Base weight = `floor(100 / N)`.
3. Distribute the remainder one point at a time to sections in this priority order: Findings section first, then Summary section, then artifact category sections in descending order of artifact count.
4. Minimum weight per section: 5 pts. Maximum: 30 pts.

Display calculated weights in the Score Summary table.

---

### Step 5 — Handle placeholder and deferred fields

Before scoring, identify any row or field containing `[TBD]`, `[PENDING]`, `[TODO]`, `N/A`, or `[FILL IN]`.

- Treat as **intentional deferrals**, not missing content.
- If a FAIL finding row has a placeholder instead of a finding description: award 50% of that row's contribution and flag as `[DEFERRED]`.
- If a row is entirely absent: apply normal missing-row scoring.

---

### Step 6 — Score each section

Apply the **Per-Section Rubric** (below) to every matched section.

```
section → { weight, score, rubric_results[], deferred_fields[], improvements[] }
```

---

### Step 7 — Apply approach policy

Before finalising scores:

- Participant uses different column names in results table (e.g., "Status" vs "Verdict") → **no deduction**
- Participant orders artifact categories differently → **no deduction**
- Participant adds extra artifact categories not in reference → **no deduction**, note as supplementary
- Participant uses inline findings rather than a separate Findings section → **no deduction** if each FAIL row has sufficient inline detail
- Participant uses different failure ID scheme (e.g., `BUG-001` vs `F-01`) → **no deduction**
- PASS rate calculation differs slightly due to rounding → **no deduction**

Deduct only for **missing content, incomplete findings, or inaccurate metrics** — not for different presentation style.

---

### Step 8 — Assemble the check report

Determine the output file path:
1. Base name: `TASK-VAL-001_check_report.md`
2. If it does not exist: write it.
3. If it exists: increment suffix (`_v2`, `_v3`, …) until a free path is found.
4. **Never overwrite an existing report file.**

Create the `checks/` directory if it does not exist.

---

### Step 9 — Surface summary in conversation

Output the following block to the console:

```
✓ Check complete — [PRODUCT_NAME] validation report

Score: [N] / 100   ([grade label])

  Header Metadata         [N]/[weight]   [✓/⚠/✗]
  Executive Summary       [N]/[weight]   [✓/⚠/✗]
  [Results category 1]    [N]/[weight]   [✓/⚠/✗]
  [Results category 2]    [N]/[weight]   [✓/⚠/✗]
  ...
  Findings                [N]/[weight]   [✓/⚠/✗]
  [Additional sections]   [N]/[weight]   [✓/⚠/✗]

Extra sections (not scored):
  - [Section heading]
  (or "None")

[N] improvement items flagged. Full report: checks/[report_filename]
[If IDENTICAL_TO_REFERENCE]: ⚠ Warning: submission is byte-for-byte identical to the reference file.
```

Then immediately output a **plain-English summary** of 5–6 sentences. Rules:
- Sentence 1: overall result — score, grade, and one-line verdict on the report's quality.
- Sentence 2: what the report does well — name the strongest 1–2 sections and specifically why (e.g., "Findings section includes file path, root cause, fix, and spec reference for every failure").
- Sentence 3 (optional): if the participant includes artifact categories or sections beyond the reference, name them and note they add coverage. If none, skip.
- Sentence 4: what needs improvement — name the specific section(s) and the gap (missing findings detail, inaccurate metrics, absent sections), stating points recoverable. If no gaps, say so.
- Sentence 5: next step — if score ≥ 75, say "You can proceed to the next task." If score < 75, say "Address the items above and re-run the checker before moving on."
- No bullet points, no markdown headers — flowing prose only.

---

## Per-Section Rubric

### Results artifact category sections (DB, ETL, Config, Tests, Docs, etc.)

Points expressed as **percentages of that section's weight**.

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Completeness** | 40% | Every artifact row has all required columns filled (artifact path, task ID, verdict, finding). FAIL rows must have a finding entry — inline description or a reference to a named finding (e.g., "see F-01"). Score proportionally: (rows with complete entries) / (total rows). |
| **Verdict documentation** | 25% | FAIL and WARN verdicts are substantiated — either inline finding or finding reference. PASS rows have a non-empty Notes/Finding entry (even brief). Score proportionally per row type: FAIL rows with no finding or finding reference score 0 for this criterion. |
| **Specificity** | 20% | Findings and notes reference specific technical details: function names, column names, task IDs, spec references (e.g., `FR-006`, `TASK-DB-001`). Vague notes like "has issues" or "needs review" score lower than notes naming specific facts. Score based on average specificity across rows. |
| **Metrics accuracy** | 10% | If the section heading states an artifact count or PASS/FAIL breakdown, it matches the actual rows. Off by more than 1 = partial deduct. |
| **Structure** | 5% | Table present with at minimum: Artifact / Task / Verdict (or Status) / Finding (or Notes) columns. Consistent formatting. |

### Summary / Executive Summary section

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Metrics accuracy** | 40% | Total artifacts, PASS count, FAIL count, WARN count, and PASS rate match what is actually in the results tables. Compute expected values from the results tables and compare. Off by more than 1 = proportional deduction. |
| **Failure coverage** | 30% | All FAIL artifacts are mentioned in the summary narrative (at minimum by count and general category; ideally by relationship — e.g., "four failures are a propagated consequence of one root cause"). |
| **Specificity** | 20% | Summary narrative names specific artifacts or failure IDs rather than generic statements. |
| **Structure** | 10% | Metrics table or equivalent present; narrative paragraph present. |

### Findings / Failure Details section

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Finding coverage** | 40% | Every FAIL artifact in the results tables has a corresponding entry in the Findings section (or sufficiently detailed inline finding). WARN artifacts addressed if WARN count > 0. Score proportionally: (failures with findings) / (total failures). |
| **Finding depth** | 30% | Each finding includes: (1) artifact file path, (2) specific root cause description, (3) fix or recommended action, (4) spec reference (task ID, FR/NFR ID, or requirement name). Score 25% per element present, per finding; average across all findings. |
| **Technical accuracy** | 20% | Root cause descriptions are technically plausible and specific (not generic). Spec references point to real task IDs or requirement IDs visible in the results table. |
| **Structure** | 10% | Findings organised by failure ID or artifact; each finding has a heading; consistent format. |

### Header Metadata section

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Field completeness** | 50% | Key metadata fields present: product/project name, validation date, spec baseline (design.md / requirements.md / tasks.md or equivalent), validator/author identity. Score proportionally per field. |
| **Accuracy** | 30% | Dates and spec version references are internally consistent with the report content. |
| **Structure** | 20% | Metadata presented as a table or labelled key–value pairs; H1 title identifies the product and report type. |

### Additional sections (DQR notes, architecture notes, coverage notes, etc.)

| Criterion | % of section pts | How to evaluate |
|---|---|---|
| **Coverage** | 50% | Section addresses the topic implied by its heading with substantive content (not a placeholder). |
| **Specificity** | 30% | Names specific rules, artifacts, behaviors, or constraints relevant to the section topic. |
| **Structure** | 20% | Section has a heading and at least one paragraph or table of content. |

**Criterion points are rounded to the nearest integer.**

---

## Auto-deducts (applied after rubric scoring)

| Condition | Deduction |
|---|---|
| FAIL artifact present in results table but has no finding entry AND no Findings section entry | −2 pts (global, once per unfound FAIL, max −6 pts) |
| Findings section entirely absent when participant has ≥ 1 FAIL verdict | −5 pts (global) |
| Summary metrics are internally inconsistent (PASS + FAIL + WARN ≠ Total stated) | −3 pts (global) |
| Results table entirely absent | −10 pts (global) |
| Artifact file paths not present in results rows (verdict rows with no artifact path) | −2 pts (global, once) |

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | **Excellent** | Thorough and accurate. You can proceed to the next task. |
| 75–89 | **Good** | Minor gaps. Address flagged items; proceeding is acceptable if items are low-risk. |
| 60–74 | **Acceptable** | Several gaps. Revise before proceeding. |
| 45–59 | **Needs work** | Significant findings undocumented or metrics inaccurate. Substantial revision required. |
| 0–44 | **Incomplete** | Results table or Findings section missing, or majority of FAILs undocumented. |

---

## Check Report Template

Written to `checks/TASK-VAL-001_check_report.md` (or `_v2`, `_v3` … if prior reports exist):

```markdown
---
task_id: TASK-VAL-001
product: [product name]
participant_file: [resolved path]
reference_file: [resolved path]
checked_at: [ISO 8601]
sections_evaluated: [N]
total_score: [N]/100
grade: [label]
identical_to_reference: [true|false]
---

# Task Check Report — validation report
_[Product name] | [timestamp]_

[If identical_to_reference: ⚠ Warning: participant file is byte-for-byte identical to the reference.]

**File resolution log:**
- Participant file: [path] — [how resolved]
- Reference file: [path] — [how resolved]
- Product: [name] — [derivation source]
- Sections in reference: [N] | Sections in participant: [N] (matched: [N], extra: [N])
- Point weights: [auto-calculated or from frontmatter]
- Participant metrics: Total [N] | PASS [N] | FAIL [N] | WARN [N] | PASS rate [N]%

---

## Score Summary

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| Header Metadata | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| Executive Summary | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| [Results category] | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| Findings | [participant heading] | [N] | [N] | ✓/⚠/✗ |
| **Total** | | **100** | **[N]** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### [Section heading] ([score]/[weight])
_Matched to participant [heading]_

**Completeness:** [rows with full entries vs. rows missing fields; list artifact paths of incomplete rows]
**Verdict documentation:** [FAIL/WARN rows with vs. without finding documentation; list undocumented verdicts]
**Specificity:** [quality of notes — named specific facts vs. vague statements; examples]
**Metrics accuracy:** [stated count vs. actual count in rows]
**Structure:** [column names present, table format consistent]

**Artifact inventory:**
- Total rows: [N] | PASS: [N] | FAIL: [N] | WARN: [N]
- FAIL rows with findings: [N]/[N]
- Rows with empty Finding/Notes: [list artifact paths]

**Deferred fields `[DEFERRED]`:** [list]

**Improvement items:**
- [ ] [Specific actionable item]

[Repeated for all evaluated sections]

---

## Extra Sections (not in reference)
[List with section heading and brief note, or "None"]

## Approach Notes
[Valid alternative approaches — inline findings instead of separate section, different column names, etc.]

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
