#!/usr/bin/env python3
"""Discovers and loads OpenClaw skills from SKILL.md + _meta.json files.

Parses YAML frontmatter (between --- delimiters) using a minimal stdlib-only
parser (no PyYAML dependency). Returns structured SkillDefinition objects.

Importable as a module or runnable as a CLI tool.
Logs to stderr, structured JSON output to stdout.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("skill_loader")


@dataclass
class SkillDefinition:
    name: str
    display_name: str = ""
    description: str = ""
    version: str = "0.0.0"
    path: str = ""
    content: str = ""
    tools: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


def _parse_frontmatter(text: str) -> tuple[Dict[str, str], str]:
    """Parse YAML-like frontmatter between --- delimiters.

    Returns (frontmatter_dict, remaining_content). Handles simple
    key: value pairs (strings only — sufficient for SKILL.md).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", text, re.DOTALL)
    if not match:
        return {}, text

    fm_block = match.group(1)
    body = match.group(2)
    fm: Dict[str, str] = {}
    for line in fm_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        colon_idx = line.find(":")
        if colon_idx == -1:
            continue
        key = line[:colon_idx].strip()
        val = line[colon_idx + 1 :].strip().strip("\"'")
        fm[key] = val
    return fm, body


def _load_meta_json(skill_dir: Path) -> Dict[str, Any]:
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("failed to parse %s: %s", meta_path, exc)
        return {}


class SkillLoader:
    """Loads OpenClaw skills from the filesystem."""

    def __init__(self) -> None:
        self._skills: Dict[str, SkillDefinition] = {}

    def load_skill(self, skill_path: str | Path) -> SkillDefinition:
        """Load a single skill from its directory (must contain SKILL.md)."""
        skill_dir = Path(skill_path)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"No SKILL.md in {skill_dir}")

        text = skill_md.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)
        meta = _load_meta_json(skill_dir)

        tools: List[str] = meta.get("tools", [])
        tags: List[str] = meta.get("tags", [])

        sd = SkillDefinition(
            name=fm.get("name", skill_dir.name),
            display_name=fm.get("displayName", fm.get("name", skill_dir.name)),
            description=fm.get("description", ""),
            version=fm.get("version", meta.get("version", "0.0.0")),
            path=str(skill_dir.resolve()),
            content=body.strip(),
            tools=tools if isinstance(tools, list) else [],
            tags=tags if isinstance(tags, list) else [],
            meta=meta,
        )
        self._skills[sd.name] = sd
        log.info("loaded skill: %s v%s (%d tools)", sd.name, sd.version, len(sd.tools))
        return sd

    def discover_skills(self, skills_dir: str | Path) -> List[Path]:
        """Find all directories under skills_dir that contain a SKILL.md."""
        base = Path(skills_dir)
        if not base.is_dir():
            log.warning("skills directory not found: %s", base)
            return []
        found = sorted(
            d.parent for d in base.rglob("SKILL.md")
            if d.parent.name != "__pycache__"
        )
        log.info("discovered %d skills in %s", len(found), base)
        return found

    def load_all(self, skills_dir: str | Path) -> List[SkillDefinition]:
        """Discover and load all skills in a directory."""
        paths = self.discover_skills(skills_dir)
        loaded = []
        for p in paths:
            try:
                loaded.append(self.load_skill(p))
            except Exception as exc:
                log.warning("skipping %s: %s", p, exc)
        return loaded

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """Return a loaded skill by name."""
        return self._skills.get(name)

    def get_tools(self, name: str) -> List[str]:
        """Extract tool names from a loaded skill."""
        skill = self._skills.get(name)
        return skill.tools if skill else []

    def all_skills(self) -> Dict[str, SkillDefinition]:
        """Return all loaded skills."""
        return dict(self._skills)


def _json_out(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenClaw skill loader")
    sub = parser.add_subparsers(dest="command", required=True)

    p_discover = sub.add_parser("discover")
    p_discover.add_argument("--dir", required=True, help="Skills directory")
    p_discover.add_argument("--json", action="store_true", dest="as_json")

    p_load = sub.add_parser("load")
    p_load.add_argument("--skill", required=True, help="Path to single skill directory")
    p_load.add_argument("--json", action="store_true", dest="as_json")

    p_all = sub.add_parser("load-all")
    p_all.add_argument("--dir", required=True, help="Skills directory")
    p_all.add_argument("--json", action="store_true", dest="as_json")

    args = parser.parse_args()
    loader = SkillLoader()

    if args.command == "discover":
        paths = loader.discover_skills(args.dir)
        _json_out([str(p) for p in paths])

    elif args.command == "load":
        try:
            sd = loader.load_skill(args.skill)
            _json_out(asdict(sd))
        except FileNotFoundError as exc:
            _json_out({"ok": False, "error": str(exc)})
            sys.exit(1)

    elif args.command == "load-all":
        skills = loader.load_all(args.dir)
        _json_out([asdict(s) for s in skills])


if __name__ == "__main__":
    main()
