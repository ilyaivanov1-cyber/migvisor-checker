# Data Dictionary Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 74/100 (Acceptable)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| bronze.purchase_staging | 12 | 78 | Columns documented; nullability and FK notation missing |
| bronze.etl_cutoff | 12 | 80 | Watermark table columns present |
| bronze.lineage_run | 12 | 75 | Run log columns documented |
| silver_fact.fact_purchase | 12 | 82 | Fact table columns and types documented |
| silver_dim.supplier | 13 | 0 | Entire table definition missing (9 columns) |
| silver_dim.stock_item | 13 | 0 | Entire table definition missing (19 columns including SCD-2 tracking) |
| SCD-2 Glossary | 13 | 78 | SCD-2 tracking fields explained |
| bronze.dq_rejections | 13 | 75 | DQ rejection log columns present |

## Auto-deducts

None.

## Summary

The data dictionary scored 74/100 (Acceptable), with the four Bronze/Silver tables (purchase_staging, etl_cutoff, lineage_run, fact_purchase) and the SCD-2 Glossary all scoring 75 to 82. The critical gap is two completely missing dimension table definitions: dim.supplier (9 columns) and dim.stock_item (19 columns including SCD-2 tracking fields), each worth approximately 12 pts. Nullability flags and FK notation are also absent across all table definitions. Adding dim.supplier and dim.stock_item are the top two priorities, together worth up to +24 pts and would push this score into the Excellent range.

## Priority Actions

1. Add dim.supplier table definition (9 columns with SCD-2 tracking fields) — +12 pts
2. Add dim.stock_item table definition (19 columns including SCD-2 tracking fields) — +12 pts
