# Check Report: architecture-diagram — Inventory_Stock_Project / Purchase

**Skill:** migvisor-task-checker-architecture-diagram (#14 of 21)
**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Checked:** 2026-09-25
**Score:** 82 / 100
**Grade:** Good

---

## Cross-File Reads

| File | Status | Notes |
|---|---|---|
| `specifications/to-be.md` | Read | Notebook names: nb_extract_watermark, nb_extract_purchase, migrate_staged_purchase_data; CLUSTER BY (date_key, supplier_key) on fact_purchase (2 columns); CDF enabled on lineage_run per LN-001 |
| `codebase/docs/data-dictionary.md` | Read | fact_purchase: no CDF; supplier/stock_item: CDF enabled; clustering on fact_purchase documented |

---

## Rubric Sections

### Section 1 — Overview and Layer Table

**Score: 18 / 18**

The Overview section defines the 4-layer medallion architecture with a correctly structured layer table:

| Layer | Schema | Role |
|---|---|---|
| Bronze | `inventory_stock.bronze` | Staging, watermark, lineage, DQ |
| Silver Dimension | `inventory_stock.silver_dim` | SCD-2 dimensions + date |
| Silver Fact | `inventory_stock.silver_fact` | Fact table via MERGE |
| Mart | `inventory_stock.mart` | BI-facing views |

All layer descriptions align with to-be.md §3.2 layer responsibilities. Catalog name `inventory_stock` is consistent throughout.

### Section 2 — Pipeline DAG

**Score: 28 / 33**

The ASCII art Pipeline DAG covers 4 labeled layers with named notebooks and target tables. Layer 1 (Ingestion/Bronze) shows the notebook execution sequence. Layer 2 (Dimensions) shows the orchestrator pattern. Layer 3 (Fact) shows SK resolution and MERGE. Layer 4 (DQ + Mart + Commit) shows the full DQ and mart refresh chain.

Cross-file check against to-be.md: to-be.md names three primary tasks: `nb_extract_watermark`, `nb_extract_purchase`, `migrate_staged_purchase_data`. The architecture diagram DAG expands this to a full notebook list consistent with the validation report's Build Output Detail section (which lists actual execution metrics for these notebooks), confirming they are genuinely part of the pipeline.

The extra notebooks are cross-file consistent:
- `nb_orchestrate_dimensions`, `nb_load_dim_supplier`, `nb_load_dim_stock_item`, `nb_populate_date_dim` — appear in validation report Build Output Detail ✓
- `nb_dq_smoke_tests`, `nb_dq_assertions`, `nb_dq_rejection_report` — appear in validation report ✓
- `nb_refresh_v_purchase_by_supplier`, `nb_refresh_v_purchase_per_stock_item`, `nb_optimize_mart` — appear in validation report ✓

Deductions:
- (-3) Two notebooks in Layer 1 (`nb_preflight_dim_check`, `nb_preflight_date_check`) do not appear in to-be.md, design.md, tasks.md, or the validation report's Build Output Detail. These appear to be architectural additions not grounded in the spec. No TASK-NNN is assigned to create them.
- (-2) The commit/watermark notebook is named `nb_advance_watermark` in the DAG, but to-be.md and design.md use the `set_etl_cutoff()` helper called from within `migrate_staged_purchase_data`. A standalone `nb_advance_watermark` task is not defined in tasks.md. This naming gap could indicate architectural drift from the spec.

### Section 3 — Delta Lake Table Properties

**Score: 18 / 25**

The Delta Lake Table Properties table covers all 8 Purchase product tables with CDF, Liquid Clustering, and Retention columns. The table is complete and aligned with data-dictionary.md for CDF flags (supplier and stock_item have CDF enabled; others disabled).

Cross-file inconsistency identified:
- Architecture diagram: `silver_fact.fact_purchase | Disabled | (date_key, supplier_key, stock_item_key) | 2555 days`
- design.md DDL: `CLUSTER BY (date_key, supplier_key)` — 2 columns only
- to-be.md §1.1: "CLUSTER BY (date_key, supplier_key)" — 2 columns only

The architecture diagram specifies 3 clustering keys for fact_purchase, but both design.md and to-be.md specify only 2 (date_key, supplier_key). This is a cross-file inconsistency. The reference architecture diagram also uses 3 columns `(date_key, supplier_key, stock_item_key)`, which suggests the intended behavior may be 3 columns and the design.md DDL may have an omission. However, the authoritative spec (design.md DDL, to-be.md) specifies 2.

Deductions:
- (-5) Clustering key count (3 in architecture vs 2 in design.md/to-be.md) is a cross-file inconsistency that must be resolved. The DDL should be the authoritative source; architecture diagram should match.
- (-2) CDF is shown as Disabled for `bronze.lineage_run`, but to-be.md explicitly states "CDF enabled on lineage_run per LN-001": "OB-004 etl_cutoff and lineage_run → bronze control Delta tables; CDF enabled on lineage_run (LN-001)." This is a cross-file inconsistency.

### Section 4 — lineage_key Propagation

**Score: 18 / 24**

The lineage_key Propagation section provides both a prose explanation and a tree diagram showing propagation from `bronze.lineage_run.lineage_key` (IDENTITY) to all downstream tables:
- bronze.purchase_staging.lineage_key ✓
- silver_dim.supplier.lineage_key ✓
- silver_dim.stock_item.lineage_key ✓
- silver_fact.fact_purchase.lineage_key ✓
- bronze.dq_rejections.lineage_key ✓

All 5 propagation paths are correct and consistent with data-dictionary.md FK documentation.

The failure signal description is correct: "A pipeline failure before `nb_advance_watermark` leaves `bronze.lineage_run.was_successful = false`." However, this should reference the actual commit step (which in the spec is handled by `close_lineage_record()` inside `migrate_staged_purchase_data`) rather than a standalone `nb_advance_watermark` notebook.

Deductions:
- (-4) The section references `nb_advance_watermark` as the commit step, but design.md §6 and to-be.md define `close_lineage_record()` as the lineage close function called within `migrate_staged_purchase_data`. The architecture diagram introduces a notebook name that contradicts the task design.
- (-2) The diagram does not show `bronze.purchase_staging.lineage_key` as a FK source — only as a propagation target. The lineage_key flows: lineage_run → purchase_staging → fact_purchase. The intermediate staging hop is correctly shown but the direction comment "constant on all rows in one extract" could be more precise.

---

## Cross-File Consistency Checks

**to-be.md alignment:**
- Catalog: `inventory_stock` ✓
- Schema naming: bronze, silver_dim, silver_fact, mart ✓
- Notebook names nb_extract_watermark, nb_extract_purchase ✓
- CLUSTER BY 2 columns (date_key, supplier_key) in to-be.md vs 3 columns in diagram ✗
- CDF on lineage_run (LN-001) in to-be.md vs CDF Disabled in diagram ✗
- Notebook `nb_advance_watermark` not in to-be.md or tasks.md ✗

**data-dictionary.md alignment:**
- CDF flags for supplier, stock_item ✓
- No CDF for fact_purchase ✓
- Retention periods match (90 days bronze staging, 2555 days silver) ✓

---

## Auto-Deducts

| Rule | Applied | Amount | Reason |
|---|---|---|---|
| Clustering key count inconsistency | Yes | -5 | Architecture shows 3 keys, design.md/to-be.md specify 2 |
| CDF on lineage_run inconsistency | Yes | -3 | Architecture shows Disabled, to-be.md explicitly enables CDF per LN-001 |

---

## Summary

The architecture diagram is a well-structured 4-section document with a comprehensive Layer Overview, detailed 4-layer ASCII Pipeline DAG, complete Delta Lake Table Properties table, and accurate lineage_key Propagation tree. The DAG's extra notebooks (dimension orchestration, DQ, mart) are confirmed by the validation report's Build Output Detail and are a strength. The cross-file inconsistencies discovered by mandatory file reads are material: the clustering key count for fact_purchase conflicts between this document (3 keys) and design.md/to-be.md (2 keys), and CDF on lineage_run is marked Disabled here but enabled in to-be.md per LN-001. The unspecified notebook `nb_advance_watermark` (not in tasks.md) also introduces architectural ambiguity.

---

## Priority Actions

1. Resolve clustering key inconsistency: verify the intended CLUSTER BY for fact_purchase — if the correct spec is 2 keys (date_key, supplier_key) per design.md §7 DDL and to-be.md §1.1, update the architecture table; if 3 keys is intended, update design.md DDL to match.
2. Update Delta Lake Table Properties: set CDF to `Enabled` for `bronze.lineage_run` consistent with LN-001 (to-be.md: "CDF enabled on lineage_run").
3. Remove or explain `nb_preflight_dim_check` and `nb_preflight_date_check` from the DAG — add corresponding TASK-NNN entries in tasks.md if these notebooks are intentional, or remove them from the DAG.
4. Replace `nb_advance_watermark` references in Sections 2 and 4 with the correct commit mechanism: `close_lineage_record()` called within `migrate_staged_purchase_data` as defined in design.md §6 and to-be.md §4.4.
