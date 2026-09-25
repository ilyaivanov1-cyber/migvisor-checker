# Check Report: TASK-AS-IS-001
**Skill:** as-is | **Trainee:** Inventory_Stock_Project | **Product:** Purchase
**Checker version:** v1 | **Generated:** 2026-09-25

---

## Score: 96 / 100 — Excellent

---

## Rubric Evaluation

### Coverage — 39 / 40

All 6 required sections present with comprehensive subsections:

- **§1 Definition:** 1.1 Definition narrative + 1.2 Metadata Table with 15 fields — exceeds the minimum of 10 required fields and meets the ≥15 target. All expected metadata attributes are present: domain name, business process, process type, business entities, business metrics, DQ rules (business and technical), storage, filters applied, calculated fields, consumers.
- **§2 Consumers:** Full consumer inventory table including `wwidw purchase and sale per stockitem dynamic`, `wwidw-ordered-by-supplier`, `migratestagedpurchasedata` (ETL dependency), and `analytics.v_ordertoyearanalytics` (cross-domain view with Package column dependency documented).
- **§3 Model:** ER diagram (Mermaid) in §3.1 + textual description table in §3.2. The ER diagram shows all tables with their column sets. Staging table documented with 14 columns (see gap note below).
- **§4 Lineage:** §4.0 target data flow, §4.1 key columns (10 columns), §4.2 Mermaid lineage diagram with Bronze/Silver/BI layers, §4.3 column-level lineage table, §4.4 11-step transformation table, §4.5 downstream dependencies. The lineage section is more detailed than the reference (11 steps vs 8 in reference) — this is a positive differentiator.
- **§5 Calculations:** §5.1 date key derivation, §5.2 ordered quantities, §5.3 SCD-2 surrogate key resolution with full T-SQL code.
- **§6 Sources:** §6.1 input sources (8 source tables), §6.2 output objects (7 tables).

Minor coverage gap (-1 pt): reference §6 enumerates source subsections in finer-grained groupings; trainee §6 uses a consolidated two-part structure that omits some secondary subsection labels present in the reference (e.g., separate subsections for OLTP tables, dimension tables, control objects). This is presentational rather than substantive.

### Specificity — 24 / 25

Exceptional specificity throughout. The SCD-2 resolution in §5.3 includes full T-SQL code with correct temporal boundary semantics (`> Valid From` exclusive, `<= Valid To` inclusive), the ORDER BY [Valid From] ASC tie-breaker, and `COALESCE(..., 0)` fallback — all three canonical specificity markers per SKILL.md domain notes. The Mermaid ER diagram in §3.1 is column-level detailed. The column-level lineage table in §4.3 traces each column from OLTP source to fact table with transformation annotations. The SSIS truncation bug is documented with the specific erroneous table name (`Integration.Order_Staging`) and the expected table name (`Integration.Purchase_Staging`).

Minor deduction (-1 pt): The consumer section does not provide the Databricks Workflow task dependency tree (nb_extract_watermark → nb_extract_purchase → migrate_staged_purchase_data) in as-is terms — this is reasonable for an as-is document but the reference elaborates on the consumer ETL dependency more fully.

### Technical Accuracy — 19 / 20

- SCD-2 boundary semantics: `> Valid From` (exclusive lower bound) and `<= Valid To` (inclusive upper bound) — correct ✓
- Tie-breaker: ORDER BY [Valid From] ASC — correct ✓
- COALESCE fallback: `COALESCE(..., 0)` for unresolved dimension lookups — correct ✓
- SSIS truncation bug: correctly identified and attributed to the `pipeline_item_truncate` step deleting from `Integration.Order_Staging` instead of `Integration.Purchase_Staging` — correct ✓
- Staging column count: trainee §3.2 states 14 columns and the column inventory includes `LineageKey` explicitly in staging. The reference notes 13 columns (not counting `LineageKey` as a staging column present at extract time). This is a minor count discrepancy (-1 pt); the difference reflects a slightly different interpretation of staging schema boundaries, not a factual error.
- All other technical details (stored procedure names, SSIS component names, catalog names, OLTP source table names) are accurate.

### Issues / Gaps — 9 / 10

**Minor gap:** Staging table column count interpretation differs from reference (14 vs 13). The trainee includes `LineageKey` as a staging column present after step 2 (SSIS sets it before writing to staging), which is technically defensible but differs from the reference's 13-column staging schema. The report should note this as a deliberate interpretation choice.

**Well-covered:** The SSIS truncation bug, all 8 input source tables, all 7 output objects, the SEQUENCE-to-IDENTITY migration implication, and the cross-domain analytics view dependency are all documented.

### Structure — 5 / 5

Logical section hierarchy followed throughout. Mermaid diagrams render correctly (syntax valid). Tables used for metadata, consumer inventory, model description, column-level lineage, and source inventory. All sections clearly delineated with markdown headings.

---

## Auto-Deduct Checks

| Check | Threshold | Result |
|---|---|---|
| SSIS staging truncation bug documented | Required — −4 pts if absent | PASS — documented in §4.4 step 2 with exact table names |
| COALESCE(..., 0) fallback documented | Required — −3 pts if absent | PASS — documented in §5.3 with T-SQL code |
| Metadata fields count ≥ 10 | Required — −4 pts if < 10 | PASS — 15 fields present (exceeds threshold) |

**Total auto-deductions: 0 pts**

---

## Cross-File Consistency Checks

No mandatory cross-file checks defined for as-is deliverable.

---

## Summary

The as-is document is one of the strongest deliverables in this batch. All 6 sections are substantively populated with correct technical content. The SCD-2 resolution section in §5.3 includes correct boundary semantics, tie-breaker logic, and COALESCE fallback — the three key specificity markers. The SSIS staging-truncation bug is correctly documented with the specific wrong table name. The 15-field metadata table exceeds requirements. The Mermaid ER and lineage diagrams provide excellent visual context. The primary gap is a minor staging column count interpretation difference (14 vs 13), reflecting the inclusion of `LineageKey` as a staging column; this is not a factual error but should be noted for consistency with downstream DDL.

---

## Priority Actions

1. Clarify the staging column count (14 vs 13): add a note explaining that `LineageKey` is included in the 14-column count because it is written to `integration.purchase_staging` by the SSIS procedure before the fact MERGE — this makes the trainee's interpretation explicit and justifiable.
2. In §2 Consumers, add the full task dependency chain (`getlastetlcutofftime` → `getpurchaseupdates` → SSIS container → `migratestagedpurchasedata`) to show the ETL consumer dependency more explicitly, matching the reference's consumer section depth.
3. In §6.2 Output Objects, add brief subsections grouping outputs by category (staging, fact, control, view) to match the reference's output organisation granularity.
