"""Fix execution tracking and error context building."""
from __future__ import annotations

import time


def build_error_context(
    recipe_id: str,
    success: bool,
    actions_taken: list[str],
    needs_manual: list[str],
    metadata: dict
) -> dict:
    """Build error context dict for trigger checking.

    Args:
        recipe_id: Recipe ID that was executed
        success: Whether execution succeeded
        actions_taken: List of action descriptions
        needs_manual: List of manual steps needed
        metadata: Execution metadata

    Returns:
        Context dict with trigger flags
    """
    return {
        "recipe_id": recipe_id,
        "auto_fix_failed": not success,
        "manual_intervention_needed": len(needs_manual) > 0,
        "complex_stack_trace": False,
        "sandbox_error": "sandbox" in recipe_id.lower(),
        "container_timeout": "timeout" in recipe_id.lower(),
        "repeated_error": False,
        "learning_opportunity": not success,
        "fix_applied": success,
        "multi_step_fix_needed": len(actions_taken) > 3,
        "critical_error": not success and "critical" in recipe_id.lower(),
        "unresolved_error": not success,
        "steps_executed": metadata.get("steps_executed", 0),
        "needs_manual_count": metadata.get("needs_manual_count", 0),
        "config_context": metadata.get("config_context", {})
    }


def build_execution_metadata(
    start_time: float,
    actions_taken: list[str],
    needs_manual: list[str],
    params: dict
) -> dict:
    """Build execution metadata dict.

    Args:
        start_time: Execution start timestamp
        actions_taken: List of action descriptions
        needs_manual: List of manual steps
        params: Execution parameters

    Returns:
        Metadata dict
    """
    duration_ms = int((time.time() - start_time) * 1000)
    return {
        "duration_ms": duration_ms,
        "steps_executed": len(actions_taken),
        "needs_manual_count": len(needs_manual),
        "execution_mode": (
            "dry_run" if "[DRY RUN]" in str(actions_taken) else "auto"
        ),
        "config_context": params.get("config_context", {})
    }
