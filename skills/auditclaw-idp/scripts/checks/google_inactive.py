"""Google Workspace inactive user detection check.

Verifies that no active (non-suspended) users have a lastLoginTime older
than 90 days.
"""

from datetime import datetime, timezone, timedelta


INACTIVE_THRESHOLD_DAYS = 90


def _list_active_users(service):
    """Fetch all active (non-suspended) users from Google Workspace."""
    users = []
    page_token = None
    while True:
        results = service.users().list(
            customer="my_customer", maxResults=500, pageToken=page_token
        ).execute()
        for user in results.get("users", []):
            if not user.get("suspended", False):
                users.append(user)
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    return users


def _parse_google_datetime(dt_str):
    """Parse Google's ISO 8601 datetime string to timezone-aware datetime."""
    if not dt_str:
        return None
    # Google format: 2024-01-15T10:30:00.000Z
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def run_google_inactive_checks(service):
    """Check for active users with no login in > 90 days.

    Args:
        service: Google Admin SDK Directory service (already authenticated).

    Returns:
        dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []
    try:
        users = _list_active_users(service)
    except Exception as e:
        return {
            "check": "google_inactive",
            "provider": "google_workspace",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "google_workspace/inactive/api",
                "status": "fail",
                "detail": f"Failed to list users: {str(e)}",
            }],
        }

    if not users:
        return {
            "check": "google_inactive",
            "provider": "google_workspace",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=INACTIVE_THRESHOLD_DAYS)

    for user in users:
        email = user.get("primaryEmail", "unknown")
        last_login_str = user.get("lastLoginTime")
        last_login = _parse_google_datetime(last_login_str)

        if last_login is None:
            findings.append({
                "resource": f"google_workspace/user/{email}/inactive",
                "status": "fail",
                "detail": "No login recorded (never logged in)",
            })
        elif last_login < threshold:
            days_ago = (now - last_login).days
            findings.append({
                "resource": f"google_workspace/user/{email}/inactive",
                "status": "fail",
                "detail": f"Last login {days_ago} days ago (threshold: {INACTIVE_THRESHOLD_DAYS})",
            })
        else:
            days_ago = (now - last_login).days
            findings.append({
                "resource": f"google_workspace/user/{email}/inactive",
                "status": "pass",
                "detail": f"Last login {days_ago} days ago",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "google_inactive",
        "provider": "google_workspace",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
