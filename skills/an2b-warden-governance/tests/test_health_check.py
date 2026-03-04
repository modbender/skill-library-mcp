"""War/Den Health Check Tests -- enterprise service connectivity validation."""

from unittest.mock import MagicMock, patch

import pytest

from warden_governance.health_check import HealthCheck
from warden_governance.settings import Settings


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


class TestHealthCheckNoKeys:
    def test_no_keys_returns_empty_results(self):
        hc = HealthCheck()
        results = hc.run(_config())
        assert results == {}

    def test_only_sentinel_key_checks_sentinel(self):
        hc = HealthCheck()
        config = _config(sentinel_api_key="snos_test")
        with patch.object(hc, "_check_sentinel", return_value={"ok": True, "error": None}) as mock:
            results = hc.run(config)
            mock.assert_called_once()
            assert "sentinel" in results
            assert "engramport" not in results

    def test_only_engramport_key_checks_engramport(self):
        hc = HealthCheck()
        config = _config(engramport_api_key="ek_bot_test")
        with patch.object(hc, "_check_engramport", return_value={"ok": True, "error": None}) as mock:
            results = hc.run(config)
            mock.assert_called_once()
            assert "engramport" in results
            assert "sentinel" not in results

    def test_both_keys_checks_both_services(self):
        hc = HealthCheck()
        config = _config(sentinel_api_key="snos_test", engramport_api_key="ek_bot_test")
        with patch.object(hc, "_check_sentinel", return_value={"ok": True, "error": None}), \
             patch.object(hc, "_check_engramport", return_value={"ok": True, "error": None}):
            results = hc.run(config)
            assert "sentinel" in results
            assert "engramport" in results


class TestHealthCheckSentinel:
    def test_sentinel_httpx_not_installed(self):
        hc = HealthCheck()
        config = _config(sentinel_api_key="snos_test")
        with patch.dict("sys.modules", {"httpx": None}):
            result = hc._check_sentinel(config)
            assert result["ok"] is False
            assert "httpx" in result["error"].lower() or "not installed" in result["error"].lower()

    def test_sentinel_connection_error(self):
        hc = HealthCheck()
        config = _config(sentinel_api_key="snos_test")
        mock_httpx = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = ConnectionError("refused")
        mock_httpx.Client.return_value = mock_client
        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            result = hc._check_sentinel(config)
            assert result["ok"] is False
            assert result["error"] is not None


class TestHealthCheckEngramPort:
    def test_engramport_httpx_not_installed(self):
        hc = HealthCheck()
        config = _config(engramport_api_key="ek_bot_test")
        with patch.dict("sys.modules", {"httpx": None}):
            result = hc._check_engramport(config)
            assert result["ok"] is False

    def test_engramport_connection_error(self):
        hc = HealthCheck()
        config = _config(engramport_api_key="ek_bot_test")
        mock_httpx = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = ConnectionError("refused")
        mock_httpx.Client.return_value = mock_client
        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            result = hc._check_engramport(config)
            assert result["ok"] is False
