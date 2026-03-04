#!/usr/bin/env python3
"""
Log Analyzer — multi-source log scanning for Cursor, nanobot/OpenClaw,
Claude transcripts, and shell history.

Importable as a module or runnable as CLI:
    python3 log_analyzer.py --hours 24 --sources cursor,nanobot,claude --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


TIMESTAMP_PATTERNS = [
    re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"),
    re.compile(r"\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})"),
    re.compile(r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"),
]

ERROR_PATTERNS = re.compile(
    r"(error|exception|traceback|fatal|panic|ENOENT|EACCES|EPERM|segfault)",
    re.IGNORECASE,
)
WARNING_PATTERNS = re.compile(
    r"(warn(?:ing)?|deprecated|notice)",
    re.IGNORECASE,
)


def _parse_timestamp(line: str) -> Optional[datetime]:
    for pat in TIMESTAMP_PATTERNS:
        m = pat.search(line)
        if m:
            raw = m.group(1)
            for fmt in (
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%d/%b/%Y:%H:%M:%S",
                "%b %d %H:%M:%S",
            ):
                try:
                    dt = datetime.strptime(raw, fmt)
                    if dt.year == 1900:
                        dt = dt.replace(year=datetime.now().year)
                    return dt
                except ValueError:
                    continue
    return None


class LogEntry:
    __slots__ = ("source", "file", "line", "timestamp", "severity")

    def __init__(
        self,
        source: str,
        file: str,
        line: str,
        timestamp: Optional[datetime],
        severity: str,
    ):
        self.source = source
        self.file = file
        self.line = line
        self.timestamp = timestamp
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "file": self.file,
            "line": self.line[:500],
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "severity": self.severity,
        }


class LogAnalyzer:
    """Multi-source log scanner and analyzer."""

    def __init__(self):
        self.cursor_log_dir = Path.home() / ".cursor" / "logs"
        self.nanobot_log_dir = Path.home() / ".openclaw" / "logs"
        self.claude_transcript_dir = Path.home() / ".claude" / "transcripts"
        self.shell_history = self._find_shell_history()

    @staticmethod
    def _find_shell_history() -> Optional[Path]:
        for name in (".zsh_history", ".bash_history", ".history"):
            p = Path.home() / name
            if p.exists():
                return p
        histfile = os.environ.get("HISTFILE")
        if histfile:
            p = Path(histfile)
            if p.exists():
                return p
        return None

    # ------------------------------------------------------------------
    # Source scanners
    # ------------------------------------------------------------------

    def scan_cursor_logs(self, hours: int = 24) -> List[LogEntry]:
        return self._scan_directory(self.cursor_log_dir, "cursor", hours)

    def scan_nanobot_logs(self, hours: int = 24) -> List[LogEntry]:
        return self._scan_directory(self.nanobot_log_dir, "nanobot", hours)

    def scan_claude_logs(self, hours: int = 24) -> List[LogEntry]:
        return self._scan_directory(self.claude_transcript_dir, "claude", hours)

    def scan_console_history(self, hours: int = 24) -> List[LogEntry]:
        if not self.shell_history:
            return []
        cutoff = datetime.now() - timedelta(hours=hours)
        entries: List[LogEntry] = []
        try:
            with open(self.shell_history, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    ts = _parse_timestamp(stripped)
                    severity = "info"
                    if ERROR_PATTERNS.search(stripped):
                        severity = "error"
                    elif WARNING_PATTERNS.search(stripped):
                        severity = "warning"
                    if severity != "info":
                        entries.append(
                            LogEntry("shell", str(self.shell_history), stripped, ts, severity)
                        )
        except Exception as exc:
            print(f"Shell history scan failed: {exc}", file=sys.stderr)
        return entries

    def analyze_all(self, hours: int = 24) -> Dict[str, Any]:
        """Scan all sources and return structured analysis."""
        all_entries: List[LogEntry] = []
        all_entries.extend(self.scan_cursor_logs(hours))
        all_entries.extend(self.scan_nanobot_logs(hours))
        all_entries.extend(self.scan_claude_logs(hours))
        all_entries.extend(self.scan_console_history(hours))

        errors = [e for e in all_entries if e.severity == "error"]
        warnings = [e for e in all_entries if e.severity == "warning"]

        return {
            "ok": True,
            "hours": hours,
            "total_entries": len(all_entries),
            "errors": [e.to_dict() for e in errors],
            "warnings": [e.to_dict() for e in warnings],
            "patterns": self.detect_patterns(all_entries),
            "metrics": {
                "error_count": len(errors),
                "warning_count": len(warnings),
                "by_source": self._count_by_source(all_entries),
            },
            "suggestions": self._generate_suggestions(errors, warnings),
        }

    # ------------------------------------------------------------------
    # Pattern detection
    # ------------------------------------------------------------------

    @staticmethod
    def detect_patterns(entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """Find recurring patterns in log entries."""
        error_messages: List[str] = []
        for e in entries:
            if e.severity == "error":
                normalized = re.sub(r"\d+", "N", e.line[:200])
                normalized = re.sub(r"0x[0-9a-fA-F]+", "0xN", normalized)
                error_messages.append(normalized)

        counter = Counter(error_messages)
        patterns: List[Dict[str, Any]] = []
        for msg, count in counter.most_common(10):
            if count >= 2:
                patterns.append({"message": msg, "count": count, "severity": "error"})
        return patterns

    @staticmethod
    def extract_errors(entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """Extract deduplicated error summaries."""
        seen: set = set()
        unique: List[Dict[str, Any]] = []
        for e in entries:
            if e.severity != "error":
                continue
            key = e.line[:120]
            if key in seen:
                continue
            seen.add(key)
            unique.append(e.to_dict())
        return unique

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_daily_report(self, hours: int = 24) -> str:
        """Create a human-readable daily analysis report."""
        analysis = self.analyze_all(hours)
        lines = [
            f"# Log Analysis Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Period: last {hours} hours",
            "",
            "## Metrics",
            f"- Total entries scanned: {analysis['total_entries']}",
            f"- Errors: {analysis['metrics']['error_count']}",
            f"- Warnings: {analysis['metrics']['warning_count']}",
            "",
            "### By Source",
        ]
        for src, count in analysis["metrics"]["by_source"].items():
            lines.append(f"- **{src}**: {count}")
        lines.append("")

        if analysis["patterns"]:
            lines.append("## Recurring Patterns")
            for p in analysis["patterns"]:
                lines.append(f"- ({p['count']}x) {p['message'][:150]}")
            lines.append("")

        if analysis["errors"][:5]:
            lines.append("## Recent Errors (top 5)")
            for err in analysis["errors"][:5]:
                lines.append(f"- [{err['source']}] {err['line'][:200]}")
            lines.append("")

        if analysis["suggestions"]:
            lines.append("## Suggestions")
            for s in analysis["suggestions"]:
                lines.append(f"- {s}")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _scan_directory(
        self, directory: Path, source: str, hours: int
    ) -> List[LogEntry]:
        entries: List[LogEntry] = []
        if not directory.exists():
            return entries

        cutoff = datetime.now() - timedelta(hours=hours)

        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in (".log", ".txt", ".jsonl", ".json", ""):
                continue
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff:
                    continue
            except OSError:
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        stripped = line.strip()
                        if not stripped:
                            continue
                        ts = _parse_timestamp(stripped)
                        severity = "info"
                        if ERROR_PATTERNS.search(stripped):
                            severity = "error"
                        elif WARNING_PATTERNS.search(stripped):
                            severity = "warning"
                        if severity != "info":
                            entries.append(
                                LogEntry(source, str(path), stripped, ts, severity)
                            )
            except Exception as exc:
                print(f"Failed to read {path}: {exc}", file=sys.stderr)

        return entries

    @staticmethod
    def _count_by_source(entries: List[LogEntry]) -> Dict[str, int]:
        counter: Dict[str, int] = {}
        for e in entries:
            counter[e.source] = counter.get(e.source, 0) + 1
        return counter

    @staticmethod
    def _generate_suggestions(
        errors: List[LogEntry], warnings: List[LogEntry]
    ) -> List[str]:
        suggestions: List[str] = []
        if len(errors) > 20:
            suggestions.append(
                "High error volume — consider checking gateway connectivity and auth tokens."
            )
        error_sources = {e.source for e in errors}
        if "cursor" in error_sources:
            suggestions.append(
                "Cursor log errors detected — check extension health and restart if needed."
            )
        if "nanobot" in error_sources:
            suggestions.append(
                "OpenClaw/nanobot errors — verify gateway is running and tokens match."
            )
        if not suggestions:
            suggestions.append("No critical issues detected.")
        return suggestions


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Log Analyzer — multi-source log scanning"
    )
    parser.add_argument("--hours", type=int, default=24, help="Lookback window in hours")
    parser.add_argument(
        "--sources",
        default="cursor,nanobot,claude,shell",
        help="Comma-separated sources to scan",
    )
    parser.add_argument("--json", action="store_true", dest="json_out")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    args = parser.parse_args()

    analyzer = LogAnalyzer()

    if args.report:
        print(analyzer.generate_daily_report(args.hours))
        return

    sources = [s.strip() for s in args.sources.split(",")]
    all_entries: List[LogEntry] = []

    if "cursor" in sources:
        all_entries.extend(analyzer.scan_cursor_logs(args.hours))
    if "nanobot" in sources:
        all_entries.extend(analyzer.scan_nanobot_logs(args.hours))
    if "claude" in sources:
        all_entries.extend(analyzer.scan_claude_logs(args.hours))
    if "shell" in sources:
        all_entries.extend(analyzer.scan_console_history(args.hours))

    errors = [e for e in all_entries if e.severity == "error"]
    warnings = [e for e in all_entries if e.severity == "warning"]

    result = {
        "ok": True,
        "hours": args.hours,
        "sources": sources,
        "total_entries": len(all_entries),
        "errors": [e.to_dict() for e in errors],
        "warnings": [e.to_dict() for e in warnings],
        "patterns": analyzer.detect_patterns(all_entries),
        "metrics": {
            "error_count": len(errors),
            "warning_count": len(warnings),
            "by_source": analyzer._count_by_source(all_entries),
        },
        "suggestions": analyzer._generate_suggestions(errors, warnings),
    }

    if args.json_out:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        print(f"Scanned {len(all_entries)} entries from {', '.join(sources)}")
        print(f"Errors: {len(errors)}, Warnings: {len(warnings)}")
        for p in result["patterns"]:
            print(f"  Pattern ({p['count']}x): {p['message'][:100]}")
        for s in result["suggestions"]:
            print(f"  Suggestion: {s}")

    sys.exit(0)


if __name__ == "__main__":
    main()
