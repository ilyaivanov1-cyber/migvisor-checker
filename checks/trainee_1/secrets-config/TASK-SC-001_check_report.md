---
task_id: TASK-SC-001
skill: task-checker-secrets-config
participant_file: trainees/trainee_1/secrets_config.py
reference_file: reference/secrets_config.py
product: Sales_Orders
generated: 2026-09-04
total_score: 3/100
grade: Incomplete
---

# TASK-SC-001 Check Report

**Product:** Sales_Orders  
**Reference:** Purchase (globalpurchase)  
**Participant file:** `trainees/trainee_1/secrets_config.py`  
**Reference file:** `reference/secrets_config.py`  
**Generated:** 2026-09-04

---

## Score Summary

**Secrets Config Score: 3/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 20 | 50/100 | 10.0 | ⚠ |
| Configuration constants | SCOPES + REQUIRED_KEYS | 20 | 0/100 | 0.0 | ✗ |
| Scope management | scope_exists + create_scope | 20 | 0/100 | 0.0 | ✗ |
| Key registration | register_key | 20 | 38/100 | 7.6 | ✗ |
| Entry point / CLI | main + argparse | 20 | 0/100 | 0.0 | ✗ |
| **Subtotal** | | | | **17.6** | |
| Auto-deducts | | | | **−15** | |
| **Total** | | | | **3/100** | |

**Grade: Incomplete**

> **Weight calculation:** N = 5, base_weight = floor(100/5) = 20, remainder = 0 → all sections receive equal weight of 20 pts.

---

## Implementation Type

**Participant implementation type: Type B — Accessor module**

The participant built a `get_secret(scope, key)` wrapper that reads secrets from Databricks at runtime via `dbutils.secrets.get()`. The reference is a **Type A — Bootstrap script**: a CLI tool that creates secret scopes and registers key values interactively before the pipeline runs. These are complementary components, but the task required the bootstrap script.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | Lines 1–3 comment block | Partial — TASK-ENV-002 present; purpose is accessor not bootstrap; no usage/prerequisites |
| Configuration constants | [MISSING] | Missing — no `SCOPES` dict, no `REQUIRED_KEYS` list |
| Scope management | [MISSING] | Missing — no `scope_exists()`, no `create_scope()`, no `create-scope` CLI call |
| Key registration | `get_secret()` function | Partial — interacts with Databricks secrets but reads (retrieval) not writes (registration) |
| Entry point / CLI | [MISSING] | Missing — no `argparse`, no `main()`, no `if __name__ == "__main__":` guard |

**Approach note:** Participant implemented a secrets **accessor** (runtime reader) rather than a secrets **bootstrap** (setup writer). The accessor module is a valid and well-designed pipeline component — but it does not satisfy the bootstrap task. Both files would be needed in a complete pipeline: the bootstrap script to provision secrets once, and the accessor module to read them at runtime.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No CLI interface (`argparse` / `--env`) | −4 pts | **Yes** — no `argparse`, no `--env` argument anywhere |
| No scope creation anywhere | −4 pts | **Yes** — no `create-scope` command, no `create_scope()` function |
| No key registration anywhere | −4 pts | **Yes** — no `secrets put`, no `register_key()` — only `secrets.get()` (read) |
| No SCOPES dict or env-to-scope mapping | −3 pts | **Yes** — no dict mapping dev/prod to scope names |
| No REQUIRED_KEYS list | −2 pts | **Yes** — no list of key names to register |
| Hardcoded secret value | −5 pts | **No** — no literal passwords, tokens, or credential strings |
| Uses `input()` instead of `getpass` | −3 pts | **No** — no interactive input at all |
| No usage/prerequisites docstring | −2 pts | **Yes** — no module-level usage or prerequisites block; function docstring only |
| No idempotency check (scope_exists) | −2 pts | **Yes** — no scope existence check before creation |

**Raw deduct total: −21 pts → capped at −15 pts**

---

## Section Feedback

### Header/Preamble — 50/100 (weight 20 → 10.0 pts)

**Criteria scored:** Content completeness (60%), `has_usage_docstring` (20%), `has_task_id` (10%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 60% | 45/100 | TASK-ENV-002 ✓; clear module purpose stated; "Never call dbutils.secrets.get() directly" is a useful guideline; but purpose is accessor not bootstrap — no usage instructions, no prerequisites |
| `has_usage_docstring` | 20% | 0/100 | No module-level `Usage:` / `Prerequisites:` docstring; only function-level docstring |
| `has_task_id` | 10% | 100/100 | TASK-ENV-002 traceability tag present |
| Structure | 10% | 95/100 | Clean 3-line comment block before imports |

**Strengths:**
- TASK-ENV-002 provides traceability.
- "Never call dbutils.secrets.get() directly" is a good pipeline convention documented at the module level.

**Gaps:**
- No `Usage:` block showing how to run the script.
- No `Prerequisites:` section (Databricks CLI, env vars).
- Module described as "access module" not "bootstrap script" — wrong task orientation.

**Improvement items:**
- [ ] Add module-level docstring:
  ```python
  """
  Usage:
      python config/secrets_config.py --env dev
      python config/secrets_config.py --env prod

  Prerequisites:
      - Databricks CLI installed and authenticated
      - DATABRICKS_HOST and DATABRICKS_TOKEN environment variables set
  """
  ```

---

### Configuration constants — 0/100 (weight 20 → 0.0 pts)

**[MISSING]** — No `SCOPES` dict and no `REQUIRED_KEYS` list anywhere in the file. The reference defines:

```python
SCOPES = {
    "dev": "globalsales-dev",
    "prod": "globalsales-prod",
}
REQUIRED_KEYS = ["source_jdbc_url", "source_jdbc_user", "source_jdbc_password"]
```

These constants are the central configuration artifact of the bootstrap script — they define which scopes exist and which keys must be registered.

**Improvement items:**
- [ ] Add `SCOPES` dict mapping `dev`/`prod` to scope names (`globalsales-dev`, `globalsales-prod`).
- [ ] Add `REQUIRED_KEYS` list with all required secret key names.

---

### Scope management — 0/100 (weight 20 → 0.0 pts)

**[MISSING]** — No `scope_exists()` check, no `create_scope()` function, and no `databricks secrets create-scope` CLI call anywhere. The reference implements an idempotent scope bootstrap:

```python
def scope_exists(scope: str) -> bool: ...
def create_scope(scope: str) -> None:
    if scope_exists(scope):
        return   # idempotent guard
    ...
```

**Improvement items:**
- [ ] Add `_run(cmd)` utility function for subprocess calls with error handling.
- [ ] Add `scope_exists(scope)` checking `databricks secrets list-scopes`.
- [ ] Add `create_scope(scope)` with idempotency guard.

---

### Key registration — 38/100 (weight 20 → 7.6 pts)

**Criteria scored:** Content completeness (55%), `has_getpass` (25%), `has_no_hardcoded_values` (10%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 20/100 | `get_secret()` reads secrets via `dbutils.secrets.get()` — a legitimate runtime accessor; but reads (retrieval) ≠ registers (provisioning). No `secrets put` or write operation anywhere |
| `has_getpass` | 25% | 0/100 | No `getpass.getpass()` — not applicable for a read-only accessor; absent because the file doesn't provision secrets |
| `has_no_hardcoded_values` | 10% | 100/100 | No literal credential values anywhere — secure by design |
| Structure | 10% | 100/100 | Well-structured `get_secret(scope, key)` function; clear docstring; `ImportError` + generic `Exception` handling is production-quality |

**Strengths:**
- `get_secret()` is well-engineered: separates `ImportError` (non-Databricks environments for unit tests) from runtime exceptions with helpful error messages.
- Test-friendly design: "Mock get_secret() in unit tests" note in docstring.
- `has_no_hardcoded_values`: no credentials anywhere.

**Gaps:**
- Reads secrets, does not register them.
- No `getpass` secure input — required for bootstrap registration.

**Improvement items:**
- [ ] Add `register_key(scope, key)` function using `getpass.getpass()` to collect value and invoke `databricks secrets put`.

---

### Entry point / CLI — 0/100 (weight 20 → 0.0 pts)

**[MISSING]** — No `argparse`, no `main()` function, no `if __name__ == "__main__":` guard. The reference entry point parses `--env dev/prod`, resolves the scope, calls `create_scope()` + loops over `REQUIRED_KEYS` calling `register_key()`, and prints a verification hint.

**Improvement items:**
- [ ] Add `main()` function with `argparse` (`--env` with `choices=["dev", "prod"]`).
- [ ] Add `if __name__ == "__main__": main()` guard.
- [ ] Print verification command at end: `databricks secrets list --scope <scope>`.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add `SCOPES` dict + `REQUIRED_KEYS` list | Configuration constants | +16 pts + removes −3 −2 deducts = +21 pts |
| 2 | Add scope management functions (`_run`, `scope_exists`, `create_scope`) | Scope management | +16 pts + removes −4 −2 deducts = +22 pts |
| 3 | Add `register_key()` with `getpass` | Key registration | +9 pts + removes −4 deduct = +13 pts |
| 4 | Add `main()` + `argparse` CLI entry point | Entry point / CLI | +12 pts + removes −4 deduct = +16 pts |
| 5 | Add module-level `Usage:` + `Prerequisites:` docstring | Header/Preamble | +3 pts + removes −2 deduct = +5 pts |

---

## Priority Actions

1. **Rewrite as a bootstrap script** — the entire file needs to be restructured from an accessor module to a CLI provisioning script. Start with `SCOPES` dict and `REQUIRED_KEYS` list, then add `scope_exists()` + `create_scope()` + `register_key()` + `main()`. This recovers up to **+97 pts** from the current base.
2. **Keep `get_secret()` as a separate file** — the accessor module is genuinely useful for pipeline notebooks. Rename it to `secrets_accessor.py` or `secrets_reader.py` and keep it as a companion module.
3. **Add `getpass` to `register_key()`** — never use `input()` for secret values; `getpass.getpass()` prevents terminal echo.

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

*Report generated by skill 35-migvisor-task-checker-secrets-config on 2026-09-04*
