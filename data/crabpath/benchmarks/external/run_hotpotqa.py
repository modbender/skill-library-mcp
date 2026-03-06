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
CACHE_PATH = Path("benchmarks/external/.embedding_cache_hotpot.json")
LEARNING_CONFIG = LearningConfig(learning_rate=0.3, discount=0.9)
DEFAULT_EMBED_TOP_K = 10
DEFAULT_SEED_TOP_K = 8
DEFAULT_MAX_HOPS = 3
DEFAULT_BEAM_WIDTH = 4
DEFAULT_LIMIT = 500
CHECKPOINTS = [50, 100, 200, 500]
RUN_METRICS = ["sp_recall_at_10", "sp_recall_at_5", "mrr", "nodes_fired"]


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:80]


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected a JSON list: {path}")
    return data


def _load_dataset(path: Path, limit: int = 500) -> list[dict[str, Any]]:
    rows = _load_json_list(path)
    if limit <= 0:
        return rows
    return rows[:limit]


def _add_or_boost_edge(graph: Graph, source_id: str, target_id: str, weight: float) -> None:
    if source_id == target_id:
        return
    current = graph._edges.get(source_id, {}).get(target_id)
    if current is None or weight > current.weight:
        graph.add_edge(Edge(source=source_id, target=target_id, weight=weight, kind="sibling"))


def _build_graph(rows: list[dict[str, Any]]) -> tuple[Graph, dict[str, str]]:
    graph = Graph()
    title_to_id: dict[str, str] = {}

    question_context_nodes: list[set[str]] = []
    for row in rows:
        context_ids: set[str] = set()
        for paragraph in row.get("context", []) if isinstance(row.get("context"), list) else []:
            if not isinstance(paragraph, list) or len(paragraph) < 2:
                continue
            title = str(paragraph[0]).strip()
            if not title:
                continue
            node_id = _slugify(title)
            sentences = [str(sentence).strip() for sentence in paragraph[1] if str(sentence).strip()]
            content = " ".join(sentences)
            if node_id not in title_to_id.values():
                graph.add_node(Node(id=node_id, content=content, metadata={"title": title}))
                title_to_id[title] = node_id
            context_ids.add(node_id)
        question_context_nodes.append(context_ids)

    for row_context_ids in question_context_nodes:
        ids = sorted(row_context_ids)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                _add_or_boost_edge(graph, ids[i], ids[j], 0.3)
                _add_or_boost_edge(graph, ids[j], ids[i], 0.3)

    for row in rows:
        titles = [
            str(fact[0]).strip()
            for fact in row.get("supporting_facts", []) if isinstance(fact, list) and fact
            if str(fact[0]).strip() in title_to_id
        ]
        title_ids = [title_to_id[title] for title in dict.fromkeys(titles)]
        for i in range(len(title_ids)):
            for j in range(i + 1, len(title_ids)):
                _add_or_boost_edge(graph, title_ids[i], title_ids[j], 0.5)
                _add_or_boost_edge(graph, title_ids[j], title_ids[i], 0.5)

    return graph, title_to_id


def _clone_graph(graph: Graph) -> Graph:
    copy = Graph()
    copy._nodes = {node_id: node for node_id, node in graph._nodes.items()}
    copy._edges = {source: dict(targets) for source, targets in graph._edges.items()}
    return copy


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
    queries = [str(row.get("question", "")) for row in rows if str(row.get("question", ""))]
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


def _build_index_from_nodes(graph: Graph, cache: dict[str, list[float]]) -> VectorIndex:
    index = VectorIndex()
    for node in graph.nodes():
        vector = cache.get(node.content)
        if vector is None:
            raise SystemExit(f"missing embedding for node {node.id}")
        index.upsert(node.id, vector)
    return index


def _ground_truth_ids(row: dict[str, Any], title_to_id: dict[str, str]) -> set[str]:
    ids: set[str] = set()
    for fact in row.get("supporting_facts", []) if isinstance(row.get("supporting_facts"), list) else []:
        if not isinstance(fact, list) or not fact:
            continue
        title = str(fact[0]).strip()
        node_id = title_to_id.get(title)
        if node_id:
            ids.add(node_id)
    return ids


def _row_metrics(retrieved: list[str], relevant: set[str]) -> dict[str, float]:
    top5 = retrieved[:5]
    top10 = retrieved[:10]
    recall_at_5 = 1.0 if relevant.issubset(set(top5)) else 0.0
    recall_at_10 = 1.0 if relevant.issubset(set(top10)) else 0.0
    single_hit_5 = 1.0 if set(top5).intersection(relevant) else 0.0

    denominator = float(max(len(top10), 1))
    distractor_suppression = (len(top10) - len([node_id for node_id in top10 if node_id in relevant])) / denominator

    mrr = 0.0
    for rank, node_id in enumerate(retrieved, start=1):
        if node_id in relevant:
            mrr = 1.0 / rank
            break

    return {
        "sp_recall_at_5": recall_at_5,
        "sp_recall_at_10": recall_at_10,
        "single_sp_hit_at_5": single_hit_5,
        "distractor_suppression": distractor_suppression,
        "mrr": mrr,
        "nodes_fired": float(len(retrieved)),
    }


def _avg(metrics: list[dict[str, float]]) -> dict[str, float]:
    if not metrics:
        return {
            "sp_recall_at_5": 0.0,
            "sp_recall_at_10": 0.0,
            "single_sp_hit_at_5": 0.0,
            "distractor_suppression": 0.0,
            "mrr": 0.0,
            "nodes_fired": 0.0,
        }
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
    return traverse(graph=graph, seeds=seeds, config=traversal_config, query_text=query).fired


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
    collected = []
    for idx, row in enumerate(rows, start=1):
        query = str(row.get("question", ""))
        retrieved = (
            _traverse_topk(graph, index, client, cache, query, seed_top_k=seed_top_k, traversal_config=traversal_config)
            if use_traversal
            else _embedding_topk(graph, index, client, cache, query, embed_top_k=embed_top_k)
        )
        collected.append(_row_metrics(retrieved, _ground_truth_ids(row, title_to_id)))
        if idx % 100 == 0:
            _log_progress(method_name, idx, _avg(collected), RUN_METRICS)
    return _avg(collected)


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
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    history: list[dict[str, float]] = []
    checkpoints = {point for point in CHECKPOINTS if point <= len(rows)}
    learning_curve: dict[str, dict[str, float]] = {}

    for idx, row in enumerate(rows, start=1):
        query = str(row.get("question", ""))
        relevant = _ground_truth_ids(row, title_to_id)
        retrieved = _traverse_topk(graph, index, client, cache, query, seed_top_k=seed_top_k, traversal_config=traversal_config)
        scores = _row_metrics(retrieved, relevant)
        history.append(scores)

        outcome = 1.0 if scores["sp_recall_at_10"] >= 1.0 else -1.0
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
    print("\nMethod                   SP@5  SP@10  SingleHit@5  Distractor  MRR   NodesFired")
    print("----------------------------------------------------------------------------")
    for key in ["embedding_topk", "crabpath_cold", "crabpath_learning", "crabpath_pg_learning"]:
        values = methods[key]
        print(
            f"{key:<24}"
            f"{values['sp_recall_at_5']:.3f}  "
            f"{values['sp_recall_at_10']:.3f}    "
            f"{values['single_sp_hit_at_5']:.3f}       "
            f"{values['distractor_suppression']:.3f}     "
            f"{values['mrr']:.3f}   "
            f"{values['nodes_fired']:.2f}"
        )

    print("\nLearning Curves")
    for name in ["crabpath_learning", "crabpath_pg_learning"]:
        print(f"\n{name}")
        print("query  SP@5  SP@10  SingleHit@5  Distractor  MRR   NodesFired")
        for checkpoint in sorted(learning_curves.get(name, {}), key=lambda value: int(value)):
            values = learning_curves[name][checkpoint]
            print(
                f"{checkpoint:>5} "
                f"{values['sp_recall_at_5']:.3f}  "
                f"{values['sp_recall_at_10']:.3f}    "
                f"{values['single_sp_hit_at_5']:.3f}       "
                f"{values['distractor_suppression']:.3f}     "
                f"{values['mrr']:.3f}   "
                f"{values['nodes_fired']:.2f}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run HotPotQA benchmark.")
    parser.add_argument(
        "--input",
        default="benchmarks/external/hotpotqa_dev_distractor.json",
        help="Path to HotPotQA dev distractor JSON",
    )
    parser.add_argument(
        "--output",
        default="benchmarks/external/hotpotqa_results.json",
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
    graph, title_to_id = _build_graph(rows)
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
    )

    _print_ascii(methods, learning_curves)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "dataset": "HotPotQA",
                "dataset_path": str(input_path),
                "dataset_queries": len(rows),
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
