# Product Transformation Rules: Purchases

| Field | Value |
|---|---|
| Project | Purchasing_Project |
| Inherits from | Purchasing_Project project-transformation-rules, version `20260921-161200` |
| Generated | 2026-09-21 |
| Active dimensions | 9 |

---

## Customization Summary

| Action | Count |
|---|---|
| Overrides | 0 |
| Extensions | 0 |
| Deactivations | 0 |
| New rules (product-only dimensions) | 4 |

No overrides, extensions, or deactivations were required against Purchasing_Project's project-level rules — all 7 project dimensions (PL, NM, TY, OB, SX, PE, LN) already cover Purchases' evidenced patterns directly, since Purchasing_Project's rules were authored with Purchases as the sole founding product. Two net-new, product-only dimensions were required: **CX** (Custom) for a business-logic gap not addressed by any project dimension, and **QA** (Quality) for product-specific data-quality monitoring not addressed by any project dimension.

This product was relocated from GlobalSales_Project into its own standalone project, Purchasing_Project (see `migVisor_workspace/Purchasing_Project/project/current/project-transformation-rules/project-transformation-rules.md` §"Open Questions" for the architectural decisions the split created). This rule set was regenerated against Purchasing_Project's newly authored project rules; the 7 inherited dimensions were verified unchanged, and the 2 product-only dimensions (CX, QA) had stale GlobalSales_Project-era references (project name, `globalsales` catalog name, `fact_purchase` table name, and cross-referenced rule IDs) corrected to Purchasing_Project's naming and rule numbering.

---

## Dimension Table

| Dimension | Prefix | File | Rule Count | Customizations |
|---|---|---|---|---|
| Platform | PL | [PL-platform.yaml](PL-platform.yaml) | 10 | None — inherited unchanged |
| Naming | NM | [NM-naming.yaml](NM-naming.yaml) | 10 | None — inherited unchanged |
| Types | TY | [TY-types.yaml](TY-types.yaml) | 29 | None — inherited unchanged |
| Objects | OB | [OB-objects.yaml](OB-objects.yaml) | 10 | None — inherited unchanged |
| Syntax | SX | [SX-syntax.yaml](SX-syntax.yaml) | 11 | None — inherited unchanged |
| Performance | PE | [PE-performance.yaml](PE-performance.yaml) | 8 | None — inherited unchanged |
| Lineage | LN | [LN-lineage.yaml](LN-lineage.yaml) | 7 | None — inherited unchanged |
| Custom | CX | [CX-custom.yaml](CX-custom.yaml) | 1 | `[new]` product-only dimension |
| Quality | QA | [QA-quality.yaml](QA-quality.yaml) | 3 | `[new]` product-only dimension |

**Total rules: 89** (85 inherited + 4 new product-only)

---

## Rule Index

### PL — Platform (10 rules, inherited unchanged)

Full rule text: [PL-platform.yaml](PL-platform.yaml). Rule IDs PL-001 through PL-010 — see the project-level index for intents. Note PL-008 and PL-009 remain `[USER INPUT REQUIRED]` (cross-catalog dimension sharing and downstream dependency exposure created by the project split).

### NM — Naming (10 rules, inherited unchanged)

Full rule text: [NM-naming.yaml](NM-naming.yaml). Rule IDs NM-001 through NM-010.

### TY — Types (29 rules, inherited unchanged)

Full rule text: [TY-types.yaml](TY-types.yaml). Rule IDs TY-001 through TY-029.

### OB — Objects (10 rules, inherited unchanged)

Full rule text: [OB-objects.yaml](OB-objects.yaml). Rule IDs OB-001 through OB-010. Note OB-002 and OB-008 remain `[USER INPUT REQUIRED]`.

### SX — Syntax (11 rules, inherited unchanged)

Full rule text: [SX-syntax.yaml](SX-syntax.yaml). Rule IDs SX-001 through SX-011.

### PE — Performance (8 rules, inherited unchanged)

Full rule text: [PE-performance.yaml](PE-performance.yaml). Rule IDs PE-001 through PE-008.

### LN — Lineage (7 rules, inherited unchanged)

Full rule text: [LN-lineage.yaml](LN-lineage.yaml). Rule IDs LN-001 through LN-007.

### CX — Custom (1 rule) `[new]`

| Rule ID | Intent | Tag |
|---|---|---|
| CX-P01 | Preserve `ordered_quantity` on `purchasing.fact.purchase` as an explicitly stored, once-computed derived measure (`ordered_outers x quantity_per_outer`), never as a Delta `GENERATED ALWAYS AS` computed column — no project-level rule addresses ETL-computed business measures (TY-029 covers only DDL-level computed columns). Cross-references PE-007 (MERGE/replace load pattern) and OB-005 (ETL task translation). | `[new]` |

### QA — Quality (3 rules) `[new]`

| Rule ID | Intent | Tag |
|---|---|---|
| QA-001 | Row-count reconciliation between the staged batch and post-load `purchasing.fact.purchase`, closing the DELETE-then-INSERT replace-pattern risk. | `[new]` |
| QA-002 | Monitor the Unknown-key-0 fallback rate for `supplier_key`/`stock_item_key` valid-time resolution against `purchasing.dim.supplier`/`purchasing.dim.stock_item`. | `[new]` |
| QA-003 | Referential-integrity LEFT ANTI JOIN assertions for `purchasing.fact.purchase` foreign keys against `purchasing.dim.supplier`, `purchasing.dim.stock_item`, `purchasing.dim.date`. | `[new]` |

---

## Open Questions Carried Forward

Unchanged from the project-level rule set — these are stakeholder/architecture decisions, not resolved by this regeneration pass:

1. **Cross-catalog conformed dimension sharing strategy** (PL-008, OB-002) — `[USER INPUT REQUIRED]`.
2. **Cross-catalog downstream dependency exposure** (PL-009, OB-008) — `[USER INPUT REQUIRED]`.
