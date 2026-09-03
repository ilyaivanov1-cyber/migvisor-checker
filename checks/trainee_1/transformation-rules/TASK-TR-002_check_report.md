---
task_id: TASK-TR-002
project: GlobalSales_Project
participant_file: project-transformation-rules.md
reference_file: project-transformation-rules final.md
checked_at: 2026-09-02T15:00:00Z
sections_evaluated: 7
total_score: 74/100
grade: Acceptable
identical_to_reference: false
---

# Task Check Report — project transformation rules
_GlobalSales_Project | 2026-09-02_

**File resolution log:**
- Participant file: `project-transformation-rules.md` — auto-resolved (priority 1 match: `project-transformation-rules.md`)
- Reference file: `project-transformation-rules final.md` — auto-resolved (priority 1 match: `project-transformation-rules final.md`)
- Project: `GlobalSales_Project` — derived from H1 heading `# Project Transformation Rules: GlobalSales_Project`
- Note: cross-project comparison — participant covers GlobalSales_Project; reference covers GlobalPurchase_Project. Both are project-level rule sets for the same source platform (SQL Server 2014 → Databricks Delta Lake). Section matching by prefix abbreviation.
- Sections in reference: 7 (1 metadata + 6 dimensions) | Sections in participant: 9 (1 metadata + 8 dimensions; matched: 6 dimensions + 1 metadata, extra: PE + LN, unmatched reference section: IF)
- Point weights: auto-calculated — N=7, floor(100/7)=14 base; +1 to NM and TY (both 6 reference rules, highest rule count)
- Auto-deducts applied: −5 pts (IF dimension entirely absent)

---

## Score Summary

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| Active Dimensions | §Dimension Table | 14 | 11 | ⚠ |
| Platform (PL) | §PL — Platform | 14 | 14 | ✓ |
| Naming (NM) | §NM — Naming | 15 | 14 | ✓ |
| Types (TY) | §TY — Types | 15 | 15 | ✓ |
| Objects (OB) | §OB — Objects | 14 | 14 | ✓ |
| Syntax (SX) | §SX — Syntax | 14 | 11 | ⚠ |
| Interface (IF) | *(no match)* | 14 | 0 | ✗ |
| *Auto-deduct: IF absent* | | | −5 | |
| **Total** | | **100** | **74** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Active Dimensions (11/14)
_Matched to participant §Dimension Table_

**Dimension coverage (4/5):** Five of six reference dimensions present — PL, NM, TY, OB, SX all appear in the Dimension Table. **Interface (IF) is absent**: no IF dimension row in the participant's Dimension Table, no IF section in the Rule Index.

**Rule count accuracy (5/5):** Count differences between participant and reference reflect the different project scope (GlobalSales has 92 rules; GlobalPurchase has 30). Internally, participant counts are self-consistent: 10+9+30+11+17+8+7 = 92 ✓. Counts per dimension match their respective rule sections. Full marks for internal consistency.

**File references (2/3):** Five of six reference YAML file links present (PL-platform.yaml, NM-naming.yaml, TY-types.yaml, OB-objects.yaml, SX-syntax.yaml ✓). **Missing: IF-interface.yaml** (no IF row in table). Extra files PE-performance.yaml and LN-lineage.yaml are noted as supplementary.

**Application order + structure (0/1):** The reference states application order `PL → NM → TY → OB → SX → IF`. The participant's Dimension Table contains no application order statement. Total rule count is stated (92) ✓.

**Rule inventory:** Reference dimensions: 6 | Participant dimensions: 7 (5 matched + 2 extra — PE, LN) | Missing: IF

**Improvement items:**
- [ ] Add Interface (IF) row to the Dimension Table: `| Interface | IF | IF-interface.yaml | 4 |`
- [ ] Add application order: `Application order: PL → NM → TY → OB → SX → IF`

---

### Platform (PL) (14/14)
_Matched to participant §PL — Platform (10 rules)_

**Rule coverage (6/6):** All 4 reference rules are covered across the participant's 10 PL rules:
- Ref PL-001 (USING DELTA) → participant PL-003 ("Convert all tables to Delta Lake format, enabling ACID transactions") ✓
- Ref PL-002 (SSIS → Workflows, Staging→Dim/Fact→Mart) → participant PL-005 ("ETL pattern → Delta MERGE + Workflows") + PL-010 (SQL Agent/SSIS → Databricks Workflows) ✓
- Ref PL-003 (schema layers: stg/dim/fact/mart) → participant PL-009 (maps integration→stg, dimension→dim, fact→fact, analytics→mart explicitly) ✓
- Ref PL-004 (SEQUENCE → IDENTITY) → participant PL-004 ✓

**Intent accuracy (4/4):** All four reference intents accurately represented. PL-009 uses the corrected schema names (stg/dim/fact/mart), consistent with the changelog entry. Full marks.

**Technical accuracy (3/3):** Correct platform targets throughout. Unity Catalog catalog name `globalsales` consistent. No wrong technology names. Full marks.

**Structure (1/1):** Table with Rule ID / Intent, IDs PL-001 through PL-010, count 10 matches heading ✓.

**Rule inventory:** Reference rules: 4 | Participant rules: 10 | Missing: none

---

### Naming (NM) (14/15)
_Matched to participant §NM — Naming (9 rules)_

**Rule coverage (5/6):** Five of six reference rules covered:
- Ref NM-001 (snake_case) → NM-001 ✓
- Ref NM-002 (spaces → underscores) → NM-002 ✓ (with specific examples: `payment method`, `stock item`, etc.)
- Ref NM-003 (v_ prefix for views) → NM-004 ✓
- Ref NM-004 (_staging suffix) → NM-005 ✓
- Ref NM-005 (schema → Unity Catalog layer mapping) → NM-003 ✓ (maps dimension→globalsales.dim, fact→globalsales.fact, etc.)
- **Ref NM-006 (no layer prefix in table names) → NOT covered.** Reference NM-006 states table names must not be prefixed with the schema layer name (e.g., `globalpurchase.fact.purchase` not `globalpurchase.fact.fact_purchase`). Participant NM-006 is about stored procedure/function naming — a different topic. No other participant rule states the no-layer-prefix constraint.

**Intent accuracy (5/5):** All 5 covered rules have accurate, product-specific intents. NM-003 in participant is more detailed than the reference, explicitly mapping all 6 schemas including `application → globalsales.app` and `sequences → retired`. Full marks for covered rules.

**Technical accuracy (3/3):** Correct Unity Catalog targets ✓. Full marks.

**Structure (2/2):** Table format ✓, NM-001 through NM-009, count 9 matches heading ✓.

**Rule inventory:** Reference rules: 6 | Participant rules: 9 | Missing IDs: ref NM-006 (no-layer-prefix constraint)

**Improvement items:**
- [ ] Add rule capturing: "Table names must not be prefixed with the schema layer name — the three-part Unity Catalog name conveys the layer (e.g., `globalsales.fact.sale`, not `globalsales.fact.fact_sale`)"

---

### Types (TY) (15/15)
_Matched to participant §TY — Types (30 rules)_

**Rule coverage (6/6):** All 6 reference type rules are covered across the participant's 30 granular rules:
- Ref TY-001 (INT/SMALLINT/TINYINT→INT; BIGINT→BIGINT) → covered by TY-001, TY-002, TY-003, TY-004 ✓
- Ref TY-002 (DECIMAL/NUMERIC/FLOAT/REAL → DECIMAL or DOUBLE) → TY-005, TY-008, TY-009 ✓
- Ref TY-003 (VARCHAR/NVARCHAR/CHAR/NCHAR → STRING) → TY-010, TY-011 ✓
- Ref TY-004 (DATE/DATETIME/DATETIME2/SMALLDATETIME/TIME → DATE/TIMESTAMP/STRING) → TY-012 through TY-017 ✓
- Ref TY-005 (BIT→BOOLEAN; UNIQUEIDENTIFIER→STRING; VARBINARY→BINARY) → TY-020, TY-022, TY-018 ✓
- Ref TY-006 (IDENTITY → GENERATED ALWAYS AS IDENTITY) → TY-023 ✓

**Intent accuracy (5/5):** All reference intents accurately represented. Participant is more granular — e.g., splits TINYINT→BYTE and SMALLINT→SMALLINT rather than mapping both to INT as the reference does. The participant's mappings are technically more precise for Databricks (Spark has a native BYTE type), and per approach policy, a more accurate alternative mapping is not penalised. Full marks.

**Technical accuracy (3/3):** All Spark SQL type targets correct. The changelog corrections (Snowflake types removed in pass 1) are fully applied — all rules reference Databricks/Spark SQL equivalents, no Snowflake syntax present. Full marks.

**Structure (2/2):** Table format ✓, TY-001 through TY-030, count 30 matches heading ✓.

**Rule inventory:** Reference rules: 6 | Participant rules: 30 | Missing: none (all reference types covered at higher granularity)

---

### Objects (OB) (14/14)
_Matched to participant §OB — Objects (11 rules)_

**Rule coverage (6/6):** All 5 reference rules covered:
- Ref OB-001 (all tables → Delta) → OB-001 (8 dim tables), OB-002 (6 fact tables), OB-003 (15 staging tables), OB-004 (16 analytics tables) — split into per-layer rules ✓
- Ref OB-002 (procedures → Python) → OB-007 ✓
- Ref OB-003 (SEQUENCE → IDENTITY) → OB-008 ✓
- Ref OB-004 (application schema → excluded/bootstrap) → OB-009 (retire app.* procedures) + OB-010 (migrate config objects to Secrets/meta) ✓
- Ref OB-005 (views → v_ prefix) → OB-005 ✓ (v_ prefix naming delegated to NM-004)

**Intent accuracy (4/4):** All covered intents accurate with specific object counts per rule (e.g., "8 dimension tables", "15 staging tables"). Full marks.

**Technical accuracy (3/3):** All targets use `globalsales.*` three-part catalog names correctly ✓. Full marks.

**Structure (1/1):** Table format ✓, OB-001 through OB-011, count 11 ✓.

**Rule inventory:** Reference rules: 5 | Participant rules: 11 | Missing: none

---

### Syntax (SX) (11/14)
_Matched to participant §SX — Syntax (17 rules)_

**Rule coverage (4/6):** Three of five reference rules clearly covered; two are absent:
- Ref SX-001 (BEGIN TRAN/COMMIT/ROLLBACK → Delta atomicity) → SX-003 ✓ and SX-002 (NOCOUNT/XACT_ABORT removal) ✓
- Ref SX-002 (staging table + migratestaged* → Delta MERGE) → SX-001 (T-SQL MERGE → Delta MERGE INTO syntax) ✓ (pattern covered in conjunction with PL-005)
- **Ref SX-003 (SCD Type-2: UPDATE ValidTo + INSERT → Delta MERGE with is_current BOOLEAN) → NOT found.** No participant rule explicitly addresses the SCD Type-2 dimension history pattern. SX-001 covers MERGE syntax conversion generally, but the SCD2-specific pattern with `is_current` flag is absent.
- **Ref SX-004 (fact DELETE+INSERT → Delta MERGE on business key) → NOT found.** No participant rule addresses the fact table incremental refresh pattern of DELETE+INSERT being converted to a MERGE keyed on the business key.
- Ref SX-005 (T-SQL functions/operators → Spark SQL) → covered extensively by SX-005 through SX-017 ✓

**Intent accuracy (3/4):** Three reference rules have accurate intents in participant. Two reference rules (SX-003, SX-004) have no corresponding rule — scored 0 for those.

**Technical accuracy (3/3):** All rules correctly target Spark SQL / Databricks equivalents. No T-SQL remnants in targets. Full marks.

**Structure (1/1):** Table format ✓, SX-001 through SX-017, count 17 ✓.

**Rule inventory:** Reference rules: 5 | Participant rules: 17 | Missing IDs: ref SX-003 (SCD2 pattern), ref SX-004 (fact DELETE+INSERT pattern)

**Improvement items:**
- [ ] Add SCD Type-2 rule: "Convert the SQL Server SCD Type-2 pattern of UPDATE ValidTo + INSERT into a single atomic Delta MERGE INTO statement with active/history logic and an `is_current BOOLEAN` flag"
- [ ] Add fact refresh rule: "Convert the SQL Server fact table refresh pattern of DELETE + INSERT into a single idempotent Delta MERGE INTO statement keyed on the business key"

---

### Interface (IF) (0/14)
_No match found in participant_

The participant has no `### IF` or Interface section anywhere in the Rule Index. The reference Interface dimension contains 4 rules covering critical ETL interface patterns:
- **IF-001**: SSIS daily ETL → Databricks Workflow (Staging→Dim/Fact→Mart task dependency order)
- **IF-002**: JDBC incremental reads filtered by `LastEditedWhen`; watermark committed to `etl_cutoff` after all downstream loads
- **IF-003**: SQL Server credentials → Databricks Secrets (JDBC URL, username, password)
- **IF-004**: Staging strategy — dimension data as transient in-memory temp views; fact data written to `stg.*` via truncate+overwrite

None of these are covered elsewhere in the participant document. Score: 0/14.

Auto-deduct: −5 pts (entire reference dimension absent from participant).

**Improvement items:**
- [ ] Add Interface (IF) dimension with at least the 4 reference rules: SSIS→Workflows orchestration (IF-001), JDBC incremental watermark pattern (IF-002), Databricks Secrets for credentials (IF-003), staging strategy for dim vs. fact data (IF-004)

---

## Extra Sections (not in reference)

| Participant section | Notes |
|---|---|
| §PE — Performance (8 rules) | Project-level performance rules covering columnstore retirement, Delta partitioning/Z-ORDER/liquid clustering, OPTIMIZE, broadcast joins, auto-optimization. Substantive and well-structured — plausible project extension. |
| §LN — Lineage (7 rules) | Project-level lineage rules covering lineage table migration, SEQUENCE→IDENTITY for lineage keys, open/close_lineage_record utilities, Unity Catalog system lineage. Substantive extension. |

---

## Approach Notes

- Cross-project comparison: participant is GlobalSales_Project (92 rules, 7 dimensions); reference is GlobalPurchase_Project (30 rules, 6 dimensions). Rule counts differ significantly because GlobalSales has a richer source schema — not an error. Count accuracy criterion evaluated against internal self-consistency, not against reference totals.
- Types (TY): participant maps TINYINT→BYTE and SMALLINT→SMALLINT rather than the reference's TINYINT/SMALLINT→INT. This is a more technically precise Spark SQL mapping and is accepted per approach policy.
- Objects (OB): participant splits reference OB-001 (all tables → Delta) into 4 per-layer rules (OB-001 dim, OB-002 fact, OB-003 staging, OB-004 analytics). Valid decomposition — no deduction.
- PE and LN extra dimensions: both contain substantive project-level rules. At project level these are unexpected (the reference doesn't define them), but the content is valid and adds value. No point deduction; flagged as extra.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. **Interface (IF) — missing dimension — up to +19 pts recoverable**: Add the IF dimension with 4 rules covering SSIS→Workflows (IF-001), JDBC incremental watermark (IF-002), Databricks Secrets for credentials (IF-003), and dimension/fact staging strategy (IF-004). This scores the 0/14 section and removes the −5 auto-deduct.
2. **Syntax (SX) — Rule coverage — +3 pts recoverable**: Add the SCD Type-2 MERGE rule (ref SX-003) and the fact DELETE+INSERT→MERGE rule (ref SX-004). Both are important ETL patterns absent from the participant.
3. **Naming (NM) — Rule coverage — +1 pt recoverable**: Add the no-layer-prefix constraint (ref NM-006): table names must not repeat the schema layer in the three-part catalog name.

---

## Next Step

Score 74 < 75: Address the priority improvements above and re-run the checker before moving on. The Interface (IF) section is the highest-priority gap — adding those 4 rules recovers up to 19 points and would push the score to approximately 93.
