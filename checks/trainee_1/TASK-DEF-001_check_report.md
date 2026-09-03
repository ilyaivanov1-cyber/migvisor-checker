---
task_id: TASK-DEF-001
skill: task-checker-product-definition
participant_file: trainees/trainee_1/product-definition.yaml
reference_file: reference/product-definition.yaml
product: Sales_Orders
generated: 2026-09-03
total_score: 63/100
grade: Acceptable
---

# TASK-DEF-001 Check Report

**Product:** Sales_Orders
**Reference:** Purchase (GlobalPurchase_Project)
**Participant file:** `trainees/trainee_1/product-definition.yaml`
**Reference file:** `reference/product-definition.yaml`
**Generated:** 2026-09-03

---

## Score Summary

**The product definition Score: 63/100**

| Section | Reference Key | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Document Metadata | (file root) | 14 | 63/100 | 8.8 | ⚠ |
| Product Identity | `product` | 14 | 85/100 | 11.9 | ✓ |
| Input Ports | `inputPorts` | 14 | 12/100 | 1.7 | ✗ |
| Output Ports / Datasets | `outputPorts` | 15 | 78/100 | 11.7 | ✓ |
| Pipeline / Orchestration | `pipeline` | 15 | 93/100 | 13.9 | ✓ |
| Data Quality | `dataQuality` | 14 | 95/100 | 13.3 | ✓ |
| Migration / Source Lineage | `migration` | 14 | 65/100 | 9.1 | ⚠ |
| **Subtotal** | | | | **70.4** | |
| Auto-deducts | | | | **−7** | |
| **Total** | | | | **63/100** | |

**Grade: Acceptable**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Document Metadata | `schemaVersion:` at file root | semantic — key name differs |
| `product` | `productIdentity` | semantic — equivalent identity block |
| `inputPorts` | [MISSING] | missing — no dedicated input port section found |
| `outputPorts` | `datasets` | semantic — covers facts, dims, staging, mart, functions |
| `pipeline` | `orchestration` | semantic — equivalent orchestration block |
| `dataQuality` | `dataQuality` | exact match |
| `migration` | `sourceLineage` | semantic — equivalent legacy object mapping block |

**Extra sections (not scored):**
`platform`, `calculatedFields`, `consumers`, `sla`, `governance`, `pendingDecisions`, `tcpArtifacts`

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| Missing section with reference equivalent (inputPorts — no dedicated source connection section) | −5 pts | Yes — no section defines JDBC source, auth method, or credential reference |
| More than 40% of output port fields missing type declarations | −2 pts | Yes — only primaryKey and a handful of FK/transformation fields carry explicit types; the majority of dataset columns lack type declarations |
| No product identifier anywhere | −5 pts | No — `productIdentity.id: sales_orders` present |
| No output port schemas/fields defined anywhere | −4 pts | No — `datasets` contains primaryKey, foreignKey, and field definitions |
| No pipeline/orchestration specification | −3 pts | No — `orchestration` section fully specified |
| No DQ assertions anywhere | −3 pts | No — `dataQuality.assertions` has 5 assertions |
| Platform target inconsistent within document | −3 pts | No — all sections consistently target Databricks / globalsales catalog |
| Input port uses hardcoded connection string | −2 pts | N/A — no inputPorts section present |

---

## Section Feedback

### Document Metadata (8.8/14 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**ODPS compliance:**
- Schema declaration: `schemaVersion: "4.1"` present — but uses a non-standard key name (`schemaVersion`) rather than the ODPS-required `schema:` URL declaration. Reference uses `schema: "https://open-data-product-initiative.github.io/open-data-product-specification/v4.1/schema"`. URL not present.
- Version: version-equivalent value "4.1" present under `schemaVersion` ✓

**Sub-criteria breakdown (raw 63/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| ODPS schema declaration | 30% | 0/100 | `schema:` key with ODPS URL absent; `schemaVersion` is non-standard |
| ODPS version | 20% | 75/100 | Version value present but under non-standard key |
| Product identification | 30% | 100/100 | `productIdentity.id` and `displayName` both present |
| Product status | 20% | 90/100 | `status: active` — valid ODPS-like status value |

**Strengths:**
- Product ID and display name clearly established
- Status field present with a meaningful value

**Gaps:**
- ODPS-required `schema:` key with the specification URL is absent — the file root does not declare compliance with the ODPS schema
- `schemaVersion` is not a standard ODPS key name; the standard is `schema:` (URL) and optionally `specVersion:` or `version:` at file root

**Improvement items:**
- [ ] Add `schema: "https://open-data-product-initiative.github.io/open-data-product-specification/v4.1/schema"` at file root level (alongside `schemaVersion`)

---

### Product Identity → `productIdentity` (11.9/14 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

**Content completeness (85/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Identity fields present | 40% | 93/100 | id, displayName, version, status, domain, description all populated; `owner: TBD` scores 50% |
| Domain metadata | 20% | 70/100 | Domain present; no `tags:` array (reference has tags: purchase, fact, delta-lake, etc.) |
| Nested details equivalent | 40% | 85/100 | Schema/catalog info present across `platform` (targetCatalog, layers) + `datasets` — distributed but complete |

**Technical accuracy:** ODPS `status: active` is non-standard (ODPS vocabulary: draft/published/deprecated/retired) — minor. `priority: primary` is an extra field not in ODPS spec; acceptable as extension.

**Structure (88/100):**
- Section key present: ✓
- Nested depth: ✓ (equivalent depth to reference product block)

**Strengths:**
- All core identity fields populated (id, displayName, version, domain, description)
- `businessProcess: Order-to-Cash` adds meaningful domain context beyond reference scope
- Extra fields (priority, businessProcess) are valid extensions

**Gaps:**
- `owner: TBD` — unresolved placeholder; reference has `[USER INPUT REQUIRED]` equivalent but owner field should be targeted for completion
- No `tags:` array for product classification/discovery (reference has 5 tags)
- Status value `active` is non-standard ODPS vocabulary (should be `draft`, `published`, or `deprecated`)

**Improvement items:**
- [ ] Add `tags:` array (e.g., sales, fact, delta-lake, medallion, order-to-cash)
- [ ] Update `status:` to ODPS vocabulary: `draft` or `published`
- [ ] Resolve `owner: TBD` with the actual team or person

---

### Input Ports → [MISSING] (1.7/14 pts)

**Criteria scored:** Content completeness (80%), Authentication spec (10%), Structure (10%)

**This is the primary structural gap in the document.** The reference defines a dedicated `inputPorts:` section specifying the JDBC source connection, authentication method, credential reference, and extraction pattern. The participant has no equivalent section. Source connection information is partially implied in `orchestration` (incremental strategy, incrementalKey) and `sourceLineage` (legacySystem name), but no section explicitly defines:

- JDBC connection type/protocol
- Source database location/URL (even as `[USER INPUT REQUIRED]` placeholder)
- Authentication method (Databricks Secrets, managed identity, etc.)
- Credentials reference (secret scope and key)
- Per-entity update frequency

**Content completeness (15/100):**
- Ports present: 0 — no input port entry defined
- Connection details: ~20% — `sourceLineage.legacySystem` names SQL Server; `orchestration.incrementalKey` documents extraction key
- Extraction pattern: ~30% — `orchestration.strategy: incremental` documented

**Authentication spec (0/100):**
- No auth method documented
- No credential reference (no Databricks Secrets scope/key)

**Structure (0/100):**
- Section key absent

**Improvement items:**
- [ ] **Add `inputPorts:` section** with at least one entry covering: type (jdbc), protocol (jdbc:sqlserver), location (`[USER INPUT REQUIRED — Databricks Secret scope and key]`), authenticationMethod (databricks-secrets), updateFrequency (nightly), extractionMode (incremental), watermarkColumn (equivalent to LastEditedWhen)
- [ ] Document Databricks Secrets scope and key reference for the JDBC URL credential

---

### Output Ports / Datasets → `datasets` (11.7/15 pts)

**Criteria scored:** Content completeness (70%), Field Schemas (20%), Structure (10%)

**Content completeness (87/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Output port categories present | 40% | 100/100 | Fact ✓, dimension ✓, staging ✓, mart ✓, functions ✓ — all reference categories covered and exceeded |
| Port metadata present | 30% | 85/100 | name, type, layer, description on all datasets; updateFrequency absent per dataset (inherited from orchestration schedule) |
| Location and format present | 30% | 70/100 | catalog.schema.table names ✓; storageFormat declared globally in `platform:` but NOT per-dataset (Delta assumed) |

**Field schemas (36/100):**
- Ports with any field-level metadata: ~8/19 datasets (fact.sale foreignKeys+primaryKey, fact.order, dim.customer pii columns, dim.city transformation columns, dim.date calendar bounds, stg.lineage primaryKey, stg.dq_rejections schema under dataQuality) = 42%
- Field coverage ratio: ~40% — FK column names and PK column present for main facts; but full measure/attribute field list absent (e.g., quantity, unit_price, tax_rate columns on fact.sale not listed)
- Field metadata completeness: ~30% — fields that ARE defined have name; type present for primaryKey and transformation fields; nullable/description largely absent

Field schemas score = 42%×40 + 40%×30 + 30%×30 = 16.8 + 12 + 9 = **38/100**

**Structure (100/100):**
- Section key present: ✓ (datasets)
- Nested depth: ✓ (facts / dimensions / staging / mart / functions sub-categories — richer than reference)

**Strengths:**
- Comprehensive dataset catalog across all medallion layers — 19 datasets vs 4 reference output ports
- `datasets.functions` correctly documents the UDF consolidation with signature and COALESCE NULL guard
- `datasets.mart` fully documents view types, parameters, and primary dataset dependencies
- dim.city legacyColumnTransformation correctly captures the GEOGRAPHY decomposition with target types
- SCD type documented per dimension

**Gaps:**
- No full field-level schema on any dataset (no flat `fields:` list with name/type/nullable/description for measures and attributes)
- `format:` not declared per dataset (only `storageFormat: Delta` in platform section)
- `updateFrequency:` absent per dataset (only schedule in orchestration section)
- Fact table measure fields (quantity, unit_price, tax_rate, etc.) not listed as fields

**Improvement items:**
- [ ] Add a `fields:` list to at least `globalsales.fact.sale` and `globalsales.fact.order` covering all measure columns with name, type, nullable, description
- [ ] Add `format: delta` and `updateFrequency: nightly` per fact/dimension dataset entry
- [ ] Add `fields:` list to dimension tables for the SCD-2 tracking columns (is_current, row_effective_date, row_expiry_date, surrogate key)

---

### Pipeline / Orchestration → `orchestration` (13.9/15 pts)

**Criteria scored:** Content completeness (75%), Dependency Chain (15%), Structure (10%)

**Content completeness (100/100):**
- Orchestration platform: `Databricks Workflows` ✓
- Schedule: `cron: "0 2 * * *"` UTC with description ✓
- Pipeline layers: 4 stages (bronze, silver_dimensions, silver_facts, gold) vs 4 reference layers ✓
- Tasks named: 14 tasks vs 9 reference tasks — min(14/9, 1.0) = 100% ✓
- Error handling: `halt_and_alert`, maxRetries=2, retryDelayMinutes=5 — extra detail not in reference ✓

**Dependency chain (50/100):**
- `runOrder` documents 4 stages in correct ETL sequence (bronze → dimensions → facts → gold) ✓
- Stage ordering is implicit (array position) — no explicit `dependsOn:` keys per stage
- Reference uses explicit `dependsOn: [ingestion]` pattern per layer → participant does not
- `dependency_ordering_correct`: bronze→dims→facts→gold is the correct dependency ordering ✓

Dependency chain score = 50%×0 + 50%×100 = **50/100**

**Structure (100/100):**
- Section key present: ✓ (orchestration)
- Nested depth: ✓ (runOrder stages with tasks, errorHandling)

**Strengths:**
- Most complete pipeline spec in the document — all 14 tasks named, schedule precise (cron UTC)
- Error handling (halt_and_alert, retries) not in reference — valuable addition
- Correct ETL layer ordering: bronze → silver_dimensions → silver_facts → gold

**Gaps:**
- `runOrder` stages lack explicit `dependsOn:` keys — ordering relies on array position rather than declared dependencies
- `alertChannel: TBD` — pending; should reference a specific Databricks notification destination or Teams/email channel

**Improvement items:**
- [ ] Add `dependsOn:` field per `runOrder` stage (e.g., `silver_dimensions: dependsOn: [bronze]`) to make dependencies explicit rather than positional
- [ ] Resolve `alertChannel: TBD` with actual notification destination

---

### Data Quality → `dataQuality` (13.3/14 pts)

**Criteria scored:** Content completeness (75%), Severity/Handling (15%), Structure (10%)

**Content completeness (98/100):**
- Assertions defined: 5 participant vs 3 reference — 100%; all reference assertion categories present (row-count ✓ via rowCountReconciliation, FK integrity ✓ via DQ-ORDER-RI-001/002, null check ✓ via DQ-SALE-001/002/DQ-ORDER-001) ✓
- Rejection sink documented: `globalsales.stg.dq_rejections` ✓; rejectionSchema with 5 fields (name + type) ✓
- Traceability field: `run_id: BIGINT` in rejectionSchema ✓ (equivalent to lineage_key)
- Reconciliation pattern: `rowCountReconciliation.enabled=true, tolerance=0` with description ✓

**Severity/handling (76/100):**
- Assertions with severity: 5/5 = 100% (critical / error labels) ✓
- Assertions with blocking classification: severity levels imply blocking but no explicit `blocks: true/false` field — partial credit 60%
- Pipeline behavior on violation: `rowCountReconciliation` explicitly states "run to fail and triggers an alert" ✓; individual assertion pipeline behavior embedded in `rejectionSink` pattern but not labeled per assertion ~60%

Severity score = 40%×100 + 40%×60 + 20%×60 = **76/100**

**Structure (100/100):**
- Section key present: ✓ (dataQuality)
- Sub-keys: assertions, rejectionSink, rejectionSchema, rowCountReconciliation, pendingThresholds — all present ✓

**Strengths:**
- Strongest section in the document — comprehensive and well-structured
- `rejectionSchema` defines the rejection table structure with 5 fields ✓
- `rowCountReconciliation` explicitly states zero-tolerance policy ✓
- `pendingThresholds` with `decisionRef: CX-DQ-01` correctly signals open items ✓
- Reference uses only 3 assertions and no rejection schema; participant exceeds reference depth significantly

**Gaps:**
- No explicit `blocks: true/false` field per assertion — reference uses `severity: blocking` vs `severity: informational`; participant uses `critical` / `error` which imply blocking but don't follow the ODPS severity vocabulary
- Individual assertions don't state pipeline behavior (halt / continue / reject-and-continue)

**Improvement items:**
- [ ] Add `blocks: true` / `blocks: false` field per assertion to make blocking classification explicit
- [ ] Consider aligning severity vocabulary with ODPS: `blocking` and `informational` rather than `critical` and `error`

---

### Migration / Source Lineage → `sourceLineage` (9.1/14 pts)

**Criteria scored:** Content completeness (80%), Source Mapping (10%), Structure (10%)

**Content completeness (62/100):**

| Sub-criterion | Weight | Score | Notes |
|---|---|---|---|
| Source system identified | 20% | 100/100 | `legacySystem: WideWorldImportersDW (SQL Server)` ✓ |
| Mappings present | 50% | 83/100 | 11 object mappings cover facts, dims, staging; missing control tables in sourceLineage block (etl_cutoff, lineage listed as datasets but not in source lineage); no orchestration mapping (SSIS → Databricks) |
| Known risks documented | 30% | 0/100 | No `knownRisks:` or equivalent risks section; reference documents 5 specific bugs and migration caveats |

Content score = 20%×100 + 50%×83 + 30%×0 = **62/100**

**Source mapping (60/100):**
- Mappings with source + target: 11/11 = 100% ✓ (each legacy object has source name and targetDataset)
- Type labels present: 0/11 = 0% — mappings are listed as `legacySourceObjects` without type classification (fact table / dimension / staging / control)
- Notes where needed: dim.city has GEOGRAPHY note ✓, function has consolidation note ✓; other objects without notes = 2/11 that need notes covered = ~50%

Source mapping score = 50%×100 + 30%×0 + 20%×50 = **60/100**

**Structure (100/100):**
- Section key present: ✓ (sourceLineage)
- Nested depth: ✓ (legacySourceObjects, legacyFunctionsConsolidated, legacyReportsMigrated)

**Strengths:**
- All 11 legacy dataset objects mapped with source name (bracket notation) and target (three-part catalog name) ✓
- `legacyFunctionsConsolidated` correctly documents the UDF consolidation with NULL guard note ✓
- `legacyReportsMigrated` lists all 9 Power BI reports — no equivalent in reference; adds value ✓
- `legacySystem` identification clear ✓

**Gaps:**
- **No `knownRisks:` section** — the reference documents 5 critical migration bugs/caveats (SSIS staging truncation bug, table-name-with-space, SCD-2 DELETE+INSERT rewrite, sentinel rows, dimension-before-fact ordering). The participant has no equivalent section documenting migration risks for Sales_Orders.
- `legacyFunctionsConsolidated.legacyFn1` and `legacyFn2` are both `TBD` — source function names not resolved
- Control tables (`etl_cutoff`, `lineage`) appear in `datasets.staging` but are absent from `sourceLineage.legacySourceObjects` — their source-to-target mapping is undocumented in the lineage block
- No type labels per mapping (fact table, dimension, staging, control, function)
- No orchestration-level mapping (SSIS container/pipeline → Databricks Workflow job)

**Improvement items:**
- [ ] **Add `knownRisks:` section** documenting Sales_Orders-specific migration caveats (e.g., GEOGRAPHY column decomposition, UDF consolidation, NOLOCK removal, Sales_Staging lineage_key asymmetry fix, dbo.OrderDetails decommission)
- [ ] Add `[Integration].[ETL_Cutoff]` and `[Integration].[Lineage]` to `legacySourceObjects` with target mappings
- [ ] Resolve `legacyFn1`/`legacyFn2` TBD values with actual legacy UDF names from as-is analysis
- [ ] Add type classification per mapping entry (fact table, dimension, staging, control table, UDF, orchestration)
- [ ] Add orchestration mapping: `SSIS pipeline (nightly)` → `Databricks Workflow nightly_etl_main`

---

## Extra Sections (not in reference)

- **`platform`** — targetCatalog, architecture, medallion layer names, storageFormat, governancePlatform, computeEndpoint. Valuable structural context that fills a gap the reference covers implicitly via tags/details. No score impact.
- **`calculatedFields`** — 8 derived/business-metric field definitions with formulas, constants (PROFIT_MARGIN_FACTOR: 1.05), and output dataset references. Substantially richer than reference scope — correctly externalises hard-coded values for parameterization. No score impact.
- **`consumers`** — 9 Power BI reports mapped to Databricks SQL endpoint with primary dataset references. Adds serving-layer traceability not in reference. No score impact.
- **`sla`** — dataFreshness T+1, load completion UTC target, retention policy by layer, pick-time SLA (TBD). Well-structured SLA contract. No score impact.
- **`governance`** — Unity Catalog RLS, CLS, PII masking (dim.customer), audit lineage. More comprehensive than anything in reference. No score impact.
- **`pendingDecisions`** — CX-P04, CX-P05, CX-DQ-01 with owners (TBD) and impacted artifacts. Correctly surfaces open decisions. No score impact.
- **`tcpArtifacts`** — workspace paths for as-is, to-be, and transformation rules artefacts. Useful for document navigation. No score impact.

---

## Improvement Items

1. **[Input Ports — Missing Section]** Add a dedicated `inputPorts:` section with JDBC source connection, auth method (databricks-secrets), credential reference (secret scope/key), and extraction pattern (incremental, watermarkColumn) → up to +12.3 pts (eliminates the largest single loss + removes -5 auto-deduct)
2. **[Migration — Known Risks]** Add `knownRisks:` block documenting Sales_Orders-specific migration caveats (GEOGRAPHY decomp, UDF consolidation, NOLOCK removal, staging lineage_key asymmetry, sentinel rows) → up to +4.2 pts
3. **[Document Metadata — ODPS Schema URL]** Add `schema: "https://open-data-product-initiative.github.io/open-data-product-specification/v4.1/schema"` at file root → up to +4.2 pts (removes partial ODPS compliance gap)
4. **[Output Ports — Field Schemas]** Add `fields:` list to fact.sale and fact.order with all measure/attribute columns (name, type, nullable, description) → up to +2.0 pts + removes -2 auto-deduct
5. **[Pipeline — Dependency Chain]** Add explicit `dependsOn:` per `runOrder` stage → up to +1.1 pts
6. **[Migration — Source Mapping Types]** Add type classification labels per sourceLineage mapping entry → up to +0.8 pts
7. **[Product Identity — Tags]** Add `tags:` array to productIdentity → up to +0.5 pts
8. **[Data Quality — Blocking Classification]** Add `blocks: true/false` per DQ assertion → up to +0.3 pts

---

## Priority Actions

1. **Add `inputPorts:` section** — even a minimal JDBC entry with placeholders (`[USER INPUT REQUIRED]` for the URL, `authenticationMethod: databricks-secrets`, `updateFrequency: nightly`, `extractionMode: incremental`) — eliminates the biggest point loss and removes the -5 auto-deduct → up to **+12.3 pts**
2. **Add `knownRisks:` to `sourceLineage`** — document at least the GEOGRAPHY column decomposition, UDF consolidation, NOLOCK removal, and Sales_Staging lineage_key asymmetry as identified risks → up to **+4.2 pts**
3. **Add ODPS `schema:` URL at file root** — one line change, resolves the Document Metadata ODPS compliance gap → up to **+4.2 pts**
4. **Add `fields:` lists to fact tables** — cover at least the measure columns on fact.sale and fact.order; also removes the -2 field-type auto-deduct → up to **+3.0 pts combined**
5. **Add `dependsOn:` per orchestration stage** — makes pipeline dependency order explicit → up to **+1.1 pts**

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| **60–74** | **Acceptable** | **Several gaps; revise before proceeding** |
| 45–59 | Needs work | Missing schemas, DQ spec, or pipeline definition |
| 0–44 | Incomplete | Critical sections absent or product unidentifiable |
