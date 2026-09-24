# Pipeline Runbook Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 72/100 (Acceptable)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| Daily Monitoring Checklist | 17 | 40 | Structured checklist missing; lacks job run status, row counts, dq_rejections count, etl_cutoff check |
| Failure Response | 17 | 80 | On-failure procedures documented |
| DQ Investigation | 17 | 50 | Missing SQL queries to inspect bronze.dq_rejections |
| Reprocessing Guide | 17 | 78 | Historical backfill procedure described |
| Escalation Path | 16 | 82 | On-call and escalation contacts present |
| Glossary | 16 | 78 | Key terms defined |

## Auto-deducts

None.

## Summary

The pipeline runbook scored 72/100 (Acceptable), with Failure Response, Reprocessing Guide, and Escalation Path sections performing well (75 to 82). The Daily Monitoring Checklist section is the biggest gap at only 40/100 — it lacks a structured checklist covering job run status, row counts, dq_rejections count, etl_cutoff update check, and lineage log entry verification. The DQ Investigation section is also weak at 50/100, missing SQL queries to inspect bronze.dq_rejections. Adding a complete Daily Monitoring Checklist is the top fix at +12 pts; adding the DQ Investigation SQL queries is second at +8 pts.

## Priority Actions

1. Add complete Daily Monitoring Checklist with job status, row counts, dq_rejections count, etl_cutoff update, and lineage log verification — +12 pts
2. Add DQ Investigation SQL queries for inspecting bronze.dq_rejections — +8 pts
