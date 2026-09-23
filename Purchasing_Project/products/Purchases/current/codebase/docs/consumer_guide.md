# Purchases — Consumer Guide

_TASK-023 | Design ref: design.md §4 Serving | Requirements: FR-007_

---

## Accessing `purchasing.fact.purchase`

`purchasing.fact.purchase` is the sole product surface exposed to cross-catalog consumers — no purchase-exclusive mart view is owned by this product. Three known consumers currently read this table directly across the catalog boundary (Design §4 Serving, row 1):

- `globalsales.mart.v_order_to_year_analytics`
- the "wwidw purchase and sale per stockitem dynamic" report
- the "wwidw-ordered-by-supplier" report

### Access profile

`[PENDING: TASK-016 not yet generated — cross-catalog exposure mechanism pending PL-009/OB-008]`. Once TASK-016 (`src/api/fact_purchase_access_profile.sql`) is generated, this section will document the confirmed access path — either a Unity Catalog cross-catalog `GRANT SELECT` or a federated/replicated read-only copy — and the exact object consumers should query.

### Governance

`[PENDING: TASK-021 not yet generated — access role matrix pending]`. Once TASK-021 (`config/fact_purchase_governance.sql`) is generated, this section will document the role/permission matrix and any row- or column-level security policy consumers must satisfy (NFR-003).

### Consumer validation

`[PENDING: TASK-022 — no BI-report generation skill is deployed in this package; see build-plan.md §4 Unmapped Tasks]`. Consumer-side access validation must be performed manually: run a representative query under each consumer role against `purchasing.fact.purchase` and confirm rows are returned without direct, ungoverned table access.
