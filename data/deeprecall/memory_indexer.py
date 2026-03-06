"""
Memory Indexer — Auto-generates a structured index of agent memories.

Creates MEMORY_INDEX.md — a lightweight table of contents that maps:
- Topics → which files contain them
- Timeline → what happened when
- People → where they're mentioned
- Projects → related files

RLM reads this FIRST, then jumps directly to the right file/section.
Without this, RLM would blindly search through every daily log.

The more memory you have, the more this matters.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import defaultdict


def extract_topics(content: str, filename: str) -> dict:
    """Extract structured info from a memory file."""
    info = {
        "headers": [],
        "people": set(),
        "projects": set(),
        "keywords": set(),
        "summary_lines": [],
    }

    # Common people patterns: **Name** or "Name" in context
    # Only match short standalone names, not multi-word technical terms
    people_pattern = re.compile(
        r'\*\*([A-Z][a-z]{1,12}(?:\s[A-Z][a-z]{1,12})?)\*\*'
    )

    # Project patterns: things that look like project names
    project_keywords = {
        "fractal", "deeprecall", "deep recall", "ide", "rlm",
        "tauri", "fast-rlm", "whisboo", "anamnesis",
    }

    # Words that look like names but aren't
    NOT_PEOPLE = {
        "done", "note", "important", "warning", "error",
        "status", "update", "pending", "blocked", "todo",
        "the", "this", "that", "overview", "key", "mode",
        "build", "plan", "test", "review", "settings",
        "editor", "context", "smart", "pinned", "live",
        "agent", "model", "budget", "cost", "file",
        "phase", "layer", "index", "scope", "query",
        "soul", "mind", "bridge", "core", "setup",
    }

    for line in content.split("\n"):
        stripped = line.strip()

        # Headers
        if stripped.startswith("#"):
            header = stripped.lstrip("#").strip()
            if header and len(header) > 1:
                info["headers"].append(header)

        # People (bold names)
        for match in people_pattern.finditer(stripped):
            name = match.group(1)
            # Filter out common non-names
            if name.lower() not in NOT_PEOPLE and name.split()[0].lower() not in NOT_PEOPLE:
                info["people"].add(name)

        # Projects
        lower = stripped.lower()
        for kw in project_keywords:
            if kw in lower:
                info["projects"].add(kw)

        # Key action lines (checkmarks, decisions)
        if any(marker in stripped for marker in ["✅", "- [x]", "→", "Decision:", "Key"]):
            clean = stripped.lstrip("- [x]✅ ").strip()
            if len(clean) > 10 and len(clean) < 200:
                info["summary_lines"].append(clean)

        # Bold keywords as topics
        for match in re.finditer(r'\*\*(.+?)\*\*', stripped):
            term = match.group(1).strip()
            if 2 < len(term) < 40:
                info["keywords"].add(term.lower())

    return info


def build_memory_index(workspace: Optional[Path] = None) -> str:
    """
    Build MEMORY_INDEX.md content from all memory files.

    Returns the index as a markdown string.
    """
    workspace = workspace or Path(
        os.environ.get("OPENCLAW_WORKSPACE",
                       os.path.expanduser("~/.openclaw/workspace"))
    )

    memory_dir = workspace / "memory"
    memory_md = workspace / "MEMORY.md"

    # Collect all daily logs
    daily_logs = {}
    if memory_dir.exists():
        for f in sorted(memory_dir.glob("*.md")):
            # Extract date from filename
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})", f.name)
            if date_match:
                date_str = date_match.group(1)
                content = f.read_text(errors="replace")
                topics = extract_topics(content, f.name)
                daily_logs[date_str] = {
                    "path": f"memory/{f.name}",
                    "size": len(content),
                    "topics": topics,
                }

    # Analyze MEMORY.md
    memory_topics = None
    if memory_md.exists():
        content = memory_md.read_text(errors="replace")
        memory_topics = extract_topics(content, "MEMORY.md")

    # Build topic → files mapping
    topic_map = defaultdict(set)
    people_map = defaultdict(set)
    project_map = defaultdict(set)

    if memory_topics:
        for kw in memory_topics["keywords"]:
            topic_map[kw].add("MEMORY.md")
        for p in memory_topics["people"]:
            people_map[p].add("MEMORY.md")
        for proj in memory_topics["projects"]:
            project_map[proj].add("MEMORY.md")

    for date_str, log in daily_logs.items():
        t = log["topics"]
        for kw in t["keywords"]:
            topic_map[kw].add(log["path"])
        for p in t["people"]:
            people_map[p].add(log["path"])
        for proj in t["projects"]:
            project_map[proj].add(log["path"])

    # Generate the index
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Memory Index",
        f"Auto-generated: {now}",
        "",
        "---",
        "",
    ]

    # Timeline
    lines.append("## Timeline")
    for date_str in sorted(daily_logs.keys(), reverse=True):
        log = daily_logs[date_str]
        t = log["topics"]
        # Get top 3 headers as summary
        summary = ", ".join(t["headers"][:4]) if t["headers"] else "No headers"
        lines.append(f"- **{date_str}** → `{log['path']}` ({log['size']:,} chars)")
        lines.append(f"  Topics: {summary}")
    lines.append("")

    # People
    if people_map:
        lines.append("## People")
        for person in sorted(people_map.keys()):
            files = sorted(people_map[person])
            files_str = ", ".join(f"`{f}`" for f in files)
            lines.append(f"- **{person}** → {files_str}")
        lines.append("")

    # Projects
    if project_map:
        lines.append("## Projects")
        for proj in sorted(project_map.keys()):
            files = sorted(project_map[proj])
            files_str = ", ".join(f"`{f}`" for f in files)
            lines.append(f"- **{proj}** → {files_str}")
        lines.append("")

    # Topic map (top 30 most referenced topics)
    if topic_map:
        lines.append("## Topics")
        # Sort by number of files referencing the topic
        sorted_topics = sorted(
            topic_map.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:30]
        for topic, files in sorted_topics:
            files_str = ", ".join(f"`{f}`" for f in sorted(files))
            lines.append(f"- {topic} → {files_str}")
        lines.append("")

    # Key events from daily logs (most recent first)
    lines.append("## Key Events")
    for date_str in sorted(daily_logs.keys(), reverse=True):
        log = daily_logs[date_str]
        summaries = log["topics"]["summary_lines"][:5]
        if summaries:
            lines.append(f"### {date_str}")
            for s in summaries:
                lines.append(f"- {s}")
            lines.append("")

    # Long-term memory summary
    if memory_topics and memory_topics["headers"]:
        lines.append("## MEMORY.md Sections")
        for h in memory_topics["headers"]:
            lines.append(f"- {h}")
        lines.append("")

    lines.append("---")
    lines.append("*This index is auto-generated. RLM reads this first to navigate memory efficiently.*")

    return "\n".join(lines)


def update_memory_index(workspace: Optional[Path] = None) -> Path:
    """Build and write MEMORY_INDEX.md to the workspace."""
    workspace = workspace or Path(
        os.environ.get("OPENCLAW_WORKSPACE",
                       os.path.expanduser("~/.openclaw/workspace"))
    )

    index_content = build_memory_index(workspace)
    index_path = workspace / "MEMORY_INDEX.md"
    index_path.write_text(index_content)

    return index_path


if __name__ == "__main__":
    path = update_memory_index()
    print(f"✅ Memory index written to: {path}")
    print()
    print(path.read_text())
