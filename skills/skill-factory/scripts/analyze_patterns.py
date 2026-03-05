#!/usr/bin/env python3
"""
analyze_patterns.py — Scan installed OpenClaw skills and extract reusable patterns.

Usage:
    python3 analyze_patterns.py [--scan-dirs DIR1,DIR2] [--output PATH] [--query TERM]

Options:
    --scan-dirs   Comma-separated list of skill directories to scan
                  Default: ~/.openclaw/workspace/skills/,~/.nvm/.../openclaw/skills/
    --output      Write report to this path (default: stdout)
    --query       Filter patterns relevant to a search term
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict


DEFAULT_SCAN_DIRS = [
    "~/.openclaw/workspace/skills/",
    "~/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/",
]


def find_skill_dirs(scan_dirs):
    """Find all directories containing a SKILL.md file."""
    skills = []
    for base in scan_dirs:
        base = Path(base).expanduser()
        if not base.exists():
            continue
        for entry in base.iterdir():
            skill_md = entry / "SKILL.md"
            if skill_md.exists():
                skills.append(entry)
    return skills


def parse_skill(skill_dir):
    """Parse a SKILL.md into structured data."""
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(errors="replace")

    # Extract frontmatter
    name, description = "", ""
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        name_m = re.search(r'^name:\s*(.+)$', fm, re.MULTILINE)
        desc_m = re.search(r'^description:\s*"(.+)"', fm, re.MULTILINE | re.DOTALL)
        if name_m:
            name = name_m.group(1).strip()
        if desc_m:
            description = desc_m.group(1).strip()

    # Extract code blocks (bash commands)
    code_blocks = re.findall(r'```(?:bash|sh)\n(.*?)```', text, re.DOTALL)

    # Extract CLI tools used
    tools = set()
    tool_patterns = [
        r'\b(docker|docker-compose|docker compose)\b',
        r'\b(curl|wget|jq)\b',
        r'\b(python3?|node|npm|npx)\b',
        r'\b(openclaw|gog|fast-browser-use)\b',
        r'\b(crontab|systemctl|screen|tmux)\b',
        r'\b(git|gh)\b',
    ]
    for pattern in tool_patterns:
        for match in re.findall(pattern, text, re.IGNORECASE):
            tools.add(match.lower())

    # Extract trigger phrases from description
    trigger_phrases = []
    if description:
        # Look for quoted phrases or "use when" clauses
        phrases = re.findall(r"'([^']+)'|\"([^\"]+)\"|\buse when\b(.+?)(?:\.|,|$)", description, re.IGNORECASE)
        for p in phrases:
            phrase = next((x for x in p if x), "").strip()
            if phrase and len(phrase) > 5:
                trigger_phrases.append(phrase)
        # Also extract the description words as trigger vocabulary
        trigger_phrases.append(description[:120])

    # Extract output formats mentioned
    output_formats = []
    for fmt in ['json', 'markdown', 'csv', 'yaml', 'table', 'log']:
        if fmt in text.lower():
            output_formats.append(fmt)

    # Extract error handling patterns
    error_patterns = []
    for pat in ['retry', 'circuit breaker', 'fallback', 'timeout', 'backoff', 'cool.?down', 'max.attempt']:
        if re.search(pat, text, re.IGNORECASE):
            error_patterns.append(pat.replace('.?', ' ').replace('.', ' '))

    return {
        "name": name or skill_dir.name,
        "description": description,
        "tools": sorted(tools),
        "trigger_phrases": trigger_phrases,
        "output_formats": output_formats,
        "error_patterns": error_patterns,
        "code_examples": len(code_blocks),
        "path": str(skill_dir),
    }


def synthesize_patterns(skills):
    """Aggregate patterns across all skills."""
    all_tools = defaultdict(list)
    all_triggers = []
    all_output_formats = defaultdict(int)
    all_error_patterns = defaultdict(int)

    for s in skills:
        for tool in s["tools"]:
            all_tools[tool].append(s["name"])
        all_triggers.extend([(phrase, s["name"]) for phrase in s["trigger_phrases"]])
        for fmt in s["output_formats"]:
            all_output_formats[fmt] += 1
        for pat in s["error_patterns"]:
            all_error_patterns[pat] += 1

    return {
        "tools": dict(all_tools),
        "trigger_vocab": all_triggers,
        "output_formats": dict(all_output_formats),
        "error_patterns": dict(all_error_patterns),
    }


def render_report(skills, patterns, query=None):
    """Render markdown report."""
    lines = ["# OpenClaw Skill Patterns", f"\n_Scanned {len(skills)} skills._\n"]

    if query:
        lines.append(f"> Filtered for: **{query}**\n")

    # Skills table
    lines.append("## Skills Inventory\n")
    lines.append("| Skill | Tools | Examples | Error Handling |")
    lines.append("|-------|-------|----------|----------------|")
    for s in sorted(skills, key=lambda x: x["name"]):
        if query and query.lower() not in s["name"].lower() and query.lower() not in s["description"].lower():
            continue
        tools = ", ".join(s["tools"][:4]) or "—"
        error = ", ".join(s["error_patterns"][:2]) or "—"
        lines.append(f"| {s['name']} | {tools} | {s['code_examples']} | {error} |")

    # Tool patterns
    lines.append("\n## Tool Usage Patterns\n")
    for tool, skill_names in sorted(patterns["tools"].items(), key=lambda x: -len(x[1])):
        if query and query.lower() not in tool:
            if not any(query.lower() in n for n in skill_names):
                continue
        lines.append(f"**{tool}** — used in: {', '.join(skill_names)}")

    # Output formats
    lines.append("\n## Output Formats\n")
    for fmt, count in sorted(patterns["output_formats"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{fmt}` — {count} skills")

    # Error handling patterns
    lines.append("\n## Error Handling Patterns\n")
    for pat, count in sorted(patterns["error_patterns"].items(), key=lambda x: -x[1]):
        lines.append(f"- **{pat}** — {count} skills")

    # Trigger vocabulary
    lines.append("\n## Trigger Phrase Vocabulary\n")
    lines.append("Common description patterns from existing skills:\n")
    seen = set()
    for phrase, skill_name in patterns["trigger_vocab"]:
        if phrase[:40] in seen:
            continue
        seen.add(phrase[:40])
        if query and query.lower() not in phrase.lower() and query.lower() not in skill_name.lower():
            continue
        snippet = phrase[:100].replace('\n', ' ')
        lines.append(f"- [{skill_name}] `{snippet}`")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze OpenClaw skill patterns")
    parser.add_argument("--scan-dirs", default=",".join(DEFAULT_SCAN_DIRS),
                        help="Comma-separated skill directories to scan")
    parser.add_argument("--output", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--query", default=None, help="Filter patterns by term")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")
    args = parser.parse_args()

    scan_dirs = [d.strip() for d in args.scan_dirs.split(",") if d.strip()]
    skill_dirs = find_skill_dirs(scan_dirs)

    if not skill_dirs:
        print("No skills found in scan directories.", file=sys.stderr)
        sys.exit(1)

    skills = [parse_skill(d) for d in skill_dirs]
    patterns = synthesize_patterns(skills)

    if args.json:
        output = json.dumps({"skills": skills, "patterns": patterns}, indent=2)
    else:
        output = render_report(skills, patterns, query=args.query)

    if args.output:
        out_path = Path(args.output).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output)
        print(f"Report written to {out_path}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
