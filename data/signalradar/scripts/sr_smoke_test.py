#!/usr/bin/env python3
"""MVP smoke test for SignalRadar runtime connectivity.

Runs run_signalradar_job.py in --dry-run mode to verify:
1) AI monitoring pipeline works (connectivity + threshold logic)
2) Watchlist-refresh pipeline works (optional, requires Notion config)

Pass condition: dry-run exits 0 for tested modes.

This smoke test invokes the job script directly.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def default_workspace_root() -> str:
    env_root = os.environ.get("SIGNALRADAR_WORKSPACE_ROOT", "").strip()
    if env_root:
        return env_root
    try:
        script_root = Path(__file__).resolve().parent.parent.parent.parent
        if (script_root / "skills" / "signalradar" / "scripts").exists():
            return str(script_root)
    except Exception:
        pass
    return str(Path.cwd())


def run_dry(
    workspace_root: str,
    mode: str,
    timeout_sec: int,
    source_retries: int,
    limit: int,
) -> tuple[bool, dict[str, Any]]:
    script = os.path.join(workspace_root, "skills", "signalradar", "scripts", "run_signalradar_job.py")
    if not os.path.isfile(script):
        return False, {"mode": mode, "status": "error", "error": f"script not found: {script}"}
    cmd = [
        sys.executable, script,
        "--mode", mode,
        "--workspace-root", workspace_root,
        "--dry-run",
        "--timeout", str(timeout_sec),
        "--source-retries", str(source_retries),
        "--limit", str(limit),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec + 30, check=False)
        if proc.returncode == 0:
            return True, {"mode": mode, "status": "ok", "stdout_tail": proc.stdout[-500:] if proc.stdout else ""}
        return False, {
            "mode": mode,
            "status": "error",
            "returncode": proc.returncode,
            "error": (proc.stderr or proc.stdout or "")[-500:],
        }
    except subprocess.TimeoutExpired:
        return False, {"mode": mode, "status": "error", "error": "timeout"}
    except Exception as exc:  # noqa: BLE001
        return False, {"mode": mode, "status": "error", "error": str(exc)}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SignalRadar connectivity smoke test (standalone)")
    p.add_argument("--workspace-root", default=default_workspace_root(), help="Workspace root directory")
    p.add_argument("--modes", default="ai", help="Comma-separated modes to test (default: ai)")
    p.add_argument("--timeout", type=int, default=30, help="Timeout per dry-run in seconds (default 30)")
    p.add_argument("--source-retries", type=int, default=1, help="Source retries (default 1)")
    p.add_argument("--limit", type=int, default=25, help="Max entries to fetch (default 25)")
    p.add_argument("--json", action="store_true", help="Print machine-readable result")
    return p


def main() -> int:
    args = build_parser().parse_args()
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    if not modes:
        modes = ["ai"]

    results: dict[str, dict[str, Any]] = {}
    all_ok = True
    for mode in modes:
        ok, entry = run_dry(args.workspace_root, mode, args.timeout, args.source_retries, args.limit)
        results[mode] = entry
        if not ok:
            all_ok = False

    out = {"ok": all_ok, "results": results}
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        label = "SMOKE_OK" if all_ok else "SMOKE_FAIL"
        parts = " ".join(f"{m}={results[m].get('status')}" for m in modes)
        print(f"{label} {parts}")
        if not all_ok:
            for m in modes:
                err = results[m].get("error")
                if err:
                    print(f"- {m}_error={err}")
    return 0 if all_ok else 3


if __name__ == "__main__":
    sys.exit(main())
