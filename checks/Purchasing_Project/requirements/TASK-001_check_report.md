# Check Report: requirements
**Trainee:** Purchasing_Project
**Product:** Purchases
**Date:** 2026-09-23
**Score:** 82/100 — Good

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| §1 Functional Requirements | 25 | 85 | 8 FRs with ID, Title, Description, Priority, Acceptance Criterion, Source; covers ingest, key resolution, calculation, lineage, MERGE load, output access, incremental cadence |
| §2 Non-Functional Requirements | 25 | 78 | 3 NFRs (uptime, latency, access control); Acceptance Criteria for NFR-001 and NFR-002 are [OWNER INPUT REQUIRED] — legitimate open items for SLA targets |
| §3 Data Quality Requirements | 25 | 85 | 3 DQRs (row-count reconciliation, unknown-key monitoring, referential conformity) — exactly matching the QA rules; NFR-005 threshold left as [OWNER INPUT REQUIRED] |
| Traceability / Source cross-refs | 25 | 80 | Each FR has a Source field referencing the product-definition YAML; DQRs reference specific QA rules (QA-001, QA-002, QA-003); some DQR→AC traceability links are missing |

## Strengths
- All 8 functional requirements are clearly specified with measurable acceptance criteria — FR-001 through FR-006 have "100% of rows" quantified ACs that are directly testable.
- DQR section is perfectly aligned with the QA transformation rules (QA-001/002/003), showing strong traceability from transformation rules → requirements.
- Source field per requirement links back to the product-definition YAML with specific port/section references, enabling full traceability from requirements to data product contract.

## Gaps
- NFR-001 (uptime) and NFR-002 (latency) Acceptance Criteria are [OWNER INPUT REQUIRED] — these need quantified thresholds before the NFR can be treated as acceptance-testable.
- FR-007 (cross-catalog consumer output) Acceptance Criterion is [OWNER INPUT REQUIRED] pending PL-009/OB-008 resolution.
- DQR→AC traceability is not explicit — DQR items are not cross-referenced to specific FR Acceptance Criteria rows.
- No explicit Acceptance Criteria section separate from per-requirement fields.

## Priority Fixes
1. Resolve NFR-001/NFR-002 SLA thresholds with the product owner and fill the Acceptance Criteria: +5 pts
2. Add DQR→FR traceability annotations (e.g., NFR-004 validates FR-006 AC): +3 pts
3. Resolve FR-007 AC once PL-009/OB-008 cross-catalog mechanism is decided: +3 pts
