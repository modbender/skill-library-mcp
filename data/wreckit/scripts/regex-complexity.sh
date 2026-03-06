#!/usr/bin/env bash
# wreckit — Regex complexity analysis (ReDoS risk)
# Separate from red-team because complex regex in validation libs is intentional
# Usage: ./regex-complexity.sh [project-path] [--context library|app]
# Output: JSON with potentially vulnerable patterns

set -euo pipefail

PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
CONTEXT="app"
shift 1 || true

if [ "${1:-}" = "--context" ] && [ -n "${2:-}" ]; then
  CONTEXT="$2"
  shift 2
fi

RECHECK_AVAILABLE=0
if command -v recheck >/dev/null 2>&1; then
  RECHECK_AVAILABLE=1
fi

python3 - "$PROJECT" "$CONTEXT" "$RECHECK_AVAILABLE" <<'PYEOF'
import json
import os
import re
import subprocess
import sys
import time

project = sys.argv[1]
context = sys.argv[2] if len(sys.argv) > 2 else "app"
recheck_available = bool(int(sys.argv[3])) if len(sys.argv) > 3 else False

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".wreckit",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
}

EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".go", ".sh", ".swift",
    ".java", ".rb", ".php", ".mjs", ".cjs"
}

JS_REGEX_RE = re.compile(r"(?<!/)/(?:\\.|[^/\\\n])+/[gimsuy]*")
REGEXP_CTOR_RE = re.compile(r"(?:new\s+)?RegExp\(\s*([\"'])(.*?)(?<!\\)\1", re.IGNORECASE)
PY_REGEX_RE = re.compile(r"re\.(?:compile|match|search)\(\s*r?([\"'])(.*?)(?<!\\)\1", re.IGNORECASE)

META_RE = re.compile(r"[\*\+\?\{\}\(\)\[\]\|\\]")

NESTED_Q_RE = re.compile(r"\([^)]*([+*]|\{\d+,?\d*\})[^)]*\)\s*([+*]|\{\d+,?\d*\})")
ALT_REPEAT_RE = re.compile(r"\([^)]*\|[^)]*\)\s*([+*]|\{\d+,?\d*\})")
DOTSTAR_REPEAT_RE = re.compile(r"\(.*?\.[*].*?\)\s*([+*]|\{\d+,?\d*\})")

patterns = []

def try_recheck(pattern: str):
    if not recheck_available:
        return None
    try:
        proc = subprocess.run(
            ["recheck", "--json", pattern],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
        )
        out = (proc.stdout + "\n" + proc.stderr).lower()
        if "vulnerable" in out or "catastrophic" in out or "exponential" in out or "redos" in out:
            return "definitive"
        if proc.returncode == 0 and ("complex" in out or "backtracking" in out):
            return "complex"
    except Exception:
        return None
    return None


def classify_pattern(pat: str) -> str | None:
    if not META_RE.search(pat):
        return None

    recheck_class = try_recheck(pat)
    if recheck_class:
        return recheck_class

    if NESTED_Q_RE.search(pat) or DOTSTAR_REPEAT_RE.search(pat):
        return "definitive"
    if ALT_REPEAT_RE.search(pat):
        return "complex"
    return None


def extract_from_line(line: str):
    found = []
    if "//" in line:
        stripped = line.lstrip()
        if stripped.startswith("//"):
            return found
    for m in JS_REGEX_RE.finditer(line):
        raw = m.group(0)
        if raw.startswith("//"):
            continue
        if "http://" in raw or "https://" in raw:
            continue
        body = raw
        if body.count("/") >= 2:
            body = body.strip().strip("/")
            body = body.rsplit("/", 1)[0]
        found.append(body)
    for m in REGEXP_CTOR_RE.finditer(line):
        found.append(m.group(2))
    for m in PY_REGEX_RE.finditer(line):
        found.append(m.group(2))
    return found


def add_pattern(file_path: str, line_num: int, pat: str, classification: str):
    patterns.append({
        "file": file_path,
        "line": line_num,
        "pattern": pat[:200],
        "classification": classification,
    })

for root, dirs, files in os.walk(project):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for filename in files:
        _, ext = os.path.splitext(filename)
        if ext.lower() not in EXTS:
            continue
        path = os.path.join(root, filename)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for idx, line in enumerate(f, start=1):
                    for pat in extract_from_line(line):
                        classification = classify_pattern(pat)
                        if classification:
                            add_pattern(path, idx, pat, classification)
        except OSError:
            continue

# Deduplicate identical patterns in same file/line
unique = []
seen = set()
for item in patterns:
    key = (item["file"], item["line"], item["pattern"], item["classification"])
    if key in seen:
        continue
    seen.add(key)
    unique.append(item)
patterns = unique

if context not in {"app", "library"}:
    context = "app"

if context == "library":
    filtered = [p for p in patterns if p["classification"] == "definitive"]
    definitive = len(filtered)
    complex_only = 0
    patterns_out = filtered
else:
    definitive = sum(1 for p in patterns if p["classification"] == "definitive")
    complex_only = sum(1 for p in patterns if p["classification"] == "complex")
    patterns_out = patterns

patterns_found = len(patterns_out)

status = "PASS"
if context == "library":
    if definitive > 0:
        status = "WARN"
else:
    if definitive > 0:
        status = "FAIL"
    elif complex_only > 0:
        status = "WARN"

report = {
    "status": status,
    "patterns_found": patterns_found,
    "definitive_redos": definitive,
    "complex_only": complex_only,
    "context": context,
    "patterns": patterns_out[:50],
}

print(json.dumps(report))

sys.exit(1 if status == "FAIL" else 0)
PYEOF
