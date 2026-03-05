"""Tests for setup_cron.py — cron job management for Apple Music DJ."""

import json
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

import setup_cron as sc


# ── build_job_defs ───────────────────────────────────────────────

class TestBuildJobDefs:
    def test_returns_all_four_jobs(self):
        defs = sc.build_job_defs("/usr/bin/python3", "/path/profile.json", "us", "/tmp/logs")
        assert set(defs.keys()) == {"weekly-mix", "new-releases", "daily-drop", "health-check"}

    def test_each_job_has_required_keys(self):
        defs = sc.build_job_defs("/usr/bin/python3", "/path/profile.json", "us", "/tmp/logs")
        for name, job in defs.items():
            assert "description" in job
            assert "schedule" in job
            assert "command" in job
            assert "log" in job

    def test_uses_python_path(self):
        defs = sc.build_job_defs("/custom/python", "/path/profile.json", "us", "/tmp/logs")
        assert "/custom/python" in defs["weekly-mix"]["command"]

    def test_uses_storefront(self):
        defs = sc.build_job_defs("/usr/bin/python3", "/path/profile.json", "gb", "/tmp/logs")
        assert "gb" in defs["new-releases"]["command"]

    def test_uses_log_dir(self):
        defs = sc.build_job_defs("/usr/bin/python3", "/path/profile.json", "us", "/var/log/music")
        for job in defs.values():
            assert job["log"].startswith("/var/log/music/")


# ── format_cron_line ─────────────────────────────────────────────

class TestFormatCronLine:
    def test_includes_schedule_and_command(self):
        job = {"schedule": "0 7 * * 1", "command": "echo hello", "log": "/tmp/test.log"}
        line = sc.format_cron_line(job, "test-job")
        assert line.startswith("0 7 * * 1 echo hello")

    def test_includes_marker(self):
        job = {"schedule": "0 7 * * 1", "command": "echo hello", "log": "/tmp/test.log"}
        line = sc.format_cron_line(job, "test-job")
        assert "# apple-music-dj:test-job" in line

    def test_includes_log_redirect(self):
        job = {"schedule": "0 7 * * 1", "command": "echo hello", "log": "/tmp/test.log"}
        line = sc.format_cron_line(job, "test-job")
        assert ">> /tmp/test.log 2>&1" in line


# ── get_current_crontab ─────────────────────────────────────────

class TestGetCurrentCrontab:
    def test_returns_crontab_content(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(
            returncode=0, stdout="* * * * * echo hi\n"
        ))
        assert sc.get_current_crontab() == "* * * * * echo hi\n"

    def test_returns_empty_on_failure(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(
            returncode=1, stdout=""
        ))
        assert sc.get_current_crontab() == ""

    def test_exits_on_missing_crontab(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", MagicMock(side_effect=FileNotFoundError))
        with pytest.raises(SystemExit):
            sc.get_current_crontab()


# ── set_crontab ──────────────────────────────────────────────────

class TestSetCrontab:
    def test_returns_true_on_success(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=0))
        assert sc.set_crontab("content") is True

    def test_returns_false_on_failure(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=1))
        assert sc.set_crontab("content") is False

    def test_returns_false_on_missing_crontab(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", MagicMock(side_effect=FileNotFoundError))
        assert sc.set_crontab("content") is False


# ── get_installed_jobs ───────────────────────────────────────────

class TestGetInstalledJobs:
    def test_extracts_job_names(self, monkeypatch):
        crontab = "0 7 * * 1 cmd1 # apple-music-dj:weekly-mix\n0 8 * * 3 cmd2 # apple-music-dj:new-releases\n"
        monkeypatch.setattr(sc, "get_current_crontab", lambda: crontab)
        jobs = sc.get_installed_jobs()
        assert "weekly-mix" in jobs
        assert "new-releases" in jobs

    def test_ignores_non_marker_lines(self, monkeypatch):
        crontab = "0 7 * * 1 some-other-job\n0 8 * * 3 cmd2 # apple-music-dj:daily-drop\n"
        monkeypatch.setattr(sc, "get_current_crontab", lambda: crontab)
        jobs = sc.get_installed_jobs()
        assert jobs == ["daily-drop"]

    def test_empty_crontab(self, monkeypatch):
        monkeypatch.setattr(sc, "get_current_crontab", lambda: "")
        assert sc.get_installed_jobs() == []


# ── cmd_list ─────────────────────────────────────────────────────

class TestCmdList:
    def test_prints_job_info(self, monkeypatch, capsys):
        monkeypatch.setattr(sc, "get_installed_jobs", lambda: ["weekly-mix"])
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", "/tmp")
        sc.cmd_list(defs)
        captured = capsys.readouterr()
        assert "weekly-mix" in captured.out
        assert "✅ installed" in captured.out
        assert "⬚ not installed" in captured.out


# ── cmd_install ──────────────────────────────────────────────────

class TestCmdInstall:
    def test_installs_selected_jobs(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(sc, "get_current_crontab", lambda: "")
        set_calls = []
        monkeypatch.setattr(sc, "set_crontab", lambda c: (set_calls.append(c), True)[-1])
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", str(tmp_path))
        sc.cmd_install(defs, ["weekly-mix"], str(tmp_path))
        assert len(set_calls) == 1
        assert "weekly-mix" in set_calls[0]

    def test_replaces_existing_job(self, monkeypatch, tmp_path, capsys):
        existing = "0 7 * * 1 old-cmd # apple-music-dj:weekly-mix\n"
        monkeypatch.setattr(sc, "get_current_crontab", lambda: existing)
        set_calls = []
        monkeypatch.setattr(sc, "set_crontab", lambda c: (set_calls.append(c), True)[-1])
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", str(tmp_path))
        sc.cmd_install(defs, ["weekly-mix"], str(tmp_path))
        # Should have replaced — only one weekly-mix line
        lines = [l for l in set_calls[0].splitlines() if "weekly-mix" in l]
        assert len(lines) == 1
        assert "old-cmd" not in set_calls[0]

    def test_skips_unknown_job(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(sc, "get_current_crontab", lambda: "")
        monkeypatch.setattr(sc, "set_crontab", lambda c: True)
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", str(tmp_path))
        sc.cmd_install(defs, ["nonexistent-job"], str(tmp_path))
        captured = capsys.readouterr()
        assert "Unknown job" in captured.err

    def test_exits_on_set_failure(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sc, "get_current_crontab", lambda: "")
        monkeypatch.setattr(sc, "set_crontab", lambda c: False)
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", str(tmp_path))
        with pytest.raises(SystemExit):
            sc.cmd_install(defs, ["weekly-mix"], str(tmp_path))


# ── cmd_remove ───────────────────────────────────────────────────

class TestCmdRemove:
    def test_removes_job(self, monkeypatch, capsys):
        existing = "0 7 * * 1 cmd # apple-music-dj:weekly-mix\n0 8 * * 3 cmd2 # apple-music-dj:new-releases\n"
        monkeypatch.setattr(sc, "get_current_crontab", lambda: existing)
        set_calls = []
        monkeypatch.setattr(sc, "set_crontab", lambda c: (set_calls.append(c), True)[-1])
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", "/tmp")
        sc.cmd_remove(defs, ["weekly-mix"])
        assert "weekly-mix" not in set_calls[0]
        assert "new-releases" in set_calls[0]

    def test_no_matching_jobs(self, monkeypatch, capsys):
        monkeypatch.setattr(sc, "get_current_crontab", lambda: "")
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", "/tmp")
        sc.cmd_remove(defs, ["weekly-mix"])
        captured = capsys.readouterr()
        assert "No matching" in captured.out

    def test_exits_on_set_failure(self, monkeypatch):
        existing = "0 7 * * 1 cmd # apple-music-dj:weekly-mix\n"
        monkeypatch.setattr(sc, "get_current_crontab", lambda: existing)
        monkeypatch.setattr(sc, "set_crontab", lambda c: False)
        defs = sc.build_job_defs("/usr/bin/python3", "/p.json", "us", "/tmp")
        with pytest.raises(SystemExit):
            sc.cmd_remove(defs, ["weekly-mix"])


# ── cmd_status ───────────────────────────────────────────────────

class TestCmdStatus:
    def test_shows_installed_jobs(self, monkeypatch, capsys):
        crontab = "0 7 * * 1 cmd # apple-music-dj:weekly-mix\n"
        monkeypatch.setattr(sc, "get_installed_jobs", lambda: ["weekly-mix"])
        monkeypatch.setattr(sc, "get_current_crontab", lambda: crontab)
        sc.cmd_status()
        captured = capsys.readouterr()
        assert "1" in captured.out
        assert "weekly-mix" in captured.out

    def test_shows_none_when_empty(self, monkeypatch, capsys):
        monkeypatch.setattr(sc, "get_installed_jobs", lambda: [])
        sc.cmd_status()
        captured = capsys.readouterr()
        assert "No apple-music-dj" in captured.out


# ── main ─────────────────────────────────────────────────────────

class TestMain:
    def test_main_status(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["setup_cron.py", "status"])
        monkeypatch.setattr("setup_cron.load_config", lambda: {})
        monkeypatch.setattr(sc, "get_installed_jobs", lambda: [])
        sc.main()
        captured = capsys.readouterr()
        assert "No apple-music-dj" in captured.out

    def test_main_list(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["setup_cron.py", "list"])
        monkeypatch.setattr("setup_cron.load_config", lambda: {})
        monkeypatch.setattr(sc, "get_installed_jobs", lambda: [])
        sc.main()
        captured = capsys.readouterr()
        assert "weekly-mix" in captured.out

    def test_main_install(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(sys, "argv", [
            "setup_cron.py", "install", "--jobs", "weekly-mix",
            "--log-dir", str(tmp_path),
        ])
        monkeypatch.setattr("setup_cron.load_config", lambda: {})
        monkeypatch.setattr(sc, "get_current_crontab", lambda: "")
        monkeypatch.setattr(sc, "set_crontab", lambda c: True)
        sc.main()

    def test_main_remove(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["setup_cron.py", "remove", "--jobs", "weekly-mix"])
        monkeypatch.setattr("setup_cron.load_config", lambda: {})
        monkeypatch.setattr(sc, "get_current_crontab", lambda: "")
        sc.main()
        captured = capsys.readouterr()
        assert "No matching" in captured.out
