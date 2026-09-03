---
task_id: TASK-VAL-001
product: Sales_Orders
participant_file: validation-report.md
reference_file: report_final.md
checked_at: 2026-09-02T16:00:00Z
sections_evaluated: 5
total_score: 80/100
grade: Good
identical_to_reference: false
---

# Task Check Report — validation report
_Sales_Orders | 2026-09-02_

**File resolution log:**
- Participant file: `validation-report.md` — auto-resolved (priority 1 match: `validation-report.md`)
- Reference file: `report_final.md` — auto-resolved (priority 1 match: `report_final.md`)
- Product: `Sales_Orders` — derived from H1 heading `# SmartBuilder Validation Report — Sales_Orders`
- Sections in reference: 5 (Header Metadata + Results + Findings + DQR Coverage Note + Summary) | Sections in participant: 8 (Header Metadata + 7 H2 sections; matched: 4, extra: 4 — Priority File Deep-Dive, Pending Decisions, Spec Conflict Register, Remediation Priority)
- Point weights: auto-calculated — N=5, floor(100/5)=20; remainder=0; all sections 20 pts each
- Participant metrics: Total 86 | PASS 80 | FAIL 6 | WARN 0 | PASS rate 93.0%

---

## Score Summary

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| Header Metadata | Header (H1 + metadata fields) | 20 | 20 | ✓ |
| Summary | §Executive Summary | 20 | 20 | ✓ |
| Results | §Results Table (8 subsections) | 20 | 20 | ✓ |
| Findings | §Failure Details | 20 | 20 | ✓ |
| DQR Coverage Note | *(no match)* | 20 | 0 | ✗ |
| **Total** | | **100** | **80** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Header Metadata (20/20)
_Matched to participant header (H1 + metadata fields before first `## `)_

**Field completeness:** All key metadata fields present — product (`Sales_Orders`) ✓, project (`GlobalSales_Project`) ✓, validator (`migVisor SmartBuilder Validation Agent`) ✓, validation date (`2026-08-28`) ✓, spec baseline (`design.md · requirements.md · tasks.md · catalog.yaml`) ✓. Participant adds `catalog.yaml` beyond what the reference declares — supplementary detail, not penalised. Full marks.

**Accuracy:** Validation date (2026-08-28) internally consistent. Spec baseline references all relevant authoritative files. Full marks.

**Structure:** Metadata presented as labelled key–value pairs ✓. H1 title identifies product and report type (`# SmartBuilder Validation Report — Sales_Orders`) ✓. Full marks.

**Deferred fields `[DEFERRED]`:** None.

**Improvement items:** None.

---

### Summary — Executive Summary (20/20)
_Matched to participant §Executive Summary_

**Metrics accuracy:** Metrics table states Total 86, PASS 80, FAIL 6, PASS rate 93.0%. Verified against results tables: DB—DDL (21) + DB—Grants (4) + DB—Queries (1) + ETL—Python (30) + Config (16) + Tests—Unit (6) + Tests—Integration (4) + Docs (4) = 86 ✓; PASS 80 ✓; FAIL 6 ✓; 80/86 = 93.02% → 93.0% ✓. No WARN artifacts — WARN row correctly absent. Full marks.

**Failure coverage:** All 6 FAIL artifacts described in the narrative and grouped by causal relationship: three UDF-related failures (F-01 DDL, F-02 sample queries, F-05 UDF test notebook) described as functionally linked; two lineage failures (F-03 watermark, F-04 extract_sales) described as cause-and-effect pair; F-06 (test_sk_resolver.py) identified as independent. Note: narrative states "four failures are functionally related" but names three artifact paths — minor counting imprecision (F-04, while upstream-caused, may have been intended as the fourth). All 6 failures accounted for. Full marks.

**Specificity:** Narrative names specific artifact paths (`fact_udf_get_total_quantity_sold.sql`, `nb_extract_watermark.py`, `nb_extract_sales.py`, `test_sk_resolver.py`), function names (`lineage_key`, `resolve_surrogate_keys()`), and spec references (design.md, tasks.md, TASK-TEST-003). Full marks.

**Structure:** Metrics table present ✓; narrative paragraph present ✓. Full marks.

**Artifact inventory:**
- Total: 86 | PASS: 80 | FAIL: 6 | WARN: 0
- All FAIL artifacts mentioned in narrative: 6/6

**Deferred fields `[DEFERRED]`:** None.

**Improvement items:** None.

---

### Results — Results Table (20/20)
_Matched to participant §Results Table (8 H3 subsections: DB—DDL, DB—Grants, DB—Queries, ETL—Python, Config, Tests—Unit, Tests—Integration, Docs)_

**Completeness:** All 86 artifact rows have artifact paths, task IDs, verdicts, and finding entries. All 6 FAIL rows have both an inline description and a cross-reference to a named finding (e.g., "see Finding F-01" through "see Finding F-06"). No blank or placeholder cells. Full marks.

**Verdict documentation:** All 6 FAIL verdicts substantiated with inline context and finding cross-reference. PASS rows have substantive notes — specific columns (`lineage_key`, `PROFIT_MARGIN_FACTOR=1.05`), design patterns (truncate-before-load, IS DISTINCT FROM), and acceptance criteria verified (e.g., "CLUSTER BY (invoice_date_key, customer_key, stock_item_key)"). Full marks.

**Specificity:** Notes reference specific technical details throughout: function names (`apply_scd2_merge()`, `resolve_surrogate_keys()`, `get_secret()`), spec IDs (`FR-LIN`, `DQ-SALE-001`, `DQ-SALE-002`), task IDs (`TASK-DB-011`, `TASK-TEST-003`), and behavioural patterns (LEFT ANTI JOIN idempotency, staleness guard, conditional OPTIMIZE). Full marks.

**Metrics accuracy:** Section heading counts verified: DB—DDL (21 ✓), DB—Grants (4 ✓), DB—Queries (1 ✓), Config (16 ✓), Tests—Unit (6 ✓), Tests—Integration (4 ✓), Docs (4 ✓). ETL—Python heading states 31; section contains rows 27–56 = 30 rows — variance of 1, within ±1 tolerance. Overall total 86 matches header ✓. Full marks.

**Structure:** Eight H3 subsections under `## Results Table`, each with a markdown table containing #, Artifact, Task, Verdict, Finding columns. Consistent formatting throughout all subsections. Full marks.

**Artifact inventory:**
- Total rows: 86 | PASS: 80 | FAIL: 6 | WARN: 0
- FAIL rows with findings: 6/6
- Rows with empty Finding/Notes: 0

**Deferred fields `[DEFERRED]`:** Rows reference `CX-P04`, `CX-P05`, `CX-DQ-01` placeholder markers — these are registered open decisions documented in the Pending Decisions section. Treated as intentional, not deferred findings.

**Improvement items:**
- [ ] Correct ETL—Python subsection heading artifact count from 31 to 30 (rows 27–56 = 30 artifacts; overall total of 86 is correct)

---

### Findings — Failure Details (20/20)
_Matched to participant §Failure Details_

**Finding coverage:** 6 FAIL artifacts in results tables; 6 corresponding findings in Failure Details (F-01 through F-06) — 6/6 ✓. No WARN artifacts — no WARN findings required. Full marks.

**Finding depth:** Each finding evaluated for 4 required elements (file path, root cause, fix/remediation, spec reference):

- **F-01** (`fact_udf_get_total_quantity_sold.sql`): file path ✓ | root cause: spec conflict between design.md 1-param INT signature and tasks.md 3-param BIGINT signature; generated artifact adopts hybrid 3-param BIGINT interpretation matching neither spec ✓ | fix: resolve conflict with product owner, align tasks.md, regenerate DDL ✓ | spec ref: `design.md §3.4`, `design.md §4.2` ✓ — **4/4**
- **F-02** (`bi_sample_queries.sql`): file path ✓ | root cause: 1-arg call against 3-param deployed DDL ✓ | fix: align call-site after F-01 resolved ✓ | spec ref: "downstream consequence of F-01" — indirect link, acceptable since F-01 carries the authoritative spec references ⚠ — **3.75/4**
- **F-03** (`nb_extract_watermark.py`): file path ✓ | root cause: notebook performs steps 1/2/4 but entirely omits step 3 — never INSERTs stg.lineage record, never calls `dbutils.jobs.taskValues.set(key="lineage_key")` ✓ | fix: add lineage INSERT + taskValues.set block after watermark window computation ✓ | spec ref: `FR-LIN (requirements.md)`, `design.md §2.3`, `design.md §5.1` ✓ — **4/4**
- **F-04** (`nb_extract_sales.py`): file path ✓ | root cause: runtime dependency on taskValue never published by F-03; all own logic correct ✓ | fix: fix F-03; no change to this notebook ✓ | spec ref: `FR-LIN`; direct consequence of F-03 ✓ — **4/4**
- **F-05** (`nb_test_udf_qty_sold.py`): file path ✓ | root cause: 1-arg call against 3-param deployed DDL ✓ | fix: align after F-01 resolved ✓ | spec ref: "downstream consequence of F-01" — indirect ⚠ — **3.75/4**
- **F-06** (`tests/unit/test_sk_resolver.py`): file path ✓ | root cause: file does not import from `src.etl.facts.sk_resolver` and does not call `resolve_surrogate_keys()` — content tests unrelated datetime and reconciliation utilities duplicating test_utils.py ✓ | fix: replace content with 3 required scenarios using local SparkSession with MagicMock dims ✓ | spec ref: `tasks.md TASK-TEST-003 acceptance criteria` ✓ — **4/4**

Average finding depth ≈ 98%. Full marks.

**Technical accuracy:** All root causes are technically specific and plausible. F-03 correctly identifies the pipeline-wide blast radius (all downstream notebooks read `lineage_key` from taskValues and will raise RuntimeError). F-06 correctly names all three missing test scenarios (successful resolution, unresolved natural key, empty source DataFrame). F-01 correctly identifies that the generated artifact matches neither spec source. Full marks.

**Structure:** Findings organised by ID (F-01 through F-06). Each finding has named sub-fields: Artifact, Task, Spec rules violated, Root cause, Required remediation. Consistent format across all 6 findings. Full marks.

**Artifact inventory:**
- FAIL rows in results tables: 6 | Findings in section: 6 | Coverage: 6/6

**Deferred fields `[DEFERRED]`:** None.

**Improvement items:** None.

---

### DQR Coverage Note (0/20)
_No match found in participant_

The reference contains a `## DQR Coverage Note` explaining that DQR-004 and DQR-005 appear in `dq_assertions_purchase.yaml` but are not loop-evaluated in `dq_engine.py` — intentional design (DQR-004 enforced via `_write_rejection()` raising RuntimeError; DQR-005 enforced via `DQBlockingFailure` blocking DAG execution). No equivalent section appears in the participant document.

**Cross-product context:** Participant (Sales_Orders / GlobalSales_Project) uses a different DQ architecture: `DQEngine` class evaluating 5 assertion types, separate `nb_dq_fact_sale` / `nb_dq_fact_order` notebooks, `dq_assertions_fact_sale.yaml` and `dq_assertions_fact_order.yaml`. The reference's specific DQR-004/005 design decision does not apply directly. The absence of a DQR Coverage Note may be valid if all DQR rules are uniformly loop-evaluated in `dq_engine.py` with no out-of-band enforcement.

Score: 0/20 (unmatched reference section per rubric).

**Improvement items:**
- [ ] Consider adding a DQ design decision note — if any DQR rules are enforced outside the main `DQEngine.evaluate_rules()` loop (e.g., via exception handling, task-value blocking, or separate enforcement), document this explicitly. If all rules are uniformly evaluated, a brief coverage note confirming this adds traceability.

---

## Extra Sections (not in reference)

| Participant section | Notes |
|---|---|
| `## Priority File Deep-Dive` | Structured acceptance-criteria checklist tables for two specific artifacts: `fact_sale.sql` (TASK-DB-008, all 13 criteria ✓) and `nb_extract_sales.py` (TASK-ING-002, 12 criteria checked including the one that fails due to F-03). High-value addition for priority artifacts. |
| `## Pending Decisions — Not Failures` | Documents three registered open decisions (CX-P04: OLTP connection strategy, CX-P05: Unity Catalog access roles, CX-DQ-01: business DQ thresholds) with affected artifact lists. Explains why CX-P0x TODOs are correct placeholders, not failures. Adds completeness and prevents misinterpretation. |
| `## Spec Conflict Register` | Formally documents SC-001 — the UDF parameter conflict between design.md §3.4/§4.2 (1-param INT) and tasks.md TASK-DB-011 (3-param BIGINT with different semantics). Includes recommendation. Reference has no equivalent — high-quality addition that makes the conflict actionable. |
| `## Remediation Priority` | Priority table (P1 Critical, P2 High, P3 Medium) mapping all findings and SC-001 to files needing change and go-live block status. Clarifies that F-04 needs no code change once F-03 is fixed. Reference has no equivalent. |

---

## Approach Notes

- Cross-product comparison: participant covers Sales_Orders (GlobalSales_Project, 86 artifacts, 6 FAILs, 0 WARNs); reference covers Purchase (GlobalPurchase_Project, 55 artifacts, 1 FAIL, 2 WARNs). Content evaluated on internal quality and completeness, not by matching reference content.
- Participant uses `## Results Table` with 8 H3 subsections; reference uses a flat `## Results` table (no H3 subsections). Reference's flat structure triggers the one-section treatment per detection rules — participant's entire Results Table evaluated as one section. No deduction for structural difference.
- Participant uses "Verdict" / "Finding" column names vs. reference "Status" / "Notes" — no deduction (approach policy).
- Participant positions Executive Summary at the top; reference Summary is at the bottom — no deduction (approach policy).
- Participant Findings section titled "Failure Details"; reference titled "Findings" — matched by keyword ("Failure" matches "Failure"), no deduction.
- ETL—Python heading count (31 stated, 30 actual rows 27–56): off by 1, within ±1 tolerance. Overall total of 86 is correct.
- DQR Coverage Note absent: product-specific section from reference documenting GlobalPurchase DQR-004/005 out-of-loop enforcement. Sales_Orders uses a different DQ architecture. Scored 0/20 per rubric; cross-product context noted.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **DQR Coverage Note — section absent — up to +20 pts recoverable**: Add a DQ enforcement design note. If `DQEngine.evaluate_rules()` handles all DQR rules uniformly with no out-of-band enforcement, state this explicitly. If any rules (e.g., row-count assertion failures, blocking DQ gates) are enforced outside the main evaluation loop, document the mechanism. This is the sole scoring gap.
2. **Results — ETL—Python heading count — 0 pts recoverable (within tolerance)**: Correct the ETL—Python subsection heading from "31 artifacts" to "30 artifacts" (rows 27–56 = 30 rows). No score impact but eliminates a count inconsistency in an otherwise fully accurate document.
3. **Summary — failure count narrative — 0 pts recoverable**: Clarify "four failures are functionally related" — either name four artifact paths explicitly (F-01, F-02, F-05, and possibly nb_extract_sales F-04 as propagation target) or revise to "three UDF-related failures." No score impact.

---

## Next Step

Score 80 ≥ 75: You can proceed to the next task. The only scoring gap is the absent DQR Coverage Note (0/20); all four matched sections scored full marks. Consider whether a DQ design decision note is applicable to Sales_Orders before submitting the final report.
