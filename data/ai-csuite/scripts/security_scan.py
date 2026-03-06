from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

PATTERNS = {
    "eval_call": r"\beval\s*\(",
    "exec_call": r"\bexec\s*\(",
    "os_system": r"os\.system\s*\(",
    "pickle_loads": r"pickle\.loads\s*\(",
    "marshal_loads": r"marshal\.loads\s*\(",
    "base64_decode": r"base64\.b64decode\s*\(",
    "dynamic_import": r"__import__\s*\(",
    "shell_true": r"shell\s*=\s*True",
}

TEXT_EXT = {".md", ".py", ".yaml", ".yml", ".json", ".txt"}


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXT:
            files.append(path)
    return files


def scan_patterns(path: Path, text: str) -> list[str]:
    issues: list[str] = []
    for name, pattern in PATTERNS.items():
        if re.search(pattern, text):
            issues.append(f"{path}: suspicious pattern: {name}")
    return issues


def import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imp in node.names:
                roots.add(imp.name.split(".")[0])
        if isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def scan_imports(path: Path, stdlib: set[str]) -> list[str]:
    issues: list[str] = []
    if path.suffix.lower() != ".py":
        return issues
    roots = import_roots(path)
    allowed = stdlib | {"__future__", "common"}
    bad = sorted(module for module in roots if module not in allowed)
    for module in bad:
        issues.append(f"{path}: non-stdlib import: {module}")
    return issues


def scan_file(path: Path, stdlib: set[str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{path}: non-utf8 text file"]
    issues = scan_patterns(path, text)
    issues.extend(scan_imports(path, stdlib))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.target).resolve()
    stdlib = set(getattr(sys, "stdlib_module_names", set()))
    all_issues: list[str] = []
    for file_path in iter_files(root):
        all_issues.extend(scan_file(file_path, stdlib))
    if all_issues:
        print("FAIL")
        for issue in all_issues:
            print(f"- {issue}")
        return 11
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
