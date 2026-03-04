"""CrabPath public API."""

from .graph import Edge, Graph, Node, remove_from_state
from .index import VectorIndex
from ._batch import batch_or_single, batch_or_single_embed
from .autotune import GraphHealth, autotune, measure_health
from .decay import DecayConfig, apply_decay
from .maintain import MaintenanceReport, run_maintenance, prune_edges, prune_orphan_nodes
from .learn import LearningConfig, apply_outcome, apply_outcome_pg, maybe_create_node
from .inject import inject_batch, inject_correction, inject_node
from .hasher import HashEmbedder, default_embed, default_embed_batch
from .score import score_retrieval
from .connect import apply_connections, suggest_connections
from .merge import apply_merge, suggest_merges
from .replay import replay_queries
from .split import generate_summaries, split_workspace
from .sync import DEFAULT_AUTHORITY_MAP, SyncReport, sync_workspace
from .store import ManagedState, load_state, save_state
from .traverse import TraversalResult, TraversalConfig, traverse

__all__ = [
    "Node",
    "Edge",
    "Graph",
    "VectorIndex",
    "GraphHealth",
    "TraversalConfig",
    "TraversalResult",
    "HashEmbedder",
    "default_embed",
    "default_embed_batch",
    "DecayConfig",
    "LearningConfig",
    "MaintenanceReport",
    "measure_health",
    "autotune",
    "prune_edges",
    "prune_orphan_nodes",
    "traverse",
    "ManagedState",
    "split_workspace",
    "generate_summaries",
    "sync_workspace",
    "SyncReport",
    "DEFAULT_AUTHORITY_MAP",
    "apply_outcome",
    "apply_outcome_pg",
    "remove_from_state",
    "maybe_create_node",
    "apply_decay",
    "batch_or_single",
    "batch_or_single_embed",
    "save_state",
    "load_state",
    "score_retrieval",
    "suggest_merges",
    "apply_merge",
    "run_maintenance",
    "suggest_connections",
    "apply_connections",
    "inject_node",
    "inject_correction",
    "inject_batch",
    "replay_queries",
]

__version__ = "10.4.0"
