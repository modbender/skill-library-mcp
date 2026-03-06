"""OpenClaw configuration validator and analyzer."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .utils import get_config


@dataclass
class ConfigIssue:
    """Represents a configuration validation issue."""
    severity: str  # "error" | "warning" | "info"
    path: str  # JSON path like "gateway.port"
    message: str
    fix_hint: str | None


class ConfigAnalyzer:
    """OpenClaw configuration validator and analyzer."""

    def __init__(self):
        """Initialize analyzer and load config."""
        self.config = get_config()

    def analyze(self) -> list[ConfigIssue]:
        """Run all configuration checks.

        Returns:
            List of issues sorted by severity (errors first)
        """
        from .config_security_checks import check_security

        issues = []
        issues.extend(self._check_gateway(self.config))
        issues.extend(self._check_channels(self.config))
        issues.extend(self._check_agents(self.config))
        issues.extend(self._check_skills(self.config))
        issues.extend(self._check_plugins(self.config))
        issues.extend(check_security(self.config))

        severity_order = {"error": 0, "warning": 1, "info": 2}
        issues.sort(key=lambda x: severity_order.get(x.severity, 3))
        return issues

    def _check_gateway(self, config: dict) -> list[ConfigIssue]:
        """Validate gateway configuration section."""
        issues = []
        gateway = config.get("gateway", {})

        port = gateway.get("port")
        if port is not None:
            if not isinstance(port, int) or port < 1 or port > 65535:
                issues.append(ConfigIssue(
                    severity="error",
                    path="gateway.port",
                    message=f"Invalid port number: {port}",
                    fix_hint="Port must be between 1 and 65535"
                ))

        auth_mode = gateway.get("authMode")
        if not auth_mode:
            issues.append(ConfigIssue(
                severity="warning",
                path="gateway.authMode",
                message="Auth mode not set",
                fix_hint="Set authMode to 'token' or 'none' (not recommended for production)"
            ))

        bind = gateway.get("bind")
        if bind and not isinstance(bind, str):
            issues.append(ConfigIssue(
                severity="error",
                path="gateway.bind",
                message="Invalid bind address format",
                fix_hint="Bind address must be a string (e.g., '0.0.0.0' or '127.0.0.1')"
            ))

        return issues

    def _check_channels(self, config: dict) -> list[ConfigIssue]:
        """Validate channel configurations."""
        issues = []
        channels = config.get("channels", {})

        required_fields = {
            "telegram": ["token"],
            "discord": ["token"],
            "slack": ["token", "appToken"],
            "whatsapp": ["dmPolicy"]
        }

        for channel_name, required in required_fields.items():
            channel_config = channels.get(channel_name, {})
            enabled = channel_config.get("enabled", False)

            if enabled:
                for field in required:
                    if not channel_config.get(field):
                        issues.append(ConfigIssue(
                            severity="error",
                            path=f"channels.{channel_name}.{field}",
                            message=f"Missing required field '{field}' for enabled {channel_name} channel",
                            fix_hint=f"Add '{field}' to channels.{channel_name} configuration"
                        ))

        return issues

    def _check_agents(self, config: dict) -> list[ConfigIssue]:
        """Validate agent configuration."""
        issues = []
        agent = config.get("agent", {})

        model = agent.get("model")
        if not model:
            issues.append(ConfigIssue(
                severity="error",
                path="agent.model",
                message="No AI model configured",
                fix_hint="Set agent.model to a valid model name (e.g., 'gpt-4', 'claude-3')"
            ))

        workspace = agent.get("workspace")
        if workspace:
            workspace_path = Path(workspace).expanduser()
            if not workspace_path.exists():
                issues.append(ConfigIssue(
                    severity="warning",
                    path="agent.workspace",
                    message=f"Workspace directory does not exist: {workspace}",
                    fix_hint="Create the directory or update the path"
                ))

        sandbox = agent.get("sandboxMode")
        if sandbox and sandbox not in ["strict", "relaxed", "off"]:
            issues.append(ConfigIssue(
                severity="error",
                path="agent.sandboxMode",
                message=f"Invalid sandbox mode: {sandbox}",
                fix_hint="Must be 'strict', 'relaxed', or 'off'"
            ))

        return issues

    def _check_skills(self, config: dict) -> list[ConfigIssue]:
        """Validate skills configuration."""
        issues = []
        skills = config.get("skills", {})
        if not isinstance(skills, dict):
            issues.append(ConfigIssue(
                severity="error", path="skills",
                message="Skills configuration must be an object",
                fix_hint="Use {} for skills section"
            ))
        return issues

    def _check_plugins(self, config: dict) -> list[ConfigIssue]:
        """Validate plugins configuration."""
        issues = []
        plugins = config.get("plugins", [])
        if not isinstance(plugins, list):
            issues.append(ConfigIssue(
                severity="error", path="plugins",
                message="Plugins configuration must be an array",
                fix_hint="Use [] for plugins section"
            ))
        return issues

    def detect_channels(self) -> list[str]:
        """Detect enabled channel names."""
        channels = self.config.get("channels", {})
        return [name for name, cfg in channels.items() if cfg.get("enabled", False)]

    def detect_model(self) -> str | None:
        """Get configured AI model name."""
        return self.config.get("agent", {}).get("model")

    def get_config_path(self, path: str):
        """Access config value using dot-notation path."""
        from .config_security_checks import get_config_path
        return get_config_path(self.config, path)
