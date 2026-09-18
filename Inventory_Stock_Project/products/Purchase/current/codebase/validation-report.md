# SmartBuilder Validation Report: Purchase

**Product:** Purchase
**Project:** Inventory_Stock_Project
**Validation Date:** 2026-09-07
**SDD Version:** 4.1
**Validator:** migvisor-validate-agent
**Total Artifacts Validated:** 27

---

## 1. Results Table

| # | Artifact | Task | Status | Findings |
|---|---|---|---|---|
| 1 | `src/db/ddl/bronze_lineage_run.sql` | TASK-001 | **PASS** | Prior finding F-001 (missing PRIMARY KEY) confirmed RESOLVED |
| 2 | `src/db/ddl/bronze_etl_cutoff.sql` | TASK-002 | **PASS** | — |
| 3 | `src/db/ddl/bronze_purchase_staging.sql` | TASK-003 | **PASS** | — |
| 4 | `src/db/ddl/bronze_dq_rejections.sql` | TASK-004 | **PASS** | — |
| 5 | `src/db/ddl/silver_fact_fact_purchase.sql` | TASK-005 | **PASS** | — |
| 6 | `src/db/ddl/silver_dim_supplier_current.sql` | TASK-006 | **PASS** | — |
| 7 | `src/db/ddl/silver_dim_stock_item_current.sql` | TASK-007 | **PASS** | — |
| 8 | `src/db/grants/purchase_grants.sql` | TASK-008 | **PASS** | All 4 silver tables granted to data_analysts — see note on path mismatch (F-001) |
| 9 | `src/common/constants.py` | TASK-009 | **PASS** | — |
| 10 | `src/common/scd2_merge.py` | TASK-010 | **PASS** | — |
| 11 | `src/common/sk_resolver.py` | TASK-011 | **PASS** | — |
| 12 | `src/common/fact_merge.py` | TASK-012 | **PASS** | — |
| 13 | `src/common/udfs.py` | TASK-013 | **PASS** | — |
| 14 | `src/etl/nb_extract_watermark.py` | TASK-014 | **FAIL** | F-002: except block uses raw spark.sql UPDATE instead of close_lineage_record helper |
| 15 | `src/etl/nb_extract_purchase.py` | TASK-015 | **FAIL** | F-003: reads 4 JDBC config keys absent from environment.yaml — KeyError at runtime |
| 16 | `src/etl/migrate_staged_purchase_data.py` | TASK-016 | **PASS** | — |
| 17 | `src/init/reseed_purchase_environment.py` | TASK-017 | **PASS** | — |
| 18 | `config/environment.yaml` | TASK-018 | **FAIL** | F-003: missing jdbc_driver, jdbc_user, jdbc_password, source_table keys |
| 19 | `config/workflows/nightly_etl_purchase.json` | TASK-019 | **FAIL** | F-004: migrate_staged_purchase_data task description contains stale table name `silver_fact.fact_purchase_order` |
| 20 | `tests/common/test_sk_resolver.py` | TASK-020 | **PASS** | — |
| 21 | `tests/common/test_udfs.py` | TASK-021 | **PASS** | — |
| 22 | `tests/etl/test_migrate_staged_purchase_data.py` | TASK-022 | **FAIL** | F-005: QA-P001 test regex `inserted=\d+` won't match actual message `inserted/updated=\d+` |
| 23 | `docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md` | TASK-023 | **PASS** | — |
| 24 | `docs/bi/wwidw_ordered_by_supplier_reconnection.md` | TASK-024 | **PASS** | — |
| 25 | `docs/design.md` | TASK-025 | **FAIL** | F-006, F-007: stale table names throughout; MERGE INTO example uses wrong columns |
| 26 | `docs/data-dictionary.md` | TASK-026 | **PASS** | — |
| 27 | `build-plan.md` | — | **FAIL** | F-008: TASK-008 output listed as `src/db/ddl/grants.sql`; actual file is `src/db/grants/purchase_grants.sql` |

**Summary:** 19 PASS / 8 FAIL — 7 unique findings (F-001 through F-008; F-001 is a prior run finding now confirmed RESOLVED as F-001-RESOLVED)

---

## 2. Prior-Run Finding Status

### F-001 (Prior Run) — CONFIRMED RESOLVED

| Field | Value |
|---|---|
| **Original finding** | `bronze_lineage_run.sql` missing `CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)` |
| **Status** | RESOLVED — PASS |
| **Verification** | Line 23 of `src/db/ddl/bronze_lineage_run.sql` contains `CONSTRAINT pk_lineage_run PRIMARY KEY (lineage_key)`. The constraint is present and matches the design intent from Design §1.2 (lineage_key described as "PK. Identity surrogate for each ETL run"). |

---

## 3. Detailed Findings

---

### F-001 — `src/db/grants/purchase_grants.sql` vs `build-plan.md` path mismatch

**Artifact(s):** `src/db/grants/purchase_grants.sql` (TASK-008), `build-plan.md`
**Severity:** LOW
**Rule:** CX-P004 (standard Purchase codebase layout), NFR-011

**Finding:**
The grants file was generated at `src/db/grants/purchase_grants.sql`. The build-plan.md codebase layout tree (line 63) lists the TASK-008 output as `src/db/ddl/grants.sql` (wrong directory, wrong filename). The `_manifest.yaml` `generated` list correctly records `products/Purchase/current/codebase/src/db/grants/purchase_grants.sql`, confirming the actual file path is correct.

The grants file itself contains all required GRANT statements:
- `GRANT SELECT ON TABLE silver_fact.fact_purchase TO data_analysts` — present
- `GRANT SELECT ON TABLE silver_dim.supplier TO data_analysts` — present
- `GRANT SELECT ON TABLE silver_dim.stock_item TO data_analysts` — present
- `GRANT SELECT ON TABLE silver_dim.date TO data_analysts` — present

All 4 silver tables required by TASK-008 for the `data_analysts` group are covered. The grants file content is PASS; only the build-plan path reference is stale.

**Root Cause:** The build-plan.md was generated before the TASK-008 file path was finalised. The SmartBuilder generator placed the file correctly under `src/db/grants/` (per CX-P004 codebase layout rule) but did not update the build-plan tree.

**Impact:** Documentation inconsistency. The Phase 1 acceptance gate in build-plan.md checks for `src/db/ddl/grants.sql` which does not exist at that path — the gate will report a false failure if run as written.

**Resolution:** Update build-plan.md line 63 from `src/db/ddl/grants.sql` to `src/db/grants/purchase_grants.sql`. Also update the Phase 1 acceptance gate description to reference the correct path. No code change required.

---

### F-002 — `nb_extract_watermark.py` except block uses raw SQL instead of close_lineage_record helper

**Artifact:** `src/etl/nb_extract_watermark.py` (TASK-014)
**Severity:** MEDIUM
**Rule:** NFR-009, CX-P005

**Finding:**
The build-plan.md and CX-P005 skeleton requirement specifies that notebooks which open a lineage record must call a `close_lineage_record` helper in both the success path and the except block. The except block of `nb_extract_watermark.py` (lines 69–75) uses a raw `spark.sql(UPDATE ...)` statement:

```python
except Exception as e:
    spark.sql(f"""
        UPDATE {LINEAGE_RUN_TABLE}
        SET was_successful = false, data_load_completed = current_timestamp()
        WHERE lineage_key = {lineage_key}
    """)
    raise
```

The `migrate_staged_purchase_data.py` notebook (TASK-016) implements the same closure via a direct `spark.sql` UPDATE, establishing a consistent pattern across the codebase. However, the build-plan.md Phase 2 constraint table explicitly states: "`close_lineage_record` in success AND except block" as a required constraint. The watermark notebook satisfies the functional intent (the lineage record is closed on failure) but deviates from the named helper pattern.

**Root Cause:** The `close_lineage_record` helper is not defined in any `src/common/` module. The spec referenced it as a pattern, but it was not materialised as a shared utility. Both `nb_extract_watermark.py` and `migrate_staged_purchase_data.py` implement the closure inline via `spark.sql`. This is a spec documentation gap: the named helper was specified but not generated as a TASK.

**Impact:** The functional behavior is correct — the lineage record is closed on exception. The deviation is a maintainability concern: future changes to the close pattern must be made in multiple places. No runtime failure results from this pattern.

**Resolution:** Either (a) accept the inline `spark.sql` UPDATE pattern as the implementation of the lineage-close step and update the build-plan constraint table to reflect this, or (b) add a `close_lineage_record` function to `src/common/constants.py` or a new `src/common/lineage_helpers.py` module and update both notebooks to call it. Option (a) is lower effort and has no functional impact.

---

### F-003 — `nb_extract_purchase.py` reads JDBC config keys absent from `environment.yaml`

**Artifact(s):** `src/etl/nb_extract_purchase.py` (TASK-015), `config/environment.yaml` (TASK-018)
**Severity:** HIGH (CRITICAL — runtime breakage)
**Rule:** FR-009, CX-P001, NFR-009

**Finding:**
`nb_extract_purchase.py` reads four JDBC connection keys from `cfg["purchase"]["etl"]` at lines 23–26:

```python
JDBC_DRIVER   = cfg["purchase"]["etl"]["jdbc_driver"]
JDBC_USER     = cfg["purchase"]["etl"]["jdbc_user"]
JDBC_PASSWORD = cfg["purchase"]["etl"]["jdbc_password"]
SOURCE_TABLE  = cfg["purchase"]["etl"]["source_table"]
```

The `config/environment.yaml` `purchase.etl` section contains only three keys:
- `initial_load_date`
- `batch_lookback_days`
- `fact_optimize_row_threshold`

The four keys referenced by `nb_extract_purchase.py` (`jdbc_driver`, `jdbc_user`, `jdbc_password`, `source_table`) are entirely absent from `environment.yaml`. Executing `nb_extract_purchase.py` will raise a `KeyError` at line 23, before any ETL logic is reached.

The `nb_extract_purchase.py` header comment notes "JDBC source connection — placeholder pending PD-001 platform decision", indicating the generator was aware the JDBC connection is a pending decision. The correct approach is to include placeholder keys (with `{{PLACEHOLDER}}` values) in `environment.yaml` so the config file is structurally complete and the notebook can load without error even before PD-001 resolves.

**Root Cause:** `environment.yaml` (TASK-018) was generated without the JDBC section because PD-001 (source JDBC connectivity) was pending. The notebook (TASK-015) was generated with config key references to a section that does not exist. Neither artifact was updated to align with the other.

**Impact:** The `nightly_etl_purchase` Databricks workflow Task 2 (`nb_extract_purchase`) will fail with `KeyError: 'jdbc_driver'` immediately on startup. The entire pipeline is blocked from running end-to-end.

**Resolution:** Add the following placeholder keys to `config/environment.yaml` under `purchase.etl`:

```yaml
    # JDBC source connection — set when PD-001 resolves (pending)
    jdbc_driver:   "{{JDBC_DRIVER_CLASS}}"
    jdbc_user:     "{{JDBC_USER}}"
    jdbc_password: "{{JDBC_PASSWORD}}"
    source_table:  "{{SOURCE_TABLE_FQTN}}"
```

This unblocks the config load. The notebook will still fail at the JDBC `.load()` call (line 39) until PD-001 resolves, but the failure will be the expected JDBC connectivity error, not a Python KeyError.

---

### F-004 — `nightly_etl_purchase.json` task description contains stale fact table name

**Artifact:** `config/workflows/nightly_etl_purchase.json` (TASK-019)
**Severity:** LOW
**Rule:** NM-001

**Finding:**
The `migrate_staged_purchase_data` task description in `nightly_etl_purchase.json` (line 65) reads:

```
"Applies SK resolution, QA assertion chain (QA-P001 through QA-P005), and MERGE INTO to promote staged rows from bronze to silver_fact.fact_purchase_order. ..."
```

The correct target table name is `silver_fact.fact_purchase` (as defined in Design §1.2, TASK-005, and all ETL code). `fact_purchase_order` is the stale legacy name from the original SQL Server source schema.

All other aspects of `nightly_etl_purchase.json` are correct:
- Quartz cron `0 0 2 * * ?` (UTC 02:00) — correct
- DBR 13.3 LTS (`spark_version: "13.3.x-scala2.12"`) — correct
- Three tasks in correct dependency order (`nb_extract_watermark` → `nb_extract_purchase` → `migrate_staged_purchase_data`) — correct
- `max_retries`: 2 / 2 / 0 (watermark / extract / migrate) — correct
- `timeout_seconds`: 1800 / 3600 / 7200 — correct

**Root Cause:** The task description string was carried forward from an earlier draft or template that used the legacy table name. The functional workflow configuration is unaffected; this is a documentation-only error in a JSON string field.

**Impact:** Cosmetic. The workflow description shown in the Databricks Jobs UI will reference a non-existent table name, which may cause confusion during operational monitoring or incident response.

**Resolution:** Update line 65 of `nightly_etl_purchase.json`: replace `silver_fact.fact_purchase_order` with `silver_fact.fact_purchase` in the `migrate_staged_purchase_data` task description string.

---

### F-005 — `test_migrate_staged_purchase_data.py` QA-P001 regex won't match actual error message

**Artifact:** `tests/etl/test_migrate_staged_purchase_data.py` (TASK-022)
**Severity:** MEDIUM
**Rule:** NFR-003, DQR-001

**Finding:**
Test `test_qa_p001_fail_raises_runtime_error` at line 395 asserts:

```python
assert re.search(r"Row count mismatch: staging=\d+, inserted=\d+", error_message)
```

The `run_qa_p001` helper defined in the same file (lines 186–191) raises:

```python
raise RuntimeError(
    f"Row count mismatch: staging={staging_count}, inserted={rows_merged}"
)
```

At first inspection the regex `inserted=\d+` appears to match `inserted={rows_merged}`. However, the actual `migrate_staged_purchase_data.py` notebook (TASK-016) raises the QA-P001 error with the message pattern:

```python
raise RuntimeError(
    f"QA-P001 FAILED — Row count mismatch: staging={staging_count}, inserted/updated={rows_merged}"
)
```

The test helper `run_qa_p001` (line 189) uses the shorter form `inserted={rows_merged}` which matches the local helper's own message. This means `test_qa_p001_fail_raises_runtime_error` tests the local helper, not the actual notebook logic.

Two independent issues result:
1. **The regex will pass against the helper** — the test itself does not fail, but it provides false confidence that the notebook's error message is validated.
2. **If the test were refactored to test the notebook's actual raise**, the regex `inserted=\d+` would fail to match `inserted/updated=\d+` because the pattern `inserted=` does not match `inserted/updated=`.

The real notebook's error message contains `inserted/updated=` (with a forward slash), which the current regex pattern does not account for.

**Root Cause:** The test helper `run_qa_p001` was written with a simplified error message that does not match the notebook's actual message. The regex was written to match the helper, not the notebook.

**Impact:** The test passes but does not validate the notebook's actual QA-P001 behavior. If the notebook's error message format is ever changed, this test will not catch the regression. The Phase 3 acceptance gate ("TASK-022 covers the RuntimeError injection path") is technically met by the test passing, but the test is not validating the correct artifact.

**Resolution:** Update the `run_qa_p001` helper (line 189) to use the full message format matching the notebook:

```python
raise RuntimeError(
    f"QA-P001 FAILED — Row count mismatch: staging={staging_count}, inserted/updated={rows_merged}"
)
```

And update the regex on line 395 to:

```python
assert re.search(
    r"QA-P001 FAILED.*Row count mismatch: staging=\d+, inserted/updated=\d+",
    error_message
)
```

---

### F-006 — `docs/design.md` uses stale Bronze table names throughout

**Artifact:** `docs/design.md` (TASK-025)
**Severity:** MEDIUM
**Rule:** NM-001, CX-P004

**Finding:**
The codebase `docs/design.md` (generated by TASK-025) was generated from a stale template and uses table names that do not match the canonical names defined in the SDD spec design.md, DDL files, and all ETL code.

**Stale names used in `docs/design.md` vs. correct names:**

| `docs/design.md` stale name | Correct name (from spec + DDL) |
|---|---|
| `stg_purchase_order` | `purchase_staging` |
| `etl_watermark_control` | `etl_cutoff` |
| `etl_lineage_run` | `lineage_run` |
| `etl_dq_rejection_store` | `dq_rejections` |
| `dim_supplier` | `supplier` |
| `dim_date` | (no table — `silver_dim.date` is an external dependency, not a Purchase product table) |
| `dim_package` | (does not exist — no package dimension in the Purchase product) |
| `fact_purchase_order` | `fact_purchase` |

The architecture diagram in §1 of `docs/design.md` shows `stg_purchase_order`, `etl_watermark_control`, `etl_lineage_run`, `etl_dq_rejection_store`, `dim_supplier`, `dim_date`, `dim_package`, `fact_purchase_order`. None of these match the actual table names in the generated DDL files or any ETL code.

**Root Cause:** `docs/design.md` was generated from a template that described a different version of the Purchase product design (possibly the as-is SQL Server schema or an intermediate draft). The SmartBuilder generator did not substitute the correct target-side table names from the finalized DDL artifacts.

**Impact:** The design document is incorrect and misleading. Any reader using `docs/design.md` to understand the deployed data model will encounter wrong table names throughout, including in the architecture diagram, layer responsibility table, SK resolution example, MERGE INTO example, QA chain diagram, and lineage propagation section.

**Resolution:** Regenerate `docs/design.md` using the correct table names from the finalized DDL artifacts. The spec `specifications/development_plan/design.md` and the generated DDL files provide the authoritative naming reference. The regenerated document should match the architecture in the spec design.md rather than the stale draft.

---

### F-007 — `docs/design.md` MERGE INTO example uses wrong columns

**Artifact:** `docs/design.md` §4 (TASK-025)
**Severity:** MEDIUM
**Rule:** FR-007, NM-001

**Finding:**
The MERGE INTO example in `docs/design.md` §4 targets `silver_fact.fact_purchase_order` (stale name) and references columns that do not exist in the actual `silver_fact.fact_purchase` table:

**Columns in MERGE INTO example that do NOT exist in `silver_fact.fact_purchase`:**
- `supplier_sk` (should be `supplier_key`)
- `package_sk` (does not exist — no package dimension)
- `total_dry_items` (does not exist in fact_purchase)
- `total_chiller_items` (does not exist in fact_purchase)
- `delivery_method_id` (does not exist in fact_purchase)
- `contact_person_id` (does not exist in fact_purchase)
- `last_modified_when` (does not exist in fact_purchase)
- `_updated_at` (does not exist in fact_purchase)
- `_inserted_at` (does not exist in fact_purchase)

**Columns in `silver_fact.fact_purchase` that are absent from the MERGE INTO example:**
- `stock_item_key`
- `ordered_outers`
- `ordered_quantity`
- `received_outers`
- `package`
- `is_order_finalized`

The MERGE INTO example is entirely inconsistent with the actual `fact_purchase` table schema defined in `src/db/ddl/silver_fact_fact_purchase.sql` and `src/common/fact_merge.py`.

**Root Cause:** Same as F-006 — `docs/design.md` was generated from a stale template that described a different (legacy or intermediate) version of the fact table schema. The MERGE INTO example was not updated to reflect the finalised `silver_fact.fact_purchase` 11-column schema.

**Impact:** The MERGE INTO documentation is completely wrong. If an engineer uses this document as a reference for writing queries against `silver_fact.fact_purchase`, every column reference will fail.

**Resolution:** Addressed by the same regeneration action as F-006. The regenerated `docs/design.md` §4 MERGE INTO example must use the actual `silver_fact.fact_purchase` column set: `date_key`, `supplier_key`, `stock_item_key`, `wwi_purchase_order_id`, `ordered_outers`, `ordered_quantity`, `received_outers`, `package`, `is_order_finalized`, `lineage_key`.

---

### F-008 — `build-plan.md` TASK-008 output path is wrong

**Artifact:** `build-plan.md`
**Severity:** LOW
**Rule:** CX-P004

**Finding:**
The build-plan.md codebase layout tree (line 63) lists:

```
│       └── grants.sql                         # TASK-008
```

The actual generated file is `src/db/grants/purchase_grants.sql` (confirmed in `_manifest.yaml` and on disk). Two errors are present:
1. The file is under `src/db/ddl/` in the tree but the actual path is `src/db/grants/`.
2. The filename is `grants.sql` in the tree but the actual filename is `purchase_grants.sql`.

The Phase 1 acceptance gate (build-plan.md line 108) reads:
> "All 8 DDL files exist under `src/db/ddl/`"

This gate will report false failures because the grants file does not exist under `src/db/ddl/`.

**Root Cause:** The build-plan codebase layout was finalized before the TASK-008 file path was determined. The CX-P004 rule places grant files under `src/db/grants/` (separate from DDL), but the build-plan was not updated after this placement decision was made.

**Impact:** The Phase 1 acceptance gate is unreliable as written. Documentation inconsistency.

**Resolution:** Update build-plan.md:
1. Move `grants.sql` entry out of the `src/db/ddl/` subtree and into a new `src/db/grants/` subtree.
2. Rename to `purchase_grants.sql`.
3. Update the Phase 1 acceptance gate to check `src/db/grants/purchase_grants.sql` as a separate check from the 7 DDL files under `src/db/ddl/`.

---

## 4. Summary

### Severity Breakdown

| Severity | Count | Findings |
|---|---|---|
| CRITICAL / HIGH | 1 | F-003 (nb_extract_purchase.py KeyError — pipeline blocked) |
| MEDIUM | 3 | F-002 (lineage helper pattern), F-005 (test regex mismatch), F-006+F-007 (docs/design.md stale content) |
| LOW | 2 | F-001 (build-plan/grants path mismatch), F-004 (workflow JSON stale description), F-008 (build-plan TASK-008 path) |

### Artifact Status Summary

| Category | Artifacts | Passed | Failed |
|---|---|---|---|
| DDL (Bronze + Silver) | 7 | 7 | 0 |
| Grants | 1 | 1 | 0 |
| ETL Python (common) | 5 | 5 | 0 |
| ETL Python (notebooks) | 3 | 1 | 2 (F-002, F-003) |
| Init notebook | 1 | 1 | 0 |
| Config | 2 | 0 | 2 (F-003, F-004) |
| Tests | 3 | 2 | 1 (F-005) |
| BI docs | 2 | 2 | 0 |
| Design/data-dict docs | 2 | 1 | 1 (F-006, F-007) |
| Build plan | 1 | 0 | 1 (F-001, F-008) |
| **Total** | **27** | **19** | **8** |

### Prioritised Remediation Order

1. **F-003 (CRITICAL)** — Add JDBC placeholder keys to `config/environment.yaml`. Blocks the entire pipeline from running.
2. **F-006 + F-007 (MEDIUM)** — Regenerate `docs/design.md` from correct table names. The design document is entirely wrong and risks operational confusion.
3. **F-005 (MEDIUM)** — Fix `run_qa_p001` error message and test regex in `test_migrate_staged_purchase_data.py`. The test provides false assurance.
4. **F-002 (MEDIUM)** — Align lineage-close pattern: either accept inline spark.sql UPDATE or add a shared helper. No functional impact currently.
5. **F-004 (LOW)** — Fix stale table name in `nightly_etl_purchase.json` description string. No functional impact.
6. **F-001 + F-008 (LOW)** — Update `build-plan.md` grants path. Documentation only.

### Prior Run Finding

| Finding | Status |
|---|---|
| F-001 (prior run) — missing PRIMARY KEY in bronze_lineage_run.sql | **RESOLVED — PASS** |

---

_Validation report generated by `migvisor-validate-agent` | SmartBuilder version 4.1 | 2026-09-07_
