# BI Connections Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 87/100 (Good)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| 1. Overview | 20 | 85 | Correct structure; catalog name `inventory_stock.mart` vs reference `globalpurchase.mart` — correct product adaptation |
| 2. Connection Details per Mart View | 20 | 88 | Both views (v_purchase_by_supplier as MV, v_purchase_per_stock_item as standard view) correctly typed and documented |
| 3. Connecting BI Tools | 20 | 85 | SQL Warehouse endpoint and Power BI/Tableau steps present; catalog placeholder adapted correctly |
| 4. Known Issues and Workarounds | 20 | 82 | Both issues addressed; references `bronze.lineage_run` (correct for this product) vs reference `stg.lineage` |
| 5. Access Provisioning | 20 | 95 | Identical to reference; contact instructions and role escalation path correct |

## Auto-deducts

None.

## Summary

The BI connections document scored 87/100 (Good) — one of the highest scores among the newly-submitted codebase deliverables. All five sections are present with complete content. The document is correctly adapted from the reference using the `inventory_stock` catalog name throughout. The Known Issues section references `bronze.lineage_run.was_successful = true` which is semantically correct for this product's naming convention. The Access Provisioning section is essentially perfect.

## Priority Actions

1. Add a section explaining the `bronze.lineage_run` monitoring check vs the reference's `stg.lineage` pattern — helps ops teams unfamiliar with this product's naming — +5 pts
2. Add the sample query for `v_purchase_by_supplier` analogous to the `v_purchase_per_stock_item` aggregate query, for a more symmetric connection guide — +4 pts
