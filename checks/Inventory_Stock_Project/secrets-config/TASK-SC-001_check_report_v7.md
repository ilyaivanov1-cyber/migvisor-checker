---
task_id: TASK-SC-001
skill: migvisor-task-checker-secrets-config
participant_file: Inventory_Stock_Project/products/Purchase/current/codebase/config/secrets_config.py
reference_file: reference/answers/module_5/codebase/config/secrets_config.py
product: Purchase
generated: 2026-09-24
total_score: 100/100
grade: Excellent
---

# TASK-SC-001 Check Report — Secrets Config
_Purchase | 2026-09-24_

## Score Summary

**Secrets Config Score: 100/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| Header/Preamble | 20 | 100/100 | 20.0 | ✓ |
| Configuration constants | 20 | 100/100 | 20.0 | ✓ |
| Scope management | 20 | 100/100 | 20.0 | ✓ |
| Key registration | 20 | 100/100 | 20.0 | ✓ |
| Entry point/CLI | 20 | 100/100 | 20.0 | ✓ |
| **Subtotal** | | | **100.0** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **100/100** | |

**Grade: Excellent**

---

## Script Type Detection

**Type A (Bootstrap)** — This script creates secret scopes and registers key names by prompting for values via `getpass`. It is a **bootstrap utility**, not an accessor. Evaluation focuses on scope creation, key registration, idempotency, and CLI interface rather than runtime secret retrieval.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | Module-level comments + docstring (lines 1–14) | Direct + enhanced |
| Configuration constants | `SCOPES` dict + `REQUIRED_KEYS` list (lines 24–29) | Direct |
| Scope management | `scope_exists()` + `create_scope()` functions (lines 40–55) | Direct |
| Key registration | `register_key()` function with `getpass` (lines 58–67) | Direct + enhanced |
| Entry point/CLI | `main()` + `argparse` + `if __name__ == "__main__"` (lines 69–92) | Direct + enhanced |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No CLI interface | −4 pts | No — `argparse` with `--env` (choices=["dev","prod"], required=True) present |
| No scope creation | −4 pts | No — `create_scope()` with `databricks secrets create-scope` present |
| No key registration | −4 pts | No — `register_key()` with `databricks secrets put` present |
| No SCOPES dict | −3 pts | No — `SCOPES = {"dev": "inventory-stock-dev", "prod": "inventory-stock-prod"}` present |
| No REQUIRED_KEYS | −2 pts | No — `REQUIRED_KEYS = ["jdbc_url", "jdbc_username", "jdbc_password"]` present |
| Hardcoded secret | −5 pts | No — values supplied via `getpass.getpass()`, never hardcoded |
| `input()` instead of `getpass` | −3 pts | No — `import getpass` at module level; `getpass.getpass()` used in `register_key()` |
| No usage docstring | −2 pts | No — module-level docstring with `Usage:` and `Prerequisites:` sections present |
| No idempotency check | −2 pts | No — `create_scope()` calls `scope_exists()` and skips creation if already present |

**Total auto-deducts: 0**

---

## Section Feedback

### Header/Preamble — 100/100 (weight 20 → 20 pts)

| Criterion | Notes |
|---|---|
| CFG/TASK ID | "CFG-006" on line 1 — valid task reference code |
| Module purpose | "Creates scopes and registers required key names for the Purchase ETL pipeline" |
| Usage instructions | Docstring with `python config/secrets_config.py --env dev/prod` |
| Prerequisites | "Databricks CLI installed and authenticated (DATABRICKS_HOST + DATABRICKS_TOKEN set)" + "Run config/secrets_setup.md" |

**Strengths:**
- Module-level comment block identifies the script's role (bootstrap, not accessor).
- Safety note: "Actual secret VALUES are supplied interactively or via environment variables — never hardcoded here" — explicit data-security policy.
- "Run once per environment (dev / prod) before deploying the pipeline" sets clear execution context.

---

### Configuration constants — 100/100 (weight 20 → 20 pts)

| Element | Value | Notes |
|---|---|---|
| `SCOPES["dev"]` | `"inventory-stock-dev"` | Correct product scope name |
| `SCOPES["prod"]` | `"inventory-stock-prod"` | Correct product scope name |
| `REQUIRED_KEYS` | `["jdbc_url", "jdbc_username", "jdbc_password"]` | 3 correct JDBC credential keys |

**Strengths:**
- SCOPES dict at module level (not buried in main) enables easy discovery and modification.
- REQUIRED_KEYS as a list drives the key registration loop — clean data-driven design.
- Scope names correctly adapted from reference (`globalpurchase-dev/prod` → `inventory-stock-dev/prod`).

---

### Scope management — 100/100 (weight 20 → 20 pts)

| Function | Criterion | Notes |
|---|---|---|
| `scope_exists(scope)` | Check via CLI JSON output | Calls `databricks secrets list-scopes --output json`; checks `scope in result.stdout` |
| `create_scope(scope)` | Idempotency guard | Calls `scope_exists()` first; prints skip message if already exists; creates only when needed |

**Strengths:**
- `scope_exists()` uses the proper CLI approach (JSON output, checks by scope name).
- `create_scope()` is fully idempotent: if scope already exists, it prints "already exists — skipping creation" and returns without error.
- Clear print statements provide operational feedback during execution.

---

### Key registration — 100/100 (weight 20 → 20 pts)

| Criterion | Notes |
|---|---|
| `register_key()` function present | Yes — lines 58–67 |
| Uses `getpass` | Yes — `import getpass` at module level; `getpass.getpass(prompt="  > ")` in function body |
| Does NOT use `input()` | Confirmed — no `input()` calls anywhere in the file |
| Value not logged or printed | "Value is not logged." printed after registration |
| `--string-value` CLI flag used | `--string-value, value` in `databricks secrets put` command |

**Strengths:**
- `getpass` imported at module level (cleaner than reference's inline `import getpass` inside the function).
- Prompt message "Enter value for {key} (input is hidden in terminal):" is user-friendly.
- `dry_run` parameter adds bonus functionality — in dry-run mode, key registration is skipped entirely, allowing pre-validation of the bootstrap sequence.

**Bonus vs. reference:**
- `register_key(scope, key, dry_run=False)` — the `dry_run` parameter allows safe testing of the full flow without writing any actual secrets. Reference lacks this.

---

### Entry point/CLI — 100/100 (weight 20 → 20 pts)

| Element | Notes |
|---|---|
| `main()` function | Present — lines 69–90 |
| `argparse` with `--env` | `add_argument("--env", choices=["dev", "prod"], required=True)` |
| `if __name__ == "__main__"` | Present — line 92 |
| Environment-to-scope resolution | `scope = SCOPES[args.env]` — uses the SCOPES dict |
| Loop over REQUIRED_KEYS | `for key in REQUIRED_KEYS: register_key(scope, key, dry_run=args.dry_run)` |

**Strengths:**
- `--env` argument with `choices` ensures only valid environments are accepted.
- `required=True` prevents silent no-op execution.
- `if __name__ == "__main__"` guard ensures the script is safe to import as a module.
- **Bonus `--dry-run` flag**: `add_argument("--dry-run", action="store_true", help="Preview scope/key registration without executing any CLI commands")` — a significant enhancement over the reference. This allows operators to validate the bootstrap sequence in CI/CD pipelines without side effects.
- Conditional execution path for dry-run: scope creation is skipped, key registration prints preview messages only.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| — | No gaps identified | — | — |

This submission is a complete, correct implementation that exceeds the reference in several areas.

---

## Priority Actions

No corrective actions required. The script is production-ready.

**Notable enhancements over reference:**
1. **`--dry-run` flag** — enables safe pre-validation of the entire bootstrap sequence.
2. **Module-level `getpass` import** — cleaner than inline import.
3. **`dry_run` parameter on `register_key()`** — allows partial execution for testing.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs work | Missing scope creation, key registration, or no CLI interface |
| 0–44 | Incomplete | Major components absent or hardcoded secrets present |

---

_Report generated by skill migvisor-task-checker-secrets-config on 2026-09-24_
