"""Tests for macOS unified log collection."""

import json
from unittest.mock import patch, MagicMock

from reefwatch.collectors.log_collector import LogCollector


def _make_config(tmp_path):
    return {
        "collectors": {
            "logs": {
                "enabled": True,
                "interval_seconds": 10,
                "sources": {"linux": [], "darwin": []},
                "use_journald": False,
                "use_unified_log": True,
            },
        },
    }


class TestUnifiedLogCollection:
    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_parses_ndjson_entries(self, mock_run, tmp_path):
        records = [
            {"timestamp": "2026-01-01 10:00:00", "eventMessage": "Login succeeded", "processImagePath": "/usr/sbin/sshd", "subsystem": "com.apple.sshd", "category": "auth"},
            {"timestamp": "2026-01-01 10:00:01", "eventMessage": "User session started", "processImagePath": "/usr/sbin/sshd", "subsystem": "com.apple.sshd", "category": "auth"},
        ]
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="\n".join(json.dumps(r) for r in records),
        )
        config = _make_config(tmp_path)
        lc = LogCollector(config)
        lc.use_unified_log = True

        entries = lc._collect_unified_log()
        assert len(entries) == 2
        assert entries[0]["source"] == "unified_log"
        assert entries[0]["line"] == "Login succeeded"
        assert entries[0]["process"] == "/usr/sbin/sshd"
        assert entries[0]["subsystem"] == "com.apple.sshd"

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_skips_empty_messages(self, mock_run, tmp_path):
        records = [
            {"timestamp": "2026-01-01 10:00:00", "eventMessage": ""},
            {"timestamp": "2026-01-01 10:00:01", "eventMessage": "Real message"},
        ]
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="\n".join(json.dumps(r) for r in records),
        )
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        entries = lc._collect_unified_log()
        assert len(entries) == 1
        assert entries[0]["line"] == "Real message"

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_truncates_long_messages(self, mock_run, tmp_path):
        long_msg = "A" * 20000
        records = [{"timestamp": "2026-01-01 10:00:00", "eventMessage": long_msg}]
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(records[0]),
        )
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        entries = lc._collect_unified_log()
        assert len(entries) == 1
        assert len(entries[0]["line"]) == lc._MAX_LOG_LINE

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_first_call_uses_last_interval(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        lc._last_unified_ts = None  # First call

        lc._collect_unified_log()
        cmd = mock_run.call_args[0][0]
        assert "--last" in cmd
        assert "10s" in cmd

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_subsequent_call_uses_start(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        lc._last_unified_ts = "2026-01-01 10:00:00"

        lc._collect_unified_log()
        cmd = mock_run.call_args[0][0]
        assert "--start" in cmd
        idx = cmd.index("--start")
        assert cmd[idx + 1] == "2026-01-01 10:00:00"

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_updates_last_ts_after_collection(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        lc._last_unified_ts = None

        lc._collect_unified_log()
        assert lc._last_unified_ts is not None

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_handles_invalid_json_lines(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"eventMessage": "good"}\nNOT JSON\n{"eventMessage": "also good"}',
        )
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        entries = lc._collect_unified_log()
        assert len(entries) == 2

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_log_command_not_found_disables(self, mock_run, tmp_path):
        mock_run.side_effect = FileNotFoundError("not found")
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        entries = lc._collect_unified_log()
        assert entries == []
        assert lc.use_unified_log is False

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_timeout_handled(self, mock_run, tmp_path):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="log show", timeout=30)
        lc = LogCollector(_make_config(tmp_path))
        lc.use_unified_log = True
        entries = lc._collect_unified_log()
        assert entries == []
        # Should NOT disable unified log on timeout (transient error)
        assert lc.use_unified_log is True
