# Skill: task-checker-secrets-rotation-runbook

## Identity

| Field | Value |
|---|---|
| Skill number | 32 |
| Skill name | task-checker-secrets-rotation-runbook |
| Task ID | TASK-SEC-002 |
| Output file | `checks/<trainee_name>/secrets-rotation/TASK-SEC-002_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check secrets rotation runbook"
- "check my secrets rotation runbook"
- "validate secrets rotation runbook"
- "score secrets rotation runbook"
- "compare secrets rotation runbook"
- "check secrets_rotation_runbook"
- "run task-checker-secrets-rotation-runbook"
- "run 32-migvisor-task-checker-secrets-rotation-runbook"
- "32"

---

## Invocation Syntax

```
/task-checker-secrets-rotation-runbook
/task-checker-secrets-rotation-runbook participant=<path> reference=<path> trainee=<name>
run task-checker-secrets-rotation-runbook
run 32-migvisor-task-checker-secrets-rotation-runbook
```

---

## Preconditions

- A participant `secrets_rotation_runbook.md` file must exist (default: `trainees/<trainee_name>/secrets_rotation_runbook.md`)
- A reference `secrets_rotation_runbook.md` file must exist (default: `reference/secrets_rotation_runbook.md`)
- The `checks/<trainee_name>/secrets-rotation/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/secrets_rotation_runbook.md` | `participant=` |
| Reference | `reference/secrets_rotation_runbook.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/secrets_rotation_runbook.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/secrets_rotation_runbook.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `secrets_rotation_runbook.md` in workspace root

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags.
2. Otherwise run auto-detection above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] secrets_rotation_runbook.md.
   Provide an explicit path: /task-checker-secrets-rotation-runbook participant=<path>
   ```
5. Read both files in full.
6. Extract document metadata from each file (lines before the first `##`):
   - Runbook title (H1)
   - Task ID tag if present
   - Scope / catalog name if mentioned

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — reference has 6 H2 headings:
- N = 7
- Section list: Header Metadata, 1. Trigger Conditions, 2. Rotation Procedure, 3. Verification Steps, 4. Rollback Procedure, 5. Notification Checklist, 6. Rotation Log

**Cross-section matching** — participant may use different section titles or structure. Match by functional role:

| Reference section | Participant equivalent examples |
|---|---|
| Trigger Conditions | Trigger conditions, when to rotate, rotation triggers, conditions for rotation, schedule |
| Rotation Procedure | Rotation procedure, rotate secrets, rotation steps, updating a secret, how to rotate |
| Verification Steps | Verification, verify, confirm, post-rotation check, validation steps |
| Rollback Procedure | Rollback, rollback procedure, recovery, revert, if rotation fails |
| Notification Checklist | Notification, notify, checklist, stakeholders, communication |
| Rotation Log | Rotation log, audit log, history, change log, log table |

**Multiple participant sections covering one reference section:** If the participant spreads the Rotation Procedure across numbered H3 steps under one H2, score all steps together as the Rotation Procedure section. If the participant has an "Emergency rotation" section, it may be combined with the Rollback Procedure section when scoring if no separate rollback section exists.

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. Rotation Procedure — bash commands, dev/prod scope separation, H3 subsections, most operational
2. Rollback Procedure — bash commands, numbered recovery steps, incident-critical
3. Verification Steps — numbered steps, notebook references, lineage/PII checks
4. Trigger Conditions — enumerated conditions list, policy references
5. Notification Checklist — checkbox items, stakeholder list
6. Rotation Log — table structure, audit trail
7. Header Metadata — simplest

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example with N=7:** base_weight=14, remainder=2 → Rotation Procedure gets 15 pts, Rollback Procedure gets 15 pts; all others get 14 pts.

---

### Step 4 — Classify Section Content Types

For each `##` section in the **reference** file, detect:

| Flag | True when |
|---|---|
| `has_bash_commands` | Section contains a fenced `bash` code block with CLI commands |
| `has_checklist_items` | Section contains `- [ ]` checkbox items |
| `has_trigger_list` | Section contains a bullet list enumerating specific rotation trigger conditions (schedule, incident, service account change, etc.) |
| `has_rotation_log_table` | Section contains a Markdown table with rotation audit columns (Date, Rotated By, Environment, Keys Rotated, Reason) |
| `has_numbered_steps` | Section uses a numbered list as the primary instruction format |
| `has_notebook_references` | Section references notebook names (`nb_*` pattern or named pipeline tasks) |
| `has_dev_prod_separation` | Section contains separate commands or sub-sections for dev and prod environments |

Also detect at **document level**:
- `doc_has_bash_commands`: any bash code blocks exist
- `doc_has_trigger_conditions`: any list of rotation trigger conditions exists
- `doc_has_verification`: any post-rotation verification steps or commands exist
- `doc_has_rollback`: any rollback or recovery procedure exists
- `doc_has_notification`: any notification checklist or stakeholder list exists
- `doc_has_rotation_log`: any rotation audit log table exists
- `doc_has_hardcoded_credentials`: any literal credential value hardcoded in a code block

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (20 if has_bash_commands else 0)
  − (15 if has_checklist_items else 0)
  − (15 if has_trigger_list else 0)
  − (20 if has_rotation_log_table else 0)
  − 10   ← structure, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Bash Commands | 20% | `has_bash_commands` in reference section |
| Checklist Format | 15% | `has_checklist_items` in reference section |
| Trigger List | 15% | `has_trigger_list` in reference section |
| Rotation Log Table | 20% | `has_rotation_log_table` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**
- **Header Metadata** — content 90%, structure 10%
- **Trigger Conditions** (has_trigger_list) — content 75%, trigger list 15%, structure 10%
- **Rotation Procedure** (has_bash_commands) — content 70%, bash 20%, structure 10%
- **Verification Steps** — content 90%, structure 10%
- **Rollback Procedure** (has_bash_commands) — content 70%, bash 20%, structure 10%
- **Notification Checklist** (has_checklist_items) — content 75%, checklist 15%, structure 10%
- **Rotation Log** (has_rotation_log_table) — content 70%, rotation log 20%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

| Sub-criterion | Weight | Checks |
|---|---|---|
| Runbook title in H1 | 35% | H1 clearly names the rotation runbook and/or product |
| Task ID / traceability tag present | 30% | Tag like `_TASK-SEC-005_` or equivalent |
| Scope / catalog reference | 20% | Scope name (e.g., `globalsales`) or catalog mentioned in header block |
| Author / generated date present | 15% | Author, version, or created date before first `##` |

---

#### Content Completeness Sub-Formula (all sections)

```
score = (topics_covered / reference_topic_count) × 55%
      + (details_are_specific_and_actionable / total_reference_details) × 30%
      + (section_intro_paragraph_present) × 15%
```

Where:
- `topics_covered`: count of participant items addressing the same operational topic as a reference item (cross-product: different scope names, notebook names, key names acceptable — same functional intent required; e.g., "rotate source_jdbc_url" ≡ "rotate jdbc_url"; "nb_extract_sales" ≡ "nb_extract_purchase")
- `details_are_specific_and_actionable`: participant items that provide concrete instructions (scope names, key names, CLI commands, notebook names, recovery steps) rather than vague or placeholder-only content
- `section_intro_paragraph_present`: a sentence or paragraph above the first list/table/code block explaining the purpose of the section

---

#### Bash Commands Sub-Formula (when criterion is scored)

```
score = (bash_blocks_present) × 35%
      + (commands_target_product_scope_or_keys) × 35%
      + (commands_are_executable) × 30%
```

Where:
- `bash_blocks_present`: at least one fenced bash code block exists in the section
- `commands_target_product_scope_or_keys`: CLI commands reference the participant's own scope (e.g., `--scope globalsales`) rather than the reference scope
- `commands_are_executable`: commands are syntactically complete — no unresolved `{{placeholder}}` substitutions (intentional `<variable>` substitutions are acceptable)

---

#### Trigger List Sub-Formula (when criterion is scored)

```
score = (trigger_list_present) × 35%
      + (triggers_covered / reference_trigger_count) × 40%
      + (policy_or_schedule_stated) × 25%
```

Where:
- `trigger_list_present`: section contains a bullet or numbered list of rotation trigger conditions
- `triggers_covered`: count of participant trigger conditions that address the same scenario as reference entries (scheduled rotation, security incident, service account change, infrastructure migration)
- `policy_or_schedule_stated`: at least one trigger includes a specific schedule (e.g., "every 90 days") or policy reference

---

#### Checklist Sub-Formula (when criterion is scored)

```
score = (checkbox_format_used) × 40%
      + (stakeholders_covered / reference_stakeholder_count) × 35%
      + (items_are_specific) × 25%
```

Where:
- `checkbox_format_used`: section uses `- [ ]` syntax for notification items
- `stakeholders_covered`: count of participant stakeholder entries matching reference roles (Data Engineering lead, Platform Security, on-call engineer, or functional equivalents)
- `items_are_specific`: each item names a specific role, team, or channel rather than a generic "notify team"

---

#### Rotation Log Table Sub-Formula (when criterion is scored)

```
score = (log_table_present) × 40%
      + (required_columns_present / reference_column_count) × 35%
      + (initial_entry_or_placeholder_present) × 25%
```

Where:
- `log_table_present`: section contains a Markdown table for recording rotation events
- `required_columns_present`: count of columns from: Date, Rotated By, Environment, Keys Rotated, Reason
- `initial_entry_or_placeholder_present`: table has at least one row (even a placeholder first entry) to show the expected format

---

#### Structure Sub-Formula (all sections)

```
score = (h2_heading_present) × 30%
      + (section_intro_or_context_present) × 25%
      + (appropriate_formatting_for_content_type) × 25%
      + (code_blocks_properly_fenced_if_present) × 20%
```

Where:
- `h2_heading_present`: section has a `##` heading with a descriptive title
- `section_intro_or_context_present`: a sentence or paragraph before the first list/table/code block
- `appropriate_formatting_for_content_type`: trigger conditions use bullet lists, checklists use `- [ ]`, steps use numbered lists, commands use fenced code blocks
- `code_blocks_properly_fenced_if_present`: CLI commands are inside fenced code blocks with a language tag

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No bash CLI code blocks anywhere in document | −4 pts | Skip if `doc_has_bash_commands` is true |
| No rotation trigger conditions documented | −4 pts | Skip if `doc_has_trigger_conditions` is true |
| No post-rotation verification steps anywhere | −4 pts | Skip if `doc_has_verification` is true |
| No rollback or recovery procedure anywhere | −4 pts | Skip if `doc_has_rollback` is true |
| No notification checklist or stakeholder list | −3 pts | Skip if `doc_has_notification` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| Hardcoded credential value in any code block | −5 pts | Applied if `doc_has_hardcoded_credentials` is true |
| Bash commands use `--string-value "<literal-credential>"` with an actual value | −3 pts | Only if literal credential strings appear in code blocks |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/secrets-rotation/TASK-SEC-002_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/secrets-rotation/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-SEC-002
skill: task-checker-secrets-rotation-runbook
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-SEC-002 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<resolved participant path>`
**Reference file:** `<resolved reference path>`
**Generated:** <today's date YYYY-MM-DD>

---

## Score Summary

**Secrets Rotation Runbook Score: <total>/100**

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
| No bash CLI code blocks anywhere | −4 pts | Yes/No — reason |
| No rotation trigger conditions | −4 pts | Yes/No — reason |
| No post-rotation verification steps | −4 pts | Yes/No — reason |
| No rollback or recovery procedure | −4 pts | Yes/No — reason |
| No notification checklist or stakeholder list | −3 pts | Yes/No — reason |
| Missing H2 section | −5 pts each (max −15) | Yes/No — list |
| Hardcoded credential value in code block | −5 pts | Yes/No — reason |
| Bash uses literal credential string-value | −3 pts | Yes/No — reason |

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
| 45–59 | Needs work | Missing rollback procedure, notification checklist, or rotation log absent |
| 0–44 | Incomplete | Major sections absent or no CLI rotation commands documented |

---

*Report generated by skill 32-migvisor-task-checker-secrets-rotation-runbook on <date>*
```

---

### Step 10 — Surface Summary in Conversation

After writing the report, output the following console block directly in the conversation:

```
╔══════════════════════════════════════════════════════════════════════╗
║  TASK-SEC-002  •  Secrets Rotation Runbook  •  <product name>       ║
╠══════════════════════════════════════════════════════════════════════╣
║  <total> / 100  —  <grade>                                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

Then write a **5–6 sentence plain-English verdict** covering:
1. What the participant did well (strongest 1–2 sections with specific detail)
2. The main structural or content gap (most impactful missing or weak section)
3. A second significant gap (second priority issue)
4. **The numeric score** — sentence 4 must state the total score as a number (e.g., "The secrets rotation runbook scores 47/100 (Needs Work).")
5. Top priority fix and estimated point recovery
6. Secondary fix or overall recommendation

Keep each sentence factual and specific to the participant's document — no generic praise.
