# Check Report: TASK-TO-BE-001
**Skill:** to-be | **Trainee:** Inventory_Stock_Project | **Product:** Purchase
**Checker version:** v1 | **Generated:** 2026-09-25

---

## Score: 94 / 100 — Excellent

---

## Rubric Evaluation

### Content Completeness — 24 / 25

All 7 required sections are present with substantive content:

**§1 Definition:** System identity table, business purpose narrative, technology stack table, stakeholders table, data domain, key metrics/KPIs table, operational context table including open stakeholder gates. Metadata table in §1.2 has 15 fields ✓. Key components list identifies all major artifacts (fact table, staging table, control tables, dimensions, notebooks, shared modules, config, workflow). Total components listed: 15 (meets the 16-deliverable expectation closely; minor gap: `scd2_merge.py` listed but not as a standalone component entry in §1.2 Key Components).

**§2 Consumers:** Three consumers in main table (wwidw_purchase_and_sale_per_stockitem_dynamic, wwidw_ordered_by_supplier, migrate_staged_purchase_data) — matches SKILL.md expectation of 3 consumers ✓. Cross-domain view section (§2.1) documents `analytics.v_ordertoyearanalytics` with Package column preservation commitment, case-sensitivity risk, and migration responsibility assignment (Order team) ✓. Consumer priority matrix present.

**§3 Model:** Mermaid ER diagram ✓ (complete column-level diagram for all 8 tables). Textual description table ✓. All 8 expected tables represented: fact_purchase (11 cols ✓), purchase_staging (15 cols ✓), etl_cutoff (3 cols ✓), lineage_run (9 cols ✓), dq_rejections (10 cols ✓), supplier (SCD-2), stock_item (SCD-2), date.

**§4 Lineage:** Key columns section (§4.1) covers 10 columns ✓. Mermaid lineage diagram (§4.2) with full task subgraph structure ✓. Column-level lineage table (§4.3) with 19 rows ✓. Step-by-step transformation table (§4.4) with 22 steps ✓ (matches SKILL.md expectation exactly). Downstream dependencies table (§4.5) ✓.

**§5 Calculations:** §5.1 date key derivation, §5.2 ordered quantities, §5.3 SCD-2 SK resolution with full Python code (sk_resolver.py), §5.4 lineage key injection, §5.5 consolidated Python UDFs. All calculation sections include mathematical formula, input table, code block, step-by-step, and thresholds/categorisation ✓.

**§6 Sources:** §6.1 input sources table (6 target-platform sources) ✓. Lineage traceability table ✓. §6.2 output tables (4 outputs) ✓.

**§7 NFR:** §7.1 SLA targets (freshness, completion, availability, alerting), §7.2 data retention policy by layer, §7.3 Unity Catalog permission model with principal/role/access matrix ✓.

Minor gap (-1 pt): §1 Key Components list does not explicitly name `scd2_merge.py` as a standalone key component (it is mentioned in the transformation summary comment and in §4.5 downstream dependencies but omitted from the §1 components list proper).

### SQL Accuracy — 28 / 30

The MERGE INTO in §4.4 step 15 uses a **4-column composite MERGE key**: `ON tgt.wwi_purchase_order_id = src.wwi_purchase_order_id AND tgt.date_key = src.date_key AND tgt.supplier_key = src.supplier_key AND tgt.stock_item_key = src.stock_item_key`. This correctly reflects the actual fact table grain (purchase order line × supplier × stock item × date) ✓.

The sk_resolver.py Python code in §5.3 is syntactically correct and logically complete:
- LEFT JOIN with temporal range condition using `CAST(valid_from AS TIMESTAMP)` and `CAST(valid_to AS TIMESTAMP)` ✓
- `ROW_NUMBER() OVER (PARTITION BY purchase_staging_key ORDER BY valid_from DESC)` ✓
- `COALESCE(supplier_key, 0)` fallback ✓
- SCD-2 boundary semantics: `> CAST(valid_from AS TIMESTAMP)` (exclusive lower) and `<= CAST(valid_to AS TIMESTAMP)` (inclusive upper) — consistent with as-is §5.3 documentation ✓

Date key derivation SQL: `CAST(po.OrderDate AS DATE)` ✓.

Minor deductions (-2 pts): The date_key join semantics in §4.1 state "FK → silver_dim.date.date (the PK of silver_dim.date is the DATE column named `date`, not `date_key`)" — this creates a slight ambiguity because the ER diagram in §3.1 shows `SILVER_DIM_DATE { DATE date_key }` (naming the PK column `date_key`). The text and the diagram use different names for the date dimension's primary key column, which is a consistency issue within the document.

### Code Accuracy — 19 / 20

Python code in §5.4 (lineage key injection) is complete and correct:
```python
dbutils.jobs.taskValues.set(key="lineage_key", value=lineage_key)
dbutils.jobs.taskValues.get(taskKey="nb_extract_watermark", key="lineage_key")
```
✓ — correct API, correct task key reference.

UDF skeleton in §5.5 (CX-P003) shows correct `@udf` decorator pattern, explicit NULL guard (`if val is None: return None`), `spark.udf.register()` call, and unit test guidance ✓.

Lineage record lifecycle (§5.4 step-by-step) correctly documents: open → publish via taskValues → stamp on staging and fact → close with succeeded=True/False ✓.

Minor gap (-1 pt): The `lineage_run.was_successful` field is documented as `BOOLEAN NULL` (three-valued: NULL=running, TRUE=success, FALSE=failure) in §1.2 metadata and §3.2 textual description, which is correct. However, §5.4 close_lineage_record step shows `succeeded=True` in the success path — no False path is shown in the calculations, which could leave reviewers uncertain whether the failure path is handled.

### Diagram Completeness — 14 / 15

Mermaid ER diagram (§3.1): Complete column-level diagram with all 8 tables, all relationship edges correctly typed (||--o{, }o--||). Bronze/Silver/Dim/Fact layers visually separated via comments ✓.

Mermaid lineage flow diagram (§4.2): 5 subgraphs (OLTP source, Task 1, Task 2, Task 3, Silver Dims, Target Fact, BI Consumers) with all edges correctly drawn. Node labels include transformation details (SX rule references, function names) ✓.

Minor deduction (-1 pt): The lineage diagram does not show the explicit dependency edges between Task 2 (nb_extract_purchase) and the Silver Dim tables (they are shown as a separate subgraph without a dependency edge from Task 2 prerequisite). The dimension load dependency is implied but not graphically explicit in the diagram.

### Structure — 10 / 10

Logical section hierarchy §1–§7. Transformation summary HTML comments present at each section end, documenting all rule IDs applied. All code blocks syntax-highlighted. Tables consistently formatted. Mermaid code blocks syntactically valid.

---

## Auto-Deduct Checks

| Check | Threshold | Result |
|---|---|---|
| 3 consumers in §2 table | −2 pts per missing (max −6) | PASS — 3 consumers present |
| 22-step transformation table (§4.4) | Required | PASS — 22 steps present |
| TY-P001 (valid_from/valid_to → DATE) applied | Required | PASS — applied to supplier and stock_item dimensions |
| sk_resolver.py with ROW_NUMBER + COALESCE | Required | PASS — full Python code with both patterns |
| lineage_key via taskValues (LN-P001) | Required | PASS — publish and consume patterns both shown |
| NFR section (§7) present | Required | PASS — §7 present with SLA, retention, RBAC |

**Total auto-deductions: 0 pts**

---

## Cross-File Consistency Checks

### Consumer Consistency (MANDATORY — read as-is.md)

**as-is consumers identified:**
1. `wwidw purchase and sale per stockitem dynamic` (BI report)
2. `wwidw-ordered-by-supplier` (BI report)
3. `migratestagedpurchasedata` (ETL stored procedure — internal ETL dependency)
4. `analytics.v_ordertoyearanalytics` (cross-domain view — Order team owned)

**to-be consumers:**
1. `wwidw_purchase_and_sale_per_stockitem_dynamic` ✓ (renamed per NM-001)
2. `wwidw_ordered_by_supplier` ✓ (renamed per NM-001)
3. `migrate_staged_purchase_data` ✓ (renamed procedure replaced by Workflow task)
4. `analytics.v_ordertoyearanalytics` ✓ (documented in §2.1 Cross-Domain Views)

**Result:** All 4 as-is consumers are accounted for in to-be. No missing consumers. **0 pts deducted.**

### Requirements Alignment (MANDATORY)

The to-be §7 NFR categories were compared against requirements.md NFR categories (from cross-file read — requirements not yet confirmed at this stage, but §7 covers): SLA targets (aligns with NFR-001 data freshness, NFR-002 availability), data retention (aligns with NFR-012), Unity Catalog RBAC (aligns with NFR-008). **Pass — NFR categories aligned.**

---

## Summary

The to-be document is comprehensive and technically precise, covering all 7 required sections with correct transformation rule citations throughout. The 22-step transformation table is complete. The sk_resolver.py Python code correctly implements the temporal range join + ROW_NUMBER DESC + COALESCE(0) pattern with DATE-typed validity columns. The 4-column composite MERGE key in §4.4 step 15 correctly reflects the actual fact grain. All 3 main consumers are present plus the cross-domain view dependency is thoroughly documented. Minor issues: a naming inconsistency in the date dimension PK column between the ER diagram (`date_key`) and the lineage text (`date`), and a slight omission in the lineage diagram's dimension dependency edges.

---

## Priority Actions

1. Resolve the date dimension PK naming inconsistency: pick one name (`date` or `date_key`) for the date dimension's primary key column and use it consistently in the ER diagram, §4.1 key columns, §4.3 column-level lineage table, and §6.1 input sources table.
2. Add `scd2_merge.py` explicitly to §1 Key Components list alongside `sk_resolver.py` and `fact_merge.py` — these three shared modules are listed in OB-P004 and all three should appear in the component inventory.
3. In §5.4 lineage key injection, add the failure path: show the `close_lineage_record(spark, lineage_key, rows_merged=0, succeeded=False)` call in the `except` block to confirm that lineage records are always closed (success or failure) without requiring reviewers to infer this from the ETL skeleton.
4. In the §4.2 Mermaid lineage diagram, add explicit dependency arrows from the dimension loading prerequisite nodes to the `migrate_staged_purchase_data` task to make the dimension-before-fact dependency visually explicit.
