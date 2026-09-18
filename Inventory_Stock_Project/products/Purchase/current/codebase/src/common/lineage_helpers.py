# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : src/common/lineage_helpers.py
# Purpose  : Shared lineage record open/close helpers — eliminates inline
#            spark.sql UPDATE duplication across ETL notebooks (resolves F-002).
# Rules    : LN-001, LN-002, LN-003, LN-P001, NFR-009, SX-P004
# =============================================================================

from datetime import datetime, timezone
from src.common.constants import LINEAGE_RUN_TABLE


def open_lineage_record(
    spark,
    table_name: str,
    pipeline_name: str,
    source_system_cutoff_time,
) -> int:
    """
    Insert a new row into bronze.lineage_run and return the generated lineage_key.

    Parameters
    ----------
    spark                    : active SparkSession
    table_name               : ETL target table name (e.g. 'fact_purchase')
    pipeline_name            : Databricks workflow name
    source_system_cutoff_time: upper-bound cutoff timestamp for this run

    Returns
    -------
    int : the IDENTITY-generated lineage_key for this run
    """
    etl_run_id = datetime.now(timezone.utc).isoformat()

    spark.sql(f"""
        INSERT INTO {LINEAGE_RUN_TABLE}
            (etl_run_id, table_name, pipeline_name, data_load_started, source_system_cutoff_time)
        VALUES (
            '{etl_run_id}',
            '{table_name}',
            '{pipeline_name}',
            current_timestamp(),
            CAST('{source_system_cutoff_time}' AS TIMESTAMP)
        )
    """)

    lineage_key = spark.sql(f"""
        SELECT MAX(lineage_key) AS lineage_key
        FROM {LINEAGE_RUN_TABLE}
        WHERE etl_run_id = '{etl_run_id}'
    """).collect()[0]["lineage_key"]

    return int(lineage_key)


def close_lineage_record(
    spark,
    lineage_key: int,
    succeeded: bool,
    rows_merged: int = 0,
) -> None:
    """
    Mark a lineage_run record as completed (success or failure).

    Parameters
    ----------
    spark        : active SparkSession
    lineage_key  : the key returned by open_lineage_record
    succeeded    : True on success path, False in except block
    rows_merged  : number of rows inserted/updated in the fact table (0 on failure)
    """
    spark.sql(f"""
        UPDATE {LINEAGE_RUN_TABLE}
        SET was_successful      = {str(succeeded).lower()},
            data_load_completed = current_timestamp(),
            table_row_count     = {rows_merged}
        WHERE lineage_key = {lineage_key}
    """)
