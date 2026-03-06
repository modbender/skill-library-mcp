"""Tests for ProcessMonitor."""

import time
from collections import namedtuple
from unittest.mock import patch, MagicMock

from reefwatch.collectors.process_monitor import ProcessMonitor


def _make_config(patterns=None, cpu_threshold=90, cpu_sustained=120):
    return {
        "collectors": {
            "processes": {
                "enabled": True,
                "interval_seconds": 30,
                "suspicious_patterns": patterns or [],
                "cpu_threshold_percent": cpu_threshold,
                "cpu_sustained_seconds": cpu_sustained,
            },
        },
    }


def _fake_proc(pid, name, cmdline, cpu_percent=0):
    """Create a mock process with the info dict psutil.process_iter expects."""
    proc = MagicMock()
    proc.info = {
        "pid": pid,
        "name": name,
        "cmdline": cmdline.split() if cmdline else [],
        "cpu_percent": cpu_percent,
    }
    return proc


class TestSuspiciousPatterns:
    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_detects_pattern_in_cmdline(self, mock_iter):
        mock_iter.return_value = [_fake_proc(100, "bash", "nc -l -p 4444")]
        pm = ProcessMonitor(_make_config(patterns=["nc -l"]))
        alerts = pm.check()
        assert len(alerts) == 1
        assert alerts[0]["type"] == "Suspicious process detected"
        assert "nc -l" in alerts[0]["rule"]

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_detects_pattern_in_name(self, mock_iter):
        mock_iter.return_value = [_fake_proc(200, "xmrig", "")]
        pm = ProcessMonitor(_make_config(patterns=["xmrig"]))
        alerts = pm.check()
        assert len(alerts) == 1

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_case_insensitive_match(self, mock_iter):
        mock_iter.return_value = [_fake_proc(300, "XMRIG", "XMRIG --donate=0")]
        pm = ProcessMonitor(_make_config(patterns=["xmrig"]))
        alerts = pm.check()
        assert len(alerts) == 1

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_no_match_returns_empty(self, mock_iter):
        mock_iter.return_value = [_fake_proc(400, "python3", "python3 app.py")]
        pm = ProcessMonitor(_make_config(patterns=["xmrig"]))
        alerts = pm.check()
        assert len(alerts) == 0

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_multiple_patterns_multiple_procs(self, mock_iter):
        mock_iter.return_value = [
            _fake_proc(500, "nc", "nc -l -p 8080"),
            _fake_proc(501, "python3", "python3 server.py"),
            _fake_proc(502, "xmrig", "xmrig --coin=btc"),
        ]
        pm = ProcessMonitor(_make_config(patterns=["nc -l", "xmrig"]))
        alerts = pm.check()
        assert len(alerts) == 2


class TestHighCPU:
    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_first_high_cpu_no_alert(self, mock_iter):
        mock_iter.return_value = [_fake_proc(600, "busy", "busy", cpu_percent=95)]
        pm = ProcessMonitor(_make_config(cpu_threshold=90, cpu_sustained=120))
        alerts = pm.check()
        # First time seeing high CPU — just recorded, no alert yet
        assert len(alerts) == 0
        assert 600 in pm._high_cpu_pids

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_sustained_high_cpu_alerts(self, mock_iter):
        mock_iter.return_value = [_fake_proc(700, "miner", "miner", cpu_percent=95)]
        pm = ProcessMonitor(_make_config(cpu_threshold=90, cpu_sustained=1))
        pm.check()  # First check — records PID

        # Backdate the first_seen so it exceeds sustained threshold
        pm._high_cpu_pids[700] = time.time() - 5

        alerts = pm.check()
        assert len(alerts) == 1
        assert alerts[0]["type"] == "Sustained high CPU usage"

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_cpu_drops_clears_tracking(self, mock_iter):
        mock_iter.return_value = [_fake_proc(800, "app", "app", cpu_percent=95)]
        pm = ProcessMonitor(_make_config(cpu_threshold=90, cpu_sustained=120))
        pm.check()
        assert 800 in pm._high_cpu_pids

        # CPU drops below threshold
        mock_iter.return_value = [_fake_proc(800, "app", "app", cpu_percent=10)]
        pm.check()
        assert 800 not in pm._high_cpu_pids

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_dead_pid_cleaned_up(self, mock_iter):
        mock_iter.return_value = [_fake_proc(900, "temp", "temp", cpu_percent=95)]
        pm = ProcessMonitor(_make_config(cpu_threshold=90, cpu_sustained=120))
        pm.check()

        # Process gone
        mock_iter.return_value = []
        pm.check()
        assert 900 not in pm._high_cpu_pids


class TestDisabled:
    def test_disabled_returns_empty(self):
        config = _make_config()
        config["collectors"]["processes"]["enabled"] = False
        pm = ProcessMonitor(config)
        assert pm.enabled is False


class TestEdgeCases:
    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_none_cmdline_handled(self, mock_iter):
        proc = MagicMock()
        proc.info = {"pid": 1000, "name": "kworker", "cmdline": None, "cpu_percent": 0}
        mock_iter.return_value = [proc]
        pm = ProcessMonitor(_make_config(patterns=["xmrig"]))
        # Should not crash
        alerts = pm.check()
        assert len(alerts) == 0

    @patch("reefwatch.collectors.process_monitor.psutil.process_iter")
    def test_none_name_handled(self, mock_iter):
        proc = MagicMock()
        proc.info = {"pid": 1001, "name": None, "cmdline": [], "cpu_percent": 0}
        mock_iter.return_value = [proc]
        pm = ProcessMonitor(_make_config(patterns=["xmrig"]))
        alerts = pm.check()
        assert len(alerts) == 0
