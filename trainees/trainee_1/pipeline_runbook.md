# Pipeline Runbook — Sales_Orders / nightly_etl_main
_TASK-DOCS-001_

## Overview

`nightly_etl_main` runs nightly at 02:00 UTC and must complete by 06:00 UTC (4-hour SLA).

---

## Manual backfill (watermark override)

To re-process data for a specific date range:

1. Update `stg.etl_cutoff` to the desired start of the re-extraction window:
   ```sql
   UPDATE globalsales.stg.etl_cutoff
   SET last_cutoff_utc = '2024-01-01T00:00:00Z', updated_at_utc = current_timestamp()
   WHERE entity_name = 'sale';
   -- Repeat for: order, customer, city, stock_item, employee, payment_method, transaction_type
   ```
2. Trigger the workflow manually from the Databricks UI or CLI:
   ```bash
   databricks jobs run-now --job-id <nightly_etl_main_job_id>
   ```
3. Monitor progress in `stg.lineage`.

---

## Re-running a failed pipeline stage

Each notebook can be re-run independently:

| Stage | Notebook path | Notes |
|---|---|---|
| Extract watermark | `.../ingestion/nb_extract_watermark` | Safe to re-run — read-only |
| Extract sales | `.../ingestion/nb_extract_sales` | Truncate-before-load — idempotent |
| Extract orders | `.../ingestion/nb_extract_orders` | Truncate-before-load — idempotent |
| Extract dimensions | `.../ingestion/nb_extract_dimensions` | Read-only extract |
| Dimension SCD2 | `.../dimensions/nb_orchestrate_dimensions` | SCD2 MERGE is idempotent |
| Fact loads | `.../facts/nb_orchestrate_facts` | Delta MERGE is idempotent |
| DQ fact.sale | `.../dq/nb_dq_fact_sale` | Re-run clears and re-writes rejections |
| DQ fact.order | `.../dq/nb_dq_fact_order` | Re-run clears and re-writes rejections |
| Commit watermark | `.../ingestion/nb_commit_watermark` | **Only run after all loads succeed** |
| Mart refresh | `.../mart/nb_refresh_v_customer_sales_summary` | Safe to re-run |
| Smoke tests | `.../dq/nb_dq_smoke_tests` | Safe to re-run |

---

## Clearing and re-processing stg.dq_rejections

```sql
-- View rejections for a specific run
SELECT * FROM globalsales.stg.dq_rejections WHERE lineage_key = <lineage_key>;

-- Clear rejections for a specific run after investigation
DELETE FROM globalsales.stg.dq_rejections WHERE lineage_key = <lineage_key>;
```

To re-inject corrected rows, insert them into the appropriate staging table and re-trigger the fact load and DQ notebooks for that lineage batch.

---

## Monitoring stg.lineage

```sql
-- Last 7 days of pipeline runs
SELECT pipeline_run_id, batch_start_utc, batch_end_utc,
       TIMESTAMPDIFF(MINUTE, batch_start_utc, batch_end_utc) AS runtime_min,
       rows_extracted, rows_loaded, rows_rejected, status
FROM globalsales.stg.lineage
WHERE batch_start_utc >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY batch_start_utc DESC;
```

---

## Troubleshooting decision tree

### 1. Source extraction failure (nb_extract_sales / nb_extract_orders)
- Check `source_jdbc_url` secret is set: `databricks secrets list --scope globalsales`
- [PENDING: CX-P04] Confirm OLTP connection strategy is finalised
- Check source system availability

### 2. DQ gate failure (nb_dq_fact_sale / nb_dq_fact_order)
- Query `stg.dq_rejections` for the failing `lineage_key`
- Identify `assertion_id` and `rejection_reason`
- [PENDING: CX-DQ-01] Check if zero-tolerance threshold should be relaxed
- Fix source data or correction procedure; re-run from fact load

### 3. Merge timeout (fact or dimension notebooks)
- Check cluster auto-scaling — may need larger node type
- Run `OPTIMIZE` on target table before re-running merge
- For fact.sale: liquid clustering may need maintenance run

### 4. Watermark corruption
- Query `stg.etl_cutoff` — verify `last_cutoff_utc` is reasonable
- If corrupted, reset to last known good cutoff (see Manual Backfill above)
- Do NOT advance watermark past the current batch start without a successful load

### 5. Mart view unavailability
- Check `mart.v_customer_sales_summary` was refreshed: query it directly
- Re-run `nb_refresh_v_customer_sales_summary`
- Check SQL Warehouse is running and not auto-terminated
