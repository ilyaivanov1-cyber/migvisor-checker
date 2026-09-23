# Project Transformation Rules: Purchasing_Project

| Field | Value |
|---|---|
| Version | 20260921-161200 |
| Generated | 2026-09-21 |
| Source | Microsoft SQL Server 2014 (`wideworldimportersdw`, Purchases-domain subset) |
| Target | Databricks (Delta Lake lakehouse) |
| Active dimensions | 7 |

---

## Dimension Table

| Dimension | Prefix | File | Rule Count |
|---|---|---|---|
| Platform | PL | [PL-platform.yaml](PL-platform.yaml) | 10 |
| Naming | NM | [NM-naming.yaml](NM-naming.yaml) | 10 |
| Types | TY | [TY-types.yaml](TY-types.yaml) | 29 |
| Objects | OB | [OB-objects.yaml](OB-objects.yaml) | 10 |
| Syntax | SX | [SX-syntax.yaml](SX-syntax.yaml) | 11 |
| Performance | PE | [PE-performance.yaml](PE-performance.yaml) | 8 |
| Lineage | LN | [LN-lineage.yaml](LN-lineage.yaml) | 7 |

**Total rules: 85**

Purchasing_Project was split off from GlobalSales_Project into its own standalone project. Its rule set was authored fresh from `project/current/modernization-plan.md` (not copy-adapted from GlobalSales_Project), scoped only to the Purchases-domain objects (`dimension.supplier`, `dimension.stock item`, `dimension.date`, `fact.purchase`, `integration.purchase_staging`/`lineage`/`etl cutoff`, `sequences.lineagekey`). Several rules (PL-008, PL-009, OB-002, OB-008) explicitly flag cross-catalog/cross-project decisions created by the split as `[USER INPUT REQUIRED]` — see the Open Questions section below.

---

## Rule Index

### PL — Platform (10 rules)

| Rule ID | Intent |
|---|---|
| PL-001 | Establish the authoritative mapping between SQL Server 2014 (source, `wideworldimportersdw` Purchases-domain subset) and Databricks Delta Lake (target, new independent Unity Catalog `purchasing`), anchoring the PL dimension and scoping engine disposition to the four owned schemas. |
| PL-002 | Map each of the four in-scope SQL Server schemas (`dimension`, `fact`, `integration`, `sequences`) to `purchasing.<layer>.<table>` Unity Catalog names, enforcing lowercase_snake_case and a distinct medallion-layer assignment from `globalsales`. |
| PL-003 | Convert every SQL Server table/view in scope (`fact.purchase`; `dimension.supplier`/`stock item`/`date`; `integration.purchase_staging`/`lineage`/`etl cutoff`; `etl_cutoff_view2024`) to Delta Lake format with ACID guarantees, enabling Change Data Feed on `fact.purchase`. |
| PL-004 | Eliminate the `sequences.lineagekey` SEQUENCE object and replace it with a Databricks-native, auditable Delta counter table, since the key is read back for batch bookkeeping, not just used as an opaque surrogate. |
| PL-005 | Replace the SSIS-orchestrated staging-and-procedure pattern (`GetPurchaseUpdates` → `Purchase_Staging` → `MigrateStagedPurchaseData`) with a Databricks-native Bronze-to-Silver notebook pattern preserving incremental extraction and the Ordered Quantity calculation. |
| PL-006 | Replace the DELETE-then-INSERT full-replace load of `fact.purchase` keyed on WWI Purchase Order ID with a Delta MERGE that reproduces the same atomic, order-scoped replace semantics. |
| PL-007 | Replace the correlated TOP(1) valid-time lookups resolving Supplier Key/Stock Item Key with a Spark-native range-join pattern, and document that Date Key requires no equivalent lookup. |
| PL-008 | Resolve the cross-catalog conformed dimension sharing strategy for `dimension.supplier` and `dimension.stock item`, now split across the `purchasing` and `globalsales` catalogs as a consequence of the project split. `[USER INPUT REQUIRED]` |
| PL-009 | Resolve cross-catalog downstream dependency exposure for the three GlobalSales_Project artifacts that read `fact.purchase` directly, now that it lives under `purchasing` rather than `globalsales`. `[USER INPUT REQUIRED]` |
| PL-010 | Replace the SSIS orchestration pipeline for Purchase extraction/load with an equivalent, standalone Databricks Workflow scoped only to Purchasing_Project. |

### NM — Naming (10 rules)

| Rule ID | Intent |
|---|---|
| NM-001 | Convert all SQL Server object names using PascalCase/camelCase/mixed case in the Purchasing domain into lowercase_snake_case. |
| NM-002 | Rename space-containing SQL Server table/view/schema names in Purchasing_Project's in-scope inventory to valid snake_case identifiers via an explicit mapping table. |
| NM-003 | Map each in-scope SQL Server schema (`dimension`, `fact`, `integration`, `sequences`) to its three-part Databricks identifier under the project's own `purchasing` catalog. |
| NM-004 | Standardise view naming for the in-scope view (`etl_cutoff_view2024`) using a lowercase `v_` prefix, stripping the redundant "view" token and trailing year. |
| NM-005 | Preserve the `_staging` suffix convention for the Purchasing landing table while excluding the two shared control tables (etl cutoff, lineage) from the suffix. |
| NM-006 | Map the two in-scope stored procedures (`migratestagedpurchasedata`, `getlineagekey`) to snake_case Python function names, excluding the informational upstream procedure. |
| NM-007 | Declare that the `sequences.lineagekey` SEQUENCE object is not migrated to Databricks; IDENTITY columns or application-generated keys replace it. |
| NM-008 | Establish a consistent naming convention for the PK/FK constraints evidenced on `fact.purchase`, documenting FKs as informational lineage since Delta Lake does not enforce them. |
| NM-009 | Rename SQL Server bracket-quoted, space-containing COLUMN names on in-scope objects to valid snake_case identifiers, preserving business-key prefixes like WWI. |
| NM-010 | Establish a naming/reference convention for cross-catalog reused dimensions and consumer objects unique to this project's split-off topology, fixing references regardless of which sharing strategy PL-008 resolves to. |

### TY — Types (29 rules)

| Rule ID | Intent |
|---|---|
| TY-001 | Convert SQL Server TINYINT to Spark SQL BYTE (baseline, no current evidence). |
| TY-002 | Preserve SMALLINT as the identical Spark SQL type (baseline, no current evidence). |
| TY-003 | Preserve SQL Server INT as Spark SQL INT — dominant integer type across Purchases business keys, surrogate keys, and calendar attributes. |
| TY-004 | Preserve SQL Server BIGINT as Spark SQL BIGINT — evidenced on Purchase Key and Purchase Staging Key surrogate keys. |
| TY-005 | Convert SQL Server DECIMAL/NUMERIC to Spark SQL DECIMAL(p,s), preserving precision and scale exactly — evidenced on UnitPrice and ExpectedUnitPricePerOuter. |
| TY-006 | Convert SQL Server MONEY to DECIMAL(19,4) in Spark SQL (baseline, no current evidence — Purchases uses plain DECIMAL). |
| TY-007 | Convert SQL Server SMALLMONEY to DECIMAL(10,4) in Spark SQL (baseline, no current evidence). |
| TY-008 | Convert SQL Server FLOAT to Spark SQL DOUBLE (baseline, no current evidence). |
| TY-009 | Convert SQL Server REAL/FLOAT(n≤24) to Spark SQL FLOAT (baseline, no current evidence). |
| TY-010 | Convert CHAR/NCHAR to Spark SQL STRING (baseline, no current evidence — all evidenced char columns are NVARCHAR). |
| TY-011 | Convert VARCHAR/NVARCHAR to Spark SQL STRING — extensively evidenced across Supplier, Stock Item, Package, Category, and other attributes. |
| TY-012 | Preserve SQL Server DATE as Spark SQL DATE — evidenced on Order Date, Date Key, and Dimension.Date.Date. |
| TY-013 | Convert SQL Server TIME to STRING with documented precision (baseline, no current evidence). |
| TY-014 | Convert SQL Server DATETIME to Spark SQL TIMESTAMP (baseline, no current evidence — evidenced timestamps are DATETIME2). |
| TY-015 | Convert SQL Server DATETIME2 to Spark SQL TIMESTAMP_NTZ — evidenced on Last Edited When, Valid From/To, and Last Modified When. |
| TY-016 | Convert SQL Server SMALLDATETIME to Spark SQL TIMESTAMP (baseline, no current evidence). |
| TY-017 | Convert SQL Server DATETIMEOFFSET to Spark SQL TIMESTAMP (baseline, no current evidence). |
| TY-018 | Convert BINARY/VARBINARY to Spark SQL BINARY — evidenced on Dimension.Stock Item.Photo. |
| TY-019 | Convert the deprecated SQL Server IMAGE type to Spark SQL BINARY (baseline, no current evidence). |
| TY-020 | Convert SQL Server BIT to Spark SQL BOOLEAN — evidenced on Is Order Finalized and Is Chiller Stock. |
| TY-021 | Faithfully replicate SQL Server NULL/NOT NULL column constraints in Delta Lake table DDL across all Purchases objects. |
| TY-022 | Convert SQL Server UNIQUEIDENTIFIER to Spark SQL STRING (baseline, no current evidence). |
| TY-023 | Replace SQL Server IDENTITY columns with Delta Lake's native GENERATED ALWAYS AS IDENTITY clause — evidenced on Fact.Purchase.Purchase Key. |
| TY-024 | Replace SQL Server SEQUENCE objects (`sequences.lineagekey`, and the as-is-evidenced Supplier/Stock Item key sequences) with Delta IDENTITY or a Python counter. Flags a minor scope-inventory gap: Sequences.SupplierKey/StockItemKey are not individually listed in `modernization-plan.md` §6.4. |
| TY-025 | Convert SQL Server XML type to Spark SQL STRING (baseline, no current evidence). |
| TY-026 | Convert SQL Server SQL_VARIANT to Spark SQL STRING (baseline, no current evidence). |
| TY-027 | Remove SQL Server column-level and database-level collation specifications when generating Spark SQL DDL (baseline, no explicit COLLATE evidenced). |
| TY-028 | Translate SQL Server DEFAULT constraint values to Spark SQL DDL defaults (baseline, no current DDL DEFAULT evidenced). |
| TY-029 | Replace SQL Server computed column definitions with Delta Lake GENERATED ALWAYS AS columns, explicitly documenting that Ordered Quantity does not qualify (it's ETL-computed, not a DDL computed column). |

### OB — Objects (10 rules)

| Rule ID | Intent |
|---|---|
| OB-001 | Migrate the net-new `dimension.supplier` table to a Delta managed SCD2 table under `purchasing.dim`, preserving its valid-time structure. |
| OB-002 | Resolve the cross-project sharing decision for the reused `dimension.stock item` and `dimension.date`, already migrated by GlobalSales_Project, without this project re-implementing their load logic. `[USER INPUT REQUIRED]` |
| OB-003 | Migrate the sole fact table, `fact.purchase`, to a Delta managed table under `purchasing.fact`, preserving its grain and documenting FK relationships as DQ expectations. |
| OB-004 | Migrate `integration.purchase_staging` to a Delta staging table preserving truncate-and-reload-per-cycle semantics. |
| OB-005 | Translate `integration.migratestagedpurchasedata` into a Databricks ETL task reproducing valid-time key resolution and an atomic targeted-replace write. |
| OB-006 | Migrate the shared lineage/batch infrastructure (`sequences.lineagekey`, `getlineagekey`, `integration.lineage`) into Purchasing_Project's own decoupled `purchasing.meta` schema. |
| OB-007 | Migrate the incremental-extraction watermark table/view (`integration.etl cutoff`, `etl_cutoff_view2024`) into Purchasing_Project's own metadata schema. |
| OB-008 | Resolve cross-project read exposure of `purchasing.fact.purchase` to the three GlobalSales_Project consumer artifacts without this project taking ownership of them. `[USER INPUT REQUIRED]` |
| OB-009 | Explicitly exclude Sales/Orders, Inventory/Stock, Finance Analytics, Emptoris, and `dbo` schema objects from all migration activities. |
| OB-010 | Document the five upstream OLTP objects feeding the extraction step as informational lineage only, never as migration targets. |

### SX — Syntax (11 rules)

| Rule ID | Intent |
|---|---|
| SX-001 | Remove `SET NOCOUNT ON`/`SET XACT_ABORT ON` procedure header directives with no Spark SQL equivalent. |
| SX-002 | Remove `WITH EXECUTE AS OWNER` from `GetPurchaseUpdates`, replaced by Unity Catalog service-principal permissions. |
| SX-003 | Preserve the `CAST(... AS date)` construct deriving Date Key from OrderDate — syntax passthrough with accompanying type mapping. |
| SX-004 | Convert the correlated TOP(1) valid-time subquery resolving Supplier Key/Stock Item Key into a set-based range-predicate join with a deduplicating window function. |
| SX-005 | Convert the `DECLARE @LineageKey` scalar-subquery capture into a Python variable assignment with a zero-row guard. |
| SX-006 | Convert the alias-prefixed join-delete (`DELETE p FROM Fact.Purchase p`) to ANSI/Spark SQL `DELETE FROM` syntax. |
| SX-007 | Convert the `BEGIN TRAN`/`COMMIT` wrapper around the delete-then-insert replace into a Delta transactional pattern (preferring a single MERGE). |
| SX-008 | Remove bracket-quoted, space-containing identifiers pervasive across the Purchases domain's SQL, converting to snake_case. |
| SX-009 | Convert schema-qualified two-part references (`dimension.*`, `fact.*`, `integration.*`, `sequences.*`) to three-part `purchasing.<schema>.<table>` Unity Catalog naming. |
| SX-010 | Convert the IDENTITY column definition backing Fact.Purchase's Purchase Key to a Databricks-compatible `GENERATED ALWAYS AS IDENTITY` column. |
| SX-011 | Convert the native `STRING_AGG`-wrapped correlated TOP-N-without-ORDER-BY derived table (in the cross-project `v_OrderToYearAnalytics` view) to a deterministic Spark SQL equivalent — informational, cross-project pattern. |

### PE — Performance (8 rules)

| Rule ID | Intent |
|---|---|
| PE-001 | Drop columnstore index definitions with no equivalent DDL object, since Delta Lake stores data as Parquet columnar files natively. |
| PE-002 | Apply `PARTITIONED BY` on `fact.purchase`'s `date_key` column to enable partition pruning for date-range predicates. |
| PE-003 | Apply Z-ORDER on `fact.purchase`'s (`supplier_key`, `stock_item_key`) columns to reduce files scanned by the per-supplier and per-stock-item reports. |
| PE-004 | Implement `integration.purchase_staging` as a transient, write-once-read-once table with no persistent optimization applied. |
| PE-005 | Enable Databricks Optimized Writes and Auto Compaction table properties on `fact.purchase` and `dimension.supplier`. |
| PE-006 | Enable broadcast join for the small `dimension.supplier`, `dimension.stock_item`, and `dimension.date` tables joined to `fact.purchase`. |
| PE-007 | Re-implement `fact.purchase`'s delete-then-insert-by-natural-key load as a single Delta MERGE, or a partition-bounded delete where full replace semantics must be preserved. |
| PE-008 | Rewrite the non-deterministic correlated TOP-N pattern reading `fact.purchase` (in `v_OrderToYearAnalytics`) as a deterministic window function with an explicit tiebreaker — cross-project pattern. |

### LN — Lineage (7 rules)

| Rule ID | Intent |
|---|---|
| LN-001 | Register and track every downstream object outside the `purchasing` catalog that reads a Purchasing_Project object, via a formal cross-project dependency registry. |
| LN-002 | Ensure the cross-project dependency registry is populated from every discovery channel, including lineage-graph-discovered consumers not listed in upstream scope documents. |
| LN-003 | Carry forward the source system's administrative Lineage Key/batch-tracking pattern into the target lakehouse as native Delta lineage metadata. |
| LN-004 | Carry forward the per-table ETL cutoff/watermark mechanism so incremental-load lineage remains intact and auditable after migration. |
| LN-005 | Document fact-to-dimension lineage edges (valid-time SCD2 key resolution) that the automatic lineage graph did not surface, as explicit column-level lineage records. |
| LN-006 | Preserve batch-level lineage continuity across full delete-then-insert reloads so the audit trail is not erased by the replace pattern. |
| LN-007 | Tag conformed dimension provenance (origin, authority status, known copies) for dimensions reused across Purchasing_Project and other projects/catalogs. |

---

## Open Questions / Recommendations Surfaced During Generation

1. **Cross-catalog conformed dimension sharing strategy** (PL-008, OB-002) — `dimension.supplier` is net-new to Purchasing_Project, but `dimension.stock item` and `dimension.date` are already owned and migrated by GlobalSales_Project. No decision has been made on whether Purchasing_Project reads these via cross-catalog reference, receives a synchronized copy, or takes over ownership. This is a stakeholder/architecture decision, not something these rules can resolve unilaterally.
2. **Cross-catalog downstream dependency exposure** (PL-009, OB-008) — three GlobalSales_Project-owned artifacts (`analytics.v_ordertoyearanalytics`, `wwidw purchase and sale per stockitem dynamic`, `wwidw-ordered-by-supplier`) read `fact.purchase` directly. Once `fact.purchase` moves to the `purchasing` catalog, these become cross-project/cross-catalog reads. No decision has been made on whether GlobalSales_Project's queries are updated to a cross-catalog reference, `fact.purchase` is exposed via a Delta Sharing/view mechanism, or these three artifacts are migrated to reference an equivalent Purchasing_Project-owned mart object.
3. **Stakeholder fields carried forward, not fabricated** — `modernization-plan.md` §9 stakeholders were requested to "reuse" GlobalSales_Project's values, but those fields are themselves unfilled `[USER INPUT REQUIRED]` placeholders in GlobalSales_Project's own plan. No concrete names existed to reuse, so Purchasing_Project's plan carries the same placeholders forward rather than inventing names.
