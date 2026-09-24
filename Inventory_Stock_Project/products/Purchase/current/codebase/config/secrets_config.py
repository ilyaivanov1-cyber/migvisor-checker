# CFG-006: Databricks Secrets bootstrap script.
# Creates scopes and registers required key names for the Purchase ETL pipeline.
# Actual secret VALUES are supplied interactively or via environment variables — never hardcoded here.
# Run once per environment (dev / prod) before deploying the pipeline.

"""
Usage:
    python config/secrets_config.py --env dev
    python config/secrets_config.py --env prod

Prerequisites:
    - Databricks CLI installed and authenticated (DATABRICKS_HOST + DATABRICKS_TOKEN set)
    - Run config/secrets_setup.md for step-by-step instructions
"""

from __future__ import annotations

import argparse
import getpass
import subprocess
import sys


SCOPES = {
    "dev": "inventory-stock-dev",
    "prod": "inventory-stock-prod",
}

REQUIRED_KEYS = ["jdbc_url", "jdbc_username", "jdbc_password"]


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result


def scope_exists(scope: str) -> bool:
    result = subprocess.run(
        ["databricks", "secrets", "list-scopes", "--output", "json"],
        capture_output=True,
        text=True,
    )
    return scope in result.stdout


def create_scope(scope: str) -> None:
    if scope_exists(scope):
        print(f"Scope '{scope}' already exists — skipping creation.")
        return
    print(f"Creating scope '{scope}' ...")
    _run(["databricks", "secrets", "create-scope", "--scope", scope])
    print(f"Scope '{scope}' created.")


def register_key(scope: str, key: str, dry_run: bool = False) -> None:
    print(f"Registering key '{key}' in scope '{scope}' ...")
    if dry_run:
        print(f"  [dry-run] Would register key '{key}' — skipping.")
        return
    print(f"  Enter value for {key} (input is hidden in terminal):")
    value = getpass.getpass(prompt="  > ")
    _run(["databricks", "secrets", "put", "--scope", scope, "--key", key, "--string-value", value])
    print(f"  Key '{key}' registered. Value is not logged.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap Databricks Secrets for inventory-stock")
    parser.add_argument("--env", choices=["dev", "prod"], required=True)
    parser.add_argument("--dry-run", action="store_true", help="Preview scope/key registration without executing any CLI commands")
    args = parser.parse_args()

    scope = SCOPES[args.env]
    if args.dry_run:
        print(f"\n=== [DRY RUN] Would bootstrap secrets for environment: {args.env} (scope: {scope}) ===\n")
    else:
        print(f"\n=== Bootstrapping secrets for environment: {args.env} (scope: {scope}) ===\n")

    if not args.dry_run:
        create_scope(scope)

    for key in REQUIRED_KEYS:
        register_key(scope, key, dry_run=args.dry_run)

    print(f"\nAll keys registered in scope '{scope}'.")
    print(f"Verify with: databricks secrets list --scope {scope}")


if __name__ == "__main__":
    main()
