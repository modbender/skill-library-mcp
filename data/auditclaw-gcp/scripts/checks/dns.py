"""GCP DNS checks: DNSSEC enabled on public zones."""

from google.cloud import dns


def run_dns_checks(project_id):
    """Run DNS DNSSEC checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []

    try:
        dns_client = dns.Client(project=project_id)
        zones = list(dns_client.list_zones())
    except Exception as e:
        return {
            "check": "dns",
            "provider": "gcp",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "dns/api",
                "status": "fail",
                "detail": f"Could not list DNS zones: {e}",
            }],
        }

    if not zones:
        return {
            "check": "dns",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for zone in zones:
        # Only check public zones
        visibility = getattr(zone, "visibility", "public") or "public"
        if visibility == "private":
            continue

        dnssec_config = getattr(zone, "dnssec_config", None)
        if dnssec_config:
            state = dnssec_config.get("state", "off") if isinstance(dnssec_config, dict) else getattr(dnssec_config, "state", "off")
        else:
            state = "off"

        enabled = state == "on"
        zone_name = getattr(zone, "name", str(zone))

        findings.append({
            "resource": f"dns/{zone_name}/dnssec",
            "status": "pass" if enabled else "fail",
            "detail": f"DNSSEC {'enabled' if enabled else 'not enabled'} for zone {zone_name}",
        })

    if not findings:
        return {
            "check": "dns",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "dns",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
