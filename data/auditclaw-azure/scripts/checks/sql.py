"""Azure SQL compliance checks: server auditing and TDE encryption."""

from azure.mgmt.sql import SqlManagementClient


def run_sql_checks(credential, subscription_id):
    """Run SQL Server checks for auditing and TDE encryption.

    Args:
        credential: Azure DefaultAzureCredential instance.
        subscription_id: Azure subscription ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    sql_client = SqlManagementClient(credential, subscription_id)
    findings = []

    try:
        servers = list(sql_client.servers.list())
    except Exception as e:
        return {
            "check": "sql",
            "provider": "azure",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "sql/api",
                "status": "fail",
                "detail": f"Failed to list SQL servers: {e}",
            }],
        }

    if not servers:
        return {
            "check": "sql",
            "provider": "azure",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for server in servers:
        server_name = server.name
        # Extract resource group from server ID
        # Format: /subscriptions/.../resourceGroups/<rg>/providers/...
        rg = server.id.split("/")[4]

        # Check 1: Server auditing enabled
        try:
            policy = sql_client.server_blob_auditing_policies.get(rg, server_name)
            auditing_on = getattr(policy, "state", None) == "Enabled"
        except Exception:
            auditing_on = False

        findings.append({
            "resource": f"sql/{server_name}/auditing",
            "status": "pass" if auditing_on else "fail",
            "detail": "Server auditing enabled" if auditing_on else "Server auditing not enabled",
        })

        # Check 2: TDE encryption on all databases (skip master)
        try:
            databases = list(sql_client.databases.list_by_server(rg, server_name))
        except Exception:
            databases = []

        for db in databases:
            if db.name == "master":
                continue

            try:
                tde = sql_client.transparent_data_encryptions.get(
                    rg, server_name, db.name
                )
                tde_on = getattr(tde, "state", None) == "Enabled"
            except Exception:
                tde_on = False

            findings.append({
                "resource": f"sql/{server_name}/{db.name}/tde",
                "status": "pass" if tde_on else "fail",
                "detail": f"TDE {'enabled' if tde_on else 'not enabled'} on {db.name}",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "sql",
        "provider": "azure",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
