---
task_id: TASK-GL-001
skill: task-checker-go-live-checklist
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/go_live_checklist.md
reference_file: reference/answers/module_5/codebase/docs/go_live_checklist.md
product: Purchase (inventory_stock)
generated: 2026-09-25
total_score: 95/100
grade: Excellent
---

# TASK-GL-001 Check Report

**Product:** Purchase (inventory_stock)
**Reference:** Purchase (globalpurchase)
**Participant file:** `Inventory_Stock_Project/products/Purchase/current/codebase/docs/go_live_checklist.md`
**Reference file:** `reference/answers/module_5/codebase/docs/go_live_checklist.md`
**Generated:** 2026-09-25

---

## Score Summary

**The go-live checklist Score: 95/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header) | 12 | 100/100 | 12.00 | ✓ |
| 1. Infrastructure | 1. Infrastructure | 12 | 100/100 | 12.00 | ✓ |
| 2. Data | 2. Data | 13 | 94/100 | 12.22 | ✓ |
| 3. Security | 3. Security | 13 | 90/100 | 11.70 | ✓ |
| 4. Pipeline | 4. Pipeline | 13 | 96/100 | 12.48 | ✓ |
| 5. Data Quality | 5. Data Quality | 13 | 89/100 | 11.57 | ✓ |
| 6. BI | 6. BI | 12 | 96/100 | 11.52 | ✓ |
| 7. Documentation | 7. Documentation | 12 | 100/100 | 12.00 | ✓ |
| **Subtotal** | | | | **95.49** | |
| Auto-deducts | | | | **0** | |
| **Total** | | | | **95/100** | |

**Grade: Excellent**

> **Weight calculation:** N = 8, base_weight = floor(100/8) = 12, remainder = 4 → Security (13), Data Quality (13), Pipeline (13), Data (13) each receive +1 from complexity ranking.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| (header) | (header) | exact |
| 1. Infrastructure | 1. Infrastructure | exact |
| 2. Data | 2. Data | exact |
| 3. Security | 3. Security | exact |
| 4. Pipeline | 4. Pipeline | exact |
| 5. Data Quality | 5. Data Quality | exact |
| 6. BI | 6. BI | exact |
| 7. Documentation | 7. Documentation | exact |

**Cross-product note:** Catalog `globalpurchase` → `inventory_stock`; schemas `stg/dim/fact/mart` → `bronze/silver_dim/silver_fact/mart`. All replacements are semantically equivalent and not penalised.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No checkbox items anywhere | −5 pts | No — all 35 items use `- [ ]` format |
| Missing H2 section in reference absent in participant | −5 pts each | No — all 7 H2 sections present |
| No task ID references anywhere | −4 pts | No — CFG-*, DB-*, GRANT-*, DQR-* refs present |
| No verification or test items | −3 pts | No — pipeline/DQ/Security have verification items |
| No security or access control items | −3 pts | No — Section 3 Security is complete |
| Items written as descriptions (≥ 50% non-imperative) | −2 pts/section | No — all items use actionable imperative format |
| No closing readiness statement | −1 pt | No — "Completing all items above..." statement present |

**Total auto-deducts: 0 pts**

---

## Section Feedback

### Header Metadata (12/12 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Content completeness (100/100):**
- Product name in H1: "Go-Live Checklist: Purchase Data Product" ✓
- Total items: 35 checklist items — production-appropriate density ✓
- Closing readiness statement: "Completing all items above constitutes sufficient evidence for production readiness." ✓

**Structure (100/100):**
- H1 present ✓
- Clean markdown ✓

**Strengths:**
- Clear product title and strong closing sign-off statement

---

### 1. Infrastructure → 1. Infrastructure (12/12 pts)

**Criteria scored:** Content (70%), Task ID References (20%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 5/5 (catalog, schemas, cluster policy, workflow+schedule, alerting)
- Checkbox format: 5/5 (100%)
- Key covered: catalog created (CFG-003), 4 schemas, cluster policy (CFG-001), workflow (CFG-002, CFG-009), alerts (CFG-011)
- Cross-product: `inventory_stock` catalog and `bronze/silver_dim/silver_fact/mart` schemas correctly adapted

**Task ID references (100/100):**
- Items with task refs: 5/5 (CFG-003, CFG-001, CFG-002/CFG-009, CFG-011)
- All task IDs are specific config references ✓

**Structure (100/100):**
- H2 present ✓, all checkboxes ✓, all actionable ✓

**Strengths:**
- Perfect task ID coverage; all five infrastructure topics addressed

---

### 2. Data → 2. Data (12.22/13 pts)

**Criteria scored:** Content (70%), Task ID References (20%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 6/6 (calendar dim, supplier sentinel, stock_item sentinel, etl_cutoff init, bronze tables, fact table)
- Checkbox format: 6/6 (100%)
- Uses `silver_dim.date`, `silver_dim.supplier`, `silver_dim.stock_item`, `bronze.etl_cutoff` — all correct product adaptations

**Task ID references (70/100):**
- Items with task refs: 3/6 (DB-007, DB-001–DB-004, DB-008)
- Items 2 and 3 (sentinel rows) and item 4 (etl_cutoff init) lack explicit DB-* task refs
- Task IDs present are specific ✓

**Structure (100/100):** All present ✓

**Gaps:**
- Sentinel row items (supplier, stock_item) and etl_cutoff initialization item lack DB-* task ID references (reference also omits these; pattern is consistent)

**Improvement items:**
- [ ] Optionally add DB task refs to sentinel row items and etl_cutoff initialization

---

### 3. Security → 3. Security (11.70/13 pts)

**Criteria scored:** Content (40%), Task ID References (20%), Verification Step (15%), Principal Names (15%), Structure (10%)

**Content completeness (100/100):**
- Topics covered: 6/6 (GRANTs applied, PII check, scopes created, keys registered, bi-SP verified, etl-SP verified)
- Checkbox format: 6/6 (100%)

**Task ID references (50/100):**
- Items with task refs: 1/6 (only item 1 cites GRANT-001–GRANT-004)
- nb_pii_compliance_check, scope creation, key registration items lack task IDs

**Verification step (100/100):**
- Manual trigger/test: Yes ✓ (bi-service-principal verified)
- Success indicator: Yes ✓ (can SELECT mart views)
- Failure/negative test: Yes ✓ (cannot MODIFY — negative permission check)

**Principal names (100/100):**
- Items naming principals: 2/2 (bi-service-principal, etl-service-principal) ✓
- Permission scopes: SELECT, MODIFY, REFRESH all stated ✓
- Negative permission test: Yes ✓ (cannot MODIFY)

**Structure (100/100):** All present ✓

**Gaps:**
- Only 1/6 security items carries a task ID reference; items 2–6 lack GRANT-* or SEC-* refs

**Improvement items:**
- [ ] Add CFG-007/CFG-008 refs to scope and key items; add GRANT-004 to bi-SP verification item → up to +1.3 pts on Task ID criterion

---

### 4. Pipeline → 4. Pipeline (12.48/13 pts)

**Criteria scored:** Content (75%), Verification Step (15%), Structure (10%)

**Content completeness (100/100):**
- Topics: 5/5 (deploy script, Jobs UI visible, manual trigger, lineage verified, cutoff advanced) ✓
- `bronze.lineage_run` with `was_successful = true` is correct product adaptation of `stg.lineage` with `status = 'success'`

**Verification step (75/100):**
- Manual trigger: Yes ✓ (40%)
- Success indicator: Yes ✓ — lineage shows success (35%)
- Failure test: No — no deliberate pipeline failure item (0%)

**Structure (100/100):** All present ✓

**Gaps:**
- No synthetic pipeline failure test item (e.g., "disconnect JDBC source and verify workflow fails with alert")

**Improvement items:**
- [ ] Add a negative pipeline test item (e.g., inject a transient JDBC error and verify alerts fire) → up to +0.4 pts

---

### 5. Data Quality → 5. Data Quality (11.57/13 pts)

**Criteria scored:** Content (40%), Task ID References (20%), Verification Step (15%), Principal Names (15%), Structure (10%)

**Content completeness (100/100):**
- Topics: 6/6 (DQ config loaded, BLOCKING rules, Informational rules, smoke tests, rejection table, synthetic test) ✓

**Task ID references (70/100):**
- Items with DQR refs: 3/6 (item 2 and 3 have DQR-001/004/005/006 and DQR-002/003)
- Item 1 (yaml loaded), item 4 (smoke tests), item 5 (rejections table), item 6 (synthetic test) lack explicit DQR task IDs

**Verification step (100/100):**
- Manual test: Yes ✓ (synthetic count mismatch = deliberate test trigger)
- Success indicator: Yes ✓ (smoke tests pass)
- Failure test: Yes ✓ (pipeline halts at nb_dq_assertions)

**Principal names (68/100):**
- Items naming principals: 1/1 (etl-service-principal for rejection table) ✓ (50%)
- Permission scope: "writable" is present but less precise than "MODIFY" (30% × 60% = 18%)
- Negative permission test: No dedicated negative test for DQ access ✓ (0%)

**Structure (100/100):** All present ✓

**Gaps:**
- Principal permission scope uses "writable" rather than explicit MODIFY privilege
- DQR task refs missing from 3/6 items

**Improvement items:**
- [ ] Replace "writable by `etl-service-principal`" with "etl-service-principal has MODIFY on `bronze.dq_rejections`" for precision
- [ ] Add DQR task IDs to item 1 (reference to dq_assertions YAML task) and item 6 (TEST-001 or similar)

---

### 6. BI → 6. BI (11.52/12 pts)

**Criteria scored:** Content (75%), Verification Step (15%), Structure (10%)

**Content completeness (100/100):**
- Topics: 5/5 (v_purchase_by_supplier queryable, v_purchase_per_stock_item queryable, analysts SELECT, connection strings updated, sample queries) ✓

**Verification step (75/100):**
- Manual trigger: Yes ✓ (sample queries run)
- Success indicator: Yes ✓ (expected results)
- Failure test: No (no "bi-service-principal cannot SELECT stg tables" negative check)

**Structure (100/100):** All present ✓

**Gaps:**
- BI connection string item references `docs/bi/bi_connections.md` (participant path); reference uses `config/bi_connections.md` — minor path difference, not penalised
- Sample query item lacks the specific file reference (`src/db/queries/bi_sample_queries.sql`) that reference includes
- No negative BI access test

**Improvement items:**
- [ ] Reference specific sample query file in item 5 for better traceability
- [ ] Optionally add a negative BI access check (e.g., confirm bi-SP cannot SELECT silver_fact tables)

---

### 7. Documentation → 7. Documentation (12/12 pts)

**Criteria scored:** Content (90%), Structure (10%)

**Content completeness (100/100):**
- Topics: 5/5 (architecture diagram reviewed, data dictionary covers tables, runbook distributed, secrets docs available, bi_connections distributed) ✓
- `docs/data-dictionary.md` (trainee) vs `docs/data_dictionary.md` (reference) — minor underscore vs hyphen difference, acceptable

**Structure (100/100):** All present ✓

**Strengths:**
- Complete documentation distribution coverage with specific file paths and named audiences (operations team, platform team, BI consumers)

---

## Extra Sections

None — participant's 7 sections map exactly to the reference 7 sections.

---

## Improvement Items

Ordered by impact (highest first):

1. **[Security — Task ID References]** Add GRANT-* refs to scope/key items and bi-SP/etl-SP verification items → up to +1.3 pts
2. **[Data Quality — Principal Names]** Replace "writable" with explicit "MODIFY" privilege in rejection table item → up to +0.7 pts
3. **[Pipeline — Verification]** Add synthetic pipeline failure test item → up to +0.5 pts
4. **[Data — Task ID References]** Add DB-* refs to sentinel row and etl_cutoff init items → up to +0.4 pts
5. **[BI — Verification]** Add negative BI access check item → up to +0.3 pts

---

## Priority Actions

1. Add task ID references to Security items 2–6 (scope creation → CFG-007, key registration → CFG-007, bi-SP verification → GRANT-004, etl-SP verification → GRANT-001/003) → up to **+1.3 pts**
2. Strengthen DQ rejection table item: replace "writable by etl-service-principal" with "etl-service-principal has MODIFY on bronze.dq_rejections (GRANT-003)" → up to **+0.7 pts**
3. Add synthetic pipeline failure test item (e.g., inject JDBC error, verify alert fires) → up to **+0.5 pts**

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing sections, no task refs, or no verification items |
| 0–44 | Incomplete | Major sections absent or no checkbox format used |
