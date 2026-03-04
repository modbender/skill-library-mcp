"""GCP Firewall checks: no unrestricted ingress to SSH/RDP/all."""

from google.cloud.compute_v1 import FirewallsClient


def run_firewall_checks(project_id):
    """Run firewall ingress checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []
    try:
        fw_client = FirewallsClient()
        rules = list(fw_client.list(project=project_id))
    except Exception as e:
        return {
            "check": "firewall",
            "provider": "gcp",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "firewall/api",
                "status": "fail",
                "detail": f"Could not list firewall rules: {e}",
            }],
        }

    if not rules:
        return {
            "check": "firewall",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    # Check each INGRESS rule for unrestricted sources
    dangerous_ports = {"22", "3389"}

    for rule in rules:
        if rule.direction != "INGRESS":
            continue
        if "0.0.0.0/0" not in (rule.source_ranges or []):
            continue

        for allowed in (rule.allowed or []):
            proto = allowed.I_p_protocol if hasattr(allowed, "I_p_protocol") else getattr(allowed, "ip_protocol", "")
            ports = list(allowed.ports) if allowed.ports else []

            # Protocol "all" means every port
            if proto == "all":
                findings.append({
                    "resource": f"firewall/{rule.name}/all-traffic",
                    "status": "fail",
                    "detail": f"Rule '{rule.name}' allows ALL traffic from 0.0.0.0/0",
                })
                continue

            # Check for dangerous ports
            for port in ports:
                port_str = str(port)
                if port_str in dangerous_ports or _port_range_contains(port_str, dangerous_ports):
                    svc = "SSH" if "22" in port_str else "RDP"
                    findings.append({
                        "resource": f"firewall/{rule.name}/{svc.lower()}",
                        "status": "fail",
                        "detail": f"Rule '{rule.name}' allows {svc} (port {port_str}) from 0.0.0.0/0",
                    })

    # If no dangerous rules found, that's a pass
    if not findings:
        findings.append({
            "resource": "firewall/ingress-check",
            "status": "pass",
            "detail": "No unrestricted ingress rules found (SSH/RDP/all)",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "firewall",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _port_range_contains(port_range, target_ports):
    """Check if a port range string (e.g. '20-25') contains any target ports."""
    if "-" not in port_range:
        return False
    try:
        start, end = port_range.split("-", 1)
        start, end = int(start), int(end)
        for tp in target_ports:
            if start <= int(tp) <= end:
                return True
    except (ValueError, TypeError):
        pass
    return False
