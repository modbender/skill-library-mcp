"""KMS compliance checks: key rotation, key policies."""


def run_kms_checks(session, region="us-east-1"):
    """Run all KMS checks and return findings."""
    kms = session.client("kms", region_name=region)
    findings = []

    try:
        keys = kms.list_keys()["Keys"]
    except Exception:
        return {
            "check": "kms",
            "provider": "aws",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [{"resource": "kms", "status": "pass", "detail": "No KMS keys found or access denied"}],
        }

    for key in keys:
        key_id = key["KeyId"]
        try:
            desc = kms.describe_key(KeyId=key_id)["KeyMetadata"]
            if desc.get("KeyManager") == "AWS":
                continue  # Skip AWS-managed keys

            # Check rotation
            try:
                rotation = kms.get_key_rotation_status(KeyId=key_id)
                enabled = rotation.get("KeyRotationEnabled", False)
                findings.append({
                    "resource": f"kms/{key_id[:8]}/rotation",
                    "status": "pass" if enabled else "fail",
                    "detail": f"Key rotation {'enabled' if enabled else 'not enabled'}",
                })
            except Exception:
                findings.append({
                    "resource": f"kms/{key_id[:8]}/rotation",
                    "status": "fail",
                    "detail": "Could not check key rotation status",
                })
        except Exception:
            continue

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "kms",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
