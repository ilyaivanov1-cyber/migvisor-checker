# UC Permission Audit Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 88/100 (Good)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| Catalog level | 25 | 90 | SHOW GRANTS ON CATALOG inventory_stock present; correct principal expectation comment |
| Schema level | 25 | 88 | All four schemas audited (bronze, silver_dim, silver_fact, mart); naming differs from reference (stg/dim/fact → bronze/silver_dim/silver_fact) — correct product adaptation |
| Table level | 25 | 85 | All tables covered: 4 bronze, 3 silver_dim, 1 silver_fact; lineage table named `lineage_run` vs reference `lineage` — minor naming divergence |
| Mart view level + Principal mapping | 25 | 88 | Both MV and standard view audited; principal-privilege mapping comment table is complete and accurate |

## Auto-deducts

None.

## Summary

The UC permission audit SQL scored 88/100 (Good) — comprehensive coverage across all four audit levels. The catalog, schema, table, and mart view grants are all audited with correct SHOW GRANTS statements. The principal-to-privilege mapping comment table at the bottom is complete with all expected grants for etl-service-principal, bi-service-principal, and purchase-analysts. The schema naming convention (`bronze/silver_dim/silver_fact/mart`) is the correct adaptation for this product, differing from the reference (`stg/dim/fact/mart`). The only minor issue is the lineage table audited as `lineage_run` while the reference audits `lineage` — this should be consistent with the actual DDL.

## Priority Actions

1. Verify the lineage table name is consistently `bronze.lineage_run` throughout (DDL, runbook, audit script) — name inconsistency could cause the SHOW GRANTS statement to target a non-existent table — +5 pts
2. Add explicit COMMENT on the catalog-level section explaining that USE CATALOG is expected for both service principals, mirroring the detail level of the table-level comments — +4 pts
