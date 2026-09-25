# Check Report: TASK-SCOPE-001
**Skill:** scope | **Trainee:** Inventory_Stock_Project | **Product:** Purchase
**Checker version:** v1 | **Generated:** 2026-09-25

---

## Score: 90 / 100 — Excellent

---

## Rubric Evaluation

### Coverage — 38 / 40

All 9 required sections are present and substantively populated: §1 Identity, §2 Description, §3 Objects (6 subsections), §4 Out-of-scope, §5 Consumers, §6 Calculation Surface, §7 Boundaries, §8 Priority, §9 Migration Risks.

Object inventory is complete: 19 objects across exactly 6 categories — Core Fact (1), Conformed Dims (3), Integration Staging (7 objects including purchase_staging and control tables), Sequences (1), SSIS Orchestration (5 items), BI Reports (2). This matches the reference count precisely.

Migration risks: trainee documents 7 risks covering all entries listed in the SKILL.md domain notes: (1) SSIS staging-truncation bug, (2) space-bearing names, (3) SEQUENCE retirement, (4) T-SQL MERGE pattern, (5) configuration_reseedetl, (6) cross-product dimension dependency (supplier/stock_item owned by shared layer), (7) cross-domain BI report (wwidw_purchase_and_sale_per_stockitem_dynamic requires coordinated Sale product cutover). All 7 SKILL.md-referenced risks are documented.

Out-of-scope section: trainee lists approximately 11 categorised entries with rationale. The reference includes 12 entries; one minor gap is the absence of `getpurchaseupdates` as an explicitly named stored procedure in the out-of-scope list (the trainee covers procedure decommissioning generally but does not name this procedure by its source identifier). Minor coverage gap (-2 pts).

### Specificity — 23 / 25

Each section uses precise identifiers: catalog `inventory_stock`, source catalog `wideworldimportersdw`, schema names (fact, dimension, integration), specific procedure names (`migratestagedpurchasedata`, `getlastetlcutofftime`, `configuration_reseedetl`), SSIS pipeline `pipeline_dailyetlmain`. Each migration risk includes a description of the risk mechanism and its migration implication. Priority is stated as PRIMARY with explicit rationale. Minor deduction: the migration impact of the cross-domain analytics view (`analytics.v_ordertoyearanalytics` referencing `fact.purchase.Package`) is mentioned in §5 Consumers but is not explicitly listed as a distinct migration risk, reducing the risk section's specificity slightly.

### Technical Accuracy — 19 / 20

Catalog target `inventory_stock` is correct and consistently used. The Medallion architecture mapping (fact → silver_fact, dimension → silver_dim, integration → bronze) is correctly implied. Consumer count of 3 (2 BI reports + 1 cross-domain view) matches reference. The SSIS truncation bug risk is correctly attributed to the wrong staging table delete (`Integration.Order_Staging` instead of `Integration.Purchase_Staging`). SEQUENCE retirement correctly identified as required. All object categorisations are technically accurate. Minor: §7 boundaries contain [USER INPUT REQUIRED] placeholders for scope owner and temporal/organisational boundaries — these are legitimate deferrals matching the reference, not errors.

### Issues / Gaps — 8 / 10

**Gap 1:** `getpurchaseupdates` stored procedure is not named explicitly in the out-of-scope objects list. Reference specifically names it as out of scope (replaced by direct JDBC extract, rule OB-002).

**Gap 2:** Migration risk for `analytics.v_ordertoyearanalytics` cross-domain dependency on both `fact.purchase` and `fact.order`/`fact.sale` is documented under §5 Consumers but is not elevated to the migration risks section (§9). The reference has this as a distinct risk entry with explicit ownership (Order product team).

Both gaps are minor and do not affect the functional correctness of the scope document.

### Structure — 5 / 5

All 9 sections present in logical order. Subsections within §3 (Objects) are clearly delineated by category. Tables used where appropriate. Consistent heading hierarchy throughout.

---

## Auto-Deduct Checks

| Check | Result |
|---|---|
| All 7 SKILL.md migration risks documented | PASS — all 7 present |
| 19 objects across 6 categories | PASS — exact match |
| [USER INPUT REQUIRED] placeholders legitimate | PASS — matches reference pattern (scope owner, boundaries) |

**Total auto-deductions: 0 pts**

---

## Cross-File Consistency Checks

No mandatory cross-file checks defined for scope deliverable.

---

## Summary

The scope document is comprehensive and covers all required sections with precise identifiers. All 7 migration risks per SKILL.md are documented with sufficient detail. The object inventory is complete at 19 objects across 6 categories. The primary gaps are the absence of `getpurchaseupdates` by name in the out-of-scope list and the non-elevation of the `analytics.v_ordertoyearanalytics` dependency to a distinct migration risk entry. Three [USER INPUT REQUIRED] placeholders (scope owner, temporal boundary, organisational boundary) are legitimate deferrals matching the reference pattern.

---

## Priority Actions

1. Add `getpurchaseupdates` by name to the out-of-scope objects list with disposition "replaced by direct JDBC incremental extract (rule OB-002); stored procedure not migrated".
2. Add a distinct migration risk entry for `analytics.v_ordertoyearanalytics` cross-domain dependency: the view references `fact.purchase.Package` with a correlated subquery and is owned by the Order product team; migration requires Order team coordination and case-sensitivity awareness.
3. Track the three [USER INPUT REQUIRED] items with explicit owners and target resolution dates before go-live sign-off.
