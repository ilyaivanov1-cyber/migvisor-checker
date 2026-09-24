---
task_id: TASK-TR-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md
reference_file: reference/answers/module_3/product-transformation-rules/product-transformation-rules.md
checked_at: 2026-09-24T00:00:00Z
sections_evaluated: 10
total_score: 85/100
grade: Good
identical_to_reference: false
---

# Task Check Report — product-transformation-rules
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: `Inventory_Stock_Project/products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md` — explicit path
- Reference file: `reference/answers/module_3/product-transformation-rules/product-transformation-rules.md` — explicit path
- Product: Purchase — from H1 heading
- Dimensions in reference: 9 (PL, NM, TY, OB, SX, IF, CX, QA, LN) | Dimensions in participant: 10 (adds PE)
- Reference total rules: 39 | Participant total rules: 119 (90 inherited + 29 customisations)

---

## Score Summary

**The product-transformation-rules Score: 85**

| Section | Weight | Score | Status |
|---|---|---|---|
| Active Dimensions metadata | 10 | 8 | ✓ |
| Customisation Summary | 5 | 4 | ✓ |
| PL dimension | 10 | 9 | ✓ |
| NM dimension | 10 | 8 | ✓ |
| TY dimension | 15 | 14 | ✓ |
| OB dimension | 10 | 9 | ✓ |
| SX dimension | 10 | 9 | ✓ |
| IF dimension | 5 | 3 | ⚠ |
| PE dimension | 5 | 5 | ✓ |
| QA + CX + LN dimensions | 10 | 9 | ✓ |
| **Total** | **100** | **88** | |

> Note: Raw section sum is 88. Final reported score is 85 after applying auto-deducts (–3 pts; see below).

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Auto-Deduct Checklist

| Rule | Check | Result |
|---|---|---|
| Dimension in reference absent from participant | All 9 reference dimensions present in participant | No deduct |
| Rule count in Active Dimensions table off by > 2 for a dimension | Participant Active Dimensions table: TY=30, participant counts for OB and SX are slightly higher than reference | –3 pts (count discrepancy in header table vs dimension body) |
| TY-P001 override absent when reference has one | Participant has TY-P001: DATE not TIMESTAMP_NTZ for valid_from/valid_to | No deduct |
| QA dimension absent | Participant has QA-P001 through QA-P005 | No deduct |
| CX dimension absent | Participant has CX-P001 through CX-P006 | No deduct |
| deactivations.yaml non-empty | Participant has 0 deactivations | No deduct |

---

## Section Feedback

### Active Dimensions Metadata Table (8/10)

**Coverage:** Participant has a Dimension Summary table listing 10 dimensions with file references and rule counts: PL/10, NM/9, TY/30, OB/15, SX/21, IF/3, PE/11, LN/9, QA/5, CX/6.
**Specificity:** Each row has YAML file path, description, and rule count.
**Technical accuracy:** Rule counts in the header table match the body content for most dimensions. Minor discrepancy: Active Dimensions table lists `OB: 15` but the actual OB dimension body has 11 inherited + 4 product = 15 (correct). `SX: 21` — body has 17+4 = 21 (correct). `TY: 30` — body has 26+4 = 30 (correct). Counts are self-consistent ✓, but deviate from reference (reference has TY=8, OB=6, SX=6) — this is expected given the different project base.
**Issues/gaps flagged:** Extra PE dimension not in reference — noted in dimensions table. No deductions for extra dimension.
**Structure:** Table format with columns for dimension, file path, and rule count ✓.

**Improvement items:**
- [ ] Add a "Customisation Type" column to the Active Dimensions table to distinguish inherited-base, override, extension, and new-rule rows. Reference has this distinction per dimension (+2 pts).

---

### Customisation Summary (4/5)

**Coverage:** Full summary block present — Overrides: 1 (TY-P001), Extensions: 13, Deactivations: 0, New rules: 12, Total customisations: 26.
**Technical accuracy:** 1 + 13 + 0 + 12 = 26 ✓. TY-P001 listed as the single override ✓. Extensions list names all 13 extension IDs (TY-P002 through TY-P004, OB-P001 through OB-P004, PE-P001/PE-P002, LN-P001, SX-P001 through SX-P003) ✓. New rules list names 12 IDs (SX-P004, QA-P001 through QA-P005, CX-P001 through CX-P006) ✓.
**Issues/gaps flagged:** Domain notes expect 12 extensions (not 13) and 11 new rules (not 12). One discrepancy in each count — participant has one extra extension (LN-P001) and one extra SX-P004. Minor.
**Structure:** Structured list ✓.

**Improvement items:**
- [ ] Reconcile with SKILL domain notes: expected 12 extensions + 11 new rules (total 23 customisations). Participant counts 13+12=25 customisations. Identify which customisation IDs to consolidate or reclassify (+1 pt).

---

### PL — Platform Rules (9/10)

**Coverage:** 10 rules present: PL-001 through PL-010. Covers USING DELTA, SSIS removal, Unity Catalog migration, medallion architecture assignment, SEQUENCE→IDENTITY, reseed script transformation, storage format defaults, workflow DAG pattern, zero-rows guard pattern, configuration externalisation.
**Specificity:** Each rule has ID, title, intent, and application guidance. Named objects (fact.purchase, sequences, SSIS packages) ✓.
**Technical accuracy:** PL-001 (USING DELTA), PL-002 (schema mapping: fact→silver_fact, dimension→silver_dim), PL-005 (SEQUENCE retirement) all accurate and match domain expectations ✓.
**Issues/gaps flagged:** PL-008 (zero-rows guard requiring `dbutils.notebook.exit("0 rows")`) is a critical pattern — present ✓.
**Structure:** Rule table with Intent, Application, and Example columns ✓.

**Improvement items:**
- [ ] PL-007 (Delta OPTIMIZE + ZORDER): rule body doesn't specify the ZORDER column candidates (date_key, supplier_key are typical). Add explicit column recommendations (+1 pt).

---

### NM — Naming Rules (8/10)

**Coverage:** 9 rules: NM-001 through NM-009. Covers snake_case, space-bracket renaming, reserved word avoidance, schema layer naming, table naming convention, column naming convention, key column suffix standards, null indicator naming, and temporary object naming.
**Specificity:** NM-002 (spaces in column names) is highest-priority item — present ✓. Named column examples (`[Supplier Key]` → `supplier_key`) ✓.
**Technical accuracy:** NM-006 ("Table names must not be prefixed with the schema layer name") is absent from the participant. Reference NM-006 specifically guards against naming tables `silver_fact_fact_purchase` or similar redundant patterns. Gap.
**Issues/gaps flagged:** NM-002 tagged as `priority: TOP_PRIORITY` ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] Add NM-010 (or equivalent): "Table names must not be prefixed with the name of the schema layer they reside in." Example: `fact_purchase` not `silver_fact_fact_purchase`. This is the NM-006 rule from the reference that is currently missing (+2 pts).

---

### TY — Type Mapping Rules (14/15)

**Coverage:** 30 rules (26 inherited + 4 product extensions). Covers all core T-SQL→Spark type mappings: INT→INT, BIGINT→BIGINT, DECIMAL/MONEY→DECIMAL, VARCHAR/NVARCHAR→STRING, DATETIME2→TIMESTAMP_NTZ, DATE→DATE, BIT→BOOLEAN, UNIQUEIDENTIFIER→STRING, VARBINARY→BINARY, geography CLR→3-column decomposition, etc.
**Specificity:** Each type mapping includes source type, target type, precision guidance, and CAST example where applicable.
**Technical accuracy:**
- DATETIME2→TIMESTAMP_NTZ ✓ (TY-012)
- NVARCHAR→STRING ✓ (TY-009)
- BIT→BOOLEAN ✓ (TY-015)
- MONEY→DECIMAL(18,2) ✓ (TY-005)
- geography CLR→three-column decomposition ✓ (TY-P004)
- **TY-P001** (override): SCD-2 `valid_from`/`valid_to` → DATE (not TIMESTAMP_NTZ) ✓
**Issues/gaps flagged:** TY-P001 is flagged as an override with rationale (DATE chosen to avoid time-zone ambiguity) ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] Reference TY-005-EXT-P01 explicitly excludes Photo (`VARBINARY(8000)`) from the VARBINARY→BINARY rule because `Photo` is excluded from scope. Participant TY-P002 maps VARBINARY→BINARY without scoping exclusions. Add a note that this mapping only applies to columns in scope for Purchase (+1 pt).

---

### OB — Object Rules (9/10)

**Coverage:** 15 rules (11 inherited + 4 product extensions). Covers CREATE TABLE IF NOT EXISTS, COMMENT clauses on tables and columns, TBLPROPERTIES, CLUSTER BY, CONSTRAINT pk_*, DDL headers, partition avoidance, CHECK constraints, and product-specific patterns (OB-P001 through OB-P004).
**Specificity:** OB-P003 (purchase_staging must carry purchase_staging_key INT GENERATED ALWAYS AS IDENTITY) ✓. OB-P004 (sk_resolver.py module pattern) ✓.
**Technical accuracy:** `CONSTRAINT pk_fact_purchase PRIMARY KEY(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)` named in OB-009 ✓. CLUSTER BY (date_key, supplier_key) named ✓.
**Issues/gaps flagged:** OB-003-EXT-P01 from reference (lineage_run must carry `was_successful BOOLEAN` with three-valued semantics NULL/TRUE/FALSE) is present as an extension ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] OB-006 (CLUSTER BY recommendations): participant names (date_key, supplier_key) but doesn't explain why stock_item_key is excluded. Add a justification note (stock_item_key has too many distinct values to cluster on efficiently) (+1 pt).

---

### SX — Syntax Rules (9/10)

**Coverage:** 21 rules (17 inherited + 4 product extensions SX-P001 through SX-P004). Covers MERGE syntax, ROW_NUMBER for SCD-2, CTE patterns, TOP removal, NOLOCK removal, correlated subquery rewrite, implicit JOIN removal, DELETE→TRUNCATE pattern, staging truncation fix (SX-014), and product-specific patterns.
**Specificity:** SX-003 (TOP(1) SCD-2 → ROW_NUMBER OVER PARTITION BY ... ORDER BY valid_from DESC = 1) ✓. SX-014 (SSIS DELETE staging truncation fix) ✓.
**Technical accuracy:** SX-003 uses `ORDER BY valid_from DESC` — matches the target Python sk_resolver pattern ✓. SX-P001 (MERGE 4-column composite key) ✓.
**Issues/gaps flagged:** SX-014 fixes the `DELETE FROM Integration.Order_Staging` → `DELETE FROM Integration.Purchase_Staging` bug ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] SX-P001 (MERGE key) body says "4-column composite: wwi_purchase_order_id, date_key, supplier_key, stock_item_key" — consistent with to-be. Verify this is reconciled with design.md §4 which currently uses single-column predicate (a known defect). Add a cross-reference note flagging the design.md §4 inconsistency as requiring a correction (+1 pt).

---

### IF — Interface Rules (3/5)

**Coverage:** 3 product-only rules (IF-P001, IF-P002, IF-P003). IF-P001 = dimension load ordering (supplier, stock_item, date must complete before fact load). IF-P002 = SK resolution contract (sk_resolver.py must accept staging table reference). IF-P003 = DQ gate (QA chain must pass before MERGE commit).
**Gap vs reference:** Reference IF has 5 rules including base project-level IF-001 through IF-004 (cross-product schema evolution, dimension ownership enforcement, lineage key interface contract, access control interface). Trainee's IF section has only product-specific rules, not the inherited base rules.
**Technical accuracy:** IF-P001 (dimension ordering) ✓. IF-P002 (SK resolver contract) ✓. IF-P003 (DQ gate) ✓.
**Issues/gaps flagged:** Base IF rules (cross-product schema evolution, access control) absent from the product rules file. These should appear in project-transformation-rules.md instead — but no cross-reference note present.
**Structure:** 3-rule table ✓.

**Improvement items:**
- [ ] Add a note at the top of the IF section: "Base IF rules (IF-001 through IF-004) are defined in project-transformation-rules.md. This section defines product-specific interface extensions only." This cross-reference accounts for the apparent low rule count (+2 pts).

---

### PE — Performance Rules (5/5)

**Coverage:** 11 rules (9 inherited from project + 2 product extensions PE-P001/PE-P002). Covers shuffle minimisation, broadcast join avoidance, AQE settings, caching policy, OPTIMIZE scheduling, file compaction, partition avoidance, and product-specific ZORDER guidance.
**Specificity:** PE-P001 (ZORDER on fact_purchase by date_key, supplier_key) ✓. PE-P002 (broadcast join threshold for dimension tables < 100MB) ✓.
**Technical accuracy:** ✓.
**Issues/gaps flagged:** n/a (PE is not in reference — treated as extra, full marks for extra dimension quality).
**Structure:** Rule table ✓.

**Improvement items:**
- None — full marks for extra dimension.

---

### QA + CX + LN Dimensions (9/10)

**Coverage:**
- QA: 5 rules (QA-P001 through QA-P005). Row count check (blocking), orphaned SK detection, RI rejection count, business rule assertions, DQ rejection store write. All 5 assertions match SKILL domain expectations ✓.
- CX: 6 rules (CX-P001 through CX-P006). Product context rules covering ordered_quantity derivation, key=0 observability, QuantityPerOuter stakeholder confirmation (CX-P003), DQ rejection schema enforcement, traceability table requirement, mart view contract.
- LN: 9 rules (8 inherited + LN-P001 product extension for lineage_key taskValues injection pattern via `dbutils.jobs.taskValues`).
**Specificity:** QA-P001 named as blocking (raises RuntimeError) ✓. CX-P003 `[PENDING]` stakeholder confirmation for QuantityPerOuter ✓. LN-P001 references `dbutils.jobs.taskValues.set(key="lineage_key", value=…)` API name ✓.
**Technical accuracy:** QA-P002 (orphaned SK check in dq_rejections) ✓. dq_rejections has 10 columns as per domain notes ✓. CX-P001 formula `ordered_quantity = QuantityPerOuter * OrderedOuters` ✓.
**Issues/gaps flagged:** CX-P003 `[PENDING]` marker ✓. LN-P001 references taskValues API ✓.
**Structure:** Three separate rule tables ✓.

**Improvement items:**
- [ ] QA-P005 (DQ rejection store): explicitly states "10 columns" not "nine columns". This corrects the NFR-007 defect. Ensure this count (10) is consistent with the requirements document. If requirements says "nine", flag the discrepancy here (+1 pt).

---

## Extra Sections / Dimensions (not in reference)

- PE dimension (11 rules) — extra, not in reference. Full marks.
- LN dimension (9 rules vs reference's 1 rule) — substantially expanded. No deduction.
- QA dimension (5 rules vs reference's 1 rule) — substantially expanded. No deduction.

## Approach Notes

- Reference file is for GlobalPurchase_Project (39 rules, 9 dimensions). Participant is for Inventory_Stock_Project (119 rules, 10 dimensions). The SKILL's domain notes describe the Inventory_Stock_Project expected structure (90 project + 26 product customisations = 116 effective). Participant aligns with the SKILL's domain notes. Larger rule set is not penalised.
- All reference dimensions are present in participant ✓.
- Reference's QA dimension had 1 rule with 5 sub-assertions; participant has 5 separate rules — equivalent coverage, different structure.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. IF dimension — Coverage — add a cross-reference note explaining IF-001 through IF-004 are in project-transformation-rules.md, and IF section here is product-only extensions → +2 pts
2. NM dimension — Coverage — add NM-010 preventing schema-layer-prefixed table names → +2 pts
3. Active Dimensions table — Structure — add "Customisation Type" column to distinguish inherited-base from override/extension/new-rule rows → +2 pts

---

## Next Step

You can proceed to the next task.
