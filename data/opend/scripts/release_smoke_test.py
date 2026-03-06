#!/usr/bin/env python3
"""Basic publish-time checks for the OpenD skill."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def file_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    openclaw = ROOT / "openclaw"
    skill = ROOT / "SKILL.md"
    readme = ROOT / "README.md"
    setup_config = ROOT / "setup_config.py"
    gitignore = ROOT / ".gitignore"

    assert_true(openclaw.exists(), "missing openclaw wrapper")
    assert_true(openclaw.stat().st_mode & 0o111, "openclaw is not executable")

    skill_text = file_text(skill)
    assert_true("OPEND_PASSWORD_SECRET_REF" in skill_text, "SKILL.md missing secret-ref documentation")
    assert_true("MOOMOO_PASSWORD" in skill_text, "SKILL.md missing legacy env disclosure")
    assert_true("MOOMOO_CONFIG_KEY" in skill_text, "SKILL.md missing config-key disclosure")
    assert_true("SIMULATE" in skill_text, "SKILL.md missing simulated trading default")
    assert_true("OPEND_SDK_PATH" in skill_text, "SKILL.md missing SDK path warning")

    readme_text = file_text(readme)
    assert_true("OpenClaw secret management" in readme_text, "README missing secret-management posture")

    setup_text = file_text(setup_config)
    assert_true("print(key.decode())" not in setup_text, "setup_config.py still prints the generated key")

    gitignore_text = file_text(gitignore)
    assert_true("config.enc" in gitignore_text, ".gitignore missing config.enc")
    assert_true("config.key" in gitignore_text, ".gitignore missing config.key")

    result = subprocess.run(
        [sys.executable, str(ROOT / "opend_cli.py"), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert_true(result.returncode == 0, "opend_cli.py --help failed")
    assert_true("--credential-method" in result.stdout, "CLI help missing credential method flag")
    assert_true("openclaw" in result.stdout, "CLI help missing openclaw credential method")

    print("release_smoke_test: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
