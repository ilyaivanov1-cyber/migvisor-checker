---
task_id: TASK-TR-001
skill: migvisor-task-checker-transformation-rules
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md
reference_file: reference/answers/module_3/product-transformation-rules/product-transformation-rules.md
product: Purchase
generated: 2026-09-18
total_score: 70/100
grade: Acceptable
---

# TASK-TR-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Transformation Rules Score: 70/100 — Acceptable**

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| Customization Summary | 10 | 80 | 8.0 | ✓ |
| Action Files | 10 | 0 | 0 | ✗ |
| Dimension Table | 10 | 75 | 7.5 | ⚠ |
| PL — Platform | 10 | 85 | 8.5 | ✓ |
| NM — Naming | 10 | 78 | 7.8 | ✓ |
| TY — Types | 10 | 80 | 8.0 | ✓ |
| OB — Objects | 10 | 78 | 7.8 | ✓ |
| SX — Syntax | 10 | 80 | 8.0 | ✓ |
| IF — Interface | 10 | 0 | 0 | ✗ |
| Auto-deducts | | | -4 | |
| **Total** | | | **70/100** | |

**Grade: Acceptable**

---

## Section Matching

| Reference Section | Trainee Section | Match |
|---|---|---|
| Customization Summary | Customization Summary | Direct |
| Action Files | [MISSING] | Missing |
| Dimension Table | Dimension Table | Direct |
| PL — Platform | PL — Platform (10 rules) | Direct |
| NM — Naming | NM — Naming (9 rules) | Direct |
| TY — Types | TY — Types (30 rules) | Direct |
| OB — Objects | OB — Objects (15 rules) | Direct |
| SX — Syntax | SX — Syntax (21 rules) | Direct |
| IF — Interface | [MISSING] | Missing |
| CX — Custom | CX — Custom | Direct |
| QA — Quality | QA — Quality | Direct |
| LN — Lineage | LN — Lineage | Direct |

Trainee adds: PE — Performance (not in reference).

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| IF (Interface) dimension entirely missing | −4 pts | Yes — Interface rules absent from product rules |

---

## Section Feedback

### Customization Summary — 80/100
Present with rule counts per dimension. Trainee uses slightly different rule count totals (includes inherited project rules in counts) which makes comparison less clean. **+8 pts**

### Action Files — [MISSING] — 0/100
Reference has an Action Files section listing the YAML files that make up the rule set. Trainee omits this section. **0 pts, −4 pts auto-deduct applied above**

### Dimension Table — 75/100
Active dimensions table present. Trainee has PE (Performance) dimension not in reference, but is missing IF (Interface). **+7.5 pts**

### PL through SX — Good coverage (~80/100 each)
All five shared dimensions present with good rule counts and content. Trainee has more rules than reference in some dimensions (includes inherited project rules), which is acceptable and adds value. **+40 pts total**

### IF — Interface — [MISSING] — 0/100
Interface dimension (5 rules in reference: data contract specifications, API shape, connector type) is entirely absent. This is the most critical gap — Interface rules define how the product exposes data to consumers. **0 pts**

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add IF — Interface dimension (5 rules) | IF | +10 pts |
| 2 | Add Action Files section | Action Files | +6 pts |

## Priority Actions

1. **Add IF — Interface dimension** — reference has 4 project + 1 product extension rules covering data contract, connector type, API shape. Worth up to **+10 pts**.
2. **Add Action Files section** — list the YAML files comprising the rule set (CX-custom.yaml, LN-lineage.yaml, etc.). Worth up to **+6 pts**.
