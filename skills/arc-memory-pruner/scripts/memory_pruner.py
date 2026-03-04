#!/usr/bin/env python3
"""Memory Pruner — Keep agent memory lean with automatic pruning and compaction."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# Safe base directories where pruning is allowed
_ALLOWED_BASES = [
    os.path.expanduser("~/.openclaw"),
    os.path.expanduser("~/.claude"),
    os.path.expanduser("~/autonomous-ai/memory"),
    os.path.expanduser("~/autonomous-ai/journal"),
    os.path.expanduser("~/autonomous-ai/agents/logs"),
]


def _validate_prune_path(file_path, operation="prune"):
    """Validate that file path is within allowed directories for pruning."""
    real = os.path.realpath(str(file_path))
    for base in _ALLOWED_BASES:
        real_base = os.path.realpath(base)
        if real.startswith(real_base + os.sep) or real == real_base:
            return real
    print(f"ERROR: {operation} blocked — {file_path} is outside allowed directories", file=sys.stderr)
    print(f"Allowed: {', '.join(_ALLOWED_BASES)}", file=sys.stderr)
    sys.exit(1)


def prune_file(file_path, max_lines=None, max_bytes=None, dry_run=False):
    """Prune a file to keep it within limits.

    - max_lines: Keep only the last N lines
    - max_bytes: Keep only the last N bytes
    """
    file_path = _validate_prune_path(file_path)
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return {"pruned": False, "reason": "not found"}
    if path.is_symlink():
        print(f"ERROR: Will not prune symlink: {file_path}", file=sys.stderr)
        return {"pruned": False, "reason": "symlink"}

    original_size = path.stat().st_size
    with open(path) as f:
        lines = f.readlines()

    original_lines = len(lines)
    pruned = False
    reason = []

    if max_lines and len(lines) > max_lines:
        lines = lines[-max_lines:]
        pruned = True
        reason.append(f"trimmed to last {max_lines} lines (was {original_lines})")

    if max_bytes and original_size > max_bytes:
        # Keep lines from the end that fit within byte limit
        kept = []
        total = 0
        for line in reversed(lines):
            line_bytes = len(line.encode('utf-8'))
            if total + line_bytes > max_bytes:
                break
            kept.insert(0, line)
            total += line_bytes
        lines = kept
        pruned = True
        reason.append(f"trimmed to {max_bytes} bytes (was {original_size})")

    if pruned:
        if dry_run:
            print(f"DRY RUN: Would prune {file_path}")
            for r in reason:
                print(f"  {r}")
            print(f"  Result: {len(lines)} lines, ~{sum(len(l.encode('utf-8')) for l in lines)} bytes")
        else:
            with open(path, 'w') as f:
                f.writelines(lines)
            new_size = path.stat().st_size
            print(f"Pruned {file_path}: {', '.join(reason)}")
            print(f"  Size: {original_size} -> {new_size} bytes")
    else:
        print(f"No pruning needed for {file_path} ({original_lines} lines, {original_size} bytes)")

    return {
        "pruned": pruned,
        "original_lines": original_lines,
        "final_lines": len(lines),
        "original_bytes": original_size,
        "reason": reason,
    }


def prune_logs(log_dir, keep=7, dry_run=False):
    """Keep only the last N log files in a directory (circular buffer)."""
    _validate_prune_path(log_dir, "prune-logs")
    if keep < 1:
        print("ERROR: --keep must be >= 1 (cannot delete all files)", file=sys.stderr)
        return {"pruned": 0}
    path = Path(log_dir)
    if not path.exists():
        print(f"Directory not found: {log_dir}")
        return {"pruned": 0}

    # Sort files by modification time (oldest first)
    files = sorted(path.iterdir(), key=lambda f: f.stat().st_mtime)
    files = [f for f in files if f.is_file()]

    if len(files) <= keep:
        print(f"No pruning needed: {len(files)} files (keep={keep})")
        return {"pruned": 0, "total": len(files)}

    to_delete = files[:-keep]
    total_freed = 0

    for f in to_delete:
        size = f.stat().st_size
        if dry_run:
            print(f"DRY RUN: Would delete {f.name} ({size} bytes)")
        else:
            f.unlink()
            print(f"Deleted {f.name} ({size} bytes)")
        total_freed += size

    action = "Would delete" if dry_run else "Deleted"
    print(f"\n{action} {len(to_delete)} files, freed {total_freed} bytes. {keep} files retained.")
    return {"pruned": len(to_delete), "freed_bytes": total_freed, "retained": keep}


def compact_file(file_path, remove_before=None, remove_pattern=None, dry_run=False):
    """Remove sections of a file based on date or pattern.

    - remove_before: Remove lines containing dates before this cutoff (YYYY-MM-DD format)
    - remove_pattern: Remove lines matching this substring
    """
    file_path = _validate_prune_path(file_path, "compact")
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    with open(path) as f:
        lines = f.readlines()

    original_count = len(lines)
    kept = []
    removed = 0

    for line in lines:
        should_remove = False

        if remove_before:
            # Check if line contains a date that's before the cutoff
            import re
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', line)
            for d in dates:
                if d < remove_before:
                    should_remove = True
                    break

        if remove_pattern and remove_pattern in line:
            should_remove = True

        if should_remove:
            removed += 1
        else:
            kept.append(line)

    if removed > 0:
        if dry_run:
            print(f"DRY RUN: Would remove {removed} lines from {file_path}")
        else:
            with open(path, 'w') as f:
                f.writelines(kept)
            print(f"Compacted {file_path}: removed {removed} lines ({original_count} -> {len(kept)})")
    else:
        print(f"No compaction needed for {file_path}")

    return {"removed": removed, "original": original_count, "final": len(kept)}


def stats(directory):
    """Show memory file sizes and stats."""
    _validate_prune_path(directory, "stats")
    path = Path(directory).expanduser()
    if not path.exists():
        print(f"Directory not found: {directory}")
        return

    files = []
    for f in sorted(path.rglob("*.md")) + sorted(path.rglob("*.json")) + sorted(path.rglob("*.log")):
        if f.is_file():
            size = f.stat().st_size
            line_count = 0
            try:
                with open(f) as fh:
                    line_count = sum(1 for _ in fh)
            except (UnicodeDecodeError, PermissionError):
                pass
            files.append({"path": str(f.relative_to(path)), "size": size, "lines": line_count})

    if not files:
        print("No memory files found.")
        return

    total_size = sum(f["size"] for f in files)
    total_lines = sum(f["lines"] for f in files)

    print(f"Memory Stats — {path}")
    print(f"{'File':<50} {'Size':>10} {'Lines':>8}")
    print("-" * 68)
    for f in sorted(files, key=lambda x: -x["size"])[:20]:
        size_str = f"{f['size']:,}" if f['size'] < 1000000 else f"{f['size']/1000000:.1f}M"
        print(f"{f['path'][:50]:<50} {size_str:>10} {f['lines']:>8}")

    print("-" * 68)
    total_str = f"{total_size:,}" if total_size < 1000000 else f"{total_size/1000000:.1f}M"
    print(f"{'Total':<50} {total_str:>10} {total_lines:>8}")
    print(f"\n{len(files)} files found")


def main():
    parser = argparse.ArgumentParser(description="Memory Pruner")
    sub = parser.add_subparsers(dest="command")

    p_prune = sub.add_parser("prune", help="Prune a file")
    p_prune.add_argument("--file", required=True, help="File to prune")
    p_prune.add_argument("--max-lines", type=int, help="Keep last N lines")
    p_prune.add_argument("--max-bytes", type=int, help="Keep last N bytes")
    p_prune.add_argument("--dry-run", action="store_true")

    p_logs = sub.add_parser("prune-logs", help="Prune log directory")
    p_logs.add_argument("--dir", required=True, help="Log directory")
    p_logs.add_argument("--keep", type=int, default=7, help="Files to keep")
    p_logs.add_argument("--dry-run", action="store_true")

    p_compact = sub.add_parser("compact", help="Compact a file")
    p_compact.add_argument("--file", required=True, help="File to compact")
    p_compact.add_argument("--remove-before", help="Remove lines with dates before YYYY-MM-DD")
    p_compact.add_argument("--remove-pattern", help="Remove lines containing this text")
    p_compact.add_argument("--dry-run", action="store_true")

    p_stats = sub.add_parser("stats", help="Show memory file stats")
    p_stats.add_argument("--dir", default=".", help="Directory to scan")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "prune":
        prune_file(args.file, args.max_lines, args.max_bytes, args.dry_run)
    elif args.command == "prune-logs":
        prune_logs(args.dir, args.keep, args.dry_run)
    elif args.command == "compact":
        compact_file(args.file, args.remove_before, args.remove_pattern, args.dry_run)
    elif args.command == "stats":
        stats(args.dir)


if __name__ == "__main__":
    main()
