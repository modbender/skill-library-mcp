"""Azure compliance check modules for auditclaw-grc."""

from .storage import run_storage_checks
from .network import run_network_checks
from .keyvault import run_keyvault_checks
from .sql import run_sql_checks
from .compute import run_compute_checks
from .appservice import run_appservice_checks
from .defender import run_defender_checks

ALL_CHECKS = {
    "storage": run_storage_checks,
    "network": run_network_checks,
    "keyvault": run_keyvault_checks,
    "sql": run_sql_checks,
    "compute": run_compute_checks,
    "appservice": run_appservice_checks,
    "defender": run_defender_checks,
}
