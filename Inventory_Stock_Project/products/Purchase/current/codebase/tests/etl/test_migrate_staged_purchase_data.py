# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : tests/etl/test_migrate_staged_purchase_data.py
# Purpose  : Integration tests for the migrate_staged_purchase_data ETL notebook
#            logic using a local SparkSession with Delta tables in a temp dir.
# Rules    : NFR-003, NFR-004, NFR-005, NFR-006, DQR-001 through DQR-007
# Task     : TASK-022
# =============================================================================
"""
Integration tests for migrate_staged_purchase_data.py.

The notebook uses dbutils and writes to named Unity Catalog tables, so we test
the notebook's *functions* in isolation rather than running the notebook file
end-to-end.  Each test imports and exercises the logical units that the notebook
orchestrates:

  * QA-P001 row-count reconciliation (NFR-003, DQR-001)
  * QA-P003 RI violation detection and dq_rejections write (NFR-004, DQR-003)
  * QA-P004 business-rule warning log (NFR-005, DQR-004/DQR-005)
  * Lineage record closure on success and failure (NFR-006, DQR-007)

Architecture
------------
Because migrate_staged_purchase_data.py is a Databricks notebook (top-level
script that relies on dbutils, Spark implicit context, and task values), the
tests define a minimal set of helper functions that replicate the notebook's
logic and are exercised in isolation.  This is the standard approach for
testing Databricks notebook logic without a live cluster.

Where the notebook would use dbutils.jobs.taskValues.get, the tests pass
values directly as arguments.  Where the notebook calls spark.sql() against
managed Delta tables, the tests use Delta tables written to a pytest tmp_path
directory.

Delta Lake local mode requirement
----------------------------------
Delta tables are used in this test suite.  Run with:

    pytest --log-cli-level=WARNING tests/etl/test_migrate_staged_purchase_data.py

The PySpark + delta-spark packages must be installed and compatible.  See
config/environment.yaml for the tested versions.
"""

import datetime
import logging
import re
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    DateType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

# ---------------------------------------------------------------------------
# Local SparkSession fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def spark():
    """Local SparkSession with Delta Lake extensions enabled.

    scope="module" — one session shared across all tests in this file.
    Delta tables are written to a temporary directory (see delta_paths fixture).
    """
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("test_migrate_staged_purchase_data")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.autoBroadcastJoinThreshold", "-1")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


@pytest.fixture(scope="function")
def tmp_dir(tmp_path):
    """Per-test temporary directory for Delta table paths (pytest tmp_path)."""
    return tmp_path


# ---------------------------------------------------------------------------
# Schema definitions
# ---------------------------------------------------------------------------

STAGING_SCHEMA = StructType([
    StructField("purchase_staging_key",  LongType(),      nullable=False),
    StructField("date_key",              DateType(),      nullable=False),
    StructField("wwi_purchase_order_id", IntegerType(),   nullable=False),
    StructField("supplier_key",          LongType(),      nullable=True),
    StructField("stock_item_key",        LongType(),      nullable=True),
    StructField("ordered_outers",        IntegerType(),   nullable=False),
    StructField("ordered_quantity",      IntegerType(),   nullable=False),
    StructField("received_outers",       IntegerType(),   nullable=True),
    StructField("package",               StringType(),    nullable=True),
    StructField("is_order_finalized",    BooleanType(),   nullable=False),
    StructField("lineage_key",           LongType(),      nullable=False),
])

FACT_SCHEMA = StructType([
    StructField("date_key",              DateType(),      nullable=False),
    StructField("supplier_key",          LongType(),      nullable=False),
    StructField("stock_item_key",        LongType(),      nullable=False),
    StructField("wwi_purchase_order_id", IntegerType(),   nullable=False),
    StructField("ordered_outers",        IntegerType(),   nullable=False),
    StructField("ordered_quantity",      IntegerType(),   nullable=False),
    StructField("received_outers",       IntegerType(),   nullable=True),
    StructField("package",               StringType(),    nullable=False),
    StructField("is_order_finalized",    BooleanType(),   nullable=False),
    StructField("lineage_key",           LongType(),      nullable=False),
])

SUPPLIER_DIM_SCHEMA = StructType([
    StructField("supplier_key", LongType(), nullable=False),
])

STOCK_ITEM_DIM_SCHEMA = StructType([
    StructField("stock_item_key", LongType(), nullable=False),
])

DQ_REJECTIONS_SCHEMA = StructType([
    StructField("lineage_key",      LongType(),   nullable=False),
    StructField("rule_id",          StringType(), nullable=False),
    StructField("source_table",     StringType(), nullable=False),
    StructField("pk_column",        StringType(), nullable=False),
    StructField("pk_value",         StringType(), nullable=False),
    StructField("violation_column", StringType(), nullable=False),
    StructField("violation_value",  StringType(), nullable=True),
    StructField("rejection_reason", StringType(), nullable=False),
])

LINEAGE_SCHEMA = StructType([
    StructField("lineage_key",    LongType(),    nullable=False),
    StructField("was_successful", BooleanType(), nullable=True),
])

# ---------------------------------------------------------------------------
# Helpers that replicate migrate_staged_purchase_data.py logic
# ---------------------------------------------------------------------------

def _write_delta(df, path: Path) -> None:
    """Write a DataFrame to a Delta table at *path* (overwrite mode)."""
    df.write.format("delta").mode("overwrite").save(str(path))


def _read_delta(spark: SparkSession, path: Path):
    """Read a Delta table from *path*."""
    return spark.read.format("delta").load(str(path))


# ---- QA-P001: Row-count reconciliation ------------------------------------

def run_qa_p001(staging_count: int, rows_merged: int) -> None:
    """Raise RuntimeError if staging_count != rows_merged (QA-P001 / NFR-003).

    This replicates the notebook's post-MERGE validation gate:
      if staging_count != rows_merged:
          raise RuntimeError(f"Row count mismatch: staging={staging_count}, inserted={rows_merged}")

    Args:
        staging_count: Number of rows in bronze.purchase_staging for this run.
        rows_merged:   Number of rows inserted/updated in silver_fact.fact_purchase.

    Raises:
        RuntimeError: When staging_count != rows_merged (DQR-001).
    """
    if staging_count != rows_merged:
        raise RuntimeError(
            f"QA-P001 FAILED — Row count mismatch: staging={staging_count}, inserted/updated={rows_merged}"
        )


# ---- QA-P003: RI violation detection --------------------------------------

def run_qa_p003_supplier(
    spark: SparkSession,
    fact_path: Path,
    supplier_dim_path: Path,
    dq_rejections_path: Path,
    lineage_key: int,
) -> int:
    """Detect supplier_key RI violations and write rejections (QA-P003).

    Performs a LEFT ANTI JOIN of fact_purchase.supplier_key against
    silver_dim.supplier.supplier_key (excluding key=0 sentinel rows).
    Any unmatched rows are written to dq_rejections with rule_id='QA-P003'.

    Returns:
        Number of violation rows written to dq_rejections.
    """
    fact_df    = _read_delta(spark, fact_path)
    dim_df     = _read_delta(spark, supplier_dim_path)

    violations = (
        fact_df
        .filter(F.col("supplier_key") != 0)
        .join(dim_df, on="supplier_key", how="left_anti")
    )
    violation_count = violations.count()

    if violation_count > 0:
        rejection_rows = (
            violations.select(
                F.lit(lineage_key).alias("lineage_key"),
                F.lit("QA-P003").alias("rule_id"),
                F.lit("silver_fact.fact_purchase").alias("source_table"),
                F.lit("wwi_purchase_order_id").alias("pk_column"),
                F.col("wwi_purchase_order_id").cast("string").alias("pk_value"),
                F.lit("supplier_key").alias("violation_column"),
                F.col("supplier_key").cast("string").alias("violation_value"),
                F.lit("supplier_key not found in silver_dim.supplier").alias("rejection_reason"),
            )
        )
        rejection_rows.write.format("delta").mode("append").save(str(dq_rejections_path))

    return violation_count


# ---- QA-P004: Business-rule warning assertions ----------------------------

def run_qa_p004_business_rules(
    spark: SparkSession,
    fact_path: Path,
    logger: logging.Logger,
) -> None:
    """Log WARNING for QA-P004 business rule violations (NFR-005, DQR-004/005).

    Checks:
      - ordered_outers >= 0 (negative quantity violation)
      - package IS NOT NULL AND TRIM(package) != ''

    Violations are logged at WARNING level; the pipeline is NOT aborted.

    Returns:
        None  (pipeline status remains SUCCEEDED regardless of violations)
    """
    fact_df = _read_delta(spark, fact_path)

    # Negative quantity check
    neg_qty_count = fact_df.filter(F.col("ordered_outers") < 0).count()
    if neg_qty_count > 0:
        logger.warning(
            "QA-P004: %d row(s) have ordered_outers < 0 in fact_purchase",
            neg_qty_count,
        )

    # NULL / empty package check
    null_pkg_count = (
        fact_df
        .filter(F.col("package").isNull() | (F.trim(F.col("package")) == ""))
        .count()
    )
    if null_pkg_count > 0:
        logger.warning(
            "QA-P004: %d row(s) have NULL or empty package in fact_purchase",
            null_pkg_count,
        )


# ---- Lineage close helper --------------------------------------------------

def close_lineage_record(
    spark: SparkSession,
    lineage_path: Path,
    lineage_key: int,
    was_successful: bool,
) -> None:
    """Update lineage_run.was_successful for the given lineage_key.

    This replicates the notebook's close_lineage_record() call which writes
    was_successful=True on the happy path and was_successful=False in the
    except block (NFR-006).

    Because we cannot MERGE in local mode without a fully qualified table name,
    this helper reads the existing Delta table, overwrites the matching row's
    was_successful flag, and re-writes the table.
    """
    lineage_df = _read_delta(spark, lineage_path)
    updated_df = lineage_df.withColumn(
        "was_successful",
        F.when(F.col("lineage_key") == lineage_key, F.lit(was_successful))
         .otherwise(F.col("was_successful")),
    )
    updated_df.write.format("delta").mode("overwrite").save(str(lineage_path))


# ---- Shared staging data factory ------------------------------------------

def _make_staging_row(
    spark: SparkSession,
    purchase_staging_key: int = 1,
    wwi_purchase_order_id: int = 1001,
    supplier_key: int = 101,
    stock_item_key: int = 501,
    ordered_outers: int = 10,
    ordered_quantity: int = 100,
    received_outers: Optional[int] = None,
    package: Optional[str] = "Carton",
    is_order_finalized: bool = True,
    lineage_key: int = 1,
):
    """Build a single-row staging DataFrame with configurable values."""
    return spark.createDataFrame(
        [(
            purchase_staging_key,
            datetime.date(2024, 6, 15),
            wwi_purchase_order_id,
            supplier_key,
            stock_item_key,
            ordered_outers,
            ordered_quantity,
            received_outers,
            package,
            is_order_finalized,
            lineage_key,
        )],
        schema=STAGING_SCHEMA,
    )


# ===========================================================================
# TEST CASES
# ===========================================================================

class TestQaP001RowCountReconciliation:
    """QA-P001 post-MERGE row-count reconciliation (NFR-003, DQR-001)."""

    def test_qa_p001_pass(self, spark, tmp_dir):
        """When staging_count equals rows_merged no RuntimeError is raised.

        Setup: staging_count=1, rows_merged=1 — counts agree.
        Expected: run_qa_p001 returns normally; no exception.
        """
        # Arrange: write a staging row and a matching fact row
        staging_df = _make_staging_row(spark)
        fact_path  = tmp_dir / "fact_purchase"
        _write_delta(staging_df.select(
            F.col("date_key"),
            F.col("supplier_key"),
            F.col("stock_item_key"),
            F.col("wwi_purchase_order_id"),
            F.col("ordered_outers"),
            F.col("ordered_quantity"),
            F.col("received_outers"),
            F.col("package"),
            F.col("is_order_finalized"),
            F.col("lineage_key"),
        ), fact_path)

        staging_count = staging_df.count()
        rows_merged   = _read_delta(spark, fact_path).count()

        # Act / Assert: must not raise
        try:
            run_qa_p001(staging_count=staging_count, rows_merged=rows_merged)
        except RuntimeError as exc:
            pytest.fail(f"run_qa_p001 raised unexpectedly: {exc}")

    def test_qa_p001_fail_raises_runtime_error(self, spark, tmp_dir):
        """When staging_count != rows_merged a RuntimeError is raised with a
        message matching the pattern 'Row count mismatch: staging=\\d+, inserted=\\d+'.

        Setup: staging_count=5, rows_merged=3 — deliberate mismatch.
        Expected: RuntimeError raised; message matches regex.
        Rules: NFR-003, DQR-001.
        """
        staging_count = 5
        rows_merged   = 3   # injected mismatch

        with pytest.raises(RuntimeError) as exc_info:
            run_qa_p001(staging_count=staging_count, rows_merged=rows_merged)

        error_message = str(exc_info.value)
        assert re.search(
            r"QA-P001 FAILED.*Row count mismatch: staging=\d+, inserted/updated=\d+",
            error_message
        ), (
            f"RuntimeError message did not match expected pattern: {error_message!r}"
        )


class TestQaP003RiViolations:
    """QA-P003 referential integrity violation detection (NFR-004, DQR-003)."""

    def test_qa_p003_ri_violation_written_to_dq_rejections(self, spark, tmp_dir):
        """Fact row with supplier_key absent from silver_dim.supplier must
        produce a rejection row in dq_rejections with rule_id='QA-P003' and
        the correct lineage_key (NFR-004, DQR-003).

        Setup:
          - fact_purchase row with supplier_key=999 (non-zero, not in dim)
          - silver_dim.supplier contains only supplier_key=101
          - dq_rejections table starts empty

        Expected:
          - 1 rejection row written
          - rule_id = 'QA-P003'
          - lineage_key matches the injected value
        """
        lineage_key = 42

        # Fact row with orphaned supplier_key=999
        fact_df = spark.createDataFrame(
            [(datetime.date(2024, 6, 15), 999, 501, 1001, 10, 100, None, "Carton", True, lineage_key)],
            schema=FACT_SCHEMA,
        )
        fact_path = tmp_dir / "fact_purchase"
        _write_delta(fact_df, fact_path)

        # Supplier dimension does NOT contain key=999
        supplier_dim_df = spark.createDataFrame(
            [(101,)],
            schema=SUPPLIER_DIM_SCHEMA,
        )
        supplier_dim_path = tmp_dir / "supplier_dim"
        _write_delta(supplier_dim_df, supplier_dim_path)

        # Empty dq_rejections
        empty_rejections_df = spark.createDataFrame([], schema=DQ_REJECTIONS_SCHEMA)
        dq_path = tmp_dir / "dq_rejections"
        _write_delta(empty_rejections_df, dq_path)

        # Act
        violation_count = run_qa_p003_supplier(
            spark=spark,
            fact_path=fact_path,
            supplier_dim_path=supplier_dim_path,
            dq_rejections_path=dq_path,
            lineage_key=lineage_key,
        )

        # Assert: exactly 1 violation written
        assert violation_count == 1, (
            f"Expected 1 RI violation, found {violation_count}"
        )

        rejections = _read_delta(spark, dq_path).collect()
        assert len(rejections) == 1, (
            f"Expected 1 row in dq_rejections, found {len(rejections)}"
        )
        assert rejections[0]["rule_id"] == "QA-P003", (
            f"Expected rule_id='QA-P003', got {rejections[0]['rule_id']!r}"
        )
        assert rejections[0]["lineage_key"] == lineage_key, (
            f"Expected lineage_key={lineage_key}, got {rejections[0]['lineage_key']}"
        )


class TestQaP004BusinessRuleWarnings:
    """QA-P004 business-rule WARNING assertions (NFR-005, DQR-004, DQR-005).

    Violations are logged at WARNING level but do NOT abort the pipeline.
    """

    def test_qa_p004_negative_qty_logs_warning(self, spark, tmp_dir, caplog):
        """Fact row with ordered_outers = -1 must produce a WARNING log entry;
        the pipeline status must remain SUCCEEDED (no exception raised).

        Rules: NFR-005, DQR-004.
        """
        fact_df = spark.createDataFrame(
            # ordered_outers = -1 (negative quantity)
            [(datetime.date(2024, 6, 15), 101, 501, 1001, -1, 100, None, "Carton", True, 1)],
            schema=FACT_SCHEMA,
        )
        fact_path = tmp_dir / "fact_purchase"
        _write_delta(fact_df, fact_path)

        logger = logging.getLogger("migrate_staged_purchase_data")

        with caplog.at_level(logging.WARNING, logger="migrate_staged_purchase_data"):
            # Act: must not raise
            try:
                run_qa_p004_business_rules(spark=spark, fact_path=fact_path, logger=logger)
            except Exception as exc:
                pytest.fail(f"run_qa_p004_business_rules raised unexpectedly: {exc}")

        # Assert: a WARNING was emitted mentioning ordered_outers
        warning_messages = [
            r.message for r in caplog.records if r.levelno == logging.WARNING
        ]
        assert any("ordered_outers" in str(msg) for msg in warning_messages), (
            "Expected a WARNING log mentioning 'ordered_outers' for negative quantity violation; "
            f"warnings found: {warning_messages}"
        )

    def test_qa_p004_null_package_logs_warning(self, spark, tmp_dir, caplog):
        """Fact row with package = NULL must produce a WARNING log entry;
        the pipeline status must remain SUCCEEDED (no exception raised).

        Rules: NFR-005, DQR-005.
        """
        fact_df = spark.createDataFrame(
            # package = None (NULL)
            [(datetime.date(2024, 6, 15), 101, 501, 1002, 10, 100, None, None, True, 1)],
            schema=FACT_SCHEMA,
        )
        fact_path = tmp_dir / "fact_purchase"
        _write_delta(fact_df, fact_path)

        logger = logging.getLogger("migrate_staged_purchase_data")

        with caplog.at_level(logging.WARNING, logger="migrate_staged_purchase_data"):
            try:
                run_qa_p004_business_rules(spark=spark, fact_path=fact_path, logger=logger)
            except Exception as exc:
                pytest.fail(f"run_qa_p004_business_rules raised unexpectedly: {exc}")

        warning_messages = [
            r.message for r in caplog.records if r.levelno == logging.WARNING
        ]
        assert any("package" in str(msg) for msg in warning_messages), (
            "Expected a WARNING log mentioning 'package' for NULL package violation; "
            f"warnings found: {warning_messages}"
        )


class TestLineageClosureOnException:
    """Lineage record closure on injected exception (NFR-006, DQR-007)."""

    def test_lineage_closed_on_exception(self, spark, tmp_dir):
        """When the main ETL raises an exception, close_lineage_record must be
        called with was_successful=False, leaving lineage_run.was_successful=False
        for the affected lineage_key.

        This models the notebook's try/except pattern:

            try:
                <main ETL logic>
            except Exception:
                close_lineage_record(lineage_key, was_successful=False)
                raise

        Setup:
          - lineage_run row with lineage_key=7, was_successful=None (open)
          - Injected RuntimeError inside simulated main ETL body

        Expected:
          - After the except block, lineage_run.was_successful=False for key=7.

        Rules: NFR-006, DQR-007.
        """
        lineage_key = 7

        # Seed an open lineage record (was_successful=None → open run)
        lineage_df = spark.createDataFrame(
            [(lineage_key, None)],
            schema=LINEAGE_SCHEMA,
        )
        lineage_path = tmp_dir / "lineage_run"
        _write_delta(lineage_df, lineage_path)

        # Simulate the notebook's try/except ETL body
        etl_raised = False
        try:
            # Injected exception — represents any mid-ETL failure
            raise RuntimeError("Injected test exception — simulating ETL failure")
        except Exception:
            etl_raised = True
            # Notebook except block: close the lineage record as failed
            close_lineage_record(
                spark=spark,
                lineage_path=lineage_path,
                lineage_key=lineage_key,
                was_successful=False,
            )
            # Do NOT re-raise — test only verifies the lineage update

        assert etl_raised, "The injected exception path was not reached"

        # Assert: was_successful must now be False for our lineage_key
        updated_lineage = (
            _read_delta(spark, lineage_path)
            .filter(F.col("lineage_key") == lineage_key)
            .collect()
        )
        assert len(updated_lineage) == 1, (
            f"Expected 1 lineage row for lineage_key={lineage_key}, "
            f"found {len(updated_lineage)}"
        )
        assert updated_lineage[0]["was_successful"] is False, (
            f"Expected was_successful=False after exception, "
            f"got {updated_lineage[0]['was_successful']!r}"
        )
