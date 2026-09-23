# Check Report: data-dictionary
**Trainee:** Purchasing_Project
**Product:** Purchases
**Date:** 2026-09-23
**Score:** 72/100 — Acceptable

## Path Note
File found at: `products/Purchases/current/codebase/docs/data_dictionary.md` (underscore variant)
Expected path: `products/Purchases/current/codebase/docs/data-dictionary.md` (hyphen variant)
File content is valid; path variant is a minor naming inconsistency.

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| `purchasing.fact.purchase` | 25 | 88 | 9 columns with type, nullable, description; FK references documented; MERGE key and stored-column semantics noted |
| `purchasing.dim.supplier` | 20 | 85 | 7 columns with complete SCD2 fields (valid_from, valid_to, is_current); Unknown row usage noted |
| `purchasing.dim.stock_item` | 20 | 82 | 7 columns; [PENDING: PL-008/OB-002] marker is correct and honest |
| `purchasing.dim.date` | 15 | 80 | 2-column minimal definition; sufficient given date dimension is a reused cross-catalog object |
| Staging and Meta tables | 20 | 0 | stg.purchase_staging (9 cols), stg.dq_rejections (7 cols), meta.lineage, meta.sequence_state, meta.etl_cutoff — all absent from this document |

## Strengths
- The four covered tables (fact.purchase, dim.supplier, dim.stock_item, dim.date) are documented thoroughly with correct types, nullability, and meaningful descriptions.
- FK notation within descriptions is clear and traceable (e.g., `FK → dim.supplier.supplier_key`).
- The [PENDING: PL-008/OB-002] markers on dim.stock_item and dim.date correctly reflect the open cross-catalog sharing decision without hiding it.

## Gaps
- Staging and meta tables are entirely absent: stg.purchase_staging (9 cols), stg.dq_rejections (7 cols), meta.lineage, meta.sequence_state, meta.etl_cutoff are all missing — this represents 20 pts of weight.
- No SCD-2 glossary or terminology section (what valid_from/valid_to means, far-future sentinel value).
- The validation report confirms this scope was intentional per TASK-023 scope, but the reference data dictionary likely covers more table types.

## Priority Fixes
1. Add stg.purchase_staging and stg.dq_rejections table definitions (9 + 7 columns): +12 pts
2. Add meta.* table definitions (lineage, sequence_state, etl_cutoff): +8 pts
3. Add a SCD-2 Glossary or Terms section explaining valid-time column semantics: +4 pts
