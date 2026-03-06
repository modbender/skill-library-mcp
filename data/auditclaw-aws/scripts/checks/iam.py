"""IAM compliance checks: password policy, MFA, access key rotation."""

from datetime import datetime, timezone


def run_iam_checks(session, region="us-east-1"):
    """Run all IAM checks and return findings."""
    findings = []
    findings.extend(_check_password_policy(session))
    findings.extend(_check_mfa_enforcement(session))
    findings.extend(_check_access_key_rotation(session))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "iam",
        "provider": "aws",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_password_policy(session):
    """Check IAM password policy meets compliance requirements."""
    iam = session.client("iam")
    try:
        policy = iam.get_account_password_policy()["PasswordPolicy"]
        checks = [
            ("min_length", policy.get("MinimumPasswordLength", 0) >= 14,
             f"Minimum length: {policy.get('MinimumPasswordLength', 0)}"),
            ("require_uppercase", policy.get("RequireUppercaseCharacters", False),
             "Uppercase characters required" if policy.get("RequireUppercaseCharacters") else "Uppercase not required"),
            ("require_lowercase", policy.get("RequireLowercaseCharacters", False),
             "Lowercase characters required" if policy.get("RequireLowercaseCharacters") else "Lowercase not required"),
            ("require_numbers", policy.get("RequireNumbers", False),
             "Numbers required" if policy.get("RequireNumbers") else "Numbers not required"),
            ("require_symbols", policy.get("RequireSymbols", False),
             "Symbols required" if policy.get("RequireSymbols") else "Symbols not required"),
            ("max_age", 0 < policy.get("MaxPasswordAge", 0) <= 90,
             f"Max password age: {policy.get('MaxPasswordAge', 'not set')} days"),
            ("reuse_prevention", policy.get("PasswordReusePrevention", 0) >= 12,
             f"Password reuse prevention: {policy.get('PasswordReusePrevention', 0)} passwords"),
        ]
        return [
            {"resource": f"password-policy-{name}", "status": "pass" if ok else "fail", "detail": detail}
            for name, ok, detail in checks
        ]
    except iam.exceptions.NoSuchEntityException:
        return [{"resource": "password-policy", "status": "fail", "detail": "No password policy configured"}]


def _check_mfa_enforcement(session):
    """Check that all IAM users have MFA enabled."""
    iam = session.client("iam")
    users = iam.list_users()["Users"]
    findings = []
    for user in users:
        mfa_devices = iam.list_mfa_devices(UserName=user["UserName"])["MFADevices"]
        findings.append({
            "resource": f"user/{user['UserName']}",
            "status": "pass" if mfa_devices else "fail",
            "detail": f"MFA {'enabled' if mfa_devices else 'not enabled'} for {user['UserName']}",
        })
    return findings


def _check_access_key_rotation(session):
    """Check that access keys are rotated within 90 days."""
    iam = session.client("iam")
    users = iam.list_users()["Users"]
    findings = []
    now = datetime.now(timezone.utc)
    for user in users:
        keys = iam.list_access_keys(UserName=user["UserName"])["AccessKeyMetadata"]
        for key in keys:
            if key["Status"] != "Active":
                continue
            age_days = (now - key["CreateDate"]).days
            findings.append({
                "resource": f"access-key/{user['UserName']}/{key['AccessKeyId'][-4:]}",
                "status": "pass" if age_days <= 90 else "fail",
                "detail": f"Key age: {age_days} days (max 90)",
            })
    return findings
