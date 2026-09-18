---
task_id: TASK-VR-001
skill: migvisor-task-checker-validation-report
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/validation-report.md
reference_file: reference/answers/module_5/reports/validation/report.md
product: Purchase
generated: 2026-09-18
total_score: 70/100
grade: Acceptable
---

# TASK-VR-001 Check Report — v3

**Product:** Purchase  
**Trainee:** Inventory_Stock_Project  
**Generated:** 2026-09-18

---

## Score Summary

**Validation Report Score: 70/100 — Acceptable**

Reference sections: Results, Findings (Failures + Warnings Fixed), DQR Coverage Note, Summary.
Trainee sections: Results Table, Prior-Run Finding Status, Detailed Findings (F-001 to F-008), Summary.

| Section | Weight | Raw | Weighted | Status |
|---|---|---|---|---|
| Results | 28 | 85 | 23.8 | ✓ |
| Findings (Failures) | 28 | 78 | 21.8 | ✓ |
| Warnings (Fixed) | 16 | 80 | 12.8 | ✓ |
| DQR Coverage Note | 14 | 0 | 0 | ✗ |
| Summary | 14 | 85 | 11.9 | ✓ |
| Auto-deducts | | | -1 | |
| **Total** | | | **70/100** | |

**Grade: Acceptable**

---

## Section Feedback

### Results — 85/100
Trainee has a well-structured Results Table. Tracks 8 findings (F-001 to F-008) with artifact, finding, severity, status. Prior-Run Finding Status section (F-001 confirmed resolved) demonstrates follow-up rigor. **+24 pts**

### Findings — 78/100
8 detailed findings with specific artifact paths, exact issue description, severity (Critical/High/Medium/Low), and status. Good specificity:
- F-001: grants SQL path mismatch vs build-plan
- F-002: nb_extract_watermark.py bare SQL in except block
- F-003: nb_extract_purchase.py missing JDBC config keys
- F-004: stale fact table name in nightly_etl workflow JSON
- F-005: test regex mismatch for QA-P001 error
- F-006: stale Bronze table names in design.md
- F-007: wrong columns in MERGE INTO example
- F-008: wrong TASK-008 output path in build-plan

**+22 pts**

### Warnings (Fixed) — 80/100
Prior-run finding F-001 tracked and confirmed resolved. Good practice. **+13 pts**

### DQR Coverage Note — [MISSING] — 0/100
Reference has a DQR Coverage Note section explaining which data quality rules were validated and which were deferred. Trainee does not have this section. **0 pts**

### Summary — 85/100
Severity breakdown, artifact status summary, prioritised remediation order, prior run finding — well-structured. **+12 pts**

---

## Auto-Deducts

| Condition | Penalty | Applied |
|---|---|---|
| DQR Coverage Note absent | −1 pt | Yes |

---

## Improvement Items

| # | Gap | Section | Est. Recoverable |
|---|---|---|---|
| 1 | Add DQR Coverage Note | DQR | +14 pts |

## Priority Actions

1. **Add DQR Coverage Note** — which DQR items (from requirements.md) were validated by SmartBuilder, which passed, which were deferred or require manual validation. Worth up to **+14 pts**.
