"""Tests for playlist_history.py — playlist creation tracking."""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

import playlist_history as ph


# ── load_history ─────────────────────────────────────────────────

class TestLoadHistory:
    def test_returns_empty_when_file_missing(self, monkeypatch):
        monkeypatch.setattr(ph, "HISTORY_FILE", Path("/nonexistent/path/history.json"))
        assert ph.load_history() == []

    def test_loads_valid_history(self, tmp_path, monkeypatch):
        data = [{"name": "Test", "date": "2025-01-01T00:00:00+00:00", "track_ids": ["t1"]}]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        result = ph.load_history()
        assert len(result) == 1
        assert result[0]["name"] == "Test"

    def test_returns_empty_on_invalid_json(self, tmp_path, monkeypatch):
        f = tmp_path / "history.json"
        f.write_text("{bad json")
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        assert ph.load_history() == []

    def test_returns_empty_on_non_list_json(self, tmp_path, monkeypatch):
        f = tmp_path / "history.json"
        f.write_text('{"not": "a list"}')
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        assert ph.load_history() == []

    def test_returns_empty_on_os_error(self, tmp_path, monkeypatch):
        f = tmp_path / "history.json"
        f.write_text("[]")
        f.chmod(0o000)
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        result = ph.load_history()
        # Restore permissions for cleanup
        f.chmod(0o644)
        assert result == []


# ── save_history ─────────────────────────────────────────────────

class TestSaveHistory:
    def test_saves_to_file(self, tmp_path, monkeypatch):
        f = tmp_path / "subdir" / "history.json"
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        data = [{"name": "Test"}]
        ph.save_history(data)
        assert json.loads(f.read_text()) == data

    def test_creates_parent_dirs(self, tmp_path, monkeypatch):
        f = tmp_path / "deep" / "nested" / "history.json"
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        ph.save_history([])
        assert f.exists()

    def test_file_has_restrictive_permissions(self, tmp_path, monkeypatch):
        f = tmp_path / "history.json"
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        ph.save_history([])
        mode = f.stat().st_mode & 0o777
        assert mode == 0o600


# ── log_playlist ─────────────────────────────────────────────────

class TestLogPlaylist:
    def test_logs_entry_and_returns_it(self, tmp_path, monkeypatch):
        f = tmp_path / "history.json"
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        entry = ph.log_playlist("My Mix", "deep-cuts", ["t1", "t2", "t3"])
        assert entry["name"] == "My Mix"
        assert entry["strategy"] == "deep-cuts"
        assert entry["track_ids"] == ["t1", "t2", "t3"]
        assert entry["track_count"] == 3
        assert "date" in entry

    def test_appends_to_existing_history(self, tmp_path, monkeypatch):
        f = tmp_path / "history.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps([{"name": "Old"}]))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        ph.log_playlist("New", "mood", ["t1"])
        history = json.loads(f.read_text())
        assert len(history) == 2

    def test_caps_at_200_entries(self, tmp_path, monkeypatch):
        f = tmp_path / "history.json"
        existing = [{"name": f"p{i}", "date": "2025-01-01", "track_ids": [], "track_count": 0, "strategy": "test"} for i in range(200)]
        f.write_text(json.dumps(existing))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        ph.log_playlist("Overflow", "test", ["t1"])
        history = json.loads(f.read_text())
        assert len(history) == 200
        assert history[-1]["name"] == "Overflow"


# ── get_recent_track_ids ─────────────────────────────────────────

class TestGetRecentTrackIds:
    def test_returns_ids_within_window(self, tmp_path, monkeypatch):
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=5)).isoformat()
        old_date = (now - timedelta(days=60)).isoformat()
        data = [
            {"date": recent_date, "track_ids": ["t1", "t2"]},
            {"date": old_date, "track_ids": ["t3"]},
        ]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        result = ph.get_recent_track_ids(days=30)
        assert result == {"t1", "t2"}

    def test_returns_empty_when_no_history(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ph, "HISTORY_FILE", tmp_path / "nope.json")
        assert ph.get_recent_track_ids() == set()

    def test_skips_entries_with_bad_dates(self, tmp_path, monkeypatch):
        data = [
            {"date": "not-a-date", "track_ids": ["t1"]},
            {"track_ids": ["t2"]},  # missing date key
        ]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        result = ph.get_recent_track_ids(days=30)
        assert result == set()


# ── check_tracks ─────────────────────────────────────────────────

class TestCheckTracks:
    def test_identifies_used_and_fresh(self, tmp_path, monkeypatch):
        now = datetime.now(timezone.utc).isoformat()
        data = [{"date": now, "track_ids": ["t1", "t2"]}]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)
        result = ph.check_tracks(["t1", "t3"])
        assert result == {"t1": True, "t3": False}


# ── CLI Commands ─────────────────────────────────────────────────

class TestCmdLog:
    def test_log_from_file(self, tmp_path, monkeypatch, capsys):
        history_file = tmp_path / "history.json"
        monkeypatch.setattr(ph, "HISTORY_FILE", history_file)

        ids_file = tmp_path / "ids.txt"
        ids_file.write_text("t1\nt2\nt3\n")

        args = MagicMock()
        args.name = "Test Playlist"
        args.strategy = "deep-cuts"
        args.track_ids_file = str(ids_file)
        args.track_ids = None

        ph.cmd_log(args)
        captured = capsys.readouterr()
        assert "t1" in captured.out

    def test_log_from_args(self, tmp_path, monkeypatch, capsys):
        history_file = tmp_path / "history.json"
        monkeypatch.setattr(ph, "HISTORY_FILE", history_file)

        args = MagicMock()
        args.name = "Test"
        args.strategy = "mood"
        args.track_ids_file = None
        args.track_ids = ["t1", "t2"]

        ph.cmd_log(args)
        captured = capsys.readouterr()
        assert "t1" in captured.out

    def test_log_exits_with_no_ids(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ph, "HISTORY_FILE", tmp_path / "history.json")

        args = MagicMock()
        args.name = "Test"
        args.strategy = "mood"
        args.track_ids_file = None
        args.track_ids = None

        with pytest.raises(SystemExit):
            ph.cmd_log(args)


class TestCmdList:
    def test_lists_entries(self, tmp_path, monkeypatch, capsys):
        data = [
            {"date": "2025-01-15T00:00:00+00:00", "name": "My Mix", "strategy": "deep-cuts", "track_count": 20}
        ]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)

        args = MagicMock()
        args.limit = None
        ph.cmd_list(args)
        captured = capsys.readouterr()
        assert "My Mix" in captured.out

    def test_limits_output(self, tmp_path, monkeypatch, capsys):
        data = [{"date": f"2025-01-{i:02d}T00:00:00+00:00", "name": f"P{i}", "strategy": "test", "track_count": 5} for i in range(1, 11)]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)

        args = MagicMock()
        args.limit = 3
        ph.cmd_list(args)
        captured = capsys.readouterr()
        # Should only show last 3
        assert "P8" in captured.out
        assert "P10" in captured.out


class TestCmdCheck:
    def test_prints_status(self, tmp_path, monkeypatch, capsys):
        now = datetime.now(timezone.utc).isoformat()
        data = [{"date": now, "track_ids": ["t1"]}]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)

        args = MagicMock()
        args.track_ids = ["t1", "t99"]
        args.days = 30
        ph.cmd_check(args)
        captured = capsys.readouterr()
        assert "recently used" in captured.out
        assert "fresh" in captured.out


class TestCmdRecentTracks:
    def test_prints_recent_ids(self, tmp_path, monkeypatch, capsys):
        now = datetime.now(timezone.utc).isoformat()
        data = [{"date": now, "track_ids": ["t1", "t2"]}]
        f = tmp_path / "history.json"
        f.write_text(json.dumps(data))
        monkeypatch.setattr(ph, "HISTORY_FILE", f)

        args = MagicMock()
        args.days = 30
        ph.cmd_recent_tracks(args)
        captured = capsys.readouterr()
        assert "t1" in captured.out
        assert "t2" in captured.out


class TestMain:
    def test_main_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ph, "HISTORY_FILE", tmp_path / "history.json")
        monkeypatch.setattr(sys, "argv", ["playlist_history.py", "list"])
        # Should not raise
        ph.main()

    def test_main_no_command_exits(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["playlist_history.py"])
        with pytest.raises(SystemExit):
            ph.main()
