"""CloudTrail compliance checks: enabled, multi-region, log validation."""


def run_cloudtrail_checks(session, region="us-east-1"):
    """Run all CloudTrail checks and return findings."""
    ct = session.client("cloudtrail", region_name=region)
    trails = ct.describe_trails()["trailList"]

    findings = []
    if not trails:
        findings.append({
            "resource": "cloudtrail",
            "status": "fail",
            "detail": "No CloudTrail trails configured",
        })
    else:
        for trail in trails:
            name = trail["Name"]
            findings.extend(_check_trail(ct, trail, name))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "cloudtrail",
        "provider": "aws",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_trail(ct, trail, name):
    """Check individual trail configuration."""
    findings = []

    # Multi-region
    is_multi = trail.get("IsMultiRegionTrail", False)
    findings.append({
        "resource": f"cloudtrail/{name}/multi-region",
        "status": "pass" if is_multi else "fail",
        "detail": f"Multi-region: {'yes' if is_multi else 'no'}",
    })

    # Log file validation
    has_validation = trail.get("LogFileValidationEnabled", False)
    findings.append({
        "resource": f"cloudtrail/{name}/log-validation",
        "status": "pass" if has_validation else "fail",
        "detail": f"Log file validation: {'enabled' if has_validation else 'disabled'}",
    })

    # Logging status
    try:
        status = ct.get_trail_status(Name=trail["TrailARN"])
        is_logging = status.get("IsLogging", False)
        findings.append({
            "resource": f"cloudtrail/{name}/logging",
            "status": "pass" if is_logging else "fail",
            "detail": f"Currently logging: {'yes' if is_logging else 'no'}",
        })
    except Exception:
        findings.append({
            "resource": f"cloudtrail/{name}/logging",
            "status": "fail",
            "detail": "Could not check logging status",
        })

    # S3 bucket configured
    has_bucket = bool(trail.get("S3BucketName"))
    findings.append({
        "resource": f"cloudtrail/{name}/s3-delivery",
        "status": "pass" if has_bucket else "fail",
        "detail": f"S3 delivery: {trail.get('S3BucketName', 'not configured')}",
    })

    return findings
