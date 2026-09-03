# Product Transformation Rules: Purchase
# Inherits from: GlobalPurchase_Project (project-transformation-rules v2026-08-25)
# Generated: 2026-08-25

---

## Customization Summary

| Type | Count | Description |
|---|---|---|
| Overrides | 0 | No project rules replaced for this product |
| Extensions | 5 | Additional detail appended to project rules |
| Deactivations | 0 | No project rules turned off for this product |
| New rules | 8 | Product-only rules (3 CX, 1 QA, 1 LN from new-rules.yaml; 5 extension rules inline in dimension files) |

**Active dimensions: 9** (6 inherited from project + 3 product-only)

---

## Action Files

| File | Content | Status |
|---|---|---|
| [extensions.yaml](extensions.yaml) | 5 extensions to project rules (SX-004-EXT-P01, TY-003-EXT-P01, TY-005-EXT-P01, OB-003-EXT-P01, IF-001-EXT-P01) | Present |
| [new-rules.yaml](new-rules.yaml) | 5 new product-only rules (CX-P01, CX-P02, CX-P03, QA-P01, LN-P01) | Present |
| override.yaml | Not applicable — no overrides | Absent (expected) |
| deactivations.yaml | Not applicable — no deactivations | Absent (expected) |

---

## Dimension Table

| Dimension | Prefix | File | Rule Count | Customizations |
|---|---|---|---|---|
| Platform | PL | [PL-platform.yaml](PL-platform.yaml) | 4 | None — project rules inherited as-is |
| Naming | NM | [NM-naming.yaml](NM-naming.yaml) | 5 | Exception list extended: Integration.Lineage → stg.lineage (no _staging suffix) |
| Types | TY | [TY-types.yaml](TY-types.yaml) | 8 | +TY-003-EXT-P01 (sysname → STRING); +TY-005-EXT-P01 (Photo VARBINARY column dropped) |
| Objects | OB | [OB-objects.yaml](OB-objects.yaml) | 6 | +OB-003-EXT-P01 (lineage_key via taskValues, not Python counter) |
| Syntax | SX | [SX-syntax.yaml](SX-syntax.yaml) | 6 | +SX-004-EXT-P01 (full-order-level replacement MERGE for purchase) |
| Interface | IF | [IF-interface.yaml](IF-interface.yaml) | 5 | +IF-001-EXT-P01 (supplier + stock_item must complete before purchase fact) |
| Custom | CX | [CX-custom.yaml](CX-custom.yaml) | 3 | Product-only: ordered_quantity derivation; key=0 DQ observability; QuantityPerOuter stakeholder confirmation |
| Quality | QA | [QA-quality.yaml](QA-quality.yaml) | 1 | Product-only: 5 DQ assertions for purchase (2 blocking, 3 informational) |
| Lineage | LN | [LN-lineage.yaml](LN-lineage.yaml) | 1 | Product-only: package column name preservation for cross-domain view compatibility |

**Total: 39 rules across 9 dimensions** (29 project-inherited + 5 extension rules + 5 product-only new rules)

---

## Rule Index

### Platform (PL) — 4 rules, no product customizations

| Rule ID | Intent |
|---|---|
| PL-001 | Every table uses USING DELTA clause in DDL |
| PL-002 | SSIS orchestration replaced by Databricks Workflow (3-tier dependency) |
| PL-003 | Medallion architecture: stg / dim / fact / mart schemas in globalpurchase |
| PL-004 | SEQUENCE objects eliminated; GENERATED ALWAYS AS IDENTITY replaces NEXT VALUE FOR |

### Naming (NM) — 5 rules, 1 minor exception extension

| Rule ID | Intent | Tag |
|---|---|---|
| NM-001 | Convert all object names to lowercase_snake_case | inherited |
| NM-002 | Replace spaces in object names with underscores | inherited |
| NM-003 | Add v_ prefix to all view names | inherited |
| NM-004 | Add _staging suffix to staging tables; etl_cutoff and lineage excepted | inherited + exception extended |
| NM-005 | Map source schemas to target schema layers (integration→stg, dimension→dim, fact→fact, analytics→mart) | inherited |

### Types (TY) — 8 rules (6 project + 2 product extensions)

| Rule ID | Intent | Tag |
|---|---|---|
| TY-001 | INT/SMALLINT/TINYINT → INT; BIGINT → BIGINT | inherited |
| TY-002 | DECIMAL(p,s)/NUMERIC → DECIMAL(p,s); FLOAT/REAL → DOUBLE | inherited |
| TY-003 | VARCHAR/NVARCHAR/CHAR/TEXT → STRING | inherited |
| TY-003-EXT-P01 | sysname system alias → STRING NOT NULL (etl_cutoff.table_name, lineage.table_name) | **product extension** |
| TY-004 | DATE → DATE; DATETIME/DATETIME2/SMALLDATETIME → TIMESTAMP; TIME → STRING | inherited |
| TY-005 | BIT → BOOLEAN; UNIQUEIDENTIFIER → STRING; VARBINARY/BINARY → BINARY | inherited |
| TY-005-EXT-P01 | Photo VARBINARY (no length = varbinary(1)) excluded from stock_item target DDL | **product extension** |
| TY-006 | IDENTITY(seed,inc) → BIGINT GENERATED ALWAYS AS IDENTITY | inherited |

### Objects (OB) — 6 rules (5 project + 1 product extension)

| Rule ID | Intent | Tag |
|---|---|---|
| OB-001 | All in-scope tables recreated as Delta tables in globalpurchase (7 tables) | inherited |
| OB-002 | migratestagedpurchasedata → nb_load_fact_purchase.py + sk_resolver.py; getpurchaseupdates not migrated | inherited |
| OB-003 | SEQUENCE objects eliminated; surrogate keys use GENERATED ALWAYS AS IDENTITY | inherited |
| OB-003-EXT-P01 | lineage_key injected from nb_extract_watermark via dbutils.jobs.taskValues (not Python counter) | **product extension** |
| OB-004 | application.* objects not migrated; configuration_reseedetl re-expressed as optional bootstrap notebook | inherited |
| OB-005 | In-scope views get v_ prefix; analytics.v_ordertoyearanalytics excluded (cross-domain, Order team owns) | inherited |

### Syntax (SX) — 6 rules (5 project + 1 product extension)

| Rule ID | Intent | Tag |
|---|---|---|
| SX-001 | Remove BEGIN TRAN / COMMIT / ROLLBACK from migratestagedpurchasedata | inherited |
| SX-002 | Replace staging+migratestaged* pattern with nb_extract_purchase_staging → nb_load_fact_purchase | inherited |
| SX-003 | SCD-2 UPDATE+INSERT → Delta MERGE INTO for supplier and stock_item | inherited |
| SX-004 | Fact DELETE+INSERT → Delta MERGE keyed on business key | inherited |
| SX-004-EXT-P01 | purchase MERGE must implement full-order-level replacement (two-phase DELETE by wwi_purchase_order_id + INSERT) | **product extension** |
| SX-005 | T-SQL functions/syntax translated to Spark SQL / Python (GETDATE→current_timestamp, ISNULL→COALESCE, TOP→LIMIT, etc.) | inherited |

### Interface (IF) — 5 rules (4 project + 1 product extension)

| Rule ID | Intent | Tag |
|---|---|---|
| IF-001 | SSIS pipeline_dailyetlmain → Databricks Workflow (3-tier dependency) | inherited |
| IF-001-EXT-P01 | nb_load_fact_purchase depends_on nb_load_dim_supplier AND nb_load_dim_stock_item (explicit Purchase dependency) | **product extension** |
| IF-002 | JDBC incremental reads filtered by last_modified_when watermark; commit after all downstream loads succeed | inherited |
| IF-003 | JDBC credentials in Databricks Secrets (globalpurchase-<env> scope); JDBC driver in cluster config | inherited |
| IF-004 | Dimension data in in-memory temp views; fact data in stg.purchase_staging via truncate+overwrite | inherited |

### Custom (CX) — 3 rules (product-only)

| Rule ID | Intent | Tag |
|---|---|---|
| CX-P01 | Derive ordered_quantity = ordered_outers * quantity_per_outer in nb_extract_purchase_staging.py | **new** |
| CX-P02 | Retain key=0 Unknown member pattern with DQ observability (write misses to stg.dq_rejections) | **new** |
| CX-P03 | QuantityPerOuter point-in-time risk — stakeholder confirmation required before go-live | **new (stakeholder gate)** |

### Quality (QA) — 1 rule with 5 assertions (product-only)

| Rule ID | Intent | Tag |
|---|---|---|
| QA-P01 | 5 DQ assertions: received_outers ≤ ordered_outers (W); positive measures (W); staging=fact row count (blocking); key=0 fraction threshold (W); is_order_finalized NOT NULL (blocking) | **new** |

### Lineage (LN) — 1 rule (product-only)

| Rule ID | Intent | Tag |
|---|---|---|
| LN-P01 | Preserve 'package' column name and STRING type in purchase; document cross-domain case-sensitivity risk for Order product team | **new** |

---

## Stakeholder Confirmations Required Before Go-Live

| ID | Question | Owner |
|---|---|---|
| CX-P03 | ordered_quantity: batch-run-time quantity_per_outer (current, preserving source) vs. order-date point-in-time? | Product owner / Procurement team |
| LN-P01 | Order product team notified of 'package' column name contract and case-sensitivity risk? | Purchase migration lead |

---

*Generated by migVisor Transformation Co-Pilot · 2026-08-25 · Purchase product · GlobalPurchase_Project*
