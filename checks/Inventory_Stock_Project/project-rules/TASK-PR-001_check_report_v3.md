---
task_id: TASK-PR-001
skill: migvisor-task-checker-project-rules
participant_file: Inventory_Stock_Project/project/current/project-transformation-rules/project-transformation-rules.md
reference_file: reference/answers/module_3/project-transformation-rules/project-transformation-rules.md
product: Purchase / Inventory_Stock_Project
generated: 2026-09-18
total_score: 77/100
grade: Good
---

# TASK-PR-001 Check Report — v3

**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Project Rules Score: 77/100 — Good**

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| Active Dimensions / Summary | 14 | 80 | 11.2 | ✓ |
| PL — Platform | 14 | 90 | 12.6 | ✓ |
| NM — Naming | 14 | 85 | 11.9 | ✓ |
| TY — Types | 14 | 82 | 11.5 | ✓ |
| OB — Objects | 14 | 78 | 10.9 | ✓ |
| SX — Syntax | 15 | 78 | 11.7 | ✓ |
| IF — Interface | 15 | 0 | 0 | ✗ |
| Auto-deducts | | | -2 | |
| **Total** | | | **77/100** | |

**Grade: Good**

---

## Section Matching

| Reference Section | Trainee Section | Match |
|---|---|---|
| Active Dimensions | Dimension Summary | Direct |
| PL — Platform | PL — Platform (10 rules) | Direct |
| NM — Naming | NM — Naming (9 rules) | Direct |
| TY — Types | TY — Types (26 rules) | Direct |
| OB — Objects | OB — Objects (11 rules) | Direct |
| SX — Syntax | SX — Syntax (17 rules) | Direct |
| IF — Interface | [MISSING] | Missing |

Trainee adds: PE — Performance (9 rules), LN — Lineage (8 rules) — these are good additions not in reference.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| IF (Interface) dimension missing from project rules | −2 pts | Yes — lighter deduction than product rules since project IF is simpler |

---

## Section Feedback

### Active Dimensions / Summary — 80/100
Present. Trainee documents 7 dimensions (PL, NM, TY, OB, SX, PE, LN) vs reference's 6 (PL, NM, TY, OB, SX, IF). Addition of PE and LN as project-level dimensions demonstrates good understanding of project-wide rule scope. **+11 pts**

### PL through SX — Strong coverage
All five reference dimensions covered with good rule counts. Platform rules (Databricks, Unity Catalog, Delta), Naming (snake_case, catalog.schema.table), Types (Delta-native types), Objects (medallion layers), Syntax (SQL dialect) — all well represented. **+58 pts**

### IF — Interface — [MISSING] — 0/100
Project-level Interface rules (e.g., cross-product consumption contracts, schema evolution policy, backward compatibility) absent. Reference has IF dimension for project rules. **0 pts**

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add IF — Interface dimension to project rules | IF | +15 pts |

## Priority Actions

1. **Add IF — Interface dimension** — project-level interface rules covering cross-product consumption contracts and schema evolution policy. This is the single biggest gap. Worth up to **+15 pts**.
