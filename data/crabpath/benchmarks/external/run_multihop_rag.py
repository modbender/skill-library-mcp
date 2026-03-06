from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

from crabpath import Edge, Graph, LearningConfig, Node, TraversalConfig, VectorIndex, apply_outcome, apply_outcome_pg, traverse


EMBED_MODEL = "text-embedding-3-small"
CACHE_PATH = Path("benchmarks/external/.embedding_cache_mhrag.json")
LEARNING_CONFIG = LearningConfig(learning_rate=0.3, discount=0.9)
DEFAULT_EMBED_TOP_K = 10
DEFAULT_SEED_TOP_K = 8
DEFAULT_MAX_HOPS = 3
DEFAULT_BEAM_WIDTH = 4
DEFAULT_LIMIT = 1000
CHECKPOINTS = [100, 250, 500, 1000, 2556]
RUN_METRICS = ["full_hit_rate", "partial_hit_rate", "evidence_recall_at_10", "mrr", "nodes_fired"]


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:80]


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected a JSON list: {path}")
    return data


def _load_dataset(path: Path, limit: int) -> list[dict[str, Any]]:
    rows = _load_json_list(path)
    filtered = [row for row in rows if str(row.get("question_type", "")) != "null_query"]
    if limit <= 0:
        return filtered
    return filtered[:limit]


def _add_or_boost_edge(graph: Graph, source_id: str, target_id: str, weight: float) -> None:
    if source_id == target_id:
        return
    current = graph._edges.get(source_id, {}).get(target_id)
    if current is None or weight > current.weight:
        graph.add_edge(Edge(source=source_id, target=target_id, weight=weight, kind="sibling"))


def _build_graph(rows: list[dict[str, Any]]) -> tuple[Graph, dict[str, str], list[str]]:
    graph = Graph()
    title_to_id: dict[str, str] = {}
    source_to_nodes: dict[str, set[str]] = {}
    category_to_nodes: dict[str, set[str]] = {}

    for row in rows:
        for evidence in row.get("evidence_list", []) if isinstance(row.get("evidence_list"), list) else []:
            if not isinstance(evidence, dict):
                continue
            title = str(evidence.get("title", "")).strip()
            if not title:
                continue
            node_id = _slugify(title)
            fact = str(evidence.get("fact", "")).strip()
            source = str(evidence.get("source", "")).strip()
            category = str(evidence.get("category", "")).strip()
            if node_id not in title_to_id.values():
                graph.add_node(
                    Node(
                        id=node_id,
                        content=fact,
                        metadata={"title": title, "source": source, "category": category},
                    )
                )
                title_to_id[title] = node_id
            else:
                node = graph.get_node(node_id)
                if node is not None and not node.content and fact:
                    node.content = fact

            if source:
                source_to_nodes.setdefault(source, set()).add(node_id)
            if category:
                category_to_nodes.setdefault(category, set()).add(node_id)

    for group in source_to_nodes.values():
        ids = sorted(group)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                _add_or_boost_edge(graph, ids[i], ids[j], 0.35)
                _add_or_boost_edge(graph, ids[j], ids[i], 0.35)

    for group in category_to_nodes.values():
        ids = sorted(group)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                _add_or_boost_edge(graph, ids[i], ids[j], 0.35)
                _add_or_boost_edge(graph, ids[j], ids[i], 0.35)

    for row in rows:
        evidence_ids = sorted(
            {
                title_to_id[str(evidence.get("title", "")).strip()]
                for evidence in row.get("evidence_list", []) if isinstance(evidence, dict)
                if str(evidence.get("title", "")).strip() in title_to_id
            }
        )
        for i in range(len(evidence_ids)):
            for j in range(i + 1, len(evidence_ids)):
                _add_or_boost_edge(graph, evidence_ids[i], evidence_ids[j], 0.5)
                _add_or_boost_edge(graph, evidence_ids[j], evidence_ids[i], 0.5)

    return graph, title_to_id, list(title_to_id.keys())


def _clone_graph(graph: Graph) -> Graph:
    copy = Graph()
    copy._nodes = {node_id: node for node_id, node in graph._nodes.items()}
    copy._edges = {source: dict(targets) for source, targets in graph._edges.items()}
    return copy


def _build_index_from_nodes(graph: Graph, cache: dict[str, list[float]]) -> VectorIndex:
    index = VectorIndex()
    for node in graph.nodes():
        vector = cache.get(node.content)
        if vector is None:
            raise SystemExit(f"missing embedding for node {node.id}")
        index.upsert(node.id, vector)
    return index


def _load_cache(path: Path) -> dict[str, list[float]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return {str(text): list(vec) for text, vec in data.items() if isinstance(text, str) and isinstance(vec, list)}


def _save_cache(path: Path, cache: dict[str, list[float]]) -> None:
    path.write_text(json.dumps(cache), encoding="utf-8")


def _chunked(values: list[str], size: int) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def _embed_batch(client: OpenAI | None, texts: list[str]) -> list[list[float]]:
    if client is None:
        raise SystemExit("OPENAI_API_KEY is required to create missing embeddings")
    try:
        response = client.embeddings.create(model=EMBED_MODEL, input=texts)
        return [list(record.embedding) for record in response.data]
    except Exception:
        time.sleep(2)
        response = client.embeddings.create(model=EMBED_MODEL, input=texts)
        return [list(record.embedding) for record in response.data]


def _cache_embeddings(client: OpenAI | None, cache: dict[str, list[float]], texts: list[str]) -> None:
    pending = list(dict.fromkeys([text for text in texts if text and text not in cache]))
    if not pending:
        return
    for chunk in _chunked(pending, 100):
        vectors = _embed_batch(client, chunk)
        for text, vector in zip(chunk, vectors):
            cache[text] = vector


def _prepare_cache(cache: dict[str, list[float]], texts: list[str], client: OpenAI | None) -> dict[str, list[float]]:
    pending = list(dict.fromkeys([text for text in texts if text and text not in cache]))
    if pending:
        if client is None:
            raise SystemExit("OPENAI_API_KEY is required to create missing embeddings")
        _cache_embeddings(client, cache, pending)
        _save_cache(CACHE_PATH, cache)
    return cache


def _required_texts(graph: Graph, rows: list[dict[str, Any]]) -> list[str]:
    texts = [node.content for node in graph.nodes() if node.content]
    queries = [str(row.get("query", "")) for row in rows if str(row.get("query", ""))]
    return list(dict.fromkeys([text for text in texts + queries if text]))


def _build_embeddings(client: OpenAI | None, graph: Graph) -> dict[str, list[float]]:
    cache = _load_cache(CACHE_PATH)
    _prepare_cache(cache, [node.content for node in graph.nodes()], client)
    _save_cache(CACHE_PATH, cache)
    return cache


def _ensure_query_embedding(client: OpenAI | None, cache: dict[str, list[float]], query: str) -> list[float]:
    if query not in cache:
        if client is None:
            raise SystemExit("OPENAI_API_KEY is required to create missing query embeddings")
        _cache_embeddings(client, cache, [query])
        _save_cache(CACHE_PATH, cache)
    vector = cache.get(query)
    if vector is None:
        raise SystemExit(f"could not embed query: {query}")
    return vector


def _ground_truth_ids(row: dict[str, Any], title_to_id: dict[str, str]) -> set[str]:
    ids: set[str] = set()
    for evidence in row.get("evidence_list", []) if isinstance(row.get("evidence_list"), list) else []:
        if not isinstance(evidence, dict):
            continue
        title = str(evidence.get("title", "")).strip()
        if not title:
            continue
        node_id = title_to_id.get(title)
        if node_id:
            ids.add(node_id)
    return ids


def _row_metrics(retrieved: list[str], relevant: set[str], embed_top_k: int) -> dict[str, float]:
    top10 = retrieved[:min(embed_top_k, 10)]
    relevant_found_top10 = len([node_id for node_id in top10 if node_id in relevant])
    full_hit = 1.0 if relevant.issubset(set(retrieved)) else 0.0
    partial_hit = 1.0 if set(retrieved).intersection(relevant) else 0.0
    recall_at_10 = relevant_found_top10 / len(relevant) if relevant else 0.0
    mrr = 0.0
    for rank, node_id in enumerate(retrieved, start=1):
        if node_id in relevant:
            mrr = 1.0 / rank
            break
    return {
        "full_hit_rate": full_hit,
        "partial_hit_rate": partial_hit,
        "evidence_recall_at_10": recall_at_10,
        "mrr": mrr,
        "nodes_fired": float(len(retrieved)),
    }


def _avg(metrics: list[dict[str, float]]) -> dict[str, float]:
    if not metrics:
        return {"full_hit_rate": 0.0, "partial_hit_rate": 0.0, "evidence_recall_at_10": 0.0, "mrr": 0.0, "nodes_fired": 0.0}
    count = len(metrics)
    return {key: sum(row[key] for row in metrics) / count for key in metrics[0]}


def _log_progress(method_name: str, processed: int, metrics: dict[str, float], keys: list[str]) -> None:
    print(
        f"[{method_name}] processed={processed} "
        + ", ".join(f"{key}={metrics[key]:.3f}" for key in keys if key in metrics)
    )


def _embedding_topk(
    graph: Graph,
    index: VectorIndex,
    client: OpenAI | None,
    cache: dict[str, list[float]],
    query: str,
    embed_top_k: int,
) -> list[str]:
    vector = _ensure_query_embedding(client, cache, query)
    return [node_id for node_id, _ in index.search(vector, top_k=embed_top_k)]


def _traverse_topk(
    graph: Graph,
    index: VectorIndex,
    client: OpenAI | None,
    cache: dict[str, list[float]],
    query: str,
    seed_top_k: int,
    traversal_config: TraversalConfig,
) -> list[str]:
    vector = _ensure_query_embedding(client, cache, query)
    seeds = [(node_id, score) for node_id, score in index.search(vector, top_k=seed_top_k)]
    if not seeds:
        return []
    result = traverse(graph=graph, seeds=seeds, config=traversal_config, query_text=query)
    return result.fired


def _run_static(
    rows: list[dict[str, Any]],
    graph: Graph,
    index: VectorIndex,
    client: OpenAI | None,
    cache: dict[str, list[float]],
    title_to_id: dict[str, str],
    use_traversal: bool,
    method_name: str,
    embed_top_k: int,
    seed_top_k: int,
    traversal_config: TraversalConfig,
) -> dict[str, float]:
    per_query = []
    for idx, row in enumerate(rows, start=1):
        query = str(row.get("query", ""))
        retrieved = (
            _traverse_topk(graph, index, client, cache, query, seed_top_k=seed_top_k, traversal_config=traversal_config)
            if use_traversal
            else _embedding_topk(graph, index, client, cache, query, embed_top_k=embed_top_k)
        )
        per_query.append(_row_metrics(retrieved, _ground_truth_ids(row, title_to_id), embed_top_k=embed_top_k))
        if idx % 100 == 0:
            _log_progress(method_name, idx, _avg(per_query), RUN_METRICS)
    return _avg(per_query)


def _run_learning(
    rows: list[dict[str, Any]],
    graph: Graph,
    index: VectorIndex,
    client: OpenAI | None,
    cache: dict[str, list[float]],
    title_to_id: dict[str, str],
    use_pg: bool,
    method_name: str,
    seed_top_k: int,
    traversal_config: TraversalConfig,
    embed_top_k: int,
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    history: list[dict[str, float]] = []
    checkpoints = {point for point in CHECKPOINTS if point <= len(rows)}
    learning_curve: dict[str, dict[str, float]] = {}

    for idx, row in enumerate(rows, start=1):
        query = str(row.get("query", ""))
        retrieved = _traverse_topk(graph, index, client, cache, query, seed_top_k=seed_top_k, traversal_config=traversal_config)
        relevant = _ground_truth_ids(row, title_to_id)
        scores = _row_metrics(retrieved, relevant, embed_top_k=embed_top_k)
        history.append(scores)

        outcome = 1.0 if scores["full_hit_rate"] >= 1.0 else -1.0
        if use_pg:
            apply_outcome_pg(graph=graph, fired_nodes=retrieved, outcome=outcome, config=LEARNING_CONFIG, temperature=1.0)
        else:
            apply_outcome(graph=graph, fired_nodes=retrieved, outcome=outcome, config=LEARNING_CONFIG)

        if idx in checkpoints:
            learning_curve[str(idx)] = _avg(history)
        if idx % 100 == 0:
            _log_progress(method_name, idx, _avg(history), RUN_METRICS)

    return _avg(history), learning_curve


def _print_ascii(methods: dict[str, dict[str, float]], learning_curves: dict[str, dict[str, dict[str, float]]]) -> None:
    print("\nMethod                  FullHit  Partial  Recall@10  MRR    NodesFired")
    print("-----------------------------------------------------------------------")
    for key in ["embedding_topk", "crabpath_cold", "crabpath_learning", "crabpath_pg_learning"]:
        values = methods[key]
        print(
            f"{key:<22}"
            f"{values['full_hit_rate']:.3f}    "
            f"{values['partial_hit_rate']:.3f}     "
            f"{values['evidence_recall_at_10']:.3f}     "
            f"{values['mrr']:.3f}   "
            f"{values['nodes_fired']:.2f}"
        )

    print("\nLearning Curves")
    for name in ["crabpath_learning", "crabpath_pg_learning"]:
        print(f"\n{name}")
        print("query  FullHit  Partial  Recall@10  MRR    NodesFired")
        for checkpoint in sorted(learning_curves.get(name, {}), key=lambda value: int(value)):
            values = learning_curves[name][checkpoint]
            print(
                f"{checkpoint:>5}  "
                f"{values['full_hit_rate']:.3f}    "
                f"{values['partial_hit_rate']:.3f}     "
                f"{values['evidence_recall_at_10']:.3f}     "
                f"{values['mrr']:.3f}   "
                f"{values['nodes_fired']:.2f}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MultiHop-RAG benchmark.")
    parser.add_argument(
        "--input",
        default="benchmarks/external/multihop_rag.json",
        help="Path to MultiHop-RAG dataset JSON",
    )
    parser.add_argument(
        "--output",
        default="benchmarks/external/multihop_rag_results.json",
        help="Path to write benchmark output JSON",
    )
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Number of dataset queries to evaluate")
    parser.add_argument(
        "--seed-top-k",
        type=int,
        default=DEFAULT_SEED_TOP_K,
        help="Seed top-k for graph traversal",
    )
    parser.add_argument(
        "--embed-top-k",
        type=int,
        default=DEFAULT_EMBED_TOP_K,
        help="Top-k for retrieval-only embedding baseline",
    )
    parser.add_argument(
        "--max-hops",
        type=int,
        default=DEFAULT_MAX_HOPS,
        help="Traversal max_hops",
    )
    parser.add_argument(
        "--beam-width",
        type=int,
        default=DEFAULT_BEAM_WIDTH,
        help="Traversal beam_width",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"dataset not found: {input_path}")
    output_path = Path(args.output)

    rows = _load_dataset(input_path, limit=args.limit)
    graph, title_to_id, titles = _build_graph(rows)
    if not graph.node_count():
        raise SystemExit("no nodes were built from dataset")

    required_texts = _required_texts(graph, rows)
    cache = _load_cache(CACHE_PATH)
    missing = [text for text in required_texts if text not in cache]
    client: OpenAI | None = OpenAI() if missing else None
    if missing and not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required to build missing embeddings")

    cache = _prepare_cache(cache, required_texts, client)
    index = _build_index_from_nodes(graph, cache)
    traversal_config = TraversalConfig(max_hops=args.max_hops, beam_width=args.beam_width)

    methods = {}
    learning_curves: dict[str, dict[str, dict[str, float]]] = {}

    methods["embedding_topk"] = _run_static(
        rows=rows,
        graph=graph,
        index=index,
        client=client,
        cache=cache,
        title_to_id=title_to_id,
        use_traversal=False,
        method_name="embedding_topk",
        embed_top_k=args.embed_top_k,
        seed_top_k=args.seed_top_k,
        traversal_config=traversal_config,
    )

    cold_graph = _clone_graph(graph)
    methods["crabpath_cold"] = _run_static(
        rows=rows,
        graph=cold_graph,
        index=_build_index_from_nodes(cold_graph, cache),
        client=client,
        cache=cache,
        title_to_id=title_to_id,
        use_traversal=True,
        method_name="crabpath_cold",
        embed_top_k=args.embed_top_k,
        seed_top_k=args.seed_top_k,
        traversal_config=traversal_config,
    )

    learning_graph = _clone_graph(graph)
    methods["crabpath_learning"], learning_curves["crabpath_learning"] = _run_learning(
        rows=rows,
        graph=learning_graph,
        index=_build_index_from_nodes(learning_graph, cache),
        client=client,
        cache=cache,
        title_to_id=title_to_id,
        use_pg=False,
        method_name="crabpath_learning",
        seed_top_k=args.seed_top_k,
        traversal_config=traversal_config,
        embed_top_k=args.embed_top_k,
    )

    pg_graph = _clone_graph(graph)
    methods["crabpath_pg_learning"], learning_curves["crabpath_pg_learning"] = _run_learning(
        rows=rows,
        graph=pg_graph,
        index=_build_index_from_nodes(pg_graph, cache),
        client=client,
        cache=cache,
        title_to_id=title_to_id,
        use_pg=True,
        method_name="crabpath_pg_learning",
        seed_top_k=args.seed_top_k,
        traversal_config=traversal_config,
        embed_top_k=args.embed_top_k,
    )

    _print_ascii(methods, learning_curves)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "dataset": "MultiHop-RAG",
                "dataset_path": str(input_path),
                "dataset_queries": len(rows),
                "titles_considered": len(titles),
                "graph_nodes": graph.node_count(),
                "graph_edges": graph.edge_count(),
                "cache_path": str(CACHE_PATH),
                "parameters": {
                    "limit": args.limit,
                    "seed_top_k": args.seed_top_k,
                    "embed_top_k": args.embed_top_k,
                    "max_hops": args.max_hops,
                    "beam_width": args.beam_width,
                },
                "method_metrics": methods,
                "learning_curves": learning_curves,
                "checkpoints": CHECKPOINTS,
                "traversal": {"max_hops": traversal_config.max_hops, "beam_width": traversal_config.beam_width},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
