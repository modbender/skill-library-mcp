"""Google Workspace super admin audit check.

Verifies that:
1. Super admin count is between 2 and 4 (inclusive).
2. All super admins have 2SV enrolled and enforced.
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


def run_google_admin_checks(service):
    """Audit super admin count and MFA status.

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
            "check": "google_admins",
            "provider": "google_workspace",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "google_workspace/admins/api",
                "status": "fail",
                "detail": f"Failed to list users: {str(e)}",
            }],
        }

    admins = [u for u in users if u.get("isAdmin", False)]
    admin_count = len(admins)

    # Finding 1: Admin count check (should be 2-4)
    if 2 <= admin_count <= 4:
        findings.append({
            "resource": "google_workspace/admins/count",
            "status": "pass",
            "detail": f"Super admin count is {admin_count} (recommended: 2-4)",
        })
    elif admin_count < 2:
        findings.append({
            "resource": "google_workspace/admins/count",
            "status": "fail",
            "detail": f"Only {admin_count} super admin(s): minimum 2 recommended for redundancy",
        })
    else:
        findings.append({
            "resource": "google_workspace/admins/count",
            "status": "fail",
            "detail": f"{admin_count} super admins: maximum 4 recommended to limit blast radius",
        })

    # Finding 2+: Each admin must have 2SV
    for admin in admins:
        email = admin.get("primaryEmail", "unknown")
        enrolled = admin.get("isEnrolledIn2Sv", False)
        enforced = admin.get("isEnforcedIn2Sv", False)

        if enrolled and enforced:
            findings.append({
                "resource": f"google_workspace/admin/{email}/mfa",
                "status": "pass",
                "detail": "Super admin has 2SV enrolled and enforced",
            })
        else:
            findings.append({
                "resource": f"google_workspace/admin/{email}/mfa",
                "status": "fail",
                "detail": f"Super admin missing 2SV (enrolled={enrolled}, enforced={enforced})",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "google_admins",
        "provider": "google_workspace",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
