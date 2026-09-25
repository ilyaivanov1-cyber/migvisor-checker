# Check Report: TASK-TR-002
**Skill:** project-rules | **Trainee:** Inventory_Stock_Project | **Product:** Purchase
**Checker version:** v1 | **Generated:** 2026-09-25

---

## Score: 95 / 100 — Excellent

---

## Rubric Evaluation

### Per-Dimension Rule Coverage — 38 / 40

The project-rules document covers 8 dimensions. All 7 SKILL.md-expected dimensions are present (PL, NM, TY, OB, SX, PE, LN) plus an additional IF (Interface) dimension:

| Dimension | Expected Count | Actual Count | Match |
|---|---|---|---|
| PL (Platform/Layer) | 10 | 10 | ✓ |
| NM (Naming) | 9 | 9 | ✓ |
| TY (Types) | 26 | 26 | ✓ |
| OB (Objects) | 11 | 11 | ✓ |
| SX (Semantics/Execute) | 17 | 17 | ✓ |
| PE (Performance) | 9 | 9 | ✓ |
| LN (Lineage) | 8 | 8 | ✓ |
| IF (Interface) | N/A (bonus) | 5 | Bonus ✓ |

All 7 expected dimensions present and counts exact. No auto-deductions apply.

Key rules verified:
- TY-012: DATETIME2→TIMESTAMP_NTZ ✓
- SX-003: critical SCD-2 correlated subquery → sk_resolver.py pre-join ✓
- LN-001: integration.lineage → bronze.lineage_run migration ✓
- PE-002: liquid clustering on Silver tables ✓
- OB-010: excluded objects list ✓
- Application order stated in dimension summary table ✓
- lineage_run DDL schema included ✓

Minor gap (-2 pts): The IF dimension (5 rules) is not in the SKILL.md expected count but its presence is architecturally valuable. However, the IF rules partially overlap in intent with rules in OB and SX dimensions (e.g., dimension load ordering is also covered in OB-007 and SX-003). This overlap creates some redundancy without clear delineation of when IF rules apply vs OB/SX rules.

### Per-Dimension Intent Accuracy — 23 / 25

Each rule's intent is clearly stated. SX-003 correctly explains the pattern replacement: T-SQL `UPDATE staging SET key = (SELECT TOP(1) ... correlated subquery)` → broadcast join + ROW_NUMBER() OVER (PARTITION BY) + COALESCE(0). LN-001 correctly documents the integration.lineage → lineage_run migration with CDF enablement rationale. PE-002 correctly identifies CLUSTER BY as the replacement for SQL Server columnstore indexes. OB-010 correctly enumerates objects excluded from migration scope. NM-001 through NM-009 cover all naming convention dimensions with appropriate rationale for snake_case, space resolution, schema layer mapping, and UTC suffix.

Minor gap (-2 pts): Some TY rules (particularly TY-017 through TY-026) have terse technical descriptions that state the mapping without explaining the migration implication or why the mapping was chosen. Production-grade rule documentation benefits from the "why" as well as the "what".

### Technical Accuracy — 19 / 20

- DATETIME2→TIMESTAMP_NTZ (TY-012): correct mapping per Databricks type system ✓
- BIT→BOOLEAN (TY-015): correct ✓
- BIGINT IDENTITY → GENERATED ALWAYS AS IDENTITY (TY-017): correct ✓
- SX-003 temporal range join semantics: `last_modified_when > CAST(valid_from AS TIMESTAMP) AND last_modified_when <= CAST(valid_to AS TIMESTAMP)` — correct, consistent with SCD-2 boundary semantics from as-is ✓
- LN-001 CDF (Change Data Feed) enablement on lineage_run: correct ✓
- OB-004 lineage_run DDL schema: 9 columns matching SKILL.md expectation ✓
- Minor accuracy concern (-1 pt): PE-002 mentions CLUSTER BY as the default strategy without explicitly referencing the DBR 13.3 version gate. The product-level TY-P001 override should be the reference for dimension validity column types, but TY-012 in project rules maps DATETIME2→TIMESTAMP_NTZ without noting the TY-P001 exception for SCD-2 validity columns. This creates a potential confusion about which rule applies to valid_from/valid_to.

### Metadata Correctness — 9 / 10

Active Dimensions metadata section is present with dimension counts, application order, and category breakdown. Total rule count stated as 90 (7 expected dimensions) which matches the sum of SKILL.md expected counts exactly. Application order (PL → NM → TY → OB → SX → IF → PE → LN) is stated and logical. Minor: the metadata section does not include an explicit cross-reference to the product-transformation-rules.md document for the extension/override rules that build on this project baseline.

### Structure — 5 / 5

Consistent rule block format. Dimension sections clearly separated with counts stated in headings. Application order table present. Dimension summary table present. Rule IDs consistently formatted (e.g., PL-001 through PL-010, SX-001 through SX-017).

---

## Auto-Deduct Checks

| Check | Threshold | Result |
|---|---|---|
| LN dimension present | −5 pts if absent | PASS — LN dimension with 8 rules present |
| TY dimension rule count = 26 | −3 pts if wrong | PASS — TY has exactly 26 rules |
| TY-012 (DATETIME2→TIMESTAMP_NTZ) present | Required | PASS — TY-012 present |
| SX-003 (critical SCD-2 conversion) present | Required | PASS — SX-003 present |
| LN-001 (lineage_run schema) present | Required | PASS — LN-001 present |

**Total auto-deductions: 0 pts**

---

## Cross-File Consistency Checks

No mandatory cross-file checks defined for project-rules deliverable.

---

## Summary

The project-rules document is exemplary. All 7 expected dimensions are present with counts that exactly match SKILL.md expectations (PL:10, NM:9, TY:26, OB:11, SX:17, PE:9, LN:8 = 90 total). The three mandatory rule verifications all pass: TY-012 (DATETIME2→TIMESTAMP_NTZ), SX-003 (SCD-2 correlated subquery replacement), and LN-001 (lineage_run migration). The IF dimension bonus adds 5 additional interface contract rules. The primary improvement opportunities are in rule documentation depth (adding "why" to TY rules) and clarifying the relationship between TY-012 (project default) and TY-P001 (product override) for SCD-2 validity column types.

---

## Priority Actions

1. Add a cross-reference note to TY-012 stating that the TY-P001 product-level override takes precedence for SCD-2 `valid_from`/`valid_to` columns specifically, mapping them to DATE rather than TIMESTAMP_NTZ — this prevents misapplication of TY-012 to dimension validity columns.
2. For TY-017 through TY-026, expand rule descriptions to include the migration implication beyond the type mapping (e.g., TY-022: DATETIMEOFFSET→TIMESTAMP_NTZ requires UTC normalisation at extract time using `AT TIME ZONE 'UTC'` in the JDBC query or a Python equivalent).
3. Add an explicit cross-reference table in the metadata section mapping project rules to their product-level extensions and overrides in product-transformation-rules.md, providing complete traceability across the two-tier rule hierarchy.
4. Clarify IF dimension boundary with OB and SX: state explicitly which IF rules take precedence over OB/SX rules when both apply to the same object (e.g., dimension load ordering — is this governed by IF-001 or OB-007?).
