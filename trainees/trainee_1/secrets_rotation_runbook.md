# Secrets Rotation Runbook — Sales_Orders Pipeline
_TASK-SEC-005 | [PENDING: CX-P04] OLTP credential rotation section_

## Overview

This runbook documents the procedure for rotating Databricks Secrets without pipeline downtime.
All secrets live in scope **`globalsales`** (see `config/secrets_setup.md`).

## Secrets inventory

| Key | Used by |
|---|---|
| `source_jdbc_url` | `nb_extract_sales`, `nb_extract_orders`, `nb_extract_dimensions` — [PENDING: CX-P04] |
| `source_jdbc_user` | Same as above |
| `source_jdbc_password` | Same as above |
| `bi_endpoint_token` | Power BI service principal — SQL Warehouse PAT |

## Rotation procedure

### Step 1: Obtain new credential

Coordinate with the source system owner (for JDBC keys) or the Databricks workspace admin (for PATs) to generate the new credential value. Do not use the old credential after the new one is issued.

### Step 2: Update the secret

```bash
databricks secrets put-secret globalsales <key-name> --string-value "<new-value>"
```

The update is atomic — the old value is replaced immediately. No restart is required.

### Step 3: Verify the new credential works

Run the affected notebook in a test context:

```bash
# For JDBC credentials:
databricks jobs run-now --job-id <watermark-job-id>
# Then check nb_extract_watermark completes without authentication errors

# For bi_endpoint_token:
# Test the SQL Warehouse connection from a Power BI Desktop file using the new PAT
```

### Step 4: Confirm nightly pipeline picks up the new secret

Databricks Secrets are read on each notebook run — no cluster restart is needed. The next nightly execution of `nightly_etl_main` will use the new value automatically.

### Step 5: Revoke the old credential

Once the new credential is confirmed working, revoke the old one in the source system (or workspace). This prevents credential reuse.

---

## [PENDING: CX-P04] — OLTP credential rotation

The OLTP connection strategy has not been confirmed. Once CX-P04 is resolved:
- Update this section with the confirmed connection type (JDBC / CDC / other)
- Document source system's credential rotation procedure
- Reference `src/etl/ingestion/nb_extract_sales.py` and `nb_extract_orders.py` for code-side impact

---

## Emergency rotation

If credentials are suspected compromised, perform Steps 1–3 immediately and notify the security team. The `nightly_etl_main` workflow will automatically pick up the new secret on its next run without manual intervention.
