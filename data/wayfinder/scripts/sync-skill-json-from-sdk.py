#!/usr/bin/env python3
"""Sync wayfinder/skill.json commands + resources from wayfinder-paths-sdk.

This repo is the source of truth for the OpenClaw/ClawHub skill packaging, but
the CLI surface area is defined by the Wayfinder Paths SDK MCP server.

What this script updates:
- skill.json.commands (adds/removes tools, excluding runner)
- skill.json.resources.static/templates (from mcp.resource(...) URIs)
- skill.json.sdk_version (from wayfinder/sdk-version.md)

It does NOT attempt to rewrite SKILL.md or reference docs.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _skill_dir() -> Path:
    return _repo_root() / "wayfinder"


def _sdk_ref() -> str:
    ref = (_skill_dir() / "sdk-version.md").read_text(encoding="utf-8").strip()
    return ref or "main"


def _find_sdk_root(repo_root: Path) -> Path:
    env = os.getenv("WAYFINDER_SDK_PATH", "").strip()
    if env and Path(env).expanduser().is_dir():
        return Path(env).expanduser().resolve()

    sibling = (repo_root.parent / "wayfinder-paths-sdk").resolve()
    if sibling.is_dir():
        return sibling

    home = (Path.home() / "wayfinder-paths-sdk").resolve()
    if home.is_dir():
        return home

    raise FileNotFoundError(
        "Cannot find wayfinder-paths-sdk. Set WAYFINDER_SDK_PATH or clone it next to this repo."
    )


def _git_current_ref(sdk_root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(sdk_root), "symbolic-ref", "-q", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except subprocess.CalledProcessError:
        pass

    return subprocess.check_output(
        ["git", "-C", str(sdk_root), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def _git_checkout(sdk_root: Path, ref: str) -> None:
    subprocess.check_call(["git", "-C", str(sdk_root), "checkout", "--quiet", ref])


def _parse_server_py(server_py: str) -> tuple[list[str], list[str]]:
    # Tools are registered like: mcp.tool()(quote_swap)
    tool_names = re.findall(r"mcp\.tool\(\)\((\w+)\)", server_py)

    # Resources are registered like: mcp.resource("wayfinder://adapters")(list_adapters)
    resource_uris = re.findall(r'mcp\.resource\("([^"]+)"\)', server_py)

    return tool_names, resource_uris


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def main() -> int:
    repo_root = _repo_root()
    skill_json_path = _skill_dir() / "skill.json"
    sdk_root = _find_sdk_root(repo_root)

    sdk_ref = _sdk_ref()
    do_checkout = "--checkout" in sys.argv[1:]
    restore_ref = _git_current_ref(sdk_root) if do_checkout else None

    try:
        if do_checkout:
            _git_checkout(sdk_root, sdk_ref)

        server_path = sdk_root / "wayfinder_paths" / "mcp" / "server.py"
        if not server_path.exists():
            raise FileNotFoundError(f"Missing SDK MCP server: {server_path}")

        tool_names, resource_uris = _parse_server_py(
            server_path.read_text(encoding="utf-8")
        )

        # Exclude intentionally-undocumented tool(s)
        tool_names = [t for t in tool_names if t != "runner"]

        # Keep a stable preferred ordering; append new tools at the end.
        preferred = [
            "resource",
            "quote_swap",
            "execute",
            "hyperliquid",
            "hyperliquid_execute",
            "polymarket",
            "polymarket_execute",
            "run_strategy",
            "wallets",
            "run_script",
        ]
        tools_set = set(tool_names)

        commands: list[str] = []
        for c in preferred:
            if c == "resource" or c in tools_set:
                commands.append(c)

        extra = sorted([t for t in tool_names if t not in set(preferred)])
        commands.extend(extra)
        commands = _ordered_unique(commands)

        static_resources = sorted([u for u in resource_uris if "{" not in u])
        template_resources = sorted([u for u in resource_uris if "{" in u])

        skill = json.loads(skill_json_path.read_text(encoding="utf-8"))
        skill["sdk_version"] = sdk_ref
        skill["commands"] = commands
        skill.setdefault("resources", {})
        skill["resources"]["static"] = static_resources
        skill["resources"]["templates"] = template_resources

        skill_json_path.write_text(
            json.dumps(skill, indent=2) + "\n", encoding="utf-8"
        )

        print("Updated:", skill_json_path)
        print("SDK root:", sdk_root)
        print("SDK ref:", sdk_ref)
        if not do_checkout:
            print("note: SDK ref was not checked out (run with --checkout to sync from a specific ref).")
        print("commands:", ", ".join(commands))
        return 0
    finally:
        if restore_ref:
            try:
                _git_checkout(sdk_root, restore_ref)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
