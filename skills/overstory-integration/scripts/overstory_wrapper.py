#!/usr/bin/env python3
"""Wraps the overstory CLI for programmatic access to agent spawning,
status inspection, worktree management, and hook installation.

Importable as a module or runnable as a CLI tool.
Logs to stderr, structured JSON output to stdout.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("overstory_wrapper")

OVERSTORY_BIN = os.getenv("OVERSTORY_BIN", "overstory")
OVERSTORY_WORKSPACE = os.getenv("OVERSTORY_WORKSPACE", "")


def _run(
    args: List[str],
    cwd: Optional[str] = None,
    timeout: int = 120,
) -> subprocess.CompletedProcess:
    log.debug("exec: %s (cwd=%s)", args, cwd)
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        if result.returncode != 0:
            log.warning("non-zero exit %d: %s", result.returncode, result.stderr.strip())
        return result
    except FileNotFoundError:
        log.error("binary not found: %s", args[0])
        raise
    except subprocess.TimeoutExpired:
        log.error("command timed out after %ds: %s", timeout, args)
        raise


class OverstoryWrapper:
    """Thin wrapper around the overstory CLI."""

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace = Path(workspace_path or OVERSTORY_WORKSPACE or Path.cwd())
        self.bin = OVERSTORY_BIN
        log.info("wrapper initialized — workspace=%s bin=%s", self.workspace, self.bin)

    def _cmd(self, *args: str, timeout: int = 120) -> Dict[str, Any]:
        result = _run([self.bin, *args], cwd=str(self.workspace), timeout=timeout)
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    def init(self) -> Dict[str, Any]:
        """Run ``overstory init`` in the workspace."""
        return self._cmd("init")

    def sling(
        self,
        task_id: str,
        capability: str,
        name: str,
        description: str,
        worktree: bool = True,
    ) -> Dict[str, Any]:
        """Spawn an agent via tmux.

        Parameters mirror the ``overstory sling`` CLI flags.
        """
        cmd = [
            "sling",
            "--task-id", task_id,
            "--capability", capability,
            "--name", name,
            "--description", description,
        ]
        if worktree:
            cmd.append("--worktree")
        return self._cmd(*cmd, timeout=30)

    def status(
        self,
        agent_name: Optional[str] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Get agent or system status."""
        cmd = ["status"]
        if agent_name:
            cmd.extend(["--agent", agent_name])
        if verbose:
            cmd.append("--verbose")
        return self._cmd(*cmd)

    def inspect(self, agent_name: str, lines: int = 50) -> Dict[str, Any]:
        """Retrieve recent transcript lines for an agent."""
        return self._cmd("inspect", "--agent", agent_name, "--lines", str(lines))

    def kill(self, agent_name: str) -> Dict[str, Any]:
        """Terminate an agent's tmux session."""
        return self._cmd("kill", "--agent", agent_name)

    def list_worktrees(self) -> Dict[str, Any]:
        """List git worktrees managed by overstory."""
        result = _run(["git", "worktree", "list", "--porcelain"], cwd=str(self.workspace))
        worktrees: List[Dict[str, str]] = []
        current: Dict[str, str] = {}
        for line in result.stdout.splitlines():
            if not line.strip():
                if current:
                    worktrees.append(current)
                    current = {}
                continue
            if line.startswith("worktree "):
                current["path"] = line.split(" ", 1)[1]
            elif line.startswith("HEAD "):
                current["head"] = line.split(" ", 1)[1]
            elif line.startswith("branch "):
                current["branch"] = line.split(" ", 1)[1]
            elif line == "bare":
                current["bare"] = "true"
            elif line == "detached":
                current["detached"] = "true"
        if current:
            worktrees.append(current)
        return {"ok": result.returncode == 0, "worktrees": worktrees}

    def cleanup_worktree(self, agent_name: str) -> Dict[str, Any]:
        """Remove the git worktree associated with an agent."""
        wt_path = self.workspace / ".overstory" / "worktrees" / agent_name
        if not wt_path.exists():
            return {"ok": False, "error": f"worktree not found: {wt_path}"}
        result = _run(
            ["git", "worktree", "remove", "--force", str(wt_path)],
            cwd=str(self.workspace),
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    def hooks_install(self) -> Dict[str, Any]:
        """Install overstory git hooks."""
        return self._cmd("hooks", "install")


def _json_out(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="overstory CLI wrapper")
    parser.add_argument("--workspace", default=None, help="Workspace root")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")

    p_sling = sub.add_parser("sling")
    p_sling.add_argument("--task-id", required=True)
    p_sling.add_argument("--capability", required=True)
    p_sling.add_argument("--name", required=True)
    p_sling.add_argument("--description", required=True)
    p_sling.add_argument("--worktree", action="store_true", default=True)
    p_sling.add_argument("--no-worktree", action="store_false", dest="worktree")

    p_status = sub.add_parser("status")
    p_status.add_argument("--agent", default=None)
    p_status.add_argument("--verbose", action="store_true")

    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("--agent", required=True)
    p_inspect.add_argument("--lines", type=int, default=50)

    p_kill = sub.add_parser("kill")
    p_kill.add_argument("--agent", required=True)

    sub.add_parser("list-worktrees")

    p_cleanup = sub.add_parser("cleanup-worktree")
    p_cleanup.add_argument("--agent", required=True)

    sub.add_parser("hooks-install")

    args = parser.parse_args()
    wrapper = OverstoryWrapper(args.workspace)

    dispatch = {
        "init": lambda: wrapper.init(),
        "sling": lambda: wrapper.sling(
            args.task_id, args.capability, args.name, args.description, args.worktree,
        ),
        "status": lambda: wrapper.status(args.agent, args.verbose),
        "inspect": lambda: wrapper.inspect(args.agent, args.lines),
        "kill": lambda: wrapper.kill(args.agent),
        "list-worktrees": lambda: wrapper.list_worktrees(),
        "cleanup-worktree": lambda: wrapper.cleanup_worktree(args.agent),
        "hooks-install": lambda: wrapper.hooks_install(),
    }

    try:
        result = dispatch[args.command]()
        _json_out(result)
        sys.exit(0 if result.get("ok", True) else 1)
    except Exception as exc:
        _json_out({"ok": False, "error": str(exc)})
        sys.exit(1)


if __name__ == "__main__":
    main()
