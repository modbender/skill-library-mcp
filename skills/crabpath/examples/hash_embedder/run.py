#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from crabpath import HashEmbedder, VectorIndex, load_state, save_state, split_workspace, traverse


def main(workspace: str) -> None:
    workspace_path = Path(workspace)
    if not workspace_path.exists():
        raise SystemExit(f"workspace not found: {workspace_path}")

    state_path = workspace_path / "state.json"

    graph, texts = split_workspace(str(workspace_path), llm_fn=None, llm_batch_fn=None)
    embedder = HashEmbedder()
    vectors = embedder.embed_batch(list(texts.items()))

    index = VectorIndex()
    for node_id, vector in vectors.items():
        index.upsert(node_id, vector)

    save_state(
        graph=graph,
        index=index,
        path=str(state_path),
        embedder_name=embedder.name,
        embedder_dim=embedder.dim,
    )

    loaded_graph, loaded_index, loaded_meta = load_state(str(state_path))
    print(
        json.dumps(
            {
                "state": str(state_path),
                "nodes": len(loaded_graph.nodes()),
                "embedder": loaded_meta.get("embedder_name"),
                "dim": loaded_meta.get("embedder_dim"),
            },
            indent=2,
        )
    )

    query_text = "What does this workspace document explain?"
    query_vec = embedder.embed(query_text)
    seeds = loaded_index.search(query_vec, top_k=4)
    result = traverse(graph=loaded_graph, seeds=seeds, query_text=query_text)

    print(json.dumps({"fired": result.fired, "context": result.context}, indent=2))

    if result.fired:
        loaded_graph, loaded_index, loaded_meta = load_state(str(state_path))
        from crabpath.learn import apply_outcome

        apply_outcome(loaded_graph, fired_nodes=result.fired[:2], outcome=1.0)
        save_state(
            graph=loaded_graph,
            index=loaded_index,
            path=str(state_path),
            embedder_name=str(loaded_meta.get("embedder_name", embedder.name)),
            embedder_dim=int(loaded_meta.get("embedder_dim", embedder.dim)),
        )
        print("learned")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 examples/hash_embedder/run.py ./workspace")
    main(sys.argv[1])
