#!/usr/bin/env python3
"""AWS Evidence Collection Orchestrator for auditclaw-grc.

Runs AWS compliance checks and stores results as evidence in the GRC database.

Usage:
    python3 aws_evidence.py --db-path /path/to/compliance.sqlite --all
    python3 aws_evidence.py --db-path /path/to/compliance.sqlite --checks iam,s3,cloudtrail
    python3 aws_evidence.py --db-path /path/to/compliance.sqlite --checks iam --region us-west-2
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

from checks import ALL_CHECKS


# Map check names to relevant compliance control IDs
CONTROL_MAPPINGS = {
    "iam": ["CC6.1", "CC6.2", "CC6.3", "A.9.2", "A.9.4", "164.312(d)"],
    "s3": ["CC6.1", "CC6.7", "A.8.2", "A.10.1", "164.312(a)(2)(iv)"],
    "cloudtrail": ["CC7.2", "CC7.3", "A.12.4", "164.312(b)"],
    "vpc": ["CC6.1", "CC6.6", "A.13.1", "164.312(e)(1)"],
    "kms": ["CC6.1", "CC6.7", "A.10.1", "164.312(a)(2)(iv)"],
    "ec2": ["CC6.1", "CC6.6", "CC6.8", "A.13.1", "164.310(a)(1)"],
    "rds": ["CC6.1", "CC6.7", "A.12.3", "164.308(a)(7)(ii)(A)"],
    "security_hub": ["CC7.1", "CC7.2", "A.12.6", "164.308(a)(1)(ii)(A)"],
    "guardduty": ["CC7.2", "CC7.3", "A.12.6", "164.308(a)(1)(ii)(D)"],
    "lambda": ["CC6.1", "CC6.6", "CC6.8", "A.14.2"],
    "cloudwatch": ["CC7.2", "CC7.3", "A.12.4", "164.312(b)"],
    "config": ["CC7.1", "CC8.1", "A.12.1", "164.308(a)(8)"],
    "eks_ecs": ["CC6.1", "CC6.6", "A.13.1", "164.312(e)(1)"],
    "elb": ["CC6.1", "CC6.7", "A.13.1", "164.312(e)(1)"],
    "credential_report": ["CC6.1", "CC6.2", "CC6.3", "A.9.2", "164.312(d)"],
}


def get_db_query_path():
    """Find the db_query.py script from the auditclaw-grc skill."""
    # Look in standard locations
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
        # Fall back to direct DB insert
        return _store_evidence_direct(db_path, check_name, result)

    controls = CONTROL_MAPPINGS.get(check_name, [])
    control_id = controls[0] if controls else "CC7.1"

    cmd = [
        sys.executable, db_query,
        "--db-path", db_path,
        "--action", "add-evidence",
        "--control-id", control_id,
        "--type", "automated",
        "--source", "aws",
        "--description", f"AWS {check_name} check: {result['passed']}/{result['total']} passed",
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
        title = f"AWS {check_name} check"
        desc = f"AWS {check_name} check: {result['passed']}/{result['total']} passed"
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO evidence (title, control_id, type, description, source, file_content, uploaded_at)
               VALUES (?, ?, 'automated', ?, 'aws', ?, ?)""",
            (title, control_id, desc, json.dumps(result, default=str), now)
        )
        conn.commit()
        return {"status": "stored", "method": "direct"}
    finally:
        conn.close()


def update_integration_status(db_path, status, error_msg=None):
    """Update the AWS integration record after a sweep."""
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM integrations WHERE provider = 'aws' LIMIT 1").fetchone()
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


def run_sweep(db_path, check_names, region="us-east-1"):
    """Run specified checks and store results."""
    try:
        import boto3
    except ImportError:
        print(json.dumps({
            "status": "error",
            "message": "boto3 not installed. Run: pip install boto3"
        }), file=sys.stderr)
        sys.exit(1)

    session = boto3.Session()
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
            result = check_fn(session, region=region)
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


def test_connection(region="us-east-1"):
    """Test AWS connectivity by probing each service with a lightweight API call."""
    try:
        import boto3
    except ImportError:
        print(json.dumps({"status": "error", "message": "boto3 not installed. Run: pip install boto3"}))
        sys.exit(1)

    session = boto3.Session()

    # Verify credentials exist
    creds = session.get_credentials()
    if not creds:
        print(json.dumps({"status": "error", "message": "No AWS credentials found. Run 'aws configure' or set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY."}))
        sys.exit(1)

    # Test each service with a lightweight probe
    service_probes = {
        "IAM": ("iam", "list_users", {"MaxItems": 1}),
        "S3": ("s3", "list_buckets", {}),
        "EC2": ("ec2", "describe_vpcs", {"MaxResults": 5}),
        "CloudTrail": ("cloudtrail", "describe_trails", {}),
        "KMS": ("kms", "list_keys", {"Limit": 1}),
        "RDS": ("rds", "describe_db_instances", {}),
        "SecurityHub": ("securityhub", "describe_hub", {}),
        "GuardDuty": ("guardduty", "list_detectors", {"MaxResults": 1}),
        "Lambda": ("lambda", "list_functions", {"MaxItems": 1}),
        "CloudWatch": ("cloudwatch", "describe_alarms", {"MaxRecords": 1}),
        "CloudWatch Logs": ("logs", "describe_log_groups", {"limit": 1}),
        "Config": ("config", "describe_configuration_recorders", {}),
        "EKS": ("eks", "list_clusters", {"maxResults": 1}),
        "ECS": ("ecs", "list_clusters", {"maxResults": 1}),
        "ELB": ("elbv2", "describe_load_balancers", {"PageSize": 1}),
    }

    results = []
    passed = 0
    failed = 0

    # Get identity first
    try:
        sts = session.client("sts", region_name=region)
        identity = sts.get_caller_identity()
        account_id = identity.get("Account", "unknown")
        arn = identity.get("Arn", "unknown")
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Cannot verify AWS identity: {str(e)}. Check credentials.",
        }))
        sys.exit(1)

    for service_name, (client_name, method_name, kwargs) in service_probes.items():
        try:
            client = session.client(client_name, region_name=region)
            getattr(client, method_name)(**kwargs)
            results.append({"service": service_name, "status": "ok", "detail": "accessible"})
            passed += 1
        except client.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("AccessDeniedException", "AccessDenied", "UnauthorizedAccess"):
                results.append({"service": service_name, "status": "denied", "detail": str(e)})
                failed += 1
            else:
                # Non-auth errors (e.g., service not enabled); still counts as accessible
                results.append({"service": service_name, "status": "ok", "detail": f"accessible ({error_code})"})
                passed += 1
        except Exception as e:
            results.append({"service": service_name, "status": "error", "detail": str(e)})
            failed += 1

    output = {
        "status": "ok",
        "provider": "aws",
        "account_id": account_id,
        "identity_arn": arn,
        "region": region,
        "total_services": len(results),
        "accessible": passed,
        "denied": failed,
        "all_passed": failed == 0,
        "results": results,
    }
    print(json.dumps(output, indent=2, default=str))
    return output


def main():
    parser = argparse.ArgumentParser(description="AWS Evidence Collection for auditclaw-grc")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to GRC compliance.sqlite database")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    parser.add_argument("--checks", help="Comma-separated list of checks to run")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--list-checks", action="store_true", help="List available checks")
    parser.add_argument("--test-connection", action="store_true", help="Test AWS connectivity")

    args = parser.parse_args()

    if args.list_checks:
        print(json.dumps({"checks": list(ALL_CHECKS.keys())}))
        return

    if args.test_connection:
        test_connection(region=args.region)
        return

    if args.all:
        check_names = list(ALL_CHECKS.keys())
    elif args.checks:
        check_names = [c.strip() for c in args.checks.split(",")]
    else:
        parser.error("Specify --all or --checks <list>")
        return

    run_sweep(args.db_path, check_names, region=args.region)


if __name__ == "__main__":
    main()
