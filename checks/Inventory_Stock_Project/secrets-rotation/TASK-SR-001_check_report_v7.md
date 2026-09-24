---
task_id: TASK-SR-001
skill: migvisor-task-checker-secrets-rotation-runbook
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_rotation_runbook.md
reference_file: reference/answers/module_5/codebase/config/secrets_rotation_runbook.md
product: Purchase
generated: 2026-09-24
total_score: 98/100
grade: Excellent
---

# TASK-SR-001 Check Report — Secrets Rotation Runbook
_Purchase | 2026-09-24_

## Score Summary

**Secrets Rotation Runbook Score: 98/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header Metadata | 14 | 85/100 | 11.9 | ✓ |
| 1. Trigger Conditions | 14 | 100/100 | 14.0 | ✓ |
| 2. Rotation Procedure | 15 | 100/100 | 15.0 | ✓ |
| 3. Verification Steps | 14 | 100/100 | 14.0 | ✓ |
| 4. Rollback Procedure | 15 | 100/100 | 15.0 | ✓ |
| 5. Notification Checklist | 14 | 100/100 | 14.0 | ✓ |
| 6. Rotation Log | 14 | 100/100 | 14.0 | ✓ |
| **Subtotal** | | | **97.9** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **98/100** | |

**Grade: Excellent**

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | (header block, CFG-008) | exact |
| 1. Trigger Conditions | 1. Trigger Conditions | exact |
| 2. Rotation Procedure | 2. Rotation Procedure | exact |
| 3. Verification Steps | 3. Verification Steps | exact |
| 4. Rollback Procedure | 4. Rollback Procedure | exact |
| 5. Notification Checklist | 5. Notification Checklist | exact |
| 6. Rotation Log | 6. Rotation Log | exact |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No bash CLI code blocks anywhere | −4 pts | No — fenced bash blocks in Sections 2 and 4 |
| No rotation trigger conditions | −4 pts | No — Section 1 has 4 trigger conditions |
| No post-rotation verification steps | −4 pts | No — Section 3 has 4 numbered verification steps |
| No rollback or recovery procedure | −4 pts | No — Section 4 covers rollback with bash commands |
| No notification checklist or stakeholder list | −3 pts | No — Section 5 has checkbox notification list |
| Missing H2 section (max −15) | −5 pts each | No — all 6 reference sections present |
| Hardcoded credential value in code block | −5 pts | No — only key name placeholders, no literal values |
| Bash uses literal credential string-value | −3 pts | No — `databricks secrets put` without --string-value flags |

**Total auto-deducts: 0**

---

## Section Feedback

### Header Metadata — 85/100 (weight 14 → 11.9 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Runbook title in H1 | 35% | 100% | "CFG-008: Credential Rotation Runbook" — clear and specific |
| Task ID / traceability tag present | 30% | 50% | "CFG-008" is a valid config reference; not TASK-* format (reference also uses CFG-008) |
| Scope / catalog reference | 20% | 80% | Scope names `inventory-stock-dev/prod` appear in Section 2; not explicitly in header block |
| Author / generated date present | 15% | 0% | No author or date (reference also lacks this) |

**Strengths:**
- H1 title clearly names the runbook and its function.

**Gaps:**
- No explicit TASK-* tag or author/date in header (same as reference — both use CFG-format only).

**Improvement items:**
- [ ] Add `_Generated: YYYY-MM-DD_` before the first `##` heading.

---

### 1. Trigger Conditions — 100/100 (weight 14 → 14 pts)

**Criteria scored:** Content (75%), Trigger List (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 100% | All 4 trigger scenarios present |
| Trigger List | 15% | 100% | Bullet list with 4 conditions; 90-day policy stated |
| Structure | 10% | 100% | H2 heading, bullet list |

**Strengths:**
- All 4 reference trigger conditions present: scheduled (90 days), security incident, service account change, JDBC URL / database migration.
- "Per security policy" note anchors the schedule to a governance requirement.

---

### 2. Rotation Procedure — 100/100 (weight 15 → 15 pts)

**Criteria scored:** Content (70%), Bash Commands (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 100% | 3 sub-steps (prepare, rotate dev, rotate prod) |
| Bash Commands | 20% | 100% | Fenced bash blocks with `inventory-stock-dev/prod` scope names |
| Structure | 10% | 100% | H2 with H3 subsections; code blocks properly fenced |

**Strengths:**
- Pre-rotation caution ("Do not revoke old credentials until pipeline verified") is present.
- H3 subsection structure mirrors the reference exactly.
- Scope names (`inventory-stock-dev`, `inventory-stock-prod`) correctly adapted for participant's product.

---

### 3. Verification Steps — 100/100 (weight 14 → 14 pts)

**Criteria scored:** Content (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 100% | 4 verification steps covering dev trigger, notebook JDBC check, PII check, lineage check |
| Structure | 10% | 100% | H2, numbered list |

**Strengths:**
- Trainee's Step 2 is enhanced vs. reference: "Confirm `nb_extract_purchase`, `nb_extract_watermark`, and `nb_extract_dimensions` complete without JDBC auth errors" — names 3 notebooks vs reference's 2. This is a more thorough verification.
- Step 4 references `inventory_stock.bronze.lineage_run` with `was_successful = true` (product-specific naming, equivalent to reference's `stg.lineage status = 'success'`).
- `nb_pii_compliance_check` step is present.

---

### 4. Rollback Procedure — 100/100 (weight 15 → 15 pts)

**Criteria scored:** Content (70%), Bash Commands (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 100% | 3-step rollback: re-rotate, re-trigger, investigate |
| Bash Commands | 20% | 100% | `databricks secrets put --scope inventory-stock-<env> --key jdbc_<key>` |
| Structure | 10% | 100% | H2, numbered list, fenced bash block |

**Strengths:**
- Parametric bash command (`inventory-stock-<env>` + `jdbc_<key>`) is both concrete and reusable for all environments and keys.
- Three-step recovery process (rotate → verify → investigate) is complete.

---

### 5. Notification Checklist — 100/100 (weight 14 → 14 pts)

**Criteria scored:** Content (75%), Checklist Format (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 100% | All 3 stakeholder roles present |
| Checklist Format | 15% | 100% | `- [ ]` checkbox syntax used for all items |
| Structure | 10% | 100% | H2 heading, checkbox list |

**Strengths:**
- All 3 reference stakeholder roles covered: Data Engineering lead, Platform Security team, On-call engineer.
- Conditional notification ("if rotation is incident-triggered") is preserved.
- Checkbox format used correctly.

---

### 6. Rotation Log — 100/100 (weight 14 → 14 pts)

**Criteria scored:** Content (70%), Rotation Log Table (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 100% | Table with all required fields |
| Rotation Log Table | 20% | 100% | Markdown table present; 5/5 required columns; initial placeholder row |
| Structure | 10% | 100% | H2 heading, Markdown table |

**Strengths:**
- All 5 required columns present: Date, Rotated By, Environment, Keys Rotated, Reason.
- Initial placeholder row with "first entry" label shows expected format.
- All 3 keys listed in the initial row (jdbc_url, jdbc_username, jdbc_password).

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | No author/generated date in header block | Header Metadata | +1 pt |
| 2 | Scope names not stated in header block itself (appear only in Section 2) | Header Metadata | <1 pt |

---

## Priority Actions

1. **Add a generated date to the header** — Insert `_Generated: YYYY-MM-DD_` before the first `##` heading. Worth up to **+1 pt**.
2. **Optionally state scope prefix in header** — A brief comment like `-- Scopes: inventory-stock-dev, inventory-stock-prod` in the header block would improve discoverability.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing rollback procedure, notification checklist, or rotation log absent |
| 0–44 | Incomplete | Major sections absent or no CLI rotation commands documented |

---

_Report generated by skill migvisor-task-checker-secrets-rotation-runbook on 2026-09-24_
