# Data Product Catalog — Explained

**Project:** Inventory_Stock_Project
**ODPS Schema Version:** 4.1
**Generated:** 2026-09-07
**Format:** YAML (machine-readable) + Markdown (human-readable)

---

## What This Spec Is

The catalog is the **machine-readable product registry** for the entire project. It comes in two formats:

- **`catalog.yaml`** — structured YAML consumable by tools, automation, and the SmartBuilder code generation phase
- **`catalog.md`** — human-readable Markdown rendering of the same data for stakeholders, reviewers, and documentation

It is produced **after** the modernization plan and transformation rules are complete, and **after** at least one product has been fully specified through the TCP flow (as-is → product rules → to-be). The catalog aggregates everything known about each data product into a single, authoritative registry.

Think of it as the **manifest** — if the modernization plan is "why are we migrating?" and the transformation rules are "how do we translate?", the catalog is "what exactly are we delivering?"

---

## Why This Spec Exists

The catalog serves three distinct audiences, each with different needs:

### 1. SmartBuilder (automated code generation)

The SmartBuilder phase reads `catalog.yaml` to know **exactly** what to build:
- Which tables to create (names, layers, clustering keys, SCD types)
- Which orchestration jobs to configure (schedule, strategy, task dependencies)
- Which DQ assertions to implement (count, targets, rejection sink)
- Which consumers to reconnect (Power BI reports, SQL Warehouse endpoints)

Without the catalog, SmartBuilder would have to parse the entire to-be document and guess — the catalog gives it structured, unambiguous inputs.

### 2. Platform team (infrastructure provisioning)

The platform team needs to provision Unity Catalog schemas, set up service principals, configure SQL Warehouse endpoints, and allocate storage. The catalog tells them:
- Which schemas exist (`bronze`, `silver_dim`, `silver_fact`)
- Which tables need CDF enabled (`lineage_run`)
- Which tables are externally owned vs. product-owned
- What retention policies apply (7 years for silver, 90 days for bronze)
- What access roles are needed (pending PD-003)

Without the catalog, the platform team pieces this together from scattered documents.

### 3. Project governance (tracking and accountability)

Project managers and stakeholders need a single place to see:
- How many products exist and their status (active vs. candidate)
- What pending decisions block production cutover
- What SLAs are committed
- What consumers will be impacted
- What the governance posture is (RLS, CLS, PII masking)

Without the catalog, this information is buried across multiple spec files.

---

## Section-by-Section Breakdown

### Project Header

```yaml
catalog:
  projectName: Inventory_Stock_Project
  projectDescription: >
    Modernisation of the WideWorldImporters procurement and inventory workload
    onto Databricks Delta Lake Unity Catalog...
  sourceSystem:
    platform: Microsoft SQL Server 2014
    database: wideworldimportersdw
  targetSystem:
    platform: Databricks Delta Lake Unity Catalog
    catalog: inventory_stock
    schemaConvention: lowercase_snake_case
    migrationMode: hybrid
```

**What it is:** The project-level metadata that frames everything below.

**Why it matters:** This header establishes the source/target contract for the entire catalog. The `catalog: inventory_stock` field is especially important — it's the Unity Catalog name that appears in every three-part table reference (`inventory_stock.silver_fact.fact_purchase`). Get this wrong and every DDL, every notebook, and every report connection breaks.

---

### Products List

```yaml
products:
  - id: Purchase          # status: active,  priority: primary
  - id: Inventory_Movement # status: candidate, priority: future
```

**What it is:** The registry of all data products in the project, with their lifecycle status.

| Product | Status | Priority | What it means |
|---|---|---|---|
| **Purchase** | active | primary | Fully specified, ready for build. All TCP artifacts exist (as-is, to-be, product rules). SmartBuilder can generate code. |
| **Inventory_Movement** | candidate | future | Identified but not yet specified. No TCP artifacts exist. Placeholder entry so the project knows what's coming next. |

**Why it matters:** The `status` field controls what's actionable. Only `active` products have downstream specs. `candidate` products are visible in the registry but have `null` for all artifact references — this prevents anyone from trying to build something that hasn't been designed yet.

---

### Purchase Product — Identity & Description

```yaml
- id: Purchase
  displayName: Purchase
  status: active
  priority: primary
  domain: Procurement / Purchasing
  businessProcess: Procure-to-Pay
  architecture: medallion
  description: >
    Covers the purchase order transaction domain sourced from the
    WideWorldImporters star schema. Implements a medallion architecture
    (bronze staging and control tables → silver dimensions and facts)
    on Databricks Delta Lake Unity Catalog. Resolves SCD-2 surrogate keys
    for supplier and stock item via a temporal range join helper. Corrects
    the legacy SSIS staging-truncation bug by replacing per-run DELETE with
    full OVERWRITE of the bronze staging table.
```

**What it is:** The product's identity card — domain, business process, architecture pattern, and a description that captures the key technical decisions.

**Why it matters:** The description isn't just prose — it names three critical facts that any reader must know:
1. **Medallion architecture** — bronze → silver layering (not a flat copy)
2. **SCD-2 surrogate key resolution** — the hardest piece of the ETL
3. **SSIS bug correction** — the migration fixes a production defect

Anyone reading this description immediately understands what makes this product non-trivial.

---

### TCP Artifacts

```yaml
tcpArtifacts:
  asIs: products/Purchase/current/specifications/as-is.md
  toBe: products/Purchase/current/specifications/to-be.md
  productTransformationRules: products/Purchase/current/specifications/product-transformation-rules/
```

**What it is:** Pointers to the three core TCP specification files for this product.

**Why it matters:** These paths are the **traceability links** between the catalog and the detailed specs. Any tool or reviewer can follow these paths to find the full analysis (as-is), the target design (to-be), and the product-specific rules. For the `Inventory_Movement` product, all three are `null` — confirming it hasn't been specified yet.

---

### Source Lineage

```yaml
sourceLineage:
  sourceDatabase: wideworldimportersdw
  sourceTables:
    - fact.purchase
    - dimension.supplier
    - dimension.stock item
    - dimension.date
  sourceIntegration:
    - integration.purchase_staging
    - integration.etl cutoff
    - integration.lineage
    - integration.migratestagedpurchasedata
    - integration.getlastetlcutofftime
    - integration.getlineagekey
    - sequences.lineagekey
    - application.configuration_reseedetl (Purchase-domain portions)
  sourceOrchestration:
    - SSIS pipeline_dailyetlmain (Purchase container)
    - SSIS pipeline_item_truncate purchase_staging (bug: targets Order_Staging)
    - SSIS pipeline_item_extract updated purchase data to staging
    - SSIS pipeline_item_migrate staged purchase data
```

**What it is:** The complete inventory of everything in the legacy system that this product touches — tables, procedures, sequences, and SSIS pipeline items.

**Why it matters:** This is the **legacy footprint** confined to a single block. All references to the old system live here and nowhere else in the catalog. This separation is deliberate — it means the rest of the catalog describes the target state, and this block is the only place you need to look to understand "where did this come from?"

The SSIS bug is flagged inline (`bug: targets Order_Staging`) so it's visible even in a quick scan of the YAML.

---

### Output Datasets — Facts

```yaml
outputDatasets:
  facts:
    - name: inventory_stock.silver_fact.fact_purchase
      type: delta_table
      layer: silver
      clusteringKeys:
        - date_key
        - supplier_key
      scdType: none
      description: >
        Grain: one row per purchase order line × supplier × stock item ×
        order date. CLUSTER BY (date_key, supplier_key). SCD-2 surrogate
        keys resolved via temporal range join in sk_resolver.py.
```

**What it is:** The central fact table — the primary analytical output of the entire product.

**Why it matters:** Three critical details are captured here that drive code generation:

| Detail | Value | Impact |
|---|---|---|
| **Grain** | One row per purchase order line × supplier × stock item × order date | Defines the MERGE predicate — if you get the grain wrong, the MERGE either duplicates rows or overwrites them incorrectly |
| **Clustering keys** | `(date_key, supplier_key)` | Determines physical data layout — queries filtering by date and supplier will be fast; other filters will be slower |
| **SCD type** | `none` | The fact table itself is not SCD — it receives resolved surrogate keys from SCD-2 dimensions, but its own rows are simple upserts |

---

### Output Datasets — Dimensions

```yaml
dimensions:
  - name: inventory_stock.silver_dim.supplier
    type: delta_table
    layer: silver
    scdType: 2
    ownership: external
    description: >
      SCD-2 supplier dimension with _current view. Externally owned.
      Read dependency for Purchase ETL surrogate key resolution.

  - name: inventory_stock.silver_dim.stock_item
    type: delta_table
    layer: silver
    scdType: 2
    ownership: external

  - name: inventory_stock.silver_dim.date
    type: delta_table
    layer: silver
    scdType: none
    ownership: external
    refreshStrategy: static
```

**What it is:** The three dimension tables that the fact table references.

**Why it matters:** The `ownership: external` field is the most important attribute here. It means:

- Purchase **reads** these tables but does **not write** to them
- Another team is responsible for loading them
- The Databricks Workflow must declare these loads as upstream dependencies
- If the external team's load fails, Purchase must not run — otherwise surrogate keys resolve to 0

The `refreshStrategy: static` on the date dimension means it's loaded once and never changes — no runtime dependency, just a "must exist" check.

This ownership model prevents the dangerous scenario where two products both try to load the same dimension table, causing race conditions or duplicate rows.

---

### Output Datasets — Staging & Control

```yaml
staging:
  - name: inventory_stock.bronze.purchase_staging
    description: >
      Written in OVERWRITE mode per run to eliminate the legacy
      SSIS staging-truncation bug. Includes lineage_key and
      _extracted_at_utc audit columns.

  - name: inventory_stock.bronze.etl_cutoff
    description: >
      High-watermark control table storing the last successfully
      processed cutoff timestamp per entity.

  - name: inventory_stock.bronze.lineage_run
    description: >
      ETL lineage and audit log table. GENERATED ALWAYS AS IDENTITY
      surrogate key replaces the legacy sequences.lineagekey.
      Change Data Feed enabled.

  - name: inventory_stock.bronze.dq_rejections
    description: >
      Centralised data quality rejection sink. Rows failing DQ
      assertions are written here with lineage_key, rule_id,
      source table, PK value, and violation detail.
```

**What it is:** The four bronze-layer tables that support the ETL pipeline.

**Why it matters:** Each table has a specific role:

| Table | Role | Why it exists |
|---|---|---|
| `purchase_staging` | Transient landing zone | OVERWRITE mode fixes the SSIS bug — no stale rows can accumulate |
| `etl_cutoff` | Watermark control | Drives incremental extraction — without it, every run would be a full reload |
| `lineage_run` | Audit log | Tracks every ETL run — when it started, when it finished, whether it succeeded, how many rows it processed |
| `dq_rejections` | DQ violation store | Captures rows that fail quality checks without blocking the pipeline — enables post-run investigation |

`dq_rejections` is a **new** table that didn't exist in the legacy system. The legacy system had no structured DQ violation tracking — problems were invisible until a business user noticed incorrect numbers in a report.

---

### Input Datasets

```yaml
inputDatasets:
  - name: inventory_stock.bronze.purchase_staging
    role: primary_source
  - name: inventory_stock.silver_dim.supplier
    role: scd2_lookup
    description: >
      Required at runtime for surrogate key resolution. Must be loaded
      before the Purchase ETL Workflow task executes (external dependency).
  - name: inventory_stock.silver_dim.stock_item
    role: scd2_lookup
  - name: inventory_stock.silver_dim.date
    role: fk_lookup
    description: FK target for date_key. Static; no runtime load dependency.
  - name: inventory_stock.bronze.etl_cutoff
    role: watermark_control
```

**What it is:** The runtime dependencies of the Purchase pipeline — what it reads at execution time.

**Why it matters:** The `role` field classifies each dependency:

| Role | Meaning | Runtime implication |
|---|---|---|
| `primary_source` | The main data input | Must be written (by `nb_extract_purchase`) before the transform step reads it |
| `scd2_lookup` | SCD-2 dimension for surrogate key resolution | **Must be loaded by another team's pipeline before Purchase runs** — this is the cross-team dependency from Risk #6 |
| `fk_lookup` | FK reference table | Must exist but has no runtime load dependency (static data) |
| `watermark_control` | Drives incremental extraction window | Read at job start to determine which source rows to extract |

The `scd2_lookup` role is the critical one. It encodes the constraint that `supplier` and `stock_item` must be pre-loaded. This drives the Workflow task dependency graph — `migrate_staged_purchase_data` cannot start until the dimension load tasks complete.

---

### Orchestration

```yaml
orchestration:
  platform: Databricks Workflows
  primaryJob: nightly_etl_purchase
  schedule: "0 2 * * *"
  strategy: incremental_nightly
  description: >
    nb_extract_watermark reads the high-watermark from bronze.etl_cutoff,
    opens a lineage record in bronze.lineage_run, and publishes lineage_key
    via taskValues. nb_extract_purchase extracts rows updated since the
    watermark into bronze.purchase_staging (OVERWRITE). migrate_staged_purchase_data
    resolves SCD-2 surrogate keys, performs MERGE INTO, executes five QA checks,
    and closes the lineage record. Dimension loads are declared as upstream task
    dependencies.
```

**What it is:** The Databricks Workflow configuration for the Purchase pipeline.

**Why it matters:** Four key details:

| Detail | Value | Impact |
|---|---|---|
| **Schedule** | `0 2 * * *` (02:00 UTC daily) | Must complete before the 06:00 UTC SLA — gives 4 hours for the pipeline to run |
| **Strategy** | `incremental_nightly` | Not a full reload — only rows modified since the last watermark are extracted |
| **Task chain** | `nb_extract_watermark` → `nb_extract_purchase` → `migrate_staged_purchase_data` | Sequential dependency — each task depends on the previous one completing successfully |
| **External dependencies** | Dimension loads must complete before the Purchase pipeline starts | Encoded as upstream task dependencies in the Workflow graph |

The description is detailed enough that someone could configure the Workflow from this spec alone — task names, data flow, dependency ordering, and the lineage key propagation mechanism (`taskValues`) are all specified.

---

### Data Quality

```yaml
dataQuality:
  assertionCount: 5
  assertionTargets:
    - inventory_stock.silver_fact.fact_purchase
    - inventory_stock.bronze.purchase_staging
  rejectionSink: inventory_stock.bronze.dq_rejections
  rowCountReconciliation:
    strategy: zero_tolerance
    description: >
      QA-P001: staging row count must equal merged fact row count.
      Mismatch raises RuntimeError and marks the Workflow task FAILED.
  pendingThresholds:
    - id: QA-DQ-01
      description: >
        Business-defined acceptable DQ failure thresholds for informational
        assertions not yet confirmed by stakeholders.
```

**What it is:** The DQ framework for the Purchase product — 5 assertions, a rejection sink, and a pending business decision.

**Why it matters:** The DQ section establishes two categories of assertions:

| Category | Behavior | Assertions |
|---|---|---|
| **Blocking** | Pipeline fails if violated | QA-P001: row count reconciliation (zero tolerance — staging count must equal merged count) |
| **Informational** | Pipeline continues; violations logged and written to `dq_rejections` | QA-P002: orphaned surrogate keys, QA-P003: RI violations, QA-P004: business rule breaches |

The `pendingThresholds` entry (QA-DQ-01) is important — it flags that **business stakeholders have not yet confirmed** what failure rates are acceptable for the informational assertions. Until this is resolved, the assertions log violations but don't block. This is a deliberate design choice: don't block production on thresholds that haven't been agreed upon.

The `rejectionSink` is `bronze.dq_rejections` — a centralized table where every violation is written with full traceability (`lineage_key`, `rule_id`, column-level detail). This didn't exist in the legacy system. In the old world, DQ problems were invisible until a business user noticed incorrect report numbers.

---

### Consumers

```yaml
consumers:
  - type: bi_reports
    platform: Power BI
    count: 2
    accessEndpoint: Databricks SQL Warehouse
    primaryDatasets:
      - inventory_stock.silver_fact.fact_purchase
      - inventory_stock.silver_dim.supplier
      - inventory_stock.silver_dim.stock_item
    reports:
      - name: wwidw_purchase_and_sale_per_stockitem_dynamic
        description: >
          Cross-domain procurement-vs-sales comparison. Requires coordinated
          cutover with the Sales_Orders product.
      - name: wwidw_ordered_by_supplier
        description: Supplier performance and fill-rate analytics.
```

**What it is:** The downstream consumers that read from the Purchase product's tables.

**Why it matters:** Two reports, two different risk profiles:

| Report | Risk | Why |
|---|---|---|
| `wwidw_purchase_and_sale_per_stockitem_dynamic` | **High** — requires coordinated cutover with Sales_Orders | This report joins `fact_purchase` with `fact_sale` (from a different product). If Purchase is migrated to Databricks but Sales_Orders is still on SQL Server, this report breaks — it can't join across platforms. Both products must be cut over together. |
| `wwidw_ordered_by_supplier` | **Low** — self-contained within Purchase domain | Only joins `fact_purchase` with `supplier` — both are in the Purchase product scope. Can be cut over independently. |

The `accessEndpoint: Databricks SQL Warehouse` specifies that Power BI connects through a SQL Warehouse, not directly to Delta tables. This is an architectural decision that affects provisioning (the platform team must set up a SQL Warehouse endpoint) and security (access is controlled at the SQL Warehouse level, not the storage level).

---

### SLA

```yaml
sla:
  dataFreshness: daily
  expectedLoadCompletionUtc: "06:00"
  retentionPolicy:
    silver: 7_years
    bronze: 90_days
```

**What it is:** The service level agreement for data freshness, load timing, and retention.

**Why it matters:**

| SLA | Value | Impact |
|---|---|---|
| **Data freshness** | Daily | Business users expect data from yesterday to be available when they arrive in the morning |
| **Load completion** | 06:00 UTC | The pipeline starts at 02:00 UTC and must finish by 06:00 UTC — a 4-hour window. If it exceeds this, the SLA is breached. |
| **Silver retention** | 7 years | `silver_fact.fact_purchase` and `silver_dim.*` must be kept for 7 years — this is likely a regulatory or compliance requirement |
| **Bronze retention** | 90 days | `bronze.purchase_staging` and control tables only need 90 days — they're transient/operational data, not long-term analytical data |

The retention split (7 years vs. 90 days) drives storage cost estimates. Silver tables accumulate over 7 years; bronze tables are automatically cleaned up after 90 days. This distinction should be configured via Unity Catalog table retention properties.

---

### Governance

```yaml
governance:
  platform: Unity Catalog
  rowLevelSecurity: false
  columnLevelSecurity: false
  piiMasking:
    enabled: false
    description: No PII columns identified in the Purchase domain at this time.
  accessRoleMatrix:
    status: pending
    description: >
      Formal Unity Catalog role assignments not yet defined.
      silver_fact.fact_purchase readable by BI service principals and analysts;
      bronze.* restricted to ETL service principals;
      bronze.dq_rejections readable by data engineering team.
```

**What it is:** The security and governance posture for the Purchase product.

**Why it matters:** The governance section documents three important facts:

1. **No RLS/CLS/PII masking needed** — the Purchase domain doesn't contain personally identifiable information. Supplier names and stock item names are business data, not personal data. This is a deliberate assessment, not an oversight.

2. **Access role matrix is pending (PD-003)** — the formal Unity Catalog role assignments haven't been defined yet. The description sketches the intended model (BI principals read silver, ETL principals read/write bronze, data engineers read `dq_rejections`), but the specific role names and grants haven't been finalized with the platform team.

3. **Unity Catalog is the governance platform** — not a separate tool, not manual permissions. This means all access control is managed through UC's RBAC model.

---

### Pending Decisions

```yaml
pendingDecisions:
  - id: PD-001
    description: >
      Source connectivity: confirm JDBC connection profile and credentials
      for the Databricks → SQL Server 2014 incremental extract.
    owner: TBD
    dueDate: TBD

  - id: PD-002
    description: >
      reseed_purchase_environment.py scope: scope owner must confirm whether
      the reseed utility is retained or dropped. Sentinel row pre-seeding
      required regardless.
    owner: TBD
    dueDate: TBD

  - id: PD-003
    description: >
      Unity Catalog access role matrix: define role assignments for BI analysts,
      data engineers, and ETL service principals.
    owner: TBD
    dueDate: TBD

  - id: QA-DQ-01
    description: >
      Business DQ thresholds: stakeholders must confirm acceptable failure
      rates for informational QA assertions before go-live.
    owner: TBD
    dueDate: TBD
```

**What it is:** Four decisions that must be resolved before the Purchase product goes to production.

**Why it matters:** Each pending decision blocks a specific part of the cutover:

| ID | What's blocked | Why it can't be resolved by automation |
|---|---|---|
| **PD-001** | `nb_extract_purchase.py` — the extract notebook can't connect to the source without JDBC credentials | Credentials are environment-specific and security-sensitive — they must be provisioned by the platform team and stored in a Databricks Secret Scope |
| **PD-002** | `reseed_purchase_environment.py` — the init notebook can't be finalized without knowing if the reseed utility is kept or dropped | This is a business decision with operational impact — keeping it means developers can reset environments; dropping it means they can't. The scope owner must decide. |
| **PD-003** | `purchase_grants.sql` — the GRANT statements can't be written without knowing the role names | Role names are organization-specific — they depend on the platform team's Unity Catalog role hierarchy |
| **QA-DQ-01** | DQ assertion tuning — informational assertions can't be tuned without business-approved thresholds | What's an acceptable orphaned-key rate? 0.1%? 1%? 5%? Only business stakeholders can answer this. |

All four have `owner: TBD` and `dueDate: TBD` — forcing functions that must be resolved during the cutover checklist (documented in the runbook).

---

### Inventory_Movement Product (Placeholder)

```yaml
- id: Inventory_Movement
  displayName: Inventory Movement
  status: candidate
  priority: future
  domain: Inventory and Supply Chain
  businessProcess: Stock Movement
  architecture: medallion
  tcpArtifacts:
    asIs: null
    toBe: null
    productTransformationRules: null
  outputDatasets: null
  orchestration: null
  dataQuality: null
  consumers: null
  sla: null
  governance: null
  pendingDecisions: null
```

**What it is:** A placeholder entry for the next data product in the project.

**Why it matters:** Everything is `null` except the identity fields. This communicates:
- "We know this product exists"
- "We know it belongs to the Inventory and Supply Chain domain"
- "We have not specified it yet — don't try to build it"

When the team is ready to start Inventory_Movement, they run the TCP flow (`/product-scope` → `/product-as-is` → `/product-transformation-rules` → `/product-to-be`), and the catalog entry gets populated with real data. Until then, the `null` fields are a clear signal: this is a known future item, not a forgotten one.

---

## How This Spec Is Used Downstream

| Consumer | What it reads from the catalog |
|---|---|
| **SmartBuilder `/smartbuilder_development-plan`** | `outputDatasets` (table definitions, clustering keys, SCD types), `orchestration` (job name, schedule, strategy), `dataQuality` (assertion count, rejection sink), `inputDatasets` (runtime dependencies with roles) |
| **SmartBuilder `/smartbuilder_generate-db`** | `outputDatasets` (table names, layers, types) → generates DDL files |
| **SmartBuilder `/smartbuilder_generate-etl`** | `orchestration` (task chain), `inputDatasets` (dependency roles), `dataQuality` (assertion targets) → generates ETL notebooks |
| **Platform team** | `targetSystem` (catalog name, schema convention), `governance` (access roles), `sla` (retention policies), `consumers` (SQL Warehouse endpoint) |
| **Project manager** | `pendingDecisions` (what blocks go-live), `products` (status of each product), `sla` (committed timelines) |
| **Runbook / cutover checklist** | `pendingDecisions` (PD-001 through PD-003, QA-DQ-01) → the cutover checklist maps 1:1 to these entries |

---

## File Reference

| File | Location | Purpose |
|---|---|---|
| `catalog.yaml` | `project/current/catalog.yaml` | Machine-readable YAML — consumed by SmartBuilder and automation |
| `catalog.md` | `project/current/catalog.md` | Human-readable Markdown rendering — for stakeholders and documentation |
