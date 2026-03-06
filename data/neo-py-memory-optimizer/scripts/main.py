#!/usr/bin/env python3
"""
Main CLI entry point for py-memory-optimizer.

Usage:
    python main.py analyze PATH [OPTIONS]

Analyzes Python code for memory optimization opportunities and generates a report.

Arguments:
    PATH    Path to a Python file or directory to analyze.

Options:
    --recursive           Recursively analyze directories.
    --format FORMAT       Output format: text, json, markdown (default: text).
    --output FILE         Write report to FILE instead of stdout.
    --show-suggestions    Include detailed optimization suggestions.
    --estimate-savings    Include estimated memory savings.
    --exclude PATTERN     Exclude files matching glob pattern (repeatable).
    --version             Show version and exit.

Examples:
    python main.py analyze script.py
    python main.py analyze ./src --recursive --format json --output report.json
    python main.py analyze . --show-suggestions --estimate-savings
"""

import argparse
import fnmatch
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Ensure imports from the same directory work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyzer
import optimizer

VERSION = "1.0.0"


def collect_python_files(
    path: str, recursive: bool, exclude_patterns: List[str]
) -> List[Path]:
    """Collect Python files from the given path, applying exclude patterns."""
    p = Path(path)
    if p.is_file():
        return [p] if p.suffix == ".py" else []

    if not p.is_dir():
        return []

    files = list(p.rglob("*.py")) if recursive else list(p.glob("*.py"))

    if exclude_patterns:
        filtered = []
        for f in files:
            try:
                rel = str(f.relative_to(p))
            except ValueError:
                rel = f.name
            if not any(fnmatch.fnmatch(rel, pat) for pat in exclude_patterns):
                filtered.append(f)
        files = filtered

    return sorted(files)


def analyze_file(filepath: Path) -> List[Dict[str, Any]]:
    """Analyze a single Python file and return enriched issues."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    raw_issues = analyzer.analyze_source(source, str(filepath))
    issues = []
    for raw in raw_issues:
        suggestion = optimizer.generate_suggestion(raw)
        full_issue = {**raw, **suggestion}
        issues.append(full_issue)
    return issues


def generate_report(
    issues: List[Dict[str, Any]],
    fmt: str,
    show_suggestions: bool,
    estimate_savings: bool,
    files_analyzed: int,
) -> str:
    """Generate a report in the requested format."""
    if fmt == "json":
        output = {
            "files_analyzed": files_analyzed,
            "total_issues": len(issues),
            "issues": [
                {k: v for k, v in iss.items() if k != "code_snippet"} for iss in issues
            ],
        }
        return json.dumps(output, indent=2)

    if fmt == "markdown":
        return _report_markdown(issues, show_suggestions, estimate_savings, files_analyzed)

    return _report_text(issues, show_suggestions, estimate_savings, files_analyzed)


def _report_markdown(
    issues: List[Dict[str, Any]],
    show_suggestions: bool,
    estimate_savings: bool,
    files_analyzed: int,
) -> str:
    lines = [
        "# Memory Analysis Report",
        "",
        f"**Files analyzed:** {files_analyzed}",
        f"**Total issues:** {len(issues)}",
        "",
    ]
    if not issues:
        lines.append("_No issues found._")
        return "\n".join(lines)

    lines.append("## Issues")
    lines.append("")
    by_file: Dict[str, list] = defaultdict(list)
    for iss in issues:
        by_file[iss["file"]].append(iss)

    for file in sorted(by_file.keys()):
        file_issues = sorted(by_file[file], key=lambda x: x["line"])
        lines.append(f"### {file}")
        lines.append("")
        for iss in file_issues:
            sev = iss.get("severity", "?").upper()
            lines.append(f"- **Line {iss['line']}** ({sev}): {iss['type']}")
            lines.append(f"  {iss['message']}")
            if show_suggestions and "suggestion" in iss:
                lines.append(f"  - **Suggestion:** {iss['suggestion']}")
                if "example" in iss:
                    lines.append(f"    ```python")
                    for el in iss["example"].split("\n"):
                        lines.append(f"    {el}")
                    lines.append(f"    ```")
                if estimate_savings and "estimated_savings" in iss:
                    lines.append(f"    - Estimated savings: {iss['estimated_savings']}")
            lines.append("")
    return "\n".join(lines)


def _report_text(
    issues: List[Dict[str, Any]],
    show_suggestions: bool,
    estimate_savings: bool,
    files_analyzed: int,
) -> str:
    lines = [
        "Memory Analysis Report",
        "======================",
        f"Files analyzed: {files_analyzed}",
        f"Total issues: {len(issues)}",
        "",
    ]
    if not issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    # Summary by severity
    severity_counts: Dict[str, int] = {}
    for iss in issues:
        sev = iss.get("severity", "unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    severity_order = ["high", "medium", "low"]
    lines.append("Summary:")
    for sev in severity_order:
        if sev in severity_counts:
            lines.append(f"  {sev.upper()}: {severity_counts[sev]}")
    lines.append("")

    lines.append("Details:")
    sorted_issues = sorted(issues, key=lambda x: (x["file"], x["line"]))
    for iss in sorted_issues:
        sev = iss.get("severity", "?").upper()
        lines.append(f"  {iss['file']}:{iss['line']} [{sev}] {iss['type']}")
        lines.append(f"    {iss['message']}")
        if show_suggestions and "suggestion" in iss:
            lines.append(f"    Suggestion: {iss['suggestion']}")
            if "example" in iss:
                lines.append(f"      Example: {iss['example']}")
            if estimate_savings and "estimated_savings" in iss:
                lines.append(f"      Estimated savings: {iss['estimated_savings']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="py-memory-optimizer",
        description="Analyze Python code for memory optimization opportunities.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze Python files for memory issues."
    )
    analyze_parser.add_argument(
        "path", type=str, help="Path to a Python file or directory."
    )
    analyze_parser.add_argument(
        "--recursive", action="store_true", help="Recursively analyze directories."
    )
    analyze_parser.add_argument(
        "--format",
        dest="output_format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text).",
    )
    analyze_parser.add_argument(
        "--output", type=str, default=None, help="Write report to file."
    )
    analyze_parser.add_argument(
        "--show-suggestions",
        action="store_true",
        help="Include optimization suggestions.",
    )
    analyze_parser.add_argument(
        "--estimate-savings",
        action="store_true",
        help="Include estimated memory savings.",
    )
    analyze_parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude files matching glob pattern (repeatable).",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        path = args.path
        if not os.path.exists(path):
            print(f"Error: path '{path}' does not exist.", file=sys.stderr)
            sys.exit(1)

        files = collect_python_files(path, args.recursive, args.exclude)
        if not files:
            print("No Python files found to analyze.", file=sys.stderr)
            sys.exit(1)

        all_issues: List[Dict[str, Any]] = []
        error_count = 0
        for filepath in files:
            try:
                issues = analyze_file(filepath)
                all_issues.extend(issues)
            except SyntaxError as e:
                print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
                error_count += 1
            except Exception as e:
                print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
                error_count += 1

        report = generate_report(
            all_issues,
            args.output_format,
            args.show_suggestions,
            args.estimate_savings,
            len(files) - error_count,
        )

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Report written to {args.output}")
        else:
            print(report)

        # Exit non-zero if there were errors reading files
        if error_count > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
