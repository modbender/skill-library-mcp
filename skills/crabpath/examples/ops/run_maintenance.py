#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from crabpath import load_state
from crabpath.maintain import run_maintenance
from callbacks import make_embed_fn, make_llm_fn


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run slow-loop maintenance")
    parser.add_argument("--state", required=True, help="Path to state.json")
    parser.add_argument("--tasks", default="health,decay,merge,prune")
    parser.add_argument(
        "--embedder",
        default="openai",
        choices=["openai", "hash"],
        help="Embedding backend for maintenance connect step (default: openai)",
    )
    parser.add_argument(
        "--llm",
        default="gpt-5-mini",
        help="LLM model for merge judgment (default: gpt-5-mini)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-merges", type=int, default=5)
    parser.add_argument("--prune-below", type=float, default=0.01)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    state_path = Path(args.state)
    if not state_path.exists():
        raise SystemExit(f"state not found: {state_path}")

    _ = load_state(str(state_path))
    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    embedder_name = args.embedder
    if embedder_name == "openai" and not api_key_present:
        print("warning: OPENAI_API_KEY not set, using --embedder hash fallback")
        embedder_name = "hash"

    embed_fn = make_embed_fn(embedder_name)
    llm_fn = make_llm_fn(args.llm) if api_key_present else None

    tasks = [task.strip() for task in args.tasks.split(",") if task.strip()]

    report = run_maintenance(
        state_path=str(state_path),
        tasks=tasks,
        embed_fn=embed_fn,
        llm_fn=llm_fn,
        dry_run=args.dry_run,
        max_merges=args.max_merges,
        prune_below=args.prune_below,
        journal_path=str(state_path.parent / "journal.jsonl"),
    )

    if args.json:
        print(json.dumps(report.__dict__))
        return

    print(f"Maintenance report for {state_path}")
    print(f"  tasks: {', '.join(report.tasks_run) if report.tasks_run else '(none)'}")
    print(f"  nodes: {report.health_before['nodes']} -> {report.health_after['nodes']}")
    print(f"  edges: {report.edges_before} -> {report.edges_after}")
    print(f"  merges: {report.merges_applied}/{report.merges_proposed}")
    print(f"  pruned: edges={report.pruned_edges} nodes={report.pruned_nodes}")
    print(f"  dry_run: {args.dry_run}")
    if report.notes:
        print(f"  notes: {', '.join(report.notes)}")


if __name__ == "__main__":
    main()
