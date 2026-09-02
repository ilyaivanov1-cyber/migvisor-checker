---
task_id: TASK-REQ-001
skill: task-checker-requirements
participant_file: requirements.md
reference_file: requirements_final.md
product: Sales_Orders
generated: 2026-09-02
total_score: 50/100
grade: Needs work
---

# TASK-REQ-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase (GlobalPurchase_Project)
**Participant file:** `requirements.md`
**Reference file:** `requirements_final.md`
**Generated:** 2026-09-02

---

## Score Summary

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 25 | 45/100 | 11 pts | ⚠ |
| Functional Requirements | 25 | 54/100 | 14 pts | ⚠ |
| Non-Functional Requirements | 25 | 69/100 | 17 pts | ⚠ |
| Data Quality Requirements | 25 | 48/100 | 12 pts | ⚠ |
| **Subtotal** | | | **54 pts** | |
| Auto-deducts | | | **−4 pts** | |
| **Total** | | | **50/100** | |

**Grade: Needs work**

Section weights: N=4, base=floor(100/4)=25, remainder=0 → all sections 25 pts.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No requirement IDs anywhere | −5 pts | No — all requirements carry traceable IDs |
| Missing H2 reference section | −5 pts each | No — all 3 reference sections present |
| No acceptance criteria anywhere in document | −4 pts | **Yes** — zero AC in any section |
| >30% of requirements lack individual AC | −3 pts | Subsumed by the −4 above (all reqs lack AC) |
| Requirement entry with no description | −2 pts each | No — all entries have description text |
| Missing `[PENDING]` markers for open items | −2 pts | No — `[PENDING: CX-P04]`, `[PENDING: CX-P05]`, `[PENDING: CX-DQ-01]` all present |

---

## Section Feedback

### Header Metadata (11/25 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Content completeness (43/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product/project identification | 30% | 60% | Product "Sales_Orders" in H1 ✓; project name not stated (GlobalSales inferred from catalog) |
| Temporal metadata | 20% | 50% | Generation date 2026-06-05 ✓; no version field |
| Document scope | 30% | 50% | "Pipeline stage: requirements" ✓; no purpose statement, no source document reference |
| Author/ownership | 20% | 0% | No author or team attribution |

**Structure (60/100):** Header block present and readable; only two metadata fields (date + stage) vs reference's five (product, project, source, date, status).

**Strengths:**
- Product name is immediately visible in the H1 title.
- Generation date is present.
- Pipeline stage tag provides useful context.

**Gaps:**
- Project name (`GlobalSales_Project` or equivalent) not stated.
- No document version or status field (e.g., `draft`, `approved`).
- No source document reference (equivalent to reference's `product-definition.yaml`).
- No author or owning team attribution.

---

### Functional Requirements (14/25 pts)

**Criteria scored:** Content completeness (50%), Acceptance Criteria (25%), Source References (15%), Structure (10%)

**Content completeness (88/100):**

Functional areas covered in participant (5/5):
- Ingestion: FR-ING-001–007 ✓
- Transformation: FR-TRN-001–013 ✓
- Serving: FR-SRV-001–004 ✓
- Orchestration: FR-ORC-001–006 ✓ *(extra, beyond reference scope)*
- Lineage: FR-LIN-001–004 ✓

Reference theme coverage (9/12):

| Reference theme | Participant coverage |
|---|---|
| Incremental ingestion | FR-ING-001–002 ✓ |
| Watermark management | FR-ING-006 ✓ |
| SCD2 dimensions | FR-TRN-005 ✓ |
| Static date calendar | FR-TRN-006 ✓ |
| Fact load with SK resolution | FR-TRN-001–004 ✓ |
| Sentinel row fallback (key=0) | ✗ Not stated as explicit FR |
| Lineage tracking | FR-LIN-001–004 ✓ |
| DQ / rejection | Covered in DQR section ✓ |
| Mart layer | FR-SRV, FR-TRN-010–013 ✓ |
| Bootstrap routine | ✗ Not present (sentinel rows, watermark seed, date calendar init) |
| Source truncation correction | ✗ Not present (reference-specific known risk) |
| Orchestration / scheduling | FR-ORC-001–006 ✓ *(extra area)* |

Requirement count: participant 34 FRs vs reference 12 FRs → ratio 1.0 (full credit).

Content score = (5/5 × 40) + (9/12 × 40) + (1.0 × 20) = 40 + 30 + 20 = 88/100 (rounding from 90 to account for bootstrap gap)

**Acceptance Criteria (0/100):**
- Requirements with any AC: 0/34 (0%)
- Measurable/testable ACs: 0/34 (0%)
- ACs referencing specific artifacts: 0/34 (0%)

Every FR has a description only. No acceptance criterion exists anywhere in this section.

**Source References (0/100):**
- Requirements with source reference: 0/34 (0%)

Reference provides a `Source` field per requirement pointing to `product-definition.yaml` sections. Participant has no equivalent.

**Structure (100/100):**
- H2 present ✓
- Subsections organized into 1.1–1.5 ✓
- Requirement IDs present (FR-ING-001, FR-TRN-001, etc.) ✓
- Consistent ID scheme (FR-AREA-NNN) ✓

**Strengths:**
- Excellent requirement depth: 34 FRs spanning ingestion, transformation, serving, orchestration, and lineage — more coverage than the reference.
- Clear ID scheme (`FR-ING-`, `FR-TRN-`, `FR-SRV-`, `FR-ORC-`, `FR-LIN-`).
- Subsection grouping (1.1–1.5) provides excellent navigability.
- `[PENDING: CX-P04]` and `[PENDING: CX-P05]` correctly mark open decisions.
- Specific artifact references in descriptions (table names, column names, catalog paths).

**Gaps:**
- Zero acceptance criteria — the single most impactful gap in the document.
- Zero source references — no traceability to the upstream specification.
- No sentinel row / key=0 fallback pattern stated as an FR.
- Bootstrap routine not captured (sentinel inserts, watermark seed, calendar init).

---

### Non-Functional Requirements (17/25 pts)

**Criteria scored:** Content completeness (65%), Acceptance Criteria (25%), Structure (10%)

**Content completeness (90/100):**

Reference NFR coverage (7/8):

| Reference NFR theme | Participant coverage |
|---|---|
| Performance (batch window, OPTIMIZE) | NFR-PRF-001–005 ✓ |
| Availability (alerting, runbook) | NFR-REL-003, NFR-REL-005 ✓ |
| Security (secrets, no hardcoded creds) | NFR-SEC-001–006 ✓ |
| Scalability | NFR-SCL-001–003 ✓ |
| Idempotency | NFR-REL-001 ✓ |
| Maintainability (constants, directory layout) | NFR-MNT-001–005 ✓ |
| **Observability** (lineage_key on every row, dq_rejections) | ✗ Covered in FR-LIN but no dedicated NFR section |
| Data retention | NFR-SCL-003 ✓ |

Requirement count: participant 24 NFRs vs reference 8 NFRs → ratio 1.0.

Content score = (5/5 × 40) + (7/8 × 40) + (1.0 × 20) = 40 + 35 + 20 = 95/100 (adjusted to 90 for observability gap).

**Acceptance Criteria (0/100):**
- Requirements with any AC: 0/24 (0%)

Every NFR has a description paragraph only. The reference provides a bulleted Acceptance Criteria list per NFR (e.g., "Running `OPTIMIZE` is triggered only when `rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD`; runs below threshold skip OPTIMIZE and log the skip reason").

**Structure (100/100):**
- H2 present ✓
- Subsections 2.1–2.5 ✓
- IDs present (NFR-PRF-001, etc.) ✓
- Consistent scheme ✓

**Strengths:**
- 24 NFRs across 5 subsections — substantially more detailed than the 8-item reference.
- Quantified thresholds present: 4-hour SLA window, 99% success rate, 99.5% endpoint availability, 30-second query response, 15-minute materialized view budget, 80% test coverage.
- Data retention periods specified numerically (90 days / 7 years / 3 years).
- Security section covers Unity Catalog, CLS, RLS, secrets, TLS, and Git-gated deployments.

**Gaps:**
- No acceptance criteria on any NFR — no testable conditions defined.
- No dedicated observability NFR (lineage_key completeness, dq_rejections coverage). These properties are in FR-LIN but observability as a quality attribute is missing from NFRs.
- Reference distinguishes idempotency as its own NFR with a MERGE-keyed acceptance criterion; participant embeds it within reliability.

---

### Data Quality Requirements (12/25 pts)

**Criteria scored:** Content completeness (40%), Acceptance Criteria (25%), Violation Handling (15%), Summary Table (10%), Structure (10%)**

**Content completeness (80/100):**

Reference DQR theme coverage:

| Reference DQR theme | Participant coverage |
|---|---|
| Row count reconciliation (BLOCKING) | DQR-REC-001–003 ✓ |
| FK referential integrity (Informational) | DQR-AST-004–005 ✓ |
| Orphaned key detection (key=0 or NULL) | ✗ Not explicitly named; partially in DQR-AST-004–005 |
| DQ rejection logging schema | DQR-REJ-001 ✓ (schema defined) |
| DQ assertion ordering guarantee | ✗ Not stated as explicit DQR |
| No null lineage_key in fact rows (BLOCKING) | ✗ Not in DQR (covered in FR-LIN-001) |
| Severity classification (BLOCKING vs Informational) | DQR-AST-006–007 ✓ (critical / error labels) |
| Threshold configuration | DQR-THR-001–002 ✓ |

Requirement count: participant 16 DQRs vs reference 6 DQRs → ratio 1.0.

Content score = (4/4 subsection areas × 40) + (5/8 reference themes × 40) + (1.0 × 20) = 40 + 25 + 20 = 85/100 (adjusted to 80 for orphaned key, ordering, and lineage_key gaps).

**Acceptance Criteria (0/100):**
- Requirements with any AC: 0/16 (0%)

Reference provides testable AC per DQR (e.g., "A LEFT ANTI JOIN between `fact.purchase` and each dimension on the respective FK column returns zero unmatched rows for a clean batch"). Participant has none.

**Violation Handling (40/100):**

Evaluated across all 16 DQRs:

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| DQRs with severity classification | 30% | 7/16 = 44% | "critical" in DQR-AST-001–003, "error" in DQR-AST-004–005; REJ/REC/THR entries have no severity |
| DQRs with action on violation | 40% | 8/16 = 50% | DQR-AST-001–005 route to dq_rejections; DQR-AST-006 halt; DQR-AST-007 continue; DQR-REC-003 halt+alert |
| DQRs with pipeline behavior described | 30% | 3/16 = 19% | DQR-AST-006 (halt), DQR-AST-007 (continue), DQR-REC-003 (halt+alert) |

Violation handling is embedded in requirement description text rather than structured as a distinct labeled section per DQR. Severity labels are present only on assertion DQRs; rejection, reconciliation, and threshold DQRs have none.

Score = (0.44 × 30) + (0.50 × 40) + (0.19 × 30) = 13.2 + 20.0 + 5.7 = 38.9/100 ≈ 40/100

**Summary Table (0/100):**

No DQR summary table present. Reference provides a table listing all DQRs with ID, Title, Severity, Blocks Load, and Blocks Mart Promotion — essential for operations teams.

**Structure (100/100):**
- H2 present ✓
- Subsections 3.1–3.4 ✓
- IDs present (DQR-AST-001, DQR-REJ-001, etc.) ✓
- Consistent scheme ✓

**Strengths:**
- 16 DQRs organized into 4 subsections (assertions, rejection handling, reconciliation, pending thresholds).
- Rejection table schema defined in DQR-REJ-001 (7 columns named).
- Row-count reconciliation requirements are detailed and actionable.
- `[PENDING: CX-DQ-01]` correctly marks unresolved threshold decisions.
- Critical vs error severity distinction present in DQR-AST-006–007.

**Gaps:**
- Zero acceptance criteria — no testable conditions per DQR.
- No DQR summary table — operations teams cannot see at-a-glance what blocks and what logs.
- Violation handling is not structured per DQR; severity absent from REJ, REC, THR entries.
- Orphaned key detection (key=0 fallback) not stated as an explicit DQR.
- Null lineage_key check in fact rows is in FR-LIN-001, not in DQR section — creates audit gap.

---

## Improvement Items

Ordered by score impact (highest first):

1. **[All sections — Acceptance Criteria]** Add per-requirement acceptance criteria to every FR, NFR, and DQR. Use the reference format: a bullet list of testable conditions per requirement (e.g., "A run with no new source rows produces an empty staging table and does not fail"). → Removes −4 auto-deduct + recaptures AC criterion score across 3 sections → up to **+25 pts**

2. **[FR — Source References]** Add a `Source:` field per functional requirement pointing to the source specification section (e.g., `product-definition.yaml → input_ports`, or an equivalent internal document). → Recaptures source refs criterion → up to **+4 pts**

3. **[DQR — Summary Table]** Add a DQR summary table at the end of section 3 listing all 16 DQRs with ID, Title, Severity, Blocks Load, and Blocks Mart Promotion. → Recaptures summary table criterion → up to **+2.5 pts**

4. **[DQR — Violation Handling]** Add a labeled "**Violation handling:**" line to every DQR entry stating: severity (BLOCKING/Informational), action on violation (route to dq_rejections, halt, continue), and pipeline behavior. → Improves violation handling from 40% to ~90% → up to **+2.5 pts**

5. **[DQR — Content]** Add an explicit `DQR-OPH-001` for orphaned key detection (fact rows where FK=0 or NULL), and `DQR-LIN-001` asserting no null `lineage_key` in fact rows (currently in FR-LIN, not DQR). → Improves DQR content score → up to **+1.5 pts**

6. **[NFR — Observability]** Add a dedicated `NFR-OBS` subsection requiring that `lineage_key` is populated on every row across all layers and that `stg.dq_rejections` is written to for every DQ violation. → Recaptures observability theme from reference → up to **+1 pt**

7. **[FR — Sentinel Row FR]** Add an explicit FR stating that when SK resolution fails, the pipeline assigns sentinel key `0` from the appropriate dimension (equivalent to FR-007 in reference). → Improves FR content score → up to **+1 pt**

8. **[FR — Bootstrap FR]** Add an explicit FR covering the one-time bootstrap routine: insert sentinel rows (key=0) into dimension tables, seed `etl_cutoff` watermark, and pre-populate `dim.date`. Must be idempotent. → Closes bootstrap gap → up to **+1 pt**

9. **[Header — Metadata fields]** Add project name, document version/status, source document reference, and author/team attribution to the header block. → Improves header content score from 43 to ~80 → up to **+1 pt**

10. **[NFR — Acceptance Criteria detail]** Even before adding full per-NFR AC blocks, add quantified thresholds as testable conditions to the highest-risk NFRs: NFR-PRF-001 (batch window SLA), NFR-REL-001 (idempotency), NFR-MNT-002 (PROFIT_MARGIN_FACTOR externalisation). → Partial AC credit → incremental pts

11. **[DQR-AST-001 through DQR-AST-003]** State severity as `BLOCKING` explicitly in the requirement text (not just embedded in the ID label `DQ-SALE-001 (critical)`). → Improves violation handling severity coverage.

12. **[DQR-REJ-001 through DQR-REJ-004]** Add severity labels to rejection-handling DQRs (e.g., BLOCKING for the logging mechanism itself per reference DQR-004).

13. **[DQR-REC-001 through DQR-REC-003]** Add explicit severity (BLOCKING) to reconciliation DQRs and structured violation handling.

14. **[NFR-SEC-006]** The NFR already states secrets must be in Databricks Secrets — add a testable AC: "A static scan of all notebooks, Python modules, and YAML files finds zero hardcoded credential values."

15. **[FR-SRV-003]** The `[PENDING: CX-P05]` marker is correct; once role matrix is confirmed, add testable AC listing the specific grants required per role.

16. **[FR-TRN-009 — UDF]** Add an acceptance criterion: "Calling `get_total_quantity_sold(NULL, NULL)` returns 0 rather than NULL" — this is the key testable condition for the COALESCE guard.

17. **[FR-ORC-004]** Add AC: "A task that fails twice and a third execution also fails does not produce a fourth automatic retry; a halt-and-alert is raised."

18. **[NFR-PRF-004]** Materialized view refresh adds ≤15 min — add an AC: "Measured over 5 consecutive nightly runs, the mart refresh step completes in ≤15 minutes."

19. **[DQR-THR-001–002]** Add acceptance criteria: "A change to the rejection threshold in the control table takes effect on the next pipeline run without a code deployment."

20. **[Header]** Convert the italic metadata line to a proper markdown table or key-value block matching the reference header format.

---

## Priority Actions

Top 5 changes with greatest score impact:

1. **Add acceptance criteria to every requirement** — this is the single highest-value action. Start with the 12 FRs that map most closely to the reference (FR-ING-001, FR-ING-006, FR-TRN-005, FR-LIN-001, etc.), using the reference format: 3–5 bullet points per requirement stating testable conditions. This alone can recover up to **+25 pts** after removing the −4 auto-deduct and scoring the AC criterion. → Target score: 71–75/100.

2. **Add Source field to every FR** — add a `Source:` line per FR pointing to the product specification document or section. This requires knowing the source doc name; if not yet agreed, use `[PENDING: specify source doc]` as a placeholder. → Recovers source refs criterion → up to **+4 pts**.

3. **Add DQR summary table** — a single table listing all 16 DQRs with ID, Severity, Blocks Load, and Blocks Mart Promotion takes about 20 lines and immediately satisfies the summary table criterion. → up to **+2.5 pts**.

4. **Structure violation handling per DQR** — add a labeled `**Violation handling:**` line to each of the 16 DQRs. At minimum: severity label + action + pipeline behavior. Converts embedded description text into an explicit, auditable field. → Improves violation handling from 40% to 85%+ → up to **+2 pts**.

5. **Add observability NFR and bootstrap FR** — add `NFR-OBS` (lineage_key completeness, dq_rejections coverage, run-log row counts) and `FR-BOOT` (idempotent bootstrap: sentinel rows + watermark seed + date calendar init). These close two structural gaps against the reference. → up to **+2 pts** combined.

---

## Extra Sections Noted

The participant includes two sections beyond the reference scope:

- **§4 Interface Requirements** — 11 IFRs covering BI report data connections, upstream source strategy (`[PENDING: CX-P04]`), and downstream dependency contracts. Not in reference but well-structured and appropriate for the product.
- **§5 Constraints and Assumptions** — 14 CON entries covering platform, retention, schedule, PII, and pending decisions. Not in reference but provides valuable delivery-risk context.

Neither extra section is penalized. Both would benefit from acceptance criteria once the core sections are updated.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing AC, source refs, or violation handling |
| 0–44 | Incomplete | Major sections missing or requirements untraced |
