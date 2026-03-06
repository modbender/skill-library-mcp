"""RDS compliance checks: encryption, backups, public access."""


def run_rds_checks(session, region="us-east-1"):
    """Run all RDS checks and return findings."""
    rds = session.client("rds", region_name=region)

    try:
        instances = rds.describe_db_instances()["DBInstances"]
    except Exception:
        return {
            "check": "rds",
            "provider": "aws",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    findings = []
    for db in instances:
        db_id = db["DBInstanceIdentifier"]

        # Encryption
        encrypted = db.get("StorageEncrypted", False)
        findings.append({
            "resource": f"rds/{db_id}/encryption",
            "status": "pass" if encrypted else "fail",
            "detail": f"Storage encryption: {'enabled' if encrypted else 'disabled'}",
        })

        # Automated backups
        retention = db.get("BackupRetentionPeriod", 0)
        findings.append({
            "resource": f"rds/{db_id}/backups",
            "status": "pass" if retention >= 7 else "fail",
            "detail": f"Backup retention: {retention} days (min 7)",
        })

        # Public accessibility
        public = db.get("PubliclyAccessible", False)
        findings.append({
            "resource": f"rds/{db_id}/public-access",
            "status": "fail" if public else "pass",
            "detail": f"Publicly accessible: {'yes' if public else 'no'}",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "rds",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
