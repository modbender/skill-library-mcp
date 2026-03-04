"""GCP IAM checks: service account key rotation, SA admin privilege restriction."""

from datetime import datetime, timezone, timedelta

from google.cloud.iam_admin_v1 import IAMClient, ListServiceAccountKeysRequest
from google.cloud.resourcemanager_v3 import ProjectsClient


def run_iam_checks(project_id):
    """Run all IAM checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []
    findings.extend(_check_sa_key_rotation(project_id))
    findings.extend(_check_sa_admin_privilege(project_id))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "iam",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_sa_key_rotation(project_id):
    """Check that all service account keys are rotated within 90 days."""
    findings = []
    max_age_days = 90

    try:
        iam_client = IAMClient()
        # List service accounts
        sa_list = iam_client.list_service_accounts(
            name=f"projects/{project_id}"
        )
        service_accounts = list(sa_list)
    except Exception as e:
        return [{
            "resource": "iam/sa-keys/api",
            "status": "fail",
            "detail": f"Could not list service accounts: {e}",
        }]

    if not service_accounts:
        return [{
            "resource": "iam/sa-keys",
            "status": "pass",
            "detail": "No service accounts found",
        }]

    now = datetime.now(timezone.utc)

    for sa in service_accounts:
        try:
            request = ListServiceAccountKeysRequest(name=sa.name)
            keys = list(iam_client.list_service_account_keys(request=request).keys)
        except Exception as e:
            findings.append({
                "resource": f"iam/{sa.email}/keys",
                "status": "fail",
                "detail": f"Could not list keys for {sa.email}: {e}",
            })
            continue

        for key in keys:
            # Skip system-managed keys
            key_type = getattr(key, "key_type", None)
            if key_type is not None and key_type != 1:
                # key_type 1 = USER_MANAGED
                continue

            created = key.valid_after_time
            if created is None:
                continue

            age = (now - created).days
            if age > max_age_days:
                findings.append({
                    "resource": f"iam/{sa.email}/key/{key.name.split('/')[-1]}",
                    "status": "fail",
                    "detail": f"Key is {age} days old (max {max_age_days})",
                })
            else:
                findings.append({
                    "resource": f"iam/{sa.email}/key/{key.name.split('/')[-1]}",
                    "status": "pass",
                    "detail": f"Key is {age} days old (within {max_age_days}-day limit)",
                })

    if not findings:
        findings.append({
            "resource": "iam/sa-keys",
            "status": "pass",
            "detail": "No user-managed service account keys found",
        })

    return findings


def _check_sa_admin_privilege(project_id):
    """Check that no service accounts have owner/editor/admin roles."""
    findings = []
    admin_roles = {"roles/owner", "roles/editor"}
    admin_suffixes = ("Admin", ".admin")

    try:
        rm_client = ProjectsClient()
        policy = rm_client.get_iam_policy(resource=f"projects/{project_id}")
    except Exception as e:
        return [{
            "resource": "iam/sa-admin/api",
            "status": "fail",
            "detail": f"Could not get IAM policy: {e}",
        }]

    sa_admin_bindings = []

    for binding in policy.bindings:
        role = binding.role
        is_admin = role in admin_roles or any(role.endswith(s) for s in admin_suffixes)
        if not is_admin:
            continue

        for member in binding.members:
            if member.startswith("serviceAccount:"):
                sa_email = member.split(":", 1)[1]
                sa_admin_bindings.append((sa_email, role))

    if sa_admin_bindings:
        for sa_email, role in sa_admin_bindings:
            findings.append({
                "resource": f"iam/{sa_email}/admin-role",
                "status": "fail",
                "detail": f"Service account has admin role: {role}",
            })
    else:
        findings.append({
            "resource": "iam/sa-admin-privilege",
            "status": "pass",
            "detail": "No service accounts have owner/editor/admin roles",
        })

    return findings
