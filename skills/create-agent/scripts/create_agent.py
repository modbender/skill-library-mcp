#!/usr/bin/env python3
"""
Create or update an Overstory agent for Overclaw.
Updates all seven integration points and optionally regenerates gateway context.
See .overstory/CREATING_AGENTS.md for the manual steps.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Allow importing analyze_agent_needs when run from workspace root
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("create_agent")

WORKSPACE = Path(os.environ.get("NANOBOT_WORKSPACE", os.environ.get("OPENCLAW_WORKSPACE", "/Users/ghost/.openclaw/workspace")))
OVERSTORY = WORKSPACE / ".overstory"
AGENT_DEFS = OVERSTORY / "agent-defs"
CONFIG_PATH = OVERSTORY / "config.yaml"
MANIFEST_PATH = OVERSTORY / "agent-manifest.json"
GATEWAY_PATH = WORKSPACE / "scripts" / "overclaw_gateway.py"
TASK_ROUTER_PATH = WORKSPACE / "skills" / "nanobot-overstory-bridge" / "scripts" / "task_router.py"
GENERATE_CONTEXT_PATH = WORKSPACE / "skills" / "nanobot-overstory-bridge" / "scripts" / "generate_agent_context.py"

# Default privilege for new agents (read-only, no memory write, no playwright/social)
DEFAULT_PRIVILEGE = {"exec_skills": "read-only", "write_memory": False, "playwright": False, "social_tools": False}


def _backup(path: Path) -> Optional[Path]:
    if not path.exists():
        return None
    backup = path.with_suffix(path.suffix + ".create_agent.bak")
    shutil.copy2(path, backup)
    return backup


def _restore(backup: Optional[Path], path: Path) -> None:
    if backup and backup.exists():
        shutil.copy2(backup, path)
        backup.unlink()


def _load_yaml(path: Path) -> Any:
    try:
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}  # Validation may be skipped
    except Exception as e:
        raise SystemExit(f"Failed to load YAML {path}: {e}")


def _dump_yaml(data: Any, path: Path) -> None:
    try:
        import yaml
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    except ImportError:
        raise SystemExit("PyYAML is required to update config.yaml. Install with: pip install pyyaml")
    except Exception as e:
        raise SystemExit(f"Failed to write YAML {path}: {e}")


def _load_json(path: Path) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def _dump_json(data: Any, path: Path) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent="\t")
        f.write("\n")


def update_config(name: str, description: str, model: str, skills: List[str], tools: List[str]) -> None:
    try:
        import yaml
    except ImportError:
        # Append new capability block without PyYAML
        text = CONFIG_PATH.read_text(encoding="utf-8")
        if f"    {name}:" in text:
            log.info("Config already has %s", name)
            return
        block = f"""    {name}:
      description: {description}
      model: {model}
"""
        if "  manifestPath:" in text:
            text = text.replace("  manifestPath:", block + "  manifestPath:", 1)
        else:
            text = text.rstrip() + "\n" + block + "\n"
        CONFIG_PATH.write_text(text, encoding="utf-8")
        log.info("Updated %s (no PyYAML)", CONFIG_PATH)
        return
    data = _load_yaml(CONFIG_PATH)
    caps = data.setdefault("agents", {}).setdefault("capabilities", {})
    entry = {"description": description, "model": model}
    if skills:
        entry["skills"] = skills
    if tools:
        entry["tools"] = tools
    caps[name] = entry
    _dump_yaml(data, CONFIG_PATH)
    log.info("Updated %s", CONFIG_PATH)


def update_manifest(
    name: str,
    file_name: str,
    model: str,
    tools: List[str],
    capabilities: List[str],
    can_spawn: bool,
    constraints: List[str],
) -> None:
    data = _load_json(MANIFEST_PATH)
    agents = data.setdefault("agents", {})
    agents[name] = {
        "file": file_name,
        "model": model,
        "tools": tools,
        "capabilities": capabilities,
        "canSpawn": can_spawn,
        "constraints": constraints,
    }
    idx = data.setdefault("capabilityIndex", {})
    for cap in capabilities:
        if cap not in idx:
            idx[cap] = []
        if name not in idx[cap]:
            idx[cap].append(name)
    _dump_json(data, MANIFEST_PATH)
    log.info("Updated %s", MANIFEST_PATH)


def agent_def_template(name: str, description: str, model: str, tools: List[str], capabilities: List[str]) -> str:
    tools_str = ", ".join(tools)
    caps_str = ", ".join(capabilities)
    return f"""# {name.replace("-", " ").title()} Agent

## Capability
{name}

## Description
{description}

## Model
{model}

## Tools Available
- {tools_str}

## nanobot Gateway Tools & Skills

All agents have access to the nanobot gateway tools ecosystem via the `gateway-tools` CLI.
Your environment includes: `$NANOBOT_GATEWAY_URL`, `$NANOBOT_WORKSPACE`, `$NANOBOT_SKILLS_DIR`, `$GATEWAY_TOOLS`.

### Your Gateway Privileges
- **Discovery**: All discovery commands
- Adjust this section per CAPABILITY_PRIVILEGES for this agent.

### Commands
```bash
python3 $GATEWAY_TOOLS list-skills --json
python3 $GATEWAY_TOOLS discover --json
python3 $GATEWAY_TOOLS status --json
```

## Task Examples
- "Example task for {name}"
- "Run {caps_str} related work"

## Instructions
1. Parse the task and identify required steps
2. Use only allowed tools and gateway commands
3. Report results via mail or output
"""


def write_agent_def(name: str, description: str, model: str, tools: List[str], capabilities: List[str]) -> None:
    AGENT_DEFS.mkdir(parents=True, exist_ok=True)
    path = AGENT_DEFS / f"{name}.md"
    content = agent_def_template(name, description, model, tools, capabilities)
    path.write_text(content, encoding="utf-8")
    log.info("Wrote %s", path)


def update_gateway_prompt(name: str) -> None:
    text = GATEWAY_PATH.read_text(encoding="utf-8")
    # Insert new capability before the period after "reviewer"
    old = 'blogger, scribe, builder, scout, reviewer. Analyze'
    new = f'blogger, scribe, builder, scout, reviewer, {name}. Analyze'
    if old not in text:
        # Fallback: find "reviewer." and add ", name" before the period
        old2 = "reviewer. Analyze"
        new2 = f"reviewer, {name}. Analyze"
        if old2 in text:
            text = text.replace(old2, new2, 1)
        else:
            log.warning("Could not find gateway prompt snippet; add %s manually to Available capabilities", name)
            return
    else:
        text = text.replace(old, new, 1)
    GATEWAY_PATH.write_text(text, encoding="utf-8")
    log.info("Updated %s (orchestrator prompt)", GATEWAY_PATH)


def update_task_router(name: str, patterns: List[str], priority: int = 8) -> None:
    text = TASK_ROUTER_PATH.read_text(encoding="utf-8")
    # Insert new entry after the last capability block, before the closing ]
    needle = '''        "priority": 9,
    },
]'''
    patterns_str = ", ".join(repr(p) for p in patterns)
    new_block = (
        "        \"priority\": 9,\n    },\n    {\n        \"capability\": \""
        + name
        + "\",\n        \"patterns\": [\n            "
        + patterns_str
        + "\n        ],\n        \"priority\": "
        + str(priority)
        + ",\n    },\n]"
    )
    if needle not in text:
        log.warning("Could not find CAPABILITY_PATTERNS end in task_router.py; add %s manually", name)
        return
    text = text.replace(needle, new_block, 1)
    TASK_ROUTER_PATH.write_text(text, encoding="utf-8")
    log.info("Updated %s", TASK_ROUTER_PATH)


def update_generate_agent_context(name: str, privilege: Optional[Dict[str, Any]] = None) -> None:
    privilege = privilege or DEFAULT_PRIVILEGE
    text = GENERATE_CONTEXT_PATH.read_text(encoding="utf-8")
    if f'"{name}"' in text:
        log.info("CAPABILITY_PRIVILEGES already has %s", name)
        return
    # Find "}\n\nMCP_TOOLS" (closing brace of CAPABILITY_PRIVILEGES) and insert new line before the }
    needle = "\n}\n\nMCP_TOOLS"
    if needle not in text:
        log.warning("Could not find CAPABILITY_PRIVILEGES end in generate_agent_context.py; add %s manually", name)
        return
    # Output Python literals (True/False), not JSON (true/false). Keep the newline we're removing.
    priv_str = json.dumps(privilege).replace("true", "True").replace("false", "False")
    new_line = f'\n    "{name}":              {priv_str},\n'
    text = text.replace(needle, new_line + "}\n\nMCP_TOOLS", 1)
    GENERATE_CONTEXT_PATH.write_text(text, encoding="utf-8")
    log.info("Updated %s", GENERATE_CONTEXT_PATH)


def regenerate_context(workspace: Path) -> bool:
    if not GENERATE_CONTEXT_PATH.exists():
        log.warning("generate_agent_context.py not found, skip regeneration")
        return False
    try:
        subprocess.run(
            [sys.executable, str(GENERATE_CONTEXT_PATH), "--workspace", str(workspace)],
            cwd=str(workspace),
            check=True,
            capture_output=True,
        )
        log.info("Regenerated gateway-context.md and skills-manifest.json")
        return True
    except subprocess.CalledProcessError as e:
        log.error("Regeneration failed: %s", e.stderr.decode() if e.stderr else e)
        return False


def validate_config() -> bool:
    _load_yaml(CONFIG_PATH)
    return True


def validate_manifest() -> bool:
    data = _load_json(MANIFEST_PATH)
    if "agents" not in data or "capabilityIndex" not in data:
        return False
    return True


def validate_agent_def(name: str) -> bool:
    path = AGENT_DEFS / f"{name}.md"
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    return "## Capability" in content and name in content


def validate_gateway_prompt(name: str) -> bool:
    text = GATEWAY_PATH.read_text(encoding="utf-8")
    return name in text and "Available capabilities" in text


def validate_task_router(name: str) -> bool:
    text = TASK_ROUTER_PATH.read_text(encoding="utf-8")
    return f'"capability": "{name}"' in text


def validate_capability_privileges(name: str) -> bool:
    text = GENERATE_CONTEXT_PATH.read_text(encoding="utf-8")
    return f'"{name}"' in text and "CAPABILITY_PRIVILEGES" in text


def validate_manifest_index(name: str, capabilities: List[str]) -> bool:
    data = _load_json(MANIFEST_PATH)
    idx = data.get("capabilityIndex", {})
    for cap in capabilities:
        if cap not in idx or name not in idx.get(cap, []):
            return False
    return True


def run_validation(name: str, capabilities: Optional[List[str]] = None) -> bool:
    ok = True
    if not validate_config():
        log.error("config.yaml validation failed")
        ok = False
    if not validate_manifest():
        log.error("agent-manifest.json validation failed")
        ok = False
    if not validate_agent_def(name):
        log.error("agent-defs/%s.md missing or invalid", name)
        ok = False
    if not validate_gateway_prompt(name):
        log.error("Gateway system prompt does not list capability %s", name)
        ok = False
    if not validate_task_router(name):
        log.error("task_router.py CAPABILITY_PATTERNS missing %s", name)
        ok = False
    if not validate_capability_privileges(name):
        log.error("generate_agent_context.py CAPABILITY_PRIVILEGES missing %s", name)
        ok = False
    if capabilities and not validate_manifest_index(name, capabilities):
        log.error("agent-manifest.json capabilityIndex missing mappings for %s", capabilities)
        ok = False
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a new Overstory agent for Overclaw (updates all 7 integration points)",
    )
    parser.add_argument("--name", required=True, help="Agent capability name (e.g. troubleshooter)")
    parser.add_argument("--description", required=True, help="One-line description")
    parser.add_argument("--capabilities", default="", help="Comma-separated capability keys for routing (e.g. troubleshoot,debug)")
    parser.add_argument("--model", default="sonnet", help="Model: haiku, sonnet, opus, claude-code")
    parser.add_argument("--tools", default="Read,Glob,Grep,Bash", help="Comma-separated tools (Read, Write, Edit, Glob, Grep, Bash, Task)")
    parser.add_argument("--can-spawn", action="store_true", help="Agent can spawn other agents")
    parser.add_argument("--constraints", default="", help="Comma-separated constraints (e.g. read-only) or empty")
    parser.add_argument("--patterns", default="", help="Comma-separated regex patterns for task_router (default: derived from name)")
    parser.add_argument("--priority", type=int, default=8, help="Task router priority (default 8)")
    parser.add_argument("--workspace", default=None, type=Path, help="Workspace root (default: NANOBOT_WORKSPACE)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not write")
    parser.add_argument("--no-regenerate", action="store_true", help="Do not run generate_agent_context.py")
    parser.add_argument("--rollback-on-fail", action="store_true", help="Restore backups if validation fails")
    parser.add_argument("--analyze-from-logs", action="store_true", help="(Future) Analyze logs for suggestions")
    parser.add_argument("--analyze-from-troubleshooting", action="store_true", help="(Future) Analyze TROUBLESHOOTING.md")
    parser.add_argument("--suggest-only", action="store_true", help="Only run analysis and print suggestions, do not create")
    args = parser.parse_args()

    global WORKSPACE
    if args.workspace:
        WORKSPACE = args.workspace.resolve()

    if args.suggest_only and (args.analyze_from_logs or args.analyze_from_troubleshooting):
        try:
            from analyze_agent_needs import run_analysis
            suggestions = run_analysis(
                workspace=WORKSPACE,
                from_logs=args.analyze_from_logs,
                from_troubleshooting=args.analyze_from_troubleshooting,
            )
            for s in suggestions:
                log.info("Suggestion: %s", s)
            return 0
        except ImportError:
            log.warning("analyze_agent_needs not available; run analysis from skills/create-agent/scripts")
            return 0

    name = args.name.strip().lower().replace(" ", "-")
    capabilities = [c.strip() for c in args.capabilities.split(",") if c.strip()]
    if not capabilities:
        capabilities = [name]
    tools = [t.strip() for t in args.tools.split(",") if t.strip()]
    constraints = [c.strip() for c in args.constraints.split(",") if c.strip()]
    patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]
    if not patterns:
        # Default: word-boundary patterns for the capability name (with - or space)
        patterns = [r"\b" + re.escape(name) + r"\b", r"\b" + re.escape(name.replace("-", " ")) + r"\b"]

    if args.dry_run:
        log.info("DRY RUN: would create agent %s with capabilities %s, tools %s", name, capabilities, tools)
        return 0

    backups: List[tuple[Path, Optional[Path]]] = [
        (CONFIG_PATH, _backup(CONFIG_PATH)),
        (MANIFEST_PATH, _backup(MANIFEST_PATH)),
        (GATEWAY_PATH, _backup(GATEWAY_PATH)),
        (TASK_ROUTER_PATH, _backup(TASK_ROUTER_PATH)),
        (GENERATE_CONTEXT_PATH, _backup(GENERATE_CONTEXT_PATH)),
    ]
    agent_def_path = AGENT_DEFS / f"{name}.md"
    agent_def_backup = _backup(agent_def_path) if agent_def_path.exists() else None

    try:
        update_config(name, args.description, args.model, [], [])
        update_manifest(name, f"{name}.md", args.model, tools, capabilities, args.can_spawn, constraints)
        write_agent_def(name, args.description, args.model, tools, capabilities)
        update_gateway_prompt(name)
        update_task_router(name, patterns, args.priority)
        update_generate_agent_context(name)

        if not run_validation(name, capabilities):
            raise RuntimeError("Validation failed after updates")

        if not args.no_regenerate:
            regenerate_context(WORKSPACE)

        log.info("Agent %s created successfully. Run generate_agent_context.py if you skipped regeneration.", name)
        return 0
    except Exception as e:
        log.exception("Create agent failed: %s", e)
        if args.rollback_on_fail:
            for path, bak in backups:
                _restore(bak, path)
            if agent_def_backup and agent_def_path.exists():
                _restore(agent_def_backup, agent_def_path)
            log.info("Rolled back all changes")
        return 1


if __name__ == "__main__":
    sys.exit(main())
