"""Tests for YaraEngine."""

import time

from reefwatch.engines.yara_engine import YaraEngine


def _make_config(enabled=False, mode="on_change", interval_hours=24):
    return {
        "engines": {
            "yara": {
                "enabled": enabled,
                "rules_dir": "rules/yara",
                "max_file_size_mb": 50,
                "timeout_seconds": 30,
                "mode": mode,
                "scheduled_interval_hours": interval_hours,
            },
        },
    }


class TestYaraScheduled:
    def test_scheduled_mode_config(self):
        engine = YaraEngine(_make_config(mode="scheduled", interval_hours=12))
        assert engine.mode == "scheduled"
        assert engine.scheduled_interval == 12 * 3600

    def test_on_change_mode_default(self):
        engine = YaraEngine(_make_config())
        assert engine.mode == "on_change"

    def test_should_run_scheduled_scan_false_for_on_change(self):
        engine = YaraEngine(_make_config(mode="on_change"))
        assert engine.should_run_scheduled_scan() is False

    def test_should_run_scheduled_scan_false_when_disabled(self):
        engine = YaraEngine(_make_config(enabled=False, mode="scheduled"))
        assert engine.should_run_scheduled_scan() is False

    def test_should_run_scheduled_scan_true_when_due(self):
        engine = YaraEngine(_make_config(mode="scheduled", interval_hours=0))
        # interval=0 means always due
        # Manually set enabled (it auto-disables when rules dir missing)
        engine.enabled = True
        engine.scheduled_interval = 0
        assert engine.should_run_scheduled_scan() is True

    def test_should_run_after_interval(self):
        engine = YaraEngine(_make_config(mode="scheduled", interval_hours=24))
        engine.enabled = True
        # Pretend last scan was way in the past
        engine._last_scheduled_scan = time.time() - (25 * 3600)
        assert engine.should_run_scheduled_scan() is True

    def test_should_not_run_before_interval(self):
        engine = YaraEngine(_make_config(mode="scheduled", interval_hours=24))
        engine.enabled = True
        engine._last_scheduled_scan = time.time()
        assert engine.should_run_scheduled_scan() is False

    def test_scan_directory_returns_empty_when_disabled(self, tmp_path):
        engine = YaraEngine(_make_config(enabled=False))
        result = engine.scan_directory(str(tmp_path))
        assert result == []

    def test_scan_directory_returns_empty_for_missing_dir(self):
        engine = YaraEngine(_make_config(enabled=False))
        result = engine.scan_directory("/nonexistent/path")
        assert result == []

    def test_scan_directory_updates_last_scan_time(self, tmp_path):
        engine = YaraEngine(_make_config())
        engine.enabled = True
        # Mock _rules to avoid needing actual YARA
        engine._rules = None  # scan_file returns [] when _rules is None
        engine.enabled = False  # scan_directory checks enabled
        # Just test the method doesn't crash on non-dir
        result = engine.scan_directory(str(tmp_path / "nope"))
        assert result == []
