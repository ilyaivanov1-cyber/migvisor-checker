---
task_id: TASK-PD-001
product: Purchase
participant_file: Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/product-definition.yaml
reference_file: reference/answers/module_5/development_plan/product-definition.yaml
checked_at: 2026-09-24T00:00:00
sections_evaluated: 6
total_score: 84/100
grade: Good
identical_to_reference: false
---

# Task Check Report — product-definition (v7)
_Purchase | 2026-09-24_

**File resolution log:**
- Participant file: Inventory_Stock_Project/products/Purchase/current/specifications/development_plan/product-definition.yaml — workspace auto-detected
- Reference file: reference/answers/module_5/development_plan/product-definition.yaml — from workspace.yaml
- Product: Purchase — from workspace.yaml
- Sections in reference: 6 content keys (product, inputPorts, outputPorts, pipeline, dataQuality, migration) | Sections in participant: 5 content keys (product.details, x-inputPorts, dataAccess, dataQuality, pipeline) + SLA (extra)
- Point weights: auto-calculated — Doc Metadata:17, product:17, x-inputPorts:17, dataAccess:17, dataQuality:16, pipeline:16

---

## Score Summary

**The product-definition Score: 84**

| Section | Weight | Score | Status |
|---|---|---|---|
| Document Metadata | 17 | 17 | ✓ |
| product | 17 | 16 | ✓ |
| x-inputPorts → inputPorts | 17 | 15 | ✓ |
| dataAccess → outputPorts | 17 | 13 | ✓ |
| dataQuality | 16 | 16 | ✓ |
| pipeline | 16 | 7 | ⚠ |
| **Total** | **100** | **84** | |

Status: ✓ ≥ 80% | ⚠ 50–79% | ✗ < 50%

---

## Section Matching Log

| Reference Section | Participant Matched Section | Match Type |
|---|---|---|
| (file root) | schema: + version: | exact |
| product | product.details | semantic |
| inputPorts | x-inputPorts | semantic |
| outputPorts | dataAccess | semantic |
| pipeline | pipeline | exact |
| dataQuality | dataQuality | exact |
| migration | [MISSING] | missing |

**Extra sections (participant-only):** `SLA` — 4 SLA entries (updateFrequency, latency, uptime, retentionPolicy). No score impact.

---

## Section Feedback

### Document Metadata (17/17)
ODPS 4.1 schema declaration (`schema: https://opendataproducts.org/v4.1/schema/odps.yaml`) present and correct. Version declared as `"4.1"`. Product identifier (productID: purchase) and status (draft) present. Full marks.

### product → product.details (16/17)
All identity fields present: productID, name, status, domain, type, visibility. Description and valueProposition accurately describe the grain-level fact table, lineage_key propagation, and the staging-truncation bug fix. Categories and tags well-specified. Minor: `owner` field contains `[USER INPUT REQUIRED]` placeholder — intentional deferral, scores 50% on that sub-criterion.

### x-inputPorts → inputPorts (15/17)
5 input ports defined (purchase_staging, supplier_dimension, stock_item_dimension, date_dimension, etl_cutoff). Each port has inputName, inputType, location, format, frequency, and description. Port descriptions are detailed and accurate. Minor: no `authenticationMethod` or credentials reference documented per port — authentication spec criterion partially unmet.

### dataAccess → outputPorts (13/17)
Two output access profiles: `fact_purchase_sql_warehouse` (SQL endpoint) and `power_bi_purchase_reports` (BI connection). Primary dataset and supporting tables listed for SQL endpoint. Auth method noted (Unity Catalog RBAC). Significant gap: no field-level schema defined for any output port — `ports_with_schema = 0/2`, leaving the field schemas criterion at 0%. Cross-product dependency correctly documented for wwidw_purchase_and_sale_per_stockitem_dynamic.

### dataQuality (16/16)
5 dimensions defined: completeness (BLOCKING, zero_tolerance), consistency (reject_and_continue), accuracy (log_and_continue), uniqueness (log_and_continue), traceability (centralised_sink). All 5 dimensions have `blocking:`, `strategy:`, and descriptive text citing QA-P001 through QA-P005. Only `completeness` is BLOCKING — correct per domain spec. Rejection sink (`bronze.dq_rejections`) documented. Full marks.

### pipeline (7/16)
Pipeline section present with orchestration (Databricks Workflows), schedule (nightly), lineage_key block (source, propagation, traceability), and assertions list (QA-P001 through QA-P005 with descriptions). Significant gaps: no explicit layer dependency chain (`dependsOn` absent from all layer definitions); pipeline layers not enumerated as ordered steps with prerequisites. The `migration` reference section is entirely absent — source system lineage, object-level mappings, and known migration risks are not documented anywhere in the file. This combined gap (pipeline deps + missing migration) accounts for the majority of lost points in this section and the document overall.

---

## Priority Improvements

1. Add field-level schemas to `dataAccess` output profiles — list column names, types, nullable, and descriptions for `silver_fact.fact_purchase` at minimum. This recovers up to +5 pts on the dataAccess section's schema criterion.
2. Add a `migration` (or `sourceLineage`) top-level block documenting the source system (SQL Server 2014 `wideworldimportersdw`), object-level source-to-target mappings (purchase_orders → fact_purchase, suppliers → dim.supplier, etc.), and known migration risks (e.g., staging-truncation bug, SSIS procedure replacement). This is the reference's largest missing section and would add up to +8 pts.
3. Add `dependsOn` ordering to pipeline layers — ingestion → dimensions → facts → mart/DQ — to satisfy the dependency chain criterion (+2 pts).
4. Add `authenticationMethod` and credential reference to each input port entry (+1 pt).

---

## Next Step
Score 84/100 (Good). Minor to moderate gaps. Proceeding is acceptable; add field schemas and migration block before final submission.
