#!/usr/bin/env python3
"""MVP prepublish gate for SignalRadar.

Verifies SignalRadar is in a publishable state by running a dry-run
across configured modes.

The gate validates unified CLI behavior and structured RunResult output.
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


def run_dry(workspace_root: str, mode: str, timeout_sec: int) -> tuple[bool, dict[str, Any]]:
    script = os.path.join(workspace_root, "skills", "signalradar", "scripts", "signalradar.py")
    if not os.path.isfile(script):
        return False, {"mode": mode, "status": "error", "error": f"script not found: {script}"}
    cmd = [
        sys.executable,
        script,
        "run",
        "--mode",
        mode,
        "--workspace-root",
        workspace_root,
        "--dry-run",
        "--output",
        "json",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, check=False)
        combined = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            return False, {
                "mode": mode,
                "status": "error",
                "returncode": proc.returncode,
                "error": combined[-500:],
            }
        # output contract check
        payload = json.loads((proc.stdout or "").strip() or "{}")
        st = str(payload.get("status", ""))
        if st not in {"NO_REPLY", "HIT", "DIGEST"}:
            return False, {
                "mode": mode,
                "status": "error",
                "error": f"invalid run status: {st}",
            }
        return True, {"mode": mode, "status": "ok", "run_status": st}
    except subprocess.TimeoutExpired:
        return False, {"mode": mode, "status": "error", "error": "timeout"}
    except Exception as exc:  # noqa: BLE001
        return False, {"mode": mode, "status": "error", "error": str(exc)}


def run_doctor(workspace_root: str, timeout_sec: int) -> tuple[bool, dict[str, Any]]:
    script = os.path.join(workspace_root, "skills", "signalradar", "scripts", "signalradar.py")
    if not os.path.isfile(script):
        return False, {"status": "error", "error": f"script not found: {script}"}
    cmd = [sys.executable, script, "doctor", "--workspace-root", workspace_root, "--output", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, check=False)
        if proc.returncode != 0:
            return False, {"status": "error", "error": (proc.stdout + proc.stderr)[-500:]}
        payload = json.loads((proc.stdout or "").strip() or "{}")
        ok = str(payload.get("status", "")).upper() == "HEALTHY"
        return ok, {"status": "ok" if ok else "warn", "payload": payload}
    except Exception as exc:  # noqa: BLE001
        return False, {"status": "error", "error": str(exc)}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SignalRadar prepublish gate (standalone)")
    p.add_argument("--workspace-root", default=default_workspace_root(), help="Workspace root directory")
    p.add_argument("--modes", default="ai", help="Comma-separated modes to gate-check (default: ai)")
    p.add_argument("--timeout", type=int, default=60, help="Timeout per dry-run in seconds (default 60)")
    # Legacy compat flags (ignored, kept for existing scripts that pass them)
    p.add_argument("--lookback-hours", type=int, default=72, help="(ignored, legacy)")
    p.add_argument("--max-findings", type=int, default=20, help="(ignored, legacy)")
    p.add_argument("--max-lines-per-job", type=int, default=200, help="(ignored, legacy)")
    p.add_argument("--job-id", action="append", default=[], help="(ignored, legacy)")
    p.add_argument("--runs-dir", default="", help="(ignored, legacy)")
    p.add_argument("--output-dir", default="", help="(ignored, legacy)")
    p.add_argument("--json", action="store_true", help="Print machine-readable result")
    return p


def main() -> int:
    args = build_parser().parse_args()
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    if not modes:
        modes = ["ai"]

    try:
        results: dict[str, dict[str, Any]] = {}
        all_ok = True

        doctor_ok, doctor_entry = run_doctor(args.workspace_root, args.timeout)
        results["doctor"] = doctor_entry
        if not doctor_ok:
            all_ok = False

        for mode in modes:
            ok, entry = run_dry(args.workspace_root, mode, args.timeout)
            results[mode] = entry
            if not ok:
                all_ok = False

        out: dict[str, Any] = {
            "ok": all_ok,
            "gate": "dry-run+contract",
            "modes_tested": modes,
            "results": results,
        }
        if args.json:
            print(json.dumps(out, ensure_ascii=False))
        else:
            if all_ok:
                print(f"PREPUBLISH_PASS dry-run ok for modes: {', '.join(modes)}")
            else:
                failed = [m for m in modes if not results[m].get("status") == "ok"]
                print(f"PREPUBLISH_FAIL dry-run failed for modes: {', '.join(failed)}")
                for m in failed:
                    err = results[m].get("error", "")
                    print(f"- {m}: {err}")
        return 0 if all_ok else 3
    except Exception as exc:  # noqa: BLE001
        out = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(out, ensure_ascii=False))
        else:
            print(f"PREPUBLISH_FAIL {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
