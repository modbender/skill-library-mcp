"""
reefwatch.config
~~~~~~~~~~~~~~~~
Configuration loading and validation utilities.
"""

from pathlib import Path

import yaml

from reefwatch._common import logger

_VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
_VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_VALID_YARA_MODES = {"on_change", "scheduled"}


def load_config(path: str) -> dict:
    p = Path(path).expanduser()
    if not p.exists():
        logger.warning(f"Config not found at {p}, using defaults")
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def validate_config(config: dict) -> list[str]:
    """Validate config and return list of warning messages."""
    warnings: list[str] = []

    # Validate intervals (must be positive)
    for section, key in [
        (("collectors", "logs"), "interval_seconds"),
        (("collectors", "processes"), "interval_seconds"),
        (("collectors", "network"), "interval_seconds"),
    ]:
        val = config
        for k in section:
            val = val.get(k, {}) if isinstance(val, dict) else {}
        interval = val.get(key) if isinstance(val, dict) else None
        if interval is not None and (not isinstance(interval, (int, float)) or interval <= 0):
            warnings.append(
                f"{'.'.join(section)}.{key} must be positive, got {interval}"
            )

    # Validate min_severity
    min_sev = config.get("alerting", {}).get("min_severity")
    if min_sev is not None and min_sev not in _VALID_SEVERITIES:
        warnings.append(
            f"alerting.min_severity '{min_sev}' is not valid "
            f"(expected one of {_VALID_SEVERITIES})"
        )

    # Validate suspicious ports (0-65535)
    ports = config.get("collectors", {}).get("network", {}).get("suspicious_ports", [])
    for port in ports:
        if not isinstance(port, int) or port < 0 or port > 65535:
            warnings.append(f"Invalid suspicious port: {port} (must be 0-65535)")

    # Validate dedup_window (non-negative)
    dedup = config.get("alerting", {}).get("dedup_window_seconds")
    if dedup is not None and (not isinstance(dedup, (int, float)) or dedup < 0):
        warnings.append(
            f"alerting.dedup_window_seconds must be non-negative, got {dedup}"
        )

    # Validate batch_window (positive)
    batch_w = config.get("alerting", {}).get("batch_window_seconds")
    if batch_w is not None and (not isinstance(batch_w, (int, float)) or batch_w <= 0):
        warnings.append(
            f"alerting.batch_window_seconds must be positive, got {batch_w}"
        )

    # Validate retry_attempts (positive int)
    retry = config.get("webhook", {}).get("retry_attempts")
    if retry is not None and (not isinstance(retry, int) or retry < 1):
        warnings.append(
            f"webhook.retry_attempts must be a positive integer, got {retry}"
        )

    # Validate log_level
    log_level = config.get("general", {}).get("log_level")
    if log_level is not None:
        if not isinstance(log_level, str):
            warnings.append(
                f"general.log_level must be a string, got {type(log_level).__name__}"
            )
        elif log_level.upper() not in _VALID_LOG_LEVELS:
            warnings.append(
                f"general.log_level '{log_level}' is not valid "
                f"(expected one of {_VALID_LOG_LEVELS})"
            )

    # Validate YARA mode
    yara_mode = config.get("engines", {}).get("yara", {}).get("mode")
    if yara_mode is not None:
        if not isinstance(yara_mode, str):
            warnings.append(
                f"engines.yara.mode must be a string, got {type(yara_mode).__name__}"
            )
        elif yara_mode not in _VALID_YARA_MODES:
            warnings.append(
                f"engines.yara.mode '{yara_mode}' is not valid "
                f"(expected one of {_VALID_YARA_MODES})"
        )

    # Validate boolean fields
    for path_keys, key in [
        (("collectors", "logs"), "use_journald"),
        (("collectors", "logs"), "use_unified_log"),
        (("alerting",), "batch_alerts"),
        (("webhook",), "allow_external"),
    ]:
        val = config
        for k in path_keys:
            val = val.get(k, {}) if isinstance(val, dict) else {}
        v = val.get(key) if isinstance(val, dict) else None
        if v is not None and not isinstance(v, bool):
            warnings.append(
                f"{'.'.join(path_keys)}.{key} should be a boolean, got {type(v).__name__}"
            )

    # Validate numeric config values (must be positive)
    for path_keys, key in [
        (("collectors", "files"), "hash_threshold_kb"),
        (("engines", "yara"), "max_file_size_mb"),
        (("engines", "yara"), "timeout_seconds"),
        (("engines", "yara"), "scheduled_interval_hours"),
        (("engines", "custom"), "integrity_interval_seconds"),
    ]:
        val = config
        for k in path_keys:
            val = val.get(k, {}) if isinstance(val, dict) else {}
        v = val.get(key) if isinstance(val, dict) else None
        if v is not None and (not isinstance(v, (int, float)) or v <= 0):
            warnings.append(
                f"{'.'.join(path_keys)}.{key} must be positive, got {v}"
            )

    # Warn if webhook token is in config file (should use env var)
    token = config.get("webhook", {}).get("token")
    if token:
        warnings.append(
            "webhook.token is set in config file — prefer OPENCLAW_HOOKS_TOKEN env var"
        )

    return warnings
