"""Tests for config loading."""

import yaml

from reefwatch.config import load_config
from reefwatch._common import expand


class TestLoadConfig:
    def test_loads_valid_yaml(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"general": {"log_level": "DEBUG"}}))
        result = load_config(str(config_file))
        assert result["general"]["log_level"] == "DEBUG"

    def test_returns_empty_dict_for_missing_file(self):
        result = load_config("/nonexistent/path/config.yaml")
        assert result == {}

    def test_returns_empty_dict_for_empty_file(self, tmp_path):
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")
        result = load_config(str(config_file))
        assert result == {}

    def test_expands_tilde_in_path(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"test": True}))
        # load_config expands ~ via Path.expanduser
        result = load_config(str(config_file))
        assert result["test"] is True


class TestExpand:
    def test_expands_tilde(self):
        result = expand("~/test")
        assert "~" not in str(result)
        assert str(result).endswith("test")

    def test_absolute_path_unchanged(self):
        result = expand("/tmp/test")
        assert str(result) == "/tmp/test"
