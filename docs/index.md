# Document Index — Inventory_Stock_Project

**Project:** Inventory_Stock_Project
**Product:** Purchase
**Last updated:** 2026-09-15

This file lists every Markdown document in the workspace with a short description. Explained files (`*-explained.md`) live in `docs/` and provide section-by-section annotation, divergence analysis, and downstream usage notes for their corresponding source document.

---

## Project-Level Specs

| File | Description |
|---|---|
| `project/current/modernization-plan.md` | Defines the scope, goals, target platform, and timeline for migrating the Inventory_Stock_Project from SQL Server 2014 to Databricks Delta Lake. Establishes the business drivers, constraints, and success criteria that govern all downstream decisions. |
| `project/current/catalog.md` | Lists all data products in the project with their type, owner, and migration priority. The single entry point for understanding what exists in the project and what order products should be migrated. |
| `project/current/project-transformation-rules/project-transformation-rules.md` | Defines the 11-dimension set of general transformation rules (naming, typing, observability, lineage, etc.) that apply to every product in the project. Product-level rules override or extend these but cannot exist without them. |

---

## Product-Level Input

| File | Description |
|---|---|
| `products/Purchase/input/product-scope.md` | Defines the boundary of the Purchase data product: what tables it owns, what systems it reads from, what it produces, and what lies outside its scope. The reference point for all "is this our responsibility?" questions. |
| `products/Purchase/input/product-requirements.md` | Captures business and stakeholder requirements for the Purchase product before the technical design begins. The human-language source for the formal requirements in `requirements.md`. |

---

## Product Specifications

| File | Description |
|---|---|
| `products/Purchase/current/specifications/as-is.md` | Documents the legacy SQL Server Purchase data structures, SSIS pipelines, and known defects as they exist before migration. The starting point the to-be design must depart from. |
| `products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md` | Extends and overrides the project-level rules with Purchase-specific decisions (e.g., DATE for SCD-2 validity columns, DirectQuery BI mode). Only the deltas from the project rules are listed here. |
| `products/Purchase/current/specifications/to-be.md` | Designs the target-state Purchase data product on Databricks: the data model, ETL logic, QA assertions, lineage architecture, and serving layer. The primary input to the SmartBuilder development plan. |

---

## Development Plan

| File | Description |
|---|---|
| `products/Purchase/current/specifications/development_plan/product-definition.md` | ODPS 4.1 product definition YAML: formal metadata, input/output ports, SLA, and classifications for the Purchase product. The machine-readable identity contract consumed by the SmartBuilder. |
| `products/Purchase/current/specifications/development_plan/requirements.md` | Translates the to-be design into 32 numbered, testable requirements (functional, non-functional, DQ, and calculations). Each requirement has an acceptance criterion the generated code must satisfy. |
| `products/Purchase/current/specifications/development_plan/design.md` | Technical design document covering the five implementation sections (data model, ingestion, transformation, serving, observability) with rule traceability. Written for the code generator and for engineering reviewers. |
| `products/Purchase/current/specifications/development_plan/tasks.md` | Breaks the design into 26 numbered, dependency-ordered tasks, each producing exactly one output file. The direct input to `generate-db` and `generate-etl`; contains inline DDL and notebook skeletons for critical tasks. |

---

## Codebase Artifacts

| File | Description |
|---|---|
| `products/Purchase/current/codebase/build-plan.md` | Organizes the 26 tasks into 3 phases and 10 named execution batches, records 5 prerequisite environment checks, and registers 4 pending decisions with the tasks they block. The last human-readable document before code generation begins. |
| `products/Purchase/current/codebase/validation-report.md` | Post-generation audit of all 27 codebase artifacts against the specifications: 19 pass, 8 fail, with root cause and resolution for each finding. The authoritative record of what was built vs. what was specified. |
| `products/Purchase/current/codebase/docs/design.md` | Operator-facing ETL technical reference covering the three-task workflow sequence, SK resolution pattern, MERGE logic, QA assertion chain, lineage lifecycle, and config structure. Written after generation for the people who run and maintain the pipeline. |
| `products/Purchase/current/codebase/docs/data-dictionary.md` | Column-level reference for all 5 Purchase tables (48 columns total): type, nullability, business meaning, and derivation for every field. The lookup resource for BI developers, monitoring engineers, and downstream product teams. |
| `products/Purchase/current/codebase/docs/runbook.md` | Operational guide covering scheduled monitoring, task-by-task failure recovery, SK resolution failure handling, the production cutover sequence (resolving all 4 pending decisions), and 5 diagnostic SQL queries. |
| `products/Purchase/current/codebase/docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md` | Power BI reconnection specification for the cross-domain procurement-vs-sales report: maps 5 legacy SQL Server tables to Unity Catalog targets, translates 11 column names, and provides a 16-item cutover checklist requiring joint coordination with the Sales_Orders product team. |
| `products/Purchase/current/codebase/docs/bi/wwidw_ordered_by_supplier_reconnection.md` | Power BI reconnection specification for the supplier performance report: maps 2 tables including the structurally changed supplier dimension (geography CLR → 3 columns), and provides a 17-item self-contained cutover checklist with no cross-product dependency. |
| `README.md` | Top-level project README providing an overview of the Inventory_Stock_Project workspace structure and navigation guide for the migVisor artifacts. |

---

## Explained Docs (`docs/`)

Explained files annotate a source document section by section, surface divergences and open items, and map how the document is used downstream.

| File | Covers | Description |
|---|---|---|
| `docs/modernization-plan-explained.md` | `project/current/modernization-plan.md` | Annotates the modernization plan's business drivers, platform choices, and scope decisions. Explains why each constraint was set and what it means for the products downstream. |
| `docs/catalog-explained.md` | `project/current/catalog.md` | Explains what the project catalog is, why it exists as a standalone document, and what the product entries reveal about migration sequencing and ownership. |
| `docs/project-transformation-rules-explained.md` | `project/current/project-transformation-rules/project-transformation-rules.md` | Annotates the 11 transformation rule dimensions, explains the rule hierarchy (project vs. product), and surfaces which rules carry the highest implementation consequence. |
| `docs/product-scope-explained.md` | `products/Purchase/input/product-scope.md` | Explains the boundary decisions in the Purchase product scope, why certain tables are included or excluded, and what the external ownership declarations mean for the ETL design. |
| `docs/product-requirements-explained.md` | `products/Purchase/input/product-requirements.md` | Annotates the business requirements and explains how they were formalized, which requirements are the most load-bearing, and where gaps were identified before design began. |
| `docs/as-is-explained.md` | `products/Purchase/current/specifications/as-is.md` | Explains the as-is analysis structure, highlights the legacy defects that drove key to-be decisions, and identifies what the as-is documentation makes explicit that the source system never did. |
| `docs/product-transformation-rules-explained.md` | `products/Purchase/current/specifications/product-transformation-rules/product-transformation-rules.md` | Explains which project-level rules the Purchase product overrides and why, and what the product-specific rules (TY-P001 DATE choice, CX rules, QA rules) mean for the generated code. |
| `docs/to-be-explained.md` | `products/Purchase/current/specifications/to-be.md` | Annotates the to-be design document section by section, explains the key architectural decisions (medallion layers, SCD-2 surrogates, QA chain design), and surfaces divergences between the to-be and the generated codebase. |
| `docs/product-definition-explained.md` | `products/Purchase/current/specifications/development_plan/product-definition.md` | Explains the ODPS product definition YAML structure, what each field means operationally, and how the definition is consumed by the SmartBuilder to generate the development plan. |
| `docs/requirements-explained.md` | `products/Purchase/current/specifications/development_plan/requirements.md` | Annotates all 32 requirements, explains how they trace to the to-be design and to the task list, and identifies requirements with ambiguous or incorrect acceptance criteria. |
| `docs/design-explained.md` | `products/Purchase/current/specifications/development_plan/design.md` | Explains the five technical design sections, traces each design decision to the requirements it satisfies, and identifies where the design introduces ambiguity that the task list or build plan had to resolve. |
| `docs/tasks-explained.md` | `products/Purchase/current/specifications/development_plan/tasks.md` | Annotates all 26 tasks across 6 types, explains the dependency graph and parallelism opportunities, and surfaces 6 divergences including the missing shared-module tasks and the single-column MERGE key defect. |
| `docs/build-plan-explained.md` | `products/Purchase/current/codebase/build-plan.md` | Explains the build plan's 9 sections, why it crosses the specification/codebase boundary, and identifies 8 divergences including the reversed lineage-close mechanism, the missing schema creation tasks, and the MERGE key defect reaching its fourth artifact. |
| `docs/validation-report-explained.md` | `products/Purchase/current/codebase/validation-report.md` | Explains all 8 validation findings (F-001 through F-008), their root causes and relationships to each other, and identifies 5 open items including why F-002 and F-005 are symptoms of the same unresolved upstream decision. |
| `docs/codebase-design-explained.md` | `products/Purchase/current/codebase/docs/design.md` | Explains the post-generation ETL design document, identifies phantom rule citations (DM-001, DM-002), flags the probable divergence of the Section 6 two-tier lineage diagram from the flat generated DDL, and notes the `date_key` derivation conflict with the data dictionary. |
| `docs/data-dictionary-explained.md` | `products/Purchase/current/codebase/docs/data-dictionary.md` | Explains all 5 tables and 48 columns in the data dictionary, highlights that it is the only document besides `to-be.md` stating the correct 4-column MERGE key, and surfaces a discrepancy between the runbook's DQ queries and the documented column names. |
| `docs/runbook-explained.md` | `products/Purchase/current/codebase/docs/runbook.md` | Explains the runbook's operational structure, identifies that its `dq_rejections` queries use wrong column names, flags the reference to a non-existent deployment script, and notes that this document has no task owner and is untracked by the manifest. |
| `docs/bi-stock-item-report-explained.md` | `products/Purchase/current/codebase/docs/bi/wwidw_purchase_and_sale_per_stockitem_dynamic_reconnection.md` | Explains the stock-item BI reconnection spec section by section, with particular attention to the cross-product dependency on Sales_Orders and the operational consequences of the DATE vs. INT `date_key` type change. |
| `docs/bi-supplier-report-explained.md` | `products/Purchase/current/codebase/docs/bi/wwidw_ordered_by_supplier_reconnection.md` | Explains the supplier BI reconnection spec, focusing on the geography CLR decomposition (one-to-three column mapping) and why this report's self-containment makes it the simpler of the two cutovers despite its more complex column mapping. |