# Check Report: design
**Trainee:** Purchasing_Project
**Product:** Purchases
**Date:** 2026-09-23
**Score:** 79/100 — Good

## Path Note
File found at non-standard location: `products/Purchases/current/specifications/development_plan/design.md`
Expected standard path: `products/Purchases/current/codebase/docs/design.md`
Content scored as found; path deviation noted as a minor organizational gap.

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| §1 Data Model | 20 | 88 | 1.1 Entities (10 entities in a clear table with layer/description); 1.2 Attributes (column-level tables for every entity with type, nullable, description) |
| §1.3 Relationships | 15 | 82 | FK relationships documented within column descriptions; could be a formal Relationships subsection |
| §1.4 Indexes and Partitioning | 15 | 80 | Clustering keys specified for dim.supplier; fact.purchase partitioning noted; stg tables correctly noted as unpartitioned |
| §2 Ingestion | 15 | 82 | Source→target ingestion mapping table with all entities, watermark approach, incremental pattern |
| §3 Transformation | 15 | 80 | Calculation IDs (CALC-001 through CALC-004) with formulas; filter IDs (FLT-001) documented |
| §4 Serving | 10 | 72 | Output access profile referenced but mechanism is [USER INPUT REQUIRED] pending PL-009/OB-008 |
| §5 Observability | 10 | 75 | Lineage tracking, QV assertions, monitoring described; alert thresholds left as open items |

## Strengths
- Data Model section is reference quality: complete entity list with layer assignment + full attribute tables per entity including type, nullability, and descriptions for every column.
- CALC-001 through CALC-004 are clearly identified and cross-referenced to requirements, making the traceability chain explicit.
- The design correctly distinguishes ordered_quantity as a stored computed column (not GENERATED ALWAYS AS), preserving the source system's point-in-time semantics — this is a non-obvious design decision well-documented here.

## Gaps
- File placed in specifications/development_plan/ rather than codebase/docs/ — this breaks the standard path that pipeline tooling and skills expect.
- Serving section (§4) leaves the cross-catalog exposure mechanism unresolved ([USER INPUT REQUIRED]).
- Formal Relationships subsection (separate from column descriptions) would improve clarity.

## Priority Fixes
1. Move/copy file to the standard path `codebase/docs/design.md`: +5 pts (path conformance)
2. Resolve or stub the Serving layer with the decided access mechanism once PL-009/OB-008 is resolved: +5 pts
3. Add a formal §1.3 Relationships table listing FK pairs explicitly: +4 pts
