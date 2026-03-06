#!/usr/bin/env python3
"""
Memory Curator — extracts insights from daily notes and commits
significant patterns to MEMORY.md.

Importable as a module or runnable as CLI:
    python3 memory_curator.py curate --days 7 --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_MEMORY_PATH = Path("/Users/ghost/.openclaw/workspace/MEMORY.md")
DEFAULT_DAILY_DIRS = [
    Path("/Users/ghost/.openclaw/workspace/memory"),
    Path("/Users/ghost/.openclaw/workspace/Notes/daily"),
]

INSIGHT_MARKERS = re.compile(
    r"(learned|realized|discovered|decided|important|remember|note to self"
    r"|key takeaway|pattern|recurring|always|never|don't forget)",
    re.IGNORECASE,
)

ERROR_PATTERN = re.compile(
    r"(error|failed|broken|bug|crash|fix|issue|problem)", re.IGNORECASE
)
DECISION_PATTERN = re.compile(
    r"(decided|chose|switched|migrated|adopted|dropped|replaced)", re.IGNORECASE
)
PREFERENCE_PATTERN = re.compile(
    r"(prefer|like|dislike|love|hate|better|worse|favorite)", re.IGNORECASE
)


class MemoryCurator:
    """Curates long-term memory from daily notes."""

    def __init__(
        self,
        memory_path: Optional[Path] = None,
        daily_dirs: Optional[List[Path]] = None,
    ):
        self.memory_path = memory_path or DEFAULT_MEMORY_PATH
        self.daily_dirs = daily_dirs or DEFAULT_DAILY_DIRS

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def read_memory(self, path: Optional[Path] = None) -> str:
        """Read current MEMORY.md contents."""
        target = path or self.memory_path
        if target.exists():
            return target.read_text(encoding="utf-8")
        return ""

    def read_daily_notes(self, days: int = 7) -> List[Dict[str, Any]]:
        """Read recent daily note files."""
        cutoff = datetime.now() - timedelta(days=days)
        notes: List[Dict[str, Any]] = []

        for daily_dir in self.daily_dirs:
            if not daily_dir.exists():
                continue
            for path in sorted(daily_dir.glob("*.md")):
                date_match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
                if not date_match:
                    continue
                try:
                    file_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                except ValueError:
                    continue
                if file_date < cutoff:
                    continue
                try:
                    content = path.read_text(encoding="utf-8")
                    notes.append({
                        "date": date_match.group(1),
                        "path": str(path),
                        "content": content,
                        "size": len(content),
                    })
                except Exception:
                    pass

        notes.sort(key=lambda n: n["date"])
        return notes

    # ------------------------------------------------------------------
    # Insight extraction
    # ------------------------------------------------------------------

    def extract_insights(self, daily_notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find insights worth keeping from daily notes."""
        insights: List[Dict[str, Any]] = []

        for note in daily_notes:
            for line in note["content"].splitlines():
                stripped = line.strip().lstrip("- ").lstrip("* ")
                if not stripped or len(stripped) < 10:
                    continue

                categories: List[str] = []
                if INSIGHT_MARKERS.search(stripped):
                    categories.append("insight")
                if ERROR_PATTERN.search(stripped):
                    categories.append("error")
                if DECISION_PATTERN.search(stripped):
                    categories.append("decision")
                if PREFERENCE_PATTERN.search(stripped):
                    categories.append("preference")

                if categories:
                    insights.append({
                        "date": note["date"],
                        "text": stripped[:500],
                        "categories": categories,
                    })

        return insights

    # ------------------------------------------------------------------
    # Significance check
    # ------------------------------------------------------------------

    @staticmethod
    def should_commit(insight: Dict[str, Any], all_insights: List[Dict[str, Any]], threshold: int = 3) -> bool:
        """Determine if a pattern is significant enough to commit.

        An insight is significant if:
        - It appears as a pattern (similar text across multiple days)
        - It's a decision or explicit lesson (categories include 'decision' or 'insight')
        - The threshold count of similar items is met
        """
        if "decision" in insight.get("categories", []):
            return True
        if "insight" in insight.get("categories", []):
            return True

        normalized = re.sub(r"\d+", "N", insight["text"].lower()[:80])
        similar_count = 0
        for other in all_insights:
            other_norm = re.sub(r"\d+", "N", other["text"].lower()[:80])
            if normalized == other_norm and other["date"] != insight.get("date"):
                similar_count += 1
        return similar_count >= threshold

    # ------------------------------------------------------------------
    # Committing
    # ------------------------------------------------------------------

    def commit_to_memory(
        self,
        insights: List[Dict[str, Any]],
        memory_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Add insights to MEMORY.md."""
        target = memory_path or self.memory_path
        existing = self.read_memory(target)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        new_lines: List[str] = []
        committed = 0
        for insight in insights:
            line = f"- [{insight['date']}] {insight['text']}"
            if line not in existing:
                new_lines.append(line)
                committed += 1

        if not new_lines:
            return {"ok": True, "committed": 0, "message": "No new insights to commit"}

        block = (
            f"\n\n## Curated Insights — {now}\n\n"
            + "\n".join(new_lines)
            + "\n"
        )

        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(block)

        return {"ok": True, "committed": committed, "path": str(target)}

    # ------------------------------------------------------------------
    # Pruning
    # ------------------------------------------------------------------

    def prune_outdated(self, days: int = 90) -> Dict[str, Any]:
        """Remove entries older than *days* from MEMORY.md."""
        content = self.read_memory()
        if not content:
            return {"ok": True, "pruned": 0}

        cutoff = datetime.now() - timedelta(days=days)
        lines = content.splitlines()
        kept: List[str] = []
        pruned = 0

        for line in lines:
            date_match = re.search(r"\[(\d{4}-\d{2}-\d{2})\]", line)
            if date_match:
                try:
                    entry_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                    if entry_date < cutoff:
                        pruned += 1
                        continue
                except ValueError:
                    pass
            kept.append(line)

        if pruned > 0:
            self.memory_path.write_text("\n".join(kept) + "\n", encoding="utf-8")

        return {"ok": True, "pruned": pruned}

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def generate_summary(self) -> Dict[str, Any]:
        """Overview of current memory state."""
        content = self.read_memory()
        daily_notes = self.read_daily_notes(days=30)

        entry_count = sum(
            1 for line in content.splitlines()
            if line.strip().startswith("- [")
        )

        categories: Counter = Counter()
        for line in content.splitlines():
            lower = line.lower()
            if ERROR_PATTERN.search(lower):
                categories["error"] += 1
            if DECISION_PATTERN.search(lower):
                categories["decision"] += 1
            if PREFERENCE_PATTERN.search(lower):
                categories["preference"] += 1
            if INSIGHT_MARKERS.search(lower):
                categories["insight"] += 1

        return {
            "ok": True,
            "memory_path": str(self.memory_path),
            "memory_size_bytes": len(content),
            "entry_count": entry_count,
            "categories": dict(categories),
            "daily_notes_count": len(daily_notes),
            "daily_notes_span": (
                f"{daily_notes[0]['date']} to {daily_notes[-1]['date']}"
                if daily_notes else "none"
            ),
        }

    # ------------------------------------------------------------------
    # Full curation pipeline
    # ------------------------------------------------------------------

    def curate(self, days: int = 7) -> Dict[str, Any]:
        """Run the full curation pipeline: read → extract → filter → commit."""
        notes = self.read_daily_notes(days)
        if not notes:
            return {
                "ok": True,
                "message": f"No daily notes found in last {days} days",
                "committed": 0,
            }

        all_insights = self.extract_insights(notes)
        significant = [
            i for i in all_insights
            if self.should_commit(i, all_insights)
        ]

        if not significant:
            return {
                "ok": True,
                "message": "No significant insights found",
                "total_insights": len(all_insights),
                "committed": 0,
            }

        commit_result = self.commit_to_memory(significant)
        return {
            **commit_result,
            "total_insights": len(all_insights),
            "significant_insights": len(significant),
        }


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Memory Curator — extracts insights and curates MEMORY.md"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # curate
    cu = sub.add_parser("curate", help="Run full curation pipeline")
    cu.add_argument("--days", type=int, default=7)
    cu.add_argument("--memory-path", help="Override MEMORY.md path")
    cu.add_argument("--json", action="store_true", dest="json_out")

    # summary
    sm = sub.add_parser("summary", help="Show memory state summary")
    sm.add_argument("--json", action="store_true", dest="json_out")

    # prune
    pr = sub.add_parser("prune", help="Remove outdated entries")
    pr.add_argument("--days", type=int, default=90, help="Remove entries older than N days")
    pr.add_argument("--json", action="store_true", dest="json_out")

    args = parser.parse_args()

    memory_path = Path(args.memory_path) if getattr(args, "memory_path", None) else None
    curator = MemoryCurator(memory_path=memory_path)

    if args.command == "curate":
        result = curator.curate(args.days)
    elif args.command == "summary":
        result = curator.generate_summary()
    elif args.command == "prune":
        result = curator.prune_outdated(args.days)
    else:
        result = {"ok": False, "error": f"Unknown command: {args.command}"}

    if getattr(args, "json_out", False):
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        for k, v in result.items():
            print(f"{k}: {v}")

    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
