"""IAM Credential Report: full analysis of all IAM users."""

import csv
import io
import time
from datetime import datetime, timezone


def run_credential_report_checks(session, region="us-east-1"):
    """Generate and analyze IAM credential report."""
    iam = session.client("iam")
    findings = []

    # Generate report
    try:
        iam.generate_credential_report()
        # Wait for report (may need a few seconds)
        for _ in range(10):
            try:
                response = iam.get_credential_report()
                break
            except iam.exceptions.CredentialReportNotReadyException:
                time.sleep(1)
        else:
            return {
                "check": "credential_report",
                "provider": "aws",
                "status": "fail",
                "total": 1,
                "passed": 0,
                "failed": 1,
                "findings": [{"resource": "credential-report", "status": "fail",
                              "detail": "Credential report generation timed out"}],
            }

        report_csv = response["Content"].decode("utf-8")
        reader = csv.DictReader(io.StringIO(report_csv))
        now = datetime.now(timezone.utc)

        for row in reader:
            user = row["user"]
            if user == "<root_account>":
                # Root account MFA
                root_mfa = row.get("mfa_active", "false") == "true"
                findings.append({
                    "resource": "iam/root/mfa",
                    "status": "pass" if root_mfa else "fail",
                    "detail": f"Root account MFA: {'enabled' if root_mfa else 'NOT ENABLED'}",
                })
                # Root access keys
                root_key1 = row.get("access_key_1_active", "false") == "true"
                root_key2 = row.get("access_key_2_active", "false") == "true"
                findings.append({
                    "resource": "iam/root/access-keys",
                    "status": "fail" if (root_key1 or root_key2) else "pass",
                    "detail": "Root access keys should not exist" if (root_key1 or root_key2)
                              else "No root access keys",
                })
                continue

            # Password last used (inactive users)
            if row.get("password_enabled", "false") == "true":
                last_used = row.get("password_last_used", "N/A")
                if last_used not in ("N/A", "no_information", "not_supported"):
                    try:
                        last_dt = datetime.fromisoformat(last_used.replace("Z", "+00:00").split("+")[0]).replace(tzinfo=timezone.utc)
                        days_inactive = (now - last_dt).days
                        findings.append({
                            "resource": f"iam/{user}/password-activity",
                            "status": "fail" if days_inactive > 90 else "pass",
                            "detail": f"Last password use: {days_inactive} days ago",
                        })
                    except (ValueError, TypeError):
                        pass

            # Access key 1 rotation
            if row.get("access_key_1_active", "false") == "true":
                rotated = row.get("access_key_1_last_rotated", "N/A")
                if rotated not in ("N/A", "not_supported"):
                    try:
                        rot_dt = datetime.fromisoformat(rotated.replace("Z", "+00:00").split("+")[0]).replace(tzinfo=timezone.utc)
                        age = (now - rot_dt).days
                        findings.append({
                            "resource": f"iam/{user}/key1-rotation",
                            "status": "pass" if age <= 90 else "fail",
                            "detail": f"Access key 1 age: {age} days",
                        })
                    except (ValueError, TypeError):
                        pass

    except Exception as e:
        return {
            "check": "credential_report",
            "provider": "aws",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{"resource": "credential-report", "status": "fail",
                          "detail": f"Could not generate credential report: {str(e)}"}],
        }

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "credential_report",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
