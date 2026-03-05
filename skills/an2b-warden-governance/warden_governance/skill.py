"""War/Den Governance Skill for OpenClaw -- the main entry point.

This is the OpenClaw skill class that registers three hooks:
- before_action: evaluate every action against policy before execution
- after_action:  write action result to governed memory
- on_error:      log errors to tamper-evident audit trail

Install: openclaw skill install an2b/warden-governance
"""

from __future__ import annotations

import logging
from pathlib import Path

from warden_governance.action_bridge import (
    ActionBridge,
    Decision,
    GovernanceError,
)
from warden_governance.memory_client import MemoryClient
from warden_governance.sentinel_client import SentinelClient
from warden_governance.settings import Settings
from warden_governance.upgrade_manager import UpgradeManager

logger = logging.getLogger("warden")

OPENCLAW_SKILLS_DIR = Path.home() / ".openclaw" / "skills"
OPENCLAW_MEMORY_DIR = Path.home() / ".openclaw" / "memory"
SKILL_INSTALL_DIR = OPENCLAW_SKILLS_DIR / "warden-governance"

# Default policy file shipped with this skill
_DEFAULT_POLICY_FILE = str(
    Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
)


class WardenGovernanceSkill:
    """OpenClaw skill class: governance for every bot action.

    Usage in openclaw config:
        skills:
          - name: warden-governance
            config:
              SENTINEL_API_KEY: ""       # blank = community mode
              ENGRAMPORT_API_KEY: ""     # blank = local memory
              WARDEN_FAIL_OPEN: "false"  # block on governance failure
    """

    def __init__(self, config: dict):
        self.settings = Settings.from_config(config)

        # If no custom policy file, use the built-in defaults
        if not self.settings.warden_policy_file:
            default_path = _DEFAULT_POLICY_FILE
            if Path(default_path).exists():
                self.settings.warden_policy_file = default_path

        # Initialize components via upgrade manager
        upgrade = UpgradeManager(self.settings)
        components = upgrade.initialize()

        self.sentinel: SentinelClient = components["sentinel"]
        self.memory: MemoryClient = components["memory"]
        self.mode: dict = components["mode"]
        self.bridge = ActionBridge()

        # Print banner
        upgrade.print_mode_banner()

    def before_action(self, action: dict, context: dict) -> dict:
        """Hook: evaluate an OpenClaw action before execution.

        Returns:
            {"proceed": True} if allowed.
            {"proceed": False, "reason": "...", "blocked_by": "warden"} if denied.
            {"proceed": False, "review": True, ...} if needs review.
        """
        try:
            warden_action = self.bridge.translate(action, context)
            result = self.sentinel.check(warden_action)
            return self.bridge.translate_decision(result.decision, result.reason)
        except GovernanceError as exc:
            return self.bridge.translate_decision(Decision.DENY, exc.reason)
        except Exception as exc:
            if self.settings.warden_fail_open:
                logger.warning(
                    "War/Den error (fail-open): %s -- action allowed", exc
                )
                return {"proceed": True}
            logger.error("War/Den error (fail-closed): %s -- action blocked", exc)
            return {
                "proceed": False,
                "reason": f"War/Den governance error: {exc}",
                "blocked_by": "warden",
            }

    def after_action(self, action: dict, result: dict, context: dict) -> None:
        """Hook: write action result to governed memory."""
        try:
            self.memory.write(
                content=f"action={action.get('type')} status={result.get('status')}",
                namespace="openclaw_actions",
                metadata={
                    "action": action,
                    "result": result,
                    "context": context,
                },
            )
        except Exception as exc:
            logger.warning("War/Den after_action memory write failed: %s", exc)

    def on_error(self, action: dict, error: Exception) -> None:
        """Hook: log errors to governed memory and audit trail."""
        try:
            self.memory.write(
                content=f"error action={action.get('type')} error={error}",
                namespace="openclaw_errors",
                metadata={
                    "action": action,
                    "error": str(error),
                    "error_type": type(error).__name__,
                },
            )
        except Exception as exc:
            logger.warning("War/Den on_error logging failed: %s", exc)
