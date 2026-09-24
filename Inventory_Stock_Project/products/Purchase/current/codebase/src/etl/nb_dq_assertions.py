# Notebook: nb_dq_assertions
# Purpose : Execute Data Quality assertions against the resolved staging view.
#           Blocking rules halt the pipeline; informational rules log rejections.
# Rules   : DQR-001 through DQR-006, FR-009, NFR-004

import yaml
from datetime import datetime, timezone
from pyspark.sql import functions as F

from src.common.constants import DQ_REJECTIONS_TABLE

lineage_key = int(dbutils.jobs.taskValues.get(
    taskKey="nb_open_batch", key="lineage_key", debugValue=-1
))

# ── Load DQ rules ─────────────────────────────────────────────────────────────
with open("tests/dq_assertions_purchase.yaml", "r") as f:
    dq_config = yaml.safe_load(f)

rules = dq_config.get("rules", [])

# ── Run assertions ────────────────────────────────────────────────────────────
blocking_failures = []

for rule in rules:
    rule_id   = rule["rule_id"]
    severity  = rule["severity"]
    condition = rule["condition"]
    description = rule.get("description", "")

    # Count rows violating this rule
    violation_df = spark.sql(f"""
        SELECT *, '{rule_id}' AS rule_id, '{severity}' AS severity
        FROM resolved_staging
        WHERE NOT ({condition})
    """).withColumn("lineage_key", F.lit(lineage_key)) \
       .withColumn("detected_at", F.lit(datetime.now(timezone.utc).isoformat()))

    violation_count = violation_df.count()

    if violation_count > 0:
        # Write violations to dq_rejections table
        violation_df.select(
            "lineage_key", "rule_id", "severity", "detected_at"
        ).write.format("delta").mode("append").saveAsTable(DQ_REJECTIONS_TABLE)

        print(f"  [{severity}] {rule_id}: {violation_count} violations — {description}")

        if severity.upper() == "BLOCKING":
            blocking_failures.append(f"{rule_id}: {violation_count} violations")
    else:
        print(f"  [PASS] {rule_id}")

# ── Fail pipeline if any blocking rules fired ─────────────────────────────────
if blocking_failures:
    raise ValueError(
        f"Pipeline halted by {len(blocking_failures)} blocking DQ failure(s):\n"
        + "\n".join(f"  - {f}" for f in blocking_failures)
    )

print(f"nb_dq_assertions complete. All blocking rules passed. lineage_key: {lineage_key}")
