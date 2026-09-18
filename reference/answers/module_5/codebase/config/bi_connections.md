# CFG-012: BI Tool Reconnection Guide

## 1. Overview

This guide helps BI developers reconnect their reports and dashboards to the new Unity Catalog endpoints after migration from the legacy source system. All BI access goes through the `globalpurchase.mart` schema.

---

## 2. Connection Details per Mart View

### 2.1 `v_purchase_by_supplier` — Supplier Purchase Summary

| Attribute | Value |
|---|---|
| **Unity Catalog path** | `globalpurchase.mart.v_purchase_by_supplier` |
| **Object type** | Materialized View |
| **Service principal** | `bi-service-principal` |
| **Minimum privilege** | `SELECT` on the view + `USE SCHEMA` on `globalpurchase.mart` |
| **Refreshed by** | ETL pipeline (nightly, after DQ clearance) |

**Sample connection query:**
```sql
SELECT * FROM globalpurchase.mart.v_purchase_by_supplier LIMIT 100;
```

---

### 2.2 `v_purchase_per_stock_item` — Per-Stock-Item Purchase Detail

| Attribute | Value |
|---|---|
| **Unity Catalog path** | `globalpurchase.mart.v_purchase_per_stock_item` |
| **Object type** | Standard View |
| **Service principal** | `bi-service-principal` |
| **Minimum privilege** | `SELECT` on the view + `USE SCHEMA` on `globalpurchase.mart` |
| **Real-time** | Yes — view reads current fact and dimension tables |

**Sample connection query:**
```sql
SELECT stock_item_name, SUM(ordered_quantity) AS total_ordered
FROM globalpurchase.mart.v_purchase_per_stock_item
GROUP BY stock_item_name
ORDER BY total_ordered DESC;
```

---

## 3. Connecting BI Tools

### Databricks SQL Warehouse endpoint

```
Server hostname:  <workspace-url>.azuredatabricks.net
HTTP path:        /sql/1.0/warehouses/<warehouse-id>
Authentication:   OAuth (bi-service-principal) or Personal Access Token
Catalog:          globalpurchase
Schema:           mart
```

### Power BI / Tableau

1. Select **Azure Databricks** as the connector.
2. Enter the server hostname and HTTP path above.
3. Set **Catalog** = `globalpurchase` and **Schema** = `mart`.
4. Select the target view (`v_purchase_by_supplier` or `v_purchase_per_stock_item`).

---

## 4. Known Issues and Workarounds

| Issue | Workaround |
|---|---|
| Materialized view shows stale data | Check `stg.lineage` for the latest `status = 'success'` run; wait for the nightly ETL or trigger a manual REFRESH via the ETL workflow. |
| `ACCESS DENIED` on mart view | Confirm `bi-service-principal` has `SELECT` on the view and `USE SCHEMA` on `globalpurchase.mart` (see GRANT-004). |

---

## 5. Access Provisioning

Contact the Data Engineering team at `data-engineering@company.com` to:
- Onboard new BI service principals
- Grant `purchase-analysts` role to end users
- Request a manual mart refresh outside the nightly schedule
