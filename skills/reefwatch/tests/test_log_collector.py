"""Tests for LogCollector."""

import json
from unittest.mock import patch, MagicMock

from reefwatch.collectors.log_collector import LogCollector


def _make_config(tmp_path, sources=None, use_journald=False):
    src_file = tmp_path / "test.log"
    src_file.write_text("")
    return {
        "collectors": {
            "logs": {
                "enabled": True,
                "interval_seconds": 10,
                "sources": {
                    "linux": sources or [],
                    "darwin": sources or [str(src_file)],
                },
                "use_journald": use_journald,
                "use_unified_log": False,
            },
        },
    }


class TestLogCollectorBasic:
    def test_collects_new_lines(self, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.write_text("")
        config = _make_config(tmp_path, sources=[str(log_file)])
        lc = LogCollector(config)

        # Append new lines
        with open(log_file, "a") as f:
            f.write("ERROR something bad\n")
            f.write("INFO all good\n")

        entries = lc.collect()
        assert len(entries) == 2
        assert entries[0]["line"] == "ERROR something bad"
        assert entries[0]["source"] == "app.log"

    def test_handles_log_rotation(self, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.write_text("old line 1\nold line 2\nold line 3\nold line 4\n")
        config = _make_config(tmp_path, sources=[str(log_file)])
        lc = LogCollector(config)

        # Simulate rotation: truncate and write smaller content
        log_file.write_text("")
        log_file.write_text("rotated\n")
        entries = lc.collect()

        assert len(entries) == 1
        assert "rotated" in entries[0]["line"]

    def test_skips_missing_sources(self, tmp_path):
        config = _make_config(tmp_path, sources=[str(tmp_path / "nonexistent.log")])
        lc = LogCollector(config)
        # Missing file was filtered during init
        entries = lc.collect()
        assert entries == []

    def test_empty_lines_skipped(self, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.write_text("")
        config = _make_config(tmp_path, sources=[str(log_file)])
        lc = LogCollector(config)

        with open(log_file, "a") as f:
            f.write("\n\n  \nactual line\n\n")

        entries = lc.collect()
        assert len(entries) == 1
        assert entries[0]["line"] == "actual line"


class TestJournald:
    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_collect_journald_parses_json(self, mock_run, tmp_path):
        records = [
            {"MESSAGE": "Started sshd", "_SYSTEMD_UNIT": "sshd.service", "PRIORITY": "6"},
            {"MESSAGE": "Login attempt", "_SYSTEMD_UNIT": "sshd.service", "PRIORITY": "4"},
        ]
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="\n".join(json.dumps(r) for r in records),
        )

        config = _make_config(tmp_path, use_journald=True)
        lc = LogCollector(config)
        # Force journald on (normally only on Linux)
        lc.use_journald = True

        entries = lc._collect_journald()
        assert len(entries) == 2
        assert entries[0]["source"] == "journald"
        assert entries[0]["line"] == "Started sshd"
        assert entries[0]["unit"] == "sshd.service"

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_first_run_uses_init_timestamp(self, mock_run, tmp_path):
        from datetime import datetime
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        config = _make_config(tmp_path, use_journald=True)
        lc = LogCollector(config)
        lc.use_journald = True
        # On Darwin, _last_journald_ts is None; simulate Linux init behavior
        if lc._last_journald_ts is None:
            lc._last_journald_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lc._collect_journald()
        cmd = mock_run.call_args[0][0]
        assert "--since" in cmd
        idx = cmd.index("--since")
        # First run uses the timestamp set at init (local time)
        ts = cmd[idx + 1]
        assert ts is not None and ts != "now"
        # Verify it looks like a timestamp (YYYY-MM-DD HH:MM:SS)
        assert len(ts) == 19 and ts[4] == "-"

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_subsequent_run_uses_timestamp(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        config = _make_config(tmp_path, use_journald=True)
        lc = LogCollector(config)
        lc.use_journald = True

        lc._collect_journald()
        # After first run, _last_journald_ts should be set
        assert lc._last_journald_ts is not None

        lc._collect_journald()
        cmd = mock_run.call_args[0][0]
        idx = cmd.index("--since")
        assert cmd[idx + 1] != "now"

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_journalctl_not_found_disables(self, mock_run, tmp_path):
        mock_run.side_effect = FileNotFoundError("not found")
        config = _make_config(tmp_path, use_journald=True)
        lc = LogCollector(config)
        lc.use_journald = True

        entries = lc._collect_journald()
        assert entries == []
        assert lc.use_journald is False

    @patch("reefwatch.collectors.log_collector.subprocess.run")
    def test_journalctl_error_returns_empty(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        config = _make_config(tmp_path, use_journald=True)
        lc = LogCollector(config)
        lc.use_journald = True

        entries = lc._collect_journald()
        assert entries == []
