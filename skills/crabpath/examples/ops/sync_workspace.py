#!/usr/bin/env python3
"""Sync an existing CrabPath state with workspace changes."""

from __future__ import annotations

import argparse
import json

from dataclasses import asdict

from crabpath import DEFAULT_AUTHORITY_MAP, sync_workspace
from callbacks import make_embed_fn


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Incrementally sync workspace markdown chunks into an existing state."
    )
    parser.add_argument("--state", required=True, help="Path to existing state.json")
    parser.add_argument("--workspace", required=True, help="Workspace directory")
    parser.add_argument(
        "--embedder",
        default="openai",
        choices=["openai", "hash"],
        help="Embedding backend for changed nodes",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args(argv)

    embed_fn = make_embed_fn(args.embedder)

    report = sync_workspace(
        state_path=args.state,
        workspace_dir=args.workspace,
        embed_fn=embed_fn,
        authority_map=DEFAULT_AUTHORITY_MAP,
    )

    payload = asdict(report)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"nodes added: {report.nodes_added}")
        print(f"nodes updated: {report.nodes_updated}")
        print(f"nodes removed: {report.nodes_removed}")
        print(f"nodes unchanged: {report.nodes_unchanged}")
        print(f"embeddings computed: {report.embeddings_computed}")
        print(f"authority set: {report.authority_set}")


if __name__ == "__main__":
    main()
