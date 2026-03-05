"""Azure Storage compliance checks: HTTPS-only, TLS 1.2, public blob access, network deny."""

from azure.mgmt.storage import StorageManagementClient


def run_storage_checks(credential, subscription_id):
    """Run all storage account checks and return findings.

    Args:
        credential: Azure DefaultAzureCredential instance.
        subscription_id: Azure subscription ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    storage_client = StorageManagementClient(credential, subscription_id)
    findings = []

    try:
        accounts = list(storage_client.storage_accounts.list())
    except Exception as e:
        return {
            "check": "storage",
            "provider": "azure",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "storage/api",
                "status": "fail",
                "detail": f"Failed to list storage accounts: {e}",
            }],
        }

    if not accounts:
        return {
            "check": "storage",
            "provider": "azure",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for acct in accounts:
        name = acct.name

        # Check 1: HTTPS-only transfer
        https_only = getattr(acct, "enable_https_traffic_only", False)
        findings.append({
            "resource": f"storage/{name}/https-only",
            "status": "pass" if https_only else "fail",
            "detail": "HTTPS-only transfer enabled" if https_only else "HTTPS-only transfer not enforced",
        })

        # Check 2: Minimum TLS version 1.2
        min_tls = getattr(acct, "minimum_tls_version", None)
        tls_ok = min_tls in ("TLS1_2", "TLS1_3") if min_tls else False
        findings.append({
            "resource": f"storage/{name}/tls-version",
            "status": "pass" if tls_ok else "fail",
            "detail": f"Minimum TLS version: {min_tls}" if min_tls else "Minimum TLS version not set",
        })

        # Check 3: Public blob access disabled
        allow_public = getattr(acct, "allow_blob_public_access", None)
        public_disabled = allow_public is False
        findings.append({
            "resource": f"storage/{name}/public-blob-access",
            "status": "pass" if public_disabled else "fail",
            "detail": "Public blob access disabled" if public_disabled else "Public blob access allowed or not explicitly disabled",
        })

        # Check 4: Network default action is Deny
        network_rules = getattr(acct, "network_rule_set", None)
        default_action = getattr(network_rules, "default_action", None) if network_rules else None
        deny_default = str(default_action).lower() == "deny" if default_action else False
        findings.append({
            "resource": f"storage/{name}/network-default-deny",
            "status": "pass" if deny_default else "fail",
            "detail": f"Network default action: {default_action}" if default_action else "Network rules not configured (default Allow)",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "storage",
        "provider": "azure",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
