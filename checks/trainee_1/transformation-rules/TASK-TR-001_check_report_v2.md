---
task_id: TASK-TR-001
project: Sales_Orders
participant_file: trainees/trainee_1/product-transformation-rules.md
reference_file: reference/product-transformation-rules.md
checked_at: 2026-09-03
sections_evaluated: 10
total_score: 88/100
grade: Good
identical_to_reference: false
---

# Task Check Report — transformation rules
_Sales_Orders | 2026-09-03_

**File resolution log:**
- Participant file: `trainees/trainee_1/product-transformation-rules.md` — auto-detected (single trainee folder)
- Reference file: `reference/product-transformation-rules.md` — auto-detected
- Project: Sales_Orders — from H1 heading `# Product Transformation Rules: Sales_Orders`
- Sections in reference: 10 (9 dimension + 1 metadata) | Sections in participant: 11 (9 matched + 1 metadata + 1 extra: PE)
- Point weights: auto-calculated — N=10, base=10, remainder=0; all sections 10 pts

---

## Score Summary

**The transformation rules Score: 88**

| Section | Matched to | Weight | Score | Status |
|---|---|---|---|---|
| Dimension Table | ## Dimension Table | 10 | 9.4 | ✓ |
| Platform (PL) | ### PL — Platform | 10 | 8.7 | ✓ |
| Naming (NM) | ### NM — Naming | 10 | 9.0 | ✓ |
| Types (TY) | ### TY — Types | 10 | 9.5 | ✓ |
| Objects (OB) | ### OB — Objects | 10 | 9.5 | ✓ |
| Syntax (SX) | ### SX — Syntax | 10 | 9.5 | ✓ |
| Interface (IF) | ### IF — Interface | 10 | 5.3 | ⚠ |
| Custom (CX) | ### CX — Custom | 10 | 9.3 | ✓ |
| Quality (QA) | ### QA — Quality | 10 | 9.5 | ✓ |
| Lineage (LN) | ### LN — Lineage | 10 | 8.3 | ✓ |
| **Total** | | **100** | **88.1** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### Dimension Table (9.4/10)
_Matched to participant ## Dimension Table_

**Dimension coverage:** All 9 reference dimensions present. Participant adds PE (Performance) as a 10th dimension — extra content, not penalized.

**Count accuracy:** Most counts internally consistent.
- TY: Dimension Table claims "16 active" but Rule Index shows 14 active TY rows. Discrepancy of 2 — within the ±2 tolerance, but should be reconciled.
- OB: Dimension Table claims "9 active + 2 inactive + 1 extension"; Rule Index shows 8 active rows and 3 inactive (OB-004, OB-009, OB-010). Minor mismatch.
- All other dimensions: internally consistent ✓

**File references:** All 10 dimensions have hyperlinked YAML file references following `<PREFIX>-<name>.yaml` pattern ✓

**Structure:** Matches reference structure closely — Dimension | Prefix | File | Rule Count | Customizations columns. Adding "(effective)" to Rule Count column name is clear and appropriate.

**Rule inventory:**
- Reference dims: 9 | Participant dims: 10 (9 matched + 1 extra: PE)

**Improvement items:**
- [ ] Reconcile TY "active" count: update Dimension Table from 16 to 14 active TY rules (verify whether 2 rules exist in YAML but are absent from the Rule Index table)
- [ ] Reconcile OB inactive count: Dimension Table says 2 inactive; Rule Index shows 3 inactive (OB-004, OB-009, OB-010)

---

### Platform (PL) (8.7/10)
_Matched to participant ### PL — Platform (10 rules, 2 product notes)_

**Rule coverage:** All 4 reference PL themes covered, with additional product-specific detail:
- USING DELTA → PL-003 ✓
- SSIS/SQL Agent → Databricks Workflows → PL-010 ✓
- Medallion architecture → PL-009 ✓ (but see intent issue below)
- SEQUENCE → IDENTITY → PL-004 ✓

Participant adds 6 extra PL rules (engine identity, schema mapping, ETL pattern, clustering election, application procedures, transaction model) — all valid.

**Intent accuracy:** PL-009 has incorrect schema names in the Rule Index: states `integration→bronze, dim→silver_dim, fact→silver_fact, analytics→gold`. The correct Sales_Orders schema mapping is `integration→stg, dim→dim, fact→fact, analytics→mart`. The changelog (2026-08-28 pass 2) claims PL-009 was corrected, but the Rule Index text still shows the old names. This is a significant accuracy issue for this rule.

**Technical accuracy:** All other rules reference correct Databricks/Delta Lake platform. PL-003 correctly distinguishes Fact.Sale (CCX→liquid clustering) from Fact.Order (rowstore→partitioned). PL-008 correctly maps XACT_ABORT ON → Delta atomic writes ✓.

**Metadata correctness:** Prefix PL consistent throughout all 10 rules ✓.

**Structure:** Table format correct, PL-NNN convention followed ✓.

**Rule inventory:**
- Reference rules: 4 | Participant rules: 10 | Missing IDs: none

**Improvement items:**
- [ ] **Fix PL-009 intent**: Change `integration→bronze, dim→silver_dim, fact→silver_fact, analytics→gold` to `integration→stg, dim→dim, fact→fact, analytics→mart` — aligns with the changelog claim and with actual schema names used throughout (OB-001 uses `globalsales.dim.*`, OB-002 uses `globalsales.fact.*`, OB-003 uses `globalsales.stg.*`)

---

### Naming (NM) (9.0/10)
_Matched to participant ### NM — Naming (9 rules, 1 product note)_

**Rule coverage:** All 5 reference NM themes covered:
- lowercase_snake_case → NM-001 ✓
- underscores for spaces → NM-002 (product-specific examples) ✓
- v_ prefix for views → NM-004 ✓
- _staging suffix + exceptions → NM-005 (partial — see intent below)
- schema layer mapping → NM-003 (partial)

Participant adds 4 extra NM rules (UDF consolidation, sequences not migrated, index/constraint naming, temp table naming).

**Intent accuracy:**
- NM-003: "Schema → catalog.schema mapping" — vague; does not state actual direction (integration→stg, dimension→dim, etc.). Reference NM-005 explicitly names all target schemas.
- NM-005: "_staging suffix for integration tables" — omits the exceptions (lineage and etl_cutoff tables do NOT get _staging suffix). Could lead to incorrect naming of those tables.

**Technical accuracy:** All Databricks naming conventions correct ✓.

**Metadata correctness:** Prefix NM consistent, 9 rules ✓.

**Structure:** Table present, NM-NNN convention ✓.

**Rule inventory:**
- Reference rules: 5 | Participant rules: 9 | Missing IDs: none

**Improvement items:**
- [ ] **Update NM-003 intent**: Explicitly state the schema mapping directions (`integration→stg, dimension→dim, fact→fact, analytics→mart`)
- [ ] **Update NM-005 intent**: Add the exceptions clause — `stg.lineage` and `stg.etl_cutoff` are NOT named with `_staging` suffix

---

### Types (TY) (9.5/10)
_Matched to participant ### TY — Types (16 active + 14 inactive + 1 extension)_

**Rule coverage:** All 6 reference project-level TY rules covered, typically with more granularity:
- INT/BIGINT → TY-003 + TY-004 ✓ (split into two rules)
- DECIMAL/FLOAT → TY-005 ✓
- NVARCHAR/TEXT → TY-011 ✓
- DATE/DATETIME → TY-012 + TY-015 (TIMESTAMP_NTZ) ✓
- BIT/VARBINARY → TY-020 + TY-018 ✓ — UNIQUEIDENTIFIER not explicitly covered
- IDENTITY → TY-023 ✓

Product extension: TY-EXTEND-001 (geography → location_wkt/lat/lon) — appropriate product-specific column handling ✓. 14 inactive rules correctly noted ✓.

**Intent accuracy:** All type mappings accurate. TY-015 uses TIMESTAMP_NTZ — valid Databricks syntax documenting timezone-naive semantics explicitly ✓.

**Technical accuracy:** All Databricks/Delta Lake types correct throughout. No Snowflake or Azure Synapse type names ✓.

**Metadata correctness:** Minor count discrepancy noted (16 claimed vs 14 counted). Within tolerance. Prefix TY consistent ✓.

**Structure:** Table format correct, inactive rules noted with clear explanation ✓.

**Rule inventory:**
- Reference rules: 8 | Participant rules: 14 active + 14 inactive + 1 extension | Missing: UNIQUEIDENTIFIER not explicit

**Improvement items:**
- [ ] Add explicit rule for UNIQUEIDENTIFIER → STRING if applicable to Sales_Orders schema; if no UNIQUEIDENTIFIER columns exist, add to inactive list
- [ ] Reconcile TY active count in Dimension Table (claims 16, Rule Index shows 14)

---

### Objects (OB) (9.5/10)
_Matched to participant ### OB — Objects (9 active + 2 inactive + 1 extension)_

**Rule coverage:** All 5 reference OB project themes covered with more granularity (separate rules per layer: OB-001 dims, OB-002 facts, OB-003 staging, OB-005 views vs single reference rule). ETL procedures → Python (OB-007) ✓, SEQUENCE → IDENTITY (OB-008) ✓, application.* not migrated (OB-009/010) ✓.

Product extension: OB-006 (UDF consolidation getTotalQuantitySold1/2 → single UDF with NULL guard) — appropriate product-specific object rule ✓.

**Intent accuracy:** All OB intents accurate and detailed. OB-003 cross-reference to LN-EXTEND-001 ✓. OB-005 correctly identifies CustomerSalesSummary as materialized view ✓.

**Technical accuracy:** globalsales.* three-part naming consistent throughout ✓.

**Metadata correctness:** Minor count discrepancy noted (Dimension Table 9+2, Rule Index 8+3). Prefix OB consistent ✓.

**Structure:** Table format correct, inactive rules clearly marked ✓.

**Rule inventory:**
- Reference rules: 6 | Participant rules: 9 active + 3 inactive + 1 extension | Missing IDs: none

**Improvement items:**
- [ ] Reconcile OB inactive count in Dimension Table (claims 2, Rule Index shows 3)

---

### Syntax (SX) (9.5/10)
_Matched to participant ### SX — Syntax (15 active + 2 inactive + 1 extension)_

**Rule coverage:** All 5 reference SX themes covered with rich expansion. Transaction control removal (SX-002/003) ✓, MERGE patterns (SX-001/003) ✓, T-SQL→Spark (SX-005/007/016) ✓, SCD-2 MERGE (SX-003) ✓.

Product extension: SX-EXTEND-001 (NOLOCK removal in v_OrderToSupplyAnalytics + auxiliary table scope review) — appropriate product-specific syntax concern ✓.

Additional rules (SX-004, SX-006, SX-009, SX-011, SX-012, SX-013, SX-014, SX-015) expand coverage beyond reference — all valid ✓.

**Intent accuracy:** All SX intents accurate. SX-013 correctly documents the IDENTITY + Python lineage pattern, cross-referencing LN-003 ✓. SX-016 CAST/CONVERT translations are specific and correct ✓.

**Technical accuracy:** All Spark SQL / Python syntax targets correct. No T-SQL constructs in target ✓.

**Metadata correctness:** 15+2+1 count matches Rule Index ✓. Prefix SX consistent ✓.

**Structure:** Table format correct, inactive rules noted, SX-NNN convention ✓.

**Rule inventory:**
- Reference rules: 6 | Participant rules: 15 active + 2 inactive + 1 extension | Missing IDs: none

**Improvement items:**
- None identified.

---

### Interface (IF) (5.3/10)
_Matched to participant ### IF — Interface (3 product-new rules)_

**Rule coverage:** This is the primary gap in the document. The reference IF dimension covers the **ingestion interface** (workflow orchestration, JDBC extraction, credentials, staging patterns). The participant's IF dimension covers the **serving interface** (Power BI reconnection, column naming, SQL endpoint provisioning).

Reference IF themes vs participant coverage:
- IF-001 (SSIS → Databricks Workflow orchestration) → partially in PL-010 (not in IF section) — 50%
- IF-001-EXT (explicit dimension dependency constraint for fact loads) → not documented as IF rule
- IF-002 (JDBC incremental reads with watermark commit pattern) → not documented as transformation rule
- IF-003 (Databricks Secrets for JDBC credentials) → referenced in requirements, not transformation rules
- IF-004 (staging truncate+overwrite pattern) → not documented in IF

Participant IF-P01/IF-P02/IF-P03 are valid Power BI serving interface rules and are appropriate product-specific additions. However, they replace rather than supplement the ingestion-side IF rules.

Coverage of reference IF themes in IF section: ~25%

**Intent accuracy:** Participant IF-P01/P02/P03 intents are accurate for the serving layer they describe, but address a different interface concern than the reference dimension defines.

**Technical accuracy:** Databricks SQL endpoint, snake_case + aliased display names — all technically correct ✓.

**Metadata correctness:** 3 rules (vs reference 5). Prefix IF consistent ✓.

**Structure:** Table format correct, IF-P0N convention ✓.

**Rule inventory:**
- Reference rules: 5 (4 project + 1 extension) | Participant rules: 3 (all product-new, different domain)
- Missing reference themes: JDBC extraction, watermark commit, Databricks Secrets, staging truncate+overwrite, explicit dimension dependency constraint

**Improvement items:**
- [ ] **Add ingestion interface rules**: (a) JDBC extraction with watermark-bounded query for `stg.sale_staging` and `stg.order_staging`, (b) Databricks Secrets for JDBC credentials (scope and key reference), (c) staging layer truncate+overwrite pattern
- [ ] **Add task dependency rule**: Document explicit dependency: fact loads depend on all dimension loads completing — the Sales_Orders equivalent of reference IF-001-EXT-P01
- [ ] Consider restructuring IF into ingestion interface + serving interface sub-groups to capture both concerns

---

### Custom (CX) (9.3/10)
_Matched to participant ### CX — Custom (4 product-new rules)_

**Rule coverage:** All expected custom concern types present with product-appropriate content. Business calculation codification (CX-P01: 1.05 profit factor as named constant + DQ sanity bound) ✓, parameterization of hard-coded values (CX-P02: date filters, rolling window) ✓, legacy cleanup (CX-P03: dbo.OrderDetails decommission, 2 BI reports reconnected) ✓, pending decision gate (CX-P04: OLTP-direct extraction strategy) ✓.

**Intent accuracy:** All CX intents accurate and grounded in analysis:
- CX-P01 correctly identifies the 1.05 factor needing a named constant + DQ sanity bound ✓
- CX-P02 correctly parameterizes both the hard-coded `'20230101'` and the `100`-day rolling window ✓
- CX-P03 identifies the correct decommission target and both affected Power BI reports ✓
- CX-P04 correctly flags OLTP-direct as PENDING_DECISION ✓

**Technical accuracy:** All CX rules reference correct schema/product context ✓.

**Metadata correctness:** 4 rules, CX-P0N prefix consistent, labelled "product-new" ✓.

**Structure:** Table format correct ✓.

**Rule inventory:**
- Reference rules: 3 (product-only) | Participant rules: 4 (product-only) | Extra: CX-P04 (supplementary)

**Deferred fields `[DEFERRED]`:** CX-P04 PENDING_DECISION — intentional deferral ✓.

**Improvement items:**
- None identified.

---

### Quality (QA) (9.5/10)
_Matched to participant ### QA — Quality (3 product-new rules)_

**Rule coverage:** Participant QA exceeds reference scope — reference bundles all assertions in 1 rule; participant separates into 3 (assertions, gate integration, reconciliation). All reference QA concern types present: data assertions (QA-P01) ✓, DQ gate integration (QA-P02) ✓, row count reconciliation (QA-P03) ✓.

**Intent accuracy:** All QA intents accurate. QA-P01 assertions are product-appropriate (dry+chiller sum, profit guard, backorder integrity, cross-fact variance ≤5%, orphan keys) ✓. QA-P02 correctly names `globalsales.stg.dq_rejections` and lineage record ✓. QA-P03 zero-tolerance reconciliation (staging = fact delta = lineage count) is precise ✓.

**Technical accuracy:** All schema references correct ✓.

**Metadata correctness:** 3 rules, QA-P0N prefix consistent ✓.

**Structure:** Table format correct ✓.

**Rule inventory:**
- Reference rules: 1 (product-only) | Participant rules: 3 (product-only) | Missing IDs: none

**Improvement items:**
- None identified.

---

### Lineage (LN) (8.3/10)
_Matched to participant ### LN — Lineage (7 rules, 1 extension)_

**Rule coverage:** Participant LN is substantially more comprehensive than the reference's single product rule, covering full lineage infrastructure migration (table migration, SEQUENCE retirement, Python utilities, propagation, Unity Catalog system lineage, run metadata). LN-004/LN-EXTEND-001 documents the Sale_Staging lineage_key asymmetry fix — a product-specific quirk similar in spirit to reference LN-P01 ✓.

The reference's LN-P01 theme (cross-domain column name compatibility risk documentation) is not explicitly present in the participant's LN section.

**Intent accuracy:** All 7 LN intents accurate:
- LN-001 (integration.lineage → globalsales.stg.lineage) ✓
- LN-002 (SEQUENCE → IDENTITY on lineage_key) ✓
- LN-003 (getlineagekey → Python open/close_lineage_record) ✓
- LN-004 (lineage_key propagation to both facts + Sale_Staging asymmetry fix) ✓
- LN-005 (ReseedAllSequences retired) ✓
- LN-006 (Unity Catalog system lineage for globalsales.*) ✓
- LN-007 (ETL run metadata per 4 pipeline tasks) ✓

**Technical accuracy:** globalsales.stg.lineage, Python utilities, Unity Catalog — all correct ✓.

**Metadata correctness:** 7 rules, LN-NNN prefix consistent ✓.

**Structure:** Table format correct ✓.

**Rule inventory:**
- Reference rules: 1 (product-only) | Participant rules: 7 + 1 extension | Minor gap: cross-domain compatibility risk

**Improvement items:**
- [ ] Consider adding a cross-domain compatibility note if any `globalsales.stg.lineage` columns have naming contracts with other products (e.g., if Order team consumes this table and depends on specific column names/types) — analogous to reference LN-P01

---

## Extra Sections (not in reference)

- **Performance (PE)** — 8 rules covering CCX index drop, partitioning/ZORDER (Fact.Order), liquid clustering election (Fact.Sale), OPTIMIZE strategy, broadcast joins, staging table policy, auto-optimize settings. Valid and detailed product-specific dimension covering physical optimization decisions not present in the reference. No score impact.

## Approach Notes

- Participant splits several reference rules into more granular per-object or per-concern rules (TY integer types split, OB objects split by layer, SX patterns expanded) — all valid; coverage maintained ✓
- Participant uses IF dimension for BI serving interface rather than ingestion interface — valid product-specific choice but results in missing ingestion-side IF rules
- NM-002 uses Sales_Orders-specific table name examples rather than generic rule — valid product-specific application ✓
- QA dimension expanded from 1 to 3 rules for clarity — adds value ✓
- Changelog documents extensive corrections in pass 1 and pass 2 (Snowflake → Databricks types, schema names, lineage function names) — PL-009 still shows pre-correction schema names

---

## Priority Improvements

1. **Interface (IF) — Rule coverage** — Add ingestion interface rules: JDBC extraction with watermark, Databricks Secrets for credentials, staging truncate+overwrite, and explicit task dependency constraint → recoverable **~+4.6 pts** on IF section (5.3 → ~9.9)
2. **Platform (PL) — PL-009 intent** — Correct medallion schema names: `bronze/silver_dim/silver_fact/gold` → `stg/dim/fact/mart` in PL-009 Rule Index text → recoverable **~+0.4 pts**
3. **Naming (NM) — NM-003/NM-005 intent clarity** — Add explicit schema mapping directions in NM-003; add staging name exceptions to NM-005 → recoverable **~+0.3 pts**

---

## Next Step

Score 88/100 is Good. The document is thorough across 9 of 10 dimensions. Address the IF ingestion interface rules before proceeding — this is the only structural gap. Minor fixes to PL-009 schema names and NM intent clarity are quick wins. You can proceed to the next task.
