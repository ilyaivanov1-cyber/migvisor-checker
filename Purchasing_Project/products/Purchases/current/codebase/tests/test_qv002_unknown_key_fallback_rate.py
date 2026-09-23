"""
TASK-018: QV-002 unknown-key fallback-rate monitoring
Design ref: design.md §5.2 Validation Rules — QV-002. Requirements: NFR-005.
Depends on: TASK-010, TASK-011

[OWNER INPUT REQUIRED — pending QA-002]: the comparison threshold against the rolling
historical baseline is not yet business-confirmed. This check computes and records the
metric only; it never blocks the run.
"""

from pyspark.sql import SparkSession


def compute_unknown_key_fallback_rate(spark: SparkSession) -> float:
    """Share of the current batch (`stg_resolved`) where supplier_key or stock_item_key
    resolved to the Unknown key (0). Non-blocking — always returns, never raises.
    """
    row = spark.sql(
        """
        SELECT
          SUM(CASE WHEN supplier_key = 0 OR stock_item_key = 0 THEN 1 ELSE 0 END) AS unknown_rows,
          COUNT(*) AS total_rows
        FROM stg_resolved
        """
    ).collect()[0]

    total_rows = row["total_rows"] or 0
    if total_rows == 0:
        return 0.0
    return row["unknown_rows"] / total_rows


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    rate = compute_unknown_key_fallback_rate(spark)
    print(f"QV-002 unknown-key fallback rate for this batch: {rate:.4%}")
