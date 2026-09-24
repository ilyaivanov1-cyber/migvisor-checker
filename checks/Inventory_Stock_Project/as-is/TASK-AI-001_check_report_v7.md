---
task_id: TASK-AI-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md
reference_file: reference/answers/module_2/1 as-is.md
checked_at: 2026-09-24T00:00:00
sections_evaluated: 6
total_score: 82/100
grade: Good
identical_to_reference: false
---

# Task Check Report — as-is (v7)
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md — workspace auto-detected
- Reference file: reference/answers/module_2/1 as-is.md — from workspace.yaml
- Product: Purchase — from workspace.yaml
- Sections in reference: 6 | Sections in participant: 6 (matched: 6)
- Point weights: auto-calculated — s1:18, s2:18, s3:17, s4:17, s5:15, s6:15

---

## Score Summary

**The as-is Score: 82**

| Section | Weight | Score | Status |
|---|---|---|---|
| 1. Definition | 18 | 17 | ✓ |
| 2. Consumers | 18 | 16 | ✓ |
| 3. Model/ER Diagram | 17 | 14 | ✓ |
| 4. Lineage (incl. Data Flow) | 17 | 15 | ✓ |
| 5. Calculations | 15 | 12 | ✓ |
| 6. Sources | 15 | 14 | ✓ |
| **Total** | **100** | **82** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Feedback

### 1. Definition (17/18)
Strong definition section with full metadata table (15 rows), correct product and fact table identification, SSIS pipeline described with confirmed staging-truncation bug called out explicitly, migration target (Databricks/Unity Catalog) documented.

### 2. Consumers (16/18)
All three named consumers present: `wwidw purchase and sale per stockitem dynamic`, `wwidw-ordered-by-supplier`, and `analytics.v_ordertoyearanalytics` with cross-domain coordination note. Internal ETL consumer (`migratestagedpurchasedata`) documented. The consumption method column is complete.

### 3. Model/ER Diagram (14/17)
Full Mermaid ER diagram present with all source tables, staging, control tables, and fact/dim relationships. Textual layer description table included. Minor: Bronze→Silver→Gold target mapping appears in section 4 (Lineage) rather than section 3 — split presentation reduces discoverability slightly.

### 4. Lineage (15/17)
Section 4.0 includes a comprehensive Bronze→Silver→Gold target data flow diagram with Delta table names per layer. Section 4.2 Mermaid lineage diagram covers OLTP→extract→staging→key resolution→fact→BI chain. Sections 4.3 (column-level lineage) and 4.4 (step-by-step transformation table with SQL) are complete and production-quality. Section 4.5 (downstream dependencies) covers all seven consumers and control table dependencies.

### 5. Calculations (12/15)
Three calculations documented: Date Key derivation, Ordered Outers/Ordered Quantity pass-through relationship, SCD-2 surrogate key resolution. Each has business purpose, formula, SQL code, and step-by-step calculation. Minor gap: no explicit note on fallback behaviour when Received Outers > Ordered Outers (DQ boundary condition not addressed as a calculation rule).

### 6. Sources (14/15)
**v7 fix applied:** Transformation Type column added to section 6.1 Input Source Tables. All 8 source objects now classified: Direct Load (PurchaseOrders, PurchaseOrderLines), Lookup/Enrichment (StockItems, PackageTypes), SCD-2 Merge (Suppliers), Passthrough (ETL Cutoff, Lineage, LineageKey). Section 6.2 Output Tables complete with all target objects. This closes the gap identified in v6.

---

## Priority Improvements

1. Consolidate Bronze→Silver→Gold data flow diagram into section 3 (Model) as well as section 4 for better navigability — +0 pts (cosmetic)
2. Add DQ boundary condition note to Calculations section for Received Outers constraint — +2 pts

---

## Next Step
You can proceed to the next task. Score 82/100 (Good).
