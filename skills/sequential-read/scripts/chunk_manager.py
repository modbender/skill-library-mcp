#!/usr/bin/env python3
"""
Manage chunks for a sequential_read session — save, get, list, structural-chunk.
Chunks are stored as <NNN>.md / <NNN>.meta.json in the session's chunks/ directory.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def get_workspace():
    ws = os.environ.get("OPENCLAW_WORKSPACE")
    if ws:
        return Path(ws)
    return Path.home() / ".openclaw" / "workspace"


def get_session_dir(session_id):
    return get_workspace() / "memory" / "sequential_read" / session_id


def chunk_path(session_dir, n):
    return session_dir / "chunks" / f"{int(n):03d}.md"


def meta_path(session_dir, n):
    return session_dir / "chunks" / f"{int(n):03d}.meta.json"


def require_session(session_id):
    sd = get_session_dir(session_id)
    if not sd.exists():
        print(f"Error: session not found: {session_id}", file=sys.stderr)
        sys.exit(1)
    return sd


# ── Structural chunker (fallback) ───────────────────────────────────

MIN_LINES = 200
TARGET_LINES = 550
MAX_LINES = 700


def find_chapter_markers(lines):
    markers = []
    patterns = [
        r"^CHAPTER\s+[IVXLCDM\d]+",
        r"^Chapter\s+[IVXLCDMivxlcdm\d]+",
        r"^PART\s+[IVXLCDM\d]+",
        r"^Part\s+[IVXLCDMivxlcdm\d]+",
        r"^\d+\.\s+\w",
        r"^[IVXLCDM]+\.\s*$",
        r"^\*\s*\*\s*\*",
        r"^—+$",
        r"^-{3,}$",
    ]
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pat in patterns:
            if re.match(pat, stripped, re.IGNORECASE):
                markers.append(i)
                break
    return markers


def find_scene_breaks(lines):
    breaks = []
    blank_count = 0
    for i, line in enumerate(lines):
        if not line.strip():
            blank_count += 1
        else:
            if blank_count >= 2:
                breaks.append(i - blank_count)
            blank_count = 0
    return breaks


def find_paragraph_breaks(lines):
    breaks = []
    for i, line in enumerate(lines):
        if not line.strip() and 0 < i < len(lines) - 1:
            breaks.append(i)
    return breaks


def structural_chunk(text_path):
    """Split text into structural chunks. Returns list of (start, end) line ranges."""
    with open(text_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    total = len(lines)
    chapter_markers = set(find_chapter_markers(lines))
    scene_breaks = set(find_scene_breaks(lines))
    para_breaks = set(find_paragraph_breaks(lines))

    chunks = []
    current_start = 0

    while current_start < total:
        ideal_end = min(current_start + TARGET_LINES, total)
        max_end = min(current_start + MAX_LINES, total)
        min_end = min(current_start + MIN_LINES, total)

        if total - current_start <= MAX_LINES:
            chunks.append((current_start, total))
            break

        best_break = None

        # Priority: chapter > scene > paragraph
        for boundary_set in (chapter_markers, scene_breaks, para_breaks):
            # Search backward from ideal first
            for i in range(ideal_end, min_end - 1, -1):
                if i in boundary_set:
                    best_break = i
                    break
            if best_break:
                break
            # Then forward
            for i in range(ideal_end, max_end):
                if i in boundary_set:
                    best_break = i
                    break
            if best_break:
                break

        if not best_break:
            best_break = ideal_end

        chunks.append((current_start, best_break))
        current_start = best_break

    return lines, chunks


# ── Subcommands ──────────────────────────────────────────────────────

def cmd_save(args):
    sd = require_session(args.session_id)
    n = int(args.chunk_number)

    text_file = Path(args.text_file)
    if not text_file.exists():
        print(f"Error: text file not found: {text_file}", file=sys.stderr)
        sys.exit(1)

    text = text_file.read_text(encoding="utf-8")
    try:
        meta = json.loads(args.meta)
    except json.JSONDecodeError as e:
        print(f"Error: invalid metadata JSON: {e}", file=sys.stderr)
        sys.exit(1)

    chunk_path(sd, n).write_text(text, encoding="utf-8")
    meta_path(sd, n).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    # Update total_chunks in session.json
    sp = sd / "session.json"
    session = json.loads(sp.read_text(encoding="utf-8"))
    if n > session.get("total_chunks", 0):
        session["total_chunks"] = n
    sp.write_text(json.dumps(session, indent=2) + "\n", encoding="utf-8")

    print(f"Saved chunk {n:03d} ({len(text)} chars)")


def cmd_get(args):
    sd = require_session(args.session_id)
    cp = chunk_path(sd, args.chunk_number)
    if not cp.exists():
        print(f"Error: chunk {args.chunk_number} not found", file=sys.stderr)
        sys.exit(1)
    print(cp.read_text(encoding="utf-8"), end="")


def cmd_get_meta(args):
    sd = require_session(args.session_id)
    mp = meta_path(sd, args.chunk_number)
    if not mp.exists():
        print(f"Error: chunk {args.chunk_number} metadata not found", file=sys.stderr)
        sys.exit(1)
    print(mp.read_text(encoding="utf-8"), end="")


def cmd_list(args):
    sd = require_session(args.session_id)
    chunks_dir = sd / "chunks"
    files = sorted(chunks_dir.glob("*.md"))
    if not files:
        print("No chunks saved yet.")
        return
    print(f"{'CHUNK':<8} {'CHARS':<10} {'TONE':<16} {'THEMES'}")
    print("-" * 70)
    for f in files:
        num = f.stem
        mp = chunks_dir / f"{num}.meta.json"
        chars = len(f.read_text(encoding="utf-8"))
        if mp.exists():
            try:
                m = json.loads(mp.read_text(encoding="utf-8"))
                tone = m.get("tone", "—")
                themes = ", ".join(m.get("themes", []))
            except json.JSONDecodeError:
                tone, themes = "?", "?"
        else:
            tone, themes = "—", "—"
        print(f"{num:<8} {chars:<10} {tone:<16} {themes}")


def cmd_structural_chunk(args):
    """Run the structural chunker on a source file and save chunks to a session."""
    sd = require_session(args.session_id)

    source = Path(args.source_file)
    if not source.exists():
        print(f"Error: source file not found: {source}", file=sys.stderr)
        sys.exit(1)

    lines, ranges = structural_chunk(str(source))
    total = len(ranges)

    for i, (start, end) in enumerate(ranges, 1):
        chunk_text = "".join(lines[start:end])
        cp = chunk_path(sd, i)
        cp.write_text(chunk_text, encoding="utf-8")

        meta = {
            "tone": "unanalysed",
            "intensity": "medium",
            "themes": [],
            "adjacent_relationship": f"structural chunk {i}/{total} (lines {start}-{end})",
            "line_range": [start, end],
            "line_count": end - start,
        }
        meta_path(sd, i).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    # Update session
    sp = sd / "session.json"
    session = json.loads(sp.read_text(encoding="utf-8"))
    session["total_chunks"] = total
    sp.write_text(json.dumps(session, indent=2) + "\n", encoding="utf-8")

    print(f"Created {total} structural chunks from {len(lines)} lines")
    for i, (start, end) in enumerate(ranges, 1):
        print(f"  {i:03d}: lines {start:>6}-{end:>6} ({end - start} lines)")


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Manage chunks for a sequential_read session")
    sub = parser.add_subparsers(dest="command")

    p_save = sub.add_parser("save", help="Save a chunk's text and metadata")
    p_save.add_argument("session_id")
    p_save.add_argument("chunk_number", type=int)
    p_save.add_argument("--text-file", required=True, help="Path to file containing chunk text")
    p_save.add_argument("--meta", required=True, help="Metadata JSON string")

    p_get = sub.add_parser("get", help="Print a chunk's text")
    p_get.add_argument("session_id")
    p_get.add_argument("chunk_number", type=int)

    p_gm = sub.add_parser("get-meta", help="Print a chunk's metadata")
    p_gm.add_argument("session_id")
    p_gm.add_argument("chunk_number", type=int)

    p_list = sub.add_parser("list", help="List all chunks in a session")
    p_list.add_argument("session_id")

    p_sc = sub.add_parser(
        "structural-chunk",
        help="Fallback: structurally chunk a source file into a session",
    )
    p_sc.add_argument("session_id")
    p_sc.add_argument("source_file", help="Path to the source text file")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {
        "save": cmd_save,
        "get": cmd_get,
        "get-meta": cmd_get_meta,
        "list": cmd_list,
        "structural-chunk": cmd_structural_chunk,
    }[args.command](args)


if __name__ == "__main__":
    main()
