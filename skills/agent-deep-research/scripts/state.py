# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""Manage workspace state for Gemini Deep Research.

Reads and manages .gemini-research.json which tracks research IDs,
file search store mappings, and upload operations.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console(stderr=True)

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def get_state_path() -> Path:
    """Return the path to the workspace state file."""
    return Path(".gemini-research.json")


def load_state() -> dict:
    """Load workspace state from disk, returning empty defaults if missing."""
    path = get_state_path()
    if not path.exists():
        return {"researchIds": [], "fileSearchStores": {}, "uploadOperations": {}}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        console.print(f"[yellow]Warning:[/yellow] failed to read state file: {exc}")
        return {"researchIds": [], "fileSearchStores": {}, "uploadOperations": {}}


def save_state(state: dict) -> None:
    """Persist workspace state to disk."""
    get_state_path().write_text(json.dumps(state, indent=2) + "\n")

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_show(_args: argparse.Namespace) -> None:
    """Display full workspace state."""
    state = load_state()
    use_json = getattr(_args, "json", False)

    if use_json:
        # Emit full state (excluding internal caches) as JSON to stdout
        output = {
            "researchIds": state.get("researchIds", []),
            "fileSearchStores": state.get("fileSearchStores", {}),
            "uploadOperations": state.get("uploadOperations", {}),
        }
        print(json.dumps(output, indent=2))
        return

    if not any(state.get(k) for k in ("researchIds", "fileSearchStores", "uploadOperations")):
        console.print("[dim]No workspace state found.[/dim]")
        return

    # Research IDs
    ids = state.get("researchIds", [])
    if ids:
        table = Table(title="Research Interactions")
        table.add_column("#", style="dim")
        table.add_column("Interaction ID")
        for i, rid in enumerate(ids, 1):
            table.add_row(str(i), rid)
        console.print(table)
    else:
        console.print("[dim]No research interactions tracked.[/dim]")

    console.print()

    # File search stores
    stores = state.get("fileSearchStores", {})
    if stores:
        table = Table(title="File Search Stores")
        table.add_column("Display Name")
        table.add_column("Resource Name")
        for name, resource in stores.items():
            table.add_row(name, resource)
        console.print(table)
    else:
        console.print("[dim]No file search stores tracked.[/dim]")

    console.print()

    # Upload operations
    ops = state.get("uploadOperations", {})
    if ops:
        table = Table(title="Upload Operations")
        table.add_column("ID", style="dim")
        table.add_column("Status")
        table.add_column("Path")
        table.add_column("Store")
        table.add_column("Progress")
        for op_id, op in ops.items():
            total = op.get("totalFiles", 0)
            done = op.get("completedFiles", 0) + op.get("skippedFiles", 0)
            pct = f"{round(done / total * 100)}%" if total else "N/A"
            status = op.get("status", "unknown")
            style = {"completed": "green", "failed": "red", "in_progress": "yellow"}.get(status, "")
            table.add_row(
                op_id[:12],
                f"[{style}]{status}[/{style}]" if style else status,
                op.get("path", ""),
                op.get("storeName", ""),
                pct,
            )
        console.print(table)
    else:
        console.print("[dim]No upload operations tracked.[/dim]")


def cmd_research(_args: argparse.Namespace) -> None:
    """List tracked research IDs."""
    state = load_state()
    ids = state.get("researchIds", [])
    use_json = getattr(_args, "json", False)

    if use_json:
        print(json.dumps(ids))
        return

    if not ids:
        console.print("[dim]No research interactions tracked.[/dim]")
        return
    table = Table(title="Research Interactions")
    table.add_column("#", style="dim")
    table.add_column("Interaction ID")
    for i, rid in enumerate(ids, 1):
        table.add_row(str(i), rid)
    console.print(table)


def cmd_stores(_args: argparse.Namespace) -> None:
    """List tracked store mappings."""
    state = load_state()
    stores = state.get("fileSearchStores", {})
    use_json = getattr(_args, "json", False)

    if use_json:
        result = [{"displayName": k, "name": v} for k, v in stores.items()]
        print(json.dumps(result))
        return

    if not stores:
        console.print("[dim]No file search stores tracked.[/dim]")
        return
    table = Table(title="File Search Stores")
    table.add_column("Display Name")
    table.add_column("Resource Name")
    for name, resource in stores.items():
        table.add_row(name, resource)
    console.print(table)


def cmd_clear(_args: argparse.Namespace) -> None:
    """Reset workspace state."""
    path = get_state_path()
    if not path.exists():
        console.print("[dim]No state file to clear.[/dim]")
        return

    if not _args.yes:
        if not sys.stdin.isatty():
            # Non-interactive context (e.g. AI agent): auto-accept
            pass
        else:
            console.print(f"This will delete [bold]{path}[/bold]. Use -y to skip this prompt.")
            try:
                answer = input("Continue? [y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(1)
            if answer not in ("y", "yes"):
                console.print("[dim]Aborted.[/dim]")
                return

    path.unlink()
    console.print("[green]Workspace state cleared.[/green]")


def cmd_gc(_args: argparse.Namespace) -> None:
    """Clean up orphaned context stores older than 24 hours."""
    state = load_state()
    ctx_stores: dict[str, str] = state.get("contextStores", {})

    if not ctx_stores:
        console.print("[dim]No context stores tracked.[/dim]")
        return

    now = time.time()
    stale: list[tuple[str, str]] = []  # (display_name, resource_name)

    for display_name, resource_name in ctx_stores.items():
        # Context store names follow the pattern: context-<hash>-<unix_timestamp>
        match = re.search(r"-(\d{10,})$", display_name)
        if not match:
            continue
        created_ts = int(match.group(1))
        age_hours = (now - created_ts) / 3600
        if age_hours > 24:
            stale.append((display_name, resource_name))

    if not stale:
        console.print("[dim]No context stores older than 24h found.[/dim]")
        return

    # Show what would be cleaned up
    table = Table(title="Stale Context Stores (>24h old)")
    table.add_column("Display Name")
    table.add_column("Resource Name")
    table.add_column("Age")
    for display_name, resource_name in stale:
        match = re.search(r"-(\d{10,})$", display_name)
        if match:
            age_h = (now - int(match.group(1))) / 3600
            age_str = f"{age_h:.1f}h"
        else:
            age_str = "unknown"
        table.add_row(display_name, resource_name, age_str)
    console.print(table)

    # Confirm deletion
    if not _args.yes:
        if sys.stdin.isatty():
            console.print(f"\nThis will delete {len(stale)} context store(s) via the Gemini API.")
            try:
                answer = input("Continue? [y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(1)
            if answer not in ("y", "yes"):
                console.print("[dim]Aborted.[/dim]")
                return
        # Non-TTY: proceed without prompting

    # Lazy-import the API client only when we actually need to delete
    from google import genai

    api_key: str | None = None
    for var in ("GEMINI_DEEP_RESEARCH_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        api_key = os.environ.get(var)
        if api_key:
            break
    if not api_key:
        console.print("[red]Error:[/red] No API key found for store deletion.")
        console.print("Set one of: GEMINI_DEEP_RESEARCH_API_KEY, GOOGLE_API_KEY, GEMINI_API_KEY")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    deleted = 0
    for display_name, resource_name in stale:
        try:
            client.file_search_stores.delete(name=resource_name)
            deleted += 1
        except Exception as exc:
            console.print(f"[yellow]Warning:[/yellow] Failed to delete {display_name}: {exc}")
            # Still remove from local state to prevent permanent failure loop
            # (e.g., store was already deleted in cloud console)

        # Remove from state regardless of API success/failure
        state = load_state()
        ctx = state.get("contextStores", {})
        ctx.pop(display_name, None)
        fs = state.get("fileSearchStores", {})
        fs.pop(display_name, None)
        hc = state.get("_hashCache", {})
        hc.pop(resource_name, None)
        save_state(state)

    console.print(f"[green]Cleaned up {deleted}/{len(stale)} context store(s).[/green]")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="state",
        description="Manage Gemini Deep Research workspace state (.gemini-research.json)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json",
        help="Output JSON to stdout for programmatic consumption",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("show", help="Display full workspace state (default)")
    sub.add_parser("research", help="List tracked research interaction IDs")
    sub.add_parser("stores", help="List tracked file search store mappings")

    clear_p = sub.add_parser("clear", help="Reset workspace state")
    clear_p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    gc_p = sub.add_parser("gc", help="Clean up orphaned context stores (>24h old)")
    gc_p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    commands = {
        "show": cmd_show,
        "research": cmd_research,
        "stores": cmd_stores,
        "clear": cmd_clear,
        "gc": cmd_gc,
        None: cmd_show,  # default
    }

    handler = commands.get(args.command, cmd_show)
    handler(args)


if __name__ == "__main__":
    main()
