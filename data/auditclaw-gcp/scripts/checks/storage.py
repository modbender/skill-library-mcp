"""GCP Cloud Storage checks: uniform bucket access, public access prevention."""

from google.cloud import storage


def run_storage_checks(project_id):
    """Run all Cloud Storage checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []
    try:
        client = storage.Client(project=project_id)
        buckets = list(client.list_buckets())
    except Exception as e:
        return {
            "check": "storage",
            "provider": "gcp",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "storage/api",
                "status": "fail",
                "detail": f"Could not list buckets: {e}",
            }],
        }

    if not buckets:
        return {
            "check": "storage",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for bucket in buckets:
        findings.extend(_check_uniform_access(bucket))
        findings.extend(_check_public_prevention(bucket))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "storage",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_uniform_access(bucket):
    """Check that uniform bucket-level access is enabled."""
    try:
        uniform = bucket.iam_configuration.uniform_bucket_level_access_enabled
        return [{
            "resource": f"storage/{bucket.name}/uniform-access",
            "status": "pass" if uniform else "fail",
            "detail": "Uniform bucket-level access enabled" if uniform
                      else "Uniform bucket-level access not enabled (legacy ACLs in use)",
        }]
    except Exception as e:
        return [{
            "resource": f"storage/{bucket.name}/uniform-access",
            "status": "fail",
            "detail": f"Could not check uniform access: {e}",
        }]


def _check_public_prevention(bucket):
    """Check that public access prevention is enforced."""
    try:
        prevention = bucket.iam_configuration.public_access_prevention
        enforced = prevention == "enforced"
        return [{
            "resource": f"storage/{bucket.name}/public-prevention",
            "status": "pass" if enforced else "fail",
            "detail": f"Public access prevention: {prevention}" if prevention
                      else "Public access prevention not configured",
        }]
    except Exception as e:
        return [{
            "resource": f"storage/{bucket.name}/public-prevention",
            "status": "fail",
            "detail": f"Could not check public access prevention: {e}",
        }]
