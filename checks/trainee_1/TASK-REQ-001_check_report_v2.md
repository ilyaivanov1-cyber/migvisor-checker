---
task_id: TASK-REQ-001
skill: task-checker-requirements
participant_file: trainees/trainee_1/requirements.md
reference_file: reference/requirements.md
product: Sales_Orders
generated: 2026-09-03
total_score: 46/100
grade: Needs Work
---

# TASK-REQ-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase (GlobalPurchase_Project)
**Participant file:** `trainees/trainee_1/requirements.md`
**Reference file:** `reference/requirements.md`
**Generated:** 2026-09-03

---

## Score Summary

**The requirements document Score: 46/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 25 | 42/100 | 10.5 | ⚠ |
| Functional Requirements | 25 | 50/100 | 12.5 | ⚠ |
| Non-Functional Requirements | 25 | 69/100 | 17.1 | ⚠ |
| Data Quality Requirements | 25 | 52/100 | 13.0 | ⚠ |
| **Subtotal** | | | **53.1** | |
| Auto-deducts | | | **-7** | |
| **Total** | | | **46/100** | |

**Grade: Needs Work**

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No requirement IDs anywhere in document | −5 pts | No — all requirements carry traceable IDs (FR-ING-001, NFR-PRF-001, DQR-AST-001, etc.) |
| Missing H2 section present in reference but absent in participant | −5 pts each | No — all 3 reference sections present (FR, NFR, DQR) |
| No acceptance criteria anywhere in document | −4 pts | Yes — zero requirements across FR, NFR, and DQR have any acceptance criteria |
| More than 30% of requirements lack individual acceptance criteria | −3 pts | Yes — 100% of requirements (all ~70 entries) lack individual AC |
| Any requirement entry has no description (ID only) | −2 pts/occurrence | No — every requirement has a description |
| Missing `[PENDING]` markers for open items | −2 pts | No — [PENDING: CX-P04], [PENDING: CX-P05], [PENDING: CX-DQ-01] all present and correctly applied |

---

## Section Feedback

### Header Metadata (10.5/25 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Sub-criteria breakdown (raw 42/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Product/project identification | 30% | 50/100 | Product name "Sales_Orders" present; project name absent |
| Temporal metadata | 20% | 75/100 | Generation date present; pipeline stage present; no version field |
| Document scope | 30% | 30/100 | Pipeline stage present; source documents not referenced |
| Author/ownership | 20% | 0/100 | No author or team attribution |

**Strengths:**
- Product name clear in H1 title
- Generation date present (2026-06-05)
- Pipeline stage labelled

**Gaps:**
- Project name absent (reference has `Project: GlobalPurchase_Project`)
- Source documents not referenced (reference lists `Source: product-definition.yaml`)
- No author or team attribution
- No version field

---

### Functional Requirements (12.5/25 pts)

**Criteria scored:** Content (50%), Acceptance Criteria (25%), Source References (15%), Structure (10%)

**Content completeness (80/100):**
- Functional areas covered: 9/12 reference themes present
  - ✓ Incremental ingestion (ING-001, ING-002)
  - ✓ Watermark management (ING-006)
  - ✓ SCD Type 2 dimension loading (TRN-005 covers 6 dimensions)
  - ✓ Static date calendar (TRN-006)
  - ✓ Fact table loading (TRN-001, TRN-002)
  - ✓ Lineage tracking (ING-003/004, LIN-001 to LIN-004)
  - ✓ DQ integration and rejection handling (LIN-003, cross-reference to DQR)
  - ✓ Mart and serving layer (SRV-001 to SRV-004)
  - ✓ Additional: calculated fields (TRN-003/004), PII masking (TRN-008), UDF consolidation (TRN-009/010/011/012/013), orchestration (ORC section)
  - ✗ Sentinel row fallback / orphaned key handling (no FR equivalent to reference FR-007)
  - ✗ Source truncation correction (no FR equivalent to reference FR-010)
  - ✗ Bootstrap initialization (no FR equivalent to reference FR-011)
- Requirement count: 34 participant vs 12 reference — capped at 100%
- Score: (9/12)×40% + (9/12)×40% + 100%×20% = **80/100**

**Acceptance criteria (0/100):**
- Requirements with AC: 0/34 = 0%
- No requirement in the FR section has an "Acceptance Criteria" field or any AC content
- Score: 0/100

**Source references (0/100):**
- Requirements with Source field: 0/34 = 0%
- No requirement references a source specification, design document, or configuration key
- Score: 0/100

**Structure (100/100):**
- H2 heading present: Yes (## 1. Functional Requirements)
- Subsections organized: Yes (1.1 Ingestion, 1.2 Transformation, 1.3 Serving, 1.4 Orchestration, 1.5 Lineage)
- Requirement IDs present: Yes — 100% coverage
- Consistent ID scheme: Yes — FR-{GROUP}-{NNN} throughout

**Strengths:**
- 34 requirements across 5 well-named subsections covering all major pipeline layers
- Highly detailed technical descriptions: table names, column names, SQL constructs, SLA timestamps, data types
- [PENDING: CX-P04] correctly embedded at point of uncertainty (ING-006, IFR-SRC-001)
- Extra functional areas beyond reference scope (UDFs, PII masking, mart views, ORC section)

**Gaps:**
- No acceptance criteria on any FR — missing the "how will we know it works" layer entirely
- No Source field — no traceability from requirements to source specs or design docs
- FR-007 equivalent (sentinel/orphaned key fallback) not in FR section
- Bootstrap initialization and source truncation correction themes absent

---

### Non-Functional Requirements (17.1/25 pts)

**Criteria scored:** Content (65%), Acceptance Criteria (25%), Structure (10%)

**Content completeness (90/100):**
- Functional areas covered: 7/8 reference NFR themes present
  - ✓ Performance: NFR-PRF-001 to 005 (pipeline SLA, clustering, ZORDER, materialized view refresh, BI query latency)
  - ✓ Availability: NFR-REL-003 (99% success rate), NFR-REL-005 (SQL endpoint 99.5%), ORC-003/004 (retry + alert in FR)
  - ✓ Security: NFR-SEC-001 to 006 (Unity Catalog, CLS masking, RLS, least privilege, TLS, secrets)
  - ✓ Scalability: NFR-SCL-001 to 003 (3× growth, liquid clustering re-evaluation, retention)
  - ✓ Idempotency: NFR-REL-001 (explicit idempotency requirement)
  - ✓ Maintainability: NFR-MNT-001 to 005 (Git versioning, constants, config externalisation, modular execution, test coverage)
  - ✓ Data Retention: NFR-SCL-003 (bronze 90d / silver 7y / gold 3y)
  - ✗ Observability: not a named NFR (lineage is in FR-LIN; no NFR for lineage_key coverage, dq_rejections logging, or pipeline log row counts)
- Requirement count: 19 participant vs 8 reference — capped at 100%
- Score: (7/8)×40% + (7/8)×40% + 100%×20% = **90/100**

**Acceptance criteria (0/100):**
- Requirements with AC: 0/19 = 0%
- No NFR has an "Acceptance Criteria" section or equivalent
- Score: 0/100

**Structure (100/100):**
- H2 heading present: Yes (## 2. Non-Functional Requirements)
- Subsections organized: Yes (2.1 Performance, 2.2 Scalability, 2.3 Reliability, 2.4 Security, 2.5 Maintainability)
- Requirement IDs present: Yes — 100% coverage
- Consistent ID scheme: Yes — NFR-{GROUP}-{NNN} throughout

**Strengths:**
- Strongest section in the document — content is detailed, domain-specific, and well-organized
- Security requirements (6 NFRs) are more thorough than the reference equivalent
- Idempotency requirement explicit and well-defined (NFR-REL-001)
- Data retention policy specific to layer (bronze/silver/gold with numeric durations)

**Gaps:**
- No acceptance criteria on any NFR — the most impactful single gap
- Observability missing as an explicit NFR (lineage_key population, dq_rejections, log row counts)

---

### Data Quality Requirements (13.0/25 pts)

**Criteria scored:** Content (40%), Acceptance Criteria (25%), Violation Handling (15%), Summary Table (10%), Structure (10%)

**Content completeness (83/100):**
- Functional areas covered: 5/6 reference DQR themes present
  - ✓ Row count reconciliation: DQR-REC-001 to 003
  - ✓ FK referential integrity: DQR-AST-004, DQR-AST-005
  - ✓ DQ rejection logging: DQR-REJ-001 to 004 (detailed schema + requirements)
  - ✓ Configurable DQ thresholds: DQR-THR-001/002 (with PENDING markers)
  - ✗ Null lineage_key assertion: covered in FR-ING-003/004 but absent as a named DQR assertion
  - ✗ DQ assertion ordering guarantee: DQR-AST-006/007 imply ordering, but no explicit "assertion ordering guarantee" DQR
- Requirement count: 16 participant vs 6 reference — capped at 100%
- Score: (5/6)×40% + (4.5/6)×40% + 100%×20% = **83/100**

**Acceptance criteria (0/100):**
- Requirements with AC: 0/16 = 0%
- No DQR has an explicit "Acceptance Criteria" section
- Score: 0/100

**Violation handling (60/100):**
- DQRs with severity labels: ~7/16 = 44% (DQR-AST-001 to 005 have inline severity; others do not)
- DQRs with explicit action on violation: ~12/16 = 75% (routing to dq_rejections, halt/continue specified)
- DQRs with pipeline behavior (stop/continue/retry): ~9/16 = 56%
- Score: 44%×30% + 75%×40% + 56%×30% = **60/100**

**Summary table (0/100):**
- No DQR summary table present
- Reference has a summary table listing all DQRs with Severity, Blocks Load, Blocks Mart Promotion columns
- Score: 0/100

**Structure (100/100):**
- H2 heading present: Yes (## 3. Data Quality Requirements)
- Subsections organized: Yes (3.1 Assertions, 3.2 Rejection Handling, 3.3 Row Count Reconciliation, 3.4 Pending Thresholds)
- Requirement IDs present: Yes — 100% coverage
- Consistent ID scheme: Yes — DQR-{TYPE}-{NNN} throughout

**Strengths:**
- DQR section is more comprehensive than reference in coverage of rejection handling (dedicated subsection)
- Severity classification present in assertions (critical, error inline labels)
- Pipeline halt vs continue behavior described for most assertion types
- [PENDING: CX-DQ-01] correctly embedded at points of threshold uncertainty

**Gaps:**
- No AC per DQR — most impactful gap
- No DQR summary table (quick reference grid by severity/blocking status)
- Severity labels inconsistently applied — only 7/16 DQRs have labeled severity
- Null lineage_key not covered as an explicit DQR assertion (it's in the FR section)
- Formal "Violation Handling:" labeled field absent; handling is embedded in prose

---

## Improvement Items

1. **[All Sections — Acceptance Criteria]** Add explicit AC to every requirement in FR, NFR, and DQR — currently earning 0/100 on AC in all three sections, plus triggering both AC auto-deducts → up to +25.9 pts combined (section gains + deduct removal)
2. **[Header — All Missing Fields]** Add project name, source document reference, and author/team attribution → up to +11.1 pts
3. **[Functional Requirements — Source References]** Add `Source:` field to every FR pointing to source spec section or design document → up to +3.75 pts (after AC is added)
4. **[DQR — Summary Table]** Add a DQR summary table listing all DQRs with ID, severity, Blocks Load, Blocks Mart Promotion → up to +2.5 pts
5. **[DQR — Violation Handling]** Add explicit labeled `Violation Handling:` section per DQR item; apply severity to all 16 DQRs → up to +1.5 pts additional
6. **[DQR — Content Coverage]** Add explicit null-lineage_key DQ assertion and DQ-ordering-guarantee DQR as named requirements → up to +1.0 pt
7. **[FR — Content Coverage]** Add explicit requirements for sentinel row fallback, source truncation correction, and bootstrap initialization → up to +1.5 pts
8. **[NFR — Observability]** Add an explicit Observability NFR covering lineage_key population, dq_rejections logging, and pipeline log row counts → up to +1.0 pt

---

## Priority Actions

1. **Add acceptance criteria to every requirement across FR, NFR, and DQR** — each AC section should have measurable conditions (counts, thresholds, pass/fail behavior) and reference specific artifacts (table names, column names, system components) → up to +25.9 pts combined
2. **Complete header metadata** — add project name (`Project: Sales_Orders`), source document reference (`Source: product-definition.yaml` or equivalent), and author/team attribution → up to +11.1 pts
3. **Add Source field to all Functional Requirements** — reference the specification section or configuration key that drives each requirement → up to +3.75 pts
4. **Complete DQR section** — add DQR summary table and explicit Violation Handling per DQR; promote null-lineage_key to a named DQR assertion → up to +4.0 pts

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| **45–59** | **Needs Work** | **Missing AC, source refs, or violation handling** |
| 0–44 | Incomplete | Major sections missing or requirements untraced |
