#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_EXCLUDES = {".git", "node_modules", ".next", "dist", "build", ".venv"}


def human_size(num: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            return f"{num:.1f}{unit}"
        num /= 1024
    return f"{num:.1f}PB"


def should_skip(path: Path, excludes) -> bool:
    parts = set(path.parts)
    return any(part in excludes for part in parts)


def collect_files(root: Path, excludes):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath = Path(dirpath)
        if should_skip(dirpath, excludes):
            dirnames[:] = []
            continue
        for name in filenames:
            p = dirpath / name
            try:
                if should_skip(p, excludes):
                    continue
                size = p.stat().st_size
                files.append((p, size))
            except (OSError, FileNotFoundError):
                continue
    return files


def build_dir_stats(root: Path, files):
    stats = {}
    root = root.resolve()
    for p, size in files:
        p = p.resolve()
        cur = p.parent
        while True:
            stats.setdefault(cur, [0, 0])
            stats[cur][0] += 1
            stats[cur][1] += size
            if cur == root:
                break
            cur = cur.parent
    return stats


def tree_lines(root: Path, stats, depth: int, excludes):
    lines = []
    root = root.resolve()
    root_count, root_size = stats.get(root, [0, 0])
    lines.append(f"{root.name}/ (files:{root_count}, size:{human_size(root_size)})")

    def walk_dir(path: Path, current_depth: int, prefix: str):
        if current_depth >= depth:
            return
        try:
            entries = sorted([p for p in path.iterdir() if p.is_dir()], key=lambda p: p.name.lower())
        except (OSError, FileNotFoundError):
            return
        entries = [p for p in entries if not should_skip(p, excludes)]
        for idx, entry in enumerate(entries):
            is_last = idx == len(entries) - 1
            branch = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")
            count, size = stats.get(entry.resolve(), [0, 0])
            lines.append(f"{prefix}{branch}{entry.name}/ (files:{count}, size:{human_size(size)})")
            walk_dir(entry, current_depth + 1, next_prefix)

    walk_dir(root, 0, "")
    return lines


def main():
    parser = argparse.ArgumentParser(description="Workspace inventory: tree with counts/sizes and largest files.")
    parser.add_argument("path", nargs="?", default=".", help="Root path")
    parser.add_argument("--depth", type=int, default=4, help="Tree depth")
    parser.add_argument("--top", type=int, default=20, help="Top N largest files")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude directory/file names")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    excludes = set(DEFAULT_EXCLUDES) | set(args.exclude)

    files = collect_files(root, excludes)
    stats = build_dir_stats(root, files)
    lines = tree_lines(root, stats, args.depth, excludes)

    files_sorted = sorted(files, key=lambda x: x[1], reverse=True)
    top_files = [
        {"path": str(p), "size": size, "size_human": human_size(size)}
        for p, size in files_sorted[: args.top]
    ]

    result = {
        "root": str(root),
        "total_files": len(files),
        "total_size": sum(size for _, size in files),
        "tree": lines,
        "top_files": top_files,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Workspace inventory")
    print("-")
    for line in lines:
        print(line)
    print("\nLargest files")
    for item in top_files:
        print(f"{item['size_human']:>8}  {item['path']}")


if __name__ == "__main__":
    sys.exit(main())
