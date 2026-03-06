"""War/Den Policy Engine Tests -- community governance correctness."""

import os
from pathlib import Path

import pytest

from warden_governance.action_bridge import Action, ActionType, CheckResult, Decision
from warden_governance.policy_engine import (
    CommunityPolicyEngine,
    PACKS,
    PolicyValidationError,
)


def _action(
    action_type: ActionType = ActionType.API_CALL,
    data: dict | None = None,
    context: dict | None = None,
    agent_id: str = "test-bot",
) -> Action:
    return Action(
        type=action_type,
        data=data or {},
        context=context or {},
        agent_id=agent_id,
    )


class TestPolicyEngineEvaluation:
    def test_no_policies_defaults_to_allow(self):
        engine = CommunityPolicyEngine()
        result = engine.evaluate(_action())
        assert result.decision == Decision.ALLOW

    def test_enforce_deny_returns_deny(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "block-all-code",
            "match": {"action.type": "code.execute"},
            "decision": "deny",
            "mode": "enforce",
            "priority": 1,
            "active": True,
            "reason": "no code",
        })
        result = engine.evaluate(_action(ActionType.CODE_EXECUTE))
        assert result.decision == Decision.DENY

    def test_enforce_review_returns_review(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "review-writes",
            "match": {"action.type": "data.write"},
            "decision": "review",
            "mode": "enforce",
            "priority": 1,
            "active": True,
            "reason": "review needed",
        })
        result = engine.evaluate(_action(ActionType.DATA_WRITE))
        assert result.decision == Decision.REVIEW

    def test_monitor_mode_returns_allow(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "monitor-api",
            "match": {"action.type": "api.call"},
            "decision": "deny",
            "mode": "monitor",
            "priority": 1,
            "active": True,
            "reason": "monitored",
        })
        result = engine.evaluate(_action(ActionType.API_CALL))
        assert result.decision == Decision.ALLOW

    def test_inactive_policy_is_skipped(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "block-code",
            "match": {"action.type": "code.execute"},
            "decision": "deny",
            "mode": "enforce",
            "priority": 1,
            "active": False,
            "reason": "no code",
        })
        result = engine.evaluate(_action(ActionType.CODE_EXECUTE))
        assert result.decision == Decision.ALLOW

    def test_first_match_wins(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "allow-api",
            "match": {"action.type": "api.call"},
            "decision": "allow",
            "mode": "enforce",
            "priority": 1,
            "active": True,
            "reason": "allowed",
        })
        engine.add_policy({
            "name": "deny-api",
            "match": {"action.type": "api.call"},
            "decision": "deny",
            "mode": "enforce",
            "priority": 2,
            "active": True,
            "reason": "denied",
        })
        result = engine.evaluate(_action(ActionType.API_CALL))
        assert result.decision == Decision.ALLOW

    def test_lower_priority_wins(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "deny-late",
            "match": {"action.type": "api.call"},
            "decision": "deny",
            "mode": "enforce",
            "priority": 10,
            "active": True,
            "reason": "denied",
        })
        engine.add_policy({
            "name": "allow-early",
            "match": {"action.type": "api.call"},
            "decision": "allow",
            "mode": "enforce",
            "priority": 1,
            "active": True,
            "reason": "allowed",
        })
        result = engine.evaluate(_action(ActionType.API_CALL))
        assert result.decision == Decision.ALLOW

    def test_dot_path_matching_on_data(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "block-email-delete",
            "match": {
                "action.type": "data.write",
                "action.data.openclaw_original": "email.delete",
            },
            "decision": "review",
            "mode": "enforce",
            "priority": 1,
            "active": True,
            "reason": "email delete needs review",
        })
        action = _action(
            ActionType.DATA_WRITE,
            data={"openclaw_original": "email.delete"},
        )
        result = engine.evaluate(action)
        assert result.decision == Decision.REVIEW

    def test_dot_path_matching_on_context(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "block-prod-code",
            "match": {"action.type": "code.execute", "context.env": "prod"},
            "decision": "deny",
            "mode": "enforce",
            "priority": 1,
            "active": True,
            "reason": "no code in prod",
        })
        # prod should match
        result = engine.evaluate(_action(ActionType.CODE_EXECUTE, context={"env": "prod"}))
        assert result.decision == Decision.DENY

        # dev should not match
        result = engine.evaluate(_action(ActionType.CODE_EXECUTE, context={"env": "dev"}))
        assert result.decision == Decision.ALLOW

    def test_partial_match_does_not_fire(self):
        engine = CommunityPolicyEngine()
        engine.add_policy({
            "name": "need-both",
            "match": {"action.type": "data.write", "context.env": "prod"},
            "decision": "deny",
            "mode": "enforce",
            "priority": 1,
            "active": True,
            "reason": "blocked",
        })
        # data.write in dev should NOT match
        result = engine.evaluate(_action(ActionType.DATA_WRITE, context={"env": "dev"}))
        assert result.decision == Decision.ALLOW


class TestPolicyValidation:
    def test_missing_required_field_raises(self):
        engine = CommunityPolicyEngine()
        with pytest.raises(PolicyValidationError, match="missing fields"):
            engine.add_policy({"name": "bad"})

    def test_invalid_decision_raises(self):
        engine = CommunityPolicyEngine()
        with pytest.raises(PolicyValidationError, match="invalid decision"):
            engine.add_policy({
                "name": "bad-decision",
                "match": {"action.type": "api.call"},
                "decision": "maybe",
                "mode": "enforce",
                "priority": 1,
                "active": True,
            })

    def test_invalid_mode_raises(self):
        engine = CommunityPolicyEngine()
        with pytest.raises(PolicyValidationError, match="invalid mode"):
            engine.add_policy({
                "name": "bad-mode",
                "match": {"action.type": "api.call"},
                "decision": "allow",
                "mode": "shadow",
                "priority": 1,
                "active": True,
            })


class TestPolicyPacks:
    def test_basic_safety_pack_loads(self):
        engine = CommunityPolicyEngine()
        engine.load_pack("basic_safety")
        assert len(engine.policies) >= 3

    def test_phi_guard_pack_loads(self):
        engine = CommunityPolicyEngine()
        engine.load_pack("phi_guard")
        assert len(engine.policies) >= 3

    def test_payments_guard_pack_loads(self):
        engine = CommunityPolicyEngine()
        engine.load_pack("payments_guard")
        assert len(engine.policies) >= 3

    def test_unknown_pack_raises(self):
        engine = CommunityPolicyEngine()
        with pytest.raises(PolicyValidationError, match="Unknown policy pack"):
            engine.load_pack("nonexistent")

    def test_basic_safety_blocks_code_in_prod(self):
        engine = CommunityPolicyEngine()
        engine.load_pack("basic_safety")
        result = engine.evaluate(
            _action(ActionType.CODE_EXECUTE, context={"env": "prod"})
        )
        assert result.decision == Decision.DENY

    def test_basic_safety_monitors_api_calls(self):
        engine = CommunityPolicyEngine()
        engine.load_pack("basic_safety")
        result = engine.evaluate(_action(ActionType.API_CALL))
        # monitor mode returns ALLOW
        assert result.decision == Decision.ALLOW


class TestPolicyFileLoading:
    def test_loads_openclaw_default_yaml(self):
        policy_path = str(
            Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
        )
        if not os.path.exists(policy_path):
            pytest.skip("Policy file not found")
        engine = CommunityPolicyEngine(policy_file=policy_path)
        assert len(engine.policies) >= 6

    def test_loaded_policies_block_email_delete(self):
        policy_path = str(
            Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
        )
        if not os.path.exists(policy_path):
            pytest.skip("Policy file not found")
        engine = CommunityPolicyEngine(policy_file=policy_path)
        result = engine.evaluate(
            _action(
                ActionType.DATA_WRITE,
                data={"openclaw_original": "email.delete"},
            )
        )
        assert result.decision == Decision.REVIEW
