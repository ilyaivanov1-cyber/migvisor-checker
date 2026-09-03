# SmartBuilder Validation Report — Sales_Orders

**Product:** Sales_Orders
**Project:** GlobalSales_Project
**Validator:** migVisor SmartBuilder Validation Agent
**Validation Date:** 2026-08-28
**Spec baseline:** design.md · requirements.md · tasks.md · catalog.yaml (project/current/catalog.yaml)

---

## Executive Summary

| Metric | Count |
|---|---|
| Total artifacts inventoried | 86 |
| Artifacts read and validated | 86 |
| PASS | 80 |
| FAIL | 6 |
| PASS rate | 93.0 % |

Six artifacts fail spec compliance. Four failures are functionally related: a UDF signature conflict between design.md and tasks.md propagated into the generated DDL (`fact_udf_get_total_quantity_sold.sql`), the test notebook that calls it (`nb_test_udf_qty_sold.py`), and the sample-query file (`bi_sample_queries.sql`). The remaining two failures are independent: `nb_extract_watermark.py` omits the required lineage record creation step, causing `nb_extract_sales.py` to fail at runtime when it reads the `lineage_key` task value that was never published; and `test_sk_resolver.py` does not test `resolve_surrogate_keys()` as required by TASK-TEST-003.

---

## Results Table

### DB — DDL (21 artifacts)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 1 | `src/db/ddl/stg_lineage.sql` | TASK-DB-001 | PASS | All columns match design.md; IDENTITY PK; idempotent CREATE TABLE IF NOT EXISTS; USING DELTA |
| 2 | `src/db/ddl/stg_etl_cutoff.sql` | TASK-DB-002 | PASS | entity_name PK; last_cutoff_utc; updated_at_utc; idempotent |
| 3 | `src/db/ddl/stg_sale_staging.sql` | TASK-DB-003 | PASS | lineage_key BIGINT NOT NULL; all source columns; idempotent; USING DELTA |
| 4 | `src/db/ddl/stg_order_staging.sql` | TASK-DB-004 | PASS | lineage_key BIGINT NOT NULL; all order columns; idempotent |
| 5 | `src/db/ddl/stg_dq_rejections.sql` | TASK-DB-005 | PASS | rejection_id IDENTITY PK; lineage_key; assertion_id; PARTITIONED BY assertion_id; idempotent |
| 6 | `src/db/ddl/dim_customer.sql` | TASK-DB-006 | PASS | SCD2 control cols; PII cols with ALTER COLUMN SET MASK; lineage_key; idempotent |
| 7 | `src/db/ddl/dim_city.sql` | TASK-DB-006 | PASS | SCD2 cols; location_wkt/lat/lon all present; lineage_key; idempotent |
| 8 | `src/db/ddl/dim_stock_item.sql` | TASK-DB-006 | PASS | SCD2 cols; all pricing/descriptive cols; lineage_key; idempotent |
| 9 | `src/db/ddl/dim_employee.sql` | TASK-DB-006 | PASS | employee_key IDENTITY; SCD2 cols; lineage_key; idempotent |
| 10 | `src/db/ddl/dim_payment_method.sql` | TASK-DB-006 | PASS | SCD2 cols; lineage_key; idempotent |
| 11 | `src/db/ddl/dim_transaction_type.sql` | TASK-DB-006 | PASS | SCD2 cols; lineage_key; idempotent |
| 12 | `src/db/ddl/dim_date.sql` | TASK-DB-007 | PASS | SCD0 — no SCD2 cols; date_key INT YYYYMMDD; all calendar cols; idempotent |
| 13 | `src/db/ddl/dim_date_populate.sql` | TASK-DB-007 | PASS | MERGE idempotent; 2013-01-01 start; rolling today+5yr horizon |
| 14 | `src/db/ddl/fact_sale.sql` | TASK-DB-008 | PASS | **Priority file** — all acceptance criteria met; see deep-dive below |
| 15 | `src/db/ddl/fact_order.sql` | TASK-DB-009 | PASS | BIGINT IDENTITY; PARTITIONED BY order_date_key; lineage_key; ZORDER delegated to OPTIMIZE; idempotent |
| 16 | `src/db/ddl/fact_udf_get_total_quantity_sold.sql` | TASK-DB-011 | **FAIL** | UDF signature mismatch vs design.md — see Finding F-01 |
| 17 | `src/db/ddl/mart_v_customer_sales_summary.sql` | TASK-DB-012 | PASS | MATERIALIZED VIEW; profit_margin_with_factor = (profit/NULLIF(...))*100*1.05; no NOLOCK |
| 18 | `src/db/ddl/mart_v_order_details.sql` | TASK-DB-013 | PASS | :start_date param; all dimension joins present |
| 19 | `src/db/ddl/mart_v_order_to_supply_analytics.sql` | TASK-DB-014 | PASS | NOLOCK removed; correct joins |
| 20 | `src/db/ddl/mart_v_order_to_year_analytics.sql` | TASK-DB-015 | PASS | :window_days param; COALESCE(:window_days, 100) default |
| 21 | `src/db/ddl/uc_column_masks.sql` | TASK-SEC-001 | PASS | mask_pii_string function; 4 ALTER TABLE SET MASK on PII cols; CX-P05 TODOs; idempotent |

### DB — Grants (4 artifacts)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 22 | `src/db/grants/dim_customer_grants.sql` | TASK-SEC-002 | PASS | SELECT/MODIFY grants; CX-P05 placeholder roles |
| 23 | `src/db/grants/fact_rls_policies.sql` | TASK-SEC-002 | PASS | CREATE OR REPLACE ROW FILTER; placeholder TRUE predicate; CX-P05 TODOs; idempotent |
| 24 | `src/db/grants/silver_layer_grants.sql` | TASK-SEC-002 | PASS | SELECT for analysts; MODIFY for ETL SP; all 9 silver tables; CX-P05 TODOs |
| 25 | `src/db/grants/mart_grants.sql` | TASK-SEC-002 | PASS | SELECT on all 4 mart views; EXECUTE on UDF; CX-P05 TODOs |

### DB — Queries (1 artifact)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 26 | `src/db/queries/bi_sample_queries.sql` | TASK-MART-004 | **FAIL** | UDF called with 1 argument; deployed DDL requires 3 — see Finding F-02 |

### ETL — Python (31 artifacts)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 27 | `src/etl/ingestion/nb_extract_watermark.py` | TASK-ING-001 | **FAIL** | Does not create stg.lineage record or publish lineage_key task value — see Finding F-03 |
| 28 | `src/etl/ingestion/nb_extract_sales.py` | TASK-ING-002 | **FAIL** | **Priority file** — own implementation correct; fails because lineage_key task value never published upstream — see Finding F-04 |
| 29 | `src/etl/ingestion/nb_extract_orders.py` | TASK-ING-003 | PASS | Mirrors sales pattern; truncate-before-load; lineage_key stamped; secrets via get_secret() |
| 30 | `src/etl/ingestion/nb_extract_dimensions.py` | TASK-ING-004 | PASS | Config-driven DIM_SOURCE_MAP; 6 entities; temp views; zero-change handling |
| 31 | `src/etl/ingestion/nb_commit_watermark.py` | TASK-ING-005 | PASS | Atomic MERGE per entity; logs previous value; idempotent |
| 32 | `src/etl/dimensions/scd2_merge.py` | TASK-TRN-001 | PASS | apply_scd2_merge() two-step pattern; IS DISTINCT FROM; DATE_SUB; LEFT ANTI JOIN; lineage_key |
| 33 | `src/etl/dimensions/nb_load_dim_customer.py` | TASK-TRN-002 | PASS | apply_scd2_merge(); name standardisation transformation; lineage_key |
| 34 | `src/etl/dimensions/nb_load_dim_city.py` | TASK-TRN-003 | PASS | decompose_geography() extracts lat/lon from WKT; apply_scd2_merge() |
| 35 | `src/etl/dimensions/nb_load_dim_stock_item.py` | TASK-TRN-004 | PASS | apply_scd2_merge(); NULL pricing defaults via coalesce; lineage_key |
| 36 | `src/etl/dimensions/nb_load_dim_employee.py` | TASK-TRN-005 | PASS | apply_scd2_merge(); is_salesperson derived; lineage_key |
| 37 | `src/etl/dimensions/nb_load_dim_payment_transaction.py` | TASK-TRN-006 | PASS | Both dim.payment_method and dim.transaction_type loaded; lineage_key |
| 38 | `src/etl/dimensions/nb_populate_dim_date.py` | TASK-TRN-007 | PASS | HISTORY_ANCHOR_DATE start; today+5yr horizon; LEFT ANTI JOIN idempotency |
| 39 | `src/etl/dimensions/nb_orchestrate_dimensions.py` | TASK-TRN-008 | PASS | 6 notebooks in dependency order; halts on first failure; NOTEBOOK_TIMEOUT_SECONDS |
| 40 | `src/etl/facts/sk_resolver.py` | TASK-TRN-009 | PASS | resolve_surrogate_keys(); left join; is_current_row=TRUE filter; unresolved rows logged |
| 41 | `src/etl/facts/fact_merge.py` | TASK-TRN-010 | PASS | apply_fact_merge(); staleness guard tgt.last_edited_when < src.last_edited_when; returns source count |
| 42 | `src/etl/facts/nb_load_fact_sale.py` | TASK-TRN-011 | PASS | Reads stg.sale_staging; SK resolution; apply_fact_merge(); conditional OPTIMIZE; lineage_key |
| 43 | `src/etl/facts/nb_load_fact_order.py` | TASK-TRN-012 | PASS | Mirrors sale pattern; ZORDER post-merge; PICK_TIME_SLA_DAYS from constants |
| 44 | `src/etl/facts/nb_orchestrate_facts.py` | TASK-TRN-013 | PASS | FACT_LOAD_MODE controls parallel/sequential; ThreadPoolExecutor; per-fact error handling |
| 45 | `src/etl/dq/dq_engine.py` | TASK-DQ-001 | PASS | DQEngine class; 5 assertion types; rejection routing to stg.dq_rejections; zero-tolerance default |
| 46 | `src/etl/dq/nb_dq_fact_sale.py` | TASK-DQ-002 | PASS | DQEngine against fact.sale; YAML assertions loaded; assert_row_count_reconciliation(); lineage update |
| 47 | `src/etl/dq/nb_dq_fact_order.py` | TASK-DQ-003 | PASS | Mirrors nb_dq_fact_sale pattern |
| 48 | `src/etl/dq/nb_dq_rejection_report.py` | TASK-DQ-004 | PASS | Groups by assertion_id and source_table; alert on DQ_CRITICAL_TOLERANCE breach |
| 49 | `src/etl/dq/nb_dq_smoke_tests.py` | TASK-DQ-005 | PASS | All silver tables; lineage entry; mart views; UDF=0 NULL-guard check |
| 50 | `src/etl/mart/nb_refresh_v_customer_sales_summary.py` | TASK-MART-001 | PASS | REFRESH MATERIALIZED VIEW; INSERT OVERWRITE fallback; p95 benchmark |
| 51 | `src/etl/mart/nb_validate_mart_views.py` | TASK-MART-002 | PASS | All 4 mart views queried; parameterised view tests |
| 52 | `src/etl/mart/nb_test_udf_qty_sold.py` | TASK-MART-003 | **FAIL** | Calls UDF with 1 argument; deployed DDL defines 3 parameters — see Finding F-05 |
| 53 | `src/etl/mart/nb_optimize_mart.py` | TASK-MART-005 | PASS | OPTIMIZE on fact.sale and fact.order; VACUUM retention from constants; idempotent |
| 54 | `src/etl/security/nb_pii_compliance_check.py` | TASK-SEC-003 | PASS | CON-SEC-001 gate; PII cols checked; masked sentinel assertion; runs independently |
| 55 | `src/common/constants.py` | TASK-ENV-001 | PASS | PROFIT_MARGIN_FACTOR=1.05; all table constants; SECRET_SCOPE; PICK_TIME_SLA_DAYS |
| 56 | `src/common/utils.py` | TASK-ENV-001 | PASS | log_info/warn/error; get_current_utc_ts(); assert_row_count_reconciliation(); docstrings |

### Config (16 artifacts)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 57 | `config/constants.py` | TASK-ENV-001 | PASS | Mirrors src/common/constants.py; PROFIT_MARGIN_FACTOR=1.05 confirmed |
| 58 | `config/utils.py` | TASK-ENV-001 | PASS | All utility functions present with docstrings |
| 59 | `config/secrets_config.py` | TASK-ENV-001 | PASS | get_secret() via dbutils; RuntimeError on missing key; no hard-coded credentials |
| 60 | `config/uc_setup.sql` | TASK-DB-010 | PASS | 4 schemas created IF NOT EXISTS; idempotent; CX-P05 owner TODOs |
| 61 | `config/dq_assertions_fact_sale.yaml` | TASK-DQ-002 | PASS | 5 assertions DQ-SALE-001..005; zero-tolerance; CX-DQ-01 TODO |
| 62 | `config/dq_assertions_fact_order.yaml` | TASK-DQ-003 | PASS | 5 assertions DQ-ORDER-001/002/RI-001/RI-002/003; zero-tolerance; CX-DQ-01 TODO |
| 63 | `config/workflow_nightly_etl_main.yml` | TASK-ORC-001 | PASS | 12 task nodes; cron 0 0 2 * * ? (02:00 UTC); all timeouts; retry policy; email on failure |
| 64 | `config/secrets_setup.md` | TASK-ENV-002 | PASS | Scope=globalsales documented; 4 keys inventoried; CLI commands; CX-P04/CX-P05 callouts |
| 65 | `config/ci_cd_pipeline.yml` | TASK-ENV-004 | PASS | GitHub Actions; flake8 lint; pytest --cov-fail-under=80; Databricks deploy on main merge |
| 66 | `config/pytest.ini` | TASK-ENV-004 | PASS | testpaths=tests; --cov-fail-under=80; coverage source configured |
| 67 | `config/bi_connections.md` | TASK-MART-004 | PASS | SQL Warehouse connection template; all 9 reports documented; NFR-PERF guidance; CX-P05 TODO |
| 68 | `config/deploy_workflow.sh` | TASK-ORC-002 | PASS | set -euo pipefail; idempotent detect-then-update; DATABRICKS_HOST/TOKEN env vars |
| 69 | `config/cluster_config.yml` | TASK-ORC-003 | PASS | DBR 14.3 LTS (>= 13.x); Standard_DS4_v2; autoscale 2-8; liquid clustering flag set |
| 70 | `config/monitoring_config.yml` | TASK-ORC-004 | PASS | Email/webhook alerts; SLA breach at 4h; stg.lineage as metrics source |
| 71 | `config/uc_permission_audit.sql` | TASK-SEC-004 | PASS | Read-only information_schema queries; CX-P05 TODO |
| 72 | `config/secrets_rotation_runbook.md` | TASK-SEC-005 | PASS | All 4 keys covered; step-by-step rotation; CX-P04 pending section; references secrets_config.py |

### Tests — Unit (6 artifacts)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 73 | `tests/unit/test_constants.py` | TASK-TEST-001 | PASS | PROFIT_MARGIN_FACTOR==1.05; all table constants; DQ_CRITICAL_TOLERANCE==0 |
| 74 | `tests/unit/test_utils.py` | TASK-TEST-001 | PASS | 7 test cases; all public utils functions; no live Spark needed |
| 75 | `tests/unit/test_scd2_merge.py` | TASK-TEST-002 | PASS | 4 test cases covering all TASK-TEST-002 acceptance criteria; MagicMock spark |
| 76 | `tests/unit/test_fact_merge.py` | TASK-TEST-003 | PASS | 4 test cases for apply_fact_merge(); staleness guard operator verified in SQL string |
| 77 | `tests/unit/test_sk_resolver.py` | TASK-TEST-003 | **FAIL** | Does not import or test resolve_surrogate_keys() — see Finding F-06 |
| 78 | `tests/unit/test_dq_engine.py` | TASK-TEST-004 | PASS | All 5 assertion types with pass+fail cases; rejection routing verified |

### Tests — Integration (4 artifacts)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 79 | `tests/integration/test_ingestion.py` | TASK-TEST-005 | PASS | pytestmark=integration guard; staging row counts; etl_cutoff update; idempotency; lineage_key non-null |
| 80 | `tests/integration/test_dimension_scd2.py` | TASK-TEST-006 | PASS | SCD2 consistency; expired rows have real expiry date; geo WKT decomposition; lineage_key non-null |
| 81 | `tests/integration/test_e2e_pipeline.py` | TASK-TEST-007 | PASS | Bronze-Silver-Gold fixture; profit_margin_with_factor arithmetic; dq_rejections empty; lineage reconciliation |
| 82 | `tests/integration/test_performance.py` | TASK-TEST-008 | PASS | Pipeline runtime <=4h; mart view p95 <=5s (10 runs, statistics.quantiles) |

### Docs (4 artifacts)

| # | Artifact | Task | Verdict | Finding |
|---|---|---|---|---|
| 83 | `docs/pipeline_runbook.md` | TASK-DOCS-001 | PASS | Manual backfill procedure; per-stage re-run guide; troubleshooting decision tree |
| 84 | `docs/data_dictionary.md` | TASK-DOCS-002 | PASS | Column-level detail for all 19 objects; PII flagged; SCD2 cols documented |
| 85 | `docs/architecture_diagram.md` | TASK-DOCS-003 | PASS | Mermaid flowchart; lineage_key propagation chain; pending decisions annotated |
| 86 | `docs/go_live_checklist.md` | TASK-DOCS-004 | PASS | CX-P04/CX-P05/CX-DQ-01 as hard gates; CON-SEC-001 gate; owner fields; sign-off checkboxes |

---

## Failure Details

### F-01 — UDF signature mismatch: `fact_udf_get_total_quantity_sold.sql`

**Artifact:** `src/db/ddl/fact_udf_get_total_quantity_sold.sql`
**Task:** TASK-DB-011
**Spec rules violated:** design.md §3.4, design.md §4.2

**Root cause — spec conflict between design.md and tasks.md:**

The two authoritative spec files contain contradictory UDF signatures:

- **design.md §3.4 and §4.2** (primary schema spec): `get_total_quantity_sold(p_stock_item_key INT) RETURNS BIGINT` — a single INT parameter.
- **tasks.md TASK-DB-011** (implementation tasks): describes `(p_customer_key BIGINT, p_start_date DATE, p_end_date DATE)` — three parameters with entirely different semantics (customer key, not stock item key).

The generated artifact adopts a third, hybrid interpretation:

```sql
CREATE OR REPLACE FUNCTION globalsales.fact.get_total_quantity_sold(
  p_stock_item_key BIGINT,   -- parameter name from design.md; type promoted to BIGINT
  p_start_date     DATE,     -- extra parameter not in design.md
  p_end_date       DATE      -- extra parameter not in design.md
)
RETURNS BIGINT
```

Validation uses **design.md as the authoritative schema source**. Against that baseline:
1. Parameter type: `BIGINT` generated vs. `INT` specified — type mismatch.
2. Parameter count: 3 generated vs. 1 specified — extra parameters not authorised.
3. The generated body filters on `p_start_date` / `p_end_date` date range, which design.md does not specify.

The generated artifact also matches neither the tasks.md signature (different parameter name: `p_stock_item_key` vs. `p_customer_key`), confirming the spec conflict was not cleanly resolved.

**Impact:** Runtime callers built against design.md will pass one INT argument and receive a SQL argument-count error. The `bi_sample_queries.sql` file calls the UDF with one argument (correct against design.md) but incorrect against the generated DDL — these two artifacts are mutually inconsistent.

**Required remediation:** Resolve the spec conflict: confirm the intended parameter list with the product owner, update the contradictory tasks.md TASK-DB-011 acceptance criteria to align with design.md, then regenerate the DDL.

---

### F-02 — UDF call-site mismatch: `bi_sample_queries.sql`

**Artifact:** `src/db/queries/bi_sample_queries.sql`
**Task:** TASK-MART-004
**Spec rules violated:** Downstream consequence of F-01; call-site inconsistent with deployed DDL

The sample query file calls the UDF with a single argument:

```sql
globalsales.fact.get_total_quantity_sold(si.stock_item_key) AS total_qty_sold
```

This call is consistent with design.md's single-parameter signature but inconsistent with the three-parameter DDL that was actually generated (F-01). In the deployed environment the call would fail with a SQL argument-count error. The file is otherwise structurally correct.

**Required remediation:** After F-01 is resolved and a canonical signature is agreed, update this call site to match. If design.md's single-parameter signature is confirmed, the call site here is correct and only the DDL needs changing.

---

### F-03 — Missing lineage record creation: `nb_extract_watermark.py`

**Artifact:** `src/etl/ingestion/nb_extract_watermark.py`
**Task:** TASK-ING-001
**Spec rules violated:** FR-LIN (requirements.md), design.md §2.3 pipeline bootstrap pseudocode, design.md §5.1 ingestion stage description

`nb_extract_watermark.py` is the first stage of `nightly_etl_main`. Its responsibilities per spec are:

1. Read the watermark cutoff from `stg.etl_cutoff` for each entity.
2. Compute the `extract_start` / `extract_end` window.
3. **Create a new `stg.lineage` record for the current run and publish the resulting `lineage_key` as a task value** — required by FR-LIN and the design.md §5.1 pseudocode.
4. Publish `{entity}_extract_start` and `{entity}_extract_end` task values for downstream stages.

The generated notebook performs steps 1, 2, and 4 correctly but **entirely omits step 3**. It never calls any equivalent of `create_lineage_record()`, never INSERTs into `stg.lineage`, and never publishes `lineage_key` as a task value.

This is a runtime-fatal gap: every downstream notebook — `nb_extract_sales`, `nb_extract_orders`, all dimension load notebooks, all fact load notebooks, all DQ notebooks, and the mart refresh notebooks — reads `lineage_key` from `_WATERMARK_TASK_KEY` task values via `dbutils.jobs.taskValues.get(key="lineage_key")`. With no such task value published, every one of those notebooks will throw a `RuntimeError` and the entire pipeline will fail on its first execution.

The `stg.lineage` record is also the foundation of FR-LIN (full data-lineage traceability): without it, no row in the platform can be traced to its pipeline run, violating the lineage requirement for all rows of every fact and dimension table.

**Required remediation:** Add a lineage record creation block to `nb_extract_watermark.py` immediately after computing the watermark window. The implementation must INSERT a row into `stg.lineage` (status='RUNNING'), retrieve the IDENTITY-generated `lineage_key`, and call `dbutils.jobs.taskValues.set(key="lineage_key", value=str(lineage_key))` before the notebook exits.

---

### F-04 — Runtime dependency on unpublished task value: `nb_extract_sales.py`

**Artifact:** `src/etl/ingestion/nb_extract_sales.py`
**Task:** TASK-ING-002
**Spec rules violated:** FR-LIN (requirements.md); direct consequence of F-03

`nb_extract_sales.py` (the priority regenerated file) correctly implements all of its own logic. The FAIL verdict is issued solely because the `lineage_key` task value it depends on is never published by `nb_extract_watermark.py` (F-03).

```python
# Lines 267-272 — will raise RuntimeError at runtime because
# nb_extract_watermark never publishes "lineage_key"
lineage_key = int(
    dbutils.jobs.taskValues.get(
        taskKey=_WATERMARK_TASK_KEY,
        key="lineage_key",
    )
)
```

All other aspects of the extraction logic are spec-compliant (see priority file deep-dive below).

**Required remediation:** Fix F-03. No change is required to `nb_extract_sales.py` itself.

---

### F-05 — UDF invoked with wrong argument count: `nb_test_udf_qty_sold.py`

**Artifact:** `src/etl/mart/nb_test_udf_qty_sold.py`
**Task:** TASK-MART-003
**Spec rules violated:** Downstream consequence of F-01; call-site inconsistent with deployed DDL

The notebook invokes the UDF with a single `stock_item_key` argument. The deployed DDL declares three parameters. As deployed, this call would fail with a SQL argument-count error at runtime.

**Required remediation:** After F-01 is resolved, align the call site with the agreed canonical signature.

---

### F-06 — Missing coverage of `resolve_surrogate_keys()`: `test_sk_resolver.py`

**Artifact:** `tests/unit/test_sk_resolver.py`
**Task:** TASK-TEST-003
**Spec rules violated:** tasks.md TASK-TEST-003 acceptance criteria

TASK-TEST-003 specifies that `test_sk_resolver.py` must test `resolve_surrogate_keys()` with at least three cases: successful resolution, unresolved natural key (key not found in dimension), and empty source DataFrame.

The generated file does not import from `src.etl.facts.sk_resolver` and does not call `resolve_surrogate_keys()` at any point. Its content tests datetime comparison utilities and a reconciliation helper (`assert_row_count_reconciliation`) — logic that duplicates coverage already present in `test_fact_merge.py` and `test_utils.py`.

The three required test cases are entirely absent:
- Successful SK resolution (join hit producing correct surrogate key) — missing.
- Unresolved natural key (left join miss, default value / NULL handling) — missing.
- Empty source DataFrame (zero-row edge case) — missing.

**Impact:** `resolve_surrogate_keys()` in `src/etl/facts/sk_resolver.py` has no unit-test coverage. The 80% coverage gate in `pytest.ini` / `ci_cd_pipeline.yml` may not be met if `sk_resolver.py` is large enough to move the aggregate below threshold.

**Required remediation:** Replace the content of `test_sk_resolver.py` with tests that import `resolve_surrogate_keys` from `src.etl.facts.sk_resolver` and cover the three required scenarios using a local SparkSession with MagicMock dimension tables.

---

## Priority File Deep-Dive

### `src/db/ddl/fact_sale.sql` (TASK-DB-008) — PASS

All TASK-DB-008 acceptance criteria are satisfied:

| Criterion | Result |
|---|---|
| `CREATE TABLE IF NOT EXISTS globalsales.fact.sale` — idempotent DDL | PASS |
| `USING DELTA` | PASS |
| `sale_key BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL` | PASS |
| `lineage_key BIGINT NOT NULL` (FR-LIN) | PASS |
| `CLUSTER BY (invoice_date_key, customer_key, stock_item_key)` | PASS |
| Column COMMENTs on all columns | PASS |
| `CHECK (quantity > 0)` — DQ-SALE-001 | PASS |
| `CHECK (tax_amount >= 0.0)` — DQ-SALE-002 | PASS |
| `delta.enableChangeDataFeed = false` | PASS |
| 7-year retention (2555 days) on both deletedFileRetentionDuration and logRetentionDuration | PASS |
| `delta.autoOptimize.optimizeWrite = true` + `autoCompact = true` | PASS |
| `delivery_date_key INT` nullable — NULL when ConfirmedDeliveryTime is NULL | PASS |
| All FK dimension columns at correct types and nullability | PASS |

### `src/etl/ingestion/nb_extract_sales.py` (TASK-ING-002) — FAIL (F-04)

The notebook's own implementation is fully spec-compliant. The FAIL verdict is solely due to F-03. All other aspects are correct:

| Criterion | Result |
|---|---|
| Truncate-before-load idempotency | PASS |
| `lineage_key` stamped on every staged row via `lit(lineage_key)` | PASS |
| `compute_derived_cols()` computes `total_including_tax = total_excluding_tax + tax_amount` | PASS |
| `city_key` sourced from `i.CityID` | PASS |
| `total_dry_items` / `total_chiller_items` from `i.TotalDryItems` / `i.TotalChillerItems` | PASS |
| `package` via LEFT JOIN to `Warehouse.PackageTypes` on `UnitPackageTypeID` | PASS |
| `last_edited_when` via CASE-based GREATEST of invoice and line timestamps | PASS |
| All columns cast to DDL-matching types in explicit `select()` | PASS |
| Zero-row extract handled with `log_warn` and early return 0 | PASS |
| JDBC credentials retrieved via `get_secret()`, not hard-coded | PASS |
| `lineage_key` used in UPDATE to `stg.lineage` after load | PASS |
| Reads `lineage_key` from watermark task values | **FAIL** — task value never published (F-03/F-04) |

---

## Pending Decisions — Not Failures

The following open decisions generate intentional placeholders across multiple artifacts. They are **not** failures — the placeholders are correct per spec:

| Decision | ID | Artifacts affected |
|---|---|---|
| OLTP connection strategy (JDBC vs. CDC) | CX-P04 | nb_extract_watermark.py, nb_extract_sales.py, nb_extract_orders.py, secrets_setup.md, secrets_rotation_runbook.md, go_live_checklist.md |
| Unity Catalog access role matrix | CX-P05 | dim_customer_grants.sql, fact_rls_policies.sql, silver_layer_grants.sql, mart_grants.sql, bi_connections.md, monitoring_config.yml, go_live_checklist.md |
| Business DQ thresholds | CX-DQ-01 | dq_assertions_fact_sale.yaml, dq_assertions_fact_order.yaml, pipeline_runbook.md, go_live_checklist.md |

All three are registered as hard go-live gates in `go_live_checklist.md` (items 1–3).

---

## Spec Conflict Register

| Conflict ID | Spec A | Spec B | Generated artifact | Recommendation |
|---|---|---|---|---|
| SC-001 | design.md §3.4/§4.2: `get_total_quantity_sold(p_stock_item_key INT)` — 1 parameter | tasks.md TASK-DB-011: `(p_customer_key BIGINT, p_start_date DATE, p_end_date DATE)` — 3 parameters, different semantics | 3-param BIGINT version — matches neither spec exactly | Resolve with product owner; update tasks.md to align with design.md; regenerate DDL, nb_test_udf_qty_sold.py, and bi_sample_queries.sql |

---

## Remediation Priority

| Priority | Finding | Files to change | Blocks go-live? |
|---|---|---|---|
| P1 — Critical | F-03: nb_extract_watermark.py missing lineage creation | `src/etl/ingestion/nb_extract_watermark.py` | Yes — blocks entire pipeline at first run |
| P1 — Critical | F-04: nb_extract_sales.py runtime failure | No change needed; fix F-03 | Yes — blocked by F-03 |
| P1 — Critical | SC-001: UDF spec conflict | Resolve spec; update tasks.md or design.md | Yes — UDF deployed in production and called by BI |
| P2 — High | F-01: UDF DDL wrong signature | `src/db/ddl/fact_udf_get_total_quantity_sold.sql` | Yes — after SC-001 resolved |
| P2 — High | F-02: bi_sample_queries.sql call-site mismatch | `src/db/queries/bi_sample_queries.sql` | After SC-001 resolved |
| P2 — High | F-05: nb_test_udf_qty_sold.py wrong arg count | `src/etl/mart/nb_test_udf_qty_sold.py` | After SC-001 resolved |
| P3 — Medium | F-06: test_sk_resolver.py missing coverage | `tests/unit/test_sk_resolver.py` | Yes — 80% coverage gate may fail |

---

_End of validation report._
