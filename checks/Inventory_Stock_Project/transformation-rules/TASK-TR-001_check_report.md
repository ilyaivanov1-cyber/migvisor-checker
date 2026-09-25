# Check Report: TASK-TR-001
**Skill:** transformation-rules | **Trainee:** Inventory_Stock_Project | **Product:** Purchase
**Checker version:** v1 | **Generated:** 2026-09-25

---

## Score: 93 / 100 — Excellent

---

## Rubric Evaluation

### Rule Coverage — 38 / 40

All 10 product transformation-rule dimensions are present:
- **PL** (Platform/Layer): 10 rules — maps schema layers, SSIS→Workflow, SEQUENCE retirement, Medallion architecture assignment.
- **NM** (Naming): 9 rules — snake_case, space resolution (NM-002), schema→layer mapping (NM-003/NM-005), stored procedure renaming (NM-004), UTC suffix convention (NM-009).
- **TY** (Types): 30 rules — includes 26 inherited project rules plus 4 product extensions (TY-P001, TY-P002, TY-P003, TY-P004). TY-P001 override (valid_from/valid_to → DATE) present ✓.
- **OB** (Objects): 15 rules — covers fact table clustering, staging OVERWRITE mode, SCD-2 _current views, Python notebook replacements, shared module naming.
- **SX** (Semantics/Execute): 21 rules — includes SX-003 (TOP(1) correlated subquery → sk_resolver.py), SX-001/SX-002 (T-SQL MERGE → Delta MERGE INTO / DELETE+INSERT), all execution pattern migrations.
- **IF** (Interface): 3 product-only rules — dimension load ordering contract, SK resolution data contract, DQ gate interface.
- **PE** (Performance): 11 rules — CLUSTER BY, liquid clustering, autoOptimize, broadcast hints, conditional OPTIMIZE.
- **LN** (Lineage): 9 rules — LN-P001 (dbutils.jobs.taskValues for lineage_key), integration.lineage → lineage_run, SEQUENCE retirement, CDF enablement.
- **QA** (Quality): 5 rules — QA-P001 through QA-P005 covering row count reconciliation, orphaned SK detection, RI checks, business rule assertions, dq_rejections store.
- **CX** (Custom/Extensions): 6 rules — CX-P001 through CX-P006 covering environment.yaml externalisation, UDFs, standard codebase layout, ETL skeleton, DDL header block.

All 10 dimensions present — no auto-deductions for missing QA or CX dimensions.

Minor gap (-2 pts): The rule count breakdown in the Active Dimensions metadata section claims 26 customisations (1 override, 13 extensions, 12 new). The override count of 1 (TY-P001) is correct. The extension/new split (13/12) is plausible but the trainee's TY dimension at 30 rules includes all 26 inherited project TY rules plus 4 product TY rules — this inflation relative to the SKILL.md expectation of a more selective product rule set means some inherited rules appear to be re-stated rather than purely customised, creating ambiguity in the customisation accounting.

### Intent Accuracy — 23 / 25

The intent behind each customisation is clearly articulated. TY-P001 explains WHY `DATE` is used instead of `TIMESTAMP_NTZ` for SCD-2 validity columns (alignment with calendar dimension join semantics and partition elimination). OB-P001 explains the sentinel bootstrap requirement. OB-P002 explains the lineage_key + _extracted_at_utc audit column rationale. LN-P001 correctly explains that taskValues propagation eliminates the need for re-reading from storage between tasks. QA-P001 through QA-P005 correctly distinguish blocking vs non-blocking behaviour.

Minor gap (-2 pts): IF dimension intent (dimension load ordering contract, SK resolution data contract, DQ gate interface) is described at a high level but does not enumerate the specific dependency failure modes and fallback behaviours that would be expected in a production-grade interface contract.

### Technical Accuracy — 18 / 20

- TY-P001 override: valid_from/valid_to → DATE (not TIMESTAMP_NTZ) — correct ✓
- TY-P002: 5-column SCD-2 control block (valid_from, valid_to, row_effective_date, row_expiry_date, is_current_row) — correct ✓
- TY-P003: MONEY→DECIMAL(18,2); SMALLMONEY→DECIMAL(10,2) — correct ✓
- TY-P004: geography CLR → 3 columns (WKT STRING, lat DOUBLE, lon DOUBLE) — correct ✓
- OB-P003: _current views as CREATE OR REPLACE VIEW (not MATERIALIZED) for thin row-filter wrappers; Gold analytics views as MATERIALIZED VIEW — correct ✓
- OB-P004: scd2_merge.py, sk_resolver.py, fact_merge.py as named shared module helpers — correct ✓
- LN-P001: dbutils.jobs.taskValues.set/get pattern — correct ✓
- deactivations.yaml: absent (correctly not present since no project rules are deactivated) ✓
- Minor technical accuracy concern (-2 pts): TY dimension inflates to 30 rules by including all 26 inherited project TY rules in the product file. The canonical pattern is for the product file to list only the product-specific overrides and extensions (4 rules: TY-P001 through TY-P004), with inherited rules living in the project-rules document. The current approach creates rule duplication across project-rules.md and product-transformation-rules.md.

### Metadata Correctness — 9 / 10

Active Dimensions metadata section is present and lists all 10 dimensions with rule counts and application order. Customisation summary (1 override, 13 extensions, 12 new = 26 total) is present. The claim of "0 deactivations" is correct per the absent deactivations.yaml. Minor deduction: the file reference paths for rule source documents could be more explicit (some rules cite rule IDs without cross-referencing the project-rules document that defines the inherited baseline).

### Structure — 5 / 5

Consistent rule block format throughout: Rule ID, Title, Category (Override/Extension/New), Rationale, Technical Detail, Rules Applied. Application order table present. All 10 dimensions have proper markdown headings with rule counts.

---

## Auto-Deduct Checks

| Check | Threshold | Result |
|---|---|---|
| QA dimension present | −5 pts if absent | PASS — QA-P001 through QA-P005 present |
| CX dimension present | −5 pts if absent | PASS — CX-P001 through CX-P006 present |
| TY-P001 override (valid_from/valid_to → DATE) | −3 pts if absent | PASS — TY-P001 present and correct |
| deactivations.yaml empty/absent | Verify | PASS — absent (correct; no project rules deactivated) |

**Total auto-deductions: 0 pts**

---

## Cross-File Consistency Checks

No mandatory cross-file checks defined for transformation-rules deliverable.

---

## Summary

The product transformation-rules document covers all 10 required dimensions with correct technical content. The three mandatory elements — QA dimension, CX dimension, and TY-P001 override — are all present and correct. The customisation accounting (1 override, 13 extensions, 12 new) aligns with SKILL.md expectations. The primary structural concern is that the TY dimension (30 rules) includes all 26 inherited project TY rules restated in the product file, which duplicates the project-rules baseline and complicates the boundary between project and product rules. The IF dimension provides a useful interface contract layer that is absent from the reference but adds value. QA and CX dimensions are complete and technically correct.

---

## Priority Actions

1. Refactor the TY dimension in product-transformation-rules.md to list only the 4 product-specific TY rules (TY-P001 through TY-P004) with explicit notation that the 26 inherited TY rules are defined in project-transformation-rules.md — this eliminates rule duplication and clarifies the project-vs-product boundary.
2. Expand the IF dimension rules to include specific failure modes: what happens if the dimension load task fails before the fact task runs, what the fallback behaviour is for SK resolution when the dimension table is empty or stale.
3. Add explicit cross-references in the Active Dimensions metadata table linking each product rule to the inherited project rule it overrides or extends, providing traceability from product customisation back to the project baseline.
