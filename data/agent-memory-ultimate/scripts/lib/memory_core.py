"""
Cognitive Memory Core — Phases 1-3: Store, Embed, Recall, Consolidate, Associate
SQLite + FTS5 + numpy vector search + association graph
"""
import sqlite3
import json
import struct
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import numpy as np

from . import embedder

log = logging.getLogger("memory_core")

# ---------- paths ----------

def find_workspace() -> Path:
    for p in [
        Path(__file__).parent.parent.parent.parent.parent,  # lib/ -> scripts/ -> agent-memory/ -> skills/ -> workspace
        Path.home() / ".openclaw" / "workspace",
    ]:
        if (p / "AGENTS.md").exists() or (p / "db").exists():
            return p
    return Path.home() / ".openclaw" / "workspace"

WORKSPACE = find_workspace()
DB_PATH = WORKSPACE / "db" / "memory.db"

# ---------- blob helpers ----------

def vec_to_blob(vec: np.ndarray) -> bytes:
    """Pack float32 array to bytes."""
    return vec.astype(np.float32).tobytes()

def blob_to_vec(blob: bytes) -> np.ndarray:
    """Unpack bytes to float32 array."""
    return np.frombuffer(blob, dtype=np.float32)

# ---------- schema ----------

SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content         TEXT NOT NULL,
    memory_type     TEXT DEFAULT 'episodic',
    source          TEXT DEFAULT 'agent',
    importance      REAL DEFAULT 0.5,
    strength        REAL DEFAULT 1.0,
    access_count    INTEGER DEFAULT 0,
    last_accessed   TEXT,
    created_at      TEXT NOT NULL,
    is_deleted      INTEGER DEFAULT 0,
    metadata        TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    content=memories,
    content_rowid=id,
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE OF content ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.id, old.content);
    INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TABLE IF NOT EXISTS memories_vec (
    memory_id   INTEGER PRIMARY KEY REFERENCES memories(id) ON DELETE CASCADE,
    embedding   BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS associations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id   INTEGER NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    target_id   INTEGER NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    edge_type   TEXT NOT NULL DEFAULT 'semantic',
    weight      REAL NOT NULL DEFAULT 0.5,
    created_at  TEXT NOT NULL,
    metadata    TEXT
);

CREATE INDEX IF NOT EXISTS idx_assoc_source ON associations(source_id);
CREATE INDEX IF NOT EXISTS idx_assoc_target ON associations(target_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_assoc_pair ON associations(source_id, target_id, edge_type);

CREATE TABLE IF NOT EXISTS shared_memories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id       INTEGER NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    shared_by       TEXT NOT NULL,
    shared_with     TEXT NOT NULL,
    consent_owner   INTEGER DEFAULT 0,
    consent_target  INTEGER DEFAULT 0,
    sensitivity     REAL DEFAULT 0.5,
    created_at      TEXT NOT NULL,
    revoked_at      TEXT
);

CREATE INDEX IF NOT EXISTS idx_shared_by ON shared_memories(shared_by);
CREATE INDEX IF NOT EXISTS idx_shared_with ON shared_memories(shared_with);

CREATE TABLE IF NOT EXISTS hierarchy (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id   INTEGER NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    parent_id   INTEGER REFERENCES hierarchy(id) ON DELETE SET NULL,
    level       INTEGER NOT NULL DEFAULT 0,
    summary     TEXT,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hierarchy_memory ON hierarchy(memory_id);
CREATE INDEX IF NOT EXISTS idx_hierarchy_parent ON hierarchy(parent_id);
CREATE INDEX IF NOT EXISTS idx_hierarchy_level ON hierarchy(level);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);
"""

# ---------- connection ----------

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

CURRENT_SCHEMA_VERSION = 4

def init_db(conn: sqlite3.Connection):
    """Create schema if not exists. Migrates if needed."""
    conn.executescript(SCHEMA)
    existing = conn.execute("SELECT version FROM schema_version").fetchone()
    if not existing:
        conn.execute(f"INSERT INTO schema_version VALUES ({CURRENT_SCHEMA_VERSION})")
    elif existing['version'] < CURRENT_SCHEMA_VERSION:
        # Migration: v1 → v2 adds associations table (already in SCHEMA via IF NOT EXISTS)
        conn.execute(f"UPDATE schema_version SET version = {CURRENT_SCHEMA_VERSION}")
    conn.commit()
    log.info(f"Database initialized at {DB_PATH} (v{CURRENT_SCHEMA_VERSION})")

# ---------- store ----------

def store(conn: sqlite3.Connection, content: str, memory_type: str = "episodic",
          source: str = "agent", importance: float = 0.5,
          metadata: Optional[dict] = None) -> int:
    """Store a memory with embedding. Returns memory id."""
    now = datetime.utcnow().isoformat() + "Z"
    meta_json = json.dumps(metadata) if metadata else None

    t0 = time.time()
    vec = embedder.embed(content)
    embed_ms = (time.time() - t0) * 1000

    with conn:
        cur = conn.execute(
            """INSERT INTO memories (content, memory_type, source, importance, strength,
               access_count, last_accessed, created_at, is_deleted, metadata)
               VALUES (?, ?, ?, ?, 1.0, 0, ?, ?, 0, ?)""",
            (content, memory_type, source, importance, now, now, meta_json)
        )
        mid = cur.lastrowid
        conn.execute(
            "INSERT INTO memories_vec (memory_id, embedding) VALUES (?, ?)",
            (mid, vec_to_blob(vec))
        )

    total_ms = (time.time() - t0) * 1000
    log.debug(f"Stored memory #{mid} ({embed_ms:.0f}ms embed, {total_ms:.0f}ms total)")
    return mid

# ---------- recall ----------

def _sanitize_fts_query(query: str) -> str:
    """Escape FTS5 special chars by quoting each token."""
    tokens = query.split()
    # Quote each token to avoid FTS5 syntax errors with special chars
    return " ".join(f'"{t}"' for t in tokens if t.strip())

def _fts_search(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[tuple[int, float]]:
    """FTS5 search. Returns list of (memory_id, bm25_score)."""
    safe_query = _sanitize_fts_query(query)
    if not safe_query:
        return []
    rows = conn.execute(
        """SELECT m.id, fts.rank
           FROM memories_fts fts
           JOIN memories m ON m.id = fts.rowid
           WHERE memories_fts MATCH ? AND m.is_deleted = 0
           ORDER BY fts.rank
           LIMIT ?""",
        (safe_query, limit)
    ).fetchall()
    if not rows:
        return []
    # Normalize BM25 scores to 0-1 (BM25 is negative, closer to 0 = better)
    scores = [abs(r['rank']) for r in rows]
    max_s = max(scores) if scores else 1
    return [(r['id'], 1.0 - abs(r['rank']) / (max_s + 1e-8)) for r in rows]

def _vec_search(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[tuple[int, float]]:
    """Vector similarity search. Returns list of (memory_id, cosine_similarity)."""
    query_vec = embedder.embed(query)

    # Load all non-deleted embeddings
    rows = conn.execute(
        """SELECT v.memory_id, v.embedding
           FROM memories_vec v
           JOIN memories m ON m.id = v.memory_id
           WHERE m.is_deleted = 0"""
    ).fetchall()

    if not rows:
        return []

    ids = [r['memory_id'] for r in rows]
    vecs = np.array([blob_to_vec(r['embedding']) for r in rows])

    results = embedder.cosine_search(query_vec, vecs, top_k=limit)
    return [(ids[idx], score) for idx, score in results]

def recall(conn: sqlite3.Connection, query: str, strategy: str = "hybrid",
           limit: int = 10, vec_weight: float = 0.7) -> list[dict]:
    """
    Recall memories matching query.
    strategy: 'hybrid' (default), 'vector', 'keyword'
    Returns list of dicts with memory fields + score.
    """
    t0 = time.time()

    if strategy == "keyword":
        scored = dict(_fts_search(conn, query, limit * 2))
    elif strategy == "vector":
        scored = dict(_vec_search(conn, query, limit * 2))
    else:  # hybrid
        fts_results = dict(_fts_search(conn, query, limit * 2))
        vec_results = dict(_vec_search(conn, query, limit * 2))

        # Merge: all unique IDs
        all_ids = set(fts_results.keys()) | set(vec_results.keys())
        scored = {}
        for mid in all_ids:
            fts_s = fts_results.get(mid, 0.0)
            vec_s = vec_results.get(mid, 0.0)
            scored[mid] = vec_s * vec_weight + fts_s * (1 - vec_weight)

    if not scored:
        return []

    # Sort by score descending
    ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:limit]

    # Fetch full memory objects
    results = []
    for mid, score in ranked:
        row = conn.execute(
            "SELECT * FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        if row:
            d = dict(row)
            d['score'] = round(score, 4)
            results.append(d)
            # Update access count
            conn.execute(
                "UPDATE memories SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
                (datetime.utcnow().isoformat() + "Z", mid)
            )

    conn.commit()
    elapsed = (time.time() - t0) * 1000
    log.debug(f"Recall '{query}' ({strategy}): {len(results)} results in {elapsed:.0f}ms")
    return results

# ---------- forget ----------

def forget(conn: sqlite3.Connection, memory_id: int = None, query: str = None) -> int:
    """Soft-delete memories. Returns count deleted."""
    if memory_id:
        with conn:
            conn.execute("UPDATE memories SET is_deleted = 1 WHERE id = ?", (memory_id,))
        return 1
    elif query:
        matches = recall(conn, query, strategy="hybrid", limit=5)
        with conn:
            for m in matches:
                conn.execute("UPDATE memories SET is_deleted = 1 WHERE id = ?", (m['id'],))
        return len(matches)
    return 0

def hard_delete(conn: sqlite3.Connection, memory_id: int) -> bool:
    """Permanently delete a memory and its embedding. Returns True if deleted."""
    with conn:
        conn.execute("DELETE FROM memories_vec WHERE memory_id = ?", (memory_id,))
        cur = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    return cur.rowcount > 0

# ---------- stats ----------

def stats(conn: sqlite3.Connection) -> dict:
    """Get database statistics."""
    total = conn.execute("SELECT COUNT(*) FROM memories WHERE is_deleted = 0").fetchone()[0]
    deleted = conn.execute("SELECT COUNT(*) FROM memories WHERE is_deleted = 1").fetchone()[0]
    by_type = dict(conn.execute(
        "SELECT memory_type, COUNT(*) FROM memories WHERE is_deleted = 0 GROUP BY memory_type"
    ).fetchall())
    vec_count = conn.execute("SELECT COUNT(*) FROM memories_vec").fetchone()[0]
    db_size_kb = DB_PATH.stat().st_size // 1024 if DB_PATH.exists() else 0

    return {
        "total_active": total,
        "total_deleted": deleted,
        "by_type": by_type,
        "with_embeddings": vec_count,
        "db_size_kb": db_size_kb,
        "db_path": str(DB_PATH),
    }

# ---------- consolidation (Phase 2) ----------

# Decay rates per memory type (per day)
DECAY_RATES = {
    "episodic": 0.92,    # Fast decay — episodes fade
    "semantic": 0.98,    # Slow decay — facts persist
    "procedural": 0.99,  # Very slow — skills are sticky
}

def apply_decay(conn: sqlite3.Connection) -> dict:
    """
    Apply Ebbinghaus-inspired strength decay based on memory type and time since last access.
    Soft-deletes memories that fall below threshold (0.1).
    Returns dict with counts: {decayed, deleted, unchanged}.
    """
    now = datetime.utcnow()
    rows = conn.execute(
        "SELECT id, memory_type, strength, last_accessed, access_count FROM memories WHERE is_deleted = 0"
    ).fetchall()

    decayed = 0
    deleted = 0
    unchanged = 0

    for row in rows:
        mid = row['id']
        mtype = row['memory_type']
        strength = row['strength']
        last_acc = datetime.fromisoformat(row['last_accessed'].replace('Z', ''))
        access_count = row['access_count']

        days_since = max((now - last_acc).total_seconds() / 86400, 0)
        if days_since < 0.01:  # Accessed very recently
            unchanged += 1
            continue

        base_rate = DECAY_RATES.get(mtype, 0.95)
        # Access count provides resistance to decay (rehearsal effect)
        rehearsal_bonus = min(access_count * 0.005, 0.04)  # max +0.04
        effective_rate = min(base_rate + rehearsal_bonus, 0.999)

        new_strength = strength * (effective_rate ** days_since)
        new_strength = round(new_strength, 6)

        if new_strength < 0.1:
            # Soft-delete faded memories
            conn.execute("UPDATE memories SET is_deleted = 1, strength = ? WHERE id = ?",
                        (new_strength, mid))
            deleted += 1
        elif abs(new_strength - strength) > 0.001:
            conn.execute("UPDATE memories SET strength = ? WHERE id = ?",
                        (new_strength, mid))
            decayed += 1
        else:
            unchanged += 1

    conn.commit()
    return {"decayed": decayed, "deleted": deleted, "unchanged": unchanged}


def cluster_memories(conn: sqlite3.Connection, days: int = 1, threshold: float = 0.5) -> list[list[int]]:
    """
    Cluster recent memories by semantic similarity using agglomerative clustering.
    Returns list of clusters (each cluster = list of memory IDs).
    Only clusters with 2+ members are returned.
    """
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import pdist

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    rows = conn.execute(
        """SELECT m.id, v.embedding FROM memories m
           JOIN memories_vec v ON v.memory_id = m.id
           WHERE m.is_deleted = 0 AND m.created_at >= ?""",
        (cutoff,)
    ).fetchall()

    if len(rows) < 2:
        return []

    ids = [r['id'] for r in rows]
    vecs = np.array([blob_to_vec(r['embedding']) for r in rows])

    # Cosine distance matrix
    dists = pdist(vecs, metric='cosine')
    # Agglomerative clustering
    Z = linkage(dists, method='average')
    labels = fcluster(Z, t=threshold, criterion='distance')

    # Group by cluster label
    from collections import defaultdict
    groups = defaultdict(list)
    for mid, label in zip(ids, labels):
        groups[label].append(mid)

    # Only return clusters with 2+ members
    return [mids for mids in groups.values() if len(mids) >= 2]


def get_memories_by_ids(conn: sqlite3.Connection, ids: list[int]) -> list[dict]:
    """Fetch full memory records by IDs."""
    if not ids:
        return []
    placeholders = ",".join("?" * len(ids))
    rows = conn.execute(
        f"SELECT * FROM memories WHERE id IN ({placeholders})", ids
    ).fetchall()
    return [dict(r) for r in rows]


def consolidate(conn: sqlite3.Connection, days: int = 1) -> dict:
    """
    Full consolidation pass:
    1. Apply decay
    2. Cluster recent memories
    3. Generate cluster summaries (stored as new semantic memories)
    Returns stats dict.
    """
    t0 = time.time()

    # Step 1: Decay
    decay_stats = apply_decay(conn)

    # Step 2: Cluster
    clusters = cluster_memories(conn, days=days)

    # Step 3: Summarize clusters
    summaries_created = 0
    for cluster_ids in clusters:
        memories = get_memories_by_ids(conn, cluster_ids)
        if not memories:
            continue

        # Build summary from cluster contents
        contents = [m['content'] for m in memories]

        # Simple extractive summary: take the most important memory as representative
        # + combine key content. (LLM summary would be Phase 2.5 upgrade)
        best = max(memories, key=lambda m: m.get('importance', 0.5))
        if len(contents) > 1:
            # Create a consolidated summary
            summary_parts = []
            for c in contents:
                # Take first 100 chars of each
                short = c[:100].strip()
                if short and short not in summary_parts:
                    summary_parts.append(short)
            summary = f"[Cluster of {len(contents)} related memories] " + " | ".join(summary_parts[:5])

            # Calculate cluster importance (max of members)
            cluster_importance = max(m.get('importance', 0.5) for m in memories)

            # Store as new level-1 summary memory
            mid = store(conn, summary,
                       memory_type="semantic",
                       source="consolidation",
                       importance=min(cluster_importance + 0.1, 1.0),
                       metadata={"cluster_members": cluster_ids, "level": 1})
            summaries_created += 1

    # Step 4: Build associations within clusters
    associations_created = 0
    for cluster_ids in clusters:
        associations_created += build_cluster_associations(conn, cluster_ids)

    elapsed = (time.time() - t0) * 1000
    return {
        "decay": decay_stats,
        "clusters_found": len(clusters),
        "summaries_created": summaries_created,
        "associations_created": associations_created,
        "elapsed_ms": round(elapsed),
    }

# ---------- associations (Phase 3) ----------

def associate(conn: sqlite3.Connection, source_id: int, target_id: int,
              edge_type: str = "semantic", weight: float = 0.5,
              metadata: dict = None) -> Optional[int]:
    """Create or update an association between two memories. Returns assoc id."""
    now = datetime.utcnow().isoformat() + "Z"
    meta_str = json.dumps(metadata) if metadata else None
    try:
        cur = conn.execute(
            """INSERT INTO associations (source_id, target_id, edge_type, weight, created_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(source_id, target_id, edge_type)
               DO UPDATE SET weight = MAX(weight, excluded.weight)""",
            (source_id, target_id, edge_type, weight, now, meta_str)
        )
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        log.warning(f"Failed to create association {source_id}->{target_id}: {e}")
        return None


def build_cluster_associations(conn: sqlite3.Connection, cluster_ids: list[int]) -> int:
    """Create semantic associations between all memories in a cluster."""
    if len(cluster_ids) < 2:
        return 0

    # Load embeddings for similarity-based weight
    rows = conn.execute(
        f"SELECT memory_id, embedding FROM memories_vec WHERE memory_id IN ({','.join('?' * len(cluster_ids))})",
        cluster_ids
    ).fetchall()

    vecs = {r['memory_id']: blob_to_vec(r['embedding']) for r in rows}
    created = 0

    for i, id_a in enumerate(cluster_ids):
        for id_b in cluster_ids[i+1:]:
            if id_a in vecs and id_b in vecs:
                sim = float(np.dot(vecs[id_a], vecs[id_b]) /
                           (np.linalg.norm(vecs[id_a]) * np.linalg.norm(vecs[id_b]) + 1e-8))
                weight = max(sim, 0.1)  # Floor at 0.1
            else:
                weight = 0.3  # Default if no embedding

            if associate(conn, id_a, id_b, "semantic", weight):
                created += 1
            # Bidirectional
            if associate(conn, id_b, id_a, "semantic", weight):
                created += 1

    return created


def build_temporal_associations(conn: sqlite3.Connection, window_minutes: int = 30) -> int:
    """Create temporal associations between memories created close in time."""
    rows = conn.execute(
        "SELECT id, created_at FROM memories WHERE is_deleted = 0 ORDER BY created_at"
    ).fetchall()

    created = 0
    for i in range(len(rows)):
        t_i = datetime.fromisoformat(rows[i]['created_at'].replace('Z', ''))
        for j in range(i + 1, len(rows)):
            t_j = datetime.fromisoformat(rows[j]['created_at'].replace('Z', ''))
            diff_min = abs((t_j - t_i).total_seconds()) / 60
            if diff_min > window_minutes:
                break
            # Weight inversely proportional to time gap
            weight = round(1.0 - (diff_min / window_minutes), 3)
            if associate(conn, rows[i]['id'], rows[j]['id'], "temporal", weight):
                created += 1
            if associate(conn, rows[j]['id'], rows[i]['id'], "temporal", weight):
                created += 1

    return created


def get_associations(conn: sqlite3.Connection, memory_id: int,
                     edge_type: str = None, direction: str = "both") -> list[dict]:
    """Get all associations for a memory. direction: 'out', 'in', or 'both'."""
    results = []

    if direction in ("out", "both"):
        q = "SELECT a.*, m.content as target_content FROM associations a JOIN memories m ON m.id = a.target_id WHERE a.source_id = ?"
        params = [memory_id]
        if edge_type:
            q += " AND a.edge_type = ?"
            params.append(edge_type)
        results.extend([dict(r) for r in conn.execute(q, params).fetchall()])

    if direction in ("in", "both"):
        q = "SELECT a.*, m.content as source_content FROM associations a JOIN memories m ON m.id = a.source_id WHERE a.target_id = ?"
        params = [memory_id]
        if edge_type:
            q += " AND a.edge_type = ?"
            params.append(edge_type)
        results.extend([dict(r) for r in conn.execute(q, params).fetchall()])

    return sorted(results, key=lambda x: x.get('weight', 0), reverse=True)


def recall_associated(conn: sqlite3.Connection, query: str, hops: int = 1,
                      limit: int = 10) -> list[dict]:
    """
    Multi-hop retrieval: recall matching memories, then follow associations.
    Returns direct matches + associated memories with hop distance.
    """
    # Get direct matches
    direct = recall(conn, query, strategy="hybrid", limit=limit)
    if not direct or hops < 1:
        return direct

    seen = {m['id'] for m in direct}
    for m in direct:
        m['hop'] = 0

    # Follow associations for each hop
    frontier = [m['id'] for m in direct]
    all_results = list(direct)

    for hop in range(1, hops + 1):
        next_frontier = []
        for mid in frontier:
            assocs = get_associations(conn, mid)
            for a in assocs:
                # Get the OTHER end
                other_id = a['target_id'] if a['source_id'] == mid else a['source_id']
                if other_id in seen:
                    continue
                seen.add(other_id)
                row = conn.execute("SELECT * FROM memories WHERE id = ? AND is_deleted = 0",
                                  (other_id,)).fetchone()
                if row:
                    d = dict(row)
                    d['score'] = round(a['weight'] * (0.7 ** hop), 4)  # Decay score by hop
                    d['hop'] = hop
                    d['via_edge'] = a['edge_type']
                    all_results.append(d)
                    next_frontier.append(other_id)

        frontier = next_frontier
        if not frontier:
            break

    # Sort: direct matches first (hop=0), then by score descending
    all_results.sort(key=lambda x: (x.get('hop', 0), -x.get('score', 0)))
    return all_results[:limit]


def association_stats(conn: sqlite3.Connection) -> dict:
    """Get association graph statistics."""
    total = conn.execute("SELECT COUNT(*) FROM associations").fetchone()[0]
    by_type = dict(conn.execute(
        "SELECT edge_type, COUNT(*) FROM associations GROUP BY edge_type"
    ).fetchall())
    avg_weight = conn.execute("SELECT AVG(weight) FROM associations").fetchone()[0] or 0
    unique_memories = conn.execute(
        "SELECT COUNT(DISTINCT id) FROM (SELECT source_id as id FROM associations UNION SELECT target_id FROM associations)"
    ).fetchone()[0]
    return {
        "total_edges": total,
        "by_type": by_type,
        "avg_weight": round(avg_weight, 3),
        "connected_memories": unique_memories,
    }

# ---------- hierarchy (Phase 4) ----------

def build_hierarchy(conn: sqlite3.Connection, max_level: int = 3) -> dict:
    """
    Build RAPTOR-style multi-level hierarchy bottom-up.
    Level 0: raw memories
    Level 1: daily/topic clusters (small groups)
    Level 2: theme clusters (medium groups)
    Level 3: domain summaries (broad groups)
    Returns stats dict.
    """
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import pdist

    t0 = time.time()
    now = datetime.utcnow().isoformat() + "Z"

    # Clear existing hierarchy
    conn.execute("DELETE FROM hierarchy")

    # Level 0: all active memories
    rows = conn.execute(
        """SELECT m.id, v.embedding FROM memories m
           JOIN memories_vec v ON v.memory_id = m.id
           WHERE m.is_deleted = 0"""
    ).fetchall()

    if len(rows) < 2:
        conn.commit()
        return {"levels": 0, "nodes": 0, "elapsed_ms": 0}

    ids = [r['id'] for r in rows]
    vecs = np.array([blob_to_vec(r['embedding']) for r in rows])

    # Insert level-0 nodes
    level_0_hids = {}
    for mid in ids:
        cur = conn.execute(
            "INSERT INTO hierarchy (memory_id, level, created_at) VALUES (?, 0, ?)",
            (mid, now)
        )
        level_0_hids[mid] = cur.lastrowid

    # Distance matrix (compute once, reuse)
    dists = pdist(vecs, metric='cosine')

    total_nodes = len(ids)
    thresholds = [0.4, 0.6, 0.8]  # Tighter → broader clustering per level

    current_ids = list(ids)
    current_vecs = vecs.copy()
    current_hids = dict(level_0_hids)  # memory_id → hierarchy_id

    for level in range(1, min(max_level, len(thresholds)) + 1):
        if len(current_vecs) < 2:
            break

        level_dists = pdist(current_vecs, metric='cosine')
        Z = linkage(level_dists, method='average')
        labels = fcluster(Z, t=thresholds[level - 1], criterion='distance')

        from collections import defaultdict
        groups = defaultdict(list)
        for idx, label in enumerate(labels):
            groups[label].append(idx)

        # Filter to clusters with 2+ members
        clusters = {k: v for k, v in groups.items() if len(v) >= 2}
        if not clusters:
            break

        next_ids = []
        next_vecs = []
        next_hids = {}

        for cluster_indices in clusters.values():
            member_ids = [current_ids[i] for i in cluster_indices]
            member_vecs = current_vecs[cluster_indices]

            # Centroid = mean of member embeddings
            centroid = member_vecs.mean(axis=0)
            centroid = centroid / (np.linalg.norm(centroid) + 1e-8)

            # Build summary text
            member_contents = []
            for mid in member_ids:
                row = conn.execute("SELECT content FROM memories WHERE id = ?", (mid,)).fetchone()
                if row:
                    member_contents.append(row['content'][:80])

            summary = f"[L{level} summary of {len(member_ids)} memories] " + " | ".join(member_contents[:4])

            # Store as new memory
            summary_mid = store(conn, summary,
                               memory_type="semantic",
                               source="hierarchy",
                               importance=0.6 + level * 0.1,
                               metadata={"level": level, "member_count": len(member_ids)})

            # Store centroid embedding
            conn.execute(
                "INSERT OR REPLACE INTO memories_vec (memory_id, embedding) VALUES (?, ?)",
                (summary_mid, vec_to_blob(centroid))
            )

            # Insert hierarchy node
            cur = conn.execute(
                "INSERT INTO hierarchy (memory_id, level, summary, created_at) VALUES (?, ?, ?, ?)",
                (summary_mid, level, summary[:200], now)
            )
            parent_hid = cur.lastrowid

            # Link children to parent
            for mid in member_ids:
                child_hid = current_hids.get(mid)
                if child_hid:
                    conn.execute("UPDATE hierarchy SET parent_id = ? WHERE id = ?",
                                (parent_hid, child_hid))

            next_ids.append(summary_mid)
            next_vecs.append(centroid)
            next_hids[summary_mid] = parent_hid
            total_nodes += 1

        # Singletons carry forward
        assigned = set()
        for indices in clusters.values():
            assigned.update(indices)
        for idx in range(len(current_ids)):
            if idx not in assigned:
                next_ids.append(current_ids[idx])
                next_vecs.append(current_vecs[idx])
                next_hids[current_ids[idx]] = current_hids[current_ids[idx]]

        current_ids = next_ids
        current_vecs = np.array(next_vecs) if next_vecs else np.array([])
        current_hids = next_hids

    conn.commit()
    elapsed = (time.time() - t0) * 1000

    # Get level counts
    level_counts = dict(conn.execute(
        "SELECT level, COUNT(*) FROM hierarchy GROUP BY level"
    ).fetchall())

    return {
        "total_nodes": total_nodes,
        "by_level": level_counts,
        "elapsed_ms": round(elapsed),
    }


def recall_adaptive(conn: sqlite3.Connection, query: str,
                    detail_level: str = "auto", limit: int = 10) -> list[dict]:
    """
    Adaptive retrieval: start at high level, drill down for specific queries.
    detail_level: 'auto', 'broad', 'specific', or int (0-3)
    """
    if detail_level == "broad":
        target_level = 2
    elif detail_level == "specific":
        target_level = 0
    elif detail_level == "auto":
        # Heuristic: short/vague queries → high level, specific → low level
        words = query.split()
        has_specifics = any(w.isdigit() or len(w) > 8 for w in words)
        has_names = any(w[0].isupper() for w in words if w)
        if len(words) <= 3 and not has_specifics:
            target_level = 2  # Broad
        elif has_specifics or has_names or len(words) > 6:
            target_level = 0  # Specific
        else:
            target_level = 1  # Medium
    else:
        target_level = int(detail_level)

    # Get memories at target level from hierarchy
    hier_rows = conn.execute(
        "SELECT memory_id FROM hierarchy WHERE level = ?", (target_level,)
    ).fetchall()

    if not hier_rows:
        # Fallback to standard recall
        return recall(conn, query, strategy="hybrid", limit=limit)

    target_ids = [r['memory_id'] for r in hier_rows]

    # Vector search within the target level
    query_vec = embedder.embed(query)
    rows = conn.execute(
        f"SELECT memory_id, embedding FROM memories_vec WHERE memory_id IN ({','.join('?' * len(target_ids))})",
        target_ids
    ).fetchall()

    if not rows:
        return recall(conn, query, strategy="hybrid", limit=limit)

    ids = [r['memory_id'] for r in rows]
    vecs = np.array([blob_to_vec(r['embedding']) for r in rows])
    results_idx = embedder.cosine_search(query_vec, vecs, top_k=limit)

    results = []
    for idx, score in results_idx:
        mid = ids[idx]
        row = conn.execute("SELECT * FROM memories WHERE id = ?", (mid,)).fetchone()
        if row:
            d = dict(row)
            d['score'] = round(float(score), 4)
            d['hierarchy_level'] = target_level
            results.append(d)

    return results


def hierarchy_stats(conn: sqlite3.Connection) -> dict:
    """Get hierarchy statistics."""
    level_counts = dict(conn.execute(
        "SELECT level, COUNT(*) FROM hierarchy GROUP BY level"
    ).fetchall())
    total = conn.execute("SELECT COUNT(*) FROM hierarchy").fetchone()[0]
    roots = conn.execute("SELECT COUNT(*) FROM hierarchy WHERE parent_id IS NULL AND level > 0").fetchone()[0]
    return {
        "total_nodes": total,
        "by_level": level_counts,
        "root_summaries": roots,
    }

# ---------- spreading activation (Phase 5) ----------

def spreading_activation(conn: sqlite3.Connection, seed_ids: list[int],
                         iterations: int = 3, decay: float = 0.7,
                         max_activated: int = 20) -> dict[int, float]:
    """
    Neural-inspired spreading activation through the memory graph.
    Returns dict of memory_id → activation_level.
    Includes lateral inhibition: competing clusters suppress each other.
    """
    # Initialize activation from seeds
    activation = {mid: 1.0 for mid in seed_ids}

    for iteration in range(iterations):
        new_activation = dict(activation)

        for mid, act_level in activation.items():
            if act_level < 0.05:  # Below threshold, skip
                continue

            # Get outbound associations
            assocs = conn.execute(
                "SELECT target_id, weight, edge_type FROM associations WHERE source_id = ?",
                (mid,)
            ).fetchall()

            for a in assocs:
                target = a['target_id']
                weight = a['weight']
                # Edge type weighting
                type_mult = {"semantic": 1.0, "temporal": 0.5, "explicit": 1.2, "causal": 1.5}.get(a['edge_type'], 0.8)
                spread = act_level * weight * type_mult * decay
                new_activation[target] = max(new_activation.get(target, 0), spread)

        activation = new_activation

    # Lateral inhibition: for each memory, reduce activation if competing with
    # strongly activated neighbors (prevents flooding)
    inhibited = {}
    for mid, act in activation.items():
        neighbors = conn.execute(
            "SELECT target_id FROM associations WHERE source_id = ? AND target_id != ?",
            (mid, mid)
        ).fetchall()
        neighbor_acts = [activation.get(n['target_id'], 0) for n in neighbors]
        if neighbor_acts:
            max_neighbor = max(neighbor_acts)
            # If a neighbor is much stronger, suppress this one
            if max_neighbor > act * 2:
                inhibited[mid] = act * 0.5
            else:
                inhibited[mid] = act
        else:
            inhibited[mid] = act

    # Sort by activation, limit
    sorted_acts = sorted(inhibited.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_acts[:max_activated])


def primed_recall(conn: sqlite3.Connection, query: str,
                  context: list[str] = None, limit: int = 10) -> list[dict]:
    """
    Context-primed recall: use conversation context to boost related memories.
    1. Recall based on query
    2. If context provided, also recall from context terms
    3. Spread activation from both sets
    4. Return top activated memories
    """
    t0 = time.time()

    # Get direct matches
    direct = recall(conn, query, strategy="hybrid", limit=limit)
    seed_ids = [m['id'] for m in direct]

    # If context provided, add context-primed seeds
    if context:
        context_text = " ".join(context[-3:])  # Last 3 context items
        context_matches = recall(conn, context_text, strategy="vector", limit=5)
        for m in context_matches:
            if m['id'] not in seed_ids:
                seed_ids.append(m['id'])

    if not seed_ids:
        return direct

    # Spread activation
    activated = spreading_activation(conn, seed_ids, iterations=2, decay=0.6)

    # Merge direct scores with activation
    results = {}
    for m in direct:
        results[m['id']] = m
        m['activation'] = activated.get(m['id'], 0)
        m['final_score'] = m.get('score', 0) * 0.6 + m.get('activation', 0) * 0.4

    # Add highly activated memories not in direct results
    for mid, act in activated.items():
        if mid not in results and act > 0.3:
            row = conn.execute("SELECT * FROM memories WHERE id = ? AND is_deleted = 0",
                              (mid,)).fetchone()
            if row:
                d = dict(row)
                d['score'] = 0
                d['activation'] = act
                d['final_score'] = act * 0.4
                d['via'] = 'activation'
                results[mid] = d

    sorted_results = sorted(results.values(), key=lambda x: x.get('final_score', 0), reverse=True)

    elapsed = (time.time() - t0) * 1000
    log.debug(f"Primed recall '{query}': {len(sorted_results)} results in {elapsed:.0f}ms")
    return sorted_results[:limit]

# ---------- cross-agent sharing (Phase 6) ----------

# Sensitivity defaults by memory type
SENSITIVITY_DEFAULTS = {
    "episodic": 0.9,    # High sensitivity — personal experiences
    "semantic": 0.3,    # Low sensitivity — factual knowledge
    "procedural": 0.2,  # Very low — skills/procedures are generally safe
}

def sensitivity_gate(memory: dict, threshold: float = 0.5) -> bool:
    """Check if a memory passes the sensitivity gate for sharing."""
    mtype = memory.get('memory_type', 'episodic')
    base = SENSITIVITY_DEFAULTS.get(mtype, 0.5)
    # Importance increases sensitivity (important personal stuff = more sensitive)
    importance = memory.get('importance', 0.5)
    effective = base * (0.5 + importance * 0.5)
    return effective < threshold


def share_memory(conn: sqlite3.Connection, memory_id: int,
                 shared_by: str, shared_with: str,
                 sensitivity_threshold: float = 0.5) -> Optional[int]:
    """
    Share a memory with another agent. Applies sensitivity gate.
    Returns share ID or None if blocked.
    """
    mem = conn.execute("SELECT * FROM memories WHERE id = ? AND is_deleted = 0",
                      (memory_id,)).fetchone()
    if not mem:
        return None

    mem_dict = dict(mem)

    # Sensitivity gate
    if not sensitivity_gate(mem_dict, sensitivity_threshold):
        log.info(f"Memory #{memory_id} blocked by sensitivity gate (type={mem_dict['memory_type']})")
        return None

    # Only semantic and procedural are shareable
    if mem_dict['memory_type'] not in ('semantic', 'procedural'):
        log.info(f"Memory #{memory_id} not shareable (type={mem_dict['memory_type']})")
        return None

    now = datetime.utcnow().isoformat() + "Z"
    sensitivity = SENSITIVITY_DEFAULTS.get(mem_dict['memory_type'], 0.5)

    try:
        cur = conn.execute(
            """INSERT INTO shared_memories
               (memory_id, shared_by, shared_with, consent_owner, sensitivity, created_at)
               VALUES (?, ?, ?, 1, ?, ?)""",
            (memory_id, shared_by, shared_with, sensitivity, now)
        )
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        log.warning(f"Failed to share memory #{memory_id}: {e}")
        return None


def approve_share(conn: sqlite3.Connection, share_id: int) -> bool:
    """Target agent approves a shared memory (dual consent)."""
    conn.execute("UPDATE shared_memories SET consent_target = 1 WHERE id = ?", (share_id,))
    conn.commit()
    return True


def revoke_share(conn: sqlite3.Connection, share_id: int = None,
                 memory_id: int = None) -> int:
    """Revoke sharing. Either by share ID or memory ID (revokes all shares of that memory)."""
    now = datetime.utcnow().isoformat() + "Z"
    if share_id:
        conn.execute("UPDATE shared_memories SET revoked_at = ? WHERE id = ?", (now, share_id))
        conn.commit()
        return 1
    elif memory_id:
        cur = conn.execute(
            "UPDATE shared_memories SET revoked_at = ? WHERE memory_id = ? AND revoked_at IS NULL",
            (now, memory_id)
        )
        conn.commit()
        return cur.rowcount
    return 0


def get_shared(conn: sqlite3.Connection, agent: str = None,
               direction: str = "both", active_only: bool = True) -> list[dict]:
    """Get shared memories for/from an agent."""
    conditions = []
    params = []

    if active_only:
        conditions.append("s.revoked_at IS NULL")
        conditions.append("s.consent_owner = 1")

    if agent and direction == "from":
        conditions.append("s.shared_by = ?")
        params.append(agent)
    elif agent and direction == "to":
        conditions.append("s.shared_with = ?")
        params.append(agent)
    elif agent:
        conditions.append("(s.shared_by = ? OR s.shared_with = ?)")
        params.extend([agent, agent])

    where = " AND ".join(conditions) if conditions else "1=1"
    rows = conn.execute(
        f"""SELECT s.*, m.content, m.memory_type, m.importance
            FROM shared_memories s
            JOIN memories m ON m.id = s.memory_id
            WHERE {where}
            ORDER BY s.created_at DESC""",
        params
    ).fetchall()
    return [dict(r) for r in rows]


def sharing_stats(conn: sqlite3.Connection) -> dict:
    """Get sharing statistics."""
    total = conn.execute("SELECT COUNT(*) FROM shared_memories").fetchone()[0]
    active = conn.execute(
        "SELECT COUNT(*) FROM shared_memories WHERE revoked_at IS NULL"
    ).fetchone()[0]
    consented = conn.execute(
        "SELECT COUNT(*) FROM shared_memories WHERE consent_owner = 1 AND consent_target = 1 AND revoked_at IS NULL"
    ).fetchone()[0]
    by_agent = dict(conn.execute(
        "SELECT shared_with, COUNT(*) FROM shared_memories WHERE revoked_at IS NULL GROUP BY shared_with"
    ).fetchall())
    return {
        "total_shares": total,
        "active": active,
        "fully_consented": consented,
        "by_target_agent": by_agent,
    }
