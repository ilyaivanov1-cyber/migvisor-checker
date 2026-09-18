---
task_id: TASK-RE-001
skill: migvisor-task-checker-requirements
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/requirements.md
reference_file: ./reference/answers/module_5/development_plan/requirements.md
generated: 2026-09-18
total_score: 83/100
grade: Good
---

# TASK-RE-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/requirements.md`  
**Reference file:** `./reference/answers/module_5/development_plan/requirements.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Requirements Score: 83/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| 1. Functional Requirements | 34 | 85/100 | 28.9 | ✓ |
| 2. Non-Functional Requirements | 33 | 80/100 | 26.4 | ✓ |
| 3. Data Quality Requirements | 33 | 84/100 | 27.72 | ✓ |
| **Subtotal** | | | **83.02** | |
| Auto-deducts | | | **0** | |
| **Total** | | | **83/100** | |

**Grade: Good**

> **Weight calculation:** N = 3, base_weight = floor(100/3) = 33, remainder = 1 → +1 to §1 Functional Requirements (highest complexity).

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| FR (Incremental Ingestion) | FR-001 | Direct |
| FR (Watermark Management) | FR-002 | Direct |
| FR (Dimension SCD-2 Supplier) | FR-004 | Direct (combined in trainee) |
| FR (Dimension SCD-2 Stock Item) | FR-005 | Direct (combined in trainee) |
| FR (Fact MERGE) | FR-007 | Direct |
| FR (DQ / Data delivery) | FR-010 | Direct |
| NFR (Freshness, Row count, RI, Business rules, DQ store, UC access) | NFR-001, 003–008 | Direct |
| DQR (Completeness, RI, Quantity, Package, Traceability, Sentinel) | DQR-001–009 | Direct |

---

## Auto-Deducts Applied

No systematic auto-deducts — trainee has more requirements than reference overall.

**Total auto-deducts: 0 pts**

---

## Section Feedback

### 1. Functional Requirements — 85/100 (weight 34 → 28.9 pts)

**Status:** ✓ Present

**Strengths:** 11 FRs with clear table format (ID, Title, Description, Priority, Acceptance Criterion, Source). All core functional requirements are present: incremental extract (FR-001), watermark management (FR-002), lineage key via taskValues (FR-003), SCD-2 supplier resolution (FR-004), SCD-2 stock item resolution (FR-005), date key derivation (FR-006), fact MERGE (FR-007), conditional OPTIMIZE (FR-008), config externalisation (FR-009), SQL Warehouse delivery (FR-010), environment initialisation notebook (FR-011). Acceptance criteria are specific and testable with concrete expected outcomes.

**Gaps vs reference:**
- Reference FR-003 (Supplier SCD-2) includes the full SCD-2 acceptance criteria (two rows per changed supplier — expired + active, sentinel key=0 always present, no active row with `valid_to ≠ '9999-12-31'`). Trainee FR-004 states "after sk_resolver.py executes... non-zero supplier_key" but focuses on key resolution, not dimension load management (SCD-2 expire + insert logic). The dimension load is an external responsibility in trainee's architecture but should be documented.
- Reference has FR-012 (Mart / Serving layer): trainee has no equivalent mart-layer FR — no requirement for materialized views or mart schema objects.
- Reference's acceptance criteria are structured in a numbered list format (1), (2), (3) — trainee uses prose. Both approaches work but the numbered list makes individual criteria independently verifiable.

---

### 2. Non-Functional Requirements — 80/100 (weight 33 → 26.4 pts)

**Status:** ✓ Present

**Strengths:** 12 NFRs covering all key non-functional areas: daily freshness (NFR-001), SQL Warehouse availability (NFR-002), row count reconciliation blocking (NFR-003), RI validation (NFR-004), orphaned SK detection (NFR-005), business rule assertions (NFR-006), DQ rejection store schema (NFR-007), UC access control (NFR-008), ETL notebook skeleton (NFR-009), DDL header block (NFR-010), codebase layout (NFR-011), data retention (NFR-012). Very comprehensive.

**Gaps vs reference:**
- NFR-002 (SQL Warehouse availability) in reference covers BI consumer SLA (99.5% uptime) — trainee NFR-002 is about "SQL Warehouse availability" but states "should-have" and the 99.5% SLA. The reference focuses more on BI consumers' ability to connect without spelling out an SLA percentage.
- NFR-003 (Row count reconciliation) — trainee specifies the exact error message format (`RuntimeError: Row count mismatch: staging=N, inserted=M`) which is excellent. Reference doesn't go this deep.
- Missing NFR for multi-environment support (dev/prod configuration separation via `--env` flag or environment.yaml env key). Reference's IF-003/IF-004 rules imply this but trainee doesn't have an explicit NFR.
- NFR-008 (Unity Catalog access control) mentions "Access role matrix definition is pending (PD-003)" — good traceability reference.

---

### 3. Data Quality Requirements — 84/100 (weight 33 → 27.72 pts)

**Status:** ✓ Present

**Strengths:** 9 DQRs tightly aligned with QA rule IDs. DQR-001 (row count reconciliation — zero tolerance), DQR-002–004 (RI completeness per FK column), DQR-005 (quantity non-negativity), DQR-006 (date key within batch window), DQR-007 (package non-null), DQR-008 (rejection traceability by lineage_key), DQR-009 (surrogate key default coverage — sentinel key=0 not NULL). All have must-have/should-have priority and acceptance criteria.

**Strengths of DQR-009 specifically:** "SELECT COUNT(*) FROM bronze.purchase_staging WHERE supplier_key IS NULL OR stock_item_key IS NULL returns 0" — this precisely tests the key=0 fallback. Excellent.

**Gaps vs reference:** No DQR for detecting stale staging rows (the legacy SSIS bug meant staging accumulated rows; although OVERWRITE mode eliminates this, a DQR asserting `_extracted_at_utc` uniformity across all staging rows would confirm it). Reference doesn't explicitly have this either, but it would be a good addition.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add FR-012 (Mart/Serving layer): materialized view and mart schema FR | §FR | +5 pts |
| 2 | Add dimension load management FRs (SCD-2 expire+insert logic for supplier and stock_item, even if externally owned) | §FR | +3 pts |
| 3 | Add NFR for multi-environment configuration separation (dev/prod via environment.yaml or --env) | §NFR | +3 pts |
| 4 | Convert acceptance criteria from prose to numbered list format for individual testability | All sections | +2 pts |

---

## Priority Actions

1. **Add mart/serving layer FR** — create FR-012 requiring at minimum a `_current` view on each SCD-2 dimension for active-row lookups. Reference explicitly has mart-layer tasks. Worth up to **+5 pts**.
2. **Document dimension load FRs** — even though dimension ETL is externally owned, FR-004/FR-005 should specify the interface contract (dimension must have current SCD-2 rows and a key=0 sentinel before the Purchase fact load executes). Worth up to **+3 pts**.
3. **Add multi-environment NFR** — specify that dev/prod environments are separated via `config/environment.yaml` env keys and that no hardcoded environment-specific values appear in code. References IF-003 credentials pattern. Worth up to **+3 pts**.

---

*Report generated by migvisor-task-checker-requirements on 2026-09-18*
