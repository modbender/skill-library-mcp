#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from crabpath import VectorIndex, load_state, save_state, split_workspace, traverse
from crabpath._batch import batch_or_single_embed
from crabpath.learn import apply_outcome
from crabpath.replay import replay_queries


def build_embed_batch_fn(client):
    def embed_batch(texts):
        ids, contents = zip(*texts)
        response = client.embeddings.create(model="text-embedding-3-small", input=list(contents))
        return {ids[i]: response.data[i].embedding for i in range(len(ids))}

    return embed_batch


def build_llm_fn(client):
    def llm_fn(system: str, user: str) -> str:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content

    return llm_fn


def main(workspace: str) -> None:
    workspace_path = Path(workspace)
    if not workspace_path.exists():
        raise SystemExit(f"workspace not found: {workspace_path}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required for this example")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    state_path = workspace_path / "state.json"

    embed_batch = build_embed_batch_fn(client)
    llm_fn = build_llm_fn(client)

    graph, texts = split_workspace(
        str(workspace_path),
        llm_fn=llm_fn,
        llm_batch_fn=None,
    )

    embeddings = batch_or_single_embed(list(texts.items()), embed_batch_fn=embed_batch)
    index = VectorIndex()
    for node_id, vector in embeddings.items():
        index.upsert(node_id, vector)

    embedder_name = "text-embedding-3-small"
    embedder_dim = len(next(iter(embeddings.values()))) if embeddings else 1536
    save_state(
        graph=graph,
        index=index,
        path=str(state_path),
        embedder_name=embedder_name,
        embedder_dim=embedder_dim,
    )

    loaded_graph, loaded_index, loaded_meta = load_state(str(state_path))
    replay_queries(
        graph=loaded_graph,
        queries=[
            "How should this system deploy?",
            "What are troubleshooting steps?",
        ],
    )

    query_text = "Where should I put deployment notes?"
    query_vector = embed_batch([("query", query_text)])["query"]
    result = traverse(
        graph=loaded_graph,
        seeds=loaded_index.search(query_vector, top_k=4),
        query_text=query_text,
    )
    print(json.dumps({"fired": result.fired, "context": result.context}, indent=2))

    if result.fired:
        apply_outcome(loaded_graph, fired_nodes=result.fired[:2], outcome=1.0)
        save_state(
            graph=loaded_graph,
            index=loaded_index,
            path=str(state_path),
            embedder_name=loaded_meta.get("embedder_name", embedder_name),
            embedder_dim=loaded_meta.get("embedder_dim", 1536),
        )
        print("learned")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 examples/openai_embedder/run.py ./workspace")
    main(sys.argv[1])
