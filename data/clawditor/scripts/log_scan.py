#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

PATTERNS = [
    (re.compile(r"\bERROR\b", re.IGNORECASE), "error"),
    (re.compile(r"\bException\b", re.IGNORECASE), "exception"),
    (re.compile(r"\bTraceback\b", re.IGNORECASE), "traceback"),
    (re.compile(r"\bfailed\b", re.IGNORECASE), "failed"),
    (re.compile(r"\btimeout\b", re.IGNORECASE), "timeout"),
    (re.compile(r"\bretry\b", re.IGNORECASE), "retry"),
]

DEFAULT_EXTS = {".log", ".txt", ".out", ".err", ".stderr", ".stdout"}
DEFAULT_DIRS = ["logs", "log", ".logs", "tmp", ".codex", ".cache", ".next/dev/logs"]
EXCLUDE_DIRS = {".git", "node_modules", ".next", "dist", "build"}


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def iter_files(paths):
    for p in paths:
        if p.is_file():
            if should_skip(p.parent):
                continue
            yield p
        elif p.is_dir():
            if should_skip(p):
                continue
            for f in p.rglob("*"):
                if f.is_file() and not should_skip(f):
                    yield f


def main():
    parser = argparse.ArgumentParser(description="Scan logs for errors/timeouts/retries.")
    parser.add_argument("path", nargs="?", default=".", help="Workspace root")
    parser.add_argument("--ext", action="append", default=[], help="Extra file extensions")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--max-lines", type=int, default=2000, help="Max lines to read per file")
    parser.add_argument("--include-root", action="store_true", help="Also scan root for log-like files")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    exts = DEFAULT_EXTS | set(args.ext)

    candidates = []
    for name in DEFAULT_DIRS:
        p = root / name
        if p.exists():
            candidates.append(p)

    if args.include_root or not candidates:
        candidates.append(root)

    results = []
    for f in iter_files(candidates):
        if f.suffix and f.suffix.lower() not in exts:
            continue
        try:
            with f.open("r", errors="ignore") as fh:
                hits = []
                for i, line in enumerate(fh):
                    if i >= args.max_lines:
                        break
                    for regex, label in PATTERNS:
                        if regex.search(line):
                            hits.append({"label": label, "line": i + 1, "text": line.strip()[:200]})
                if hits:
                    results.append({"file": str(f), "hits": hits})
        except OSError:
            continue

    summary = {
        "files_with_hits": len(results),
        "total_hits": sum(len(r["hits"]) for r in results),
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    files_with_hits = summary["files_with_hits"]
    total_hits = summary["total_hits"]

    print("Log scan summary")
    print(f"Files with hits: {files_with_hits}")
    print(f"Total hits: {total_hits}")
    for r in results:
        file_path = r["file"]
        print(f"\n{file_path}")
        for h in r["hits"][:20]:
            label = h["label"]
            line_no = h["line"]
            text = h["text"]
            print(f"  [{label}] L{line_no}: {text}")


if __name__ == "__main__":
    sys.exit(main())
