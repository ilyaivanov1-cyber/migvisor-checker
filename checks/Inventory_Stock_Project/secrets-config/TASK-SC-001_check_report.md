---
task_id: TASK-SC-001
skill: task-checker-secrets-config
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_config.py
reference_file: reference/answers/module_5/codebase/config/secrets_config.py
product: Purchase (inventory_stock)
generated: 2026-09-25
total_score: 100/100
grade: Excellent
---

# TASK-SC-001 Check Report

**Product:** Purchase (inventory_stock)
**Reference:** Purchase (globalpurchase)
**Participant file:** `Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_config.py`
**Reference file:** `reference/answers/module_5/codebase/config/secrets_config.py`
**Generated:** 2026-09-25

---

## Score Summary

**Secrets Config Score: 100/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 20 | 100/100 | 20.00 | ✓ |
| Configuration constants | SCOPES + REQUIRED_KEYS | 20 | 100/100 | 20.00 | ✓ |
| Scope management | scope_exists + create_scope | 20 | 100/100 | 20.00 | ✓ |
| Key registration | register_key | 20 | 100/100 | 20.00 | ✓ |
| Entry point / CLI | main + argparse | 20 | 100/100 | 20.00 | ✓ |
| **Subtotal** | | | | **100.00** | |
| Auto-deducts | | | | **0** | |
| **Total** | | | | **100/100** | |

**Grade: Excellent**

> **Weight calculation:** N = 5, base_weight = floor(100/5) = 20, remainder = 0 → all sections receive equal weight of 20 pts.

---

## Implementation Type

**Participant implementation type:** Type A — Bootstrap script

The participant implemented a full CLI-driven bootstrap script matching the reference intent: scope creation, key registration via `getpass`, and an `--env` CLI argument. The participant goes beyond the reference by adding a `--dry-run` mode for previewing scope/key operations without executing any CLI commands.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | Comment block + module docstring (lines 1–14) | Direct |
| Configuration constants | SCOPES dict + REQUIRED_KEYS list (lines 23–29) | Direct |
| Scope management | scope_exists() + create_scope() functions (lines 40–55) | Direct |
| Key registration | register_key() function (lines 58–66) | Direct |
| Entry point / CLI | main() + argparse + if __name__ == "__main__" (lines 69–92) | Direct |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No CLI interface (argparse / --env) | −4 pts | No — argparse with `--env` choices=["dev","prod"] required ✓ |
| No scope creation | −4 pts | No — create_scope() with subprocess create-scope ✓ |
| No key registration | −4 pts | No — register_key() with secrets put ✓ |
| No SCOPES dict | −3 pts | No — SCOPES = {"dev": "inventory-stock-dev", "prod": "inventory-stock-prod"} ✓ |
| No REQUIRED_KEYS list | −2 pts | No — REQUIRED_KEYS = ["jdbc_url", "jdbc_username", "jdbc_password"] ✓ |
| Hardcoded secret value | −5 pts | No — no literal credentials anywhere ✓ |
| Uses input() for secret | −3 pts | No — getpass.getpass() used ✓ |
| No usage/prerequisites docstring | −2 pts | No — module docstring with Usage: and Prerequisites: present ✓ |
| No idempotency check (scope_exists) | −2 pts | No — scope_exists() checks before creating ✓ |

**Total auto-deducts: 0 pts**

---

## Section Feedback

### Header/Preamble — 100/100 (weight 20 → 20.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100 | CFG-006, purpose, usage, prerequisites ✓ |
| has_usage_docstring | 20% | 100 | `Usage:` and `Prerequisites:` blocks in docstring ✓ |
| has_task_id | 10% | 100 | CFG-006 in header comment ✓ |
| Structure | 10% | 100 | Comment block before imports + docstring ✓ |

**Strengths:**
- Complete module docstring with `Usage:` examples and `Prerequisites:` (CLI auth requirements) ✓
- CFG-006 task ID ✓
- "never hardcoded here" security note ✓
- "Run once per environment (dev / prod)" operational context ✓

---

### Configuration constants — 100/100 (weight 20 → 20.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 100 | SCOPES dict and REQUIRED_KEYS complete ✓ |
| has_scope_dict | 25% | 100 | {"dev": "inventory-stock-dev", "prod": "inventory-stock-prod"} ✓ |
| has_required_keys | 15% | 100 | ["jdbc_url", "jdbc_username", "jdbc_password"] ✓ |

**Strengths:**
- SCOPES dict uses product-correct scope names (`inventory-stock-dev/prod`) ✓
- REQUIRED_KEYS matches the 3 keys registered in secrets_setup.md ✓
- Clean module-level constants — no environment-specific logic mixed in ✓

---

### Scope management — 100/100 (weight 20 → 20.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100 | scope_exists() + create_scope() + _run() helper ✓ |
| has_scope_exists_check | 25% | 100 | scope_exists() checks list-scopes before create ✓ |
| has_scope_creation | 10% | 100 | create-scope subprocess command ✓ |
| Structure | 10% | 100 | Functions separated; error handling via _run() ✓ |

**Strengths:**
- Idempotency guard: `scope_exists()` checks before creating — safe to re-run ✓
- `_run()` helper centralises subprocess error handling with `sys.exit(1)` on failure ✓
- Print feedback ("Scope already exists — skipping creation" / "Scope created") aids operator visibility ✓

---

### Key registration — 100/100 (weight 20 → 20.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100 | register_key reads securely, invokes put, confirms non-logging ✓ |
| has_getpass | 25% | 100 | `getpass.getpass()` imported at module level ✓ |
| has_no_hardcoded_values | 10% | 100 | No literal credentials ✓ |
| Structure | 10% | 100 | Scope + key + dry_run params; confirmation print ✓ |

**Strengths:**
- `getpass` imported at module level (cleaner than reference's inline import inside function) ✓
- `--dry-run` parameter allows previewing key registration without executing CLI commands — exceeds reference ✓
- "Value is not logged" confirmation print ✓
- `has_no_hardcoded_values`: no literal credential strings anywhere ✓

---

### Entry point / CLI — 100/100 (weight 20 → 20.00 pts)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 100 | main() orchestrates scope + keys; argparse ✓ |
| has_cli_interface | 30% | 100 | argparse with --env choices=["dev","prod"] required ✓ |
| Structure | 15% | 100 | if __name__ == "__main__": guard ✓; progress prints ✓; verify hint ✓ |

**Strengths:**
- `--env` with `choices=["dev", "prod"]` required argument ✓
- `--dry-run` flag adds production-safe previewing capability — significant enhancement over reference ✓
- Dry-run branch prints "[DRY RUN] Would bootstrap..." clearly distinguishing execution modes ✓
- Verification hint: "Verify with: databricks secrets list --scope {scope}" ✓
- `if __name__ == "__main__":` guard ✓

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| — | No significant gaps identified | — | 0 pts |

The participant's script is a complete Type A bootstrap that exceeds the reference in three ways:
1. `--dry-run` mode for safe pre-flight checks
2. `getpass` imported at module level (cleaner pattern)
3. More explicit user messaging in register_key (hidden input note before prompt)

---

## Priority Actions

No priority actions required. The script is ready for production use.

Optional enhancements (no score impact):
1. Add `--dry-run` documentation to the module docstring `Usage:` block (currently `--dry-run` is only described in argparse help string).
2. Consider adding a post-loop summary line listing all keys registered for operator confirmation.
3. The `--string-value` flag passes the secret via subprocess argv — in security-sensitive environments, consider using `--stdin-file` or a named pipe instead of argv injection. This is a reference pattern limitation, not a participant error.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs Work | CLI or scope management absent |
| 0–44 | Incomplete | Bootstrap elements entirely absent or accessor module submitted instead |

---

*Report generated by skill 35-migvisor-task-checker-secrets-config on 2026-09-25*
