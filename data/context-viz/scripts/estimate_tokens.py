#!/usr/bin/env python3
"""Estimate token counts for OpenClaw workspace files.

Usage: python3 estimate_tokens.py /path/to/workspace

Outputs JSON with per-file token estimates, totals, and memory/ inventory.
Token estimate: ~4 characters per token (rough average).
"""

import json
import os
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4

WORKSPACE_FILES = [
    ("AGENTS.md", "📋", "AGENTS.md"),
    ("SOUL.md", "👻", "SOUL.md"),
    ("USER.md", "👤", "USER.md"),
    ("TOOLS.md", "🔧", "TOOLS.md"),
    ("HEARTBEAT.md", "💓", "HEARTBEAT.md"),
    ("MEMORY.md", "🧠", "MEMORY.md"),
    ("IDENTITY.md", "🪪", "IDENTITY.md"),
]

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)

def scan_memory_dir(workspace: str):
    """Scan memory/ directory for all files, grouped by type."""
    memory_dir = os.path.join(workspace, "memory")
    if not os.path.isdir(memory_dir):
        return [], 0, 0

    entries = []
    total_tokens = 0
    total_bytes = 0

    for root, dirs, files in os.walk(memory_dir):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in sorted(files):
            if fname.startswith('.'):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, workspace)
            try:
                size = os.path.getsize(fpath)
                total_bytes += size
                # Estimate tokens for text files only
                if fname.endswith(('.md', '.json', '.txt', '.yaml', '.yml')):
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    tokens = estimate_tokens(content)
                else:
                    tokens = 0  # binary files
                total_tokens += tokens
                entries.append({
                    "path": rel,
                    "bytes": size,
                    "tokens": tokens,
                })
            except (OSError, IOError):
                continue

    return entries, total_tokens, total_bytes

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 estimate_tokens.py <workspace_path>", file=sys.stderr)
        sys.exit(1)

    workspace = sys.argv[1]

    # Workspace files (loaded into context)
    context_files = []
    total_context_tokens = 0
    for filename, emoji, label in WORKSPACE_FILES:
        path = os.path.join(workspace, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            tokens = estimate_tokens(content)
            chars = len(content)
        else:
            tokens = 0
            chars = 0
        context_files.append({
            "file": filename, "emoji": emoji, "label": label,
            "chars": chars, "tokens": tokens,
            "exists": os.path.exists(path),
        })
        total_context_tokens += tokens

    # Memory files (NOT in context, but useful inventory)
    mem_entries, mem_tokens, mem_bytes = scan_memory_dir(workspace)

    # Group memory files by category
    categories = {}
    for entry in mem_entries:
        parts = entry["path"].split(os.sep)
        if len(parts) >= 3:
            cat = parts[1]  # memory/<category>/...
        else:
            # Categorize by filename pattern
            fname = parts[-1]
            if "chinese-ai-digest" in fname:
                cat = "chinese-ai-digests"
            elif "linkedin" in fname or "benedikt" in fname:
                cat = "linkedin"
            elif fname.startswith("2026-"):
                cat = "daily-notes"
            else:
                cat = "other"
        if cat not in categories:
            categories[cat] = {"files": 0, "tokens": 0, "bytes": 0}
        categories[cat]["files"] += 1
        categories[cat]["tokens"] += entry["tokens"]
        categories[cat]["bytes"] += entry["bytes"]

    output = {
        "workspace": workspace,
        "contextFiles": context_files,
        "totalContextFileTokens": total_context_tokens,
        "systemOverheadEstimate": 9000,
        "memory": {
            "totalFiles": len(mem_entries),
            "totalTokens": mem_tokens,
            "totalBytes": mem_bytes,
            "categories": categories,
        },
        "note": "Token estimates use ~4 chars/token. Memory files are NOT loaded into context but shown as inventory."
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
