---
task_id: TASK-UC-001
skill: migvisor-task-checker-uc-permission-audit
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/uc_permission_audit.sql
reference_file: reference/answers/module_5/codebase/config/uc_permission_audit.sql
product: Purchase
generated: 2026-09-24
total_score: 98/100
grade: Excellent
---

# TASK-UC-001 Check Report — UC Permission Audit
_Purchase | 2026-09-24_

## Score Summary

**UC Permission Audit Score: 98/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 16 | 95/100 | 15.2 | ✓ |
| Catalog-level audit | Catalog-level | 16 | 100/100 | 16.0 | ✓ |
| Schema-level audit | Schema-level | 17 | 100/100 | 17.0 | ✓ |
| Table-level audit | Table-level | 17 | 100/100 | 17.0 | ✓ |
| Mart/View-level audit | Mart/View-level | 17 | 100/100 | 17.0 | ✓ |
| Principal-to-privilege mapping | Principal mapping | 17 | 100/100 | 17.0 | ✓ |
| **Subtotal** | | | | **99.2** | |
| Auto-deducts | | | | **−1** | |
| **Total** | | | | **98/100** | |

**Grade: Excellent**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → Schema-level, Table-level, Mart/View-level, and Principal mapping each receive +1 → 17 pts. Header/Preamble and Catalog-level → 16 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | Comment block: "CFG-004: Unity Catalog permission audit script..." | Direct |
| Catalog-level audit | `SHOW GRANTS ON CATALOG inventory_stock` block | Direct |
| Schema-level audit | Four `SHOW GRANTS ON SCHEMA inventory_stock.*` statements | Direct |
| Table-level audit | `SHOW GRANTS ON TABLE inventory_stock.*` statements (8 tables) | Direct |
| Mart/View-level audit | `SHOW GRANTS ON MATERIALIZED VIEW` + `SHOW GRANTS ON VIEW` | Direct |
| Principal-to-privilege mapping | Comment table at end of file | Direct |

**Approach note:** Both reference and participant use `SHOW GRANTS ON <object>` (per-object inspection). This is the standard audit approach for Databricks Unity Catalog. Scoring reflects coverage and completeness, not syntactic preference.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No catalog-level audit anywhere | −4 pts | No — `SHOW GRANTS ON CATALOG inventory_stock` present |
| No schema-level audit anywhere | −4 pts | No — all 4 schemas audited |
| No table-level audit anywhere | −4 pts | No — 8 tables covered across all schema tiers |
| No principal-to-privilege mapping | −3 pts | No — comment table maps all 3 principals |
| No read-only / idempotency note | −2 pts | No — "Read-only" and "Idempotent: SHOW GRANTS statements do not modify any state" present |
| DML statement present | −5 pts | No — script is entirely SHOW GRANTS statements |
| Hardcoded credential value | −5 pts | No |
| Uses reference catalog name verbatim | −2 pts | No — uses `inventory_stock`, not `globalpurchase` |
| No section separator comments | −3 pts | No — `-- ──` box-drawing separators present for all sections |

**Note:** −1 pt conservative adjustment: the header comment uses "CFG-004:" task reference format rather than a TASK-UC-* style tag. The reference also uses CFG-004, so this is a very minor deviation from the TASK-* convention expected by the rubric's `has_task_id` criterion.

**Total auto-deducts: −1**

---

## Section Feedback

### Header/Preamble — 95/100 (weight 16 → 15.2 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100% | CFG-004 ID, catalog name, purpose, idempotency — all present |
| has_idempotency_note | 20% | 100% | "Read-only — lists all grants..." + "SHOW GRANTS statements do not modify any state" |
| has_task_id | 10% | 50% | "CFG-004:" present but not TASK-* format; reference also uses CFG-004 |
| Structure | 10% | 100% | Clean comment block before first SQL statement |

**Strengths:**
- Dual idempotency assurance: "Read-only" label + explicit "do not modify any state" explanation.
- Detailed expected-grants comments for catalog level (states which principals should have USE CATALOG and why absence is significant).
- Inline contextual comments throughout (e.g., "If these are absent, downstream SHOW GRANTS on schema/table will also fail...") — exceeds the reference.

**Gaps:**
- Task identifier uses CFG-004 format rather than TASK-UC-001 (minor).

---

### Catalog-level audit — 100/100 (weight 16 → 16 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100% | SHOW GRANTS ON CATALOG inventory_stock with expected grants documented |
| SQL approach | 25% | 100% | SHOW GRANTS — valid and idiomatic approach |
| has_catalog_name | 15% | 100% | `inventory_stock` used correctly throughout |

**Strengths:**
- Expected grant annotations ("etl-service-principal → USE CATALOG, bi-service-principal → USE CATALOG") are documented in comments.
- Troubleshooting note ("If these are absent, downstream SHOW GRANTS... will also fail") adds operational value beyond the reference.

---

### Schema-level audit — 100/100 (weight 17 → 17 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 100% | All 4 schemas audited |
| has_schema_coverage | 30% | 100% | 4/4 tiers: bronze, silver_dim, silver_fact, mart |
| SQL approach | 10% | 100% | SHOW GRANTS ON SCHEMA |
| Structure | 10% | 100% | Section separator comment; correct scope |

**Strengths:**
- All 4 schema tiers covered (bronze≡stg, silver_dim≡dim, silver_fact≡fact, mart=mart — cross-product naming).
- Expected privileges noted inline for each schema (e.g., "etl-service-principal has USE SCHEMA + SELECT + MODIFY").

---

### Table-level audit — 100/100 (weight 17 → 17 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 100% | 8 tables across bronze, silver_dim, silver_fact |
| has_table_coverage | 30% | 100% | Specific table names across all layers |
| SQL approach | 10% | 100% | SHOW GRANTS ON TABLE |
| Structure | 10% | 100% | Section separator comment; group comments by schema tier |

**Strengths:**
- Bronze tier: purchase_staging, etl_cutoff, lineage_run, dq_rejections (4 tables).
- Silver_dim: supplier, stock_item, date (3 dimension tables).
- Silver_fact: fact_purchase (1 fact table).
- Inline expected-privilege comments (e.g., "Expected: etl → SELECT+MODIFY; bi → SELECT") add audit traceability.
- Cross-product note: `lineage_run` vs reference's `lineage` — different naming convention for same logical table, correctly adapted.

---

### Mart/View-level audit — 100/100 (weight 17 → 17 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100% | Both mart objects covered |
| Coverage | 30% | 100% | MATERIALIZED VIEW + VIEW explicitly distinguished |
| Structure | 15% | 100% | Separate section with `-- ──` separator |

**Strengths:**
- Explicit distinction between MATERIALIZED VIEW (`v_purchase_by_supplier`) and standard VIEW (`v_purchase_per_stock_item`) — matches reference exactly.
- Expected grants annotation ("Expected: bi + analysts → SELECT; etl → SELECT+REFRESH on materialized view") present.

---

### Principal-to-privilege mapping — 100/100 (weight 17 → 17 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100% | All 3 principals mapped to all objects and privileges |
| Coverage | 25% | 100% | etl-service-principal (SELECT/MODIFY/REFRESH), bi-service-principal (SELECT), purchase-analysts (SELECT) |
| Structure | 15% | 100% | Formatted comment table with aligned columns |

**Strengths:**
- All 3 principal types covered: ETL service principal, BI service principal, analysts group.
- SELECT/MODIFY/REFRESH privilege distinctions correctly documented.
- Comment table aligns columns with pipe notation for readability.
- Trainee's mapping correctly includes bronze-tier tables (which the reference omits for ETL principal) — a thorough addition.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Header uses CFG-004 format rather than TASK-UC-001 | Header/Preamble | +1 pt |

---

## Priority Actions

1. **Add TASK-UC-001 tag to header comment** — Supplement "CFG-004:" with "TASK-UC-001" to satisfy the TASK-* traceability requirement. Worth up to **+1 pt**.

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

_Report generated by skill migvisor-task-checker-uc-permission-audit on 2026-09-24_
