"""Generate PNG figures from all simulation result JSON outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent


def _load(name: str) -> dict[str, Any]:
    path = ROOT / name
    return json.loads(path.read_text(encoding="utf-8"))


def _deploy_pipeline(result: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    history = result["edge_weights_over_time"]
    queries = [item["query"] for item in history]
    edge_keys = ["deploy_query->check_ci", "check_ci->inspect_manifest", "inspect_manifest->rollback", "rollback->verify"]

    for edge_key in edge_keys:
        values = [item["edge_weights"][edge_key] for item in history]
        ax.plot(queries, values, label=edge_key, marker="o")

    ax.set_title("Deploy pipeline: edge strength over queries")
    ax.set_xlabel("query")
    ax.set_ylabel("weight")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "deploy_pipeline.png")
    plt.close(fig)


def _negation(result: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    history = result["weight_history"]
    queries = [item["query"] for item in history]
    good = [item["good_weight"] for item in history]
    bad = [item["bad_weight"] for item in history]

    ax.plot(queries, good, label="run tests", marker="o")
    ax.plot(queries, bad, label="skip tests (deprecated)", marker="o")
    ax.axhline(0.0, linestyle="--", color="black", alpha=0.5)
    ax.set_title("Negation: good vs bad edge weight")
    ax.set_xlabel("query")
    ax.set_ylabel("weight")
    ax.set_ylim(-1.0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "negation.png")
    plt.close(fig)


def _context_reduction(result: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    history = result["nodes_fired_series"]
    queries = [item["query"] for item in history]
    fired = [item["nodes_fired"] for item in history]
    ax.plot(queries, fired, marker="o", linewidth=1.2)
    ax.set_title("Context reduction: nodes fired per query")
    ax.set_xlabel("query")
    ax.set_ylabel("nodes fired")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ROOT / "context_reduction.png")
    plt.close(fig)


def _forgetting(result: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    history = result["tier_history"]
    queries = [item["query"] for item in history]
    dormant = [item["dormant_pct"] for item in history]
    habitual = [item["habitual_pct"] for item in history]
    reflex = [item["reflex_pct"] for item in history]

    ax.stackplot(
        queries,
        dormant,
        habitual,
        reflex,
        labels=["dormant", "habitual", "reflex"],
        colors=["#8c564b", "#1f77b4", "#2ca02c"],
        alpha=0.8,
    )
    ax.set_title("Selective forgetting: edge tier distribution")
    ax.set_xlabel("query")
    ax.set_ylabel("proportion")
    ax.set_ylim(0, 1.0)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(ROOT / "forgetting.png")
    plt.close(fig)


def _edge_damping(result: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    labels = ["damped (0.3)", "undamped (1.0)"]
    reached = [1 if result["damped"]["reached_D"] else 0, 1 if result["undamped"]["reached_D"] else 0]
    colors = ["#2ca02c", "#d62728"]
    ax.bar(labels, reached, color=colors, alpha=0.8)
    ax.set_title("Edge damping: reaches branch D")
    ax.set_ylabel("reached D (1=yes, 0=no)")
    ax.set_ylim(0, 1.1)
    for idx, value in enumerate(reached):
        label = "yes" if value else "no"
        ax.text(idx, value + 0.03, label, ha="center")
    fig.tight_layout()
    fig.savefig(ROOT / "edge_damping.png")
    plt.close(fig)


def _domain_separation(result: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    nodes = sorted(result["nodes"], key=lambda item: (item["file"], item["id"]))
    file_order = ["alpha", "beta", "gamma"]
    colors = {"alpha": "#1f77b4", "beta": "#2ca02c", "gamma": "#ff7f0e"}
    coords = {}
    for file_index, file_name in enumerate(file_order):
        file_nodes = [node["id"] for node in nodes if node["file"] == file_name]
        for position, node_id in enumerate(file_nodes):
            y = -position
            x = file_index * 2
            coords[node_id] = (x, y)
            ax.scatter(x, y, s=140, color=colors[file_name], label=file_name if position == 0 else "")
            ax.text(x + 0.02, y, node_id, fontsize=8)

    for source_id, target_id, weight in result["final_cross_file_edges"]:
        sx, sy = coords[source_id]
        tx, ty = coords[target_id]
        ax.plot([sx, tx], [sy, ty], color="#d62728", linewidth=2.0 + 2.0 * weight, alpha=0.6)

    ax.set_title("Domain separation: clustered files with sparse bridges")
    ax.set_xticks([0, 2, 4])
    ax.set_xticklabels(file_order)
    ax.set_yticks([])
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(-4.5, 0.5)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "domain_separation.png")
    plt.close(fig)


def _brain_death(result: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    rounds = result["rounds"]
    x = [item["round"] for item in rounds]
    dormant = [item["post_health"]["dormant_pct"] for item in rounds]
    habitual = [item["post_health"]["habitual_pct"] for item in rounds]
    reflex = [item["post_health"]["reflex_pct"] for item in rounds]

    ax.plot(x, dormant, label="dormant", linewidth=1.5)
    ax.plot(x, habitual, label="habitual", linewidth=1.5)
    ax.plot(x, reflex, label="reflex", linewidth=1.5)
    ax.set_title("Brain death recovery: health trajectory")
    ax.set_xlabel("round")
    ax.set_ylabel("health percentage")
    ax.set_ylim(0, 1.0)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "brain_death.png")
    plt.close(fig)


def _to_matrix(node_ids: list[str], edges: list[dict[str, Any]]) -> list[list[float]]:
    index = {node_id: i for i, node_id in enumerate(node_ids)}
    size = len(node_ids)
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    for edge in edges:
        source_i = index[edge["source"]]
        target_j = index[edge["target"]]
        matrix[source_i][target_j] = edge["weight"]
    return matrix


def _individuation(result: dict[str, Any]) -> None:
    node_ids = sorted(result["nodes"])
    matrix_a = _to_matrix(node_ids, result["graph_a_edges"])
    matrix_b = _to_matrix(node_ids, result["graph_b_edges"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    im0 = axes[0].imshow(matrix_a, vmin=0.0, vmax=1.0, aspect="auto")
    axes[0].set_title("Graph A (coding)")
    axes[0].set_xlabel("target")
    axes[0].set_ylabel("source")

    im1 = axes[1].imshow(matrix_b, vmin=0.0, vmax=1.0, aspect="auto")
    axes[1].set_title("Graph B (safety)")
    axes[1].set_xlabel("target")
    axes[1].set_ylabel("source")

    fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

    x_idx = list(range(len(node_ids)))
    tick_step = max(1, len(node_ids) // 8)
    ticks = x_idx[::tick_step]
    labels = [node_ids[i] for i in ticks]
    for axis in axes:
        axis.set_xticks(ticks)
        axis.set_xticklabels(labels, rotation=90, fontsize=7)
        axis.set_yticks(ticks)
        axis.set_yticklabels(labels, fontsize=7)

    fig.suptitle("Individuation: final graph matrices", fontsize=12)
    fig.savefig(ROOT / "individuation.png")
    plt.close(fig)


def main() -> None:
    deploy = _load("deploy_pipeline_results.json")
    negation = _load("negation_results.json")
    context = _load("context_reduction_results.json")
    forgetting = _load("forgetting_results.json")
    damping = _load("edge_damping_results.json")
    domains = _load("domain_separation_results.json")
    brain = _load("brain_death_results.json")
    individ = _load("individuation_results.json")

    _deploy_pipeline(deploy)
    _negation(negation)
    _context_reduction(context)
    _forgetting(forgetting)
    _edge_damping(damping)
    _domain_separation(domains)
    _brain_death(brain)
    _individuation(individ)


if __name__ == "__main__":
    main()
