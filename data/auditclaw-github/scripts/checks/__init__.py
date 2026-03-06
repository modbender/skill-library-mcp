"""GitHub compliance check modules for auditclaw-grc."""

from .branch_protection import run_branch_protection_checks
from .secret_scanning import run_secret_scanning_checks
from .dependabot import run_dependabot_checks
from .two_factor import run_two_factor_checks
from .deploy_keys import run_deploy_keys_checks
from .audit_log import run_audit_log_checks
from .webhooks import run_webhooks_checks
from .codeowners import run_codeowners_checks
from .ci_cd import run_ci_cd_checks

ALL_CHECKS = {
    "branch_protection": run_branch_protection_checks,
    "secret_scanning": run_secret_scanning_checks,
    "dependabot": run_dependabot_checks,
    "two_factor": run_two_factor_checks,
    "deploy_keys": run_deploy_keys_checks,
    "audit_log": run_audit_log_checks,
    "webhooks": run_webhooks_checks,
    "codeowners": run_codeowners_checks,
    "ci_cd": run_ci_cd_checks,
}
