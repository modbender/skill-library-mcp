"""Shared fixtures for ReefWatch tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_config(tmp_path):
    """Minimal valid config dict for testing."""
    return {
        "general": {
            "log_file": str(tmp_path / "reefwatch.log"),
            "log_level": "DEBUG",
            "pid_file": str(tmp_path / "reefwatch.pid"),
            "alerts_history": str(tmp_path / "alerts_history.json"),
            "max_alerts_history": 100,
        },
        "webhook": {
            "url": "http://127.0.0.1:18789/hooks/wake",
            "token": "test-token",
            "retry_attempts": 2,
            "retry_delay_seconds": 1,
        },
        "alerting": {
            "dedup_window_seconds": 60,
            "min_severity": "MEDIUM",
            "batch_alerts": False,
            "batch_window_seconds": 5,
        },
        "collectors": {
            "logs": {
                "enabled": True,
                "interval_seconds": 10,
                "sources": {"linux": [], "darwin": []},
                "use_journald": False,
            },
            "files": {
                "enabled": True,
                "watched_paths": {"common": [], "linux": [], "darwin": []},
                "scan_extensions": [".py", ".sh"],
            },
            "processes": {
                "enabled": True,
                "interval_seconds": 30,
                "suspicious_patterns": ["xmrig", "nc -l"],
                "cpu_threshold_percent": 90,
                "cpu_sustained_seconds": 120,
            },
            "network": {
                "enabled": True,
                "interval_seconds": 60,
                "suspicious_ports": [4444, 1337],
                "connection_rate_threshold": 50,
                "ioc_blocklist": "",
            },
        },
        "engines": {
            "yara": {"enabled": False, "rules_dir": "rules/yara"},
            "sigma": {"enabled": False, "rules_dir": "rules/sigma"},
            "custom": {"enabled": True, "rules_dir": "rules/custom"},
        },
    }


@pytest.fixture
def make_alert():
    """Factory for creating test alert dicts."""

    def _make(
        type="Test alert",
        severity="HIGH",
        source="test",
        detail="test detail",
        rule="test/rule_001",
        time="2026-01-01T00:00:00Z",
    ):
        return {
            "type": type,
            "severity": severity,
            "source": source,
            "detail": detail,
            "rule": rule,
            "time": time,
        }

    return _make
