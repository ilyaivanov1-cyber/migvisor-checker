"""
TASK-015: Advance etl_cutoff watermark
Design ref: design.md §5.3 Monitoring and Alerting. Requirements: FR-008.
Depends on: TASK-006 (meta.etl_cutoff DDL), TASK-014 (MERGE load)
"""

from datetime import datetime

from pyspark.sql import SparkSession


def advance_etl_cutoff(spark: SparkSession, new_cutoff: datetime) -> None:
    """Advance the purchase_staging watermark.

    Must only be called after TASK-014's MERGE has committed successfully and QV-001
    (TASK-017) has passed — the orchestration config (TASK-020) gates this call; this
    function performs no success check of its own, so no watermark advance occurs on a
    failed or QV-001-failed run only if the caller withholds invocation accordingly.
    """
    spark.sql(
        """
        UPDATE purchasing.meta.etl_cutoff
        SET last_cutoff = :new_cutoff, updated_at = current_timestamp()
        WHERE entity_name = 'purchase_staging'
        """,
        new_cutoff=new_cutoff,
    )


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    advance_etl_cutoff(spark, new_cutoff=datetime.utcnow())
