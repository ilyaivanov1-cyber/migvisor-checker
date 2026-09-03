# Databricks Secrets Setup — Sales_Orders Pipeline
_TASK-ENV-002_

## Secret scope

All pipeline secrets use scope: **`globalsales`**

Create the scope once per workspace (requires admin or SP with manage-secrets permission):

```bash
databricks secrets create-scope --scope globalsales
```

## Keys

| Key | Purpose | Note |
|---|---|---|
| `source_jdbc_url` | OLTP source JDBC connection URL | [PENDING: CX-P04] |
| `source_jdbc_user` | OLTP source credential username | [PENDING: CX-P04] |
| `source_jdbc_password` | OLTP source credential password | [PENDING: CX-P04] |
| `bi_endpoint_token` | Databricks SQL endpoint PAT for BI tools | Set after SQL Warehouse is provisioned |

## Adding / updating a key

```bash
databricks secrets put --scope globalsales --key source_jdbc_url
# paste the value when prompted, then Ctrl+D
```

Or via the API:

```bash
databricks secrets put-secret globalsales source_jdbc_url --string-value "jdbc:sqlserver://..."
```

## Access grant

Grant the nightly ETL service principal read access to the scope:

```bash
# [PENDING: CX-P05] replace with confirmed SP application-id
databricks secrets put-acl --scope globalsales \
  --principal "{{UC_ROLE_SERVICE_PRINCIPAL}}" \
  --permission READ
```

## Code-side access

All notebooks reference secrets exclusively via `secrets_config.py`:

```python
from config.secrets_config import get_secret
jdbc_url = get_secret("globalsales", "source_jdbc_url")
```

Never call `dbutils.secrets.get()` directly in pipeline notebooks.

## Rotation procedure

See `config/secrets_rotation_runbook.md`.
