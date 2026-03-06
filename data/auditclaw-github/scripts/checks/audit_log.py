"""Audit log checks: admin audit log accessibility."""


def run_audit_log_checks(org, github_client):
    """Check audit log availability and recent admin actions."""
    findings = []

    try:
        # Try to access audit log
        audit_entries = list(org.get_audit_log(include="all")[:10])
        findings.append({
            "resource": f"{org.login}/audit-log",
            "status": "pass",
            "detail": f"Audit log accessible, {len(audit_entries)} recent entries found",
        })
    except Exception:
        findings.append({
            "resource": f"{org.login}/audit-log",
            "status": "fail",
            "detail": "Audit log not accessible (requires GitHub Enterprise or admin access)",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "audit_log",
        "provider": "github",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
