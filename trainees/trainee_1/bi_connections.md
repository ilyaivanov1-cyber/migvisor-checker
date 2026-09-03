# BI Connections — Sales_Orders
_TASK-MART-004 | [PENDING: CX-P05] BI service account grants_

## SQL Warehouse connection string

```
Server:   <databricks-workspace>.azuredatabricks.net
Port:     443
HTTP Path: /sql/1.0/warehouses/<warehouse-id>
Catalog:  globalsales
Schema:   mart
```

Authentication: Personal Access Token (PAT) or Service Principal OAuth.  
Store credentials in the Power BI Gateway credential store — never in the report file.

## BI report connections (IFR-BI-001..009)

| Report | Primary asset | Mode | Notes |
|---|---|---|---|
| `wwidw-sales` | `mart.v_customer_sales_summary` | DirectQuery | High row count — use SQL Warehouse auto-scale |
| `wwidw-sales-nofilter` | `mart.v_customer_sales_summary` | DirectQuery | Same view; no filter applied |
| `wwidw-dynamic-product-basket-current` | `fact.sale`, `dim.stock_item` | DirectQuery | |
| `wwidw-dynamic-product-basket-prior` | `fact.sale`, `dim.stock_item` | DirectQuery | Filter by prior year in report |
| `wwidw-purchase-sale-per-stockitem` | `fact.sale`, `dim.stock_item` | DirectQuery | |
| `wwidw-orderdetails` | `mart.v_order_details` | DirectQuery | Pass `:start_date` param |
| `wwidw-orderdetails-by-employee-2024` | `mart.v_order_details`, `dim.employee` | DirectQuery | Year filter in report layer |
| `wwidw-orderitemsrankings` | `fact.order`, `dim.stock_item` | DirectQuery | |
| `wwidw-total-orders-march-per-province` | `fact.order`, `dim.city` | DirectQuery | Month + province filter in report |

## Performance guidance (NFR-PERF ≤ 5s p95)

- SQL Warehouse: start with **Small (2 DBU/h)**; scale to **Medium** if p95 > 5s under concurrent load
- Enable **query result caching** on the SQL Warehouse (default: enabled)
- For `wwidw-sales` and `wwidw-sales-nofilter`, apply report-level date slicer to limit rows returned
- Liquid clustering on `fact.sale (invoice_date_key, customer_key, stock_item_key)` ensures efficient data skipping

## Grant targets — [PENDING: CX-P05]

```sql
-- TODO: CX-P05 — replace placeholder with confirmed BI service account name
GRANT SELECT ON SCHEMA globalsales.mart TO `{{UC_ROLE_BI_SERVICE_PRINCIPAL}}`;
GRANT EXECUTE ON FUNCTION globalsales.fact.get_total_quantity_sold TO `{{UC_ROLE_BI_SERVICE_PRINCIPAL}}`;
```
