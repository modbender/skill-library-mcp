#!/usr/bin/env python3
"""GCP Evidence Collection Orchestrator for auditclaw-grc.

Runs GCP compliance checks and stores results as evidence in the GRC database.

Usage:
    python3 gcp_evidence.py --db-path /path/to/compliance.sqlite --all
    python3 gcp_evidence.py --db-path /path/to/compliance.sqlite --checks storage,firewall,iam
    python3 gcp_evidence.py --db-path /path/to/compliance.sqlite --project-id my-project
    python3 gcp_evidence.py --list-checks
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
    "storage": ["CC6.1", "CC6.3", "A.8.3", "164.312(a)(1)"],
    "firewall": ["CC6.1", "CC6.6", "A.8.20", "164.312(e)(1)"],
    "iam": ["CC6.1", "CC6.3", "A.5.15", "164.312(a)(1)"],
    "logging": ["CC7.1", "CC7.2", "A.8.15", "164.312(b)"],
    "kms": ["CC6.1", "A.8.24", "164.312(a)(2)(iv)"],
    "dns": ["CC6.6", "A.8.20"],
    "bigquery": ["CC6.1", "CC6.6", "A.8.3", "164.312(a)(1)"],
    "compute": ["CC6.1", "CC6.3", "A.5.15", "164.312(a)(1)"],
    "cloudsql": ["CC6.1", "CC6.6", "A.8.20", "164.312(a)(1)"],
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
        "--source", "gcp",
        "--description", f"GCP {check_name} check: {result['passed']}/{result['total']} passed",
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
        title = f"GCP {check_name} check"
        desc = f"GCP {check_name} check: {result['passed']}/{result['total']} passed"
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO evidence (title, control_id, type, description, source, file_content, uploaded_at)
               VALUES (?, ?, 'automated', ?, 'gcp', ?, ?)""",
            (title, control_id, desc, json.dumps(result, default=str), now)
        )
        conn.commit()
        return {"status": "stored", "method": "direct"}
    finally:
        conn.close()


def update_integration_status(db_path, status, error_msg=None):
    """Update the GCP integration record after a sweep."""
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM integrations WHERE provider = 'gcp' LIMIT 1").fetchone()
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


def run_sweep(db_path, check_names, project_id):
    """Run specified checks and store results."""
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
            result = check_fn(project_id)
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
    """Test GCP connectivity by verifying credentials and probing services."""
    try:
        from google.cloud import storage as gcs
        from google.auth import default as auth_default
    except ImportError:
        print(json.dumps({"status": "error", "message": "Google Cloud SDK not installed. Run: pip install google-cloud-storage google-cloud-compute google-cloud-kms google-cloud-logging google-cloud-dns google-cloud-resource-manager"}))
        sys.exit(1)

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print(json.dumps({"status": "error", "message": "GCP_PROJECT_ID not set. Run 'setup gcp' for instructions."}))
        sys.exit(1)

    results = []
    passed = 0
    failed = 0

    # Verify credentials
    try:
        credentials, detected_project = auth_default()
        results.append({"service": "Authentication", "status": "ok", "detail": f"credentials valid (project: {detected_project or project_id})"})
        passed += 1
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"GCP authentication failed: {str(e)}. Set GOOGLE_APPLICATION_CREDENTIALS."}))
        sys.exit(1)

    # Dynamically test services
    optional_probes = [
        ("Compute Engine", "google.cloud.compute_v1", "InstancesClient", "aggregated_list", {"project": project_id, "max_results": 1}),
        ("Cloud KMS", "google.cloud.kms_v1", "KeyManagementServiceClient", "list_key_rings", {"parent": f"projects/{project_id}/locations/global"}),
        ("Cloud Logging", "google.cloud.logging_v2", "Client", None, None),
    ]

    # Test Cloud Storage first (most common)
    try:
        list(gcs.Client(project=project_id).list_buckets(max_results=1))
        results.append({"service": "Cloud Storage", "status": "ok", "detail": "accessible"})
        passed += 1
    except Exception as e:
        if "403" in str(e) or "Forbidden" in str(e):
            results.append({"service": "Cloud Storage", "status": "denied", "detail": str(e)[:200]})
            failed += 1
        else:
            results.append({"service": "Cloud Storage", "status": "ok", "detail": f"accessible ({type(e).__name__})"})
            passed += 1

    # Test remaining services
    for service_name, module_path, class_name, method_name, kwargs in optional_probes:
        try:
            mod = importlib.import_module(module_path)
            client_class = getattr(mod, class_name)
            if method_name:
                client = client_class()
                method = getattr(client, method_name)
                list(method(**kwargs))
            else:
                client_class(project=project_id)
            results.append({"service": service_name, "status": "ok", "detail": "accessible"})
            passed += 1
        except ImportError:
            results.append({"service": service_name, "status": "skipped", "detail": "SDK not installed"})
        except Exception as e:
            if "403" in str(e) or "PERMISSION_DENIED" in str(e):
                results.append({"service": service_name, "status": "denied", "detail": str(e)[:200]})
                failed += 1
            else:
                results.append({"service": service_name, "status": "ok", "detail": f"accessible ({type(e).__name__})"})
                passed += 1

    output = {
        "status": "ok",
        "provider": "gcp",
        "project_id": project_id,
        "total_services": len(results),
        "accessible": passed,
        "denied": failed,
        "all_passed": failed == 0,
        "results": results,
    }
    print(json.dumps(output, indent=2, default=str))
    return output


def main():
    parser = argparse.ArgumentParser(description="GCP Evidence Collection for auditclaw-grc")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to GRC compliance.sqlite database")
    parser.add_argument("--project-id", help="GCP project ID (or set GCP_PROJECT_ID env var)")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    parser.add_argument("--checks", help="Comma-separated list of checks to run")
    parser.add_argument("--list-checks", action="store_true", help="List available checks")
    parser.add_argument("--test-connection", action="store_true", help="Test GCP connectivity")

    args = parser.parse_args()

    if args.list_checks:
        print(json.dumps({"checks": list(ALL_CHECKS.keys())}))
        return

    if args.test_connection:
        test_connection()
        return

    project_id = args.project_id or os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        parser.error("--project-id or GCP_PROJECT_ID env var is required")

    if args.all:
        check_names = list(ALL_CHECKS.keys())
    elif args.checks:
        check_names = [c.strip() for c in args.checks.split(",")]
    else:
        parser.error("Specify --all or --checks <list>")
        return

    run_sweep(args.db_path, check_names, project_id)


if __name__ == "__main__":
    main()
