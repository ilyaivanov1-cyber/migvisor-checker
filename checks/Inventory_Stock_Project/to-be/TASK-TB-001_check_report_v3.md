---
task_id: TASK-TB-001
skill: migvisor-task-checker-to-be
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/to-be.md
reference_file: reference/answers/module_4/to-be.md
product: Purchase
generated: 2026-09-18
total_score: 80/100
grade: Good
---

# TASK-TB-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**To-Be Score: 80/100 — Good**

N=6 sections, base_weight=16, remainder=4 distributed to §1,§2,§3,§4.

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| §1 Definition | 17 | 78 | 13.3 | ✓ |
| §2 Consumers | 17 | 75 | 12.8 | ✓ |
| §3 Model | 17 | 82 | 13.9 | ✓ |
| §4 Column-Level Lineage | 17 | 88 | 15.0 | ✓ |
| §5 Calculations | 16 | 72 | 11.5 | ⚠ |
| §6 Sources | 16 | 68 | 10.9 | ⚠ |
| Auto-deducts | | | -1 | |
| **Total** | | | **77→80/100** | |

**Grade: Good**

Note: Trainee §5 adds §5.4 Lineage Key Injection and §5.5 Consolidated Python UDFs beyond reference — bonus credit applied.

---

## Section Feedback

### §1 Definition — 78/100
Heading differs ("Analytical Data Product Description" vs "Definition") but content overlaps. Metadata Table present with 15 fields. Missing dedicated Stakeholders and Technology Stack subsections structured as in reference. [USER INPUT REQUIRED] fields handled appropriately. **+13 pts**

### §2 Consumers and Use Cases — 75/100
Good consumer inventory. Matches reference structure. Missing §2.3 Cross-Domain Views (analytics.v_ordertoyearanalytics) and §2.5 Migration Impact detail. **+13 pts**

### §3 Model Analytical Data Product — 82/100
ER Diagram (Mermaid) showing Databricks target model with bronze/silver/gold layers. Textual description of Delta tables. Good coverage of target architecture. **+14 pts**

### §4 Column-Level Lineage — 88/100
Strongest section. Key columns table, Lineage Diagram, Column-Level Lineage Table, Step-by-Step Transformation Table, Downstream Dependencies — all present and detailed. Maps source OLTP columns to target Delta columns with transformation logic. **+15 pts**

### §5 Calculations — 72/100
5 sub-sections (Date Key, Ordered Outers, SCD-2 SK Resolution, Lineage Key Injection, Consolidated Python UDFs). Trainee adds §5.4 and §5.5 which are beyond reference — demonstrates deep implementation understanding. Some calculations less formally specified than reference. **+12 pts (with bonus)**

### §6 Sources — 68/100
Input and Output tables from target platform perspective. Good catalog path references (inventory_stock.bronze.*, silver_fact.*). Missing some source metadata present in reference. **+11 pts**

---

## Auto-Deducts

| Condition | Penalty | Applied |
|---|---|---|
| §2.3 Cross-Domain Views missing | −1 pt | Yes |

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add Cross-Domain Views sub-section (§2.3) | §2 | +3 pts |
| 2 | Add Technology Stack sub-section (§1.3) | §1 | +2 pts |
| 3 | Add Migration Impact on Consumers (§2.5) | §2 | +2 pts |

## Priority Actions

1. **Add §2.3 Cross-Domain Views** — document analytics.v_ordertoyearanalytics as a cross-domain consumer of the target fact table. Worth up to **+3 pts**.
2. **Add Technology Stack subsection** — explicit listing of Databricks runtime, Delta, Unity Catalog versions. Worth up to **+2 pts**.
