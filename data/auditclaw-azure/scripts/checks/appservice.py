"""Azure App Service compliance checks: HTTPS-only and TLS 1.2+."""

from azure.mgmt.web import WebSiteManagementClient


def run_appservice_checks(credential, subscription_id):
    """Run App Service checks for HTTPS enforcement and minimum TLS version.

    Args:
        credential: Azure DefaultAzureCredential instance.
        subscription_id: Azure subscription ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    web_client = WebSiteManagementClient(credential, subscription_id)
    findings = []

    try:
        apps = list(web_client.web_apps.list())
    except Exception as e:
        return {
            "check": "appservice",
            "provider": "azure",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "appservice/api",
                "status": "fail",
                "detail": f"Failed to list App Services: {e}",
            }],
        }

    if not apps:
        return {
            "check": "appservice",
            "provider": "azure",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for app in apps:
        app_name = app.name
        rg = app.resource_group

        # Get app configuration for TLS settings
        try:
            config = web_client.web_apps.get_configuration(rg, app_name)
        except Exception:
            config = None

        # Check HTTPS-only and TLS 1.2 as a single finding
        https_only = getattr(app, "https_only", False)
        min_tls = getattr(config, "min_tls_version", None) if config else None
        tls_ok = min_tls in ("1.2", "1.3") if min_tls else False

        both_ok = bool(https_only) and tls_ok

        detail_parts = []
        detail_parts.append(f"HTTPS-only: {'yes' if https_only else 'no'}")
        detail_parts.append(f"Min TLS: {min_tls if min_tls else 'not set'}")

        findings.append({
            "resource": f"appservice/{app_name}/https-tls",
            "status": "pass" if both_ok else "fail",
            "detail": "; ".join(detail_parts),
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "appservice",
        "provider": "azure",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
