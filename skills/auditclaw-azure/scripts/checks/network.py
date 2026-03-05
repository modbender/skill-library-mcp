"""Azure Network compliance checks: NSG unrestricted SSH and RDP."""

from azure.mgmt.network import NetworkManagementClient

OPEN_SOURCES = {"*", "0.0.0.0/0", "Internet", "0.0.0.0", "any"}


def run_network_checks(credential, subscription_id):
    """Run NSG checks for unrestricted SSH (22) and RDP (3389).

    Args:
        credential: Azure DefaultAzureCredential instance.
        subscription_id: Azure subscription ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    net_client = NetworkManagementClient(credential, subscription_id)
    findings = []

    try:
        nsgs = list(net_client.network_security_groups.list_all())
    except Exception as e:
        return {
            "check": "network",
            "provider": "azure",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "network/api",
                "status": "fail",
                "detail": f"Failed to list NSGs: {e}",
            }],
        }

    if not nsgs:
        return {
            "check": "network",
            "provider": "azure",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for nsg in nsgs:
        nsg_name = nsg.name
        ssh_open = False
        rdp_open = False

        for rule in (nsg.security_rules or []):
            if (rule.direction == "Inbound"
                    and rule.access == "Allow"
                    and rule.source_address_prefix in OPEN_SOURCES):
                port_range = str(rule.destination_port_range) if rule.destination_port_range else ""
                if _port_matches(port_range, 22):
                    ssh_open = True
                if _port_matches(port_range, 3389):
                    rdp_open = True

        # Finding 1: SSH not open to world
        findings.append({
            "resource": f"network/{nsg_name}/ssh-unrestricted",
            "status": "fail" if ssh_open else "pass",
            "detail": "SSH (port 22) open to 0.0.0.0/0" if ssh_open else "SSH (port 22) not open to world",
        })

        # Finding 2: RDP not open to world
        findings.append({
            "resource": f"network/{nsg_name}/rdp-unrestricted",
            "status": "fail" if rdp_open else "pass",
            "detail": "RDP (port 3389) open to 0.0.0.0/0" if rdp_open else "RDP (port 3389) not open to world",
        })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "network",
        "provider": "azure",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _port_matches(port_range, target_port):
    """Check if a port range string includes the target port."""
    if port_range == "*":
        return True
    try:
        if "-" in port_range:
            low, high = port_range.split("-", 1)
            return int(low) <= target_port <= int(high)
        return int(port_range) == target_port
    except (ValueError, TypeError):
        return False
