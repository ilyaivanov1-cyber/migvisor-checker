#!/usr/bin/env bash
# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : scripts/deploy_ddl.sh
# Purpose  : Execute all Purchase DDL files and grants against the target
#            Unity Catalog in the correct Phase 1 dependency order.
#
# Usage    : ./scripts/deploy_ddl.sh [--catalog CATALOG] [--profile PROFILE]
#
# Options  :
#   --catalog  Unity Catalog name (default: inventory_stock)
#   --profile  Databricks CLI profile (default: DEFAULT)
#
# Prerequisites:
#   - Databricks CLI installed and configured (databricks configure)
#   - Target catalog and schemas already exist:
#       inventory_stock.bronze
#       inventory_stock.silver_fact
#       inventory_stock.silver_dim
#   - Resolve PD-003 (role matrix) before running grants
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
CATALOG="inventory_stock"
PROFILE="DEFAULT"
CODEBASE="products/Purchase/current/codebase"
DDL_DIR="${CODEBASE}/src/db/ddl"
GRANTS_DIR="${CODEBASE}/src/db/grants"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --catalog)  CATALOG="$2";  shift 2 ;;
    --profile)  PROFILE="$2";  shift 2 ;;
    *)          echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "========================================================"
echo "Purchase DDL Deployment"
echo "  Catalog : ${CATALOG}"
echo "  Profile : ${PROFILE}"
echo "  DDL dir : ${DDL_DIR}"
echo "========================================================"

# ---------------------------------------------------------------------------
# Helper: execute a SQL file via Databricks CLI
# ---------------------------------------------------------------------------
run_sql() {
  local label="$1"
  local file="$2"
  echo ""
  echo ">>> [${label}] ${file}"
  databricks --profile "${PROFILE}" sql execute \
    --warehouse-id "${WAREHOUSE_ID:?Set WAREHOUSE_ID env var to your SQL warehouse ID}" \
    --file "${file}"
  echo "    OK"
}

# ---------------------------------------------------------------------------
# Phase 1 — Bronze layer (dependency order)
# ---------------------------------------------------------------------------
echo ""
echo "--- Phase 1: Bronze layer ---"

# lineage_run must be first — other tables reference lineage_key via FK
run_sql "BRONZE-1" "${DDL_DIR}/bronze_lineage_run.sql"

# etl_cutoff is standalone — no FK dependencies
run_sql "BRONZE-2" "${DDL_DIR}/bronze_etl_cutoff.sql"

# purchase_staging references lineage_key → lineage_run must exist
run_sql "BRONZE-3" "${DDL_DIR}/bronze_purchase_staging.sql"

# dq_rejections references lineage_key → lineage_run must exist
run_sql "BRONZE-4" "${DDL_DIR}/bronze_dq_rejections.sql"

# ---------------------------------------------------------------------------
# Phase 2 — Silver Fact layer
# ---------------------------------------------------------------------------
echo ""
echo "--- Phase 2: Silver Fact layer ---"

run_sql "SILVER-FACT-1" "${DDL_DIR}/silver_fact_fact_purchase.sql"

# ---------------------------------------------------------------------------
# Phase 3 — Silver Dim layer (views — depend on Dimensions team base tables)
# ---------------------------------------------------------------------------
echo ""
echo "--- Phase 3: Silver Dim layer (views) ---"
echo "    NOTE: silver_dim.supplier and silver_dim.stock_item base tables"
echo "          must be pre-loaded by the Dimensions team before these views"
echo "          can be created and return data."

run_sql "SILVER-DIM-1" "${DDL_DIR}/silver_dim_supplier_current.sql"
run_sql "SILVER-DIM-2" "${DDL_DIR}/silver_dim_stock_item_current.sql"

# ---------------------------------------------------------------------------
# Phase 4 — Grants (PD-003: resolve role matrix before running)
# ---------------------------------------------------------------------------
echo ""
echo "--- Phase 4: Unity Catalog grants ---"
echo "    WARNING: Resolve PD-003 (confirm role names) before this step."
echo "    Press ENTER to continue or Ctrl+C to skip grants."
read -r

run_sql "GRANTS" "${GRANTS_DIR}/purchase_grants.sql"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "========================================================"
echo "Deployment complete."
echo "  7 DDL files executed against catalog: ${CATALOG}"
echo ""
echo "Next steps:"
echo "  1. Verify tables exist: SHOW TABLES IN ${CATALOG}.bronze"
echo "  2. Seed etl_cutoff: run reseed_purchase_environment.py (requires PD-002 sign-off)"
echo "  3. Confirm silver_dim base tables loaded by Dimensions team"
echo "  4. Trigger nightly_etl_purchase workflow for first run"
echo "========================================================"
