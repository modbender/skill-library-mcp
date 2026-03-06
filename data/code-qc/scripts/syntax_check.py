#!/usr/bin/env python3
"""Check all Python files for syntax errors using py_compile.

Usage:
    python syntax_check.py <directory> [--exclude dir1,dir2] [--json]

Example:
    python syntax_check.py src/ --exclude vendor,generated
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import py_compile
import sys
from dataclasses import dataclass, field

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


@dataclass
class SyntaxIssue:
    """Record of a syntax error."""

    file: str
    error: str
    line: int | None = None
    column: int | None = None

    def to_dict(self) -> dict:
        result: dict = {"file": self.file, "error": self.error}
        if self.line is not None:
            result["line"] = self.line
        if self.column is not None:
            result["column"] = self.column
        return result


@dataclass
class SyntaxResults:
    """Results of a syntax check run."""

    total: int = 0
    passed: int = 0
    errors: list[SyntaxIssue] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": len(self.errors),
            "errors": [e.to_dict() for e in self.errors],
        }


def check_syntax(root: str, exclude: list[str] | None = None) -> SyntaxResults:
    """Check all Python files in a directory for syntax errors.

    Args:
        root: Directory to check
        exclude: List of directory names to skip

    Returns:
        SyntaxResults with pass/fail counts and error details
    """
    exclude = exclude or []
    results = SyntaxResults()

    skip_dirs = exclude + ["__pycache__", ".git", ".venv", "venv", "node_modules"]

    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)

        # Skip excluded directories
        if any(ex in rel.split(os.sep) for ex in skip_dirs):
            continue

        # Filter dirnames to prevent descending into excluded dirs
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for fname in filenames:
            if not fname.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, fname)
            results.total += 1

            try:
                py_compile.compile(filepath, doraise=True)
                results.passed += 1
            except py_compile.PyCompileError as e:
                # Extract line/column if available
                line = None
                column = None
                if hasattr(e, "exc_value") and e.exc_value:
                    exc = e.exc_value
                    if hasattr(exc, "lineno"):
                        line = exc.lineno
                    if hasattr(exc, "offset"):
                        column = exc.offset

                results.errors.append(
                    SyntaxIssue(
                        file=os.path.relpath(filepath, root),
                        error=str(e.msg) if hasattr(e, "msg") else str(e),
                        line=line,
                        column=column,
                    )
                )

    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Syntax check for Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python syntax_check.py src/
  python syntax_check.py . --exclude vendor,migrations --json
        """,
    )
    parser.add_argument("directory", help="Root directory to check")
    parser.add_argument(
        "--exclude", default="", help="Comma-separated dirs to exclude"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    exclude = [x.strip() for x in args.exclude.split(",") if x.strip()]
    results = check_syntax(args.directory, exclude)

    if args.json:
        print(json.dumps(results.to_dict(), indent=2))
    else:
        logger.info(f"Syntax Check: {args.directory}")
        logger.info(f"  Total:  {results.total}")
        logger.info(f"  Passed: {results.passed}")
        logger.info(f"  Errors: {len(results.errors)}")

        if results.errors:
            logger.info("\n❌ Syntax Errors:")
            for e in results.errors:
                loc = f":{e.line}" if e.line else ""
                logger.info(f"  {e.file}{loc}: {e.error}")

    sys.exit(1 if results.errors else 0)


if __name__ == "__main__":
    main()
