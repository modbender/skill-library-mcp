#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold an MCP server starter package.")
    parser.add_argument("--input", required=False, help="Path to JSON input.")
    parser.add_argument("--output", required=True, help="Path to output artifact.")
    parser.add_argument("--format", choices=["json", "md", "csv"], default="json")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing scaffold files.")
    parser.add_argument(
        "--allow-outside-workspace",
        action="store_true",
        help="Allow scaffold_root to resolve outside the current workspace.",
    )
    return parser.parse_args()


def load_payload(path: str | None, max_input_bytes: int = MAX_INPUT_BYTES) -> dict:
    if not path:
        return {}
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.stat().st_size > max_input_bytes:
        raise ValueError(
            f"Input file exceeds {max_input_bytes} bytes: {input_path}"
        )
    return json.loads(input_path.read_text(encoding="utf-8"))


def normalize_name(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def resolve_path_in_workspace(
    raw_path: Path,
    workspace_root: Path,
    label: str,
    allow_outside_workspace: bool,
) -> Path:
    resolved = raw_path.resolve()
    if allow_outside_workspace:
        return resolved
    try:
        resolved.relative_to(workspace_root)
    except ValueError as exc:
        raise ValueError(
            f"{label} must be inside workspace root: {workspace_root}"
        ) from exc
    return resolved


def render(result: dict, output_path: Path, fmt: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return

    if fmt == "md":
        lines = [
            f"# {result['summary']}",
            "",
            f"- status: {result['status']}",
            "",
            "## Planned Files",
        ]
        for item in result["details"]["file_map"]:
            lines.append(f"- {item}")
        lines.extend(["", "## Tools"])
        for tool in result["details"]["tools"]:
            lines.append(f"- {tool['name']}: {tool['description']}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "description"])
        for tool in result["details"]["tools"]:
            writer.writerow([tool["name"], tool["description"]])


def maybe_write_scaffold(root: Path, file_map: list[str], dry_run: bool) -> None:
    if dry_run:
        return
    for relative_path in file_map:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".py":
            path.write_text("# Starter file\n", encoding="utf-8")
        elif path.suffix == ".json":
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("# Starter document\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    workspace_root = Path.cwd().resolve()
    server_name = normalize_name(str(payload.get("server_name", "mcp-server"))) or "mcp-server"
    tools = payload.get("tools", [])
    if not isinstance(tools, list):
        tools = []

    normalized_tools = []
    for tool in tools:
        normalized_tools.append(
            {
                "name": normalize_name(str(tool.get("name", "tool"))),
                "description": str(tool.get("description", "No description provided")),
            }
        )

    raw_scaffold_root = Path(payload.get("scaffold_root", f"artifacts/{server_name}"))
    scaffold_root = resolve_path_in_workspace(
        raw_scaffold_root,
        workspace_root,
        "scaffold_root",
        args.allow_outside_workspace,
    )
    file_map = [
        "server.py",
        "tool_registry.py",
        "schemas/tools.json",
        "README.md",
    ]
    maybe_write_scaffold(scaffold_root, file_map, args.dry_run)

    result = {
        "status": "ok",
        "summary": f"Prepared MCP scaffold for '{server_name}'",
        "artifacts": [str(Path(args.output))],
        "details": {
            "server_name": server_name,
            "scaffold_root": str(scaffold_root),
            "file_map": file_map,
            "tools": normalized_tools,
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
