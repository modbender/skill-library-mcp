"""Azure Compute compliance checks: VM disk encryption at host."""

from azure.mgmt.compute import ComputeManagementClient


def run_compute_checks(credential, subscription_id):
    """Run VM checks for disk encryption (encryption at host).

    Args:
        credential: Azure DefaultAzureCredential instance.
        subscription_id: Azure subscription ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    compute_client = ComputeManagementClient(credential, subscription_id)
    findings = []

    try:
        vms = list(compute_client.virtual_machines.list_all())
    except Exception as e:
        return {
            "check": "compute",
            "provider": "azure",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "compute/api",
                "status": "fail",
                "detail": f"Failed to list VMs: {e}",
            }],
        }

    if not vms:
        return {
            "check": "compute",
            "provider": "azure",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for vm in vms:
        vm_name = vm.name
        sec_profile = getattr(vm, "security_profile", None)
        encryption_at_host = getattr(sec_profile, "encryption_at_host", False) if sec_profile else False

        findings.append({
            "resource": f"compute/{vm_name}/disk-encryption",
            "status": "pass" if encryption_at_host else "fail",
            "detail": "Encryption at host enabled" if encryption_at_host else "Encryption at host not enabled",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "compute",
        "provider": "azure",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
