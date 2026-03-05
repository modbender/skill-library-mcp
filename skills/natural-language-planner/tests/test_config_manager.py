"""
Tests for scripts.config_manager — settings management.

Run with:  python -m pytest tests/test_config_manager.py -v
"""

import sys
import os
import json

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.config_manager import (
    load_config,
    save_config,
    set_config_path,
    get_setting,
    set_setting,
    get_checkin_frequency,
    set_checkin_frequency,
    get_preference,
    DEFAULT_CONFIG,
)


@pytest.fixture
def workspace(tmp_path):
    """Create a temporary workspace for config tests."""
    ws = tmp_path / "config_workspace"
    ws.mkdir()
    (ws / ".nlplanner").mkdir()
    set_config_path(str(ws))
    return ws


class TestLoadSaveConfig:
    def test_load_returns_defaults_when_no_file(self, workspace):
        config = load_config(str(workspace))
        assert config["version"] == DEFAULT_CONFIG["version"]
        assert "settings" in config

    def test_save_and_load_roundtrip(self, workspace):
        config = load_config(str(workspace))
        config["workspace_path"] = str(workspace)
        config["settings"]["dashboard_port"] = 9090
        assert save_config(config, str(workspace))

        loaded = load_config(str(workspace))
        assert loaded["workspace_path"] == str(workspace)
        assert loaded["settings"]["dashboard_port"] == 9090

    def test_load_merges_with_defaults(self, workspace):
        """New default keys should appear even if config file is old."""
        # Write a minimal config
        config_path = workspace / ".nlplanner" / "config.json"
        config_path.write_text(json.dumps({"version": "0.9.0"}), encoding="utf-8")

        loaded = load_config(str(workspace))
        # Should have the default settings merged in
        assert "settings" in loaded
        assert "checkin_frequency_hours" in loaded["settings"]

    def test_load_handles_invalid_json(self, workspace):
        config_path = workspace / ".nlplanner" / "config.json"
        config_path.write_text("not valid json {{{", encoding="utf-8")

        config = load_config(str(workspace))
        # Should return defaults
        assert config["version"] == DEFAULT_CONFIG["version"]


class TestSettings:
    def test_get_set_setting(self, workspace):
        # Save a baseline config
        config = load_config(str(workspace))
        save_config(config, str(workspace))

        assert set_setting("dashboard_port", 3000)
        assert get_setting("dashboard_port") == 3000

    def test_get_setting_missing_key(self, workspace):
        config = load_config(str(workspace))
        save_config(config, str(workspace))
        assert get_setting("nonexistent_key") is None


class TestCheckinFrequency:
    def test_default_frequency(self, workspace):
        config = load_config(str(workspace))
        save_config(config, str(workspace))
        assert get_checkin_frequency() == 24

    def test_set_frequency(self, workspace):
        config = load_config(str(workspace))
        save_config(config, str(workspace))
        assert set_checkin_frequency(48)
        assert get_checkin_frequency() == 48

    def test_minimum_frequency(self, workspace):
        config = load_config(str(workspace))
        save_config(config, str(workspace))
        assert set_checkin_frequency(0)  # Should clamp to 1
        assert get_checkin_frequency() == 1


class TestPreferences:
    def test_get_preference(self, workspace):
        config = load_config(str(workspace))
        save_config(config, str(workspace))
        assert get_preference("default_project") == "inbox"

    def test_get_missing_preference(self, workspace):
        config = load_config(str(workspace))
        save_config(config, str(workspace))
        assert get_preference("nonexistent") is None
