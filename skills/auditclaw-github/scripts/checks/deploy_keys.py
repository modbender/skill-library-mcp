"""Deploy key audit: check for read-write vs read-only keys."""


def run_deploy_keys_checks(org, github_client):
    """Audit deploy keys across organization repos."""
    findings = []

    for repo in org.get_repos():
        if repo.archived:
            continue
        repo_name = repo.full_name

        try:
            keys = list(repo.get_keys())
            if not keys:
                continue

            for key in keys:
                read_only = key.read_only if hasattr(key, 'read_only') else True
                findings.append({
                    "resource": f"{repo_name}/deploy-key/{key.id}",
                    "status": "pass" if read_only else "fail",
                    "detail": f"Deploy key '{key.title}': {'read-only' if read_only else 'READ-WRITE (risky)'}",
                })
        except Exception:
            continue

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "deploy_keys",
        "provider": "github",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
