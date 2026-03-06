"""Security audit checks for OpenClaw configuration."""
from __future__ import annotations

from typing import Any

from .config_analyzer import ConfigIssue


def check_security(config: dict) -> list[ConfigIssue]:
    """Run security audit checks on configuration.

    Args:
        config: Full OpenClaw config dict

    Returns:
        List of security-related issues
    """
    issues = []
    gateway = config.get("gateway", {})
    channels = config.get("channels", {})
    agent = config.get("agent", {})

    # Check for default auth token
    auth_token = gateway.get("authToken")
    if auth_token == "changeme":
        issues.append(ConfigIssue(
            severity="error",
            path="gateway.authToken",
            message="Using default auth token 'changeme'",
            fix_hint="Generate a secure random token for production use"
        ))

    # Check for open DM policy without restrictions
    for channel_name, channel_config in channels.items():
        dm_policy = channel_config.get("dmPolicy")
        allow_from = channel_config.get("allowFrom", [])

        if dm_policy == "open" and not allow_from:
            issues.append(ConfigIssue(
                severity="warning",
                path=f"channels.{channel_name}.dmPolicy",
                message=f"Channel {channel_name} has open DM policy without allowFrom restrictions",
                fix_hint="Add allowFrom list or change dmPolicy to 'whitelist'"
            ))

    # Check sandbox mode in production
    sandbox = agent.get("sandboxMode")
    if sandbox == "off":
        issues.append(ConfigIssue(
            severity="warning",
            path="agent.sandboxMode",
            message="Sandbox mode is disabled",
            fix_hint="Enable sandbox mode ('strict' or 'relaxed') for production environments"
        ))

    return issues


def get_config_path(config: dict, path: str) -> Any:
    """Access config value using dot-notation path.

    Args:
        config: Config dict to search
        path: Dot-separated path (e.g., 'gateway.port')

    Returns:
        Value at path or None if not found
    """
    parts = path.split(".")
    value = config

    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None

    return value
