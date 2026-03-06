"""Okta global session policy check.

Verifies that the Okta sign-on policy enforces:
1. MFA is required (useMfaForFactorEnrollment or conditions include MFA).
2. Session lifetime <= 12 hours (720 minutes).
3. Session idle timeout <= 1 hour (60 minutes).

Uses async Okta SDK v3 with a sync wrapper.
"""

import asyncio

try:
    from okta.client import Client as OktaClient
except ImportError:
    OktaClient = None


# Compliance thresholds (in minutes)
MAX_SESSION_LIFETIME_MINUTES = 720   # 12 hours
MAX_SESSION_IDLE_MINUTES = 60        # 1 hour


def run_okta_session_checks(okta_config):
    """Sync wrapper around async Okta session policy checks.

    Args:
        okta_config: dict with orgUrl and token keys.

    Returns:
        dict with check, provider, status, total, passed, failed, findings.
    """
    return asyncio.run(_run_okta_session_checks_async(okta_config))


async def _run_okta_session_checks_async(okta_config):
    """Check Okta sign-on policies for MFA and session bounds."""
    findings = []
    try:
        client = OktaClient(okta_config)
        policies, _, err = await client.list_policies({"type": "OKTA_SIGN_ON"})
        if err:
            raise Exception(str(err))
    except Exception as e:
        return {
            "check": "okta_sessions",
            "provider": "okta",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "okta/sessions/api",
                "status": "fail",
                "detail": f"Failed to list sign-on policies: {str(e)}",
            }],
        }

    if not policies:
        return {
            "check": "okta_sessions",
            "provider": "okta",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "okta/sessions/policy",
                "status": "fail",
                "detail": "No sign-on policies found",
            }],
        }

    for policy in policies:
        policy_name = getattr(policy, "name", "unknown")
        settings = getattr(policy, "settings", None)

        # Check MFA requirement
        # Okta sign-on policies can require MFA via conditions or settings
        conditions = getattr(policy, "conditions", None)
        people = getattr(conditions, "people", None) if conditions else None

        # Check if policy has MFA requirement in settings
        mfa_required = False
        if settings:
            # Some Okta orgs use maxSessionLifetimeMinutes at the settings level
            max_session = getattr(settings, "maxSessionLifetimeMinutes", None)
            max_idle = getattr(settings, "maxSessionIdleMinutes", None)

            # Check for MFA in conditions
            auth_context = getattr(conditions, "authContext", None) if conditions else None
            if auth_context:
                auth_type = getattr(auth_context, "authType", "")
                if auth_type == "ANY" or auth_type == "MFA":
                    mfa_required = True

            # Also check for useMfaForFactorEnrollment
            if getattr(settings, "useMfaForFactorEnrollment", False):
                mfa_required = True
        else:
            max_session = None
            max_idle = None

        # Finding: MFA requirement
        if mfa_required:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/mfa",
                "status": "pass",
                "detail": "MFA is required for sign-on",
            })
        else:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/mfa",
                "status": "fail",
                "detail": "MFA is not required for sign-on",
            })

        # Finding: Session lifetime
        if max_session is not None and max_session <= MAX_SESSION_LIFETIME_MINUTES:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/lifetime",
                "status": "pass",
                "detail": f"Session lifetime is {max_session} min (<= {MAX_SESSION_LIFETIME_MINUTES})",
            })
        elif max_session is not None:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/lifetime",
                "status": "fail",
                "detail": f"Session lifetime is {max_session} min (required <= {MAX_SESSION_LIFETIME_MINUTES})",
            })
        else:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/lifetime",
                "status": "fail",
                "detail": "Session lifetime not configured (unbounded)",
            })

        # Finding: Session idle timeout
        if max_idle is not None and max_idle <= MAX_SESSION_IDLE_MINUTES:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/idle",
                "status": "pass",
                "detail": f"Session idle timeout is {max_idle} min (<= {MAX_SESSION_IDLE_MINUTES})",
            })
        elif max_idle is not None:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/idle",
                "status": "fail",
                "detail": f"Session idle timeout is {max_idle} min (required <= {MAX_SESSION_IDLE_MINUTES})",
            })
        else:
            findings.append({
                "resource": f"okta/session_policy/{policy_name}/idle",
                "status": "fail",
                "detail": "Session idle timeout not configured (unbounded)",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "okta_sessions",
        "provider": "okta",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
