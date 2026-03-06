"""GCP Compute checks: no default service account with cloud-platform scope."""

from google.cloud.compute_v1 import InstancesClient


def run_compute_checks(project_id):
    """Run Compute Engine instance checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []

    try:
        inst_client = InstancesClient()
        agg_list = inst_client.aggregated_list(project=project_id)
    except Exception as e:
        return {
            "check": "compute",
            "provider": "gcp",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "compute/api",
                "status": "fail",
                "detail": f"Could not list instances: {e}",
            }],
        }

    for zone, response in agg_list:
        instances = response.instances if response.instances else []
        for instance in instances:
            instance_name = instance.name
            service_accounts = instance.service_accounts or []

            if not service_accounts:
                findings.append({
                    "resource": f"compute/{instance_name}/service-account",
                    "status": "pass",
                    "detail": "No service account attached",
                })
                continue

            for sa in service_accounts:
                email = sa.email or ""
                scopes = list(sa.scopes) if sa.scopes else []

                is_default = email.endswith("-compute@developer.gserviceaccount.com")
                has_cloud_platform = "https://www.googleapis.com/auth/cloud-platform" in scopes

                if is_default and has_cloud_platform:
                    findings.append({
                        "resource": f"compute/{instance_name}/service-account",
                        "status": "fail",
                        "detail": f"Default service account with cloud-platform scope ({email})",
                    })
                elif is_default:
                    findings.append({
                        "resource": f"compute/{instance_name}/service-account",
                        "status": "pass",
                        "detail": f"Default service account with limited scopes ({email})",
                    })
                else:
                    findings.append({
                        "resource": f"compute/{instance_name}/service-account",
                        "status": "pass",
                        "detail": f"Custom service account ({email})",
                    })

    if not findings:
        return {
            "check": "compute",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "compute",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
