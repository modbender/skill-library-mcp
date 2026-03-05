#!/usr/bin/env python3
"""
release_notes.py -- Generate aggregated release notes across all skills.

Scans .agents/skills/*/SKILL.md for version information and git history,
then produces formatted release notes grouped by category.

Usage:
    python release_notes.py --since "2024-01-01"
    python release_notes.py --version "1.3.0"
    python release_notes.py --json
    python release_notes.py --since "2024-06-01" --json

No external dependencies required (stdlib only).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILLS_DIR = Path(".agents/skills")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

CATEGORIES = {
    "New Skills": "Skills added since the cutoff",
    "Updated Skills": "Skills with version bumps",
    "New Scripts": "Automation scripts added",
    "New Commands": "Commands or templates added",
}


# ---------------------------------------------------------------------------
# Terminal colors
# ---------------------------------------------------------------------------
def _has_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_COLOR = _has_color()

def _c(code: str, t: str) -> str:
    return f"\033[{code}m{t}\033[0m" if _COLOR else t

def bold(t: str) -> str:  return _c("1", t)
def dim(t: str) -> str:   return _c("2", t)
def cyan(t: str) -> str:  return _c("36", t)
def green(t: str) -> str: return _c("32", t)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------
def git_root() -> Path:
    """Find the repository root."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
        return Path(out)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def git_log_since_date(since: str, path: str = "") -> list[dict[str, str]]:
    """Get commits since a date, optionally scoped to a path.
    Returns list of dicts with 'hash', 'date', 'message'."""
    cmd = [
        "git", "log", f"--since={since}",
        "--format=%H|%aI|%s", "--no-merges",
    ]
    if path:
        cmd.extend(["--", path])
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    if not out:
        return []
    results: list[dict[str, str]] = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            results.append({"hash": parts[0], "date": parts[1], "message": parts[2]})
    return results


def file_added_after(filepath: Path, since: str) -> bool:
    """Check if a file was first added to git after the given date."""
    try:
        out = subprocess.check_output(
            ["git", "log", "--diff-filter=A", "--format=%aI",
             "--follow", "--", str(filepath)],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    if not out:
        # Not tracked yet — treat as new
        return True
    # The last line is the earliest (first add)
    first_date = out.splitlines()[-1][:10]
    return first_date >= since[:10]


# ---------------------------------------------------------------------------
# Skill scanning
# ---------------------------------------------------------------------------
@dataclass
class SkillInfo:
    name: str
    path: Path
    version: Optional[str] = None
    description: str = ""
    is_new: bool = False
    commits: list[dict[str, str]] = field(default_factory=list)
    new_scripts: list[str] = field(default_factory=list)
    new_commands: list[str] = field(default_factory=list)


def parse_frontmatter_field(fm_text: str, key: str) -> str:
    """Extract a simple scalar value from frontmatter text."""
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", fm_text, re.MULTILINE)
    if not m:
        return ""
    val = m.group(1).strip().strip("\"'")
    return val


def scan_skills(root: Path, since: str) -> list[SkillInfo]:
    """Scan all skills and collect change information since a date."""
    base = root / SKILLS_DIR
    if not base.is_dir():
        return []

    skills: list[SkillInfo] = []
    for skill_dir in sorted(base.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text()
        fm_match = FRONTMATTER_RE.match(content)
        fm_text = fm_match.group(1) if fm_match else ""

        info = SkillInfo(
            name=skill_dir.name,
            path=skill_dir,
            version=parse_frontmatter_field(fm_text, "version") or None,
            description=parse_frontmatter_field(fm_text, "description"),
        )

        # Check if skill is new (SKILL.md added after since date)
        info.is_new = file_added_after(skill_md, since)

        # Get commits for this skill since date
        rel_path = str(skill_dir.relative_to(root))
        info.commits = git_log_since_date(since, rel_path)

        # Detect new scripts
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.is_dir():
            for f in sorted(scripts_dir.iterdir()):
                if f.is_file() and file_added_after(f, since):
                    info.new_scripts.append(f.name)

        # Detect new commands/templates
        for subdir_name in ("templates", "commands", "assets"):
            subdir = skill_dir / subdir_name
            if subdir.is_dir():
                for f in sorted(subdir.iterdir()):
                    if f.is_file() and file_added_after(f, since):
                        info.new_commands.append(f"{subdir_name}/{f.name}")

        skills.append(info)

    return skills


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------
@dataclass
class ReleaseNotes:
    version: Optional[str]
    since: str
    generated: str
    new_skills: list[SkillInfo] = field(default_factory=list)
    updated_skills: list[SkillInfo] = field(default_factory=list)
    new_scripts: list[tuple[str, str]] = field(default_factory=list)  # (skill, script)
    new_commands: list[tuple[str, str]] = field(default_factory=list)  # (skill, file)


def aggregate(skills: list[SkillInfo], version: Optional[str], since: str) -> ReleaseNotes:
    """Aggregate skill data into structured release notes."""
    notes = ReleaseNotes(
        version=version,
        since=since,
        generated=date.today().isoformat(),
    )

    for info in skills:
        if not info.commits and not info.is_new:
            continue

        if info.is_new:
            notes.new_skills.append(info)
        elif info.commits:
            notes.updated_skills.append(info)

        for script in info.new_scripts:
            notes.new_scripts.append((info.name, script))
        for cmd in info.new_commands:
            notes.new_commands.append((info.name, cmd))

    return notes


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------
def format_markdown(notes: ReleaseNotes) -> str:
    """Render release notes as markdown."""
    lines: list[str] = []
    title = f"Release {notes.version}" if notes.version else "Release Notes"
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Generated**: {notes.generated}  ")
    lines.append(f"**Changes since**: {notes.since}")
    lines.append("")

    if notes.new_skills:
        lines.append("## New Skills")
        lines.append("")
        for info in notes.new_skills:
            ver = f" (v{info.version})" if info.version else ""
            lines.append(f"- **{info.name}**{ver}")
            if info.description:
                # Truncate long descriptions
                desc = info.description[:120]
                if len(info.description) > 120:
                    desc += "..."
                lines.append(f"  {desc}")
        lines.append("")

    if notes.updated_skills:
        lines.append("## Updated Skills")
        lines.append("")
        for info in notes.updated_skills:
            ver = f" (v{info.version})" if info.version else ""
            commit_count = len(info.commits)
            lines.append(f"- **{info.name}**{ver} — {commit_count} commit(s)")
        lines.append("")

    if notes.new_scripts:
        lines.append("## New Scripts")
        lines.append("")
        for skill_name, script in notes.new_scripts:
            lines.append(f"- `{skill_name}/scripts/{script}`")
        lines.append("")

    if notes.new_commands:
        lines.append("## New Commands & Templates")
        lines.append("")
        for skill_name, cmd_file in notes.new_commands:
            lines.append(f"- `{skill_name}/{cmd_file}`")
        lines.append("")

    # Statistics
    total_commits = sum(len(s.commits) for s in notes.new_skills + notes.updated_skills)
    lines.append("---")
    lines.append("")
    lines.append(f"**Stats**: {len(notes.new_skills)} new skill(s), "
                 f"{len(notes.updated_skills)} updated, "
                 f"{total_commits} total commit(s)")
    lines.append("")

    return "\n".join(lines)


def format_json(notes: ReleaseNotes) -> str:
    """Render release notes as JSON."""
    data = {
        "version": notes.version,
        "since": notes.since,
        "generated": notes.generated,
        "new_skills": [
            {"name": s.name, "version": s.version, "description": s.description}
            for s in notes.new_skills
        ],
        "updated_skills": [
            {"name": s.name, "version": s.version, "commits": len(s.commits)}
            for s in notes.updated_skills
        ],
        "new_scripts": [
            {"skill": skill, "script": script}
            for skill, script in notes.new_scripts
        ],
        "new_commands": [
            {"skill": skill, "file": cmd}
            for skill, cmd in notes.new_commands
        ],
        "stats": {
            "new_skills": len(notes.new_skills),
            "updated_skills": len(notes.updated_skills),
            "new_scripts": len(notes.new_scripts),
            "new_commands": len(notes.new_commands),
            "total_commits": sum(
                len(s.commits) for s in notes.new_skills + notes.updated_skills
            ),
        },
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate aggregated release notes across all skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python release_notes.py --since "2024-01-01"\n'
            '  python release_notes.py --version "1.3.0"\n'
            "  python release_notes.py --json\n"
            '  python release_notes.py --since "2024-06-01" --json\n'
        ),
    )
    p.add_argument("--since", metavar="DATE", default=None,
                   help="Include changes since this date (YYYY-MM-DD). "
                        "Defaults to 30 days ago.")
    p.add_argument("--version", metavar="VER", default=None,
                   help="Label the release notes with this version string")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Output as JSON instead of markdown")
    return p


def default_since() -> str:
    """Default to 30 days ago."""
    from datetime import timedelta
    d = date.today() - timedelta(days=30)
    return d.isoformat()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    since = args.since or default_since()

    # Validate date format
    try:
        datetime.strptime(since[:10], "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {since}. Use YYYY-MM-DD.", file=sys.stderr)
        return 1

    root = git_root()
    os.chdir(root)

    skills = scan_skills(root, since)
    if not skills:
        print("No skills found.", file=sys.stderr)
        return 1

    notes = aggregate(skills, args.version, since)

    if args.json_output:
        print(format_json(notes))
    else:
        print(format_markdown(notes))

    return 0


if __name__ == "__main__":
    sys.exit(main())
