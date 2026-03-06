#!/usr/bin/env python3
"""SignalRadar unified CLI entrypoint.

Commands:
- run: execute monitoring mode through run_signalradar_job.py
- doctor: runtime and config sanity checks
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
    return str(Path(__file__).resolve().parent.parent.parent.parent)


def _json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def cmd_run(args: argparse.Namespace) -> int:
    script = Path(__file__).resolve().parent / "run_signalradar_job.py"
    cmd = [
        sys.executable,
        str(script),
        "--mode",
        args.mode,
        "--workspace-root",
        args.workspace_root,
    ]
    if args.config:
        cmd.extend(["--config", args.config])
    if args.dry_run:
        cmd.append("--dry-run")
    if args.route_primary:
        cmd.extend(["--route-primary", args.route_primary])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    status = "NO_REPLY" if stdout == "NO_REPLY" else ("HIT" if proc.returncode == 0 else "ERROR")
    payload = {
        "schema_version": "1.0.0",
        "mode": args.mode,
        "status": status,
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }

    if args.output == "json":
        _json_print(payload)
    else:
        if stdout:
            print(stdout)
        if proc.returncode != 0 and stderr:
            print(stderr)

    return proc.returncode


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(args.workspace_root)
    skill_root = root / "skills" / "signalradar"
    config_path = Path(args.config) if args.config else root / "config" / "signalradar_config.json"

    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    check("skill_root_exists", skill_root.exists(), str(skill_root))
    check("run_script_exists", (skill_root / "scripts" / "run_signalradar_job.py").exists(), "run entry")
    check("route_script_exists", (skill_root / "scripts" / "route_delivery.py").exists(), "delivery entry")
    check("config_exists_optional", True, str(config_path) if config_path.exists() else f"missing(optional): {config_path}")
    check("cache_dir_writable", (root / "cache").exists() or root.exists(), str(root / "cache"))

    ok = all(item["ok"] for item in checks)
    payload = {
        "schema_version": "1.0.0",
        "status": "HEALTHY" if ok else "WARN",
        "checks": checks,
    }
    if args.output == "json":
        _json_print(payload)
    else:
        if ok:
            print("HEALTHY")
        else:
            print("WARN")
            for item in checks:
                if not item["ok"]:
                    print(f"- {item['name']}: {item['detail']}")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="SignalRadar unified CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run monitoring mode")
    p_run.add_argument("--mode", required=True, choices=["ai", "crypto", "geopolitics", "watchlist-refresh"])
    p_run.add_argument("--workspace-root", default=default_workspace_root())
    p_run.add_argument("--config", default="")
    p_run.add_argument("--route-primary", default="")
    p_run.add_argument("--route-fallback", action="append", default=[])
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--output", choices=["text", "json"], default="text")
    p_run.set_defaults(func=cmd_run)

    p_doc = sub.add_parser("doctor", help="check runtime health")
    p_doc.add_argument("--workspace-root", default=default_workspace_root())
    p_doc.add_argument("--config", default="")
    p_doc.add_argument("--output", choices=["text", "json"], default="text")
    p_doc.set_defaults(func=cmd_doctor)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
