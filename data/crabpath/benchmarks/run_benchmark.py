from __future__ import annotations

import argparse
import json
import platform
import re
import time
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crabpath import (
    HashEmbedder,
    TraversalConfig,
    VectorIndex,
    apply_outcome,
    apply_outcome_pg,
    split_workspace,
    traverse,
)
from crabpath.replay import default_keyword_seed_fn

WORD_RE = re.compile(r"[A-Za-z0-9']+")


def _tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in WORD_RE.finditer(text or "")}


def _node_file(graph: Any, node_id: str) -> str | None:
    node = graph.get_node(node_id)
    if not node:
        return None
    value = node.metadata.get("file")
    return value if isinstance(value, str) else None


def _rank_to_files(graph: Any, node_ids: list[str], max_files: int | None = None) -> list[str]:
    files: list[str] = []
    seen: set[str] = set()
    for node_id in node_ids if max_files is None else node_ids[:max_files]:
        file = _node_file(graph, node_id)
        if file is None or file in seen:
            continue
        seen.add(file)
        files.append(file)
    return files


def _recall_at_k(predicted: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len([f for f in predicted[:k] if f in relevant]) / len(relevant)


def _precision_at_k(predicted: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    return len([f for f in predicted[:k] if f in relevant]) / k


def _mrr(predicted: list[str], relevant: set[str]) -> float:
    for rank, file_name in enumerate(predicted, start=1):
        if file_name in relevant:
            return 1.0 / rank
    return 0.0


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if q <= 0.0:
        return float(min(values))
    if q >= 1.0:
        return float(max(values))

    ordered = sorted(values)
    index = int((len(ordered) - 1) * q)
    return float(ordered[index])


def _evaluate(ranked_nodes: list[str], graph: Any, relevant: list[str]) -> dict[str, float]:
    relevant_set = set(relevant)
    ranked_files = _rank_to_files(graph, ranked_nodes)
    return {
        "Recall@3": _recall_at_k(ranked_files, relevant_set, 3),
        "Recall@5": _recall_at_k(ranked_files, relevant_set, 5),
        "Precision@3": _precision_at_k(ranked_files, relevant_set, 3),
        "MRR": _mrr(ranked_files, relevant_set),
        "predicted_files": ranked_files[:5],
    }


def _run_query_set(
    name: str,
    queries: list[dict[str, object]],
    graph: Any,
    method: Callable[[str, Any], list[str]],
) -> tuple[dict[str, float], list[dict[str, object]], dict[str, float]]:
    totals = {
        "Recall@3": 0.0,
        "Recall@5": 0.0,
        "Precision@3": 0.0,
        "MRR": 0.0,
    }
    details: list[dict[str, object]] = []
    latencies_ms: list[float] = []

    for row in queries:
        query = str(row.get("query", ""))
        relevant = row.get("relevant")
        relevant_files = list(relevant) if isinstance(relevant, list) else []

        start = time.perf_counter()
        ranked_nodes = method(query, graph)
        latency_ms = (time.perf_counter() - start) * 1000
        scores = _evaluate(ranked_nodes, graph, relevant_files)
        latencies_ms.append(latency_ms)

        for key in totals:
            totals[key] += scores[key]

        details.append(
            {
                "query": query,
                "relevant": relevant_files,
                "predicted_files": scores.pop("predicted_files"),
                "scores": {k: scores[k] for k in totals},
                "latency_ms": latency_ms,
            }
        )

    query_count = len(queries) if queries else 1
    averaged = {key: value / query_count for key, value in totals.items()}
    latency_stats = {
        "p50_ms": _percentile(latencies_ms, 0.50),
        "p95_ms": _percentile(latencies_ms, 0.95),
    }
    return averaged, details, latency_stats


def _extract_fired_path(result: Any, graph: Any) -> list[str]:
    if not result:
        return []
    if result.steps:
        return [result.steps[0].from_node, *[step.to_node for step in result.steps]]

    fired = list(result.fired or [])
    if len(fired) <= 1:
        return fired

    valid: list[str] = []
    for node_id in fired:
        if graph.get_node(node_id) is not None:
            valid.append(node_id)
    return valid


def _run_learning_query_set(
    name: str,
    queries: list[dict[str, object]],
    graph: Any,
    config: TraversalConfig,
    seed_fn: Callable[[Any, str], list[tuple[str, float]]],
    learn_fn: Callable[[Any, list[str]], dict],
) -> tuple[dict[str, float], list[dict[str, object]], dict[str, float], dict[str, dict[str, float]]]:
    totals = {
        "Recall@3": 0.0,
        "Recall@5": 0.0,
        "Precision@3": 0.0,
        "MRR": 0.0,
    }
    details: list[dict[str, object]] = []
    latencies_ms: list[float] = []

    query_count = len(queries)
    checkpoints = [5, 10, 20, query_count] if query_count > 0 else []
    seen: set[int] = set()
    milestones: list[int] = []
    for point in checkpoints:
        if point <= 0:
            continue
        if point in seen:
            continue
        if point > query_count:
            continue
        seen.add(point)
        milestones.append(point)
    learning_curve: dict[str, dict[str, float]] = {}

    for idx, row in enumerate(queries, start=1):
        query = str(row.get("query", ""))
        relevant = row.get("relevant")
        relevant_files = list(relevant) if isinstance(relevant, list) else []
        start = time.perf_counter()
        seeded_nodes = seed_fn(graph, query)
        result = traverse(graph=graph, seeds=seeded_nodes, config=config, query_text=query)
        latency_ms = (time.perf_counter() - start) * 1000

        scores = _evaluate(result.fired, graph, relevant_files)
        latencies_ms.append(latency_ms)
        for key in totals:
            totals[key] += scores[key]
        details.append(
            {
                "query": query,
                "relevant": relevant_files,
                "predicted_files": scores.pop("predicted_files"),
                "scores": {k: scores[k] for k in totals},
                "latency_ms": latency_ms,
            }
        )

        fired_nodes = _extract_fired_path(result, graph)
        learn_fn(graph, fired_nodes)

        if idx in milestones:
            learning_curve[str(idx) if idx != query_count else "N"] = {
                key: value / idx for key, value in totals.items()
            }

    query_count = len(queries) if queries else 1
    averaged = {key: value / query_count for key, value in totals.items()}
    latency_stats = {
        "p50_ms": _percentile(latencies_ms, 0.50),
        "p95_ms": _percentile(latencies_ms, 0.95),
    }
    return averaged, details, latency_stats, learning_curve


def _keyword_overlap(graph: Any, query: str, top_k: int) -> list[str]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []
    scores: list[tuple[str, float]] = []
    for node in graph.nodes():
        node_tokens = _tokenize(node.content)
        overlap = len(query_tokens & node_tokens) / len(query_tokens)
        scores.append((node.id, overlap))
    scores.sort(key=lambda item: (item[1], item[0]), reverse=True)
    return [node_id for node_id, _ in scores[:top_k]]


def _hash_overlap(index: VectorIndex, embedder: HashEmbedder, query: str, top_k: int) -> list[str]:
    query_vec = embedder.embed(query)
    return [node_id for node_id, _ in index.search(query_vec, top_k=top_k)]


def _weighted_hash_seeds(index: VectorIndex, embedder: HashEmbedder, query: str, top_k: int) -> list[tuple[str, float]]:
    seeds = _hash_overlap(index=index, embedder=embedder, query=query, top_k=top_k)
    if not seeds:
        return []
    return [(node_id, 1.0 - 0.05 * idx) for idx, node_id in enumerate(seeds)]


def _keyword_seeds(query: str, graph: Any, top_k: int) -> list[tuple[str, float]]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []
    scores = [
        (node.id, len(query_tokens & _tokenize(node.content)) / len(query_tokens))
        for node in graph.nodes()
    ]
    scores.sort(key=lambda item: (item[1], item[0]), reverse=True)
    return scores[:top_k]


def _traverse(graph: Any, index: VectorIndex, embedder: HashEmbedder, query: str, seed_k: int, config: TraversalConfig) -> list[str]:
    seed_weights = _weighted_hash_seeds(index=index, embedder=embedder, query=query, top_k=seed_k)
    if not seed_weights:
        return []
    result = traverse(graph=graph, seeds=seed_weights, config=config, query_text=query)
    return result.fired


def _build_index(graph: Any, texts: dict[str, str], embedder: HashEmbedder) -> VectorIndex:
    index = VectorIndex()
    for node_id, content in texts.items():
        index.upsert(node_id, embedder.embed(content))
    return index


def _print_table(
    scores_by_method: dict[str, dict[str, float]],
    latency_by_method: dict[str, dict[str, float]],
) -> None:
    print("\nMethod                  Recall@3 Recall@5 Precision@3 MRR    p50_ms p95_ms")
    print("--------------------------------------------------------------")
    for name, scores in scores_by_method.items():
        latency = latency_by_method.get(name, {})
        print(
            f"{name:<22} "
            f"{scores['Recall@3']:.3f}    "
            f"{scores['Recall@5']:.3f}     "
            f"{scores['Precision@3']:.3f}       "
            f"{scores['MRR']:.3f}  "
            f"{latency.get('p50_ms', 0.0):7.3f} "
            f"{latency.get('p95_ms', 0.0):7.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a reproducible CrabPath retrieval benchmark.")
    parser.add_argument("--workspace", default=".", help="Workspace directory to split")
    parser.add_argument("--queries-path", default="benchmarks/queries.json", help="Path to query definitions")
    parser.add_argument("--seed-top-k", type=int, default=20, help="Top-k for keyword overlap")
    parser.add_argument("--hash-top-k", type=int, default=20, help="Top-k for hash similarity search")
    parser.add_argument("--traverse-seed-k", type=int, default=8, help="Seed top-k for traverse")
    parser.add_argument("--traverse-max-hops", type=int, default=8, help="Traverse max_hops")
    parser.add_argument("--traverse-beam-width", type=int, default=4, help="Traverse beam_width")
    parser.add_argument("--replay-max-hops", type=int, default=2, help="Replay traverse max_hops")
    args = parser.parse_args()

    workspace_path = Path(args.workspace).resolve()
    queries_path = Path(args.queries_path)
    if not queries_path.exists():
        raise SystemExit(f"queries file missing: {queries_path}")

    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    if not isinstance(queries, list):
        raise SystemExit("queries.json must contain a list")

    print(f"Splitting workspace: {workspace_path}")
    split_start = time.perf_counter()
    graph, texts = split_workspace(workspace_path)
    split_ms = (time.perf_counter() - split_start) * 1000

    embed_start = time.perf_counter()
    embedder = HashEmbedder()
    index = _build_index(graph, texts, embedder)
    embed_ms = (time.perf_counter() - embed_start) * 1000
    print(f"Graph nodes: {graph.node_count()} | Chunks: {len(texts)}")
    print(f"Init timings: split={split_ms:.3f}ms embed={embed_ms:.3f}ms")
    print("Benchmark timings are machine-dependent and vary by hardware, OS, and runtime conditions.")

    base_graph = graph
    traverse_config = TraversalConfig(max_hops=args.traverse_max_hops, beam_width=args.traverse_beam_width)
    replay_config = TraversalConfig(max_hops=args.replay_max_hops, beam_width=args.traverse_beam_width)
    latency_ms: dict[str, dict[str, float]] = {}
    learning_curves: dict[str, dict[str, dict[str, float]]] = {}

    scores: dict[str, dict[str, float]] = {}
    per_query: dict[str, list[dict[str, object]]] = {}
    weighted_hash_seeds = lambda query_graph, query_text: _weighted_hash_seeds(
        index=index,
        embedder=embedder,
        query=query_text,
        top_k=args.traverse_seed_k,
    )
    keyword_seed = lambda query_graph, query_text: default_keyword_seed_fn(graph=query_graph, query_text=query_text)

    scores["keyword_overlap"], per_query["keyword_overlap"], latency_ms["keyword_overlap"] = _run_query_set(
        name="keyword_overlap",
        queries=queries,
        graph=deepcopy(base_graph),
        method=lambda query, query_graph: _keyword_overlap(graph=query_graph, query=query, top_k=args.seed_top_k),
    )

    scores["hash_embed_similarity"], per_query["hash_embed_similarity"], latency_ms["hash_embed_similarity"] = _run_query_set(
        name="hash_embed_similarity",
        queries=queries,
        graph=deepcopy(base_graph),
        method=lambda query, query_graph: _hash_overlap(index=index, embedder=embedder, query=query, top_k=args.hash_top_k),
    )

    scores["static_traverse"], per_query["static_traverse"], latency_ms["static_traverse"] = _run_query_set(
        name="static_traverse",
        queries=queries,
        graph=deepcopy(base_graph),
        method=lambda query, query_graph: _traverse(
            graph=query_graph,
            index=index,
            embedder=embedder,
            query=query,
            seed_k=args.traverse_seed_k,
            config=traverse_config,
        ),
    )

    scores["crabpath_traverse"], per_query["crabpath_traverse"], latency_ms["crabpath_traverse"], learning_curves["crabpath_traverse"] = _run_learning_query_set(
        name="crabpath_traverse",
        queries=queries,
        graph=deepcopy(base_graph),
        config=traverse_config,
        seed_fn=weighted_hash_seeds,
        learn_fn=lambda learning_graph, fired_nodes: apply_outcome(graph=learning_graph, fired_nodes=fired_nodes, outcome=1.0),
    )

    no_inhibition_config = TraversalConfig(
        max_hops=args.traverse_max_hops,
        beam_width=args.traverse_beam_width,
        inhibitory_threshold=-999,
    )
    scores["crabpath_no_inhibition"], per_query["crabpath_no_inhibition"], latency_ms["crabpath_no_inhibition"], learning_curves["crabpath_no_inhibition"] = _run_learning_query_set(
        name="crabpath_no_inhibition",
        queries=queries,
        graph=deepcopy(base_graph),
        config=no_inhibition_config,
        seed_fn=weighted_hash_seeds,
        learn_fn=lambda learning_graph, fired_nodes: apply_outcome(graph=learning_graph, fired_nodes=fired_nodes, outcome=1.0),
    )

    scores["crabpath_pg"], per_query["crabpath_pg"], latency_ms["crabpath_pg"], learning_curves["crabpath_pg"] = _run_learning_query_set(
        name="crabpath_pg",
        queries=queries,
        graph=deepcopy(base_graph),
        config=traverse_config,
        seed_fn=weighted_hash_seeds,
        learn_fn=lambda learning_graph, fired_nodes: apply_outcome_pg(graph=learning_graph, fired_nodes=fired_nodes, outcome=1.0),
    )

    scores["crabpath_with_replay"], per_query["crabpath_with_replay"], latency_ms["crabpath_with_replay"], learning_curves["crabpath_with_replay"] = _run_learning_query_set(
        name="crabpath_with_replay",
        queries=queries,
        graph=deepcopy(base_graph),
        config=replay_config,
        seed_fn=keyword_seed,
        learn_fn=lambda learning_graph, fired_nodes: apply_outcome(graph=learning_graph, fired_nodes=fired_nodes, outcome=1.0),
    )

    scores["crabpath_pg_with_replay"], per_query["crabpath_pg_with_replay"], latency_ms["crabpath_pg_with_replay"], learning_curves["crabpath_pg_with_replay"] = _run_learning_query_set(
        name="crabpath_pg_with_replay",
        queries=queries,
        graph=deepcopy(base_graph),
        config=replay_config,
        seed_fn=keyword_seed,
        learn_fn=lambda learning_graph, fired_nodes: apply_outcome_pg(graph=learning_graph, fired_nodes=fired_nodes, outcome=1.0),
    )

    _print_table(scores, latency_ms)

    results_path = Path("benchmarks/results.json")
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace_path),
        "query_source": str(queries_path),
        "query_count": len(queries),
        "init_timing_ms": {"split": split_ms, "embed": embed_ms},
        "graph_nodes": graph.node_count(),
        "chunks": len(texts),
        "embedder": embedder.name,
        "embedder_dim": embedder.dim,
        "traversal": {
            "max_hops": args.traverse_max_hops,
            "beam_width": args.traverse_beam_width,
            "seed_k": args.traverse_seed_k,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine_notes": "Benchmarks are timing-sensitive and may vary across machines.",
        },
        "methods": {},
    }

    for method_name, method_scores in scores.items():
        method_latency = latency_ms.get(method_name, {"p50_ms": 0.0, "p95_ms": 0.0})
        output["methods"][method_name] = {
            "scores": method_scores,
            "latency_ms": method_latency,
            "per_query": per_query[method_name],
            "learning_curve": learning_curves.get(method_name, {}),
        }

    results_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Saved: {results_path}")


if __name__ == "__main__":
    main()
