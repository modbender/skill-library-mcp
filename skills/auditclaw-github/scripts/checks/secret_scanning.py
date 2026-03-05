"""Secret scanning checks: enabled status, active alerts."""


def run_secret_scanning_checks(org, github_client):
    """Check secret scanning across organization repos."""
    findings = []

    for repo in org.get_repos():
        if repo.archived:
            continue
        repo_name = repo.full_name

        try:
            # Check if secret scanning is available/enabled
            alerts = list(repo.get_secret_scanning_alerts(state="open"))
            open_count = len(alerts)

            findings.append({
                "resource": f"{repo_name}/secret-scanning",
                "status": "fail" if open_count > 0 else "pass",
                "detail": f"{open_count} open secret scanning alerts" if open_count > 0
                          else "No open secret scanning alerts",
            })
        except Exception:
            # Secret scanning may not be available (free tier)
            findings.append({
                "resource": f"{repo_name}/secret-scanning",
                "status": "fail",
                "detail": "Secret scanning not available or not enabled",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "secret_scanning",
        "provider": "github",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
