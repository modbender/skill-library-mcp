#!/usr/bin/env python3
"""Initialize clawflow within an OpenClaw agent workspace.

Adds the tasks/ and mailbox/ directories (inbox, outbox, archive) to an agent's
workspace. Agent identity and peer discovery come from openclaw.json config —
not from custom files.

Usage:
    python3 init.py [--workspace DIR]

Examples:
    python3 init.py                                    → uses ~/.openclaw/workspace
    python3 init.py --workspace ~/.openclaw/workspace-work

Prerequisites:
    - Agent should be configured: openclaw agents list
    - Workspace should exist: openclaw setup (or openclaw agents add <n>)
      (init.py will create the directory if it doesn't exist, with a warning)
"""

import argparse
import json
import subprocess
from pathlib import Path


def discover_workspace() -> Path | None:
    """Try to get the default workspace from openclaw config."""
    try:
        result = subprocess.run(
            ["openclaw", "config", "get", "agents.defaults.workspace"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).expanduser()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def list_agents() -> list[dict] | None:
    """Try to list configured agents via openclaw CLI."""
    try:
        result = subprocess.run(
            ["openclaw", "agents", "list", "--json"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return None


def init_clawflow(workspace: Path):
    """Create the tasks/ directory inside an OpenClaw workspace."""
    # Create workspace dir if missing (with warning)
    if not workspace.exists():
        print(f"  Warning: Workspace not found at {workspace}")
        print(f"  Creating it. Consider running `openclaw setup` for full workspace init.")
        workspace.mkdir(parents=True, exist_ok=True)
        print(f"  Created {workspace}/")

    # Create clawflow directories
    dirs = {
        "mailbox/inbox":   "incoming messages (logged before processing)",
        "mailbox/outbox":  "outgoing messages (dispatches + replies sent)",
        "mailbox/archive": "processed messages (durable audit trail)",
        "tasks":           "task working directories (DAGs, results)",
    }
    for subdir, desc in dirs.items():
        d = workspace / subdir
        created = not d.exists()
        d.mkdir(parents=True, exist_ok=True)
        status = "Created" if created else "Exists "
        print(f"  {status} {d}/  ← {desc}")

    # Check for expected OpenClaw files
    oc_files = ["IDENTITY.md", "AGENTS.md", "SOUL.md"]
    present = [f for f in oc_files if (workspace / f).exists()]
    missing = [f for f in oc_files if f not in present]

    if missing:
        print(f"\n  Note: Missing OpenClaw files: {', '.join(missing)}")
        print(f"  Run `openclaw setup` to create them.")

    print(f"\nClawflow ready in {workspace}")
    print(f"  mailbox/   → agent-level message log (inbox, outbox, archive)")
    print(f"  tasks/     → per-task DAG state and results")
    print()

    # Show available agents
    agents = list_agents()
    if agents:
        print("Available agents (from openclaw agents list):")
        for a in agents:
            agent_id = a.get("id", "?")
            name = a.get("name") or a.get("identity", {}).get("name", "")
            label = f" ({name})" if name else ""
            print(f"  - {agent_id}{label}")
    else:
        print("Tip: run `openclaw agents list` to see available peer agents")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize clawflow in an OpenClaw agent workspace",
    )
    parser.add_argument(
        "--workspace", default=None,
        help="Agent workspace path (default: from openclaw config, "
             "fallback ~/.openclaw/workspace)",
    )
    args = parser.parse_args()

    if args.workspace:
        workspace = Path(args.workspace).expanduser()
    else:
        workspace = discover_workspace()
        if workspace is None:
            workspace = Path.home() / ".openclaw" / "workspace"
            print(f"Could not read openclaw config; using default: {workspace}")

    print(f"Initializing clawflow in: {workspace}")
    init_clawflow(workspace)


if __name__ == "__main__":
    main()
