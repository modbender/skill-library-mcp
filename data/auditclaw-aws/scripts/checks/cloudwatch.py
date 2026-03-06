"""CloudWatch compliance checks: log group retention, metric alarms."""


def run_cloudwatch_checks(session, region="us-east-1"):
    """Run all CloudWatch checks and return findings."""
    findings = []
    findings.extend(_check_log_retention(session, region))
    findings.extend(_check_metric_alarms(session, region))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "cloudwatch",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_log_retention(session, region):
    """Check that log groups have retention policies set."""
    logs = session.client("logs", region_name=region)
    findings = []

    try:
        log_groups = logs.describe_log_groups()["logGroups"]
    except Exception:
        return []

    for lg in log_groups:
        name = lg["logGroupName"]
        retention = lg.get("retentionInDays")
        findings.append({
            "resource": f"logs/{name}",
            "status": "pass" if retention else "fail",
            "detail": f"Retention: {retention} days" if retention else "No retention policy (logs kept forever)",
        })

    return findings


def _check_metric_alarms(session, region):
    """Check for essential CloudWatch metric alarms."""
    cw = session.client("cloudwatch", region_name=region)
    findings = []

    try:
        alarms = cw.describe_alarms(StateValue="OK")["MetricAlarms"]
        alarms += cw.describe_alarms(StateValue="ALARM")["MetricAlarms"]
        alarms += cw.describe_alarms(StateValue="INSUFFICIENT_DATA")["MetricAlarms"]

        findings.append({
            "resource": "cloudwatch/alarms",
            "status": "pass" if len(alarms) >= 1 else "fail",
            "detail": f"{len(alarms)} metric alarms configured",
        })
    except Exception:
        findings.append({
            "resource": "cloudwatch/alarms",
            "status": "fail",
            "detail": "Could not check metric alarms",
        })

    return findings
