"""GCP compliance check modules for auditclaw-grc."""

from .storage import run_storage_checks
from .firewall import run_firewall_checks
from .iam import run_iam_checks
from .gcp_logging import run_logging_checks
from .kms import run_kms_checks
from .dns import run_dns_checks
from .bigquery import run_bigquery_checks
from .compute import run_compute_checks
from .cloudsql import run_cloudsql_checks

ALL_CHECKS = {
    "storage": run_storage_checks,
    "firewall": run_firewall_checks,
    "iam": run_iam_checks,
    "logging": run_logging_checks,
    "kms": run_kms_checks,
    "dns": run_dns_checks,
    "bigquery": run_bigquery_checks,
    "compute": run_compute_checks,
    "cloudsql": run_cloudsql_checks,
}
