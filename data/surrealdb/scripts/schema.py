# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rich>=13.0.0",
#   "websockets>=12.0",
# ]
# ///
"""SurrealDB schema introspection and export tool.

Subcommands:
  export   -- Export the complete schema as SurrealQL DEFINE statements.
  inspect  -- Structured view of tables, fields, indexes, events, and access.
  diff     -- Compare two SurrealQL schema files and show differences.
"""

from __future__ import annotations

import argparse
import asyncio
import difflib
import json
import os
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

stderr_console = Console(stderr=True)

DEFAULT_ENDPOINT = "ws://localhost:8000"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(name: str) -> str | None:
    val = os.environ.get(name, "").strip()
    return val if val else None


import re as _re

_SAFE_IDENT = _re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _sanitize_identifier(name: str) -> str:
    """Validate that a name is a safe SurrealQL identifier.

    Prevents SurrealQL injection by rejecting names that contain
    anything other than alphanumeric characters and underscores.
    """
    name = name.strip()
    if not name or not _SAFE_IDENT.match(name):
        raise ValueError(
            f"Invalid identifier: {name!r}. "
            "Identifiers must match [a-zA-Z_][a-zA-Z0-9_]*."
        )
    return name


async def _ws_query(endpoint: str, user: str, password: str, ns: str, db: str, query: str) -> Any:
    """Connect via WebSocket RPC, authenticate, USE ns/db, and execute a query."""
    import websockets  # type: ignore[import-untyped]

    ws_ep = endpoint.rstrip("/") + "/rpc"
    async with websockets.connect(ws_ep, open_timeout=10, close_timeout=5) as ws:
        # Sign in
        signin_msg = json.dumps({
            "id": "signin",
            "method": "signin",
            "params": [{"user": user, "pass": password}],
        })
        await ws.send(signin_msg)
        signin_resp = json.loads(await ws.recv())
        if signin_resp.get("error"):
            raise RuntimeError(f"Auth failed: {signin_resp['error']}")

        # USE
        use_msg = json.dumps({
            "id": "use",
            "method": "use",
            "params": [ns, db],
        })
        await ws.send(use_msg)
        use_resp = json.loads(await ws.recv())
        if use_resp.get("error"):
            raise RuntimeError(f"USE failed: {use_resp['error']}")

        # Query
        query_msg = json.dumps({
            "id": "query",
            "method": "query",
            "params": [query],
        })
        await ws.send(query_msg)
        query_resp = json.loads(await ws.recv())
        if query_resp.get("error"):
            raise RuntimeError(f"Query failed: {query_resp['error']}")
        return query_resp.get("result")


def run_query(endpoint: str, user: str, password: str, ns: str, db: str, query: str) -> Any:
    """Synchronous wrapper for WebSocket query."""
    return asyncio.get_event_loop().run_until_complete(
        _ws_query(endpoint, user, password, ns, db, query),
    )


def _extract_result(raw: Any) -> Any:
    """Extract the inner result from a SurrealDB query response list."""
    if isinstance(raw, list) and raw:
        first = raw[0]
        if isinstance(first, dict) and "result" in first:
            return first["result"]
        return first
    return raw


# ---------------------------------------------------------------------------
# export subcommand
# ---------------------------------------------------------------------------

def cmd_export(args: argparse.Namespace) -> None:
    """Export the complete database schema as SurrealQL DEFINE statements."""
    ep = args.endpoint or _env("SURREAL_ENDPOINT") or DEFAULT_ENDPOINT
    user = args.user or _env("SURREAL_USER") or "root"
    password = args.password or _env("SURREAL_PASS") or "root"
    ns = args.ns or _env("SURREAL_NS") or "test"
    db = args.db or _env("SURREAL_DB") or "test"

    stderr_console.print(f"Exporting schema from {ep} / {ns} / {db} ...")

    try:
        db_info_raw = run_query(ep, user, password, ns, db, "INFO FOR DB")
    except Exception as exc:
        stderr_console.print(f"[red]Failed to query database:[/red] {exc}")
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)

    db_info = _extract_result(db_info_raw)
    statements: list[str] = []

    # Header
    statements.append(f"-- Schema export for namespace: {ns}, database: {db}")
    statements.append(f"-- Endpoint: {ep}")
    statements.append("")

    if not isinstance(db_info, dict):
        stderr_console.print("[yellow]Unexpected INFO FOR DB format. Dumping raw result.[/yellow]")
        raw_str = json.dumps(db_info_raw, indent=2, default=str)
        statements.append(f"-- Raw INFO FOR DB:\n-- {raw_str}")
        _output_schema(statements, args)
        return

    # Iterate over known schema categories
    category_order = ["accesses", "analyzers", "functions", "models", "params", "tables", "users"]
    # Some versions use shorthand keys
    key_aliases = {"ac": "accesses", "az": "analyzers", "fn": "functions", "ml": "models",
                   "pa": "params", "tb": "tables", "us": "users"}

    normalized: dict[str, dict] = {}
    for k, v in db_info.items():
        canon = key_aliases.get(k, k)
        if isinstance(v, dict):
            normalized[canon] = v

    for category in category_order:
        items = normalized.get(category, {})
        if not items:
            continue
        statements.append(f"-- {category.upper()}")
        for name, definition in sorted(items.items()):
            if isinstance(definition, str):
                stmt = definition.rstrip(";") + ";"
                statements.append(stmt)
            else:
                statements.append(f"-- {name}: {json.dumps(definition, default=str)}")
        statements.append("")

    # Per-table detail
    tables = normalized.get("tables", {})
    for tbl_name in sorted(tables.keys()):
        statements.append(f"-- TABLE: {tbl_name}")
        try:
            tbl_info_raw = run_query(ep, user, password, ns, db, f"INFO FOR TABLE {_sanitize_identifier(tbl_name)}")
            tbl_info = _extract_result(tbl_info_raw)
            if isinstance(tbl_info, dict):
                for section_key in ("fields", "fd", "indexes", "ix", "events", "ev", "lives", "lv"):
                    section = tbl_info.get(section_key)
                    if isinstance(section, dict) and section:
                        for item_name, item_def in sorted(section.items()):
                            if isinstance(item_def, str):
                                statements.append(item_def.rstrip(";") + ";")
                            else:
                                statements.append(f"-- {item_name}: {json.dumps(item_def, default=str)}")
            else:
                statements.append(f"-- (raw) {json.dumps(tbl_info, default=str)}")
        except Exception as exc:
            statements.append(f"-- Error fetching table info: {exc}")
        statements.append("")

    _output_schema(statements, args)


def _output_schema(statements: list[str], args: argparse.Namespace) -> None:
    """Write schema to stderr (pretty), stdout (JSON), and optionally to a file."""
    schema_text = "\n".join(statements)

    # Rich syntax highlighting on stderr
    stderr_console.print(Syntax(schema_text, "sql", theme="monokai", line_numbers=True))

    # Machine-readable JSON on stdout
    output = {"schema": schema_text, "line_count": len(statements)}

    if hasattr(args, "output_dir") and args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "schema.surql"
        out_file.write_text(schema_text)
        stderr_console.print(f"Schema written to {out_file}")
        output["file"] = str(out_file)

    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# inspect subcommand
# ---------------------------------------------------------------------------

def cmd_inspect(args: argparse.Namespace) -> None:
    """Structured inspection of the database schema."""
    ep = args.endpoint or _env("SURREAL_ENDPOINT") or DEFAULT_ENDPOINT
    user = args.user or _env("SURREAL_USER") or "root"
    password = args.password or _env("SURREAL_PASS") or "root"
    ns = args.ns or _env("SURREAL_NS") or "test"
    db = args.db or _env("SURREAL_DB") or "test"

    stderr_console.print(f"Inspecting schema on {ep} / {ns} / {db} ...")

    try:
        db_info_raw = run_query(ep, user, password, ns, db, "INFO FOR DB")
    except Exception as exc:
        stderr_console.print(f"[red]Failed:[/red] {exc}")
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)

    db_info = _extract_result(db_info_raw)
    key_aliases = {"ac": "accesses", "az": "analyzers", "fn": "functions", "ml": "models",
                   "pa": "params", "tb": "tables", "us": "users"}

    normalized: dict[str, dict] = {}
    if isinstance(db_info, dict):
        for k, v in db_info.items():
            canon = key_aliases.get(k, k)
            if isinstance(v, dict):
                normalized[canon] = v

    # Build a Rich tree for stderr
    tree = Tree(f"[bold]Database: {ns}/{db}[/bold]")
    inspection: dict[str, Any] = {"namespace": ns, "database": db, "tables": {}}

    tables = normalized.get("tables", {})
    for tbl_name in sorted(tables.keys()):
        tbl_branch = tree.add(f"[cyan]{tbl_name}[/cyan]")
        tbl_detail: dict[str, Any] = {"fields": {}, "indexes": {}, "events": {}, "accesses": {}}

        try:
            tbl_info_raw = run_query(ep, user, password, ns, db, f"INFO FOR TABLE {_sanitize_identifier(tbl_name)}")
            tbl_info = _extract_result(tbl_info_raw)
            if isinstance(tbl_info, dict):
                section_map = {
                    "fields": ["fields", "fd"],
                    "indexes": ["indexes", "ix"],
                    "events": ["events", "ev"],
                    "accesses": ["accesses", "ac"],
                }
                for label, keys in section_map.items():
                    section_data: dict = {}
                    for key in keys:
                        if key in tbl_info and isinstance(tbl_info[key], dict):
                            section_data.update(tbl_info[key])
                    if section_data:
                        sec_branch = tbl_branch.add(f"[yellow]{label}[/yellow]")
                        for item_name, item_def in sorted(section_data.items()):
                            display = item_def if isinstance(item_def, str) else json.dumps(item_def, default=str)
                            sec_branch.add(f"{item_name}: {display}")
                        tbl_detail[label] = section_data
        except Exception as exc:
            tbl_branch.add(f"[red]Error: {exc}[/red]")
            tbl_detail["error"] = str(exc)

        inspection["tables"][tbl_name] = tbl_detail

    # Summary table
    summary_table = Table(title="Schema Summary", show_lines=True)
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value")
    summary_table.add_row("Namespace", ns)
    summary_table.add_row("Database", db)
    summary_table.add_row("Tables", str(len(tables)))
    total_fields = sum(len(t.get("fields", {})) for t in inspection["tables"].values())
    total_indexes = sum(len(t.get("indexes", {})) for t in inspection["tables"].values())
    summary_table.add_row("Total Fields", str(total_fields))
    summary_table.add_row("Total Indexes", str(total_indexes))

    stderr_console.print(summary_table)
    stderr_console.print(tree)

    # JSON on stdout
    print(json.dumps(inspection, indent=2, default=str))


# ---------------------------------------------------------------------------
# diff subcommand
# ---------------------------------------------------------------------------

def cmd_diff(args: argparse.Namespace) -> None:
    """Compare two SurrealQL schema files."""
    file1 = Path(args.file1)
    file2 = Path(args.file2)

    if not file1.exists():
        stderr_console.print(f"[red]File not found:[/red] {file1}")
        print(json.dumps({"error": f"File not found: {file1}"}))
        sys.exit(1)
    if not file2.exists():
        stderr_console.print(f"[red]File not found:[/red] {file2}")
        print(json.dumps({"error": f"File not found: {file2}"}))
        sys.exit(1)

    lines1 = file1.read_text().splitlines(keepends=True)
    lines2 = file2.read_text().splitlines(keepends=True)

    diff_lines = list(difflib.unified_diff(
        lines1, lines2,
        fromfile=str(file1),
        tofile=str(file2),
        lineterm="",
    ))

    # Categorize changes
    additions = [l for l in diff_lines if l.startswith("+") and not l.startswith("+++")]
    removals = [l for l in diff_lines if l.startswith("-") and not l.startswith("---")]

    diff_text = "\n".join(diff_lines) if diff_lines else "(no differences)"

    # Rich output on stderr
    if diff_lines:
        stderr_console.print(Panel(f"Differences: {file1.name} vs {file2.name}", style="bold"))
        stderr_console.print(Syntax(diff_text, "diff", theme="monokai"))
        stderr_console.print(f"\n[green]+{len(additions)} additions[/green], [red]-{len(removals)} removals[/red]")
    else:
        stderr_console.print("[green]Schemas are identical.[/green]")

    # JSON on stdout
    output = {
        "file1": str(file1),
        "file2": str(file2),
        "identical": len(diff_lines) == 0,
        "additions": len(additions),
        "removals": len(removals),
        "diff": diff_text,
    }
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schema",
        description="SurrealDB schema introspection and export tool.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Shared connection args
    def add_connection_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--endpoint", type=str, default=None, help="SurrealDB endpoint (default: SURREAL_ENDPOINT or ws://localhost:8000)")
        p.add_argument("--user", type=str, default=None, help="Username (default: SURREAL_USER or root)")
        p.add_argument("--pass", dest="password", type=str, default=None, help="Password (default: SURREAL_PASS or root)")
        p.add_argument("--ns", type=str, default=None, help="Namespace (default: SURREAL_NS or test)")
        p.add_argument("--db", type=str, default=None, help="Database (default: SURREAL_DB or test)")

    # export
    export_parser = subparsers.add_parser("export", help="Export the complete schema as SurrealQL")
    add_connection_args(export_parser)
    export_parser.add_argument("--output-dir", type=str, default=None, help="Directory to write schema.surql file")

    # inspect
    inspect_parser = subparsers.add_parser("inspect", help="Structured schema inspection")
    add_connection_args(inspect_parser)

    # diff
    diff_parser = subparsers.add_parser("diff", help="Compare two SurrealQL schema files")
    diff_parser.add_argument("--file1", type=str, required=True, help="First schema file")
    diff_parser.add_argument("--file2", type=str, required=True, help="Second schema file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    dispatch = {
        "export": cmd_export,
        "inspect": cmd_inspect,
        "diff": cmd_diff,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
