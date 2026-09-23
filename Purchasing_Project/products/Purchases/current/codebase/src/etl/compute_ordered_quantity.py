"""
TASK-012: Compute ordered_quantity
Design ref: design.md §3.1 Calculations — CALC-001.
Requirements: FR-004
Depends on: TASK-009 (extraction, via the resolved-keys chain TASK-010/TASK-011)
"""

from pyspark.sql import DataFrame, SparkSession


def compute_ordered_quantity(spark: SparkSession) -> DataFrame:
    """Compute ordered_quantity = ordered_outers * quantity_per_outer for every row in
    `stg_with_keys` (TASK-011's output). The value is materialized in transformation
    code here, not via a GENERATED ALWAYS AS DDL clause (FR-004). Registers the result
    as the `stg_resolved` temp view for TASK-014 to consume.
    """
    df = spark.sql(
        """
        SELECT
          *,
          ordered_outers * quantity_per_outer AS ordered_quantity
        FROM stg_with_keys
        """
    )
    df.createOrReplaceTempView("stg_resolved")
    return df


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    compute_ordered_quantity(spark)
