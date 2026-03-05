"""Two-factor authentication checks: org-level 2FA enforcement."""


def run_two_factor_checks(org, github_client):
    """Check 2FA enforcement at organization level."""
    findings = []

    try:
        # Check org 2FA requirement
        two_factor_required = org.two_factor_requirement_enabled
        findings.append({
            "resource": f"{org.login}/2fa-requirement",
            "status": "pass" if two_factor_required else "fail",
            "detail": "Organization 2FA requirement: enabled" if two_factor_required
                      else "Organization 2FA requirement: NOT enabled",
        })
    except Exception:
        findings.append({
            "resource": f"{org.login}/2fa-requirement",
            "status": "fail",
            "detail": "Could not check 2FA requirement (may need admin access)",
        })

    # Check members without 2FA
    try:
        members_no_2fa = list(org.get_members(filter_="2fa_disabled"))
        findings.append({
            "resource": f"{org.login}/members-without-2fa",
            "status": "fail" if members_no_2fa else "pass",
            "detail": f"{len(members_no_2fa)} members without 2FA" if members_no_2fa
                      else "All members have 2FA enabled",
        })
    except Exception:
        findings.append({
            "resource": f"{org.login}/members-without-2fa",
            "status": "fail",
            "detail": "Could not check member 2FA status",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "two_factor",
        "provider": "github",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
