"""Auto-fix execution engine for OpenClaw diagnostics."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .utils import DATA_DIR, load_json
from .fix_step_executor import execute_step
from .fix_execution_tracker import build_error_context, build_execution_metadata
from .diagnostic_integrations import DiagnosticIntegrations, DiagnosticSuggestion
from .recovery_integrations import RecoveryIntegrations, RecoverySuggestion


@dataclass
class FixRecipe:
    """Structured fix recipe with execution metadata."""
    id: str
    title: str
    safe_auto: bool
    description: str
    steps: list[dict]
    rollback: str | None
    requires_restart: bool


@dataclass
class FixResult:
    """Result of fix execution."""
    recipe_id: str
    success: bool
    message: str
    actions_taken: list[str]
    needs_manual: list[str]
    diagnostic_suggestions: list[DiagnosticSuggestion] = field(default_factory=list)
    recovery_suggestions: list[RecoverySuggestion] = field(default_factory=list)
    execution_metadata: dict = field(default_factory=dict)


class FixEngine:
    """Engine for executing automated fixes."""

    def __init__(self):
        """Initialize and load fix recipes from JSON."""
        self.recipes: dict[str, FixRecipe] = {}
        self.diag_integrations = DiagnosticIntegrations()
        self.recovery_integrations = RecoveryIntegrations()
        self._load_recipes()

    def _load_recipes(self) -> None:
        """Load fix recipes from data/fix-recipes.json."""
        data = load_json(DATA_DIR / "fix-recipes.json")
        if data:
            self.recipes = self._parse_recipes(data)

    def _parse_recipes(self, data: dict) -> dict[str, FixRecipe]:
        """Convert JSON data to FixRecipe instances."""
        recipes = {}
        for item in data.get("recipes", []):
            try:
                recipe = FixRecipe(
                    id=item.get("id", ""),
                    title=item.get("title", ""),
                    safe_auto=item.get("safe_auto", False),
                    description=item.get("description", ""),
                    steps=item.get("steps", []),
                    rollback=item.get("rollback"),
                    requires_restart=item.get("requires_restart", False)
                )
                recipes[recipe.id] = recipe
            except (KeyError, TypeError):
                continue
        return recipes

    def get_recipe(self, recipe_id: str) -> FixRecipe | None:
        """Get recipe by ID."""
        return self.recipes.get(recipe_id)

    def can_auto_fix(self, recipe_id: str) -> bool:
        """Check if recipe is safe for auto-execution."""
        recipe = self.get_recipe(recipe_id)
        return recipe.safe_auto if recipe else False

    def execute(
        self,
        recipe_id: str,
        dry_run: bool = False,
        params: dict | None = None
    ) -> FixResult:
        """Execute fix recipe.

        Args:
            recipe_id: Recipe ID to execute
            dry_run: If True, only describe actions without executing
            params: Parameter substitution dict

        Returns:
            FixResult with execution details
        """
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return FixResult(
                recipe_id=recipe_id, success=False,
                message=f"Recipe not found: {recipe_id}",
                actions_taken=[], needs_manual=[]
            )

        if params is None:
            params = {}

        # Track execution timing
        start_time = time.time()
        actions = []
        needs_manual = []
        steps_failed = 0

        for i, step in enumerate(recipe.steps, start=1):
            success, message = execute_step(step, dry_run, params)

            prefix = "[DRY RUN] " if dry_run else ""
            actions.append(f"{prefix}Step {i}: {message}")

            if not success:
                steps_failed += 1
                if not dry_run:
                    result = FixResult(
                        recipe_id=recipe_id, success=False,
                        message=f"Failed at step {i}: {message}",
                        actions_taken=actions, needs_manual=needs_manual
                    )
                    self._track_execution(recipe_id, result, start_time, params)
                    return result

        result = FixResult(
            recipe_id=recipe_id, success=True,
            message=f"Successfully executed {recipe.title}",
            actions_taken=actions, needs_manual=needs_manual
        )

        # Track execution and check triggers
        self._track_execution(recipe_id, result, start_time, params)

        return result

    def list_safe_recipes(self) -> list[FixRecipe]:
        """Get all recipes with safe_auto=True."""
        return [r for r in self.recipes.values() if r.safe_auto]

    def list_all_recipes(self) -> list[FixRecipe]:
        """Get all recipes."""
        return list(self.recipes.values())

    def _track_execution(
        self,
        recipe_id: str,
        result: FixResult,
        start_time: float,
        params: dict
    ) -> None:
        """Track execution and check integration triggers."""
        metadata = build_execution_metadata(
            start_time, result.actions_taken, result.needs_manual, params
        )
        result.execution_metadata = metadata

        # Track for evolver
        self.recovery_integrations.track_execution(
            recipe_id, result.success, metadata
        )

        # Build context and check triggers
        error_context = build_error_context(
            recipe_id, result.success,
            result.actions_taken, result.needs_manual, metadata
        )
        result.diagnostic_suggestions = self.diag_integrations.check_triggers(
            error_context
        )
        result.recovery_suggestions = self.recovery_integrations.check_triggers(
            error_context
        )
