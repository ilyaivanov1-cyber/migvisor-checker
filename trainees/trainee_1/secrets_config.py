# TASK-ENV-002: Databricks Secrets access module
# All pipeline notebooks import secrets exclusively through this module.
# Never call dbutils.secrets.get() directly in pipeline code.

from __future__ import annotations


def get_secret(scope: str, key: str) -> str:
    """Return the secret value for the given scope and key.

    Raises a RuntimeError with a clear message if the key is missing,
    rather than letting dbutils raise an opaque exception.
    """
    try:
        # dbutils is injected by the Databricks runtime; not available in unit tests.
        # Tests should mock this function directly.
        from pyspark.dbutils import DBUtils  # noqa: PLC0415
        from pyspark.sql import SparkSession  # noqa: PLC0415

        spark = SparkSession.getActiveSession()
        dbutils = DBUtils(spark)
        return dbutils.secrets.get(scope=scope, key=key)
    except ImportError:
        raise RuntimeError(
            "dbutils is not available outside a Databricks runtime. "
            "Mock get_secret() in unit tests."
        ) from None
    except Exception as exc:
        raise RuntimeError(
            f"Secret '{key}' not found in scope '{scope}'. "
            f"Ensure the secret is provisioned per secrets_setup.md. "
            f"Original error: {exc}"
        ) from exc
