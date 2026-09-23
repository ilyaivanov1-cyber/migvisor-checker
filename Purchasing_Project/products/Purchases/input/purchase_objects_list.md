# Purchase — Objects in Scope

## Core Fact Table

- `wideworldimportersdw.fact.purchase` — table — purchase order line items (base node)

---

## Conformed Dimensions (read dependencies)

- `wideworldimportersdw.dimension.supplier` — table — SCD-2 lookup in `migratestagedpurchasedata` (read dependency; ETL not Purchase-owned)
- `wideworldimportersdw.dimension.stock item` — table — SCD-2 lookup in `migratestagedpurchasedata` (read dependency; ETL not Purchase-owned)
- `wideworldimportersdw.dimension.date` — table — FK target for `[Date Key]` (shared infrastructure; pre-populated by shared infra layer)

---

## Integration Staging Layer

- `wideworldimportersdw.integration.purchase_staging` — table — staging area for purchase data before fact insert
- `wideworldimportersdw.integration.etl cutoff` — table — ETL watermark (shared infrastructure; consumed by Purchase)
- `wideworldimportersdw.integration.lineage` — table — ETL run log (shared infrastructure; consumed by Purchase)
- `wideworldimportersdw.integration.migratestagedpurchasedata` — stored procedure — resolves surrogate keys, upserts into `fact.purchase`, updates lineage and cutoff
- `wideworldimportersdw.integration.getlastetlcutofftime` — stored procedure — reads ETL cutoff watermark (shared infrastructure)
- `wideworldimportersdw.integration.getlineagekey` — stored procedure — generates lineage run key via `sequences.lineagekey` (shared infrastructure)
- `wideworldimportersdw.application.configuration_reseedetl` — stored procedure — **Purchase-domain portions only**: TRUNCATE `fact.purchase`; insert key=0 sentinel rows into `dimension.supplier` and `dimension.stock item`; reset ETL cutoff to base time

---

## Sequences / Infrastructure

- `wideworldimportersdw.sequences.lineagekey` — sequence — generates lineage run keys (shared infrastructure; used by all migrate procedures)

---

## SSIS Orchestration Pipeline (Purchase container only)

- `demo_ssis…pipeline_dailyetlmain` — workflow — master daily ETL workflow (shared; Purchase container runs within it)
- `demo_ssis…pipeline_item_set tablename to purchase` — dataflow — sets `tablename` variable before the purchase load container
- `demo_ssis…pipeline_item_truncate purchase_staging` — dataflow — intended to truncate `purchase_staging` ⚠ **bug: actually deletes from `Integration.Order_Staging`**
- `demo_ssis…pipeline_item_extract updated purchase data to staging` — dataflow — loads purchase updates into `purchase_staging`
- `demo_ssis…pipeline_item_migrate staged purchase data` — dataflow — calls `migratestagedpurchasedata`

---

## BI Reports (downstream consumers)

- `wwidw purchase and sale per stockitem dynamic` — BI report — reads `fact.purchase`
- `wwidw-ordered-by-supplier` — BI report — reads `fact.purchase` and `dimension.supplier`
