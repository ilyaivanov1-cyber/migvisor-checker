---
task_id: TASK-SCOPE-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/input/product-scope.md
reference_file: reference/answers/module_2/0 product-scope.md
checked_at: 2026-09-24T00:00:00Z
sections_evaluated: 9
total_score: 91/100
grade: Excellent
identical_to_reference: false
---

# Task Check Report — product-scope
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: `Inventory_Stock_Project/products/Purchase/input/product-scope.md` — explicit path
- Reference file: `reference/answers/module_2/0 product-scope.md` — explicit path
- Product: Purchase — from H1 heading
- Sections in reference: 9 | Sections in participant: 9 (matched: 9)
- Point weights: auto-calculated — §1:7, §2:10, §3:25, §4:12, §5:10, §6:10, §7:8, §8:8, §9:10

---

## Score Summary

**The product scope Score: 91**

| Section | Weight | Score | Status |
|---|---|---|---|
| §1 Identity | 7 | 7 | ✓ |
| §2 Description | 10 | 9 | ✓ |
| §3 Objects in Scope | 25 | 23 | ✓ |
| §4 Out-of-Scope Objects | 12 | 11 | ✓ |
| §5 Consumers | 10 | 9 | ✓ |
| §6 Calculation Surface | 10 | 9 | ✓ |
| §7 Boundaries | 8 | 8 | ✓ |
| §8 Priority and Sequencing | 8 | 8 | ✓ |
| §9 Known Migration Risks | 10 | 7 | ⚠ |
| **Total** | **100** | **91** | |

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### §1 Identity (7/7)

**Coverage:** All identity fields present — product name, parent project, scope owner (correctly marked `[USER INPUT REQUIRED]`), discovery mode, plan stage. `[DEFERRED]`: scope owner.
**Specificity:** Full discovery mode string with base node named explicitly.
**Technical accuracy:** Parent project name differs from reference (`Inventory_Stock_Project` vs `GlobalPurchase_Project`) — this is the correct project name for this trainee workspace, not an error.
**Issues/gaps flagged:** n/a for identity section.
**Structure:** Table format consistent with reference ✓.

**Improvement items:**
- None — full marks.

---

### §2 Description (9/10)

**Coverage:** Domain covered (procurement order domain), architecture (SSIS→Databricks), SSIS bug called out, dimension ownership model (SCD-2 read dependencies) clearly articulated.
**Specificity:** Names `wideworldimportersdw.fact.purchase`, SQL Server 2014, Databricks Delta Lake, `migratestagedpurchasedata`.
**Technical accuracy:** Source and target systems correctly identified, direction correct.
**Issues/gaps flagged:** SSIS staging-truncation bug explicitly called out in description ✓.
**Structure:** Prose form consistent with reference ✓.

**Improvement items:**
- [ ] Minor: description could note the catalog name (`inventory_stock`) as the reference names `globalpurchase` — currently absent from description prose (+1 pt).

---

### §3 Objects in Scope (23/25)

**Coverage:** 6 subsections vs reference's 7. Trainee has 3.1–3.6; reference has 3.5 "Analytics Views" which notes no analytics views are owned. 19 objects covered across 6 categories consistent with domain notes. All critical objects present: fact.purchase (11 cols named), 3 conformed dimensions, 7 integration staging objects, 1 sequence, 5 SSIS pipeline items, 2 BI reports.
**Specificity:** Named objects with types, roles, schema paths, and column lists for fact.purchase.
**Technical accuracy:** Correct source system. SSIS bug documented inline in 3.5 (pipeline truncation item).
**Issues/gaps flagged:** SSIS bug called out with specific wrong table name (`Integration.Order_Staging`) ✓. configuration_reseedetl scope uncertainty noted ✓.
**Structure:** 6 subsections with tables throughout. Missing the "3.5 Analytics Views" subsection (reference uses it to explicitly note no analytics views are owned by Purchase).

**Improvement items:**
- [ ] Add a brief §3.5 Analytics Views note stating no analytics views are owned by Purchase — `analytics.v_ordertoyearanalytics` reads `fact.purchase` but is cross-domain and out of scope. This recovers ~2 pts.

---

### §4 Out-of-Scope Objects (11/12)

**Coverage:** 11+ exclusion entries covering: cross-domain facts, other product staging/procedures, dimension ETL procedures, unrelated dimensions, analytics views, application config procedures, reseed utilities, SSMS artifacts. Comparable breadth to reference (8–9 categories).
**Specificity:** All entries include reasons for exclusion.
**Technical accuracy:** Correctly identifies which cross-domain objects to exclude.
**Issues/gaps flagged:** Partial exclusion pattern for `configuration_reseedetl` called out ✓.
**Structure:** Table format with Object and Reason columns ✓.

**Improvement items:**
- [ ] Minor: could explicitly list OLTP source-side procedures (`wideworldimporters.integration.getpurchaseupdates`) as out of scope as the reference does (+1 pt).

---

### §5 Consumers (9/10)

**Coverage:** All 3 reference consumers documented: `wwidw purchase and sale per stockitem dynamic`, `wwidw-ordered-by-supplier`, `analytics.v_ordertoyearanalytics`. Trainee also includes `integration.migratestagedpurchasedata` as an internal ETL consumer — extra content, not penalised.
**Specificity:** Use cases, business questions answered, and consumption method documented for each consumer.
**Technical accuracy:** Cross-domain dependency on Sales_Orders correctly identified. Coordination requirement stated.
**Issues/gaps flagged:** Analytics view cross-domain risk and coordination requirement called out ✓.
**Structure:** Table format ✓. Extra ETL consumer row adds value.

**Improvement items:**
- [ ] Minor: differentiate "downstream BI consumer" from "ETL control dependency" more explicitly for the internal consumer (+1 pt).

---

### §6 Calculation Surface (9/10)

**Coverage:** 4 calculation areas documented: staging merge procedure (SCD-2 key resolution), ETL cutoff watermarking, lineage key generation (SEQUENCE→IDENTITY redesign), staging truncation fix. Reference covers same 3+1 areas.
**Specificity:** Named procedures, specific SCD-2 pattern, MERGE INTO replacement noted.
**Technical accuracy:** Direction correct (describes source-side calculations that must be reimplemented).
**Issues/gaps flagged:** No scalar UDFs or analytics views owned — explicitly stated ✓.
**Structure:** Bullet-point prose consistent with reference ✓.

**Improvement items:**
- [ ] Minor: could state the `COALESCE(..., 0)` fallback sentinel pattern as a key calculation detail (+1 pt).

---

### §7 Boundaries (8/8)

**Coverage:** All 6 boundary rows present — temporal (deferred), organizational (deferred), system source, system target, ETL orchestration source, ETL orchestration target.
**Specificity:** Named source database (`wideworldimportersdw`, SQL Server 2014), named target catalog and layer architecture (`inventory_stock`, bronze/silver/gold).
**Technical accuracy:** `[USER INPUT REQUIRED]` for temporal and organizational boundaries consistent with reference pattern ✓.
**Issues/gaps flagged:** Temporal boundary deferred to scope owner ✓.
**Structure:** Table format ✓. Full marks.

**Improvement items:**
- None.

---

### §8 Priority and Sequencing (8/8)

**Coverage:** All required fields — Priority (PRIMARY), rationale, dependencies (dimension products must load before fact), successor products.
**Specificity:** Named dependency on supplier and stock_item dimension products. Names specific workflow task dependency requirement.
**Technical accuracy:** ✓.
**Issues/gaps flagged:** Cross-product runtime dependency explicitly flagged ✓.
**Structure:** Table format ✓. Full marks.

**Improvement items:**
- None.

---

### §9 Known Migration Risks (7/10)

**Coverage:** 7 risks documented vs 8 in reference. Risks 1–7 all present and match reference risks 1–7. Reference risk #8 (`analytics.v_ordertoyearanalytics` cross-domain BI report requiring coordinated cutover with Order product) is absent from this section (though the analytics view migration risk is mentioned in §5 Consumers).
**Specificity:** Bugs named with specific wrong table names, object names in angle-bracket notation, T-SQL objects named.
**Technical accuracy:** All risks correctly framed with correct implications.
**Issues/gaps flagged:** All 7 documented risks include implication statements ✓.
**Structure:** Numbered table with Risk and Implication columns ✓.

**Improvement items:**
- [ ] Add Risk #8: `analytics.v_ordertoyearanalytics` cross-domain BI report requires coordinated cutover with both the Order and Sales_Orders product teams — cannot be rebuilt by Purchase alone. Moving this from §5 prose into §9 risks table recovers ~3 pts.

---

## Extra Sections (not in reference)

None — participant has exactly the same 9 sections as the reference.

## Approach Notes

- Participant uses `Inventory_Stock_Project` as parent project (vs reference `GlobalPurchase_Project`) and `inventory_stock` as catalog name (vs `globalpurchase`). This reflects the correct workspace for this trainee and is not penalised.
- §3 uses 6 subsections vs reference's 7 (omitting analytics views subsection); content is equivalent — no deduction per approach policy.
- §5 includes an extra consumer (`integration.migratestagedpurchasedata` as ETL control dependency) not in reference — noted as extra value, not penalised.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. §9 Known Migration Risks — Coverage — add Risk #8 for analytics.v_ordertoyearanalytics cross-domain cutover requirement → +3 pts
2. §3 Objects in Scope — Structure — add §3.5 Analytics Views subsection noting no analytics views are Purchase-owned, and that analytics.v_ordertoyearanalytics is cross-domain → +2 pts
3. §2 Description — Specificity — add target catalog name (`inventory_stock`) to the description prose → +1 pt

---

## Next Step

You can proceed to the next task.
