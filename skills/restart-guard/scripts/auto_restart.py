#!/usr/bin/env python3
"""
restart-guard: auto_restart.py
One-command entrypoint: write context + trigger enhanced restart.
"""

import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(description="Auto run restart-guard flow")
    parser.add_argument("--config", required=True, help="Path to restart-guard.yaml")
    parser.add_argument("--reason", default="", help="Restart reason")
    parser.add_argument("--note", default="", help="Additional note for context")
    parser.add_argument("--triggered-by", default="agent", help="Who triggered this restart")
    parser.add_argument("--verify", nargs=2, action="append", metavar=("CMD", "EXPECT"))
    parser.add_argument("--resume", action="append", metavar="STEP")
    parser.add_argument("--force", action="store_true", help="Ignore cooldown lock")
    parser.add_argument("--notify-mode", default="origin", help="origin|selected|all")
    parser.add_argument("--origin-session-key", default="", help="Origin session key")
    parser.add_argument("--channel", default="", help="Selected channel")
    parser.add_argument("--target", default="", help="Selected target")
    # Legacy flags for compatibility with older callers.
    parser.add_argument("--notify-channel", default="", help=argparse.SUPPRESS)
    parser.add_argument("--notify-target", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()

    reason = (args.reason or "").strip() or "user requested restart"
    channel = (args.channel or args.notify_channel or "").strip()
    target = (args.target or args.notify_target or "").strip()

    write_cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, "write_context.py"),
        "--config",
        args.config,
        "--reason",
        reason,
        "--triggered-by",
        args.triggered_by,
    ]
    if args.note:
        write_cmd.extend(["--note", args.note])
    for item in args.verify or []:
        if len(item) == 2:
            write_cmd.extend(["--verify", item[0], item[1]])
    for step in args.resume or []:
        write_cmd.extend(["--resume", step])

    restart_cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, "restart.py"),
        "--config",
        args.config,
        "--reason",
        reason,
        "--notify-mode",
        args.notify_mode,
    ]
    if args.force:
        restart_cmd.append("--force")
    if args.origin_session_key:
        restart_cmd.extend(["--origin-session-key", args.origin_session_key])
    if channel:
        restart_cmd.extend(["--channel", channel])
    if target:
        restart_cmd.extend(["--target", target])

    rc = subprocess.call(write_cmd)
    if rc != 0:
        sys.exit(rc)
    rc = subprocess.call(restart_cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()
