"""Google Workspace MFA enforcement check.

Verifies that all active (non-suspended) users have 2-Step Verification
enrolled AND enforced.
"""


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


def run_google_mfa_checks(service):
    """Check that all active users have 2SV enrolled and enforced.

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
            "check": "google_mfa",
            "provider": "google_workspace",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "google_workspace/mfa/api",
                "status": "fail",
                "detail": f"Failed to list users: {str(e)}",
            }],
        }

    if not users:
        return {
            "check": "google_mfa",
            "provider": "google_workspace",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for user in users:
        email = user.get("primaryEmail", "unknown")
        enrolled = user.get("isEnrolledIn2Sv", False)
        enforced = user.get("isEnforcedIn2Sv", False)

        if enrolled and enforced:
            findings.append({
                "resource": f"google_workspace/user/{email}/mfa",
                "status": "pass",
                "detail": "2SV enrolled and enforced",
            })
        elif enrolled and not enforced:
            findings.append({
                "resource": f"google_workspace/user/{email}/mfa",
                "status": "fail",
                "detail": "2SV enrolled but not enforced",
            })
        else:
            findings.append({
                "resource": f"google_workspace/user/{email}/mfa",
                "status": "fail",
                "detail": "2SV not enrolled",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "google_mfa",
        "provider": "google_workspace",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
