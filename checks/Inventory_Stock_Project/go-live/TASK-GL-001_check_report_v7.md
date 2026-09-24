---
task_id: TASK-GL-001
skill: migvisor-task-checker-go-live-checklist
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/go_live_checklist.md
reference_file: reference/answers/module_5/codebase/docs/go_live_checklist.md
product: Purchase
generated: 2026-09-24
total_score: 95/100
grade: Excellent
---

# TASK-GL-001 Check Report — Go-Live Checklist
_Purchase | 2026-09-24_

## Score Summary

**Go-Live Checklist Score: 95/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 12 | 100/100 | 12.0 | ✓ |
| 1. Infrastructure | 12 | 100/100 | 12.0 | ✓ |
| 2. Data | 13 | 94/100 | 12.2 | ✓ |
| 3. Security | 13 | 90/100 | 11.7 | ✓ |
| 4. Pipeline | 13 | 96/100 | 12.5 | ✓ |
| 5. Data Quality | 13 | 92/100 | 12.0 | ✓ |
| 6. BI | 12 | 96/100 | 11.5 | ✓ |
| 7. Documentation | 12 | 100/100 | 12.0 | ✓ |
| **Subtotal** | | | **96.0** | |
| Auto-deducts | | | **−1** | |
| **Total** | | | **95/100** | |

**Grade: Excellent**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | (header block) | exact |
| 1. Infrastructure | 1. Infrastructure | exact |
| 2. Data | 2. Data | exact |
| 3. Security | 3. Security | exact |
| 4. Pipeline | 4. Pipeline | exact |
| 5. Data Quality | 5. Data Quality | exact |
| 6. BI | 6. BI | exact |
| 7. Documentation | 7. Documentation | exact |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No checkbox items anywhere in document | −5 pts | No — all items use `- [ ]` format |
| Missing H2 section present in reference but absent | −5 pts each | No — all 7 sections present |
| No task ID references anywhere in document | −4 pts | No — CFG-001, CFG-002, CFG-003, DB-007, GRANT-001–GRANT-004, DQR-001–DQR-006 all present |
| No verification or test items anywhere | −3 pts | No — bi-service-principal verified, synthetic DQ failure test present |
| No security or access control items anywhere | −3 pts | No — full Security section with principals and GRANTs |
| Items written as descriptions not actions (≥50% per section) | −2 pts per section | No — all items use imperative verbs |
| No closing readiness or sign-off statement | −1 pt | No — closing statement present |

**Note:** Minor −1 pt conservative adjustment applied for the Security section's lower task-ID density (only 1 of 6 items carries a GRANT-* reference code) compared to the reference pattern expectation.

**Total auto-deducts: −1**

---

## Section Feedback

### Header Metadata (12/12 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Strengths:**
- H1 title "Go-Live Checklist: Purchase Data Product" clearly names the product.
- 38 checkbox items present across 7 sections — sufficient density for production readiness.
- Closing readiness statement ("Completing all items above constitutes sufficient evidence for production readiness.") matches the reference exactly.

**Gaps:**
- None significant.

---

### 1. Infrastructure → Infrastructure (12/12 pts)

**Criteria scored:** Content (70%), Task ID References (20%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 5/5 (catalog creation, schema creation, cluster policy, workflow deployment, alerting)
- All items in checkbox format: 5/5 (100%)
- Key covered topics: Unity Catalog (`inventory_stock`), four schemas (`bronze`, `silver_dim`, `silver_fact`, `mart`), cluster policy (CFG-001), workflow schedule (CFG-002, CFG-009), alert recipients (CFG-011)
- Cross-product naming: `inventory_stock` catalog with medallion-style schemas replaces `globalpurchase` with stg/dim/fact — functionally equivalent, no penalty

**Task ID references (100/100):**
- Items with task ID refs: 5/5 (CFG-003, CFG-001, CFG-002+CFG-009, CFG-011)
- Task IDs are specific: Yes

**Structure (100/100):**
- H2 present: Yes
- All items are checkboxes: Yes
- Items are actionable imperatives: Yes

**Strengths:**
- Every Infrastructure item carries a CFG task reference.
- Medallion schema naming (`bronze/silver_dim/silver_fact/mart`) is well-documented.

**Gaps:**
- None.

---

### 2. Data → Data (12/13 pts)

**Criteria scored:** Content (70%), Task ID References (20%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 6/6 (calendar dimension, supplier sentinel, stock_item sentinel, etl_cutoff init, staging tables, fact table MERGE)
- All items in checkbox format: 6/6 (100%)

**Task ID references (70/100):**
- Items with task ID refs: 3/6 (DB-007, DB-001 through DB-004, DB-008)
- Missing task IDs: sentinel row items and etl_cutoff item lack task references
- Task IDs are specific: Yes for those present
- Score: (3/6)×60% + (3/3)×40% = 30% + 40% = 70%

**Structure (100/100):**
- H2 present: Yes
- All items are checkboxes: Yes
- Items are actionable imperatives: Yes

**Strengths:**
- `bronze.etl_cutoff` initialized with `HISTORY_ANCHOR_DATE` for entity `fact_purchase` — specific and actionable.
- Sentinel row IDs (wwi_supplier_id=0, wwi_stock_item_id=0) are explicitly stated.

**Gaps:**
- Sentinel row insertion items (silver_dim.supplier, silver_dim.stock_item) and etl_cutoff item lack DB-* task ID references.

**Improvement items:**
- [ ] Add task ID references (e.g., DB-002, DB-003) to the sentinel row and etl_cutoff initialization items.

---

### 3. Security → Security (12/13 pts)

**Criteria scored:** Content (40%), Task ID References (20%), Verification Step (15%), Principal Names (15%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 6/6 (GRANT scripts applied, PII compliance check, dev/prod scopes created, keys registered, bi-service-principal verified, etl-service-principal verified)
- All items in checkbox format: 6/6 (100%)

**Task ID references (50/100):**
- Items with task ID refs: 1/6 ("GRANT-001 through GRANT-004 applied")
- Other items reference notebooks (nb_pii_compliance_check) but not GRANT-* task IDs individually
- Score: (1/6)×60% + (1/1)×40% = 10% + 40% = 50%

**Verification step (100/100):**
- Manual trigger / test item present: Yes — "bi-service-principal verified: can SELECT mart views, cannot MODIFY"
- Success indicator item present: Yes — "can SELECT"
- Failure/negative test item present: Yes — "cannot MODIFY" functions as a negative permission check

**Principal names (100/100):**
- Items naming specific principals: 2/2 (bi-service-principal, etl-service-principal)
- Principals have permission scopes: Yes (SELECT, MODIFY, REFRESH explicitly stated)
- Negative permission test present: Yes ("cannot MODIFY")

**Structure (100/100):**
- H2 present: Yes
- All items are checkboxes: Yes
- Items are actionable imperatives: Yes

**Strengths:**
- Both service principals verified with explicit privilege scopes (SELECT+MODIFY+REFRESH for ETL; SELECT-only for BI).
- Negative permission test ("cannot MODIFY") is present.
- Dev and prod scope names (`inventory-stock-dev`, `inventory-stock-prod`) are named explicitly.

**Gaps:**
- Task ID density is low: only the first GRANT item carries task references. Items for PII check, scope creation, and key registration lack task IDs.

**Improvement items:**
- [ ] Add GRANT-002, GRANT-003, GRANT-004 task IDs to scope creation and key registration items where applicable.

---

### 4. Pipeline → Pipeline (12/13 pts)

**Criteria scored:** Content (75%), Verification Step (15%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 5/5 (deploy script, Databricks Jobs UI visibility, manual end-to-end test, lineage status, watermark advance)
- All items in checkbox format: 5/5 (100%)
- Cross-product: `bronze.lineage_run was_successful = true` ≡ `stg.lineage status = 'success'` — same functional check

**Verification step (75/100):**
- Manual trigger / test item present: Yes → 40%
- Success indicator item present: Yes (lineage_run shows success) → 35%
- Failure/negative test item present: No → 0%

**Structure (100/100):**
- H2 present: Yes
- All items are checkboxes: Yes
- Items are actionable imperatives: Yes

**Strengths:**
- Full 5-item pipeline checklist covering deployment through lineage validation.
- Watermark advancement check confirms state is properly persisted after test run.

**Gaps:**
- No explicit failure scenario test (e.g., what happens if the pipeline run fails — no negative test item).

**Improvement items:**
- [ ] Add a failure-scenario test item (e.g., "verify pipeline alerts fire on a deliberately failed run") to reach 100% on verification criterion.

---

### 5. Data Quality → Data Quality (12/13 pts)

**Criteria scored:** Content (55%), Task ID References (20%), Verification Step (15%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 6/6 (config loaded, BLOCKING rules, Informational rules, smoke tests, rejection table, synthetic failure)
- All items in checkbox format: 6/6 (100%)

**Task ID references (60/100):**
- Items with task ID refs: 2/6 (DQR-001/DQR-004/DQR-005/DQR-006 BLOCKING item; DQR-002/DQR-003 Informational item)
- Other 4 items lack task IDs
- Score: (2/6)×60% + (2/2)×40% = 20% + 40% = 60%

**Verification step (100/100):**
- Manual trigger / test item present: Yes (synthetic count mismatch test) → 40%
- Success indicator item present: Yes (nb_dq_smoke_tests passes) → 35%
- Failure/negative test item present: Yes (synthetic failure verifying pipeline halts at nb_dq_assertions) → 25%

**Structure (100/100):**
- H2 present: Yes
- All items are checkboxes: Yes
- Items are actionable imperatives: Yes

**Strengths:**
- Synthetic failure test is present with specific mechanism (count mismatch) and expected behavior (pipeline halts).
- BLOCKING vs Informational severity distinction documented with specific DQR IDs.

**Gaps:**
- 4 out of 6 items lack DQR task ID references (config load, smoke tests, rejection table, synthetic failure items).

**Improvement items:**
- [ ] Add task ID references to the DQ config load item and rejection table item.

---

### 6. BI → BI (12/12 pts)

**Criteria scored:** Content (75%), Verification Step (15%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 5/5 (v_purchase_by_supplier queryable, v_purchase_per_stock_item queryable, purchase-analysts SELECT, connection strings updated, sample queries)
- All items in checkbox format: 5/5 (100%)
- Cross-product: trainee references `docs/bi/bi_connections.md` vs reference `config/bi_connections.md` — same functional document

**Verification step (75/100):**
- Manual trigger / test item present: Yes (sample queries return expected results) → 40%
- Success indicator item present: Yes (results return expected) → 35%
- Failure/negative test item present: No → 0%

**Structure (100/100):**
- H2 present: Yes
- All items are checkboxes: Yes
- Items are actionable imperatives: Yes

**Strengths:**
- Both mart views listed explicitly with their principal (`bi-service-principal`) and group (`purchase-analysts`).
- Connection strings reference the correct product-specific document (`docs/bi/bi_connections.md`).

**Gaps:**
- No BI failure scenario or negative access test.

---

### 7. Documentation → Documentation (12/12 pts)

**Criteria scored:** Content (90%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 5/5 (architecture diagram, data dictionary, runbook distributed, secrets docs, BI connections)
- All items in checkbox format: 5/5 (100%)
- Minor file path variations (docs/data-dictionary.md vs docs/data_dictionary.md, docs/runbook.md vs docs/pipeline_runbook.md) are cross-product differences — no penalty

**Structure (100/100):**
- H2 present: Yes
- All items are checkboxes: Yes
- Items are actionable imperatives: Yes

**Strengths:**
- All five reference documentation topics present.
- Distribution targets are correctly specified (operations team, platform team, BI consumers).

**Gaps:**
- None.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Low task ID density in Security section (only 1/6 items carry GRANT-* refs) | Security | +2 pts |
| 2 | Missing task IDs on sentinel row + etl_cutoff items | Data | +1 pt |
| 3 | Low task ID density in Data Quality (config load, rejection table items lack DQR refs) | Data Quality | +1 pt |
| 4 | No pipeline failure-scenario test item | Pipeline | +1 pt |
| 5 | No BI negative access test | BI | <1 pt |

---

## Priority Actions

1. **Add task ID refs to Security items** — Tag PII check, scope creation, and key registration items with GRANT-002 through GRANT-004 references. Worth up to **+2 pts**.
2. **Add DB-* task IDs to Data sentinel row items** — Tag `silver_dim.supplier` and `silver_dim.stock_item` sentinel row items with their DB task codes. Worth up to **+1 pt**.
3. **Add a pipeline failure test item** — Include a negative test item verifying the pipeline alert fires on deliberate failure. Worth up to **+1 pt**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing sections, no task refs, or no verification items |
| 0–44 | Incomplete | Major sections absent or no checkbox format used |
