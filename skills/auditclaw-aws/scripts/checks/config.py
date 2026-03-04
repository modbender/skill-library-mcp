"""AWS Config compliance checks: recorder status, rule compliance."""


def run_config_checks(session, region="us-east-1"):
    """Run all AWS Config checks and return findings."""
    cfg = session.client("config", region_name=region)
    findings = []

    # Check Config recorder
    try:
        recorders = cfg.describe_configuration_recorders()["ConfigurationRecorders"]
        if not recorders:
            findings.append({
                "resource": "config/recorder",
                "status": "fail",
                "detail": "No Config recorder configured",
            })
        else:
            statuses = cfg.describe_configuration_recorder_status()["ConfigurationRecordersStatus"]
            for status in statuses:
                recording = status.get("recording", False)
                findings.append({
                    "resource": f"config/recorder/{status.get('name', 'default')}",
                    "status": "pass" if recording else "fail",
                    "detail": f"Config recorder: {'recording' if recording else 'not recording'}",
                })
    except Exception:
        findings.append({
            "resource": "config/recorder",
            "status": "fail",
            "detail": "Could not check Config recorder (not enabled or access denied)",
        })

    # Check Config rule compliance
    try:
        rules = cfg.describe_compliance_by_config_rule()["ComplianceByConfigRules"]
        compliant = sum(1 for r in rules if r.get("Compliance", {}).get("ComplianceType") == "COMPLIANT")
        non_compliant = sum(1 for r in rules if r.get("Compliance", {}).get("ComplianceType") == "NON_COMPLIANT")

        findings.append({
            "resource": "config/rules",
            "status": "pass" if non_compliant == 0 else "fail",
            "detail": f"Config rules: {compliant} compliant, {non_compliant} non-compliant out of {len(rules)} total",
        })
    except Exception:
        pass  # Config rules may not be set up

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "config",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
