# Requirements: Purchase

**Product:** Purchase · **Project:** GlobalPurchase_Project
**Source:** product-definition.yaml · **Date:** 2026-08-25
**Status:** draft

---

## Functional Requirements

---

### FR-001 — Incremental Data Ingestion from Source System

| Field | Detail |
|---|---|
| **ID** | FR-001 |
| **Title** | Incremental Data Ingestion from Source System |
| **Description** | The pipeline must read procurement records incrementally from the configured JDBC source connection on each nightly execution. Only records created or modified after the high-water mark stored in `stg.etl_cutoff` must be fetched. The ingested payload must be landed in the `globalpurchase.stg` staging schema using a truncate-and-overwrite pattern before any transformation step begins. |
| **Acceptance Criteria** | (1) On each run, the JDBC read predicate applies the watermark value from `stg.etl_cutoff`, so zero rows are re-read from before the last successful watermark. (2) `stg.purchase_staging` contains exactly the rows returned by the bounded JDBC query after the ingestion task completes. (3) A run with no new source rows produces an empty staging table and does not fail. (4) The ingestion task is the first task in the Databricks Workflow DAG; no downstream task may start before it completes successfully. |
| **Source** | `product-definition.yaml` → `input_ports`, `pipeline.layers.ingestion`, `staging.purchase_staging` |

---

### FR-002 — Watermark Management

| Field | Detail |
|---|---|
| **ID** | FR-002 |
| **Title** | Watermark Management via ETL Cutoff Table |
| **Description** | The system must maintain a persistent high-water mark in `stg.etl_cutoff` that records the upper boundary of the most recently ingested batch. At the start of each run the current watermark is read and used to bound the JDBC query. At the end of a successful run the watermark must be advanced to the maximum source timestamp observed in the ingested rows. The watermark must not be updated if the pipeline run fails before all layers complete successfully. |
| **Acceptance Criteria** | (1) The watermark row in `stg.etl_cutoff` for the Purchase product exists after bootstrap and has a valid non-null value. (2) After a successful nightly run, the watermark value is strictly greater than the value recorded before the run started. (3) After a failed run (any layer), the watermark value is identical to the value recorded before the run started. (4) Successive full runs never produce duplicate fact rows attributable to overlapping watermark windows. |
| **Source** | `product-definition.yaml` → `input_ports.watermark_table`, `staging.etl_cutoff` |

---

### FR-003 — Dimension Loading: Supplier (SCD Type 2)

| Field | Detail |
|---|---|
| **ID** | FR-003 |
| **Title** | Supplier Dimension Load with Slowly Changing Dimension Type 2 |
| **Description** | The system must maintain `globalpurchase.dim.supplier` as a Slowly Changing Dimension Type 2 table. On each run the pipeline must compare incoming supplier attributes against the current active rows in the dimension. For each supplier whose attributes have changed, the existing active row must be expired (`row_expiry_date` and `valid_to` set to the day before the effective date, `is_current_row = false`) and a new active row inserted (`is_current_row = true`, `valid_from` and `row_effective_date` set to the current processing date, `valid_to` / `row_expiry_date` set to `9999-12-31`). New suppliers must be inserted as active rows. Unchanged suppliers must not produce a new row. |
| **Acceptance Criteria** | (1) A supplier attribute change produces exactly two rows in `dim.supplier` for that supplier: one expired and one active. (2) A new supplier produces exactly one row with `is_current_row = true`. (3) An unchanged supplier produces no additional rows. (4) No active row has `valid_to` other than `9999-12-31`. (5) No expired row has a null `row_expiry_date`. (6) A sentinel row with `supplier_key = 0` is always present. |
| **Source** | `product-definition.yaml` → `output_ports.dim.supplier`, `known_risks.scd2_rewrite`, `known_risks.sentinel_rows` |

---

### FR-004 — Dimension Loading: Stock Item (SCD Type 2)

| Field | Detail |
|---|---|
| **ID** | FR-004 |
| **Title** | Stock Item Dimension Load with Slowly Changing Dimension Type 2 |
| **Description** | The system must maintain `globalpurchase.dim.stock_item` as a Slowly Changing Dimension Type 2 table using the same merge logic as FR-003. All SCD-2 merge semantics (expire, insert, skip-unchanged) described in FR-003 apply equally to this dimension. |
| **Acceptance Criteria** | (1) All SCD-2 acceptance criteria from FR-003 apply to `dim.stock_item`. (2) A sentinel row with `stock_item_key = 0` is always present. (3) The dimension contains at least one active row per distinct stock item present in the source batch. |
| **Source** | `product-definition.yaml` → `output_ports.dim.stock_item`, `known_risks.scd2_rewrite`, `known_risks.sentinel_rows` |

---

### FR-005 — Dimension Loading: Date Calendar

| Field | Detail |
|---|---|
| **ID** | FR-005 |
| **Title** | Static Date Calendar Dimension Bootstrap and Availability |
| **Description** | The system must provide a pre-populated static date calendar in `globalpurchase.dim.date`. `date_key` must be an integer in `YYYYMMDD` format. The calendar is populated once during bootstrap and is not refreshed on nightly runs. The nightly pipeline must verify that `dim.date` is non-empty before fact loading proceeds; it must not truncate or re-populate the table. |
| **Acceptance Criteria** | (1) After bootstrap, `dim.date` contains one row per calendar day with no gaps and no duplicate `date_key` values. (2) `date_key` equals the integer `YYYYMMDD` representation of each calendar day. (3) The nightly pipeline does not modify `dim.date` row count or content. (4) A pre-run check confirms `dim.date` is non-empty; if empty the pipeline aborts before any fact rows are written. |
| **Source** | `product-definition.yaml` → `output_ports.dim.date`, `pipeline.layers.ingestion` |

---

### FR-006 — Fact Table Loading: Purchase Fact

| Field | Detail |
|---|---|
| **ID** | FR-006 |
| **Title** | Purchase Fact Table Load with Surrogate Key Resolution |
| **Description** | The system must populate `globalpurchase.fact.purchase` from staged procurement records. For each staged row, the pipeline must resolve `date_key` from `dim.date`, `supplier_key` from `dim.supplier` (current active row), and `stock_item_key` from `dim.stock_item` (current active row). `purchase_key` is generated automatically as a BIGINT identity value. |
| **Acceptance Criteria** | (1) Each staged row produces exactly one row in `fact.purchase` after a successful run. (2) `date_key`, `supplier_key`, and `stock_item_key` match the current active dimension rows as of the processing date. (3) `purchase_key` is non-null, unique, and monotonically increasing across runs. (4) `lineage_key` is non-null on every fact row and references a valid row in `stg.lineage`. |
| **Source** | `product-definition.yaml` → `output_ports.fact.purchase`, `pipeline.layers.facts` |

---

### FR-007 — Orphaned Key Handling and Sentinel Row Fallback

| Field | Detail |
|---|---|
| **ID** | FR-007 |
| **Title** | Orphaned Surrogate Key Resolution Using Sentinel Rows |
| **Description** | When a staged fact row cannot be matched to an active dimension row, the pipeline must assign sentinel surrogate key `0` for the unresolved dimension rather than dropping the row or raising a fatal error. The unresolved row must also be recorded in `stg.dq_rejections` as an informational DQ event. |
| **Acceptance Criteria** | (1) An unresolvable supplier natural key produces a fact row with `supplier_key = 0`. (2) An unresolvable stock item natural key produces a fact row with `stock_item_key = 0`. (3) Every fact row written with a sentinel key has a corresponding entry in `stg.dq_rejections` (informational). (4) The pipeline does not abort due to unresolved dimension keys. (5) Sentinel rows exist in `dim.supplier` and `dim.stock_item` before any fact load. |
| **Source** | `product-definition.yaml` → `known_risks.sentinel_rows`, `dq.fk_integrity`, `dq.orphaned_keys` |

---

### FR-008 — Lineage Tracking

| Field | Detail |
|---|---|
| **ID** | FR-008 |
| **Title** | Pipeline Lineage Tracking |
| **Description** | The system must record a lineage entry in `stg.lineage` for each pipeline execution, capturing: execution timestamp, pipeline run identifier, source row count, target row count, and run status. Each inserted fact row must carry the `lineage_key` of the lineage record for that run. |
| **Acceptance Criteria** | (1) A new row is inserted into `stg.lineage` at the start of each pipeline run. (2) Every fact row produced by a given run carries the same non-null `lineage_key`. (3) The lineage record's source row count equals the count of rows in `stg.purchase_staging` for that run. (4) The lineage record is updated with final run status upon pipeline completion. |
| **Source** | `product-definition.yaml` → `staging.lineage`, `output_ports.fact.purchase.columns.lineage_key` |

---

### FR-009 — Data Quality Checks and Rejection Handling

| Field | Detail |
|---|---|
| **ID** | FR-009 |
| **Title** | Data Quality Validation, Reconciliation, and Rejection Logging |
| **Description** | **Blocking:** staging count must equal fact delta for the batch — mismatch halts pipeline. **Informational:** FK integrity (LEFT ANTI JOIN per FK column) and orphaned key detection (key=0 or NULL). All informational failures written to `stg.dq_rejections`; do not halt pipeline. |
| **Acceptance Criteria** | (1) A count mismatch does not advance to mart tasks and raises an observable error. (2) A matching count always proceeds to mart tasks. (3) Every FK or orphaned-key violation produces one row in `stg.dq_rejections` per offending fact row per violated constraint. (4) Rejection records include: run ID, timestamp, table, column, reason, offending key. (5) Zero DQ violations → zero rejection rows for that run. |
| **Source** | `product-definition.yaml` → `dq.*`, `staging.dq_rejections` |

---

### FR-010 — Source Truncation Correction

| Field | Detail |
|---|---|
| **ID** | FR-010 |
| **Title** | Correct Handling of Source Data Truncation Defect |
| **Description** | A known defect in the source integration caused purchase staging to receive stale data from an incorrect table rather than being truncated before each run. The target pipeline must apply a corrective truncate-before-overwrite pattern in `stg.purchase_staging` to ensure each run reflects only current-batch data. |
| **Acceptance Criteria** | (1) `stg.purchase_staging` contains only rows from the current batch after each ingestion run. (2) No stale rows from prior runs accumulate in the staging table. (3) The truncate operation is the first step of the ingestion task, before any rows are written. |
| **Source** | `product-definition.yaml` → `known_risks.risk-1` (SSIS truncation bug) |

---

### FR-011 — Bootstrap Initialization

| Field | Detail |
|---|---|
| **ID** | FR-011 |
| **Title** | One-Time Bootstrap Initialization of Sentinel Rows, Watermark, and Date Calendar |
| **Description** | A bootstrap routine executed once before the first nightly run must: (1) insert sentinel rows (`key = 0`) into `dim.supplier` and `dim.stock_item`; (2) pre-populate `dim.date` with the full static calendar; (3) create the initial watermark row in `stg.etl_cutoff`. The routine must be idempotent — re-running produces no duplicates and no errors. |
| **Acceptance Criteria** | (1) After bootstrap, `dim.supplier` contains exactly one row with `supplier_key = 0`. (2) After bootstrap, `dim.stock_item` contains exactly one row with `stock_item_key = 0`. (3) After bootstrap, `dim.date` contains one row per calendar day with no gaps or duplicates. (4) After bootstrap, `stg.etl_cutoff` contains one row for Purchase with a non-null watermark. (5) Running bootstrap twice produces no additional rows and no errors. |
| **Source** | `product-definition.yaml` → `known_risks.sentinel_rows`, `staging.etl_cutoff`, `output_ports.dim.date` |

---

### FR-012 — Mart and Serving Layer Population

| Field | Detail |
|---|---|
| **ID** | FR-012 |
| **Title** | Mart Layer Population from Fact and Dimension Layers |
| **Description** | After all fact and dimension loads complete and the blocking DQ check passes, the pipeline must refresh `globalpurchase.mart` by reading from `fact.purchase` joined to current active dimension rows. Mart population is the final DAG task and must not execute if any upstream task has failed. |
| **Acceptance Criteria** | (1) After a successful nightly run, the mart layer reflects all fact rows accumulated through that run. (2) The mart task does not execute when any upstream DAG task is in a failed state. (3) Mart rows correctly resolve dimension attributes from `is_current_row = true` dimension rows. (4) Mart population completes within the nightly batch window. |
| **Source** | `product-definition.yaml` → `pipeline.layers.mart_and_dq`, `output_ports` |

---

## Non-Functional Requirements

This section defines the non-functional requirements (NFRs) governing quality attributes of the Purchase data product. All requirements apply to the target Databricks Delta Lake environment managed through Unity Catalog.

---

### NFR-001 — Performance

**Description**
The end-to-end nightly Databricks Workflow — spanning ingestion, dimensions, facts, and mart_and_dq layers — must complete within the allocated nightly batch window so that curated data is available for business consumption at the agreed service time. The `fact.purchase` table uses Delta Lake clustering on `(date_key, supplier_key, stock_item_key)` to minimise query scan volume. A conditional `OPTIMIZE` is executed after each merge only when `rows_merged` exceeds the `FACT_OPTIMIZE_ROW_THRESHOLD` constant, preventing unnecessary compute cycles on low-volume runs.

**Acceptance Criteria**
- The full pipeline completes within the nightly batch window on a representative production data volume, verified over five consecutive business-day runs.
- `OPTIMIZE` is triggered on `fact.purchase` only when `rows_merged > FACT_OPTIMIZE_ROW_THRESHOLD`; runs below the threshold skip `OPTIMIZE` and log the skip reason.
- Query plans on `fact.purchase` using `date_key`, `supplier_key`, or `stock_item_key` predicates demonstrate file pruning through Delta clustering statistics.

---

### NFR-002 — Availability

**Description**
The Purchase pipeline is scheduled as a nightly Databricks Workflow. A pipeline failure must not go undetected; automated alerting must notify the responsible team within a defined time window so that recovery or reprocessing can occur before the next business day begins.

**Acceptance Criteria**
- The Databricks Workflow is configured with a nightly schedule and raises an alert (email or webhook) on any task-level or job-level failure.
- Alert delivery occurs within 15 minutes of job failure detection.
- Runbook documentation covers the standard recovery procedure (re-trigger, partial reprocess) and is accessible to the on-call team.

---

### NFR-003 — Security

**Description**
All credentials required by the pipeline are stored exclusively in Databricks Secrets under the `globalpurchase-dev` and `globalpurchase-prod` scopes. No credential value may appear in plaintext in notebook code, configuration files, YAML definitions, or version-controlled assets. Access is governed by Unity Catalog GRANT statements per layer.

**Acceptance Criteria**
- A static scan of all notebooks, Python modules, YAML, and config files finds zero hardcoded credential values.
- Secrets are retrieved exclusively through `dbutils.secrets.get(scope=..., key=...)` calls.
- Unity Catalog GRANT statements restrict SELECT, MODIFY, and USAGE rights to minimum required principals per layer.
- Dev and prod scopes are isolated: prod secrets are inaccessible from dev cluster policies.

---

### NFR-004 — Scalability

**Description**
The data product must accommodate growth in purchase transaction volume, supplier count, and date range without requiring schema changes or architectural redesign. Delta Lake clustering provides physical layout optimisation that improves as data accumulates.

**Acceptance Criteria**
- Adding row volume to `fact.purchase` does not require DDL changes.
- A 2x increase in daily ingestion volume is handled within the same pipeline structure and batch window.

---

### NFR-005 — Idempotency

**Description**
Every step in the pipeline — ingestion, dimension upserts, fact merge, mart refresh, and DQ processing — must be idempotent. Re-executing any step or the full pipeline for the same business date must produce identical target table state.

**Acceptance Criteria**
- Running the full pipeline twice for the same business date yields row counts and checksums identical to a single run.
- Dimension upserts use MERGE INTO so that re-runs update existing keys rather than insert duplicates.
- Fact merges use MERGE INTO keyed on `wwi_purchase_order_id` so repeated execution produces the same fact row set.

---

### NFR-006 — Maintainability

**Description**
The codebase must follow the defined layout so that any team member can locate, modify, and test artifacts without tribal knowledge. Table and column names are referenced exclusively through `constants.py`.

**Accepted Directory Layout**

```
config/          — environment configuration (no secrets)
docs/            — generated and hand-authored documentation
src/
  db/            — DDL, views, grants, policies, indexes
  etl/           — pipeline notebooks and Python modules
```

**Acceptance Criteria**
- All deliverable files reside within the defined layout.
- `constants.py` contains all table-name, schema-name, and threshold constants; a grep for hardcoded schema-qualified table names in ETL logic returns zero results.
- Linting and formatting checks (`flake8`, `black`) pass with zero errors on all Python files.

---

### NFR-007 — Observability

**Description**
Every row processed by the pipeline carries a `lineage_key` enabling end-to-end traceability from raw ingestion through to mart layer. DQ evaluation outcomes are written to `stg.dq_rejections` so that data stewards can review and remediate quality issues.

**Acceptance Criteria**
- `lineage_key` is populated on every row in every layer; a query returning rows with a NULL `lineage_key` from any managed table returns zero rows.
- `stg.dq_rejections` is written to in every pipeline run where DQ violations are detected.
- Pipeline logs capture row counts (input, merged/inserted, rejected) per task, accessible in Databricks Workflow run history.

---

### NFR-008 — Data Retention

**Retention Schedule**

| Layer | Tables | Delta Log Retention | Delta File Retention |
|---|---|---|---|
| Fact | `fact.purchase` | 2 555 days | 2 555 days |
| Dimension | All `dim.*` tables | 2 555 days | 2 555 days |
| Staging | All `stg.*` tables | 90 days | 90 days |

**Acceptance Criteria**
- `delta.logRetentionDuration` and `delta.deletedFileRetentionDuration` table properties are set in the DDL for every managed table and match the schedule above.
- Running `DESCRIBE DETAIL` on each table confirms the retention properties.
- Fact and dimension tables retain full Delta history for at least 2 555 days.

---

## Data Quality Requirements

This section defines the data quality requirements (DQRs) governing the Purchase data product pipeline. All assertions execute after dimension and fact table loads and before mart promotion. Failures are persisted to `globalpurchase.stg.dq_rejections` and are traceable via `lineage_key`. Blocking failures halt the pipeline; informational failures are logged and reviewed without blocking the load.

---

### DQR-001 — Row Count Reconciliation

**ID:** DQR-001 · **Severity:** BLOCKING

**Description:** After each incremental batch load, the number of rows processed from the staging layer must equal the net delta of rows inserted or updated in `globalpurchase.fact.purchase`. Zero tolerance — no row may be silently dropped or duplicated between staging and the fact table.

**Acceptance Criteria:**
- The staging row count for the batch equals the net row delta in `fact.purchase` for the same batch identifier.
- The reconciliation check completes before any downstream mart refresh is triggered.

**Violation Handling:** Pipeline halts immediately. No mart promotion occurs. The discrepant batch is flagged in `stg.dq_rejections` with batch identifier, expected count, actual count, and `lineage_key`.

---

### DQR-002 — Foreign Key Referential Integrity

**ID:** DQR-002 · **Severity:** Informational

**Description:** All non-null FK columns in `fact.purchase` — `supplier_key`, `stock_item_key`, and `date_key` — must resolve to a valid surrogate key in their respective dimension tables. Implemented as a LEFT ANTI JOIN per FK column.

**Acceptance Criteria:**
- A LEFT ANTI JOIN between `fact.purchase` and each dimension on the respective FK column returns zero unmatched rows for a clean batch.
- The check runs after fact load and before mart promotion.

**Violation Handling:** Violations written to `stg.dq_rejections` with rule ID, offending FK column, unresolved key value, and `lineage_key`. Load is not blocked; mart promotion proceeds.

---

### DQR-003 — Orphaned Key Detection

**ID:** DQR-003 · **Severity:** Informational

**Description:** Rows in `fact.purchase` where any of `supplier_key`, `stock_item_key`, or `date_key` carries a value of `0` or `NULL` are flagged as orphaned key occurrences requiring review.

**Acceptance Criteria:**
- Every fact row is inspected for FK values equal to `0` or `NULL` across all three FK columns.
- Orphaned key occurrences are written to `stg.dq_rejections` with column name, key value, and `lineage_key`.

**Violation Handling:** Do not block load or mart promotion. Flagged rows retained in `fact.purchase` for downstream analysis.

---

### DQR-004 — DQ Rejection Logging

**ID:** DQR-004 · **Severity:** Blocking (logging mechanism itself must not fail)

**Description:** Every DQ failure detected by DQR-001 through DQR-006 must be written to `stg.dq_rejections`.

**Required Rejection Record Attributes:**

| Attribute | Description |
|---|---|
| `dq_rule_id` | Identifier of the DQR that fired |
| `batch_id` | Batch or load window identifier |
| `lineage_key` | FK to the lineage tracking table |
| `affected_column` | Column or FK that triggered the violation |
| `observed_value` | The value that caused the failure |
| `expected_condition` | Human-readable statement of the violated condition |
| `severity` | `BLOCKING` or `Informational` |
| `recorded_at` | Timestamp of rejection insert |

**Acceptance Criteria:**
- Every DQ assertion that detects a violation writes at least one record to `stg.dq_rejections` before the pipeline proceeds or halts.
- A failure to write a rejection record is itself a blocking pipeline error.

---

### DQR-005 — DQ Assertion Ordering Guarantee

**ID:** DQR-005 · **Severity:** BLOCKING

**Description:** All DQ assertions must complete and their results written to `stg.dq_rejections` before any mart view refresh or reporting layer promotion is triggered.

**Acceptance Criteria:**
- The pipeline DAG enforces an explicit dependency: mart promotion tasks depend on completion of all DQ assertion tasks.
- Any blocking DQ failure terminates the pipeline before the mart promotion task is scheduled.
- Informational DQ failures allow mart promotion to proceed but must be fully logged first.

---

### DQR-006 — No Null lineage_key in Fact Rows

**ID:** DQR-006 · **Severity:** BLOCKING

**Description:** Every row inserted into `fact.purchase` must carry a non-null `lineage_key` that resolves to a valid record in the lineage tracking table. Zero tolerance.

**Acceptance Criteria:**
- After each batch load, `COUNT(*) WHERE lineage_key IS NULL = 0` in `fact.purchase` for rows inserted in the current batch.
- The check runs as part of the DQ assertion suite (after load, before mart promotion).

**Violation Handling:** Blocking pipeline halt. Affected rows identified by batch identifier and written to `stg.dq_rejections` using `purchase_key` or source natural key as fallback reference. Null `lineage_key` rows must not be promoted to the mart.

---

### DQR Summary Table

| ID | Title | Severity | Blocks Load | Blocks Mart Promotion |
|---|---|---|---|---|
| DQR-001 | Row Count Reconciliation | BLOCKING | Yes | Yes |
| DQR-002 | FK Referential Integrity | Informational | No | No |
| DQR-003 | Orphaned Key Detection | Informational | No | No |
| DQR-004 | DQ Rejection Logging | BLOCKING (mechanism) | Yes (if write fails) | Yes (if write fails) |
| DQR-005 | DQ Assertion Ordering Guarantee | BLOCKING | N/A | Yes |
| DQR-006 | No Null lineage_key in fact.purchase | BLOCKING | Yes | Yes |

---

*Generated by migVisor SmartBuilder · 2026-08-25*
