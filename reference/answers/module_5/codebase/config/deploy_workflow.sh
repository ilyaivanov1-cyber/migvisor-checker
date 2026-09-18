#!/usr/bin/env bash
# CFG-009: Deployment script — upload notebooks and create/update the Databricks Workflow.
# Usage: ./config/deploy_workflow.sh --env dev|prod
# Requires: DATABRICKS_HOST and DATABRICKS_TOKEN set in environment.
# Exits non-zero on any error.

set -euo pipefail

# ── Argument parsing ──────────────────────────────────────────────────────────
ENV=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --env) ENV="$2"; shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$ENV" ]]; then
    echo "ERROR: --env dev|prod is required." >&2
    exit 1
fi

if [[ "$ENV" != "dev" && "$ENV" != "prod" ]]; then
    echo "ERROR: --env must be 'dev' or 'prod'." >&2
    exit 1
fi

# ── Prerequisites check ───────────────────────────────────────────────────────
if ! command -v databricks &>/dev/null; then
    echo "ERROR: Databricks CLI not found. Install it and retry." >&2
    exit 1
fi

if [[ -z "${DATABRICKS_HOST:-}" ]]; then
    echo "ERROR: DATABRICKS_HOST is not set." >&2
    exit 1
fi

if [[ -z "${DATABRICKS_TOKEN:-}" ]]; then
    echo "ERROR: DATABRICKS_TOKEN is not set." >&2
    exit 1
fi

CLI_VERSION=$(databricks --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
echo "Databricks CLI version: ${CLI_VERSION}"

# ── Configuration ─────────────────────────────────────────────────────────────
WORKSPACE_PATH="/Shared/globalpurchase"
NOTEBOOK_DIR="src/etl"
WORKFLOW_CONFIG="config/workflow_nightly_etl_main.yml"
JOB_NAME="globalpurchase_nightly_etl_main"

echo "=== Deploying to environment: ${ENV} ==="
echo "Workspace: ${DATABRICKS_HOST}"

# ── Step 1: Upload notebooks ──────────────────────────────────────────────────
echo "Uploading notebooks from ${NOTEBOOK_DIR}/ to ${WORKSPACE_PATH}/..."

find "${NOTEBOOK_DIR}" -name "*.py" | while read -r notebook; do
    target="${WORKSPACE_PATH}/${notebook%.py}"
    target_dir=$(dirname "$target")
    echo "  Uploading: ${notebook} → ${target}"
    databricks workspace mkdirs "${target_dir}" 2>/dev/null || true
    databricks workspace import \
        --language PYTHON \
        --format SOURCE \
        --overwrite \
        "${notebook}" \
        "${target}"
done

echo "Notebook upload complete."

# ── Step 2: Create or update the Workflow ────────────────────────────────────
echo "Checking if job '${JOB_NAME}' exists..."

EXISTING_JOB_ID=$(databricks jobs list --output json 2>/dev/null \
    | python3 -c "
import json, sys
jobs = json.load(sys.stdin).get('jobs', [])
match = [j['job_id'] for j in jobs if j.get('settings', {}).get('name') == '${JOB_NAME}']
print(match[0] if match else '')
" 2>/dev/null || echo "")

if [[ -n "$EXISTING_JOB_ID" ]]; then
    echo "Updating existing job ID: ${EXISTING_JOB_ID}"
    databricks jobs reset --job-id "${EXISTING_JOB_ID}" --json "@${WORKFLOW_CONFIG}"
    echo "Job updated."
else
    echo "Creating new job '${JOB_NAME}'..."
    databricks jobs create --json "@${WORKFLOW_CONFIG}"
    echo "Job created."
fi

echo ""
echo "=== Deployment complete for environment: ${ENV} ==="
