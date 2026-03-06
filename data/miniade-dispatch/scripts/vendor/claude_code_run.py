#!/usr/bin/env python3
"""Run Claude Code (claude CLI) reliably.

Default mode is *auto*:
- If the prompt looks like it uses interactive slash commands (e.g. /speckit.*)
  we start an interactive Claude Code session in tmux (PTY).
- Otherwise we run headless (-p) through `script(1)` to force a pseudo-terminal.

Why this wrapper exists:
- Claude Code can hang when run without a TTY.
- CI / exec environments are often non-interactive.

Docs:
- Headless: https://code.claude.com/docs/en/headless
- Agent Teams: https://code.claude.com/docs/en/agent-teams
"""

from __future__ import annotations

import argparse
import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_CLAUDE = os.environ.get("CLAUDE_CODE_BIN", "claude")


def which(name: str) -> str | None:
    paths = os.environ.get("PATH", "").split(":")
    for p in paths:
        cand = Path(p) / name
        try:
            if cand.is_file() and os.access(cand, os.X_OK):
                return str(cand)
        except OSError:
            pass
    return None


def looks_like_slash_commands(prompt: str | None) -> bool:
    if not prompt:
        return False
    for line in prompt.splitlines():
        if line.strip().startswith("/"):
            return True
    return False


def build_headless_cmd(args: argparse.Namespace) -> list[str]:
    cmd: list[str] = [args.claude_bin]

    if args.permission_mode:
        cmd += ["--permission-mode", args.permission_mode]

    if args.prompt is not None:
        cmd += ["-p", args.prompt]

    if args.allowedTools:
        cmd += ["--allowedTools", args.allowedTools]

    if args.output_format:
        cmd += ["--output-format", args.output_format]

    if args.json_schema:
        cmd += ["--json-schema", args.json_schema]

    if args.append_system_prompt:
        cmd += ["--append-system-prompt", args.append_system_prompt]

    if args.system_prompt:
        cmd += ["--system-prompt", args.system_prompt]

    if args.continue_latest:
        cmd.append("--continue")

    if args.resume:
        cmd += ["--resume", args.resume]

    # Agent Teams support
    if args.teammate_mode:
        cmd += ["--teammate-mode", args.teammate_mode]

    if args.extra:
        cmd += args.extra

    return cmd


def build_agent_teams_env(args: argparse.Namespace) -> dict[str, str]:
    """Build environment dict with Agent Teams support."""
    env = os.environ.copy()
    if args.agent_teams:
        env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"
    return env


def run_with_pty(
    cmd: list[str],
    cwd: str | None,
    env: dict[str, str] | None = None,
    max_seconds: int = 0,
) -> int:
    cmd_str = " ".join(shlex.quote(c) for c in cmd)

    script_bin = which("script")
    proc_args = [script_bin, "-q", "-c", cmd_str, "/dev/null"] if script_bin else cmd

    proc = subprocess.Popen(
        proc_args,
        cwd=cwd,
        text=True,
        env=env,
        preexec_fn=os.setsid,
    )

    def kill_group(sig: signal.Signals) -> None:
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            pass

    def handle_signal(signum: int, _frame: object) -> None:
        kill_group(signal.SIGTERM)
        raise SystemExit(128 + signum)

    old_term = signal.signal(signal.SIGTERM, handle_signal)
    old_int = signal.signal(signal.SIGINT, handle_signal)

    try:
        if max_seconds and max_seconds > 0:
            try:
                return proc.wait(timeout=max_seconds)
            except subprocess.TimeoutExpired:
                kill_group(signal.SIGTERM)
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    kill_group(signal.SIGKILL)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
                return 124

        return proc.wait()
    finally:
        signal.signal(signal.SIGTERM, old_term)
        signal.signal(signal.SIGINT, old_int)


def tmux_cmd(socket_path: str, *args: str) -> list[str]:
    return ["tmux", "-S", socket_path, *args]


def tmux_capture(socket_path: str, target: str, lines: int = 200) -> str:
    out = subprocess.check_output(
        tmux_cmd(socket_path, "capture-pane", "-p", "-J", "-t", target, "-S", f"-{lines}"),
        text=True,
    )
    return out


def tmux_wait_for_text(socket_path: str, target: str, pattern: str, timeout_s: int = 30, poll_s: float = 0.5) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            buf = tmux_capture(socket_path, target, lines=200)
            if pattern in buf:
                return True
        except subprocess.CalledProcessError:
            pass
        time.sleep(poll_s)
    return False


def run_interactive_tmux(args: argparse.Namespace) -> int:
    if not which("tmux"):
        print("tmux not found in PATH; cannot run interactive mode.", file=sys.stderr)
        return 2

    socket_dir = args.tmux_socket_dir or os.environ.get("CLAWDBOT_TMUX_SOCKET_DIR") or f"{os.environ.get('TMPDIR', '/tmp')}/clawdbot-tmux-sockets"
    Path(socket_dir).mkdir(parents=True, exist_ok=True)
    socket_path = str(Path(socket_dir) / args.tmux_socket_name)

    session = args.tmux_session
    target = f"{session}:0.0"

    subprocess.run(tmux_cmd(socket_path, "kill-session", "-t", session), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(tmux_cmd(socket_path, "new", "-d", "-s", session, "-n", "shell"))

    cwd = args.cwd or os.getcwd()

    # Set Agent Teams env var inside tmux session if enabled
    if args.agent_teams:
        subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "-l", "--", "export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1"))
        subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"))
        time.sleep(0.3)

    claude_parts = [args.claude_bin]
    if args.permission_mode:
        claude_parts += ["--permission-mode", args.permission_mode]
    if args.allowedTools:
        claude_parts += ["--allowedTools", args.allowedTools]
    if args.append_system_prompt:
        claude_parts += ["--append-system-prompt", args.append_system_prompt]
    if args.system_prompt:
        claude_parts += ["--system-prompt", args.system_prompt]
    if args.continue_latest:
        claude_parts.append("--continue")
    if args.resume:
        claude_parts += ["--resume", args.resume]
    # Agent Teams teammate mode
    if args.teammate_mode:
        claude_parts += ["--teammate-mode", args.teammate_mode]
    if args.extra:
        claude_parts += args.extra

    launch = f"cd {shlex.quote(cwd)} && " + " ".join(shlex.quote(p) for p in claude_parts)
    subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "-l", "--", launch))
    subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"))

    # Workspace trust prompt (first run in a new folder).
    if tmux_wait_for_text(socket_path, target, "Yes, I trust this folder", timeout_s=20):
        subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)
        time.sleep(0.8)
        if tmux_wait_for_text(socket_path, target, "Yes, I trust this folder", timeout_s=2):
            subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "1"), check=False)
            subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)

    # Bypass Permissions warning prompt (when running with --permission-mode bypassPermissions).
    # If we send task text before accepting this prompt, it can accidentally choose the default "No, exit".
    if tmux_wait_for_text(socket_path, target, "Yes, I accept", timeout_s=10):
        # Select option 2 and confirm.
        subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "2"), check=False)
        subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)
        time.sleep(0.8)

    if args.prompt:
        for line in [ln for ln in args.prompt.splitlines() if ln.strip()]:
            subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "-l", "--", line))
            subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"))
            time.sleep(args.interactive_send_delay_ms / 1000.0)

    print("Started interactive Claude Code in tmux.")
    print("To monitor:")
    print(f"  tmux -S {shlex.quote(socket_path)} attach -t {shlex.quote(session)}")
    print("To snapshot output:")
    print(f"  tmux -S {shlex.quote(socket_path)} capture-pane -p -J -t {shlex.quote(target)} -S -200")

    if args.interactive_wait_s > 0:
        time.sleep(args.interactive_wait_s)
        try:
            snap = tmux_capture(socket_path, target, lines=200)
            print("\n--- tmux snapshot (last 200 lines) ---\n")
            print(snap)
        except subprocess.CalledProcessError:
            pass

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Run Claude Code reliably (headless or interactive via tmux)")

    ap.add_argument("-p", "--prompt", help="Prompt text. In headless mode this is passed via -p. In interactive mode it is sent as keystrokes.")
    ap.add_argument(
        "--mode",
        choices=["auto", "headless", "interactive"],
        default="auto",
        help="Execution mode. auto switches to interactive when prompt contains slash commands (lines starting with '/').",
    )

    ap.add_argument(
        "--permission-mode",
        default=None,
        help=(
            "Claude Code permission mode (passed through to `claude --permission-mode`). "
            "Common values include: plan, acceptEdits, dontAsk, bypassPermissions, default."
        ),
    )

    ap.add_argument("--allowedTools", dest="allowedTools", help="Allowed tools allowlist string")
    ap.add_argument("--output-format", dest="output_format", choices=["text", "json", "stream-json"], help="Output format (headless)")
    ap.add_argument("--json-schema", dest="json_schema", help="JSON schema (string) when using --output-format json")

    ap.add_argument("--append-system-prompt", dest="append_system_prompt", help="Append to Claude Code default system prompt")
    ap.add_argument("--system-prompt", dest="system_prompt", help="Replace system prompt")

    ap.add_argument("--continue", dest="continue_latest", action="store_true", help="Continue the most recent session")
    ap.add_argument("--resume", help="Resume a specific session ID")

    # Agent Teams options
    ap.add_argument(
        "--agent-teams",
        action="store_true",
        help="Enable Agent Teams (sets CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1). Allows spawning multiple coordinated Claude Code instances.",
    )
    ap.add_argument(
        "--teammate-mode",
        choices=["auto", "in-process", "tmux"],
        default=None,
        help="Agent Teams display mode. auto (default) uses in-process; tmux creates split panes.",
    )

    ap.add_argument(
        "--claude-bin",
        default=DEFAULT_CLAUDE,
        help=f"Path to claude binary (default: {DEFAULT_CLAUDE}). You can also set CLAUDE_CODE_BIN.",
    )

    ap.add_argument("--cwd", help="Working directory to run claude in (defaults to current directory)")
    ap.add_argument(
        "--max-seconds",
        type=int,
        default=int(os.environ.get("CLAUDE_CODE_MAX_SECONDS", "0")),
        help="Max runtime for headless mode in seconds (0 disables timeout).",
    )

    ap.add_argument("--tmux-session", default="cc", help="tmux session name (interactive mode)")
    ap.add_argument("--tmux-socket-dir", default=None, help="tmux socket dir (defaults to $CLAWDBOT_TMUX_SOCKET_DIR or /tmp)")
    ap.add_argument("--tmux-socket-name", default="claude-code.sock", help="tmux socket file name")
    ap.add_argument("--interactive-wait-s", type=int, default=0, help="Wait N seconds then print a tmux output snapshot")
    ap.add_argument("--interactive-send-delay-ms", type=int, default=800, help="Delay between sending lines in interactive mode")

    ap.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args after --")

    args = ap.parse_args()

    extra = args.extra
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.extra = extra

    if not Path(args.claude_bin).exists():
        print(f"claude binary not found: {args.claude_bin}", file=sys.stderr)
        print("Tip: set CLAUDE_CODE_BIN=/path/to/claude", file=sys.stderr)
        return 2

    mode = args.mode
    if mode == "auto" and looks_like_slash_commands(args.prompt):
        mode = "interactive"

    if mode == "interactive":
        return run_interactive_tmux(args)

    cmd = build_headless_cmd(args)
    env = build_agent_teams_env(args)
    return run_with_pty(cmd, cwd=args.cwd, env=env, max_seconds=args.max_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
