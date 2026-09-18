# Go-Live Checklist: Purchase Data Product

## 1. Infrastructure

- [ ] Unity Catalog created (`CREATE CATALOG globalpurchase` — CFG-003)
- [ ] All four schemas created: `stg`, `dim`, `fact`, `mart` (CFG-003)
- [ ] Cluster policy applied (CFG-001)
- [ ] Databricks Workflow deployed and schedule active (CFG-002, CFG-009)
- [ ] Alert recipients configured (CFG-011)

## 2. Data

- [ ] `dim.date` populated with 2000-01-01 to 2030-12-31 calendar (DB-007)
- [ ] `dim.supplier` sentinel row (wwi_supplier_id=0) inserted
- [ ] `dim.stock_item` sentinel row (wwi_stock_item_id=0) inserted
- [ ] `stg.etl_cutoff` initialized for entity `purchase` with HISTORY_ANCHOR_DATE
- [ ] All staging tables exist and are empty on first run (DB-001 through DB-004)
- [ ] Fact table created and accepts MERGE operations (DB-008)

## 3. Security

- [ ] GRANT-001 through GRANT-004 applied (all principals have correct privileges)
- [ ] `nb_pii_compliance_check` passed (zero hardcoded credentials)
- [ ] Dev and prod Secrets scopes created (`globalpurchase-dev`, `globalpurchase-prod`)
- [ ] All secret keys registered: `jdbc_url`, `jdbc_username`, `jdbc_password`
- [ ] `bi-service-principal` verified: can SELECT mart views, cannot MODIFY
- [ ] `etl-service-principal` verified: can SELECT+MODIFY dim+fact+mart, can REFRESH MV

## 4. Pipeline

- [ ] `deploy_workflow.sh --env prod` executed successfully
- [ ] Workflow appears in Databricks Jobs UI with correct schedule
- [ ] Manual trigger of Workflow in dev completes end-to-end without errors
- [ ] `stg.lineage` shows `status = 'success'` for the manual test run
- [ ] `stg.etl_cutoff.last_cutoff_time` advanced after the manual test run

## 5. Data Quality

- [ ] `config/dq_assertions_purchase.yaml` loaded and all six DQR rules enabled
- [ ] DQR-001, DQR-004, DQR-005, DQR-006 are `severity: BLOCKING`
- [ ] DQR-002, DQR-003 are `severity: Informational`
- [ ] `nb_dq_smoke_tests` passes on a populated catalog
- [ ] `stg.dq_rejections` table exists and is writable by `etl-service-principal`
- [ ] Test DQ failure: introduce a synthetic count mismatch, verify pipeline halts at nb_dq_purchase

## 6. BI

- [ ] `mart.v_purchase_by_supplier` queryable by `bi-service-principal`
- [ ] `mart.v_purchase_per_stock_item` queryable by `bi-service-principal`
- [ ] `purchase-analysts` can SELECT both mart views
- [ ] BI tool connection strings updated per `config/bi_connections.md`
- [ ] Sample queries from `src/db/queries/bi_sample_queries.sql` return expected results

## 7. Documentation

- [ ] `docs/architecture_diagram.md` reviewed and accurate
- [ ] `docs/data_dictionary.md` covers all managed tables
- [ ] `docs/pipeline_runbook.md` distributed to operations team
- [ ] `config/secrets_setup.md` and `config/secrets_rotation_runbook.md` available to platform team
- [ ] `config/bi_connections.md` distributed to BI consumers

---

**Completing all items above constitutes sufficient evidence for production readiness.**
