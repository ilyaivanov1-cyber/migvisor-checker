# To-Be Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 80/100 (Good)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| Overview | 17 | 82 | Target platform and approach clearly stated |
| Target Architecture | 17 | 85 | Medallion layers documented; UC catalog and schemas named |
| Data Model | 17 | 88 | Fact and dimension tables documented with schema |
| ETL Pipeline Design | 17 | 82 | Notebook sequence documented; MERGE strategy described |
| Migration Strategy | 16 | 76 | Phased approach present; historical load strategy adequate |
| Non-Functional Requirements | 16 | 60 | SLA targets, data retention policy, and UC permission model missing |

## Auto-deducts

None.

## Summary

The to-be design document scored 80/100 (Good), with consistent performance across all six sections — Overview, Target Architecture, Data Model, ETL Pipeline Design, and Migration Strategy all scored 76 to 88. The Non-Functional Requirements section is the weakest, lacking SLA targets, data retention policy, and UC permission model. The cross-domain view analytics.v_ordertoyearanalytics is not documented as a consumer of the target fact table. Priority fixes: add the Cross-Domain Views subsection (+3 pts) and expand the NFR section with SLA and retention policy (+3 pts). Adding a Technology Stack subsection with explicit Databricks, Delta, and UC versions recovers another +2 pts.

## Priority Actions

1. Add Cross-Domain Views subsection documenting analytics.v_ordertoyearanalytics — +3 pts
2. Expand NFR section with SLA targets, data retention policy, and UC permission model — +3 pts
