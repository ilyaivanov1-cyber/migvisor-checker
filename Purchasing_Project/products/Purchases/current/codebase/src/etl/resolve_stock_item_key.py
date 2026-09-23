"""
TASK-011: Resolve stock_item_key via valid-time lookup
Design ref: design.md §3.1 Calculations — CALC-003.
Requirements: FR-003
Depends on: TASK-003 (dim.stock_item access), TASK-009 (extraction)

Reads purchasing.dim.stock_item via whichever access mechanism TASK-003 established
(cross-catalog grant or duplicated copy) — no change to this join logic is required
regardless of which mechanism was chosen.
"""

from pyspark.sql import DataFrame, SparkSession


def resolve_stock_item_key(spark: SparkSession) -> DataFrame:
    """Resolve stock_item_key for every row in `stg_with_supplier_key` (TASK-010's output)
    via a valid-time range-join against purchasing.dim.stock_item, falling back to the
    Unknown key 0 when no matching window is found. Registers the result as the
    `stg_with_keys` temp view for TASK-012 to chain from.
    """
    df = spark.sql(
        """
        SELECT
          s.*,
          COALESCE(d.stock_item_key, 0) AS stock_item_key
        FROM stg_with_supplier_key AS s
        LEFT JOIN purchasing.dim.stock_item AS d
          ON d.wwi_stock_item_id = s.wwi_stock_item_id
         AND s.transaction_date >= d.valid_from
         AND s.transaction_date <  d.valid_to
        """
    )
    df.createOrReplaceTempView("stg_with_keys")
    return df


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    resolve_stock_item_key(spark)
