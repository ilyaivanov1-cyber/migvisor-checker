---
task_id: TASK-SEC-002
skill: task-checker-secrets-rotation-runbook
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_rotation_runbook.md
reference_file: reference/answers/module_5/codebase/config/secrets_rotation_runbook.md
product: Purchase (inventory_stock)
generated: 2026-09-25
total_score: 94/100
grade: Excellent
---

# TASK-SEC-002 Check Report

**Product:** Purchase (inventory_stock)
**Reference:** Purchase (globalpurchase)
**Participant file:** `Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_rotation_runbook.md`
**Reference file:** `reference/answers/module_5/codebase/config/secrets_rotation_runbook.md`
**Generated:** 2026-09-25

---

## Score Summary

**Secrets Rotation Runbook Score: 94/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 14 | 85/100 | 11.90 | ✓ |
| 1. Trigger Conditions | 1. Trigger Conditions | 14 | 100/100 | 14.00 | ✓ |
| 2. Rotation Procedure | 2. Rotation Procedure | 15 | 100/100 | 15.00 | ✓ |
| 3. Verification Steps | 3. Verification Steps | 14 | 84/100 | 11.76 | ✓ |
| 4. Rollback Procedure | 4. Rollback Procedure | 15 | 100/100 | 15.00 | ✓ |
| 5. Notification Checklist | 5. Notification Checklist | 14 | 100/100 | 14.00 | ✓ |
| 6. Rotation Log | 6. Rotation Log | 14 | 87/100 | 12.18 | ✓ |
| **Subtotal** | | | | **93.84** | |
| Auto-deducts | | | | **0** | |
| **Total** | | | | **94/100** | |

**Grade: Excellent**

> **Weight calculation:** N = 7, base_weight = floor(100/7) = 14, remainder = 2 → Rotation Procedure (15 pts) and Rollback Procedure (15 pts) receive +1 each from complexity ranking. All others = 14 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| (header block) | (header block) | exact |
| 1. Trigger Conditions | 1. Trigger Conditions | exact |
| 2. Rotation Procedure | 2. Rotation Procedure | exact |
| 3. Verification Steps | 3. Verification Steps | exact |
| 4. Rollback Procedure | 4. Rollback Procedure | exact |
| 5. Notification Checklist | 5. Notification Checklist | exact |
| 6. Rotation Log | 6. Rotation Log | exact |

**Cross-product note:** `globalpurchase-dev/prod` → `inventory-stock-dev/prod`; `stg.lineage` → `inventory_stock.bronze.lineage_run`; notebook `nb_extract_purchase` and `nb_extract_dimensions` → `nb_extract_purchase`, `nb_extract_watermark`, `nb_extract_dimensions` (trainee adds an extra notebook, no penalty).

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No bash CLI code blocks anywhere | −4 pts | No — bash blocks present in Sections 2 and 4 |
| No rotation trigger conditions | −4 pts | No — Section 1 lists 4 trigger conditions ✓ |
| No post-rotation verification steps | −4 pts | No — Section 3 has 4 numbered verification steps ✓ |
| No rollback or recovery procedure | −4 pts | No — Section 4 present with bash commands ✓ |
| No notification checklist or stakeholder list | −3 pts | No — Section 5 has checkbox items ✓ |
| Missing H2 section | −5 pts each (max −15) | No — all 6 H2 sections present |
| Hardcoded credential value in code block | −5 pts | No — no hardcoded values |
| Bash uses literal credential string-value | −3 pts | No — only key names, no literal values |

**Total auto-deducts: 0 pts**

---

## Section Feedback

### Header Metadata — 85/100 (weight 14 → 11.90 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Runbook title in H1 | 35% | 100 | "CFG-008: Credential Rotation Runbook" ✓ |
| Task ID / traceability tag | 30% | 100 | CFG-008 present ✓ |
| Scope / catalog reference | 20% | 100 | inventory-stock scopes mentioned in Section 2 ✓ |
| Author / generated date | 15% | 0 | Not present (reference also omits) |

**Strengths:** Clear runbook title with CFG ID.
**Gaps:** No author/date (consistent with reference).

---

### 1. Trigger Conditions — 100/100 (weight 14 → 14.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 100 | 4/4 triggers; intro sentence ✓; schedule stated ✓ |
| Trigger List | 15% | 100 | All 4 triggers present; "every 90 days" schedule ✓ |
| Structure | 10% | 100 | H2 ✓, bullet list ✓ |

**Strengths:**
- All four trigger conditions present: scheduled (90 days), security incident, service account change, database migration ✓
- Specific schedule policy ("every 90 days, per security policy") ✓
- Intro sentence "Rotate JDBC credentials when any of the following occur:" ✓

---

### 2. Rotation Procedure — 100/100 (weight 15 → 15.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 100 | 3 sub-sections; "do not revoke" guidance ✓ |
| Bash Commands | 20% | 100 | inventory-stock-dev/prod; 3 keys per scope ✓ |
| Structure | 10% | 100 | H2 + H3 sub-sections ✓; fenced bash ✓ |

**Strengths:**
- Three H3 sub-sections (Prepare, Dev, Prod) — well-structured ✓
- Critical operational guidance: "Do not revoke old credentials until the pipeline is verified" ✓
- All 6 put commands correct (3 keys × 2 scopes) ✓

---

### 3. Verification Steps — 84/100 (weight 14 → 11.76 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 85 | 4 steps; notebook names ✓; no intro sentence |
| Structure | 10% | 75 | H2 ✓; numbered list ✓; no intro before steps |

**Content completeness (85/100):**
- Step 1: Trigger manual Workflow run ✓
- Step 2: Confirm `nb_extract_purchase`, `nb_extract_watermark`, `nb_extract_dimensions` complete without JDBC errors ✓ (adds nb_extract_watermark beyond reference — extra value)
- Step 3: Run `nb_pii_compliance_check` ✓
- Step 4: Check `inventory_stock.bronze.lineage_run` — status must be `was_successful = true` ✓
- Intro paragraph: Missing (goes straight to numbered steps — same as reference pattern)

**Gaps:**
- No intro sentence before numbered steps (consistent with reference)

---

### 4. Rollback Procedure — 100/100 (weight 15 → 15.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 100 | 3 recovery steps; bash command ✓; intro ✓ |
| Bash Commands | 20% | 100 | `inventory-stock-<env>` placeholder ✓; executable |
| Structure | 10% | 100 | H2 ✓; intro ✓; numbered steps ✓; fenced bash ✓ |

**Strengths:**
- Intro "If the pipeline fails with new credentials:" ✓
- Bash command uses `<env>` and `<key>` as intentional variable placeholders (not {{placeholder}}) ✓
- Three recovery steps: re-rotate, re-trigger, investigate ✓

---

### 5. Notification Checklist — 100/100 (weight 14 → 14.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 100 | 3 stakeholders; intro sentence ✓ |
| Checklist Format | 15% | 100 | `- [ ]` format ✓; all 3 roles specific ✓ |
| Structure | 10% | 100 | H2 ✓; checkbox items ✓ |

**Strengths:**
- All three stakeholders: Data Engineering lead, Platform Security team, On-call engineer ✓
- Checkbox format used correctly ✓
- Condition "if rotation is incident-triggered" on on-call item shows operational precision ✓

---

### 6. Rotation Log — 87/100 (weight 14 → 12.18 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 85 | Table present; 5 columns ✓; placeholder entry ✓; no intro |
| Rotation Log Table | 20% | 100 | All 5 columns; initial row ✓ |
| Structure | 10% | 75 | H2 ✓; no intro paragraph before table |

**Content completeness (85/100):**
- All 5 required columns: Date, Rotated By, Environment, Keys Rotated, Reason ✓
- Initial placeholder entry: "*(first entry)*" row with "dev + prod" and "Initial setup" ✓
- Intro paragraph: Missing (goes straight to table — consistent with reference)

**Strengths:**
- Placeholder first entry demonstrates expected log format ✓
- "dev + prod" in Environment column shows both-environment rotation is documented ✓

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add intro sentences to Verification Steps and Rotation Log | Sections 3, 6 | +2 pts |
| 2 | Add author/generated date to header block | Header | +2 pts |
| 3 | Add context to verification step 4 (note `was_successful` field name differs from reference `status='success'`) | Section 3 | +1 pt |

---

## Priority Actions

1. **Add intro sentences** to Sections 3 (Verification Steps) and 6 (Rotation Log) — worth up to **+2 pts**.
2. **Add header metadata** (author or date) to the header block — worth up to **+2 pts**.
3. **Inline note** in verification step 4 explaining the product-specific field name (`was_successful = true` vs reference's `status = 'success'`) to aid auditors — minor but shows precision.

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

*Report generated by skill 32-migvisor-task-checker-secrets-rotation-runbook on 2026-09-25*
