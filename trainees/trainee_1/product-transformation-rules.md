# Product Transformation Rules: Sales_Orders

| Field | Value |
|---|---|
| Product | Sales_Orders |
| Project | GlobalSales_Project |
| Inherits from | project-transformation-rules v1.0.1 |
| Generated | 2026-06-05 |
| Updated | 2026-08-28 |
| Project rules version | 1.0.1 |
| Changelog | 2026-08-28 (pass 2) — PL: corrected all schema/layer names throughout (bronze/silver_dim/silver_fact/gold → stg/dim/fact/mart) in PL-002, PL-009, PL-010; fixed silver_fact.Sale → globalsales.fact.sale and silver_fact.Order → globalsales.fact.order (4 occurrences); normalized quality_dimensions to ODPS lowercase across all 10 PL rules. OB: removed erroneous NM-EXTEND-001 reference in OB-001 (step 4 and product_notes); fixed Integration.Sale_Staging staging → stg in OB-003. SX: corrected SX-014 schema mapping (bronze/gold/silver → globalsales.stg/fact/dim/mart); fixed SX-013 NEXT VALUE FOR guidance (monotonically_increasing_id() → open_lineage_record()/close_lineage_record() per lineage_utils.py). QA: corrected all fact/dim/stg/lineage schema names in QA-P01 SQL expressions (gold.fact_* → fact.*, gold.dim_* → dim.*, silver.* → stg.*_staging, lineage → stg.lineage); renamed algorithm variables (silver_*_count → stg_*_count, gold_*_count → fact_*_count) in QA-P03; normalized quality_dimensions to ODPS lowercase in QA-P01/P02/P03 (Completeness, Referential Integrity, Auditability, Lineage → completeness, validity, coverage, completeness). new-rules: fixed CX-P02 quality_dimensions flexibility → timeliness. 2026-08-28 (pass 1) — TY: corrected platform target throughout (Snowflake → Databricks/Delta Lake); fixed TY-003/TY-004 types (NUMBER(10,0)/NUMBER(19,0) → INT/BIGINT); fixed TY-023 IDENTITY DDL (AUTOINCREMENT → GENERATED ALWAYS AS IDENTITY); rewrote TY-024 SEQUENCE (Snowflake SEQUENCE → Python lineage_utils/Delta IDENTITY); fixed TY-029 DEFAULT functions (UUID_STRING() → uuid(), CURRENT_TIMESTAMP() lowercase); fixed TY-030 computed columns (VIRTUAL → GENERATED ALWAYS AS); fixed TY-EXTEND-001 geography (Snowflake GEOGRAPHY → Databricks H3/WKT). NM: fixed NM-009 (dbt model naming → Databricks tmp_/df_ convention); corrected quality_dimensions capitalization; removed Snowflake/dbt terminology. PE: corrected all OPTIMIZE statements to globalsales.* three-part catalog names (10 fixes). LN: corrected schema fct → fact throughout (5 replace_all passes). |

---

## Customization Summary

| Action type | Count | Details |
|---|---|---|
| Overrides | 0 | No project rules overridden |
| Extensions | 6 | TY-EXTEND-001, SX-EXTEND-001, LN-EXTEND-001, OB-EXTEND-001, PE-EXTEND-001 (via extensions.yaml) + SX product note on SX-EXTEND-001 |
| Deactivations | 0 | No project rules deactivated |
| New product rules | 10 | CX-P01..P04, QA-P01..P03, IF-P01..P03 (via new-rules.yaml) |

The Sales_Orders product inherits all 92 project-level rules directly. It adds 6 extensions addressing product-specific structures (geography column, duplicate UDFs, lineage asymmetry, liquid clustering election, NOLOCK scope review, and Sale_Staging lineage fix) and 10 new rules covering undocumented business logic (1.05 profit factor), hard-coded date filters, dbo schema cleanup, OLTP-direct BI dependency, data quality assertions, and Power BI reconnection strategy.

---

## Dimension Table

| Dimension | Prefix | File | Rule Count (effective) | Customizations |
|---|---|---|---|---|
| Platform | PL | [PL-platform.yaml](PL-platform.yaml) | 10 | 2 product notes (PL-003, PL-006) |
| Naming | NM | [NM-naming.yaml](NM-naming.yaml) | 9 | 1 product note (NM-006 UDF consolidation) |
| Types | TY | [TY-types.yaml](TY-types.yaml) | 16 active + 14 inactive + 1 extension | TY-EXTEND-001: geography → WKT+lat+lon |
| Objects | OB | [OB-objects.yaml](OB-objects.yaml) | 9 active + 2 inactive + 1 extension | OB-EXTEND-001: UDF consolidation |
| Syntax | SX | [SX-syntax.yaml](SX-syntax.yaml) | 15 active + 2 inactive + 1 extension | SX-EXTEND-001: NOLOCK + auxiliary table scope |
| Performance | PE | [PE-performance.yaml](PE-performance.yaml) | 8 | PE-EXTEND-001: Fact.Sale → liquid clustering |
| Lineage | LN | [LN-lineage.yaml](LN-lineage.yaml) | 7 | LN-EXTEND-001: Sale_Staging lineage_key fix |
| Custom | CX | [CX-custom.yaml](CX-custom.yaml) | 4 (product-new) | CX-P01..P04 |
| Quality | QA | [QA-quality.yaml](QA-quality.yaml) | 3 (product-new) | QA-P01..P03 |
| Interface | IF | [IF-interface.yaml](IF-interface.yaml) | 3 (product-new) | IF-P01..P03 |

**Total effective rules: 92 (inherited) + 10 (new) = 102**

---

## Rule Index

### PL — Platform (10 rules, 2 product notes)

| Rule ID | Intent | Tag |
|---|---|---|
| PL-001 | Platform identity and engine contract: SQL Server 2014 → Databricks | inherited |
| PL-002 | Schema namespace mapping: dimension/fact/integration/analytics → Unity Catalog | inherited |
| PL-003 | Storage format: Fact.Sale (CCX) + Fact.Order (rowstore) → USING DELTA | inherited + note |
| PL-004 | SEQUENCE replacement: sequences.lineagekey → IDENTITY/Python counter | inherited |
| PL-005 | ETL pattern: MigrateStagedSaleData/OrderData procedures → Delta MERGE notebooks | inherited |
| PL-006 | Columnstore/partition → Z-ORDER/liquid clustering: Fact.Sale elects liquid clustering | inherited + note |
| PL-007 | Application procedure disposition: not in Sales_Orders scope (retained for traceability) | inherited |
| PL-008 | Transaction model: XACT_ABORT ON in ETL procedures → Delta atomic writes + Python try/except | inherited |
| PL-009 | Medallion architecture: integration→bronze, dim→silver_dim, fact→silver_fact, analytics→gold | inherited |
| PL-010 | SQL Agent / SSIS dailyetlmain → Databricks Workflows nightly batch | inherited |

### NM — Naming (9 rules, 1 product note)

| Rule ID | Intent | Tag |
|---|---|---|
| NM-001 | PascalCase → snake_case for all objects | inherited |
| NM-002 | Space-bearing names: `payment method`, `stock item`, `transaction type`, `etl cutoff` | inherited |
| NM-003 | Schema → catalog.schema mapping | inherited |
| NM-004 | v_ prefix for views: CustomerSalesSummary → v_customer_sales_summary | inherited |
| NM-005 | _staging suffix for integration tables | inherited |
| NM-006 | Procedure/function naming: getTotalQuantitySold1/2 → get_total_quantity_sold (consolidated) | inherited + note |
| NM-007 | sequences.* not migrated | inherited |
| NM-008 | Index/constraint naming: pk_, uq_, chk_ prefixes | inherited |
| NM-009 | Temp table naming: #temp → tmp_/df_ | inherited |

### TY — Types (16 active + 14 inactive + 1 extension)

| Rule ID | Intent | Tag |
|---|---|---|
| TY-003 | INT → INT (CustomerKey, Quantity, TotalDryItems, etc.) | inherited |
| TY-004 | BIGINT → BIGINT (SaleKey, OrderKey surrogate PKs) | inherited |
| TY-005 | DECIMAL(p,s) → DECIMAL(p,s) (UnitPrice, TaxRate, Profit, all monetary columns) | inherited |
| TY-011 | NVARCHAR → STRING (Description, Package, etc.) | inherited |
| TY-012 | DATE → DATE (OrderDateKey, InvoiceDateKey, PickedDateKey) | inherited |
| TY-015 | DATETIME2 → TIMESTAMP_NTZ (ValidFrom/ValidTo on all SCD2 dims) | inherited |
| TY-018 | VARBINARY → BINARY (Photo on StockItem and Employee dims) | inherited |
| TY-020 | BIT → BOOLEAN (IsChillerStock on StockItem) | inherited |
| TY-021 | Preserve NOT NULL constraints | inherited |
| TY-023 | IDENTITY → GENERATED ALWAYS AS IDENTITY (Fact.Sale.SaleKey, Fact.Order.OrderKey) | inherited |
| TY-024 | SEQUENCE → IDENTITY/Python counter (sequences.lineagekey) | inherited |
| TY-027 | Collation → Spark UTF-8 default | inherited |
| TY-029 | DEFAULT constraints translation | inherited |
| TY-030 | Computed columns → GENERATED ALWAYS AS | inherited |
| TY-EXTEND-001 | geography → location_wkt STRING + location_lat DOUBLE + location_lon DOUBLE (Dimension.City.Location) | extension |
| *(TY-001,006-010,013-017,019,022,025-026,028 not activated — types absent from Sales_Orders schema)* | | inactive |

### OB — Objects (9 active + 2 inactive + 1 extension)

| Rule ID | Intent | Tag |
|---|---|---|
| OB-001 | 7 dimension tables → globalsales.dim.* (note: PaymentMethod + TransactionType are orphaned — no FK to facts) | inherited |
| OB-002 | 2 fact tables → globalsales.fact.sale (liquid clustering) + globalsales.fact.order (partitioned) | inherited |
| OB-003 | 5 staging tables → globalsales.stg.* (Sale_Staging gains lineage_key per LN-EXTEND-001) | inherited |
| OB-005 | 4 analytics views → globalsales.mart.* (CustomerSalesSummary = materialized view; others = regular views) | inherited |
| OB-006 | 2 UDFs consolidated → single globalsales.fact.get_total_quantity_sold with NULL guard | extension (OB-EXTEND-001) |
| OB-007 | 4+ ETL procedures → Python tasks (get_sale_updates, get_order_updates, migrate_staged_sale_data, migrate_staged_order_data) | inherited |
| OB-008 | Sequences.LineageKey + IDENTITY PKs → Delta IDENTITY columns | inherited |
| OB-011 | dbo.OrderDetails excluded; BI reports reconnected to single v_order_details (CX-P03) | inherited + note |
| OB-004 | Analytics schema contains only views — deferred to OB-005 | inactive |
| OB-009 | No application procedures in Sales_Orders scope | inactive |
| OB-010 | No config objects in Sales_Orders scope | inactive |

### SX — Syntax (15 active + 2 inactive + 1 extension)

| Rule ID | Intent | Tag |
|---|---|---|
| SX-001 | MERGE → MERGE INTO (MigrateStagedSaleData/OrderData upsert patterns) | inherited |
| SX-002 | SET NOCOUNT ON / SET XACT_ABORT ON removal from all ETL procedures | inherited |
| SX-003 | Transaction control: DELETE+INSERT in Migrate* procedures → Delta MERGE atomic | inherited |
| SX-004 | @@ROWCOUNT/@@ERROR in GetSaleUpdates/GetOrderUpdates → Delta metrics + try/except | inherited |
| SX-005 | GETUTCDATE() / SYSDATETIME() in ETL cutoff and lineage → current_timestamp() / datetime.utcnow() | inherited |
| SX-006 | COALESCE used for SCD2 fallback key (0 = Unknown) → COALESCE preserved | inherited |
| SX-007 | TOP(1) in SCD2 key resolution → LIMIT 1 with ORDER BY Valid_From DESC | inherited |
| SX-EXTEND-001 | NOLOCK removal in v_OrderToSupplyAnalytics + auxiliary table scope review flag | extension |
| SX-009 | PRINT statements in ETL procedures → logger.info/error | inherited |
| SX-011 | OBJECT_ID existence checks → DROP TABLE IF EXISTS / spark.catalog | inherited |
| SX-012 | Window functions in analytics views → Spark SQL window functions | inherited |
| SX-013 | IDENTITY(1,1) + NEXT VALUE FOR sequences.lineagekey → GENERATED ALWAYS AS IDENTITY / Python | inherited |
| SX-014 | Schema-qualified references: Integration./Fact./Dimension. → Unity Catalog three-part names | inherited |
| SX-015 | Bracket quoting removal: [Stock Item Key] → stock_item_key | inherited |
| SX-016 | CAST/CONVERT: CONVERT(CHAR(8), GETDATE()-100, 112) in v_OrderToYearAnalytics → DATE_FORMAT(DATE_SUB(current_date(),100),'yyyyMMdd'); ROUND(Quantity*UnitPrice,2) preserved | inherited |
| SX-010 | EXECUTE AS — not found in Sales_Orders scope | inactive |
| SX-017 | FOR XML PATH — not found in Sales_Orders scope | inactive |

### PE — Performance (8 rules, 1 product election)

| Rule ID | Intent | Tag |
|---|---|---|
| PE-001 | CCX_Fact_Sale columnstore index dropped — Delta columnar by default | inherited |
| PE-002 | Fact.Order PARTITIONED BY (order_date) — standard date partitioning (Fact.Sale → PE-004 instead) | inherited (Fact.Order only) |
| PE-003 | Fact.Order ZORDER BY (customer_key, stock_item_key) — Fact.Sale → liquid clustering (no ZORDER) | inherited (Fact.Order only) |
| PE-004 | Fact.Sale → CLUSTER BY (invoice_date, customer_key, stock_item_key): liquid clustering elected per CCX evidence | extension (PE-EXTEND-001) |
| PE-005 | OPTIMIZE in nightly ETL: Fact.Sale (no ZORDER); Fact.Order (ZORDER); all dims (plain OPTIMIZE); staging excluded | inherited |
| PE-006 | Broadcast join for all 7 dim tables — all small relative to fact tables | inherited |
| PE-007 | 5 staging tables: transient, no OPTIMIZE, no partitioning, short retention | inherited |
| PE-008 | autoOptimize.optimizeWrite + autoOptimize.autoCompact on all non-staging Delta tables | inherited |

### LN — Lineage (7 rules, 1 extension)

| Rule ID | Intent | Tag |
|---|---|---|
| LN-001 | integration.lineage → globalsales.stg.lineage Delta table | inherited |
| LN-002 | sequences.lineagekey SEQUENCE → IDENTITY on lineage_key column | inherited |
| LN-003 | integration.getlineagekey → open_lineage_record() / close_lineage_record() Python utilities | inherited |
| LN-004 | lineage_key propagated to Fact.Sale + Fact.Order; Sale_Staging gains lineage_key (asymmetry fix per LN-EXTEND-001) | extension (LN-EXTEND-001) |
| LN-005 | ReseedAllSequences + ReseedSequenceBeyondTableValues retired | inherited |
| LN-006 | Unity Catalog system lineage enabled for globalsales.* tables | inherited |
| LN-007 | ETL run metadata captured by 4 pipeline tasks (get_sale_updates, get_order_updates, migrate_staged_sale_data, migrate_staged_order_data) | inherited |

### CX — Custom (4 product-new rules)

| Rule ID | Intent | Tag |
|---|---|---|
| CX-P01 | Document + confirm 1.05 profit margin factor; codify as named constant; add DQ sanity bound | product-new |
| CX-P02 | Parameterise hard-coded date filters: OrderDetails '20230101' + v_OrderToYearAnalytics rolling 100-day window | product-new |
| CX-P03 | Decommission dbo.OrderDetails duplicate; reconnect 2 Power BI reports to single v_order_details | product-new |
| CX-P04 | Document dae – global – demos OLTP-direct connection as PENDING_DECISION before go-live | product-new |

### QA — Quality (3 product-new rules)

| Rule ID | Intent | Tag |
|---|---|---|
| QA-P01 | 5 DQ assertions: dry+chiller sum=quantity; profit guard; backorder integrity; cross-fact variance ≤5%; orphan key checks | product-new |
| QA-P02 | DQ gate integration: failed rows → globalsales.stg.dq_rejections; results captured in lineage record | product-new |
| QA-P03 | ETL row count reconciliation: staging count = fact table delta = lineage.table_row_count (zero tolerance) | product-new |

### IF — Interface (3 product-new rules)

| Rule ID | Intent | Tag |
|---|---|---|
| IF-P01 | Power BI reconnection: 9 reports mapped to Databricks SQL endpoint targets (5 → fact.sale, 3 → fact.order, 2 → mart.v_order_details, 1 → CX-P04 TBD) | product-new |
| IF-P02 | Column naming compatibility: Gold views expose snake_case + aliased display names for Power BI | product-new |
| IF-P03 | Databricks SQL endpoint provisioning and BI connectivity validation | product-new |
