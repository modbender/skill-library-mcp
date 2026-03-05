#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daemonize command via double-fork")
    parser.add_argument("--log", required=True, help="Log file path")
    parser.add_argument("--pid-file", required=True, help="PID file path")
    parser.add_argument("--cwd", default="/", help="Working directory")
    parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to run, prefixed by --")
    args = parser.parse_args()

    if args.cmd and args.cmd[0] == "--":
        args.cmd = args.cmd[1:]
    if not args.cmd:
        parser.error("command required after --")
    return args


def main() -> int:
    args = _parse_args()

    log_path = Path(args.log).expanduser()
    pid_path = Path(args.pid_file).expanduser()
    cwd = Path(args.cwd).expanduser()

    log_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.parent.mkdir(parents=True, exist_ok=True)

    read_fd, write_fd = os.pipe()
    first_pid = os.fork()

    if first_pid > 0:
        os.close(write_fd)
        with os.fdopen(read_fd, "r", encoding="utf-8", errors="ignore") as reader:
            daemon_pid = reader.read().strip()
        os.waitpid(first_pid, 0)
        if not daemon_pid:
            return 1
        print(daemon_pid)
        return 0

    os.close(read_fd)
    os.setsid()
    second_pid = os.fork()

    if second_pid > 0:
        os._exit(0)

    try:
        os.chdir(str(cwd))
    except Exception:
        os.chdir("/")

    os.umask(0o022)

    with log_path.open("ab", buffering=0) as log_file:
        with open(os.devnull, "rb", buffering=0) as devnull:
            os.dup2(devnull.fileno(), sys.stdin.fileno())
            os.dup2(log_file.fileno(), sys.stdout.fileno())
            os.dup2(log_file.fileno(), sys.stderr.fileno())

    try:
        pid_path.write_text(f"{os.getpid()}\n", encoding="utf-8")
    except OSError:
        pass

    with os.fdopen(write_fd, "w", encoding="utf-8", errors="ignore") as writer:
        writer.write(str(os.getpid()))
        writer.flush()

    os.execvp(args.cmd[0], args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
