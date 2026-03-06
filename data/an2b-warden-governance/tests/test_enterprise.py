"""War/Den Enterprise Tests -- upgrade path, mode detection, health check."""

from unittest.mock import MagicMock, patch

import pytest

from warden_governance.settings import Settings
from warden_governance.upgrade_manager import (
    MODE_FULL_COMMUNITY,
    MODE_FULL_ENTERPRISE,
    MODE_GOVERNED_COMMUNITY,
    MODE_MEMORY_ENTERPRISE,
    UpgradeManager,
)


def _config(tmp_path=None, **overrides) -> Settings:
    defaults = {
        "sentinel_api_key": "",
        "engramport_api_key": "",
        "warden_policy_packs": "",
    }
    if tmp_path:
        defaults["warden_memory_db"] = str(tmp_path / "memory.db")
        defaults["warden_audit_db"] = str(tmp_path / "audit.db")
    defaults.update(overrides)
    return Settings(**defaults)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UpgradeManager Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestUpgradeManager:
    def test_detects_full_community(self, tmp_path):
        config = _config(tmp_path)
        mode = UpgradeManager(config).detect_mode()
        assert mode["mode"] == MODE_FULL_COMMUNITY
        assert mode["governance"] == "community"
        assert mode["memory"] == "community"

    def test_detects_governed_community(self, tmp_path):
        config = _config(tmp_path, sentinel_api_key="snos_test")
        mode = UpgradeManager(config).detect_mode()
        assert mode["mode"] == MODE_GOVERNED_COMMUNITY
        assert mode["governance"] == "enterprise"
        assert mode["memory"] == "community"

    def test_detects_memory_enterprise(self, tmp_path):
        config = _config(tmp_path, engramport_api_key="ek_bot_test")
        mode = UpgradeManager(config).detect_mode()
        assert mode["mode"] == MODE_MEMORY_ENTERPRISE
        assert mode["governance"] == "community"
        assert mode["memory"] == "enterprise"

    def test_detects_full_enterprise(self, tmp_path):
        config = _config(
            tmp_path,
            sentinel_api_key="snos_test",
            engramport_api_key="ek_bot_test",
        )
        mode = UpgradeManager(config).detect_mode()
        assert mode["mode"] == MODE_FULL_ENTERPRISE
        assert mode["governance"] == "enterprise"
        assert mode["memory"] == "enterprise"

    def test_initialize_returns_correct_components_community(self, tmp_path):
        config = _config(tmp_path)
        components = UpgradeManager(config).initialize()
        assert components["mode"]["mode"] == MODE_FULL_COMMUNITY

    def test_banner_prints_community(self, tmp_path, capsys):
        config = _config(tmp_path)
        upgrade = UpgradeManager(config)
        banner = upgrade.print_mode_banner()
        assert "Community" in banner or "Local" in banner
        assert "getsentinelos.com" in banner

    def test_banner_prints_enterprise(self, tmp_path, capsys):
        config = _config(
            tmp_path,
            sentinel_api_key="snos_test",
            engramport_api_key="ek_bot_test",
        )
        upgrade = UpgradeManager(config)
        banner = upgrade.print_mode_banner()
        assert "Enterprise" in banner or "Sentinel_OS" in banner
        assert "getsentinelos.com" not in banner


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Settings Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSettings:
    def test_from_config_dict(self):
        settings = Settings.from_config({
            "SENTINEL_API_KEY": "test-key",
            "ENGRAMPORT_API_KEY": "",
            "WARDEN_FAIL_OPEN": "true",
            "WARDEN_AGENT_ID": "my-bot",
        })
        assert settings.sentinel_api_key == "test-key"
        assert settings.engramport_api_key == ""
        assert settings.warden_fail_open is True
        assert settings.warden_agent_id == "my-bot"
        assert settings.warden_mode == "enterprise"

    def test_community_mode_when_no_sentinel_key(self):
        settings = Settings.from_config({
            "SENTINEL_API_KEY": "",
        })
        assert settings.warden_mode == "community"

    def test_enterprise_mode_when_sentinel_key_set(self):
        settings = Settings.from_config({
            "SENTINEL_API_KEY": "snos_valid",
        })
        assert settings.warden_mode == "enterprise"

    def test_defaults_are_sensible(self):
        settings = Settings()
        assert settings.sentinel_api_key == ""
        assert settings.warden_fail_open is False
        assert settings.warden_cache_ttl == 300
        assert settings.warden_agent_id == "openclaw-agent"

    def test_from_env_reads_environment(self):
        import os
        with patch.dict(os.environ, {
            "SENTINEL_API_KEY": "snos_env_test",
            "WARDEN_FAIL_OPEN": "true",
            "WARDEN_AGENT_ID": "env-bot",
            "WARDEN_CACHE_TTL": "600",
        }, clear=False):
            settings = Settings.from_env()
            assert settings.sentinel_api_key == "snos_env_test"
            assert settings.warden_fail_open is True
            assert settings.warden_agent_id == "env-bot"
            assert settings.warden_cache_ttl == 600

    def test_cache_ttl_from_config(self):
        settings = Settings.from_config({
            "WARDEN_CACHE_TTL": "120",
        })
        assert settings.warden_cache_ttl == 120

    def test_engramport_fallback_default_true(self):
        settings = Settings()
        assert settings.engramport_fallback is True
