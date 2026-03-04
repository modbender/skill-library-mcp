"""Okta inactive/stale user detection check.

Verifies that no active Okta users have a lastLogin older than 90 days.
Uses async Okta SDK v3 with a sync wrapper.
"""

import asyncio
from datetime import datetime, timezone, timedelta

try:
    from okta.client import Client as OktaClient
except ImportError:
    OktaClient = None


INACTIVE_THRESHOLD_DAYS = 90


def run_okta_inactive_checks(okta_config):
    """Sync wrapper around async Okta inactive user checks.

    Args:
        okta_config: dict with orgUrl and token keys.

    Returns:
        dict with check, provider, status, total, passed, failed, findings.
    """
    return asyncio.run(_run_okta_inactive_checks_async(okta_config))


def _parse_okta_datetime(dt_str):
    """Parse Okta's ISO 8601 datetime string to timezone-aware datetime."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(str(dt_str).replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


async def _run_okta_inactive_checks_async(okta_config):
    """Check for active Okta users with no login in > 90 days."""
    findings = []
    try:
        client = OktaClient(okta_config)
        users, _, err = await client.list_users({"filter": 'status eq "ACTIVE"'})
        if err:
            raise Exception(str(err))
    except Exception as e:
        return {
            "check": "okta_inactive",
            "provider": "okta",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "okta/inactive/api",
                "status": "fail",
                "detail": f"Failed to list users: {str(e)}",
            }],
        }

    if not users:
        return {
            "check": "okta_inactive",
            "provider": "okta",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=INACTIVE_THRESHOLD_DAYS)

    for user in users:
        email = user.profile.login if user.profile else user.id
        last_login_str = getattr(user, "last_login", None)
        last_login = _parse_okta_datetime(last_login_str)

        if last_login is None:
            findings.append({
                "resource": f"okta/user/{email}/inactive",
                "status": "fail",
                "detail": "No login recorded (never logged in)",
            })
        elif last_login < threshold:
            days_ago = (now - last_login).days
            findings.append({
                "resource": f"okta/user/{email}/inactive",
                "status": "fail",
                "detail": f"Last login {days_ago} days ago (threshold: {INACTIVE_THRESHOLD_DAYS})",
            })
        else:
            days_ago = (now - last_login).days
            findings.append({
                "resource": f"okta/user/{email}/inactive",
                "status": "pass",
                "detail": f"Last login {days_ago} days ago",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "okta_inactive",
        "provider": "okta",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
