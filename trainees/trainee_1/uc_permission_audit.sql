-- TASK-SEC-004: Unity Catalog permission audit script
-- Queries information_schema.object_privileges for all grants on globalsales catalog.
-- Read-only — no DDL or DML.
-- [PENDING: CX-P05] expected role matrix not yet confirmed; compare output against matrix when available.

USE CATALOG globalsales;

-- All privileges on all objects in the globalsales catalog
SELECT
  object_type,
  object_name,
  privilege_type,
  grantee,
  is_grantable
FROM globalsales.information_schema.object_privileges
ORDER BY object_type, object_name, grantee, privilege_type;

-- Schema-level privileges summary
SELECT
  object_name    AS schema_name,
  grantee,
  COLLECT_SET(privilege_type) AS privileges
FROM globalsales.information_schema.object_privileges
WHERE object_type = 'SCHEMA'
GROUP BY object_name, grantee
ORDER BY schema_name, grantee;

-- Table-level privileges summary for silver and gold layers
SELECT
  object_name    AS table_name,
  grantee,
  COLLECT_SET(privilege_type) AS privileges
FROM globalsales.information_schema.object_privileges
WHERE object_type IN ('TABLE', 'VIEW')
  AND (object_name LIKE 'globalsales.dim.%'
    OR object_name LIKE 'globalsales.fact.%'
    OR object_name LIKE 'globalsales.mart.%')
GROUP BY object_name, grantee
ORDER BY table_name, grantee;
