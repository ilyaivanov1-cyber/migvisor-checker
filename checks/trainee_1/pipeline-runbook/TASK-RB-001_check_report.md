---
task_id: TASK-RB-001
skill: task-checker-pipeline-runbook
participant_file: trainees/trainee_1/pipeline_runbook.md
reference_file: reference/pipeline_runbook.md
product: Sales_Orders
generated: 2026-09-03
total_score: 32/100
grade: Incomplete
---

# TASK-RB-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase Data Product
**Participant file:** `trainees/trainee_1/pipeline_runbook.md`
**Reference file:** `reference/pipeline_runbook.md`
**Generated:** 2026-09-03

---

## Score Summary

**The pipeline runbook Score: 32/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 14 | 83/100 | 11.6 | ✓ Pass |
| Daily Monitoring Checklist | 1. Daily Monitoring Checklist | 14 | 51/100 | 7.1 | ⚠ Partial |
| Failure Response | 2. Failure Response | 15 | 78/100 | 11.6 | ✓ Pass |
| Partial Reprocessing Guide | 3. Partial Reprocessing Guide | 14 | 75/100 | 10.4 | ✓ Pass |
| DQ Investigation | 4. DQ Investigation | 15 | 54/100 | 8.1 | ⚠ Partial |
| Escalation Path | 5. Escalation Path | 14 | 0/100 | 0.0 | ✗ Missing |
| Contacts | 6. Contacts | 14 | 0/100 | 0.0 | ✗ Missing |
| **Subtotal** | | | | **48.8** | |
| Auto-deducts | | | | **−17.0** | |
| **Total** | | | | **32/100** | |

**Grade: Incomplete**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | H1 + `_TASK-DOCS-001_` preamble | exact |
| 1. Daily Monitoring Checklist | `## Monitoring stg.lineage` | semantic — monitoring section, different format |
| 2. Failure Response | `## Re-running a failed pipeline stage` + `## Troubleshooting decision tree` | semantic — combined both sections |
| 3. Partial Reprocessing Guide | `## Manual backfill (watermark override)` | semantic — near-exact |
| 4. DQ Investigation | `## Clearing and re-processing stg.dq_rejections` | semantic — partial coverage |
| 5. Escalation Path | [MISSING] | missing |
| 6. Contacts | [MISSING] | missing |
| *(not in reference)* | `## Overview` | extra |

**Note:** The participant spreads Failure Response content across two sections (`## Re-running a failed pipeline stage` and `## Troubleshooting decision tree`). Both are scored together as a single matched section — the combined content covers the reference's diagnosis table, re-trigger steps, and scenario-specific troubleshooting.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No `- [ ]` checklist items anywhere in document | −4 pts | **Yes — no checkbox format found anywhere: −4 pts** |
| No SQL code blocks anywhere | −4 pts | **No** — SQL present in multiple sections |
| No failure/troubleshooting section | −5 pts | **No** — `## Troubleshooting decision tree` present |
| No escalation path or contacts anywhere in document | −3 pts | **Yes — both absent: −3 pts** |
| Missing H2 section: 5. Escalation Path | −5 pts | **Yes: −5 pts** |
| Missing H2 section: 6. Contacts | −5 pts | **Yes: −5 pts** |
| No notebook/task name references anywhere | −3 pts | **No** — `nb_*` names present throughout |
| SQL uses wrong catalog (reference catalog instead of participant's) | −2 pts | **No** — `globalsales` used consistently |

**Total auto-deducts: −17 pts**

---

## Section Feedback

### Header Metadata — 83/100 (weight 14 → 11.6 pts)

**Criteria scored:** Content (90%), Structure (10%)

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product / pipeline name in H1 | 35% | 100 | "Sales_Orders / nightly_etl_main" — both product and pipeline named |
| Task ID / traceability tag | 30% | 100 | `_TASK-DOCS-001_` present |
| Catalog / platform reference | 20% | 40 | Not in header lines; `globalsales` appears in code blocks below but not in the document preamble |
| Schedule / SLA stated | 15% | 60 | Present in `## Overview` ("02:00 UTC… 4-hour SLA") — good content, but placed in a separate section rather than the header |

**Strengths:**
- H1 names both the product (`Sales_Orders`) and the pipeline (`nightly_etl_main`) — immediately clear
- Task ID tag provides traceability

**Gaps:**
- Catalog (`globalsales`) not stated in the header/preamble block
- Schedule and SLA placed in `## Overview` rather than the header itself

**Improvement items:**
- [ ] Add a one-line preamble or subtitle: `_Catalog: globalsales | Schedule: 02:00 UTC nightly | SLA: complete by 06:00 UTC_`

---

### 1. Daily Monitoring Checklist → `## Monitoring stg.lineage` — 51/100 (weight 14 → 7.1 pts)

**Criteria scored:** Content (55%), Checklist Format (15%), SQL Queries (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 48/100 | ~2/5 reference topics covered; SQL monitors lineage but misses Workflow run status, alert inbox, etl_cutoff advance check |
| Checklist Format | 15% | **0/100** | **No `- [ ]` items anywhere in section** |
| SQL Queries | 20% | 91/100 | SQL present, uses globalsales, executable, returns runtime_min + row counts — richer than reference |
| Structure | 10% | 70/100 | H2 present, SQL fenced, no intro paragraph |

**Content completeness detail (48/100):**
- Lineage status monitoring ✓ (SQL queries stg.lineage)
- Runtime and row counts monitored ✓ (TIMESTAMPDIFF, rows_extracted/loaded/rejected)
- Workflow run status check ✗ (no "check Databricks Workflow run status" step)
- Alert inbox check ✗ (no Slack/email alert verification step)
- etl_cutoff advance verification ✗ (no check that `last_cutoff_utc` advanced)
- Dim row count spot-check ✗ (not mentioned)

Topics: ~2/5 = 40%; steps specific: 85%; intro: 0%  
Content = 40×0.55 + 85×0.30 + 0×0.15 = 22.0 + 25.5 + 0 = 47.5/100

**Strengths:**
- SQL query is thorough — returns runtime, rows extracted/loaded/rejected, status all in one query
- 7-day window with `ORDER BY batch_start_utc DESC` is operationally useful
- `TIMESTAMPDIFF(MINUTE, ...)` column makes SLA compliance immediately visible

**Gaps:**
- **No checklist format at all** — the reference section is a morning ops checklist (`- [ ]`), not a query reference. Without checkbox items, an operator cannot track which checks have been completed each morning
- Workflow job status check absent (Databricks UI check)
- Alert inbox verification absent (Slack/email check)
- `stg.etl_cutoff` advance check absent — confirms the pipeline processed new data
- Dimension table row count spot-check absent

**Improvement items:**
- [ ] Reformat as a morning checklist: convert each monitoring step to `- [ ]` format
- [ ] Add: `- [ ] Check Databricks Workflow run status: globalsales_nightly_etl_main`
- [ ] Add: `- [ ] Verify alert inbox — no failure emails or Slack alerts`
- [ ] Add: `- [ ] Confirm stg.etl_cutoff.last_cutoff_utc for entity_name = 'sale' advanced`
- [ ] Add: `- [ ] Spot-check dim.customer and dim.city for expected row counts`
- [ ] Keep the SQL query as a "Quick lineage query" reference below the checklist

---

### 2. Failure Response → `## Re-running a failed pipeline stage` + `## Troubleshooting decision tree` — 78/100 (weight 15 → 11.6 pts)

**Criteria scored:** Content (70%), Diagnosis / Action Table (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 77/100 | ~5/6 topics; strong scenario coverage; no section intro |
| Diagnosis / Action Table | 20% | 86/100 | Re-run table functions as action table; 10 notebook entries exceed reference's 7 |
| Structure | 10% | 65/100 | Two H2s covering one reference section; no intro paragraph; no H3 sub-sections like reference |

**Content completeness detail (77/100):**
- Identify failed task ✓ (troubleshooting decision tree covers 5 failure scenarios)
- Diagnose root cause ✓ (each scenario has specific checks: secret scope, PENDING blockers, OPTIMIZE)
- Re-trigger instructions ✓ (CLI command present; idempotency noted per notebook)
- JDBC credential errors ✓ (`databricks secrets list --scope globalsales`)
- Source unavailability ✓ (CX-P04 PENDING note)
- SCD-2 MERGE conflict → covered via "Merge timeout" section ✓
- Missing sentinel row scenario → absent (reference entry: "Insert sentinel rows into dim.supplier/dim.stock_item") ✗

Topics: ~5/6 = 83%; steps specific: 88%; intro: 0%  
Content = 83×0.55 + 88×0.30 + 0×0.15 = 45.7 + 26.4 + 0 = 72/100

**Diagnosis / Action Table (86/100):**
- Table present: `## Re-running a failed pipeline stage` has Stage | Notebook path | Notes table ✓
- 10/7 notebook stages covered ✓
- Each entry has concrete action: notebook path + idempotency note ✓

**Strengths:**
- Notebook paths are fully qualified (`.../ingestion/nb_extract_watermark`) — operator can navigate directly
- Idempotency classification per notebook ("Safe to re-run", "Truncate-before-load", "Delta MERGE is idempotent") is excellent
- Troubleshooting decision tree with 5 detailed failure scenarios goes beyond the reference
- `databricks jobs run-now --job-id` CLI command adds automation option absent from reference
- PENDING blockers (CX-P04, CX-DQ-01) correctly annotated as open decisions

**Gaps:**
- Sentinel row insertion scenario missing ("Missing sentinel row → Insert sentinel rows into dim.*")
- No introductory paragraph explaining when to use this section
- Content split across two H2 sections makes navigation less clear

**Improvement items:**
- [ ] Add sentinel row scenario to the troubleshooting tree: when fact load fails with "surrogate key not found", insert sentinel rows into dim.customer/dim.city
- [ ] Add a one-line intro before the re-run table: "Use this table when a specific notebook fails and needs to be re-run independently after fixing the root cause."

---

### 3. Partial Reprocessing Guide → `## Manual backfill (watermark override)` — 75/100 (weight 14 → 10.4 pts)

**Criteria scored:** Content (70%), SQL Queries (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 68/100 | 3/4 topics; missing verification SQL and idempotency warning callout |
| SQL Queries | 20% | 97/100 | Excellent — UPDATE SQL, CLI trigger, product catalog |
| Structure | 10% | 75/100 | H2 present, numbered steps, SQL fenced; no intro |

**Content completeness detail (68/100):**
- Step 1 — Reset watermark ✓ (UPDATE stg.etl_cutoff, includes multi-entity note)
- Step 2 — Trigger pipeline ✓ (CLI command with `databricks jobs run-now`)
- Step 3 — Verify ✗ (reference has SELECT to confirm cutoff advanced; participant only says "Monitor progress in stg.lineage" — no SELECT query)
- Idempotency/duplicate warning ✗ (reference has `> **Warning:**` callout; absent in participant)

Topics: 3/4 = 75%; steps specific: 90%; intro: 0%  
Content = 75×0.55 + 90×0.30 + 0×0.15 = 41.25 + 27 + 0 = 68/100

**Strengths:**
- Multi-entity comment (`-- Repeat for: order, customer, city, stock_item…`) adapts the reference to the Sales_Orders product
- `updated_at_utc = current_timestamp()` correctly accounts for the extra column in `stg.etl_cutoff`
- CLI trigger command is a practical addition not in the reference

**Gaps:**
- No verification SQL after triggering (reference: `SELECT last_cutoff_time…` to confirm the watermark advanced)
- No warning callout about re-processing duplicates or MERGE idempotency implications

**Improvement items:**
- [ ] Add Step 3 verification SQL:
  ```sql
  SELECT entity_name, last_cutoff_utc FROM globalsales.stg.etl_cutoff
  WHERE entity_name IN ('sale', 'order');
  -- Confirm timestamps advanced to the expected end of the reprocessed window
  ```
- [ ] Add `> **Warning:** Resetting the watermark re-processes source rows. The fact MERGE is idempotent — no duplicate rows — but lineage will show multiple runs for overlapping windows.`

---

### 4. DQ Investigation → `## Clearing and re-processing stg.dq_rejections` — 54/100 (weight 15 → 8.1 pts)

**Criteria scored:** Content (50%), SQL Queries (20%), Diagnosis / Action Table (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 57/100 | ~3/5 topics; missing DQ rules table and cross-run aggregation query |
| SQL Queries | 20% | 97/100 | Present, globalsales catalog, SELECT + DELETE both executable |
| Diagnosis / Action Table | 20% | **0/100** | **No DQ rules table at all** |
| Structure | 10% | 65/100 | H2 present, SQL fenced, no intro |

**Content completeness detail (57/100):**
- Per-run violation query ✓ (`SELECT * FROM stg.dq_rejections WHERE lineage_key = <key>`)
- Cross-run aggregation query ✗ (reference has JOIN to stg.lineage + GROUP BY per rule+severity — absent)
- DQ rules table ✗ (reference documents DQR-001, DQR-002, DQR-003, DQR-006 with description+action — absent)
- Clear rejections after investigation ✓ (`DELETE FROM stg.dq_rejections WHERE lineage_key = <key>`)
- Re-injection procedure ✓ (prose description)

Topics: ~3/5 = 60%; steps specific: 80%; intro: 0%  
Content = 60×0.55 + 80×0.30 + 0×0.15 = 33 + 24 + 0 = 57/100

**Strengths:**
- DELETE query for clearing rejections is a practical operational step not in the reference
- Re-injection procedure explains the correct approach (re-insert into staging + re-trigger)
- SQL uses `globalsales` catalog consistently

**Gaps:**
- **No DQ rules table** — reference documents the 4 common DQ failures (DQR-001 count mismatch, DQR-002 FK violations, DQR-003 sentinel key, DQR-006 null lineage_key) with specific actions. This is the most actionable part of DQ investigation
- No cross-run summary query (`JOIN stg.lineage GROUP BY rule+severity`)
- No intro paragraph explaining when to use this section

**Improvement items:**
- [ ] Add a DQ common failures table adapted for Sales_Orders:
  | Rule | Description | Action |
  |---|---|---|
  | DQ-SALE-001 | Staging/fact count mismatch | Check for MERGE errors; compare stg.sale_staging vs fact.sale row counts |
  | DQ-SALE-002 | FK integrity violations | Rows reference missing dimension keys; check SCD-2 load |
  | DQ-SALE-003 | Null lineage_key | lineage_key injection failed in nb_extract_sales |
  | DQ-SALE-004 | Null profit | NULL profit from source; check Sales.InvoiceLines |
- [ ] Add cross-run summary SQL:
  ```sql
  SELECT l.pipeline_run_id, l.batch_start_utc, r.assertion_id, COUNT(*) AS violations
  FROM globalsales.stg.dq_rejections r
  JOIN globalsales.stg.lineage l ON r.lineage_key = l.lineage_key
  GROUP BY l.pipeline_run_id, l.batch_start_utc, r.assertion_id
  ORDER BY l.batch_start_utc DESC;
  ```

---

### 5. Escalation Path → [MISSING] — 0/100 (weight 14 → 0.0 pts)

No escalation path section exists in the participant document. The reference defines a 3-column table (Severity | Contact | Channel) covering pipeline failures, DQ violations, source system unavailability, and security incidents.

**Gaps:**
- No severity-to-contact mapping documented
- No on-call channel (Slack, PagerDuty) referenced
- Security incidents have no escalation path

**Improvement items:**
- [ ] Add `## Escalation Path` with a Severity | Contact | Channel table. Adapt from the reference with your actual team channels and on-call tools

---

### 6. Contacts → [MISSING] — 0/100 (weight 14 → 0.0 pts)

No contacts section exists. The reference lists Data Engineering lead, Platform team, and Security team email addresses.

**Improvement items:**
- [ ] Add `## Contacts` with at minimum: Data Engineering lead and on-call channel

---

## Extra Section

**`## Overview`** — describes pipeline schedule ("02:00 UTC nightly"), SLA ("must complete by 06:00 UTC"), and run name. Useful context that could be integrated into the header preamble. No score impact.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add `## Escalation Path` with severity/contact/channel table | Escalation Path | +14 pts + 5 deduct removal = +19 pts |
| 2 | Add `## Contacts` section with team contacts | Contacts | +12 pts + 5 deduct removal = +17 pts |
| 3 | Reformat monitoring section as `- [ ]` checklist; add 4 missing checks | Daily Monitoring Checklist | +8 pts + 4 deduct removal = +12 pts |
| 4 | Add DQ rules table (4 common failures with action) + cross-run SQL | DQ Investigation | +8 pts |
| 5 | Add verification SQL to Manual backfill + idempotency warning callout | Partial Reprocessing Guide | +3 pts |
| 6 | Add sentinel row scenario to Troubleshooting decision tree | Failure Response | +2 pts |
| 7 | Add catalog + SLA to header preamble | Header Metadata | +1 pt |

Addressing items 1–3 alone would push the score to approximately **71/100 (Acceptable)**.  
Addressing all 7 items could reach approximately **85/100 (Good)**.

---

## Priority Actions

1. **Add `## Escalation Path` + `## Contacts`** — these two sections are worth **+36 pts combined** (section scores + deduct removal). Create a severity-to-contact table with Slack channels / PagerDuty for pipeline failures, DQ violations, source unavailability, and security incidents. Add a Contacts list with team leads. Single highest-impact action.

2. **Convert `## Monitoring stg.lineage` to a checkbox checklist** — remove the existing SQL (keep as "Quick lineage query" below the checklist), add `- [ ]` items for: Workflow run status, lineage status=SUCCESS check, alert inbox check, etl_cutoff advance check, dim row count spot-check. Worth **+12 pts** (section improvement + −4 deduct removal).

3. **Add the DQ rules table to `## Clearing and re-processing stg.dq_rejections`** — document at least 4 common DQ assertion IDs (DQ-SALE-001 through DQ-SALE-004) with description and corrective action. Also add the cross-run aggregation SQL. Worth **+8 pts**.

4. **Add Step 3 verify SQL + warning callout to `## Manual backfill`** — confirm watermark advanced after reprocessing; add `> **Warning:**` for idempotency implications. Worth **+3 pts**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing monitoring checklist, escalation path, or SQL queries absent |
| 0–44 | Incomplete | Major sections absent or no operational procedures documented |

---

*Report generated by skill 29-migvisor-task-checker-pipeline-runbook on 2026-09-03*
