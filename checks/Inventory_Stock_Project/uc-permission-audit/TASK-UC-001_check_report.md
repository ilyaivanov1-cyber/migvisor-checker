---
task_id: TASK-UC-001
skill: task-checker-uc-permission-audit
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/uc_permission_audit.sql
reference_file: reference/answers/module_5/codebase/config/uc_permission_audit.sql
product: Purchase (inventory_stock)
generated: 2026-09-25
total_score: 100/100
grade: Excellent
---

# TASK-UC-001 Check Report

**Product:** Purchase (inventory_stock)
**Reference:** Purchase (globalpurchase)
**Participant file:** `Inventory_Stock_Project/products/Purchase/current/codebase/config/uc_permission_audit.sql`
**Reference file:** `reference/answers/module_5/codebase/config/uc_permission_audit.sql`
**Generated:** 2026-09-25

---

## Score Summary

**UC Permission Audit Score: 100/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 16 | 100/100 | 16.00 | ✓ |
| Catalog-level audit | Catalog-level | 16 | 100/100 | 16.00 | ✓ |
| Schema-level audit | Schema-level | 17 | 100/100 | 17.00 | ✓ |
| Table-level audit | Table-level | 17 | 100/100 | 17.00 | ✓ |
| Mart/View-level audit | Mart/View-level | 17 | 100/100 | 17.00 | ✓ |
| Principal-to-privilege mapping | Principal mapping | 17 | 100/100 | 17.00 | ✓ |
| **Subtotal** | | | | **100.00** | |
| Auto-deducts | | | | **0** | |
| **Total** | | | | **100/100** | |

**Grade: Excellent**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → Schema-level, Table-level, Mart/View-level, and Principal mapping each receive +1 → 17 pts. Header/Preamble and Catalog-level → 16 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | Header/Preamble (lines 1–5) | Direct |
| Catalog-level audit | `SHOW GRANTS ON CATALOG inventory_stock` block | Direct |
| Schema-level audit | SHOW GRANTS ON SCHEMA blocks (4 schemas) | Direct |
| Table-level audit | SHOW GRANTS ON TABLE blocks (bronze + silver_dim + silver_fact) | Direct |
| Mart/View-level audit | SHOW GRANTS ON MATERIALIZED VIEW + VIEW blocks | Direct |
| Principal-to-privilege mapping | Comment table (lines 49–62) | Direct |

**Approach note:** Both reference and participant use `SHOW GRANTS ON <object>` (per-object inspection). This is the expected approach; information_schema alternative was not used — no issue.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No catalog-level audit anywhere | −4 pts | No — `SHOW GRANTS ON CATALOG inventory_stock` present |
| No schema-level audit anywhere | −4 pts | No — 4 SHOW GRANTS ON SCHEMA statements present |
| No table-level audit anywhere | −4 pts | No — 8 SHOW GRANTS ON TABLE statements present |
| No principal-to-privilege mapping | −3 pts | No — complete comment table present |
| No read-only / idempotency note | −2 pts | No — "Idempotent: SHOW GRANTS statements do not modify any state" ✓ |
| DML statement present | −5 pts | No — read-only SHOW GRANTS only |
| Hardcoded credential value | −5 pts | No — no credentials in script |
| Uses reference catalog name verbatim | −2 pts | No — uses `inventory_stock` throughout |
| No section separator comments | −3 pts | No — `-- ──` separator comments present for all sections |

**Total auto-deducts: 0 pts**

---

## Section Feedback

### Header/Preamble — 100/100 (weight 16 → 16.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100 | CFG-004 ID, catalog name, purpose, run-after context ✓ |
| has_idempotency_note | 20% | 100 | "Idempotent: SHOW GRANTS statements do not modify any state" ✓ |
| has_task_id | 10% | 100 | CFG-004 ✓ |
| Structure | 10% | 100 | Comment block before first SQL ✓ |

**Strengths:**
- Idempotency note explicitly stated and technically precise ✓
- Run context documented: "Run after GRANT-001 through GRANT-004 to verify the expected privilege mapping" ✓
- CFG-004 task ID present ✓

---

### Catalog-level audit — 100/100 (weight 16 → 16.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100 | SHOW GRANTS ON CATALOG inventory_stock ✓ |
| SQL approach | 25% | 100 | SHOW GRANTS approach ✓ |
| has_catalog_name | 15% | 100 | inventory_stock ✓ |

**Strengths:**
- Participant adds explanatory comment about downstream impact if catalog-level grants are absent — exceeds reference in operational guidance:
  "If these are absent, downstream SHOW GRANTS on schema/table will also fail with insufficient privileges. Re-run CFG-004 GRANT-001 to restore."

---

### Schema-level audit — 100/100 (weight 17 → 17.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 100 | All 4 schemas covered ✓ |
| has_schema_coverage | 30% | 100 | bronze, silver_dim, silver_fact, mart — all 4 tiers ✓ |
| SQL approach | 10% | 100 | SHOW GRANTS ✓ |
| Structure | 10% | 100 | Section separator comment ✓ |

**Strengths:**
- 4 schemas (bronze, silver_dim, silver_fact, mart) correctly map to reference's 4 tiers (stg, dim, fact, mart)
- Inline comments document expected grants per schema (e.g., "silver_dim: etl-service-principal and bi-service-principal have USE SCHEMA") ✓

---

### Table-level audit — 100/100 (weight 17 → 17.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 100 | Tables in bronze, silver_dim, silver_fact all covered ✓ |
| has_table_coverage | 30% | 100 | 8 specific table names; comprehensive coverage ✓ |
| SQL approach | 10% | 100 | SHOW GRANTS ON TABLE ✓ |
| Structure | 10% | 100 | Section separator, inline comments ✓ |

**Strengths:**
- All 8 tables explicitly named: bronze (purchase_staging, etl_cutoff, lineage_run, dq_rejections), silver_dim (supplier, stock_item, date), silver_fact (fact_purchase) ✓
- Inline comments document expected grants (e.g., "Expected: etl → SELECT+MODIFY; bi → SELECT") ✓

---

### Mart/View-level audit — 100/100 (weight 17 → 17.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100 | Materialized view + standard view covered ✓ |
| Coverage | 30% | 100 | SHOW GRANTS ON MATERIALIZED VIEW and SHOW GRANTS ON VIEW both used ✓ |
| Structure | 15% | 100 | Separate section, comment header ✓ |

**Strengths:**
- Correctly distinguishes MATERIALIZED VIEW (v_purchase_by_supplier) from VIEW (v_purchase_per_stock_item) with separate SHOW GRANTS syntax ✓
- Inline comment: "Expected: bi + analysts → SELECT; etl → SELECT+REFRESH on materialized view" ✓

---

### Principal-to-privilege mapping — 100/100 (weight 17 → 17.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100 | All 3 principal types; all objects; all privileges ✓ |
| Coverage | 25% | 100 | etl-SP, bi-SP, purchase-analysts + SELECT/MODIFY/REFRESH ✓ |
| Structure | 15% | 100 | Formatted ASCII comment table with aligned columns ✓ |

**Strengths:**
- Complete 9-row principal mapping table covering all three principals ✓
- All privilege types covered: SELECT, MODIFY, REFRESH ✓
- Correct alignment between reference and participant schemas:
  - `globalpurchase.dim.supplier` → `inventory_stock.silver_dim.supplier` ✓
  - `globalpurchase.fact.purchase` → `inventory_stock.silver_fact.fact_purchase` ✓
- Formatted with aligned columns for readability ✓

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| — | No significant gaps identified | — | 0 pts |

The participant's script is a complete, accurate, and well-commented adaptation of the reference. No improvement items are needed before proceeding.

---

## Priority Actions

No priority actions required. The script is ready for production use.

Optional enhancements (no score impact):
1. Add a `USE CATALOG inventory_stock;` statement at the top for explicitness in environments where the active catalog may vary.
2. Add a trailing verification comment summarising the number of SHOW GRANTS statements executed (9 object-level + 4 schema-level + 1 catalog-level = 14 total).

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

*Report generated by skill 33-migvisor-task-checker-uc-permission-audit on 2026-09-25*
