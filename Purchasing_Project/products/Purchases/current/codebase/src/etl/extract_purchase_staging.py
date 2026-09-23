"""
TASK-009: Incremental extraction into purchasing.stg.purchase_staging
Design ref: design.md §2 Ingestion, row 1; §3.2 Filters — FLT-001.
Requirements: FR-001
Depends on: TASK-001 (stg.purchase_staging DDL), TASK-006 (meta.etl_cutoff DDL)
"""

from datetime import datetime, timezone

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

from assign_lineage_key import begin_batch


def extract_purchase_staging(spark: SparkSession, new_cutoff: datetime) -> int:
    """Extract source rows modified since the prior watermark into purchasing.stg.purchase_staging.

    :param spark: active SparkSession
    :param new_cutoff: upper bound (inclusive) for this run's extraction window; caller-supplied,
        never hard-coded (per TASK-009 acceptance criteria)
    :return: lineage_key issued for this batch (TASK-013 begin_batch), stamped on every extracted row
        so the NOT NULL lineage_key column on purchasing.stg.purchase_staging is always satisfied
    """
    lineage_key, _run_id = begin_batch(spark)

    prior_cutoff = spark.sql(
        "SELECT last_cutoff FROM purchasing.meta.etl_cutoff WHERE entity_name = 'purchase_staging'"
    ).collect()[0]["last_cutoff"]

    extracted = spark.sql(
        """
        SELECT
          wwi_purchase_order_id,
          wwi_supplier_id,
          wwi_stock_item_id,
          transaction_date,
          ordered_outers,
          quantity_per_outer,
          received_outers,
          last_modified_when
        FROM source.purchase_order_lines
        WHERE last_modified_when > :prior_cutoff
          AND last_modified_when <= :new_cutoff
        """,
        prior_cutoff=prior_cutoff,
        new_cutoff=new_cutoff,
    ).withColumn("lineage_key", lit(lineage_key))

    # Transient, write-once-read-once landing table (Design §1.4) — truncate before writing this batch.
    spark.sql("TRUNCATE TABLE purchasing.stg.purchase_staging")
    extracted.write.mode("append").saveAsTable("purchasing.stg.purchase_staging")

    return lineage_key


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    extract_purchase_staging(spark, new_cutoff=datetime.now(timezone.utc))
