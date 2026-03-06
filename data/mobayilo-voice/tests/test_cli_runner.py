import subprocess
from pathlib import Path

from lib.cli_runner import CliRunner


class DummyProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_parse_json_with_preamble(monkeypatch, tmp_path):
    cli = tmp_path / "moby"
    cli.write_text("#!/bin/sh\n")
    cli.chmod(0o755)

    mixed_stdout = (
        "Auto-starting local desktop agent on 127.0.0.1:7788...\n"
        "Opened local agent page. Allow microphone access if prompted.\n"
        "[agent] queued call id=call-1 destination=+817085210572\n"
        "{\n"
        '  "call_id": "call-1",\n'
        '  "status": "queued"\n'
        "}\n"
    )

    def fake_run(*args, **kwargs):
        return DummyProc(returncode=0, stdout=mixed_stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    runner = CliRunner(cli_path=str(cli), timeout=5)
    result = runner.run(["call", "+817085210572", "--json"], parse_json=True)

    assert result.json["call_id"] == "call-1"
    assert result.json["status"] == "queued"
