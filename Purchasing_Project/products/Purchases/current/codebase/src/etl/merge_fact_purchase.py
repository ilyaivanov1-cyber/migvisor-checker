"""
TASK-014: Delta MERGE load into purchasing.fact.purchase
Design ref: design.md §1.2 Attributes — fact.purchase; §3.1 Calculations. Requirements: FR-006.
Depends on: TASK-007 (fact.purchase DDL), TASK-010, TASK-011, TASK-012, TASK-013

Consumes the `stg_resolved` temp view produced by TASK-010/011/012 (supplier_key,
stock_item_key, ordered_quantity already resolved) and the lineage_key stamped on
every row during extraction (TASK-009 via TASK-013 begin_batch). date_key is derived
deterministically from transaction_date (Design §2 Ingestion row 4 — declarative FK
target only, no active load-time lookup against dim.date is performed).
"""

from pyspark.sql import SparkSession


def merge_fact_purchase(spark: SparkSession) -> None:
    """Scoped Delta MERGE keyed on wwi_purchase_order_id (FR-006)."""
    spark.sql(
        """
        MERGE INTO purchasing.fact.purchase AS target
        USING (
          SELECT
            wwi_purchase_order_id,
            supplier_key,
            stock_item_key,
            CAST(date_format(transaction_date, 'yyyyMMdd') AS BIGINT) AS date_key,
            ordered_outers,
            quantity_per_outer,
            ordered_quantity,
            received_outers,
            lineage_key
          FROM stg_resolved
        ) AS source
        ON target.wwi_purchase_order_id = source.wwi_purchase_order_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
        """
    )


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    merge_fact_purchase(spark)
