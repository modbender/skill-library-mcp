#!/usr/bin/env python3
"""TBOT controller (operations only).

Responsibilities:
- start/stop/restart/status/logs for TradingBoat/TBOT runtime
- supports docker compose or systemd based on env MODE
- enforces explicit confirmation for mutating ops

This file is intentionally NOT responsible for JSON generation.
JSON generation lives in scripts/tbotjson.py.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List, Tuple


def require_run_it(action: str, run_it: bool) -> None:
    if run_it or os.getenv("RUN_IT") == "1":
        return
    raise SystemExit(
        f"[guard] '{action}' requires explicit confirmation: pass --run-it or set RUN_IT=1"
    )


def run(cmd: List[str], *, cwd: str | None = None) -> int:
    p = subprocess.run(cmd, cwd=cwd)
    return p.returncode


def docker_compose_base() -> Tuple[List[str], str]:
    compose_dir = os.getenv("COMPOSE_DIR", "")
    if not compose_dir:
        raise SystemExit(
            "COMPOSE_DIR is required when MODE=docker. "
            "Set it to the folder that contains docker-compose.yml (e.g. .../openclaw-on-tradingboat)."
        )

    # UX guardrails: help first-time users when .env is missing.
    compose_yml = os.path.join(compose_dir, "docker-compose.yml")
    if not os.path.exists(compose_yml):
        raise SystemExit(
            f"docker-compose.yml not found in COMPOSE_DIR: {compose_dir}\n"
            "Set COMPOSE_DIR to the openclaw-on-tradingboat folder."
        )

    env_path = os.path.join(compose_dir, ".env")
    if not os.path.exists(env_path):
        sample = os.path.join(compose_dir, ".env.sample")
        stable_dotenv = os.path.join(compose_dir, "stable", "tbot", "dotenv")
        hint = ""
        if os.path.exists(sample):
            hint = f"\nCreate it with:\n  cp {sample} {env_path}\nThen edit required fields (TWS_USERID, TWS_PASSWORD, etc.)."
        elif os.path.exists(stable_dotenv):
            hint = f"\nCreate it with:\n  cp {stable_dotenv} {env_path}\nThen edit required fields (TWS_USERID, TWS_PASSWORD, etc.)."
        raise SystemExit(
            f"Missing required env file: {env_path}\n"
            "This project uses docker compose variable interpolation, so .env is required."
            + hint
        )

    base: List[str] = ["docker", "compose"]
    project = os.getenv("COMPOSE_PROJECT", "")
    if project:
        base += ["--project-name", project]
    return base, compose_dir


def systemd_service() -> Tuple[List[str], str]:
    service = os.getenv("SERVICE_NAME", "")
    if not service:
        raise SystemExit("SERVICE_NAME is required when MODE=systemd")

    use_user = os.getenv("SYSTEMD_USER", "1") == "1"
    base = ["systemctl"]
    if use_user:
        base.append("--user")
    return base, service


def cmd_status(_: argparse.Namespace) -> int:
    mode = os.getenv("MODE", "docker")
    if mode == "docker":
        base, cwd = docker_compose_base()
        return run(base + ["ps"], cwd=cwd)

    base, service = systemd_service()
    return run(base + ["status", "--no-pager", service])


def cmd_logs(args: argparse.Namespace) -> int:
    mode = os.getenv("MODE", "docker")
    tail = str(args.tail)

    if mode == "docker":
        base, cwd = docker_compose_base()
        return run(base + ["logs", f"--tail={tail}"], cwd=cwd)

    service = os.getenv("SERVICE_NAME", "")
    if not service:
        raise SystemExit("SERVICE_NAME is required when MODE=systemd")

    use_user = os.getenv("SYSTEMD_USER", "1") == "1"
    cmd = ["journalctl"]
    if use_user:
        cmd.append("--user")
    cmd += ["-u", service, "-n", tail, "--no-pager"]
    return run(cmd)


def cmd_start(args: argparse.Namespace) -> int:
    require_run_it("start", args.run_it)
    mode = os.getenv("MODE", "docker")
    if mode == "docker":
        base, cwd = docker_compose_base()
        return run(base + ["up", "-d"], cwd=cwd)

    base, service = systemd_service()
    return run(base + ["start", service])


def cmd_stop(args: argparse.Namespace) -> int:
    require_run_it("stop", args.run_it)
    mode = os.getenv("MODE", "docker")
    if mode == "docker":
        base, cwd = docker_compose_base()
        return run(base + ["down"], cwd=cwd)

    base, service = systemd_service()
    return run(base + ["stop", service])


def cmd_restart(args: argparse.Namespace) -> int:
    require_run_it("restart", args.run_it)
    mode = os.getenv("MODE", "docker")
    if mode == "docker":
        base, cwd = docker_compose_base()
        rc = run(base + ["down"], cwd=cwd)
        if rc != 0:
            return rc
        return run(base + ["up", "-d"], cwd=cwd)

    base, service = systemd_service()
    return run(base + ["restart", service])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tbotctl", description="TBOT operations controller")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show docker/systemd status")

    logs_p = sub.add_parser("logs", help="Show recent logs")
    logs_p.add_argument("--tail", type=int, default=200)

    for name in ("start", "stop", "restart"):
        sp = sub.add_parser(name, help=f"{name} TradingBoat/TBOT runtime")
        sp.add_argument("--run-it", action="store_true", help="Required confirmation")

    return p


def main(argv: List[str]) -> int:
    p = build_parser()
    args = p.parse_args(argv)

    if not args.cmd:
        p.print_help()
        return 0

    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "logs":
        return cmd_logs(args)
    if args.cmd == "start":
        return cmd_start(args)
    if args.cmd == "stop":
        return cmd_stop(args)
    if args.cmd == "restart":
        return cmd_restart(args)

    raise SystemExit(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
