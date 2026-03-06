"""Azure Key Vault compliance checks: soft delete + purge protection."""

from azure.mgmt.keyvault import KeyVaultManagementClient


def run_keyvault_checks(credential, subscription_id):
    """Run Key Vault checks for soft delete and purge protection.

    Args:
        credential: Azure DefaultAzureCredential instance.
        subscription_id: Azure subscription ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    kv_client = KeyVaultManagementClient(credential, subscription_id)
    findings = []

    try:
        vaults = list(kv_client.vaults.list_by_subscription())
    except Exception as e:
        return {
            "check": "keyvault",
            "provider": "azure",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "keyvault/api",
                "status": "fail",
                "detail": f"Failed to list Key Vaults: {e}",
            }],
        }

    if not vaults:
        return {
            "check": "keyvault",
            "provider": "azure",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for vault in vaults:
        vault_name = vault.name
        props = vault.properties if vault.properties else None

        soft_delete = getattr(props, "enable_soft_delete", False) if props else False
        purge_protection = getattr(props, "enable_purge_protection", False) if props else False

        both_enabled = bool(soft_delete) and bool(purge_protection)
        detail_parts = []
        if soft_delete:
            detail_parts.append("soft delete enabled")
        else:
            detail_parts.append("soft delete disabled")
        if purge_protection:
            detail_parts.append("purge protection enabled")
        else:
            detail_parts.append("purge protection disabled")

        findings.append({
            "resource": f"keyvault/{vault_name}/soft-delete-purge",
            "status": "pass" if both_enabled else "fail",
            "detail": "; ".join(detail_parts),
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "keyvault",
        "provider": "azure",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
