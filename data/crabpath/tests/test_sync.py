from __future__ import annotations

from pathlib import Path

from crabpath import DEFAULT_AUTHORITY_MAP, VectorIndex, load_state, save_state
from crabpath.cli import main
from crabpath.hasher import HashEmbedder, default_embed
from crabpath.graph import Graph
from crabpath.split import split_workspace
from crabpath.sync import sync_workspace


def _write_state(path: Path, graph: Graph, index: VectorIndex) -> None:
    """Persist a graph and index pair with canonical hash defaults."""
    save_state(
        graph=graph,
        index=index,
        path=path,
        embedder_name="hash-v1",
        embedder_dim=HashEmbedder().dim,
    )


def _state_from_workspace(workspace: Path, state_path: Path) -> None:
    """Build state from current workspace and write it to state_path."""
    graph, texts = split_workspace(str(workspace))
    index = VectorIndex()
    for node_id, content in texts.items():
        index.upsert(node_id, default_embed(content))
    _write_state(state_path, graph, index)


def test_sync_detects_new_files(tmp_path: Path) -> None:
    """sync detects new files."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "SOUL.md").write_text("# Soul\nKeep these rules.", encoding="utf-8")

    state_path = tmp_path / "state.json"
    # start from empty state to force adds
    _write_state(state_path, graph=Graph(), index=VectorIndex())

    report = sync_workspace(
        state_path=str(state_path),
        workspace_dir=str(workspace),
        embed_fn=default_embed,
        authority_map=DEFAULT_AUTHORITY_MAP,
    )
    assert report.nodes_added == 1
    assert report.nodes_updated == 0
    assert report.nodes_unchanged == 0
    assert report.embeddings_computed == 1

    graph, index, _ = load_state(str(state_path))
    assert graph.get_node("SOUL.md::0") is not None
    assert index._vectors["SOUL.md::0"] == default_embed("# Soul\nKeep these rules.")


def test_sync_detects_changed_content(tmp_path: Path) -> None:
    """sync detects updated chunks when content changes."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "AGENTS.md"
    source.write_text("# Agents\nOriginal", encoding="utf-8")

    state_path = tmp_path / "state.json"
    _state_from_workspace(workspace, state_path)

    source.write_text("# Agents\nRevised", encoding="utf-8")
    report = sync_workspace(state_path=str(state_path), workspace_dir=str(workspace), embed_fn=default_embed)
    assert report.nodes_added == 0
    assert report.nodes_updated == 1
    assert report.nodes_unchanged == 0
    assert report.embeddings_computed == 1

    graph, _, _ = load_state(str(state_path))
    assert graph.get_node("AGENTS.md::0").content == "# Agents\nRevised"


def test_sync_preserves_unchanged_nodes(tmp_path: Path) -> None:
    """sync does not recompute embeddings for unchanged nodes."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "MEMORY.md").write_text("# Memory\nStable", encoding="utf-8")

    state_path = tmp_path / "state.json"
    _state_from_workspace(workspace, state_path)

    report = sync_workspace(
        state_path=str(state_path),
        workspace_dir=str(workspace),
        embed_fn=default_embed,
    )
    assert report.nodes_added == 0
    assert report.nodes_updated == 0
    assert report.nodes_unchanged == 1
    assert report.embeddings_computed == 0


def test_sync_sets_authority_from_map(tmp_path: Path) -> None:
    """sync sets authority from configured map for mapped source files."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "USER.md").write_text("# User\nIdentity is stable.", encoding="utf-8")

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph=Graph(), index=VectorIndex())

    report = sync_workspace(
        state_path=str(state_path),
        workspace_dir=str(workspace),
        embed_fn=default_embed,
        authority_map=DEFAULT_AUTHORITY_MAP,
    )
    assert report.authority_set["canonical"] == 1

    graph, _, _ = load_state(str(state_path))
    node = graph.get_node("USER.md::0")
    assert node is not None
    assert node.metadata["authority"] == "canonical"


def test_sync_dry_run_doesnt_modify(tmp_path: Path) -> None:
    """sync dry-run does not modify state payload."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "IDENTITY.md"
    source.write_text("# Identity\nA", encoding="utf-8")
    state_path = tmp_path / "state.json"
    _state_from_workspace(workspace, state_path)

    source.write_text("# Identity\nB", encoding="utf-8")
    before = state_path.read_text(encoding="utf-8")

    code = main(
        [
            "sync",
            "--state",
            str(state_path),
            "--workspace",
            str(workspace),
            "--embedder",
            "hash",
            "--dry-run",
            "--json",
        ]
    )
    assert code == 0
    after = state_path.read_text(encoding="utf-8")
    assert before == after

    graph, _, _ = load_state(str(state_path))
    assert graph.get_node("IDENTITY.md::0").content == "# Identity\nA"
