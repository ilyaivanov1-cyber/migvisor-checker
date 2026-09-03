# Go-Live Checklist — Sales_Orders Pipeline
_TASK-DOCS-004 | CON-SEC-001, NFR-MAINT_

All items must be completed and signed off before promoting `nightly_etl_main` to production.

---

## Section 1: Pending Decision Gates (hard prerequisites)

| # | Decision | ID | Status | Owner | Sign-off |
|---|---|---|---|---|---|
| 1 | OLTP-direct connection strategy confirmed | CX-P04 | OPEN | Infrastructure / DE Lead | ☐ |
| 2 | Unity Catalog access role matrix finalised | CX-P05 | OPEN | Data Platform / Security Lead | ☐ |
| 3 | Business DQ thresholds confirmed | CX-DQ-01 | OPEN | Business / Data Governance Lead | ☐ |

**These three items are hard gates — production go-live cannot proceed until all are resolved.**

---

## Section 2: Security & Compliance

| # | Check | Owner | Sign-off |
|---|---|---|---|
| 4 | TASK-SEC-003 PII compliance notebook passed (CON-SEC-001) | Security Lead | ☐ |
| 5 | Unity Catalog column masks applied to dim.customer PII columns | DE Team | ☐ |
| 6 | RLS policies on fact.sale and fact.order deployed | Security Lead | ☐ |
| 7 | Databricks Secrets provisioned for all keys in `secrets_setup.md` | Infrastructure | ☐ |
| 8 | No credentials hard-coded in any notebook or config file | Code Review | ☐ |

---

## Section 3: Testing

| # | Check | Owner | Sign-off |
|---|---|---|---|
| 9 | All unit tests pass (`pytest tests/unit/`) | DE Team | ☐ |
| 10 | Integration tests pass against staging environment | DE Team | ☐ |
| 11 | End-to-end pipeline test (TASK-TEST-007) passed | DE Team | ☐ |
| 12 | Performance benchmark within NFR-PERF bounds (≤4h pipeline, ≤5s p95 mart query) | DE Team | ☐ |
| 13 | Code coverage ≥ 80% confirmed | DE Team | ☐ |

---

## Section 4: Operations

| # | Check | Owner | Sign-off |
|---|---|---|---|
| 14 | Pipeline runbook reviewed and approved by operations team | Ops Lead | ☐ |
| 15 | Data dictionary reviewed by data steward | Data Steward | ☐ |
| 16 | CI/CD pipeline configured and first deployment tested | DE Team | ☐ |
| 17 | Databricks Workflow `nightly_etl_main` deployed via `deploy_workflow.sh` | DE Team | ☐ |
| 18 | Monitoring and alerting configured (email/webhook recipients confirmed) | Ops Lead | ☐ |
| 19 | SQL Warehouse provisioned and BI connections validated | BI Team | ☐ |
| 20 | Delta table retention policies applied (bronze 90d / silver 7y / gold 3y) | DE Team | ☐ |

---

## Section 5: Data

| # | Check | Owner | Sign-off |
|---|---|---|---|
| 21 | Full historical load (2013-01-01 onward) completed successfully | DE Team | ☐ |
| 22 | dim.date populated through at least today + 5 years | DE Team | ☐ |
| 23 | All 9 BI reports reconnected to Databricks SQL endpoint | BI Team | ☐ |
| 24 | Power BI report owners validated data accuracy vs legacy system | BI Team / Business | ☐ |

---

## Final approval

| Role | Name | Date | Signature |
|---|---|---|---|
| Data Engineering Lead | | | |
| Security Lead | | | |
| Data Steward | | | |
| Operations Lead | | | |
| Business Owner | | | |
