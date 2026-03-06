"""Tests for AlertManager."""

import json
import time
from unittest.mock import patch, MagicMock

from reefwatch.alert_manager import AlertManager


def read_jsonl(path) -> list[dict]:
    """Read a JSONL file and return list of parsed dicts."""
    lines = path.read_text().strip().split("\n")
    return [json.loads(line) for line in lines if line.strip()]


class TestAlertManagerInit:
    def test_reads_alerting_config(self, sample_config):
        mgr = AlertManager(sample_config, "http://localhost:1234", "tok")
        assert mgr.dedup_window == 60
        assert mgr.min_severity == "MEDIUM"
        assert mgr.batch_alerts_flag is False
        assert mgr.batch_window == 5

    def test_reads_webhook_config(self, sample_config):
        mgr = AlertManager(sample_config, "http://localhost:1234", "tok")
        assert mgr.webhook_config == sample_config["webhook"]

    def test_defaults_on_empty_config(self, tmp_path):
        config = {
            "general": {
                "alerts_history": str(tmp_path / "alerts.json"),
            }
        }
        mgr = AlertManager(config, "", "")
        assert mgr.dedup_window == 300
        assert mgr.min_severity == "MEDIUM"
        assert mgr.batch_alerts_flag is True
        assert mgr.batch_window == 30


class TestConfigRetry:
    def test_reads_from_webhook_config(self, sample_config):
        mgr = AlertManager(sample_config, "http://localhost:1234", "tok")
        retry = mgr._config_retry()
        assert retry["attempts"] == 2
        assert retry["delay"] == 1

    def test_defaults_when_no_webhook_section(self, tmp_path):
        config = {
            "general": {
                "alerts_history": str(tmp_path / "alerts.json"),
            }
        }
        mgr = AlertManager(config, "", "")
        retry = mgr._config_retry()
        assert retry["attempts"] == 3
        assert retry["delay"] == 5


class TestSeverityFiltering:
    def test_filters_low_when_min_is_medium(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        alert = make_alert(severity="LOW", rule="low_rule")
        mgr.submit(alert)
        # Should not be saved to history (filtered out)
        assert not mgr.history_file.exists()

    def test_accepts_medium_when_min_is_medium(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        alert = make_alert(severity="MEDIUM", rule="med_rule")
        mgr.submit(alert)
        assert mgr.history_file.exists()

    def test_accepts_high(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        alert = make_alert(severity="HIGH", rule="high_rule")
        mgr.submit(alert)
        assert mgr.history_file.exists()

    def test_accepts_critical(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        alert = make_alert(severity="CRITICAL", rule="crit_rule")
        mgr.submit(alert)
        assert mgr.history_file.exists()

    def test_unknown_severity_treated_as_medium(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        alert = make_alert(severity="BOGUS", rule="bogus_rule")
        # Should NOT crash (was ValueError before fix)
        mgr.submit(alert)
        # BOGUS treated as MEDIUM, which meets the min_severity=MEDIUM threshold
        assert mgr.history_file.exists()

    def test_missing_severity_defaults_to_medium(self, sample_config):
        mgr = AlertManager(sample_config, "", "")
        alert = {"type": "test", "rule": "no_sev_rule"}
        mgr.submit(alert)
        assert mgr.history_file.exists()


class TestDeduplication:
    def test_same_rule_deduped_within_window(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        alert = make_alert(rule="dup_rule")
        mgr.submit(alert)
        mgr.submit(alert)  # Should be deduped

        history = read_jsonl(mgr.history_file)
        assert len(history) == 1

    def test_different_rules_not_deduped(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        mgr.submit(make_alert(rule="rule_a"))
        mgr.submit(make_alert(rule="rule_b"))

        history = read_jsonl(mgr.history_file)
        assert len(history) == 2

    def test_same_rule_accepted_after_window(self, sample_config, make_alert):
        sample_config["alerting"]["dedup_window_seconds"] = 0  # No dedup
        mgr = AlertManager(sample_config, "", "")
        alert = make_alert(rule="dup_rule2")
        mgr.submit(alert)
        time.sleep(0.01)
        mgr.submit(alert)

        history = read_jsonl(mgr.history_file)
        assert len(history) == 2


class TestHistoryPersistence:
    def test_saves_alert_as_jsonl(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        mgr.submit(make_alert(rule="hist_rule"))

        history = read_jsonl(mgr.history_file)
        assert len(history) == 1
        assert history[0]["rule"] == "hist_rule"

    def test_appends_to_existing_file(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        mgr.submit(make_alert(rule="rule_a"))
        mgr.submit(make_alert(rule="rule_b"))

        history = read_jsonl(mgr.history_file)
        assert len(history) == 2
        assert history[0]["rule"] == "rule_a"
        assert history[1]["rule"] == "rule_b"

    def test_creates_parent_directory(self, tmp_path, sample_config, make_alert):
        nested = tmp_path / "deep" / "nested" / "alerts.jsonl"
        sample_config["general"]["alerts_history"] = str(nested)
        mgr = AlertManager(sample_config, "", "")
        mgr.submit(make_alert(rule="nested_rule"))

        assert nested.exists()


class TestHistoryRotation:
    def test_rotates_when_exceeding_max(self, sample_config, make_alert):
        sample_config["general"]["max_alerts_history"] = 3
        sample_config["alerting"]["dedup_window_seconds"] = 0
        mgr = AlertManager(sample_config, "", "")

        # Submit exactly 50 to trigger rotation (happens at _history_count % 50 == 0)
        for i in range(50):
            mgr.submit(make_alert(rule=f"rule_{i}"))
            time.sleep(0.001)

        history = read_jsonl(mgr.history_file)
        assert len(history) == 3

    def test_rotation_keeps_latest(self, sample_config, make_alert):
        sample_config["general"]["max_alerts_history"] = 5
        sample_config["alerting"]["dedup_window_seconds"] = 0
        mgr = AlertManager(sample_config, "", "")

        # Write exactly 50 to trigger first rotation check
        for i in range(50):
            mgr.submit(make_alert(rule=f"rot_{i}"))
            time.sleep(0.001)

        history = read_jsonl(mgr.history_file)
        assert len(history) == 5
        # Last entry should be the most recent
        assert history[-1]["rule"] == "rot_49"


class TestBatching:
    def test_batch_mode_queues_alerts(self, sample_config, make_alert):
        sample_config["alerting"]["batch_alerts"] = True
        sample_config["alerting"]["batch_window_seconds"] = 60
        mgr = AlertManager(sample_config, "", "")
        mgr.submit(make_alert(rule="batch_1"))

        with mgr._batch_lock:
            assert len(mgr._batch) == 1
            assert mgr._batch_timer is not None
        # Cleanup
        mgr.shutdown()

    def test_non_batch_mode_sends_immediately(self, sample_config, make_alert):
        sample_config["alerting"]["batch_alerts"] = False
        mgr = AlertManager(sample_config, "", "")
        with patch.object(mgr, "_send") as mock_send:
            mgr.submit(make_alert(rule="immediate_rule"))
            mock_send.assert_called_once()


class TestShutdown:
    def test_shutdown_flushes_pending_batch(self, sample_config, make_alert):
        sample_config["alerting"]["batch_alerts"] = True
        sample_config["alerting"]["batch_window_seconds"] = 60
        mgr = AlertManager(sample_config, "", "")
        with patch.object(mgr, "_send") as mock_send:
            mgr.submit(make_alert(rule="pending_1"))
            mgr.submit(make_alert(rule="pending_2"))

            # Alerts are queued, not yet sent
            mock_send.assert_not_called()

            # Shutdown should flush them
            mgr.shutdown()
            mock_send.assert_called_once()
            sent_alerts = mock_send.call_args[0][0]
            assert len(sent_alerts) == 2

    def test_shutdown_cancels_timer(self, sample_config, make_alert):
        sample_config["alerting"]["batch_alerts"] = True
        sample_config["alerting"]["batch_window_seconds"] = 60
        mgr = AlertManager(sample_config, "", "")
        mgr.submit(make_alert(rule="timer_test"))

        assert mgr._batch_timer is not None
        mgr.shutdown()
        assert mgr._batch_timer is None

    def test_shutdown_noop_when_no_pending(self, sample_config):
        mgr = AlertManager(sample_config, "", "")
        # Should not raise
        mgr.shutdown()


class TestWebhookValidation:
    def test_localhost_accepted(self, sample_config):
        mgr = AlertManager(sample_config, "http://localhost:18789/hooks/wake", "")
        # URL is rewritten with resolved IP (DNS pinning) but stays functional
        assert mgr.webhook_url != ""
        assert "/hooks/wake" in mgr.webhook_url
        assert mgr._webhook_host_header == "localhost"

    def test_127_0_0_1_accepted(self, sample_config):
        mgr = AlertManager(sample_config, "http://127.0.0.1:18789/hooks/wake", "")
        # IP literal stays unchanged (no DNS resolution needed)
        assert mgr.webhook_url == "http://127.0.0.1:18789/hooks/wake"

    def test_external_host_blocked_by_default(self, sample_config):
        mgr = AlertManager(sample_config, "http://evil.com:1234/hook", "")
        # External hosts are blocked (URL cleared) unless allow_external is set
        assert mgr.webhook_url == ""

    def test_external_host_allowed_with_https(self, sample_config):
        from unittest.mock import patch
        sample_config["webhook"]["allow_external"] = True
        # Mock DNS so test doesn't depend on real resolution
        with patch("reefwatch.alert_manager.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("93.184.216.34",))]
            mgr = AlertManager(sample_config, "https://remote.host:9999/hook", "")
        assert mgr.webhook_url != ""
        assert "/hook" in mgr.webhook_url
        assert mgr._webhook_host_header == "remote.host"

    def test_external_http_blocked_even_with_allow_external(self, sample_config):
        sample_config["webhook"]["allow_external"] = True
        mgr = AlertManager(sample_config, "http://remote.host:9999/hook", "")
        assert mgr.webhook_url == ""  # HTTP blocked for external hosts

    def test_invalid_scheme_disables_webhook(self, sample_config):
        mgr = AlertManager(sample_config, "ftp://localhost/hook", "")
        assert mgr.webhook_url == ""

    def test_empty_url_accepted(self, sample_config):
        mgr = AlertManager(sample_config, "", "")
        assert mgr.webhook_url == ""


class TestWebhookSend:
    @patch("reefwatch.alert_manager.requests.post")
    def test_sends_to_webhook_url(self, mock_post, sample_config, make_alert):
        mock_post.return_value = MagicMock(ok=True)
        mgr = AlertManager(sample_config, "http://localhost:9999/hook", "my-token")
        mgr._send([make_alert()])

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer my-token"

    @patch("reefwatch.alert_manager.requests.post")
    def test_retries_on_failure(self, mock_post, sample_config, make_alert):
        mock_post.side_effect = ConnectionError("refused")
        sample_config["webhook"]["retry_attempts"] = 2
        sample_config["webhook"]["retry_delay_seconds"] = 0
        mgr = AlertManager(sample_config, "http://localhost:9999/hook", "")
        mgr._send([make_alert()])

        assert mock_post.call_count == 2

    def test_no_webhook_logs_only(self, sample_config, make_alert):
        mgr = AlertManager(sample_config, "", "")
        # Should not raise
        mgr._send([make_alert()])
