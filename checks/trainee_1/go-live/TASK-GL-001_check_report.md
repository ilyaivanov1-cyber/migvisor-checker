---
task_id: TASK-GL-001
skill: task-checker-go-live-checklist
participant_file: trainees/trainee_1/go_live_checklist.md
reference_file: reference/go_live_checklist.md
product: Sales_Orders
generated: 2026-09-03
total_score: 40/100
grade: Incomplete
---

# TASK-GL-001 Check Report

**Product:** Sales_Orders Pipeline
**Reference:** Purchase Data Product
**Participant file:** `trainees/trainee_1/go_live_checklist.md`
**Reference file:** `reference/go_live_checklist.md`
**Generated:** 2026-09-03

---

## Score Summary

**The go-live checklist Score: 40/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 12 | 88/100 | 10.56 | ✓ Pass |
| 1. Infrastructure | 1. Infrastructure | 12 | 30/100 | 3.60 | ✗ Missing |
| 2. Data | 2. Data | 13 | 40/100 | 5.20 | ✗ Below threshold |
| 3. Security | 3. Security | 13 | 46/100 | 5.98 | ⚠ Partial |
| 4. Pipeline | 4. Pipeline | 13 | 60/100 | 7.80 | ⚠ Partial |
| 5. Data Quality | 5. Data Quality | 13 | 5/100 | 0.65 | ✗ Missing |
| 6. BI | 6. BI | 12 | 68/100 | 8.16 | ⚠ Partial |
| 7. Documentation | 7. Documentation | 12 | 64/100 | 7.68 | ⚠ Partial |
| **Subtotal** | | | | **49.63** | |
| Auto-deducts | | | | **−10.0** | |
| **Total** | | | | **40/100** | |

**Grade: Incomplete**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | H1 + preamble lines | exact |
| 1. Infrastructure | [MISSING] | missing |
| 2. Data | `## Section 5: Data` (items 21–22) | semantic (partial) |
| 3. Security | `## Section 2: Security & Compliance` | semantic |
| 4. Pipeline | `## Section 4: Operations` (item 17) + `## Section 3: Testing` (item 11) | semantic (split across sections) |
| 5. Data Quality | [MISSING] | missing |
| 6. BI | items 19, 23, 24 in Sections 4 & 5 | semantic (scattered, no dedicated section) |
| 7. Documentation | items 14–15 in Section 4 + item 7 in Section 2 | semantic (scattered) |
| *(not in reference)* | `## Section 1: Pending Decision Gates` | extra |
| *(not in reference)* | `## Section 3: Testing` | extra |
| *(not in reference)* | `## Final approval` | extra |

**Note:** The participant reorganised the checklist around a delivery-team workflow (gates → security → testing → operations → data → sign-off) rather than mirroring the reference's technical readiness categories (infrastructure → data → security → pipeline → DQ → BI → docs). This is a valid structural choice but it leaves Infrastructure and Data Quality with no dedicated section.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No checkbox items anywhere | −5 pts | **No** — ☐ table cells used throughout |
| Missing H2: 1. Infrastructure | −5 pts | **Yes — no dedicated Infrastructure section** |
| Missing H2: 5. Data Quality | −5 pts | **Yes — no dedicated Data Quality section** |
| No task ID references anywhere | −4 pts | **No** — TASK-SEC-003, TASK-TEST-007, CX-P04/P05/DQ-01, CON-SEC-001 present |
| No verification/test items anywhere | −3 pts | **No** — Section 3 Testing contains items 9–13 |
| No security or access control items | −3 pts | **No** — Section 2 Security & Compliance present |
| Items written as descriptions, not actions | −2 pts/section (max −6) | **No** — all items use actionable imperative or verifiable-state phrasing |
| No closing readiness statement | −1 pt | **No** — preamble + Final approval table present |

**Total auto-deducts: −10 pts**

---

## Section Feedback

### Header Metadata — 88/100 (weight 12 → 10.56 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product name in H1 | 40% | 95 | "Sales_Orders Pipeline" immediately clear |
| Item count stated or derivable | 20% | 50 | 24 items countable; not explicitly stated in header |
| Closing readiness statement | 40% | 100 | Preamble: "All items must be completed and signed off before promoting `nightly_etl_main` to production" + Final approval sign-off table |

**Strengths:**
- Preamble includes a clear production gate statement naming the specific workflow (`nightly_etl_main`)
- Task/constraint IDs tagged in preamble line (`TASK-DOCS-004 | CON-SEC-001, NFR-MAINT`)
- Final approval table with named roles adds accountability structure absent from reference

**Gaps:**
- Total item count not explicitly stated

---

### 1. Infrastructure → [MISSING] — 30/100 (weight 12 → 3.60 pts)

**Criteria scored:** Content (70%), Task ID References (20%), Structure (10%)

No dedicated Infrastructure section exists. Items 17 (workflow deployed) and 18 (monitoring and alerting) in Section 4: Operations cover 2 of 5 reference topics. Item 20 (Delta table retention policies) adds a storage configuration item not present in the reference Infrastructure section.

**Content completeness (43/100):**
- Topics covered: 2/5 (workflow deployed, alerting configured)
- Missing topics: Unity Catalog creation, schema creation (stg/dim/fact/mart), cluster policy application
- Items in checkbox format (☐ table cells): partial credit 50%

**Task ID references (0/100):**
- Items 17, 18 carry no CFG-* task IDs

**Structure (0/100):**
- No dedicated `## Infrastructure` heading

**Improvement items:**
- [ ] Add `## Infrastructure` section covering: catalog created (`CREATE CATALOG globalorders`), all schemas created (stg/dim/fact/mart), cluster/compute policy applied, workflow deployed and scheduled, alert recipients configured
- [ ] Reference CFG-* task IDs for infrastructure items (e.g., CFG-003 catalog creation, CFG-001 cluster policy)

---

### 2. Data → `## Section 5: Data` — 40/100 (weight 13 → 5.20 pts)

**Criteria scored:** Content (55%), Task ID References (20%), Verification Step (15%), Structure (10%)

**Content completeness (38/100):**
- Topics covered: ~2/6 (dim.date populated ✓; historical load implies staging setup and fact table MERGE ready ✓ partial)
- Missing: dimension sentinel/default rows (dim.customer key=0, dim.stock_item key=0, etc.), stg.etl_cutoff initialized with history anchor date, staging tables confirmed empty on first run
- Items in checkbox format: ☐ → 50%

**Task ID references (0/100):**
- No DB-* task IDs on any data bootstrap items

**Verification step (75/100):**
- Manual trigger: item 21 "full historical load completed" → 100
- Success indicator: "completed successfully" → 100
- Failure test: absent → 0

**Structure (83/100):**
- H2 present: Yes (`## Section 5: Data`) → 100
- Items are checkboxes: ☐ → 70
- Items are actionable: Yes → 80

**Strengths:**
- dim.date coverage range explicitly stated ("through at least today + 5 years") — more specific than reference
- Full historical load item goes beyond reference scope (reference focuses on first-run readiness, not historical backfill)

**Gaps:**
- No sentinel/default row items for any dimension table
- No stg.etl_cutoff initialization item
- No confirmation that staging tables are empty before first production run

**Improvement items:**
- [ ] Add: dimension default/sentinel rows inserted (key=0 or equivalent) for each SCD-2 dimension
- [ ] Add: etl_cutoff / watermark control table seeded with history anchor date per entity
- [ ] Add: staging tables exist and are empty on first run (explicit verification)
- [ ] Add DB-* task ID references to data bootstrap items

---

### 3. Security → `## Section 2: Security & Compliance` — 46/100 (weight 13 → 5.98 pts)

**Criteria scored:** Content (40%), Task ID References (20%), Verification Step (15%), Principal Names (15%), Structure (10%)

**Content completeness (56/100):**
- Topics covered: ~3.5/6 (PII check ✓, grants/access control ✓ via column masks + RLS, secrets provisioned ✓)
- Missing: named service principal verification with explicit permission scopes, negative permission test (bi principal cannot MODIFY)
- Items in checkbox format: ☐ → 50%

**Task ID references (52/100):**
- Items with task IDs: 1/5 (item 4: TASK-SEC-003)
- Task ID is specific: Yes

**Verification step (28/100):**
- Manual test item: absent (no "run and verify" step)
- Success indicator: item 4 "passed" → 80
- Failure/negative test: absent → 0

**Principal names (0/100):**
- No items name specific service principals (e.g., `sales-etl-sp`, `sales-bi-sp`, or equivalent)
- No permission-scope notation (cannot MODIFY, can SELECT, etc.)
- No negative permission test

**Structure (87/100):**
- H2 present: Yes (`## Section 2: Security & Compliance`) → 100
- Items are checkboxes: ☐ → 70
- Items are actionable: Yes → 90

**Strengths:**
- Column-level masking (dim.customer PII columns) and row-level security (RLS on facts) are stronger security controls than reference's grant-only approach
- Item 8 ("no credentials hard-coded") is a good shift-left security check
- TASK-SEC-003 task ID reference demonstrates traceability

**Gaps:**
- No named service principals — items refer to "Security Lead" / "DE Team" (owners) rather than the actual principals being checked
- No negative permission test (e.g., verify BI principal cannot write to fact table)
- Only 1 of 5 items carries a task ID

**Improvement items:**
- [ ] Add specific service principal verification items: `<etl-sp>` can SELECT+MODIFY dim/fact/mart; `<bi-sp>` can SELECT mart views, cannot MODIFY
- [ ] Add a negative permission test: verify that `<bi-sp>` cannot INSERT/UPDATE/DELETE fact or dim tables
- [ ] Add GRANT task IDs (e.g., GRANT-001 through GRANT-00N) to access control items

---

### 4. Pipeline → `## Section 4: Operations` + `## Section 3: Testing` — 60/100 (weight 13 → 7.80 pts)

**Criteria scored:** Content (75%), Verification Step (15%), Structure (10%)

**Content completeness (57/100):**
- Topics covered: 3/5 (deploy_workflow.sh ✓ item 17; workflow visible in UI implied by deployment ✓; end-to-end test ✓ item 11)
- Missing: explicit lineage status check (`stg.lineage.status = 'success'` or equivalent after test run); watermark/cutoff advancement verified after test run
- Items in checkbox format: ☐ → 50%

**Verification step (65/100):**
- Manual trigger: item 11 (TASK-TEST-007 end-to-end test) → 100
- Success indicator: item 11 "passed" → 70 (no explicit lineage/cutoff success state check)
- Failure test: absent → 0

**Structure (77/100):**
- H2 present: Split — ## Section 4: Operations + ## Section 3: Testing → 70
- Items are checkboxes: ☐ → 70
- Items are actionable: Yes → 90

**Strengths:**
- End-to-end pipeline test (TASK-TEST-007) with a traceable task ID is a strong pipeline verification item
- item 16 (CI/CD pipeline tested) goes beyond the reference scope
- Performance benchmark item (item 12) with explicit SLAs (≤4h pipeline, ≤5s p95 mart query) adds operational rigor

**Gaps:**
- No explicit "stg.lineage (or equivalent run log) shows status=success" item after test run
- No explicit "watermark/cutoff table advanced after test run" item — both are critical indicators that the pipeline committed successfully

**Improvement items:**
- [ ] Add: run log / lineage table shows `status = 'success'` for manual test run
- [ ] Add: watermark / etl_cutoff table shows advanced timestamp after manual test run

---

### 5. Data Quality → [MISSING] — 5/100 (weight 13 → 0.65 pts)

**Criteria scored:** Content (55%), Task ID References (20%), Verification Step (15%), Structure (10%)

No dedicated Data Quality section exists. The only DQ reference in the document is CX-DQ-01 in the Pending Decision Gates table (business DQ thresholds TBD). There are no DQ assertion configuration items, no severity level checks, no rejection table verification, and no synthetic failure test anywhere in the checklist.

**Content completeness (5/100):**
- Topics covered: ~0/6 — CX-DQ-01 acknowledged as pending but no actionable DQ readiness items
- Missing: DQ assertion config loaded, blocking rules enabled, informational rules enabled, DQ smoke test passes, rejection table exists and writable, synthetic DQ failure test

**Task ID references (0/100):** None

**Verification step (0/100):** No DQ test items

**Structure (0/100):** No H2 heading

**Gaps:**
- Entire DQ category absent from actionable checklist
- No check that DQ assertion configuration is loaded for production
- No check that blocking vs informational severity is correctly applied
- No synthetic failure test (introduce a count mismatch, verify pipeline halts)
- No verification that `dq_rejections` (or equivalent) table is writable

**Improvement items:**
- [ ] Add `## Data Quality` section with the following items:
  - [ ] DQ assertion config file loaded and all rules enabled
  - [ ] Blocking-severity rules verified (row count, FK integrity, or equivalent)
  - [ ] Informational-severity rules verified (orphan keys, or equivalent)
  - [ ] DQ smoke test notebook passes on populated catalog
  - [ ] Rejection/violations table exists and is writable by ETL service principal
  - [ ] Synthetic failure test: introduce a deliberate mismatch, verify pipeline halts on blocking rule

---

### 6. BI → items 19, 23, 24 (scattered) — 68/100 (weight 12 → 8.16 pts)

**Criteria scored:** Content (60%), Verification Step (15%), Principal Names (15%), Structure (10%)

**Content completeness (85/100):**
- Topics covered: ~5/5 (mart views queryable via "9 BI reports reconnected" ✓; BI user access implied by reconnection ✓; connection strings updated ✓ item 19; data accuracy validated ✓ item 24)
- Items in checkbox format: ☐ → 50%

**Verification step (68/100):**
- Manual test: item 24 (Power BI owners validated data accuracy vs legacy) → 100
- Success indicator: "validated" → 80
- Failure/negative test: absent → 0

**Principal names (0/100):**
- Items 23, 24 reference "BI Team", "Power BI report owners" (roles/teams, not service principals)
- No items naming specific BI service principals or user groups with explicit SELECT grant
- No negative permission test for BI principals

**Structure (67/100):**
- No dedicated `## BI` section; items split across Sections 4 and 5 → 50
- Items are checkboxes: ☐ → 70
- Items are actionable: Yes → 80

**Strengths:**
- Item 23 ("All 9 BI reports reconnected to Databricks SQL endpoint") has a concrete count (9 reports) — more specific than reference
- Item 24 (Power BI owners validated data accuracy vs legacy system) is a business sign-off step absent from the reference — excellent addition

**Gaps:**
- No named service principal (e.g., `sales-bi-sp` or equivalent) with explicit SELECT-only scope
- Items split across two unrelated sections — no dedicated BI section

**Improvement items:**
- [ ] Add a named BI service principal verification item: `<bi-sp>` can query all mart views; cannot write
- [ ] Consider consolidating BI items into a dedicated `## BI` section

---

### 7. Documentation → items 14–15, 7 (scattered) — 64/100 (weight 12 → 7.68 pts)

**Criteria scored:** Content (90%), Structure (10%)

**Content completeness (64/100):**
- Topics covered: ~3.5/5 (data dictionary reviewed ✓ item 15; runbook to ops ✓ item 14; secrets_setup.md referenced ✓ item 7 partial; BI connections validated ✓ item 19 partial)
- Missing: architecture diagram explicitly reviewed and confirmed accurate; bi_connections.md explicitly distributed to BI consumers

**Structure (67/100):**
- No dedicated `## Documentation` section; items embedded in Security and Operations → 50
- Items are checkboxes: ☐ → 70
- Items are actionable: Yes → 80

**Strengths:**
- Runbook reviewed AND approved by operations team (item 14) — stronger phrasing than reference's "distributed"
- Data dictionary reviewed by a named stakeholder role (data steward) adds accountability

**Gaps:**
- Architecture diagram review not included
- No explicit "bi_connections.md distributed to BI consumers" item
- Documentation items scattered across Operations and Security sections with no dedicated heading

**Improvement items:**
- [ ] Add: architecture diagram reviewed and confirmed accurate before go-live
- [ ] Add: BI connections document explicitly distributed to BI consumers
- [ ] Consider a dedicated `## Documentation` section to consolidate scattered doc items

---

## Extra Sections (participant-only, not in reference)

- **`## Section 1: Pending Decision Gates`** — hard-gate table for CX-P04, CX-P05, CX-DQ-01 with owner and sign-off columns. Excellent governance addition; makes blockers explicit before the checklist begins. No score impact.

- **`## Section 3: Testing`** — dedicated testing section with unit tests, integration tests, end-to-end test (TASK-TEST-007), performance benchmarks, and code coverage threshold. Goes well beyond reference scope. No score impact (credited in Pipeline section scoring).

- **`## Final approval`** — formal sign-off table with 5 named roles (DE Lead, Security Lead, Data Steward, Ops Lead, Business Owner) and signature columns. Strong governance structure absent from reference. No score impact.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add `## Data Quality` section with DQ config, blocking/informational rules, smoke test, rejection table, synthetic failure test | Data Quality | +17 pts (12.35 scoring + 5 deduct removal) |
| 2 | Add `## Infrastructure` section with catalog, schema, cluster policy, workflow deployment, alerts + CFG-* task IDs | Infrastructure | +12 pts (7.4 scoring + 5 deduct removal) |
| 3 | Add dimension sentinel/default rows, etl_cutoff seeding, and staging table initialization to Data section | Data | +5 pts |
| 4 | Add named service principal verification items with permission scopes to Security | Security | +3 pts |
| 5 | Add lineage/run log status=success and watermark advancement verification to Pipeline | Pipeline | +2 pts |
| 6 | Add architecture diagram review item and explicit BI connections distribution to Documentation | Documentation | +2 pts |
| 7 | Add negative permission test to Security (BI principal cannot write to fact/dim) | Security | +1 pt |

Addressing items 1 and 2 alone (adding the two missing sections) would push the score to approximately **69/100 (Acceptable)**.

---

## Priority Actions

1. **Add `## Data Quality` section** — this is the single largest gap. Include: DQ assertion config loaded, blocking rules verified, informational rules verified, DQ smoke test passes, rejection table writable, synthetic failure test performed. Worth up to **+17 pts**.

2. **Add `## Infrastructure` section** — cover catalog created, schemas created, cluster policy, workflow deployed and scheduled, alert recipients. Reference CFG-* task IDs. Worth up to **+12 pts**.

3. **Add dimension sentinel rows and watermark seeding to `## Section 5: Data`** — sentinel/default rows for each SCD-2 dimension and etl_cutoff initialization are critical pre-load steps. Worth up to **+5 pts**.

4. **Add service principal verification to `## Section 2: Security`** — name the ETL and BI service principals and verify their permission scopes explicitly. Worth up to **+3 pts**.

5. **Add run-log success and watermark advancement checks to pipeline items** — after E2E test, confirm `stg.lineage` (or equivalent) shows success and the cutoff timestamp advanced. Worth up to **+2 pts**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing sections, no task refs, or no verification items |
| 0–44 | Incomplete | Major sections absent or no checkbox format used |

---

*Report generated by skill 27-migvisor-task-checker-go-live-checklist on 2026-09-03*
