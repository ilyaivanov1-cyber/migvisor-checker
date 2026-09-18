# Pipeline Runbook: Purchase Data Product

## 1. Daily Monitoring Checklist

Run each morning after the nightly pipeline (expected completion by ~03:00 UTC):

- [ ] Check Databricks Workflow run status: `globalpurchase_nightly_etl_main`
- [ ] Verify `stg.lineage` latest row has `status = 'success'`
- [ ] Verify alert inbox — no failure emails or Slack alerts
- [ ] Spot-check `dim.supplier` and `dim.stock_item` for expected row counts
- [ ] Confirm `stg.etl_cutoff.last_cutoff_time` for `entity_name = 'purchase'` advanced

**Quick lineage query:**
```sql
SELECT pipeline_run_id, started_at, completed_at, status, source_row_count, rows_loaded
FROM globalpurchase.stg.lineage
WHERE entity_name = 'purchase'
ORDER BY started_at DESC
LIMIT 5;
```

---

## 2. Failure Response

### 2.1 Identify the failed task

1. Open the Databricks Workflow run in the Jobs UI.
2. Identify the task with the red failure indicator.
3. Click the task → View logs.

### 2.2 Diagnose the failure

| Failed task | Likely cause | First action |
|---|---|---|
| nb_extract_watermark | etl_cutoff schema missing | Run CFG-003 (uc_setup.sql) |
| nb_extract_dimensions | JDBC credential error | Verify Secrets scope (`globalpurchase-dev`/`prod`) |
| nb_extract_purchase | JDBC timeout / source unavailable | Check source system availability |
| nb_orchestrate_dimensions | SCD-2 MERGE conflict | Check for schema drift in source tables |
| nb_orchestrate_facts | Missing sentinel row | Insert sentinel rows into dim.supplier/dim.stock_item |
| nb_dq_purchase | BLOCKING DQ failure | Query stg.dq_rejections (see §4) |
| nb_commit_watermark | Upstream task failed | Should not run — investigate the actual failing task |

### 2.3 Re-trigger after fix

- Fix the root cause.
- Re-trigger the failed run from the Workflow UI (Repair Run).
- The watermark in `stg.etl_cutoff` is unchanged on failure — re-running re-processes the same window safely.

---

## 3. Partial Reprocessing Guide

To reprocess data for a specific date range:

**Step 1: Reset the watermark**
```sql
-- Set to the start of the desired reprocessing window (UTC timestamp)
UPDATE globalpurchase.stg.etl_cutoff
SET last_cutoff_time = CAST('2026-01-01T00:00:00Z' AS TIMESTAMP)
WHERE entity_name = 'purchase';
```

**Step 2: Trigger the pipeline**
Run the Databricks Workflow manually. It will pick up all source rows since the reset watermark.

**Step 3: Verify**
```sql
SELECT last_cutoff_time FROM globalpurchase.stg.etl_cutoff WHERE entity_name = 'purchase';
-- Confirm the watermark advanced to the expected end of the reprocessed window.
```

> **Warning:** Resetting the watermark to an earlier date re-processes source rows and may produce duplicate MERGE operations. The fact MERGE is idempotent (UPDATE existing rows), so no duplicate fact rows will appear — but lineage will show multiple runs for overlapping windows.

---

## 4. DQ Investigation

**Query all violations for a specific run:**
```sql
SELECT dq_rule_id, affected_column, observed_value, expected_condition, severity, recorded_at
FROM globalpurchase.stg.dq_rejections
WHERE lineage_key = <lineage_key>
ORDER BY recorded_at;
```

**Query recent DQ summary across runs:**
```sql
SELECT l.pipeline_run_id, l.started_at, r.dq_rule_id, r.severity, COUNT(*) AS violations
FROM globalpurchase.stg.dq_rejections r
JOIN globalpurchase.stg.lineage l ON r.lineage_key = l.lineage_key
GROUP BY l.pipeline_run_id, l.started_at, r.dq_rule_id, r.severity
ORDER BY l.started_at DESC;
```

**Common DQ failures:**

| Rule | Description | Action |
|---|---|---|
| DQR-001 | Staging/fact count mismatch | Check for MERGE errors; compare staging and fact row counts manually |
| DQR-002 | FK integrity violations | Rows reference dimensions not found; check for SCD-2 load failures |
| DQR-003 | Sentinel key usage | Normal if source has new/unknown suppliers or stock items; investigate root cause |
| DQR-006 | Null lineage_key | Check ING-003 — lineage_key injection may have failed |

---

## 5. Escalation Path

| Severity | Contact | Channel |
|---|---|---|
| Pipeline failure (blocking) | Data Engineering on-call | Slack #data-oncall or PagerDuty |
| DQ violation (informational) | Data Engineering team | Slack #data-quality |
| Source system unavailable | Platform team | Slack #platform-oncall |
| Security incident | Security team | security@company.com |

---

## 6. Contacts

- Data Engineering lead: data-engineering@company.com
- Platform team: platform@company.com
- Security team: security@company.com
