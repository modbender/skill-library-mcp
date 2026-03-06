"""War/Den Memory Tests -- every memory operation is governed."""

import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from warden_governance.action_bridge import ActionType, GovernanceError
from warden_governance.local_store import LocalMemoryStore
from warden_governance.memory_client import MemoryClient
from warden_governance.sentinel_client import SentinelClient
from warden_governance.settings import Settings


def _community_config(tmp_path, **overrides) -> Settings:
    defaults = {
        "sentinel_api_key": "",
        "engramport_api_key": "",
        "warden_policy_packs": "",
        "warden_memory_db": str(tmp_path / "memory.db"),
        "warden_audit_db": str(tmp_path / "audit.db"),
    }
    defaults.update(overrides)
    return Settings(**defaults)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MemoryClient Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestMemoryClient:
    def test_write_calls_sentinel_check_first(self, tmp_path):
        config = _community_config(tmp_path)
        sentinel = SentinelClient(config)
        client = MemoryClient(config, sentinel)

        with patch.object(sentinel, "check", wraps=sentinel.check) as mock_check:
            client.write("test content", namespace="test")
            assert mock_check.call_count == 1
            action = mock_check.call_args[0][0]
            assert action.type == ActionType.MEMORY_WRITE

    def test_read_calls_sentinel_check_first(self, tmp_path):
        config = _community_config(tmp_path)
        sentinel = SentinelClient(config)
        client = MemoryClient(config, sentinel)

        with patch.object(sentinel, "check", wraps=sentinel.check) as mock_check:
            client.read("query", namespace="test")
            assert mock_check.call_count == 1
            action = mock_check.call_args[0][0]
            assert action.type == ActionType.MEMORY_READ

    def test_delete_calls_sentinel_check_first(self, tmp_path):
        config = _community_config(tmp_path)
        sentinel = SentinelClient(config)
        client = MemoryClient(config, sentinel)

        with patch.object(sentinel, "check", wraps=sentinel.check) as mock_check:
            client.delete("fake-id")
            assert mock_check.call_count == 1
            action = mock_check.call_args[0][0]
            assert action.type == ActionType.MEMORY_DELETE

    def test_synthesize_calls_sentinel_check_first(self, tmp_path):
        config = _community_config(tmp_path)
        sentinel = SentinelClient(config)
        client = MemoryClient(config, sentinel)

        with patch.object(sentinel, "check", wraps=sentinel.check) as mock_check:
            client.synthesize("query", namespaces=["test"])
            assert mock_check.call_count == 1
            action = mock_check.call_args[0][0]
            assert action.type == ActionType.MEMORY_SYNTHESIZE

    def test_deny_raises_governance_error(self, tmp_path):
        config = _community_config(tmp_path)
        sentinel = SentinelClient(config)
        client = MemoryClient(config, sentinel)

        with patch.object(
            sentinel, "check",
            side_effect=GovernanceError("denied", "pol_1"),
        ):
            with pytest.raises(GovernanceError):
                client.write("test content")

    def test_memory_never_written_on_deny(self, tmp_path):
        config = _community_config(tmp_path)
        sentinel = SentinelClient(config)
        client = MemoryClient(config, sentinel)

        with patch.object(
            sentinel, "check",
            side_effect=GovernanceError("denied", "pol_1"),
        ):
            with pytest.raises(GovernanceError):
                client.write("should not be stored")

        store = LocalMemoryStore(config)
        results = store.read(
            bot_id=config.warden_agent_id,
            query="should not",
            namespace="default",
        )
        assert len(results) == 0

    def test_community_mode_uses_local_store(self, tmp_path):
        config = _community_config(tmp_path)
        sentinel = SentinelClient(config)
        client = MemoryClient(config, sentinel)
        assert client.store_mode == "community"
        assert isinstance(client.store, LocalMemoryStore)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LocalMemoryStore Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestLocalMemoryStore:
    def test_write_stores_to_sqlite(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)

        memory_id = store.write(
            bot_id="bot-1",
            content="test memory content",
            namespace="default",
            metadata={"key": "value"},
        )
        assert memory_id

        with sqlite3.connect(str(tmp_path / "memory.db")) as conn:
            row = conn.execute(
                "SELECT * FROM memories WHERE memory_id = ?", (memory_id,)
            ).fetchone()
        assert row is not None

    def test_read_returns_matching_memories(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)

        store.write("bot-1", "the weather is sunny", "default", {})
        store.write("bot-1", "I like pizza", "default", {})

        results = store.read("bot-1", "weather", "default")
        assert len(results) == 1
        assert "sunny" in results[0]["content"]

    def test_read_filters_by_namespace(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)

        store.write("bot-1", "workspace note", "work", {})
        store.write("bot-1", "personal note", "personal", {})

        work_results = store.read("bot-1", "note", "work")
        assert len(work_results) == 1
        assert "workspace" in work_results[0]["content"]

    def test_read_filters_expired_memories(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)

        store.write("bot-1", "expired content", "default", {}, ttl_days=0)

        results = store.read("bot-1", "expired", "default")
        assert len(results) == 0

    def test_delete_removes_from_sqlite(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)

        memory_id = store.write("bot-1", "to delete", "default", {})
        assert store.delete("bot-1", memory_id) is True

        results = store.read("bot-1", "to delete", "default")
        assert len(results) == 0

    def test_delete_returns_false_for_nonexistent(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)
        assert store.delete("bot-1", "nonexistent-id") is False

    def test_synthesize_returns_content_string(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)

        store.write("bot-1", "memory one", "ns1", {})
        store.write("bot-1", "memory two", "ns2", {})

        result = store.synthesize("bot-1", "memory", ["ns1", "ns2"])
        assert "memory one" in result
        assert "memory two" in result

    def test_synthesize_empty_returns_empty(self, tmp_path):
        config = _community_config(tmp_path)
        store = LocalMemoryStore(config)
        result = store.synthesize("bot-1", "nothing", ["default"])
        assert result == ""
