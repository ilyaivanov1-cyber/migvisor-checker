# Check Report: TASK-REQ-001
**Skill:** requirements | **Trainee:** Inventory_Stock_Project | **Product:** Purchase
**Checker version:** v1 | **Generated:** 2026-09-25

---

## Score: 88 / 100 — Good

---

## Rubric Evaluation

### Content Completeness — 24 / 25

Total requirements: 33 (12 FR + 12 NFR + 9 DQR) — exceeds the 25-requirement threshold and the 32-requirement reference count.

**FR (12 requirements, FR-001 through FR-012):**
All core functional areas covered: incremental extract from staging (FR-001), watermark-bounded extraction (FR-002), lineage key propagation via taskValues (FR-003), SCD-2 SK resolution for supplier (FR-004) and stock_item (FR-005), date key derivation (FR-006), fact MERGE INTO (FR-007), conditional OPTIMIZE (FR-008), configuration externalisation (FR-009), SQL Warehouse data delivery (FR-010), environment initialisation notebook (FR-011), mart layer population (FR-012).

FR-012 (Mart layer) adds a requirement not explicitly in the reference's 11 FRs — this is a valuable addition given the design includes mart views.

**NFR (12 requirements, NFR-001 through NFR-012):**
All major non-functional categories covered: data freshness (NFR-001), availability (NFR-002), row count reconciliation blocking (NFR-003), RI validation non-blocking (NFR-004), orphaned SK detection (NFR-005), business rule assertions (NFR-006), DQ rejection store (NFR-007), Unity Catalog access control (NFR-008), ETL notebook skeleton (NFR-009), DDL header block (NFR-010), codebase layout (NFR-011), data retention (NFR-012).

**DQR (9 requirements, DQR-001 through DQR-009):**
All DQ dimensions covered: row count zero-tolerance (DQR-001), RI completeness for all 3 FK columns (DQR-002/003/004), quantity non-negativity (DQR-005), date window (DQR-006), package non-null (DQR-007), rejection traceability (DQR-008), surrogate key default coverage (DQR-009).

**Bonus:** DQR-to-AC traceability table (§4) maps each DQR to the FR/NFR acceptance criterion it validates. This is not in the reference but adds significant QA value.

Minor gap (-1 pt): FR-007 uses a single-column MERGE key (`wwi_purchase_order_id`) in the acceptance criterion, which is inconsistent with to-be §4.4 step 15 (4-column composite key). See cross-file check below.

### Structure — 10 / 10

Three-section structure (FR / NFR / DQR) clearly delineated with markdown heading levels. Summary count line present at end of §3. Traceability table (§4) well organised. Column headers consistent across all three requirement tables: ID, Title, Description, Priority, Acceptance Criterion, Source.

### Acceptance Criteria Quality — 23 / 25

Acceptance criteria are specific and measurable throughout:
- FR-001: "contains only rows with `_extracted_at_utc` equal to the current run's extraction timestamp; no rows from a prior run are present" ✓
- FR-003: "Every row written to `silver_fact.fact_purchase`, `bronze.purchase_staging`, and `bronze.dq_rejections` in a given run carries the same `lineage_key` value" ✓
- FR-004/005: Three-part AC: (a) matching rows get non-zero SK, (b) non-matching rows get key=0, (c) no row has null SK ✓
- NFR-003: "injecting a mismatch... causes the Workflow task to FAIL with `RuntimeError: Row count mismatch: staging=N, inserted=M`" ✓
- NFR-004: "a rejection row is present in `bronze.dq_rejections` with `fk_column = 'supplier_key'`" — **KNOWN ERROR**: column is `violation_column` not `fk_column` (see cross-file check below)

Minor deductions (-2 pts):
- NFR-004 AC uses `fk_column` instead of `violation_column` — the dq_rejections schema (as documented in to-be §3.1 ER diagram and NFR-007 itself) has `violation_column`, not `fk_column`. The NFR-004 acceptance criterion references a non-existent column name.
- NFR-007 correctly lists 10 required columns in the description, avoiding the "says 9 but lists 10" error present in the reference. ✓

### Source References — 14 / 15

All 33 requirements have a populated Source column referencing the product-definition.yaml section that drove the requirement (x-inputPorts, SLA, Details, dataAccess, dataQuality). Cross-references between FR and NFR are present (e.g., FR-008 references CX-P001, NFR-009 references CX-P005). DQR source column references the corresponding QA rule ID (QA-P001 through QA-P005).

Minor gap (-1 pt): Some source references are too coarse (e.g., NFR-001 Source: "SLA / updateFrequency + latency" without specifying the section ID or rule reference). A few NFR requirements would benefit from explicit rule ID citations alongside the product-definition section reference.

### Violation Handling — 14 / 15

Blocking vs non-blocking behaviour is correctly and consistently specified:
- Blocking: NFR-003 (row count mismatch → RuntimeError + FAILED status), NFR-004 implicit in DQR-001, FR-003 (lineage integrity)
- Non-blocking / Warning: NFR-004 (RI violations → dq_rejections, pipeline continues), NFR-005 (orphaned SKs → WARNING log, no FAIL), NFR-006 (business rule violations → WARNING log, no FAIL)
- DQR-001 through DQR-004 (`must-have`) vs DQR-005 through DQR-007 (`should-have`) priority split ✓

Minor gap (-1 pt): NFR-004 acceptance criterion says "the Workflow task status is SUCCEEDED" which is correct. However, the description says "referential integrity... violations must be written to `bronze.dq_rejections`" without specifying the `rule_id = 'QA-P003'` that should be stamped on each rejection row — the AC includes it (`rule_id = 'QA-P003'`) but the description omits it, creating a description-to-AC asymmetry.

### Summary Table — 10 / 10

DQR-to-AC traceability table (§4) is comprehensive and correctly maps all 9 DQRs to the FR/NFR acceptance criteria they validate, with clear descriptions of the validation relationship. This bonus section exceeds requirements.

---

## Auto-Deduct Checks

| Check | Threshold | Result |
|---|---|---|
| Total requirements ≥ 25 | −8 pts if < 25 | PASS — 33 requirements |
| Priority split present (must-have / should-have) | −4 pts if absent | PASS — priorities specified for all 33 |
| FR / NFR / DQR all present | −5 pts if any missing | PASS — all 3 types present |

**Total auto-deductions: 0 pts**

---

## Cross-File Consistency Checks (MANDATORY)

### MERGE Key Consistency (read to-be.md §4.4 step 15)

**to-be MERGE key:** 4-column composite key:
`wwi_purchase_order_id AND date_key AND supplier_key AND stock_item_key`

**FR-007 MERGE key:** "keyed on `wwi_purchase_order_id`" (single column)

**Result: INCONSISTENCY FLAGGED.** FR-007's acceptance criterion states the MERGE is "keyed on `wwi_purchase_order_id`" but to-be §4.4 step 15 defines a 4-column composite MERGE key. This is the same known defect present in the design document and the reference requirements. The acceptance criterion in FR-007 must be updated to the 4-column composite key to correctly reflect idempotency semantics: "Running the MERGE twice with the same staging input (same `wwi_purchase_order_id`, `date_key`, `supplier_key`, `stock_item_key` combinations) produces the same `silver_fact.fact_purchase` row count."

**Deduction: −2 pts** (cross-file MERGE key inconsistency between requirements FR-007 and to-be §4.4).

### DDL Column Name Consistency (data-dictionary.md — verification pending Batch B)

**NFR-004 column name error:** The NFR-004 acceptance criterion uses `fk_column = 'supplier_key'` but the `bronze.dq_rejections` schema (documented in to-be §3.1 ER diagram and NFR-007 requirements) has the column named `violation_column`, not `fk_column`. This is a column name inconsistency within the requirements document.

The correct AC should read: `violation_column = 'supplier_key'`, `rule_id = 'QA-P003'`.

**Deduction: included in acceptance criteria quality score (−1 pt).**

---

## Summary

The requirements document is well-structured with 33 requirements covering FR, NFR, and DQR categories — all above the minimum thresholds. The acceptance criteria are specific and measurable throughout, with correct blocking vs non-blocking classification. The DQR-to-AC traceability table is a valuable bonus. Two known errors identified: (1) FR-007 uses a single-column MERGE key (`wwi_purchase_order_id`) inconsistent with the 4-column composite MERGE key in to-be §4.4 step 15 — this is a cross-file consistency defect that must be corrected; (2) NFR-004 acceptance criterion uses `fk_column` where the actual `dq_rejections` column is named `violation_column`. Both errors are present in the reference requirements as well and represent known defects to document and correct.

---

## Priority Actions

1. **Correct FR-007 MERGE key:** Update the FR-007 description and acceptance criterion to the 4-column composite MERGE key: "keyed on `(wwi_purchase_order_id, date_key, supplier_key, stock_item_key)`" — matching to-be §4.4 step 15 and the actual fact table grain. Update the idempotency acceptance criterion accordingly.
2. **Correct NFR-004 column name:** Replace `fk_column = 'supplier_key'` with `violation_column = 'supplier_key'` in the NFR-004 acceptance criterion. The `bronze.dq_rejections` schema has `violation_column` (as defined in to-be §3.1 and NFR-007 column list) — `fk_column` does not exist in the schema.
3. **Strengthen source references for NFR requirements:** Add explicit rule ID citations (e.g., NFR-001 → LN-005 / LN-P001, NFR-009 → CX-P005) alongside the product-definition section references to provide full traceability from requirement to transformation rule.
4. **Align NFR-004 description with AC:** Add `rule_id = 'QA-P003'` to the NFR-004 description text so that the description and acceptance criterion are consistent — both should specify that the `rule_id` column on the rejection row identifies the quality rule that triggered the write.
