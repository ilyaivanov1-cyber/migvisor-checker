# Skill 33 — task-checker-uc-permission-audit

## Identity

- **Skill number:** 33
- **Skill name:** task-checker-uc-permission-audit
- **Trigger phrases:** "check uc permission audit", "check my uc permission audit", "run 33", "run skill 33"
- **Participant file:** `trainees/<trainee_name>/uc_permission_audit.sql`
- **Reference file:** `reference/uc_permission_audit.sql`
- **Output path:** `checks/<trainee_name>/uc-permission-audit/TASK-UC-001_check_report.md`
- **Task ID prefix:** TASK-UC

---

## Purpose

Evaluate a Unity Catalog permission audit SQL script against the reference. The script is read-only (SHOW GRANTS or information_schema queries) and intended to verify the expected privilege mapping after all GRANT scripts have been applied.

Both `SHOW GRANTS ON <object>` and `information_schema.object_privileges` SELECT queries are accepted as valid approaches — functional equivalence is scored, not syntactic identity. Catalog/schema names differ between reference (globalpurchase) and participant (e.g. globalsales) — this is expected and never penalised.

---

## Step 1 — Resolve files

1. Identify the trainee name:
   - If only one subfolder exists under `trainees/`, use it automatically.
   - If multiple exist, use the `trainee=<name>` argument or ask.
2. Set:
   - `participant_file = trainees/<trainee_name>/uc_permission_audit.sql`
   - `reference_file = reference/uc_permission_audit.sql`
3. Read both files fully before scoring.

---

## Step 2 — Detect sections

SQL sections are identified by comment block headers. In the reference file, sections are marked with `-- ──` box-drawing separators. In participant files, sections may use plain `-- Section name` comment lines or SQL block groupings.

**Reference sections (fixed — detect from reference, not from participant):**

| # | Section | Detection rule |
|---|---|---|
| 0 | Header/Preamble | All lines before the first `-- ──` separator or first SQL statement |
| 1 | Catalog-level audit | Block containing `SHOW GRANTS ON CATALOG` or `WHERE object_type = 'CATALOG'` |
| 2 | Schema-level audit | Block containing `SHOW GRANTS ON SCHEMA` or `WHERE object_type = 'SCHEMA'` |
| 3 | Table-level audit | Block containing `SHOW GRANTS ON TABLE` or `WHERE object_type IN ('TABLE'...)` |
| 4 | Mart/View-level audit | Block containing `SHOW GRANTS ON VIEW` / `SHOW GRANTS ON MATERIALIZED VIEW` or VIEW filter |
| 5 | Principal-to-privilege mapping | Comment block or query that maps principals → objects → privileges |

**N = 6** sections (Header/Preamble + 5 content sections).

For each reference section, find the best matching participant block by content intent. If no participant block covers a reference section, mark it **[MISSING]**.

---

## Step 3 — Calculate weights

```
N = 6
base_weight = floor(100 / 6) = 16
remainder = 100 − (16 × 6) = 4
→ distribute +1 to the 4 highest-complexity sections
```

| Section | Weight |
|---|---|
| Header/Preamble | 16 |
| Catalog-level audit | 16 |
| Schema-level audit | 17 |
| Table-level audit | 17 |
| Mart/View-level audit | 17 |
| Principal-to-privilege mapping | 17 |
| **Total** | **100** |

---

## Step 4 — Section flags

Detect which features are present in the participant file before scoring:

| Flag | Detection rule |
|---|---|
| `has_show_grants` | File contains `SHOW GRANTS ON` statement |
| `has_information_schema` | File contains `information_schema.object_privileges` reference |
| `has_catalog_name` | File references participant's own catalog name |
| `has_schema_coverage` | All 4 schema tiers covered (stg/dim/fact/mart or equivalents) |
| `has_table_coverage` | Specific table names OR comprehensive LIKE pattern covering dim/fact/mart |
| `has_principal_mapping` | Comment block or SELECT listing principal → object → privilege |
| `has_idempotency_note` | Header comment explicitly states script is read-only or idempotent |
| `has_task_id` | Header comment contains a TASK-* traceability tag |

---

## Step 5 — Adaptive criteria per section

Score each section 0–100, then apply the weight.

### Header / Preamble (weight 16)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 60% | CFG/TASK ID present, catalog name stated, purpose described |
| `has_idempotency_note` | 20% | Explicit "read-only" or "idempotent" comment |
| `has_task_id` | 10% | TASK-* traceability tag in header block |
| Structure | 10% | Comment block appears before first SQL statement; clean formatting |

### Catalog-level audit (weight 16)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 60% | Catalog-level coverage present — SHOW GRANTS ON CATALOG or equivalent WHERE filter |
| SQL approach | 25% | Either `SHOW GRANTS` or `information_schema` accepted; note which is used |
| `has_catalog_name` | 15% | Correct participant catalog name referenced |

**If MISSING:** raw score = 0; apply −4 auto-deduct (see Step 6).

### Schema-level audit (weight 17)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 50% | All expected schema tiers covered (stg, dim, fact, mart or equivalents) |
| `has_schema_coverage` | 30% | All 4 tiers present (+7.5 pts each) |
| SQL approach | 10% | Either syntax accepted |
| Structure | 10% | Section comment header; SQL correctly scoped to SCHEMA object type |

### Table-level audit (weight 17)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 50% | Tables in dim, fact layers covered; stg tables covered |
| `has_table_coverage` | 30% | Specific table names preferred; LIKE pattern acceptable if comprehensive |
| SQL approach | 10% | Either syntax accepted |
| Structure | 10% | Section comment header; correct object type filter |

### Mart/View-level audit (weight 17)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 55% | Views and/or materialized views in mart schema addressed |
| Coverage | 30% | Both VIEW and MATERIALIZED VIEW types distinguished (or covered under same filter) |
| Structure | 15% | Separate section or clearly distinguished from table audit |

**Note:** If participant uses a single table-level query that also catches views via `object_type IN ('TABLE', 'VIEW')`, credit mart/view coverage partially but note the lack of explicit separation.

### Principal-to-privilege mapping (weight 17)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 60% | ETL SP, BI SP, and analyst group mapped to objects and privileges |
| Coverage | 25% | All 3 principal types covered; SELECT / MODIFY / REFRESH mentioned |
| Structure | 15% | Formatted comment table, or structured SELECT — readable and complete |

**If MISSING:** raw score = 0; apply −3 auto-deduct.

---

## Step 6 — Auto-deducts

Apply globally after section scoring. Cap at −20 pts total.

| Condition | Penalty | How to detect |
|---|---|---|
| No catalog-level audit anywhere | −4 pts | No `SHOW GRANTS ON CATALOG` and no `WHERE object_type = 'CATALOG'` anywhere |
| No schema-level audit anywhere | −4 pts | No `SHOW GRANTS ON SCHEMA` and no `WHERE object_type = 'SCHEMA'` anywhere |
| No table-level audit anywhere | −4 pts | No `SHOW GRANTS ON TABLE` and no `WHERE object_type IN ('TABLE'...)` anywhere |
| No principal-to-privilege mapping | −3 pts | No comment table or query mapping principals → objects → privileges |
| No read-only / idempotency note | −2 pts | No "read-only" or "idempotent" comment in header block |
| DML statement present (INSERT/UPDATE/DELETE/MERGE) | −5 pts | Script contains write operations — violates read-only audit intent |
| Hardcoded credential or password value | −5 pts | Literal password, token, or connection string value in any statement |
| Uses reference catalog name verbatim | −2 pts | Participant script contains `globalpurchase` instead of their own catalog |
| No section separator comments anywhere | −3 pts | No `--` comment headers delineating logical sections |

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

Create the output directory if it does not exist: `checks/<trainee_name>/uc-permission-audit/`

Output file: `TASK-UC-001_check_report.md`

If a file already exists at that path, increment the suffix (`_v2`, `_v3`, …) and never overwrite.

**Report structure:**

```markdown
---
task_id: TASK-UC-001
skill: task-checker-uc-permission-audit
participant_file: trainees/<trainee_name>/uc_permission_audit.sql
reference_file: reference/uc_permission_audit.sql
product: <product_name>
generated: <YYYY-MM-DD>
total_score: <N>/100
grade: <grade>
---

# TASK-UC-001 Check Report

**Product:** <product>
**Reference:** Purchase (globalpurchase)
**Participant file:** `trainees/<trainee_name>/uc_permission_audit.sql`
**Reference file:** `reference/uc_permission_audit.sql`
**Generated:** <date>

---

## Score Summary

**UC Permission Audit Score: <N>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 16 | .../100 | ... | ✓/⚠/✗ |
| Catalog-level audit | Catalog-level | 16 | .../100 | ... | ✓/⚠/✗ |
| Schema-level audit | Schema-level | 17 | .../100 | ... | ✓/⚠/✗ |
| Table-level audit | Table-level | 17 | .../100 | ... | ✓/⚠/✗ |
| Mart/View-level audit | Mart/View-level | 17 | .../100 | ... | ✓/⚠/✗ |
| Principal-to-privilege mapping | Principal mapping | 17 | .../100 | ... | ✓/⚠/✗ |
| **Subtotal** | | | | **...** | |
| Auto-deducts | | | | **−...** | |
| **Total** | | | | **<N>/100** | |

**Grade: <grade>**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → Schema-level, Table-level, Mart/View-level, and Principal mapping each receive +1 → 17 pts. Header/Preamble and Catalog-level → 16 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | ... | Direct / Partial / [MISSING] |
| Catalog-level audit | ... | ... |
| Schema-level audit | ... | ... |
| Table-level audit | ... | ... |
| Mart/View-level audit | ... | ... |
| Principal-to-privilege mapping | ... | ... |

**Approach note:** Reference uses `SHOW GRANTS ON <object>` (per-object inspection). Participant uses [approach detected]. Both are valid; scoring reflects coverage and completeness, not syntactic preference.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No catalog-level audit anywhere | −4 pts | Yes/No — [reason] |
| No schema-level audit anywhere | −4 pts | Yes/No — [reason] |
| No table-level audit anywhere | −4 pts | Yes/No — [reason] |
| No principal-to-privilege mapping | −3 pts | Yes/No — [reason] |
| No read-only / idempotency note | −2 pts | Yes/No — [reason] |
| DML statement present | −5 pts | Yes/No |
| Hardcoded credential value | −5 pts | Yes/No |
| Uses reference catalog name | −2 pts | Yes/No |
| No section separator comments | −3 pts | Yes/No |

**Total auto-deducts: −N pts**

---

## Section Feedback

### Header/Preamble — <raw>/100 (weight 16 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Catalog-level audit — <raw>/100 (weight 16 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Schema-level audit — <raw>/100 (weight 17 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Table-level audit — <raw>/100 (weight 17 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Mart/View-level audit — <raw>/100 (weight 17 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Principal-to-privilege mapping — <raw>/100 (weight 17 → <weighted> pts)

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
3. **[Third fix]** — [description] worth up to **+N pts**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs Work | Missing schema/table audit or principal mapping absent |
| 0–44 | Incomplete | Major sections absent or DML statements present |

---

*Report generated by skill 33-migvisor-task-checker-uc-permission-audit on <date>*
```

---

## Step 9 — Console summary

After writing the report, output a console verdict in this exact format:

```
╔══════════════════════════════════════════════════════════════════╗
║  TASK-UC-001 · UC Permission Audit · <product> · <date>         ║
╠══════════════════════════════════════════════════════════════════╣
║  Score: <N>/100 · Grade: <grade>                                 ║
╚══════════════════════════════════════════════════════════════════╝
```

Follow immediately with a **5–6 sentence plain-English verdict**:

1. Overall score and grade in one sentence.
2. What was done well — strongest section or most effective approach used.
3. The most critical gap — missing section, approach limitation, or coverage gap.
4. **Must state the numeric score and name the two highest-priority fixes.**
5. Note on the approach difference (`SHOW GRANTS` vs `information_schema`) and its practical implication for auditability.
6. Recommendation: proceed to next task or revise first.
