"""Notification and integration skill hooks for OpenClaw Doctor Pro."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .utils import DATA_DIR, load_json


@dataclass
class IntegrationSuggestion:
    """Suggestion for notification/integration skill."""
    skill_slug: str
    skill_name: str
    priority: str
    reason: str
    benefit: str
    install_command: str
    config_example: str | None = None


class NotificationHooks:
    """Manages notification and integration skill hooks."""

    def __init__(self):
        """Initialize notification hooks."""
        self.hooks = self._load_hooks()
        self.error_patterns = self._load_error_patterns()

    def _load_hooks(self) -> dict:
        """Load integration hooks configuration."""
        hooks_file = DATA_DIR / "integration-hooks.json"
        data = load_json(hooks_file) if hooks_file.exists() else {}
        return data.get("hooks", {}).get("notifications", {})

    def _load_error_patterns(self) -> dict:
        """Load known error patterns."""
        patterns_file = DATA_DIR / "error-patterns.json"
        return load_json(patterns_file) if patterns_file.exists() else {}

    def check_triggers(self, error_context: dict) -> list[IntegrationSuggestion]:
        """Check all notification triggers and return suggestions.

        Args:
            error_context: Context about error and fix attempt

        Returns:
            List of integration skill suggestions
        """
        suggestions = []

        github = self._check_github(error_context)
        if github:
            suggestions.append(github)

        slack = self._check_slack(error_context)
        if slack:
            suggestions.append(slack)

        discord = self._check_discord(error_context)
        if discord:
            suggestions.append(discord)

        return suggestions

    def _check_github(self, context: dict) -> IntegrationSuggestion | None:
        """Check if github integration should be suggested."""
        unresolved = context.get("unresolved", False)
        new_pattern = self._is_new_error_pattern(context)

        if not (unresolved or new_pattern):
            return None

        hook_config = self.hooks.get("github", {})
        reason = "Unresolved error pattern detected" if unresolved else "New error pattern detected"

        return IntegrationSuggestion(
            skill_slug="github",
            skill_name="github",
            priority=hook_config.get("priority", "HIGH"),
            reason=reason,
            benefit="Auto-report bugs to OpenClaw repo",
            install_command=hook_config.get("install_command", "openclaw skills install github"),
            config_example="Set GITHUB_TOKEN in .env"
        )

    def _check_slack(self, context: dict) -> IntegrationSuggestion | None:
        """Check if slack integration should be suggested."""
        critical = context.get("critical_error", False)
        team_env = self._detect_team_env()

        if not (critical and team_env):
            return None

        hook_config = self.hooks.get("slack-integration", {})

        return IntegrationSuggestion(
            skill_slug="slack-integration",
            skill_name="slack-integration",
            priority=hook_config.get("priority", "HIGH"),
            reason="Critical error in team environment",
            benefit="Alert team immediately",
            install_command=hook_config.get("install_command", "openclaw skills install slack-integration"),
            config_example="Set SLACK_WEBHOOK_URL in .env"
        )

    def _check_discord(self, context: dict) -> IntegrationSuggestion | None:
        """Check if discord integration should be suggested."""
        suggestion_count = context.get("skill_suggestions_count", 0)
        unclear = context.get("resolution_unclear", False)

        if not (suggestion_count >= 3 or unclear):
            return None

        hook_config = self.hooks.get("discord-bot", {})

        return IntegrationSuggestion(
            skill_slug="discord-bot",
            skill_name="discord-bot",
            priority=hook_config.get("priority", "MEDIUM"),
            reason="Community help may be beneficial",
            benefit="Get help from OpenClaw community",
            install_command=hook_config.get("install_command", "openclaw skills install discord-bot"),
            config_example="Join OpenClaw Discord server"
        )

    def _is_new_error_pattern(self, context: dict) -> bool:
        """Detect if error is a new pattern."""
        error_code = context.get("error_code")
        if not error_code:
            return False

        patterns = self.error_patterns.get("patterns", [])
        return not any(p.get("code") == error_code for p in patterns)

    def _detect_team_env(self) -> bool:
        """Detect if running in team environment."""
        # Check for .git directory
        git_dir = Path.cwd() / ".git"
        if git_dir.exists():
            return True

        # Check CI environment variables
        ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI"]
        if any(os.getenv(var) for var in ci_vars):
            return True

        return False
