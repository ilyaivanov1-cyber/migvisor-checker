---
task_id: TASK-SEC-001
skill: task-checker-secrets-setup
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_setup.md
reference_file: reference/answers/module_5/codebase/config/secrets_setup.md
product: Purchase (inventory_stock)
generated: 2026-09-25
total_score: 91/100
grade: Excellent
---

# TASK-SEC-001 Check Report

**Product:** Purchase (inventory_stock)
**Reference:** Purchase (globalpurchase)
**Participant file:** `Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_setup.md`
**Reference file:** `reference/answers/module_5/codebase/config/secrets_setup.md`
**Generated:** 2026-09-25

---

## Score Summary

**Secrets Setup Score: 91/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 11 | 85/100 | 9.35 | ✓ |
| Prerequisites | Prerequisites | 11 | 86/100 | 9.46 | ✓ |
| Step 1 — Create the Dev Scope | Step 1 — Create the Dev Scope | 11 | 90/100 | 9.90 | ✓ |
| Step 2 — Create the Prod Scope | Step 2 — Create the Prod Scope | 11 | 90/100 | 9.90 | ✓ |
| Step 3 — Register Required Keys (Dev) | Step 3 — Register Required Keys (Dev) | 12 | 98/100 | 11.76 | ✓ |
| Step 4 — Register Required Keys (Prod) | Step 4 — Register Required Keys (Prod) | 11 | 98/100 | 10.78 | ✓ |
| Step 5 — Verify | Step 5 — Verify (without revealing values) | 11 | 100/100 | 11.00 | ✓ |
| Step 6 — Credential Rotation | Step 6 — Credential Rotation | 11 | 84/100 | 9.24 | ✓ |
| Reference | Reference | 11 | 84/100 | 9.24 | ✓ |
| **Subtotal** | | | | **90.63** | |
| Auto-deducts | | | | **0** | |
| **Total** | | | | **91/100** | |

**Grade: Excellent**

> **Weight calculation:** N = 9, base_weight = floor(100/9) = 11, remainder = 1 → Step 3 (Register Required Keys Dev) receives +1 = 12 pts. All others = 11 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| (header block) | (header block) | exact |
| Prerequisites | Prerequisites | exact |
| Step 1 — Create the Dev Scope | Step 1 — Create the Dev Scope | exact |
| Step 2 — Create the Prod Scope | Step 2 — Create the Prod Scope | exact |
| Step 3 — Register Required Keys (Dev) | Step 3 — Register Required Keys (Dev) | exact |
| Step 4 — Register Required Keys (Prod) | Step 4 — Register Required Keys (Prod) | exact |
| Step 5 — Verify (without revealing values) | Step 5 — Verify (without revealing values) | exact |
| Step 6 — Credential Rotation | Step 6 — Credential Rotation | exact |
| Reference | Reference | exact |

**Cross-product note:** `globalpurchase-dev/prod` → `inventory-stock-dev/prod`. All scope names correctly adapted. Participant adds extra "Verify after Step 3/4" blocks using `dbutils.secrets.get()` — additional thoroughness beyond reference, no penalty.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No bash/CLI code blocks anywhere | −4 pts | No — bash blocks present in Steps 1–4, Reference section |
| No scope creation command anywhere | −4 pts | No — `databricks secrets create-scope` present in Steps 1 and 2 |
| No key registration command anywhere | −4 pts | No — `databricks secrets put` present in Steps 3 and 4 |
| No verification step anywhere | −4 pts | No — `dbutils.secrets.list()` present in Step 5 |
| No dev/prod scope separation | −3 pts | No — separate dev and prod scopes documented ✓ |
| Missing H2 section | −5 pts each (max −15) | No — all 8 H2 sections present |
| Hardcoded credentials in code block | −5 pts | No — no credential values hardcoded |
| ACL command placeholder only | −2 pts | N/A — no ACL command block |

**Total auto-deducts: 0 pts**

---

## Section Feedback

### Header Metadata — 85/100 (weight 11 → 9.35 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Runbook/guide name in H1 | 35% | 100 | "CFG-007: Secrets Initialization Runbook" ✓ |
| Task ID / traceability tag | 30% | 100 | CFG-007 present ✓ |
| Catalog / scope reference | 20% | 100 | inventory-stock-dev/prod mentioned ✓ |
| Author / generated date | 15% | 0 | Not present (reference also omits) |

**Strengths:** Clear runbook title with CFG ID.
**Gaps:** No author/date (consistent with reference pattern).

---

### Prerequisites — 86/100 (weight 11 → 9.46 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 85 | CLI req, env vars, network access ✓; no intro sentence |
| Bash Commands | 20% | 83 | Export block present; not product-scope specific (expected) |
| Structure | 10% | 100 | H2 ✓, fenced block ✓ |

**Strengths:** All three prerequisites documented; export commands in fenced bash block.
**Gaps:** No intro sentence before the bullet list.

---

### Step 1 — Create the Dev Scope — 90/100 (weight 11 → 9.90 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 85 | Scope creation + verify; no intro sentence |
| Bash Commands | 20% | 100 | `databricks secrets create-scope --scope inventory-stock-dev` ✓ |
| Verification Step | 20% | 88 | `list-scopes | grep inventory-stock-dev`; expected output not explained |
| Structure | 10% | 100 | H2 ✓, fenced bash ✓ |

**Strengths:** Correct scope name; verify command present immediately after creation.

---

### Step 2 — Create the Prod Scope — 90/100 (weight 11 → 9.90 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 85 | Prod scope command; no intro sentence |
| Bash Commands | 20% | 100 | `databricks secrets create-scope --scope inventory-stock-prod` ✓ |
| Structure | 10% | 100 | H2 ✓, fenced bash ✓ |

**Strengths:** Correct prod scope name; clean, minimal section.

---

### Step 3 — Register Required Keys (Dev) — 98/100 (weight 12 → 11.76 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100 | All 3 keys; "interactively and never logged" ✓; intro sentence ✓ |
| Bash Commands | 20% | 100 | `databricks secrets put --scope inventory-stock-dev --key jdbc_*` ✓ |
| Key Inventory | 15% | 88 | 3/3 keys present; key names shown but no per-key purpose docs |
| Structure | 10% | 100 | H2 ✓, intro ✓, fenced bash ✓ |

**Strengths:**
- Intro "Register each key individually. Values are entered interactively and never logged." ✓
- Participant adds a "Verify after Step 3" block with `dbutils.secrets.get()` — extra thoroughness beyond reference
- The get() verification confirms key registration (Databricks returns REDACTED, not the actual value)

**Gaps:**
- Key inventory lacks per-key purpose documentation (e.g., "jdbc_url — source database connection URL")

**Improvement items:**
- [ ] Add one-line purpose for each key (jdbc_url, jdbc_username, jdbc_password) in the key list or as inline comments

---

### Step 4 — Register Required Keys (Prod) — 98/100 (weight 11 → 10.78 pts)

Same pattern as Step 3 with prod scope. All 3 keys correctly registered to `inventory-stock-prod`. Extra verify block adds value.

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100 | All 3 keys, inventory-stock-prod ✓ |
| Bash Commands | 20% | 100 | Correct scope ✓ |
| Key Inventory | 15% | 88 | 3/3 keys; no per-key purpose docs |
| Structure | 10% | 100 | H2 ✓, fenced bash ✓ |

---

### Step 5 — Verify — 100/100 (weight 11 → 11.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100 | `list()` call ✓; non-revealing explanation ✓; expected output shown ✓ |
| Python Code | 15% | 100 | Python block present; uses inventory-stock-dev ✓ |
| Verification Step | 20% | 100 | Non-revealing `list()` ✓; expected output explained ✓ |
| Structure | 10% | 100 | H2 ✓, python block ✓, explanation ✓ |

**Strengths:**
- `dbutils.secrets.list()` (not get) — correctly non-revealing ✓
- Expected output shown with exact key names ✓
- "values are never exposed" explanation present ✓

---

### Step 6 — Credential Rotation — 84/100 (weight 11 → 9.24 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 85 | References rotation_runbook.md ✓; no intro sentence |
| Structure | 10% | 75 | H2 ✓; no intro sentence before the reference link |

**Strengths:** Correctly cross-references `config/secrets_rotation_runbook.md`.
**Gaps:** Single-line reference without introductory context sentence.

---

### Reference — 84/100 (weight 11 → 9.24 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 85 | Doc link, key names, scope widget note ✓ (exceeds reference!) |
| Key Inventory | 15% | 88 | 3/3 keys; no per-key purpose |
| Structure | 10% | 75 | H2 ✓; no intro sentence |

**Strengths:**
- Adds the critical scope widget note: `env_scope` widget must match scope names exactly, including hyphens — this is MORE detailed than the reference and shows operational awareness.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add per-key purpose documentation (one line per key) | Steps 3, 4, Reference | +2 pts |
| 2 | Add intro sentences to sections that lack them (Prerequisites, Steps 2, 6, Reference) | Multiple | +2 pts |
| 3 | Explain expected output after `list-scopes | grep` verification | Step 1 | +1 pt |

---

## Priority Actions

1. **Add per-key purpose docs** to the key list in Steps 3 and 4 (e.g., `jdbc_url — JDBC connection URL for the source database`) — worth up to **+2 pts**.
2. **Add intro sentences** to Step 2, Step 6, and Reference sections before the first code block or link — worth up to **+2 pts**.
3. **Explain expected grep output** in Step 1 verification ("grep output confirms scope is listed") — worth up to **+1 pt**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing scope creation, key registration, or verification absent |
| 0–44 | Incomplete | Major steps absent or no CLI commands documented |

---

*Report generated by skill 31-migvisor-task-checker-secrets-setup on 2026-09-25*
