"""Tests for config validation."""

from reefwatch.config import validate_config


class TestValidateConfig:
    def test_valid_config_no_warnings(self, sample_config):
        # Remove the token to avoid the "token in config" warning
        sample_config["webhook"]["token"] = ""
        warnings = validate_config(sample_config)
        assert warnings == []

    def test_negative_interval(self, sample_config):
        sample_config["collectors"]["logs"]["interval_seconds"] = -5
        warnings = validate_config(sample_config)
        assert any("interval_seconds" in w and "positive" in w for w in warnings)

    def test_zero_interval(self, sample_config):
        sample_config["collectors"]["processes"]["interval_seconds"] = 0
        warnings = validate_config(sample_config)
        assert any("interval_seconds" in w for w in warnings)

    def test_invalid_severity(self, sample_config):
        sample_config["alerting"]["min_severity"] = "SUPER_HIGH"
        warnings = validate_config(sample_config)
        assert any("min_severity" in w for w in warnings)

    def test_valid_severity_accepted(self, sample_config):
        sample_config["webhook"]["token"] = ""
        for sev in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            sample_config["alerting"]["min_severity"] = sev
            warnings = validate_config(sample_config)
            assert not any("min_severity" in w for w in warnings)

    def test_invalid_port(self, sample_config):
        sample_config["collectors"]["network"]["suspicious_ports"] = [80, 99999]
        warnings = validate_config(sample_config)
        assert any("99999" in w for w in warnings)

    def test_negative_port(self, sample_config):
        sample_config["collectors"]["network"]["suspicious_ports"] = [-1]
        warnings = validate_config(sample_config)
        assert any("-1" in w for w in warnings)

    def test_negative_dedup_window(self, sample_config):
        sample_config["alerting"]["dedup_window_seconds"] = -10
        warnings = validate_config(sample_config)
        assert any("dedup_window" in w for w in warnings)

    def test_zero_dedup_window_accepted(self, sample_config):
        sample_config["alerting"]["dedup_window_seconds"] = 0
        sample_config["webhook"]["token"] = ""
        warnings = validate_config(sample_config)
        assert not any("dedup_window" in w for w in warnings)

    def test_negative_batch_window(self, sample_config):
        sample_config["alerting"]["batch_window_seconds"] = -1
        warnings = validate_config(sample_config)
        assert any("batch_window" in w for w in warnings)

    def test_zero_retry_attempts(self, sample_config):
        sample_config["webhook"]["retry_attempts"] = 0
        warnings = validate_config(sample_config)
        assert any("retry_attempts" in w for w in warnings)

    def test_empty_config_no_crash(self):
        warnings = validate_config({})
        assert warnings == []

    def test_multiple_issues_reported(self, sample_config):
        sample_config["collectors"]["logs"]["interval_seconds"] = -1
        sample_config["alerting"]["min_severity"] = "INVALID"
        sample_config["collectors"]["network"]["suspicious_ports"] = [99999]
        warnings = validate_config(sample_config)
        assert len(warnings) >= 3


class TestNewValidations:
    def test_invalid_log_level(self, sample_config):
        sample_config["general"]["log_level"] = "VERBOSE"
        warnings = validate_config(sample_config)
        assert any("log_level" in w for w in warnings)

    def test_valid_log_levels(self, sample_config):
        sample_config["webhook"]["token"] = ""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            sample_config["general"]["log_level"] = level
            warnings = validate_config(sample_config)
            assert not any("log_level" in w for w in warnings)

    def test_invalid_yara_mode(self, sample_config):
        sample_config["engines"]["yara"]["mode"] = "always"
        warnings = validate_config(sample_config)
        assert any("yara.mode" in w for w in warnings)

    def test_valid_yara_modes(self, sample_config):
        sample_config["webhook"]["token"] = ""
        for mode in ["on_change", "scheduled"]:
            sample_config["engines"]["yara"]["mode"] = mode
            warnings = validate_config(sample_config)
            assert not any("yara.mode" in w for w in warnings)

    def test_non_boolean_warns(self, sample_config):
        sample_config["alerting"]["batch_alerts"] = "yes"
        warnings = validate_config(sample_config)
        assert any("boolean" in w for w in warnings)

    def test_token_in_config_warns(self, sample_config):
        sample_config["webhook"]["token"] = "secret-123"
        warnings = validate_config(sample_config)
        assert any("token" in w.lower() and "env" in w.lower() for w in warnings)

    def test_empty_token_no_warning(self, sample_config):
        sample_config["webhook"]["token"] = ""
        warnings = validate_config(sample_config)
        assert not any("token" in w.lower() and "env" in w.lower() for w in warnings)
