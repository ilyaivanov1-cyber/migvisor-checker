# As-Is Analysis — Purchase

## 1. Definition

### 1.1 System Identity

| Field | Value |
|---|---|
| Data product name | Purchase |
| Parent project | GlobalPurchase_Project |
| Source system | `WideWorldImportersDW` |
| Base node (fact table) | `wideworldimportersdw.fact.purchase` (object id: `197f0cba-80b1-4837-b448-3268bdf6649c`) |
| Source database platform | Microsoft SQL Server 2014 |
| Source schema | `Fact` (curated layer), `Integration` (staging/ETL layer) |
| Target platform | Databricks Delta Lake (target catalog: `globalpurchase`) |
| DDL confirmed by MCP | Yes — DDL retrieved and verified via migVisor Explainer |

The Purchase data product is the authoritative procurement fact in the `WideWorldImportersDW` data warehouse. It is defined at its core by the table `Fact.Purchase`, which records each purchase order line as a grain-level row keyed by surrogate dimension keys (date, supplier, stock item) and the source system's natural purchase order identifier. The table was discovered and confirmed by querying the migVisor Explainer graph; the full DDL is reproduced below for reference.

**Confirmed DDL (source):**

```sql
CREATE TABLE WideWorldImportersDW.Fact.Purchase (
    Purchase Key   bigint IDENTITY(1,1) NOT NULL,
    Date Key       date                 NOT NULL,
    Supplier Key   int                  NOT NULL,
    Stock Item Key int                  NOT NULL,
    WWI Purchase Order ID int           NULL,
    Ordered Outers int                  NOT NULL,
    Ordered Quantity int                NOT NULL,
    Received Outers int                 NOT NULL,
    Package        nvarchar(100) COLLATE Latin1_General_100_CI_AS NOT NULL,
    Is Order Finalized bit              NOT NULL,
    Lineage Key    int                  NOT NULL,
    CONSTRAINT PK_Fact_Purchase
        PRIMARY KEY (Purchase Key, Date Key),
    CONSTRAINT FK_Fact_Purchase_Date_Key_Dimension_Date
        FOREIGN KEY (Date Key) REFERENCES Dimension.Date(Date),
    CONSTRAINT FK_Fact_Purchase_Stock_Item_Key_Dimension_Stock_Item
        FOREIGN KEY (Stock Item Key) REFERENCES [Dimension].[Stock Item](Stock Item Key),
    CONSTRAINT FK_Fact_Purchase_Supplier_Key_Dimension_Supplier
        FOREIGN KEY (Supplier Key) REFERENCES Dimension.Supplier(Supplier Key)
);
```

**Key structural observations from the DDL:**

- The primary key is a composite of `Purchase Key` (IDENTITY surrogate) and `Date Key`, which is uncommon — `Date Key` participates in the PK as a partitioning-aware design choice rather than a natural business key component.
- `Stock Item Key` references `[Dimension].[Stock Item]` — the dimension table name contains a space, which is a known migration risk (requires renaming in the target platform).
- `Lineage Key` is a non-nullable FK to `Integration.Lineage`, tying every fact row to its ETL run record.
- No `Received Quantity` column is present — received volume is tracked only in outers (`Received Outers`), not in individual units.

---

### 1.2 Business Purpose

The Purchase data product serves the **procurement and purchasing** domain of the WideWorldImporters (WWI) business. It answers the following business questions:

- How many units (outers and quantities) were ordered from each supplier, for each stock item, on each date?
- How many outers were actually received versus ordered (fill/receipt rate)?
- Which purchase orders are open (not yet finalized) versus closed?
- How many distinct purchase orders were placed in a given period?
- What is the purchasing volume trend by supplier, stock item, date range, or packaging type?

The product supports procurement analysis, supplier performance tracking, inventory replenishment planning, and order fulfilment monitoring. It is the primary fact table used by the two purchase-domain BI reports:

- `wwidw purchase and sale per stockitem dynamic` — cross-domain purchase/sale comparison by stock item
- `wwidw-ordered-by-supplier` — purchase volume analysis by supplier

The product does not own or produce any analytics views (the cross-domain `analytics.v_ordertoyearanalytics` reads `fact.purchase` but is driven by the `fact.order` domain and is out of scope for this product).

---

### 1.3 Technology Stack

| Layer | Source-system technology |
|---|---|
| Database engine | Microsoft SQL Server 2014 (`WideWorldImportersDW` database) |
| Schema model | Kimball star schema — `Fact` schema for the curated layer, `Integration` schema for staging and ETL control |
| ETL orchestration | SQL Server Integration Services (SSIS) — nightly batch (`pipeline_dailyetlmain`) |
| ETL logic | T-SQL stored procedure (`integration.migratestagedpurchasedata`) called from SSIS |
| Staging table | `integration.purchase_staging` — landing area for incremental purchase-update extracts |
| Watermark / incremental control | `integration.etl cutoff` table + `integration.getlastetlcutofftime` procedure |
| Lineage / audit | `integration.lineage` table + `sequences.lineagekey` SQL Server SEQUENCE object |
| Dimension management | SCD Type 2 lookups in T-SQL (correlated subqueries in `migratestagedpurchasedata`); dimension tables in `Dimension` schema |
| BI / reporting | Reports consuming `fact.purchase` (tool names not disclosed in scope; two reports confirmed in scope) |
| Target platform | Databricks Delta Lake (Databricks Lakehouse; Unity Catalog; catalog: `globalpurchase`) |

---

### 1.4 Stakeholders

The product scope document indicates the scope owner field as `[USER INPUT REQUIRED]` — a named owner has not been provided. The following stakeholder roles are inferred from the system design and migration context:

| Role | Responsibility | Notes |
|---|---|---|
| Scope owner (TBD) | Accountable for the Purchase product migration | To be confirmed by project team |
| DW / ETL engineering team | Owns the SSIS pipeline, T-SQL procedures, and staging layer | Source-side operational owners |
| BI / reporting team | Consumes `fact.purchase` via the two scoped BI reports | Downstream consumers |
| Procurement / purchasing business team | Uses BI reports for operational and analytical decision-making | Business stakeholders |
| Databricks platform team | Provides the target lakehouse infrastructure | Target-platform owners |
| Shared infrastructure team | Owns conformed dimensions (`dimension.supplier`, `dimension.stock item`, `dimension.date`), `integration.lineage`, `integration.etl cutoff`, and the lineage sequence | These objects are dependencies, not owned by Purchase |
| Migration project lead | Governs the GlobalPurchase_Project program | Cross-product sequencing and risk oversight |

---

### 1.5 Data Domain and Subject Area

**Primary domain:** Procurement / Purchasing

**Subject area:** Purchase order management — the recording, staging, and warehousing of purchase orders placed by WideWorldImporters with its suppliers for stock items.

**Grain of `fact.purchase`:** One row per purchase order line item, at the day–supplier–stock item level of granularity. The `WWI Purchase Order ID` provides the source-system natural key for order-level aggregation.

**Dimension coverage:**

| Dimension | Table | Role |
|---|---|---|
| Date | `dimension.date` | When the purchase was recorded; FK target `Date Key` |
| Supplier | `dimension.supplier` | Who supplied the goods; SCD-2; resolved by ETL |
| Stock item | `dimension.stock item` | What was purchased; SCD-2; resolved by ETL (note: name contains a space — migration risk) |

All three dimensions are conformed dimensions shared across the WideWorldImportersDW star schema. They are loaded by shared infrastructure ETL outside the Purchase product boundary and are consumed (as read dependencies) by the Purchase ETL procedure.

**Staging layer:** `integration.purchase_staging` holds intermediate purchase update rows extracted from the source OLTP system before surrogate key resolution and fact loading. Its grain mirrors the fact table but uses WWI natural keys in place of DW surrogate keys.

**Control tables in scope (shared infrastructure, consumed by Purchase):**

- `integration.etl cutoff` — stores the last successful incremental cutoff timestamp for each table load
- `integration.lineage` — records one audit row per ETL run per table, with start/end timestamps, success flag, and source cutoff time

---

### 1.6 Key Metrics and KPIs

The following measures are physically present in `fact.purchase` and constitute the product's analytical surface:

| Metric | Column(s) | Definition | Business use |
|---|---|---|---|
| Ordered quantity | `Ordered Quantity` | Number of individual units ordered in a purchase order line | Purchase volume analysis |
| Ordered outers | `Ordered Outers` | Number of outer packs ordered | Logistics and packaging volume |
| Received outers | `Received Outers` | Number of outer packs actually received | Delivery fulfilment tracking |
| Fill rate (outers) | `Received Outers` / `Ordered Outers` | Derived ratio — outers received as a proportion of outers ordered | Supplier performance KPI |
| Open orders | `Is Order Finalized = 0` | Count or share of purchase lines not yet finalized | Open order monitoring |
| Finalized orders | `Is Order Finalized = 1` | Count or share of finalized purchase lines | Order closure rate |
| Purchase order volume | `COUNT(DISTINCT WWI Purchase Order ID)` | Number of distinct purchase orders in scope | Procurement activity volume |
| Lineage coverage | `Lineage Key` | Operational — links each fact row to its ETL run for auditability | Data quality / traceability |

**Note:** There is no `Received Quantity` column — received volume is tracked in outers only. This is a deliberate source-system design choice and will be preserved unless a transformation rule specifies otherwise.

**BI reports consuming these metrics:**

- `wwidw purchase and sale per stockitem dynamic` — aggregates purchase and sale metrics per stock item dynamically
- `wwidw-ordered-by-supplier` — aggregates `Ordered Quantity` / `Ordered Outers` by supplier dimension attributes

---

### 1.7 Operational Context

**Load pattern:** Batch — incremental daily load

**Orchestration:** SSIS master daily ETL workflow (`demo_ssis…pipeline_dailyetlmain`), which includes a "Load Purchase Fact" container. The container executes the following steps in sequence:

| SSIS task | Object ID | Action |
|---|---|---|
| `pipeline_item_set tablename to purchase` | `e630fc7c-26b8-41a1-9701-342991f19c46` | Sets a `TableName` pipeline variable to `Purchase` |
| `pipeline_item_truncate purchase_staging` | `88c761dd-8756-453e-96b2-e587e568b9e3` | **Bug:** Executes `DELETE FROM Integration.Order_Staging` instead of `Integration.Purchase_Staging` |
| `pipeline_item_extract updated purchase data to staging` | `5b1ac205-a17d-4ead-83e7-14d95b112a54` | Loads incremental purchase updates from source OLTP into `integration.purchase_staging` |
| `pipeline_item_migrate staged purchase data` | `9492a03b-5837-41c1-bc25-f00592b94c8c` | Calls `integration.migratestagedpurchasedata` to resolve keys and load `fact.purchase` |

**Incremental strategy:** ETL cutoff watermark — `integration.getlastetlcutofftime` reads the last successful cutoff timestamp from `integration.etl cutoff`. Only rows in the source OLTP system with a `LastEditedWhen` (or equivalent) value after the cutoff are extracted into staging.

**Load pattern in the fact table:** DELETE + INSERT — `migratestagedpurchasedata` deletes existing rows for the affected purchase order IDs from `fact.purchase` and re-inserts them with freshly resolved surrogate keys. This is a full-order-level reload of changed orders, not a pure upsert. In the target platform, this pattern must be replaced with a Delta Lake `MERGE` operation.

**Key operational risks identified:**

1. The SSIS truncate task targets the wrong staging table (`Order_Staging` instead of `Purchase_Staging`) — this is a live bug in the source system.
2. SQL Server `SEQUENCE` objects (used for `Lineage Key` generation via `sequences.lineagekey`) have no direct Databricks equivalent; the lineage key mechanism must be redesigned for the target platform.
3. SCD-2 key resolution for `dimension.supplier` and `dimension.stock item` is performed inside the ETL procedure using correlated subqueries; this logic must be re-implemented in the target platform (likely as Delta Live Tables or Databricks notebooks).

**Operational schedule:** Daily batch. No real-time or streaming ingestion is present in the source system. The target Databricks workflow will replicate the daily batch cadence unless a streaming ingestion pattern is adopted as a transformation decision.

**Reset / seed utility:** `application.configuration_reseedetl` is a warehouse-wide reset procedure with Purchase-specific portions: it truncates `fact.purchase` and resets sentinel rows (key=0 Unknown rows required by the `COALESCE` fallback in `migratestagedpurchasedata`). This utility must be accounted for in the target platform's initialisation and testing workflows.

---

## 2. Consumers

### 2.1 Consumer Inventory

MCP lineage traversal (`traverse-lineage` downstream from `fact.purchase`, id `197f0cba-80b1-4837-b448-3268bdf6649c`) and relation queries confirm five objects that hold an edge to `fact.purchase`. Two are READ consumers (BI reports), one is a READ consumer with cross-domain ownership (analytical view), and two hold MODIFY edges (ETL loader and maintenance procedure — not downstream consumers in the business sense).

| Consumer | Object ID | Node Type | Relation | Ownership | Criticality |
|---|---|---|---|---|---|
| `wwidw purchase and sale per stockitem dynamic` | `8db5c99c-6f81-4021-95ff-5b33f9f1af5b` | BI Report | READ | Purchase-owned | High — primary purchase + sales performance report |
| `wwidw-ordered-by-supplier` | `f8751a7d-43dc-4fb2-be8e-c7b64774469c` | BI Report | READ | Purchase-owned | High — primary supplier-facing purchase report |
| `analytics.v_ordertoyearanalytics` | `b942748e-163b-4919-92de-fd51f4ba2d52` | Analytical View (SQL Server) | READ | Cross-domain (Order-driven) | Medium — out-of-scope for Purchase; coordination with Order product required |
| `integration.migratestagedpurchasedata` | `b79b9b8c-99af-4d42-8e97-e9206b8d5f02` | Stored Procedure (ETL) | MODIFY (write) | Purchase ETL — upstream loader, not a consumer | N/A |
| `application.configuration_reseedetl` | `fe4d64b7-b146-4b4f-8495-fd7f770e0961` | Stored Procedure (Admin) | MODIFY (TRUNCATE) | DBA / admin maintenance | Low — dev/reset utility only |

**Consumer count by type:**
- BI Reports (Purchase-owned): 2
- Analytical Views (cross-domain, out-of-scope): 1
- Admin / maintenance procedures touching `fact.purchase`: 1 (not a downstream consumer)

---

### 2.2 BI Reports

#### 2.2.1 `wwidw purchase and sale per stockitem dynamic`

| Attribute | Value |
|---|---|
| Full name | `wwidw purchase and sale per stockitem dynamic.wwidw purchase and sale per stockitem dynamic` |
| Object ID | `8db5c99c-6f81-4021-95ff-5b33f9f1af5b` |
| Node type | report |
| Tables read (MCP `explore-neighbors`) | `fact.purchase`, `fact.sale`, `dimension.stock item`, `dimension.date` |
| Source code available | No (report definition not stored in lineage graph) |

**Data consumed from this product:** `fact.purchase` (all purchase order lines) and `dimension.stock item` (stock item attributes including product name, colour, brand, size, tax rate, unit price, package type).

**Cross-domain data read:** Also reads `fact.sale` — this report is inherently cross-domain (purchase vs. sales comparison) even though `fact.purchase` is the primary subject and it is listed as a Purchase-owned downstream.

**Inferred business purpose:** Side-by-side comparison of quantities purchased versus quantities sold for each stock item. Likely used to analyse stock item procurement performance, identify over- or under-purchased items, and support inventory/buying decisions. The "dynamic" qualifier in the name suggests a parameterised or pivot-style layout where the user can select the period or product group at runtime.

**Typical users (inferred from naming and domain):** Procurement managers, inventory planners, category buyers.

**Refresh frequency:** The ETL feeding `fact.purchase` runs daily (SSIS batch `migratestagedpurchasedata`). Report data is therefore current to the previous business day at most.

---

#### 2.2.2 `wwidw-ordered-by-supplier`

| Attribute | Value |
|---|---|
| Full name | `wwidw-ordered-by-supplier.wwidw-ordered-by-supplier` |
| Object ID | `f8751a7d-43dc-4fb2-be8e-c7b64774469c` |
| Node type | report |
| Tables read (MCP `explore-neighbors`) | `fact.purchase`, `dimension.supplier`, `dimension.date` |
| Source code available | No (report definition not stored in lineage graph) |

**Data consumed from this product:** `fact.purchase` (purchase order lines including quantity, unit price, package type, lineage key) and `dimension.supplier` (supplier name, category, primary contact, supplier reference, payment days, postal code, SCD validity window).

**Business purpose:** Aggregated view of purchase order activity segmented by supplier. Likely answers questions such as: Which suppliers account for the highest order volumes? What is the trend in orders placed per supplier over a given period? Are there seasonal patterns in supplier ordering?

**Typical users (inferred):** Procurement managers, supplier relationship managers, finance analysts reviewing payables.

**Refresh frequency:** Same daily SSIS batch cycle as above.

---

### 2.3 Analytical Views

#### 2.3.1 `analytics.v_ordertoyearanalytics` — Cross-Domain View (Out-of-Scope)

| Attribute | Value |
|---|---|
| Object ID | `b942748e-163b-4919-92de-fd51f4ba2d52` |
| Schema | `analytics` (WideWorldImportersDW) |
| Node type | view |
| Primary driving table | `fact.order` (INNER JOIN — the driving fact) |
| Tables read | `fact.order`, `fact.purchase`, `fact.sale`, `dimension.customer`, `dimension.date` (order date, picked date), `dimension.employee` |
| Ownership | Cross-domain — driven by Order product; out-of-scope for Purchase |

**How `fact.purchase` is consumed:**

```sql
(select string_agg(Order_Purch, '\')
 from (
     select top 5 p.[Stock Item Key] Order_Purch
     from Fact.Purchase p
     where fo.Package = p.Package
 ) p
 where p.Order_Purch < fo.[Stock Item Key]
) as ORDER_ID_PURCH
```

The dependency is a correlated subquery in the SELECT list, not a JOIN in the FROM clause. For each order row (`fo`), it looks up the top 5 `Stock Item Key` values from `fact.purchase` where the `Package` column matches the order's `Package` value, then filters to stock item keys less than the order's own stock item key, and string-aggregates the results into `ORDER_ID_PURCH`. This is a weak, package-code-based correlation, not a primary key join.

**Implication for Purchase migration:** Because the join predicate is `fo.Package = p.Package` (a free-text packaging descriptor, not a surrogate key), this correlated subquery will survive a schema or column rename provided the `Package` column is preserved in the migrated `fact.purchase` Delta table with the same name and data type. However, because the view is driven by `fact.order` and joins across multiple domains, it cannot be rebuilt solely by the Purchase product team.

---

### 2.4 Consumption Patterns

**Direct table reads:** Both BI reports access `fact.purchase` directly (no intermediate views), confirmed by MCP `explore-neighbors` results. There is no semantic layer (e.g., Analysis Services cube) captured in the lineage graph between the reports and the base tables.

**Implied access pattern for `wwidw purchase and sale per stockitem dynamic`:** Likely aggregates on `[Stock Item Key]` with time-period filters using `dimension.date`. Joins `fact.purchase` and `fact.sale` on `[Stock Item Key]` (and possibly `[Date Key]`) to compare purchase vs. sales quantities and values per stock item.

**Implied access pattern for `wwidw-ordered-by-supplier`:** Likely aggregates on `[Supplier Key]` with date filters. Joins `fact.purchase` to `dimension.supplier` on `[Supplier Key]` and to `dimension.date` on `[Date Key]`.

**Correlated subquery access (analytics view):** `analytics.v_ordertoyearanalytics` accesses `fact.purchase` via a correlated subquery using `Package` as the join key. This pattern will break if `Package` is renamed or its data type changes in the migrated schema.

**Maintenance procedure access:** `application.configuration_reseedetl` issues a `TRUNCATE TABLE Fact.Purchase` statement. This is a developer/DBA reset utility — not a business consumer and should not be migrated as a downstream dependency.

---

### 2.5 Migration Impact on Consumers

| Consumer | Impact | Detail |
|---|---|---|
| `wwidw purchase and sale per stockitem dynamic` | **Connection string change required** | Report must be retargeted from SQL Server 2014 `WideWorldImportersDW` to the Databricks Delta Lake endpoint. |
| `wwidw purchase and sale per stockitem dynamic` | **Cross-domain dependency** | Report also reads `fact.sale`. Migration cannot complete until both Purchase and Sale products are on Databricks. |
| `wwidw-ordered-by-supplier` | **Connection string change required** | Simpler — only touches Purchase domain tables. Can be reconnected as soon as Purchase goes live on Databricks. |
| `analytics.v_ordertoyearanalytics` | **Cross-domain, out-of-scope** | Must be rebuilt when both Purchase and Order products have migrated. If `Package` is renamed, the view's predicate must be updated. Owned by Order product team. |
| `application.configuration_reseedetl` | **Do not migrate** | Dev/reseed utility. Equivalent functionality on Databricks (if needed) would be a notebook or script. |

**Schema and naming considerations:**
- If the target Databricks schema uses a unified catalog namespace (e.g., `<catalog>.<schema>.purchase_fact`), all consumer SQL and connection strings must be updated accordingly.
- The `Package` column must be preserved with its current name and type to avoid breaking the `analytics.v_ordertoyearanalytics` correlated subquery.

---

### 2.6 Consumer Priority for Migration

| Priority | Consumer | Rationale |
|---|---|---|
| 1 | `wwidw-ordered-by-supplier` | Purchase-only consumer; no cross-domain blockers. High business value for procurement reporting. Primary go-live acceptance criterion. |
| 2 | `wwidw purchase and sale per stockitem dynamic` | High business value, but blocked until `fact.sale` (Sale product) is also migrated. Cross-product dependency item. |
| 3 | `analytics.v_ordertoyearanalytics` | Out-of-scope for Purchase; migration responsibility lies with the Order product team. |
| — | `application.configuration_reseedetl` | Not a business consumer. Decommission when SQL Server source is retired. |

---

## 3. Model

### 3.1 Model Overview

The Purchase data product is structured as a **classic star schema** hosted in the `WideWorldImportersDW` database on SQL Server 2014. The schema is organized across three SQL Server schemas: `Fact`, `Dimension`, and `Integration`, with a shared `Sequences` schema for surrogate key generation.

| Layer | Schema | Object Count | Notes |
|---|---|---|---|
| Fact | `Fact` | 1 table | Central fact table |
| Conformed Dimensions | `Dimension` | 3 tables | supplier, stock item, date |
| Staging / Integration | `Integration` | 3 tables | purchase_staging, etl_cutoff, lineage |
| Sequences | `Sequences` | 3+ sequences | SupplierKey, StockItemKey, LineageKey (and others) |

**Total in-scope tables: 7**

The model follows a **single-level star schema** — there is no snowflaking. The fact table references dimensions directly via integer surrogate keys (`Supplier Key`, `Stock Item Key`) and a date natural key (`Date Key` as `date` type). Two of the three dimensions implement **SCD Type 2** (supplier, stock item) using `Valid From` / `Valid To` `datetime2` columns; the date dimension is a static reference table.

---

### 3.2 Fact Table: fact.purchase

#### DDL (as retrieved)

```sql
CREATE TABLE WideWorldImportersDW.Fact.Purchase (
    [Purchase Key]          bigint IDENTITY(1,1) NOT NULL,
    [Date Key]              date NOT NULL,
    [Supplier Key]          int NOT NULL,
    [Stock Item Key]        int NOT NULL,
    [WWI Purchase Order ID] int NULL,
    [Ordered Outers]        int NOT NULL,
    [Ordered Quantity]      int NOT NULL,
    [Received Outers]       int NOT NULL,
    [Package]               nvarchar(100) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Is Order Finalized]    bit NOT NULL,
    [Lineage Key]           int NOT NULL
    ,CONSTRAINT PK_Fact_Purchase PRIMARY KEY ([Purchase Key], [Date Key])
    ,CONSTRAINT FK_Fact_Purchase_Date_Key_Dimension_Date
        FOREIGN KEY ([Date Key]) REFERENCES Dimension.Date([Date])
    ,CONSTRAINT FK_Fact_Purchase_Stock_Item_Key_Dimension_Stock Item
        FOREIGN KEY ([Stock Item Key]) REFERENCES Dimension.[Stock Item]([Stock Item Key])
    ,CONSTRAINT FK_Fact_Purchase_Supplier_Key_Dimension_Supplier
        FOREIGN KEY ([Supplier Key]) REFERENCES Dimension.Supplier([Supplier Key])
);
```

#### Column inventory

| Column | Data Type | Nullable | Constraint / Notes |
|---|---|---|---|
| `Purchase Key` | bigint | NOT NULL | IDENTITY(1,1); part of composite PK |
| `Date Key` | date | NOT NULL | Part of composite PK; FK → `Dimension.Date(Date)` |
| `Supplier Key` | int | NOT NULL | FK → `Dimension.Supplier(Supplier Key)` |
| `Stock Item Key` | int | NOT NULL | FK → `Dimension.[Stock Item](Stock Item Key)` |
| `WWI Purchase Order ID` | int | NULL | Source system purchase order reference; no FK constraint |
| `Ordered Outers` | int | NOT NULL | Quantity ordered in outer packaging units |
| `Ordered Quantity` | int | NOT NULL | Total individual units ordered |
| `Received Outers` | int | NOT NULL | Quantity received in outer units |
| `Package` | nvarchar(100) | NOT NULL | Collation: Latin1_General_100_CI_AS |
| `Is Order Finalized` | bit | NOT NULL | Boolean flag; 1 = finalized |
| `Lineage Key` | int | NOT NULL | FK-by-convention → `Integration.Lineage(Lineage Key)`; no declared constraint |

**Column count: 11**

#### Key structure

| Constraint | Columns | Type |
|---|---|---|
| `PK_Fact_Purchase` | `(Purchase Key, Date Key)` | Composite clustered primary key |

The primary key is **composite**, pairing the IDENTITY surrogate (`Purchase Key`) with `Date Key`. This is atypical for a fact table. Databricks Delta Lake does not enforce primary keys, so the composite uniqueness guarantee must be enforced at the ETL layer.

**Row grain:** One row = one purchase order line item for one supplier/stock item combination on one calendar date.

#### Foreign keys declared

| Constraint Name | Column | References |
|---|---|---|
| `FK_Fact_Purchase_Date_Key_Dimension_Date` | `Date Key` | `Dimension.Date(Date)` |
| `FK_Fact_Purchase_Stock_Item_Key_Dimension_Stock Item` | `Stock Item Key` | `Dimension.[Stock Item](Stock Item Key)` |
| `FK_Fact_Purchase_Supplier_Key_Dimension_Supplier` | `Supplier Key` | `Dimension.Supplier(Supplier Key)` |

**FK join note — date dimension:** The foreign key references `Dimension.Date(Date)` — the **natural date key** of type `date`, not an integer surrogate. `fact.purchase.Date Key` is also of type `date`.

---

### 3.3 Dimension Tables

#### 3.3.1 dimension.supplier

**DDL (as retrieved):**

```sql
CREATE TABLE WideWorldImportersDW.Dimension.Supplier (
    [Supplier Key]      int DEFAULT (NEXT VALUE FOR [Sequences].[SupplierKey]) NOT NULL,
    [WWI Supplier ID]   int NOT NULL,
    [Supplier]          nvarchar(200) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Category]          nvarchar(100) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Primary Contact]   nvarchar(100) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Supplier Reference] nvarchar(40) COLLATE Latin1_General_100_CI_AS NULL,
    [Payment Days]      int NOT NULL,
    [Postal Code]       nvarchar(20) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Valid From]        datetime2 NOT NULL,
    [Valid To]          datetime2 NOT NULL,
    [Lineage Key]       int NOT NULL
    ,CONSTRAINT PK_Dimension_Supplier PRIMARY KEY ([Supplier Key])
);
```

**Column inventory:**

| Column | Data Type | Nullable | Notes |
|---|---|---|---|
| `Supplier Key` | int | NOT NULL | Surrogate PK; DEFAULT = `NEXT VALUE FOR [Sequences].[SupplierKey]` |
| `WWI Supplier ID` | int | NOT NULL | Natural key from source OLTP system |
| `Supplier` | nvarchar(200) | NOT NULL | Supplier name |
| `Category` | nvarchar(100) | NOT NULL | Supplier category |
| `Primary Contact` | nvarchar(100) | NOT NULL | Contact name |
| `Supplier Reference` | nvarchar(40) | NULL | External reference code |
| `Payment Days` | int | NOT NULL | Standard payment terms (days) |
| `Postal Code` | nvarchar(20) | NOT NULL | Delivery/billing postal code |
| `Valid From` | datetime2 | NOT NULL | SCD-2 effective start timestamp |
| `Valid To` | datetime2 | NOT NULL | SCD-2 effective end timestamp (9999-12-31 = current) |
| `Lineage Key` | int | NOT NULL | ETL run reference |

**Column count: 11. SCD strategy: Type 2.** Active row identified by `Valid To = '9999-12-31 23:59:59.9999999'`. Surrogate key generated by `NEXT VALUE FOR [Sequences].[SupplierKey]` — supports explicit `key=0` Unknown sentinel row insertion.

---

#### 3.3.2 dimension.stock item

**DDL (as retrieved):**

```sql
CREATE TABLE WideWorldImportersDW.Dimension.[Stock Item] (
    [Stock Item Key]            int DEFAULT (NEXT VALUE FOR [Sequences].[StockItemKey]) NOT NULL,
    [WWI Stock Item ID]         int NOT NULL,
    [Stock Item]                nvarchar(200) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Color]                     nvarchar(40) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Selling Package]           nvarchar(100) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Buying Package]            nvarchar(100) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Brand]                     nvarchar(100) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Size]                      nvarchar(40) COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Lead Time Days]            int NOT NULL,
    [Quantity Per Outer]        int NOT NULL,
    [Is Chiller Stock]          bit NOT NULL,
    [Barcode]                   nvarchar(100) COLLATE Latin1_General_100_CI_AS NULL,
    [Tax Rate]                  decimal(18,3) NOT NULL,
    [Unit Price]                decimal(18,2) NOT NULL,
    [Recommended Retail Price]  decimal(18,2) NULL,
    [Typical Weight Per Unit]   decimal(18,3) NOT NULL,
    [Photo]                     varbinary NULL,
    [Valid From]                datetime2 NOT NULL,
    [Valid To]                  datetime2 NOT NULL,
    [Lineage Key]               int NOT NULL
    ,CONSTRAINT PK_Dimension_Stock_Item PRIMARY KEY ([Stock Item Key])
);
```

**Column count: 20. SCD strategy: Type 2.**

**Notable issues:**
- **Table name contains a space**: `Dimension.[Stock Item]` — requires bracket quoting throughout T-SQL; must be renamed to `dim_stock_item` (snake_case) on Databricks.
- **`Photo` column**: declared as `varbinary` with no length — resolves to `varbinary(1)` in SQL Server. Must be evaluated for inclusion (drop, externalize to object storage, or convert to Base64 string).

---

#### 3.3.3 dimension.date

**Structure summary (62 columns):**

| Column group | Count | Purpose |
|---|---|---|
| Natural date key | 1 | `Date` (date) — PK and FK target |
| Integer day/week/month keys | 15+ | `DateKey`, `Year Week Key`, `Year Month Key`, etc. |
| Calendar label strings | 20+ | Human-readable period labels (nvarchar) |
| Period boundary dates | 4 | `Beginning of Month/Quarter/Half Year/Year` (date) |
| Calendar period numbers | 6 | `Calendar Week/Month/Quarter/Half of Year/Year Number` |
| Fiscal period numbers | 5 | `Fiscal Month/Quarter/Half of Year/Year Number` |
| ISO week | 1 | `ISO Week Number` |

**SCD strategy: None (static reference table).** Pre-populated for a fixed date range; no incremental updates. The natural `Date` column is both PK and FK target.

**Key anomaly:** `fact.purchase` joins to `dimension.date` using `Date Key date` (a `date`-typed column) referencing `Dimension.Date(Date)`. `dimension.date` also has an integer column named `DateKey` (no space) and `Date Key` (with space) — neither of these integers is the FK target. The `date`-typed `Date` column is the reference point.

---

### 3.4 Staging Tables

#### 3.4.1 integration.purchase_staging

**DDL (as retrieved):**

```sql
CREATE TABLE WideWorldImportersDW.Integration.Purchase_Staging (
    [Purchase Staging Key] bigint IDENTITY(1,1) NOT NULL,
    [Date Key]             date NULL,
    [Supplier Key]         int NULL,
    [Stock Item Key]       int NULL,
    [WWI Purchase Order ID] int NULL,
    [Ordered Outers]       int NULL,
    [Ordered Quantity]     int NULL,
    [Received Outers]      int NULL,
    [Package]              nvarchar(100) COLLATE Latin1_General_100_CI_AS NULL,
    [Is Order Finalized]   bit NULL,
    [WWI Supplier ID]      int NULL,
    [WWI Stock Item ID]    int NULL,
    [Last Modified When]   datetime2 NULL
    ,CONSTRAINT PK_Integration_Purchase_Staging PRIMARY KEY ([Purchase Staging Key])
);
```

**Column count: 13.** All payload columns nullable. Contains both resolved surrogate keys (`Supplier Key`, `Stock Item Key` — NULL on arrival, resolved in-place) and source natural keys (`WWI Supplier ID`, `WWI Stock Item ID`). Truncated each ETL run.

---

#### 3.4.2 integration.etl_cutoff

```sql
CREATE TABLE WideWorldImportersDW.Integration.[ETL Cutoff] (
    [Table Name]   sysname COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Cutoff Time]  datetime2 NOT NULL
    ,CONSTRAINT PK_Integration_ETL_Cutoff PRIMARY KEY ([Table Name])
);
```

**Column count: 2.** ETL watermark registry. Each row records the maximum source-system timestamp processed for a given target table. Shared infrastructure — used by all ETL flows.

---

#### 3.4.3 integration.lineage

```sql
CREATE TABLE WideWorldImportersDW.Integration.Lineage (
    [Lineage Key]              int DEFAULT (NEXT VALUE FOR [Sequences].[LineageKey]) NOT NULL,
    [Data Load Started]        datetime2 NOT NULL,
    [Table Name]               sysname COLLATE Latin1_General_100_CI_AS NOT NULL,
    [Data Load Completed]      datetime2 NULL,
    [Was Successful]           bit NOT NULL,
    [Source System Cutoff Time] datetime2 NOT NULL
    ,CONSTRAINT PK_Integration_Lineage PRIMARY KEY ([Lineage Key])
);
```

**Column count: 6.** ETL run audit log. Each ETL run inserts a row at start (with `Data Load Completed = NULL`), executes the load, then updates the row on completion with end timestamp and success flag. The `Lineage Key` is stamped onto every row written to fact and dimension tables.

---

### 3.5 Sequences

T-SQL `SEQUENCE` objects in the `Sequences` schema provide surrogate key generation for dimension tables and the lineage audit table.

| Sequence | Referenced By | Purpose |
|---|---|---|
| `[Sequences].[SupplierKey]` | `Dimension.Supplier(Supplier Key)` DEFAULT | Generates int surrogate keys for the supplier dimension |
| `[Sequences].[StockItemKey]` | `Dimension.[Stock Item](Stock Item Key)` DEFAULT | Generates int surrogate keys for the stock item dimension |
| `[Sequences].[LineageKey]` | `Integration.Lineage(Lineage Key)` DEFAULT | Generates int keys for ETL run audit rows |

**Migration challenge:** Databricks has no native SEQUENCE object equivalent. The `key=0` sentinel requirement means whichever approach is chosen must allow explicit insertion of `key=0` rows, ruling out strict auto-generated IDENTITY semantics without workarounds.

---

### 3.6 Relationships and Foreign Keys

**Declared FK constraints in fact.purchase:**

| Constraint | From Column | To Table | To Column | Enforcement |
|---|---|---|---|---|
| `FK_Fact_Purchase_Date_Key_Dimension_Date` | `[Date Key]` (date) | `Dimension.Date` | `[Date]` (date) | Enforced in SQL Server (trusted) |
| `FK_Fact_Purchase_Stock_Item_Key_Dimension_Stock Item` | `[Stock Item Key]` (int) | `Dimension.[Stock Item]` | `[Stock Item Key]` (int) | Enforced in SQL Server (trusted) |
| `FK_Fact_Purchase_Supplier_Key_Dimension_Supplier` | `[Supplier Key]` (int) | `Dimension.Supplier` | `[Supplier Key]` (int) | Enforced in SQL Server (trusted) |

**Logical FKs (undeclared):** `fact.purchase.[Lineage Key]` → `Integration.Lineage.[Lineage Key]` (no FK constraint declared).

**Typical analytical join pattern:**

```sql
SELECT
    d.[Calendar Year],
    s.[Supplier],
    si.[Stock Item],
    SUM(fp.[Ordered Quantity]) AS TotalOrdered
FROM Fact.Purchase fp
JOIN Dimension.Date d ON fp.[Date Key] = d.[Date]
JOIN Dimension.Supplier s ON fp.[Supplier Key] = s.[Supplier Key]
    AND fp.[Date Key] BETWEEN s.[Valid From] AND s.[Valid To]
JOIN Dimension.[Stock Item] si ON fp.[Stock Item Key] = si.[Stock Item Key]
    AND fp.[Date Key] BETWEEN si.[Valid From] AND si.[Valid To]
GROUP BY d.[Calendar Year], s.[Supplier], si.[Stock Item];
```

---

### 3.7 Notable Schema Issues

| # | Issue | Affected Object | Severity | Details |
|---|---|---|---|---|
| 1 | **Table name contains a space** | `Dimension.[Stock Item]` | High | Requires bracket quoting in all T-SQL; must be renamed to `dim_stock_item` on Databricks. All ETL, SSIS packages, reports, and stored procedures referencing this object must be updated. |
| 2 | **Composite PK on fact table** | `fact.purchase` | High | PK is `(Purchase Key, Date Key)` — IDENTITY + date FK. Delta Lake does not enforce PKs; uniqueness invariant must be validated at ETL time. |
| 3 | **`Photo` column declared as `varbinary` (no length)** | `Dimension.[Stock Item]` | Medium | Resolves to `varbinary(1)` — only 1 byte. If unused, drop in target; if needed, re-declare as `varbinary(max)` or store externally. |
| 4 | **Date FK joins on `date` type, not integer** | `fact.purchase` → `dimension.date` | Medium | FK target is the `date`-typed `Date` column, not the integer `DateKey` or `Date Key` columns. Naming ambiguity requires careful mapping. |
| 5 | **`ETL Cutoff` table name contains a space** | `Integration.[ETL Cutoff]` | Medium | Requires bracket quoting and renaming in target platform. |
| 6 | **Sequences have no Databricks equivalent** | All dimension + lineage tables | Medium | Three sequence objects drive surrogate key generation. Re-implementation required. |
| 7 | **Collation: Latin1_General_100_CI_AS** | All nvarchar columns | Low | Special characters in Latin-1 extended range must be validated during migration. |
| 8 | **`sysname` data type** | `Integration.[ETL Cutoff]`, `Integration.Lineage` | Low | SQL Server system alias for `nvarchar(128) NOT NULL`; must be mapped to `STRING` or `VARCHAR(128)` on Databricks. |

---

### 3.8 Schema Diagram

```
                    ┌──────────────────────────────┐
                    │    Dimension.Date             │
                    │  PK: Date (date)              │
                    │  (62 columns — static ref)    │
                    └──────────────┬───────────────┘
                                   │ FK: Date Key → Date
                                   │
 ┌────────────────────────┐        │       ┌──────────────────────────────┐
 │  Dimension.Supplier    │        │       │  Dimension.[Stock Item]      │
 │  PK: Supplier Key(int) │        │       │  PK: Stock Item Key (int)   │
 │  NK: WWI Supplier ID   │        │       │  NK: WWI Stock Item ID      │
 │  SCD-2: Valid From/To  │        │       │  SCD-2: Valid From/To       │
 │  Key gen: SupplierKey  │        │       │  Key gen: StockItemKey      │
 │  sequence              │        │       │  sequence                   │
 └───────────┬────────────┘        │       └──────────────┬──────────────┘
             │ FK: Supplier Key    │              FK: Stock Item Key │
             │                    ▼                                  │
             │       ┌────────────────────────────┐                 │
             └──────►│      Fact.Purchase          │◄────────────────┘
                     │  PK: (Purchase Key,         │
                     │       Date Key)             │
                     │  Purchase Key: bigint       │
                     │    IDENTITY(1,1)            │
                     │  Date Key: date             │
                     │  Supplier Key: int          │
                     │  Stock Item Key: int        │
                     │  WWI Purchase Order ID: int │
                     │  Ordered Outers: int        │
                     │  Ordered Quantity: int      │
                     │  Received Outers: int       │
                     │  Package: nvarchar(100)     │
                     │  Is Order Finalized: bit    │
                     │  Lineage Key: int ──────────┼────────────────────┐
                     └────────────────────────────┘                    │
                                                                        ▼
 ┌────────────────────────────────────┐   ┌────────────────────────────────────┐
 │  Integration.Purchase_Staging      │   │  Integration.Lineage               │
 │  PK: Purchase Staging Key (bigint) │   │  PK: Lineage Key (int)             │
 │  IDENTITY(1,1)                     │   │  Key gen: LineageKey sequence      │
 │  All payload columns nullable      │   │  Data Load Started: datetime2      │
 │  WWI Supplier ID: int (NK lookup)  │   │  Table Name: sysname               │
 │  WWI Stock Item ID: int (NK lookup)│   │  Data Load Completed: datetime2    │
 │  Last Modified When: datetime2     │   │  Was Successful: bit               │
 │  (truncated each ETL run)          │   │  Source System Cutoff Time: dt2    │
 └────────────────────────────────────┘   └────────────────────────────────────┘

 ┌────────────────────────────────────┐
 │  Integration.[ETL Cutoff]          │
 │  PK: Table Name (sysname)          │
 │  Cutoff Time: datetime2            │
 │  (one row per target table)        │
 └────────────────────────────────────┘
```

---

## 4. Lineage

### 4.1 Lineage Overview

The Purchase data product follows a classic incremental-extract ETL pattern spanning two SQL Server databases and one SSIS orchestration layer. Data originates in the **WideWorldImporters OLTP** database (`wideworldimporters`), flows through an integration staging area, and lands in the **WideWorldImportersDW** data warehouse (`wideworldimportersdw`) as `fact.purchase`. From there it is consumed by one analytics view and two BI reports.

**End-to-end hop count: 6 hops from OLTP source tables to fact table.**

```
OLTP tables (4)
    → [Hop 1] getpurchaseupdates (extraction procedure, OLTP side)
    → [Hop 2] pipeline_item_extract updated purchase data to staging (SSIS dataflow)
    → [Hop 3] integration.purchase_staging (DW staging table)
    → [Hop 4] pipeline_item_migrate staged purchase data (SSIS dataflow)
    → [Hop 5] integration.migratestagedpurchasedata (DW ETL procedure)
    → [Hop 6] fact.purchase (DW fact table)
         → v_ordertoyearanalytics, wwidw-ordered-by-supplier, wwidw purchase and sale per stockitem dynamic
```

---

### 4.2 Upstream Lineage

#### Layer 1 — OLTP Source Tables (`wideworldimporters` database)

| Table | Schema | Role in extraction |
|---|---|---|
| `wideworldimporters.purchasing.purchaseorders` | Purchasing | Purchase order header; supplies `PurchaseOrderID`, `OrderDate`, `SupplierID`, `LastEditedWhen` |
| `wideworldimporters.purchasing.purchaseorderlines` | Purchasing | Line items; supplies `StockItemID`, `PackageTypeID`, `OrderedOuters`, `ReceivedOuters`, `IsOrderLineFinalized`, `LastEditedWhen` |
| `wideworldimporters.warehouse.stockitems` | Warehouse | Reference for `QuantityPerOuter` used to derive `[Ordered Quantity]` |
| `wideworldimporters.warehouse.packagetypes` | Warehouse | Reference for `PackageTypeName` mapped to `Package` column |

#### Layer 2 — Source Extraction Procedure

**`wideworldimporters.integration.getpurchaseupdates`** (id: `4ea8c05f-2fd5-4882-8910-6272bc94670d`)

Accepts `@LastCutoff datetime2(7)` and `@NewCutoff datetime2(7)`. The incremental filter uses `CASE WHEN pol.LastEditedWhen > po.LastEditedWhen THEN pol.LastEditedWhen ELSE po.LastEditedWhen END` — the later of the header or line modification timestamp. Any change to either the order header or any line will re-extract all lines for that order within the cutoff window.

Key output column: `[Ordered Quantity] = pol.OrderedOuters * si.QuantityPerOuter` — the only derived measure computed at extraction time.

#### Layer 3 — SSIS Extract Dataflow

**`pipeline_item_extract updated purchase data to staging`** (id: `5b1ac205-a17d-4ead-83e7-14d95b112a54`) — calls `getpurchaseupdates` and loads the result into `integration.purchase_staging`.

#### Layer 4 — Integration Staging Table

**`wideworldimportersdw.integration.purchase_staging`** (id: `a016e5b7-ab70-4e45-af51-b70ae237c7e2`) — holds extracted rows transiently. `Supplier Key` and `Stock Item Key` are NULL on arrival; resolved in-place by `migratestagedpurchasedata`.

#### Layer 5 — SSIS Migrate Dataflow

**`pipeline_item_migrate staged purchase data`** (id: `9492a03b-5837-41c1-bc25-f00592b94c8c`) — calls `migratestagedpurchasedata`.

#### Layer 6 — Core ETL Procedure

**`wideworldimportersdw.integration.migratestagedpurchasedata`** (id: `b79b9b8c-99af-4d42-8e97-e9206b8d5f02`) — full step-by-step in Section 4.3.

#### Layer 7 — Fact Table

**`wideworldimportersdw.fact.purchase`** (id: `197f0cba-80b1-4837-b448-3268bdf6649c`)

---

### 4.3 ETL Transformation Steps (migratestagedpurchasedata)

The procedure executes with `EXECUTE AS OWNER` inside a single `BEGIN TRAN / COMMIT` block with `XACT_ABORT ON`.

**Step 1 — Acquire Lineage Key:**
```sql
DECLARE @LineageKey int = (
    SELECT TOP(1) [Lineage Key]
    FROM Integration.Lineage
    WHERE [Table Name] = N'Purchase'
      AND [Data Load Completed] IS NULL
    ORDER BY [Lineage Key] DESC
);
```

**Step 2 — Resolve Supplier Surrogate Key (SCD-2 Lookup):**
```sql
UPDATE p
    SET p.[Supplier Key] = COALESCE((
        SELECT TOP(1) s.[Supplier Key]
        FROM Dimension.Supplier AS s
        WHERE s.[WWI Supplier ID] = p.[WWI Supplier ID]
          AND p.[Last Modified When] > s.[Valid From]
          AND p.[Last Modified When] <= s.[Valid To]
        ORDER BY s.[Valid From]), 0)
FROM Integration.Purchase_Staging AS p;
```

**Step 3 — Resolve Stock Item Surrogate Key (SCD-2 Lookup):** Same pattern against `Dimension.[Stock Item]`.

**Step 4 — Delete Existing Fact Rows:**
```sql
DELETE p
FROM Fact.Purchase AS p
WHERE p.[WWI Purchase Order ID] IN (
    SELECT [WWI Purchase Order ID] FROM Integration.Purchase_Staging
);
```

**Step 5 — Insert Current Data:**
```sql
INSERT Fact.Purchase
    ([Date Key], [Supplier Key], [Stock Item Key], [WWI Purchase Order ID],
     [Ordered Outers], [Ordered Quantity], [Received Outers], Package,
     [Is Order Finalized], [Lineage Key])
SELECT [Date Key], [Supplier Key], [Stock Item Key], [WWI Purchase Order ID],
       [Ordered Outers], [Ordered Quantity], [Received Outers], Package,
       [Is Order Finalized], @LineageKey
FROM Integration.Purchase_Staging;
```

**Step 6 — Mark Lineage Record Complete:**
```sql
UPDATE Integration.Lineage
    SET [Data Load Completed] = SYSDATETIME(), [Was Successful] = 1
WHERE [Lineage Key] = @LineageKey;
```

**Step 7 — Advance ETL Cutoff:**
```sql
UPDATE Integration.[ETL Cutoff]
    SET [Cutoff Time] = (SELECT [Source System Cutoff Time] FROM Integration.Lineage
                         WHERE [Lineage Key] = @LineageKey)
WHERE [Table Name] = N'Purchase';
```

**Step 8 — Commit:** Single `COMMIT` covers all preceding steps; `XACT_ABORT ON` ensures full rollback on any failure.

---

### 4.4 Downstream Lineage

| Object | Type | ID | Usage |
|---|---|---|---|
| `wwidw purchase and sale per stockitem dynamic` | BI Report | `8db5c99c-6f81-4021-95ff-5b33f9f1af5b` | Reads `fact.purchase` for purchase-side metrics in cross-domain purchase-and-sale analysis |
| `wwidw-ordered-by-supplier` | BI Report | `f8751a7d-43dc-4fb2-be8e-c7b64774469c` | Reads `fact.purchase` for supplier ordering analysis |
| `wideworldimportersdw.analytics.v_ordertoyearanalytics` | SQL View | `b942748e-163b-4919-92de-fd51f4ba2d52` | Reads `fact.purchase` via correlated subquery on `Package` column |
| `wideworldimportersdw.application.configuration_reseedetl` | Procedure | `fe4d64b7-b146-4b4f-8495-fd7f770e0961` | Issues `TRUNCATE TABLE Fact.Purchase` — maintenance only |

---

### 4.5 Data Flow Diagram

```
WIDEWORLDIMPORTERS (OLTP — out of scope for migration)
══════════════════════════════════════════════════════

  purchasing.purchaseorders ──────┐
  purchasing.purchaseorderlines ──┤
  warehouse.stockitems ───────────┼──► integration.getpurchaseupdates
  warehouse.packagetypes ─────────┘         │ (incremental extract, cutoff-bounded)
                                            ▼
SSIS ORCHESTRATION LAYER
══════════════════════════════════════════════════════
  pipeline_dailyetlmain (workflow)
    │
    ├──[1]── pipeline_item_set tablename to purchase
    ├──[2]── pipeline_item_truncate purchase_staging
    │              ⚠ BUG: executes DELETE FROM Integration.Order_Staging
    ├──[3]── pipeline_item_extract updated purchase data to staging
    │              │ loads result into integration.purchase_staging
    └──[4]── pipeline_item_migrate staged purchase data
                   │ calls ▼

WIDEWORLDIMPORTERSDW (DW)
══════════════════════════════════════════════════════
  integration.migratestagedpurchasedata
    ├── READ  integration.lineage          → acquire @LineageKey
    ├── READ  dimension.supplier           → SCD-2 surrogate key lookup
    │         UPDATE purchase_staging.[Supplier Key]
    ├── READ  dimension.stock item         → SCD-2 surrogate key lookup
    │         UPDATE purchase_staging.[Stock Item Key]
    ├── DELETE fact.purchase               → remove prior rows for same WWI Purchase Order IDs
    ├── INSERT fact.purchase ◄─────────────── from purchase_staging (stamps @LineageKey)
    ├── UPDATE integration.lineage         → mark Data Load Completed, Was Successful = 1
    └── UPDATE integration.etl cutoff     → advance Cutoff Time for 'Purchase'

                              ▼
  ╔═══════════════════════════════════════════╗
  ║         fact.purchase                     ║
  ╚═══════════════════════════════════════════╝
                    │
      ┌─────────────┼──────────────────────────────────┐
      ▼             ▼                                  ▼
  wwidw-ordered  wwidw purchase and sale        analytics.v_ordertoyearanalytics
  -by-supplier   per stockitem dynamic          (correlated subquery on Package)
  (BI Report)    (BI Report)                   (cross-domain, order analytics view)
```

---

### 4.6 Lineage Dependencies (Cross-Product)

| Dependency | Object | Why required | Failure consequence |
|---|---|---|---|
| Supplier dimension must be current | `dimension.supplier` | SCD-2 time-window lookup uses `[Valid From]`/`[Valid To]` | If supplier ETL has not run, new/changed suppliers yield `[Supplier Key] = 0` (Unknown) in `fact.purchase` |
| Stock item dimension must be current | `dimension.stock item` | Same SCD-2 time-window lookup pattern | If stock item ETL has not run, new/changed stock items yield `[Stock Item Key] = 0` (Unknown) |
| Date dimension must cover all date keys | `dimension.date` | `[Date Key]` in staging is a `date` value; missing dates yield no match in downstream queries | `dimension.date` is static (pre-populated); no ETL dependency, but column type mismatch awareness required |

**ETL ordering constraint:** `pipeline_dailyetlmain` must execute Supplier and Stock Item ETL tasks to completion before the Purchase fact load tasks. Silent `COALESCE(..., 0)` fallback means ordering failures produce no error — only bad data.

---

### 4.7 Shared Infrastructure in Lineage

| Object | Role | Notes |
|---|---|---|
| `integration.lineage` | READ (start) + MODIFY (end) by `migratestagedpurchasedata` | Lineage row must be pre-inserted by SSIS before procedure runs |
| `integration.etl cutoff` | READ (at extract) + MODIFY (at end of migrate) | Cutoff advanced only after successful load |
| `integration.getlastetlcutofftime` | Reads ETL cutoff for given table name | Called before SSIS extract step |
| `integration.getlineagekey` | Inserts open lineage row, returns key | Called by SSIS before migrate step |
| `sequences.lineagekey` | Generates int keys for lineage rows | No native Databricks equivalent |

---

### 4.8 Lineage Graph Anomalies

**Anomaly 1 — SSIS Bug: Wrong Table Truncated (Critical):** `pipeline_item_truncate purchase_staging` (id: `88c761dd-8756-453e-96b2-e587e568b9e3`) executes `DELETE FROM Integration.Order_Staging` instead of `Integration.Purchase_Staging`. As a result, stale rows accumulate in `purchase_staging` across ETL cycles. The DELETE+INSERT pattern provides partial protection for already-loaded order IDs, but stale rows for orders outside the current extract window are silently re-loaded, potentially causing double-counting.

**Anomaly 2 — migratestagedpurchasedata Has MODIFY Relation to purchase_staging:** The UPDATE steps for SCD-2 key resolution alter staging in-place rather than using it as read-only — staging is used as a working area.

**Anomaly 3 — configuration_reseedetl Modifies fact.purchase:** This maintenance procedure (`fe4d64b7`) issues `TRUNCATE TABLE Fact.Purchase` as part of a full DW reseed. Not part of the daily ETL flow, but appears in the lineage graph as a MODIFY relation.

**Anomaly 4 — Cross-Domain Dependency in v_ordertoyearanalytics:** Joins `fact.order` to `fact.purchase` on the string column `Package`. No referential integrity enforces this relationship; consistent package naming between Order and Purchase ETL pipelines is required for correctness.

**Anomaly 5 — Traverse-Lineage Direction Behaviour:** MCP `traverse-lineage` with `direction=upstream` from `fact.purchase` returned the same node set as downstream traversal. Lineage directionality in this section was established through `find-paths` and `explore-neighbors` calls rather than traverse results alone.

---

### 4.9 Migration Lineage Impact

| Area | As-Is | To-Be |
|---|---|---|
| Orchestration | `pipeline_dailyetlmain` SSIS workflow | Databricks Workflow (DAG) with equivalent task ordering |
| Source extraction | SSIS OLE DB call to `getpurchaseupdates` | Databricks native JDBC connector reading four OLTP tables directly |
| Staging | SQL Server `integration.purchase_staging` | Delta Lake staging table; stateless per-run pattern eliminates accumulation bug |
| Core ETL | DELETE + INSERT inside SQL Server transaction | Delta Lake `MERGE INTO` using `[WWI Purchase Order ID]` as merge key, wrapped in Delta ACID transaction |
| SCD-2 key resolution | Correlated UPDATE subqueries inside ETL proc | Pre-join step: broadcast join staging × dimension filtered by validity window, using `ROW_NUMBER()` tiebreaker |
| Lineage/cutoff tables | SQL Server tables updated within ETL transaction | Delta tables with equivalent ACID semantics; or replaced by Databricks workflow run history + Unity Catalog lineage |
| Downstream consumers | BI reports reading SQL Server DW | Re-pointed to Databricks SQL Warehouse endpoint |

---

## 5. Calculations

### 5.1 Calculations Overview

The Purchase data product is **calculation-light at the measure level** but **calculation-heavy at the infrastructure level**. No aggregations, running totals, or complex business metrics are computed within the ETL layer. All measures loaded into `fact.purchase` are passed through verbatim from the OLTP source, with a single multiplicative derived column computed at extraction time.

| Area | Location | Complexity |
|---|---|---|
| SCD-2 surrogate key resolution | `integration.migratestagedpurchasedata` (UPDATE step) | High — correlated subqueries with point-in-time filter |
| Fact load refresh pattern | `integration.migratestagedpurchasedata` (DELETE + INSERT) | High — no idempotency guarantees without sentinel rows |
| Incremental watermark management | `getlastetlcutofftime`, `getlineagekey`, `migratestagedpurchasedata` | Medium — multi-table transaction with inline watermark update |
| Derived measure at extract | `wideworldimporters.integration.getpurchaseupdates` | Low — single multiply |
| Analytical view derivations | `analytics.v_ordertoyearanalytics` | High — fragile cross-domain join on string column, correlated subqueries, date casts |

---

### 5.2 Surrogate Key Resolution (SCD-2 Lookups)

Both `[Supplier Key]` and `[Stock Item Key]` are resolved in `integration.migratestagedpurchasedata` via correlated UPDATE subqueries using a point-in-time lookup against the SCD-2 validity window.

**Supplier Key resolution — exact SQL:**
```sql
UPDATE p
    SET p.[Supplier Key] = COALESCE((SELECT TOP(1) s.[Supplier Key]
                                 FROM Dimension.Supplier AS s
                                 WHERE s.[WWI Supplier ID] = p.[WWI Supplier ID]
                                 AND p.[Last Modified When] > s.[Valid From]
                                 AND p.[Last Modified When] <= s.[Valid To]
                                 ORDER BY s.[Valid From]), 0)
FROM Integration.Purchase_Staging AS p;
```

**Stock Item Key resolution — exact SQL:**
```sql
UPDATE p
    SET p.[Stock Item Key] = COALESCE((SELECT TOP(1) si.[Stock Item Key]
                                       FROM Dimension.[Stock Item] AS si
                                       WHERE si.[WWI Stock Item ID] = p.[WWI Stock Item ID]
                                       AND p.[Last Modified When] > si.[Valid From]
                                       AND p.[Last Modified When] <= si.[Valid To]
                                       ORDER BY si.[Valid From]), 0)
FROM Integration.Purchase_Staging AS p;
```

**Logic details:**
1. Natural key match by `WWI Supplier ID` / `WWI Stock Item ID`.
2. Point-in-time filter: `Last Modified When > Valid From` (exclusive) AND `Last Modified When <= Valid To` (inclusive).
3. Tiebreaker: `TOP(1) ORDER BY Valid From ASC`.
4. `COALESCE(..., 0)` assigns key=0 (Unknown member) when no match found — **silent data quality failure**. Requires `key=0` sentinel rows in both dimension tables.

**Timing constraint:** Both dimension tables must be fully loaded before `migratestagedpurchasedata` runs.

**Migration challenge:** No direct Databricks equivalent. Must decompose into a pre-join step: broadcast join staging × dimension filtered by validity window, using `ROW_NUMBER() OVER (PARTITION BY natural_key ORDER BY valid_from)` with `WHERE rn = 1`. Left join with `COALESCE` on the join output column for the Unknown fallback.

---

### 5.3 Fact Load Pattern: DELETE + INSERT

**DELETE step — exact SQL:**
```sql
DELETE p
FROM Fact.Purchase AS p
WHERE p.[WWI Purchase Order ID] IN (SELECT [WWI Purchase Order ID] FROM Integration.Purchase_Staging);
```

**INSERT step — exact SQL:**
```sql
INSERT Fact.Purchase
    ([Date Key], [Supplier Key], [Stock Item Key], [WWI Purchase Order ID], [Ordered Outers], [Ordered Quantity],
     [Received Outers], Package, [Is Order Finalized], [Lineage Key])
SELECT [Date Key], [Supplier Key], [Stock Item Key], [WWI Purchase Order ID], [Ordered Outers], [Ordered Quantity],
       [Received Outers], Package, [Is Order Finalized], @LineageKey
FROM Integration.Purchase_Staging;
```

**Upsert semantics:** Full-order-replacement — a single changed line item causes all lines of that order to be deleted and re-inserted. No partial line-level update.

**Migration challenge:** Must be rewritten as a two-phase Delta operation or a MERGE paired with explicit deletion of unmatched lines for matched order IDs. Standard MERGE does not handle the deletion of lines absent from staging that previously existed in the fact table.

---

### 5.4 Lineage and Watermark Management

**Lineage key acquisition:** `getlineagekey` inserts a new open lineage row and returns the key. `migratestagedpurchasedata` reads this open row via `TOP(1) WHERE [Data Load Completed] IS NULL ORDER BY [Lineage Key] DESC`.

**Watermark read:** `getlastetlcutofftime` reads `[Cutoff Time]` from `integration.[ETL Cutoff]` for the given `@TableName`.

**Lineage completion stamp:**
```sql
UPDATE Integration.Lineage
    SET [Data Load Completed] = SYSDATETIME(), [Was Successful] = 1
WHERE [Lineage Key] = @LineageKey;
```

**ETL cutoff advancement:**
```sql
UPDATE Integration.[ETL Cutoff]
    SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                         FROM Integration.Lineage
                         WHERE [Lineage Key] = @LineageKey)
WHERE [Table Name] = N'Purchase';
```

**Atomic transaction wrapper:** `SET XACT_ABORT ON; BEGIN TRAN; ... COMMIT;` — all steps atomic; any failure causes complete rollback.

---

### 5.5 Extraction Calculations (getpurchaseupdates)

**Full procedure body:**
```sql
CREATE PROCEDURE Integration.GetPurchaseUpdates
@LastCutoff datetime2(7),
@NewCutoff datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    SELECT CAST(po.OrderDate AS date) AS [Date Key],
           po.PurchaseOrderID AS [WWI Purchase Order ID],
           pol.OrderedOuters AS [Ordered Outers],
           pol.OrderedOuters * si.QuantityPerOuter AS [Ordered Quantity],
           pol.ReceivedOuters AS [Received Outers],
           pt.PackageTypeName AS Package,
           pol.IsOrderLineFinalized AS [Is Order Finalized],
           po.SupplierID AS [WWI Supplier ID],
           pol.StockItemID AS [WWI Stock Item ID],
           CASE WHEN pol.LastEditedWhen > po.LastEditedWhen
                THEN pol.LastEditedWhen
                ELSE po.LastEditedWhen END AS [Last Modified When]
    FROM Purchasing.PurchaseOrders AS po
    INNER JOIN Purchasing.PurchaseOrderLines AS pol
        ON po.PurchaseOrderID = pol.PurchaseOrderID
    INNER JOIN Warehouse.StockItems AS si
        ON pol.StockItemID = si.StockItemID
    INNER JOIN Warehouse.PackageTypes AS pt
        ON pol.PackageTypeID = pt.PackageTypeID
    WHERE CASE WHEN pol.LastEditedWhen > po.LastEditedWhen
               THEN pol.LastEditedWhen
               ELSE po.LastEditedWhen END > @LastCutoff
    AND CASE WHEN pol.LastEditedWhen > po.LastEditedWhen
             THEN pol.LastEditedWhen
             ELSE po.LastEditedWhen END <= @NewCutoff
    ORDER BY po.PurchaseOrderID;
END;
```

**Derived column:** `pol.OrderedOuters * si.QuantityPerOuter AS [Ordered Quantity]` — the only numeric computation. The join to `Warehouse.StockItems` exists solely for this calculation.

**Watermark filter:** `max(pol.LastEditedWhen, po.LastEditedWhen) > @LastCutoff AND <= @NewCutoff`. The CASE expression is evaluated twice per row (no CTE) — minor inefficiency to address in migration.

**Date conversion:** `CAST(po.OrderDate AS date)` — no-op cast on a `date` column, explicit for documentation.

**Migration risk — `QuantityPerOuter` at time of extraction:** `QuantityPerOuter` is read from `StockItems` at the time of the daily batch run, not at the time the purchase order was placed. If the stock item's quantity-per-outer changes between order date and extraction date, `[Ordered Quantity]` reflects the current value, not the historical one. The migration must decide whether to preserve this behavior or correct it using a point-in-time lookup.

---

### 5.6 Analytical View Calculations (v_ordertoyearanalytics)

**Purchase cross-reference — fragile string join:**
```sql
(SELECT STRING_AGG(Order_Purch, '\')
 FROM (SELECT TOP 5 p.[Stock Item Key] AS Order_Purch
       FROM Fact.Purchase p
       WHERE fo.Package = p.Package) p
 WHERE p.Order_Purch < fo.[Stock Item Key]) AS ORDER_ID_PURCH
```

Join predicate `fo.Package = p.Package` is a string equality join on a free-text `NVARCHAR` column with no referential integrity. `TOP 5` without `ORDER BY` produces non-deterministic results.

**Tax coverage calculation anomaly:**
```sql
([Total Excluding Tax] - [Tax Amount]) * [Tax Rate] AS [Tax Coverage]
```
Uses `[Total Excluding Tax] - [Tax Amount]` as the base — unusual; `[Total Excluding Tax]` should already exclude tax. This may be a calculation error in the original view.

**Date conversions:**
```sql
CAST(CONVERT(varchar, dod.[DateKey], 112) AS INT) AS Order_Date
```
Format 112 produces YYYYMMDD string, then cast to INT. Double conversion is inefficient and fails on NULL.

**Dead code branch:**
```sql
CASE ISNULL(dod.[Day], 365)
    WHEN 0    THEN 365
    WHEN NULL THEN 365   -- unreachable: ISNULL already eliminates NULL
    ELSE ISNULL(dod.[Day], 365)
END AS Order_Day_Converted
```

**Salesperson correlated subquery:** Two-tier fallback across `fact.order` and `fact.sale` with `WITH (NOLOCK)` — significant performance risk at scale.

---

### 5.7 COALESCE and NULL Handling

| Location | Expression | Business meaning |
|---|---|---|
| `migratestagedpurchasedata` | `COALESCE(<supplier_subquery>, 0)` | Unresolved supplier → Unknown member (key=0). Silent data quality failure. |
| `migratestagedpurchasedata` | `COALESCE(<stock_item_subquery>, 0)` | Unresolved stock item → Unknown member (key=0). Silent data quality failure. |
| `v_ordertoyearanalytics` | `COALESCE(NULLIF(<order_emp_key>, ''), <sale_emp_key>)` | Salesperson fallback: order → sale domain. |
| `v_ordertoyearanalytics` | `ISNULL(dod.[Day], 365)` | Null day-of-year replaced with 365 (year-end proxy). |
| `v_ordertoyearanalytics` | `c.Category + ':' + c.[Buying Group]` | No NULL guard — concatenation produces NULL if either component is NULL. |

**Key risk:** `COALESCE(..., 0)` converts a lookup failure into a silent bad-data write. In Databricks, this pattern should be replaced with explicit DQ monitoring and row quarantine unless the Unknown member pattern is intentionally carried forward.

---

### 5.8 Data Type Conversions

| Location | Conversion | Source type | Target type | Notes |
|---|---|---|---|---|
| `getpurchaseupdates` | `CAST(po.OrderDate AS date)` | `date` | `date` | No-op cast |
| `getpurchaseupdates` | `CASE WHEN pol.LastEditedWhen > po.LastEditedWhen ...` | `datetime2` | `datetime2` | MAX-of-two datetime2 |
| `migratestagedpurchasedata` | `SYSDATETIME()` | system | `datetime2(7)` | Completion timestamp |
| `v_ordertoyearanalytics` | `CAST(CONVERT(varchar, dod.[DateKey], 112) AS INT)` | `date` | `int` | YYYYMMDD integer; fails on NULL |
| `v_ordertoyearanalytics` | `'  ' AS Submission` | literal | `varchar(2)` | Placeholder column — two spaces, no business value |

**Migration note:** `datetime2(7)` maps to Databricks `TIMESTAMP` (microsecond precision; 100-nanosecond ticks truncated — acceptable for ETL watermarks). `Package` column (`NVARCHAR`) maps to Databricks `STRING`; Databricks is case-sensitive by default while SQL Server with default collation is case-insensitive — this difference must be handled in the string join in `v_ordertoyearanalytics`.

---

### 5.9 Calculation Migration Complexity

**Overall rating: HIGH**

| Priority | Challenge | Current pattern | Required migration action |
|---|---|---|---|
| 1 | SCD-2 surrogate key resolution | Correlated UPDATE subquery per staging row | Decompose into pre-join step: broadcast join staging × dimension filtered by validity window, `ROW_NUMBER()` tiebreaker, COALESCE for fallback |
| 2 | Full-order-replacement upsert | DELETE by WWI Purchase Order ID + INSERT all staging rows | Two-phase Delta operation or MERGE with explicit delete-of-unmatched logic |
| 3 | Sentinel key=0 dependency | `COALESCE(lookup, 0)` writes key=0 on miss | Decide: retain Unknown member pattern or introduce explicit row-level rejection/quarantine |
| 4 | Multi-step atomic transaction | `BEGIN TRAN` wraps all steps | Replace with Delta ACID semantics; structure as ordered sequence of Delta writes |
| 5 | Package-string cross-domain join in analytics view | `fo.Package = p.Package` (string, no RI) | Replace with proper foreign key relationship or redesign `ORDER_ID_PURCH` derivation |
| 6 | YYYYMMDD integer date key conversions | `CAST(CONVERT(varchar, date, 112) AS INT)` | Evaluate target date dimension key type; replace double-conversion if using native date |
| 7 | Incremental watermark CASE expression repeated in WHERE | CASE expression evaluated twice per row | Rewrite using CTE or derived table in Spark SQL to pre-compute once |

---

## 6. Sources

### 6.1 Source System Inventory

| Role | System | Database | Platform | Connection Method |
|---|---|---|---|---|
| Transactional source | wideworldimporters | Microsoft SQL Server (OLTP) | On-premises SQL Server 2014 | SSIS OLE DB connection; called via `integration.getpurchaseupdates` |
| Data warehouse | wideworldimportersdw | Microsoft SQL Server 2014 | On-premises SQL Server 2014 | SSIS OLE DB connection; internal to the DW server |
| Orchestration | SSIS daily batch | SQL Server Integration Services | On-premises SSIS | Package: `demo_ssis.folder_ssis-project.pipeline_dailyetlmain` |

No external file feeds, CDC streams, or message queues are involved in the current architecture.

---

### 6.2 OLTP Source Tables

| OLTP Table | Schema | Role in Extract | Key Columns Used |
|---|---|---|---|
| `wideworldimporters.purchasing.purchaseorders` | `purchasing` | Purchase order header | `PurchaseOrderID`, `OrderDate`, `SupplierID`, `LastEditedWhen` |
| `wideworldimporters.purchasing.purchaseorderlines` | `purchasing` | Purchase order line detail | `PurchaseOrderID`, `StockItemID`, `PackageTypeID`, `OrderedOuters`, `ReceivedOuters`, `IsOrderLineFinalized`, `LastEditedWhen` |
| `wideworldimporters.warehouse.stockitems` | `warehouse` | Stock item attributes | `StockItemID`, `QuantityPerOuter` |
| `wideworldimporters.warehouse.packagetypes` | `warehouse` | Package type description | `PackageTypeID`, `PackageTypeName` |

Join topology: `purchaseorders` INNER JOIN `purchaseorderlines` on `PurchaseOrderID`, INNER JOIN `stockitems` on `StockItemID`, INNER JOIN `packagetypes` on `PackageTypeID`. All four tables accessed in a single result-set query.

Note: `wideworldimporters.integration.getpurchaseupdates` is explicitly out-of-scope for migration; it is replaced by a Databricks native connector reading the four OLTP tables directly.

---

### 6.3 Extraction Method

**SSIS Dataflow:** `pipeline_item_extract updated purchase data to staging` (id: `5b1ac205-a17d-4ead-83e7-14d95b112a54`) calls `wideworldimporters.integration.getpurchaseupdates` and loads the result into `wideworldimportersdw.integration.purchase_staging`.

**Full procedure body:** (See Section 5.5 for complete SQL.)

Key characteristics:
- **No CDC** — last-modified-timestamp polling, not Change Data Capture.
- **No OLTP staging** — direct result set from procedure; no intermediate temp table on OLTP side.
- **Measure derivation at extract time** — `[Ordered Quantity] = OrderedOuters * QuantityPerOuter` computed during extraction.
- **Package type denormalized** — `pt.PackageTypeName` fetched at extract time as raw string.

---

### 6.4 Incremental Load Pattern

**Watermark table:** `wideworldimportersdw.integration.[ETL Cutoff]` — one row per entity with `[Cutoff Time]` high-water mark.

**ETL cutoff lifecycle for Purchase:**
1. SSIS reads previous watermark via `getlastetlcutofftime` with `@TableName = 'Purchase'` → returns `@LastCutoff`.
2. SSIS sets `@NewCutoff` to the current batch run time.
3. `getpurchaseupdates` filters: `max(pol.LastEditedWhen, po.LastEditedWhen) > @LastCutoff AND <= @NewCutoff`.
4. After successful `migratestagedpurchasedata`, watermark is advanced to `[Source System Cutoff Time]` from the lineage row.

**Incremental change detection:** The derived expression `CASE WHEN pol.LastEditedWhen > po.LastEditedWhen THEN pol.LastEditedWhen ELSE po.LastEditedWhen END` — any change to header or any line brings all lines for that order into the extract window.

**Filter:** Open/closed: `> @LastCutoff AND <= @NewCutoff` — records exactly at previous cutoff are excluded; records exactly at new cutoff are included.

---

### 6.5 Staging Layer

`wideworldimportersdw.integration.purchase_staging` (id: `a016e5b7-ab70-4e45-af51-b70ae237c7e2`) — intermediate landing zone between SSIS extraction and fact load. (Full DDL and column roles documented in Section 3.4.1.)

**Staging lifecycle per batch:**
1. SSIS executes truncate step (⚠ bug: targets `Order_Staging` instead of `Purchase_Staging`).
2. Extract dataflow loads rows from `getpurchaseupdates` into staging.
3. `migratestagedpurchasedata` updates `[Supplier Key]` and `[Stock Item Key]` in-place.
4. Rows transferred to `fact.purchase` (DELETE + INSERT per `WWI Purchase Order ID`).
5. Staging not archived; fully replaced on each batch run.

---

### 6.6 Dimension Sources

**dimension.supplier:**

| Element | Detail |
|---|---|
| OLTP source tables | `purchasing.suppliers`, `purchasing.suppliers_archive`, `purchasing.suppliercategories`, `purchasing.suppliercategories_archive`, `application.people` |
| OLTP extraction procedure | `wideworldimporters.integration.getsupplierupdates` |
| DW load procedure | `wideworldimportersdw.integration.migratestagedsupplierdata` |
| SCD type | Type 2 — temporal snapshots via `FOR SYSTEM_TIME AS OF` queries |

**dimension.stock item:**

| Element | Detail |
|---|---|
| OLTP source tables | `warehouse.stockitems`, `warehouse.stockitems_archive`, `warehouse.packagetypes`, `warehouse.colors` |
| OLTP extraction procedure | `wideworldimporters.integration.getstockitemupdates` |
| DW load procedure | `wideworldimportersdw.integration.migratestagedstockitemdata` |
| SCD type | Type 2 — temporal snapshots via `FOR SYSTEM_TIME AS OF` queries |

**dimension.date:** Static — no OLTP extraction dependency. `[Date Key]` in the purchase fact is `po.OrderDate` cast to `date`, joining to `dimension.date` by date value.

**Dimension-to-purchase dependency:** Both supplier and stock item ETL must complete before `migratestagedpurchasedata` runs. Silent `COALESCE(..., 0)` fallback means ordering failures produce no error — only incorrect key=0 values in `fact.purchase`.

---

### 6.7 Data Freshness and Latency

| Aspect | Current behavior |
|---|---|
| Batch frequency | Once daily — SSIS `pipeline_dailyetlmain` as scheduled daily job |
| Maximum lag | Up to 24 hours between OLTP transaction commit and appearance in `fact.purchase` |
| Incremental detection | Last-modified-timestamp comparison (`LastEditedWhen` on header and line); not CDC |
| Watermark persistence | Updated transactionally within `migratestagedpurchasedata` upon successful load |
| Order-level reload | The load deletes and re-inserts all lines for any `WWI Purchase Order ID` present in staging |
| Historic re-seeds | `configuration_reseedetl` can reset `fact.purchase` for full-reload when required |

---

### 6.8 Source-to-Target Column Mapping (High-Level)

| OLTP Column(s) | Transformation in `getpurchaseupdates` | Staging Column | Fact Column |
|---|---|---|---|
| `po.OrderDate` | `CAST(po.OrderDate AS date)` | `[Date Key]` | `[Date Key]` |
| — | SCD-2 lookup on `dimension.supplier` using `[WWI Supplier ID]` + `[Last Modified When]` | `[Supplier Key]` | `[Supplier Key]` |
| — | SCD-2 lookup on `dimension.stock item` using `[WWI Stock Item ID]` + `[Last Modified When]` | `[Stock Item Key]` | `[Stock Item Key]` |
| `po.PurchaseOrderID` | Direct pass-through | `[WWI Purchase Order ID]` | `[WWI Purchase Order ID]` |
| `pol.OrderedOuters` | Direct pass-through | `[Ordered Outers]` | `[Ordered Outers]` |
| `pol.OrderedOuters`, `si.QuantityPerOuter` | `pol.OrderedOuters * si.QuantityPerOuter` | `[Ordered Quantity]` | `[Ordered Quantity]` |
| `pol.ReceivedOuters` | Direct pass-through | `[Received Outers]` | `[Received Outers]` |
| `pt.PackageTypeName` | Direct pass-through (denormalized string) | `[Package]` | `[Package]` |
| `pol.IsOrderLineFinalized` | Direct pass-through | `[Is Order Finalized]` | `[Is Order Finalized]` |
| `po.SupplierID` | Direct pass-through | `[WWI Supplier ID]` | _(not in fact — used for key resolution only)_ |
| `pol.StockItemID` | Direct pass-through | `[WWI Stock Item ID]` | _(not in fact — used for key resolution only)_ |
| `pol.LastEditedWhen`, `po.LastEditedWhen` | MAX-of-two CASE expression | `[Last Modified When]` | _(not in fact — used for dimension lookups and watermark)_ |
| — | Fetched from `Integration.Lineage` by `migratestagedpurchasedata` | _(not in staging)_ | `[Lineage Key]` |

---

### 6.9 Migration Impact on Sources

| Area | Current state | Target state |
|---|---|---|
| Extraction mechanism | SSIS OLE DB call to `getpurchaseupdates` | Databricks native JDBC/ODBC connector reading four OLTP tables directly |
| Source-side procedure | `getpurchaseupdates` — active and required | Out-of-scope; does not migrate; decommissioned after cutover |
| Incremental logic | Timestamp filter within stored procedure | Re-implemented in Databricks (Delta Lake change data feed, watermark metadata tables, or Autoloader) |
| Measure computation | `OrderedOuters * QuantityPerOuter` computed in SQL at extract time | Must be implemented in Databricks transformation layer (Spark SQL or dbt model) |
| Staging zone | SQL Server `integration.purchase_staging` | Databricks Delta table (raw or bronze layer); stateless per-run eliminates accumulation bug |
| Watermark store | `wideworldimportersdw.integration.[ETL Cutoff]` SQL Server table | Databricks-native metadata store or Delta table |

**Connectivity requirements:** Databricks must have network access to the `wideworldimporters` SQL Server instance — firewall rules, JDBC/ODBC driver configuration, and read-only service account credentials for four OLTP tables.

**Key migration risks from source-side changes:**

1. **No CDC on source** — if any OLTP process modifies rows without updating `LastEditedWhen`, changes will be missed. Migration is an opportunity to assess whether CDC should be introduced.
2. **Join-at-extract vs. join-at-transform** — four OLTP tables currently joined in one query; in Databricks, these tables will likely be ingested separately and joined in a transformation layer.
3. **`PackageTypeName` denormalization** — `packagetypes.PackageTypeName` is denormalized at extract time; the Databricks model may require ingesting `packagetypes` as a separate reference table.
4. **`QuantityPerOuter` at time of order** — current extraction reads `QuantityPerOuter` at batch run time, not at order creation time. If stock item quantity-per-outer changes between order date and extraction date, `[Ordered Quantity]` reflects the current value. Migration must decide whether to preserve this behavior or correct it using a point-in-time lookup.
