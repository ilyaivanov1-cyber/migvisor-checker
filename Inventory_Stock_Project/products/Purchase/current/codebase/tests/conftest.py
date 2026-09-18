# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : tests/conftest.py
# Purpose  : Shared pytest fixtures — SparkSession, schemas, and sample
#            DataFrames reused across all Purchase test modules.
# =============================================================================

import datetime
import pytest

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField,
    LongType, IntegerType, StringType,
    BooleanType, DateType, TimestampType,
)


# ---------------------------------------------------------------------------
# SparkSession — local mode, Delta enabled, reused for the entire test session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("purchase_tests")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


# ---------------------------------------------------------------------------
# Schema definitions — mirror the generated DDL files exactly
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def purchase_staging_schema():
    return StructType([
        StructField("wwi_purchase_order_id", IntegerType(),  False),
        StructField("ordered_outers",        IntegerType(),  False),
        StructField("ordered_quantity",       IntegerType(),  False),
        StructField("received_outers",        IntegerType(),  True),
        StructField("package",                StringType(),   False),
        StructField("is_order_finalized",     BooleanType(),  False),
        StructField("last_modified_when",     TimestampType(), False),
        StructField("lineage_key",            LongType(),     False),
        StructField("supplier_key",           LongType(),     True),
        StructField("stock_item_key",         LongType(),     True),
        StructField("date_key",               DateType(),     True),
    ])


@pytest.fixture(scope="session")
def fact_purchase_schema():
    return StructType([
        StructField("purchase_key",           LongType(),     False),
        StructField("date_key",               DateType(),     False),
        StructField("supplier_key",           LongType(),     False),
        StructField("stock_item_key",         LongType(),     False),
        StructField("wwi_purchase_order_id",  IntegerType(),  False),
        StructField("ordered_outers",         IntegerType(),  False),
        StructField("ordered_quantity",       IntegerType(),  False),
        StructField("received_outers",        IntegerType(),  True),
        StructField("package",                StringType(),   False),
        StructField("is_order_finalized",     BooleanType(),  False),
        StructField("lineage_key",            LongType(),     False),
    ])


@pytest.fixture(scope="session")
def supplier_dim_schema():
    return StructType([
        StructField("supplier_key",   LongType(),   False),
        StructField("wwi_supplier_id", IntegerType(), False),
        StructField("supplier",        StringType(),  False),
        StructField("valid_from",      DateType(),    False),
        StructField("valid_to",        DateType(),    False),
        StructField("is_current_row",  BooleanType(), False),
    ])


@pytest.fixture(scope="session")
def stock_item_dim_schema():
    return StructType([
        StructField("stock_item_key",   LongType(),   False),
        StructField("wwi_stock_item_id", IntegerType(), False),
        StructField("stock_item",        StringType(),  False),
        StructField("valid_from",        DateType(),    False),
        StructField("valid_to",          DateType(),    False),
        StructField("is_current_row",    BooleanType(), False),
    ])


# ---------------------------------------------------------------------------
# Sample DataFrames
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sample_staging_df(spark, purchase_staging_schema):
    rows = [
        (1001, 10, 120, 10, "Each",  True,  datetime.datetime(2024, 3, 15, 12, 0, 0), 1, None, None, None),
        (1002, 5,  60,  None, "Carton", False, datetime.datetime(2024, 3, 15, 13, 0, 0), 1, None, None, None),
    ]
    return spark.createDataFrame(rows, schema=purchase_staging_schema)


@pytest.fixture(scope="session")
def sample_supplier_dim_df(spark, supplier_dim_schema):
    rows = [
        (10, 42, "Fabrikam, Inc.", datetime.date(2020, 1, 1), datetime.date(9999, 12, 31), True),
        (11, 43, "Litware Corp.",  datetime.date(2021, 6, 1), datetime.date(9999, 12, 31), True),
    ]
    return spark.createDataFrame(rows, schema=supplier_dim_schema)


@pytest.fixture(scope="session")
def sample_stock_item_dim_df(spark, stock_item_dim_schema):
    rows = [
        (20, 100, "USB food flash drive - sushi roll",  datetime.date(2019, 1, 1), datetime.date(9999, 12, 31), True),
        (21, 101, "Chocolate Frogs 250g",                datetime.date(2020, 3, 1), datetime.date(9999, 12, 31), True),
    ]
    return spark.createDataFrame(rows, schema=stock_item_dim_schema)
