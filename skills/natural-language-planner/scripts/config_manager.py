"""
Configuration management for the Natural Language Planner.

Handles loading, saving, and accessing user settings stored in
.nlplanner/config.json within the workspace directory.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from .utils import ensure_directory, safe_read_file, safe_write_file

logger = logging.getLogger("nlplanner.config")

# Default configuration values
DEFAULT_CONFIG: dict[str, Any] = {
    "version": "1.0.0",
    "workspace_path": "",
    "settings": {
        "checkin_frequency_hours": 24,
        "auto_archive_completed_days": 30,
        "default_priority": "medium",
        "dashboard_port": 8080,
        "dashboard_auto_start": True,
        "dashboard_allow_network": False,
        "enable_notifications": False,
    },
    "preferences": {
        "default_project": "inbox",
        "task_id_format": "task-{counter:03d}",
        "project_id_format": "{slug}",
    },
}

# Module-level cached config path
_config_path: Optional[Path] = None


def _get_config_path(workspace_path: Optional[str] = None) -> Path:
    """
    Resolve the path to config.json.

    Args:
        workspace_path: Explicit workspace path. If None, uses cached or default.

    Returns:
        Path to the config.json file.
    """
    global _config_path

    if workspace_path:
        p = Path(workspace_path).expanduser().resolve()
        _config_path = p / ".nlplanner" / "config.json"
    elif _config_path is None:
        # Fallback: look for a config in the current directory or home
        _config_path = Path.home() / "nlplanner" / ".nlplanner" / "config.json"

    return _config_path


def set_config_path(workspace_path: str) -> None:
    """
    Set the workspace path used by the config manager.

    Call this early — before any other config operations — to point
    the planner at the correct workspace directory.

    Args:
        workspace_path: Absolute or ~-relative path to the workspace root.
    """
    _get_config_path(workspace_path)
    logger.info("Config path set to %s", _config_path)


def load_config(workspace_path: Optional[str] = None) -> dict[str, Any]:
    """
    Load the configuration file.

    If the file doesn't exist, returns a copy of DEFAULT_CONFIG.

    Args:
        workspace_path: Optional explicit workspace path.

    Returns:
        Configuration dictionary.

    Example:
        >>> config = load_config("/home/user/nlplanner")
        >>> config["settings"]["dashboard_port"]
        8080
    """
    path = _get_config_path(workspace_path)

    if not path.exists():
        logger.info("No config file found at %s — using defaults.", path)
        return _deep_copy_config(DEFAULT_CONFIG)

    raw = safe_read_file(path)
    if raw is None:
        logger.warning("Could not read config — using defaults.")
        return _deep_copy_config(DEFAULT_CONFIG)

    try:
        config = json.loads(raw)
        # Merge with defaults so new keys are always present
        merged = _merge_config(DEFAULT_CONFIG, config)
        return merged
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file: %s", e)
        return _deep_copy_config(DEFAULT_CONFIG)


def save_config(config: dict[str, Any], workspace_path: Optional[str] = None) -> bool:
    """
    Persist the configuration dictionary to disk.

    Args:
        config: The configuration dictionary to save.
        workspace_path: Optional explicit workspace path.

    Returns:
        True if saved successfully, False otherwise.
    """
    path = _get_config_path(workspace_path)
    ensure_directory(path.parent)

    try:
        content = json.dumps(config, indent=2, ensure_ascii=False)
        return safe_write_file(path, content)
    except (TypeError, ValueError) as e:
        logger.error("Failed to serialize config: %s", e)
        return False


def get_workspace_path() -> str:
    """
    Return the configured workspace path.

    Returns:
        The workspace root directory path as a string.
    """
    config = load_config()
    return config.get("workspace_path", "")


def set_workspace_path(path: str) -> bool:
    """
    Update the workspace path in the configuration.

    Also updates the internal config path pointer so subsequent
    operations use the new workspace.

    Args:
        path: New workspace root directory path.

    Returns:
        True if the config was saved successfully.
    """
    resolved = str(Path(path).expanduser().resolve())
    set_config_path(resolved)
    config = load_config(resolved)
    config["workspace_path"] = resolved
    return save_config(config, resolved)


def get_setting(key: str) -> Any:
    """
    Get a single setting value by key.

    Args:
        key: The setting name (e.g., 'dashboard_port').

    Returns:
        The setting value, or None if not found.
    """
    config = load_config()
    return config.get("settings", {}).get(key)


def set_setting(key: str, value: Any) -> bool:
    """
    Update a single setting value.

    Args:
        key: The setting name.
        value: The new value.

    Returns:
        True if saved successfully.
    """
    config = load_config()
    config.setdefault("settings", {})[key] = value
    return save_config(config)


def get_checkin_frequency() -> int:
    """
    Get the check-in frequency in hours.

    Returns:
        Number of hours between proactive check-ins.
    """
    return get_setting("checkin_frequency_hours") or 24


def set_checkin_frequency(hours: int) -> bool:
    """
    Set the check-in frequency.

    Args:
        hours: Number of hours between check-ins (minimum 1).

    Returns:
        True if saved successfully.
    """
    hours = max(1, hours)
    return set_setting("checkin_frequency_hours", hours)


def get_preference(key: str) -> Any:
    """
    Get a single preference value by key.

    Args:
        key: The preference name (e.g., 'default_project').

    Returns:
        The preference value, or None if not found.
    """
    config = load_config()
    return config.get("preferences", {}).get(key)


# ── Internal helpers ────────────────────────────────────────────────

def _deep_copy_config(source: dict) -> dict:
    """Return a deep copy of a config dict via JSON round-trip."""
    return json.loads(json.dumps(source))


def _merge_config(defaults: dict, overrides: dict) -> dict:
    """
    Recursively merge *overrides* into *defaults*.

    Keys present in overrides take precedence; keys only in defaults
    are preserved so that newly added settings always appear.
    """
    merged = _deep_copy_config(defaults)
    for key, value in overrides.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged
