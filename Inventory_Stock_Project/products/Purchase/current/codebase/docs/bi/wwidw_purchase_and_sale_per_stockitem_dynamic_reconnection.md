# Power BI Reconnection Specification: `wwidw_purchase_and_sale_per_stockitem_dynamic`

_Product: Purchase | Project: Inventory_Stock_Project | Task: TASK-023 | Rule: FR-010 | Generated: 2026-09-07_

---

## 1. Report Name and Description

| Field | Value |
|---|---|
| **Report Name** | `wwidw_purchase_and_sale_per_stockitem_dynamic` |
| **Legacy Connection** | Direct SQL Server 2014 — `wideworldimportersdw` database |
| **New Connection** | Databricks SQL Warehouse via Unity Catalog `inventory_stock` |
| **Description** | Cross-domain procurement-vs-sales comparison report. Compares purchase volumes against sales volumes per stock item; identifies open (non-finalized) purchase orders relative to corresponding sales activity. Requires coordinated cutover with the **Sales_Orders** product because it joins `silver_fact.fact_purchase` (Purchase product) with `silver_fact.fact_sale` (Sales_Orders product) and `silver_dim.stock_item`. |
| **Report Type** | DirectQuery (Databricks SQL Warehouse) |
| **Primary Use Case** | Which stock items are ordered in volumes matching sales demand? How do receipt quantities compare to sales per stock item? Which stock items have open purchase orders relative to their sales activity? |

---

## 2. Databricks SQL Warehouse Connection Details

| Parameter | Value |
|---|---|
| **Connection String** | `dbsql://{{DATABRICKS_HOST}}/sql/1.0/warehouses/{{WAREHOUSE_ID}}` |
| **Authentication** | Unity Catalog service principal (read-only) |
| **Credential Type** | OAuth 2.0 — client credentials flow (service principal client ID + client secret) |
| **Catalog** | `inventory_stock` |
| **HTTP Path** | `/sql/1.0/warehouses/{{WAREHOUSE_ID}}` |
| **Port** | 443 |
| **Protocol** | HTTPS |
| **Driver** | Simba Spark ODBC Driver (or Databricks ODBC Driver v2.x) |

> Replace `{{DATABRICKS_HOST}}` with the Databricks workspace hostname (e.g. `adb-1234567890.1.azuredatabricks.net`) and `{{WAREHOUSE_ID}}` with the SQL Warehouse ID. Both values are environment-specific and must be supplied at deployment time.

**Power BI Desktop connection steps:**
1. In Power BI Desktop, select **Get Data → Databricks**.
2. Enter the Server (`{{DATABRICKS_HOST}}`) and HTTP Path (`/sql/1.0/warehouses/{{WAREHOUSE_ID}}`).
3. Select **DirectQuery** as the connectivity mode.
4. Authenticate with the read-only service principal credentials (client ID + client secret).
5. Browse to catalog `inventory_stock` and select the tables listed in Section 3.

---

## 3. Table Mapping: Legacy SQL Server to Target Databricks

| Legacy Connection | Legacy Schema.Table | Target Unity Catalog Table | Notes |
|---|---|---|---|
| `wideworldimportersdw` (SQL Server 2014) | `fact.purchase` | `inventory_stock.silver_fact.fact_purchase` | Purchase product — primary fact table for this report |
| `wideworldimportersdw` (SQL Server 2014) | `fact.sale` | `inventory_stock.silver_fact.fact_sale` | **Sales_Orders product** — external cross-product dependency; see Section 5 |
| `wideworldimportersdw` (SQL Server 2014) | `dimension.stock item` | `inventory_stock.silver_dim.stock_item` | Space in legacy name resolved per NM-002; use `silver_dim.stock_item_current` view for current-version rows only |
| `wideworldimportersdw` (SQL Server 2014) | `dimension.supplier` | `inventory_stock.silver_dim.supplier` | Use `silver_dim.supplier_current` view for current-version rows only |
| `wideworldimportersdw` (SQL Server 2014) | `dimension.date` | `inventory_stock.silver_dim.date` | Shared infrastructure date dimension; read-only |

> All dimension references in the report query must be updated from `dimension.<name>` to `inventory_stock.silver_dim.<name>` (schema mapping: `dimension` → `silver_dim` per PL-002). SCD-2 `_current` views (`supplier_current`, `stock_item_current`) pre-filter to `is_current_row = TRUE` and should be used in place of the base dimension tables wherever the report requires current-state dimension attributes.

---

## 4. Column Name Mapping: `fact_purchase`

All column names have been converted from PascalCase (SQL Server) to lowercase_snake_case (Databricks) per transformation rule NM-001.

| Legacy Column Name (`fact.purchase`) | Target Column Name (`silver_fact.fact_purchase`) | Data Type | Notes |
|---|---|---|---|
| `PurchaseKey` | `purchase_key` | BIGINT | Surrogate PK; `GENERATED ALWAYS AS IDENTITY` on target |
| `DateKey` | `date_key` | DATE | FK → `silver_dim.date.date`; YYYYMMDD INT in legacy, DATE in target (TY-010) |
| `SupplierKey` | `supplier_key` | BIGINT | FK → `silver_dim.supplier.supplier_key`; SCD-2 surrogate resolved by `sk_resolver.py` |
| `StockItemKey` | `stock_item_key` | BIGINT | FK → `silver_dim.stock_item.stock_item_key`; SCD-2 surrogate resolved by `sk_resolver.py` |
| `WWIPurchaseOrderID` | `wwi_purchase_order_id` | INT | Natural / business key; retained as MERGE predicate column |
| `OrderedOuters` | `ordered_outers` | INT | Quantity in outer packaging units; pass-through from source |
| `OrderedQuantity` | `ordered_quantity` | INT | Total individual item quantity; pass-through from source |
| `ReceivedOuters` | `received_outers` | INT (nullable) | Actual received outer quantity; nullable (may be NULL for open orders) |
| `Package` | `package` | STRING | Package type name; NVARCHAR(50) → STRING (TY-009) |
| `IsOrderFinalized` | `is_order_finalized` | BOOLEAN | BIT → BOOLEAN (TY-015); `TRUE` = finalized, `FALSE` = open order |
| `LineageKey` | `lineage_key` | BIGINT | FK → `bronze.lineage_run.lineage_key`; audit column propagated via `taskValues` |

> If the legacy report references any other columns from `fact.purchase` not listed above, consult the data dictionary at `docs/data-dictionary.md` and the as-is analysis at `specifications/as-is.md`.

---

## 5. Cross-Product Dependency

> **IMPORTANT: This report requires BOTH the Purchase and Sales_Orders products to be fully deployed and available before cutover. A coordinated cutover is mandatory.**

| Dependency | Details |
|---|---|
| **Purchase product** | Provides `inventory_stock.silver_fact.fact_purchase`. Must be fully loaded and validated before cutover. |
| **Sales_Orders product** | Provides `inventory_stock.silver_fact.fact_sale`. This table is an **external dependency** — it is owned by the Sales_Orders product, not by the Purchase product. The Purchase ETL pipeline does not write to or manage `fact_sale`. |
| **Shared dimensions** | `inventory_stock.silver_dim.stock_item` and `inventory_stock.silver_dim.date` are shared infrastructure objects; their availability must also be confirmed. |

**Risk:** If the Sales_Orders product is not yet cut over to Databricks at the time of Purchase cutover, the report will fail to connect to `silver_fact.fact_sale`. In this case, the report must remain on the legacy SQL Server connection until both products are available, or the BI team must maintain a dual-connection configuration during the transition period.

**Coordination actions required:**
- Schedule a joint cutover window with the Sales_Orders product team.
- Validate `silver_fact.fact_sale` row counts and date coverage against the legacy `fact.sale` before the joint cutover.
- Test the cross-product join in Power BI Desktop against the Databricks SQL Warehouse before go-live.
- Confirm that `silver_dim.stock_item` and `silver_dim.date` are fully populated and accessible to the BI service principal.

---

## 6. Cutover Checklist

Complete all items in order before switching the report's data source from the legacy SQL Server to the Databricks SQL Warehouse.

| # | Action | Owner | Status |
|---|---|---|---|
| 1 | Confirm `inventory_stock.silver_fact.fact_purchase` is fully loaded; row count matches legacy `fact.purchase` within agreed tolerance | Data Engineering | [ ] |
| 2 | Confirm `inventory_stock.silver_fact.fact_sale` (Sales_Orders product) is fully loaded; row count matches legacy `fact.sale` within agreed tolerance | Sales_Orders Data Engineering | [ ] |
| 3 | Confirm `inventory_stock.silver_dim.stock_item` and `silver_dim.stock_item_current` are available and populated | Data Engineering | [ ] |
| 4 | Confirm `inventory_stock.silver_dim.supplier` and `silver_dim.supplier_current` are available and populated | Data Engineering | [ ] |
| 5 | Confirm `inventory_stock.silver_dim.date` is available and fully populated for the report's date range | Data Engineering | [ ] |
| 6 | Confirm the BI read-only service principal has `SELECT` grants on `silver_fact.fact_purchase`, `silver_fact.fact_sale`, `silver_dim.stock_item`, `silver_dim.supplier`, `silver_dim.date` | Data Engineering / DBA | [ ] |
| 7 | Update report data source to `dbsql://{{DATABRICKS_HOST}}/sql/1.0/warehouses/{{WAREHOUSE_ID}}` | BI Developer | [ ] |
| 8 | Update all table references in report queries from legacy three-part names to `inventory_stock.*.*` names (see Section 3) | BI Developer | [ ] |
| 9 | Update all column references from PascalCase to lowercase_snake_case (see Section 4) | BI Developer | [ ] |
| 10 | Update `DateKey` filter expressions: legacy `DateKey` is INT (YYYYMMDD); target `date_key` is DATE — update any date filter logic accordingly | BI Developer | [ ] |
| 11 | Test DirectQuery execution in Power BI Desktop; verify report renders correctly against Databricks SQL Warehouse | BI Developer | [ ] |
| 12 | Validate report output (row counts, key metrics) against legacy report output for a representative date range | BI Developer + Business Analyst | [ ] |
| 13 | Obtain sign-off from business stakeholder | Business Analyst | [ ] |
| 14 | Publish updated report to Power BI Service; update workspace connection | BI Developer | [ ] |
| 15 | Decommission legacy SQL Server direct connection from Power BI report | BI Developer | [ ] |
| 16 | Document cutover completion date and approver in change log | Project Manager | [ ] |

---

_Rules applied: FR-010, NM-001, NM-002, PL-002, TY-009, TY-010, TY-015_
