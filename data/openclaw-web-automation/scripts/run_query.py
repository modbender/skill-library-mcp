#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a public-site automation query")
    parser.add_argument("--query", required=True, help="Natural-language website task")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    schema_rel = Path("schemas/manifest.schema.json")

    def _find_repo_root() -> Path | None:
        env_root = os.getenv("OPENCLAW_AUTOMATION_ROOT", "").strip()
        if env_root:
            p = Path(env_root).expanduser().resolve()
            if (p / schema_rel).exists():
                return p

        # Original in-repo path.
        in_repo = Path(__file__).resolve().parents[3]
        if (in_repo / schema_rel).exists():
            return in_repo

        # Fallback: search cwd ancestry.
        cur = Path.cwd().resolve()
        candidates = [cur, *cur.parents]
        for c in candidates:
            if (c / schema_rel).exists():
                return c
        return None

    root = _find_repo_root()
    if root is None:
        print(
            "Could not locate OpenClaw Automation Kit root. "
            "Set OPENCLAW_AUTOMATION_ROOT to your repo path and ensure "
            "`pip install -e .` has been run there.",
            file=sys.stderr,
        )
        return 2

    cmd = [
        sys.executable,
        "-m",
        "openclaw_automation.cli",
        "run-query",
        "--query",
        args.query,
    ]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr.strip() or proc.stdout.strip())
        return proc.returncode

    # Normalize output to compact JSON for tool users.
    try:
        parsed = json.loads(proc.stdout)
        print(json.dumps(parsed, indent=2))
    except Exception:
        print(proc.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
