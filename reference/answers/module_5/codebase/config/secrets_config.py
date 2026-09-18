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
import subprocess
import sys


SCOPES = {
    "dev": "globalpurchase-dev",
    "prod": "globalpurchase-prod",
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


def register_key(scope: str, key: str) -> None:
    print(f"Registering key '{key}' in scope '{scope}' ...")
    print(f"  Enter value for {key} (input is hidden in terminal):")
    import getpass
    value = getpass.getpass(prompt="  > ")
    _run(["databricks", "secrets", "put", "--scope", scope, "--key", key, "--string-value", value])
    print(f"  Key '{key}' registered. Value is not logged.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap Databricks Secrets for globalpurchase")
    parser.add_argument("--env", choices=["dev", "prod"], required=True)
    args = parser.parse_args()

    scope = SCOPES[args.env]
    print(f"\n=== Bootstrapping secrets for environment: {args.env} (scope: {scope}) ===\n")

    create_scope(scope)

    for key in REQUIRED_KEYS:
        register_key(scope, key)

    print(f"\nAll keys registered in scope '{scope}'.")
    print(f"Verify with: databricks secrets list --scope {scope}")


if __name__ == "__main__":
    main()
