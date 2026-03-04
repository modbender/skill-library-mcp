#!/usr/bin/env python3
"""GitHub Evidence Collection Orchestrator for auditclaw-grc.

Runs GitHub compliance checks and stores results as evidence in the GRC database.

Usage:
    python3 github_evidence.py --db-path /path/to/compliance.sqlite --org my-org --all
    python3 github_evidence.py --db-path /path/to/compliance.sqlite --org my-org --checks branch_protection,secret_scanning
"""

import argparse
import json
import os
import sqlite3

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")
import subprocess
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from checks import ALL_CHECKS

CONTROL_MAPPINGS = {
    "branch_protection": ["CC8.1", "CC6.1", "A.14.2", "164.312(e)(1)"],
    "secret_scanning": ["CC6.1", "CC6.7", "A.9.4", "164.312(a)(1)"],
    "dependabot": ["CC7.1", "CC8.1", "A.12.6", "164.308(a)(1)(ii)(A)"],
    "two_factor": ["CC6.1", "CC6.2", "A.9.4", "164.312(d)"],
    "deploy_keys": ["CC6.1", "CC6.3", "A.9.2", "164.312(a)(1)"],
    "audit_log": ["CC7.2", "CC7.3", "A.12.4", "164.312(b)"],
    "webhooks": ["CC6.1", "CC6.7", "A.13.1", "164.312(e)(1)"],
    "codeowners": ["CC8.1", "CC2.2", "A.14.2", "164.308(a)(4)(ii)(C)"],
    "ci_cd": ["CC8.1", "CC7.1", "A.14.2", "164.312(e)(1)"],
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
    controls = CONTROL_MAPPINGS.get(check_name, [])
    control_id = controls[0] if controls else "CC7.1"

    if db_query:
        cmd = [
            sys.executable, db_query,
            "--db-path", db_path,
            "--action", "add-evidence",
            "--control-id", control_id,
            "--type", "automated",
            "--source", "github",
            "--description", f"GitHub {check_name} check: {result['passed']}/{result['total']} passed",
            "--file-content", json.dumps(result, default=str),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return {"status": "stored", "method": "db_query"}

    # Direct DB insert fallback
    return _store_evidence_direct(db_path, check_name, result)


def _store_evidence_direct(db_path, check_name, result):
    """Direct DB insert fallback if db_query.py not available."""
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        controls = CONTROL_MAPPINGS.get(check_name, [])
        control_id = controls[0] if controls else "CC7.1"
        title = f"GitHub {check_name} check"
        desc = f"GitHub {check_name} check: {result['passed']}/{result['total']} passed"
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO evidence (title, control_id, type, description, source, file_content, uploaded_at)
               VALUES (?, ?, 'automated', ?, 'github', ?, ?)""",
            (title, control_id, desc, json.dumps(result, default=str), now)
        )
        conn.commit()
        return {"status": "stored", "method": "direct"}
    finally:
        conn.close()


def update_integration_status(db_path, status, error_msg=None):
    """Update the GitHub integration record after a sweep."""
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM integrations WHERE provider = 'github' LIMIT 1").fetchone()
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


def run_sweep(db_path, org_name, check_names, token=None):
    """Run specified checks and store results."""
    try:
        from github import Github
    except ImportError:
        print(json.dumps({
            "status": "error",
            "message": "PyGithub not installed. Run: pip install PyGithub"
        }), file=sys.stderr)
        sys.exit(1)

    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print(json.dumps({
            "status": "error",
            "message": "GITHUB_TOKEN not set"
        }), file=sys.stderr)
        sys.exit(1)

    g = Github(token)
    org = g.get_organization(org_name)

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
            result = check_fn(org, g)
            total_passed += result.get("passed", 0)
            total_failed += result.get("failed", 0)
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
            results.append({"check": check_name, "status": "error", "error": str(e)})

    overall_status = "pass" if total_failed == 0 and not errors else "fail"

    if errors:
        update_integration_status(db_path, "error", "; ".join(errors))
    else:
        update_integration_status(db_path, "active")

    output = {
        "status": "ok",
        "sweep_status": overall_status,
        "org": org_name,
        "checks_run": len(results),
        "total_findings": total_passed + total_failed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "errors": errors,
        "results": results,
    }

    print(json.dumps(output, indent=2, default=str))
    return output


def test_connection(token=None):
    """Test GitHub connectivity by verifying token and checking accessible scopes."""
    try:
        from github import Github, GithubException
    except ImportError:
        print(json.dumps({"status": "error", "message": "PyGithub not installed. Run: pip install PyGithub"}))
        sys.exit(1)

    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print(json.dumps({"status": "error", "message": "GITHUB_TOKEN not set. Create a token at GitHub → Settings → Developer Settings → Personal Access Tokens."}))
        sys.exit(1)

    g = Github(token)
    results = []
    passed = 0
    failed = 0

    # Test basic auth
    try:
        user = g.get_user()
        username = user.login
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Token invalid or expired: {str(e)}"}))
        sys.exit(1)

    # Test repo access
    probes = {
        "User Authentication": lambda: user.login,
        "List Organizations": lambda: [o.login for o in g.get_user().get_orgs()],
        "List Repositories": lambda: g.get_user().get_repos(sort="updated").get_page(0)[:1],
        "Rate Limit": lambda: g.get_rate_limit().core.remaining,
    }

    for probe_name, probe_fn in probes.items():
        try:
            probe_fn()
            results.append({"check": probe_name, "status": "ok", "detail": "accessible"})
            passed += 1
        except Exception as e:
            results.append({"check": probe_name, "status": "denied", "detail": str(e)})
            failed += 1

    rate_limit = g.get_rate_limit()
    output = {
        "status": "ok",
        "provider": "github",
        "authenticated_as": username,
        "rate_limit_remaining": rate_limit.core.remaining,
        "rate_limit_total": rate_limit.core.limit,
        "total_checks": len(results),
        "accessible": passed,
        "denied": failed,
        "all_passed": failed == 0,
        "results": results,
        "note": "For full check coverage, ensure the token has repo, read:org, and security_events scopes.",
    }
    print(json.dumps(output, indent=2, default=str))
    return output


def main():
    parser = argparse.ArgumentParser(description="GitHub Evidence Collection for auditclaw-grc")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to GRC compliance.sqlite database")
    parser.add_argument("--org", help="GitHub organization name")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    parser.add_argument("--checks", help="Comma-separated list of checks to run")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--list-checks", action="store_true", help="List available checks")
    parser.add_argument("--test-connection", action="store_true", help="Test GitHub connectivity")

    args = parser.parse_args()

    if args.list_checks:
        print(json.dumps({"checks": list(ALL_CHECKS.keys())}))
        return

    if args.test_connection:
        test_connection(token=args.token)
        return

    if not args.org:
        parser.error("--org is required (unless using --list-checks or --test-connection)")

    if args.all:
        check_names = list(ALL_CHECKS.keys())
    elif args.checks:
        check_names = [c.strip() for c in args.checks.split(",")]
    else:
        parser.error("Specify --all or --checks <list>")
        return

    run_sweep(args.db_path, args.org, check_names, token=args.token)


if __name__ == "__main__":
    main()
