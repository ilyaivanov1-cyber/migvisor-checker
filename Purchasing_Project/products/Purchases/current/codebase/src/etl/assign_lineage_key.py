"""
TASK-013: Assign lineage_key to the batch
Design ref: design.md §3.1 Calculations — CALC-004; §5.1 Lineage Tracking.
Requirements: FR-005
Depends on: TASK-004 (meta.lineage DDL), TASK-005 (meta.sequence_state DDL), TASK-009 (extraction)

begin_batch() is called from extract_purchase_staging.py at batch start so every row
written to purchasing.stg.purchase_staging carries a non-null lineage_key. end_batch()
is called after merge_fact_purchase.py and the QV-001/002/003 checks complete, closing
the lineage record with a final status.
"""

import uuid
from datetime import datetime, timezone

from pyspark.sql import SparkSession


def begin_batch(spark: SparkSession) -> tuple:
    """Issue a new lineage_key and open a RUNNING lineage record for this run.

    :return: (lineage_key, run_id)
    """
    run_id = str(uuid.uuid4())

    # Atomic read-increment-write via conditional MERGE avoids duplicate keys under concurrent runs.
    spark.sql(
        """
        MERGE INTO purchasing.meta.sequence_state AS target
        USING (SELECT 'lineage_key' AS sequence_name) AS source
        ON target.sequence_name = source.sequence_name
        WHEN MATCHED THEN UPDATE SET target.current_value = target.current_value + 1
        """
    )
    lineage_key = spark.sql(
        "SELECT current_value FROM purchasing.meta.sequence_state WHERE sequence_name = 'lineage_key'"
    ).collect()[0]["current_value"]

    spark.sql(
        """
        INSERT INTO purchasing.meta.lineage (lineage_key, run_id, batch_start, batch_end, status)
        VALUES (:lineage_key, :run_id, :batch_start, NULL, 'RUNNING')
        """,
        lineage_key=lineage_key,
        run_id=run_id,
        batch_start=datetime.now(timezone.utc),
    )
    return lineage_key, run_id


def end_batch(spark: SparkSession, lineage_key: int, status: str) -> None:
    """Close the lineage record for this run.

    :param status: 'SUCCESS' or 'FAILED'
    """
    if status not in ("SUCCESS", "FAILED"):
        raise ValueError(f"status must be 'SUCCESS' or 'FAILED', got {status!r}")

    spark.sql(
        """
        UPDATE purchasing.meta.lineage
        SET status = :status, batch_end = :batch_end
        WHERE lineage_key = :lineage_key
        """,
        status=status,
        batch_end=datetime.now(timezone.utc),
        lineage_key=lineage_key,
    )


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    issued_key, issued_run_id = begin_batch(spark)
    print(f"Opened lineage_key={issued_key} run_id={issued_run_id}")
