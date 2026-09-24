# Go-Live Checklist: Purchase Data Product

## 1. Infrastructure

- [ ] Unity Catalog created (`CREATE CATALOG inventory_stock` — CFG-003)
- [ ] All four schemas created: `bronze`, `silver_dim`, `silver_fact`, `mart` (CFG-003)
- [ ] Cluster policy applied (CFG-001)
- [ ] Databricks Workflow deployed and schedule active (CFG-002, CFG-009)
- [ ] Alert recipients configured (CFG-011)

## 2. Data

- [ ] `silver_dim.date` populated with 2000-01-01 to 2030-12-31 calendar (DB-007)
- [ ] `silver_dim.supplier` sentinel row (wwi_supplier_id=0) inserted
- [ ] `silver_dim.stock_item` sentinel row (wwi_stock_item_id=0) inserted
- [ ] `bronze.etl_cutoff` initialized for entity `fact_purchase` with HISTORY_ANCHOR_DATE
- [ ] All bronze tables exist and are empty on first run (DB-001 through DB-004)
- [ ] Fact table created and accepts MERGE operations (DB-008)

## 3. Security

- [ ] GRANT-001 through GRANT-004 applied (all principals have correct privileges)
- [ ] PII compliance check passed (zero hardcoded credentials)
- [ ] Dev and prod Secrets scopes created (`inventory-stock-dev`, `inventory-stock-prod`)
- [ ] All secret keys registered: `jdbc_url`, `jdbc_username`, `jdbc_password`
- [ ] `bi-service-principal` verified: can SELECT mart views, cannot MODIFY
- [ ] `etl-service-principal` verified: can SELECT+MODIFY silver_dim+silver_fact+mart, can REFRESH MV

## 4. Pipeline

- [ ] Workflow deployed and visible in Databricks Jobs UI with correct schedule
- [ ] Manual trigger of Workflow in dev completes end-to-end without errors
- [ ] `bronze.lineage_run` shows `was_successful = true` for the manual test run
- [ ] `bronze.etl_cutoff.last_cutoff_time` advanced after the manual test run

## 5. Data Quality

- [ ] `tests/dq_assertions_purchase.yaml` loaded and all DQR rules enabled
- [ ] Blocking DQR rules halt the pipeline on failure
- [ ] Informational DQR rules log to `bronze.dq_rejections` without stopping the pipeline
- [ ] `bronze.dq_rejections` table exists and is writable by `etl-service-principal`
- [ ] Test DQ failure: introduce a synthetic count mismatch, verify pipeline halts at nb_dq_assertions

## 6. BI

- [ ] `mart.v_purchase_by_supplier` queryable by `bi-service-principal`
- [ ] `mart.v_purchase_per_stock_item` queryable by `bi-service-principal`
- [ ] `purchase-analysts` can SELECT both mart views
- [ ] BI tool connection strings updated per `docs/bi/bi_connections.md`
- [ ] Sample queries return expected results

## 7. Documentation

- [ ] `docs/architecture_diagram.md` reviewed and accurate
- [ ] `docs/data-dictionary.md` covers all managed tables
- [ ] `docs/runbook.md` distributed to operations team
- [ ] `config/secrets_setup.md` and `config/secrets_rotation_runbook.md` available to platform team
- [ ] `docs/bi/bi_connections.md` distributed to BI consumers

---

**Completing all items above constitutes sufficient evidence for production readiness.**
