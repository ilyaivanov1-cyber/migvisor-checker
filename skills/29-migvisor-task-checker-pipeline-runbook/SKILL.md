# Skill: task-checker-pipeline-runbook

## Identity

| Field | Value |
|---|---|
| Skill number | 29 |
| Skill name | task-checker-pipeline-runbook |
| Task ID | TASK-RB-001 |
| Output file | `checks/<trainee_name>/pipeline-runbook/TASK-RB-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check pipeline runbook"
- "check my pipeline runbook"
- "validate pipeline runbook"
- "score pipeline runbook"
- "compare pipeline runbook"
- "run task-checker-pipeline-runbook"
- "run 29-migvisor-task-checker-pipeline-runbook"
- "29"

---

## Invocation Syntax

```
/task-checker-pipeline-runbook
/task-checker-pipeline-runbook participant=<path> reference=<path> trainee=<name>
run task-checker-pipeline-runbook
run 29-migvisor-task-checker-pipeline-runbook
```

---

## Preconditions

- A participant `pipeline_runbook.md` file must exist (default: `trainees/<trainee_name>/pipeline_runbook.md`)
- A reference `pipeline_runbook.md` file must exist (default: `reference/pipeline_runbook.md`)
- The `checks/<trainee_name>/pipeline-runbook/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/pipeline_runbook.md` | `participant=` |
| Reference | `reference/pipeline_runbook.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/pipeline_runbook.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/pipeline_runbook.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `pipeline_runbook.md` in workspace root

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags.
2. Otherwise run auto-detection above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] pipeline_runbook.md.
   Provide an explicit path: /task-checker-pipeline-runbook participant=<path>
   ```
5. Read both files in full.
6. Extract document metadata from each file (lines before the first `##`):
   - Product name / pipeline name (H1 title)
   - Task ID tag if present
   - Catalog/platform reference if mentioned

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — reference has 6 H2 headings:
- N = 7
- Section list: Header Metadata, 1. Daily Monitoring Checklist, 2. Failure Response, 3. Partial Reprocessing Guide, 4. DQ Investigation, 5. Escalation Path, 6. Contacts

**Cross-section matching** — participant may use different section titles or restructure. Match by functional role:

| Reference section | Participant equivalent examples |
|---|---|
| Daily Monitoring Checklist | Morning checklist, daily monitoring, operations checklist, health check, monitoring section |
| Failure Response | Failure diagnosis, re-running failed notebooks, troubleshooting, failure scenarios, incident response |
| Partial Reprocessing Guide | Manual backfill, watermark override, reprocessing, backfill instructions, resetting cutoff |
| DQ Investigation | DQ investigation, data quality failures, clearing rejections, dq_rejections queries |
| Escalation Path | Escalation, incident response, on-call, severity contacts |
| Contacts | Contacts, team contacts, support, email list |

**Multiple sections covering one reference section:** If the participant spreads one reference section across multiple sections (e.g., separate "Re-running failed stage" and "Troubleshooting decision tree" both mapping to "Failure Response"), score both together as a single matched section — use the combined content to evaluate the reference section's criteria.

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. Failure Response — most complex: H3 subsections, diagnosis table, multi-step repair flow
2. DQ Investigation — SQL queries, DQ rules table, join query across stg tables
3. Daily Monitoring Checklist — checklist items, SQL health query, multiple monitoring topics
4. Partial Reprocessing Guide — SQL code blocks, numbered steps, idempotency warning
5. Escalation Path — contact table, severity mapping
6. Contacts — simple contact list
7. Header Metadata — simplest

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

---

### Step 4 — Classify Section Content Types

For each `##` section in the **reference** file, detect:

| Flag | True when |
|---|---|
| `has_checklist_items` | Section contains `- [ ]` checkbox items |
| `has_sql_queries` | Section contains a fenced SQL code block (` ```sql `) |
| `has_diagnosis_table` | Section contains a markdown table mapping failed task/scenario to cause and action |
| `has_escalation_table` | Section contains a markdown table mapping severity or issue type to contact/channel |
| `has_numbered_steps` | Section contains an ordered numbered list as the primary instruction format |
| `has_warning_callout` | Section contains a `> **Warning:**` or `> **Note:**` blockquote callout |
| `has_notebook_references` | Section references notebook names matching `nb_*` pattern or equivalent task names |
| `has_subsections` | Section contains `###` H3 subheadings |

Also detect at **document level**:
- `doc_has_checklist_items`: any `- [ ]` checkbox items exist
- `doc_has_sql_queries`: any SQL code blocks exist
- `doc_has_failure_section`: a failure response / troubleshooting section exists
- `doc_has_escalation_or_contacts`: an escalation path or contacts section exists
- `doc_has_notebook_refs`: any `nb_*` notebook name references exist

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (15 if has_checklist_items else 0)
  − (20 if has_sql_queries else 0)
  − (20 if has_diagnosis_table else 0)
  − (20 if has_escalation_table else 0)
  − 10   ← structure, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Checklist Format | 15% | `has_checklist_items` in reference section |
| SQL Queries | 20% | `has_sql_queries` in reference section |
| Diagnosis / Action Table | 20% | `has_diagnosis_table` in reference section |
| Escalation Table | 20% | `has_escalation_table` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**
- **Header Metadata** — content 90%, structure 10%
- **Daily Monitoring Checklist** (has_checklist, has_sql) — content 55%, checklist 15%, SQL 20%, structure 10%
- **Failure Response** (has_diagnosis_table) — content 70%, diagnosis table 20%, structure 10%
- **Partial Reprocessing Guide** (has_sql) — content 70%, SQL 20%, structure 10%
- **DQ Investigation** (has_sql, has_diagnosis_table) — content 50%, SQL 20%, diagnosis table 20%, structure 10%
- **Escalation Path** (has_escalation_table) — content 70%, escalation table 20%, structure 10%
- **Contacts** — content 90%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

| Sub-criterion | Weight | Checks |
|---|---|---|
| Product / pipeline name in H1 | 35% | H1 title clearly names the product and/or pipeline |
| Task ID / traceability tag present | 30% | Tag like `_TASK-DOCS-001_` or equivalent |
| Catalog / platform reference | 20% | Catalog name (e.g., `globalsales`) or platform (Databricks) mentioned in header |
| Schedule / SLA stated | 15% | Pipeline schedule (cron, time) or SLA window stated |

---

#### Content Completeness Sub-Formula (all procedure sections)

For each procedure section, content completeness measures **operational topic coverage**:

```
score = (topics_covered / reference_topic_count) × 55%
      + (steps_are_specific_and_actionable / total_reference_steps) × 30%
      + (section_intro_paragraph_present) × 15%
```

Where:
- `topics_covered`: count of participant steps/items that address the same operational topic as a reference step (cross-product: different table names, notebook names, catalog names are acceptable — same operational intent required; e.g., "check stg.lineage status" ≡ "verify lineage row has status=success")
- `steps_are_specific_and_actionable`: participant steps that reference specific objects (table names, notebook paths, SQL, secrets scope) or provide a concrete executable action — not vague ("check the pipeline", "monitor the data")
- `section_intro_paragraph_present`: a sentence or paragraph above the checklist/steps/table that explains when or why to perform this procedure

---

#### Checklist Format Sub-Formula (when criterion is scored)

```
score = (checkbox_format_used) × 40%
      + (items_are_ordered_or_grouped) × 30%
      + (items_are_verifiable_pass_fail) × 30%
```

Where:
- `checkbox_format_used`: section uses `- [ ]` syntax for checklist items
- `items_are_ordered_or_grouped`: items are logically ordered (sequential operations) or grouped by topic
- `items_are_verifiable_pass_fail`: each item describes an observable condition that can be marked done/not-done (not just "look at the pipeline")

---

#### SQL Queries Sub-Formula (when criterion is scored)

```
score = (sql_blocks_present) × 30%
      + (sql_targets_product_catalog_tables) × 35%
      + (sql_queries_are_executable / total_sql_blocks) × 35%
```

Where:
- `sql_blocks_present`: at least one fenced ` ```sql ` block exists in the section
- `sql_targets_product_catalog_tables`: SQL references the participant's catalog/schema (e.g., `globalsales.stg.*`) not placeholder text or the reference catalog
- `sql_queries_are_executable`: SQL is syntactically complete — no missing mandatory clauses, no unresolved placeholders except intentional `<variable>` substitutions

---

#### Diagnosis / Action Table Sub-Formula (when criterion is scored)

```
score = (diagnosis_table_present) × 40%
      + (failure_scenarios_covered / reference_failure_count) × 35%
      + (each_entry_has_concrete_action) × 25%
```

Where:
- `diagnosis_table_present`: section contains a markdown table with at least columns for: failed task/scenario, cause/description, and recommended action
- `failure_scenarios_covered`: count of participant failure scenarios that address the same functional failure type as reference entries (cross-product: different notebook names OK)
- `each_entry_has_concrete_action`: each table row's action cell describes a specific step (not just "investigate" or "check logs")

---

#### Escalation Table Sub-Formula (when criterion is scored)

```
score = (escalation_table_present) × 50%
      + (severity_levels_or_issue_types_present) × 25%
      + (contact_channels_are_specific) × 25%
```

Where:
- `escalation_table_present`: section contains a markdown table mapping severity/issue type to contact/channel
- `severity_levels_or_issue_types_present`: table has at least 2 distinct severity levels or issue types (not just one generic row)
- `contact_channels_are_specific`: channel cells name a specific Slack channel, email address, or on-call tool (PagerDuty, OpsGenie, etc.) — not just "contact the team"

---

#### Structure Sub-Formula (all sections)

```
score = (h2_heading_present) × 30%
      + (section_intro_or_context_present) × 25%
      + (appropriate_formatting_for_content_type) × 25%
      + (code_blocks_properly_fenced_if_present) × 20%
```

Where:
- `h2_heading_present`: section has a `##` heading with a clear descriptive title
- `section_intro_or_context_present`: a sentence or paragraph before the first list/table/code block explains when or why this procedure is used
- `appropriate_formatting_for_content_type`: checklists use `- [ ]`, steps use numbered lists, tables use Markdown table syntax, code uses fenced blocks
- `code_blocks_properly_fenced_if_present`: if SQL or shell commands present, they are inside fenced code blocks with a language tag

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No `- [ ]` checklist items anywhere in document | −4 pts | Skip if `doc_has_checklist_items` is true |
| No SQL code blocks anywhere in document | −4 pts | Skip if `doc_has_sql_queries` is true |
| No failure response or troubleshooting section | −5 pts | Skip if `doc_has_failure_section` is true |
| No escalation path or contacts anywhere | −3 pts | Skip if `doc_has_escalation_or_contacts` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| No notebook names or task names anywhere in document | −3 pts | Skip if `doc_has_notebook_refs` is true |
| SQL present but uses wrong catalog (reference catalog instead of participant's) | −2 pts | Only if SQL blocks exist |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/pipeline-runbook/TASK-RB-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/pipeline-runbook/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-RB-001
skill: task-checker-pipeline-runbook
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-RB-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<resolved participant path>`
**Reference file:** `<resolved reference path>`
**Generated:** <today's date YYYY-MM-DD>

---

## Score Summary

**The pipeline runbook Score: <total>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | <w> | <r>/100 | <pts> | ✓/⚠/✗ |
| ... one row per section ... |
| **Subtotal** | | | | **<sum>** | |
| Auto-deducts | | | | **−<n>** | |
| **Total** | | | | **<total>/100** | |

**Grade: <grade>**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| ... |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No checklist items anywhere | −4 pts | Yes/No — reason |
| No SQL code blocks anywhere | −4 pts | Yes/No — reason |
| No failure/troubleshooting section | −5 pts | Yes/No — reason |
| No escalation or contacts | −3 pts | Yes/No — reason |
| Missing H2 section | −5 pts each (max −15) | Yes/No — list |
| No notebook/task names anywhere | −3 pts | Yes/No — reason |
| SQL uses wrong catalog | −2 pts | Yes/No — reason |

**Total auto-deducts: −<n> pts**

---

## Section Feedback

### <Section Title> — <raw>/100 (weight <w> → <pts> pts)

**Criteria scored:** <list of active criteria with weights>

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| ... |

**Strengths:**
- ...

**Gaps:**
- ...

**Improvement items:**
- [ ] ...

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | ... | ... | +N pts |

---

## Priority Actions

1. **<Action>** — <detail>. Worth up to **+N pts**.
...

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing monitoring checklist, escalation path, or SQL queries absent |
| 0–44 | Incomplete | Major sections absent or no operational procedures documented |

---

*Report generated by skill 29-migvisor-task-checker-pipeline-runbook on <date>*
```

---

### Step 10 — Surface Summary in Conversation

After writing the report, output the following console block directly in the conversation:

```
╔══════════════════════════════════════════════════════════════════════╗
║  TASK-RB-001  •  Pipeline Runbook  •  <product name>                ║
╠══════════════════════════════════════════════════════════════════════╣
║  <total> / 100  —  <grade>                                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

Then write a **5–6 sentence plain-English verdict** covering:
1. What the participant did well (strongest 1–2 sections with specific detail)
2. The main structural or content gap (most impactful missing or weak section)
3. A second significant gap (second priority issue)
4. **The numeric score** — sentence 4 must state the total score as a number (e.g., "The pipeline runbook scores 62/100 (Acceptable).")
5. Top priority fix and estimated point recovery
6. Secondary fix or overall recommendation

Keep each sentence factual and specific to the participant's document — no generic praise.
