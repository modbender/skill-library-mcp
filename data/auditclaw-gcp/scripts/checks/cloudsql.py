"""GCP Cloud SQL checks: SSL enforcement, no public IP with 0.0.0.0/0."""

from googleapiclient.discovery import build
import google.auth


def run_cloudsql_checks(project_id):
    """Run Cloud SQL compliance checks and return findings.

    Uses the discovery-based googleapiclient (not the newer google-cloud-sql library).

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []

    try:
        credentials, _ = google.auth.default()
        sqladmin = build("sqladmin", "v1", credentials=credentials)
        result = sqladmin.instances().list(project=project_id).execute()
        instances = result.get("items", [])
    except Exception as e:
        return {
            "check": "cloudsql",
            "provider": "gcp",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "cloudsql/api",
                "status": "fail",
                "detail": f"Could not list Cloud SQL instances: {e}",
            }],
        }

    if not instances:
        return {
            "check": "cloudsql",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for inst in instances:
        inst_name = inst.get("name", "unknown")
        settings = inst.get("settings", {})
        ip_config = settings.get("ipConfiguration", {})

        findings.extend(_check_ssl(inst_name, ip_config))
        findings.extend(_check_public_ip(inst_name, ip_config))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "cloudsql",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_ssl(inst_name, ip_config):
    """Check that SSL/TLS is required for connections."""
    require_ssl = ip_config.get("requireSsl", False)
    return [{
        "resource": f"cloudsql/{inst_name}/ssl",
        "status": "pass" if require_ssl else "fail",
        "detail": f"SSL {'required' if require_ssl else 'not required'} for instance {inst_name}",
    }]


def _check_public_ip(inst_name, ip_config):
    """Check for public IP exposure with 0.0.0.0/0 authorized network."""
    ipv4_enabled = ip_config.get("ipv4Enabled", False)

    if not ipv4_enabled:
        return [{
            "resource": f"cloudsql/{inst_name}/public-ip",
            "status": "pass",
            "detail": f"Instance {inst_name} has no public IP",
        }]

    authorized_networks = ip_config.get("authorizedNetworks", [])
    open_networks = [
        n for n in authorized_networks
        if n.get("value") == "0.0.0.0/0"
    ]

    if open_networks:
        return [{
            "resource": f"cloudsql/{inst_name}/public-ip",
            "status": "fail",
            "detail": f"Instance {inst_name} has public IP with 0.0.0.0/0 authorized",
        }]

    return [{
        "resource": f"cloudsql/{inst_name}/public-ip",
        "status": "pass",
        "detail": f"Instance {inst_name} has public IP but no 0.0.0.0/0 authorized",
    }]
