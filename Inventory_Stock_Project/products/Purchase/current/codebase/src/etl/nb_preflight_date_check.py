# Notebook: nb_preflight_date_check
# Purpose : Verify that the date dimension is populated and covers the
#           required calendar range before the main ETL runs.
# Rules   : FR-011, NFR-003, DQR-006

from src.common.constants import DATE_DIM_TABLE

MIN_DATE = "2000-01-01"
MAX_DATE = "2030-12-31"

# ── Date dimension row count check ────────────────────────────────────────────
date_count = spark.sql(f"SELECT COUNT(*) AS cnt FROM {DATE_DIM_TABLE}").first()["cnt"]

if date_count == 0:
    raise ValueError(
        f"{DATE_DIM_TABLE} is empty. "
        "Populate the date dimension with calendar data from 2000-01-01 to 2030-12-31 first."
    )

# ── Date range coverage check ─────────────────────────────────────────────────
range_row = spark.sql(f"""
    SELECT
        MIN(calendar_date) AS min_date,
        MAX(calendar_date) AS max_date
    FROM {DATE_DIM_TABLE}
""").first()

min_date = str(range_row["min_date"])
max_date = str(range_row["max_date"])

if min_date > MIN_DATE:
    raise ValueError(
        f"Date dimension starts at {min_date}, expected {MIN_DATE} or earlier. "
        "Backfill the date dimension before running the pipeline."
    )

if max_date < MAX_DATE:
    raise ValueError(
        f"Date dimension ends at {max_date}, expected {MAX_DATE} or later. "
        "Extend the date dimension before running the pipeline."
    )

print(f"Date preflight OK. Row count: {date_count}, range: {min_date} — {max_date}")
