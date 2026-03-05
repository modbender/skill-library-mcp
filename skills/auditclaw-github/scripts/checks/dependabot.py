"""Dependabot checks: vulnerability alerts by severity."""


def run_dependabot_checks(org, github_client):
    """Check Dependabot alerts across organization repos."""
    findings = []

    for repo in org.get_repos():
        if repo.archived:
            continue
        repo_name = repo.full_name

        try:
            alerts = list(repo.get_dependabot_alerts(state="open"))
            by_severity = {}
            for alert in alerts:
                sev = alert.security_vulnerability.severity if hasattr(alert, 'security_vulnerability') else "unknown"
                by_severity[sev] = by_severity.get(sev, 0) + 1

            critical = by_severity.get("critical", 0)
            high = by_severity.get("high", 0)
            total = len(alerts)

            findings.append({
                "resource": f"{repo_name}/dependabot",
                "status": "fail" if critical > 0 or high > 3 else "pass",
                "detail": f"{total} open alerts ({critical} critical, {high} high)" if total > 0
                          else "No open Dependabot alerts",
            })
        except Exception:
            findings.append({
                "resource": f"{repo_name}/dependabot",
                "status": "fail",
                "detail": "Dependabot not available or not enabled",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "dependabot",
        "provider": "github",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
