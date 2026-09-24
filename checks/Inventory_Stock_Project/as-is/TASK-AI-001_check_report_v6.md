---
task_id: TASK-AI-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md
reference_file: reference/answers/module_2/1 as-is.md
checked_at: 2026-09-24T12:00:00
sections_evaluated: 6
total_score: 77/100
grade: Good
identical_to_reference: false
---

# Task Check Report — as-is (v6)
_Purchase | 2026-09-24_

## Score Summary

| Section | Weight | Score | Status |
|---|---|---|---|
| 1 Definition | 17 | 16 | ✓ |
| 2 Consumers | 17 | 16 | ✓ |
| 3 Model/ER Diagram | 17 | 15 | ✓ |
| 4 Lineage | 17 | 14 | ✓ |
| 5 Calculations | 16 | 10 | ⚠ |
| 6 Sources | 16 | 6 | ⚠ |
| **Total** | **100** | **77** | |

---

## Section Feedback

### §1 Definition (16/17)
Comprehensive product definition with metadata table (15 rows), domain description, key components. Strong. Minor: Data Access and Restrictions field deferred.

### §2 Consumers (16/17)
analytics.v_ordertoyearanalytics now included with full correlated subquery detail and coordination note. All 4 consumer types present (2 BI reports, 1 analytical view, 1 internal ETL). Near-perfect.

### §3 Model/ER Diagram (15/17)
Detailed Mermaid ER diagram with all key entities and relationships. Textual description covers all 4 layers. Minor: missing explicit diagram of the target (Databricks) model.

### §4 Lineage (14/17)
Bronze→Silver→Gold data flow diagram now present (§4.0) — excellent addition with ASCII diagram and mapping table showing source→target for all objects. Lineage diagram (Mermaid), column-level lineage table, step-by-step transformation table, and downstream dependencies all strong. Minor: mart layer representation in lineage diagram is simplified.

### §5 Calculations (10/17)
3 calculations documented in detail (Date Key Derivation, Ordered Outers/Quantity, SCD-2 Key Resolution). Weaker than reference which includes additional calculation nuances. Coverage ~65% of reference calculation surface.

### §6 Sources (6/16)
Input source tables table is present (8 rows). Output tables section lists DW objects. Missing: explicit source-to-target mapping table with transformation type column. Reference has more comprehensive source inventory structure.

---

## Priority Improvements

1. Expand Sources section with explicit source-to-target transformation type mapping — +5 pts
2. Add Databricks target model ER diagram alongside source model — +3 pts

---

## Next Step
Score ≥ 75 — you can proceed to the next task.
