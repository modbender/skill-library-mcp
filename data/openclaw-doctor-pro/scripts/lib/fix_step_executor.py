"""Step execution logic for the fix engine."""
from __future__ import annotations

from pathlib import Path

from .utils import run_command, get_config, save_json, CONFIG_FILE


def substitute_params(text: str, params: dict) -> str:
    """Replace {key} placeholders with values from params dict.

    Args:
        text: Text with {placeholder} markers
        params: Dict with replacement values

    Returns:
        Text with substitutions applied
    """
    for key, value in params.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text


def execute_step(
    step: dict,
    dry_run: bool,
    params: dict
) -> tuple[bool, str]:
    """Execute a single recipe step.

    Args:
        step: Step dict with type and data
        dry_run: If True, only describe action
        params: Parameter substitution dict

    Returns:
        Tuple of (success, message)
    """
    step_type = step.get("type", "")

    if step_type == "command":
        return _execute_command_step(step, dry_run, params)
    elif step_type == "config_set":
        return _execute_config_set_step(step, dry_run, params)
    elif step_type == "file_op":
        return _execute_file_op_step(step, dry_run, params)
    elif step_type == "message":
        message = substitute_params(step.get("message", ""), params)
        return True, message
    else:
        return False, f"Unknown step type: {step_type}"


def _execute_command_step(step: dict, dry_run: bool, params: dict) -> tuple[bool, str]:
    """Execute a command step."""
    cmd = substitute_params(step.get("command", ""), params)

    if dry_run:
        return True, f"Would run: {cmd}"

    returncode, stdout, stderr = run_command(cmd.split())
    if returncode == 0:
        return True, f"Executed: {cmd}"
    else:
        return False, f"Command failed: {stderr}"


def _execute_config_set_step(step: dict, dry_run: bool, params: dict) -> tuple[bool, str]:
    """Execute a config_set step."""
    key = substitute_params(step.get("key", ""), params)
    value = substitute_params(step.get("value", ""), params)

    if dry_run:
        return True, f"Would set config {key}={value}"

    config = get_config() or {}
    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value

    if save_json(CONFIG_FILE, config):
        return True, f"Set config {key}={value}"
    else:
        return False, "Failed to save config"


def _execute_file_op_step(step: dict, dry_run: bool, params: dict) -> tuple[bool, str]:
    """Execute a file operation step."""
    operation = step.get("operation", "")
    path = Path(substitute_params(step.get("path", ""), params))

    if dry_run:
        return True, f"Would perform file op: {operation} on {path}"

    try:
        if operation == "create":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            return True, f"Created file: {path}"
        elif operation == "delete":
            path.unlink(missing_ok=True)
            return True, f"Deleted file: {path}"
        elif operation == "mkdir":
            path.mkdir(parents=True, exist_ok=True)
            return True, f"Created directory: {path}"
        else:
            return False, f"Unknown file operation: {operation}"
    except Exception as e:
        return False, f"File operation failed: {e}"
