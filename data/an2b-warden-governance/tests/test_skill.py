"""War/Den Skill Tests -- the Meta inbox can never happen again."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from warden_governance.action_bridge import (
    ActionBridge,
    ActionType,
    CheckResult,
    Decision,
    GovernanceError,
)
from warden_governance.sentinel_client import PolicyDecisionCache, SentinelClient
from warden_governance.skill import WardenGovernanceSkill


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _skill_config(tmp_path, **overrides) -> dict:
    """Build a minimal skill config dict for testing."""
    config = {
        "SENTINEL_API_KEY": "",
        "ENGRAMPORT_API_KEY": "",
        "WARDEN_FAIL_OPEN": "false",
        "WARDEN_AGENT_ID": "test-openclaw-agent",
        "WARDEN_MEMORY_DB": str(tmp_path / "memory.db"),
        "WARDEN_AUDIT_DB": str(tmp_path / "audit.db"),
        "WARDEN_POLICY_PACKS": "",
    }
    config.update(overrides)
    return config


def _make_skill(tmp_path, **overrides) -> WardenGovernanceSkill:
    """Create a WardenGovernanceSkill with test config."""
    return WardenGovernanceSkill(_skill_config(tmp_path, **overrides))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WardenGovernanceSkill Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestWardenGovernanceSkill:
    def test_before_action_allows_correctly(self, tmp_path):
        skill = _make_skill(tmp_path)
        result = skill.before_action(
            {"type": "email.read", "data": {"query": "inbox"}},
            {"agent_id": "bot-1", "env": "dev", "user": "u"},
        )
        assert result["proceed"] is True

    def test_before_action_blocks_deny(self, tmp_path):
        skill = _make_skill(tmp_path, WARDEN_POLICY_PACKS="basic_safety")
        result = skill.before_action(
            {"type": "shell.execute", "data": {"command": "rm -rf /"}},
            {"agent_id": "bot-1", "env": "prod", "user": "u"},
        )
        assert result["proceed"] is False
        assert "blocked" in result.get("reason", "").lower() or "blocked_by" in result

    def test_before_action_flags_review(self, tmp_path):
        skill = _make_skill(tmp_path)
        review_result = CheckResult(
            decision=Decision.REVIEW,
            reason="requires human review",
        )
        with patch.object(skill.sentinel, "check", return_value=review_result):
            result = skill.before_action(
                {"type": "email.delete", "data": {}},
                {"agent_id": "bot-1"},
            )
        assert result["proceed"] is False
        assert result.get("review") is True

    def test_after_action_writes_to_memory(self, tmp_path):
        skill = _make_skill(tmp_path)
        with patch.object(skill.memory, "write") as mock_write:
            skill.after_action(
                {"type": "email.read", "data": {}},
                {"status": "ok"},
                {"agent_id": "bot-1"},
            )
            mock_write.assert_called_once()
            call_kwargs = mock_write.call_args
            assert "openclaw_actions" in str(call_kwargs)

    def test_on_error_logs_to_audit(self, tmp_path):
        skill = _make_skill(tmp_path)
        with patch.object(skill.memory, "write") as mock_write:
            skill.on_error(
                {"type": "shell.execute", "data": {}},
                RuntimeError("something failed"),
            )
            mock_write.assert_called_once()
            call_kwargs = mock_write.call_args
            assert "openclaw_errors" in str(call_kwargs)

    def test_fail_open_false_blocks_on_warden_failure(self, tmp_path):
        skill = _make_skill(tmp_path, WARDEN_FAIL_OPEN="false")
        with patch.object(
            skill.sentinel, "check",
            side_effect=RuntimeError("governance engine crashed"),
        ):
            result = skill.before_action(
                {"type": "email.send", "data": {}},
                {"agent_id": "bot-1"},
            )
        assert result["proceed"] is False
        assert "warden" in result.get("blocked_by", "")

    def test_fail_open_true_allows_on_warden_failure(self, tmp_path):
        skill = _make_skill(tmp_path, WARDEN_FAIL_OPEN="true")
        with patch.object(
            skill.sentinel, "check",
            side_effect=RuntimeError("governance engine crashed"),
        ):
            result = skill.before_action(
                {"type": "email.read", "data": {}},
                {"agent_id": "bot-1"},
            )
        assert result["proceed"] is True

    def test_skill_initializes_community_mode(self, tmp_path):
        skill = _make_skill(tmp_path)
        assert skill.mode["mode"] == "full_community"
        assert skill.mode["governance"] == "community"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Protected Actions Tests (OpenClaw Default Policies)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestProtectedActions:
    def _make_policy_skill(self, tmp_path) -> WardenGovernanceSkill:
        policy_path = str(
            Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
        )
        return _make_skill(
            tmp_path,
            WARDEN_POLICY_FILE=policy_path,
            WARDEN_POLICY_PACKS="",
        )

    def test_email_delete_triggers_review(self, tmp_path):
        skill = self._make_policy_skill(tmp_path)
        result = skill.before_action(
            {"type": "email.delete", "data": {"subject": "Important meeting"}},
            {"agent_id": "bot-1", "env": "dev", "user": "researcher"},
        )
        assert result["proceed"] is False

    def test_shell_execute_in_prod_triggers_deny(self, tmp_path):
        skill = self._make_policy_skill(tmp_path)
        result = skill.before_action(
            {"type": "shell.execute", "data": {"command": "ls"}},
            {"agent_id": "bot-1", "env": "prod", "user": "u"},
        )
        assert result["proceed"] is False

    def test_file_delete_triggers_review(self, tmp_path):
        skill = self._make_policy_skill(tmp_path)
        result = skill.before_action(
            {"type": "file.delete", "data": {"path": "/tmp/notes.txt"}},
            {"agent_id": "bot-1", "env": "dev", "user": "u"},
        )
        assert result["proceed"] is False

    def test_payment_create_triggers_review(self, tmp_path):
        skill = self._make_policy_skill(tmp_path)
        result = skill.before_action(
            {"type": "payment.create", "data": {"amount": 100}},
            {"agent_id": "bot-1", "env": "dev", "user": "u"},
        )
        assert result["proceed"] is False

    def test_api_call_is_monitored_not_blocked(self, tmp_path):
        skill = self._make_policy_skill(tmp_path)
        result = skill.before_action(
            {"type": "api.call", "data": {"url": "https://example.com"}},
            {"agent_id": "bot-1", "env": "dev", "user": "u"},
        )
        assert result["proceed"] is True

    def test_email_read_is_not_blocked(self, tmp_path):
        skill = self._make_policy_skill(tmp_path)
        result = skill.before_action(
            {"type": "email.read", "data": {"query": "inbox"}},
            {"agent_id": "bot-1", "env": "dev", "user": "u"},
        )
        assert result["proceed"] is True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Integration Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestOpenClawIntegration:
    def test_full_action_flow_allow(self, tmp_path):
        skill = _make_skill(tmp_path)
        result = skill.before_action(
            {"type": "message.send", "data": {"text": "Hello!"}},
            {"agent_id": "bot-1", "env": "dev", "user": "u"},
        )
        assert result["proceed"] is True

    def test_full_action_flow_deny(self, tmp_path):
        skill = _make_skill(tmp_path, WARDEN_POLICY_PACKS="basic_safety")
        result = skill.before_action(
            {"type": "code.execute", "data": {"code": "import os; os.system('rm -rf /')"}},
            {"agent_id": "bot-1", "env": "prod", "user": "u"},
        )
        assert result["proceed"] is False

    def test_community_mode_works_with_no_keys(self, tmp_path):
        skill = _make_skill(tmp_path)
        assert skill.mode["governance"] == "community"
        assert skill.mode["memory"] == "community"
        result = skill.before_action(
            {"type": "email.read", "data": {}},
            {"agent_id": "bot-1", "env": "dev", "user": "u"},
        )
        assert result["proceed"] is True

    def test_audit_log_written_for_every_action(self, tmp_path):
        skill = _make_skill(tmp_path)
        with patch.object(skill.sentinel.audit_log, "write") as mock_audit:
            skill.before_action(
                {"type": "email.read", "data": {}},
                {"agent_id": "bot-1", "env": "dev", "user": "u"},
            )
            mock_audit.assert_called_once()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# The Meta Inbox Test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestMetaResearcherInboxProtection:
    def test_meta_researcher_inbox_protection(self, tmp_path):
        """Simulate the exact Meta inbox incident.

        A Meta AI security researcher asked her OpenClaw agent to triage her inbox.
        The agent deleted 200 emails despite being told to confirm first.

        With War/Den:
        1. Agent receives instruction to delete emails
        2. email.delete action fires
        3. War/Den intercepts via before_action
        4. OpenClaw default policy: email.delete -> REVIEW
        5. Email NOT deleted
        6. User notified for approval

        This test must pass. This is the whole point.
        """
        policy_path = str(
            Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
        )
        skill = _make_skill(
            tmp_path,
            WARDEN_POLICY_FILE=policy_path,
            WARDEN_POLICY_PACKS="",
        )

        # Simulate: agent tries to delete 200 emails one at a time
        blocked_count = 0
        for i in range(200):
            result = skill.before_action(
                {
                    "type": "email.delete",
                    "data": {
                        "email_id": f"msg_{i}",
                        "subject": f"Meeting notes #{i}",
                    },
                },
                {
                    "agent_id": "meta-researcher-bot",
                    "env": "prod",
                    "user": "researcher@meta.com",
                },
            )
            if not result["proceed"]:
                blocked_count += 1

        # Every single email.delete must be blocked
        assert blocked_count == 200, (
            f"Only {blocked_count}/200 email deletes were blocked. "
            "The Meta researcher's inbox would have been destroyed."
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PolicyDecisionCache Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestPolicyDecisionCache:
    def test_cache_returns_allow_on_hit(self):
        cache = PolicyDecisionCache(ttl_seconds=300)
        result = CheckResult(decision=Decision.ALLOW, reason="ok")
        cache.set("api.call", "dev", result)
        cached = cache.get("api.call", "dev")
        assert cached is not None
        assert cached.decision == Decision.ALLOW

    def test_cache_never_stores_deny(self):
        cache = PolicyDecisionCache(ttl_seconds=300)
        result = CheckResult(decision=Decision.DENY, reason="blocked")
        cache.set("code.execute", "prod", result)
        cached = cache.get("code.execute", "prod")
        assert cached is None

    def test_cache_never_stores_review(self):
        cache = PolicyDecisionCache(ttl_seconds=300)
        result = CheckResult(decision=Decision.REVIEW, reason="needs review")
        cache.set("email.delete", "prod", result)
        cached = cache.get("email.delete", "prod")
        assert cached is None

    def test_cache_expires_after_ttl(self):
        import time

        cache = PolicyDecisionCache(ttl_seconds=1)
        result = CheckResult(decision=Decision.ALLOW, reason="ok")
        cache.set("api.call", "dev", result)
        # Force expiry
        key = "api.call:dev"
        cache._cache[key]["cached_at"] = time.time() - 2
        cached = cache.get("api.call", "dev")
        assert cached is None

    def test_cache_clears_on_clear(self):
        cache = PolicyDecisionCache(ttl_seconds=300)
        result = CheckResult(decision=Decision.ALLOW, reason="ok")
        cache.set("api.call", "dev", result)
        assert cache.get("api.call", "dev") is not None
        cache.clear()
        stats = cache.stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["cached_keys"] == 0
        assert cache.get("api.call", "dev") is None

    def test_stats_track_hits_and_misses(self):
        cache = PolicyDecisionCache(ttl_seconds=300)
        result = CheckResult(decision=Decision.ALLOW, reason="ok")
        cache.set("api.call", "dev", result)
        cache.get("api.call", "dev")  # hit
        cache.get("api.call", "dev")  # hit
        cache.get("email.send", "dev")  # miss
        stats = cache.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["cached_keys"] == 1
        assert stats["hit_rate"] == 2 / 3

    def test_high_frequency_100_actions_1_sentinel_call(self, tmp_path):
        """100 identical api.call actions -> 1 Sentinel call, 99 cache hits."""
        skill = _make_skill(tmp_path)

        call_count = 0
        original_evaluate = skill.sentinel.policy_engine.evaluate

        def counting_evaluate(action):
            nonlocal call_count
            call_count += 1
            return original_evaluate(action)

        with patch.object(
            skill.sentinel.policy_engine, "evaluate",
            side_effect=counting_evaluate,
        ):
            for i in range(100):
                result = skill.before_action(
                    {"type": "api.call", "data": {"url": "https://example.com"}},
                    {"agent_id": "bot-1", "env": "dev", "user": "u"},
                )
                assert result["proceed"] is True

        assert call_count == 1, (
            f"Sentinel was called {call_count} times for 100 identical actions. "
            "Expected exactly 1 call + 99 cache hits."
        )

        stats = skill.sentinel.cache.stats()
        assert stats["hits"] == 99
        assert stats["misses"] == 1
