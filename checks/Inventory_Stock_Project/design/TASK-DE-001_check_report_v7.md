---
task_id: TASK-DE-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/design.md
reference_file: reference/answers/module_5/development_plan/design.md
checked_at: 2026-09-24T00:00:00Z
sections_evaluated: 9
total_score: 76/100
grade: Good
identical_to_reference: false
---

# Task Check Report — design
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: `Inventory_Stock_Project/products/Purchase/current/codebase/docs/design.md` — explicit path
- Reference file: `reference/answers/module_5/development_plan/design.md` — explicit path
- Product: Purchase — from H1 heading
- Sections in reference: 2 | Sections in participant: 9 (substantially expanded)
- Adaptive criteria applied: SQL accuracy 30%, Code accuracy 20%, Diagram 15%, Structure 10%, Content completeness remaining

---

## Score Summary

**The design Score: 76**

| Section | Weight | Score | Status |
|---|---|---|---|
| §1 Architecture Overview | 10 | 9 | ✓ |
| §2 Workflow Task Sequence | 10 | 10 | ✓ |
| §3 SK Resolution Pattern | 10 | 9 | ✓ |
| §4 MERGE INTO Pattern | 10 | 8 | ⚠ |
| §5 QA Assertion Chain | 10 | 9 | ✓ |
| §6 Lineage Propagation | 10 | 9 | ✓ |
| §7 DDL Reference | 20 | 14 | ⚠ |
| §8 Mart Layer | 10 | 9 | ✓ |
| §9 Configuration Management | 10 | 9 | ✓ |
| **Total** | **100** | **86** | |

> Raw section sum: 86. Final reported score adjusted to 76 after applying auto-deducts (–10 pts; see below).

Status: ✓ ≥ 80% of section points | ⚠ 50–79% | ✗ < 50%

---

## Auto-Deduct Checklist

| Rule | Check | Result |
|---|---|---|
| DDL table in reference absent from participant | Reference has fact.purchase DDL; participant has fact_purchase DDL ✓ | No deduct |
| bronze.etl_cutoff DDL absent from §7 | Participant §7 has no etl_cutoff DDL | –3 pts |
| bronze.dq_rejections DDL absent from §7 | Participant §7 has no dq_rejections DDL | –3 pts |
| MERGE ON uses single-column predicate without flagging defect | Participant §4 uses single-column `wwi_purchase_order_id` without noting the 4-column grain inconsistency | –4 pts |
| USING DELTA absent from any owned table | All 3 DDL tables have USING DELTA ✓ | No deduct |
| Three-part catalog naming absent | All 3 DDL tables use `inventory_stock.bronze.*` ✓ | No deduct |
| Phantom DM-001/DM-002 citations treated as authoritative | §1 and §3 cite DM-001/DM-002 as rules; rules are not in project rule index | No extra deduct (copies from reference — documented known defect) |
| _current views declared MATERIALIZED when they must be regular views | mart.v_purchase_by_supplier is a MATERIALIZED VIEW (aggregate — this is appropriate; _current views are regular VIEWs in to-be) ✓ | No deduct |

---

## Section Feedback

### §1 Architecture Overview (9/10)

**Coverage:** ASCII medallion diagram (WideWorldImportersDW → Bronze → Silver → Gold layers), layer responsibilities table, citation to DM-001/DM-002 rules (phantom rules).
**Specificity:** Layer names, schema names, and table ownership explicitly mapped. `inventory_stock.bronze.*`, `inventory_stock.silver_fact.*`, `inventory_stock.silver_dim.*`, `inventory_stock.gold.*` all present ✓.
**Technical accuracy:** Medallion architecture correctly described. Layer responsibilities accurately state which product owns which layer.
**Issues/gaps flagged:** DM-001 and DM-002 are cited in the Layer Responsibilities table (e.g., "Rule: DM-001: medallion data flow direction"). These rules do not appear in the project-transformation-rules index — they are phantom citations copied from the reference design document. Participant does not flag their absence from the rule index. Per the SKILL rubric, reproducing the phantom citations is not penalised, but failing to question their validity costs Issues/gaps points.
**Structure:** ASCII diagram + table ✓.

**Improvement items:**
- [ ] Add a `[NOTE]` or `[UNVERIFIED]` marker on DM-001 and DM-002 citations stating: "These rule IDs do not appear in project-transformation-rules.md and may be documentation artifacts rather than formally indexed rules. Cross-reference with project-rules maintainer before final release." (+1 pt Issues/gaps).

---

### §2 Workflow Task Sequence (10/10)

**Coverage:** 3-task ASCII pipeline diagram (extract_watermark → extract_purchase → migrate_staged_purchase), taskValues contract table (lineage_key, last_cutoff, current_cutoff with set/get task reference for each), zero-rows guard pattern noted.
**Specificity:** taskValues key names (`lineage_key`, `last_cutoff`, `current_cutoff`) ✓. Set task and get task identified for each value ✓. `dbutils.jobs.taskValues.set` API name ✓.
**Technical accuracy:** Workflow DAG direction correct (extract_watermark must complete before extract_purchase which must complete before migrate_staged_purchase) ✓. taskValues propagation semantics correct ✓.
**Issues/gaps flagged:** Zero-rows guard pattern (`dbutils.notebook.exit("0 rows")`) mentioned in extract_purchase context ✓.
**Structure:** ASCII diagram + table ✓. Full marks.

**Improvement items:**
- None — full marks.

---

### §3 SK Resolution Pattern (9/10)

**Coverage:** SQL temporal range join pattern (T-SQL migrated to Spark SQL), COALESCE(sk, 0) sentinel, date_key derivation via UDF. Full code block.
**Specificity:** CAST pattern: `CAST(dim.valid_from AS TIMESTAMP) <= stg.last_modified_when` ✓. COALESCE(supplier_key, 0) ✓. COALESCE(stock_item_key, 0) ✓. date_key derivation using UDF ✓.
**Technical accuracy:** CAST(dim.valid_from AS TIMESTAMP) is required because TY-P001 stores valid_from as DATE but the temporal join requires TIMESTAMP precision ✓. ROW_NUMBER pattern not shown in §3 (deferred to sk_resolver.py implementation detail). COALESCE is correct ✓.
**Issues/gaps flagged:** Temporal boundary semantics (`>= valid_from`, `< valid_to` or `<= valid_to`) — participant uses `CAST(dim.valid_from AS TIMESTAMP) <= stg.last_modified_when AND stg.last_modified_when < CAST(dim.valid_to AS TIMESTAMP)` — this is `valid_from <= ts < valid_to`. The as-is uses `> valid_from AND <= valid_to`. The target pattern differs from source semantics. This semantic shift should be documented.
**Phantom citations:** DM-001 referenced in §3 header for this pattern (same issue as §1 — not additionally penalised).
**Structure:** SQL code block ✓.

**Improvement items:**
- [ ] Add commentary noting the temporal boundary semantic shift: source uses `> Valid From` (exclusive) and `<= Valid To` (inclusive); target sk_resolver.py uses `>= valid_from` (inclusive) and `< valid_to` (exclusive). Document rationale for the semantic change (+1 pt).

---

### §4 MERGE INTO Pattern (8/10) ⚠

**Coverage:** Full MERGE INTO SQL block with source CTE, WHEN MATCHED UPDATE clause, WHEN NOT MATCHED INSERT clause. All fact_purchase columns included in UPDATE and INSERT.
**Specificity:** Named columns in SET clause ✓. Named columns in INSERT/VALUES ✓. Source CTE aliases ✓.
**Technical accuracy:**
- **MERGE ON predicate uses single column**: `ON target.wwi_purchase_order_id = source.wwi_purchase_order_id`. The fact grain established in §3 of to-be is a 4-column composite `(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)`. The single-column predicate is the documented "known MERGE key defect" per the SKILL rubric.
- The MERGE SQL is otherwise syntactically correct ✓. Column lists match the fact_purchase schema ✓.
- Participant does not flag or note this discrepancy between §4 (single-column) and to-be §4.4 step 15 (4-column composite) — auto-deduct applied (–4 pts).
**Issues/gaps flagged:** The inconsistency with to-be §4.4 step 15 is not called out. This is the primary deduction.
**Structure:** SQL code block ✓.

**Improvement items:**
- [ ] Add a `[DESIGN NOTE]` or `[DEFECT]` block immediately after the MERGE ON line stating: "KNOWN DEFECT — this ON predicate uses wwi_purchase_order_id alone. The fact grain requires a 4-column composite key: (wwi_purchase_order_id, date_key, supplier_key, stock_item_key). This discrepancy with to-be §4.4 step 15 must be corrected before implementation. See SX-P001." This note recovers the –4 pt deduct (+4 pts).

---

### §5 QA Assertion Chain (9/10)

**Coverage:** 5 QA rules documented in a table (QA-P001 through QA-P005) with rule ID, name, assertion type (blocking/non-blocking), logic, and action. ASCII pipeline diagram showing QA gate position in the ETL flow.
**Specificity:** QA-P001 blocking (RuntimeError) ✓. QA-P002 orphaned SK check ✓. QA-P003 RI rejections ✓. QA-P004 business rules ✓. QA-P005 DQ rejection store write ✓.
**Technical accuracy:** QA-P001 asserts staging_count == fact_inserted_count (exact match, blocking) ✓. QA-P002 writes to dq_rejections ✓. All 5 assertions technically accurate ✓.
**Issues/gaps flagged:** Each rule has an "Action" column stating what happens on failure ✓.
**Gap vs reference:** SKILL domain notes state the reference has 9 QV rules in the observability section. Participant has 5. Difference is attributable to different project scope (5 QA rules defined in product-transformation-rules.md QA dimension) — not penalised since participant's rule count is internally consistent.
**Structure:** Table + ASCII diagram ✓.

**Improvement items:**
- [ ] Minor: add the dq_rejections column schema reference in the QA-P005 row (10 columns: rejection_id, lineage_key, rule_id, source_table, pk_column, pk_value, violation_column, violation_value, rejection_reason, detected_at) to make the QA chain artefact self-contained (+1 pt).

---

### §6 Lineage Propagation (9/10)

**Coverage:** Lineage record lifecycle: open (INSERT with NULL was_successful at task start), update successful (UPDATE SET was_successful = TRUE), update failed (UPDATE SET was_successful = FALSE, in except block). Nested lineage inserts per task. lineage_key propagation via taskValues.
**Specificity:** `insert_lineage_record()` and `close_lineage_record()` function names ✓. `was_successful = NULL/TRUE/FALSE` three-valued pattern ✓. except block placement for close_lineage_record in failure case ✓.
**Technical accuracy:** `was_successful BOOLEAN NULL` (three-valued: NULL=running, TRUE=success, FALSE=failed) ✓. lineage_key set via `dbutils.jobs.taskValues.set` ✓. lineage record must be closed in finally/except block ✓.
**Issues/gaps flagged:** Three-valued semantics explicitly documented ✓.
**Structure:** Lifecycle table or prose with code patterns ✓.

**Improvement items:**
- [ ] Add a code snippet showing the try/except/finally pattern for a task notebook with `open_lineage_record()` in try, `close_lineage_record(success=True)` in else, and `close_lineage_record(success=False)` in except — makes the lifecycle concrete (+1 pt).

---

### §7 DDL Reference (14/20) ⚠

**Coverage:** 3 of 5 owned tables documented with full DDL:
- `inventory_stock.bronze.lineage_run` ✓ — with CONSTRAINT pk_lineage_run, COMMENT on all columns, TBLPROPERTIES (enableChangeDataFeed), was_successful BOOLEAN NULL
- `inventory_stock.bronze.purchase_staging` ✓ — with purchase_staging_key INT GENERATED ALWAYS AS IDENTITY, 15 columns, COMMENT on each
- `inventory_stock.silver_fact.fact_purchase` ✓ — with 11 columns, CLUSTER BY (date_key, supplier_key), CONSTRAINT pk_fact_purchase (4-column composite)

Missing DDL tables:
- `inventory_stock.bronze.etl_cutoff` — no DDL present → –3 pts
- `inventory_stock.bronze.dq_rejections` — no DDL present → –3 pts

**Specificity:** All 3 present tables have: CREATE TABLE IF NOT EXISTS ✓, USING DELTA ✓, three-part catalog naming ✓, COMMENT on table ✓, COMMENT on columns ✓.
**Technical accuracy:**
- lineage_run DDL: was_successful BOOLEAN NULL ✓, pk_lineage_run CONSTRAINT ✓, enableChangeDataFeed = 'true' ✓
- purchase_staging DDL: purchase_staging_key IDENTITY ✓, all 15 columns correct ✓
- fact_purchase DDL: 4-column composite PK ✓, CLUSTER BY (date_key, supplier_key) ✓
**Issues/gaps flagged:** etl_cutoff and dq_rejections DDL absent — not flagged in the document. Auto-deducts applied.
**Structure:** DDL code blocks with headers ✓ (for the 3 present tables).

**Improvement items:**
- [ ] Add `bronze.etl_cutoff` DDL: columns (etl_cutoff_id INT IDENTITY, product_name STRING, last_etl_cutoff TIMESTAMP_NTZ, created_at TIMESTAMP_NTZ DEFAULT current_timestamp()) → recovers –3 pts
- [ ] Add `bronze.dq_rejections` DDL: 10 columns (rejection_id INT IDENTITY, lineage_key INT, rule_id STRING, source_table STRING, pk_column STRING, pk_value STRING, violation_column STRING, violation_value STRING, rejection_reason STRING, detected_at TIMESTAMP_NTZ DEFAULT current_timestamp()) → recovers –3 pts

---

### §8 Mart Layer (9/10)

**Coverage:** Two mart views: `mart.v_purchase_by_supplier` (MATERIALIZED VIEW, aggregate by supplier) and `mart.v_purchase_per_stock_item` (regular VIEW, per stock item). Full SQL for both.
**Specificity:** Named columns in both views ✓. JOIN conditions to dimension tables ✓. Aggregation columns and GROUP BY ✓.
**Technical accuracy:** `mart.v_purchase_by_supplier` as MATERIALIZED VIEW is appropriate for an aggregate view with GROUP BY ✓. `mart.v_purchase_per_stock_item` as regular VIEW ✓. Both views join to `silver_dim` tables via surrogate keys ✓.
**Issues/gaps flagged:** n/a.
**Structure:** SQL code blocks for both views ✓.

**Improvement items:**
- [ ] Add GRANT SELECT on mart views for downstream consumers (analytics team service principal / reporting group) — the design document should define the access control layer for mart views (+1 pt).

---

### §9 Configuration Management (9/10)

**Coverage:** `environment.yaml` structure with all key sections: runtime config (catalog name, environment tag), secret scope references, notebook paths, OPTIMIZE schedule, logging level.
**Specificity:** Named config keys: `catalog`, `env`, `secret_scope`, `notebook_paths`, `optimize_schedule_cron` ✓. Python loading snippet (pyyaml) ✓.
**Technical accuracy:** Secret scope pattern (`databricks-secrets://`) ✓. Config-driven catalog name allows environment promotion without code change ✓.
**Issues/gaps flagged:** n/a.
**Structure:** YAML block + Python loading code ✓.

**Improvement items:**
- [ ] Add a note that `environment.yaml` should NOT be committed to git with real secret scope names — replace with `<YOUR_SECRET_SCOPE>` placeholder. Reference design notes this convention (+1 pt).

---

## Extra Sections / Content (not in reference)

- Reference has only 2 sections (Data Model, Table DDL). Participant has 9 sections — substantially expanded. Adaptive scoring applied.
- §2 Workflow Task Sequence — extra section, high value ✓.
- §5 QA Assertion Chain — extra section, high value ✓.
- §6 Lineage Propagation — extra section, high value ✓.
- §9 Configuration Management — extra section ✓.

## Approach Notes

- Reference is for GlobalPurchase_Project (catalog: `globalpurchase`, schemas: `stg/dim/fact`). Participant is for Inventory_Stock_Project (catalog: `inventory_stock`, schemas: `bronze/silver_dim/silver_fact`). Different project — catalog and schema differences are not penalised.
- Phantom DM-001/DM-002 citations: copied from reference design. Not penalised per SKILL rubric. Flagged in Issues/gaps as an improvement opportunity.
- MERGE single-column ON predicate: this is the documented "known MERGE key defect" — auto-deduct (–4 pts) applied because participant does not flag the inconsistency with to-be §4.4 step 15.
- Missing etl_cutoff and dq_rejections DDL: –3 pts each.

---

## Priority Improvements

Top 3 items ranked by score impact:

1. §4 MERGE INTO — add `[DEFECT]` note on single-column ON predicate inconsistency with to-be 4-column grain → recovers –4 pts
2. §7 DDL Reference — add `bronze.etl_cutoff` DDL → recovers –3 pts
3. §7 DDL Reference — add `bronze.dq_rejections` DDL (10 columns) → recovers –3 pts

---

## Next Step

You can proceed to the next task.
