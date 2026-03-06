#!/usr/bin/env python3
"""
Python wrapper around the overstory CLI for agent swarm operations.
Importable as a module or executable as a CLI tool.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=os.environ.get("BRIDGE_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("overstory_client")

DEFAULT_TIMEOUT = 120


class OverstoryError(Exception):
    """Raised when an overstory CLI command fails."""


class OverstoryClient:
    """Wrapper around the overstory CLI binary."""

    def __init__(self, binary: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        self.binary = binary or os.environ.get("OVERSTORY_BIN", "overstory")
        self.timeout = timeout

    def _run(self, args: List[str], timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute an overstory CLI command and return parsed output."""
        cmd = [self.binary] + args
        log.debug("Running: %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
            )
        except FileNotFoundError:
            raise OverstoryError(
                f"overstory binary not found at '{self.binary}'. "
                "Set OVERSTORY_BIN or install overstory."
            )
        except subprocess.TimeoutExpired:
            raise OverstoryError(
                f"Command timed out after {timeout or self.timeout}s: {' '.join(cmd)}"
            )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise OverstoryError(
                f"overstory exited {result.returncode}: {stderr or result.stdout.strip()}"
            )

        stdout = result.stdout.strip()
        if not stdout:
            return {"ok": True}

        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return {"raw": stdout}

    # ── Agent lifecycle ─────────────────────────────────────────

    def sling(
        self,
        task_id: str,
        capability: str,
        name: str,
        description: str,
        parent: Optional[str] = None,
        force_hierarchy: bool = False,
    ) -> Dict[str, Any]:
        """Spawn a new agent via `overstory sling`."""
        log.info("Slinging agent %s (capability=%s)", name, capability)
        args = [
            "sling",
            "--task-id", task_id,
            "--capability", capability,
            "--name", name,
            "--description", description,
        ]
        if parent:
            args.extend(["--parent", parent])
        if force_hierarchy:
            args.append("--force-hierarchy")
        return self._run(args)

    def status(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get agent status. If agent_name is None, returns all agents."""
        args = ["status"]
        if agent_name:
            args.extend(["--agent", agent_name])
        return self._run(args)

    def inspect(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed transcript/state for a specific agent."""
        log.info("Inspecting agent %s", agent_name)
        return self._run(["inspect", "--agent", agent_name])

    def list_agents(self) -> Dict[str, Any]:
        """List all active agents."""
        return self._run(["list"])

    def merge(self, agent_name: str) -> Dict[str, Any]:
        """Trigger merge for an agent's worktree."""
        log.info("Merging agent %s", agent_name)
        return self._run(["merge", "--agent", agent_name])

    # ── Mail system ─────────────────────────────────────────────

    def mail_send(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """Send a message between agents."""
        log.info("Mail %s → %s (priority=%s)", from_agent, to_agent, priority)
        return self._run([
            "mail", "send",
            "--from", from_agent,
            "--to", to_agent,
            "--message", message,
            "--priority", priority,
        ])

    def mail_read(self, agent_name: str) -> Dict[str, Any]:
        """Read mail for an agent."""
        return self._run(["mail", "read", "--agent", agent_name])

    # ── Coordination ────────────────────────────────────────────

    def coordinator_start(self) -> Dict[str, Any]:
        """Start the persistent coordinator agent."""
        log.info("Starting coordinator")
        return self._run(["coordinator", "start"])

    def supervisor_start(self, project: str) -> Dict[str, Any]:
        """Start a per-project supervisor."""
        log.info("Starting supervisor for project %s", project)
        return self._run(["supervisor", "start", "--project", project])


# ── CLI interface ───────────────────────────────────────────────

def _cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="overstory CLI wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # sling
    p_sling = sub.add_parser("sling", help="Spawn a new agent")
    p_sling.add_argument("--task-id", required=True)
    p_sling.add_argument("--capability", required=True)
    p_sling.add_argument("--name", required=True)
    p_sling.add_argument("--description", required=True)
    p_sling.add_argument("--json", action="store_true")

    # status
    p_status = sub.add_parser("status", help="Get agent status")
    p_status.add_argument("--agent", default=None)
    p_status.add_argument("--json", action="store_true")

    # inspect
    p_inspect = sub.add_parser("inspect", help="Inspect agent details")
    p_inspect.add_argument("--agent", required=True)
    p_inspect.add_argument("--json", action="store_true")

    # list
    p_list = sub.add_parser("list", help="List active agents")
    p_list.add_argument("--json", action="store_true")

    # merge
    p_merge = sub.add_parser("merge", help="Merge agent worktree")
    p_merge.add_argument("--agent", required=True)
    p_merge.add_argument("--json", action="store_true")

    # mail send
    p_mail_send = sub.add_parser("mail-send", help="Send inter-agent mail")
    p_mail_send.add_argument("--from-agent", required=True)
    p_mail_send.add_argument("--to-agent", required=True)
    p_mail_send.add_argument("--message", required=True)
    p_mail_send.add_argument("--priority", default="normal")
    p_mail_send.add_argument("--json", action="store_true")

    # mail read
    p_mail_read = sub.add_parser("mail-read", help="Read agent mail")
    p_mail_read.add_argument("--agent", required=True)
    p_mail_read.add_argument("--json", action="store_true")

    # coordinator
    p_coord = sub.add_parser("coordinator-start", help="Start coordinator")
    p_coord.add_argument("--json", action="store_true")

    # supervisor
    p_sup = sub.add_parser("supervisor-start", help="Start project supervisor")
    p_sup.add_argument("--project", required=True)
    p_sup.add_argument("--json", action="store_true")

    args = parser.parse_args()
    client = OverstoryClient()

    try:
        if args.command == "sling":
            result = client.sling(args.task_id, args.capability, args.name, args.description)
        elif args.command == "status":
            result = client.status(args.agent)
        elif args.command == "inspect":
            result = client.inspect(args.agent)
        elif args.command == "list":
            result = client.list_agents()
        elif args.command == "merge":
            result = client.merge(args.agent)
        elif args.command == "mail-send":
            result = client.mail_send(args.from_agent, args.to_agent, args.message, args.priority)
        elif args.command == "mail-read":
            result = client.mail_read(args.agent)
        elif args.command == "coordinator-start":
            result = client.coordinator_start()
        elif args.command == "supervisor-start":
            result = client.supervisor_start(args.project)
        else:
            parser.print_help()
            sys.exit(1)

        print(json.dumps(result, indent=2))
    except OverstoryError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
