# Go-Live Checklist Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 78/100 (Good)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| 1. Infrastructure | 15 | 82 | All five items present; schema names adapted correctly to bronze/silver_dim/silver_fact/mart |
| 2. Data | 15 | 80 | Sentinel rows and etl_cutoff init present; entity name `fact_purchase` vs reference `purchase` minor difference |
| 3. Security | 14 | 85 | All security items covered; PII check noted as generic text vs reference's specific notebook name `nb_pii_compliance_check` |
| 4. Pipeline | 14 | 75 | Missing `deploy_workflow.sh --env prod` deployment step; lineage check uses `bronze.lineage_run` (correct adaptation) |
| 5. Data Quality | 14 | 65 | DQ file path differs (`tests/` vs `config/`); specific DQR-001/002/003/004/005/006 severity mapping not listed |
| 6. BI | 14 | 80 | Both mart views checked for correct principals; references bi_connections.md correctly |
| 7. Documentation | 14 | 78 | All seven doc files referenced; file name differences (runbook.md vs pipeline_runbook.md, data-dictionary.md vs data_dictionary.md) |

## Auto-deducts

None.

## Summary

The go-live checklist scored 78/100 (Good) with solid coverage across all seven sections. The Data Quality section is the weakest at 65/100 because the DQ assertions file path is `tests/dq_assertions_purchase.yaml` rather than the expected `config/dq_assertions_purchase.yaml`, and the specific DQR rule IDs (DQR-001 through DQR-006) with their blocking/informational severity labels are not enumerated. The Pipeline section is missing the `deploy_workflow.sh --env prod` deployment command as an explicit checklist item. The Security section is slightly weaker because PII compliance is referenced generically rather than as the specific `nb_pii_compliance_check` notebook.

## Priority Actions

1. Update DQ section: correct DQ assertions file path to `config/dq_assertions_purchase.yaml` and add explicit DQR-001/004/005/006 (BLOCKING) and DQR-002/003 (Informational) severity labels — +7 pts
2. Add `deploy_workflow.sh --env prod` as an explicit Pipeline checklist item and reference the specific lineage status column — +5 pts
