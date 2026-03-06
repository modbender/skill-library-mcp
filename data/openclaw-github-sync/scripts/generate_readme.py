#!/usr/bin/env python3
"""Generate/update README.md in the sync repo.

- Produces an executive summary based on current exported contents.
- Maintains a simple changelog (prepends newest entry; keeps recent history).

Inputs:
  argv[1] = sync repo directory
  argv[2] = template path
  argv[3] = optional path to a git-status porcelain file (for changelog)
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path


def utc_now_str() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def list_skill_names(sync_dir: Path) -> list[str]:
    skills_dir = sync_dir / "skills"
    if not skills_dir.is_dir():
        return []
    out: list[str] = []
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            out.append(child.name)
    return out


def list_projects(sync_dir: Path) -> list[str]:
    projects_dir = sync_dir / "projects"
    if not projects_dir.is_dir():
        return []
    out: list[str] = []
    for child in sorted(projects_dir.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            out.append(child.name + "/")
        elif child.is_file() and child.name.lower() != "readme.md":
            out.append(child.name)
    return out


def cron_summary(sync_dir: Path) -> str:
    cron_json = sync_dir / "ops" / "cron-jobs.json"
    if not cron_json.exists():
        return "- No cron export found (ops/cron-jobs.json missing)."

    try:
        data = json.loads(cron_json.read_text(encoding="utf-8"))
    except Exception:
        return "- Cron export present but could not be parsed (ops/cron-jobs.json)."

    # openclaw cron list --json currently returns an array of jobs (assumed).
    if isinstance(data, dict) and "jobs" in data and isinstance(data["jobs"], list):
        jobs = data["jobs"]
    elif isinstance(data, list):
        jobs = data
    else:
        jobs = []

    enabled = 0
    disabled = 0
    names: list[str] = []
    for j in jobs:
        if isinstance(j, dict):
            if j.get("enabled", True):
                enabled += 1
            else:
                disabled += 1
            n = j.get("name") or j.get("id") or j.get("jobId")
            if n:
                names.append(str(n))

    lines = [f"- Jobs exported: {len(jobs)} (enabled: {enabled}, disabled: {disabled})"]
    if names:
        # keep it executive: list up to 20 names
        sample = names[:20]
        lines.append("- Job names (sample): " + ", ".join(sample) + (" …" if len(names) > 20 else ""))
    lines.append("- Source: ops/cron-jobs.json")
    return "\n".join(lines)


def memory_summary(sync_dir: Path) -> str:
    mem_dir = sync_dir / "memory"
    if not mem_dir.exists():
        return "- No memory export found."

    public_dir = mem_dir / "public"
    public_files = []
    if public_dir.is_dir():
        public_files = sorted([p.name for p in public_dir.glob("*.md")])

    state_files = []
    for p in sorted(mem_dir.glob("*.json")):
        state_files.append(p.name)

    lines = []
    if public_files:
        lines.append("- Public memory notes: " + ", ".join(public_files))
    else:
        lines.append("- Public memory notes: none (memory/public is empty or not exported)")

    if state_files:
        lines.append("- State files: " + ", ".join(state_files))

    return "\n".join(lines)


def status_to_change_bullets(status_text: str) -> str:
    """Convert `git status --porcelain` output into brief bullets."""
    status_text = status_text.strip("\n")
    if not status_text.strip():
        return "- No file changes detected."

    added, modified, deleted, other = [], [], [], []
    for line in status_text.splitlines():
        # Porcelain v1: XY <path>
        m = re.match(r"^(..?)\s+(.*)$", line)
        if not m:
            other.append(line)
            continue
        xy = m.group(1)
        path = m.group(2)

        # Treat either side as the signal.
        if "A" in xy or xy == "??":
            added.append(path)
        elif "D" in xy:
            deleted.append(path)
        elif "M" in xy or "R" in xy or "C" in xy:
            modified.append(path)
        else:
            other.append(path)

    def fmt(label: str, items: list[str]) -> list[str]:
        if not items:
            return []
        # keep the readme small
        sample = items[:30]
        suffix = " …" if len(items) > 30 else ""
        return [f"- {label} ({len(items)}): " + ", ".join(sample) + suffix]

    lines: list[str] = []
    lines += fmt("Added", added)
    lines += fmt("Modified", modified)
    lines += fmt("Deleted", deleted)
    if other:
        sample = other[:30]
        suffix = " …" if len(other) > 30 else ""
        lines.append(f"- Other ({len(other)}): " + ", ".join(sample) + suffix)

    return "\n".join(lines) if lines else "- Changes detected, but could not classify."


def extract_existing_changelog(readme_text: str) -> str:
    # We own the "## Changelog" section: everything after that header.
    m = re.search(r"^##\s+Changelog\s*$", readme_text, flags=re.MULTILINE)
    if not m:
        return ""
    return readme_text[m.end() :].strip()  # keep as-is


def build_new_changelog(existing_changelog: str, entry: str, keep_entries: int = 20) -> str:
    # Split by top-level entry headings we generate: "### YYYY-..."
    parts = []
    if existing_changelog:
        parts = re.split(r"(?m)^###\s+", existing_changelog)
        # re.split keeps leading text in parts[0]; normalize
        rebuilt = []
        for i, p in enumerate(parts):
            p = p.strip()
            if not p:
                continue
            if i == 0 and not existing_changelog.lstrip().startswith("###"):
                # stray preface text; drop
                continue
            rebuilt.append("### " + p)
        existing_entries = rebuilt
    else:
        existing_entries = []

    new_entries = [entry] + existing_entries
    return "\n\n".join(new_entries[:keep_entries]).strip() + "\n"


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: generate_readme.py <sync_dir> <template_path> [status_file]", file=sys.stderr)
        return 2

    sync_dir = Path(sys.argv[1]).resolve()
    template_path = Path(sys.argv[2]).resolve()
    status_file = Path(sys.argv[3]).resolve() if len(sys.argv) >= 4 else None

    template = read_text(template_path)
    if not template.strip():
        print(f"ERROR: template is empty: {template_path}", file=sys.stderr)
        return 3

    readme_path = sync_dir / "README.md"
    existing = read_text(readme_path)

    status_text = ""
    if status_file and status_file.exists():
        status_text = read_text(status_file)

    last_updated = utc_now_str()

    overview = "\n".join(
        [
            "This repository is an automatically-generated, *non-sensitive* snapshot of selected OpenClaw workspace context.",
            "It is intended for review/tweaks (skills, project scaffolding, automation state) without syncing secrets.",
        ]
    )

    skills = list_skill_names(sync_dir)
    skills_md = "- (none exported)" if not skills else "\n".join([f"- {s}" for s in skills])

    projects = list_projects(sync_dir)
    projects_md = "- (none exported)" if not projects else "\n".join([f"- {p}" for p in projects])

    cron_md = cron_summary(sync_dir)
    memory_md = memory_summary(sync_dir)

    existing_changelog = extract_existing_changelog(existing)
    changes_md = status_to_change_bullets(status_text)
    entry = "\n".join(
        [
            f"### {last_updated}",
            "", 
            "Changes in this sync:",
            changes_md,
        ]
    ).strip() + "\n"

    changelog = build_new_changelog(existing_changelog, entry)

    out = template
    out = out.replace("{{LAST_UPDATED}}", last_updated)
    out = out.replace("{{OVERVIEW}}", overview)
    out = out.replace("{{SKILLS}}", skills_md)
    out = out.replace("{{PROJECTS}}", projects_md)
    out = out.replace("{{CRON}}", cron_md)
    out = out.replace("{{MEMORY}}", memory_md)
    out = out.replace("{{CHANGELOG}}", changelog.strip() + "\n")

    # If README missing or empty, create it. Otherwise overwrite with our managed template output.
    readme_path.write_text(out, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
