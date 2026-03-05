"""Diagnostic enhancement integration hooks."""
from __future__ import annotations

from dataclasses import dataclass

from .utils import DATA_DIR, load_json


@dataclass
class DiagnosticSuggestion:
    """Diagnostic skill suggestion metadata."""
    skill_slug: str
    skill_name: str
    category: str
    priority: str
    reason: str
    install_command: str
    documentation_url: str | None = None


class DiagnosticIntegrations:
    """Hook points for diagnostic enhancement skills."""

    def __init__(self):
        """Initialize with integration hooks data."""
        self.hooks = self._load_hooks()

    def _load_hooks(self) -> dict:
        """Load integration hooks JSON."""
        path = DATA_DIR / "integration-hooks.json"
        data = load_json(path)
        return data.get("hooks", {}) if data else {}

    def check_triggers(
        self,
        error_context: dict
    ) -> list[DiagnosticSuggestion]:
        """
        Check all diagnostic triggers and return suggestions.

        Args:
            error_context: Error context with trigger flags

        Returns:
            List of diagnostic suggestions
        """
        suggestions = []

        # Check diagnostic enhancement hooks
        diag_hooks = self.hooks.get("diagnostic_enhancement", {})
        suggestions.extend(self._check_category(
            diag_hooks, error_context, "diagnostic_enhancement"
        ))

        # Check recovery automation hooks
        recovery_hooks = self.hooks.get("recovery_automation", {})
        suggestions.extend(self._check_category(
            recovery_hooks, error_context, "recovery_automation"
        ))

        # Check notification hooks
        notify_hooks = self.hooks.get("notifications", {})
        suggestions.extend(self._check_category(
            notify_hooks, error_context, "notifications"
        ))

        return suggestions

    def _check_category(
        self,
        hooks: dict,
        context: dict,
        category: str
    ) -> list[DiagnosticSuggestion]:
        """Check hooks in a category."""
        suggestions = []

        for skill_slug, hook_config in hooks.items():
            if not hook_config.get("enabled", False):
                # Only suggest if hook is enabled
                continue

            trigger_on = hook_config.get("trigger_on", [])
            if self._should_trigger(trigger_on, context):
                suggestions.append(self._create_suggestion(
                    skill_slug, hook_config, category, context
                ))

        return suggestions

    def _should_trigger(
        self,
        trigger_conditions: list[str],
        context: dict
    ) -> bool:
        """Check if any trigger condition is met."""
        for condition in trigger_conditions:
            if context.get(condition, False):
                return True
        return False

    def _create_suggestion(
        self,
        skill_slug: str,
        hook_config: dict,
        category: str,
        context: dict
    ) -> DiagnosticSuggestion:
        """Create diagnostic suggestion from hook config."""
        # Generate human-readable skill name
        skill_name = skill_slug.replace("-", " ").title()

        # Generate reason based on trigger
        trigger_on = hook_config.get("trigger_on", [])
        matched_triggers = [
            t for t in trigger_on if context.get(t, False)
        ]
        reason = hook_config.get("description", "")
        if matched_triggers:
            reason = f"{reason} (Triggered by: {', '.join(matched_triggers)})"

        return DiagnosticSuggestion(
            skill_slug=skill_slug,
            skill_name=skill_name,
            category=category,
            priority=hook_config.get("priority", "MEDIUM"),
            reason=reason,
            install_command=hook_config.get(
                "install_command",
                f"openclaw skills install {skill_slug}"
            )
        )

    def check_specific_skill(
        self,
        skill_slug: str,
        category: str,
        error_context: dict
    ) -> DiagnosticSuggestion | None:
        """Check if a specific skill should be suggested.

        Args:
            skill_slug: Skill to check (e.g. "debug-pro")
            category: Hook category (e.g. "diagnostic_enhancement")
            error_context: Error context dict

        Returns:
            Suggestion or None
        """
        hooks = self.hooks.get(category, {})
        hook = hooks.get(skill_slug, {})
        trigger_on = hook.get("trigger_on", [])
        if self._should_trigger(trigger_on, error_context):
            return self._create_suggestion(
                skill_slug, hook, category, error_context
            )
        return None
