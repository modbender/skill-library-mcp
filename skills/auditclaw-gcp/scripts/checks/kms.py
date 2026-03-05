"""GCP KMS checks: key rotation period <= 90 days."""

from google.cloud.kms_v1 import KeyManagementServiceClient


def run_kms_checks(project_id):
    """Run KMS key rotation checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []
    max_rotation_days = 90
    max_rotation_seconds = max_rotation_days * 86400

    try:
        kms_client = KeyManagementServiceClient()
        # List all key rings in the project (all locations)
        parent = f"projects/{project_id}/locations/-"
        key_rings = list(kms_client.list_key_rings(parent=parent))
    except Exception as e:
        return {
            "check": "kms",
            "provider": "gcp",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "kms/api",
                "status": "fail",
                "detail": f"Could not list KMS key rings: {e}",
            }],
        }

    for key_ring in key_rings:
        try:
            crypto_keys = list(kms_client.list_crypto_keys(parent=key_ring.name))
        except Exception as e:
            ring_name = key_ring.name.split("/")[-1] if "/" in key_ring.name else key_ring.name
            findings.append({
                "resource": f"kms/{ring_name}/keys",
                "status": "fail",
                "detail": f"Could not list keys in ring {ring_name}: {e}",
            })
            continue

        for key in crypto_keys:
            # Only check ENCRYPT_DECRYPT keys (symmetric)
            purpose = getattr(key, "purpose", None)
            if purpose is not None and purpose != 1:
                # purpose 1 = ENCRYPT_DECRYPT
                continue

            rotation = key.rotation_period
            if rotation is None or rotation.total_seconds() == 0:
                findings.append({
                    "resource": f"kms/{key.name.split('/')[-1]}",
                    "status": "fail",
                    "detail": "No rotation period configured",
                })
            elif rotation.total_seconds() > max_rotation_seconds:
                days = int(rotation.total_seconds() / 86400)
                findings.append({
                    "resource": f"kms/{key.name.split('/')[-1]}",
                    "status": "fail",
                    "detail": f"Rotation period is {days} days (max {max_rotation_days})",
                })
            else:
                days = int(rotation.total_seconds() / 86400)
                findings.append({
                    "resource": f"kms/{key.name.split('/')[-1]}",
                    "status": "pass",
                    "detail": f"Rotation period is {days} days (within {max_rotation_days}-day limit)",
                })

    if not findings:
        return {
            "check": "kms",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "kms",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
