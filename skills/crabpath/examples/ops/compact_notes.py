#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from crabpath.compact import compact_daily_notes
from callbacks import make_embed_fn, make_llm_fn


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compact older daily notes and inject summaries")
    parser.add_argument("--state", required=True, help="Path to state.json")
    parser.add_argument("--memory-dir", required=True, help="Directory with YYYY-MM-DD.md notes")
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--target-lines", type=int, default=15)
    parser.add_argument("--llm", choices=["none", "openai"], default="none")
    parser.add_argument("--embedder", choices=["hash", "openai"], default="hash")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    state_path = Path(args.state)
    if not state_path.exists():
        raise SystemExit(f"state not found: {state_path}")

    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    embedder = args.embedder
    if embedder == "openai" and not api_key_present:
        print("warning: OPENAI_API_KEY not set, using --embedder hash fallback")
        embedder = "hash"

    llm_fn = make_llm_fn("gpt-5-mini") if args.llm == "openai" and api_key_present else None
    embed_fn = make_embed_fn(embedder)

    report = compact_daily_notes(
        state_path=str(state_path),
        memory_dir=args.memory_dir,
        max_age_days=args.max_age_days,
        target_lines=args.target_lines,
        embed_fn=embed_fn,
        llm_fn=llm_fn,
        journal_path=str(state_path.parent / "journal.jsonl"),
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps(report.__dict__, indent=2))
        return

    print(f"Compaction report for {state_path}")
    print(f"  scanned: {report.files_scanned}")
    print(f"  compacted: {report.files_compacted}")
    print(f"  skipped: {report.files_skipped}")
    print(f"  nodes_injected: {report.nodes_injected}")
    print(f"  lines: {report.lines_before} -> {report.lines_after}")


if __name__ == "__main__":
    main()
