# Check Report: pipeline-runbook
**Trainee:** Purchasing_Project
**Product:** Purchases
**Date:** 2026-09-23
**Score:** 0/100 — Incomplete

## File Status
**File not submitted.**

Expected path: `Purchasing_Project/products/Purchases/current/codebase/docs/runbook.md`
Reference answer: `reference/answers/module_5/codebase/docs/pipeline_runbook.md`

## Impact
Submitting this deliverable would add approximately 4.8 points to the overall 21-skill average score.

## Recommended Action
Create the pipeline runbook using the reference as a guide. Key sections typically include:
- Daily Monitoring Checklist (job run status, row counts, DQ rejection counts, watermark advance check)
- Failure Response procedures (what to do when the MERGE fails, when QV-001 blocks the watermark)
- DQ Investigation guide (SQL queries to inspect stg.dq_rejections, unknown-key fallback analysis)
- Reprocessing Guide (how to re-run a failed batch safely)
- Escalation Path (who to contact and when)
