# Skill: task-checker-go-live-checklist

## Identity

| Field | Value |
|---|---|
| Skill number | 27 |
| Skill name | task-checker-go-live-checklist |
| Task ID | TASK-GL-001 |
| Output file | `checks/<trainee_name>/go-live/TASK-GL-001_check_report.md` |

---

## Trigger Phrases

This skill activates on any of:

- "check go live checklist"
- "check go-live checklist"
- "validate go live checklist"
- "score go live checklist"
- "compare go live checklist"
- "check my go live checklist"
- "run task-checker-go-live-checklist"
- "run 27-migvisor-task-checker-go-live-checklist"
- "27"

---

## Invocation Syntax

```
/task-checker-go-live-checklist
/task-checker-go-live-checklist participant=<path> reference=<path> trainee=<name>
run task-checker-go-live-checklist
run 27-migvisor-task-checker-go-live-checklist
```

---

## Preconditions

- A participant `go_live_checklist.md` file must exist (default: `trainees/<trainee_name>/go_live_checklist.md`)
- A reference `go_live_checklist.md` file must exist (default: `reference/go_live_checklist.md`)
- The `checks/<trainee_name>/go-live/` directory must exist (create it if absent)

---

## Input Inventory

| Role | Default path | Override key |
|---|---|---|
| Participant | `trainees/<trainee_name>/go_live_checklist.md` | `participant=` |
| Reference | `reference/go_live_checklist.md` | `reference=` |

Auto-detection fallback order for participant:
1. If `trainee=<name>` provided: `trainees/<name>/go_live_checklist.md`
2. Scan `trainees/` for subdirectories:
   - Exactly 1: use `trainees/<that-name>/go_live_checklist.md`; record `<that-name>` as the trainee name
   - 0 or 2+: abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Fallback: `go_live_checklist.md` in workspace root

---

## Workflow

### Step 1 — Resolve Files

1. Apply override paths if provided via `participant=` / `reference=` flags.
2. Otherwise run auto-detection above. If multiple `trainees/` subdirectories are found and no `trainee=` flag is given, abort with: *"Multiple trainee folders found: [list]. Specify with `trainee=<name>`."*
3. Record the resolved trainee name (`trainees/<name>/...` → `<name>`; use `unknown_trainee` if not under `trainees/`).
4. If either file cannot be resolved, abort with:
   ```
   ERROR: Could not locate [participant|reference] go_live_checklist.md.
   Provide an explicit path: /task-checker-go-live-checklist participant=<path>
   ```
5. Read both files in full.
6. Extract document metadata from each file (lines before the first `##`):
   - Product name (H1 title)
   - Total checklist item count (count of `- [ ]` and `- [x]` lines)
   - Closing readiness statement (last non-empty line)

---

### Step 2 — Detect Sections

Build the scored section list from the **reference** file:

1. Always add **Header Metadata** as section 0 (covers lines before the first `##` heading).
2. For each `## ` H2 heading in the reference file, add a section entry. Record the title exactly as written.
3. Result: N scored sections = 1 (Header Metadata) + count of `##` headings in reference.

**Example** — if reference has 7 H2 headings (1. Infrastructure, 2. Data, 3. Security, 4. Pipeline, 5. Data Quality, 6. BI, 7. Documentation):
- N = 8
- Section list: Header Metadata, 1. Infrastructure, 2. Data, 3. Security, 4. Pipeline, 5. Data Quality, 6. BI, 7. Documentation

**Cross-product section matching** — the participant may use different H2 titles for equivalent functional areas. Match by semantic equivalence:

| Reference section | Participant equivalent examples |
|---|---|
| Infrastructure | Infrastructure, Environment Setup, Platform Setup, Catalog & Schemas, Cluster Setup |
| Data | Data, Data Bootstrap, Seed Data, Initial Data Load, Bootstrap Data, Reference Data |
| Security | Security, Access Control, Permissions, Grants & Secrets, IAM, RBAC |
| Pipeline | Pipeline, Workflow, ETL, Orchestration, Deployment, Job Deployment |
| Data Quality | Data Quality, DQ, Quality Checks, Quality Assertions, DQ Rules |
| BI | BI, Reporting, Mart Access, Power BI, BI Layer, Dashboards |
| Documentation | Documentation, Docs, Runbooks, Handover, Knowledge Transfer |
| (any other reference H2) | Semantic match by topic |

Record both the reference section title and the matched participant title (or `[MISSING]` if no equivalent found).

---

### Step 3 — Calculate Section Weights

```
base_weight = floor(100 / N)
remainder   = 100 − (base_weight × N)
```

**Complexity ranking** (highest → lowest) for remainder distribution:

1. Security — most complex: GRANT tasks, PII/credential checks, secret scopes, service principal verification with specific permission scopes
2. Data Quality — DQ assertion config, severity level verification, rejection table, synthetic failure test
3. Pipeline — workflow deployment, schedule verification, end-to-end manual trigger, lineage status, watermark advancement
4. Data — dimension table bootstrap, sentinel rows, staging initialization, cutoff table seeding
5. Infrastructure — catalog, schemas, cluster policy, workflow deployment, alerting
6. BI — mart view accessibility, connection strings, sample query verification
7. Documentation — doc file review and distribution to stakeholders
8. Header Metadata — simplest

Distribute 1 extra point per section to the top-ranked sections until remainder is exhausted.

**Example** (N=8, base=12, remainder=4):
- Security → 13 pts
- Data Quality → 13 pts
- Pipeline → 13 pts
- Data → 13 pts
- Infrastructure → 12 pts
- BI → 12 pts
- Documentation → 12 pts
- Header Metadata → 12 pts

---

### Step 4 — Classify Section Content Types

For each section in the **reference** and **participant** files, detect:

| Flag | True when |
|---|---|
| `has_checkbox_items` | Section contains `- [ ]` or `- [x]` formatted checklist items |
| `has_task_id_refs` | One or more items reference specific task IDs (CFG-*, DB-*, GRANT-*, DQR-*, TEST-*, etc.) |
| `has_specific_names` | Items name specific tables, notebooks, config files, or catalog/schema paths |
| `has_verification_step` | Section includes at least one "test", "verify", "confirm", or "check passes" item |
| `has_principal_names` | Items name specific service principals, user groups, or roles |
| `has_dq_severity_labels` | Items state severity levels (BLOCKING, Informational, or equivalent) |
| `has_synthetic_test` | Section includes an injected-failure or synthetic error test item |
| `has_secret_items` | Section references secrets scopes, secret keys, or credential registration |
| `has_distribution_items` | Section includes items for distributing or handing over documents/credentials |

Also detect at **document level**:
- `doc_has_checkboxes`: any `- [ ]` or `- [x]` items exist
- `doc_has_task_refs`: any task ID references exist
- `doc_has_verification`: any test/verify items exist
- `doc_has_security_items`: any security, credential, or access control items exist
- `doc_has_closing_statement`: document ends with a readiness/sign-off statement

---

### Step 5 — Build Adaptive Criteria per Section

For each section, derive criterion weights based on what the **reference** section contains:

```
content_pct = 100
  − (20 if has_task_id_refs else 0)
  − (15 if has_verification_step else 0)
  − (15 if has_principal_names else 0)
  − 10   ← structure/conventions, always present
minimum content_pct = 25%
```

The resulting criteria set for a section:

| Criterion | Weight | Active when |
|---|---|---|
| Content completeness | `content_pct` | Always |
| Structure | 10% | Always |
| Task ID references | 20% | `has_task_id_refs` in reference section |
| Verification step | 15% | `has_verification_step` in reference section |
| Principal names | 15% | `has_principal_names` in reference section |

**Note**: use the **reference** section's flags to decide which criteria are scored; use the **participant** section to evaluate how well each criterion is met.

**Section-specific examples:**

- **Header Metadata** — content 90%, structure 10%
- **Infrastructure** (has task_id_refs) — content 70%, task refs 20%, structure 10%
- **Data** (has task_id_refs, has verification_step) — content 55%, task refs 20%, verification 15%, structure 10%
- **Security** (has task_id_refs, has verification_step, has principal_names) — content 40%, task refs 20%, verification 15%, principals 15%, structure 10%
- **Pipeline** (has task_id_refs, has verification_step) — content 55%, task refs 20%, verification 15%, structure 10%
- **Data Quality** (has task_id_refs, has verification_step) — content 55%, task refs 20%, verification 15%, structure 10%
- **BI** (has task_id_refs, has verification_step) — content 55%, task refs 20%, verification 15%, structure 10%
- **Documentation** (has specific_names) — content 90%, structure 10%

---

### Step 6 — Score Each Section

#### Header Metadata

Evaluate against the reference header fields:

| Sub-criterion | Weight | Checks |
|---|---|---|
| Product name in H1 | 40% | H1 title present and names the product |
| Item count stated or derivable | 20% | Total checklist items countable; dense enough for production readiness |
| Closing readiness statement | 40% | Document ends with a sign-off / readiness declaration |

Score = weighted sum of sub-criteria, each rated 0–100%.

---

#### Content Completeness Sub-Formula (all sections)

For a checklist section, content completeness measures **functional topic coverage**:

```
score = (topics_covered / reference_item_count) × 70%
      + (items_use_checkbox_format / total_items) × 30%
```

Where:
- `topics_covered`: count of participant items that address the same functional topic as a reference item (cross-product: participant may use different table/task names; topic must match, e.g., "dim sentinel row inserted" ≡ "seed dimension default row")
- `items_use_checkbox_format`: participant items formatted as `- [ ]` or `- [x]`

---

#### Task ID References Sub-Formula (when criterion is scored)

```
score = (items_with_task_id_refs / total_items) × 60%
      + (task_ids_are_specific / items_with_task_id_refs) × 40%
```

Where:
- `items_with_task_id_refs`: items that include at least one task ID (e.g., DB-007, CFG-003, GRANT-001, DQR-004)
- `task_ids_are_specific`: referenced IDs are specific task codes (not just "see task list")

---

#### Verification Step Sub-Formula (when criterion is scored)

```
score = (has_manual_trigger_or_test_item) × 40%
      + (has_success_indicator_item) × 35%
      + (has_failure_test_item) × 25%
```

Where:
- `has_manual_trigger_or_test_item`: at least one item explicitly tests or manually triggers the component
- `has_success_indicator_item`: at least one item verifies a positive outcome (status=success, query returns results, etc.)
- `has_failure_test_item`: at least one item deliberately introduces a failure and verifies the system detects it (e.g., synthetic DQ mismatch, negative permission test)

---

#### Principal Names Sub-Formula (when criterion is scored)

```
score = (items_naming_principals / items_requiring_principal_check) × 50%
      + (principals_have_permission_scopes / named_principals) × 30%
      + (negative_permission_test_present) × 20%
```

Where:
- `items_naming_principals`: items that name specific service principals or user groups (not just "users have access")
- `principals_have_permission_scopes`: named principals have their allowed operations specified (SELECT, MODIFY, REFRESH, etc.)
- `negative_permission_test_present`: at least one item verifies that a principal cannot do something it should not (e.g., `bi-service-principal` cannot MODIFY)

---

#### Structure Sub-Formula (all sections)

```
score = (h2_present) × 30%
      + (all_items_are_checkboxes) × 40%
      + (items_are_actionable_imperatives) × 30%
```

Where:
- `h2_present`: section has a `##` heading
- `all_items_are_checkboxes`: every item uses `- [ ]` or `- [x]` format (not plain bullet points or numbered lists)
- `items_are_actionable_imperatives`: items start with an imperative verb or describe a state to verify (not vague descriptions)

---

#### Section-Specific Scoring Notes

**Infrastructure:**
- Equivalent topics to look for: catalog created, schemas created, cluster/compute policy, workflow/job deployed and scheduled, alerting configured
- Cross-product: different catalog names (e.g., `globalorders` vs `globalpurchase`) are equivalent

**Data:**
- Equivalent topics: date/calendar dimension populated, dimension sentinel/default rows inserted, staging tables initialized empty, watermark/cutoff table seeded, fact table ready for MERGE
- Cross-product: sentinel row concept and initialization pattern scored by presence, not identical table names

**Security:**
- Equivalent topics: GRANT tasks applied, PII/credential compliance check, secrets scopes and keys registered, service principal read access verified, service principal write access verified, negative permission test
- Cross-product: different principal names (e.g., `sales-etl-sp` vs `etl-service-principal`) are equivalent

**Pipeline:**
- Equivalent topics: workflow deployment script executed, workflow visible in orchestration UI, manual end-to-end test run, lineage/run status verified as success, watermark advanced after test run
- Cross-product: different workflow tool names (Databricks Workflows, ADF, Airflow) are equivalent

**Data Quality:**
- Equivalent topics: DQ config loaded, blocking severity rules enabled, informational severity rules enabled, smoke tests pass, rejection table exists and writable, synthetic failure test performed
- Cross-product: DQR IDs, blocking/informational rule counts, and config file names will differ

**BI:**
- Equivalent topics: mart views queryable by BI principal, BI user group can SELECT, connection strings updated, sample queries return expected results
- Cross-product: different mart view names, BI tool names, and group names are equivalent

**Documentation:**
- Equivalent topics: architecture diagram reviewed, data dictionary covers all tables, runbook distributed to ops team, secrets/credentials docs available to platform team, BI connection docs distributed to BI consumers
- Cross-product: different file paths and team names are equivalent

---

### Step 7 — Apply Auto-Deducts

Calculate global penalties after all section scores are summed:

| Condition | Penalty | Notes |
|---|---|---|
| No checkbox items anywhere in document | −5 pts | Skip if `doc_has_checkboxes` is true |
| Missing H2 section present in reference but absent in participant | −5 pts each | Max −15 pts total |
| No task ID references anywhere in document | −4 pts | Skip if `doc_has_task_refs` is true |
| No verification or test items anywhere in document | −3 pts | Skip if `doc_has_verification` is true |
| No security or access control items anywhere | −3 pts | Skip if `doc_has_security_items` is true |
| Items in a section are written as descriptions, not actions (≥ 50% of items lack imperative verbs or verifiable states) | −2 pts per section | Max −6 pts total |
| No closing readiness or sign-off statement | −1 pt | Skip if `doc_has_closing_statement` is true |

Compute:
```
subtotal     = sum of all section weighted scores
auto_deducts = sum of applicable penalties (negative)
total_score  = max(subtotal + auto_deducts, 0)
```

---

### Step 8 — Resolve Output Path

1. Extract the trainee name from the participant file path: `trainees/<name>/...` → `<name>`. If not under `trainees/`, use `unknown_trainee`.
2. Base path: `checks/<trainee_name>/go-live/TASK-GL-001_check_report.md`
3. If the path does not exist → use it.
4. If it exists → increment suffix: `_v2`, `_v3`, … until a free path is found.
5. Never overwrite an existing report.

Create `checks/<trainee_name>/go-live/` directory if it does not exist.

---

### Step 9 — Write Check Report

Write the report to the resolved output path using this template:

```markdown
---
task_id: TASK-GL-001
skill: task-checker-go-live-checklist
participant_file: <resolved participant path>
reference_file: <resolved reference path>
product: <participant product name>
generated: <today's date YYYY-MM-DD>
total_score: <N>/100
grade: <grade label>
---

# TASK-GL-001 Check Report

**Product:** <participant product name>
**Reference:** <reference product name>
**Participant file:** `<path>`
**Reference file:** `<path>`
**Generated:** <today's date>

---

## Score Summary

**The go-live checklist Score: <total>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header) | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| <Section 2> | <ref title> | <W> | <S>/100 | <pts> | ✓/⚠/✗ |
| ... | | | | | |
| **Subtotal** | | | | **<subtotal>** | |
| Auto-deducts | | | | **<deducts>** | |
| **Total** | | | | **<total>/100** | |

**Grade: <grade>**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| <ref title> | <participant title> or [MISSING] | exact / semantic / missing |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| <condition> | −<N> pts | <Yes/No — reason> |

---

## Section Feedback

### Header Metadata (<weighted_score>/<weight> pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

**Improvement items:**
- [ ] <specific action>

---

### <Reference Section> → participant: <matched title> (<weighted_score>/<weight> pts)

**Criteria scored:** Content (<pct>%)[, Task ID References (20%)][, Verification Step (15%)][, Principal Names (15%)], Structure (10%)

**Content completeness (<score>/100):**
- Topics covered: <N>/<ref_item_count>
- Items in checkbox format: <N>/<total> (<pct>%)
- Key covered topics: <list>
- Key missing topics: <list>

**Task ID references (<score>/100):** *(if applicable)*
- Items with task ID refs: <N>/<total>
- Task IDs are specific: Yes/No

**Verification step (<score>/100):** *(if applicable)*
- Manual trigger / test item present: Yes/No
- Success indicator item present: Yes/No
- Failure/negative test item present: Yes/No

**Principal names (<score>/100):** *(if applicable)*
- Items naming specific principals: <N>/<items requiring principals>
- Principals have permission scopes: Yes/No
- Negative permission test present: Yes/No

**Structure (<score>/100):**
- H2 present: Yes/No
- All items are checkboxes: Yes/No
- Items are actionable imperatives: Yes/No

**Strengths:**
- <bullet>

**Gaps:**
- <bullet>

**Improvement items:**
- [ ] <specific action>

---

## Extra Sections (participant-only, not in reference)

- **<section title>** — <brief description>. No score impact.

---

## Improvement Items

List all identified gaps as actionable items, ordered by impact (highest first):

1. **[Section — Criterion]** <specific action> → up to +<N> pts
2. ...

---

## Priority Actions

Top 3–5 changes that will have the greatest score impact:

1. <action> → up to +<N> pts
2. ...

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing sections, no task refs, or no verification items |
| 0–44 | Incomplete | Major sections absent or no checkbox format used |
```

Status icons: ✓ = scored ≥ 70% of weight, ⚠ = 40–69%, ✗ = < 40%.

---

### Step 10 — Surface Summary to Console

After writing the report, output to the conversation:

```
╔══════════════════════════════════════════════════════════╗
║  TASK-GL-001  Go-Live Checklist Check                    ║
║  Product : <participant product>                         ║
║  Score   : <total>/100   Grade: <grade>                  ║
║  Report  : checks/<trainee_name>/go-live/TASK-GL-001_check_report<suffix>.md ║
╚══════════════════════════════════════════════════════════╝
```

Then write exactly 5–6 sentences of plain-English verdict following these rules:

1. **Sentence 1** — overall quality and what the participant did well (strongest section or criterion).
2. **Sentence 2** — the single most impactful gap (the section or criterion that lost the most points).
3. **Sentence 3** — structural observation: how well the participant's sections map to the reference, checkbox format consistency, and whether extra sections add value.
4. **Sentence 4** — state the final score explicitly: "The go-live checklist scores **<total>/100** (<grade>)" and identify the next most important fix.
5. **Sentence 5** — the single highest-value actionable change the participant should make before resubmitting.
6. **Sentence 6** *(optional)* — note any extra sections or outstanding depth that goes beyond the reference scope.

Do **not** exceed 6 sentences. Do **not** use bullet points in the prose verdict. The final score **must appear as a number** in sentence 4.

---

## Score Interpretation

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing sections, no task refs, or no verification items |
| 0–44 | Incomplete | Major sections absent or no checkbox format used |

---

## Cross-Product Evaluation Note

The participant and reference describe **different products** (e.g., participant = Sales_Orders, reference = Purchase). In this case:

- **Do not** penalize for different catalog names, table names, task IDs, config file names, or service principal names.
- **Do** evaluate functional topic coverage: each reference checklist item represents a functional readiness check that should have an equivalent in the participant checklist.
- **Do** evaluate structural patterns: checkbox format, task ID referencing convention, verification step presence, principal-with-scope notation.
- **Do not** penalize for a different number of items per section — score by coverage of equivalent functional topics, not item count match.
- **Do not** penalize for different DQ rule IDs, different mart view names, or different secret key names — score the presence of the pattern (DQ severity documented, mart access verified, secrets registered) not the specific names.
- Content completeness reflects whether the participant has thought through the same readiness concerns for their product, not whether they copied the reference item list.

---

## Notes on Participant Format Variants

Go-live checklist documents may use different organizational formats:

| Participant format | Reference expects | Impact |
|---|---|---|
| Numbered H2 sections (`## 1. Infrastructure`) | Equivalent — semantic match applies | No penalty |
| Unnumbered H2 sections (`## Infrastructure`) | Numbered H2 sections | No penalty |
| `- [x]` checked items | `- [ ]` unchecked items | No penalty — checked items score equally; checked boxes are a bonus (implies self-review) |
| Plain `- ` bullet items (no checkbox) | `- [ ]` checkbox items | Structure criterion reduced; checkbox format sub-criterion scores 0 for that section |
| Numbered list items (`1. `) instead of checkboxes | `- [ ]` checkbox items | Structure criterion reduced; treat as partial checkbox equivalent |
| Combined sections (e.g., Security + Pipeline together) | Separate sections | Score content coverage from the combined section for both reference sections; apply −5 missing-H2 deduct only if content is also absent |
| `[PENDING]` or `{{PLACEHOLDER}}` in items | Specific values | Score item as 50% on specificity sub-criterion — acknowledged deferral better than absent |
| Notes or rationale inline with checklist items | Clean checklist items only | Bonus for clarity; no penalty |
