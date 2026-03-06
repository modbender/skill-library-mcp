# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""Manage Gemini File Search stores (corpora).

Provides create, list, delete, and query operations for file search
stores used with Gemini RAG grounding.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types
from rich.console import Console
from rich.table import Table

console = Console(stderr=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_api_key() -> str:
    """Resolve the API key from environment variables."""
    for var in ("GEMINI_DEEP_RESEARCH_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        key = os.environ.get(var)
        if key:
            return key
    console.print("[red]Error:[/red] No API key found.")
    console.print("Set one of: GEMINI_DEEP_RESEARCH_API_KEY, GOOGLE_API_KEY, GEMINI_API_KEY")
    sys.exit(1)


def get_client() -> genai.Client:
    """Create an authenticated GenAI client."""
    return genai.Client(api_key=get_api_key())


def get_state_path() -> Path:
    """Return the path to the workspace state file."""
    return Path(".gemini-research.json")


def load_state() -> dict:
    path = get_state_path()
    if not path.exists():
        return {"researchIds": [], "fileSearchStores": {}, "uploadOperations": {}}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {"researchIds": [], "fileSearchStores": {}, "uploadOperations": {}}


def save_state(state: dict) -> None:
    get_state_path().write_text(json.dumps(state, indent=2) + "\n")


def get_default_model() -> str:
    """Return the model to use for file search queries."""
    return os.environ.get(
        "GEMINI_DEEP_RESEARCH_MODEL",
        os.environ.get("GEMINI_MODEL", "gemini-3.1-pro-preview"),
    )

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_create(args: argparse.Namespace) -> None:
    """Create a new file search store."""
    client = get_client()
    display_name: str = args.name

    console.print(f"Creating store [bold]{display_name}[/bold]...")
    store = client.file_search_stores.create(config={"display_name": display_name})

    # Persist mapping
    state = load_state()
    state.setdefault("fileSearchStores", {})[display_name] = store.name
    save_state(state)

    console.print(f"[green]Created store:[/green] {store.name} ({display_name})")
    # Also emit machine-readable output to stdout
    print(json.dumps({"name": store.name, "displayName": display_name}))


def cmd_list(_args: argparse.Namespace) -> None:
    """List all file search stores."""
    client = get_client()

    stores: list[dict] = []
    for store in client.file_search_stores.list():
        display = getattr(store, "display_name", None)
        if display is None:
            cfg = getattr(store, "config", None)
            display = getattr(cfg, "display_name", "") if cfg else ""
        stores.append({"name": store.name, "displayName": display})

    if not stores:
        console.print("[dim]No file search stores found.[/dim]")
        print(json.dumps([]))
        return

    table = Table(title="File Search Stores")
    table.add_column("Resource Name")
    table.add_column("Display Name")
    for s in stores:
        table.add_row(s["name"], s["displayName"])
    console.print(table)

    # Machine-readable on stdout
    print(json.dumps(stores, indent=2))


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete a file search store."""
    client = get_client()
    store_id: str = args.id
    force: bool = args.force

    if not force:
        if not sys.stdin.isatty():
            # Non-interactive context (e.g. AI agent): auto-accept
            force = True
        else:
            console.print(f"Deleting store [bold]{store_id}[/bold]. Use --force to skip this prompt.")
            try:
                answer = input("Continue? [y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(1)
            if answer not in ("y", "yes"):
                console.print("[dim]Aborted.[/dim]")
                return

    console.print(f"Deleting store [bold]{store_id}[/bold]...")
    client.file_search_stores.delete(name=store_id, config={"force": force})
    console.print(f"[green]Deleted store:[/green] {store_id}")

    # Clean up local state: remove the store mapping
    state = load_state()
    stores = state.get("fileSearchStores", {})
    removed = [k for k, v in stores.items() if v == store_id or k == store_id]
    for k in removed:
        del stores[k]
    if removed:
        save_state(state)
        console.print(f"[dim]Removed {len(removed)} local mapping(s).[/dim]")


def cmd_query(args: argparse.Namespace) -> None:
    """Query a file search store with grounded generation."""
    import time as _time

    client = get_client()
    store_name: str = args.id
    question: str = args.question
    model = get_default_model()
    output_dir = getattr(args, "output_dir", None)

    console.print(f"Querying store [bold]{store_name}[/bold]...")
    start = _time.monotonic()
    try:
        response = client.models.generate_content(
            model=model,
            contents=question,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name],
                        )
                    )
                ]
            ),
        )
        text = response.text if response.text else "No response generated."
    except Exception as exc:
        console.print(f"[red]Query failed:[/red] {exc}")
        sys.exit(1)
    duration = int(_time.monotonic() - start)

    if output_dir:
        import re
        base = Path(output_dir)
        ts = _time.strftime("%Y%m%d-%H%M%S")
        query_dir = base / f"query-{ts}"
        query_dir.mkdir(parents=True, exist_ok=True)

        (query_dir / "response.md").write_text(text)
        metadata = {
            "store": store_name,
            "question": question,
            "model": model,
            "response_size_bytes": len(text.encode("utf-8")),
            "duration_seconds": duration,
        }
        (query_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

        summary_text = text[:200].replace("\n", " ").strip()
        if len(text) > 200:
            summary_text += "..."
        compact = {
            "output_dir": str(query_dir),
            "response_file": str(query_dir / "response.md"),
            "response_size_bytes": len(text.encode("utf-8")),
            "duration_seconds": duration,
            "summary": summary_text,
        }
        console.print(f"[green]Results saved to:[/green] {query_dir}")
        print(json.dumps(compact))
        return

    # Output answer to stdout (rich formatting on stderr)
    console.print("[green]Answer:[/green]")
    print(text)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="store",
        description="Manage Gemini File Search stores",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    create_p = sub.add_parser("create", help="Create a new file search store")
    create_p.add_argument("name", help="Display name for the store")

    # list
    sub.add_parser("list", help="List all file search stores")

    # delete
    del_p = sub.add_parser("delete", help="Delete a file search store")
    del_p.add_argument("id", help="Resource name of the store (e.g. fileSearchStores/...)")
    del_p.add_argument("--force", action="store_true", help="Force delete even if store contains documents")

    # query
    query_p = sub.add_parser("query", help="Query a file search store")
    query_p.add_argument("id", help="Resource name of the store")
    query_p.add_argument("question", help="The question to ask")
    query_p.add_argument(
        "--output-dir", metavar="DIR",
        help="Save response and metadata to this directory",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "delete": cmd_delete,
        "query": cmd_query,
    }

    handler = commands.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    handler(args)


if __name__ == "__main__":
    main()
