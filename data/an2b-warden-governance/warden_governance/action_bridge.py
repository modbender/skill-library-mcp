"""War/Den Action Bridge -- maps OpenClaw action types to War/Den governance types.

Every OpenClaw action is translated to a War/Den Action before governance evaluation.
The bridge preserves all original OpenClaw data in metadata so nothing is lost.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ActionType(Enum):
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    MEMORY_DELETE = "memory.delete"
    MEMORY_SYNTHESIZE = "memory.synthesize"
    MESSAGE_SEND = "message.send"
    DATA_READ = "data.read"
    DATA_WRITE = "data.write"
    API_CALL = "api.call"
    CODE_EXECUTE = "code.execute"


class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


class GovernanceError(Exception):
    """Raised when governance denies an action."""

    def __init__(self, reason: str, policy_id: str | None = None):
        self.reason = reason
        self.policy_id = policy_id
        super().__init__(reason)


@dataclass
class Action:
    type: ActionType
    data: dict[str, Any]
    context: dict[str, Any]
    agent_id: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_sentinel_payload(self) -> dict:
        """Serialize to the Sentinel /api/v1/check request body."""
        return {
            "agentId": self.agent_id,
            "action": {
                "type": self.type.value,
                "data": self.data,
            },
            "context": self.context,
        }


@dataclass
class CheckResult:
    """Structured result from a governance check."""

    decision: Decision
    reason: str = ""
    policy_id: str | None = None
    check_id: str | None = None
    evaluated_at: str | None = None
    latency_ms: float = 0


# Complete mapping of all 15 OpenClaw action types to War/Den ActionTypes
OPENCLAW_TO_WARDEN: dict[str, ActionType] = {
    "email.send": ActionType.MESSAGE_SEND,
    "email.delete": ActionType.DATA_WRITE,
    "email.read": ActionType.DATA_READ,
    "file.write": ActionType.DATA_WRITE,
    "file.delete": ActionType.DATA_WRITE,
    "file.read": ActionType.DATA_READ,
    "browser.navigate": ActionType.API_CALL,
    "browser.click": ActionType.API_CALL,
    "shell.execute": ActionType.CODE_EXECUTE,
    "api.call": ActionType.API_CALL,
    "calendar.create": ActionType.DATA_WRITE,
    "calendar.delete": ActionType.DATA_WRITE,
    "message.send": ActionType.MESSAGE_SEND,
    "code.execute": ActionType.CODE_EXECUTE,
    "payment.create": ActionType.API_CALL,
}

# Actions that carry high inherent risk
HIGH_RISK_ACTIONS: set[str] = {
    "email.delete",
    "file.delete",
    "shell.execute",
    "code.execute",
    "payment.create",
    "calendar.delete",
}


class ActionBridge:
    """Translates OpenClaw actions to War/Den Actions and decisions back."""

    def translate(self, openclaw_action: dict, openclaw_context: dict) -> Action:
        """Map an OpenClaw action dict to a War/Den Action object."""
        oc_type = openclaw_action.get("type", "")
        warden_type = OPENCLAW_TO_WARDEN.get(oc_type, ActionType.API_CALL)

        data = dict(openclaw_action.get("data", {}))
        data["openclaw_original"] = oc_type

        context = dict(openclaw_context)
        if oc_type in HIGH_RISK_ACTIONS:
            context["risk"] = "high"

        agent_id = openclaw_context.get("agent_id", "openclaw-agent")

        return Action(
            type=warden_type,
            data=data,
            context=context,
            agent_id=agent_id,
        )

    def translate_decision(self, decision: Decision, reason: str) -> dict:
        """Map a War/Den governance decision back to OpenClaw response format."""
        if decision == Decision.ALLOW:
            return {"proceed": True}
        elif decision == Decision.DENY:
            return {
                "proceed": False,
                "reason": reason,
                "blocked_by": "warden",
            }
        elif decision == Decision.REVIEW:
            return {
                "proceed": False,
                "reason": reason,
                "review": True,
                "blocked_by": "warden",
            }
        return {"proceed": False, "reason": reason, "blocked_by": "warden"}
