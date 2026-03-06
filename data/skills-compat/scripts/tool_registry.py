#!/usr/bin/env python3
"""Unified tool registry for nanobot, overstory, and Ollama.

Singleton registry that collects tool definitions from OpenClaw skills,
MCP servers, or manual registration, then exports in each system's
native format.

Importable as a module or runnable as a CLI tool.
Logs to stderr, structured JSON output to stdout.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("tool_registry")


@dataclass
class ToolDef:
    name: str
    skill: str = ""
    description: str = ""
    schema: Dict[str, Any] = field(default_factory=dict)
    source: str = "skill"  # "skill" | "mcp" | "manual"
    capability: str = ""
    handler: Optional[str] = None  # serialized reference; actual callable stored separately

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("handler", None)
        return d


class ToolRegistry:
    """Singleton tool registry."""

    _instance: Optional["ToolRegistry"] = None
    _handlers: Dict[str, Callable] = {}

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDef] = {}

    @classmethod
    def instance(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (useful for testing)."""
        cls._instance = None
        cls._handlers = {}

    def register_tool(
        self,
        name: str,
        skill: str,
        handler: Optional[Callable] = None,
        schema: Optional[Dict[str, Any]] = None,
        description: str = "",
        capability: str = "",
    ) -> None:
        td = ToolDef(
            name=name,
            skill=skill,
            description=description,
            schema=schema or {},
            source="manual" if not skill else "skill",
            capability=capability,
        )
        self._tools[name] = td
        if handler is not None:
            self._handlers[name] = handler
        log.info("registered tool: %s (skill=%s)", name, skill)

    def register_mcp_tool(
        self,
        name: str,
        mcp_server: str,
        schema: Dict[str, Any],
        description: str = "",
    ) -> None:
        td = ToolDef(
            name=name,
            skill=mcp_server,
            description=description,
            schema=schema,
            source="mcp",
        )
        self._tools[name] = td
        log.info("registered MCP tool: %s (server=%s)", name, mcp_server)

    def register_skill_tools(
        self,
        skill_name: str,
        skills_dir: str | Path,
    ) -> int:
        """Auto-register tools declared in a skill's _meta.json.

        Returns number of tools registered.
        """
        from skill_loader import SkillLoader  # local import to avoid circular at module level

        loader = SkillLoader()
        try:
            sd = loader.load_skill(Path(skills_dir) / skill_name)
        except FileNotFoundError:
            log.warning("skill not found: %s in %s", skill_name, skills_dir)
            return 0

        count = 0
        for tool_name in sd.tools:
            self.register_tool(
                name=tool_name,
                skill=skill_name,
                description=f"Tool from {sd.display_name}",
                capability="",
            )
            count += 1
        log.info("registered %d tools from skill %s", count, skill_name)
        return count

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        td = self._tools.get(name)
        return td.to_dict() if td else None

    def list_tools(self, capability_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        tools = self._tools.values()
        if capability_filter:
            tools = [t for t in tools if t.capability == capability_filter]
        return [t.to_dict() for t in sorted(tools, key=lambda t: t.name)]

    def execute_tool(self, name: str, params: Dict[str, Any]) -> Any:
        """Execute a registered tool's handler."""
        handler = self._handlers.get(name)
        if handler is None:
            return {"ok": False, "error": f"no handler registered for tool '{name}'"}
        try:
            return handler(**params)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def export_for_nanobot(self) -> List[Dict[str, Any]]:
        """Export registry in nanobot tool format."""
        return [
            {
                "name": td.name,
                "skill": td.skill,
                "description": td.description,
                "parameters": td.schema,
            }
            for td in sorted(self._tools.values(), key=lambda t: t.name)
        ]

    def export_for_overstory(self) -> List[Dict[str, Any]]:
        """Export registry in overstory tool format."""
        return [
            {
                "tool": td.name,
                "source_skill": td.skill,
                "description": td.description,
                "input_schema": td.schema,
            }
            for td in sorted(self._tools.values(), key=lambda t: t.name)
        ]

    def export_for_ollama(self) -> List[Dict[str, Any]]:
        """Export as Ollama tool-calling format (JSON schema for functions)."""
        return [
            {
                "type": "function",
                "function": {
                    "name": td.name,
                    "description": td.description,
                    "parameters": td.schema if td.schema else {"type": "object", "properties": {}},
                },
            }
            for td in sorted(self._tools.values(), key=lambda t: t.name)
        ]


def _json_out(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified tool registry")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--json", action="store_true", dest="as_json")
    p_list.add_argument("--capability", default=None)

    p_export = sub.add_parser("export")
    p_export.add_argument("--format", required=True, choices=["nanobot", "overstory", "ollama"])

    p_reg = sub.add_parser("register")
    p_reg.add_argument("--skill", required=True, help="Skill name")
    p_reg.add_argument("--dir", required=True, help="Skills directory")

    args = parser.parse_args()
    registry = ToolRegistry.instance()

    if args.command == "list":
        _json_out(registry.list_tools(args.capability))

    elif args.command == "export":
        exporters = {
            "nanobot": registry.export_for_nanobot,
            "overstory": registry.export_for_overstory,
            "ollama": registry.export_for_ollama,
        }
        _json_out(exporters[args.format]())

    elif args.command == "register":
        count = registry.register_skill_tools(args.skill, args.dir)
        _json_out({"ok": True, "skill": args.skill, "tools_registered": count})
        _json_out(registry.list_tools())


if __name__ == "__main__":
    main()
