---
task_id: TASK-SC-001
skill: migvisor-task-checker-scope
trainee_file: ./Inventory_Stock_Project/products/Purchase/input/product-scope.md
reference_file: ./reference/answers/module_2/0 product-scope.md
generated: 2026-09-18
total_score: 80/100
grade: Good
---

# TASK-SC-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/input/product-scope.md`  
**Reference file:** `./reference/answers/module_2/0 product-scope.md`  
**Generated:** 2026-09-18

---

## Score Summary

**Scope Score: 80/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| 1 Identity | 11 | 90/100 | 9.9 | ✓ |
| 2 Description | 11 | 92/100 | 10.1 | ✓ |
| 3 Objects in Scope | 12 | 80/100 | 9.6 | ⚠ |
| 4 Out-of-Scope Objects | 11 | 82/100 | 9.0 | ✓ |
| 5 Consumers | 11 | 75/100 | 8.25 | ⚠ |
| 6 Calculation Surface | 11 | 85/100 | 9.35 | ✓ |
| 7 Boundaries | 11 | 88/100 | 9.68 | ✓ |
| 8 Priority and Sequencing | 11 | 82/100 | 9.02 | ✓ |
| 9 Known Migration Risks | 11 | 85/100 | 9.35 | ✓ |
| **Subtotal** | | | **84.25** | |
| Auto-deducts | | | **−4** | |
| **Total** | | | **80/100** | |

**Grade: Good**

> **Weight calculation:** N = 9, base_weight = floor(100/9) = 11, remainder = 1 → 1 pt added to §3 Objects in Scope (highest complexity).

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| 1 Identity | §1 Identity | Direct |
| 2 Description | §2 Description | Direct |
| 3 Objects in Scope | §3 Objects in Scope | Direct |
| 4 Out-of-Scope Objects | §4 Out-of-Scope Objects | Direct |
| 5 Consumers | §5 Consumers | Direct |
| 6 Calculation Surface | §6 Calculation Surface | Direct |
| 7 Boundaries | §7 Boundaries | Direct |
| 8 Priority and Sequencing | §8 Priority and Sequencing | Direct |
| 9 Known Migration Risks | §9 Known Migration Risks | Direct |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| Object IDs (UUIDs) absent from all object tables | −2 pts | Yes — reference includes migVisor graph UUIDs for every in-scope object; trainee has none |
| Missing cross-domain consumer `analytics.v_ordertoyearanalytics` in §5 | −2 pts | Yes — reference lists this view as a third consumer; trainee §5 omits it entirely |

**Total auto-deducts: −4 pts**

---

## Section Feedback

### 1 Identity — 90/100 (weight 11 → 9.9 pts)

**Status:** ✓ Present

**Strengths:** All five identity fields present. `Parent project` correctly reflects the trainee's actual project name (`Inventory_Stock_Project`). Discovery mode correctly references Pattern A / migVisor Explainer MCP with base node anchor.

**Gaps:** Discovery mode omits the UUID (`197f0cba-80b1-4837-b448-3268bdf6649c`) of `fact.purchase` as the MCP base node anchor — the reference always includes this.

---

### 2 Description — 92/100 (weight 11 → 10.1 pts)

**Status:** ✓ Present

**Strengths:** Excellent narrative. Clearly identifies SSIS staging-truncation bug, explains SCD-2 read-dependency pattern for `dimension.supplier` and `dimension.stock item`, and correctly names the two BI reports. Migration target is stated correctly.

**Gaps:** Does not mention `analytics.v_ordertoyearanalytics` cross-domain view that also reads from `fact.purchase`.

---

### 3 Objects in Scope — 80/100 (weight 12 → 9.6 pts)

**Status:** ⚠ Partial

**Strengths:** All core objects correctly identified and grouped: fact table (§3.1), conformed dimensions (§3.2), integration staging layer (§3.3), sequences (§3.4), SSIS pipeline items (§3.5), BI reports (§3.6). Correct object names including space in `dimension.stock item`. SSIS bug accurately documented in pipeline item row.

**Gaps:**
- No Object IDs (migVisor graph UUIDs) in any table — reference includes UUIDs for every in-scope object for traceability.
- Missing §3.5 Analytics Views subsection present in reference — `analytics.v_ordertoyearanalytics` reads from `fact.purchase` via a correlated subquery and should be noted as an in-scope consumer (even if out-of-scope for migration).
- `application.configuration_reseedetl` description is less specific than reference about the COALESCE fallback sentinel row mechanism.

---

### 4 Out-of-Scope Objects — 82/100 (weight 11 → 9.0 pts)

**Status:** ✓ Present

**Strengths:** Good coverage of out-of-scope fact tables, staging tables, migrate procedures, non-Purchase dimensions, and analytics views.

**Gaps:** Does not list the OLTP-side source procedure `wideworldimporters.integration.getpurchaseupdates` and its four OLTP source tables as out-of-scope (these are explicitly in the reference and important because they are not migrated — replaced by Databricks JDBC connectors). Missing `integration.populatedatedimensionforyear` and `sequences.supplierkey`/`sequences.stockitemkey` utilities.

---

### 5 Consumers — 75/100 (weight 11 → 8.25 pts)

**Status:** ⚠ Partial

**Strengths:** Both BI reports correctly listed with their read dependencies (`fact.purchase`, `dimension.supplier`).

**Gaps:** Missing `analytics.v_ordertoyearanalytics` as a third consumer (cross-domain analytical view that reads `fact.purchase` via correlated subquery on `Package` column). This view is in-scope for documentation because it reads from the product's fact table, even though it's driven by the Order domain and out-of-scope for migration ownership.

---

### 6 Calculation Surface — 85/100 (weight 11 → 9.35 pts)

**Status:** ✓ Present

**Strengths:** Accurately covers the four key calculation areas: staging merge (SCD-2 key resolution), ETL cutoff watermarking, lineage key generation, and staging truncation correction. Correctly notes no scalar UDFs or analytics views are Purchase-owned.

**Gaps:** Does not mention that `Ordered Quantity = Ordered Outers × QuantityPerOuter` is computed in the OLTP extraction procedure (`getpurchaseupdates`) at extract time — the reference treats this as a calculation surface item. Also missing explicit note that the DELETE + INSERT pattern must be rewritten as `MERGE INTO`.

---

### 7 Boundaries — 88/100 (weight 11 → 9.68 pts)

**Status:** ✓ Present

**Strengths:** All six boundary rows present. Source system, target system, ETL orchestration (source and target) all correctly described. Temporal and organizational boundaries marked as [USER INPUT REQUIRED].

**Gaps:** Target catalog name `inventory_stock` differs from reference `globalpurchase` — but this is acceptable since different project names lead to different catalog names. Minor: SSIS pipeline package path is less precise than reference.

---

### 8 Priority and Sequencing — 82/100 (weight 11 → 9.02 pts)

**Status:** ✓ Present

**Strengths:** Priority = PRIMARY, rationale correctly given, dimension load dependency correctly noted. Successor products mentioned.

**Gaps:** Reference includes a more specific dependency note about `dimension.stock item` ETL ownership needing resolution before as-is analysis (this is a discovery-phase planning insight). Reference's Successor products field is `[USER INPUT REQUIRED]` — trainee lists `Inventory_Movement` which is a reasonable forward-planning assumption but adds an assumption the reference does not make.

---

### 9 Known Migration Risks — 85/100 (weight 11 → 9.35 pts)

**Status:** ✓ Present

**Strengths:** 7 of 8 risks correctly identified and well-documented. SSIS bug (Risk 1), space in object names (Risk 2), supplier ETL ordering dependency (Risk 3), `migratestagedpurchasedata` rewrite complexity (Risk 4), reseed utility (Risk 5), dimension ETL not owned by Purchase (Risk 6) — all present and accurate.

**Gaps:** Missing Risk 8: `wwidw purchase and sale per stockitem dynamic` is a cross-domain BI report reading both `fact.purchase` (Purchase) and `fact.sale` (Sales_Orders) — the reference notes that partial migration (Purchase only) will break this report and requires coordinated cutover with the Sales_Orders product team.

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add `analytics.v_ordertoyearanalytics` as third consumer with correlated subquery description | §5 | +3 pts |
| 2 | Add migVisor graph UUIDs to all object tables in §3 | §3 | +2 pts |
| 3 | Add Risk 8: cross-domain BI report cutover coordination | §9 | +1 pt |
| 4 | Add OLTP source procedure (`getpurchaseupdates`) to §4 out-of-scope with note about Databricks JDBC replacement | §4 | +1 pt |
| 5 | Add `Ordered Quantity = Ordered Outers × QuantityPerOuter` to §6 calculation surface | §6 | +1 pt |

---

## Priority Actions

1. **Add `analytics.v_ordertoyearanalytics` consumer** — document it as a cross-domain view that reads `fact.purchase` via a correlated subquery on the `Package` column, noting it is out-of-scope for Purchase migration ownership but must be coordinated with the Order product team. Worth up to **+3 pts**.
2. **Add migVisor UUIDs to object tables** — include the graph object IDs for `fact.purchase`, `dimension.supplier`, `dimension.stock item`, `integration.purchase_staging`, SSIS pipeline items, and BI reports. Required for complete traceability. Worth up to **+2 pts**.
3. **Add cross-domain cutover risk** — add Risk 8 about `wwidw purchase and sale per stockitem dynamic` requiring coordinated cutover with Sales_Orders. Worth **+1 pt**.

---

## Grading Scale

| Score | Grade | Recommended action |
|---|---|---|
| 90–100 | Excellent | Proceed to the next task |
| 75–89 | Good | Minor gaps; proceeding is acceptable |
| 60–74 | Acceptable | Several gaps; revise before proceeding |
| 45–59 | Needs Work | Missing tables, incorrect SQL, or diagrams absent |
| 0–44 | Incomplete | Major sections missing or SQL systematically wrong |

---

*Report generated by migvisor-task-checker-scope on 2026-09-18*
