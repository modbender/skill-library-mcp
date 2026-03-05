#!/usr/bin/env python3
"""
Reference Search Tool

Searches local skill references for a query string.

Usage:
    python scripts/search.py --query "dopamine"
    python scripts/search.py --query "cognitive load" --ignore-case
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REFERENCE_ROOT = (SKILL_ROOT / "references").resolve()
MAX_QUERY_CHARS = 256
MAX_RESULTS_CAP = 1000
MAX_FILE_BYTES = 2_000_000


@dataclass
class Result:
    """Standard result structure for skill scripts."""
    success: bool
    data: dict
    errors: List[str]
    warnings: List[str]


def normalize_extensions(raw_exts: List[str]) -> Set[str]:
    normalized = set()
    for ext in raw_exts:
        if not ext:
            continue
        normalized.add(ext.lower() if ext.startswith(".") else f".{ext.lower()}")
    return normalized


def resolve_search_root(path_arg: str) -> Path:
    raw = Path((path_arg or ".").strip())
    if raw.is_absolute():
        resolved = raw.resolve()
    else:
        parts = raw.parts
        if parts and parts[0] == "references":
            raw = Path(*parts[1:]) if len(parts) > 1 else Path(".")
        resolved = (REFERENCE_ROOT / raw).resolve()
    try:
        resolved.relative_to(REFERENCE_ROOT)
    except ValueError as exc:
        raise ValueError("Search path must stay inside the references directory.") from exc
    if not resolved.is_dir():
        raise ValueError(f"Path not found or not a directory: {path_arg}")
    return resolved


def iter_files(root: Path, exts: Set[str]) -> List[Path]:
    matches: List[Path] = []
    for dirpath, _, filenames in os.walk(root):
        parent = Path(dirpath)
        for name in filenames:
            candidate = parent / name
            if candidate.is_symlink():
                continue
            if exts and candidate.suffix.lower() not in exts:
                continue
            try:
                if candidate.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            resolved = candidate.resolve()
            try:
                resolved.relative_to(REFERENCE_ROOT)
            except ValueError:
                continue
            matches.append(resolved)
    return matches


def search_files(paths: List[Path], query: str, ignore_case: bool, max_results: int) -> List[Dict[str, str]]:
    results = []
    needle = query.casefold() if ignore_case else query
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                for idx, line in enumerate(handle, start=1):
                    haystack = line.casefold() if ignore_case else line
                    if needle in haystack:
                        results.append({
                            "path": str(path.relative_to(SKILL_ROOT)),
                            "line": idx,
                            "text": line.rstrip("\n")
                        })
                        if max_results and len(results) >= max_results:
                            return results
        except OSError:
            continue
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Search skill references for a query.")
    parser.add_argument("--query", required=True, help="Query string.")
    parser.add_argument("--path", default="references", help="Root path to search.")
    parser.add_argument("--regex", action="store_true", help="Disabled for security reasons.")
    parser.add_argument("--ignore-case", action="store_true", help="Case-insensitive search.")
    parser.add_argument("--ext", action="append", default=[".md"], help="File extension filter.")
    parser.add_argument("--max-results", type=int, default=200, help="Maximum number of matches.")
    parser.add_argument("--json", action="store_true", help="Return machine-readable JSON output.")
    args = parser.parse_args()

    errors = []
    warnings = []

    if not args.query.strip():
        errors.append("Query is empty.")
        result = Result(success=False, data={}, errors=errors, warnings=warnings)
        print(json.dumps(asdict(result), indent=2))
        return 1

    if len(args.query) > MAX_QUERY_CHARS:
        errors.append(f"Query exceeds {MAX_QUERY_CHARS} characters.")
        result = Result(success=False, data={}, errors=errors, warnings=warnings)
        print(json.dumps(asdict(result), indent=2))
        return 1

    if args.max_results < 1 or args.max_results > MAX_RESULTS_CAP:
        errors.append(f"--max-results must be between 1 and {MAX_RESULTS_CAP}.")
        result = Result(success=False, data={}, errors=errors, warnings=warnings)
        print(json.dumps(asdict(result), indent=2))
        return 1

    if args.regex:
        errors.append("Regex mode is disabled for security reasons. Use literal queries only.")
        result = Result(success=False, data={}, errors=errors, warnings=warnings)
        print(json.dumps(asdict(result), indent=2))
        return 1

    try:
        root = resolve_search_root(args.path)
    except ValueError as exc:
        errors.append(str(exc))
        result = Result(success=False, data={}, errors=errors, warnings=warnings)
        print(json.dumps(asdict(result), indent=2))
        return 1

    exts = normalize_extensions(args.ext)
    paths = iter_files(root, exts)
    matches = search_files(paths, args.query, args.ignore_case, args.max_results)

    if not matches:
        warnings.append("No matches found.")

    data = {
        "query": args.query,
        "path": str(root.relative_to(SKILL_ROOT)),
        "regex": False,
        "ignore_case": args.ignore_case,
        "matches": matches,
    }
    result = Result(success=True, data=data, errors=errors, warnings=warnings)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        for match in matches:
            print(f"{match['path']}:{match['line']}:{match['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
