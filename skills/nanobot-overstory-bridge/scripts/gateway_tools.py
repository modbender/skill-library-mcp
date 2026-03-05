#!/usr/bin/env python3
"""Gateway Tools CLI — lets overstory Claude Code agents access OverClaw gateway tools and skills.

Part of the OverClaw stack (port 18800). Executable as a CLI, importable as a module.
Outputs JSON to stdout, logs to stderr.

Env vars: NANOBOT_GATEWAY_URL (default http://localhost:18800),
          NANOBOT_WORKSPACE, NANOBOT_SKILLS_DIR, GATEWAY_TOOLS.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

NANOBOT_GATEWAY_URL = os.environ.get("NANOBOT_GATEWAY_URL", "http://localhost:18800")
NANOBOT_WORKSPACE = Path(os.environ.get("NANOBOT_WORKSPACE", "/Users/ghost/.openclaw/workspace"))
NANOBOT_SKILLS_DIR = Path(os.environ.get("NANOBOT_SKILLS_DIR", "/Users/ghost/.openclaw/workspace/skills"))
UI_SETTINGS_PATH = NANOBOT_WORKSPACE / ".overclaw_ui" / "settings.json"

logging.basicConfig(
    level=os.environ.get("GATEWAY_TOOLS_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("gateway-tools")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_out(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def _parse_frontmatter(text: str) -> Dict[str, str]:
    """Extract YAML-ish frontmatter from ``---`` delimited blocks without pyyaml."""
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
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Bad _meta.json in %s: %s", skill_dir.name, exc)
        return None


def find_skill_script(skill_name: str, script_name: Optional[str] = None) -> Optional[Path]:
    """Locate a script inside a skill's scripts/ directory."""
    skill_dir = NANOBOT_SKILLS_DIR / skill_name
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return None

    if script_name:
        candidate = scripts_dir / script_name
        return candidate if candidate.is_file() else None

    py_files = sorted(scripts_dir.glob("*.py"))
    if len(py_files) == 1:
        return py_files[0]

    meta = _read_meta_json(skill_dir)
    if meta and meta.get("mainScript"):
        candidate = scripts_dir / meta["mainScript"]
        if candidate.is_file():
            return candidate

    for name_hint in (f"{skill_name}.py", "main.py", "cli.py"):
        candidate = scripts_dir / name_hint
        if candidate.is_file():
            return candidate

    return py_files[0] if py_files else None


# ---------------------------------------------------------------------------
# Skill / tool discovery
# ---------------------------------------------------------------------------

def discover_skills(skills_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Scan all skills and return structured metadata."""
    skills_dir = skills_dir or NANOBOT_SKILLS_DIR
    results: List[Dict[str, Any]] = []
    if not skills_dir.is_dir():
        log.warning("Skills directory not found: %s", skills_dir)
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


def _slug_from_name(name: str, max_len: int = 48) -> str:
    """Generate a safe folder name from a name or prompt."""
    s = re.sub(r"[^a-z0-9\s\-]", "", (name or "project")[:max_len].lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-") or "project"
    return s[:max_len]


def create_project_folder(name: str = "project") -> Dict[str, Any]:
    """Create a new project folder under the workspace and set it as current in the Overclaw UI.
    Writes to .overclaw_ui/settings.json so the UI switches to the new folder.
    """
    slug = _slug_from_name(name)
    base = NANOBOT_WORKSPACE / slug
    path = base
    n = 1
    while path.exists():
        n += 1
        path = NANOBOT_WORKSPACE / f"{slug}-{n}"
    path.mkdir(parents=True, exist_ok=True)
    # Update UI settings so Overclaw UI shows this folder as current
    default_settings = {"default_project_folder": "overstory", "current_project_folder": "", "create_project_on_next_prompt": False}
    if UI_SETTINGS_PATH.is_file():
        try:
            data = json.loads(UI_SETTINGS_PATH.read_text(encoding="utf-8"))
            for k in default_settings:
                if k not in data:
                    data[k] = default_settings[k]
        except (json.JSONDecodeError, OSError):
            data = dict(default_settings)
    else:
        data = dict(default_settings)
    data["current_project_folder"] = str(path)
    data["create_project_on_next_prompt"] = False
    UI_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    UI_SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log.info("Created project folder: %s", path.name)
    return {"ok": True, "path": str(path), "name": path.name}


def discover_tools(skills_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Aggregate tools from skill _meta.json files, known MCP tool sets, and built-in gateway tools."""
    tools: List[Dict[str, Any]] = []

    # Built-in: create project folder (so user can ask in chat instead of using a button)
    tools.append({
        "name": "create_project_folder",
        "source": "gateway",
        "source_type": "builtin",
        "description": "Create a new project folder under the workspace and set it as the current project in the Overclaw UI. Use when the user asks to create a folder, new project, or workspace. Params: name (string, optional) - folder name or description; defaults to 'project'.",
    })
    # Built-in: approve an agent's current confirmation prompt (lead approves worker)
    tools.append({
        "name": "approve_agent",
        "source": "gateway",
        "source_type": "builtin",
        "description": "Approve an agent's current confirmation prompt (sends Down+Enter to their terminal). Use when a worker has sent you mail requesting approval. Params: agent (string, required) - agent name, e.g. builder-abc123 or scout-xyz.",
    })

    for skill in discover_skills(skills_dir):
        for tool_name in skill.get("tools", []):
            tools.append({
                "name": tool_name,
                "source": skill["name"],
                "source_type": "skill",
                "description": f"Tool from {skill['displayName']}",
            })
        for script in skill.get("scripts", []):
            tools.append({
                "name": f"{skill['name']}/{script}",
                "source": skill["name"],
                "source_type": "skill_script",
                "description": f"Script in {skill['displayName']}",
            })

    mcp_tools = _discover_mcp_tools()
    tools.extend(mcp_tools)
    return tools


def _discover_mcp_tools() -> List[Dict[str, Any]]:
    """Read MCP tool names from known config locations."""
    tools: List[Dict[str, Any]] = []
    playwright_tools = [
        "playwright_navigate", "playwright_screenshot", "playwright_get_content",
        "playwright_click", "playwright_fill", "playwright_execute_script",
        "playwright_get_attribute", "playwright_wait_for",
    ]
    for t in playwright_tools:
        tools.append({"name": t, "source": "playwright-mcp", "source_type": "mcp", "description": f"Playwright MCP tool: {t}"})

    config_candidates = [
        NANOBOT_WORKSPACE / ".nanobot" / "config.json",
        Path.home() / ".nanobot" / "config.json",
    ]
    for cfg_path in config_candidates:
        if not cfg_path.is_file():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
            for server_name, server_cfg in cfg.get("mcpServers", {}).items():
                for tool_name in server_cfg.get("tools", []):
                    tools.append({
                        "name": tool_name,
                        "source": server_name,
                        "source_type": "mcp",
                        "description": f"MCP tool from {server_name}",
                    })
        except (json.JSONDecodeError, OSError) as exc:
            log.debug("Could not read MCP config %s: %s", cfg_path, exc)
    return tools


# ---------------------------------------------------------------------------
# Execution helpers
# ---------------------------------------------------------------------------

def exec_skill(skill_name: str, script_name: Optional[str] = None, args: str = "") -> Dict[str, Any]:
    """Run a skill's script and capture output."""
    script = find_skill_script(skill_name, script_name)
    if script is None:
        return {"error": f"Script not found for skill '{skill_name}'" + (f" script '{script_name}'" if script_name else ""), "exit_code": 1}

    return _run_script(script, args)


def run_script(skill_name: str, script_name: str, args: str = "") -> Dict[str, Any]:
    """Run any script from any skill directly."""
    script = find_skill_script(skill_name, script_name)
    if script is None:
        return {"error": f"Script '{script_name}' not found in skill '{skill_name}'", "exit_code": 1}
    return _run_script(script, args)


def exec_tool(tool_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a tool by name — resolves to built-in, MCP, or skill script."""
    params = params or {}

    if tool_name == "create_project_folder":
        return create_project_folder(params.get("name") or "project")

    if tool_name == "approve_agent":
        agent = params.get("agent") or params.get("name")
        if not agent:
            return {"error": "approve_agent requires 'agent' (agent name)", "exit_code": 1}
        try:
            req = urllib.request.Request(
                f"{NANOBOT_GATEWAY_URL}/api/agents/{urllib.parse.quote(str(agent))}/approve",
                data=b"",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                out = json.loads(resp.read())
                if not out.get("ok"):
                    return {"error": out.get("error", "approve failed"), "exit_code": 1, "response": out}
                return {"ok": True, "agent": agent, "message": out.get("message", "approved")}
        except Exception as exc:
            log.warning("approve_agent failed for %s: %s", agent, exc)
            return {"error": str(exc), "exit_code": 1}

    mcp_tools = {t["name"]: t for t in _discover_mcp_tools()}
    if tool_name in mcp_tools:
        return _exec_mcp_tool(tool_name, params)

    if "/" in tool_name:
        skill_name, script_name = tool_name.split("/", 1)
        return exec_skill(skill_name, script_name, json.dumps(params))

    all_tools = discover_tools()
    for t in all_tools:
        if t["name"] == tool_name and t["source_type"] == "skill":
            skill_scripts = [s for s in all_tools if s["source"] == t["source"] and s["source_type"] == "skill_script"]
            if skill_scripts:
                parts = skill_scripts[0]["name"].split("/", 1)
                return exec_skill(parts[0], parts[1] if len(parts) > 1 else None, json.dumps(params))

    return {"error": f"Tool '{tool_name}' not found", "exit_code": 1}


def _exec_mcp_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Try to reach the MCP tool via the playwright bridge or nanobot gateway."""
    try:
        import urllib.request
        payload = json.dumps({"tool": tool_name, "params": params}).encode()
        req = urllib.request.Request(
            f"{NANOBOT_GATEWAY_URL}/mcp/execute",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as exc:
        log.warning("MCP gateway call failed for %s: %s", tool_name, exc)
        return {"error": f"MCP execution failed: {exc}", "tool": tool_name, "exit_code": 1}


def _run_script(script: Path, args: str) -> Dict[str, Any]:
    """Subprocess wrapper for running a Python script."""
    import shlex
    cmd = [sys.executable, str(script)] + (shlex.split(args) if args else [])
    log.info("Running: %s", " ".join(cmd))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {"stdout": proc.stdout, "stderr": proc.stderr, "exit_code": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "Script timed out after 120s", "exit_code": 124}
    except OSError as exc:
        return {"error": str(exc), "exit_code": 1}


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

MEMORY_PATH = NANOBOT_WORKSPACE / "MEMORY.md"


def memory_read(section: Optional[str] = None) -> Dict[str, Any]:
    """Read MEMORY.md (optionally a specific section)."""
    if not MEMORY_PATH.is_file():
        return {"error": "MEMORY.md not found", "path": str(MEMORY_PATH)}
    text = MEMORY_PATH.read_text()
    stat = MEMORY_PATH.stat()
    result: Dict[str, Any] = {
        "path": str(MEMORY_PATH),
        "size": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }
    if section:
        pattern = rf"(?:^|\n)(## {re.escape(section)}\s*\n)(.*?)(?=\n## |\Z)"
        m = re.search(pattern, text, re.DOTALL)
        result["section"] = section
        result["content"] = m.group(2).strip() if m else None
        if not m:
            result["warning"] = f"Section '## {section}' not found"
    else:
        result["content"] = text
    return result


def memory_write(section: str, content: str) -> Dict[str, Any]:
    """Append a timestamped entry to MEMORY.md under the given section."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{timestamp}] {content}\n"

    if MEMORY_PATH.is_file():
        text = MEMORY_PATH.read_text()
    else:
        text = "# Memory\n"

    header = f"## {section}"
    if header in text:
        idx = text.index(header) + len(header)
        next_section = re.search(r"\n## ", text[idx:])
        insert_at = idx + next_section.start() if next_section else len(text)
        text = text[:insert_at].rstrip() + entry + text[insert_at:]
    else:
        text = text.rstrip() + f"\n\n{header}\n{entry}"

    MEMORY_PATH.write_text(text)
    log.info("Wrote to MEMORY.md section '%s'", section)
    return {"ok": True, "section": section, "timestamp": timestamp, "path": str(MEMORY_PATH)}


# ---------------------------------------------------------------------------
# Status / discovery
# ---------------------------------------------------------------------------

def check_status() -> Dict[str, Any]:
    """Check health of gateway and related services."""
    status: Dict[str, Any] = {"timestamp": datetime.now(timezone.utc).isoformat()}

    # nanobot gateway
    try:
        import urllib.request
        with urllib.request.urlopen(f"{NANOBOT_GATEWAY_URL}/health", timeout=5) as resp:
            status["gateway"] = {"url": NANOBOT_GATEWAY_URL, "status": "ok", "code": resp.status}
    except Exception as exc:
        status["gateway"] = {"url": NANOBOT_GATEWAY_URL, "status": "unreachable", "error": str(exc)}

    # ollama
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as resp:
            data = json.loads(resp.read())
            models = [m.get("name", "?") for m in data.get("models", [])]
            status["ollama"] = {"status": "ok", "models": models}
    except Exception as exc:
        status["ollama"] = {"status": "unreachable", "error": str(exc)}

    # overstory
    try:
        proc = subprocess.run(["overstory", "status"], capture_output=True, text=True, timeout=10)
        status["overstory"] = {"status": "ok" if proc.returncode == 0 else "error", "output": proc.stdout.strip()[:500]}
    except FileNotFoundError:
        status["overstory"] = {"status": "not_installed"}
    except Exception as exc:
        status["overstory"] = {"status": "error", "error": str(exc)}

    status["workspace"] = str(NANOBOT_WORKSPACE)
    status["skills_dir"] = str(NANOBOT_SKILLS_DIR)
    return status


def full_discover() -> Dict[str, Any]:
    """Combine skills + tools + status into a single discovery payload."""
    return {
        "skills": discover_skills(),
        "tools": discover_tools(),
        "status": check_status(),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gateway-tools", description="Gateway Tools CLI for Claude Code Agents")
    sub = parser.add_subparsers(dest="command")

    ls = sub.add_parser("list-skills", help="Discover all available skills")
    ls.add_argument("--json", action="store_true", default=True)

    lt = sub.add_parser("list-tools", help="Discover all available tools")
    lt.add_argument("--json", action="store_true", default=True)

    es = sub.add_parser("exec-skill", help="Execute a skill's script")
    es.add_argument("--skill", required=True, help="Skill name")
    es.add_argument("--script", default=None, help="Script filename (auto-detected if omitted)")
    es.add_argument("--args", default="", help="Arguments to pass to the script")

    et = sub.add_parser("exec-tool", help="Execute a specific tool")
    et.add_argument("--tool", required=True, help="Tool name")
    et.add_argument("--params", default="{}", help="JSON params dict")

    rs = sub.add_parser("run-script", help="Run any script from any skill")
    rs.add_argument("--skill", required=True)
    rs.add_argument("--script", required=True)
    rs.add_argument("--args", default="")

    mr = sub.add_parser("memory-read", help="Read from MEMORY.md")
    mr.add_argument("--section", default=None)
    mr.add_argument("--json", action="store_true", default=True)

    mw = sub.add_parser("memory-write", help="Append to MEMORY.md")
    mw.add_argument("--section", required=True)
    mw.add_argument("--content", required=True)

    st = sub.add_parser("status", help="Check gateway and system status")
    st.add_argument("--json", action="store_true", default=True)

    ds = sub.add_parser("discover", help="Full discovery dump")
    ds.add_argument("--json", action="store_true", default=True)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help(sys.stderr)
        return 1

    handlers = {
        "list-skills": lambda: _json_out(discover_skills()),
        "list-tools": lambda: _json_out(discover_tools()),
        "exec-skill": lambda: _json_out(exec_skill(args.skill, args.script, args.args)),
        "exec-tool": lambda: _json_out(exec_tool(args.tool, json.loads(args.params))),
        "run-script": lambda: _json_out(run_script(args.skill, args.script, args.args)),
        "memory-read": lambda: _json_out(memory_read(args.section)),
        "memory-write": lambda: _json_out(memory_write(args.section, args.content)),
        "status": lambda: _json_out(check_status()),
        "discover": lambda: _json_out(full_discover()),
    }

    try:
        handlers[args.command]()
    except Exception as exc:
        log.exception("Command '%s' failed", args.command)
        _json_out({"error": str(exc)})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
