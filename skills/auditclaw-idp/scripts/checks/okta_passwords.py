"""Okta password policy compliance check.

Verifies that the Okta password policy meets minimum thresholds:
- minLength >= 12
- history >= 5
- maxAttempts <= 5
- maxAgeDays <= 90

Uses async Okta SDK v3 with a sync wrapper.
"""

import asyncio

try:
    from okta.client import Client as OktaClient
except ImportError:
    OktaClient = None


# Compliance thresholds
MIN_PASSWORD_LENGTH = 12
MIN_HISTORY_COUNT = 5
MAX_LOCKOUT_ATTEMPTS = 5
MAX_AGE_DAYS = 90


def run_okta_password_checks(okta_config):
    """Sync wrapper around async Okta password policy checks.

    Args:
        okta_config: dict with orgUrl and token keys.

    Returns:
        dict with check, provider, status, total, passed, failed, findings.
    """
    return asyncio.run(_run_okta_password_checks_async(okta_config))


async def _run_okta_password_checks_async(okta_config):
    """Check Okta password policies against compliance thresholds."""
    findings = []
    try:
        client = OktaClient(okta_config)
        policies, _, err = await client.list_policies({"type": "PASSWORD"})
        if err:
            raise Exception(str(err))
    except Exception as e:
        return {
            "check": "okta_passwords",
            "provider": "okta",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "okta/passwords/api",
                "status": "fail",
                "detail": f"Failed to list password policies: {str(e)}",
            }],
        }

    if not policies:
        return {
            "check": "okta_passwords",
            "provider": "okta",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "okta/passwords/policy",
                "status": "fail",
                "detail": "No password policies found",
            }],
        }

    for policy in policies:
        policy_name = getattr(policy, "name", "unknown")
        settings = getattr(policy, "settings", None)
        if not settings:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}",
                "status": "fail",
                "detail": "Password policy has no settings",
            })
            continue

        password_settings = getattr(settings, "password", None)
        if not password_settings:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}",
                "status": "fail",
                "detail": "Password policy has no password settings",
            })
            continue

        complexity = getattr(password_settings, "complexity", None)
        age = getattr(password_settings, "age", None)
        lockout = getattr(password_settings, "lockout", None)

        # Check minLength
        min_length = getattr(complexity, "min_length", 0) if complexity else 0
        if min_length >= MIN_PASSWORD_LENGTH:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/min_length",
                "status": "pass",
                "detail": f"Minimum password length is {min_length} (>= {MIN_PASSWORD_LENGTH})",
            })
        else:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/min_length",
                "status": "fail",
                "detail": f"Minimum password length is {min_length} (required >= {MIN_PASSWORD_LENGTH})",
            })

        # Check history count
        history_count = getattr(age, "history_count", 0) if age else 0
        if history_count >= MIN_HISTORY_COUNT:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/history",
                "status": "pass",
                "detail": f"Password history count is {history_count} (>= {MIN_HISTORY_COUNT})",
            })
        else:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/history",
                "status": "fail",
                "detail": f"Password history count is {history_count} (required >= {MIN_HISTORY_COUNT})",
            })

        # Check max lockout attempts
        max_attempts = getattr(lockout, "max_attempts", 999) if lockout else 999
        if max_attempts <= MAX_LOCKOUT_ATTEMPTS:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/lockout",
                "status": "pass",
                "detail": f"Max lockout attempts is {max_attempts} (<= {MAX_LOCKOUT_ATTEMPTS})",
            })
        else:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/lockout",
                "status": "fail",
                "detail": f"Max lockout attempts is {max_attempts} (required <= {MAX_LOCKOUT_ATTEMPTS})",
            })

        # Check max age days
        max_age_days = getattr(age, "max_age_days", 999) if age else 999
        if max_age_days <= MAX_AGE_DAYS:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/max_age",
                "status": "pass",
                "detail": f"Max password age is {max_age_days} days (<= {MAX_AGE_DAYS})",
            })
        else:
            findings.append({
                "resource": f"okta/password_policy/{policy_name}/max_age",
                "status": "fail",
                "detail": f"Max password age is {max_age_days} days (required <= {MAX_AGE_DAYS})",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "okta_passwords",
        "provider": "okta",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
