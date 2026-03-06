"""Okta MFA enrollment check.

Verifies that all active Okta users have at least one MFA factor enrolled.
Uses async Okta SDK v3 with a sync wrapper.
"""

import asyncio

try:
    from okta.client import Client as OktaClient
except ImportError:
    OktaClient = None


def run_okta_mfa_checks(okta_config):
    """Sync wrapper around async Okta MFA checks.

    Args:
        okta_config: dict with orgUrl and token keys.

    Returns:
        dict with check, provider, status, total, passed, failed, findings.
    """
    return asyncio.run(_run_okta_mfa_checks_async(okta_config))


async def _run_okta_mfa_checks_async(okta_config):
    """Check that all active Okta users have at least 1 MFA factor enrolled."""
    findings = []
    try:
        client = OktaClient(okta_config)
        users, _, err = await client.list_users({"filter": 'status eq "ACTIVE"'})
        if err:
            raise Exception(str(err))
    except Exception as e:
        return {
            "check": "okta_mfa",
            "provider": "okta",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "okta/mfa/api",
                "status": "fail",
                "detail": f"Failed to list users: {str(e)}",
            }],
        }

    if not users:
        return {
            "check": "okta_mfa",
            "provider": "okta",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for user in users:
        user_id = user.id
        email = user.profile.login if user.profile else user_id
        try:
            factors, _, factor_err = await client.list_factors(user_id)
            if factor_err:
                factors = []
        except Exception:
            factors = []

        active_factors = [f for f in (factors or []) if getattr(f, "status", "") == "ACTIVE"]

        if active_factors:
            findings.append({
                "resource": f"okta/user/{email}/mfa",
                "status": "pass",
                "detail": f"{len(active_factors)} active MFA factor(s) enrolled",
            })
        else:
            findings.append({
                "resource": f"okta/user/{email}/mfa",
                "status": "fail",
                "detail": "No active MFA factors enrolled",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "okta_mfa",
        "provider": "okta",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
