# Check Report: product-definition — Inventory_Stock_Project / Purchase

**Skill:** migvisor-task-checker-product-definition (#9 of 21)
**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Checked:** 2026-09-25
**Score:** 58 / 100
**Grade:** Needs work

---

## Cross-File Reads

| File | Status | Notes |
|---|---|---|
| `specifications/to-be.md` | Read | Confirms pipeline notebooks (nb_extract_watermark, nb_extract_purchase, migrate_staged_purchase_data), JDBC source, 2 Power BI consumers, migration from SQL Server 2014; migration section mandatory |
| `specifications/development_plan/requirements.md` | Read | 33 requirements; DQR-001 through DQR-009 defined |

---

## Rubric Sections (ODPS 4.1 blocks)

### Block 1 — details

**Score: 18 / 20**

productID, name, status (draft), domain (Procurement/Purchasing), description, valueProposition, type, visibility, categories, and tags are all populated. Owner field is present with a placeholder value — acceptable for draft status. The description and valueProposition are substantive and aligned with to-be.md §1.1.

Minor deduction (-2): The `owner` field contains a placeholder string rather than a resolvable identity (team name or email). The reference provides a structured owner block with name, email, and team. For a draft this is acceptable but noted.

### Block 2 — x-inputPorts

**Score: 10 / 20**

The trainee defines 5 input ports: `purchase_staging`, `supplier_dimension`, `stock_item_dimension`, `date_dimension`, and `etl_cutoff`. Each port has location, format, frequency, and description fields. The ports are internally consistent with the architecture.

Significant deduction (-10): The JDBC source port is missing. to-be.md explicitly describes the pipeline as performing a "JDBC extract (watermark-bounded)" from a transactional SQL Server source. The reference defines a single JDBC SQL Server input port with connection schema, host, driver, and field-level type definitions. The trainee's ports describe only the target-side Delta Lake tables, not the JDBC upstream source. This means the product definition does not capture the actual external input of the pipeline.

Additionally, no port carries field-level schemas (column name, type, nullable). The reference provides 11 field definitions per output port; the trainee provides none.

### Block 3 — dataAccess

**Score: 16 / 18**

Two access methods defined: `sql_endpoint` (default, SQL warehouse) and `bi_reports` (two Power BI report connections). Both match the consumers described in to-be.md §2. The bi_reports entry names both reports (`wwidw_purchase_and_sale_per_stockitem_dynamic` and `wwidw_ordered_by_supplier`) as required.

Minor deduction (-2): Access method entries do not include connection endpoint URLs or Unity Catalog three-part table references. The reference provides these details.

### Block 4 — dataQuality

**Score: 17 / 20**

Five DQ dimensions defined: completeness (BLOCKING), consistency, accuracy, uniqueness, traceability. Each has a strategy description and blocking flag. The BLOCKING flag on completeness is correct — it maps to QA-P001 (row count reconciliation) in requirements.md.

Deduction (-3): The trainee's dataQuality block uses its own internal dimension taxonomy rather than referencing the DQR-001 through DQR-009 IDs from requirements.md. The assertions section in the pipeline block lists assertion names (e.g. `QA-P001`) but these do not map explicitly to DQR IDs, making cross-document traceability harder. The reference maps each assertion to a DQR ID.

### Block 5 — pipeline

**Score: 8 / 16**

The pipeline block includes orchestration, schedule (nightly), lineage_key, and assertions fields. The assertions list references QA-P001 through QA-P004 by name.

Significant deductions:
- (-5) No named layers with `dependsOn` chains. The reference defines 4 named pipeline layers (ingestion, dimensions, facts, mart+dq) with explicit layer-level dependencies. The trainee's pipeline block is flat with no structural layer hierarchy.
- (-3) The assertions section does not include severity (BLOCKING vs Informational) or the rejectionsTable reference. These are present in the reference and expected per ODPS 4.1.

### Block 6 — migration (MISSING)

**Score: 0 / 6**

The migration section is entirely absent. to-be.md §1.1 explicitly describes the migration from SQL Server 2014 `wideworldimportersdw` with source object mapping (purchase_staging, etl_cutoff, lineage, sequences.lineagekey, etc.) and 9 mapped source objects. The reference product-definition includes a migration block with source object mapping and 5 known risks. ODPS 4.1 requires the migration section for products undergoing platform migration.

---

## Auto-Deducts

| Rule | Applied | Amount | Reason |
|---|---|---|---|
| Missing migration section | Yes | -5 | Required ODPS 4.1 block absent; confirmed required by to-be.md migration context |
| No output port field schemas | Yes | -4 | No field-level definitions for any port; reference provides 11 fields per port |

---

## Cross-File Consistency Checks

**to-be.md alignment:** The product name, catalog (`inventory_stock`), pipeline workflow name (`nightly_etl_purchase`), and consumer names match to-be.md. However, the JDBC source that to-be.md describes as the primary external input is not represented as an input port. The lineage_key propagation described in to-be.md §4.4 is referenced in the pipeline block (lineage_key field) but the pipeline block lacks the structural detail to express this.

**requirements.md alignment:** The dataQuality block's DQ dimensions map approximately to DQR groups in requirements.md, but the mapping is implicit. DQR-007 (package non-null), DQR-008 (DQ rejection traceability), DQR-009 (SK default coverage) are not represented.

---

## Summary

The product-definition.yaml establishes a well-structured ODPS 4.1 document with strong details, dataAccess, and dataQuality blocks. The five dataQuality dimensions include correct BLOCKING flags for completeness. Consumer identification matches to-be.md. The critical gaps are: the missing migration section (required for any platform migration product per ODPS 4.1), the absent JDBC source input port, the flat pipeline block without named layers and dependsOn chains, and no field-level schemas on any port. These gaps reduce the definition from a complete specification to a partial framework that would require substantial additions before formal review.

---

## Priority Actions

1. Add migration section: map 9 source objects from SQL Server 2014 to target Delta Lake equivalents; list known risks (PD-001 JDBC, PD-002 reseed, PD-003 grants, QA-DQ-01 thresholds, sequences.lineagekey retirement).
2. Add JDBC SQL Server input port to x-inputPorts with host, driver, schema, and connection reference fields.
3. Restructure pipeline block into 4 named layers (ingestion, dimensions, facts, mart_dq) with explicit dependsOn relationships matching the to-be.md workflow task sequence.
4. Add field-level schemas to at least the primary output port (fact_purchase: 11 columns with name, type, nullable flags).
