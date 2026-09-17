# Skill: task-checker-bi-connections

## Identity

| Field | Value |
|---|---|
| Skill number | 30 |
| Skill name | task-checker-bi-connections |
| Task ID | TASK-BI-001 |
| Output file | `checks/<trainee_name>/bi-connections/TASK-BI-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check bi connections"
- "check my bi connections"
- "validate bi connections"
- "score bi connections"
- "compare bi connections"
- "check bi_connections"
- "run task-checker-bi-connections"
- "run 30-migvisor-task-checker-bi-connections"
- "30"

---

## Invocation Syntax

```
/task-checker-bi-connections
/task-checker-bi-connections participant=<path> reference=<path> trainee=<name>
run task-checker-bi-connections
run 30-migvisor-task-checker-bi-connections
```

---

## Preconditions

- A participant `bi_connections.md` file must exist (default: `trainees/<trainee_name>/bi_connections.md`)
- A reference `bi_connections.md` file must exist (default: `reference/bi_connections.md`)
- The `checks/<trainee_name>/bi-connections/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/bi_connections.md` | `participant=` |
| Reference | `reference/bi_connections.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/bi_connections.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/bi_connections.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `bi_connections.md` in workspace root

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags.
2. Otherwise run auto-detection above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] bi_connections.md.
   Provide an explicit path: /task-checker-bi-connections participant=<path>
   ```
5. Read both files in full.
6. Extract document metadata from each file (lines before the first `##`):
   - Product name / guide title (H1 title)
   - Task ID tag if present
   - Catalog / schema reference if mentioned

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — reference has 5 H2 headings:
- N = 6
- Section list: Header Metadata, 1. Overview, 2. Connection Details per Mart View, 3. Connecting BI Tools, 4. Known Issues and Workarounds, 5. Access Provisioning

**Cross-section matching** — participant may use different section titles or restructure. Match by functional role:

| Reference section | Participant equivalent examples |
|---|---|
| Overview | Introduction, background, purpose, about this guide |
| Connection Details per Mart View | BI report connections, view connections, report list, per-view endpoint, mart view details, view inventory |
| Connecting BI Tools | SQL Warehouse connection string, connection setup, endpoint configuration, connecting to Databricks |
| Known Issues and Workarounds | Known issues, troubleshooting, caveats, common problems, FAQ |
| Access Provisioning | Access setup, grant targets, permissions, GRANT SQL, access provisioning, security setup |

**Multiple sections covering one reference section:** If the participant spreads one reference section across multiple sections (e.g., separate "Connection string" and "Power BI steps" both mapping to "Connecting BI Tools"), score both together as a single matched section — use the combined content to evaluate the reference section's criteria.

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. Connection Details per Mart View — most complex: H3 per-view subsections, attribute tables, SQL sample queries, multiple views
2. Connecting BI Tools — connection string block, numbered BI tool steps, multiple tool types
3. Known Issues and Workarounds — issue/workaround table, cross-reference to other docs
4. Access Provisioning — bullet list, contact info, role/principal details
5. Overview — intro paragraph only
6. Header Metadata — simplest

Distribute remainder points to the top-ranked sections (2 pts each to top sections) until remainder is exhausted.

**Example with N=6:** base_weight=16, remainder=4 → Connection Details gets 18 pts, Connecting BI Tools gets 18 pts, all others get 16 pts.

---

### Step 4 — Classify Section Content Types

For each `##` section in the **reference** file, detect:

| Flag | True when |
|---|---|
| `has_attribute_table` | Section contains a Markdown table with per-view configuration attributes (Unity Catalog path, Object type, Service principal, Minimum privilege, Refresh/Real-time) |
| `has_connection_string` | Section contains a connection string block listing Server hostname, HTTP path, Authentication, Catalog, and Schema fields |
| `has_bi_tool_steps` | Section contains a numbered list of steps for connecting a BI tool (Power BI, Tableau, or similar) |
| `has_issues_table` | Section contains a Markdown table with at least Issue and Workaround columns |
| `has_sql_sample` | Section contains a fenced SQL code block presented as a sample or example query |
| `has_numbered_steps` | Section contains an ordered numbered list as the primary instruction format |
| `has_subsections` | Section contains `###` H3 subheadings |

Also detect at **document level**:
- `doc_has_attribute_tables`: any per-view attribute tables exist
- `doc_has_connection_string`: any connection string block exists
- `doc_has_bi_tool_steps`: any numbered BI tool steps exist
- `doc_has_issues_table`: any known issues table exists
- `doc_has_access_provisioning`: any access provisioning or GRANT SQL section exists
- `doc_has_contact_info`: any email address or named contact / team appears in the document

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (15 if has_attribute_table else 0)
  − (20 if has_connection_string else 0)
  − (15 if has_bi_tool_steps else 0)
  − (20 if has_issues_table else 0)
  − 10   ← structure, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Attribute Table | 15% | `has_attribute_table` in reference section |
| Connection String | 20% | `has_connection_string` in reference section |
| BI Tool Steps | 15% | `has_bi_tool_steps` in reference section |
| Issues Table | 20% | `has_issues_table` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**
- **Header Metadata** — content 90%, structure 10%
- **Overview** — content 90%, structure 10%
- **Connection Details per Mart View** (has_attribute_table) — content 75%, attribute table 15%, structure 10%
- **Connecting BI Tools** (has_connection_string, has_bi_tool_steps) — content 55%, connection string 20%, BI steps 15%, structure 10%
- **Known Issues and Workarounds** (has_issues_table) — content 70%, issues table 20%, structure 10%
- **Access Provisioning** — content 90%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

| Sub-criterion | Weight | Checks |
|---|---|---|
| Guide / product name in H1 | 35% | H1 title clearly names the product or guide |
| Task ID / traceability tag present | 30% | Tag like `_TASK-MART-004_` or equivalent reference |
| Catalog / schema reference | 20% | Catalog name (e.g., `globalsales`) or platform (Databricks) mentioned in header |
| Author / generated date present | 15% | Author, created date, or version tag appears before first `##` |

---

#### Content Completeness Sub-Formula (all sections)

For each section, content completeness measures **functional topic coverage**:

```
score = (topics_covered / reference_topic_count) × 55%
      + (details_are_specific_and_complete / total_reference_details) × 30%
      + (section_intro_paragraph_present) × 15%
```

Where:
- `topics_covered`: count of participant items that address the same functional topic as a reference item (cross-product: different view names, catalog names, SP names are acceptable — same functional intent required; e.g., "SELECT on globalsales.mart.v_sales" ≡ "SELECT on globalpurchase.mart.v_purchase_by_supplier")
- `details_are_specific_and_complete`: participant items that provide concrete values (UC paths, SP names, privilege levels, URLs, email addresses) rather than vague placeholders or omissions
- `section_intro_paragraph_present`: a sentence or paragraph above the first table/list/code block that explains the purpose of this section

---

#### Attribute Table Sub-Formula (when criterion is scored)

```
score = (attribute_table_present) × 35%
      + (required_rows_covered / reference_row_count) × 35%
      + (values_are_concrete_not_placeholder) × 30%
```

Where:
- `attribute_table_present`: section contains a Markdown table with at least two columns for per-view configuration attributes
- `required_rows_covered`: count of participant table rows that map to reference rows (Unity Catalog path, Object type, Service principal, Minimum privilege, Refresh/Real-time) — cross-product equivalents allowed
- `values_are_concrete_not_placeholder`: attribute cells contain actual values (UC paths, SP names, privilege statements) rather than `<placeholder>`, `TBD`, or blanks

---

#### Connection String Sub-Formula (when criterion is scored)

```
score = (connection_block_present) × 35%
      + (required_fields_present / reference_field_count) × 40%
      + (values_use_participant_catalog) × 25%
```

Where:
- `connection_block_present`: section contains a connection string block (code block or table) listing connection parameters
- `required_fields_present`: count of fields present from: Server hostname, HTTP path, Authentication, Catalog, Schema
- `values_use_participant_catalog`: the Catalog and Schema fields reference the participant's own catalog/schema (e.g., `globalsales` / `mart`) not the reference catalog (`globalpurchase`)

---

#### BI Tool Steps Sub-Formula (when criterion is scored)

```
score = (bi_steps_present) × 40%
      + (tools_covered / reference_tool_count) × 35%
      + (steps_are_actionable) × 25%
```

Where:
- `bi_steps_present`: section contains a numbered or bulleted list of steps for connecting a BI tool
- `tools_covered`: count of BI tools (Power BI, Tableau, etc.) for which connection steps are provided
- `steps_are_actionable`: steps reference specific UI elements, menu paths, or field values rather than vague instructions ("open Power BI" without further detail)

---

#### Issues Table Sub-Formula (when criterion is scored)

```
score = (issues_table_present) × 40%
      + (issues_covered / reference_issue_count) × 35%
      + (each_entry_has_concrete_workaround) × 25%
```

Where:
- `issues_table_present`: section contains a Markdown table with at least Issue and Workaround columns
- `issues_covered`: count of participant issue rows that address the same functional problem as reference entries (stale MV data, ACCESS DENIED, etc.) — cross-product equivalents allowed
- `each_entry_has_concrete_workaround`: each table row's workaround cell describes a specific step or command rather than "contact support" or "try again"

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
- `section_intro_or_context_present`: a sentence or paragraph before the first list/table/code block explains the purpose of this section
- `appropriate_formatting_for_content_type`: tables use Markdown table syntax, connection strings use code blocks, steps use numbered lists
- `code_blocks_properly_fenced_if_present`: if SQL or connection strings are present, they are inside fenced code blocks with a language tag

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No per-view attribute tables anywhere in document | −4 pts | Skip if `doc_has_attribute_tables` is true |
| No connection string block anywhere in document | −4 pts | Skip if `doc_has_connection_string` is true |
| No known issues or troubleshooting section anywhere | −4 pts | Skip if `doc_has_issues_table` is true |
| No access provisioning contact info anywhere | −3 pts | Skip if `doc_has_contact_info` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| GRANT SQL present but uses only `{{placeholder}}` values with no concrete SP/role names | −2 pts | Only if GRANT SQL block exists |
| Connection string uses reference catalog/schema instead of participant's own | −2 pts | Only if connection string block exists |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/bi-connections/TASK-BI-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/bi-connections/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-BI-001
skill: task-checker-bi-connections
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-BI-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<resolved participant path>`
**Reference file:** `<resolved reference path>`
**Generated:** <today's date YYYY-MM-DD>

---

## Score Summary

**BI Connections Score: <total>/100**

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
| No per-view attribute tables anywhere | −4 pts | Yes/No — reason |
| No connection string block anywhere | −4 pts | Yes/No — reason |
| No known issues section anywhere | −4 pts | Yes/No — reason |
| No access provisioning contact info | −3 pts | Yes/No — reason |
| Missing H2 section | −5 pts each (max −15) | Yes/No — list |
| GRANT SQL placeholder only | −2 pts | Yes/No — reason |
| Connection string uses wrong catalog | −2 pts | Yes/No — reason |

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
| 45–59 | Needs work | Missing per-view attribute tables, connection string, or known issues absent |
| 0–44 | Incomplete | Major sections absent or BI connection details not documented |

---

*Report generated by skill 30-migvisor-task-checker-bi-connections on <date>*
```

---

### Step 10 — Surface Summary in Conversation

After writing the report, output the following console block directly in the conversation:

```
╔══════════════════════════════════════════════════════════════════════╗
║  TASK-BI-001  •  BI Connections  •  <product name>                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  <total> / 100  —  <grade>                                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

Then write a **5–6 sentence plain-English verdict** covering:
1. What the participant did well (strongest 1–2 sections with specific detail)
2. The main structural or content gap (most impactful missing or weak section)
3. A second significant gap (second priority issue)
4. **The numeric score** — sentence 4 must state the total score as a number (e.g., "The BI connections document scores 58/100 (Needs Work).")
5. Top priority fix and estimated point recovery
6. Secondary fix or overall recommendation

Keep each sentence factual and specific to the participant's document — no generic praise.
