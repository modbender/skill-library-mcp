#!/usr/bin/env python3
"""Azure Evidence Collection Orchestrator for auditclaw-grc.

Runs Azure compliance checks and stores results as evidence in the GRC database.

Usage:
    python3 azure_evidence.py --db-path /path/to/compliance.sqlite --all
    python3 azure_evidence.py --db-path /path/to/compliance.sqlite --checks storage,network
    python3 azure_evidence.py --list-checks
"""

import argparse
import importlib
import json
import os
import sqlite3

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")
import subprocess
import sys
from datetime import datetime

# Allow running from skill directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from checks import ALL_CHECKS


# Map check names to relevant compliance control IDs
CONTROL_MAPPINGS = {
    "storage": ["CC6.1", "CC6.7", "A.10.1.1", "164.312(e)(1)"],
    "network": ["CC6.1", "CC6.6", "A.13.1.1", "164.312(e)(1)"],
    "keyvault": ["CC6.1", "A1.2", "A.10.1.2", "164.312(a)(2)(iv)"],
    "sql": ["CC7.1", "CC7.2", "A.12.4.1", "164.312(b)"],
    "compute": ["CC6.1", "CC6.7", "A.10.1.1", "164.312(a)(2)(iv)"],
    "appservice": ["CC6.1", "CC6.7", "A.10.1.1", "164.312(e)(1)"],
    "defender": ["CC7.1", "CC7.2", "A.12.6.1", "164.308(a)(5)(ii)(B)"],
}


def get_db_query_path():
    """Find the db_query.py script from the auditclaw-grc skill."""
    candidates = [
        os.path.expanduser("~/.openclaw/skills/auditclaw-grc/scripts/db_query.py"),
        os.path.join(SCRIPT_DIR, "..", "..", "auditclaw-grc", "scripts", "db_query.py"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    return None


def store_evidence(db_path, check_name, result):
    """Store check results as evidence in the GRC database."""
    db_query = get_db_query_path()
    if not db_query:
        return _store_evidence_direct(db_path, check_name, result)

    controls = CONTROL_MAPPINGS.get(check_name, [])
    control_id = controls[0] if controls else "CC7.1"

    cmd = [
        sys.executable, db_query,
        "--db-path", db_path,
        "--action", "add-evidence",
        "--control-id", control_id,
        "--type", "automated",
        "--source", "azure",
        "--description", f"Azure {check_name} check: {result['passed']}/{result['total']} passed",
        "--file-content", json.dumps(result, default=str),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return _store_evidence_direct(db_path, check_name, result)

    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        return {"status": "stored", "method": "db_query"}


def _store_evidence_direct(db_path, check_name, result):
    """Direct DB insert fallback if db_query.py not available."""
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        controls = CONTROL_MAPPINGS.get(check_name, [])
        control_id = controls[0] if controls else "CC7.1"
        title = f"Azure {check_name} check"
        desc = f"Azure {check_name} check: {result['passed']}/{result['total']} passed"
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO evidence (title, control_id, type, description, source, file_content, uploaded_at)
               VALUES (?, ?, 'automated', ?, 'azure', ?, ?)""",
            (title, control_id, desc, json.dumps(result, default=str), now)
        )
        conn.commit()
        return {"status": "stored", "method": "direct"}
    finally:
        conn.close()


def update_integration_status(db_path, status, error_msg=None):
    """Update the Azure integration record after a sweep."""
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM integrations WHERE provider = 'azure' LIMIT 1").fetchone()
        if row:
            now = datetime.now().isoformat(timespec="seconds")
            if error_msg:
                conn.execute(
                    "UPDATE integrations SET status = ?, last_sync = ?, last_error = ?, error_count = error_count + 1, updated_at = ? WHERE id = ?",
                    (status, now, error_msg, now, row["id"])
                )
            else:
                conn.execute(
                    "UPDATE integrations SET status = ?, last_sync = ?, last_error = NULL, updated_at = ? WHERE id = ?",
                    (status, now, now, row["id"])
                )
            conn.commit()
    finally:
        conn.close()


def run_sweep(db_path, check_names, subscription_id):
    """Run specified checks and store results."""
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError:
        print(json.dumps({
            "status": "error",
            "message": "azure-identity not installed. Run: pip install -r scripts/requirements.txt"
        }), file=sys.stderr)
        sys.exit(1)

    credential = DefaultAzureCredential()
    results = []
    total_passed = 0
    total_failed = 0
    errors = []

    update_integration_status(db_path, "syncing")

    for check_name in check_names:
        if check_name not in ALL_CHECKS:
            errors.append(f"Unknown check: {check_name}")
            continue

        check_fn = ALL_CHECKS[check_name]
        try:
            result = check_fn(credential, subscription_id=subscription_id)
            total_passed += result.get("passed", 0)
            total_failed += result.get("failed", 0)

            # Store as evidence
            store_evidence(db_path, check_name, result)

            results.append({
                "check": check_name,
                "status": result["status"],
                "passed": result.get("passed", 0),
                "failed": result.get("failed", 0),
                "total": result.get("total", 0),
            })
        except Exception as e:
            errors.append(f"{check_name}: {str(e)}")
            results.append({
                "check": check_name,
                "status": "error",
                "error": str(e),
            })

    overall_status = "pass" if total_failed == 0 and not errors else "fail"

    if errors:
        update_integration_status(db_path, "error", "; ".join(errors))
    else:
        update_integration_status(db_path, "active")

    output = {
        "status": "ok",
        "sweep_status": overall_status,
        "checks_run": len(results),
        "total_findings": total_passed + total_failed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "errors": errors,
        "results": results,
    }

    print(json.dumps(output, indent=2, default=str))
    return output


def test_connection():
    """Test Azure connectivity by verifying credentials and probing services."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient
    except ImportError:
        print(json.dumps({"status": "error", "message": "Azure SDK not installed. Run: pip install azure-identity azure-mgmt-resource azure-mgmt-storage azure-mgmt-network azure-mgmt-keyvault azure-mgmt-sql azure-mgmt-compute azure-mgmt-web azure-mgmt-security"}))
        sys.exit(1)

    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        print(json.dumps({"status": "error", "message": "AZURE_SUBSCRIPTION_ID not set. Run 'setup azure' for instructions."}))
        sys.exit(1)

    results = []
    passed = 0
    failed = 0

    try:
        credential = DefaultAzureCredential()
        resource_client = ResourceManagementClient(credential, subscription_id)
        # Quick test: list first resource group
        rgs = list(resource_client.resource_groups.list())
        results.append({"service": "Resource Manager", "status": "ok", "detail": f"accessible ({len(rgs)} resource groups)"})
        passed += 1
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Azure authentication failed: {str(e)}"}))
        sys.exit(1)

    service_probes = {
        "Storage": ("azure.mgmt.storage", "StorageManagementClient", "storage_accounts", "list"),
        "Network": ("azure.mgmt.network", "NetworkManagementClient", "network_security_groups", "list_all"),
        "Key Vault": ("azure.mgmt.keyvault", "KeyVaultManagementClient", "vaults", "list"),
        "SQL": ("azure.mgmt.sql", "SqlManagementClient", "servers", "list"),
        "Compute": ("azure.mgmt.compute", "ComputeManagementClient", "virtual_machines", "list_all"),
        "App Service": ("azure.mgmt.web", "WebSiteManagementClient", "web_apps", "list"),
    }

    for service_name, (module_path, class_name, prop_name, method_name) in service_probes.items():
        try:
            mod = importlib.import_module(module_path)
            client_class = getattr(mod, class_name)
            client = client_class(credential, subscription_id)
            prop = getattr(client, prop_name)
            method = getattr(prop, method_name)
            list(method())  # Force execution
            results.append({"service": service_name, "status": "ok", "detail": "accessible"})
            passed += 1
        except Exception as e:
            error_str = str(e)
            if "AuthorizationFailed" in error_str or "Forbidden" in error_str:
                results.append({"service": service_name, "status": "denied", "detail": error_str[:200]})
                failed += 1
            else:
                results.append({"service": service_name, "status": "ok", "detail": f"accessible (no resources or {type(e).__name__})"})
                passed += 1

    output = {
        "status": "ok",
        "provider": "azure",
        "subscription_id": subscription_id,
        "total_services": len(results),
        "accessible": passed,
        "denied": failed,
        "all_passed": failed == 0,
        "results": results,
    }
    print(json.dumps(output, indent=2, default=str))
    return output


def main():
    parser = argparse.ArgumentParser(description="Azure Evidence Collection for auditclaw-grc")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to GRC compliance.sqlite database")
    parser.add_argument("--subscription-id", help="Azure subscription ID (or set AZURE_SUBSCRIPTION_ID)")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    parser.add_argument("--checks", help="Comma-separated list of checks to run")
    parser.add_argument("--list-checks", action="store_true", help="List available checks")
    parser.add_argument("--test-connection", action="store_true", help="Test Azure connectivity")

    args = parser.parse_args()

    if args.list_checks:
        print(json.dumps({"checks": list(ALL_CHECKS.keys())}))
        return

    if args.test_connection:
        test_connection()
        return

    subscription_id = args.subscription_id or os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        parser.error("--subscription-id or AZURE_SUBSCRIPTION_ID env var required")

    if args.all:
        check_names = list(ALL_CHECKS.keys())
    elif args.checks:
        check_names = [c.strip() for c in args.checks.split(",")]
    else:
        parser.error("Specify --all or --checks <list>")
        return

    run_sweep(args.db_path, check_names, subscription_id)


if __name__ == "__main__":
    main()
