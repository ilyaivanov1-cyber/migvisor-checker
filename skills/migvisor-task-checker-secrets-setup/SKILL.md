# Skill: task-checker-secrets-setup

## Identity

| Field | Value |
|---|---|
| Skill number | 31 |
| Skill name | task-checker-secrets-setup |
| Task ID | TASK-SEC-001 |
| Output file | `checks/<trainee_name>/secrets-setup/TASK-SEC-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check secrets setup"
- "check my secrets setup"
- "validate secrets setup"
- "score secrets setup"
- "compare secrets setup"
- "check secrets_setup"
- "run task-checker-secrets-setup"
- "run 31-migvisor-task-checker-secrets-setup"
- "31"

---

## Invocation Syntax

```
/task-checker-secrets-setup
/task-checker-secrets-setup participant=<path> reference=<path> trainee=<name>
run task-checker-secrets-setup
run 31-migvisor-task-checker-secrets-setup
```

---

## Preconditions

- A participant `secrets_setup.md` file must exist (default: `trainees/<trainee_name>/secrets_setup.md`)
- A reference `secrets_setup.md` file must exist (default: `reference/secrets_setup.md`)
- The `checks/<trainee_name>/secrets-setup/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/secrets_setup.md` | `participant=` |
| Reference | `reference/secrets_setup.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/secrets_setup.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/secrets_setup.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `secrets_setup.md` in workspace root

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags.
2. Otherwise run auto-detection above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] secrets_setup.md.
   Provide an explicit path: /task-checker-secrets-setup participant=<path>
   ```
5. Read both files in full.
6. Extract document metadata from each file (lines before the first `##`):
   - Runbook / guide title (H1)
   - Task ID tag if present
   - Pipeline / catalog name if mentioned

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — reference has 8 H2 headings:
- N = 9
- Section list: Header Metadata, Prerequisites, Step 1 — Create the Dev Scope, Step 2 — Create the Prod Scope, Step 3 — Register Required Keys (Dev), Step 4 — Register Required Keys (Prod), Step 5 — Verify, Step 6 — Credential Rotation, Reference

**Cross-section matching** — participant may use different section titles or structure. Match by functional role:

| Reference section | Participant equivalent examples |
|---|---|
| Prerequisites | Prerequisites, requirements, before you start, setup requirements |
| Step 1 — Create the Dev Scope | Secret scope, create scope, scope setup, dev scope |
| Step 2 — Create the Prod Scope | Prod scope, production scope, create prod scope |
| Step 3 — Register Required Keys (Dev) | Keys, adding a key, register keys, put secret, key registration, adding/updating a key |
| Step 4 — Register Required Keys (Prod) | Prod keys, production keys |
| Step 5 — Verify | Verify, validation, list keys, check setup, verification |
| Step 6 — Credential Rotation | Rotation, rotate secrets, credential rotation, rotation procedure |
| Reference | Reference, references, links, documentation, external links |

**Multiple sections covering one reference section:** If the participant merges multiple reference steps into one section (e.g., a single "Secret scope" covering both dev and prod scope creation), score the combined content against all matched reference sections — do not double-penalise for the structural merge.

**Single section covering multiple reference steps:** If the participant has one "Keys" or "Adding a key" section that addresses both Steps 3 and 4, score it against both reference steps combined.

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. Step 3 — Register Required Keys (Dev) — bash commands, multiple key names, security-critical
2. Step 5 — Verify — Python/bash verification code, security practice (non-revealing check)
3. Step 1 — Create the Dev Scope — bash CLI command, scope naming
4. Step 4 — Register Required Keys (Prod) — same pattern as Step 3
5. Prerequisites — bash env var exports, software requirements
6. Step 2 — Create the Prod Scope — bash CLI only
7. Step 6 — Credential Rotation — reference pointer only
8. Reference — links and key name index
9. Header Metadata — simplest

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example with N=9:** base_weight=11, remainder=1 → Step 3 (Register Required Keys Dev) gets 12 pts; all others get 11 pts.

---

### Step 4 — Classify Section Content Types

For each `##` section in the **reference** file, detect:

| Flag | True when |
|---|---|
| `has_bash_commands` | Section contains a fenced `bash` (or shell) code block with CLI commands |
| `has_python_code` | Section contains a fenced `python` code block |
| `has_key_inventory` | Section contains a list or table enumerating specific secret key names |
| `has_verification_step` | Section contains a command to list or inspect secrets without revealing their values (e.g., `dbutils.secrets.list(...)`) |
| `has_env_var_exports` | Section contains `export VAR=...` shell commands for environment setup |
| `has_numbered_steps` | Section uses a numbered list as the primary instruction format |
| `has_external_reference` | Section contains a hyperlink or cross-reference to another document |

Also detect at **document level**:
- `doc_has_bash_commands`: any bash/CLI code blocks exist
- `doc_has_scope_creation`: any `databricks secrets create-scope` command exists
- `doc_has_key_registration`: any `databricks secrets put` command exists
- `doc_has_verification`: any non-revealing key verification (list keys) command exists
- `doc_has_dev_prod_separation`: separate dev and prod scopes or environments are documented
- `doc_has_hardcoded_credentials`: any literal password, token, or connection string value hardcoded in a code block (not a placeholder)

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (20 if has_bash_commands else 0)
  − (15 if has_python_code else 0)
  − (15 if has_key_inventory else 0)
  − (20 if has_verification_step else 0)
  − 10   ← structure, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Bash Commands | 20% | `has_bash_commands` in reference section |
| Python Code | 15% | `has_python_code` in reference section |
| Key Inventory | 15% | `has_key_inventory` in reference section |
| Verification Step | 20% | `has_verification_step` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**
- **Header Metadata** — content 90%, structure 10%
- **Prerequisites** (has_bash_commands) — content 70%, bash commands 20%, structure 10%
- **Step 1 Create Dev Scope** (has_bash_commands, has_verification_step) — content 50%, bash 20%, verification 20%, structure 10%
- **Step 2 Create Prod Scope** (has_bash_commands) — content 70%, bash 20%, structure 10%
- **Step 3 Register Keys Dev** (has_bash_commands, has_key_inventory) — content 55%, bash 20%, key inventory 15%, structure 10%
- **Step 4 Register Keys Prod** (has_bash_commands, has_key_inventory) — content 55%, bash 20%, key inventory 15%, structure 10%
- **Step 5 Verify** (has_python_code, has_verification_step) — content 55%, python 15%, verification 20%, structure 10%
- **Step 6 Rotation** — content 90%, structure 10%
- **Reference** (has_key_inventory) — content 75%, key inventory 15%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

| Sub-criterion | Weight | Checks |
|---|---|---|
| Runbook / guide name in H1 | 35% | H1 title clearly names the runbook and/or product |
| Task ID / traceability tag present | 30% | Tag like `_TASK-ENV-002_` or equivalent |
| Catalog / scope reference | 20% | Catalog name (e.g., `globalsales`) or scope name mentioned in header block |
| Author / generated date present | 15% | Author, version, or created date before first `##` |

---

#### Content Completeness Sub-Formula (all sections)

```
score = (topics_covered / reference_topic_count) × 55%
      + (details_are_specific_and_complete / total_reference_details) × 30%
      + (section_intro_paragraph_present) × 15%
```

Where:
- `topics_covered`: count of participant items addressing the same operational topic as a reference item (cross-product: different scope names, key names, catalog names acceptable — same functional intent required; e.g., `globalsales` scope ≡ `globalpurchase-dev` scope)
- `details_are_specific_and_complete`: participant items providing concrete values (scope names, key names, CLI flags, notebook paths) rather than vague instructions or unresolved placeholders
- `section_intro_paragraph_present`: a sentence or paragraph above the first code block or list explaining when or why to perform this step

---

#### Bash Commands Sub-Formula (when criterion is scored)

```
score = (bash_blocks_present) × 35%
      + (commands_target_product_scope_or_keys) × 35%
      + (commands_are_executable) × 30%
```

Where:
- `bash_blocks_present`: at least one fenced bash/shell code block exists in the section
- `commands_target_product_scope_or_keys`: CLI commands reference the participant's own scope/catalog (e.g., `--scope globalsales`) not the reference scope (`globalpurchase-dev`)
- `commands_are_executable`: commands are syntactically complete — no missing mandatory flags, no unresolved `{{placeholder}}` substitutions (intentional `<variable>` substitutions are acceptable)

---

#### Python Code Sub-Formula (when criterion is scored)

```
score = (python_block_present) × 40%
      + (code_uses_product_scope) × 35%
      + (code_is_syntactically_complete) × 25%
```

Where:
- `python_block_present`: at least one fenced Python code block exists in the section
- `code_uses_product_scope`: Python code references the participant's own scope name (e.g., `"globalsales"`) rather than the reference scope
- `code_is_syntactically_complete`: Python snippet has no syntax errors and no unresolved `{{placeholder}}` substitutions

---

#### Key Inventory Sub-Formula (when criterion is scored)

```
score = (key_list_or_table_present) × 35%
      + (keys_covered / reference_key_count) × 40%
      + (key_purposes_documented) × 25%
```

Where:
- `key_list_or_table_present`: section contains a list or table enumerating specific secret key names
- `keys_covered`: count of participant key names that address the same functional credential type as reference keys (cross-product: `source_jdbc_url` ≡ `jdbc_url`; `source_jdbc_user` ≡ `jdbc_username`)
- `key_purposes_documented`: each key has a description of what it is used for (not just the key name alone)

---

#### Verification Step Sub-Formula (when criterion is scored)

```
score = (verification_command_present) × 40%
      + (verification_is_non_revealing) × 35%
      + (expected_output_or_context_explained) × 25%
```

Where:
- `verification_command_present`: section contains a command to list or inspect registered keys (e.g., `dbutils.secrets.list(...)` or `databricks secrets list`)
- `verification_is_non_revealing`: the command lists key names only — it does not call `dbutils.secrets.get(...)` or print actual secret values
- `expected_output_or_context_explained`: the section explains what a successful verification looks like (expected key names, comment about values never being exposed)

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
- `section_intro_or_context_present`: a sentence or paragraph before the first code block or list
- `appropriate_formatting_for_content_type`: CLI commands use bash code blocks, Python uses python code blocks, key lists use tables or bullet lists
- `code_blocks_properly_fenced_if_present`: if CLI or Python commands present, they are inside fenced code blocks with a language tag

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No bash/CLI code blocks anywhere in document | −4 pts | Skip if `doc_has_bash_commands` is true |
| No scope creation command anywhere | −4 pts | Skip if `doc_has_scope_creation` is true |
| No key registration command anywhere | −4 pts | Skip if `doc_has_key_registration` is true |
| No verification step anywhere | −4 pts | Skip if `doc_has_verification` is true |
| No dev/prod scope separation documented | −3 pts | Skip if `doc_has_dev_prod_separation` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| Hardcoded credentials found in any code block | −5 pts | Applied if `doc_has_hardcoded_credentials` is true |
| ACL/GRANT command uses only `{{placeholder}}` for principal | −2 pts | Only if ACL command block exists |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/secrets-setup/TASK-SEC-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/secrets-setup/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-SEC-001
skill: task-checker-secrets-setup
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-SEC-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<resolved participant path>`
**Reference file:** `<resolved reference path>`
**Generated:** <today's date YYYY-MM-DD>

---

## Score Summary

**Secrets Setup Score: <total>/100**

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
| No bash/CLI code blocks anywhere | −4 pts | Yes/No — reason |
| No scope creation command anywhere | −4 pts | Yes/No — reason |
| No key registration command anywhere | −4 pts | Yes/No — reason |
| No verification step anywhere | −4 pts | Yes/No — reason |
| No dev/prod scope separation | −3 pts | Yes/No — reason |
| Missing H2 section | −5 pts each (max −15) | Yes/No — list |
| Hardcoded credentials in code block | −5 pts | Yes/No — reason |
| ACL command placeholder only | −2 pts | Yes/No — reason |

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
| 45–59 | Needs work | Missing scope creation, key registration, or verification absent |
| 0–44 | Incomplete | Major steps absent or no CLI commands documented |

---

*Report generated by skill 31-migvisor-task-checker-secrets-setup on <date>*
```

---

### Step 10 — Surface Summary in Conversation

After writing the report, output the following console block directly in the conversation:

```
╔══════════════════════════════════════════════════════════════════════╗
║  TASK-SEC-001  •  Secrets Setup  •  <product name>                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  <total> / 100  —  <grade>                                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

Then write a **5–6 sentence plain-English verdict** covering:
1. What the participant did well (strongest 1–2 sections with specific detail)
2. The main structural or content gap (most impactful missing or weak section)
3. A second significant gap (second priority issue)
4. **The numeric score** — sentence 4 must state the total score as a number (e.g., "The secrets setup document scores 54/100 (Needs Work).")
5. Top priority fix and estimated point recovery
6. Secondary fix or overall recommendation

Keep each sentence factual and specific to the participant's document — no generic praise.
