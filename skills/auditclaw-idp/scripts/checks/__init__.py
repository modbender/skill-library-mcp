"""IDP compliance check modules for auditclaw-grc (Google Workspace + Okta)."""

from .google_mfa import run_google_mfa_checks
from .google_admins import run_google_admin_checks
from .google_inactive import run_google_inactive_checks
from .google_passwords import run_google_password_checks
from .okta_mfa import run_okta_mfa_checks
from .okta_passwords import run_okta_password_checks
from .okta_inactive import run_okta_inactive_checks
from .okta_sessions import run_okta_session_checks

# Provider-specific check sets
GOOGLE_CHECKS = {
    "google_mfa": run_google_mfa_checks,
    "google_admins": run_google_admin_checks,
    "google_inactive": run_google_inactive_checks,
    "google_passwords": run_google_password_checks,
}

OKTA_CHECKS = {
    "okta_mfa": run_okta_mfa_checks,
    "okta_passwords": run_okta_password_checks,
    "okta_inactive": run_okta_inactive_checks,
    "okta_sessions": run_okta_session_checks,
}

# Combined registry
ALL_CHECKS = {**GOOGLE_CHECKS, **OKTA_CHECKS}
