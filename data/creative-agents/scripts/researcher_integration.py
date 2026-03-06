#!/usr/bin/env python3
"""
Researcher Integration — discovers and invokes the last30days skill,
parses results into structured research reports.

Importable as a module or runnable as CLI:
    python3 researcher_integration.py --topic "AI agents" --days 30 --json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


SKILL_SEARCH_PATHS = [
    Path.home() / ".claude" / "skills" / "last30days",
    Path.home() / ".agents" / "skills" / "last30days",
    Path.home() / ".openclaw" / "workspace" / "skills" / "last30days",
    Path.home() / ".local" / "share" / "last30days",
]


class ResearcherIntegration:
    """Wraps the last30days skill for structured research."""

    def __init__(self, skill_path: Optional[Path] = None):
        self.skill_path = skill_path or self.discover_skill()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    @staticmethod
    def discover_skill() -> Optional[Path]:
        """Locate the last30days skill on disk."""
        for candidate in SKILL_SEARCH_PATHS:
            if candidate.is_dir():
                for name in ("last30days", "last30days.py", "main.py", "cli.py"):
                    target = candidate / name
                    if target.exists():
                        return candidate
                return candidate
        env = os.environ.get("LAST30DAYS_SKILL_PATH")
        if env:
            p = Path(env)
            if p.exists():
                return p
        return None

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run_research(
        self,
        topic: str,
        sources: Optional[List[str]] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Invoke the last30days skill and return raw output."""
        if not self.skill_path:
            return {
                "ok": False,
                "error": "last30days skill not found. Searched: "
                + ", ".join(str(p) for p in SKILL_SEARCH_PATHS),
            }

        cmd: List[str] = ["python3"]

        entry = self.skill_path / "last30days.py"
        if not entry.exists():
            entry = self.skill_path / "main.py"
        if not entry.exists():
            entry = self.skill_path / "cli.py"
        if not entry.exists():
            return {
                "ok": False,
                "error": f"No entry point found in {self.skill_path}",
            }

        cmd.append(str(entry))
        cmd.extend(["--topic", topic, "--days", str(days)])

        if sources:
            cmd.extend(["--sources", ",".join(sources)])

        cmd.append("--json")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                return {
                    "ok": False,
                    "error": result.stderr.strip() or f"exit code {result.returncode}",
                    "stdout": result.stdout.strip(),
                }
            return self.parse_results(result.stdout)
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Skill timed out after 300s"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def parse_results(raw_output: str) -> Dict[str, Any]:
        """Parse skill output into structured data."""
        try:
            data = json.loads(raw_output)
            data["ok"] = True
            return data
        except json.JSONDecodeError:
            pass

        sections: Dict[str, List[str]] = {}
        current_section = "general"
        sections[current_section] = []

        for line in raw_output.splitlines():
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("# "):
                current_section = stripped.lstrip("# ").strip().lower().replace(" ", "_")
                sections[current_section] = []
            elif stripped:
                sections[current_section].append(stripped)

        return {"ok": True, "raw": raw_output, "sections": sections}

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    @staticmethod
    def format_report(results: Dict[str, Any]) -> str:
        """Create a formatted markdown report from parsed results."""
        if not results.get("ok"):
            return f"# Research Failed\n\n{results.get('error', 'Unknown error')}"

        lines: List[str] = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines.append(f"# Research Report — {now}")
        lines.append("")

        if "sections" in results:
            for section, items in results["sections"].items():
                heading = section.replace("_", " ").title()
                lines.append(f"## {heading}")
                for item in items:
                    if item.startswith("- ") or item.startswith("* "):
                        lines.append(item)
                    else:
                        lines.append(f"- {item}")
                lines.append("")
        elif "raw" in results:
            lines.append(results["raw"])
        else:
            for key, value in results.items():
                if key == "ok":
                    continue
                lines.append(f"## {key.replace('_', ' ').title()}")
                if isinstance(value, list):
                    for item in value:
                        lines.append(f"- {item}")
                elif isinstance(value, dict):
                    lines.append(f"```json\n{json.dumps(value, indent=2)}\n```")
                else:
                    lines.append(str(value))
                lines.append("")

        return "\n".join(lines)


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Researcher Integration — invoke last30days skill"
    )
    parser.add_argument("--topic", required=True, help="Research topic")
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days")
    parser.add_argument(
        "--sources",
        help="Comma-separated sources (reddit,twitter,youtube,web)",
    )
    parser.add_argument("--json", action="store_true", dest="json_out", help="JSON output")
    parser.add_argument(
        "--skill-path", help="Override skill discovery with explicit path"
    )
    args = parser.parse_args()

    skill_path = Path(args.skill_path) if args.skill_path else None
    researcher = ResearcherIntegration(skill_path=skill_path)

    sources = args.sources.split(",") if args.sources else None
    results = researcher.run_research(args.topic, sources=sources, days=args.days)

    if args.json_out:
        json.dump(results, sys.stdout, indent=2)
        print()
    else:
        print(researcher.format_report(results))

    sys.exit(0 if results.get("ok") else 1)


if __name__ == "__main__":
    main()
