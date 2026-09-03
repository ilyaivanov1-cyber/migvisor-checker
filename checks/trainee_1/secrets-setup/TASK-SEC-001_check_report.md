---
task_id: TASK-SEC-001
skill: task-checker-secrets-setup
participant_file: trainees/trainee_1/secrets_setup.md
reference_file: reference/secrets_setup.md
product: Sales_Orders
generated: 2026-09-03
total_score: 24/100
grade: Incomplete
---

# TASK-SEC-001 Check Report

**Product:** Sales_Orders  
**Reference:** Purchase (globalpurchase)  
**Participant file:** `trainees/trainee_1/secrets_setup.md`  
**Reference file:** `reference/secrets_setup.md`  
**Generated:** 2026-09-03

---

## Score Summary

**Secrets Setup Score: 24/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 11 | 65/100 | 7.2 | ⚠ |
| Prerequisites | ## Prerequisites | 11 | 0/100 | 0.0 | ✗ |
| Step 1 — Create the Dev Scope | ## Step 1 — Create the Dev Scope | 11 | 64/100 | 7.0 | ⚠ |
| Step 2 — Create the Prod Scope | ## Step 2 — Create the Prod Scope | 11 | 43/100 | 4.7 | ⚠ |
| Step 3 — Register Required Keys (Dev) | ## Step 3 — Register Required Keys (Dev) | 12 | 89/100 | 10.7 | ✓ |
| Step 4 — Register Required Keys (Prod) | ## Step 4 — Register Required Keys (Prod) | 11 | 57/100 | 6.3 | ⚠ |
| Step 5 — Verify | ## Step 5 — Verify (without revealing values) | 11 | 0/100 | 0.0 | ✗ |
| Step 6 — Credential Rotation | ## Step 6 — Credential Rotation | 11 | 84/100 | 9.2 | ✓ |
| Reference | ## Reference | 11 | 30/100 | 3.3 | ✗ |
| **Subtotal** | | | | **48.4** | |
| Auto-deducts | | | | **−24** | |
| **Total** | | | | **24/100** | |

**Grade: Incomplete**

> **Weight calculation:** N = 9, base_weight = floor(100/9) = 11, remainder = 1. Step 3 (Register Required Keys Dev) receives +1 → 12 pts. All others → 11 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | Lines 1–2 before first `##` | Direct match |
| Prerequisites | [MISSING] | Missing |
| Step 1 — Create the Dev Scope | `## Secret scope` | Partial — scope creation present but single scope, no dev/prod separation |
| Step 2 — Create the Prod Scope | `## Secret scope` (merged) | Partial — prod scope absent; participant uses unified `globalsales` scope |
| Step 3 — Register Required Keys (Dev) | `## Keys` + `## Adding / updating a key` | Good match — key table + CLI command; merged dev+prod into one scope |
| Step 4 — Register Required Keys (Prod) | `## Keys` + `## Adding / updating a key` (merged) | Partial — same key registration approach applies but no prod-scope commands |
| Step 5 — Verify (without revealing values) | [MISSING] | Missing |
| Step 6 — Credential Rotation | `## Rotation procedure` | Direct match |
| Reference | `## Keys` (partial) | Partial — key inventory present; no documentation links or scope widget reference |

**Extra participant sections (unscored):** `## Access grant`, `## Code-side access` — no reference equivalents; these add operational value but are not in the reference scoring model.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No bash/CLI code blocks anywhere | −4 pts | **No** — `databricks secrets create-scope` and `databricks secrets put` commands present |
| No scope creation command anywhere | −4 pts | **No** — `databricks secrets create-scope --scope globalsales` present in `## Secret scope` |
| No key registration command anywhere | −4 pts | **No** — `databricks secrets put --scope globalsales --key source_jdbc_url` present |
| No verification step anywhere | −4 pts | **Yes** — no `dbutils.secrets.list(...)` or `databricks secrets list` command anywhere in the document |
| No dev/prod scope separation | −3 pts | **Yes** — participant uses a single `globalsales` scope; no dev/prod-labeled scopes or environment separation documented |
| Missing H2 section | −5 pts each (max −15) | **Yes** — Prerequisites (−5), Step 5 Verify (−5), Reference (−5) → **−15 pts** (cap reached) |
| Hardcoded credentials in code block | −5 pts | **No** — no literal passwords, tokens, or connection strings in code blocks |
| ACL command placeholder only | −2 pts | **Yes** — `## Access grant` uses `{{UC_ROLE_SERVICE_PRINCIPAL}}` with a TODO comment |

**Total auto-deducts: −24 pts**

---

## Section Feedback

### Header Metadata — 65/100 (weight 11 → 7.2 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Runbook / guide name in H1 | 35% | 100/100 | "Databricks Secrets Setup — Sales_Orders Pipeline" — clear product and guide name |
| Task ID / traceability tag | 30% | 100/100 | `_TASK-ENV-002_` present on line 2 |
| Catalog / scope reference | 20% | 0/100 | No catalog or scope name in the header block; `globalsales` first appears inside `## Secret scope` |
| Author / generated date | 15% | 0/100 | No author, version, or created date before first `##` |

**Strengths:**
- Product name and task ID both clearly stated.

**Gaps:**
- No scope or catalog reference in header block.
- No generated date or author/version line.

**Improvement items:**
- [ ] Add `Scope: globalsales` or similar to the header block.
- [ ] Add a version or generated date line.

---

### Prerequisites — 0/100 (weight 11 → 0.0 pts)

**[MISSING]** — Participant document has no prerequisites section. The reference lists: Databricks CLI version requirement (`databricks --version ≥ 0.18`), environment variable setup (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`), and network access requirement.

**Improvement items:**
- [ ] Add a `## Prerequisites` section with: (1) Databricks CLI install check (`databricks --version ≥ 0.18`), (2) env var exports for `DATABRICKS_HOST` and `DATABRICKS_TOKEN`, (3) network access requirement.

---

### Step 1 — Create the Dev Scope — 64/100 (weight 11 → 7.0 pts)

**Criteria scored:** Content completeness (50%), Bash Commands (20%), Verification Step (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 50% | 68/100 | Scope creation command present with good context (permission note, scope name); no verify command after creation; single scope instead of dev-labeled scope |
| Bash Commands | 20% | 100/100 | `databricks secrets create-scope --scope globalsales` — syntactically complete, uses participant's own scope name |
| Verification Step | 20% | 0/100 | No verification command after scope creation (reference uses `databricks secrets list-scopes \| grep …`) |
| Structure | 10% | 95/100 | Clear H2 heading; intro paragraph explains scope and permission requirement; bash code block fenced correctly |

**Strengths:**
- Scope creation command is complete and uses the correct participant scope name.
- Intro context ("requires admin or SP with manage-secrets permission") is more informative than the reference.

**Gaps:**
- No verify command after scope creation.
- Scope is not labeled as dev (or equivalent env split).

**Improvement items:**
- [ ] Add a verify step after scope creation: `databricks secrets list-scopes | grep globalsales`.
- [ ] Consider documenting environment-specific scope naming (e.g., `globalsales-dev`, `globalsales-prod`).

---

### Step 2 — Create the Prod Scope — 43/100 (weight 11 → 4.7 pts)

**Criteria scored:** Content completeness (70%), Bash Commands (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 40/100 | Participant uses a unified `globalsales` scope with no prod-labeled variant; concept of environment-separated scopes is absent |
| Bash Commands | 20% | 60/100 | The `create-scope` command in `## Secret scope` covers the creation mechanism but targets a single scope; no prod-scope command |
| Structure | 10% | 30/100 | No dedicated `## Step 2` or prod scope H2; scope creation merged into single section without env distinction |

**Strengths:**
- Scope creation mechanism is understood and documented.

**Gaps:**
- No prod scope (`globalsales-prod` or equivalent) — the reference requires a separate prod scope for safe credential isolation.
- No environment separation documented anywhere.

**Improvement items:**
- [ ] Add a dedicated prod scope creation step: `databricks secrets create-scope --scope globalsales-prod`.
- [ ] Document when dev scope vs prod scope is used (e.g., ETL widget `env_scope` value).

---

### Step 3 — Register Required Keys (Dev) — 89/100 (weight 12 → 10.7 pts)

**Criteria scored:** Content completeness (55%), Bash Commands (20%), Key Inventory (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 82/100 | All 3 JDBC credential key types documented plus `bi_endpoint_token` (extra); interactive entry (Ctrl+D) described; no dev-scope context |
| Bash Commands | 20% | 100/100 | `databricks secrets put --scope globalsales --key source_jdbc_url` — complete; API alternative also valid |
| Key Inventory | 15% | 100/100 | Keys table: 4 keys with Purpose and Note columns; cross-product equivalents: `source_jdbc_url` ≡ `jdbc_url`, `source_jdbc_user` ≡ `jdbc_username`, `source_jdbc_password` ≡ `jdbc_password` |
| Structure | 10% | 90/100 | Two H2 sections (Keys + Adding/updating) work together; table and code blocks correctly formatted |

**Strengths:**
- Keys table is complete with purposes and PENDING status (CX-P04) for each credential.
- Both CLI (`secrets put`) and API alternatives documented.
- `bi_endpoint_token` is an extra key not in the reference — adds useful coverage.
- Interactive entry instruction (Ctrl+D) matches reference's "values entered interactively and never logged" intent.

**Gaps:**
- Keys are registered to a single `globalsales` scope, not a dev-labeled scope.
- No per-environment key table (dev vs prod column).

**Improvement items:**
- [ ] Once dev/prod scopes are added, duplicate key registration commands for `globalsales-prod` scope.

---

### Step 4 — Register Required Keys (Prod) — 57/100 (weight 11 → 6.3 pts)

**Criteria scored:** Content completeness (55%), Bash Commands (20%), Key Inventory (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 55% | 55/100 | Same key registration mechanism applies conceptually to prod; no prod-scope commands documented; no prod-specific key notes |
| Bash Commands | 20% | 65/100 | `databricks secrets put` works for prod if scope name is changed; no prod-specific commands present |
| Key Inventory | 15% | 75/100 | Key names from `## Keys` table apply cross-environment; no prod-specific key notes or values |
| Structure | 10% | 25/100 | No dedicated prod keys section; section entirely merged with dev keys |

**Gaps:**
- No dedicated prod key registration section or commands.
- No note distinguishing prod key values from dev (e.g., prod JDBC URL is different from dev).

**Improvement items:**
- [ ] Add `## Step 4 — Register Required Keys (Prod)` with `--scope globalsales-prod` commands.
- [ ] Note any prod-specific key values or restrictions (e.g., prod JDBC URL requires VPN access).

---

### Step 5 — Verify (without revealing values) — 0/100 (weight 11 → 0.0 pts)

**[MISSING]** — No verification step anywhere in the participant document. The reference uses `dbutils.secrets.list(scope="globalpurchase-dev")` in a notebook, explicitly noting that values are never exposed. This is a security-critical step: it confirms keys were registered correctly without logging the actual credentials.

**Improvement items:**
- [ ] Add a `## Verify` section with:
  ```python
  # Run in a Databricks notebook
  dbutils.secrets.list(scope="globalsales")
  # Expected: [SecretMetadata(key='source_jdbc_password'), SecretMetadata(key='source_jdbc_url'), SecretMetadata(key='source_jdbc_user'), ...]
  ```
- [ ] Add the explanatory note: "The `list()` call returns key names only — values are never exposed."

---

### Step 6 — Credential Rotation — 84/100 (weight 11 → 9.2 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 85/100 | Same external reference document (`config/secrets_rotation_runbook.md`) cited; matches reference verbatim in intent; no intro context |
| Structure | 10% | 75/100 | H2 heading present; content is a single cross-reference line; no intro or context sentence |

**Strengths:**
- Correct rotation runbook path cited.
- Matches reference's level of detail (pointer only, no inline rotation procedure).

**Gaps:**
- No intro sentence explaining when rotation is needed.

**Improvement items:**
- [ ] Add one sentence: "Rotate credentials whenever a team member leaves or credentials are suspected to be compromised."

---

### Reference — 30/100 (weight 11 → 3.3 pts)

**Criteria scored:** Content completeness (75%), Key Inventory (15%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 75% | 33/100 | `## Keys` table documents key names and purposes; no Databricks Secrets documentation hyperlink; no scope widget reference (`env_scope`) |
| Key Inventory | 15% | 100/100 | `## Keys` table enumerates all key names with purposes |
| Structure | 10% | 85/100 | Well-formatted table; no dedicated Reference H2 |

**Gaps:**
- No `## Reference` section with documentation links.
- No reference to `env_scope` widget value or how notebooks select the scope.

**Improvement items:**
- [ ] Add a `## Reference` section with: (1) link to Databricks Secrets docs, (2) note on `env_scope` widget values (`globalsales-dev` / `globalsales-prod`), (3) key names consumed by notebooks.

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add dev/prod scope separation (`globalsales-dev`, `globalsales-prod`) and separate key registration steps | Steps 2 + 4 | +9 pts + removes −3 deduct = +12 pts |
| 2 | Add `## Prerequisites` section (CLI version, env var exports, network access) | Prerequisites | +9 pts + removes −5 missing H2 = +14 pts |
| 3 | Add `## Verify` section with `dbutils.secrets.list(...)` and non-revealing explanation | Step 5 | +7 pts + removes −4 verification deduct + −5 missing H2 = +16 pts |
| 4 | Add `## Reference` section with docs link and scope widget documentation | Reference | +4 pts + removes −5 missing H2 = +9 pts |
| 5 | Resolve `{{UC_ROLE_SERVICE_PRINCIPAL}}` ACL placeholder with actual SP name | Access grant | +2 pts |
| 6 | Add scope/catalog reference and date to header block | Header Metadata | +2 pts |

---

## Priority Actions

1. **Add `## Verify` section** — this is the highest-leverage single fix: removes the −4 verification auto-deduct, removes one −5 missing-H2 deduct, and scores 11 pts of section weight. A single `dbutils.secrets.list(scope="globalsales")` call with the "values never exposed" note is sufficient. Worth up to **+16 pts**.
2. **Add `## Prerequisites` section** — removes the −5 missing-H2 deduct and scores 11 pts of section weight. Needs three items: Databricks CLI version check, `DATABRICKS_HOST`/`DATABRICKS_TOKEN` env var exports, network access note. Worth up to **+14 pts**.
3. **Split into dev/prod scopes** — add `globalsales-dev` and `globalsales-prod` scopes throughout, separate Steps 2 and 4. Removes the −3 dev/prod deduct and substantially improves Steps 2 and 4 scores. Worth up to **+12 pts**.
4. **Add `## Reference` section** — removes the final −5 missing-H2 deduct and adds a documentation anchor for future readers. Worth up to **+9 pts**.

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

*Report generated by skill 31-migvisor-task-checker-secrets-setup on 2026-09-03*
