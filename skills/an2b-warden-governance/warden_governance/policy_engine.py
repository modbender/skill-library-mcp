"""War/Den Community Policy Engine -- real governance, zero cloud dependency.

Evaluation logic is identical to Sentinel_OS cloud.
Same input, same output. That's the consistency guarantee.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

from warden_governance.action_bridge import Action, CheckResult, Decision

logger = logging.getLogger("warden")


class PolicyValidationError(Exception):
    """Raised when a policy definition is invalid."""


# Pre-built policy packs
BASIC_SAFETY_PACK = [
    {
        "name": "block-code-execute-prod",
        "match": {"action.type": "code.execute", "context.env": "prod"},
        "decision": "deny",
        "mode": "enforce",
        "priority": 1,
        "active": True,
        "reason": "Code execution blocked in production",
    },
    {
        "name": "monitor-data-writes",
        "match": {"action.type": "data.write"},
        "decision": "allow",
        "mode": "monitor",
        "priority": 10,
        "active": True,
        "reason": "Data write monitored",
    },
    {
        "name": "monitor-api-calls",
        "match": {"action.type": "api.call"},
        "decision": "allow",
        "mode": "monitor",
        "priority": 10,
        "active": True,
        "reason": "API call monitored",
    },
]

PHI_GUARD_PACK = [
    {
        "name": "deny-phi-read-dev",
        "match": {
            "action.type": "memory.read",
            "context.data_class": "PHI",
            "context.env": "dev",
        },
        "decision": "deny",
        "mode": "enforce",
        "priority": 1,
        "active": True,
        "reason": "PHI access denied in dev environment",
    },
    {
        "name": "review-memory-export",
        "match": {"action.type": "memory.export"},
        "decision": "review",
        "mode": "enforce",
        "priority": 5,
        "active": True,
        "reason": "Memory export requires human review",
    },
    {
        "name": "monitor-phi-api-calls",
        "match": {"action.type": "api.call", "context.data_class": "PHI"},
        "decision": "allow",
        "mode": "monitor",
        "priority": 10,
        "active": True,
        "reason": "PHI API call monitored",
    },
]

PAYMENTS_GUARD_PACK = [
    {
        "name": "deny-payments-dev",
        "match": {
            "action.type": "api.call",
            "context.service": "payments",
            "context.env": "dev",
        },
        "decision": "deny",
        "mode": "enforce",
        "priority": 1,
        "active": True,
        "reason": "Payment actions denied in dev environment",
    },
    {
        "name": "review-large-payments",
        "match": {"action.type": "api.call", "context.service": "payments"},
        "decision": "review",
        "mode": "enforce",
        "priority": 5,
        "active": True,
        "reason": "Payment actions require human review",
    },
    {
        "name": "monitor-financial-api",
        "match": {"action.type": "api.call", "context.service": "financial"},
        "decision": "allow",
        "mode": "monitor",
        "priority": 10,
        "active": True,
        "reason": "Financial API call monitored",
    },
]

PACKS: dict[str, list[dict]] = {
    "basic_safety": BASIC_SAFETY_PACK,
    "phi_guard": PHI_GUARD_PACK,
    "payments_guard": PAYMENTS_GUARD_PACK,
}


class CommunityPolicyEngine:
    """Local policy evaluation engine.

    Algorithm:
    1. Filter to active policies only
    2. Sort by priority ascending (lower = higher priority)
    3. For each policy, check if action matches ALL conditions
    4. First match wins
    5. If mode=monitor: log but return ALLOW
    6. If mode=enforce: return the decision
    7. If no match: default ALLOW
    """

    REQUIRED_FIELDS = {"name", "match", "decision", "mode", "priority", "active"}

    def __init__(self, policy_file: str | None = None):
        self.policies: list[dict] = []

        if policy_file and os.path.exists(policy_file):
            self.load_file(policy_file)

    def load_file(self, path: str) -> None:
        """Load policies from a YAML file."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise PolicyValidationError(f"Invalid YAML in {path}: {exc}")

        if not data or "policies" not in data:
            raise PolicyValidationError(
                f"Policy file {path} must contain a 'policies' key"
            )

        for policy in data["policies"]:
            self._validate_policy(policy)

        self.policies.extend(data["policies"])
        self._sort_policies()

    def load_pack(self, pack_name: str) -> None:
        """Load a pre-built policy pack by name."""
        if pack_name not in PACKS:
            raise PolicyValidationError(
                f"Unknown policy pack: {pack_name}. "
                f"Available: {', '.join(PACKS.keys())}"
            )

        for policy in PACKS[pack_name]:
            self._validate_policy(policy)

        self.policies.extend(PACKS[pack_name])
        self._sort_policies()

    def add_policy(self, policy: dict) -> None:
        """Add a single policy at runtime."""
        self._validate_policy(policy)
        self.policies.append(policy)
        self._sort_policies()

    def evaluate(self, action: Action) -> CheckResult:
        """Evaluate an action against loaded policies."""
        action_dict = self._action_to_flat_dict(action)
        active_policies = [p for p in self.policies if p.get("active", True)]

        for policy in active_policies:
            if self._matches(policy["match"], action_dict):
                decision_str = policy["decision"]
                mode = policy["mode"]
                reason = policy.get("reason", f"matched policy: {policy['name']}")

                if mode == "monitor":
                    logger.info(
                        "[WARDEN POLICY] MONITOR policy=%s action=%s "
                        "(would be %s in enforce mode)",
                        policy["name"],
                        action.type.value,
                        decision_str.upper(),
                    )
                    return CheckResult(
                        decision=Decision.ALLOW,
                        reason=f"monitor: {reason}",
                        policy_id=policy["name"],
                    )

                decision = Decision(decision_str)
                return CheckResult(
                    decision=decision,
                    reason=reason,
                    policy_id=policy["name"],
                )

        return CheckResult(
            decision=Decision.ALLOW,
            reason="no policy matched -- default allow",
            policy_id=None,
        )

    def _action_to_flat_dict(self, action: Action) -> dict[str, Any]:
        """Convert an Action to a flat dict for dot-path matching."""
        flat: dict[str, Any] = {}
        flat["action.type"] = action.type.value
        for k, v in action.data.items():
            flat[f"action.data.{k}"] = v
        for k, v in action.context.items():
            flat[f"context.{k}"] = v
        flat["agent_id"] = action.agent_id
        return flat

    def _matches(self, match_conditions: dict, action_dict: dict) -> bool:
        """Check if ALL conditions in a policy match the action."""
        for dot_path, expected in match_conditions.items():
            actual = action_dict.get(dot_path)
            if actual != expected:
                return False
        return True

    def _validate_policy(self, policy: dict) -> None:
        """Validate a policy dict has all required fields."""
        missing = self.REQUIRED_FIELDS - set(policy.keys())
        if missing:
            raise PolicyValidationError(
                f"Policy '{policy.get('name', '<unnamed>')}' missing fields: "
                f"{', '.join(sorted(missing))}"
            )
        if policy["decision"] not in ("allow", "deny", "review"):
            raise PolicyValidationError(
                f"Policy '{policy['name']}' has invalid decision: {policy['decision']}. "
                "Must be allow, deny, or review."
            )
        if policy["mode"] not in ("enforce", "monitor"):
            raise PolicyValidationError(
                f"Policy '{policy['name']}' has invalid mode: {policy['mode']}. "
                "Must be enforce or monitor."
            )

    def _sort_policies(self) -> None:
        """Sort policies by priority ascending (lower number = higher priority)."""
        self.policies.sort(key=lambda p: p.get("priority", 999))
