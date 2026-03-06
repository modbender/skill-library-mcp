"""Webhook security checks: HTTPS, secrets configured."""


def run_webhooks_checks(org, github_client):
    """Check webhook security across organization repos."""
    findings = []

    for repo in org.get_repos():
        if repo.archived:
            continue
        repo_name = repo.full_name

        try:
            hooks = list(repo.get_hooks())
            for hook in hooks:
                config = hook.config if hasattr(hook, 'config') else {}
                url = config.get("url", "")
                has_secret = bool(config.get("secret"))
                is_https = url.startswith("https://")

                issues = []
                if not is_https:
                    issues.append("HTTP (not HTTPS)")
                if not has_secret:
                    issues.append("no secret configured")

                findings.append({
                    "resource": f"{repo_name}/webhook/{hook.id}",
                    "status": "pass" if is_https and has_secret else "fail",
                    "detail": "Secure webhook (HTTPS + secret)" if not issues
                              else f"Webhook issues: {', '.join(issues)}",
                })
        except Exception:
            continue

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "webhooks",
        "provider": "github",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
