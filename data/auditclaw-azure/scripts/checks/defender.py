"""Azure Defender for Cloud compliance checks: Standard tier plans."""

from azure.mgmt.security import SecurityCenter

CRITICAL_PLANS = {
    "VirtualMachines", "SqlServers", "AppServices",
    "StorageAccounts", "KeyVaults", "Containers", "Arm",
}


def run_defender_checks(credential, subscription_id):
    """Run Defender for Cloud checks for Standard tier on critical resource types.

    Args:
        credential: Azure DefaultAzureCredential instance.
        subscription_id: Azure subscription ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    sec_client = SecurityCenter(credential, subscription_id)
    findings = []

    try:
        pricings_result = sec_client.pricings.list()
        pricings = pricings_result.value if hasattr(pricings_result, "value") else list(pricings_result)
    except Exception as e:
        return {
            "check": "defender",
            "provider": "azure",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "defender/api",
                "status": "fail",
                "detail": f"Failed to list Defender pricing tiers: {e}",
            }],
        }

    found_plans = set()
    for pricing in pricings:
        plan_name = getattr(pricing, "name", None)
        if plan_name not in CRITICAL_PLANS:
            continue

        found_plans.add(plan_name)
        tier = getattr(pricing, "pricing_tier", None)
        is_standard = str(tier).lower() == "standard" if tier else False

        findings.append({
            "resource": f"defender/{plan_name}/tier",
            "status": "pass" if is_standard else "fail",
            "detail": f"Defender plan {plan_name}: {tier}" if tier else f"Defender plan {plan_name}: tier unknown",
        })

    # Report missing plans as failures
    for plan_name in sorted(CRITICAL_PLANS - found_plans):
        findings.append({
            "resource": f"defender/{plan_name}/tier",
            "status": "fail",
            "detail": f"Defender plan {plan_name} not found",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "defender",
        "provider": "azure",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
