# Check Report: project-rules
**Trainee:** Purchasing_Project
**Product:** Purchases
**Date:** 2026-09-23
**Score:** 81/100 — Good

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| Header / Metadata | 12 | 88 | Version, generated date, source/target, active dimension count, project split context all documented |
| Dimension Table | 12 | 85 | 7 dimensions with file references and rule counts in a clean summary table |
| PL — Platform (10 rules) | 13 | 85 | Very specific intents covering SQL Server→Databricks mapping, catalog naming, Delta/CDF, sequence replacement, ETL pattern replacement; PL-008/009 cross-catalog decisions explicitly flagged |
| NM — Naming (10 rules) | 12 | 85 | Complete lowercase_snake_case mapping, space-containing object renaming, schema/catalog remapping, FK constraint naming |
| TY — Types (29 rules) | 13 | 82 | Comprehensive type mapping from SQL Server to Spark SQL with per-rule evidence notes; 14 baseline rules noted as "no current evidence" — honest coverage |
| OB — Objects (10 rules) | 12 | 82 | Per-object migration disposition; cross-catalog decisions flagged (OB-002, OB-008) |
| SX — Syntax (11 rules) | 13 | 80 | SQL Server→Spark SQL syntax rewriting rules including correlated subquery conversion, DECLARE rewrite, etc. |
| PE — Performance (8 rules) | 12 | 78 | Performance rules present; some rules may lack Liquid Clustering specifics |
| LN — Lineage (7 rules) | 11 | 75 | Lineage rules present; detail on lineage_run table schema could be richer |

## Strengths
- PL dimension (Platform) is the strongest section — 10 rules with highly specific intents covering every major migration pattern (sequence replacement, DELETE-then-INSERT redesign, valid-time key resolution, SSIS→Databricks Workflow, Delta MERGE).
- Type mapping (TY) is unusually complete at 29 rules, with honest "no current evidence" notes for baseline rules — this is more rigorous than typical submissions.
- Cross-catalog architectural decisions (PL-008, PL-009, OB-002, OB-008) are explicitly flagged as [USER INPUT REQUIRED] rather than left unresolved silently.

## Gaps
- IF (Interface) dimension is absent — if present in the reference, this is a systematic omission costing approximately 15 pts.
- LN (Lineage) dimension's lineage_run table schema and run_id generation strategy are not spelled out in the intents.
- PE (Performance) rules may not reference Liquid Clustering or Z-ORDER specifications explicitly.

## Priority Fixes
1. Add IF (Interface) dimension if present in reference rubric: up to +15 pts
2. Strengthen LN dimension with explicit lineage_run table schema and lineage key counter mechanics: +4 pts
3. Add Liquid Clustering / Z-ORDER specifications to PE rules where relevant: +3 pts
