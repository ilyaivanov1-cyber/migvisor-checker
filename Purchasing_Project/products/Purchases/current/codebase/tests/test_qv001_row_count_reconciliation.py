"""
TASK-017: QV-001 row-count reconciliation assertion
Design ref: design.md §5.2 Validation Rules — QV-001. Requirements: NFR-004.
Depends on: TASK-014 (MERGE load)
"""

from pyspark.sql import SparkSession


class QV001ReconciliationError(Exception):
    """Raised when staged and post-load distinct wwi_purchase_order_id counts diverge."""


def assert_row_count_reconciliation(spark: SparkSession) -> None:
    """Blocking assertion (QA-001): mismatch halts the run before the watermark advances."""
    staged_count = spark.sql(
        "SELECT COUNT(DISTINCT wwi_purchase_order_id) AS n FROM purchasing.stg.purchase_staging"
    ).collect()[0]["n"]

    loaded_count = spark.sql(
        """
        SELECT COUNT(DISTINCT f.wwi_purchase_order_id) AS n
        FROM purchasing.fact.purchase AS f
        INNER JOIN (SELECT DISTINCT wwi_purchase_order_id FROM purchasing.stg.purchase_staging) AS s
          ON f.wwi_purchase_order_id = s.wwi_purchase_order_id
        """
    ).collect()[0]["n"]

    if staged_count != loaded_count:
        raise QV001ReconciliationError(
            f"QV-001 failed: staged distinct count={staged_count} != post-load count={loaded_count}. "
            "Blocking run before watermark advance (QA-001)."
        )


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    assert_row_count_reconciliation(spark)
