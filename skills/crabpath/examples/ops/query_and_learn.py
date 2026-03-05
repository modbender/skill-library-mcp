#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from crabpath import TraversalConfig, apply_outcome, load_state, save_state, traverse
from crabpath.journal import log_learn, log_query
from callbacks import make_embed_fn


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Traverse + apply one-shot outcome")
    parser.add_argument("--state", required=True, help="Path to state.json")
    parser.add_argument("--query", required=True, help="Query text")
    parser.add_argument("--top", type=int, default=4)
    parser.add_argument("--outcome", type=float, default=1.0)
    parser.add_argument("--journal")
    parser.add_argument(
        "--embedder",
        default="openai",
        choices=["openai", "hash"],
        help="Embedding backend to use (default: openai)",
    )
    args = parser.parse_args(argv)

    state_path = Path(args.state)
    if not state_path.exists():
        raise SystemExit(f"state not found: {state_path}")
    if args.top <= 0:
        raise SystemExit("--top must be >= 1")

    graph, index, meta = load_state(str(state_path))

    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    embedder_name = args.embedder
    if embedder_name == "openai" and not api_key_present:
        print("warning: OPENAI_API_KEY not set, using --embedder hash fallback")
        embedder_name = "hash"
    embed_fn = make_embed_fn(embedder_name)
    query_vector = embed_fn(args.query)

    expected_dim = meta.get("embedder_dim")
    if isinstance(expected_dim, int) and len(query_vector) != expected_dim:
        raise SystemExit(
            f"Embedding dim mismatch: query={len(query_vector)} state={expected_dim}. "
            "Use the same embedder configuration as the state.")

    seeds = index.search(query_vector, top_k=args.top)
    result = traverse(graph=graph, seeds=seeds, query_text=args.query, config=TraversalConfig(max_context_chars=8000))

    print("Fired nodes:")
    for node_id in result.fired:
        print(f"- {node_id}")
    print("Context:")
    print(result.context or "(no context)")

    if result.fired:
        apply_outcome(graph=graph, fired_nodes=result.fired, outcome=args.outcome)

    save_state(graph=graph, index=index, path=str(state_path), meta=meta)

    journal_path = args.journal or str(state_path.parent / "journal.jsonl")
    log_query(query_text=args.query, fired_ids=result.fired, node_count=graph.node_count(), journal_path=journal_path)
    if result.fired:
        log_learn(fired_ids=result.fired, outcome=args.outcome, journal_path=journal_path)

    print(json.dumps({
        "state": str(state_path),
        "query": args.query,
        "fired_nodes": result.fired,
        "context": result.context,
        "outcome": args.outcome,
    }))


if __name__ == "__main__":
    main()
