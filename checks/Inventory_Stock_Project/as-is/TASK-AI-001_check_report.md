---
task_id: TASK-AI-001
skill: migvisor-task-checker-as-is
trainee_file: ./Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md
reference_file: ./reference/answers/module_2/1 as-is.md
generated: 2026-09-18
total_score: 67/100
grade: Acceptable
---

# TASK-AI-001 Check Report

**Product:** Purchase  
**Trainee file:** `./Inventory_Stock_Project/products/Purchase/current/specifications/as-is.md`  
**Reference file:** `./reference/answers/module_2/1 as-is.md`  
**Generated:** 2026-09-18

---

## Score Summary

**As-Is Score: 67/100**

| Section | Weight | Raw Score | Weighted | Status |
|---|---|---|---|---|
| 1 Definition | 16 | 65/100 | 10.4 | ⚠ |
| 2 Consumers | 16 | 60/100 | 9.6 | ⚠ |
| 3 Model | 17 | 72/100 | 12.24 | ⚠ |
| 4 Lineage | 17 | 78/100 | 13.26 | ✓ |
| 5 Calculations | 17 | 72/100 | 12.24 | ⚠ |
| 6 Sources | 17 | 40/100 | 6.8 | ✗ |
| **Subtotal** | | | **64.54** | |
| Auto-deducts | | | **−7** | |
| **Total** | | | **67/100** | |

**Grade: Acceptable**

> **Weight calculation:** N = 6, base_weight = floor(100/6) = 16, remainder = 4 → 1 pt each added to §3 Model, §4 Lineage, §5 Calculations, §6 Sources.

---

## Section Matching Log

| Reference Section | Matched | Match Type |
|---|---|---|
| 1 Definition (1.1–1.7) | §1 Definition (1.1 narrative + 1.2 metadata table) | Partial |
| 2 Consumers (2.1–2.6) | §2 Consumers (table) | Partial |
| 3 Model (3.1–3.8) | §3 Model (3.1 ER diagram + 3.2 textual) | Partial |
| 4 Lineage (4.1–4.9) | §4 Lineage (4.1–4.5) | Partial |
| 5 Calculations (5.1–5.9) | §5 Calculations (5.1–5.3) | Partial |
| 6 Sources (6.1–6.9) | §6 Sources (6.1–6.2) | Partial |

---

## Auto-Deducts Applied

| Condition | Penalty | Applied |
|---|---|---|
| Missing `analytics.v_ordertoyearanalytics` consumer analysis (correlated subquery on Package, cross-domain implication) | −3 pts | Yes — absent from §2; reference documents query logic, migration implication, ownership |
| §6 Sources missing extraction method, column mapping, incremental load pattern, staging lifecycle | −2 pts | Yes — trainee has only source/output tables; reference has §6.3–6.9 |
| §1 Definition missing stakeholder table, technology stack table, KPI table, operational context | −2 pts | Yes — reference has §1.3–1.7 with full detail; trainee has a metadata table instead |

**Total auto-deducts: −7 pts**

---

## Section Feedback

### 1 Definition — 65/100 (weight 16 → 10.4 pts)

**Status:** ⚠ Partial

**Strengths:** §1.1 narrative is excellent — names fact table, ETL engine, staging layer, SSIS bug, migration target, and two BI reports clearly. §1.2 metadata table with 15 fields is well-structured and covers domain, process type, business entities, metrics, description, impacted reports, data sources, filters, calculated fields, and DQ rules.

**Gaps:**
- Reference §1.2 documents the confirmed DDL (full `CREATE TABLE` with all 11 columns and constraints) — trainee mentions the DDL structure in §1.1 text but doesn't include the confirmed DDL in a code block.
- Reference §1.3 Technology Stack table (Database engine, schema model, ETL orchestration, ETL logic, staging, watermark, lineage, dimension management, BI, target platform) — not present separately in trainee.
- Reference §1.4 Stakeholders table (Scope owner, DW/ETL engineering, BI/reporting, procurement business team, Databricks platform, shared infrastructure, migration project lead) — absent.
- Reference §1.5 Data Domain and Subject Area (grain definition, dimension coverage table) — partially covered in §1.2.
- Reference §1.6 Key Metrics and KPIs (table: ordered qty, ordered outers, received outers, fill rate, open/finalized orders, purchase order volume, lineage coverage) — trainee §1.2 mentions metrics but without full KPI table.
- Reference §1.7 Operational Context (SSIS task sequence, incremental strategy details, load pattern, reset utility) — partially present in §1.1 narrative but not as structured subsection.

---

### 2 Consumers — 60/100 (weight 16 → 9.6 pts)

**Status:** ⚠ Partial

**Strengths:** All three consumers correctly identified (2 BI reports + internal ETL `migratestagedpurchasedata`). Use cases and business questions answered are articulated well for both reports.

**Gaps:**
- Missing `analytics.v_ordertoyearanalytics` analytical view — reference §2.3 documents this view, its cross-domain ownership, and the fragile `fo.Package = p.Package` string join. This is analytically significant and migration-impactful.
- Missing §2.4 Consumption Patterns — no semantic layer, direct table reads, implied access patterns for both reports.
- Missing §2.5 Migration Impact on Consumers — table mapping each consumer to its migration action (connection string change, cross-domain dependency, decommission).
- Missing §2.6 Consumer Priority for Migration — ranked list of consumers by migration priority with rationale.

---

### 3 Model — 72/100 (weight 17 → 12.24 pts)

**Status:** ⚠ Partial

**Strengths:** Excellent Mermaid ER diagram (§3.1) covering all 7 in-scope tables with correct column types, PKs, FKs, and relationship labels. Textual description table (§3.2) correctly categorizes all layers. ETL staging lifecycle briefly noted including SSIS bug.

**Gaps:**
- Reference §3.2–3.8 provide full `CREATE TABLE` DDLs with confirmed column inventories for all 7 tables (fact, 3 dimensions, 3 integration tables). Trainee's ER diagram shows structure but DDLs not included.
- Reference §3.2 fact.purchase column inventory (11 columns with exact data types, nullability, constraints) — trainee ER has column list but without detailed type annotations.
- Reference §3.5 Sequences section (3 sequence objects: SupplierKey, StockItemKey, LineageKey with roles and migration challenge) — partially mentioned in §3.2 narrative.
- Reference §3.7 Notable Schema Issues table (8 issues: space in object name, composite PK, varbinary Photo, date FK type, ETL Cutoff space, sequences, collation, sysname) — absent. Critical migration risk documentation.
- Reference §3.8 Schema Diagram (ASCII art) — trainee has Mermaid ER diagram which is arguably better.

---

### 4 Lineage — 78/100 (weight 17 → 13.26 pts)

**Status:** ✓ Present

**Strengths:** §4.2 Mermaid lineage diagram is very good — shows OLTP → extract → staging → SCD-2 resolution → fact load → BI consumption with correct bug annotation. §4.3 Column-Level Lineage Table covers all 9 fact columns with source, intermediate, and derivation. §4.4 Step-by-Step Transformation Table has 11 steps with SQL examples for all major operations including both key resolutions, delete, insert, lineage completion, watermark advance. §4.5 Known Downstream Dependencies is comprehensive.

**Gaps:**
- Reference §4.1 includes 6-hop lineage chain summary with hop count — trainee doesn't explicitly count hops.
- Reference §4.6 Lineage Dependencies (Cross-Product) table — trainee covers this in §4.5 but less formally.
- Reference §4.7 Shared Infrastructure in Lineage table — not a separate section in trainee.
- Reference §4.8 Lineage Graph Anomalies — 5 anomalies documented (wrong table truncated, MODIFY relation to staging, configuration_reseedetl TRUNCATE, cross-domain Package join, traversal direction behavior). Trainee mentions the bug but not the other anomalies.
- Reference §4.9 Migration Lineage Impact table (as-is vs. to-be for orchestration, extraction, staging, core ETL, SCD-2, lineage/cutoff, downstream consumers) — absent. Important migration planning section.

---

### 5 Calculations — 72/100 (weight 17 → 12.24 pts)

**Status:** ⚠ Partial

**Strengths:** Three detailed calculation sections: §5.1 Date Key Derivation (business purpose, formula, SQL, step-by-step, thresholds), §5.2 Ordered Outers and Ordered Quantity (business purpose, formula, SQL, step-by-step, thresholds — correctly notes both are pass-throughs from OLTP), §5.3 SCD-2 Surrogate Key Resolution (full SQL for both supplier and stock item, step-by-step, thresholds table for resolved/unresolved/overlapping cases).

**Gaps:**
- Reference §5.1 (Calculations Overview table) — not separately structured in trainee.
- Reference §5.4 Lineage and Watermark Management (exact SQL for lineage acquisition, lineage completion stamp, cutoff advancement, atomic transaction wrapper) — not documented as a separate calculation section in trainee.
- Reference §5.5 Extraction Calculations — full `CREATE PROCEDURE Integration.GetPurchaseUpdates` body with all SQL. Trainee references getpurchaseupdates in §4.4 extract step but doesn't document the full procedure.
- Reference §5.6 Analytical View Calculations (`v_ordertoyearanalytics` with fragile Package join, tax coverage anomaly, date conversion inefficiency, dead code branch) — entirely absent.
- Reference §5.7 COALESCE and NULL Handling table — trainee mentions COALESCE in §5.3 but no dedicated section.
- Reference §5.8 Data Type Conversions table — absent.
- Reference §5.9 Calculation Migration Complexity table (7 priority challenges) — absent.

---

### 6 Sources — 40/100 (weight 17 → 6.8 pts)

**Status:** ✗ Incomplete

**Strengths:** §6.1 Input Source Tables — correctly lists all 8 source objects with platform, schema, and key fields. §6.2 Output Tables — lists 7 output objects with description.

**Gaps:**
- Reference §6.3 Extraction Method — SSIS dataflow details, procedure body reference, no CDC / no OLTP staging / measure derivation at extract time / package type denormalization.
- Reference §6.4 Incremental Load Pattern — ETL cutoff lifecycle (4-step sequence), incremental change detection expression, filter semantics (exclusive/inclusive bounds).
- Reference §6.5 Staging Layer — staging lifecycle (5 steps including SSIS bug), full reference back to §3.4.1 DDL.
- Reference §6.6 Dimension Sources — for both supplier and stock item: OLTP source tables, extraction procedure, DW load procedure, SCD type. Missing from trainee entirely.
- Reference §6.7 Data Freshness and Latency table (batch frequency, maximum lag, incremental detection method, watermark persistence, order-level reload, historic re-seeds).
- Reference §6.8 Source-to-Target Column Mapping table (10 rows mapping OLTP columns through transformation to fact columns).
- Reference §6.9 Migration Impact on Sources (6 areas: extraction, source procedure, incremental logic, measure computation, staging zone, watermark store + connectivity requirements + key migration risks).

---

## Improvement Items

| # | Gap | Section | Est. Points |
|---|---|---|---|
| 1 | Add complete §6.3–6.9: extraction method, incremental load pattern, staging lifecycle, dimension sources, data freshness, column mapping, migration impact | §6 | +8 pts |
| 2 | Add `analytics.v_ordertoyearanalytics` consumer with correlated subquery analysis and migration impact | §2 | +4 pts |
| 3 | Add §1.3 Technology Stack, §1.4 Stakeholders, §1.6 KPI table, §1.7 Operational Context | §1 | +3 pts |
| 4 | Add §3.7 Notable Schema Issues table (8 issues) and full confirmed DDLs for all tables | §3 | +3 pts |
| 5 | Add §4.8 Lineage Graph Anomalies and §4.9 Migration Lineage Impact table | §4 | +2 pts |
| 6 | Add §5.5 full `GetPurchaseUpdates` procedure body, §5.6 analytics view calculations, §5.9 migration complexity table | §5 | +2 pts |

---

## Priority Actions

1. **Complete §6 Sources** — add §6.3 extraction method, §6.4 incremental load pattern, §6.6 dimension sources, §6.7 data freshness, §6.8 source-to-target column mapping, and §6.9 migration impact on sources. This is the most incomplete section. Worth up to **+8 pts**.
2. **Add analytics view consumer** — document `analytics.v_ordertoyearanalytics` in §2 with the correlated subquery on `Package`, cross-domain implication, and migration impact note. Worth up to **+4 pts**.
3. **Add §1 definition subsections** — add Technology Stack (§1.3), Stakeholders (§1.4), and Operational Context (§1.7) as structured tables rather than embedding in narrative. Worth up to **+3 pts**.

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

*Report generated by migvisor-task-checker-as-is on 2026-09-18*
