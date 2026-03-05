"""GuardDuty compliance checks: detector status, active findings."""


def run_guardduty_checks(session, region="us-east-1"):
    """Run GuardDuty checks and return findings."""
    gd = session.client("guardduty", region_name=region)
    findings = []

    # Check if GuardDuty is enabled
    try:
        detectors = gd.list_detectors()["DetectorIds"]
        if not detectors:
            return {
                "check": "guardduty",
                "provider": "aws",
                "status": "fail",
                "total": 1,
                "passed": 0,
                "failed": 1,
                "findings": [{
                    "resource": "guardduty/detector",
                    "status": "fail",
                    "detail": "GuardDuty not enabled (no detectors)",
                }],
            }

        detector_id = detectors[0]
        detector = gd.get_detector(DetectorId=detector_id)
        status = detector.get("Status", "DISABLED")
        findings.append({
            "resource": "guardduty/detector",
            "status": "pass" if status == "ENABLED" else "fail",
            "detail": f"GuardDuty detector status: {status}",
        })

        # Get active findings
        finding_ids = gd.list_findings(
            DetectorId=detector_id,
            FindingCriteria={"Criterion": {"service.archived": {"Eq": ["false"]}}},
            MaxResults=50,
        ).get("FindingIds", [])

        if finding_ids:
            gd_findings = gd.get_findings(
                DetectorId=detector_id,
                FindingIds=finding_ids,
            ).get("Findings", [])

            by_severity = {"High": 0, "Medium": 0, "Low": 0}
            for f in gd_findings:
                sev = f.get("Severity", 0)
                if sev >= 7:
                    by_severity["High"] += 1
                elif sev >= 4:
                    by_severity["Medium"] += 1
                else:
                    by_severity["Low"] += 1

            findings.append({
                "resource": "guardduty/findings",
                "status": "fail" if by_severity["High"] > 0 else "pass",
                "detail": f"Active findings: {len(finding_ids)} ({by_severity['High']} high, {by_severity['Medium']} medium, {by_severity['Low']} low)",
            })
        else:
            findings.append({
                "resource": "guardduty/findings",
                "status": "pass",
                "detail": "No active findings",
            })

    except Exception:
        return {
            "check": "guardduty",
            "provider": "aws",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "guardduty/detector",
                "status": "fail",
                "detail": "Could not access GuardDuty (not enabled or access denied)",
            }],
        }

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "guardduty",
        "provider": "aws",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
