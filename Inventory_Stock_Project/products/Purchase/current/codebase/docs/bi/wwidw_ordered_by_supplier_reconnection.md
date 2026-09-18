# Power BI Reconnection Specification: `wwidw_ordered_by_supplier`

_Product: Purchase | Project: Inventory_Stock_Project | Task: TASK-024 | Rule: FR-010 | Generated: 2026-09-07_

---

## 1. Report Name and Description

| Field | Value |
|---|---|
| **Report Name** | `wwidw_ordered_by_supplier` |
| **Legacy Connection** | Direct SQL Server 2014 — `wideworldimportersdw` database |
| **New Connection** | Databricks SQL Warehouse via Unity Catalog `inventory_stock` |
| **Description** | Supplier performance and fulfillment reliability report. Assesses order fill rates by supplier, tracks open vs finalized order distribution, and surfaces high-volume suppliers for procurement review. This report is self-contained within the Purchase product — it has no cross-product dependency. |
| **Report Type** | DirectQuery (Databricks SQL Warehouse) |
| **Primary Use Case** | Which suppliers are filling orders in full (received vs ordered outers)? What is the open vs finalized order distribution per supplier? Which suppliers have the highest purchase order volumes? What is the fill rate trend across suppliers? |

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
| `wideworldimportersdw` (SQL Server 2014) | `dimension.supplier` | `inventory_stock.silver_dim.supplier` | Use `silver_dim.supplier_current` view for current-version supplier attributes; pre-filters to `is_current_row = TRUE` |

> All dimension references in the report query must be updated from `dimension.<name>` to `inventory_stock.silver_dim.<name>` (schema mapping: `dimension` → `silver_dim` per PL-002). The `silver_dim.supplier_current` view is the recommended join target for this report because it pre-filters to current SCD-2 versions, avoiding the need to add `WHERE is_current_row = TRUE` to report queries.

**Note:** This report does NOT reference `fact.sale` or any other object outside the Purchase product. It is fully self-contained and can be cut over independently of the Sales_Orders product.

---

## 4. Column Name Mapping

All column names have been converted from PascalCase (SQL Server) to lowercase_snake_case (Databricks) per transformation rule NM-001.

### 4.1. `fact_purchase` Column Mapping

| Legacy Column Name (`fact.purchase`) | Target Column Name (`silver_fact.fact_purchase`) | Data Type | Notes |
|---|---|---|---|
| `PurchaseKey` | `purchase_key` | BIGINT | Surrogate PK; `GENERATED ALWAYS AS IDENTITY` on target |
| `DateKey` | `date_key` | DATE | FK → `silver_dim.date.date`; YYYYMMDD INT in legacy, DATE in target (TY-010) |
| `SupplierKey` | `supplier_key` | BIGINT | FK → `silver_dim.supplier.supplier_key`; SCD-2 surrogate resolved by `sk_resolver.py` |
| `StockItemKey` | `stock_item_key` | BIGINT | FK → `silver_dim.stock_item.stock_item_key` |
| `WWIPurchaseOrderID` | `wwi_purchase_order_id` | INT | Natural / business key |
| `OrderedOuters` | `ordered_outers` | INT | Quantity in outer packaging units; pass-through from source |
| `OrderedQuantity` | `ordered_quantity` | INT | Total individual item quantity; pass-through from source |
| `ReceivedOuters` | `received_outers` | INT (nullable) | Actual received outer quantity; nullable (may be NULL for open orders) |
| `Package` | `package` | STRING | Package type name; NVARCHAR(50) → STRING (TY-009) |
| `IsOrderFinalized` | `is_order_finalized` | BOOLEAN | BIT → BOOLEAN (TY-015); `TRUE` = finalized, `FALSE` = open order |
| `LineageKey` | `lineage_key` | BIGINT | FK → `bronze.lineage_run.lineage_key`; audit column |

### 4.2. `supplier` Dimension Column Mapping

The supplier dimension has undergone structural changes in addition to name normalisation. Key changes are noted below.

| Legacy Column Name (`dimension.supplier`) | Target Column Name (`silver_dim.supplier`) | Data Type | Notes |
|---|---|---|---|
| `SupplierKey` | `supplier_key` | BIGINT | SCD-2 surrogate PK |
| `WWISupplierID` | `wwi_supplier_id` | INT | Legacy business key; retained for lineage traceability |
| `Supplier` | `supplier` | STRING | Supplier name; NVARCHAR → STRING (TY-009) |
| `Category` | `category` | STRING | Supplier category |
| `PrimaryContact` | `primary_contact` | STRING | Primary contact name |
| `PostalCode` | `postal_code` | STRING | Postal code |
| `DeliveryLocation` | `delivery_location_wkt` | STRING | Legacy `geography` CLR column decomposed; WKT representation (TY-P004) |
| `DeliveryLocation` | `delivery_location_lat` | DOUBLE | Latitude extracted from geography CLR per TY-P004 |
| `DeliveryLocation` | `delivery_location_lon` | DOUBLE | Longitude extracted from geography CLR per TY-P004 |
| `ValidFrom` | `valid_from` | DATE | SCD-2 version start; DATETIME2 → DATE (TY-P001) |
| `ValidTo` | `valid_to` | DATE | SCD-2 version end; DATETIME2 → DATE (TY-P001) |
| — | `row_effective_date` | DATE | SCD-2 control column (new, TY-P002) |
| — | `row_expiry_date` | DATE | SCD-2 control column (new, TY-P002) |
| — | `is_current_row` | BOOLEAN | SCD-2 current-version flag (new, TY-P002) |
| `LineageKey` | `lineage_key` | BIGINT | FK → `bronze.lineage_run` |

> The `delivery_location_wkt`, `delivery_location_lat`, and `delivery_location_lon` columns replace the single `DeliveryLocation geography` CLR column from the legacy system. If the report referenced geographic calculations on the legacy `DeliveryLocation` column, those expressions must be rewritten using the three decomposed target columns.

> Use `inventory_stock.silver_dim.supplier_current` (the `_current` view) instead of the base `supplier` table to avoid manually filtering `WHERE is_current_row = TRUE` in report queries.

---

## 5. Cross-Product Dependency

This report is **self-contained within the Purchase product**. It joins only:
- `inventory_stock.silver_fact.fact_purchase` (Purchase product)
- `inventory_stock.silver_dim.supplier` (shared dimension, managed by the Purchase product scope)

There is no dependency on the Sales_Orders product, `fact_sale`, or any other external product. This report can be cut over to Databricks independently, without coordinating with any other product team.

---

## 6. Cutover Checklist

Complete all items in order before switching the report's data source from the legacy SQL Server to the Databricks SQL Warehouse.

| # | Action | Owner | Status |
|---|---|---|---|
| 1 | Confirm `inventory_stock.silver_fact.fact_purchase` is fully loaded; row count matches legacy `fact.purchase` within agreed tolerance | Data Engineering | [ ] |
| 2 | Confirm `inventory_stock.silver_dim.supplier` and `silver_dim.supplier_current` are fully populated; row count matches legacy `dimension.supplier` (current rows) | Data Engineering | [ ] |
| 3 | Confirm the BI read-only service principal has `SELECT` grants on `silver_fact.fact_purchase` and `silver_dim.supplier` (and `silver_dim.supplier_current`) | Data Engineering / DBA | [ ] |
| 4 | Update report data source to `dbsql://{{DATABRICKS_HOST}}/sql/1.0/warehouses/{{WAREHOUSE_ID}}` | BI Developer | [ ] |
| 5 | Update `fact.purchase` table reference to `inventory_stock.silver_fact.fact_purchase` (see Section 3) | BI Developer | [ ] |
| 6 | Update `dimension.supplier` table reference to `inventory_stock.silver_dim.supplier_current` (see Section 3) | BI Developer | [ ] |
| 7 | Update all `fact.purchase` column references from PascalCase to lowercase_snake_case (see Section 4.1) | BI Developer | [ ] |
| 8 | Update all `dimension.supplier` column references from PascalCase to lowercase_snake_case (see Section 4.2) | BI Developer | [ ] |
| 9 | Update `DateKey` filter expressions: legacy `DateKey` is INT (YYYYMMDD); target `date_key` is DATE — update any date filter logic accordingly | BI Developer | [ ] |
| 10 | Rewrite any expressions referencing the legacy `DeliveryLocation geography` CLR column to use `delivery_location_wkt`, `delivery_location_lat`, or `delivery_location_lon` as appropriate (see Section 4.2) | BI Developer | [ ] |
| 11 | Remove `WHERE is_current_row = TRUE` filter from supplier join if switching to `supplier_current` view (filter is pre-applied in the view) | BI Developer | [ ] |
| 12 | Test DirectQuery execution in Power BI Desktop; verify report renders correctly against Databricks SQL Warehouse | BI Developer | [ ] |
| 13 | Validate report output (supplier list, fill rates, order volumes) against legacy report output for a representative date range | BI Developer + Business Analyst | [ ] |
| 14 | Obtain sign-off from business stakeholder | Business Analyst | [ ] |
| 15 | Publish updated report to Power BI Service; update workspace connection | BI Developer | [ ] |
| 16 | Decommission legacy SQL Server direct connection from Power BI report | BI Developer | [ ] |
| 17 | Document cutover completion date and approver in change log | Project Manager | [ ] |

---

_Rules applied: FR-010, NM-001, NM-002, PL-002, TY-009, TY-010, TY-015, TY-P001, TY-P002, TY-P004_
