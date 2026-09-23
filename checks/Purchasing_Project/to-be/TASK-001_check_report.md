# Check Report: to-be
**Trainee:** Purchasing_Project
**Product:** Purchases
**Date:** 2026-09-23
**Score:** 84/100 — Good

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| §1 Definition | 17 | 85 | 15-field metadata table with only 3 [USER INPUT REQUIRED] fields; calculated fields, technical DQ rules, storage details all populated |
| §1.1 Definition narrative | 12 | 88 | Clear product identity in target terms; grain, key components, dimensions correctly specified |
| §1.2 Metadata Table | 17 | 82 | All 15 fields present; Business DQ Rules, Process Type, Data Access are [USER INPUT REQUIRED] — legitimate open items |
| §2 Consumers | 17 | 85 | All 3 cross-catalog consumers identified; full use case descriptions, business questions, consumption method (correctly flagged as [USER INPUT REQUIRED] pending PL-009/OB-008 decision) |
| §3 Model (ER Diagram) | 17 | 88 | Mermaid ER diagram with complete entity set; column types, PK/FK markers present; includes stg and meta tables |
| Fragment assembly metadata | Note | — | Fragment assembly instructions (stop conditions, written-by/read-by annotations) are visible in the document — these are generation artifacts, not missing content. No score penalty. |

## Strengths
- All three cross-catalog consumers are documented with full detail including business questions, use cases, and an honest [USER INPUT REQUIRED] on the consumption mechanism — this reflects correct understanding of the open architectural decision.
- The Consumers section discovered and documented wwidw-ordered-by-supplier (a third consumer not in the scope document), showing thorough lineage graph analysis.
- Metadata table fields 10 (Filters Applied) and 11 (Calculated Fields Added) are exceptionally detailed — specific Spark range-join patterns, MERGE semantics, and formula for ordered_quantity are all documented.

## Gaps
- Process Type (Field 3), Data Access and Restrictions (Field 8), and Business DQ Rules (Field 12) remain [USER INPUT REQUIRED].
- Cross-catalog exposure mechanism for all three consumers is unresolved — a placeholder accepted here but should be tracked for resolution.
- Fragment assembly stop-condition instructions are visible in the output document (e.g., "Stop condition: Stop immediately after the metadata table") — indicates the assembly pipeline needs cleanup.

## Priority Fixes
1. Resolve or escalate Process Type and Business DQ Rules with the product owner: +5 pts
2. Strip or relocate fragment assembly metadata (stop conditions, transformation summaries) into comments or a separate internal doc: +4 pts
3. Once PL-009/OB-008 is decided, fill in the Consumption Method field for all three consumers: +3 pts
