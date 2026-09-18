# CFG-008: Credential Rotation Runbook

## 1. Trigger Conditions

Rotate JDBC credentials when any of the following occur:
- Scheduled rotation (every 90 days, per security policy)
- Security incident: suspected credential exposure
- Service account change
- JDBC URL or database migration

---

## 2. Rotation Procedure

### 2.1 Prepare new credentials

Obtain new JDBC credentials from the DBA or secret vault before rotating.
Do **not** revoke old credentials until the pipeline is verified with new ones.

### 2.2 Rotate Dev scope

```bash
databricks secrets put --scope globalpurchase-dev --key jdbc_url
databricks secrets put --scope globalpurchase-dev --key jdbc_username
databricks secrets put --scope globalpurchase-dev --key jdbc_password
```

### 2.3 Rotate Prod scope

```bash
databricks secrets put --scope globalpurchase-prod --key jdbc_url
databricks secrets put --scope globalpurchase-prod --key jdbc_username
databricks secrets put --scope globalpurchase-prod --key jdbc_password
```

---

## 3. Verification Steps

1. Trigger a manual Workflow run in the dev environment.
2. Confirm `nb_extract_dimensions` and `nb_extract_purchase` complete without JDBC auth errors.
3. Run `nb_pii_compliance_check` to verify zero hardcoded credentials in the codebase.
4. Check `stg.lineage` — the run status must be `success`.

---

## 4. Rollback Procedure

If the pipeline fails with new credentials:
1. Re-rotate to the previous credentials immediately:
   ```bash
   databricks secrets put --scope globalpurchase-<env> --key jdbc_<key>
   ```
2. Re-trigger the Workflow to confirm recovery.
3. Investigate the new credentials before retrying rotation.

---

## 5. Notification Checklist

Notify the following after any rotation:
- [ ] Data Engineering lead
- [ ] Platform Security team
- [ ] On-call engineer if rotation is incident-triggered

---

## 6. Rotation Log

| Date | Rotated By | Environment | Keys Rotated | Reason |
|---|---|---|---|---|
| *(first entry)* | | dev + prod | jdbc_url, jdbc_username, jdbc_password | Initial setup |
