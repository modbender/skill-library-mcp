"""Tests for ReefWatchDaemon orchestration logic."""

from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from reefwatch.daemon import ReefWatchDaemon


def _make_config(tmp_path):
    return {
        "general": {
            "log_file": str(tmp_path / "reefwatch.log"),
            "log_level": "DEBUG",
            "pid_file": str(tmp_path / "reefwatch.pid"),
            "status_file": str(tmp_path / "status.json"),
            "alerts_history": str(tmp_path / "alerts.json"),
            "max_alerts_history": 100,
        },
        "webhook": {
            "url": "",
            "token": "",
            "retry_attempts": 1,
            "retry_delay_seconds": 0,
        },
        "alerting": {
            "dedup_window_seconds": 0,
            "min_severity": "LOW",
            "batch_alerts": False,
            "batch_window_seconds": 1,
        },
        "collectors": {
            "logs": {
                "enabled": False,
                "interval_seconds": 10,
                "sources": {"linux": [], "darwin": []},
                "use_journald": False,
                "use_unified_log": False,
            },
            "files": {
                "enabled": False,
                "watched_paths": {"common": [], "linux": [], "darwin": []},
                "scan_extensions": [],
            },
            "processes": {
                "enabled": False,
                "interval_seconds": 30,
                "suspicious_patterns": [],
                "cpu_threshold_percent": 90,
                "cpu_sustained_seconds": 120,
            },
            "network": {
                "enabled": False,
                "interval_seconds": 60,
                "suspicious_ports": [],
                "connection_rate_threshold": 50,
                "ioc_blocklist": "",
            },
        },
        "engines": {
            "yara": {"enabled": False, "rules_dir": str(tmp_path / "rules" / "yara")},
            "sigma": {"enabled": False, "rules_dir": str(tmp_path / "rules" / "sigma")},
            "custom": {"enabled": False, "rules_dir": str(tmp_path / "rules" / "custom")},
        },
    }


class TestDaemonInit:
    def test_initializes_all_components(self, tmp_path):
        config = _make_config(tmp_path)
        daemon = ReefWatchDaemon(config, "", "")
        assert daemon.log_collector is not None
        assert daemon.file_watcher is not None
        assert daemon.process_monitor is not None
        assert daemon.network_monitor is not None
        assert daemon.yara_engine is not None
        assert daemon.sigma_engine is not None
        assert daemon.custom_engine is not None
        assert daemon.alert_mgr is not None

    def test_critical_paths_expanded(self, tmp_path):
        config = _make_config(tmp_path)
        daemon = ReefWatchDaemon(config, "", "")
        home = str(Path.home())
        # All critical paths should be absolute (no ~ or relative segments)
        for cp in daemon._critical_paths:
            assert cp.startswith("/"), f"Path not absolute: {cp}"
            assert "~" not in cp, f"Path contains ~: {cp}"
        # Should contain expanded home path for openclaw
        assert any(".openclaw" in p for p in daemon._critical_paths)
        assert any(".ssh" in p for p in daemon._critical_paths)

    def test_cycle_divisors_calculated(self, tmp_path):
        config = _make_config(tmp_path)
        daemon = ReefWatchDaemon(config, "", "")
        assert daemon._proc_every >= 1
        assert daemon._net_every >= 1
        assert daemon._integrity_every >= 1
        assert daemon._status_every >= 1


class TestCycleLogic:
    def test_cycle_no_crash_all_disabled(self, tmp_path):
        """Cycle should complete without errors when all collectors/engines disabled."""
        config = _make_config(tmp_path)
        daemon = ReefWatchDaemon(config, "", "")
        # Run a cycle — should not raise
        daemon._cycle(0)

    def test_status_file_written(self, tmp_path):
        config = _make_config(tmp_path)
        daemon = ReefWatchDaemon(config, "", "")
        daemon._write_status(0)
        status_file = Path(config["general"]["status_file"])
        assert status_file.exists()

        import json
        status = json.loads(status_file.read_text())
        assert "pid" in status
        assert "uptime_seconds" in status
        assert "cycles" in status
        assert "collectors" in status
        assert "engines" in status

    def test_submit_increments_counter(self, tmp_path):
        config = _make_config(tmp_path)
        daemon = ReefWatchDaemon(config, "", "")
        assert daemon._alerts_sent == 0
        daemon._submit({
            "type": "test",
            "severity": "HIGH",
            "source": "test",
            "detail": "test",
            "rule": "test/rule",
            "time": "2026-01-01T00:00:00Z",
        })
        assert daemon._alerts_sent == 1


class TestCriticalPathMatching:
    def test_exact_match_on_etc_paths(self, tmp_path):
        config = _make_config(tmp_path)
        config["collectors"]["files"]["enabled"] = True
        daemon = ReefWatchDaemon(config, "", "")

        # /etc/passwd should be in critical paths
        assert "/etc/passwd" in daemon._critical_paths
        assert "/etc/shadow" in daemon._critical_paths
        assert "/etc/sudoers" in daemon._critical_paths


class TestWebhookValidation:
    def test_external_http_blocked(self, tmp_path):
        config = _make_config(tmp_path)
        config["webhook"]["allow_external"] = True
        daemon = ReefWatchDaemon(config, "http://external.com/hook", "")
        # External HTTP should be blocked (HTTPS required)
        assert daemon.alert_mgr.webhook_url == ""

    def test_external_https_allowed(self, tmp_path):
        from unittest.mock import patch
        config = _make_config(tmp_path)
        config["webhook"]["allow_external"] = True
        with patch("reefwatch.alert_manager.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("54.237.57.21",))]
            daemon = ReefWatchDaemon(config, "https://external.com/hook", "")
        assert daemon.alert_mgr.webhook_url != ""
        assert "/hook" in daemon.alert_mgr.webhook_url

    def test_localhost_http_allowed(self, tmp_path):
        config = _make_config(tmp_path)
        daemon = ReefWatchDaemon(config, "http://localhost:18789/hook", "")
        # URL is rewritten with pinned IP but stays functional
        assert daemon.alert_mgr.webhook_url != ""
        assert "/hook" in daemon.alert_mgr.webhook_url
