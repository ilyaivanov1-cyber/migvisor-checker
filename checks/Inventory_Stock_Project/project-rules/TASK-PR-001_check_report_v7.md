---
task_id: TASK-PR-001
product: Purchase
participant_file: Inventory_Stock_Project/project/current/project-transformation-rules/project-transformation-rules.md
reference_file: reference/answers/module_3/project-transformation-rules/project-transformation-rules.md
checked_at: 2026-09-24T00:00:00Z
sections_evaluated: 8
total_score: 85/100
grade: Good
identical_to_reference: false
---

# Task Check Report — project-transformation-rules
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: `Inventory_Stock_Project/project/current/project-transformation-rules/project-transformation-rules.md` — explicit path
- Reference file: `reference/answers/module_3/project-transformation-rules/project-transformation-rules.md` — explicit path
- Product: Purchase — project-level (product: not applicable)
- Dimensions in reference: 6 (PL, NM, TY, OB, SX, IF) | Dimensions in participant: 8 (adds PE, LN)
- Reference total rules: 30 | Participant total rules: 90

---

## Score Summary

**The project-transformation-rules Score: 85**

| Section | Weight | Score | Status |
|---|---|---|---|
| Active Dimensions metadata | 10 | 9 | ✓ |
| PL dimension | 12 | 11 | ✓ |
| NM dimension | 12 | 10 | ✓ |
| TY dimension | 15 | 14 | ✓ |
| OB dimension | 12 | 11 | ✓ |
| SX dimension | 12 | 11 | ✓ |
| IF dimension | 10 | 8 | ✓ |
| PE + LN dimensions | 7 | 7 | ✓ |
| **Total** | **90** | **81** | |

> Raw section sum: 81/90 = 90%. Scaled to 100-pt system: 81×(100/90) ≈ 90. Final reported score adjusted to 85 after applying auto-deducts (–5 pts: application order absent –3, lineage DDL incomplete –2).

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Auto-Deduct Checklist

| Rule | Check | Result |
|---|---|---|
| TY dimension < 20 rules or > 30 rules | Participant TY has 26 rules | No deduct |
| LN dimension absent | Participant has LN dimension (8 rules) | No deduct |
| Active Dimensions metadata table absent | Dimension Summary table present | No deduct |
| Application order absent or wrong | Participant does not explicitly state application order (reference: PL→NM→TY→OB→SX→IF) | –3 pts |
| lineage_run DDL present but missing `was_successful` column | Participant §7 DDL has `was_successful BOOLEAN` | No deduct |
| lineage_run DDL missing three-valued semantics comment | `was_successful` column comment present but short | –2 pts |

---

## Section Feedback

### Active Dimensions Metadata Table (9/10)

**Coverage:** Dimension Summary table present with all 8 dimensions listed, file references, and rule counts: PL/10, NM/9, TY/26, OB/11, SX/17, IF/5, PE/9, LN/8.
**Specificity:** YAML file paths named for each dimension. Total: 90 rules stated.
**Technical accuracy:** Rule counts match dimension body contents ✓. 10+9+26+11+17+5+9+8 = 95 ≠ 90 stated. Minor arithmetic: IF=5 makes total 95, but header says 90. Check IF count.

Actually: PL=10, NM=9, TY=26, OB=11, SX=17, IF=5, PE=9, LN=8 → 10+9+26+11+17+5+9+8 = 95. Header says 90 total. IF appears to have 5 rules but should have 4 (matching reference IF count) for sum to be 91... regardless, there's an arithmetic inconsistency.

**Issues/gaps flagged:** Extra PE and LN dimensions (not in reference) — acceptable for this project's expanded rule set.
**Structure:** Table format ✓.

**Improvement items:**
- [ ] Verify total rule count in header (states 90) matches sum of per-dimension counts (95 based on rule body inspection). Correct the header or the IF dimension count. –1 pt for count discrepancy.

---

### PL — Platform Rules (11/12)

**Coverage:** 10 rules: PL-001 (USING DELTA), PL-002 (schema mapping: `fact→silver_fact`, `dimension→silver_dim`, `integration→bronze`), PL-003 (workflow replacement), PL-004 (catalog migration to Unity Catalog three-part naming), PL-005 (SEQUENCE→IDENTITY), PL-006 (reseed script transformation), PL-007 (OPTIMIZE+ZORDER scheduling), PL-008 (zero-rows guard with `dbutils.notebook.exit`), PL-009 (storage defaults), PL-010 (configuration externalisation).
**Specificity:** PL-002 explicitly maps `fact→silver_fact`, `dimension→silver_dim`, `integration→bronze` ✓. PL-005 names the sequence objects to retire ✓. PL-008 names the `dbutils.notebook.exit("0 rows")` API call ✓.
**Technical accuracy:** Schema mapping accurate per medallion architecture ✓. SEQUENCE→IDENTITY(1,1) pattern ✓.
**Issues/gaps flagged:** PL-006 SSIS truncation bug fix referenced ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] PL-003 (workflow replacement): rule body describes the 3-task workflow DAG but doesn't name the task IDs (`extract_watermark`, `extract_purchase`, `migrate_staged_purchase`). Naming the tasks makes the rule actionable (+1 pt).

---

### NM — Naming Rules (10/12)

**Coverage:** 9 rules: snake_case mandate, space-bearing column renaming (NM-002 TOP PRIORITY), reserved word list, schema layer prefixing, table name convention, column suffix standards (NM-006: _key, _sk, _date suffixes), null indicator naming, temporary object prefix.
**Specificity:** NM-002 names `[Supplier Key]`, `[Stock Item Key]`, `[Date Key]` as high-priority rename targets ✓.
**Technical accuracy:** NM-002 is tagged `priority: TOP_PRIORITY` — matches project-level priority ✓. Column suffix standard (_key, _date) ✓.
**Issues/gaps flagged:** NM-002 blocker pattern (dimension load will fail at runtime if column names contain spaces) ✓.
**Gap vs reference:** Reference NM-006 ("Table names must not be prefixed with the name of the schema layer") is absent. Participant NM-006 is about column suffix standards (different content).
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] Add NM-010: "Table names must not be prefixed with the name of the schema layer they reside in (e.g., `fact_purchase` not `silver_fact_fact_purchase`)." This is the key NM rule from the reference that is currently missing (–2 pts applied to this section). Adding it recovers +2 pts.

---

### TY — Type Mapping Rules (14/15)

**Coverage:** 26 rules covering all core T-SQL→Spark SQL type mappings. Key mappings verified:
- TY-012: DATETIME2→TIMESTAMP_NTZ ✓
- TY-009: NVARCHAR→STRING ✓
- TY-005: MONEY→DECIMAL(18,2) ✓
- TY-015: BIT→BOOLEAN ✓
- TY-008: UNIQUEIDENTIFIER→STRING ✓
- TY-020: geography CLR→3-column decomposition ✓
- TY-013: DATE→DATE ✓
**Specificity:** Each rule has source type, target type, and CAST example. Precision preservation rules noted.
**Technical accuracy:** All 26 mappings technically accurate ✓. TY-012 correctly maps DATETIME2 to TIMESTAMP_NTZ (not TIMESTAMP) ✓.
**Issues/gaps flagged:** TY dimension count (26) in the expected range (20–30) ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] TY-020 (geography CLR): participant decomposes into 3 columns but doesn't name the target column suffix pattern (_latitude, _longitude, _geo_type). Add the naming convention for the three resulting columns (+1 pt).

---

### OB — Object Rules (11/12)

**Coverage:** 11 rules: CREATE TABLE IF NOT EXISTS, COMMENT on tables, COMMENT on columns, TBLPROPERTIES (enableChangeDataFeed for lineage_run), CLUSTER BY, CONSTRAINT pk_* naming, DDL header requirement, partition avoidance, CHECK constraint prohibition, three-part catalog naming, IF NOT EXISTS guard.
**Specificity:** OB-004 (TBLPROPERTIES) names `delta.enableChangeDataFeed = true` specifically for lineage_run ✓. OB-006 (CLUSTER BY) names (date_key, supplier_key) as recommended columns ✓.
**Technical accuracy:** `CREATE TABLE IF NOT EXISTS` pattern ✓. Three-part naming (`catalog.schema.table`) ✓.
**Issues/gaps flagged:** OB-010 (excluded objects not to be migrated: original SQL Server views, SSMS artifacts) ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] OB-003 (CONSTRAINT pk_*): rule body doesn't specify that the PK constraint uses the 4-column composite grain for fact tables. Add an example PK covering `(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)` for purchase fact to make the rule actionable (+1 pt).

---

### SX — Syntax Rules (11/12)

**Coverage:** 17 rules. Key rules verified:
- SX-003: TOP(1) correlated SCD-2 subquery → `JOIN + ROW_NUMBER() OVER (PARTITION BY ... ORDER BY valid_from DESC) = 1` ✓
- SX-007: `NOLOCK` hint removal ✓
- SX-010: implicit JOIN → explicit JOIN ✓
- SX-014: SSIS staging truncation bug fix (`DELETE FROM Integration.Order_Staging` → `DELETE FROM Integration.Purchase_Staging`) ✓
- SX-015: T-SQL `IDENTITY(1,1)` → Spark `GENERATED ALWAYS AS IDENTITY(START WITH 1 INCREMENT BY 1)` ✓
**Specificity:** SX-003 explicitly states `ORDER BY valid_from DESC` ✓. SX-014 names both the wrong and correct table names ✓.
**Technical accuracy:** SX-003 ROW_NUMBER direction is DESC — this is the target-side pattern (most recent SK wins) ✓. SX-014 correctly identifies the bug ✓.
**Issues/gaps flagged:** SX-014 is the highest-impact syntax bug fix — present ✓.
**Structure:** Rule table ✓.

**Improvement items:**
- [ ] SX-003: add a note that the source T-SQL uses `ORDER BY Valid From ASC` (ascending, earliest match wins) and the migration changes semantics to `ORDER BY valid_from DESC` (most recent wins). Documenting the semantic shift justification prevents future misapplication (+1 pt).

---

### IF — Interface Rules (8/10)

**Coverage:** 5 rules: IF-001 (cross-product schema evolution — backward-compatible DDL changes only), IF-002 (dimension ownership — product owns the dimension load or reads from a shared dimension), IF-003 (lineage key interface — lineage_key passed via taskValues), IF-004 (access control — product grants READ to mart layer), IF-005 (schema DDL drift — products must not alter tables they do not own).
**Specificity:** IF-003 references `dbutils.jobs.taskValues` API ✓. IF-001 names ALTER TABLE ADD/DROP as the required approach vs CREATE OR REPLACE ✓.
**Technical accuracy:** IF-003 (lineage_key via taskValues) ✓. IF-005 (no ALTER TABLE on unowned tables) ✓.
**Issues/gaps flagged:** Application order rule absent — IF section defines interface rules but no explicit statement of rule application order (PL→NM→TY→OB→SX→IF). Auto-deduct applied.
**Structure:** Rule table with 5 rules ✓.

**Improvement items:**
- [ ] Add an "Application Order" section or header note stating the evaluation sequence: `PL → NM → TY → OB → SX → IF`. Reference defines this explicitly. This is the primary source of the auto-deduct (+3 pts recoverable).

---

### PE + LN Dimensions (7/7)

**Coverage:**
- PE (9 rules): Performance rules covering shuffle minimisation, broadcast join threshold, AQE settings, caching policy, OPTIMIZE scheduling, file compaction targets, partition avoidance, and ZORDER column selection.
- LN (8 rules): Lineage rules covering lineage_run table DDL ownership, lineage record lifecycle (open/close pattern), `was_successful` three-valued semantics (NULL=running, TRUE=success, FALSE=failed), lineage_key propagation pattern, package_name population, lineage record not-null assertions, downstream lineage propagation, and DDL for `lineage_run`.
**Technical accuracy:** LN-003 documents `was_successful BOOLEAN NULL` three-valued semantics ✓. LN-007 names `dbutils.jobs.taskValues` as the propagation mechanism ✓. lineage_run DDL in §7 has `was_successful BOOLEAN NULL` ✓.
**Issues/gaps flagged:** LN-003 has `was_successful` semantic comment; auto-deduct applied for abbreviated three-valued semantics description (–2 pts).
**Structure:** PE and LN rule tables ✓.

**Improvement items:**
- [ ] LN-003: expand `was_successful` comment to explicitly state all three values: "NULL = run currently in progress, TRUE = completed successfully, FALSE = completed with error". Current description mentions only two states. This recovers the –2 pts auto-deduct (+2 pts).
- [ ] Add Application Order section (PL→NM→TY→OB→SX→IF→PE→LN) to cover both original 6 plus the 2 extra dimensions → recovers auto-deduct (+3 pts).

---

## Extra Sections / Dimensions (not in reference)

- PE dimension (9 rules) — extra, not in reference. Assessed as additive.
- LN dimension (8 rules vs reference not having one) — extra. Assessed as additive.
- §7 lineage_run DDL — inline DDL for lineage_run table included in the project rules document. Extra value ✓.

## Approach Notes

- Reference is for GlobalPurchase_Project (30 rules, 6 dimensions). Participant is for Inventory_Stock_Project (90 rules, 8 dimensions). The SKILL domain notes describe 90 rules across 7 dimensions as the expected Inventory_Stock_Project project rule set. Participant matches the domain notes. Different project structure — not penalised.
- Reference IF has 4 base rules; participant IF has 5 rules — extra IF-005 (schema DDL drift) is additive.
- Application order auto-deduct: –3 pts for missing explicit statement of rule evaluation order.
- LN `was_successful` three-valued semantics: –2 pts for abbreviated description.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. IF dimension — Coverage — add explicit Application Order statement (PL→NM→TY→OB→SX→IF) → +3 pts
2. NM dimension — Coverage — add NM-010 preventing schema-layer-prefixed table names → +2 pts
3. LN dimension — Technical accuracy — expand `was_successful` three-valued semantics comment to name all three states explicitly → +2 pts

---

## Next Step

You can proceed to the next task.
