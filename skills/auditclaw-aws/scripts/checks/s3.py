"""S3 compliance checks: encryption, public access, versioning, logging."""


def run_s3_checks(session, region="us-east-1"):
    """Run all S3 checks and return findings."""
    findings = []
    findings.extend(_check_encryption(session))
    findings.extend(_check_public_access_block(session))
    findings.extend(_check_versioning(session))
    findings.extend(_check_logging(session))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "s3",
        "provider": "aws",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_encryption(session):
    """Check all S3 buckets have default encryption."""
    s3 = session.client("s3")
    buckets = s3.list_buckets()["Buckets"]
    findings = []
    for bucket in buckets:
        try:
            enc = s3.get_bucket_encryption(Bucket=bucket["Name"])
            algo = enc["ServerSideEncryptionConfiguration"]["Rules"][0][
                "ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"]
            findings.append({
                "resource": f"s3/{bucket['Name']}",
                "status": "pass",
                "detail": f"Encrypted with {algo}",
            })
        except Exception:
            findings.append({
                "resource": f"s3/{bucket['Name']}",
                "status": "fail",
                "detail": "No default encryption configured",
            })
    return findings


def _check_public_access_block(session):
    """Check all S3 buckets have public access blocked."""
    s3 = session.client("s3")
    buckets = s3.list_buckets()["Buckets"]
    findings = []
    for bucket in buckets:
        try:
            pab = s3.get_public_access_block(Bucket=bucket["Name"])["PublicAccessBlockConfiguration"]
            all_blocked = all([
                pab.get("BlockPublicAcls", False),
                pab.get("IgnorePublicAcls", False),
                pab.get("BlockPublicPolicy", False),
                pab.get("RestrictPublicBuckets", False),
            ])
            findings.append({
                "resource": f"s3/{bucket['Name']}/public-access",
                "status": "pass" if all_blocked else "fail",
                "detail": "All public access blocked" if all_blocked else "Some public access not blocked",
            })
        except Exception:
            findings.append({
                "resource": f"s3/{bucket['Name']}/public-access",
                "status": "fail",
                "detail": "Public access block not configured",
            })
    return findings


def _check_versioning(session):
    """Check all S3 buckets have versioning enabled."""
    s3 = session.client("s3")
    buckets = s3.list_buckets()["Buckets"]
    findings = []
    for bucket in buckets:
        try:
            ver = s3.get_bucket_versioning(Bucket=bucket["Name"])
            enabled = ver.get("Status") == "Enabled"
            findings.append({
                "resource": f"s3/{bucket['Name']}/versioning",
                "status": "pass" if enabled else "fail",
                "detail": f"Versioning {'enabled' if enabled else 'not enabled'}",
            })
        except Exception:
            findings.append({
                "resource": f"s3/{bucket['Name']}/versioning",
                "status": "fail",
                "detail": "Could not check versioning",
            })
    return findings


def _check_logging(session):
    """Check all S3 buckets have access logging enabled."""
    s3 = session.client("s3")
    buckets = s3.list_buckets()["Buckets"]
    findings = []
    for bucket in buckets:
        try:
            log = s3.get_bucket_logging(Bucket=bucket["Name"])
            enabled = "LoggingEnabled" in log
            findings.append({
                "resource": f"s3/{bucket['Name']}/logging",
                "status": "pass" if enabled else "fail",
                "detail": f"Access logging {'enabled' if enabled else 'not enabled'}",
            })
        except Exception:
            findings.append({
                "resource": f"s3/{bucket['Name']}/logging",
                "status": "fail",
                "detail": "Could not check logging",
            })
    return findings
