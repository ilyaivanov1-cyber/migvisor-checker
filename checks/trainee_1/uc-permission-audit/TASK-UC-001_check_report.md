---
task_id: TASK-UC-001
skill: task-checker-uc-permission-audit
participant_file: trainees/trainee_1/uc_permission_audit.sql
reference_file: reference/uc_permission_audit.sql
product: Sales_Orders
generated: 2026-09-04
total_score: 44/100
grade: Incomplete
---

# TASK-UC-001 Check Report

**Product:** Sales_Orders  
**Reference:** Purchase (globalpurchase)  
**Participant file:** `trainees/trainee_1/uc_permission_audit.sql`  
**Reference file:** `reference/uc_permission_audit.sql`  
**Generated:** 2026-09-04

---

## Score Summary

**UC Permission Audit Score: 44/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 16 | 87/100 | 13.9 | ✓ |
| Catalog-level audit | Catalog-level | 16 | 39/100 | 6.2 | ✗ |
| Schema-level audit | Schema-level | 17 | 80/100 | 13.6 | ✓ |
| Table-level audit | Table-level | 17 | 66/100 | 11.2 | ⚠ |
| Mart/View-level audit | Mart/View-level | 17 | 33/100 | 5.6 | ✗ |
| Principal-to-privilege mapping | Principal mapping | 17 | 0/100 | 0.0 | ✗ |
| **Subtotal** | | | | **50.6** | |
| Auto-deducts | | | | **−7** | |
| **Total** | | | | **44/100** | |

**Grade: Incomplete**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → Schema-level, Table-level, Mart/View-level, and Principal mapping each receive +1 → 17 pts. Header/Preamble and Catalog-level → 16 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | Lines 1–4 before `USE CATALOG` | Direct match |
| Catalog-level audit | `USE CATALOG globalsales` + first all-objects SELECT | Partial — no explicit `WHERE object_type = 'CATALOG'` filter |
| Schema-level audit | `-- Schema-level privileges summary` SELECT | Good match — `WHERE object_type = 'SCHEMA'` with `COLLECT_SET` aggregation |
| Table-level audit | `-- Table-level privileges summary` SELECT | Partial — dim/fact/mart via LIKE; stg tables absent |
| Mart/View-level audit | Table-level SELECT (`object_type IN ('TABLE', 'VIEW')` + `LIKE 'globalsales.mart.%'`) | Partial — VIEW implicitly caught; MATERIALIZED VIEW not in `object_type` filter; no dedicated section |
| Principal-to-privilege mapping | [MISSING] | Missing — no comment table or principal → privilege mapping anywhere |

**Approach note:** Reference uses `SHOW GRANTS ON <object>` (per-object inspection, one statement per object). Participant uses `information_schema.object_privileges` SELECT queries (bulk retrieval). Both are valid; scoring reflects coverage and completeness, not syntactic preference. The `information_schema` approach is more concise and returns all grants at once, but requires explicit `object_type` filters to match the reference's targeted per-level coverage.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No catalog-level audit anywhere | −4 pts | **Yes** — no `SHOW GRANTS ON CATALOG` and no `WHERE object_type = 'CATALOG'` anywhere; broad all-objects SELECT does not substitute for explicit catalog audit |
| No schema-level audit anywhere | −4 pts | **No** — `WHERE object_type = 'SCHEMA'` present in schema-level SELECT |
| No table-level audit anywhere | −4 pts | **No** — `WHERE object_type IN ('TABLE', 'VIEW')` present in table-level SELECT |
| No principal-to-privilege mapping | −3 pts | **Yes** — no comment table and no SELECT mapping principals → objects → privileges |
| No read-only / idempotency note | −2 pts | **No** — "Read-only — no DDL or DML" explicit in header |
| DML statement present | −5 pts | **No** — only SELECT and USE CATALOG; no INSERT/UPDATE/DELETE/MERGE |
| Hardcoded credential value | −5 pts | **No** — no passwords, tokens, or connection strings |
| Uses reference catalog name | −2 pts | **No** — uses `globalsales` throughout; `globalpurchase` absent |
| No section separator comments | −3 pts | **No** — `-- All privileges…`, `-- Schema-level…`, `-- Table-level…` comments present |

**Total auto-deducts: −7 pts**

---

## Section Feedback

### Header/Preamble — 87/100 (weight 16 → 13.9 pts)

**Criteria scored:** Content completeness (60%), `has_idempotency_note` (20%), `has_task_id` (10%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 80/100 | TASK-SEC-004 present, `globalsales` catalog stated, purpose described; PENDING note (CX-P05) adds useful context; no CFG ID equivalent |
| `has_idempotency_note` | 20% | 100/100 | "Read-only — no DDL or DML" is explicit and clear |
| `has_task_id` | 10% | 100/100 | TASK-SEC-004 traceability tag present |
| Structure | 10% | 90/100 | Clean comment block before first SQL statement; well-formatted |

**Strengths:**
- Read-only declaration is explicit and prominent.
- PENDING flag (CX-P05) documents a known gap — honest and traceable.
- TASK-SEC-004 provides full traceability.

**Gaps:**
- No CFG-* runbook ID equivalent (reference has CFG-004).
- No "run after GRANT scripts" context note.

**Improvement items:**
- [ ] Add a CFG/runbook reference (e.g., `-- CFG-004 equivalent: run after all GRANT scripts`).

---

### Catalog-level audit — 39/100 (weight 16 → 6.2 pts)

**Criteria scored:** Content completeness (60%), SQL approach (25%), `has_catalog_name` (15%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 15/100 | No explicit catalog-level grants query; `USE CATALOG globalsales` sets context but does not list grants; first all-objects SELECT implicitly includes catalog rows but has no `WHERE object_type = 'CATALOG'` filter |
| SQL approach | 25% | 65/100 | `information_schema` approach is valid; but no catalog-specific filter demonstrates intentional catalog audit |
| `has_catalog_name` | 15% | 100/100 | `globalsales` used correctly throughout |

**Gaps:**
- No `WHERE object_type = 'CATALOG'` filter anywhere — catalog-level grants are not explicitly audited.
- `USE CATALOG` is a context-setter, not an audit statement.

**Improvement items:**
- [ ] Add a catalog-level query:
  ```sql
  -- Catalog-level privileges
  SELECT object_type, object_name, privilege_type, grantee
  FROM globalsales.information_schema.object_privileges
  WHERE object_type = 'CATALOG'
  ORDER BY grantee, privilege_type;
  ```

---

### Schema-level audit — 80/100 (weight 17 → 13.6 pts)

**Criteria scored:** Content completeness (50%), `has_schema_coverage` (30%), SQL approach (10%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 80/100 | Schema SELECT with `WHERE object_type = 'SCHEMA'` covers all schemas; `COLLECT_SET(privilege_type)` aggregation is clear; no explicit stg/dim/fact/mart enumeration but broad query covers all |
| `has_schema_coverage` | 30% | 70/100 | All 4 tiers implicitly covered by broad schema query; no per-schema expected-privilege annotation (reference annotates expected grants per schema) |
| SQL approach | 10% | 100/100 | `information_schema` with `WHERE object_type = 'SCHEMA'` is correct |
| Structure | 10% | 85/100 | Clear `-- Schema-level privileges summary` comment header; well-formatted SELECT |

**Strengths:**
- `COLLECT_SET(privilege_type)` aggregation is more readable than individual `SHOW GRANTS` per schema.
- `GROUP BY schema_name, grantee` gives a clean per-principal view.

**Gaps:**
- No inline comments documenting expected grants per schema (reference annotates: "stg: etl-SP has USE SCHEMA + SELECT + MODIFY").

**Improvement items:**
- [ ] Add inline comments stating expected grants for each schema tier (stg, dim, fact, mart).

---

### Table-level audit — 66/100 (weight 17 → 11.2 pts)

**Criteria scored:** Content completeness (50%), `has_table_coverage` (30%), SQL approach (10%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 62/100 | dim/fact/mart tables covered via LIKE patterns; stg tables entirely absent (no `LIKE 'globalsales.stg.%'`); `object_type IN ('TABLE', 'VIEW')` is valid |
| `has_table_coverage` | 30% | 55/100 | LIKE pattern covers 3 of 4 layers; specific table names (supplier, stock_item, purchase etc.) not enumerated — LIKE is acceptable but less precise |
| SQL approach | 10% | 100/100 | `information_schema` with `LIKE` filter is correct |
| Structure | 10% | 85/100 | Clear `-- Table-level privileges summary` header |

**Gaps:**
- `stg` layer entirely absent — `globalsales.stg.*` tables (staging, etl_cutoff, lineage, dq_rejections) not audited.
- LIKE pattern matches broadly; no validation against specific expected table names.

**Improvement items:**
- [ ] Add `OR object_name LIKE 'globalsales.stg.%'` to the table-level LIKE filter.
- [ ] Consider enumerating specific expected table names in a comment for verification reference.

---

### Mart/View-level audit — 33/100 (weight 17 → 5.6 pts)

**Criteria scored:** Content completeness (55%), Coverage (30%), Structure (15%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 40/100 | Mart views caught by table-level query via `object_type IN ('TABLE', 'VIEW')` + `LIKE 'globalsales.mart.%'`; MATERIALIZED VIEW not in `object_type` filter; no dedicated section |
| Coverage | 30% | 35/100 | VIEW covered implicitly; MATERIALIZED VIEW (`object_type = 'MATERIALIZED VIEW'`) absent from filter |
| Structure | 15% | 0/100 | No dedicated mart/view section or comment distinguishing it from table audit |

**Gaps:**
- `MATERIALIZED VIEW` object type not included in `object_type IN ('TABLE', 'VIEW')` — materialized views have a distinct type in Unity Catalog and require explicit inclusion.
- No dedicated mart/view section — mart view coverage is buried inside the table-level query.

**Improvement items:**
- [ ] Add a dedicated mart/view section:
  ```sql
  -- Mart view and materialized view privileges
  SELECT object_type, object_name, privilege_type, grantee
  FROM globalsales.information_schema.object_privileges
  WHERE object_type IN ('VIEW', 'MATERIALIZED VIEW')
    AND object_name LIKE 'globalsales.mart.%'
  ORDER BY object_type, object_name, grantee;
  ```
- [ ] Remove VIEW from the table-level query's `object_type` filter to avoid double-counting.

---

### Principal-to-privilege mapping — 0/100 (weight 17 → 0.0 pts)

**[MISSING]** — No comment table and no SELECT that maps principals to specific objects and expected privileges. The reference includes a formatted comment block listing every principal, object, and privilege set expected after all GRANT scripts run. This is the most important verification artifact — it allows an operator to confirm the actual output matches expectations.

**Improvement items:**
- [ ] Add a principal-to-privilege mapping comment block:
  ```sql
  -- ── Expected principal-to-privilege mapping ─────────────────────────────────
  -- Compare query results above against this matrix:
  --
  -- Principal                  | Object                        | Privileges
  -- -------------------------- | ----------------------------- | ----------------------
  -- etl-service-principal      | globalsales.dim.*             | SELECT, MODIFY
  -- etl-service-principal      | globalsales.fact.*            | SELECT, MODIFY
  -- etl-service-principal      | globalsales.mart.* (MV)       | SELECT, REFRESH
  -- bi-service-principal       | globalsales.dim.*             | SELECT
  -- bi-service-principal       | globalsales.fact.*            | SELECT
  -- bi-service-principal       | globalsales.mart.*            | SELECT
  -- sales-analysts              | globalsales.mart.*            | SELECT
  ```

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add principal-to-privilege mapping comment block | Principal mapping | +12 pts + removes −3 deduct = +15 pts |
| 2 | Add `WHERE object_type = 'CATALOG'` query for catalog-level audit | Catalog-level | +8 pts + removes −4 deduct = +12 pts |
| 3 | Add dedicated mart/view section with `MATERIALIZED VIEW` in `object_type` filter | Mart/View-level | +8 pts |
| 4 | Add `globalsales.stg.%` LIKE filter to table-level query | Table-level | +3 pts |
| 5 | Add inline expected-grant annotations per schema | Schema-level | +2 pts |

---

## Priority Actions

1. **Add principal-to-privilege mapping** — entirely missing; a comment table listing ETL SP, BI SP, and analyst roles with their expected objects and privileges removes the −3 deduct and scores the full 17-pt section. Worth up to **+15 pts**.
2. **Add catalog-level audit query** — add `WHERE object_type = 'CATALOG'` SELECT to explicitly audit catalog grants; removes the −4 deduct and improves Catalog section from 39→85. Worth up to **+12 pts**.
3. **Add dedicated mart/view section** — add `MATERIALIZED VIEW` to the `object_type` filter and split it into its own section; improves Mart/View from 33→85. Worth up to **+8 pts**.
4. **Add stg layer to table query** — one additional LIKE clause (`OR object_name LIKE 'globalsales.stg.%'`) closes the stg coverage gap. Worth up to **+3 pts**.

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

*Report generated by skill 33-migvisor-task-checker-uc-permission-audit on 2026-09-04*
