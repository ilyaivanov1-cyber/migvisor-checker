---
task_id: TASK-AI-001
skill: migvisor-task-checker-as-is
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md
reference_file: reference/answers/module_2/1 as-is.md
product: Purchase
generated: 2026-09-18
total_score: 68/100
grade: Acceptable
---

# TASK-AI-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**As-Is Score: 68/100 — Acceptable**

N=6 sections, base_weight = floor(100/6) = 16, remainder = 4 → distributed to §1,§2,§3,§4.

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| §1 Definition | 17 | 68 | 11.6→12 | ⚠ |
| §2 Consumers | 17 | 62 | 10.5→11 | ⚠ |
| §3 Model | 17 | 72 | 12.2→12 | ⚠ |
| §4 Lineage | 17 | 82 | 13.9→14 | ✓ |
| §5 Calculations | 16 | 70 | 11.2→11 | ⚠ |
| §6 Sources | 16 | 50 | 8.0→8 | ⚠ |
| Auto-deducts | | | 0 | |
| **Total** | | | **68/100** | |

**Grade: Acceptable**

---

## Section Feedback

### §1 Definition — 68/100
Reference has 7 structured subsections (System Identity, Business Purpose, Technology Stack, Stakeholders, Data Domain, Key Metrics, Operational Context). Trainee has §1.1 Definition (narrative) and §1.2 Metadata Table (15 fields). Coverage is solid — business process, entities, metrics, DQ rules, storage are all documented in the metadata table. Missing: dedicated Stakeholders sub-section, Technology Stack breakdown, Operational Context (SLA, batch schedule, monitoring). **+12 pts**

### §2 Consumers — 62/100
Trainee has 3 consumers (2 BI reports + migratestagedpurchasedata ETL) with good detail. Reference has 6 subsections: Consumer Inventory, BI Reports, Analytical Views, Consumption Patterns, Migration Impact on Consumers, Consumer Priority. Trainee misses Analytical Views (analytics.v_ordertoyearanalytics), Consumption Patterns, Migration Impact sub-structure, Consumer Priority ranking. **+11 pts**

### §3 Model — 72/100
ER Diagram (Mermaid) is well-structured showing all key entities. Textual description covers Primary Source, Fact Table, Dimensions, Processing with good detail. Reference has 8 subsections with separate tables for fact, dimensions, staging, sequences, relationships, schema issues, schema diagram. Trainee misses dedicated sections for Sequences (lineagekey), Notable Schema Issues (space in dimension name), and formal Relationships table. **+12 pts**

### §4 Lineage — 82/100
Strongest section. Key Columns/Metrics table (9 columns with derivation detail), Lineage Diagram (Mermaid flowchart with classDefs), Column-Level Lineage Table, Step-by-Step Transformation Table, Known Downstream Dependencies. More detailed than reference in transformation steps. Well-documented SSIS bug in diagram. **+14 pts**

### §5 Calculations — 70/100
Covers Date Key Derivation, Ordered Outers/Quantity (pass-through), SCD-2 Surrogate Key Resolution with good technical detail. Reference may have more formal calculation taxonomy. Missing: explicit lineage key calculation documented as a calculation (documented in lineage section but not calculation section). **+11 pts**

### §6 Sources — 50/100
Trainee has Input Source Tables and Output Tables. Reference likely has more detail on source system credentials, extraction queries, source system metadata. Trainee sources section appears brief compared to reference. **+8 pts**

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add §2.3 Analytical Views (analytics.v_ordertoyearanalytics) | §2 | +4 pts |
| 2 | Add §2.4–2.6: Consumption Patterns, Migration Impact, Priority | §2 | +3 pts |
| 3 | Add Stakeholders sub-section to §1 | §1 | +3 pts |
| 4 | Add Technology Stack and Operational Context | §1 | +3 pts |
| 5 | Add Notable Schema Issues sub-section to §3 | §3 | +2 pts |
| 6 | Expand §6 Sources with more metadata | §6 | +3 pts |

## Priority Actions

1. **Add Analytical Views sub-section to §2** — document analytics.v_ordertoyearanalytics as cross-domain consumer. Worth up to **+4 pts**.
2. **Add Consumption Patterns and Migration Impact to §2** — describe how each consumer connects, what breaks if fact.purchase moves to Databricks. Worth up to **+3 pts**.
3. **Expand §1 with Stakeholders and Operational Context** — named stakeholders and SLA/schedule details. Worth up to **+3 pts**.
