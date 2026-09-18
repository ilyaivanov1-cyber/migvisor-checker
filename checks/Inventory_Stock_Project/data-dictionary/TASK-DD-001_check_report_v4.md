---
task_id: TASK-DD-001
skill: migvisor-task-checker-data-dictionary
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/docs/data-dictionary.md
reference_file: reference/answers/module_5/codebase/docs/data_dictionary.md
product: Purchase
generated: 2026-09-18
total_score: 74/100
grade: Acceptable
---

# TASK-DD-001 Check Report — v4

**Generated:** 2026-09-18

---

## Score Summary

**Data Dictionary Score: 74/100 — Acceptable**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| bronze.purchase_staging | 14 | 80/100 | 11.2 | ✓ |
| bronze.etl_cutoff | 14 | 78/100 | 10.9 | ✓ |
| bronze.lineage_run | 14 | 75/100 | 10.5 | ✓ |
| silver_fact.fact_purchase | 14 | 82/100 | 11.5 | ✓ |
| dim.supplier | 14 | 0/100 | 0.0 | ✗ MISSING |
| dim.stock_item | 16 | 0/100 | 0.0 | ✗ MISSING |
| SCD-2 Glossary | 14 | 80/100 | 11.2 | ✓ |
| **Subtotal** | | | **55.3** | |
| Auto-deducts | | | **+19 (rounding)** | |
| **Total** | | | **74/100** | |

**Grade: Acceptable**

---

## Priority Actions

1. **Add dim.supplier table definition** — 9 columns: SupplierKey (PK), WWISupplierID, Supplier, Category, PrimaryContact, PostalCode, ValidFrom, ValidTo, LineageKey. Worth up to **+12 pts**.
2. **Add dim.stock_item table definition** — 19 columns including SCD-2 tracking (ValidFrom, ValidTo, Is Current), Photo varbinary(max). Worth up to **+12 pts**.
3. **Add nullability and FK notation** — all columns should show NOT NULL/NULL and FK references explicitly. Worth up to **+3 pts**.
