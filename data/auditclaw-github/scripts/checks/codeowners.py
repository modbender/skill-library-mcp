"""CODEOWNERS file checks: presence in repositories."""


def run_codeowners_checks(org, github_client):
    """Check for CODEOWNERS files in organization repos."""
    findings = []

    for repo in org.get_repos():
        if repo.archived:
            continue
        repo_name = repo.full_name

        has_codeowners = False
        for path in ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]:
            try:
                repo.get_contents(path)
                has_codeowners = True
                break
            except Exception:
                continue

        findings.append({
            "resource": f"{repo_name}/codeowners",
            "status": "pass" if has_codeowners else "fail",
            "detail": "CODEOWNERS file found" if has_codeowners else "No CODEOWNERS file",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "codeowners",
        "provider": "github",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
