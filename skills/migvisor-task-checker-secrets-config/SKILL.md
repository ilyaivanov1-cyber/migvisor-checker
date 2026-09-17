# Skill 35 — task-checker-secrets-config

## Identity

- **Skill number:** 35
- **Skill name:** task-checker-secrets-config
- **Trigger phrases:** "check secrets config", "check my secrets config", "run 35", "run skill 35"
- **Participant file:** `trainees/<trainee_name>/secrets_config.py`
- **Reference file:** `reference/secrets_config.py`
- **Output path:** `checks/<trainee_name>/secrets-config/TASK-SC-001_check_report.md`
- **Task ID prefix:** TASK-SC

---

## Purpose

Evaluate a Databricks Secrets bootstrap Python script against the reference. The reference is a CLI script (`--env dev/prod`) that creates secret scopes and registers required keys interactively using `getpass` — never hardcoding values.

The participant may implement either:
- **Type A — Bootstrap script:** CLI-driven scope creation + key registration (matches reference intent)
- **Type B — Accessor module:** A `get_secret()` wrapper that reads secrets via `dbutils` for use by pipeline notebooks

Both types are scored against the reference rubric. Type B scores lower because scope creation, key registration, CLI interface, and configuration constants are absent — but code quality, error handling, and no-hardcoded-values discipline are credited.

Scope/catalog names differ between reference (globalpurchase) and participant (e.g. globalsales) — never penalised.

---

## Step 1 — Resolve files

1. Identify the trainee name:
   - If only one subfolder exists under `trainees/`, use it automatically.
   - If multiple exist, use the `trainee=<name>` argument or ask.
2. Set:
   - `participant_file = trainees/<trainee_name>/secrets_config.py`
   - `reference_file = reference/secrets_config.py`
3. Read both files fully. Detect whether the participant implemented Type A (bootstrap) or Type B (accessor) before scoring.

---

## Step 2 — Detect sections

**Reference sections (fixed — N=5):**

| # | Section | Detection rule |
|---|---|---|
| 0 | Header/Preamble | Comment block + module docstring before first `import` or `from` statement |
| 1 | Configuration constants | `SCOPES` dict and `REQUIRED_KEYS` list (or equivalent env-to-scope mapping) |
| 2 | Scope management | `scope_exists()` + `create_scope()` functions (idempotent scope bootstrap) |
| 3 | Key registration | `register_key()` function using secure input (`getpass`) to register each key |
| 4 | Entry point / CLI | `main()` function + `argparse` with `--env` argument + `if __name__ == "__main__":` guard |

**N = 5** sections.

For each reference section, find the best matching participant code block by content intent. If absent, mark **[MISSING]**.

---

## Step 3 — Calculate weights

```
N = 5
base_weight = floor(100 / 5) = 20
remainder = 100 − (20 × 5) = 0
→ all sections receive equal weight of 20 pts
```

| Section | Weight |
|---|---|
| Header/Preamble | 20 |
| Configuration constants | 20 |
| Scope management | 20 |
| Key registration | 20 |
| Entry point / CLI | 20 |
| **Total** | **100** |

---

## Step 4 — Section flags

| Flag | Detection rule |
|---|---|
| `has_cli_interface` | `argparse` with `--env` or equivalent environment selector |
| `has_scope_dict` | `SCOPES` dict or equivalent env → scope mapping |
| `has_required_keys` | `REQUIRED_KEYS` list or equivalent key inventory |
| `has_scope_creation` | `create_scope()` or `databricks secrets create-scope` call |
| `has_scope_exists_check` | `scope_exists()` or idempotency check before creating |
| `has_key_registration` | `register_key()` or `secrets put` / `dbutils.secrets` write equivalent |
| `has_getpass` | `getpass.getpass()` or equivalent secure non-echoing input |
| `has_no_hardcoded_values` | No literal credential strings in any statement |
| `has_usage_docstring` | Module-level docstring or comment block documenting usage + prerequisites |
| `has_task_id` | TASK-* or CFG-* traceability tag in header |
| `is_type_b_accessor` | File contains `get_secret()` / `dbutils.secrets.get()` but no scope creation or CLI |

---

## Step 5 — Adaptive criteria per section

Score each section 0–100, then apply the weight.

**If `is_type_b_accessor = TRUE`:** note the implementation type in the Section Matching Log and score each section against the reference rubric. Credit any overlapping elements (no hardcoded values, task ID, Python code quality) but score missing bootstrap elements as 0.

### Header / Preamble (weight 20)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 60% | CFG/TASK ID, module purpose, usage instructions, prerequisites |
| `has_usage_docstring` | 20% | Module-level docstring with `Usage:` and `Prerequisites:` blocks |
| `has_task_id` | 10% | TASK-* or CFG-* tag in header comment |
| Structure | 10% | Comment block before imports; docstring present; clean formatting |

### Configuration constants (weight 20)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 60% | `SCOPES` dict with dev/prod keys → scope names; `REQUIRED_KEYS` list |
| `has_scope_dict` | 25% | Env-to-scope mapping present and correct |
| `has_required_keys` | 15% | Key list matches expected secrets (jdbc_url / jdbc_username / jdbc_password or participant equivalents) |

**If MISSING:** raw score = 0; apply −3 auto-deduct.

### Scope management (weight 20)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 55% | `scope_exists()` check + `create_scope()` logic; subprocess/CLI invocation |
| `has_scope_exists_check` | 25% | Idempotency guard before creating scope |
| `has_scope_creation` | 10% | `create-scope` command or equivalent present |
| Structure | 10% | Functions separated; docstrings or comments; error handling via `_run()` or equivalent |

**If MISSING:** raw score = 0; apply −4 auto-deduct.

### Key registration (weight 20)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 55% | `register_key()` reads value securely, invokes `secrets put`, confirms non-logging |
| `has_getpass` | 25% | `getpass.getpass()` or equivalent secure input (never `input()`) |
| `has_no_hardcoded_values` | 10% | No literal secret values in any statement |
| Structure | 10% | Function accepts scope + key; clear print confirmation; value not logged |

**Note:** A Type B `get_secret()` accessor partially maps here — credit `has_no_hardcoded_values` and structure, but score content completeness low (read ≠ register).

**If MISSING:** raw score = 0; apply −4 auto-deduct.

### Entry point / CLI (weight 20)

| Criterion | Weight | Notes |
|---|---|---|
| Content completeness | 55% | `main()` orchestrates scope creation + key loop; `argparse` with `--env` |
| `has_cli_interface` | 30% | `argparse` with `--env dev/prod` required argument present |
| Structure | 15% | `if __name__ == "__main__":` guard; prints progress + verification hint |

**If MISSING:** raw score = 0; apply −4 auto-deduct.

---

## Step 6 — Auto-deducts

Apply globally after section scoring. Cap at **−20 pts** total.

| Condition | Penalty | How to detect |
|---|---|---|
| No CLI interface (`argparse` / `--env`) | −4 pts | No `argparse` and no `--env` argument anywhere |
| No scope creation anywhere | −4 pts | No `create-scope` and no `create_scope()` call anywhere |
| No key registration anywhere | −4 pts | No `secrets put` and no `register_key()` anywhere |
| No SCOPES dict or env-to-scope mapping | −3 pts | No dict mapping `dev`/`prod` to scope names |
| No REQUIRED_KEYS list | −2 pts | No list of key names to register |
| Hardcoded secret value | −5 pts | Literal password, token, or credential string anywhere |
| Uses `input()` instead of `getpass` for secret value | −3 pts | `input(...)` used to collect a secret value (echoes to terminal) |
| No usage/prerequisites docstring | −2 pts | No module-level docstring or comment block explaining how to run the script |
| No idempotency check (scope_exists) | −2 pts | No check before creating scope — would fail on re-run if scope exists |

---

## Step 7 — Score calculation

```
weighted_subtotal = Σ (section_raw_score × section_weight / 100)
total = max(0, round(weighted_subtotal − auto_deducts))
```

**Grade scale:**

| Score | Grade |
|---|---|
| 90–100 | Excellent |
| 75–89 | Good |
| 60–74 | Acceptable |
| 45–59 | Needs Work |
| 0–44 | Incomplete |

---

## Step 8 — Write report

Create the output directory if it does not exist: `checks/<trainee_name>/secrets-config/`

Output file: `TASK-SC-001_check_report.md`

If a file already exists at that path, increment the suffix (`_v2`, `_v3`, …) and never overwrite.

**Report structure:**

```markdown
---
task_id: TASK-SC-001
skill: task-checker-secrets-config
participant_file: trainees/<trainee_name>/secrets_config.py
reference_file: reference/secrets_config.py
product: <product_name>
generated: <YYYY-MM-DD>
total_score: <N>/100
grade: <grade>
---

# TASK-SC-001 Check Report

**Product:** <product>
**Reference:** Purchase (globalpurchase)
**Participant file:** `trainees/<trainee_name>/secrets_config.py`
**Reference file:** `reference/secrets_config.py`
**Generated:** <date>

---

## Score Summary

**Secrets Config Score: <N>/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header/Preamble | (header block) | 20 | .../100 | ... | ✓/⚠/✗ |
| Configuration constants | SCOPES + REQUIRED_KEYS | 20 | .../100 | ... | ✓/⚠/✗ |
| Scope management | scope_exists + create_scope | 20 | .../100 | ... | ✓/⚠/✗ |
| Key registration | register_key | 20 | .../100 | ... | ✓/⚠/✗ |
| Entry point / CLI | main + argparse | 20 | .../100 | ... | ✓/⚠/✗ |
| **Subtotal** | | | | **...** | |
| Auto-deducts | | | | **−...** | |
| **Total** | | | | **<N>/100** | |

**Grade: <grade>**

> **Weight calculation:** N = 5, base_weight = floor(100/5) = 20, remainder = 0 → all sections receive equal weight of 20 pts.

---

## Implementation Type

**Participant implementation type:** Type A — Bootstrap script / Type B — Accessor module

[One sentence explaining what the participant built and how it relates to the reference intent.]

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header/Preamble | ... | Direct / Partial / [MISSING] |
| Configuration constants | ... | ... |
| Scope management | ... | ... |
| Key registration | ... | ... |
| Entry point / CLI | ... | ... |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No CLI interface | −4 pts | Yes/No — [reason] |
| No scope creation | −4 pts | Yes/No — [reason] |
| No key registration | −4 pts | Yes/No — [reason] |
| No SCOPES dict | −3 pts | Yes/No — [reason] |
| No REQUIRED_KEYS list | −2 pts | Yes/No — [reason] |
| Hardcoded secret value | −5 pts | Yes/No |
| Uses input() for secret | −3 pts | Yes/No |
| No usage/prerequisites docstring | −2 pts | Yes/No |
| No idempotency check | −2 pts | Yes/No |

**Total auto-deducts: −N pts**

---

## Section Feedback

### Header/Preamble — <raw>/100 (weight 20 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Configuration constants — <raw>/100 (weight 20 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Scope management — <raw>/100 (weight 20 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Key registration — <raw>/100 (weight 20 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

### Entry point / CLI — <raw>/100 (weight 20 → <weighted> pts)

[Criteria table + strengths + gaps + improvement items]

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | ... | ... | +N pts |
...

---

## Priority Actions

1. **[Highest-impact fix]** — [description] worth up to **+N pts**.
2. **[Second fix]** — [description] worth up to **+N pts**.
3. **[Third fix]** — [description] worth up to **+N pts**.

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

*Report generated by skill 35-migvisor-task-checker-secrets-config on <date>*
```

---

## Step 9 — Console summary

After writing the report, output a console verdict in this exact format:

```
╔══════════════════════════════════════════════════════════════════╗
║  TASK-SC-001 · Secrets Config · <product> · <date>               ║
╠══════════════════════════════════════════════════════════════════╣
║  Score: <N>/100 · Grade: <grade>                                 ║
╚══════════════════════════════════════════════════════════════════╝
```

Follow immediately with a **5–6 sentence plain-English verdict**:

1. Overall score, grade, and implementation type detected (Type A bootstrap or Type B accessor).
2. What was done well — best-scoring section or strongest code quality element.
3. The most critical gap — which bootstrap elements are absent and why they matter.
4. **Must state the numeric score and name the two highest-priority fixes.**
5. Note whether the participant's implementation has standalone value (e.g. a good accessor module has pipeline utility even if it doesn't match the bootstrap task).
6. Recommendation: implement the bootstrap script from scratch, or adapt existing code.
