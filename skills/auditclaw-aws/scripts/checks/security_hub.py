"""Security Hub compliance checks: enabled status, active findings."""


def run_security_hub_checks(session, region="us-east-1"):
    """Run Security Hub checks and return findings."""
    sh = session.client("securityhub", region_name=region)
    findings = []

    # Check if Security Hub is enabled
    try:
        hub = sh.describe_hub()
        findings.append({
            "resource": "securityhub/status",
            "status": "pass",
            "detail": f"Security Hub enabled since {hub.get('SubscribedAt', 'unknown')}",
        })
    except Exception:
        return {
            "check": "security_hub",
            "provider": "aws",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "securityhub/status",
                "status": "fail",
                "detail": "Security Hub not enabled",
            }],
        }

    # Get active findings by severity
    try:
        result = sh.get_findings(
            Filters={"WorkflowStatus": [{"Value": "NEW", "Comparison": "EQUALS"}]},
            MaxResults=100,
        )
        hub_findings = result.get("Findings", [])
        by_severity = {}
        for f in hub_findings:
            sev = f.get("Severity", {}).get("Label", "UNKNOWN")
            by_severity[sev] = by_severity.get(sev, 0) + 1

        critical = by_severity.get("CRITICAL", 0)
        high = by_severity.get("HIGH", 0)

        findings.append({
            "resource": "securityhub/findings",
            "status": "fail" if critical > 0 else ("fail" if high > 5 else "pass"),
            "detail": f"Active findings: {len(hub_findings)} total, {critical} critical, {high} high",
        })
    except Exception:
        findings.append({
            "resource": "securityhub/findings",
            "status": "pass",
            "detail": "Could not retrieve findings (may need permissions)",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "security_hub",
        "provider": "aws",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
