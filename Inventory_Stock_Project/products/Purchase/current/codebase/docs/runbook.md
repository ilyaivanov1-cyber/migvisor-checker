# Runbook — Purchase ETL Product

---

## 0. Daily Monitoring Checklist

Run each morning after the nightly pipeline (expected completion by ~03:00 UTC):

- [ ] Check Databricks Workflow run status: `nightly_etl_purchase` — confirm `Succeeded` in the Jobs UI
- [ ] Verify `bronze.lineage_run` latest row has `was_successful = true`
- [ ] Verify alert inbox — no failure emails or Slack alerts from the monitoring webhook
- [ ] Spot-check `silver_dim.supplier` and `silver_dim.stock_item` for expected row counts (Dimensions team dependency)
- [ ] Confirm `bronze.etl_cutoff.cutoff_time` for `table_name = 'fact_purchase'` advanced since yesterday
- [ ] Confirm `silver_fact.fact_purchase` row count is consistent with expected daily batch size

**Quick lineage query:**
```sql
SELECT lineage_key, pipeline_name, data_load_started, data_load_completed,
       was_successful, table_row_count, source_system_cutoff_time
FROM inventory_stock.bronze.lineage_run
WHERE table_name = 'fact_purchase'
ORDER BY data_load_started DESC
LIMIT 5;
```

**Watermark check:**
```sql
SELECT table_name, cutoff_time, last_updated_utc
FROM inventory_stock.bronze.etl_cutoff
WHERE table_name = 'fact_purchase';
```

---

**Project:** Inventory_Stock_Project  
**Product:** Purchase  
**Target:** `inventory_stock` Unity Catalog (Databricks Delta Lake)  
**Workflow:** `nightly_etl_purchase` — runs at 02:00 UTC, halt-and-alert policy

---

## 1. Normal Operations

### 1.1 Scheduled Run

The Databricks Workflow `nightly_etl_purchase` runs automatically at 02:00 UTC each night.

Task execution order:
```
nb_extract_watermark  →  nb_extract_purchase  →  migrate_staged_purchase_data
```

Monitor in the Databricks Workflows UI. On success, `bronze.lineage_run` will contain a new row where `was_successful = true`.

### 1.2 Manual Trigger

To trigger outside the schedule (e.g., after a source-side data fix):

1. Open the Databricks Workspace for the `inventory_stock` environment.
2. Navigate to **Workflows → nightly_etl_purchase**.
3. Click **Run now**.
4. Confirm the triggered run appears in the **Runs** tab with status `Running`.

No parameter overrides are needed for a standard re-run — the watermark is read from `bronze.etl_cutoff` automatically.

---

## 2. Failure Recovery

### 2.1 General Approach

The pipeline uses a **halt-and-alert** policy. On any task failure:
- Databricks stops all downstream tasks in the run.
- An alert is sent to the configured notification channel.
- The `bronze.lineage_run` record for the failed run is closed with `was_successful = false`.

To recover, identify the failed task in the Runs tab and follow the section below for that task.

---

### 2.2 `nb_extract_watermark` Failed

**Symptom:** Run fails at the first task; no data was extracted.

**Steps:**
1. Check the task logs for connection or table errors.
2. Verify `bronze.etl_cutoff` exists and contains a row for `purchase_staging`:
   ```sql
   SELECT * FROM inventory_stock.bronze.etl_cutoff WHERE source_table = 'purchase_staging';
   ```
3. If the row is missing, re-run `reseed_purchase_environment.py` (requires PD-002 sign-off — see Pending Decisions).
4. After the root cause is fixed, **Run now** from the Workflows UI.

---

### 2.3 `nb_extract_purchase` Failed

**Symptom:** Watermark task succeeded; extract task failed. May be a JDBC connectivity issue (PD-001 pending).

**Steps:**
1. Check task logs for JDBC connection errors, SSL errors, or timeout messages.
2. Verify the SQL Server source is reachable and credentials are valid (see `config/environment.yaml` — `purchase.etl.jdbc_*` keys).
3. If the connection is healthy, check for schema changes on `integration.purchase_staging` in the source.
4. A partial write to `bronze.purchase_staging` may have occurred. The table is overwritten each run, so a clean re-run is safe.
5. Check `bronze.lineage_run` for the failed run:
   ```sql
   SELECT * FROM inventory_stock.bronze.lineage_run ORDER BY data_load_started DESC LIMIT 5;
   ```
6. The failed lineage record already has `was_successful = false`. No manual cleanup is needed.
7. After fixing the root cause, **Run now**.

---

### 2.4 `migrate_staged_purchase_data` Failed — QA-P001 RuntimeError

**Symptom:** Final task raises `RuntimeError: QA-P001 FAILED — row count mismatch`. This is a **blocking** assertion. The MERGE INTO did not execute.

**Steps:**
1. Check task logs for the staging row count vs. expected count.
2. Review `bronze.purchase_staging` row count:
   ```sql
   SELECT COUNT(*) FROM inventory_stock.bronze.purchase_staging;
   ```
3. Compare against `bronze.lineage_run.table_row_count` from the previous successful run.
4. If staging count is 0, the extract step wrote no rows — re-trigger from `nb_extract_purchase`.
5. If staging count is unexpectedly high (duplicate rows), investigate the JDBC extract predicate in `nb_extract_purchase.py` and the watermark in `bronze.etl_cutoff`.
6. Do **not** manually modify `bronze.purchase_staging` or `bronze.lineage_run` — re-run the full pipeline after fixing the root cause.

---

### 2.5 `migrate_staged_purchase_data` Failed — Other Errors

**Steps:**
1. Check `bronze.dq_rejections` for rows from the current `lineage_key`:
   ```sql
   SELECT rule_id, COUNT(*) AS rejected_rows
   FROM inventory_stock.bronze.dq_rejections
   WHERE lineage_key = <current_lineage_key>
   GROUP BY rule_id;
   ```
2. If QA-P003 (referential integrity) violations are present, check whether `silver_dim.supplier` and `silver_dim.stock_item` have been refreshed by the Dimensions team.
3. After investigating, re-trigger from the failed task using **Repair run** in the Databricks UI, or **Run now** for a full restart.

---

## 3. Surrogate Key Resolution Failure

The `migrate_staged_purchase_data` notebook resolves surrogate keys by joining against:
- `inventory_stock.silver_dim.supplier`
- `inventory_stock.silver_dim.stock_item`

**Critical external dependency:** These tables must be pre-loaded by the Dimensions team before Purchase ETL can succeed.

If SK resolution produces all-null `supplier_key` or `stock_item_key` values:
1. Verify with the Dimensions team that their SCD-2 load has run.
2. Check view freshness:
   ```sql
   SELECT COUNT(*) FROM inventory_stock.silver_dim.supplier_current;
   SELECT COUNT(*) FROM inventory_stock.silver_dim.stock_item_current;
   ```
3. If views return 0 rows, escalate to the Dimensions team — do not proceed with Purchase ETL.

---

## 4. Cutover Checklist

Before running in production for the first time, resolve all Pending Decisions:

| ID | Action Required | Blocks |
|---|---|---|
| **PD-001** | Confirm JDBC driver class, credentials, and Databricks Secret Scope name; update `config/environment.yaml` | `nb_extract_purchase.py` |
| **PD-002** | Obtain scope-owner sign-off for `reseed_purchase_environment.py`; execute in each environment (dev → staging → prod) sequentially | Initial environment seeding |
| **PD-003** | Confirm Unity Catalog role names with the platform team; execute `src/db/grants/purchase_grants.sql` | BI access via `silver_dim` views |
| **QA-DQ-01** | Agree DQ threshold values with business stakeholders; update `config/environment.yaml` `business_rules.*` keys | QA-P004 informational assertion tuning |

**Cutover sequence:**
1. Resolve PD-001 — update `environment.yaml`, test JDBC connectivity from the cluster.
2. Get PD-002 sign-off — run `reseed_purchase_environment.py` to seed `bronze.etl_cutoff`.
3. Run `scripts/deploy_ddl.sh` (or execute DDL files manually) against the target catalog.
4. Verify prerequisites (see README.md § Prerequisites).
5. Confirm Dimensions team has loaded `silver_dim.supplier` and `silver_dim.stock_item`.
6. Trigger `nb_extract_watermark` standalone to verify watermark reads correctly.
7. Trigger full pipeline `nightly_etl_purchase` → verify `bronze.lineage_run` shows `was_successful = true`.
8. Resolve PD-003 — run `purchase_grants.sql` to grant BI access.
9. Resolve QA-DQ-01 — tune business rule thresholds in `environment.yaml`.

---

## 5. DQ Investigation

**Query all violations for a specific run:**
```sql
SELECT rule_id, violation_column, violation_value, rejection_reason, detected_at
FROM inventory_stock.bronze.dq_rejections
WHERE lineage_key = <lineage_key>
ORDER BY detected_at;
```

**Query recent DQ summary across runs:**
```sql
SELECT lr.pipeline_name, lr.data_load_started, dq.rule_id, COUNT(*) AS violations
FROM inventory_stock.bronze.dq_rejections dq
JOIN inventory_stock.bronze.lineage_run lr ON dq.lineage_key = lr.lineage_key
GROUP BY lr.pipeline_name, lr.data_load_started, dq.rule_id
ORDER BY lr.data_load_started DESC;
```

**Common DQ failures and actions:**

| Rule ID | Description | Action |
|---|---|---|
| QA-P001 | Staging/fact count mismatch | Check for MERGE errors; compare `SELECT COUNT(*) FROM bronze.purchase_staging` vs `lineage_run.table_row_count` |
| QA-P002 | Orphaned surrogate key (key=0) | Investigate unresolvable `wwi_supplier_id` or `wwi_stock_item_id`; check if Dimensions team SCD-2 load ran |
| QA-P003 | FK integrity violation | Rows reference dimension keys that don't exist; check dimension load freshness |
| QA-P004 | Business rule violation | Negative quantities or null package field; investigate source data quality |

**Query to find all DQ rejections from the most recent run:**
```sql
SELECT dq.rule_id, dq.pk_column, dq.pk_value, dq.violation_column,
       dq.violation_value, dq.rejection_reason, dq.detected_at
FROM inventory_stock.bronze.dq_rejections dq
WHERE dq.lineage_key = (
    SELECT MAX(lineage_key) FROM inventory_stock.bronze.lineage_run
    WHERE table_name = 'fact_purchase'
)
ORDER BY dq.detected_at;
```

---

## 6. Useful Queries

```sql
-- Last 10 pipeline runs
SELECT lineage_key, pipeline_name, data_load_started, data_load_completed,
       was_successful, table_row_count, source_system_cutoff_time
FROM inventory_stock.bronze.lineage_run
ORDER BY data_load_started DESC
LIMIT 10;

-- Current watermark
SELECT * FROM inventory_stock.bronze.etl_cutoff;

-- DQ rejection summary (last run)
SELECT rule_id, rejection_reason, COUNT(*) AS cnt
FROM inventory_stock.bronze.dq_rejections
WHERE lineage_key = (SELECT MAX(lineage_key) FROM inventory_stock.bronze.lineage_run)
GROUP BY rule_id, rejection_reason
ORDER BY cnt DESC;

-- Fact table row count
SELECT COUNT(*) FROM inventory_stock.silver_fact.fact_purchase;
```

---

## 7. Partial Reprocessing — Watermark Reset

Use this procedure when you need to reprocess a historical date range — for example, after a source-side data correction that altered records outside the most recent batch window.

> **Warning:** Resetting the watermark causes the next pipeline run to re-extract all rows where `last_modified_when > <target_date>`. Verify the source system has the corrected data before resetting. The MERGE INTO pattern is idempotent: re-extracted rows with the same MERGE predicate key `(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)` will UPDATE in place; new rows will INSERT. No duplicates are created.

**Step 1 — Reset the watermark to the target start date:**

```sql
UPDATE inventory_stock.bronze.etl_cutoff
SET cutoff_time     = '<target_start_date>',
    last_updated_utc = current_timestamp()
WHERE table_name = 'fact_purchase';
```

Replace `<target_start_date>` with the earliest date from which you need to reprocess (e.g. `'2026-09-01 00:00:00'`).

**Step 2 — Trigger the full pipeline:**

Navigate to **Workflows → nightly_etl_purchase → Run now** in the Databricks UI. The pipeline extracts all rows where `last_modified_when > <target_start_date>` from the source system.

**Step 3 — Verify reprocessing:**

```sql
-- Confirm the watermark advanced past the reprocessed period
SELECT table_name, cutoff_time, last_updated_utc
FROM inventory_stock.bronze.etl_cutoff
WHERE table_name = 'fact_purchase';

-- Confirm a new successful lineage run exists
SELECT lineage_key, data_load_started, data_load_completed, was_successful, table_row_count
FROM inventory_stock.bronze.lineage_run
WHERE table_name = 'fact_purchase'
ORDER BY data_load_started DESC
LIMIT 3;
```

---

## 8. Escalation Path

| Severity | Condition | Channel | Target Response Time |
|---|---|---|---|
| P1 — Pipeline Blocked | `was_successful = false` AND pipeline not recovered within 2 hours of 02:00 UTC run start | Slack `#data-eng-incidents` + PagerDuty on-call | 30 minutes |
| P2 — DQ Blocking Failure | QA-P001 RuntimeError raised (row count mismatch) — MERGE did not execute; data may be stale | Slack `#data-eng-incidents` | 1 hour |
| P3 — Informational DQ | QA-P003 RI violations or QA-P004 business rule warnings logged but pipeline succeeded | Slack `#data-eng-monitoring` | Next business day |
| P4 — Source Unavailable | JDBC connectivity failure in `nb_extract_purchase` (PD-001 pending); source system unreachable | Slack `#platform-engineering` | 2 hours |
| P5 — Security Incident | Unexpected secret access, Unity Catalog audit alert, credential rotation required | Email `security@company.com` + Slack `#security-incidents` | Immediate |

Escalation owner: Data Engineering Lead — see Contacts section.

---

## 9. Contacts

| Team | Role | Contact |
|---|---|---|
| Data Engineering | Pipeline owner; primary on-call for Purchase ETL failures and DQ incidents | `data-engineering@company.com` / Slack `#data-engineering` |
| Platform Engineering | Databricks cluster, Unity Catalog, Workflow infrastructure, secret scopes | `platform@company.com` / Slack `#platform-engineering` |
| Security / IAM | Secret scope management, service principal credentials, Unity Catalog permission audits | `security@company.com` / Slack `#security-incidents` |
| Dimensions Team | Owns `silver_dim.supplier` and `silver_dim.stock_item` loads (external dependency for Purchase ETL) | `dimensions-team@company.com` / Slack `#dimensions-team` |

> Placeholder contacts — update with actual team aliases before production go-live.
