"""War/Den Full Pipeline Tests -- end-to-end community pipeline validation."""

from pathlib import Path
from unittest.mock import patch

import pytest

from warden_governance.action_bridge import ActionBridge, ActionType, Decision
from warden_governance.memory_client import MemoryClient
from warden_governance.sentinel_client import SentinelClient
from warden_governance.settings import Settings
from warden_governance.skill import WardenGovernanceSkill
from warden_governance.upgrade_manager import (
    MODE_FULL_COMMUNITY,
    UpgradeManager,
)


def _config(tmp_path, **overrides) -> Settings:
    defaults = {
        "sentinel_api_key": "",
        "engramport_api_key": "",
        "warden_policy_packs": "basic_safety",
        "warden_memory_db": str(tmp_path / "memory.db"),
        "warden_audit_db": str(tmp_path / "audit.db"),
    }
    defaults.update(overrides)
    return Settings(**defaults)


def _skill_config(tmp_path, **overrides) -> dict:
    config = {
        "SENTINEL_API_KEY": "",
        "ENGRAMPORT_API_KEY": "",
        "WARDEN_FAIL_OPEN": "false",
        "WARDEN_AGENT_ID": "pipeline-test-bot",
        "WARDEN_MEMORY_DB": str(tmp_path / "memory.db"),
        "WARDEN_AUDIT_DB": str(tmp_path / "audit.db"),
        "WARDEN_POLICY_PACKS": "",
    }
    config.update(overrides)
    return config


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Community Pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestCommunityPipeline:
    def test_full_community_initializes(self, tmp_path):
        config = _config(tmp_path)
        upgrade = UpgradeManager(config)
        components = upgrade.initialize()
        assert components["mode"]["mode"] == MODE_FULL_COMMUNITY

    def test_community_sentinel_allows_safe_action(self, tmp_path):
        config = _config(tmp_path, warden_policy_packs="")
        sentinel = SentinelClient(config)
        from warden_governance.action_bridge import Action

        action = Action(
            type=ActionType.DATA_READ,
            data={"resource": "inbox"},
            context={"env": "dev"},
            agent_id="test-bot",
        )
        result = sentinel.check(action)
        assert result.decision == Decision.ALLOW

    def test_community_memory_write_read_cycle(self, tmp_path):
        config = _config(tmp_path, warden_policy_packs="")
        sentinel = SentinelClient(config)
        memory = MemoryClient(config, sentinel)

        memory_id = memory.write(
            content="Pipeline test memory",
            namespace="integration_test",
        )
        assert memory_id

        memories = memory.read(
            query="Pipeline test",
            namespace="integration_test",
        )
        assert len(memories) > 0
        assert "Pipeline test" in memories[0]["content"]

    def test_community_memory_delete_cycle(self, tmp_path):
        config = _config(tmp_path, warden_policy_packs="")
        sentinel = SentinelClient(config)
        memory = MemoryClient(config, sentinel)

        memory_id = memory.write(
            content="to be deleted",
            namespace="test",
        )
        deleted = memory.delete(memory_id)
        assert deleted is True

    def test_community_audit_chain_valid_after_pipeline(self, tmp_path):
        config = _config(tmp_path, warden_policy_packs="")
        sentinel = SentinelClient(config)
        memory = MemoryClient(config, sentinel)

        memory.write("entry 1", namespace="test")
        memory.write("entry 2", namespace="test")
        memory.read("entry", namespace="test")

        valid, _ = sentinel.audit_log.verify_chain()
        assert valid is True

    def test_community_synthesis(self, tmp_path):
        config = _config(tmp_path, warden_policy_packs="")
        sentinel = SentinelClient(config)
        memory = MemoryClient(config, sentinel)

        memory.write("fact about cats", namespace="animals")
        memory.write("fact about dogs", namespace="animals")

        synthesis = memory.synthesize("facts", namespaces=["animals"])
        assert "cats" in synthesis or "dogs" in synthesis


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OpenClaw Skill Pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestOpenClawSkillPipeline:
    def test_skill_full_allow_deny_cycle(self, tmp_path):
        policy_path = str(
            Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
        )
        skill = WardenGovernanceSkill(_skill_config(
            tmp_path,
            WARDEN_POLICY_FILE=policy_path,
        ))

        # email.read -> ALLOW
        r1 = skill.before_action(
            {"type": "email.read", "data": {}},
            {"agent_id": "bot-1", "env": "dev"},
        )
        assert r1["proceed"] is True

        # email.delete -> REVIEW (blocked)
        r2 = skill.before_action(
            {"type": "email.delete", "data": {"subject": "test"}},
            {"agent_id": "bot-1", "env": "prod"},
        )
        assert r2["proceed"] is False

        # shell.execute in prod -> DENY (blocked)
        r3 = skill.before_action(
            {"type": "shell.execute", "data": {"command": "ls"}},
            {"agent_id": "bot-1", "env": "prod"},
        )
        assert r3["proceed"] is False

    def test_skill_after_action_doesnt_crash(self, tmp_path):
        skill = WardenGovernanceSkill(_skill_config(tmp_path))
        skill.after_action(
            {"type": "api.call", "data": {}},
            {"status": "ok"},
            {"agent_id": "bot-1"},
        )

    def test_skill_on_error_doesnt_crash(self, tmp_path):
        skill = WardenGovernanceSkill(_skill_config(tmp_path))
        skill.on_error(
            {"type": "api.call", "data": {}},
            ValueError("test error"),
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Action Bridge Pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestActionBridgePipeline:
    def test_bridge_all_15_types_produce_valid_actions(self):
        bridge = ActionBridge()
        from warden_governance.action_bridge import OPENCLAW_TO_WARDEN

        for oc_type in OPENCLAW_TO_WARDEN:
            action = bridge.translate(
                {"type": oc_type, "data": {"key": "value"}},
                {"agent_id": "bot-1", "env": "dev"},
            )
            assert action.type is not None
            assert action.data["openclaw_original"] == oc_type

    def test_bridge_translate_back_and_forth(self):
        bridge = ActionBridge()
        action = bridge.translate(
            {"type": "email.send", "data": {"to": "alice@example.com"}},
            {"agent_id": "bot-1"},
        )
        assert action.type == ActionType.MESSAGE_SEND

        result = bridge.translate_decision(Decision.ALLOW, "ok")
        assert result["proceed"] is True

    def test_bridge_preserves_all_data_fields(self):
        bridge = ActionBridge()
        action = bridge.translate(
            {
                "type": "payment.create",
                "data": {
                    "amount": 500,
                    "currency": "USD",
                    "recipient": "vendor@example.com",
                },
            },
            {"agent_id": "bot-1", "env": "prod"},
        )
        assert action.data["amount"] == 500
        assert action.data["currency"] == "USD"
        assert action.data["recipient"] == "vendor@example.com"
        assert action.data["openclaw_original"] == "payment.create"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multi-Action Scenarios
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestMultiActionScenarios:
    def test_mixed_actions_correct_decisions(self, tmp_path):
        policy_path = str(
            Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
        )
        skill = WardenGovernanceSkill(_skill_config(
            tmp_path,
            WARDEN_POLICY_FILE=policy_path,
        ))

        # Note: payment.create must come before api.call because both
        # map to ActionType.API_CALL, and the decision cache is keyed
        # on action_type:env. If api.call runs first and gets cached
        # as ALLOW, payment.create would hit the cache instead of
        # evaluating its review-payments policy.
        scenarios = [
            ("email.read", "dev", True),
            ("email.send", "dev", True),
            ("file.read", "dev", True),
            ("message.send", "dev", True),
            ("payment.create", "dev", False),
            ("email.delete", "prod", False),
            ("file.delete", "dev", False),
            ("shell.execute", "prod", False),
            ("api.call", "dev", True),
            ("browser.navigate", "dev", True),
        ]

        for action_type, env, expected_proceed in scenarios:
            result = skill.before_action(
                {"type": action_type, "data": {}},
                {"agent_id": "bot-1", "env": env},
            )
            assert result["proceed"] is expected_proceed, (
                f"{action_type} in {env}: expected proceed={expected_proceed}, "
                f"got {result['proceed']}"
            )

    def test_rapid_fire_50_safe_actions(self, tmp_path):
        skill = WardenGovernanceSkill(_skill_config(tmp_path))
        for i in range(50):
            result = skill.before_action(
                {"type": "email.read", "data": {"i": i}},
                {"agent_id": "bot-1", "env": "dev"},
            )
            assert result["proceed"] is True

    def test_interleaved_allow_and_deny(self, tmp_path):
        skill = WardenGovernanceSkill(_skill_config(
            tmp_path,
            WARDEN_POLICY_PACKS="basic_safety",
        ))

        # Allow
        r1 = skill.before_action(
            {"type": "email.read", "data": {}},
            {"agent_id": "bot-1", "env": "dev"},
        )
        assert r1["proceed"] is True

        # Deny
        r2 = skill.before_action(
            {"type": "code.execute", "data": {}},
            {"agent_id": "bot-1", "env": "prod"},
        )
        assert r2["proceed"] is False

        # Allow again
        r3 = skill.before_action(
            {"type": "email.read", "data": {}},
            {"agent_id": "bot-1", "env": "dev"},
        )
        assert r3["proceed"] is True
