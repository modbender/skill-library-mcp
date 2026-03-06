"""Graph health measurement and simple self-tuning suggestions."""

from __future__ import annotations

from dataclasses import dataclass

from .graph import Graph
from .decay import DecayConfig
from .learn import LearningConfig


@dataclass
class GraphHealth:
    """Readout of graph state for auto-tuning decisions."""

    dormant_pct: float
    habitual_pct: float
    reflex_pct: float
    cross_file_edge_pct: float
    orphan_nodes: int


def measure_health(graph: Graph) -> GraphHealth:
    """Measure aggregate weights and orphan ratio for tuning."""
    total_edges = graph.edge_count()
    if total_edges == 0:
        return GraphHealth(
            dormant_pct=0.0,
            habitual_pct=0.0,
            reflex_pct=0.0,
            cross_file_edge_pct=0.0,
            orphan_nodes=graph.node_count(),
        )

    reflex = habitual = dormant = cross_file = 0
    for source_edges in graph._edges.values():
        source_node = graph.get_node(source_edges and next(iter(source_edges.values())).source)
        source_file = source_node.metadata.get("file") if source_node else None
        for edge in source_edges.values():
            if edge.weight >= 0.6:
                reflex += 1
            elif 0.2 <= edge.weight < 0.6:
                habitual += 1
            else:
                dormant += 1

            target_node = graph.get_node(edge.target)
            target_file = target_node.metadata.get("file") if target_node else None
            if source_file is not None and target_file is not None and source_file != target_file:
                cross_file += 1

    dormant_pct = dormant / total_edges
    habitual_pct = habitual / total_edges
    reflex_pct = reflex / total_edges
    cross_file_edge_pct = cross_file / total_edges

    orphan = 0
    for node in graph.nodes():
        has_out = len(graph.outgoing(node.id)) > 0
        has_in = len(graph.incoming(node.id)) > 0
        if not has_out and not has_in:
            orphan += 1

    return GraphHealth(
        dormant_pct=dormant_pct,
        habitual_pct=habitual_pct,
        reflex_pct=reflex_pct,
        cross_file_edge_pct=cross_file_edge_pct,
        orphan_nodes=orphan,
    )


def autotune(graph: Graph, health: GraphHealth) -> list[dict]:
    """Return suggested adjustments for graph-level health tuning.

    ``graph`` is required because orphan and cross-file statistics come directly
    from structure traversal. ``health`` is a precomputed health snapshot used to
    decide which knobs to adjust.

    Knobs:
    - ``half_life``
    - ``hebbian_increment``
    - ``promotion_threshold``
    """
    deltas: list[dict] = []

    if health.dormant_pct > 0.65:
        deltas.append(
            {
                "knob": "half_life",
                "suggested_adjustment": "decrease",
                "value": 10,
                "reason": "Many dormant edges; slow decay to preserve low-signal paths longer.",
            }
        )
        deltas.append(
            {
                "knob": "promotion_threshold",
                "suggested_adjustment": "decrease",
                "value": 0.05,
                "reason": "Promote more edges from dormant into habitual processing.",
            }
        )

    if health.habitual_pct < 0.2:
        deltas.append(
            {
                "knob": "hebbian_increment",
                "suggested_adjustment": "increase",
                "value": 0.02,
                "reason": "Few habitual pathways; strengthen co-firing structure faster.",
            }
        )

    if health.reflex_pct > 0.8:
        deltas.append(
            {
                "knob": "half_life",
                "suggested_adjustment": "increase",
                "value": 15,
                "reason": "Predominantly reflex traffic; relax decay to avoid over-pruning.",
            }
        )

    if health.orphan_nodes > graph.node_count() * 0.2:
        deltas.append(
            {
                "knob": "promotion_threshold",
                "suggested_adjustment": "decrease",
                "value": 0.02,
                "reason": "Many orphan nodes; lower threshold to reconnect exploration.",
            }
        )

    if health.cross_file_edge_pct < 0.1 and graph.node_count() > 1:
        deltas.append(
            {
                "knob": "promotion_threshold",
                "suggested_adjustment": "decrease",
                "value": 0.05,
                "reason": "Promote more dormant edges and increase cross-file exploration.",
            }
        )

    return deltas


def _clamp_half_life(value: float) -> int:
    """Clamp half-life to a safe range for decay."""
    return max(10, min(500, int(round(value))))


def apply_autotune(
    graph: Graph,
    suggestions: list[dict],
    decay_config: DecayConfig | None = None,
    learning_config: LearningConfig | None = None,
) -> tuple[DecayConfig, LearningConfig]:
    """Apply suggestions and return the resulting tuning configurations."""
    del graph
    decay_cfg = DecayConfig() if decay_config is None else DecayConfig(**decay_config.__dict__)
    learning_cfg = LearningConfig() if learning_config is None else LearningConfig(**learning_config.__dict__)

    for suggestion in suggestions:
        knob = suggestion.get("knob")
        adjustment = suggestion.get("suggested_adjustment")
        value = suggestion.get("value")
        if knob is None or adjustment not in {"increase", "decrease"} or not isinstance(value, (int, float)):
            continue

        delta = value if adjustment == "increase" else -value
        if knob == "half_life":
            decay_cfg = DecayConfig(half_life=_clamp_half_life(decay_cfg.half_life + delta))
        elif knob == "hebbian_increment":
            learning_cfg = LearningConfig(**learning_cfg.__dict__ | {"hebbian_increment": learning_cfg.hebbian_increment + delta})
        elif knob == "promotion_threshold":
            learning_cfg = LearningConfig(
                **learning_cfg.__dict__
                | {"promotion_threshold": max(1, round(learning_cfg.promotion_threshold + delta))}
            )

    return decay_cfg, learning_cfg
