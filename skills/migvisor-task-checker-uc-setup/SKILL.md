# Skill 34 — task-checker-uc-setup

## Identity

- **Skill number:** 34
- **Skill name:** task-checker-uc-setup
- **Trigger phrases:** "check uc setup", "check my uc setup", "run 34", "run skill 34"
- **Participant file:** `trainees/<trainee_name>/uc_setup.sql`
- **Reference file:** `reference/uc_setup.sql`
- **Output path:** `checks/<trainee_name>/uc-setup/TASK-UC-002_check_report.md`
- **Task ID prefix:** TASK-UC-002

---

## Purpose

Evaluate a Unity Catalog bootstrap SQL script against the reference. The script provisions the top-level catalog and the four medallion schemas (stg, dim, fact, mart) using idempotent `IF NOT EXISTS` guards. It must be safe to re-run and must not contain any destructive or credential-bearing statements.

Catalog/schema names differ between reference (globalpurchase) and participant (e.g. globalsales) — this is expected and never penalised. Commented-out statements are noted but do not trigger auto-deducts unless the placeholder is uncommented and unresolved.

---

## Step 1 — Resolve files

1. Identify the trainee name:
   - If only one subfolder exists under `trainees/`, use it automatically.
   - If multiple exist, use the `trainee=<name>` argument or ask.
2. Set:
   - `participant_file = trainees/<trainee_name>/uc_setup.sql`
   - `reference_file = reference/uc_setup.sql`
3. Read both files fully before scoring.

---

## Step 2 — Detect sections

SQL sections are identified by comment headers and logical SQL block groupings.

**Reference sections (fixed — detect from reference, not from participant):**

| # | Section | Detection rule |
|---|---|---|
| 0 | Header/Preamble | All comment lines before the first SQL statement |
| 1 | Catalog creation | Block containing `CREATE CATALOG` |
| 2 | Schema creation | Block(s) containing `CREATE SCHEMA` statements (all 4 schemas together) |
| 3 | Verification step | Block containing `SHOW SCHEMAS` or a verification comment/query |

**N = 4** sections.

For each reference section, find the best matching participant block by content intent. If no participant block covers a reference section, mark it **[MISSING]**.

---

## Step 3 — Calculate weights

```
N = 4
base_weight = floor(100 / 4) = 25
remainder = 100 − (25 × 4) = 0
→ all sections receive equal weight
```

| Section | Weight |
|---|---|
| Header/Preamble | 25 |
| Catalog creation | 25 |
| Schema creation | 25 |
| Verification step | 25 |
| **Total** | **100** |

---

## Step 4 — Section flags

Detect which features are present in the participant file before scoring:

| Flag | Detection rule |
|---|---|
| `has_if_not_exists_catalog` | `CREATE CATALOG IF NOT EXISTS` present |
| `has_if_not_exists_schemas` | All `CREATE SCHEMA` statements use `IF NOT EXISTS` |
| `has_all_schemas` | All 4 schemas present: stg, dim, fact, mart (or equivalent layer names) |
| `has_catalog_comment` | `COMMENT` string on the `CREATE CATALOG` statement |
| `has_schema_comments` | `COMMENT` string on every `CREATE SCHEMA` statement |
| `has_verification_step` | `SHOW SCHEMAS` or equivalent verification query present (executable or as comment) |
| `has_idempotency_note` | Header comment states script is idempotent or safe to re-run |
| `has_task_id` | Header comment contains a TASK-* or CFG-* traceability tag |
| `has_ownership_placeholder` | Uncommented `ALTER ... OWNER TO` with unresolved `{{...}}` placeholder |

---

## Step 5 — Adaptive criteria per section

Score each section 0–100, then apply the weight.

### Header / Preamble (weight 25)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 60% | Task/CFG ID present, catalog name stated, purpose described, execution context noted |
| `has_idempotency_note` | 20% | Explicit "idempotent" or "safe to re-run" comment |
| `has_task_id` | 10% | TASK-* or CFG-* traceability tag |
| Structure | 10% | Comment block before first SQL statement; clean formatting |

### Catalog creation (weight 25)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 60% | `CREATE CATALOG IF NOT EXISTS` with COMMENT; extra statements (USE CATALOG, commented-out OWNER) acceptable |
| `has_if_not_exists_catalog` | 20% | `IF NOT EXISTS` guard required for idempotency |
| `has_catalog_comment` | 15% | Descriptive COMMENT string on the catalog |
| Structure | 5% | Inline comment before CREATE statement |

### Schema creation (weight 25)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 50% | All 4 schemas created with correct catalog prefix, meaningful COMMENT strings |
| `has_all_schemas` | 25% | stg, dim, fact, mart all present (+6.25 pts each) |
| `has_if_not_exists_schemas` | 15% | All CREATE SCHEMA statements use IF NOT EXISTS |
| `has_schema_comments` | 10% | Every schema has a COMMENT string |

**Note:** Layer labels (Bronze/Silver/Gold) are encouraged and add content value. Commented-out `ALTER SCHEMA OWNER TO` statements are acceptable as forward placeholders — do not penalise if commented.

### Verification step (weight 25)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 70% | Verification present; executable statement preferred over comment-only |
| `has_verification_step` | 20% | `SHOW SCHEMAS IN <catalog>` or equivalent query present |
| Structure | 10% | Inline comment describing what to check |

**Bonus note:** An executable `SHOW SCHEMAS IN <catalog>;` scores higher than a commented-out version — the participant's actual executable statement exceeds the reference in this section.

---

## Step 6 — Auto-deducts

Apply globally after section scoring. Cap at −15 pts total.

| Condition | Penalty | How to detect |
|---|---|---|
| No `IF NOT EXISTS` on `CREATE CATALOG` | −4 pts | `CREATE CATALOG` without `IF NOT EXISTS` |
| Missing `IF NOT EXISTS` on any `CREATE SCHEMA` | −2 pts each (max −8) | Any `CREATE SCHEMA` without `IF NOT EXISTS` |
| Missing any required schema (stg/dim/fact/mart) | −3 pts each (max −12) | Schema absent from file |
| No COMMENT on catalog | −2 pts | `CREATE CATALOG` has no `COMMENT` clause |
| No COMMENTs on schemas | −2 pts | Any `CREATE SCHEMA` missing a `COMMENT` clause |
| No verification step | −3 pts | No `SHOW SCHEMAS` and no verification comment anywhere |
| Hardcoded credential or password value | −5 pts | Literal password, token, or connection string in any statement |
| DROP or REPLACE without IF EXISTS guard | −3 pts | `DROP CATALOG`, `DROP SCHEMA`, `CREATE OR REPLACE` present |
| Unresolved ownership placeholder uncommented | −2 pts | Uncommented `ALTER ... OWNER TO` with `{{...}}` or `<placeholder>` value |

---

## Step 7 — Score calculation

```
weighted_subtotal = Σ (section_raw_score × section_weight / 100)
total = max(0, round(weighted_subtotal − auto_deducts))
```

**Grade scale:**

| Score | Grade |
|---|---|
| 90–100 | Excellent |
| 75–89 | Good |
| 60–74 | Acceptable |
| 45–59 | Needs Work |
| 0–44 | Incomplete |

---

## Step 8 — Write report

Create the output directory if it does not exist: `checks/<trainee_name>/uc-setup/`

Output file: `TASK-UC-002_check_report.md`

If a file already exists at that path, increment the suffix (`_v2`, `_v3`, …) and never overwrite.

**Report structure:**

```markdown
---
task_id: TASK-UC-002
skill: task-checker-uc-setup
participant_file: trainees/<trainee_name>/uc_setup.sql
reference_file: reference/uc_setup.sql
product: <product_name>
generated: <YYYY-MM-DD>
total_score: <N>/100
grade: <grade>
---

# TASK-UC-002 Check Report

**Product:** <product>
**Reference:** Purchase (globalpurchase)
**Participant file:** `trainees/<trainee_name>/uc_setup.sql`
**Reference file:** `reference/uc_setup.sql`
**Generated:** <date>

---

## Score Summary

**UC Setup Score: <N>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 25 | .../100 | ... | ✓/⚠/✗ |
| Catalog creation | CREATE CATALOG | 25 | .../100 | ... | ✓/⚠/✗ |
| Schema creation | CREATE SCHEMA ×4 | 25 | .../100 | ... | ✓/⚠/✗ |
| Verification step | SHOW SCHEMAS | 25 | .../100 | ... | ✓/⚠/✗ |
| **Subtotal** | | | | **...** | |
| Auto-deducts | | | | **−...** | |
| **Total** | | | | **<N>/100** | |

**Grade: <grade>**

> **Weight calculation:** N = 4, base_weight = floor(100/4) = 25, remainder = 0 → all sections receive equal weight of 25 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | ... | Direct / Partial / [MISSING] |
| Catalog creation | ... | ... |
| Schema creation | ... | ... |
| Verification step | ... | ... |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No IF NOT EXISTS on CREATE CATALOG | −4 pts | Yes/No — [reason] |
| Missing IF NOT EXISTS on any CREATE SCHEMA | −2 pts each | Yes/No |
| Missing required schema | −3 pts each | Yes/No |
| No COMMENT on catalog | −2 pts | Yes/No |
| No COMMENTs on schemas | −2 pts | Yes/No |
| No verification step | −3 pts | Yes/No |
| Hardcoded credential value | −5 pts | Yes/No |
| DROP/REPLACE without IF EXISTS | −3 pts | Yes/No |
| Unresolved ownership placeholder uncommented | −2 pts | Yes/No |

**Total auto-deducts: −N pts**

---

## Section Feedback

### Header/Preamble — <raw>/100 (weight 25 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Catalog creation — <raw>/100 (weight 25 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Schema creation — <raw>/100 (weight 25 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Verification step — <raw>/100 (weight 25 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | ... | ... | +N pts |
...

---

## Priority Actions

1. **[Highest-impact fix]** — [description] worth up to **+N pts**.
2. **[Second fix]** — [description] worth up to **+N pts**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs Work | Missing IF NOT EXISTS guards or schemas absent |
| 0–44 | Incomplete | Major sections absent or destructive statements present |

---

*Report generated by skill 34-migvisor-task-checker-uc-setup on <date>*
```

---

## Step 9 — Console summary

After writing the report, output a console verdict in this exact format:

```
╔══════════════════════════════════════════════════════════════════╗
║  TASK-UC-002 · UC Setup · <product> · <date>                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Score: <N>/100 · Grade: <grade>                                 ║
╚══════════════════════════════════════════════════════════════════╝
```

Follow immediately with a **5–6 sentence plain-English verdict**:

1. Overall score and grade in one sentence.
2. What was done well — strongest section or most complete element.
3. The most critical gap — missing guard, absent schema, unresolved placeholder, or missing verification.
4. **Must state the numeric score and name the two highest-priority fixes.**
5. Note any extras the participant added beyond the reference (layer labels, ownership section, USE CATALOG) and their value.
6. Recommendation: proceed to next task or revise first.
