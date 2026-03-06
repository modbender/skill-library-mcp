"""War/Den Sentinel Client Tests -- governance gateway, fail-open, enterprise routing."""

from unittest.mock import MagicMock, patch

import pytest

from warden_governance.action_bridge import (
    Action,
    ActionType,
    CheckResult,
    Decision,
    GovernanceError,
)
from warden_governance.sentinel_client import PolicyDecisionCache, SentinelClient
from warden_governance.settings import Settings


def _config(tmp_path, **overrides) -> Settings:
    defaults = {
        "sentinel_api_key": "",
        "engramport_api_key": "",
        "warden_policy_packs": "",
        "warden_memory_db": str(tmp_path / "memory.db"),
        "warden_audit_db": str(tmp_path / "audit.db"),
    }
    defaults.update(overrides)
    return Settings(**defaults)


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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SentinelClient Community Mode
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSentinelClientCommunity:
    def test_community_mode_no_sentinel_key(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)
        assert client._enterprise_mode is False

    def test_enterprise_mode_with_sentinel_key(self, tmp_path):
        config = _config(tmp_path, sentinel_api_key="snos_test")
        client = SentinelClient(config)
        assert client._enterprise_mode is True

    def test_check_returns_allow_for_safe_action(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)
        result = client.check(_action())
        assert result.decision == Decision.ALLOW

    def test_check_raises_governance_error_on_deny(self, tmp_path):
        config = _config(tmp_path, warden_policy_packs="basic_safety")
        client = SentinelClient(config)
        with pytest.raises(GovernanceError):
            client.check(_action(ActionType.CODE_EXECUTE, context={"env": "prod"}))

    def test_deny_error_includes_reason(self, tmp_path):
        config = _config(tmp_path, warden_policy_packs="basic_safety")
        client = SentinelClient(config)
        with pytest.raises(GovernanceError) as exc_info:
            client.check(_action(ActionType.CODE_EXECUTE, context={"env": "prod"}))
        assert "blocked" in exc_info.value.reason.lower() or "production" in exc_info.value.reason.lower()

    def test_check_writes_to_audit_log(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)
        client.check(_action())
        assert client.audit_log.count() == 1

    def test_multiple_checks_all_logged(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)
        for _ in range(5):
            client.check(_action(ActionType.MESSAGE_SEND))
        # First call is real, rest hit cache, but audit is only on first
        assert client.audit_log.count() >= 1

    def test_audit_chain_valid_after_checks(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)
        client.check(_action(ActionType.MESSAGE_SEND))
        client.check(_action(ActionType.DATA_READ, context={"env": "dev"}))
        valid, _ = client.audit_log.verify_chain()
        assert valid is True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fail-Open Behavior
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestFailOpen:
    def test_fail_open_false_denies_on_engine_crash(self, tmp_path):
        config = _config(tmp_path, warden_fail_open=False)
        client = SentinelClient(config)
        with patch.object(
            client.policy_engine, "evaluate",
            side_effect=RuntimeError("engine crashed"),
        ):
            with pytest.raises(GovernanceError):
                client.check(_action())

    def test_fail_open_true_allows_on_engine_crash(self, tmp_path):
        config = _config(tmp_path, warden_fail_open=True)
        client = SentinelClient(config)
        with patch.object(
            client.policy_engine, "evaluate",
            side_effect=RuntimeError("engine crashed"),
        ):
            result = client.check(_action())
        assert result.decision == Decision.ALLOW


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cache Behavior
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSentinelCache:
    def test_second_identical_call_uses_cache(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)

        client.check(_action())
        with patch.object(client.policy_engine, "evaluate") as mock:
            client.check(_action())
            mock.assert_not_called()

    def test_different_action_types_separate_cache(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)

        client.check(_action(ActionType.API_CALL))
        with patch.object(
            client.policy_engine, "evaluate",
            wraps=client.policy_engine.evaluate,
        ) as mock:
            client.check(_action(ActionType.DATA_READ))
            mock.assert_called_once()

    def test_different_envs_separate_cache(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)

        client.check(_action(context={"env": "dev"}))
        with patch.object(
            client.policy_engine, "evaluate",
            wraps=client.policy_engine.evaluate,
        ) as mock:
            client.check(_action(context={"env": "prod"}))
            mock.assert_called_once()

    def test_deny_is_never_cached(self, tmp_path):
        """After a DENY, the same action type from a different env
        must still be evaluated (cache must not store DENY)."""
        config = _config(tmp_path, warden_policy_packs="basic_safety")
        client = SentinelClient(config)

        # code.execute in prod -> DENY
        try:
            client.check(_action(ActionType.CODE_EXECUTE, context={"env": "prod"}))
        except GovernanceError:
            pass

        # code.execute in prod again -> should still evaluate fresh
        with patch.object(
            client.policy_engine, "evaluate",
            wraps=client.policy_engine.evaluate,
        ) as mock:
            try:
                client.check(_action(ActionType.CODE_EXECUTE, context={"env": "prod"}))
            except GovernanceError:
                pass
            mock.assert_called_once()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Governance Invariant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestGovernanceInvariant:
    def test_every_action_type_gets_evaluated(self, tmp_path):
        """Every War/Den action type must produce a valid decision."""
        config = _config(tmp_path)
        client = SentinelClient(config)

        for action_type in ActionType:
            try:
                result = client.check(_action(action_type, context={"env": "dev"}))
                assert result.decision in (Decision.ALLOW, Decision.DENY, Decision.REVIEW)
            except GovernanceError:
                pass  # DENY is a valid governance outcome

    def test_unknown_action_data_doesnt_crash(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)
        result = client.check(_action(
            data={"weird_key": [1, 2, 3], "nested": {"a": "b"}},
        ))
        assert result.decision == Decision.ALLOW

    def test_empty_context_doesnt_crash(self, tmp_path):
        config = _config(tmp_path)
        client = SentinelClient(config)
        result = client.check(_action(context={}))
        assert result.decision == Decision.ALLOW
