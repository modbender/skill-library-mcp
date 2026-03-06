"""Traversal functions for dynamic retrieval over a learned memory graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .graph import Edge, Graph


RouteFn = Callable[[str | None, list[Edge], str], list[str]]


@dataclass
class TraversalConfig:
    """Configuration controlling query-time traversal.

    Attributes:
        max_hops: maximum traversal depth from seed nodes.
        beam_width: maximum frontier size per hop.
        edge_damping: multiplicative decay per reuse
            (``w = w * damping^use_count``). Lower values are more
            aggressive loop prevention. Default ``0.3``.
        fire_threshold: minimum activation score required for a node to fire.
            Default ``0.0``.
        visit_penalty: penalty for revisiting a node in the same traversal.
        inhibitory_threshold: edges with weight <= this value actively suppress
            target nodes. Default ``-0.01``.
        max_context_chars: maximum characters in assembled context; ``None``
            means unlimited.
        reflex_threshold: minimum edge weight for reflex-tier edges.
        habitual_range: inclusive lower/upper bounds for habitual-tier edges.
    """

    max_hops: int = 30
    beam_width: int = 8
    edge_damping: float = 0.3
    fire_threshold: float = 0.01
    visit_penalty: float = 0.0
    inhibitory_threshold: float = -0.01
    max_fired_nodes: int | None = None
    max_context_chars: int | None = None
    reflex_threshold: float = 0.6
    habitual_range: tuple[float, float] = (0.2, 0.6)


@dataclass
class TraversalStep:
    """One transition chosen by traversal."""

    from_node: str
    to_node: str
    edge_weight: float
    effective_weight: float
    tier: str


@dataclass
class TraversalResult:
    """Traversal output used by retrieval and learning."""

    fired: list[str]
    steps: list[TraversalStep]
    context: str
    tier_summary: dict[str, str] = field(default_factory=dict)


def _tier(weight: float, config: TraversalConfig) -> str:
    """ tier."""
    if weight <= config.inhibitory_threshold:
        return "inhibitory"
    if weight >= config.reflex_threshold:
        return "reflex"
    if config.habitual_range[0] <= weight < config.habitual_range[1]:
        return "habitual"
    return "dormant"


def _tier_summary(config: TraversalConfig) -> dict[str, str]:
    """ tier summary."""
    return {
        "reflex": f">= {config.reflex_threshold}",
        "habitual": f"{config.habitual_range[0]} - {config.habitual_range[1]}",
        "dormant": f"< {config.habitual_range[0]}",
        "inhibitory": f"< {config.inhibitory_threshold}",
    }


def _incoming_inhibition(
    graph: Graph,
    node_id: str,
    active_scores: dict[str, float],
    config: TraversalConfig,
) -> float:
    """Calculate inhibitory suppression from incoming negative edges."""
    if not active_scores:
        return 0.0

    total = 0.0
    for source_node, edge in graph.incoming(node_id):
        if source_node.id not in active_scores or edge.weight >= 0:
            continue
        if edge.weight > config.inhibitory_threshold:
            continue
        total += active_scores[source_node.id] * edge.weight
    return total


def _build_context(
    graph: Graph,
    fired_scores: dict[str, float],
    fired: list[str],
    max_chars: int | None,
) -> str:
    """Build textual context from ranked fired nodes."""
    if not fired:
        return ""
    if max_chars is None:
        ordered = sorted(
            ((node_id, fired_scores.get(node_id, 0.0), idx) for idx, node_id in enumerate(fired)),
            key=lambda item: (item[1], -item[2]),
            reverse=True,
        )
        return "\n\n".join(
            graph.get_node(node_id).content
            for node_id, _score, _order in ordered
            if graph.get_node(node_id) is not None
        )

    if max_chars <= 0:
        return ""

    ordered = sorted(
        ((node_id, fired_scores.get(node_id, 0.0), idx) for idx, node_id in enumerate(fired)),
        key=lambda item: (item[1], -item[2]),
        reverse=True,
    )
    chunks: list[str] = []
    used = 0
    for idx, (node_id, _score, _order) in enumerate(ordered):
        node = graph.get_node(node_id)
        if node is None:
            continue

        separator = "\n\n" if chunks else ""
        if used + len(separator) + len(node.content) <= max_chars:
            chunks.append(node.content)
            used += len(separator) + len(node.content)
            continue

        if not chunks:
            chunks.append(node.content[:max_chars])
            used = max_chars
        break

    return "\n\n".join(chunks)


def traverse(
    graph: Graph,
    seeds: list[tuple[str, float]],
    config: TraversalConfig | None = None,
    route_fn: RouteFn | None = None,
    query_text: str | None = None,
) -> TraversalResult:
    """Traverse graph from seed nodes using edge tiers and fatigue damping.

    Edge tiers:
    - reflex (w >= threshold): auto follow.
    - habitual (within range): follow by weight, or by ``route_fn`` when supplied.
    - inhibitory: suppress target activation.
    - dormant: skipped.

    Every directed edge is discounted by ``damping^k`` where ``k`` is how many times
    that edge was used in this traversal episode.

    Args:
    route_fn: callback receives ``(node_id, candidate_edges, context)`` where
    ``candidate_edges`` are graph edges and ``context`` is ``query_text``.
    """
    cfg = config or TraversalConfig()
    if cfg.max_hops <= 0 or cfg.beam_width <= 0:
        return TraversalResult([], [], "")

    valid_seeds = [(node_id, score) for node_id, score in seeds if graph.get_node(node_id)]
    if not valid_seeds:
        return TraversalResult([], [], "")

    seed_scores = {node_id: score for node_id, score in valid_seeds}
    frontier: list[tuple[str, float]] = []
    for node_id, base_score in sorted(valid_seeds, key=lambda item: item[1], reverse=True):
        suppression = _incoming_inhibition(graph, node_id, seed_scores, cfg)
        adjusted_score = base_score + suppression
        if suppression <= cfg.inhibitory_threshold:
            continue
        if adjusted_score < cfg.fire_threshold:
            continue
        frontier.append((node_id, adjusted_score))

    frontier = frontier[: cfg.beam_width]
    if not frontier:
        return TraversalResult([], [], "")

    if cfg.max_fired_nodes is not None:
        frontier = frontier[: cfg.max_fired_nodes]

    seen_counts: dict[str, int] = {node_id: 1 for node_id, _ in frontier}
    fired: list[str] = [node_id for node_id, _ in frontier]
    fired_scores: dict[str, float] = {node_id: score for node_id, score in frontier}
    steps: list[TraversalStep] = []
    used_edges: dict[tuple[str, str], int] = {}
    cumulative_chars = 0
    if cfg.max_context_chars is not None:
        cumulative_chars = sum(
            len(graph.get_node(node_id).content)
            for node_id in fired
            if graph.get_node(node_id) is not None
        )
    if cfg.max_fired_nodes is not None and len(fired) >= cfg.max_fired_nodes:
        context = _build_context(graph=graph, fired_scores=fired_scores, fired=fired, max_chars=cfg.max_context_chars)
        return TraversalResult(fired=fired, steps=steps, context=context)
    if cfg.max_context_chars is not None and cumulative_chars >= cfg.max_context_chars:
        context = _build_context(graph=graph, fired_scores=fired_scores, fired=fired, max_chars=cfg.max_context_chars)
        return TraversalResult(fired=fired, steps=steps, context=context)

    for _ in range(cfg.max_hops):
        if not frontier:
            break

        raw_candidates: list[tuple[str, str, float, float, str]] = []
        habitual_by_source: dict[str, list[tuple[str, str, float, float, str, Edge]]] = {}
        for source_id, source_score in frontier:
            for target_node, edge in graph.outgoing(source_id):
                use_count = used_edges.get((source_id, target_node.id), 0)
                effective = edge.weight * (cfg.edge_damping**use_count)
                if effective <= 0.0:
                    continue

                tier = _tier(edge.weight, cfg)
                if tier in {"dormant", "inhibitory"}:
                    continue

                score = source_score * effective
                inhibition = _incoming_inhibition(graph, target_node.id, dict(fired_scores), cfg)
                if inhibition <= cfg.inhibitory_threshold:
                    continue
                score += inhibition
                if target_node.id in seen_counts:
                    score -= cfg.visit_penalty
                if score < cfg.fire_threshold:
                    continue

                raw_candidates.append((source_id, target_node.id, score, effective, tier))
                if tier == "habitual":
                    habitual_by_source.setdefault(source_id, []).append((source_id, target_node.id, score, effective, tier, edge))

        if not raw_candidates:
            break

        reflexive = [item for item in raw_candidates if item[4] == "reflex"]
        habitual = [item for item in raw_candidates if item[4] == "habitual"]

        selected: list[tuple[str, str, float, float, str]] = []
        if route_fn is not None and habitual:
            for source_id in sorted(habitual_by_source):
                candidates = habitual_by_source[source_id]
                wanted = set(route_fn(source_id, [candidate[-1] for candidate in candidates], query_text or ""))
                selected.extend((s, t, score, effective, tier) for s, t, score, effective, tier, _ in candidates if t in wanted)
            selected.extend(reflexive)
        else:
            selected.extend(sorted(habitual, key=lambda item: item[2], reverse=True))
            selected.extend(sorted(reflexive, key=lambda item: item[2], reverse=True))

        selected = sorted(selected, key=lambda item: item[2], reverse=True)

        next_frontier: list[tuple[str, float]] = []
        target_seen: set[str] = set()
        stop_expanding = False

        for source_id, target_id, score, effective, tier in selected[: cfg.beam_width]:
            if target_id in target_seen:
                continue

            edge = graph._edges.get(source_id, {}).get(target_id)
            if edge is None:
                continue

            target_seen.add(target_id)
            if target_id not in seen_counts:
                seen_counts[target_id] = 1
                fired.append(target_id)
                if cfg.max_fired_nodes is not None and len(fired) >= cfg.max_fired_nodes:
                    stop_expanding = True
                if cfg.max_context_chars is not None:
                    target_node = graph.get_node(target_id)
                    if target_node is not None:
                        cumulative_chars += len(target_node.content)
                    if cumulative_chars >= cfg.max_context_chars:
                        stop_expanding = True
            else:
                seen_counts[target_id] += 1

            fired_scores[target_id] = max(fired_scores.get(target_id, float("-inf")), score)
            used_edges[(source_id, target_id)] = used_edges.get((source_id, target_id), 0) + 1
            steps.append(
                TraversalStep(
                    from_node=source_id,
                    to_node=target_id,
                    edge_weight=edge.weight,
                    effective_weight=effective,
                    tier=tier,
                )
            )
            next_frontier.append((target_id, score))
            if stop_expanding:
                break

        frontier = next_frontier
        fired_scores.update(next_frontier)
        if stop_expanding:
            break

    context = _build_context(graph=graph, fired_scores=fired_scores, fired=fired, max_chars=cfg.max_context_chars)
    return TraversalResult(fired=fired, steps=steps, context=context, tier_summary=_tier_summary(cfg))
