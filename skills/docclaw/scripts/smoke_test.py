#!/usr/bin/env python3
"""Smoke tests for docclaw skill scripts (including edge cases)."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
REFRESH = SCRIPTS_DIR / "refresh_docs_index.py"
FETCH = SCRIPTS_DIR / "fetch_doc_markdown.py"
FIND_LOCAL = SCRIPTS_DIR / "find_local_docs.py"


def run(cmd: list[str], expect_code: int = 0) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip())
    if proc.returncode != expect_code:
        raise RuntimeError(
            f"Command failed (expected {expect_code}, got {proc.returncode}): {' '.join(cmd)}"
        )
    return proc


def assert_no_hardcoded_nimbus_paths() -> None:
    files = [SKILL_DIR / "SKILL.md", REFRESH, FETCH, FIND_LOCAL]
    bad = []
    for p in files:
        text = p.read_text(encoding="utf-8")
        if "/Users/Nimbus/" in text:
            bad.append(str(p))
    if bad:
        raise RuntimeError(f"Found hardcoded /Users/Nimbus paths in: {', '.join(bad)}")


def assert_no_local_docs_env_override() -> None:
    text = FIND_LOCAL.read_text(encoding="utf-8")
    if "OPENCLAW_DOCS_LOCAL_PATHS" in text:
        raise RuntimeError("OPENCLAW_DOCS_LOCAL_PATHS override is not allowed.")


def assert_not_running_as_root() -> None:
    geteuid = getattr(os, "geteuid", None)
    if callable(geteuid) and geteuid() == 0:
        raise RuntimeError("Do not run smoke_test.py as root.")


def main() -> int:
    assert_no_hardcoded_nimbus_paths()
    assert_no_local_docs_env_override()
    assert_not_running_as_root()

    with tempfile.TemporaryDirectory(prefix="docclaw-smoke-") as td:
        tmp = Path(td)
        index_json = tmp / "index.json"
        index_md = tmp / "index.md"
        out_dir = tmp / "cache"

        # 1) Refresh index (network + parser path)
        run(
            [
                sys.executable,
                str(REFRESH),
                "--out-json",
                str(index_json),
                "--out-md",
                str(index_md),
                "--timeout",
                "25",
            ]
        )
        payload = json.loads(index_json.read_text(encoding="utf-8"))
        entries = payload.get("entries", [])
        if len(entries) < 100:
            raise RuntimeError(f"Index too small: {len(entries)} entries")
        malicious_index = tmp / "index-malicious.json"
        filtered_entries = [e for e in entries if str(e.get("path", "")) != "cli/docs"]
        filtered_entries.insert(
            0,
            {
                "title": "CLI Docs",
                "description": "",
                "markdown_url": "https://example.com/evil.md",
                "html_url": "https://example.com/evil",
                "path": "cli/docs",
                "section": "cli",
                "source": "test",
            },
        )
        payload["entries"] = filtered_entries
        malicious_index.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        # 2) Fetch by slug
        run(
            [
                sys.executable,
                str(FETCH),
                "cli/docs",
                "--index",
                str(index_json),
                "--cache-dir",
                str(out_dir),
            ]
        )

        # 3) Full URL input should be rejected (slug-only policy)
        run(
            [
                sys.executable,
                str(FETCH),
                "https://docs.openclaw.ai/automation/hooks",
                "--index",
                str(index_json),
                "--cache-dir",
                str(out_dir),
            ],
            expect_code=1,
        )

        # 4) Malicious index entry should not cause off-domain fetch
        run(
            [
                sys.executable,
                str(FETCH),
                "cli/docs",
                "--index",
                str(malicious_index),
                "--cache-dir",
                str(out_dir),
            ]
        )

        # 5) Fetch by title keyword
        run(
            [
                sys.executable,
                str(FETCH),
                "Hooks",
                "--index",
                str(index_json),
                "--cache-dir",
                str(out_dir),
            ]
        )

        # 6) Edge case: expected failure on nonsense slug
        run(
            [
                sys.executable,
                str(FETCH),
                "totally-nonexistent-doc-slug-9f6db6a1",
                "--index",
                str(index_json),
                "--cache-dir",
                str(out_dir),
            ],
            expect_code=1,
        )

        # 7) Untrusted docs roots should be rejected
        run(
            [
                sys.executable,
                str(REFRESH),
                "--docs-root",
                "https://example.com",
                "--out-json",
                str(index_json),
                "--out-md",
                str(index_md),
            ],
            expect_code=1,
        )

        # 8) Local docs discovery script should run (may return 0 or 1 depending host)
        _ = subprocess.run([sys.executable, str(FIND_LOCAL), "--json"], text=True, capture_output=True)

    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
