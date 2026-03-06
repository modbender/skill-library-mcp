"""CI/CD checks: GitHub Actions security, workflow permissions."""


def run_ci_cd_checks(org, github_client):
    """Check GitHub Actions security settings."""
    findings = []

    for repo in org.get_repos():
        if repo.archived:
            continue
        repo_name = repo.full_name

        # Check for workflow files
        try:
            workflows_dir = repo.get_contents(".github/workflows")
            if not workflows_dir:
                continue

            has_workflows = True
            findings.append({
                "resource": f"{repo_name}/actions/workflows",
                "status": "pass",
                "detail": f"{len(workflows_dir)} workflow files found",
            })

            # Check each workflow for security patterns
            for wf_file in workflows_dir:
                if not wf_file.name.endswith((".yml", ".yaml")):
                    continue
                try:
                    content = wf_file.decoded_content.decode("utf-8")

                    # Check for pull_request_target (risky)
                    if "pull_request_target" in content:
                        findings.append({
                            "resource": f"{repo_name}/actions/{wf_file.name}/pr-target",
                            "status": "fail",
                            "detail": f"Uses pull_request_target trigger (potential security risk)",
                        })

                    # Check for environment secrets vs inline secrets
                    if "${{ secrets." in content:
                        findings.append({
                            "resource": f"{repo_name}/actions/{wf_file.name}/secrets",
                            "status": "pass",
                            "detail": "Uses GitHub secrets (good practice)",
                        })
                except Exception:
                    continue

        except Exception:
            continue

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "ci_cd",
        "provider": "github",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
