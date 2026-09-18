# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/common/udfs.py
# Rules    : CX-P003, NFR-009, NFR-011, NM-001
# Purpose  : Reusable NULL-guarded Python UDFs for Spark SQL registration.
#            Centralises date-key derivation and package-name normalisation
#            so that all ETL notebooks share identical transformation logic.
# =============================================================================

from __future__ import annotations

from datetime import date, datetime
from typing import Optional


# ---------------------------------------------------------------------------
# UDF: format_date_key
# ---------------------------------------------------------------------------

def format_date_key(dt: Optional[datetime | date]) -> Optional[str]:
    """Return an ISO date string (YYYY-MM-DD) from a TIMESTAMP or DATE value.

    Business purpose
    ----------------
    Derives the ``date_key`` surrogate used to join fact rows to
    ``silver_dim.dim_date``.  A consistent, zero-padded ISO string is required
    so that string-based date-key lookups always match the dimension values
    loaded by the DIM layer pipeline.

    Rule references
    ---------------
    - **CX-P003** : date_key must be derived from ``last_modified_when`` cast
      to DATE before joining to ``dim_date``.
    - **NFR-009** : NULL inputs must propagate as NULL rather than raise
      exceptions so that incomplete source rows do not abort the pipeline.
    - **NFR-011** : Date formatting must be deterministic and timezone-neutral
      (UTC assumed upstream).

    Parameters
    ----------
    dt:
        A :class:`datetime.datetime`, :class:`datetime.date`, or ``None``.

    Returns
    -------
    str | None
        ISO-formatted date string ``"YYYY-MM-DD"``, or ``None`` when *dt* is
        ``None``.

    Examples
    --------
    >>> format_date_key(datetime(2024, 3, 15, 10, 30, 0))
    '2024-03-15'
    >>> format_date_key(date(2024, 3, 15))
    '2024-03-15'
    >>> format_date_key(None) is None
    True

    Spark SQL registration
    ----------------------
    Register once per SparkSession (typically in a shared init notebook):

        from pyspark.sql.functions import udf
        from pyspark.sql.types import StringType
        from src.common.udfs import format_date_key

        format_date_key_udf = udf(format_date_key, StringType())
        spark.udf.register("format_date_key", format_date_key, StringType())

    Usage in SQL:
        SELECT format_date_key(last_modified_when) AS date_key FROM staging_table;
    """
    # NULL guard — rule NFR-009
    if dt is None:
        return None

    # Support both datetime and date objects
    if isinstance(dt, datetime):
        return dt.date().isoformat()
    if isinstance(dt, date):
        return dt.isoformat()

    # Fallback: attempt string coercion for edge cases (e.g. pandas Timestamp)
    try:
        return str(dt)[:10]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# UDF: safe_trim
# ---------------------------------------------------------------------------

def safe_trim(s: Optional[str]) -> Optional[str]:
    """Strip leading and trailing whitespace from a string with a NULL guard.

    Business purpose
    ----------------
    Normalises package/product names sourced from legacy systems where trailing
    spaces and mixed-whitespace padding are common data-quality issues.  Clean
    names are required for consistent grouping and display in BI reports and for
    reliable equality joins on ``package_name`` in the silver layer.

    Rule references
    ---------------
    - **NM-001**  : All name/label columns must be whitespace-trimmed before
      loading into the silver layer.
    - **NFR-009** : NULL inputs must propagate as NULL rather than raise
      exceptions.
    - **NFR-011** : Transformation functions must be deterministic and
      side-effect-free.
    - **CX-P003** : Package name normalisation is part of the context-enrichment
      pass applied during the silver staging step.

    Parameters
    ----------
    s:
        A :class:`str` or ``None``.

    Returns
    -------
    str | None
        Whitespace-stripped string, an empty string ``""`` when the input is
        already empty after stripping, or ``None`` when *s* is ``None``.

    Examples
    --------
    >>> safe_trim("  Widget A  ")
    'Widget A'
    >>> safe_trim("")
    ''
    >>> safe_trim("   ")
    ''
    >>> safe_trim(None) is None
    True

    Spark SQL registration
    ----------------------
    Register once per SparkSession (typically in a shared init notebook):

        from pyspark.sql.functions import udf
        from pyspark.sql.types import StringType
        from src.common.udfs import safe_trim

        safe_trim_udf = udf(safe_trim, StringType())
        spark.udf.register("safe_trim", safe_trim, StringType())

    Usage in SQL:
        SELECT safe_trim(package_name) AS package_name FROM staging_table;
    """
    # NULL guard — rule NFR-009
    if s is None:
        return None

    # Empty string is a valid value; return it as-is after strip
    return s.strip()
