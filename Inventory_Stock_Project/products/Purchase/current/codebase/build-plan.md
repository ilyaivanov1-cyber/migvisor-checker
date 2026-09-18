# SmartBuilder Build Plan: Purchase

_Product: Purchase | Project: Inventory_Stock_Project | Generated: 2026-09-07_
_Derived from: `specifications/development_plan/design.md` + `specifications/development_plan/tasks.md`_
_SDD version: 4.1 | Manifest: `products/Purchase/current/_manifest.yaml`_

---

## Overview

| Field | Value |
|---|---|
| **Product** | Purchase |
| **Project** | Inventory_Stock_Project |
| **Target catalog** | `inventory_stock` (Databricks Delta Lake Unity Catalog) |
| **Total tasks** | 26 |
| **Execution phases** | 3 |
| **Primary skill** | `/smartbuilder_generate-db` (Phase 1) + `/smartbuilder_generate-etl` (Phases 2–3) |

**Task breakdown by type:**

| Type | Count | Phase |
|---|---|---|
| DDL | 8 | Phase 1 |
| ETL | 9 | Phase 2 |
| Config | 2 | Phase 2 |
| Test | 3 | Phase 3 |
| BI | 2 | Phase 3 |
| Docs | 2 | Phase 3 |
| **Total** | **26** | |

---

## Codebase Layout

All generated artifacts are placed under `products/Purchase/current/codebase/`:

```
codebase/
├── config/
│   ├── environment.yaml                          # TASK-018
│   └── workflows/
│       └── nightly_etl_purchase.json             # TASK-019
├── docs/
│   ├── design.md                                 # TASK-025
│   └── data-dictionary.md                        # TASK-026
├── src/
│   ├── common/
│   │   ├── constants.py                          # TASK-009
│   │   ├── scd2_merge.py                         # TASK-010
│   │   ├── sk_resolver.py                        # TASK-011
│   │   ├── fact_merge.py                         # TASK-012
│   │   └── udfs.py                               # TASK-013
│   ├── db/
│   │   ├── ddl/
│   │   │   ├── bronze_lineage_run.sql             # TASK-001
│   │   │   ├── bronze_etl_cutoff.sql              # TASK-002
│   │   │   ├── bronze_purchase_staging.sql        # TASK-003
│   │   │   ├── bronze_dq_rejections.sql           # TASK-004
│   │   │   ├── silver_fact_fact_purchase.sql      # TASK-005
│   │   │   ├── silver_dim_supplier_current.sql    # TASK-006
│   │   │   └── silver_dim_stock_item_current.sql  # TASK-007
│   │   └── grants/
│   │       └── purchase_grants.sql                # TASK-008
│   ├── etl/
│   │   ├── nb_extract_watermark.py               # TASK-014
│   │   ├── nb_extract_purchase.py                # TASK-015
│   │   └── migrate_staged_purchase_data.py       # TASK-016
│   └── init/
│       └── reseed_purchase_environment.py        # TASK-017
└── tests/
    ├── common/
    │   ├── test_sk_resolver.py                   # TASK-020
    │   └── test_udfs.py                          # TASK-021
    └── etl/
        └── test_migrate_staged_purchase_data.py  # TASK-022
```

_BI reconnection specs (TASK-023, TASK-024) are delivered as Markdown documents in `docs/bi/`._

---

## Execution Phases

### Phase 1 — Database Layer (DDL)

**Skill:** `/smartbuilder_generate-db`
**Parallelism:** TASK-001, TASK-002, TASK-006, TASK-007 can run in parallel (no dependencies). TASK-003, TASK-004, TASK-005 depend on TASK-001 or TASK-002. TASK-008 depends on TASK-001, TASK-003, TASK-004, TASK-005.

**Execution order within Phase 1:**

```
Batch 1 (parallel): TASK-001, TASK-002, TASK-006, TASK-007
Batch 2 (parallel): TASK-003, TASK-004, TASK-005   ← after TASK-001 + TASK-002
Batch 3 (sequential): TASK-008                      ← after Batch 2
```

| Task ID | Title | Output File | Dependencies |
|---|---|---|---|
| TASK-001 | Create `bronze.lineage_run` | `src/db/ddl/bronze_lineage_run.sql` | — |
| TASK-002 | Create `bronze.etl_cutoff` | `src/db/ddl/bronze_etl_cutoff.sql` | — |
| TASK-003 | Create `bronze.purchase_staging` | `src/db/ddl/bronze_purchase_staging.sql` | TASK-001, TASK-002 |
| TASK-004 | Create `bronze.dq_rejections` | `src/db/ddl/bronze_dq_rejections.sql` | TASK-001 |
| TASK-005 | Create `silver_fact.fact_purchase` | `src/db/ddl/silver_fact_fact_purchase.sql` | TASK-001 |
| TASK-006 | Create `silver_dim.supplier_current` view | `src/db/ddl/silver_dim_supplier_current.sql` | — |
| TASK-007 | Create `silver_dim.stock_item_current` view | `src/db/ddl/silver_dim_stock_item_current.sql` | — |
| TASK-008 | Unity Catalog GRANT statements | `src/db/grants/purchase_grants.sql` | TASK-001, TASK-003, TASK-004, TASK-005 |

**Phase 1 acceptance gate:** 7 DDL files exist under `src/db/ddl/`; grants file exists at `src/db/grants/purchase_grants.sql`; each file begins with the CX-P006 standard header block; `grep -c '-- RULES    : $' src/db/ddl/*.sql` returns 0.

---

### Phase 2 — ETL Pipeline + Configuration

**Skill:** `/smartbuilder_generate-etl`
**Parallelism:** TASK-009 (constants) and TASK-010 (scd2_merge) can run in parallel. TASK-011, TASK-012, TASK-013 depend on TASK-009. TASK-018 (environment.yaml) has no dependencies. Notebooks are sequential: TASK-014 → TASK-015 → TASK-016 → TASK-017.

**Execution order within Phase 2:**

```
Batch 1 (parallel): TASK-009, TASK-010, TASK-018
Batch 2 (parallel): TASK-011, TASK-012, TASK-013   ← after TASK-009
Batch 3 (sequential): TASK-014                     ← after TASK-009
Batch 4 (sequential): TASK-015                     ← after TASK-014
Batch 5 (sequential): TASK-016                     ← after TASK-011, TASK-012, TASK-014, TASK-015
Batch 6 (sequential): TASK-017                     ← after TASK-016 (optional; init notebook)
Batch 7 (sequential): TASK-019                     ← after TASK-014, TASK-015, TASK-016
```

| Task ID | Title | Output File | Dependencies |
|---|---|---|---|
| TASK-009 | `src/common/constants.py` | `src/common/constants.py` | TASK-001, TASK-003, TASK-005 (DDL complete) |
| TASK-010 | `src/common/scd2_merge.py` | `src/common/scd2_merge.py` | — |
| TASK-011 | `src/common/sk_resolver.py` | `src/common/sk_resolver.py` | TASK-009 |
| TASK-012 | `src/common/fact_merge.py` | `src/common/fact_merge.py` | TASK-009 |
| TASK-013 | `src/common/udfs.py` | `src/common/udfs.py` | TASK-009 |
| TASK-014 | `src/etl/nb_extract_watermark.py` | `src/etl/nb_extract_watermark.py` | TASK-009, TASK-001, TASK-002 (DDL complete) |
| TASK-015 | `src/etl/nb_extract_purchase.py` | `src/etl/nb_extract_purchase.py` | TASK-009, TASK-003 (DDL complete), TASK-014 |
| TASK-016 | `src/etl/migrate_staged_purchase_data.py` | `src/etl/migrate_staged_purchase_data.py` | TASK-011, TASK-012, TASK-014, TASK-015 |
| TASK-017 | `src/init/reseed_purchase_environment.py` | `src/init/reseed_purchase_environment.py` | TASK-001–005 (DDL complete) |
| TASK-018 | `config/environment.yaml` | `config/environment.yaml` | — |
| TASK-019 | Workflow JSON | `config/workflows/nightly_etl_purchase.json` | TASK-014, TASK-015, TASK-016 |

**Key design constraints enforced in Phase 2:**

| Constraint | Rule | Enforced in |
|---|---|---|
| Standard notebook skeleton (6 sections in order) | NFR-009, CX-P005 | TASK-014, TASK-015, TASK-016, TASK-017 |
| Lineage-close via direct `spark.sql UPDATE` in except block | NFR-009 | TASK-014, TASK-016 |
| No hard-coded date literals | FR-009, CX-P001 | TASK-014, TASK-015, TASK-016 |
| SK resolution: temporal range join + DESC tie-breaker + COALESCE to 0 | FR-004, FR-005, CALC-002, CALC-003 | TASK-011 |
| MERGE INTO keyed on `wwi_purchase_order_id` | FR-007 | TASK-012, TASK-016 |
| OPTIMIZE conditional on `rows_merged > 10,000` | FR-008, PE-P002 | TASK-016 |
| Row count reconciliation raises RuntimeError | NFR-003, DQR-001 | TASK-016 |
| DQ rejections written to `bronze.dq_rejections` with `lineage_key` | NFR-004, NFR-007 | TASK-016 |

**Phase 2 acceptance gate:** All 11 ETL/config files exist; static scan of `src/etl/` finds zero hard-coded ISO date literals; every notebook file contains the 6-section skeleton in order; `config/environment.yaml` contains `purchase.etl.fact_optimize_row_threshold`.

---

### Phase 3 — Tests, BI Specs, Documentation

**Skill:** `/smartbuilder_generate-etl`
**Parallelism:** TASK-020, TASK-021, TASK-023, TASK-024, TASK-025, TASK-026 can all run in parallel after Phase 2. TASK-022 depends on TASK-016 (Phase 2 complete).

| Task ID | Title | Output File | Dependencies |
|---|---|---|---|
| TASK-020 | `tests/common/test_sk_resolver.py` | `tests/common/test_sk_resolver.py` | TASK-011 |
| TASK-021 | `tests/common/test_udfs.py` | `tests/common/test_udfs.py` | TASK-013 |
| TASK-022 | `tests/etl/test_migrate_staged_purchase_data.py` | `tests/etl/test_migrate_staged_purchase_data.py` | TASK-016 |
| TASK-023 | BI spec: `wwidw_purchase_and_sale_per_stockitem_dynamic` | `docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic.md` | TASK-005 |
| TASK-024 | BI spec: `wwidw_ordered_by_supplier` | `docs/bi/wwidw_ordered_by_supplier.md` | TASK-005 |
| TASK-025 | `docs/design.md` | `docs/design.md` | TASK-016 |
| TASK-026 | `docs/data-dictionary.md` | `docs/data-dictionary.md` | TASK-005 |

**Phase 3 acceptance gate:** All 7 test/BI/docs files exist; TASK-020 covers all three SK resolution scenarios (match → non-zero, no-match → 0, multiple versions → most recent); TASK-022 covers the RuntimeError injection path (row count mismatch) and `close_lineage_record(succeeded=False)` call verification.

---

## Full Task Dependency Graph

```
                                  ┌─────────────────────────────────────────┐
                                  │             Phase 1 (DDL)               │
                                  │                                         │
TASK-001 ──┬──────────────────────┤──► TASK-003 ──► TASK-008               │
           │                      │                                         │
TASK-002 ──┘                      │──► TASK-004 ──► TASK-008               │
                                  │                                         │
TASK-001 ──────────────────────── │──► TASK-005 ──► TASK-008               │
TASK-006 (independent)            │                                         │
TASK-007 (independent)            │                                         │
                                  └─────────────────────────────────────────┘
                                                   │
                                                   ▼
                                  ┌─────────────────────────────────────────┐
                                  │          Phase 2 (ETL + Config)         │
                                  │                                         │
                         TASK-009 ──► TASK-011 ──┬──► TASK-016             │
                         TASK-010 (independent)   │                         │
                         TASK-018 (independent)   │                         │
                         TASK-009 ──► TASK-012 ──┘                         │
                         TASK-009 ──► TASK-013                              │
                         TASK-009 ──► TASK-014 ──► TASK-015 ──► TASK-016   │
                         TASK-016 → TASK-019 (workflow config)              │
                         TASK-017 (init; optional; after DDL complete)      │
                                  └─────────────────────────────────────────┘
                                                   │
                                                   ▼
                                  ┌─────────────────────────────────────────┐
                                  │       Phase 3 (Test + BI + Docs)        │
                                  │                                         │
                         TASK-020 (after TASK-011)                          │
                         TASK-021 (after TASK-013)                          │
                         TASK-022 (after TASK-016)                          │
                         TASK-023, TASK-024 (after TASK-005)               │
                         TASK-025, TASK-026 (after TASK-016/TASK-005)      │
                                  └─────────────────────────────────────────┘
```

---

## SDD Spec Cross-Reference

| Design Section | Tasks | Key Rules |
|---|---|---|
| §1 Data Model | TASK-001 through TASK-008 | NM-001, TY-P001, TY-P002, OB-001, OB-003, OB-P001, OB-P002, CX-P006, LN-001 |
| §2 Ingestion (watermark + extract) | TASK-014, TASK-015, TASK-018 | FR-001, FR-002, FR-003, CALC-001, CALC-005, CX-P001, CX-P005 |
| §3 Transformation (SK + MERGE) | TASK-010, TASK-011, TASK-012, TASK-016 | FR-004, FR-005, FR-007, FR-008, CALC-002, CALC-003, CALC-006, FLT-001–004, TY-P001, PE-P002 |
| §4 Serving | TASK-008, TASK-019, TASK-023, TASK-024 | FR-010, NFR-002, NFR-008, SE-001 |
| §5 Observability (DQ assertions) | TASK-016, TASK-004, TASK-022 | QA-P001–005, NFR-003–007, DQR-001–009 |

---

## Prerequisite Checks

Before executing Phase 1, verify:

| Check | Command |
|---|---|
| Databricks CLI configured | `databricks configure --check` |
| Unity Catalog `inventory_stock` accessible | `databricks catalogs get inventory_stock` |
| Target schemas exist | `SHOW SCHEMAS IN inventory_stock` returns `bronze`, `silver_dim`, `silver_fact` |
| SCD-2 dimension tables pre-loaded (external dependency) | `SELECT COUNT(*) FROM inventory_stock.silver_dim.supplier` returns > 0 |
| Source JDBC connectivity (PD-001 pending) | Confirm connection profile before TASK-015 extract is run |

---

## Pending Decisions (from SDD)

| ID | Blocks | Description |
|---|---|---|
| PD-001 | TASK-015, TASK-019 | Source JDBC connectivity — confirm connection profile and credentials for SQL Server 2014 incremental extract |
| PD-002 | TASK-017 | `reseed_purchase_environment.py` scope — requires scope owner sign-off before execution |
| PD-003 | TASK-008 | Unity Catalog access role matrix — role assignments not yet defined; GRANT statements in TASK-008 must be reviewed after PD-003 resolves |
| QA-DQ-01 | TASK-016, TASK-022 | Business DQ thresholds — acceptable failure rates for informational QA assertions; does not block code generation but affects test expectations |

---

_Build plan generated from `specifications/development_plan/tasks.md` (26 tasks) and `specifications/development_plan/design.md`._
_SmartBuilder version: 4.1 | Next skill: `/smartbuilder_generate-db Purchase TASK-001`_
