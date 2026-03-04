#!/usr/bin/env python3
"""IDP Evidence Collection Orchestrator for auditclaw-grc.

Runs identity provider compliance checks (Google Workspace + Okta) and stores
results as evidence in the GRC database.

Usage:
    python3 idp_evidence.py --db-path /path/to/compliance.sqlite --all
    python3 idp_evidence.py --db-path /path/to/compliance.sqlite --provider google
    python3 idp_evidence.py --db-path /path/to/compliance.sqlite --provider okta
    python3 idp_evidence.py --db-path /path/to/compliance.sqlite --checks google_mfa,okta_mfa
    python3 idp_evidence.py --list-checks
"""

import argparse
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

from checks import ALL_CHECKS, GOOGLE_CHECKS, OKTA_CHECKS


# Map check names to relevant compliance control IDs
CONTROL_MAPPINGS = {
    "google_mfa": ["CC6.1", "A.9.4.2", "IA-2", "164.312(d)"],
    "google_admins": ["CC6.1", "CC6.3", "A.9.2.3", "164.312(a)(1)"],
    "google_inactive": ["CC6.2", "CC6.3", "A.9.2.6", "164.312(a)(1)"],
    "google_passwords": ["CC6.1", "A.9.4.3", "164.312(d)"],
    "okta_mfa": ["CC6.1", "A.9.4.2", "IA-2", "164.312(d)"],
    "okta_passwords": ["CC6.1", "A.9.4.3", "164.312(d)"],
    "okta_inactive": ["CC6.2", "CC6.3", "A.9.2.6", "164.312(a)(1)"],
    "okta_sessions": ["CC6.1", "CC6.6", "A.9.4.2", "164.312(d)"],
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
    control_id = controls[0] if controls else "CC6.1"

    cmd = [
        sys.executable, db_query,
        "--db-path", db_path,
        "--action", "add-evidence",
        "--control-id", control_id,
        "--type", "automated",
        "--source", "idp",
        "--description", f"IDP {check_name} check: {result['passed']}/{result['total']} passed",
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
        control_id = controls[0] if controls else "CC6.1"
        title = f"IDP {check_name} check"
        desc = f"IDP {check_name} check: {result['passed']}/{result['total']} passed"
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO evidence (title, control_id, type, description, source, file_content, uploaded_at)
               VALUES (?, ?, 'automated', ?, 'idp', ?, ?)""",
            (title, control_id, desc, json.dumps(result, default=str), now)
        )
        conn.commit()
        return {"status": "stored", "method": "direct"}
    finally:
        conn.close()


def update_integration_status(db_path, status, error_msg=None):
    """Update the IDP integration record after a sweep."""
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM integrations WHERE provider = 'idp' LIMIT 1").fetchone()
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


def _google_configured():
    """Check if Google Workspace env vars are set."""
    return bool(
        os.environ.get("GOOGLE_WORKSPACE_SA_KEY")
        and os.environ.get("GOOGLE_WORKSPACE_ADMIN_EMAIL")
    )


def _okta_configured():
    """Check if Okta env vars are set."""
    return bool(
        os.environ.get("OKTA_ORG_URL")
        and os.environ.get("OKTA_API_TOKEN")
    )


def _build_google_service():
    """Build the Google Admin SDK Directory service with delegated credentials."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/admin.directory.user.readonly"]
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_WORKSPACE_SA_KEY"], scopes=SCOPES
    )
    delegated = creds.with_subject(os.environ["GOOGLE_WORKSPACE_ADMIN_EMAIL"])
    return build("admin", "directory_v1", credentials=delegated)


def _build_okta_config():
    """Build the Okta client configuration dict."""
    return {
        "orgUrl": os.environ["OKTA_ORG_URL"],
        "token": os.environ["OKTA_API_TOKEN"],
    }


def run_sweep(db_path, check_names, provider="all"):
    """Run specified checks and store results."""
    results = []
    total_passed = 0
    total_failed = 0
    errors = []
    skipped = []

    update_integration_status(db_path, "syncing")

    # Build clients only when needed
    google_service = None
    okta_config = None

    google_needed = any(c in GOOGLE_CHECKS for c in check_names)
    okta_needed = any(c in OKTA_CHECKS for c in check_names)

    if google_needed:
        if _google_configured():
            try:
                google_service = _build_google_service()
            except Exception as e:
                errors.append(f"Google Workspace auth failed: {str(e)}")
        else:
            skipped.append("Google Workspace checks skipped (env vars not set)")

    if okta_needed:
        if _okta_configured():
            try:
                okta_config = _build_okta_config()
            except Exception as e:
                errors.append(f"Okta auth failed: {str(e)}")
        else:
            skipped.append("Okta checks skipped (env vars not set)")

    for check_name in check_names:
        if check_name not in ALL_CHECKS:
            errors.append(f"Unknown check: {check_name}")
            continue

        # Skip checks for unconfigured providers
        if check_name in GOOGLE_CHECKS and google_service is None:
            continue
        if check_name in OKTA_CHECKS and okta_config is None:
            continue

        check_fn = ALL_CHECKS[check_name]
        try:
            if check_name in GOOGLE_CHECKS:
                result = check_fn(google_service)
            else:
                result = check_fn(okta_config)

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
        "skipped": skipped,
        "errors": errors,
        "results": results,
    }

    print(json.dumps(output, indent=2, default=str))
    return output


def test_connection():
    """Test identity provider connectivity for configured providers."""
    results = []
    passed = 0
    failed = 0
    providers_tested = []

    # Test Google Workspace
    if _google_configured():
        providers_tested.append("google_workspace")
        try:
            service = _build_google_service()
            # Try listing 1 user to verify access
            resp = service.users().list(domain="primary", maxResults=1).execute()
            user_count = resp.get("totalUsers", "unknown")
            results.append({"service": "Google Workspace Auth", "status": "ok", "detail": "credentials valid"})
            results.append({"service": "Google Admin SDK", "status": "ok", "detail": f"accessible ({user_count} users in directory)"})
            passed += 2
        except Exception as e:
            results.append({"service": "Google Workspace", "status": "error", "detail": str(e)[:200]})
            failed += 1
    else:
        results.append({
            "service": "Google Workspace",
            "status": "not_configured",
            "detail": "Set GOOGLE_WORKSPACE_SA_KEY and GOOGLE_WORKSPACE_ADMIN_EMAIL to enable."
        })

    # Test Okta
    if _okta_configured():
        providers_tested.append("okta")
        try:
            import requests
            org_url = os.environ["OKTA_ORG_URL"].rstrip("/")
            if not org_url.startswith("https://"):
                print(json.dumps({"status": "error", "message": "OKTA_ORG_URL must use HTTPS"}))
                sys.exit(1)
            token = os.environ["OKTA_API_TOKEN"]
            headers = {"Authorization": f"SSWS {token}", "Accept": "application/json"}
            # Test user endpoint
            resp = requests.get(f"{org_url}/api/v1/users?limit=1", headers=headers, timeout=10)
            if resp.status_code == 200:
                results.append({"service": "Okta Auth", "status": "ok", "detail": "credentials valid"})
                results.append({"service": "Okta Users API", "status": "ok", "detail": "accessible"})
                passed += 2
            elif resp.status_code == 401:
                results.append({"service": "Okta", "status": "denied", "detail": "Token invalid or expired"})
                failed += 1
            else:
                results.append({"service": "Okta", "status": "error", "detail": f"HTTP {resp.status_code}: {resp.text[:200]}"})
                failed += 1
        except ImportError:
            results.append({"service": "Okta", "status": "error", "detail": "requests not installed. Run: pip install requests"})
            failed += 1
        except Exception as e:
            results.append({"service": "Okta", "status": "error", "detail": str(e)[:200]})
            failed += 1
    else:
        results.append({
            "service": "Okta",
            "status": "not_configured",
            "detail": "Set OKTA_ORG_URL and OKTA_API_TOKEN to enable."
        })

    output = {
        "status": "ok",
        "provider": "idp",
        "providers_tested": providers_tested,
        "total_checks": len(results),
        "accessible": passed,
        "denied": failed,
        "all_passed": failed == 0,
        "results": results,
    }
    print(json.dumps(output, indent=2, default=str))
    return output


def main():
    parser = argparse.ArgumentParser(description="IDP Evidence Collection for auditclaw-grc")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to GRC compliance.sqlite database")
    parser.add_argument("--all", action="store_true", help="Run all checks for configured providers")
    parser.add_argument("--checks", help="Comma-separated list of checks to run")
    parser.add_argument("--provider", choices=["google", "okta", "all"], default="all",
                        help="Provider to run checks for (default: all)")
    parser.add_argument("--list-checks", action="store_true", help="List available checks")
    parser.add_argument("--test-connection", action="store_true", help="Test IDP connectivity")

    args = parser.parse_args()

    if args.list_checks:
        print(json.dumps({
            "checks": list(ALL_CHECKS.keys()),
            "google_checks": list(GOOGLE_CHECKS),
            "okta_checks": list(OKTA_CHECKS),
        }))
        return

    if args.test_connection:
        test_connection()
        return

    if args.all:
        if args.provider == "google":
            check_names = list(GOOGLE_CHECKS)
        elif args.provider == "okta":
            check_names = list(OKTA_CHECKS)
        else:
            check_names = list(ALL_CHECKS.keys())
    elif args.checks:
        check_names = [c.strip() for c in args.checks.split(",")]
    else:
        parser.error("Specify --all or --checks <list>")
        return

    run_sweep(args.db_path, check_names, provider=args.provider)


if __name__ == "__main__":
    main()
