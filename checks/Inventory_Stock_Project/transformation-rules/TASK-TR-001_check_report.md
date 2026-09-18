---
task_id: TASK-TR-001
skill: migvisor-task-checker-transformation-rules
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md
reference_file: ./reference/answers/module_3/product-transformation-rules/product-transformation-rules.md
generated: 2026-09-18
total_score: 72/100
grade: Acceptable
---

# TASK-TR-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md`  
**Reference file:** `./reference/answers/module_3/product-transformation-rules/product-transformation-rules.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Transformation Rules Score: 72/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Customization Summary | 20 | 88/100 | 17.6 | ✓ |
| Action Files | 20 | 50/100 | 10.0 | ⚠ |
| Dimension Table | 20 | 92/100 | 18.4 | ✓ |
| Rule Index | 20 | 85/100 | 17.0 | ✓ |
| Stakeholder Confirmations | 20 | 30/100 | 6.0 | ✗ |
| **Subtotal** | | | **69.0** | |
| Auto-deducts | | | **−7** | |
| **Total** | | | **72/100** | |

**Grade: Acceptable**

> **Weight calculation:** N = 5, base_weight = floor(100/5) = 20, remainder = 0 → all sections 20 pts.

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| Customization Summary | §Customization Summary | Direct |
| Action Files | Embedded in Dimension Table | Partial |
| Dimension Table | §Dimension Table | Direct |
| Rule Index (all 9 dimensions) | §Rule Index (9 dimensions) | Direct |
| Stakeholder Confirmations Required | Not present separately | Missing |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| Missing explicit Stakeholder Confirmations section with owner assignments | −3 pts | Yes — reference has 2 stakeholder gates (CX-P03, LN-P01) with named owners; trainee embeds these concerns in rules but no confirmation table |
| Missing Package column name preservation rule (LN-P01 equivalent) | −2 pts | Yes — trainee LN-P001 is about taskValues injection; Package column preservation for cross-domain Order team compatibility is absent |
| Missing IF (Interface) dimension coverage at product level | −2 pts | Yes — reference has 5 IF rules for SSIS→Workflow orchestration, JDBC watermark, credentials, staging strategy; trainee absorbs these into OB and LN but no dedicated IF dimension |

**Total auto-deducts: −7 pts**

---

## Section Feedback

### Customization Summary — 88/100 (weight 20 → 17.6 pts)

**Status:** ✓ Present

**Strengths:** Correct structure with Type/Count/Rule IDs table. Counts are clear and well-organized. 26 total customizations (1 override, 13 extensions, 12 new rules) vs reference's 13 (5 extensions, 8 new rules) — trainee is more thorough.

**Gaps:** Header metadata uses "Active dimensions: 9" and "Product-only dimensions: 2" — reference uses a cleaner one-table summary format. Trainee doesn't note "Overrides: 0" or "Deactivations: 0" explicitly in the same row (reference shows all types including zero-count ones for completeness).

---

### Action Files — 50/100 (weight 20 → 10.0 pts)

**Status:** ⚠ Partial

**Strengths:** Yaml files are referenced by hyperlink in the Dimension Table (e.g., `[TY-types.yaml](TY-types.yaml)`).

**Gaps:** Reference has an explicit **Action Files** section listing each yaml file with content description and status (Present/Absent). Trainee has no such section. The distinction between which files exist vs. which are expected (override.yaml absent — expected) is not documented.

---

### Dimension Table — 92/100 (weight 20 → 18.4 pts)

**Status:** ✓ Present

**Strengths:** 9 dimensions with file links, rule counts, and customizations applied per row. Trainee adds PE (Performance) dimension which the reference lacks — this is a value-add. Rule counts are higher than reference (trainee: 90+ total vs reference: 39) showing greater depth. Tags column clearly labels Override/Extension/New for each rule.

**Gaps:** Minor: reference's "Customizations" column includes specific rule IDs in parentheses; trainee's "Customizations Applied" column has this for some dimensions but not all consistently.

---

### Rule Index — 85/100 (weight 20 → 17.0 pts)

**Status:** ✓ Present

**Strengths:** All 9 dimensions present with complete rule tables and Tags. PL dimension has 10 rules covering platform migration strategy. NM has 9 rules including TOP PRIORITY NM-002 for space-bearing names. TY has 30 rules including DATETIME2 → TIMESTAMP_NTZ override (TY-P001) and extended SCD-2 block pattern (TY-P002). SX has product-specific extensions for Purchase MERGE pattern and lineage injection.

**Gaps:**
- Missing IF (Interface) dimension: no dedicated section for SSIS→Workflow interface rules, JDBC credential storage, task dependency contracts.
- LN-P001 (trainee) covers taskValues injection — correct — but missing Package column preservation rule that the reference's LN-P01 specifies (preserve `package` column name and STRING type; document cross-domain case-sensitivity risk for Order product team).
- Reference has `SX-004-EXT-P01` (full-order-level replacement MERGE for Purchase) — trainee has SX-P004 for inline lineage-close pattern conversion — different coverage.

---

### Stakeholder Confirmations — 30/100 (weight 20 → 6.0 pts)

**Status:** ✗ Missing as standalone section

**Strengths:** CX-P001 and CX-P002 reference config externalisation and business rule parameters. CX-P003 exists (consolidating duplicate scalar functions) but doesn't correspond to reference's CX-P03 (QuantityPerOuter point-in-time stakeholder confirmation).

**Gaps:** Reference has an explicit `## Stakeholder Confirmations Required Before Go-Live` section with:
1. **CX-P03**: ordered_quantity temporality — batch-run-time `quantity_per_outer` vs. order-date point-in-time → Product owner / Procurement team
2. **LN-P01**: Order product team notified of `package` column name contract → Purchase migration lead

Neither of these confirmation gates is explicitly documented as a decision gate with a named owner in the trainee's rules. These are important go-live blockers that should surface as explicit stakeholder confirmations.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add explicit Stakeholder Confirmations section with 2 gates (QuantityPerOuter temporality, Package column contract) and named owners | §Stakeholder Confirmations | +8 pts |
| 2 | Add LN-P001 or LN-P002 for Package column name preservation and case-sensitivity risk for Order product team | §Rule Index / LN | +3 pts |
| 3 | Add IF (Interface) dimension covering SSIS→Workflow dependencies, JDBC watermark strategy, credentials | §Rule Index | +3 pts |
| 4 | Add explicit Action Files section listing yaml files with present/absent status | §Action Files | +3 pts |

---

## Priority Actions

1. **Add Stakeholder Confirmations section** — two explicit go-live gates: (a) QuantityPerOuter temporality decision (batch-time vs. order-date point-in-time) with Procurement team owner, (b) Package column name contract notification with Order product team. Worth up to **+8 pts**.
2. **Add Package column preservation LN rule** — `package` column must preserve its name and STRING type in the target Delta schema; document case-sensitivity risk (SQL Server CI vs. Databricks CS) for `v_ordertoyearanalytics` compatibility with Order product. Worth up to **+3 pts**.
3. **Add IF dimension or equivalent** — at minimum document the explicit task dependency contract (supplier load → stock_item load → fact_purchase load) as an IF rule with the nb_load_fact_purchase.depends_on pattern. Worth up to **+3 pts**.

---

*Report generated by migvisor-task-checker-transformation-rules on 2026-09-18*
