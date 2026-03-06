#!/usr/bin/env python3
"""
Bidirectional memory sync between nanobot and overstory.
Pushes nanobot MEMORY.md context to overstory agents and pulls
agent insights back into nanobot memory.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=os.environ.get("BRIDGE_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("memory_sync")

DEFAULT_MEMORY_PATH = Path(
    os.environ.get(
        "NANOBOT_MEMORY_PATH",
        "/Users/ghost/.openclaw/workspace/MEMORY.md",
    )
)


class MemorySync:
    """Bidirectional memory synchronization between nanobot and overstory."""

    def __init__(self, memory_path: Optional[Path] = None):
        self.memory_path = Path(memory_path) if memory_path else DEFAULT_MEMORY_PATH

    def _read_memory(self) -> str:
        """Read current MEMORY.md contents."""
        if not self.memory_path.exists():
            log.warning("Memory file not found: %s", self.memory_path)
            return ""
        return self.memory_path.read_text(encoding="utf-8")

    def _write_memory(self, content: str) -> None:
        """Write content to MEMORY.md."""
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory_path.write_text(content, encoding="utf-8")
        log.info("Updated memory at %s", self.memory_path)

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse MEMORY.md into sections keyed by heading."""
        sections: Dict[str, str] = {}
        current_heading = "_preamble"
        lines: List[str] = []

        for line in content.splitlines():
            heading_match = re.match(r"^(#{1,3})\s+(.+)$", line)
            if heading_match:
                if lines:
                    sections[current_heading] = "\n".join(lines).strip()
                current_heading = heading_match.group(2).strip()
                lines = []
            else:
                lines.append(line)

        if lines:
            sections[current_heading] = "\n".join(lines).strip()

        return sections

    def sync_to_overstory(self, memory_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Push nanobot MEMORY.md context to overstory agents.
        Returns the memory payload ready to be sent.
        """
        path = Path(memory_path) if memory_path else self.memory_path
        if not path.exists():
            return {"ok": False, "error": f"Memory file not found: {path}"}

        content = path.read_text(encoding="utf-8")
        sections = self._parse_sections(content)

        payload = {
            "source": "nanobot",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "memory_path": str(path),
            "sections": list(sections.keys()),
            "content": content,
            "char_count": len(content),
        }

        log.info(
            "Prepared memory sync payload: %d sections, %d chars",
            len(sections), len(content),
        )
        return {"ok": True, "payload": payload}

    def sync_from_overstory(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update nanobot MEMORY.md with insights from overstory agents.
        insights should have: {"insight": str, "agent": str (optional), "section": str (optional)}
        """
        insight_text = insights.get("insight", "")
        if not insight_text:
            return {"ok": False, "error": "No insight text provided"}

        agent = insights.get("agent", "overstory-agent")
        section = insights.get("section", "Overstory Insights")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        entry = f"- [{timestamp}] ({agent}) {insight_text}"

        return self.update_memory(section, entry, source=agent)

    def get_context_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Extract relevant memory context for a specific agent.
        Filters by capability keywords inferred from the agent name.
        """
        content = self._read_memory()
        if not content:
            return {"agent": agent_name, "context": "", "sections": []}

        sections = self._parse_sections(content)

        cap_keywords = {
            "researcher": ["research", "analysis", "data", "trends", "papers"],
            "builder": ["code", "build", "deploy", "api", "feature", "bug"],
            "scout": ["explore", "search", "find", "discover"],
            "blogger": ["blog", "article", "content", "publish"],
            "social-media": ["social", "tweet", "post", "twitter"],
            "scribe": ["log", "memory", "note", "document", "summary"],
            "reviewer": ["review", "merge", "audit", "feedback"],
        }

        relevant_keywords: List[str] = []
        agent_lower = agent_name.lower()
        for cap, keywords in cap_keywords.items():
            if cap in agent_lower:
                relevant_keywords = keywords
                break

        if not relevant_keywords:
            return {
                "agent": agent_name,
                "context": content[:2000],
                "sections": list(sections.keys()),
                "note": "No capability match; returning truncated full memory",
            }

        matched_sections: Dict[str, str] = {}
        for heading, body in sections.items():
            combined = (heading + " " + body).lower()
            if any(kw in combined for kw in relevant_keywords):
                matched_sections[heading] = body

        context_parts = [f"## {h}\n{b}" for h, b in matched_sections.items()]
        context = "\n\n".join(context_parts)

        return {
            "agent": agent_name,
            "context": context[:4000],
            "sections": list(matched_sections.keys()),
            "keywords_used": relevant_keywords,
        }

    def update_memory(
        self, section: str, content: str, source: str = "overstory"
    ) -> Dict[str, Any]:
        """Add an entry to MEMORY.md under the given section heading."""
        current = self._read_memory()

        section_header = f"## {section}"
        if section_header in current:
            idx = current.index(section_header)
            end_of_header = current.index("\n", idx) + 1

            next_section = re.search(r"\n## ", current[end_of_header:])
            if next_section:
                insert_at = end_of_header + next_section.start()
            else:
                insert_at = len(current)

            updated = current[:insert_at].rstrip() + "\n" + content + "\n\n" + current[insert_at:].lstrip()
        else:
            updated = current.rstrip() + f"\n\n{section_header}\n\n{content}\n"

        self._write_memory(updated)

        log.info("Added memory entry to section '%s' (source=%s)", section, source)
        return {
            "ok": True,
            "section": section,
            "source": source,
            "memory_path": str(self.memory_path),
        }

    def prune_memory(self, max_entries: int = 100) -> Dict[str, Any]:
        """Remove oldest bullet entries beyond max_entries limit."""
        content = self._read_memory()
        if not content:
            return {"ok": True, "pruned": 0}

        lines = content.splitlines()
        bullet_indices = [i for i, line in enumerate(lines) if line.strip().startswith("- [")]
        overflow = len(bullet_indices) - max_entries

        if overflow <= 0:
            return {"ok": True, "pruned": 0, "total_entries": len(bullet_indices)}

        remove_set = set(bullet_indices[:overflow])
        pruned_lines = [line for i, line in enumerate(lines) if i not in remove_set]

        self._write_memory("\n".join(pruned_lines))

        log.info("Pruned %d oldest entries (kept %d)", overflow, max_entries)
        return {"ok": True, "pruned": overflow, "remaining": max_entries}


# ── CLI interface ───────────────────────────────────────────────

def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Bidirectional memory sync: nanobot ↔ overstory")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("sync", help="Sync memory between nanobot and overstory")
    p_sync.add_argument(
        "--direction", required=True,
        choices=["to_overstory", "from_overstory"],
        help="Sync direction",
    )
    p_sync.add_argument("--insight", default=None, help="Insight text (for from_overstory)")
    p_sync.add_argument("--agent", default=None, help="Agent name (for from_overstory)")
    p_sync.add_argument("--section", default=None, help="Memory section (for from_overstory)")
    p_sync.add_argument("--memory-path", default=None, help="Override memory path")
    p_sync.add_argument("--json", action="store_true")

    p_context = sub.add_parser("context", help="Get memory context for an agent")
    p_context.add_argument("--agent", required=True, help="Agent name")
    p_context.add_argument("--json", action="store_true")

    p_prune = sub.add_parser("prune", help="Prune old memory entries")
    p_prune.add_argument("--max-entries", type=int, default=100)
    p_prune.add_argument("--json", action="store_true")

    p_update = sub.add_parser("update", help="Add a memory entry")
    p_update.add_argument("--section", required=True)
    p_update.add_argument("--content", required=True)
    p_update.add_argument("--source", default="overstory")
    p_update.add_argument("--json", action="store_true")

    args = parser.parse_args()

    mem_path = Path(args.memory_path) if hasattr(args, "memory_path") and args.memory_path else None
    sync = MemorySync(memory_path=mem_path)

    if args.command == "sync":
        if args.direction == "to_overstory":
            result = sync.sync_to_overstory(memory_path=mem_path)
        else:
            insights = {}
            if args.insight:
                insights["insight"] = args.insight
            if args.agent:
                insights["agent"] = args.agent
            if args.section:
                insights["section"] = args.section
            if not insights.get("insight"):
                result = {"error": "Must provide --insight for from_overstory sync"}
            else:
                result = sync.sync_from_overstory(insights)

    elif args.command == "context":
        result = sync.get_context_for_agent(args.agent)

    elif args.command == "prune":
        result = sync.prune_memory(args.max_entries)

    elif args.command == "update":
        result = sync.update_memory(args.section, args.content, args.source)

    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    _cli()
