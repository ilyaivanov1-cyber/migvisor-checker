# Design Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 73/100 (Acceptable)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| Overview | 13 | 82 | Architecture summary and design rationale present |
| Bronze DDL | 13 | 55 | Partial DDL; missing formal CREATE TABLE with column types, constraints, COMMENT strings |
| Silver DDL | 13 | 52 | Similar gap to Bronze — DDL blocks incomplete |
| MERGE/ETL Logic | 13 | 80 | MERGE strategy and watermark logic well-documented |
| Python Notebooks | 13 | 78 | Notebook responsibilities documented |
| Architecture Diagram | 13 | 82 | Pipeline DAG embedded and readable |
| Mart/Serving Layer | 12 | 30 | Gold-layer design largely absent; BI views not defined |
| Data Quality | 10 | 75 | DQ assertions referenced |

## Auto-deducts

None.

## Summary

The technical design document scored 73/100 (Acceptable), with the Overview, MERGE/ETL Logic, Python Notebooks, and Architecture Diagram sections scoring well. The Bronze and Silver DDL sections are below standard — formal CREATE TABLE statements with all column types, constraints, and COMMENT strings are missing. The Mart/Serving Layer section scored only 30/100, indicating the gold-layer design is largely absent. The top fix is adding complete DDL blocks for bronze.purchase_staging, bronze.lineage_run, and silver_fact.fact_purchase, worth up to +8 pts. Adding the Mart Layer section for downstream BI views is the second priority at +4 pts.

## Priority Actions

1. Add complete DDL blocks for bronze.purchase_staging, bronze.lineage_run, and silver_fact.fact_purchase — +8 pts
2. Add Mart Layer section with view definitions for mart.v_purchase_by_supplier and v_purchase_per_stock_item — +4 pts
