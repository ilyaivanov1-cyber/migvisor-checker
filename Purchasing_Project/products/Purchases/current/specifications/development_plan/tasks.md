# Purchases — Implementation Tasks
_Generated: 2026-09-22 | Pipeline stage: tasks_

---

## Task Summary

| Task ID | Type | Title | Depends On | Requirements |
|---|---|---|---|---|
| TASK-001 | DDL | Create `purchasing.stg.purchase_staging` | none | FR-001 |
| TASK-002 | DDL | Create `purchasing.dim.supplier` (SCD2) | none | FR-002 |
| TASK-003 | DDL | Establish cross-catalog access to `purchasing.dim.stock_item` / `purchasing.dim.date` | none | FR-003 |
| TASK-004 | DDL | Create `purchasing.meta.lineage` | none | FR-005 |
| TASK-005 | DDL | Create `purchasing.meta.sequence_state` | none | FR-005 |
| TASK-006 | DDL | Create `purchasing.meta.etl_cutoff` and `purchasing.meta.v_etl_cutoff` | none | FR-001, FR-008 |
| TASK-007 | DDL | Create `purchasing.fact.purchase` | TASK-002, TASK-003, TASK-004 | FR-004, FR-005, FR-006 |
| TASK-008 | DDL | Create `purchasing.stg.dq_rejections` | TASK-004 | NFR-006 |
| TASK-009 | ETL | Incremental extraction into `purchase_staging` | TASK-001, TASK-006 | FR-001 |
| TASK-010 | ETL | Resolve `supplier_key` via valid-time lookup | TASK-002, TASK-009 | FR-002 |
| TASK-011 | ETL | Resolve `stock_item_key` via valid-time lookup | TASK-003, TASK-009 | FR-003 |
| TASK-012 | ETL | Compute `ordered_quantity` | TASK-009 | FR-004 |
| TASK-013 | ETL | Assign `lineage_key` to the batch | TASK-004, TASK-005, TASK-009 | FR-005 |
| TASK-014 | ETL | Delta MERGE load into `fact.purchase` | TASK-007, TASK-010, TASK-011, TASK-012, TASK-013 | FR-006 |
| TASK-015 | ETL | Advance `etl_cutoff` watermark | TASK-006, TASK-014 | FR-008 |
| TASK-016 | API | Output access profile for `fact.purchase` | TASK-007 | FR-007 |
| TASK-017 | test | QV-001 row-count reconciliation assertion | TASK-014 | NFR-004 |
| TASK-018 | test | QV-002 unknown-key fallback-rate monitoring | TASK-010, TASK-011 | NFR-005 |
| TASK-019 | test | QV-003 referential conformity assertions | TASK-008, TASK-014 | NFR-006 |
| TASK-020 | config | Orchestrate the end-to-end Workflow job chain | TASK-009, TASK-010, TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-017, TASK-018, TASK-019 | FR-001, FR-008 |
| TASK-021 | config | Apply access control and governance to `fact.purchase` | TASK-007, TASK-016 | NFR-003 |
| TASK-022 | BI | Validate cross-catalog consumer access to `fact.purchase` | TASK-016, TASK-021 | FR-007 |
| TASK-023 | docs | Data dictionary and consumer guide | TASK-007, TASK-016, TASK-022 | FR-007 |

**Total: 23 tasks** (DDL 8, ETL 7, API 1, test 3, config 2, BI 1, docs 1)

---

## Task Details

### TASK-001: Create `purchasing.stg.purchase_staging`
- **ID:** TASK-001
- **Type:** DDL
- **Depends On:** none
- **Requirements:** FR-001
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/stg_purchase_staging.sql`
- **Detailed Description:** Create the Delta table `purchasing.stg.purchase_staging` per Design §1.2 Attributes — `purchasing.stg.purchase_staging`, with columns: `wwi_purchase_order_id` BIGINT NOT NULL, `wwi_supplier_id` BIGINT NOT NULL, `wwi_stock_item_id` BIGINT NOT NULL, `transaction_date` DATE NOT NULL, `ordered_outers` BIGINT NOT NULL, `quantity_per_outer` BIGINT NOT NULL, `received_outers` BIGINT NULL, `last_modified_when` TIMESTAMP NOT NULL, `lineage_key` BIGINT NOT NULL. This is a transient, write-once-read-once landing table (Design §1.4 Indexes and Partitioning) — no partitioning, clustering, or Change Data Feed is applied.
- **Acceptance Criteria:**
  - Table exists at `purchasing.stg.purchase_staging` with the exact column set and types listed above
  - DDL is idempotent (`CREATE TABLE IF NOT EXISTS`)
  - No partitioning or Z-ORDER clustering is defined on this table

---

### TASK-002: Create `purchasing.dim.supplier` (SCD2)
- **ID:** TASK-002
- **Type:** DDL
- **Depends On:** none
- **Requirements:** FR-002
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/dim_supplier.sql`
- **Detailed Description:** Create the Delta table `purchasing.dim.supplier` per Design §1.2 Attributes — `purchasing.dim.supplier`, with columns: `supplier_key` BIGINT NOT NULL (surrogate PK), `wwi_supplier_id` BIGINT NOT NULL (business key), `supplier_name` STRING NOT NULL, `category` STRING NULL, `valid_from` TIMESTAMP NOT NULL, `valid_to` TIMESTAMP NOT NULL, `is_current` BOOLEAN NOT NULL. Apply the clustering key `(wwi_supplier_id, valid_from)` per Design §1.4 Indexes and Partitioning to support valid-time range-join lookups. Seed the table with a single Unknown row: `supplier_key = 0`, `wwi_supplier_id = -1`, `supplier_name = 'Unknown'`, `valid_from` = minimum representable timestamp, `valid_to` = maximum representable timestamp, `is_current = true`.
- **Acceptance Criteria:**
  - Table exists at `purchasing.dim.supplier` with the exact column set and types listed above
  - Clustering key `(wwi_supplier_id, valid_from)` is applied
  - The Unknown row (`supplier_key = 0`) exists and its `valid_from`/`valid_to` window spans all representable dates
  - DDL is idempotent

---

### TASK-003: Establish cross-catalog access to `purchasing.dim.stock_item` / `purchasing.dim.date`
- **ID:** TASK-003
- **Type:** DDL
- **Depends On:** none
- **Requirements:** FR-003
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/dim_stock_item_access.sql`
  - `products/Purchases/current/codebase/src/db/ddl/dim_date_access.sql`
- **Detailed Description:** Establish read access for `purchasing.dim.stock_item` and `purchasing.dim.date` per Design §2 Ingestion, rows 3–4. `[OWNER INPUT REQUIRED — cross-catalog sharing mechanism pending PL-008/OB-002]`: implement as a Unity Catalog cross-catalog `GRANT SELECT` against the existing `globalsales.dim.stock_item` / `globalsales.dim.date` tables, or as an independently duplicated and maintained copy under `purchasing.dim.stock_item` / `purchasing.dim.date` — whichever mechanism is confirmed. Both scripts must be written so that only the object reference (grant statement vs. `CREATE TABLE ... AS SELECT` mirror) needs to change once PL-008/OB-002 is resolved; downstream tasks (TASK-011, TASK-018) address `purchasing.dim.stock_item` and `purchasing.dim.date` by name regardless of which mechanism is chosen. Until resolved, stub both scripts with the duplicated-copy path (`CREATE TABLE IF NOT EXISTS purchasing.dim.stock_item ... ` / `... purchasing.dim.date ...`) mirroring the attribute set in Design §1.2, and mark each with an inline `-- [PENDING: PL-008/OB-002]` comment.
- **Acceptance Criteria:**
  - `purchasing.dim.stock_item` and `purchasing.dim.date` are queryable by fully-qualified name from the `purchasing` catalog
  - Both scripts carry an inline `[PENDING: PL-008/OB-002]` marker
  - Switching mechanisms (grant vs. duplicate) requires no change to any downstream task's SQL

---

### TASK-004: Create `purchasing.meta.lineage`
- **ID:** TASK-004
- **Type:** DDL
- **Depends On:** none
- **Requirements:** FR-005
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/meta_lineage.sql`
- **Detailed Description:** Create the Delta table `purchasing.meta.lineage` per Design §1.2 Attributes — `purchasing.meta.lineage`, with columns: `lineage_key` BIGINT NOT NULL (surrogate PK, issued from `purchasing.meta.sequence_state`), `run_id` STRING NOT NULL, `batch_start` TIMESTAMP NOT NULL, `batch_end` TIMESTAMP NULL, `status` STRING NOT NULL (`RUNNING` | `SUCCESS` | `FAILED`).
- **Acceptance Criteria:**
  - Table exists at `purchasing.meta.lineage` with the exact column set and types listed above
  - `status` is constrained (via CHECK constraint or documented convention) to `RUNNING`, `SUCCESS`, or `FAILED`
  - DDL is idempotent

---

### TASK-005: Create `purchasing.meta.sequence_state`
- **ID:** TASK-005
- **Type:** DDL
- **Depends On:** none
- **Requirements:** FR-005
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/meta_sequence_state.sql`
- **Detailed Description:** Create the Delta counter table `purchasing.meta.sequence_state` referenced in Design §3.1 Calculations (CALC-004). Single-row table with columns `sequence_name` STRING NOT NULL (PK, value `'lineage_key'`), `current_value` BIGINT NOT NULL. Seed with one row: `sequence_name = 'lineage_key'`, `current_value = 0`.
- **Acceptance Criteria:**
  - Table exists at `purchasing.meta.sequence_state` with the exact column set and types listed above
  - Exactly one seed row exists for `sequence_name = 'lineage_key'`
  - Concurrent increments of `current_value` do not produce duplicate values (enforced via atomic `MERGE`/conditional update in TASK-013)

---

### TASK-006: Create `purchasing.meta.etl_cutoff` and `purchasing.meta.v_etl_cutoff`
- **ID:** TASK-006
- **Type:** DDL
- **Depends On:** none
- **Requirements:** FR-001, FR-008
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/meta_etl_cutoff.sql`
  - `products/Purchases/current/codebase/src/db/ddl/meta_v_etl_cutoff.sql`
- **Detailed Description:** Create the Delta table `purchasing.meta.etl_cutoff` per Design §1.2 Attributes — `purchasing.meta.etl_cutoff`, with columns: `entity_name` STRING NOT NULL (PK), `last_cutoff` TIMESTAMP NOT NULL, `updated_at` TIMESTAMP NOT NULL. Seed with one row: `entity_name = 'purchase_staging'`, `last_cutoff` = minimum representable timestamp, `updated_at` = current timestamp at seed time. Create the view `purchasing.meta.v_etl_cutoff` as `SELECT * FROM purchasing.meta.etl_cutoff` for cutoff/watermark reporting (Design §1.1 Entities).
- **Acceptance Criteria:**
  - Table exists at `purchasing.meta.etl_cutoff` with the exact column set and types listed above, seeded with the `purchase_staging` row
  - View `purchasing.meta.v_etl_cutoff` exists and returns all rows of `purchasing.meta.etl_cutoff`
  - DDL is idempotent

---

### TASK-007: Create `purchasing.fact.purchase`
- **ID:** TASK-007
- **Type:** DDL
- **Depends On:** TASK-002, TASK-003, TASK-004
- **Requirements:** FR-004, FR-005, FR-006
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/fact_purchase.sql`
- **Detailed Description:** Create the Delta table `purchasing.fact.purchase` per Design §1.2 Attributes — `purchasing.fact.purchase`, with columns: `wwi_purchase_order_id` BIGINT NOT NULL (MERGE key, FR-006), `supplier_key` BIGINT NOT NULL (FK → `dim.supplier.supplier_key`), `stock_item_key` BIGINT NOT NULL (FK → `dim.stock_item.stock_item_key`), `date_key` BIGINT NOT NULL (FK → `dim.date.date_key`), `ordered_outers` BIGINT NOT NULL, `quantity_per_outer` BIGINT NOT NULL, `ordered_quantity` BIGINT NOT NULL (stored, not generated — no `GENERATED ALWAYS AS` clause, per FR-004), `received_outers` BIGINT NULL, `lineage_key` BIGINT NOT NULL (FK → `meta.lineage.lineage_key`). Apply `PARTITIONED BY (date_key)` and Z-ORDER on `(supplier_key, stock_item_key)` per Design §1.4 Indexes and Partitioning. Enable Change Data Feed (`delta.enableChangeDataFeed = true`).
- **Acceptance Criteria:**
  - Table exists at `purchasing.fact.purchase` with the exact column set and types listed above
  - `ordered_quantity` column definition contains no `GENERATED ALWAYS AS` clause
  - Table is partitioned by `date_key` and Z-ORDERed on `(supplier_key, stock_item_key)`
  - Change Data Feed is enabled
  - DDL is idempotent

---

### TASK-008: Create `purchasing.stg.dq_rejections`
- **ID:** TASK-008
- **Type:** DDL
- **Depends On:** TASK-004
- **Requirements:** NFR-006
- **Deliverables:**
  - `products/Purchases/current/codebase/src/db/ddl/stg_dq_rejections.sql`
- **Detailed Description:** Create the Delta table `purchasing.stg.dq_rejections` per Design §1.2 Attributes — `purchasing.stg.dq_rejections`, with columns: `rejection_id` BIGINT NOT NULL (surrogate PK), `lineage_key` BIGINT NOT NULL (FK → `meta.lineage.lineage_key`), `assertion_id` STRING NOT NULL (e.g. `QA-003`), `source_table` STRING NOT NULL, `source_key` BIGINT NULL, `rejection_reason` STRING NOT NULL, `rejected_at` TIMESTAMP NOT NULL.
- **Acceptance Criteria:**
  - Table exists at `purchasing.stg.dq_rejections` with the exact column set and types listed above
  - DDL is idempotent

---

### TASK-009: Incremental extraction into `purchase_staging`
- **ID:** TASK-009
- **Type:** ETL
- **Depends On:** TASK-001, TASK-006
- **Requirements:** FR-001
- **Deliverables:**
  - `products/Purchases/current/codebase/src/etl/extract_purchase_staging.py`
- **Detailed Description:** Implement the incremental extraction notebook/job per Design §2 Ingestion, row 1 and §3.2 Filters (FLT-001). Read the current watermark from `purchasing.meta.etl_cutoff` where `entity_name = 'purchase_staging'`. Extract only source rows where `last_modified_when > :prior_cutoff AND last_modified_when <= :new_cutoff`, where `:new_cutoff` is the extraction run's start timestamp. Write the extracted rows into `purchasing.stg.purchase_staging`, truncating any prior batch contents first (transient table, per Design §1.4).
- **Acceptance Criteria:**
  - 100% of rows with `last_modified_when` in `(:prior_cutoff, :new_cutoff]` are present in `purchasing.stg.purchase_staging` after the run
  - No row outside that window is present
  - The job accepts `:prior_cutoff` and `:new_cutoff` as parameters and does not hard-code watermark values

---

### TASK-010: Resolve `supplier_key` via valid-time lookup
- **ID:** TASK-010
- **Type:** ETL
- **Depends On:** TASK-002, TASK-009
- **Requirements:** FR-002
- **Deliverables:**
  - `products/Purchases/current/codebase/src/etl/resolve_supplier_key.py`
- **Detailed Description:** Implement supplier key resolution per Design §3.1 Calculations (CALC-002). For every row in `purchasing.stg.purchase_staging`, join to `purchasing.dim.supplier` where `dim.supplier.wwi_supplier_id = stg.purchase_staging.wwi_supplier_id AND stg.purchase_staging.transaction_date >= dim.supplier.valid_from AND stg.purchase_staging.transaction_date < dim.supplier.valid_to`. Set `supplier_key` to the matched `dim.supplier.supplier_key`; if no match is found, set `supplier_key = 0` (Unknown). Persist the resolved `supplier_key` alongside the staged row for TASK-014 to consume.
- **Acceptance Criteria:**
  - For every staged row, the resolved `supplier_key` equals the surrogate key of the `dim.supplier` row whose valid-time window contains the row's `transaction_date`, or `0` if none exists
  - Verified for 100% of rows in the batch

---

### TASK-011: Resolve `stock_item_key` via valid-time lookup
- **ID:** TASK-011
- **Type:** ETL
- **Depends On:** TASK-003, TASK-009
- **Requirements:** FR-003
- **Deliverables:**
  - `products/Purchases/current/codebase/src/etl/resolve_stock_item_key.py`
- **Detailed Description:** Implement stock item key resolution per Design §3.1 Calculations (CALC-003), mirroring TASK-010's pattern against `purchasing.dim.stock_item`: join on `dim.stock_item.wwi_stock_item_id = stg.purchase_staging.wwi_stock_item_id AND stg.purchase_staging.transaction_date >= dim.stock_item.valid_from AND stg.purchase_staging.transaction_date < dim.stock_item.valid_to`, falling back to `stock_item_key = 0` when unresolved. This task reads `purchasing.dim.stock_item` via whichever access mechanism TASK-003 established; no change to this task's join logic is required regardless of which mechanism was chosen.
- **Acceptance Criteria:**
  - For every staged row, the resolved `stock_item_key` equals the surrogate key of the `dim.stock_item` row whose valid-time window contains the row's `transaction_date`, or `0` if none exists
  - Verified for 100% of rows in the batch

---

### TASK-012: Compute `ordered_quantity`
- **ID:** TASK-012
- **Type:** ETL
- **Depends On:** TASK-009
- **Requirements:** FR-004
- **Deliverables:**
  - `products/Purchases/current/codebase/src/etl/compute_ordered_quantity.py`
- **Detailed Description:** Implement the ordered quantity calculation per Design §3.1 Calculations (CALC-001): `ordered_quantity = ordered_outers * quantity_per_outer`, computed in the transformation step and stored as a materialized column value (not via a `GENERATED ALWAYS AS` DDL clause) when the row is written to `purchasing.fact.purchase` in TASK-014.
- **Acceptance Criteria:**
  - For 100% of rows processed, the computed `ordered_quantity` equals `ordered_outers * quantity_per_outer`
  - The calculation is performed in transformation code, not in a generated-column DDL expression

---

### TASK-013: Assign `lineage_key` to the batch
- **ID:** TASK-013
- **Type:** ETL
- **Depends On:** TASK-004, TASK-005, TASK-009
- **Requirements:** FR-005
- **Deliverables:**
  - `products/Purchases/current/codebase/src/etl/assign_lineage_key.py`
- **Detailed Description:** Implement lineage key issuance per Design §3.1 Calculations (CALC-004) and §5.1 Lineage Tracking. At batch start, insert a `purchasing.meta.lineage` row with `status = 'RUNNING'` and a newly issued `lineage_key` obtained by atomically incrementing `purchasing.meta.sequence_state.current_value` where `sequence_name = 'lineage_key'` (read-increment-write via conditional `MERGE` to avoid race conditions). Stamp this `lineage_key` on every row of the current batch. At batch end, update the `purchasing.meta.lineage` row's `status` to `SUCCESS` or `FAILED` and set `batch_end`.
- **Acceptance Criteria:**
  - Every row processed in the batch carries the same non-null `lineage_key`, which resolves to a `purchasing.meta.lineage` row for this run
  - `purchasing.meta.sequence_state.current_value` never issues the same `lineage_key` twice, including under concurrent runs
  - The `purchasing.meta.lineage` row's `status` transitions from `RUNNING` to `SUCCESS` or `FAILED` by the end of the run

---

### TASK-014: Delta MERGE load into `fact.purchase`
- **ID:** TASK-014
- **Type:** ETL
- **Depends On:** TASK-007, TASK-010, TASK-011, TASK-012, TASK-013
- **Requirements:** FR-006
- **Deliverables:**
  - `products/Purchases/current/codebase/src/etl/merge_fact_purchase.py`
- **Detailed Description:** Implement the scoped Delta MERGE per Design §3.1/§1.2 and FR-006. `MERGE INTO purchasing.fact.purchase AS target USING <resolved_batch> AS source ON target.wwi_purchase_order_id = source.wwi_purchase_order_id`, scoped to the set of `wwi_purchase_order_id` values present in the current batch (`WHEN MATCHED THEN UPDATE SET *`, `WHEN NOT MATCHED THEN INSERT *`). Rows for `wwi_purchase_order_id` values not present in the batch must remain byte-identical. The `source` dataset carries `supplier_key` (TASK-010), `stock_item_key` (TASK-011), `ordered_quantity` (TASK-012), and `lineage_key` (TASK-013) already resolved.
- **Acceptance Criteria:**
  - After a run, rows for any `wwi_purchase_order_id` present in the batch exactly match the batch's resolved data
  - Rows for purchase orders absent from the batch are byte-identical to their pre-run state
  - The MERGE statement is scoped to the batch's `wwi_purchase_order_id` set (not a full-table scan comparison)

---

### TASK-015: Advance `etl_cutoff` watermark
- **ID:** TASK-015
- **Type:** ETL
- **Depends On:** TASK-006, TASK-014
- **Requirements:** FR-008
- **Deliverables:**
  - `products/Purchases/current/codebase/src/etl/advance_etl_cutoff.py`
- **Detailed Description:** Implement watermark bookkeeping per Design §5.3 Monitoring and Alerting and FR-008. After TASK-014's MERGE commits successfully and after QV-001 (TASK-017) passes, update `purchasing.meta.etl_cutoff` where `entity_name = 'purchase_staging'`, setting `last_cutoff` to the run's `:new_cutoff` value and `updated_at` to the current timestamp. If the MERGE or QV-001 does not succeed, this task must not run and the watermark must not advance.
- **Acceptance Criteria:**
  - Each successful, fully-validated run advances `purchasing.meta.etl_cutoff.last_cutoff` to the newly processed batch's upper bound
  - No watermark advance occurs on a failed or QV-001-failed run

---

### TASK-016: Output access profile for `fact.purchase`
- **ID:** TASK-016
- **Type:** API
- **Depends On:** TASK-007
- **Requirements:** FR-007
- **Deliverables:**
  - `products/Purchases/current/codebase/src/api/fact_purchase_access_profile.sql`
- **Detailed Description:** Implement the output access profile per Design §4 Serving. `[OWNER INPUT REQUIRED — cross-catalog exposure mechanism pending PL-009/OB-008]`: implement as a Unity Catalog cross-catalog `GRANT SELECT ON TABLE purchasing.fact.purchase TO <consumer-role>`, or as a federated/replicated read-only copy exposed to `globalsales`, whichever mechanism is confirmed. This is the sole access path for the three known cross-catalog consumers (Design §4, row 1) — no purchase-exclusive mart view is owned by this product.
- **Acceptance Criteria:**
  - `purchasing.fact.purchase` is readable by the three known cross-catalog consumers through the implemented access profile
  - The script carries an inline `[PENDING: PL-009/OB-008]` marker until the mechanism is confirmed

---

### TASK-017: QV-001 row-count reconciliation assertion
- **ID:** TASK-017
- **Type:** test
- **Depends On:** TASK-014
- **Requirements:** NFR-004
- **Deliverables:**
  - `products/Purchases/current/codebase/tests/test_qv001_row_count_reconciliation.py`
- **Detailed Description:** Implement QV-001 per Design §5.2 Validation Rules. After TASK-014's MERGE, assert that the count of distinct `wwi_purchase_order_id` values in the staged batch (`purchasing.stg.purchase_staging`) exactly equals the count of matching rows reflected in `purchasing.fact.purchase`. On mismatch, raise a blocking failure that prevents TASK-015 from advancing the watermark and writes an alert.
- **Acceptance Criteria:**
  - Any mismatch between staged and post-load distinct `wwi_purchase_order_id` counts blocks the run before the watermark advances
  - A passing assertion allows TASK-015 to proceed

---

### TASK-018: QV-002 unknown-key fallback-rate monitoring
- **ID:** TASK-018
- **Type:** test
- **Depends On:** TASK-010, TASK-011
- **Requirements:** NFR-005
- **Deliverables:**
  - `products/Purchases/current/codebase/tests/test_qv002_unknown_key_fallback_rate.py`
- **Detailed Description:** Implement QV-002 per Design §5.2 Validation Rules. Compute the rate of rows in the current batch where `supplier_key = 0` or `stock_item_key = 0` (Unknown fallback), and compare against a rolling historical baseline. `[OWNER INPUT REQUIRED — threshold pending QA-002]`: the comparison threshold is not yet business-confirmed; implement the metric computation and emit it as a non-blocking monitoring alert regardless of the pending threshold.
- **Acceptance Criteria:**
  - The fallback rate for the batch is computed and recorded for every run
  - The check never blocks the run (non-blocking), pending QA-002 threshold confirmation

---

### TASK-019: QV-003 referential conformity assertions
- **ID:** TASK-019
- **Type:** test
- **Depends On:** TASK-008, TASK-014
- **Requirements:** NFR-006
- **Deliverables:**
  - `products/Purchases/current/codebase/tests/test_qv003_referential_conformity.py`
- **Detailed Description:** Implement QV-003 per Design §5.2 Validation Rules. After TASK-014's MERGE, run LEFT ANTI JOIN assertions of `purchasing.fact.purchase` against `purchasing.dim.supplier`, `purchasing.dim.stock_item`, and `purchasing.dim.date` on `supplier_key`, `stock_item_key`, and `date_key` respectively. Any row failing to resolve is written to `purchasing.stg.dq_rejections` with `assertion_id = 'QA-003'`, `source_table = 'purchasing.fact.purchase'`, `source_key = wwi_purchase_order_id`, and the current run's `lineage_key`. This check is non-blocking.
- **Acceptance Criteria:**
  - Zero orphaned foreign keys are permitted to pass undetected
  - Any row failing the referential-integrity assertion is written to `purchasing.stg.dq_rejections` within the same run
  - The check does not block the run

---

### TASK-020: Orchestrate the end-to-end Workflow job chain
- **ID:** TASK-020
- **Type:** config
- **Depends On:** TASK-009, TASK-010, TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-017, TASK-018, TASK-019
- **Requirements:** FR-001, FR-008
- **Deliverables:**
  - `products/Purchases/current/codebase/config/purchase_pipeline_workflow.yml`
- **Detailed Description:** Configure the Databricks Workflows job chain per Design §5.3 Monitoring and Alerting and the orchestration sequence: extraction (TASK-009) → key resolution (TASK-010, TASK-011) → calculations (TASK-012, TASK-013) → MERGE load (TASK-014) → QV-001/QV-002/QV-003 (TASK-017/018/019) → watermark advance (TASK-015). QV-001 failure must halt the chain before the watermark-advance task runs; QV-002 and QV-003 failures must not halt the chain.
- **Acceptance Criteria:**
  - The job chain runs all tasks in the dependency order listed above
  - A QV-001 failure prevents the watermark-advance step from executing
  - QV-002/QV-003 failures allow the chain to complete

---

### TASK-021: Apply access control and governance to `fact.purchase`
- **ID:** TASK-021
- **Type:** config
- **Depends On:** TASK-007, TASK-016
- **Requirements:** NFR-003
- **Deliverables:**
  - `products/Purchases/current/codebase/config/fact_purchase_governance.sql`
- **Detailed Description:** Configure Unity Catalog governance for `purchasing.fact.purchase` per Design §4 Serving and NFR-003. `[OWNER INPUT REQUIRED — access role matrix and row/column-level security policy pending]`: apply the confirmed role/permission matrix once available. Until confirmed, scaffold the grant script with placeholder role names marked `-- [PENDING: role matrix]`, so only the role identifiers need to change once the matrix is finalized.
- **Acceptance Criteria:**
  - A governance script exists and applies without error against `purchasing.fact.purchase`
  - Role identifiers are isolated to a single, clearly marked section pending confirmation

---

### TASK-022: Validate cross-catalog consumer access to `fact.purchase`
- **ID:** TASK-022
- **Type:** BI
- **Depends On:** TASK-016, TASK-021
- **Requirements:** FR-007
- **Deliverables:**
  - `products/Purchases/current/codebase/tests/test_consumer_access_validation.py`
- **Detailed Description:** Validate that the three known cross-catalog consumers (Design §4 Serving, row 1) can read `purchasing.fact.purchase` through the access profile implemented in TASK-016, under the governance rules applied in TASK-021. Run a representative query from a session scoped to the consumer role and confirm rows are returned without direct, ungoverned table access.
- **Acceptance Criteria:**
  - A query executed under the consumer role successfully reads `purchasing.fact.purchase` via the access profile
  - No consumer requires direct, ungoverned access to the underlying table

---

### TASK-023: Data dictionary and consumer guide
- **ID:** TASK-023
- **Type:** docs
- **Depends On:** TASK-007, TASK-016, TASK-022
- **Requirements:** FR-007
- **Deliverables:**
  - `products/Purchases/current/codebase/docs/data_dictionary.md`
  - `products/Purchases/current/codebase/docs/consumer_guide.md`
- **Detailed Description:** Author the data dictionary covering every column of `purchasing.fact.purchase`, `purchasing.dim.supplier`, `purchasing.dim.stock_item`, and `purchasing.dim.date` (names, types, descriptions, per Design §1.2 Attributes), and the consumer guide describing how to obtain read access via the profile implemented in TASK-016 and the governance rules in TASK-021.
- **Acceptance Criteria:**
  - Every column listed in Design §1.2 Attributes for the four documented entities appears in the data dictionary with name, type, and description
  - The consumer guide documents the access mechanism confirmed in TASK-016

---
