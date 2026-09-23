"""
TASK-019: QV-003 referential conformity assertions
Design ref: design.md §5.2 Validation Rules — QV-003. Requirements: NFR-006.
Depends on: TASK-008 (stg.dq_rejections DDL), TASK-014 (MERGE load)
"""

from pyspark.sql import SparkSession

_ASSERTIONS = [
    ("supplier_key", "purchasing.dim.supplier", "supplier_key"),
    ("stock_item_key", "purchasing.dim.stock_item", "stock_item_key"),
    ("date_key", "purchasing.dim.date", "date_key"),
]


def assert_referential_conformity(spark: SparkSession, lineage_key: int) -> None:
    """LEFT ANTI JOIN assertions of fact.purchase against each dimension. Non-blocking —
    orphaned rows are routed to purchasing.stg.dq_rejections rather than failing the run.
    """
    for fk_column, dim_table, dim_key in _ASSERTIONS:
        spark.sql(
            f"""
            INSERT INTO purchasing.stg.dq_rejections
              (rejection_id, lineage_key, assertion_id, source_table, source_key, rejection_reason, rejected_at)
            SELECT
              abs(hash(f.wwi_purchase_order_id, '{fk_column}')) AS rejection_id,
              {lineage_key} AS lineage_key,
              'QA-003' AS assertion_id,
              'purchasing.fact.purchase' AS source_table,
              f.wwi_purchase_order_id AS source_key,
              '{fk_column} does not resolve to {dim_table}.{dim_key}' AS rejection_reason,
              current_timestamp() AS rejected_at
            FROM purchasing.fact.purchase AS f
            LEFT ANTI JOIN {dim_table} AS d
              ON f.{fk_column} = d.{dim_key}
            """
        )


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    assert_referential_conformity(spark, lineage_key=0)
