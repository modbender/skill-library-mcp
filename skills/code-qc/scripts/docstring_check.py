#!/usr/bin/env python3
"""Check for missing module, class, and function docstrings using AST.

Usage:
    python docstring_check.py <directory> [--exclude dir1,dir2] [--classes] [--functions]
    python docstring_check.py <directory> --skip-init  # Skip __init__.py files

Example:
    python docstring_check.py src/ --classes --functions --exclude tests,migrations
"""
from __future__ import annotations

import argparse
import ast
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


@dataclass
class DocstringResults:
    """Results of a docstring check run."""

    total_modules: int = 0
    missing_module_docstring: list[str] = field(default_factory=list)
    missing_class_docstring: list[str] = field(default_factory=list)
    missing_function_docstring: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_modules": self.total_modules,
            "missing_module_docstring": self.missing_module_docstring,
            "missing_class_docstring": self.missing_class_docstring,
            "missing_function_docstring": self.missing_function_docstring,
            "total_missing": (
                len(self.missing_module_docstring)
                + len(self.missing_class_docstring)
                + len(self.missing_function_docstring)
            ),
        }


def should_check_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Determine if a function should have a docstring.

    Skip private/dunder methods and very short functions.
    """
    name = node.name

    # Skip private methods (single underscore)
    if name.startswith("_") and not name.startswith("__"):
        return False

    # Skip most dunder methods (they're well-known)
    if name.startswith("__") and name.endswith("__"):
        # But check __init__ if it has non-trivial logic
        if name == "__init__":
            # Check if body has more than just assignments
            non_assign_stmts = [
                stmt
                for stmt in node.body
                if not isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.Expr, ast.Pass))
            ]
            return len(non_assign_stmts) > 0
        return False

    # Skip very short functions (1-2 lines, likely trivial)
    if len(node.body) <= 2:
        # Unless they have complex logic
        has_complex = any(
            isinstance(stmt, (ast.If, ast.For, ast.While, ast.Try, ast.With))
            for stmt in node.body
        )
        if not has_complex:
            return False

    return True


def check_docstrings(
    root: str,
    exclude: list[str] | None = None,
    check_classes: bool = False,
    check_functions: bool = False,
    skip_init: bool = False,
) -> DocstringResults:
    """Check for missing docstrings in Python files.

    Args:
        root: Directory to check
        exclude: List of directory names to skip
        check_classes: Also check class docstrings
        check_functions: Also check function docstrings
        skip_init: Skip __init__.py files

    Returns:
        DocstringResults with lists of missing docstrings
    """
    exclude = exclude or []
    results = DocstringResults()

    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)

        # Skip excluded directories
        skip_dirs = exclude + ["__pycache__", ".git", ".venv", "venv", "node_modules"]
        if any(ex in rel.split(os.sep) for ex in skip_dirs):
            continue

        # Filter out excluded dirs from dirnames to prevent descending
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for fname in filenames:
            if not fname.endswith(".py"):
                continue

            # Handle __init__.py based on flag
            if fname == "__init__.py" and skip_init:
                continue

            filepath = os.path.join(dirpath, fname)
            relpath = os.path.relpath(filepath, root)
            results.total_modules += 1

            try:
                with open(filepath, encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {relpath}: {e}")
                continue
            except UnicodeDecodeError as e:
                logger.warning(f"Encoding error in {relpath}: {e}")
                continue

            # Module docstring
            if not ast.get_docstring(tree):
                results.missing_module_docstring.append(relpath)

            # Walk AST for class and function definitions
            for node in ast.walk(tree):
                if check_classes and isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        results.missing_class_docstring.append(
                            f"{relpath}::{node.name}"
                        )

                if check_functions and isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    if should_check_function(node) and not ast.get_docstring(node):
                        results.missing_function_docstring.append(
                            f"{relpath}::{node.name}"
                        )

    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Docstring check for Python modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python docstring_check.py src/
  python docstring_check.py . --classes --functions
  python docstring_check.py . --skip-init --exclude tests,migrations
        """,
    )
    parser.add_argument("directory", help="Root directory to check")
    parser.add_argument(
        "--exclude", default="", help="Comma-separated dirs to exclude"
    )
    parser.add_argument(
        "--classes", action="store_true", help="Also check class docstrings"
    )
    parser.add_argument(
        "--functions", action="store_true", help="Also check function docstrings"
    )
    parser.add_argument(
        "--skip-init",
        action="store_true",
        help="Skip __init__.py files (default: check them)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    exclude = [x.strip() for x in args.exclude.split(",") if x.strip()]
    results = check_docstrings(
        args.directory,
        exclude,
        check_classes=args.classes,
        check_functions=args.functions,
        skip_init=args.skip_init,
    )

    if args.json:
        print(json.dumps(results.to_dict(), indent=2))
    else:
        logger.info(f"Docstring Check: {args.directory}")
        logger.info(f"  Modules checked: {results.total_modules}")
        logger.info(
            f"  Missing module docstring: {len(results.missing_module_docstring)}"
        )

        if results.missing_module_docstring:
            for m in results.missing_module_docstring[:10]:  # Limit output
                logger.info(f"    ⚠️  {m}")
            if len(results.missing_module_docstring) > 10:
                remaining = len(results.missing_module_docstring) - 10
                logger.info(f"    ... and {remaining} more")

        if args.classes:
            logger.info(
                f"  Missing class docstring: {len(results.missing_class_docstring)}"
            )
            for c in results.missing_class_docstring[:10]:
                logger.info(f"    ⚠️  {c}")
            if len(results.missing_class_docstring) > 10:
                remaining = len(results.missing_class_docstring) - 10
                logger.info(f"    ... and {remaining} more")

        if args.functions:
            logger.info(
                f"  Missing function docstring: {len(results.missing_function_docstring)}"
            )
            for f in results.missing_function_docstring[:10]:
                logger.info(f"    ⚠️  {f}")
            if len(results.missing_function_docstring) > 10:
                remaining = len(results.missing_function_docstring) - 10
                logger.info(f"    ... and {remaining} more")

    # Docstring missing is a warning, not an error
    sys.exit(0)


if __name__ == "__main__":
    main()
