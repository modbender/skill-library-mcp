#!/usr/bin/env python3
"""Guarded privileged execution with approval, policy checks, and audit logging.
Review before enabling. No network calls are made from this script.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Allow importing sibling modules when executed from arbitrary cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_logger import append_audit  # noqa: E402
from command_policy import evaluate_command  # noqa: E402
from prompt_policy import load_policy  # noqa: E402


def run_guard(args, *guard_args):
    cmd = [
        sys.executable,
        str(Path(__file__).with_name("root_session_guard.py")),
        "--state-file",
        args.state_file,
        "--timeout-minutes",
        str(args.timeout_minutes),
        *guard_args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


def ask_for_approval(reason: str, command_argv: List[str]) -> bool:
    append_audit({"action": "approval_requested", "reason": reason, "argv": command_argv})
    print("Approval required for elevated execution.")
    print(f"Reason: {reason}")
    print("Command argv:")
    print(json.dumps(command_argv, indent=2))
    answer = input("Approve elevated access for this command? [y/N]: ").strip().lower()
    approved = answer in {"y", "yes"}
    append_audit({"action": "approval_decision", "reason": reason, "argv": command_argv, "approved": approved})
    return approved


def run_command(argv: List[str], use_sudo: bool, sudo_kill_cache: bool) -> int:
    sudo_bin = os.environ.get("OPENCLAW_REAL_SUDO", "sudo")
    exec_argv = [sudo_bin, "--"] + argv if use_sudo else argv
    print("Executing argv:")
    print(json.dumps(exec_argv, indent=2))
    if use_sudo and sudo_kill_cache:
        # Best-effort: ensure sudo timestamp for this user is not reused implicitly.
        subprocess.run([sudo_bin, "-k"], check=False, capture_output=True, text=True)
    append_audit({"action": "exec_start", "argv": argv, "use_sudo": use_sudo})
    result = subprocess.run(exec_argv)
    append_audit({"action": "exec_finish", "argv": argv, "use_sudo": use_sudo, "returncode": result.returncode})
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute privileged commands with approval + idle-timeout guard",
    )
    parser.add_argument(
        "--state-file",
        default=str(Path.home() / ".openclaw" / "security" / "root-session-state.json"),
        help="Path to root session state file",
    )
    parser.add_argument(
        "--timeout-minutes",
        type=int,
        default=30,
        help="Idle timeout for elevated mode / approval session",
    )
    parser.add_argument(
        "--reason",
        required=True,
        help="Business/security reason for privileged command",
    )
    parser.add_argument(
        "--use-sudo",
        action="store_true",
        help="Prefix command with sudo",
    )
    parser.add_argument(
        "--sudo-kill-cache",
        action="store_true",
        default=False,
        help="Run `sudo -k` before execution to reduce implicit sudo reuse",
    )
    parser.add_argument(
        "--keep-session",
        action="store_true",
        default=False,
        help="Keep elevated session after command (still restricted to allowlisted argv; expires on idle timeout)",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help='Command to run, e.g. -- "systemctl restart nginx"',
    )
    return parser.parse_args()


def _get_task_session_id() -> Optional[str]:
    session_id = os.environ.get("OPENCLAW_TASK_SESSION_ID") or None
    require_session = os.environ.get("OPENCLAW_REQUIRE_SESSION_ID") == "1"
    if require_session and not session_id:
        return "__MISSING__"
    return session_id


def main() -> int:
    args = parse_args()
    if not args.command:
        print("No command supplied.", file=sys.stderr)
        return 2

    argv = args.command
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        print("No command supplied after -- delimiter.", file=sys.stderr)
        return 2

    if os.environ.get("OPENCLAW_REQUIRE_POLICY_FILES") == "1":
        required = [
            Path.home() / ".openclaw" / "security" / "command-policy.json",
            Path.home() / ".openclaw" / "security" / "approved_ports.json",
            Path.home() / ".openclaw" / "security" / "egress_allowlist.json",
        ]
        missing = [str(p) for p in required if not p.exists()]
        if missing:
            append_audit({"action": "policy_files_missing", "missing": missing})
            print("Missing required policy files. Refusing privileged execution.", file=sys.stderr)
            return 7

    policy_result = evaluate_command(argv)
    if not policy_result.get("allowed", False):
        append_audit(
            {
                "action": "policy_block",
                "argv": argv,
                "reason": policy_result.get("reason"),
                "pattern": policy_result.get("pattern"),
            }
        )
        print("Command blocked by policy.", file=sys.stderr)
        return 3

    session_id = _get_task_session_id()
    if session_id == "__MISSING__":
        append_audit({"action": "session_id_missing", "argv": argv})
        print("Task session id is required but not provided.", file=sys.stderr)
        return 6

    argv_json = json.dumps(argv)
    if session_id:
        authz = run_guard(args, "authorize", "--argv-json", argv_json, "--session-id", session_id)
    else:
        authz = run_guard(args, "authorize", "--argv-json", argv_json)
    if authz.returncode not in (0, 2):
        sys.stderr.write(authz.stderr or authz.stdout)
        return authz.returncode

    needs_approval = authz.returncode == 2
    prompt_policy = load_policy()
    if prompt_policy.get("require_confirmation_for_untrusted") and os.environ.get("OPENCLAW_UNTRUSTED_SOURCE") == "1":
        confirm = input("Untrusted content source detected. Proceed? [y/N]: ").strip().lower()
        if confirm not in {"y", "yes"}:
            append_audit({"action": "untrusted_source_block", "argv": argv})
            return 5
        append_audit({"action": "untrusted_source_confirmed", "argv": argv})

    if needs_approval and not ask_for_approval(args.reason, argv):
        print("User denied elevated access. Running in normal mode is required.")
        run_guard(args, "normal-used")
        append_audit({"action": "approval_denied", "reason": args.reason, "argv": argv})
        return 1

    if needs_approval:
        token_required = os.environ.get("OPENCLAW_APPROVAL_TOKEN")
        if token_required:
            env_path = Path.home() / ".openclaw" / "env"
            if env_path.exists() and (env_path.stat().st_mode & 0o077):
                print("Warning: ~/.openclaw/env permissions are too open; tighten to 600.")
            token = input("Enter approval token: ").strip()
            if token != token_required:
                append_audit({"action": "approval_token_failed", "argv": argv})
                print("Invalid approval token.", file=sys.stderr)
                return 4
            append_audit({"action": "approval_token_ok", "argv": argv})

        approve_args = ["approve", "--reason", args.reason, "--argv-json", argv_json]
        if session_id:
            approve_args += ["--session-id", session_id]
        approve = run_guard(args, *approve_args)
        if approve.returncode != 0:
            sys.stderr.write(approve.stderr or approve.stdout)
            return approve.returncode
        append_audit({"action": "approval_granted", "reason": args.reason, "argv": argv, "session_id": session_id})

    try:
        if args.use_sudo:
            run_guard(args, "elevated-used")
        return run_command(argv, args.use_sudo, args.sudo_kill_cache)
    finally:
        if not args.keep_session:
            run_guard(args, "drop")
            append_audit({"action": "drop_elevation", "argv": argv, "reason": "post-command"})
        if args.use_sudo and args.sudo_kill_cache:
            sudo_bin = os.environ.get("OPENCLAW_REAL_SUDO", "sudo")
            subprocess.run([sudo_bin, "-k"], check=False, capture_output=True, text=True)


if __name__ == "__main__":
    raise SystemExit(main())
