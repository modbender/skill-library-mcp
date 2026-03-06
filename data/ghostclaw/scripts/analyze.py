#!/usr/bin/env python3
"""
Ghostclaw Core Analyzer — computes "vibe health" of a codebase.

Features:
- Stack detection
- File size distribution analysis
- Basic architectural smell detection
- JSON report output
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List

def count_lines(filepath: str) -> int:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def find_files(root: str, exts: List[str]) -> List[str]:
    files = []
    for ext in exts:
        files.extend(Path(root).rglob(f"*{ext}"))
    return [str(f) for f in files]

def analyze_node(root: str) -> Dict:
    ts_ex = ['.ts', '.tsx', '.js', '.jsx']
    files = find_files(root, ts_ex)
    total_lines = sum(count_lines(f) for f in files)

    # Metrics
    large_files = [f for f in files if count_lines(f) > 400]
    avg_lines = total_lines / len(files) if files else 0

    score = 100
    blem = []
    ghosts = []
    flags = []

    if len(large_files) > 0:
        penalty = min(30, len(large_files) * 5)
        score -= penalty
        blem.append(f"{len(large_files)} files >400 lines (ModuleGhosts)")
        ghosts.append("ModuleGhosts: large files indicate low cohesion")

    if avg_lines > 200 and len(files) > 0:
        score -= 10
        blem.append(f"Average file size {avg:.0f} lines — consider splitting")

    # Detect potential circular structure via imports count (future AST)
    # For now, just surface heuristics

    if score < 60:
        ghosts.append("Architectural mismatch: services may be too heavy or controllers too thick")

    return {
        "stack": "node",
        "files_analyzed": len(files),
        "total_lines": total_lines,
        "vibe_score": max(0, score),
        "issues": blem,
        "architectural_ghosts": ghosts,
        "red_flags": flags
    }

def analyze_python(root: str) -> Dict:
    py_files = find_files(root, ['.py'])
    total_lines = sum(count_lines(f) for f in py_files)

    large_files = [f for f in py_files if count_lines(f) > 300]
    avg_lines = total_lines / len(py_files) if py_files else 0

    score = 100
    blem = []
    ghosts = []
    flags = []

    if len(large_files) > 0:
        penalty = min(25, len(large_files) * 4)
        score -= penalty
        blem.append(f"{len(large_files)} Python files >300 lines (ModuleGhosts)")
        ghosts.append("ModuleGhosts: consider extracting smaller modules")

    if avg_lines > 180 and len(py_files) > 0:
        score -= 10
        blem.append(f"Average file size {avg:.0f} lines — thick modules")

    if score < 60:
        ghosts.append("Possible God models or services doing too much")

    return {
        "stack": "python",
        "files_analyzed": len(py_files),
        "total_lines": total_lines,
        "vibe_score": max(0, score),
        "issues": blem,
        "architectural_ghosts": ghosts,
        "red_flags": flags
    }

def detect_stack(root: str) -> str:
    root_path = Path(root)
    if any((root_path / f).exists() for f in ['package.json', 'tsconfig.json', 'vite.config.ts', 'next.config.js']):
        return 'node'
    if any((root_path / f).exists() for f in ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile']):
        return 'python'
    if any((root_path / f).exists() for f in ['go.mod']):
        return 'go'
    return 'unknown'

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: ghostclaw-analyze.py <repo_root>"}))
        sys.exit(1)

    root = sys.argv[1]
    stack = detect_stack(root)

    if stack == 'node':
        report = analyze_node(root)
    elif stack == 'python':
        report = analyze_python(root)
    elif stack == 'go':
        report = {"stack": "go", "vibe_score": 100, "issues": [], "notes": ["Go detection not yet implemented"]}
    else:
        report = {"stack": "unknown", "vibe_score": 50, "issues": ["Cannot detect tech stack; no build files found"]}

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
