#!/usr/bin/env python3
"""
Format SKILL.md for optimal display on ClawHub.
Output structure: Description | Installation | Usage | Examples | Commands.
"""

import argparse
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str):
    """Extract YAML frontmatter and body. Returns (frontmatter_dict, body_str)."""
    frontmatter = {}
    body = content
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                import yaml
                frontmatter = yaml.safe_load(parts[1]) or {}
            except ImportError:
                # Minimal key: value parsing if no PyYAML
                for line in parts[1].strip().split("\n"):
                    m = re.match(r"^(\w+):\s*(.*)$", line)
                    if m:
                        val = m.group(2).strip().strip('"').strip("'")
                        frontmatter[m.group(1)] = val
            body = parts[2].lstrip("\n")
    return frontmatter, body


def extract_sections(body: str):
    """Split body by ## headers. Returns list of (title, content)."""
    sections = []
    pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    last_end = 0
    for m in pattern.finditer(body):
        if last_end < m.start():
            sections.append(("_intro", body[last_end:m.start()].strip()))
        start = m.end()
        next_m = pattern.search(body, start)
        end = next_m.start() if next_m else len(body)
        sections.append((m.group(1).strip(), body[start:end].strip()))
        last_end = end
    if last_end < len(body) and not sections:
        sections.append(("_intro", body.strip()))
    return sections


def normalize_section_title(title: str):
    """Map variant titles to canonical ClawHub section names."""
    t = title.lower()
    if "description" in t or "overview" in t or "about" in t:
        return "Description"
    if "install" in t or "setup" in t:
        return "Installation"
    if "usage" in t or "how to use" in t or "when to use" in t or "use" in t:
        return "Usage"
    if "example" in t:
        return "Examples"
    if "command" in t or "cli" in t:
        return "Commands"
    return title


def collect_into_canonical(sections: list, frontmatter: dict):
    """Group sections by canonical name. Returns dict section_name -> list of content blocks."""
    canonical = {
        "Description": [],
        "Installation": [],
        "Usage": [],
        "Examples": [],
        "Commands": [],
    }
    intro = []
    other = []

    for title, content in sections:
        if title == "_intro":
            intro.append(content)
            continue
        can = normalize_section_title(title)
        if can in canonical:
            canonical[can].append((title, content))
        else:
            other.append((title, content))

    # Build description from frontmatter + intro
    desc_parts = []
    if frontmatter.get("description"):
        desc_parts.append(frontmatter["description"])
    if intro:
        intro_text = re.sub(r"^#\s+.+$", "", intro[0], count=1).strip()
        if intro_text:
            desc_parts.append(intro_text)
    if desc_parts:
        canonical["Description"].insert(0, ("Description", "\n\n".join(desc_parts)))

    return canonical, other


def generate_examples_from_description(description: str, name: str):
    """Generate 1–2 benefit-focused example blocks from the skill description."""
    name_slug = name or "skill"
    lines = [
        "**Example: See the benefit**",
        f"*Scenario:* User needs what {name_slug} provides (see description above).",
        f"*Action:* Run the main command for this skill (see **Commands** below).",
        "*Outcome:* The skill delivers the described benefit—faster, clearer, or more reliable.",
        "",
        "Add concrete examples here: paste real command + short outcome to showcase benefits.",
    ]
    return "\n".join(lines)


def merge_commands(content_blocks: list):
    """Merge multiple command sections into one: collect code blocks and bullet lists."""
    merged = []
    for _title, content in content_blocks:
        # Preserve code blocks and lines that look like commands
        merged.append(content)
    return "\n\n".join(merged)


def emit_markdown(frontmatter: dict, canonical: dict, other: list, generate_examples: bool):
    """Emit full markdown in ClawHub order."""
    out = []
    # Frontmatter
    out.append("---")
    for k, v in frontmatter.items():
        if v is not None:
            out.append(f"{k}: {v}")
    out.append("---")
    out.append("")

    # Title
    display = frontmatter.get("displayName") or frontmatter.get("name", "Skill").replace("-", " ").title()
    out.append(f"# {display}")
    out.append("")

    order = ["Description", "Installation", "Usage", "Examples", "Commands"]
    for sec in order:
        blocks = canonical.get(sec, [])
        if not blocks and sec == "Examples" and generate_examples:
            blocks = [("Examples", generate_examples_from_description(
                frontmatter.get("description", ""), frontmatter.get("name", "")))]
        if not blocks:
            continue
        out.append(f"## {sec}")
        out.append("")
        for _title, content in blocks:
            if content.strip():
                out.append(content.strip())
                out.append("")
        out.append("")

    # Other sections (preserve under original titles)
    for title, content in other:
        if content.strip():
            out.append(f"## {title}")
            out.append("")
            out.append(content.strip())
            out.append("")
            out.append("")

    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Format SKILL.md for ClawHub display")
    ap.add_argument("input", type=Path, help="Path to SKILL.md or skill directory")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output file (default: stdout)")
    ap.add_argument("--generate-examples", action="store_true", help="Generate example block from description if missing")
    ap.add_argument("--inplace", action="store_true", help="Overwrite input file (use with care)")
    ap.add_argument("--security-check", action="store_true", help="Run security review checks after formatting")
    args = ap.parse_args()

    path = args.input
    if not path.is_file():
        path = path / "SKILL.md"
    if not path.is_file():
        print(f"Error: not a file: {args.input}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)
    sections = extract_sections(body)
    canonical, other = collect_into_canonical(sections, frontmatter)
    result = emit_markdown(frontmatter, canonical, other, args.generate_examples)

    if args.inplace:
        path.write_text(result, encoding="utf-8")
        print(f"Wrote {path}", file=sys.stderr)
    elif args.output:
        args.output.write_text(result, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(result, end="")
    
    # Run security check if requested
    if args.security_check:
        skill_dir = path.parent if path.name == "SKILL.md" else path
        security_script = Path(__file__).parent / "security_review.py"
        if security_script.exists():
            import subprocess
            print("\n" + "=" * 70, file=sys.stderr)
            print("Running security review...", file=sys.stderr)
            print("=" * 70 + "\n", file=sys.stderr)
            try:
                subprocess.run([sys.executable, str(security_script), str(skill_dir)], check=False)
            except Exception as e:
                print(f"Warning: Security check failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
