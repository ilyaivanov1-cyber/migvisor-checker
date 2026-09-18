# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : tests/common/test_sk_resolver.py
# Purpose  : Unit tests for src/common/sk_resolver.py using a local SparkSession.
#            No live Databricks cluster required — all data is in-memory.
# Rules    : FR-004, FR-005, DQR-009
# Task     : TASK-020
# =============================================================================
"""
Unit tests for sk_resolver.resolve_supplier_key and resolve_stock_item_key.

Test matrix
-----------
Supplier key (FR-004 / CALC-002):
  1. test_supplier_key_temporal_match               — row WITHIN validity range → non-zero key
  2. test_supplier_key_no_match_returns_zero         — row OUTSIDE all ranges   → key = 0
  3. test_supplier_key_tie_breaker_selects_most_recent — two overlapping versions → highest valid_from wins
  4. test_supplier_key_no_nulls_after_resolution     — DQR-009: no NULL supplier_key values after resolution

Stock-item key (FR-005 / CALC-003):
  5. test_stock_item_key_temporal_match              — row WITHIN validity range → non-zero key
  6. test_stock_item_key_no_match_returns_zero       — row OUTSIDE all ranges   → key = 0
  7. test_stock_item_key_tie_breaker_selects_most_recent — two overlapping versions → highest valid_from wins
  8. test_stock_item_key_no_nulls_after_resolution   — DQR-009: no NULL stock_item_key values after resolution

Temporal logic (TY-P001)
------------------------
valid_from and valid_to are stored as DATE in the dimension tables.
sk_resolver.py CASTs them to TIMESTAMP before the inequality comparison:
  last_modified_when >  CAST(valid_from AS TIMESTAMP)
  last_modified_when <= CAST(valid_to   AS TIMESTAMP)

The tests mirror this by creating dimension rows with DateType columns and
staging rows with TimestampType last_modified_when values.
"""

import datetime

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DateType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from src.common.sk_resolver import resolve_stock_item_key, resolve_supplier_key

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def spark():
    """Return a local SparkSession for the test module.

    scope="module" means one SparkSession is shared across all tests in this
    file, which avoids the overhead of repeatedly starting and stopping Spark.
    """
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("test_sk_resolver")
        # Disable adaptive query execution and broadcast-auto-join thresholds
        # so that BROADCAST hints work deterministically in local mode.
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.autoBroadcastJoinThreshold", "-1")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

STAGING_SCHEMA = StructType([
    StructField("purchase_staging_key",  LongType(),      nullable=False),
    StructField("wwi_supplier_id",       IntegerType(),   nullable=False),
    StructField("wwi_stock_item_id",     IntegerType(),   nullable=False),
    StructField("last_modified_when",    TimestampType(), nullable=False),
])

SUPPLIER_DIM_SCHEMA = StructType([
    StructField("wwi_supplier_id", IntegerType(), nullable=False),
    StructField("supplier_key",    LongType(),    nullable=False),
    StructField("valid_from",      DateType(),    nullable=False),
    StructField("valid_to",        DateType(),    nullable=False),
])

STOCK_ITEM_DIM_SCHEMA = StructType([
    StructField("wwi_stock_item_id", IntegerType(), nullable=False),
    StructField("stock_item_key",    LongType(),    nullable=False),
    StructField("valid_from",        DateType(),    nullable=False),
    StructField("valid_to",          DateType(),    nullable=False),
])

# Convenience date constants
_D = datetime.date
_DT = datetime.datetime

# Dimension version: 2020-01-01 (exclusive lower bound) to 2030-12-31 (inclusive upper bound)
VALID_FROM_EARLY  = _D(2020, 1, 1)
VALID_TO_LATE     = _D(2030, 12, 31)

# Second dimension version for tie-breaker tests: starts after first version
VALID_FROM_LATER  = _D(2023, 6, 1)


# ===========================================================================
# SUPPLIER KEY TESTS
# ===========================================================================

class TestResolveSupplierKey:
    """Unit tests for resolve_supplier_key (FR-004, CALC-002, DQR-009)."""

    def test_supplier_key_temporal_match(self, spark):
        """Staging row with last_modified_when WITHIN dimension validity range
        must resolve to a non-zero supplier_key (FR-004, CALC-002).

        Dimension version: valid_from=2020-01-01, valid_to=2030-12-31
        Probe timestamp: 2024-06-15 10:00:00 — clearly inside the window.
        Expected: supplier_key = 101 (the dimension's surrogate key).
        """
        staging_df = spark.createDataFrame(
            [(1, 42, 99, _DT(2024, 6, 15, 10, 0, 0))],
            schema=STAGING_SCHEMA,
        )
        supplier_dim_df = spark.createDataFrame(
            [(42, 101, VALID_FROM_EARLY, VALID_TO_LATE)],
            schema=SUPPLIER_DIM_SCHEMA,
        )

        result = resolve_supplier_key(staging_df, supplier_dim_df)
        rows = result.collect()

        assert len(rows) == 1, "Expected exactly one output row"
        assert rows[0]["supplier_key"] == 101, (
            f"Expected supplier_key=101, got {rows[0]['supplier_key']}"
        )

    def test_supplier_key_no_match_returns_zero(self, spark):
        """Staging row with last_modified_when OUTSIDE all dimension validity
        ranges must receive supplier_key = 0 (DQR-009 — no NULL FKs).

        Dimension version covers 2020-01-01 to 2021-12-31.
        Probe timestamp: 2024-06-15 — after the version expired.
        Expected: supplier_key = 0 (COALESCE default).
        """
        staging_df = spark.createDataFrame(
            [(2, 42, 99, _DT(2024, 6, 15, 10, 0, 0))],
            schema=STAGING_SCHEMA,
        )
        supplier_dim_df = spark.createDataFrame(
            [(42, 101, _D(2020, 1, 1), _D(2021, 12, 31))],
            schema=SUPPLIER_DIM_SCHEMA,
        )

        result = resolve_supplier_key(staging_df, supplier_dim_df)
        rows = result.collect()

        assert len(rows) == 1, "Expected exactly one output row"
        assert rows[0]["supplier_key"] == 0, (
            f"Expected supplier_key=0 (unresolved), got {rows[0]['supplier_key']}"
        )

    def test_supplier_key_tie_breaker_selects_most_recent(self, spark):
        """When TWO dimension versions both overlap last_modified_when, the
        ROW_NUMBER() de-duplication (ORDER BY valid_from DESC) must select the
        version with the highest valid_from (FLT-003).

        Setup:
          Version A: valid_from=2020-01-01, supplier_key=101
          Version B: valid_from=2023-06-01, supplier_key=202  <-- most recent
        Both cover the probe timestamp 2024-06-15.
        Expected: supplier_key = 202.
        """
        staging_df = spark.createDataFrame(
            [(3, 42, 99, _DT(2024, 6, 15, 10, 0, 0))],
            schema=STAGING_SCHEMA,
        )
        supplier_dim_df = spark.createDataFrame(
            [
                (42, 101, VALID_FROM_EARLY, VALID_TO_LATE),   # Version A — older
                (42, 202, VALID_FROM_LATER, VALID_TO_LATE),   # Version B — newer
            ],
            schema=SUPPLIER_DIM_SCHEMA,
        )

        result = resolve_supplier_key(staging_df, supplier_dim_df)
        rows = result.collect()

        assert len(rows) == 1, "ROW_NUMBER de-duplication must produce exactly one row"
        assert rows[0]["supplier_key"] == 202, (
            f"Expected most-recent version supplier_key=202, got {rows[0]['supplier_key']}"
        )

    def test_supplier_key_no_nulls_after_resolution(self, spark):
        """After resolution, no row in the result may have a NULL supplier_key
        (DQR-009 — NULL FK values are forbidden in the fact table).

        Setup: mix of two staging rows — one that matches and one that doesn't.
        Both should produce non-NULL supplier_key values (matched → 101, unmatched → 0).
        """
        staging_df = spark.createDataFrame(
            [
                (4, 42, 99, _DT(2024, 6, 15, 10, 0, 0)),   # will match
                (5, 99, 99, _DT(2024, 6, 15, 10, 0, 0)),   # no dimension row for wwi_supplier_id=99
            ],
            schema=STAGING_SCHEMA,
        )
        supplier_dim_df = spark.createDataFrame(
            [(42, 101, VALID_FROM_EARLY, VALID_TO_LATE)],
            schema=SUPPLIER_DIM_SCHEMA,
        )

        result = resolve_supplier_key(staging_df, supplier_dim_df)
        null_count = result.filter(result["supplier_key"].isNull()).count()

        assert null_count == 0, (
            f"DQR-009 violated: {null_count} row(s) have NULL supplier_key after resolution"
        )


# ===========================================================================
# STOCK ITEM KEY TESTS
# ===========================================================================

class TestResolveStockItemKey:
    """Unit tests for resolve_stock_item_key (FR-005, CALC-003, DQR-009)."""

    def test_stock_item_key_temporal_match(self, spark):
        """Staging row with last_modified_when WITHIN dimension validity range
        must resolve to a non-zero stock_item_key (FR-005, CALC-003).

        Dimension version: valid_from=2020-01-01, valid_to=2030-12-31
        Probe timestamp: 2024-06-15 10:00:00 — clearly inside the window.
        Expected: stock_item_key = 501.
        """
        staging_df = spark.createDataFrame(
            [(10, 42, 77, _DT(2024, 6, 15, 10, 0, 0))],
            schema=STAGING_SCHEMA,
        )
        stock_item_dim_df = spark.createDataFrame(
            [(77, 501, VALID_FROM_EARLY, VALID_TO_LATE)],
            schema=STOCK_ITEM_DIM_SCHEMA,
        )

        result = resolve_stock_item_key(staging_df, stock_item_dim_df)
        rows = result.collect()

        assert len(rows) == 1, "Expected exactly one output row"
        assert rows[0]["stock_item_key"] == 501, (
            f"Expected stock_item_key=501, got {rows[0]['stock_item_key']}"
        )

    def test_stock_item_key_no_match_returns_zero(self, spark):
        """Staging row with last_modified_when OUTSIDE all dimension validity
        ranges must receive stock_item_key = 0 (DQR-009).

        Dimension version covers 2020-01-01 to 2021-12-31.
        Probe timestamp: 2024-06-15 — after the version expired.
        Expected: stock_item_key = 0.
        """
        staging_df = spark.createDataFrame(
            [(11, 42, 77, _DT(2024, 6, 15, 10, 0, 0))],
            schema=STAGING_SCHEMA,
        )
        stock_item_dim_df = spark.createDataFrame(
            [(77, 501, _D(2020, 1, 1), _D(2021, 12, 31))],
            schema=STOCK_ITEM_DIM_SCHEMA,
        )

        result = resolve_stock_item_key(staging_df, stock_item_dim_df)
        rows = result.collect()

        assert len(rows) == 1, "Expected exactly one output row"
        assert rows[0]["stock_item_key"] == 0, (
            f"Expected stock_item_key=0 (unresolved), got {rows[0]['stock_item_key']}"
        )

    def test_stock_item_key_tie_breaker_selects_most_recent(self, spark):
        """When TWO dimension versions both overlap last_modified_when, the
        ROW_NUMBER() de-duplication (ORDER BY valid_from DESC) must select the
        version with the highest valid_from (FLT-003).

        Setup:
          Version A: valid_from=2020-01-01, stock_item_key=501
          Version B: valid_from=2023-06-01, stock_item_key=602  <-- most recent
        Both cover the probe timestamp 2024-06-15.
        Expected: stock_item_key = 602.
        """
        staging_df = spark.createDataFrame(
            [(12, 42, 77, _DT(2024, 6, 15, 10, 0, 0))],
            schema=STAGING_SCHEMA,
        )
        stock_item_dim_df = spark.createDataFrame(
            [
                (77, 501, VALID_FROM_EARLY, VALID_TO_LATE),   # Version A — older
                (77, 602, VALID_FROM_LATER, VALID_TO_LATE),   # Version B — newer
            ],
            schema=STOCK_ITEM_DIM_SCHEMA,
        )

        result = resolve_stock_item_key(staging_df, stock_item_dim_df)
        rows = result.collect()

        assert len(rows) == 1, "ROW_NUMBER de-duplication must produce exactly one row"
        assert rows[0]["stock_item_key"] == 602, (
            f"Expected most-recent version stock_item_key=602, got {rows[0]['stock_item_key']}"
        )

    def test_stock_item_key_no_nulls_after_resolution(self, spark):
        """After resolution, no row in the result may have a NULL stock_item_key
        (DQR-009 — NULL FK values are forbidden in the fact table).

        Setup: mix of two staging rows — one that matches and one that doesn't.
        Both should produce non-NULL stock_item_key values (matched → 501, unmatched → 0).
        """
        staging_df = spark.createDataFrame(
            [
                (13, 42, 77, _DT(2024, 6, 15, 10, 0, 0)),   # will match
                (14, 42, 88, _DT(2024, 6, 15, 10, 0, 0)),   # no dimension row for wwi_stock_item_id=88
            ],
            schema=STAGING_SCHEMA,
        )
        stock_item_dim_df = spark.createDataFrame(
            [(77, 501, VALID_FROM_EARLY, VALID_TO_LATE)],
            schema=STOCK_ITEM_DIM_SCHEMA,
        )

        result = resolve_stock_item_key(staging_df, stock_item_dim_df)
        null_count = result.filter(result["stock_item_key"].isNull()).count()

        assert null_count == 0, (
            f"DQR-009 violated: {null_count} row(s) have NULL stock_item_key after resolution"
        )
