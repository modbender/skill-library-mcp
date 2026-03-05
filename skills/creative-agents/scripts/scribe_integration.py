#!/usr/bin/env python3
"""
Scribe Integration — orchestrates the full scribe pipeline:
log analysis → pattern detection → memory curation → MEMORY.md update.

Wraps the existing scribe skill and extends it with memory commit
functionality via LogAnalyzer and MemoryCurator.

Importable as a module or runnable as CLI:
    python3 scribe_integration.py --mode daily --commit-memory --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from log_analyzer import LogAnalyzer
from memory_curator import MemoryCurator


SCRIBE_SKILL_PATH = Path("/Users/ghost/.openclaw/workspace/skills/scribe/scripts/scribe.py")
OPENCLAW_HOME = Path("/Users/ghost/.openclaw")


class ScribeIntegration:
    """Orchestrates the scribe pipeline with memory commits."""

    def __init__(
        self,
        scribe_path: Optional[Path] = None,
        openclaw_home: Optional[Path] = None,
    ):
        self.scribe_path = scribe_path or SCRIBE_SKILL_PATH
        self.openclaw_home = openclaw_home or OPENCLAW_HOME
        self.log_analyzer = LogAnalyzer()
        self.memory_curator = MemoryCurator()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def get_log_sources(self) -> Dict[str, str]:
        """Return configured log source paths."""
        return {
            "cursor": str(self.log_analyzer.cursor_log_dir),
            "nanobot": str(self.log_analyzer.nanobot_log_dir),
            "claude": str(self.log_analyzer.claude_transcript_dir),
            "shell": str(self.log_analyzer.shell_history or "not found"),
        }

    # ------------------------------------------------------------------
    # Scribe invocation
    # ------------------------------------------------------------------

    def _run_scribe(self, mode: str) -> Dict[str, Any]:
        """Invoke the existing scribe skill."""
        if not self.scribe_path.exists():
            return {
                "ok": False,
                "error": f"Scribe skill not found at {self.scribe_path}",
            }

        cmd = [
            "python3", str(self.scribe_path),
            "--mode", mode,
            "--openclaw-home", str(self.openclaw_home),
            "--json",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                return {
                    "ok": False,
                    "error": result.stderr.strip() or f"exit code {result.returncode}",
                }
            try:
                return {**json.loads(result.stdout), "ok": True}
            except json.JSONDecodeError:
                return {"ok": True, "output": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Scribe timed out (120s)"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Pipeline modes
    # ------------------------------------------------------------------

    def run_daily(self, commit_memory: bool = False) -> Dict[str, Any]:
        """Run daily scribe + optional memory curation."""
        scribe_result = self._run_scribe("daily")
        log_result = self.log_analyzer.analyze_all(hours=24)

        result: Dict[str, Any] = {
            "ok": True,
            "mode": "daily",
            "timestamp": datetime.now().isoformat(),
            "scribe": scribe_result,
            "log_analysis": {
                "total_entries": log_result.get("total_entries", 0),
                "error_count": log_result.get("metrics", {}).get("error_count", 0),
                "warning_count": log_result.get("metrics", {}).get("warning_count", 0),
                "patterns": log_result.get("patterns", []),
                "suggestions": log_result.get("suggestions", []),
            },
        }

        if commit_memory:
            curation_result = self.memory_curator.curate(days=1)
            result["memory_curation"] = curation_result

        return result

    def run_weekly(self, commit_memory: bool = True) -> Dict[str, Any]:
        """Run weekly scribe + memory curation."""
        scribe_result = self._run_scribe("weekly")
        log_result = self.log_analyzer.analyze_all(hours=168)

        result: Dict[str, Any] = {
            "ok": True,
            "mode": "weekly",
            "timestamp": datetime.now().isoformat(),
            "scribe": scribe_result,
            "log_analysis": {
                "total_entries": log_result.get("total_entries", 0),
                "error_count": log_result.get("metrics", {}).get("error_count", 0),
                "warning_count": log_result.get("metrics", {}).get("warning_count", 0),
                "patterns": log_result.get("patterns", []),
                "suggestions": log_result.get("suggestions", []),
            },
        }

        if commit_memory:
            curation_result = self.memory_curator.curate(days=7)
            result["memory_curation"] = curation_result

        return result

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Full pipeline: log analysis → pattern detection → memory curation → update."""
        now = datetime.now()
        log_result = self.log_analyzer.analyze_all(hours=24)
        report = self.log_analyzer.generate_daily_report(hours=24)
        scribe_result = self._run_scribe("daily")
        curation_result = self.memory_curator.curate(days=7)
        summary = self.memory_curator.generate_summary()

        return {
            "ok": True,
            "mode": "full_pipeline",
            "timestamp": now.isoformat(),
            "steps": {
                "log_analysis": {
                    "total_entries": log_result.get("total_entries", 0),
                    "error_count": log_result.get("metrics", {}).get("error_count", 0),
                    "warning_count": log_result.get("metrics", {}).get("warning_count", 0),
                    "patterns": log_result.get("patterns", []),
                },
                "scribe": scribe_result,
                "memory_curation": curation_result,
                "memory_summary": summary,
            },
            "report": report,
        }

    # ------------------------------------------------------------------
    # Cron scheduling
    # ------------------------------------------------------------------

    @staticmethod
    def schedule_cron(mode: str = "daily", time: str = "00:00") -> Dict[str, Any]:
        """Generate a cron entry for scheduling.

        Does not install automatically — returns the entry for the user
        to add to their crontab.
        """
        hour, minute = time.split(":")
        script = str(SCRIBE_SKILL_PATH.parent.parent / "creative-agents" / "scripts" / "scribe_integration.py")

        if mode == "daily":
            cron_expr = f"{minute} {hour} * * *"
        elif mode == "weekly":
            cron_expr = f"{minute} {hour} * * 0"
        else:
            return {"ok": False, "error": f"Unknown mode: {mode}"}

        entry = f"{cron_expr} /usr/bin/env python3 {script} --mode {mode} --commit-memory --json >> ~/.openclaw/logs/scribe-cron.log 2>&1"

        return {
            "ok": True,
            "cron_entry": entry,
            "instruction": f"Add this line to your crontab (crontab -e): {entry}",
        }


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scribe Integration — full scribe pipeline with memory commits"
    )
    parser.add_argument(
        "--mode",
        choices=["daily", "weekly", "full"],
        default="daily",
        help="Pipeline mode",
    )
    parser.add_argument(
        "--commit-memory",
        action="store_true",
        help="Commit insights to MEMORY.md",
    )
    parser.add_argument("--json", action="store_true", dest="json_out")
    parser.add_argument("--schedule", help="Generate cron entry (e.g. --schedule 00:00)")
    parser.add_argument("--openclaw-home", help="Override OpenClaw home directory")
    parser.add_argument("--scribe-path", help="Override scribe.py path")
    args = parser.parse_args()

    if args.schedule:
        result = ScribeIntegration.schedule_cron(args.mode, args.schedule)
        if args.json_out:
            json.dump(result, sys.stdout, indent=2)
            print()
        else:
            print(result.get("cron_entry") or result.get("error"))
        sys.exit(0 if result.get("ok") else 1)

    scribe_path = Path(args.scribe_path) if args.scribe_path else None
    openclaw_home = Path(args.openclaw_home) if args.openclaw_home else None
    integration = ScribeIntegration(
        scribe_path=scribe_path, openclaw_home=openclaw_home
    )

    if args.mode == "daily":
        result = integration.run_daily(commit_memory=args.commit_memory)
    elif args.mode == "weekly":
        result = integration.run_weekly(commit_memory=args.commit_memory)
    elif args.mode == "full":
        result = integration.run_full_pipeline()
    else:
        result = {"ok": False, "error": f"Unknown mode: {args.mode}"}

    if args.json_out:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        print(f"Mode: {result.get('mode')}")
        print(f"Timestamp: {result.get('timestamp')}")
        scribe = result.get("scribe", {})
        if scribe.get("daily_note"):
            print(f"Daily note: {scribe['daily_note']}")
        if scribe.get("weekly_note"):
            print(f"Weekly note: {scribe['weekly_note']}")
        la = result.get("log_analysis", {})
        print(f"Log entries: {la.get('total_entries', 0)}, Errors: {la.get('error_count', 0)}")
        mc = result.get("memory_curation", {})
        if mc:
            print(f"Memory commits: {mc.get('committed', 0)}")

    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
