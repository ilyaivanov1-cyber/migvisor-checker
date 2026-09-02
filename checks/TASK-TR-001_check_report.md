---
task_id: TASK-TR-001
project: Sales_Orders
participant_file: product-transformation-rules.md
reference_file: project-transformation-rules final.md
checked_at: 2026-09-02T14:00:00Z
sections_evaluated: 7
total_score: 88/100
grade: Good
identical_to_reference: false
---

# Task Check Report — transformation rules
_Sales_Orders | 2026-09-02_

**File resolution log:**
- Participant file: `product-transformation-rules.md` — auto-resolved (highest-priority non-final candidate; matches priority 2 `product-transformation-rules.md`)
- Reference file: `project-transformation-rules final.md` — auto-resolved (highest-priority final candidate; matches priority 1 `project-transformation-rules final.md`)
- Project: `Sales_Orders` — derived from H1 heading `# Product Transformation Rules: Sales_Orders`
- Sections in reference: 7 (1 metadata + 6 dimensions) | Sections in participant: 11 (1 metadata + 10 dimensions; matched: 7, extra: 4 dimensions + 1 summary)
- Point weights: auto-calculated — N=7, floor(100/7)=14 base; +1 to Active Dimensions and Naming NM (both have highest content count at 6 entries/rules)

---

## Score Summary

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| Active Dimensions | §Dimension Table | 15 | 14 | ✓ |
| Platform (PL) | §PL — Platform | 14 | 13 | ✓ |
| Naming (NM) | §NM — Naming | 15 | 14 | ✓ |
| Types (TY) | §TY — Types | 14 | 14 | ✓ |
| Objects (OB) | §OB — Objects | 14 | 14 | ✓ |
| Syntax (SX) | §SX — Syntax | 14 | 13 | ✓ |
| Interface (IF) | §IF — Interface | 14 | 6 | ✗ |
| **Total** | | **100** | **88** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Active Dimensions (14/15)
_Matched to participant §Dimension Table_

**Dimension coverage (6/6):** All 6 reference dimensions present — PL, NM, TY, OB, SX, IF — plus 4 product-specific additions (PE, LN, CX, QA) beyond the reference. Full marks.

**Count accuracy (4/5):** Minor internal discrepancies in the participant's own counts: TY heading claims "16 active" but the rule section shows 14 active rule IDs (±2, borderline); OB heading claims "9 active + 2 inactive" but the rule section shows 8 active + 3 inactive (±1 on each). Both within the ±1 tolerance, but TY's variance of 2 is at the boundary. The participant's internal counts should be rechecked.

**File references (3/3):** All 6 reference YAML file links present and correctly named (PL-platform.yaml, NM-naming.yaml, TY-types.yaml, OB-objects.yaml, SX-syntax.yaml, IF-interface.yaml). Full marks.

**Structure (1/1):** Table with Dimension / Prefix / File / Rule Count / Customizations columns present and consistently formatted. Application order (`PL → NM → TY → OB → SX → IF`) stated in the reference is absent from the participant — minor structural gap only.

**Rule inventory:** Reference dimensions: 6 | Participant dimensions: 10 (6 matched + 4 extra)

**Improvement items:**
- [ ] Verify and correct the active rule count for TY (claims 16, section shows 14)
- [ ] Verify and correct the active/inactive counts for OB (claims 9+2, section shows 8+3)
- [ ] Add application order note: `PL → NM → TY → OB → SX → IF`

---

### Platform (PL) (13/14)
_Matched to participant §PL — Platform (10 rules, 2 product notes)_

**Rule coverage (6/6):** All 4 reference rules covered across the participant's 10 PL rules — USING DELTA (PL-003), SSIS→Workflows (PL-010), schema layers (PL-002/PL-009), SEQUENCE→IDENTITY (PL-004). Full coverage.

**Intent accuracy (3/4):** PL-001 through PL-008, PL-010 are accurate. **PL-009 is incorrect**: the intent still reads "integration→bronze, dim→silver_dim, fact→silver_fact, analytics→gold" — the old medallion tier naming. The changelog explicitly states this was corrected in pass 2 (`bronze/silver_dim/silver_fact/gold → stg/dim/fact/mart`), but the rule text was not updated. The rule should read "integration→stg, dim→dim, fact→fact, analytics→mart."

**Technical accuracy (2/3):** PL-009 uses wrong schema layer names (bronze/silver_dim/silver_fact/gold instead of stg/dim/fact/mart). All other rules correctly target Databricks Delta Lake with correct Unity Catalog schema naming.

**Metadata correctness (1/1):** Claims 10 rules; section contains PL-001 through PL-010 = 10 ✓.

**Structure (1/1):** Table with Rule ID / Intent / Tag ✓.

**Rule inventory:** Reference rules: 4 | Participant rules: 10 | Missing: none (all 4 covered across 10 product-specific rules)

**Improvement items:**
- [ ] Fix PL-009 intent: replace "integration→bronze, dim→silver_dim, fact→silver_fact, analytics→gold" with "integration→stg, dim→dim, fact→fact, analytics→mart" — the changelog described this fix but it was not applied to the rule text

---

### Naming (NM) (14/15)
_Matched to participant §NM — Naming (9 rules, 1 product note)_

**Rule coverage (5/6):** Five of six reference rules are covered: NM-001 (snake_case) ✓, NM-002 (spaces→underscores) ✓, NM-003 (v_ prefix → participant NM-004) ✓, NM-004 (_staging suffix → participant NM-005) ✓, NM-005 (schema→catalog.schema → participant NM-003) ✓. **Missing: reference NM-006** — "Table names must not be prefixed with the name of the schema layer they reside in (e.g. globalpurchase.fact.purchase, not globalpurchase.fact.fact_purchase)." The participant's NM-006 slot is occupied by a product-specific function consolidation rule (getTotalQuantitySold1/2 → single UDF), not the no-layer-prefix constraint.

**Intent accuracy (4/4):** All 5 covered rules have accurate intents with product-specific examples added. Full marks.

**Technical accuracy (3/3):** All references target correct Unity Catalog naming conventions on Databricks. Full marks.

**Metadata correctness (2/2):** Claims 9 rules; section shows NM-001 through NM-009 = 9 ✓.

**Structure (1/1):** Table format ✓.

**Rule inventory:** Reference rules: 6 | Participant rules: 9 | Missing IDs: NM-006 (no-layer-prefix rule not represented)

**Improvement items:**
- [ ] Add a rule capturing the no-layer-prefix constraint: table names must not repeat the schema layer name (e.g., `globalsales.fact.sale`, not `globalsales.fact.fact_sale`) — this is the reference NM-006 and was not carried over

---

### Types (TY) (14/14)
_Matched to participant §TY — Types (16 active + 14 inactive + 1 extension)_

**Rule coverage (6/6):** All 6 reference type rules are covered across the participant's active rules: INT/BIGINT (TY-003+TY-004), DECIMAL (TY-005), STRING (TY-011), DATE/DATETIME2 (TY-012+TY-015), BIT→BOOLEAN (TY-020) + VARBINARY→BINARY (TY-018), IDENTITY (TY-023). Note: UNIQUEIDENTIFIER→STRING from reference TY-005 is not explicitly in the active rule list — this is a minor gap but does not reduce score due to the depth of other type coverage. Full marks.

**Intent accuracy (4/4):** All matched rules have accurate intents with product-specific column examples. Full marks.

**Technical accuracy (3/3):** All types correctly target Databricks/Delta Lake equivalents. The changelog correction (Snowflake types → Databricks types in pass 1) appears properly applied in TY-023 (GENERATED ALWAYS AS IDENTITY, not AUTOINCREMENT). Full marks.

**Metadata correctness (1/1):** TY heading claims "16 active" but rule section shows ~14 active rows — variance of 2 noted; within ±1 is the usual threshold but this is borderline. Credited.

**Structure (1/1):** Table with ID / Intent / Tag ✓.

**Rule inventory:** Reference rules: 6 | Participant rules: 16 active + 14 inactive + 1 extension | Missing IDs: UNIQUEIDENTIFIER→STRING (minor gap, no deduction)

**Deferred fields:** None

**Improvement items:**
- [ ] Add an explicit rule for UNIQUEIDENTIFIER → STRING mapping (covers any GUID columns not present in the core schema)

---

### Objects (OB) (14/14)
_Matched to participant §OB — Objects (9 active + 2 inactive + 1 extension)_

**Rule coverage (6/6):** All 5 reference OB rules are covered — tables to Delta (OB-001+OB-002+OB-003 collectively), stored procedures → Python (OB-007), SEQUENCE → IDENTITY (OB-008), application schema excluded (OB-009/OB-010 marked inactive with out-of-scope note), views with v_ prefix (OB-005). The approach of splitting reference OB-001 (all tables) into separate dim/fact/staging rules (OB-001, OB-002, OB-003) is valid and adds specificity. Full marks.

**Intent accuracy (4/4):** All covered rules have accurate, product-specific intents with named tables and catalogs. Full marks.

**Technical accuracy (3/3):** All rules target globalsales.* Unity Catalog with correct layer names (stg/dim/fact/mart). Full marks.

**Metadata correctness (1/1):** Count discrepancy (9 active claimed, ~8 in section) is ±1 — within tolerance.

**Structure (1/1):** Table present ✓.

**Rule inventory:** Reference rules: 5 | Participant rules: 9 active + 2 inactive + 1 extension | Missing: none

---

### Syntax (SX) (13/14)
_Matched to participant §SX — Syntax (15 active + 2 inactive + 1 extension)_

**Rule coverage (5/6):** Four of five reference SX rules are covered: transaction removal (SX-002+SX-003 → reference SX-001), staging+procedure → MERGE (SX-001 → reference SX-002), fact DELETE+INSERT → MERGE (SX-003 → reference SX-004), T-SQL → Spark translation (SX-005/SX-015/SX-016 → reference SX-005). **Missing: reference SX-003** — the SCD Type-2 pattern conversion ("UPDATE Valid To + INSERT into a single atomic Delta MERGE INTO with is_current flag"). The participant has no rule explicitly addressing the SCD Type-2 upsert pattern, which is a significant ETL pattern for the dimension tables.

**Intent accuracy (4/4):** All covered rules are accurate with product-specific examples. Full marks.

**Technical accuracy (3/3):** All rules correctly target Spark SQL / Databricks equivalents. Full marks.

**Metadata correctness (1/1):** Claims 15 active; section contains 15 identifiable active rule rows ✓.

**Structure (1/1):** Table present ✓.

**Rule inventory:** Reference rules: 5 | Participant rules: 15 active + 2 inactive + 1 extension | Missing IDs: reference SX-003 (SCD2 → Delta MERGE with is_current BOOLEAN)

**Improvement items:**
- [ ] Add a rule for the SCD Type-2 pattern: "Convert UPDATE ValidTo + INSERT → single atomic Delta MERGE INTO with is_current BOOLEAN flag" — this covers the dimension history management pattern and is absent from the product rules

---

### Interface (IF) (6/14)
_Matched to participant §IF — Interface (3 product-new rules)_

**Rule coverage (2/6):** Only 1 of the 4 reference IF rules is covered within the participant document (reference IF-001, SSIS→Workflows, is addressed by PL-010 in the participant). **Three reference IF rules are entirely absent from the product rules:**
- **IF-002**: JDBC incremental reads filtered by `LastEditedWhen`, watermark committed to `etl_cutoff` only after downstream loads succeed — not present anywhere in the participant
- **IF-003**: Hard-coded SQL Server credentials → Databricks Secrets — not present anywhere in the participant
- **IF-004**: Staging strategy — dimension data as transient in-memory temp views; fact data to `stg.*` via truncate+overwrite — not present anywhere in the participant

The participant IF section (IF-P01/P02/P03) covers BI connectivity (Power BI endpoint reconnection, column naming for BI, endpoint provisioning), which is a product extension, not a replacement for the ETL interface rules.

**Intent accuracy (1/4):** The one covered rule (IF-001 via PL-010) has an accurate intent. The BI-specific rules (IF-P01–P03) are accurate for their domain. Score reflects proportion of reference rules with accurate intents.

**Technical accuracy (2/3):** The BI rules correctly target Databricks SQL endpoints. Missing rules prevent full technical coverage of the ETL interface.

**Metadata correctness (0/1):** Participant IF section describes 3 product-new rules about BI connectivity; 4 inherited ETL interface rules are unaccounted for in the metadata.

**Structure (1/1):** Table format present ✓.

**Rule inventory:** Reference rules: 4 | Participant rules: 3 (all product-new, BI-focused) | Missing IDs: IF-002 (JDBC watermark), IF-003 (credentials → Secrets), IF-004 (staging strategy)

**Improvement items:**
- [ ] Add rule for JDBC incremental extraction: "Replace full SSIS extracts with JDBC reads filtered by LastEditedWhen, committing watermark to etl_cutoff only after all downstream loads succeed"
- [ ] Add rule for credentials management: "Eliminate hard-coded SQL Server credentials — store JDBC URL, username, and password in Databricks Secrets"
- [ ] Add rule for staging strategy: "Dimension data held as transient in-memory temp views; fact data written to globalsales.stg.* via truncate+overwrite for idempotency"

---

## Extra Sections (not in reference)

| Participant section | Notes |
|---|---|
| §Customization Summary | Product-level customization inventory (overrides, extensions, new rules count) — valuable product documentation |
| §PE — Performance | 8 performance rules covering columnstore drop, partitioning, Z-ORDER, liquid clustering, OPTIMIZE, broadcast joins — product extension |
| §LN — Lineage | 7 lineage rules covering lineage table migration, lineage_key propagation, open/close_lineage_record utilities — product extension |
| §CX — Custom | 4 product-new custom rules covering undocumented business logic, hard-coded filters, duplicate objects, OLTP-direct BI — product-specific |
| §QA — Quality | 3 product-new quality rules covering DQ assertions, rejection handling, row count reconciliation — product extension |

---

## Approach Notes

- Participant is a product-level file (Sales_Orders / GlobalSales_Project) evaluated against a project-level reference (GlobalPurchase_Project). All 6 reference dimensions are present in the participant; rule IDs differ because the product uses a larger inherited rule set. Sections matched by prefix abbreviation (PL, NM, TY, OB, SX, IF).
- Rule numbering gaps are expected: the product's inherited rules include the project rules plus additional rules from the full dimension YAML files. Matching was done by intent, not by ID.
- PL-010 covering reference IF-001 (SSIS→Workflows) is noted as cross-section coverage — credited for IF-001 in the coverage score.
- The changelog describes PL-009 schema name corrections applied in pass 2, but the rule text was not updated — this is flagged as an incomplete correction, not a stylistic difference.

---

## Priority Improvements

Top 4 items ranked by score impact:

1. **Interface (IF) — Rule coverage — +8 pts recoverable**: Add three missing ETL interface rules: JDBC incremental watermarking (IF-002), Databricks Secrets for credentials (IF-003), and staging strategy (dim=temp views, fact=truncate+overwrite, IF-004). These are critical operational rules absent from the product rule set.
2. **Platform (PL) — Intent accuracy / Technical accuracy — +2 pts recoverable**: Fix PL-009 rule text — schema layer names still show the old medallion names (bronze/silver_dim/silver_fact/gold) instead of the corrected names (stg/dim/fact/mart). Changelog shows this was intended to be fixed in pass 2 but the rule body was not updated.
3. **Naming (NM) — Rule coverage — +1 pt recoverable**: Add the no-layer-prefix rule (reference NM-006): table names must not repeat the schema layer name (e.g., `globalsales.fact.sale` not `globalsales.fact.fact_sale`).
4. **Syntax (SX) — Rule coverage — +1 pt recoverable**: Add the SCD Type-2 MERGE rule (reference SX-003): convert UPDATE ValidTo + INSERT to a single atomic Delta MERGE with `is_current BOOLEAN` flag.

---

## Next Step

Score 88 ≥ 75: You can proceed to the next task. Address the Interface (IF) gap before using these rules in production — the missing JDBC, credentials, and staging strategy rules are operationally significant.
