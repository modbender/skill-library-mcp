"""GCP Logging checks: audit logging enabled, log export sink exists.

Named gcp_logging.py to avoid conflict with Python's built-in logging module.
"""

from google.cloud.resourcemanager_v3 import ProjectsClient
from google.cloud.logging_v2 import Client as LoggingClient


def run_logging_checks(project_id):
    """Run all logging checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []
    findings.extend(_check_audit_logging(project_id))
    findings.extend(_check_log_export_sink(project_id))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "logging",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_audit_logging(project_id):
    """Check that audit logging is enabled for all services (data access logs)."""
    try:
        rm_client = ProjectsClient()
        policy = rm_client.get_iam_policy(resource=f"projects/{project_id}")
    except Exception as e:
        return [{
            "resource": "logging/audit-config/api",
            "status": "fail",
            "detail": f"Could not get IAM policy for audit config: {e}",
        }]

    # Check audit configs on the policy
    audit_configs = getattr(policy, "audit_configs", []) or []

    if not audit_configs:
        return [{
            "resource": "logging/audit-config",
            "status": "fail",
            "detail": "No audit logging configuration found",
        }]

    # Look for allServices audit config
    has_all_services = False
    for config in audit_configs:
        service = getattr(config, "service", "")
        if service == "allServices":
            has_all_services = True
            log_types = [getattr(lc, "log_type", None) for lc in (config.audit_log_configs or [])]
            # log_type values: 1=ADMIN_READ, 2=DATA_WRITE, 3=DATA_READ
            has_all_types = len(log_types) >= 3
            if has_all_types:
                return [{
                    "resource": "logging/audit-config",
                    "status": "pass",
                    "detail": "Audit logging enabled for all services with all log types",
                }]
            else:
                return [{
                    "resource": "logging/audit-config",
                    "status": "fail",
                    "detail": f"Audit logging configured but only {len(log_types)} log type(s) enabled (need 3: ADMIN_READ, DATA_WRITE, DATA_READ)",
                }]

    if not has_all_services:
        return [{
            "resource": "logging/audit-config",
            "status": "fail",
            "detail": "Audit logging not configured for allServices",
        }]

    return []


def _check_log_export_sink(project_id):
    """Check that at least one log export sink exists (ideally with no filter for all logs)."""
    try:
        log_client = LoggingClient(project=project_id)
        sinks = list(log_client.list_sinks())
    except Exception as e:
        return [{
            "resource": "logging/export-sink/api",
            "status": "fail",
            "detail": f"Could not list log sinks: {e}",
        }]

    if not sinks:
        return [{
            "resource": "logging/export-sink",
            "status": "fail",
            "detail": "No log export sinks configured",
        }]

    # Check if any sink has no filter (captures all logs)
    for sink in sinks:
        sink_filter = getattr(sink, "filter_", "") or ""
        if not sink_filter:
            return [{
                "resource": f"logging/export-sink/{sink.name}",
                "status": "pass",
                "detail": f"Log export sink '{sink.name}' captures all logs (no filter)",
            }]

    # Sinks exist but all have filters
    return [{
        "resource": "logging/export-sink",
        "status": "pass",
        "detail": f"{len(sinks)} log export sink(s) configured (all have filters)",
    }]
