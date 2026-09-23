"""
TASK-010: Resolve supplier_key via valid-time lookup
Design ref: design.md §3.1 Calculations — CALC-002.
Requirements: FR-002
Depends on: TASK-002 (dim.supplier DDL), TASK-009 (extraction)
"""

from pyspark.sql import DataFrame, SparkSession


def resolve_supplier_key(spark: SparkSession) -> DataFrame:
    """Resolve supplier_key for every row in purchasing.stg.purchase_staging via a
    valid-time range-join against purchasing.dim.supplier, falling back to the
    Unknown key 0 when no matching window is found. Registers the result as the
    `stg_with_supplier_key` temp view for TASK-011 to chain from.
    """
    df = spark.sql(
        """
        SELECT
          s.*,
          COALESCE(d.supplier_key, 0) AS supplier_key
        FROM purchasing.stg.purchase_staging AS s
        LEFT JOIN purchasing.dim.supplier AS d
          ON d.wwi_supplier_id = s.wwi_supplier_id
         AND s.transaction_date >= d.valid_from
         AND s.transaction_date <  d.valid_to
        """
    )
    df.createOrReplaceTempView("stg_with_supplier_key")
    return df


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    resolve_supplier_key(spark)
