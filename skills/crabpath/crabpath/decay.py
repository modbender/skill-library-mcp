"""Edge weight decay mechanics."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .graph import Graph


@dataclass
class DecayConfig:
    """Decay control for weights in long-running graphs."""

    half_life: int = 80
    min_weight: float = 0.01


def apply_decay(
    graph: Graph,
    config: DecayConfig | None = None,
    *,
    skip_source_ids: set[str] | None = None,
    source_half_life_scale: Callable[[str], float] | None = None,
) -> int:
    """Apply decay to edge weights with optional source-level authority controls.

    ``skip_source_ids`` prevents decay for edges whose source node ID is included.
    ``source_half_life_scale`` returns a multiplier for the source's decay
    half-life.
    """
    cfg = config or DecayConfig()
    if cfg.half_life <= 0:
        return 0

    base_factor = 0.5 ** (1.0 / cfg.half_life)
    changed = 0

    for source_id, source_edges in graph._edges.items():
        if skip_source_ids is not None and source_id in skip_source_ids:
            continue
        scale = 1.0
        if source_half_life_scale is not None:
            try:
                scale = float(source_half_life_scale(source_id))
            except (TypeError, ValueError):
                scale = 1.0
        if scale <= 0:
            continue

        factor = base_factor if scale == 1 else 0.5 ** (1.0 / (cfg.half_life * scale))
        for edge in source_edges.values():
            old = edge.weight
            new = old * factor
            if abs(new) < cfg.min_weight:
                new = 0.0
            if new != old:
                edge.weight = new
                changed += 1

    return changed
