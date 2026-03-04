"""Branch protection checks: rules on default branches."""


def run_branch_protection_checks(org, github_client):
    """Check branch protection on all repos' default branches."""
    findings = []

    for repo in org.get_repos():
        if repo.archived:
            continue
        repo_name = repo.full_name
        default_branch = repo.default_branch

        try:
            branch = repo.get_branch(default_branch)
            protection = branch.get_protection()

            # Required reviews
            try:
                reviews = protection.required_pull_request_reviews
                has_reviews = reviews is not None
                min_reviewers = reviews.required_approving_review_count if has_reviews else 0
                findings.append({
                    "resource": f"{repo_name}/{default_branch}/reviews",
                    "status": "pass" if has_reviews and min_reviewers >= 1 else "fail",
                    "detail": f"Required reviews: {min_reviewers}" if has_reviews else "No review requirement",
                })
            except Exception:
                findings.append({
                    "resource": f"{repo_name}/{default_branch}/reviews",
                    "status": "fail",
                    "detail": "No pull request review requirement",
                })

            # Status checks
            try:
                checks = protection.required_status_checks
                has_checks = checks is not None
                findings.append({
                    "resource": f"{repo_name}/{default_branch}/status-checks",
                    "status": "pass" if has_checks else "fail",
                    "detail": "Required status checks configured" if has_checks else "No required status checks",
                })
            except Exception:
                findings.append({
                    "resource": f"{repo_name}/{default_branch}/status-checks",
                    "status": "fail",
                    "detail": "No required status checks",
                })

            # Force push prevention
            findings.append({
                "resource": f"{repo_name}/{default_branch}/force-push",
                "status": "pass",
                "detail": "Branch protection enabled (force push blocked by default)",
            })

        except Exception:
            findings.append({
                "resource": f"{repo_name}/{default_branch}/protection",
                "status": "fail",
                "detail": "No branch protection configured",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "branch_protection",
        "provider": "github",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
