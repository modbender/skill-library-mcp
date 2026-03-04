"""CLI integration tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CLI_MODULE = [sys.executable, "-m", "detect_file_type"]


def run_cli(*args: str, stdin_data: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [*CLI_MODULE, *args],
        capture_output=True,
        text=stdin_data is None,
        input=stdin_data if stdin_data is not None else None,
        timeout=60,
    )


def run_cli_text(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [*CLI_MODULE, *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestJsonOutput:
    def test_single_file_json(self):
        result = run_cli_text(str(FIXTURES_DIR / "sample.png"))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["label"] == "png"
        assert data["mime_type"] == "image/png"
        assert isinstance(data["score"], float)
        assert data["group"] == "image"
        assert isinstance(data["is_text"], bool)

    def test_multiple_files_json(self):
        result = run_cli_text(
            str(FIXTURES_DIR / "tiny.txt"),
            str(FIXTURES_DIR / "sample.png"),
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 2

    def test_json_output_parseable(self):
        result = run_cli_text(str(FIXTURES_DIR / "sample.zip"))
        data = json.loads(result.stdout)
        required_keys = {"path", "label", "mime_type", "score", "group", "description", "is_text"}
        assert required_keys.issubset(data.keys())

    def test_duplicate_paths_preserve_order(self):
        tiny = str(FIXTURES_DIR / "tiny.txt")
        png = str(FIXTURES_DIR / "sample.png")
        result = run_cli_text(tiny, png, tiny)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert [item["path"] for item in data] == [tiny, png, tiny]


class TestHumanOutput:
    def test_human_format(self):
        result = run_cli_text("--human", str(FIXTURES_DIR / "sample.png"))
        assert result.returncode == 0
        assert "image/png" in result.stdout
        assert "score:" in result.stdout

    def test_human_batch(self):
        result = run_cli_text(
            "--human",
            str(FIXTURES_DIR / "tiny.txt"),
            str(FIXTURES_DIR / "sample.png"),
        )
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 2


class TestMimeOutput:
    def test_mime_format(self):
        result = run_cli_text("--mime", str(FIXTURES_DIR / "sample.png"))
        assert result.returncode == 0
        assert result.stdout.strip() == "image/png"

    def test_mime_batch(self):
        result = run_cli_text(
            "--mime",
            str(FIXTURES_DIR / "tiny.txt"),
            str(FIXTURES_DIR / "sample.png"),
        )
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 2


class TestErrorHandling:
    def test_nonexistent_file(self):
        result = run_cli_text(str(FIXTURES_DIR / "does_not_exist.xyz"))
        assert result.returncode != 0
        assert "No such file" in result.stderr

    def test_empty_file(self):
        result = run_cli_text(str(FIXTURES_DIR / "empty.bin"))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["label"] == "empty"

    def test_partial_failure_exit_code(self):
        result = run_cli_text(
            str(FIXTURES_DIR / "sample.png"),
            str(FIXTURES_DIR / "does_not_exist.xyz"),
        )
        # Should exit 2 (partial failure) — some files succeeded, some failed
        assert result.returncode == 2

    def test_partial_failure_preserves_success_order_with_duplicates(self):
        tiny = str(FIXTURES_DIR / "tiny.txt")
        png = str(FIXTURES_DIR / "sample.png")
        missing = str(FIXTURES_DIR / "does_not_exist.xyz")

        result = run_cli_text(tiny, missing, png, tiny)
        assert result.returncode == 2
        data = json.loads(result.stdout)
        assert [item["path"] for item in data] == [tiny, png, tiny]


class TestStdin:
    def test_stdin_detection(self):
        result = subprocess.run(
            [*CLI_MODULE, "-"],
            input=b"Hello, this is plain text content for stdin detection.\n" * 20,
            capture_output=True,
            timeout=60,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["path"] == "-"
        assert data["group"] == "text"

    def test_stdin_spool_mode_explicit(self):
        result = run_cli("--stdin-mode", "spool", "-", stdin_data=b"plain text from spool mode\n")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["path"] == "-"
        assert data["group"] == "text"

    def test_stdin_head_mode_warns_when_capped(self):
        result = run_cli(
            "--stdin-mode",
            "head",
            "--stdin-max-bytes",
            "32",
            "-",
            stdin_data=b"A" * 128,
        )
        assert result.returncode == 0
        stderr = result.stderr.decode("utf-8", errors="replace")
        assert "stdin head mode reached max bytes" in stderr
        data = json.loads(result.stdout)
        assert data["path"] == "-"

    def test_stdin_head_mode_no_warning_when_under_cap(self):
        result = run_cli(
            "--stdin-mode",
            "head",
            "--stdin-max-bytes",
            "4096",
            "-",
            stdin_data=b"short stdin payload",
        )
        assert result.returncode == 0
        stderr = result.stderr.decode("utf-8", errors="replace")
        assert "stdin head mode reached max bytes" not in stderr

    def test_multiple_stdin_inputs_are_rejected(self):
        result = run_cli("-", "-", stdin_data=b"hello from stdin\n" * 20)
        assert result.returncode == 1
        stderr = result.stderr.decode("utf-8", errors="replace")
        assert "multiple stdin inputs are not supported" in stderr


class TestRecursive:
    def test_recursive_directory(self):
        result = run_cli_text("--recursive", "--json", str(FIXTURES_DIR))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 4  # At least our fixture files
