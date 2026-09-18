# CFG-007: Secrets Initialization Runbook

## Prerequisites

- Databricks CLI installed (`databricks --version` ≥ 0.18)
- Workspace URL and token available:
  ```
  export DATABRICKS_HOST=https://<your-workspace>.azuredatabricks.net
  export DATABRICKS_TOKEN=<your-pat-token>
  ```
- Network access to the Databricks workspace

---

## Step 1 — Create the Dev Scope

```bash
databricks secrets create-scope --scope globalpurchase-dev
```

Verify:
```bash
databricks secrets list-scopes | grep globalpurchase-dev
```

---

## Step 2 — Create the Prod Scope

```bash
databricks secrets create-scope --scope globalpurchase-prod
```

---

## Step 3 — Register Required Keys (Dev)

Register each key individually. Values are entered interactively and never logged.

```bash
databricks secrets put --scope globalpurchase-dev --key jdbc_url
databricks secrets put --scope globalpurchase-dev --key jdbc_username
databricks secrets put --scope globalpurchase-dev --key jdbc_password
```

---

## Step 4 — Register Required Keys (Prod)

```bash
databricks secrets put --scope globalpurchase-prod --key jdbc_url
databricks secrets put --scope globalpurchase-prod --key jdbc_username
databricks secrets put --scope globalpurchase-prod --key jdbc_password
```

---

## Step 5 — Verify (without revealing values)

```python
# Run in a Databricks notebook:
dbutils.secrets.list(scope="globalpurchase-dev")
# Expected: [SecretMetadata(key='jdbc_password'), SecretMetadata(key='jdbc_url'), SecretMetadata(key='jdbc_username')]
```

The `list()` call returns key names only — values are never exposed.

---

## Step 6 — Credential Rotation

See `config/secrets_rotation_runbook.md` for rotation procedures.

---

## Reference

- [Databricks Secrets documentation](https://docs.databricks.com/security/secrets/index.html)
- Key names consumed by notebooks: `jdbc_url`, `jdbc_username`, `jdbc_password`
- Scope used in ETL widgets: `env_scope` widget value set to `globalpurchase-dev` or `globalpurchase-prod`
