"""Recovery automation skill integration hooks for OpenClaw Doctor Pro."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from .utils import DATA_DIR, load_json, save_json


HISTORY_FILE = DATA_DIR / "fix-execution-history.json"
MIN_ATTEMPTS_FOR_EVOLVER = 5
SUCCESS_RATE_THRESHOLD = 0.8
MULTI_STEP_THRESHOLD = 3
MULTI_CHANNEL_THRESHOLD = 2


@dataclass
class RecoverySuggestion:
    """Suggestion for recovery automation skill."""
    skill_slug: str
    skill_name: str
    priority: str
    reason: str
    benefit: str
    install_command: str


class RecoveryIntegrations:
    """Manages recovery automation skill integrations."""

    def __init__(self):
        """Initialize recovery integrations."""
        self.hooks = self._load_hooks()
        self.history = self._load_history()

    def _load_hooks(self) -> dict:
        """Load integration hooks configuration."""
        hooks_file = DATA_DIR / "integration-hooks.json"
        data = load_json(hooks_file) if hooks_file.exists() else {}
        return data.get("hooks", {}).get("recovery_automation", {})

    def _load_history(self) -> dict:
        """Load fix execution history."""
        if HISTORY_FILE.exists():
            return load_json(HISTORY_FILE)
        return {"executions": [], "success_rates": {}}

    def _save_history(self) -> None:
        """Save fix execution history."""
        save_json(HISTORY_FILE, self.history)

    def track_execution(
        self,
        recipe_id: str,
        success: bool,
        metadata: dict
    ) -> None:
        """Track fix execution for evolver analysis.

        Args:
            recipe_id: Fix recipe ID
            success: Whether fix succeeded
            metadata: Additional execution metadata
        """
        execution = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "recipe_id": recipe_id,
            "success": success,
            **metadata
        }

        self.history["executions"].append(execution)
        self._update_success_rates(recipe_id, success)
        self._save_history()

    def _update_success_rates(self, recipe_id: str, success: bool) -> None:
        """Update success rate for recipe."""
        rates = self.history.get("success_rates", {})

        if recipe_id not in rates:
            rates[recipe_id] = {"total": 0, "success": 0, "rate": 0.0}

        rates[recipe_id]["total"] += 1
        if success:
            rates[recipe_id]["success"] += 1

        total = rates[recipe_id]["total"]
        successes = rates[recipe_id]["success"]
        rates[recipe_id]["rate"] = successes / total if total > 0 else 0.0

        self.history["success_rates"] = rates

    def calculate_success_rate(self, recipe_id: str) -> float:
        """Calculate success rate from history.

        Args:
            recipe_id: Fix recipe ID

        Returns:
            Success rate (0.0 to 1.0)
        """
        rates = self.history.get("success_rates", {})
        if recipe_id in rates:
            return rates[recipe_id]["rate"]
        return 1.0

    def check_triggers(self, fix_context: dict) -> list[RecoverySuggestion]:
        """Check all recovery triggers and return suggestions.

        Args:
            fix_context: Context about fix execution

        Returns:
            List of recovery skill suggestions
        """
        suggestions = []

        evolver = self._check_evolver(fix_context)
        if evolver:
            suggestions.append(evolver)

        workflow = self._check_workflow_builder(fix_context)
        if workflow:
            suggestions.append(workflow)

        multi_agent = self._check_multi_agent(fix_context)
        if multi_agent:
            suggestions.append(multi_agent)

        return suggestions

    def _check_evolver(self, context: dict) -> RecoverySuggestion | None:
        """Check if evolver should be suggested."""
        recipe_id = context.get("recipe_id")
        if not recipe_id:
            return None

        rates = self.history.get("success_rates", {})
        if recipe_id not in rates:
            return None

        stats = rates[recipe_id]
        if stats["total"] < MIN_ATTEMPTS_FOR_EVOLVER:
            return None

        if stats["rate"] >= SUCCESS_RATE_THRESHOLD:
            return None

        hook_config = self.hooks.get("evolver", {})
        return RecoverySuggestion(
            skill_slug="evolver",
            skill_name="evolver",
            priority=hook_config.get("priority", "HIGH"),
            reason=f"Fix success rate is {stats['rate']:.0%} ({stats['success']}/{stats['total']})",
            benefit="Auto-refine recipes based on outcomes",
            install_command=hook_config.get("install_command", "openclaw skills install evolver")
        )

    def _check_workflow_builder(self, context: dict) -> RecoverySuggestion | None:
        """Check if workflow-builder should be suggested."""
        steps_count = context.get("steps_executed", 0)
        manual_steps = context.get("needs_manual_count", 0)

        total_steps = steps_count + manual_steps
        if total_steps < MULTI_STEP_THRESHOLD:
            return None

        hook_config = self.hooks.get("workflow-builder", {})
        return RecoverySuggestion(
            skill_slug="workflow-builder",
            skill_name="workflow-builder",
            priority=hook_config.get("priority", "HIGH"),
            reason=f"Fix requires {total_steps} manual steps",
            benefit="Create reusable automated workflows",
            install_command=hook_config.get("install_command", "openclaw skills install workflow-builder")
        )

    def _check_multi_agent(self, context: dict) -> RecoverySuggestion | None:
        """Check if multi-agent should be suggested."""
        config_context = context.get("config_context", {})
        channels = config_context.get("channels_enabled", [])

        if len(channels) < MULTI_CHANNEL_THRESHOLD:
            return None

        hook_config = self.hooks.get("multi-agent", {})
        return RecoverySuggestion(
            skill_slug="multi-agent",
            skill_name="multi-agent",
            priority=hook_config.get("priority", "HIGH"),
            reason=f"Config has {len(channels)} channels enabled",
            benefit="Run multiple diagnostics simultaneously",
            install_command=hook_config.get("install_command", "openclaw skills install multi-agent")
        )
