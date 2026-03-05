#!/usr/bin/env python3
"""Agent Context Generator — produces gateway-context.md and skills-manifest.json for overstory agent overlays.

The generated context document tells agents what tools and skills are available,
how to invoke them, and what privilege tiers apply.

Outputs JSON to stdout, logs to stderr.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

NANOBOT_GATEWAY_URL = os.environ.get("NANOBOT_GATEWAY_URL", "http://localhost:18800")
NANOBOT_WORKSPACE = Path(os.environ.get("NANOBOT_WORKSPACE", "/Users/ghost/.openclaw/workspace"))
NANOBOT_SKILLS_DIR = Path(os.environ.get("NANOBOT_SKILLS_DIR", "/Users/ghost/.openclaw/workspace/skills"))

logging.basicConfig(
    level=os.environ.get("GATEWAY_TOOLS_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("generate-agent-context")


# ---------------------------------------------------------------------------
# Reuse helpers from gateway_tools (or inline if imported as standalone)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> Dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    result: Dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip().strip("\"'")
    return result


def _read_meta_json(skill_dir: Path) -> Optional[Dict[str, Any]]:
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Privilege matrix
# ---------------------------------------------------------------------------

CAPABILITY_PRIVILEGES = {
    "scout":                {"exec_skills": "read-only",     "write_memory": False, "playwright": "get_content only", "social_tools": False},
    "builder":              {"exec_skills": True,            "write_memory": True,  "playwright": True,               "social_tools": False},
    "researcher":           {"exec_skills": "research only", "write_memory": False, "playwright": "get_content only", "social_tools": False},
    "social-media-manager": {"exec_skills": "social only",   "write_memory": False, "playwright": True,               "social_tools": True},
    "blogger":              {"exec_skills": "content only",  "write_memory": True,  "playwright": False,              "social_tools": False},
    "scribe":               {"exec_skills": "scribe/log only", "write_memory": True, "playwright": False,             "social_tools": False},
    "reviewer":             {"exec_skills": "read-only",     "write_memory": False, "playwright": False,              "social_tools": False},
    "coordinator":          {"exec_skills": "discovery only","write_memory": False,  "playwright": False,              "social_tools": False},
    "lead":                 {"exec_skills": "discovery only","write_memory": False,  "playwright": False,              "social_tools": False},
}

MCP_TOOLS = [
    "playwright_navigate", "playwright_screenshot", "playwright_get_content",
    "playwright_click", "playwright_fill", "playwright_execute_script",
    "playwright_get_attribute", "playwright_wait_for",
]


# ---------------------------------------------------------------------------
# AgentContextGenerator
# ---------------------------------------------------------------------------

class AgentContextGenerator:
    def __init__(
        self,
        skills_dir: Optional[Path] = None,
        workspace: Optional[Path] = None,
        gateway_url: Optional[str] = None,
    ):
        self.skills_dir = skills_dir or NANOBOT_SKILLS_DIR
        self.workspace = workspace or NANOBOT_WORKSPACE
        self.gateway_url = gateway_url or NANOBOT_GATEWAY_URL
        self.gateway_tools_path = Path(__file__).parent / "gateway_tools.py"

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_skills(self, skills_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        skills_dir = skills_dir or self.skills_dir
        results: List[Dict[str, Any]] = []
        if not skills_dir.is_dir():
            return results

        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            skill_dir = skill_md.parent
            skill_name = skill_dir.name

            try:
                fm = _parse_frontmatter(skill_md.read_text())
            except OSError:
                fm = {}
            meta = _read_meta_json(skill_dir) or {}

            scripts_dir = skill_dir / "scripts"
            scripts = [p.name for p in sorted(scripts_dir.glob("*.py"))] if scripts_dir.is_dir() else []

            results.append({
                "name": fm.get("name") or meta.get("name") or skill_name,
                "displayName": fm.get("displayName") or meta.get("displayName") or skill_name,
                "description": fm.get("description") or meta.get("description", ""),
                "version": fm.get("version") or meta.get("version", "unknown"),
                "tags": meta.get("tags", []),
                "tools": meta.get("tools", []),
                "scripts": scripts,
                "path": str(skill_dir),
            })
        return results

    def discover_mcp_tools(self, config_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        tools: List[Dict[str, Any]] = []

        for t in MCP_TOOLS:
            tools.append({"name": t, "source": "playwright-mcp", "source_type": "mcp", "description": f"Playwright MCP tool: {t}"})

        candidates = [config_path] if config_path else [
            self.workspace / ".nanobot" / "config.json",
            Path.home() / ".nanobot" / "config.json",
        ]
        for cfg_path in candidates:
            if cfg_path is None or not cfg_path.is_file():
                continue
            try:
                cfg = json.loads(cfg_path.read_text())
                for server_name, server_cfg in cfg.get("mcpServers", {}).items():
                    for tool_name in server_cfg.get("tools", []):
                        tools.append({"name": tool_name, "source": server_name, "source_type": "mcp", "description": f"MCP tool from {server_name}"})
            except (json.JSONDecodeError, OSError):
                pass
        return tools

    # ------------------------------------------------------------------
    # Context generation
    # ------------------------------------------------------------------

    def generate_context(self) -> str:
        skills = self.discover_skills()
        mcp_tools = self.discover_mcp_tools()
        cli = f"python3 {self.gateway_tools_path}"

        lines: List[str] = []
        lines.append("# nanobot Gateway — Tools & Skills Available to Agents")
        lines.append("")
        lines.append(f"_Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_")
        lines.append("")

        # Gateway endpoint
        lines.append("## Gateway Endpoint")
        lines.append(f"- URL: {self.gateway_url}")
        lines.append(f"- CLI: `{cli} <command>`")
        lines.append("")

        # Skills
        lines.append("## Available Skills")
        lines.append("")
        for skill in skills:
            version = skill["version"]
            lines.append(f"### {skill['name']} (v{version})")
            lines.append(skill["description"])
            for script in skill.get("scripts", []):
                lines.append(f"- `{cli} exec-skill --skill {skill['name']} --script {script} --args '<args>'`")
            if not skill.get("scripts"):
                lines.append(f"- `{cli} exec-skill --skill {skill['name']} --args '<args>'`")
            lines.append("")

        # MCP tools
        lines.append("## Available MCP Tools")
        tool_names = [t["name"] for t in mcp_tools]
        lines.append(f"- {', '.join(tool_names)}")
        lines.append("")

        # Memory system
        lines.append("## Memory System")
        lines.append(f"- Read: `{cli} memory-read --json`")
        lines.append(f"- Read section: `{cli} memory-read --section \"Section Name\" --json`")
        lines.append(f"- Write: `{cli} memory-write --section \"Section\" --content \"Content\"`")
        lines.append(f"- MEMORY.md location: {self.workspace / 'MEMORY.md'}")
        lines.append("")

        # Privilege matrix
        lines.append("## Tool Privileges by Capability")
        lines.append("| Capability | Can Execute Skills | Can Write Memory | Can Use Playwright | Can Use Social Tools |")
        lines.append("|---|---|---|---|---|")
        for cap, privs in CAPABILITY_PRIVILEGES.items():
            exec_str = _priv_str(privs["exec_skills"])
            mem_str = "Yes" if privs["write_memory"] else "No"
            pw_str = _priv_str(privs["playwright"])
            social_str = "Yes" if privs["social_tools"] else "No"
            lines.append(f"| {cap} | {exec_str} | {mem_str} | {pw_str} | {social_str} |")
        lines.append("")

        return "\n".join(lines)

    def write_context(self, output_path: Optional[Path] = None) -> Path:
        output_path = output_path or (self.workspace / ".overstory" / "gateway-context.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.generate_context()
        output_path.write_text(content)
        log.info("Wrote gateway context to %s (%d bytes)", output_path, len(content))
        return output_path

    # ------------------------------------------------------------------
    # Manifest generation
    # ------------------------------------------------------------------

    def generate_skills_manifest(self) -> Dict[str, Any]:
        skills = self.discover_skills()
        mcp_tools = self.discover_mcp_tools()
        return {
            "generated": datetime.now(timezone.utc).isoformat(),
            "gateway_url": self.gateway_url,
            "workspace": str(self.workspace),
            "skills_count": len(skills),
            "tools_count": sum(len(s.get("tools", [])) for s in skills) + len(mcp_tools),
            "skills": skills,
            "mcp_tools": [t["name"] for t in mcp_tools],
            "capabilities": list(CAPABILITY_PRIVILEGES.keys()),
        }

    def write_manifest(self, output_path: Optional[Path] = None) -> Path:
        output_path = output_path or (self.workspace / ".overstory" / "skills-manifest.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = self.generate_skills_manifest()
        output_path.write_text(json.dumps(manifest, indent=2, default=str) + "\n")
        log.info("Wrote skills manifest to %s", output_path)
        return output_path


def _priv_str(val: Any) -> str:
    if val is True:
        return "Yes"
    if val is False:
        return "No"
    return str(val)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="generate-agent-context",
        description="Generate gateway-context.md and skills-manifest.json for overstory agent overlays",
    )
    parser.add_argument(
        "--output", "-o",
        default=str(NANOBOT_WORKSPACE / ".overstory" / "gateway-context.md"),
        help="Output path for gateway-context.md",
    )
    parser.add_argument(
        "--manifest", "-m",
        default=str(NANOBOT_WORKSPACE / ".overstory" / "skills-manifest.json"),
        help="Output path for skills-manifest.json",
    )
    parser.add_argument("--skills-dir", default=None, help="Override skills directory")
    parser.add_argument("--workspace", default=None, help="Override workspace path")
    parser.add_argument("--gateway-url", default=None, help="Override gateway URL")
    parser.add_argument("--context-only", action="store_true", help="Only generate gateway-context.md")
    parser.add_argument("--manifest-only", action="store_true", help="Only generate skills-manifest.json")
    parser.add_argument("--json", action="store_true", help="Output result summary as JSON to stdout")
    args = parser.parse_args(argv)

    gen = AgentContextGenerator(
        skills_dir=Path(args.skills_dir) if args.skills_dir else None,
        workspace=Path(args.workspace) if args.workspace else None,
        gateway_url=args.gateway_url,
    )

    result: Dict[str, Any] = {}

    try:
        if not args.manifest_only:
            ctx_path = gen.write_context(Path(args.output))
            result["context_path"] = str(ctx_path)
            result["context_size"] = ctx_path.stat().st_size

        if not args.context_only:
            man_path = gen.write_manifest(Path(args.manifest))
            result["manifest_path"] = str(man_path)
            result["manifest_size"] = man_path.stat().st_size

        result["ok"] = True
    except Exception as exc:
        log.exception("Generation failed")
        result["ok"] = False
        result["error"] = str(exc)

    if args.json:
        json.dump(result, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        for k, v in result.items():
            print(f"{k}: {v}", file=sys.stderr)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
