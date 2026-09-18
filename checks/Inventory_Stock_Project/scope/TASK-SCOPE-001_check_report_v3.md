---
task_id: TASK-SCOPE-001
skill: migvisor-task-checker-scope
participant_file: Inventory_Stock_Project/products/Purchase/input/product-scope.md
reference_file: reference/answers/module_2/0 product-scope.md
product: Purchase
generated: 2026-09-18
total_score: 81/100
grade: Good
---

# TASK-SCOPE-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Scope Score: 81/100 — Good**

N=9 sections, base_weight = floor(100/9) = 11, remainder = 1 → §3 gets 12 pts.

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| §1 Identity | 11 | 90 | 9.9→10 | ✓ |
| §2 Description | 11 | 85 | 9.35→9 | ✓ |
| §3 Objects in Scope | 12 | 78 | 9.36→9 | ⚠ |
| §4 Out-of-Scope Objects | 11 | 80 | 8.8→9 | ✓ |
| §5 Consumers | 11 | 65 | 7.15→7 | ⚠ |
| §6 Calculation Surface | 11 | 88 | 9.68→10 | ✓ |
| §7 Boundaries | 11 | 95 | 10.45→10 | ✓ |
| §8 Priority and Sequencing | 11 | 78 | 8.58→9 | ✓ |
| §9 Known Migration Risks | 11 | 75 | 8.25→8 | ⚠ |
| Auto-deducts | | | 0 | |
| **Total** | | | **81/100** | |

**Grade: Good**

---

## Section Feedback

### §1 Identity — 90/100
All required fields present. [USER INPUT REQUIRED] for scope owner is a valid deferral. Product name, discovery mode, and plan stage are correct. Minor: no UUID-based discovery ID (reference has a specific node UUID). **+10 pts**

### §2 Description — 85/100
Covers procurement domain, SCD-2 read dependencies, SSIS bug, and migration target. Adds useful context about the SSIS staging-truncation bug. Slightly less explicit about shared infrastructure migration layer than reference. **+9 pts**

### §3 Objects in Scope — 78/100
6 subsections vs reference's 7. Missing §3.5 Analytics Views (reference notes `analytics.v_ordertoyearanalytics` reads `fact.purchase` but is not Purchase-owned). Trainee's BI Reports section (§3.6) notes cross-domain report correctly. No object UUIDs present. Column detail for `fact.purchase` is excellent. **+9 pts**

### §4 Out-of-Scope Objects — 80/100
Good coverage with reasons for all exclusions. Missing: `wideworldimporters.integration.getpurchaseupdates` and OLTP source dependencies, some shared infrastructure utilities (`integration.populatedatedimensionforyear`, etc.). **+9 pts**

### §5 Consumers — 65/100
Only 2 consumers listed (both BI reports). Missing `analytics.v_ordertoyearanalytics` cross-domain view that reads `fact.purchase` via correlated subquery. **+7 pts**

### §6 Calculation Surface — 88/100
Excellent coverage — staging merge procedure, ETL cutoff watermarking, lineage key generation, staging truncation correction. Adds more detail than reference on sequences.lineagekey redesign and getlastetlcutofftime. **+10 pts**

### §7 Boundaries — 95/100
All 6 boundary rows present and accurate: Temporal [USER INPUT REQUIRED], Organizational [USER INPUT REQUIRED], source system, target system, ETL orchestration source and target. Task dependency note for dimension ordering is a good addition. **+10 pts**

### §8 Priority and Sequencing — 78/100
Priority PRIMARY with rationale and dependencies covered. Gives Inventory_Movement as successor (reference has [USER INPUT REQUIRED]). Missing the specific cross-product ETL ordering detail (stock item read by 5 fact procedures). **+9 pts**

### §9 Known Migration Risks — 75/100
7 of 8 reference risks documented. Missing: Risk 5 (migratestagedsupplierdata/migratestagedstockitemdata SCD-2 UPDATE+INSERT pattern) and Risk 8 (analytics.v_ordertoyearanalytics cross-domain view coordination). All 7 present risks have specific technical detail. **+8 pts**

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add analytics.v_ordertoyearanalytics as consumer | §5 | +4 pts |
| 2 | Add §3.5 Analytics Views subsection | §3 | +3 pts |
| 3 | Add OLTP source dependencies to out-of-scope | §4 | +2 pts |
| 4 | Add Risk 8 (analytics.v_ordertoyearanalytics coordination) | §9 | +2 pts |
| 5 | Add Risk 5 (SCD-2 UPDATE+INSERT for supplier/stock item ETL) | §9 | +2 pts |

## Priority Actions

1. **Add analytics.v_ordertoyearanalytics to §5 Consumers** — cross-domain view that reads fact.purchase via correlated subquery; needs coordination note. Worth up to **+4 pts**.
2. **Add §3.5 Analytics Views subsection** — reference explicitly states no analytics views are owned by Purchase but documents the cross-domain dependency. Worth up to **+3 pts**.
3. **Add two missing risks** — SCD-2 UPDATE+INSERT pattern and analytics view coordination. Worth up to **+4 pts**.
