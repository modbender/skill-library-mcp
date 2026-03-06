#!/usr/bin/env python3
"""
Humanizer Integration — discovers the humanizer skill and runs content
through it to produce natural-sounding output. Also handles blog post
creation and SEO optimization.

Importable as a module or runnable as CLI:
    python3 humanizer_integration.py --content "Technical text" --style casual --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


SKILL_SEARCH_PATHS = [
    Path.home() / ".openclaw" / "workspace" / "skills" / "humanizer",
    Path.home() / ".claude" / "skills" / "humanizer",
    Path.home() / ".agents" / "skills" / "humanizer",
    Path.home() / ".local" / "share" / "humanizer",
]


class HumanizerIntegration:
    """Discovers and invokes the humanizer skill for natural content."""

    def __init__(self, skill_path: Optional[Path] = None):
        self.skill_path = skill_path or self.discover_skill()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    @staticmethod
    def discover_skill() -> Optional[Path]:
        """Locate the humanizer skill on disk."""
        for candidate in SKILL_SEARCH_PATHS:
            if candidate.is_dir():
                for name in ("humanizer.py", "humanize.py", "main.py", "cli.py"):
                    if (candidate / name).exists():
                        return candidate
                scripts = candidate / "scripts"
                if scripts.is_dir():
                    for name in ("humanizer.py", "humanize.py", "main.py"):
                        if (scripts / name).exists():
                            return candidate
                return candidate
        env = os.environ.get("HUMANIZER_SKILL_PATH")
        if env:
            p = Path(env)
            if p.exists():
                return p
        return None

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def humanize(
        self,
        content: str,
        style: str = "casual",
        tone: str = "friendly",
    ) -> Dict[str, Any]:
        """Run content through the humanizer skill."""
        if not self.skill_path:
            return self._fallback_humanize(content, style, tone)

        entry = self._find_entry_point()
        if not entry:
            return self._fallback_humanize(content, style, tone)

        cmd = [
            "python3", str(entry),
            "--content", content,
            "--style", style,
            "--tone", tone,
            "--json",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return {
                    "ok": False,
                    "error": result.stderr.strip() or f"exit code {result.returncode}",
                }
            try:
                return {**json.loads(result.stdout), "ok": True}
            except json.JSONDecodeError:
                return {"ok": True, "humanized": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Humanizer timed out (120s)"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _find_entry_point(self) -> Optional[Path]:
        if not self.skill_path:
            return None
        for name in ("humanizer.py", "humanize.py", "main.py", "cli.py"):
            p = self.skill_path / name
            if p.exists():
                return p
            p = self.skill_path / "scripts" / name
            if p.exists():
                return p
        return None

    @staticmethod
    def _fallback_humanize(
        content: str, style: str, tone: str
    ) -> Dict[str, Any]:
        """Lightweight local humanization when the skill is unavailable."""
        text = content
        replacements = {
            "utilize": "use",
            "implement": "build",
            "leverage": "use",
            "facilitate": "help",
            "subsequently": "then",
            "aforementioned": "this",
            "in order to": "to",
            "it is important to note that": "",
            "it should be noted that": "",
        }
        lower = text.lower()
        for old, new in replacements.items():
            if old in lower:
                pattern = re.compile(re.escape(old), re.IGNORECASE)
                text = pattern.sub(new, text)
        return {
            "ok": True,
            "humanized": text,
            "method": "fallback",
            "note": "Humanizer skill not found — applied basic transformations only",
        }

    # ------------------------------------------------------------------
    # Blog post creation
    # ------------------------------------------------------------------

    def create_blog_post(
        self,
        topic: str,
        research_data: Optional[Dict[str, Any]] = None,
        word_count: int = 1500,
    ) -> Dict[str, Any]:
        """Generate a blog post, optionally using research data."""
        outline = self._generate_outline(topic, research_data)
        draft = self._generate_draft(topic, outline, word_count)
        humanized = self.humanize(draft, style="conversational", tone="friendly")
        final_content = humanized.get("humanized", draft)

        return {
            "ok": True,
            "topic": topic,
            "word_count": len(final_content.split()),
            "outline": outline,
            "content": final_content,
        }

    @staticmethod
    def _generate_outline(
        topic: str, research_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        sections = [
            f"# {topic}",
            "## Introduction",
            f"## What is {topic}?",
            "## Key Benefits",
            "## How to Get Started",
            "## Best Practices",
            "## Common Pitfalls",
            "## Conclusion",
        ]
        if research_data and "sections" in research_data:
            for section_name in research_data["sections"]:
                heading = section_name.replace("_", " ").title()
                if heading.lower() not in [s.lower().lstrip("# ") for s in sections]:
                    sections.insert(-1, f"## {heading}")
        return sections

    @staticmethod
    def _generate_draft(topic: str, outline: List[str], word_count: int) -> str:
        """Build a skeleton draft from the outline."""
        lines = []
        for heading in outline:
            lines.append(heading)
            lines.append("")
            if "introduction" in heading.lower():
                lines.append(
                    f"In this post we'll explore {topic} — what it is, why it "
                    "matters, and how you can start using it today."
                )
            elif "conclusion" in heading.lower():
                lines.append(
                    f"{topic} is an evolving space with plenty of room to "
                    "experiment. Start small, iterate, and share what you learn."
                )
            else:
                lines.append(f"[Content for {heading.lstrip('# ')} — expand to ~{word_count // len(outline)} words]")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # SEO optimization
    # ------------------------------------------------------------------

    @staticmethod
    def optimize_seo(content: str, keywords: List[str]) -> Dict[str, Any]:
        """Add basic SEO optimization to content."""
        lines = content.split("\n")
        title = ""
        for line in lines:
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
                break

        keyword_str = ", ".join(keywords)
        meta = (
            f"\n---\n"
            f"title: \"{title}\"\n"
            f"description: \"{title} — {keyword_str}\"\n"
            f"keywords: [{keyword_str}]\n"
            f"date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"---\n"
        )

        keyword_density: Dict[str, int] = {}
        content_lower = content.lower()
        for kw in keywords:
            count = content_lower.count(kw.lower())
            keyword_density[kw] = count

        return {
            "ok": True,
            "content": meta + content,
            "meta": {
                "title": title,
                "keywords": keywords,
                "keyword_density": keyword_density,
            },
        }


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Humanizer Integration — natural content generation"
    )
    parser.add_argument("--content", help="Content to humanize")
    parser.add_argument("--style", default="casual", help="Writing style")
    parser.add_argument("--tone", default="friendly", help="Writing tone")
    parser.add_argument("--blog-topic", help="Generate a blog post on this topic")
    parser.add_argument("--word-count", type=int, default=1500)
    parser.add_argument("--seo-keywords", help="Comma-separated SEO keywords")
    parser.add_argument("--skill-path", help="Override skill path")
    parser.add_argument("--json", action="store_true", dest="json_out")
    args = parser.parse_args()

    skill_path = Path(args.skill_path) if args.skill_path else None
    hi = HumanizerIntegration(skill_path=skill_path)

    if args.blog_topic:
        result = hi.create_blog_post(args.blog_topic, word_count=args.word_count)
        if args.seo_keywords:
            kws = [k.strip() for k in args.seo_keywords.split(",")]
            seo = hi.optimize_seo(result["content"], kws)
            result["content"] = seo["content"]
            result["seo"] = seo["meta"]
    elif args.content:
        result = hi.humanize(args.content, style=args.style, tone=args.tone)
    else:
        parser.error("Provide --content or --blog-topic")
        return

    if args.json_out:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        print(result.get("humanized") or result.get("content", ""))

    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
