# Sales_Orders — Requirements
_Generated: 2026-06-05 | Pipeline stage: requirements_

---

## 1. Functional Requirements

### 1.1 Data Ingestion

**FR-ING-001** — The pipeline must ingest incremental sales transaction data nightly from the upstream source system into `globalsales.stg.sale_staging`, capturing only records added or modified since the last successful ETL cutoff recorded in `globalsales.stg.etl_cutoff`.

**FR-ING-002** — The pipeline must ingest incremental order data nightly from the upstream source system into `globalsales.stg.order_staging`, capturing only records added or modified since the last successful ETL cutoff recorded in `globalsales.stg.etl_cutoff`.

**FR-ING-003** — Every row written to `globalsales.stg.sale_staging` must carry a non-null `lineage_key` that references a corresponding entry in `globalsales.stg.lineage`, ensuring full traceability from raw ingestion to the fact layer.

**FR-ING-004** — Every row written to `globalsales.stg.order_staging` must carry a non-null `lineage_key` that references a corresponding entry in `globalsales.stg.lineage`.

**FR-ING-005** — The pipeline must record a new entry in `globalsales.stg.lineage` at the start of each ETL run, capturing the run identifier, source system reference, batch window start, batch window end, and pipeline version.

**FR-ING-006** — The pipeline must update `globalsales.stg.etl_cutoff` to the high-watermark timestamp of the successfully processed batch only after the full batch has passed all DQ assertions, ensuring idempotent re-runs on failure. `[PENDING: CX-P04 — confirm direct OLTP extraction strategy vs. CDC / intermediate landing zone]`

**FR-ING-007** — Historical data load must cover all records from 2013-01-01 onward. The initial full load must be idempotent so it can be safely re-executed.

### 1.2 Data Transformation

**FR-TRN-001** — The pipeline must merge staged sale records from `globalsales.stg.sale_staging` into `globalsales.fact.sale`, using BIGINT IDENTITY as the surrogate primary key and liquid clustering on `(invoice_date_key, customer_key, stock_item_key)`.

**FR-TRN-002** — The pipeline must merge staged order records from `globalsales.stg.order_staging` into `globalsales.fact.order`, using BIGINT IDENTITY as the surrogate primary key and partition key `order_date_key` with ZORDER on `(customer_key, stock_item_key)`.

**FR-TRN-003** — The pipeline must compute and persist the following calculated fields on `globalsales.fact.sale` during the merge:
- `total_excluding_tax`
- `tax_amount`
- `total_including_tax`
- `profit`
- `total_dry_items`
- `total_chiller_items`

**FR-TRN-004** — The pipeline must compute and persist the following calculated fields on `globalsales.fact.order` during the merge:
- `backorder_count`
- `pick_time_sla_met` (Boolean or equivalent flag indicating whether pick time met the SLA threshold)

**FR-TRN-005** — Dimension tables (`globalsales.dim.customer`, `globalsales.dim.city`, `globalsales.dim.stock_item`, `globalsales.dim.employee`, `globalsales.dim.payment_method`, `globalsales.dim.transaction_type`) must implement SCD Type 2 logic: new versions are inserted with an updated effective date range; superseded versions are closed by setting their end-effective date.

**FR-TRN-006** — `globalsales.dim.date` must be treated as a static (SCD Type 0) dimension; no updates or inserts outside of an explicit calendar extension process are permitted.

**FR-TRN-007** — `globalsales.dim.city` must decompose the legacy geography column into three target columns: `location_wkt` (Well-Known Text geometry), `location_lat` (DOUBLE), and `location_lon` (DOUBLE). No legacy compound geography type may be stored in the target.

**FR-TRN-008** — PII attributes in `globalsales.dim.customer` (e.g., customer name, contact details) must be masked at write time in accordance with the Unity Catalog Column-Level Security (CLS) masking policy; raw PII must never be persisted in plain text in the Delta table.

**FR-TRN-009** — The SQL UDF `globalsales.fact.get_total_quantity_sold` must consolidate the logic of the two legacy UDFs into a single Databricks SQL UDF, applying a `COALESCE` NULL guard so that NULL inputs return 0 rather than NULL.

**FR-TRN-010** — The gold mart view `globalsales.mart.v_customer_sales_summary` must be implemented as a materialized view and must compute `profit_margin_with_factor` as:
```
(profit / total_including_tax) * 100 * 1.05
```
where the constant `1.05` is the `PROFIT_MARGIN_FACTOR` configuration value and must be parameterised (not hard-coded) to allow future adjustment without code changes.

**FR-TRN-011** — The gold mart view `globalsales.mart.v_order_details` must expose a `:start_date` query parameter to allow consumers to filter results by order date without full-scan behaviour.

**FR-TRN-012** — The gold mart view `globalsales.mart.v_order_to_supply_analytics` must be implemented without any NOLOCK hints or equivalent non-transactional read patterns; Databricks Delta Lake snapshot isolation provides the required consistency guarantees natively.

**FR-TRN-013** — The gold mart view `globalsales.mart.v_order_to_year_analytics` must expose a `:window_days` query parameter defaulting to `100`, enabling consumers to control the rolling time window without modifying the view definition.

### 1.3 Data Serving

**FR-SRV-001** — All nine Power BI reports must be served exclusively via the Databricks SQL endpoint; no direct Delta table access from BI tools is permitted.

**FR-SRV-002** — `globalsales.mart.v_customer_sales_summary` (materialized) must be refreshed as part of the nightly pipeline so that the view reflects the current day's data before the 06:00 UTC SLA deadline.

**FR-SRV-003** — All gold mart views and the `fact.get_total_quantity_sold` UDF must be accessible to the Power BI service principal under the access roles defined in the Unity Catalog role matrix. `[PENDING: CX-P05 — access role matrix not yet finalised]`

**FR-SRV-004** — Row-level security (RLS) policies must be applied at the Unity Catalog level on relevant silver and gold assets so that consumers see only the data they are authorised to access.

### 1.4 Orchestration and Scheduling

**FR-ORC-001** — The pipeline must be orchestrated by the Databricks Workflow `nightly_etl_main`, scheduled to trigger nightly at 02:00 UTC.

**FR-ORC-002** — The pipeline must operate in incremental mode on every scheduled run, processing only the delta since the last successful ETL cutoff.

**FR-ORC-003** — On task failure the orchestrator must halt the pipeline and raise an alert (email and/or Databricks notification channel) without proceeding to downstream tasks.

**FR-ORC-004** — The orchestrator must automatically retry a failed task up to a maximum of 2 times before raising a halt-and-alert condition.

**FR-ORC-005** — The pipeline must complete all tasks and make data available downstream no later than 06:00 UTC (T+1 SLA window of 4 hours from trigger to completion).

**FR-ORC-006** — A full historical backfill run must be executable on demand outside the nightly schedule without modifying the `nightly_etl_main` workflow definition.

### 1.5 Lineage and Auditability

**FR-LIN-001** — Every fact row written to `globalsales.fact.sale` and `globalsales.fact.order` must be traceable to its source staging row via the `lineage_key` foreign key into `globalsales.stg.lineage`.

**FR-LIN-002** — `globalsales.stg.lineage` must capture, at minimum: run ID, source reference, batch window start timestamp, batch window end timestamp, row counts ingested, row counts rejected, pipeline version, and final run status.

**FR-LIN-003** — `globalsales.stg.dq_rejections` must record every row rejected by a DQ assertion, including: assertion ID, rejection reason, source table, source primary key value, batch run ID, and rejection timestamp.

**FR-LIN-004** — Delta table history (transaction log) must be preserved for all bronze, silver, and gold assets to support time-travel queries and audit requirements within the retention periods defined in NFR-SCL-003.

---

## 2. Non-Functional Requirements

### 2.1 Performance

**NFR-PRF-001** — The nightly incremental pipeline must process the expected nightly delta (estimated at ~33,000 rows for `fact.sale` at ~12M rows/year) and complete all staging, transformation, DQ, and mart refresh steps within the 4-hour SLA window (02:00–06:00 UTC).

**NFR-PRF-002** — `globalsales.fact.sale` must use liquid clustering on `(invoice_date_key, customer_key, stock_item_key)` to ensure that typical analytical query patterns execute with efficient data skipping on Databricks.

**NFR-PRF-003** — `globalsales.fact.order` must use partition pruning on `order_date_key` and ZORDER on `(customer_key, stock_item_key)` to ensure that date-range and dimension-filtered queries execute with minimal file scan.

**NFR-PRF-004** — The materialized view `globalsales.mart.v_customer_sales_summary` must be designed so that its incremental refresh adds no more than 15 minutes to the total nightly pipeline runtime.

**NFR-PRF-005** — Power BI queries against the Databricks SQL endpoint must return results for standard report filters (date range, customer, product) within 30 seconds under normal concurrent load from all 9 reports.

### 2.2 Scalability

**NFR-SCL-001** — The pipeline architecture must accommodate volume growth to at least 3× the current rate (~36M rows/year) without requiring structural refactoring of the medallion layers or the orchestration workflow.

**NFR-SCL-002** — Liquid clustering on `fact.sale` must be re-evaluated and re-applied if the cumulative row count exceeds a threshold that degrades skipping efficiency, as part of a scheduled maintenance task (not the nightly ETL).

**NFR-SCL-003** — Data retention periods must be enforced at the layer level: bronze staging tables 90 days, silver dimension and fact tables 7 years, gold mart assets 3 years. Vacuum and retention policies must be configured accordingly.

### 2.3 Reliability and Availability

**NFR-REL-001** — The pipeline must be idempotent: re-executing any run for a given batch window must produce the same final state in all target tables without duplicating rows or corrupting dimension history.

**NFR-REL-002** — All Delta tables must use ACID transactions (provided natively by Delta Lake); partial writes must never be visible to consumers.

**NFR-REL-003** — The nightly pipeline must achieve a minimum success rate of 99% over any rolling 30-day window, measured as runs that complete within the SLA without manual intervention.

**NFR-REL-004** — In the event of a pipeline failure, the data state must be recoverable to the last successful run without data loss, using Delta transaction log rollback or re-run from the preserved ETL cutoff.

**NFR-REL-005** — The Databricks SQL endpoint serving Power BI must maintain 99.5% availability during business hours (06:00–22:00 UTC Monday–Friday).

### 2.4 Security and Governance

**NFR-SEC-001** — All data assets must be registered in Databricks Unity Catalog under the `globalsales` catalog; no assets may exist outside Unity Catalog governance boundaries.

**NFR-SEC-002** — Column-level security (CLS) masking policies must be applied to all PII columns in `globalsales.dim.customer`; unmasked access must be restricted to authorised roles only, enforced by Unity Catalog. `[PENDING: CX-P05 — role definitions not yet finalised]`

**NFR-SEC-003** — Row-level security (RLS) must be implemented via Unity Catalog row filters on applicable silver and gold tables, not via application-layer filtering in the ETL code.

**NFR-SEC-004** — Service principals and user groups must follow the principle of least privilege; no consumer role may be granted write or DDL permissions on silver or gold tables.

**NFR-SEC-005** — All data in transit between the source system and Databricks must use encrypted transport (TLS 1.2 or higher).

**NFR-SEC-006** — Secrets (JDBC credentials, API keys, storage access keys) must be stored in Databricks Secrets and never hard-coded in notebooks or configuration files.

### 2.5 Maintainability

**NFR-MNT-001** — All ETL pipeline code must be versioned in source control (Git); deployments to the Databricks Workflow must be triggered exclusively via the CI/CD pipeline, not manual uploads.

**NFR-MNT-002** — The `PROFIT_MARGIN_FACTOR` constant (1.05) used in `mart.v_customer_sales_summary` must be externalised as a configurable parameter (e.g., a Databricks Workflow parameter or a configuration table), enabling business-driven updates without code changes.

**NFR-MNT-003** — Pipeline configuration (schedule, retry count, alert targets, ETL cutoff table reference) must be externalised and must not require code changes to adjust operational parameters.

**NFR-MNT-004** — Each pipeline module (staging ingest, DQ check, dimension SCD2 merge, fact merge, mart refresh) must be independently executable and testable in isolation.

**NFR-MNT-005** — Unit and integration tests must achieve at least 80% code coverage of transformation logic, DQ assertion functions, and UDF implementations.

---

## 3. Data Quality Requirements

### 3.1 Assertions

**DQR-AST-001** — `DQ-SALE-001` (critical): Every row written to `globalsales.fact.sale` must satisfy `total_including_tax IS NOT NULL AND total_including_tax >= 0`. Rows failing this assertion must be routed to `globalsales.stg.dq_rejections` and must not be merged into the fact table.

**DQR-AST-002** — `DQ-SALE-002` (critical): Every row written to `globalsales.fact.sale` must satisfy `invoice_date_key IS NOT NULL`. Rows failing this assertion must be routed to `globalsales.stg.dq_rejections` and must not be merged into the fact table.

**DQR-AST-003** — `DQ-ORDER-001` (critical): Every row written to `globalsales.fact.order` must satisfy `order_date_key IS NOT NULL`. Rows failing this assertion must be routed to `globalsales.stg.dq_rejections` and must not be merged into the fact table.

**DQR-AST-004** — `DQ-ORDER-RI-001` (error): Every `customer_key` in `globalsales.stg.order_staging` must resolve to an active record in `globalsales.dim.customer`. Rows with unresolvable `customer_key` values must be routed to `globalsales.stg.dq_rejections`.

**DQR-AST-005** — `DQ-ORDER-RI-002` (error): Every `stock_item_key` in `globalsales.stg.order_staging` must resolve to an active record in `globalsales.dim.stock_item`. Rows with unresolvable `stock_item_key` values must be routed to `globalsales.stg.dq_rejections`.

**DQR-AST-006** — DQ assertions rated `critical` (DQ-SALE-001, DQ-SALE-002, DQ-ORDER-001) must cause the pipeline to halt and raise an alert if the rejection volume exceeds zero tolerance (i.e., any critical rejection stops the run). `[PENDING: CX-DQ-01 — business DQ thresholds not yet confirmed; zero-tolerance is the interim default]`

**DQR-AST-007** — DQ assertions rated `error` (DQ-ORDER-RI-001, DQ-ORDER-RI-002) must log rejections to `stg.dq_rejections` and may allow the pipeline to continue processing non-rejected rows, subject to confirmation of business tolerance thresholds. `[PENDING: CX-DQ-01]`

### 3.2 Rejection Handling

**DQR-REJ-001** — `globalsales.stg.dq_rejections` must accept rejected rows from all DQ assertions. The table schema must include at minimum: `rejection_id` (IDENTITY), `assertion_id`, `source_table`, `source_pk_value`, `rejection_reason`, `batch_run_id` (FK to `stg.lineage`), `rejected_at` (TIMESTAMP).

**DQR-REJ-002** — Rejected rows must be stored in `stg.dq_rejections` with sufficient detail for an operations analyst to identify, correct, and resubmit the rejected record without access to source system logs.

**DQR-REJ-003** — Rejected rows must never be silently dropped; every rejection must produce exactly one entry in `stg.dq_rejections`.

**DQR-REJ-004** — A resubmission process must be defined such that corrected rows from `stg.dq_rejections` can be re-injected into the staging layer and processed by the next ETL run without triggering duplicate-key violations on the fact tables.

### 3.3 Row Count Reconciliation

**DQR-REC-001** — After each nightly run, the pipeline must perform a zero-tolerance row count reconciliation: the count of rows successfully staged minus the count of rows rejected must equal the count of rows merged into the target fact or dimension table.

**DQR-REC-002** — The reconciliation check must be recorded in `globalsales.stg.lineage` as part of the run metadata (rows_staged, rows_rejected, rows_merged).

**DQR-REC-003** — Any discrepancy in the row count reconciliation (staged ≠ rejected + merged) must immediately halt the pipeline and raise a critical alert, even if individual DQ assertions passed.

### 3.4 Pending Thresholds

**DQR-THR-001** — `[PENDING: CX-DQ-01]` Once business DQ thresholds are confirmed, the pipeline must enforce configurable percentage-based rejection thresholds per assertion ID. Until CX-DQ-01 is resolved, zero-tolerance (0 rejections permitted for critical assertions) remains the enforced default.

**DQR-THR-002** — `[PENDING: CX-DQ-01]` The threshold configuration must be stored in a control table or Databricks Workflow parameter (not hard-coded), enabling business teams to adjust thresholds without a code release.

---

## 4. Interface Requirements

### 4.1 BI Consumers

**IFR-BI-001** — The Databricks SQL endpoint must expose the following nine Power BI report data connections via named datasets or views accessible to the Power BI service principal:

| Report Name | Primary Asset(s) |
|---|---|
| `wwidw-sales` | `mart.v_customer_sales_summary` |
| `wwidw-sales-nofilter` | `mart.v_customer_sales_summary` |
| `wwidw-dynamic-product-basket-current` | `fact.sale`, `dim.stock_item` |
| `wwidw-dynamic-product-basket-prior` | `fact.sale`, `dim.stock_item` |
| `wwidw-purchase-sale-per-stockitem` | `fact.sale`, `dim.stock_item` |
| `wwidw-orderdetails` | `mart.v_order_details` |
| `wwidw-orderdetails-by-employee-2024` | `mart.v_order_details`, `dim.employee` |
| `wwidw-orderitemsrankings` | `fact.order`, `dim.stock_item` |
| `wwidw-total-orders-march-per-province` | `fact.order`, `dim.city` |

**IFR-BI-002** — The `:start_date` parameter on `mart.v_order_details` must be passed from the Power BI report query at runtime; the view must not default to a full-table scan when the parameter is omitted.

**IFR-BI-003** — The `:window_days` parameter on `mart.v_order_to_year_analytics` must default to `100` when not supplied by the consumer, and the view must document this default in its DDL comment.

**IFR-BI-004** — Power BI datasets must connect to the Databricks SQL endpoint using a service principal with read-only permissions scoped to the `globalsales.mart` schema and the specific gold assets listed in IFR-BI-001. `[PENDING: CX-P05]`

**IFR-BI-005** — All BI-facing assets must remain schema-stable (no column drops, no column renames, no data-type narrowing) unless a versioned migration process is followed and BI report owners are notified in advance.

### 4.2 Upstream Sources

**IFR-SRC-001** — The pipeline must ingest from the upstream OLTP source system using the integration strategy to be confirmed. `[PENDING: CX-P04 — confirm whether direct OLTP extraction (JDBC), CDC stream, or intermediate landing zone is the approved pattern]`

**IFR-SRC-002** — Until CX-P04 is resolved, the pipeline interface contract assumes batch extraction into `stg.sale_staging` and `stg.order_staging` via a JDBC connection using the ETL service principal credentials stored in Databricks Secrets.

**IFR-SRC-003** — The extraction query must be bounded by the ETL cutoff recorded in `stg.etl_cutoff` so that only incremental data is fetched per run.

**IFR-SRC-004** — The source schema contract (column names, data types, and nullability of the staging tables) must be documented and version-controlled; any upstream schema change must trigger a compatibility check before deployment.

### 4.3 Downstream Dependencies

**IFR-DWN-001** — Downstream consumers (Power BI, any future API layer) must treat the gold mart views (`mart.v_customer_sales_summary`, `mart.v_order_details`, `mart.v_order_to_supply_analytics`, `mart.v_order_to_year_analytics`) as the stable consumption interface; direct access to silver `fact.*` or `dim.*` tables by external consumers is prohibited except as explicitly granted. `[PENDING: CX-P05]`

**IFR-DWN-002** — The SQL UDF `globalsales.fact.get_total_quantity_sold` must be callable from any SQL context within the `globalsales` catalog by authorised roles; its signature must remain backward-compatible unless a versioned deprecation process is followed.

**IFR-DWN-003** — If any downstream system depends on a specific T+1 data freshness guarantee (data available by 06:00 UTC), that dependency must be registered in the project interface register, and the pipeline SLA must be monitored against it.

---

## 5. Constraints and Assumptions

**CON-001** — The target platform is exclusively Databricks Delta Lake with Unity Catalog on the `globalsales` catalog. No other database engines, cloud storage schemas, or compute platforms are in scope for this data product.

**CON-002** — The medallion architecture layers are fixed: `stg` (bronze/staging), `dim`/`fact` (silver), `mart` (gold). Introducing additional layers or bypassing the medallion flow requires a formal architecture change request.

**CON-003** — The pipeline schedule is fixed at nightly at 02:00 UTC with a maximum of 2 automatic retries. Changes to schedule frequency or retry policy require an operational change request against `nightly_etl_main`.

**CON-004** — Historical data coverage starts at 2013-01-01. No data predating this boundary is in scope; the initial full load must not attempt to ingest records with dates before this boundary.

**CON-005** — The `PROFIT_MARGIN_FACTOR` constant is set at 1.05 as of the product definition date. Any change to this value is a business decision and must follow the parameterisation mechanism defined in NFR-MNT-002; it is not a code bug.

**CON-006** — `dim.date` is a static calendar dimension (SCD Type 0). Calendar extension beyond the currently loaded date range is an explicit, separately scheduled operation and is out of scope for the nightly ETL.

**CON-007** — PII masking on `dim.customer` is a mandatory compliance control. Any relaxation of masking rules requires legal/compliance sign-off and a Unity Catalog policy update; the ETL code must not contain any bypass logic.

**CON-008** — `[PENDING: CX-P04]` The upstream extraction strategy has not been confirmed. If a CDC or streaming approach is selected, the staging layer interface contract and the ETL cutoff mechanism may need to be revised. This requirement document assumes batch extraction as the default.

**CON-009** — `[PENDING: CX-P05]` The Unity Catalog access role matrix has not been finalised. All security and serving requirements referencing role names use placeholder descriptions. Role names, group assignments, and permission grants must be resolved before the access control layer can be fully implemented.

**CON-010** — `[PENDING: CX-DQ-01]` Business DQ thresholds have not been confirmed. Until confirmed, all critical assertions operate under zero-tolerance (any rejection halts the pipeline). The design must accommodate threshold configuration without a code release once thresholds are agreed.

**CON-011** — The nightly pipeline volume is estimated at ~12M rows/year on `fact.sale` (~33,000 rows/night). This assumption underpins all performance NFRs. A volume revalidation must be performed if actual ingestion deviates by more than 20% from this estimate.

**CON-012** — The `mart.v_order_to_supply_analytics` view explicitly excludes any NOLOCK or dirty-read patterns. Delta Lake snapshot isolation is assumed sufficient for all consumer consistency requirements. If a consumer requires a different isolation level, this constraint must be revisited.

**CON-013** — All nine Power BI reports are existing reports being re-pointed to the new Databricks SQL endpoint. Report logic (measures, calculated columns) is out of scope; only the data layer interface is in scope for this product.

**CON-014** — Data retention enforcement (bronze 90 days / silver 7 years / gold 3 years) relies on Databricks Delta table `TBLPROPERTIES` retention settings and scheduled VACUUM jobs. Retention configuration is a deployment-time concern and must be applied before the pipeline goes to production.
