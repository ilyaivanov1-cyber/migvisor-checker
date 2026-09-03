---
task_id: TASK-SEC-002
skill: task-checker-secrets-rotation-runbook
participant_file: trainees/trainee_1/secrets_rotation_runbook.md
reference_file: reference/secrets_rotation_runbook.md
product: Sales_Orders
generated: 2026-09-03
total_score: 12/100
grade: Incomplete
---

# TASK-SEC-002 Check Report

**Product:** Sales_Orders  
**Reference:** Purchase (globalpurchase)  
**Participant file:** `trainees/trainee_1/secrets_rotation_runbook.md`  
**Reference file:** `reference/secrets_rotation_runbook.md`  
**Generated:** 2026-09-03

---

## Score Summary

**Secrets Rotation Runbook Score: 12/100**

| Section | Reference Title | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|---|
| Header Metadata | (header block) | 14 | 65/100 | 9.1 | ⚠ |
| 1. Trigger Conditions | ## 1. Trigger Conditions | 14 | 0/100 | 0.0 | ✗ |
| 2. Rotation Procedure | ## 2. Rotation Procedure | 15 | 81/100 | 12.2 | ✓ |
| 3. Verification Steps | ## 3. Verification Steps | 14 | 62/100 | 8.7 | ⚠ |
| 4. Rollback Procedure | ## 4. Rollback Procedure | 15 | 24/100 | 3.6 | ✗ |
| 5. Notification Checklist | ## 5. Notification Checklist | 14 | 0/100 | 0.0 | ✗ |
| 6. Rotation Log | ## 6. Rotation Log | 14 | 0/100 | 0.0 | ✗ |
| **Subtotal** | | | | **33.6** | |
| Auto-deducts | | | | **−22** | |
| **Total** | | | | **12/100** | |

**Grade: Incomplete**

> **Weight calculation:** N = 7, base_weight = floor(100/7) = 14, remainder = 2. Rotation Procedure and Rollback Procedure each receive +1 → 15 pts. All others → 14 pts.

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| Header Metadata | Lines 1–2 before first `##` | Direct match |
| 1. Trigger Conditions | [MISSING] | Missing — no trigger list anywhere in document |
| 2. Rotation Procedure | `## Rotation procedure` (Steps 1, 2, 5) | Good match — different structure but functionally equivalent; single scope instead of dev/prod |
| 3. Verification Steps | `## Rotation procedure` (Steps 3, 4) — embedded | Partial — verification within rotation section; 2 of 4 reference topics covered |
| 4. Rollback Procedure | `## Emergency rotation` | Partial — incident-triggered forward rotation ≠ re-rotation to previous credentials on failure |
| 5. Notification Checklist | [MISSING] | Missing — no checklist or stakeholder list anywhere |
| 6. Rotation Log | [MISSING] | Missing — no rotation audit table anywhere |

**Extra participant sections (unscored):** `## Overview`, `## Secrets inventory`, `## [PENDING: CX-P04] — OLTP credential rotation` — no direct reference equivalents; inventory and overview add context value.

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| No bash CLI code blocks anywhere | −4 pts | **No** — `databricks secrets put-secret` and `databricks jobs run-now` present |
| No rotation trigger conditions | −4 pts | **Yes** — no list of conditions (scheduled rotation, security incident, service account change, migration) anywhere in document |
| No post-rotation verification steps | −4 pts | **No** — Steps 3 and 4 of `## Rotation procedure` cover verification |
| No rollback or recovery procedure | −4 pts | **No** — `## Emergency rotation` is a form of emergency recovery procedure |
| No notification checklist or stakeholder list | −3 pts | **Yes** — no notification section, no stakeholder names, no `- [ ]` items anywhere |
| Missing H2 section | −5 pts each (max −15) | **Yes** — Trigger Conditions (−5), Notification Checklist (−5), Rotation Log (−5) → **−15 pts** (cap reached) |
| Hardcoded credential value in code block | −5 pts | **No** — `<new-value>` is an angle-bracket placeholder, not a literal credential |
| Bash uses literal `--string-value` credential | −3 pts | **No** — `--string-value "<new-value>"` uses placeholder; no actual credential value present |

**Total auto-deducts: −22 pts**

---

## Section Feedback

### Header Metadata — 65/100 (weight 14 → 9.1 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Runbook title in H1 | 35% | 100/100 | "Secrets Rotation Runbook — Sales_Orders Pipeline" — clear and descriptive |
| Task ID / traceability tag | 30% | 100/100 | `_TASK-SEC-005 \| [PENDING: CX-P04] OLTP credential rotation section_` — task ID + pending flag present |
| Scope / catalog reference | 20% | 0/100 | `globalsales` first appears in `## Overview`; no scope reference in the header block itself |
| Author / generated date | 15% | 0/100 | No author, version, or created date before first `##` |

**Improvement items:**
- [ ] Add `Scope: globalsales` to the header block.
- [ ] Add a generated date or version line.

---

### 1. Trigger Conditions — 0/100 (weight 14 → 0.0 pts)

**[MISSING]** — Participant document has no section listing when rotation should be triggered. The reference enumerates four conditions: scheduled rotation (every 90 days), security incident/suspected exposure, service account change, and JDBC URL or database migration.

**Improvement items:**
- [ ] Add a `## Trigger Conditions` section with a bullet list covering: (1) scheduled rotation cadence (e.g., every 90 days), (2) security incident / suspected credential exposure, (3) service account or principal change, (4) source system migration or JDBC URL change.

---

### 2. Rotation Procedure — 81/100 (weight 15 → 12.2 pts)

**Criteria scored:** Content completeness (70%), Bash Commands (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 74/100 | Prepare → update → revoke flow maps well to reference; single `globalsales` scope instead of separate dev/prod scopes; "do not use old credential after new issued" slightly differs from reference's safer "do not revoke old until pipeline verified" |
| Bash Commands | 20% | 100/100 | `databricks secrets put-secret globalsales <key-name> --string-value "<new-value>"` — complete, targets participant scope, uses acceptable placeholders |
| Structure | 10% | 94/100 | H2 heading + numbered H3 steps; each step has an intro sentence; bash code blocks fenced correctly |

**Strengths:**
- 5-step procedure is comprehensive: obtain → update → verify → confirm pipeline pickup → revoke old.
- Step 5 (Revoke old credential) explicitly addresses cleanup, adding security value.
- Verification is embedded inline with actionable bash commands and specific notebook reference (`nb_extract_watermark`).
- `bi_endpoint_token` rotation path is documented separately (SQL Warehouse PAT via Power BI Desktop).

**Gaps:**
- Single `globalsales` scope; no separate dev-scope and prod-scope rotation commands.
- "Do not use the old credential after the new one is issued" — this is less safe than the reference's guidance (reference: "do not revoke until pipeline is verified with new ones").

**Improvement items:**
- [ ] Add separate rotation commands for `globalsales-dev` and `globalsales-prod` scopes once dev/prod split is established.
- [ ] Revise Step 1 safety note to match reference: keep old credential active until new one is verified working, then revoke.

---

### 3. Verification Steps — 62/100 (weight 14 → 8.7 pts)

**Criteria scored:** Content completeness (90%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 90% | 61/100 | Manual job trigger (`databricks jobs run-now`) ✓; notebook auth error check ✓; PII compliance check (`nb_pii_compliance_check`) absent ✗; `stg.lineage` success check absent ✗ |
| Structure | 10% | 69/100 | No dedicated `## Verification` H2; embedded within Rotation procedure as Steps 3–4; bash code block present and fenced |

**Strengths:**
- `databricks jobs run-now --job-id <watermark-job-id>` is a specific, actionable trigger command.
- Step 4 explains automatic secret pickup (no cluster restart needed) — useful operational context.

**Gaps:**
- Missing PII compliance check equivalent (reference: run `nb_pii_compliance_check` to verify zero hardcoded credentials).
- No lineage check — reference requires confirming `stg.lineage` shows `status = 'success'`.
- Verification steps are embedded inside Rotation Procedure, not in their own section.

**Improvement items:**
- [ ] Add a `## Verification Steps` section (or at minimum a dedicated H3 in Rotation procedure).
- [ ] Add a lineage check step: query `stg.lineage` (or equivalent) to confirm `status = 'success'` after the rotation run.
- [ ] Add a PII/hardcoded credential audit step.

---

### 4. Rollback Procedure — 24/100 (weight 15 → 3.6 pts)

**Criteria scored:** Content completeness (70%), Bash Commands (20%), Structure (10%)

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Content completeness | 70% | 21/100 | `## Emergency rotation` addresses credential compromise (incident response) — a different scenario from rollback (new credentials fail → revert to old). Re-rotation to previous credentials is absent; no workflow re-trigger for recovery confirmation; no investigation step |
| Bash Commands | 20% | 0/100 | No bash commands in `## Emergency rotation`; rollback CLI command absent |
| Structure | 10% | 93/100 | Clear H2 heading; concise intro sentence; well-formatted prose |

**Strengths:**
- Emergency rotation section correctly directs operators to perform Steps 1–3 immediately on incident.
- Mentions automatic `nightly_etl_main` pickup — no manual restart required.

**Gaps:**
- Core rollback action missing: reference requires re-rotating to the **previous** credential immediately when new credentials fail (not just rotating forward again).
- No bash command for rollback re-rotation.
- No instruction to re-trigger the workflow to confirm recovery.
- "Notify the security team" is vague — no named contact or channel.

**Improvement items:**
- [ ] Add a `## Rollback Procedure` section distinct from Emergency rotation.
- [ ] Include bash command: `databricks secrets put-secret globalsales <key-name> --string-value "<previous-value>"` (or interactive `put` variant).
- [ ] Add numbered steps: (1) re-rotate to previous credential, (2) re-trigger pipeline to confirm recovery, (3) investigate new credential failure before retrying.

---

### 5. Notification Checklist — 0/100 (weight 14 → 0.0 pts)

**[MISSING]** — No notification checklist or stakeholder list anywhere in the document. The reference requires notifying: Data Engineering lead, Platform Security team, and on-call engineer (for incident-triggered rotations). The `## Emergency rotation` section mentions "notify the security team" but provides no structured checklist.

**Improvement items:**
- [ ] Add a `## Notification Checklist` section with `- [ ]` items:
  - `- [ ] Data Engineering lead`
  - `- [ ] Platform Security team`
  - `- [ ] On-call engineer (incident-triggered rotations only)`

---

### 6. Rotation Log — 0/100 (weight 14 → 0.0 pts)

**[MISSING]** — No rotation audit log table in the participant document. The reference maintains a table with columns: Date, Rotated By, Environment, Keys Rotated, Reason.

**Improvement items:**
- [ ] Add a `## Rotation Log` section with a Markdown audit table:

  | Date | Rotated By | Environment | Keys Rotated | Reason |
  |---|---|---|---|---|
  | *(first entry)* | | globalsales | source_jdbc_url, source_jdbc_user, source_jdbc_password | Initial setup |

---

## Improvement Items (ordered by impact)

| # | Gap | Section | Est. Points Recoverable |
|---|---|---|---|
| 1 | Add `## Notification Checklist` with `- [ ]` stakeholder items | Notification Checklist | +10 pts + removes −3 deduct = +13 pts |
| 2 | Add `## Rotation Log` audit table (Date / Rotated By / Environment / Keys / Reason) | Rotation Log | +10 pts |
| 3 | Add `## Trigger Conditions` bullet list (scheduled, incident, service account, migration) | Trigger Conditions | +10 pts + removes −4 deduct = +14 pts |
| 4 | Add `## Rollback Procedure` with re-rotation bash command and numbered steps | Rollback Procedure | +7 pts (Rollback raw improvement from 24→80) |
| 5 | Add dedicated `## Verification Steps` section with lineage check and PII audit | Verification Steps | +5 pts (structure improvement) |
| 6 | Add scope/catalog reference and date to header block | Header Metadata | +2 pts |

---

## Priority Actions

1. **Add `## Trigger Conditions`** — entirely missing and triggers the −4 auto-deduct plus −5 missing-H2 penalty. A simple bullet list (schedule, incident, service account change, migration) recovers up to **+14 pts**.
2. **Add `## Notification Checklist`** — missing section with no participant content; three `- [ ]` lines remove the −3 notification deduct and add 14 pts of section weight. Worth up to **+13 pts**.
3. **Add `## Rotation Log`** — a five-column Markdown table with one placeholder row takes under a minute to add and recovers up to **+10 pts** at minimal effort.
4. **Add a proper `## Rollback Procedure`** — the current Emergency rotation section covers incident response (forward) but not failure recovery (backward). A bash re-rotation command + three numbered steps recovers up to **+7 pts** in the Rollback section.

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

*Report generated by skill 32-migvisor-task-checker-secrets-rotation-runbook on 2026-09-03*
