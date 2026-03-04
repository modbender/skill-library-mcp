#!/usr/bin/env python3
"""
LadybugDB storage for NIMA Memory.
Called from index.js via execFileSync.

Author: Lilu
Date: 2026-02-15
"""
import sys
import json
import os
import time

# Try importing real_ladybug directly (installed for python3.13 system-wide)
# Avoid injecting venv paths — causes circular import when wrong Python version's
# partially-initialized package gets loaded first
try:
    import real_ladybug as lb
    LADYBUG_AVAILABLE = True
except ImportError:
    # Fallback: try venv paths
    VENV_PATHS = [
        os.path.expanduser("~/.openclaw/workspace/.venv/lib/python3.13/site-packages"),
        os.path.expanduser("~/.openclaw/workspace/.venv/lib/python3.11/site-packages"),
    ]
    LADYBUG_AVAILABLE = False
    for vp in VENV_PATHS:
        if os.path.exists(vp) and vp not in sys.path:
            sys.path.insert(0, vp)
            try:
                import real_ladybug as lb
                LADYBUG_AVAILABLE = True
                break
            except ImportError:
                continue

LADYBUG_DB = os.path.expanduser("~/.nima/memory/ladybug.lbug")
SQLITE_DB = os.path.expanduser(os.environ.get("NIMA_SQLITE_DB",
    os.path.join(os.environ.get("NIMA_HOME", "~/.nima"), "memory", "graph.sqlite")))
MAX_TEXT_LENGTH = 2000
MAX_SUMMARY_LENGTH = 500


def _get_embedding(text: str):
    """Generate Voyage embedding for semantic search. Returns bytes blob or None."""
    api_key = os.environ.get("VOYAGE_API_KEY")
    if not api_key or not text.strip():
        return None
    try:
        import struct
        import voyageai
        client = voyageai.Client(api_key=api_key)
        result = client.embed([text[:2000]], model="voyage-3-lite")
        vec = result.embeddings[0]
        return struct.pack(f'{len(vec)}f', *vec)
    except Exception:
        return None


def _dual_write_sqlite(data: dict, input_id: int, contemplation_id: int, output_id: int):
    """
    Dual-write memory turn to SQLite for FTS + embedding search.
    Non-fatal — LadybugDB is primary, SQLite is supplementary.
    """
    import sqlite3
    
    if not os.path.exists(SQLITE_DB):
        return
    
    conn = sqlite3.connect(SQLITE_DB, timeout=5.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    
        timestamp = data.get("timestamp", int(time.time() * 1000))
        turn_id = data.get("turn_id", f"turn_{timestamp}")
        affect_json = data.get("affect_json", "{}")
        session_key = data.get("session_key", "")
        fe_score = data.get("fe_score", 0.5)
    
        layers = [
            ("input", data["input"], input_id),
            ("contemplation", data["contemplation"], contemplation_id),
            ("output", data["output"], output_id),
        ]
    
        node_ids = []
        for layer, content, ladybug_id in layers:
            text = content.get("text", "")[:MAX_TEXT_LENGTH]
            summary = content.get("summary", "")[:MAX_SUMMARY_LENGTH]
            who = content.get("who", "self") if layer == "input" else "self"
        
            # Generate embedding for output layer (most searchable)
            embedding_blob = _get_embedding(text) if layer == "output" else None
        
            cur = conn.execute(
                """INSERT INTO memory_nodes 
                    (id, timestamp, layer, text, summary, who, affect_json, 
                     session_key, turn_id, fe_score, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ladybug_id, timestamp, layer, text, summary, who,
                 affect_json, session_key, turn_id, fe_score, embedding_blob)
            )
            node_ids.append(cur.lastrowid)
    
        # Create edges
        if len(node_ids) == 3:
            for src, tgt, rel in [
                (node_ids[0], node_ids[1], 'triggered'),
                (node_ids[1], node_ids[2], 'produced'),
                (node_ids[2], node_ids[0], 'responded_to'),
            ]:
                conn.execute(
                    "INSERT INTO memory_edges (source_id, target_id, relation) VALUES (?, ?, ?)",
                    (src, tgt, rel)
                )
    
        # Create turn record
        conn.execute(
            """INSERT OR IGNORE INTO memory_turns 
                (turn_id, input_node_id, contemplation_node_id, output_node_id, timestamp, affect_json)
                VALUES (?, ?, ?, ?, ?, ?)""",
            (turn_id, node_ids[0], node_ids[1], node_ids[2], timestamp, affect_json)
        )
    
        conn.commit()
        print(f"[ladybug_store] SQLite dual-write OK: {node_ids}", file=sys.stderr)
    finally:
        conn.close()


def _open_db_safe(db_path=None, max_retries=2):
    """
    Open LadybugDB with WAL corruption auto-recovery.
    If DB fails due to corrupted WAL, renames the WAL and retries.
    This is the HOT PATH — called on every conversation turn.
    """
    path     = db_path or LADYBUG_DB
    wal_path = path + '.wal'

    for attempt in range(max_retries):
        try:
            db   = lb.Database(path)
            conn = lb.Connection(db)
            try:
                conn.execute("LOAD VECTOR")
            except Exception:
                pass
            return db, conn
        except RuntimeError as e:
            msg = str(e).lower()
            if any(k in msg for k in ('wal', 'corrupted', 'invalid wal')) and os.path.exists(wal_path):
                bak = wal_path + f'.bak_{int(time.time())}'
                os.rename(wal_path, bak)
                print(f"nima-memory: WAL corrupted — auto-recovered (→ {os.path.basename(bak)})",
                      file=sys.stderr)
            else:
                raise

    raise RuntimeError(f"LadybugDB failed to open after {max_retries} recovery attempts: {path}")


def get_next_id(conn) -> int:
    """Get next available node ID."""
    result = conn.execute("MATCH (n:MemoryNode) RETURN max(n.id) as max_id")
    for row in result:
        max_id = row[0]
        return (max_id or 0) + 1
    return 1


def truncate(text: str, max_len: int) -> str:
    """Truncate text to max length."""
    if not text:
        return ""
    return text[:max_len] if len(text) <= max_len else text[:max_len-3] + "..."


def store_memory(data_file: str) -> bool:
    """
    Store memory turn to LadybugDB.
    
    AUDIT FIX 2026-02-16: Added proper transaction rollback (Issue #2)
    
    Args:
        data_file: Path to JSON file with memory data
        
    Returns:
        True if stored successfully
        
    Raises:
        Exception: On failure (error is also printed to stderr)
    """
    if not LADYBUG_AVAILABLE:
        print("error:real_ladybug not installed", file=sys.stderr)
        return False
    
    if not os.path.exists(LADYBUG_DB):
        print(f"error:database not found at {LADYBUG_DB}", file=sys.stderr)
        return False
    
    # AUDIT FIX: Parse JSON with explicit error handling
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"error:invalid JSON in data file: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"error:data file not found: {data_file}", file=sys.stderr)
        return False
    
    db, conn = _open_db_safe(LADYBUG_DB)

    # Track created nodes for potential cleanup
    created_nodes = []
    
    try:
        # Load vector extension if available
        try:
            conn.execute("LOAD VECTOR")
        except:
            pass
        
        # Get next IDs
        base_id = get_next_id(conn)
        input_id = base_id
        contemplation_id = base_id + 1
        output_id = base_id + 2
        
        timestamp = data.get("timestamp", int(time.time() * 1000))
        turn_id = data.get("turn_id", f"turn_{timestamp}")
        affect_json = data.get("affect_json", "{}")
        session_key = data.get("session_key", "")
        conversation_id = data.get("conversation_id", "")
        fe_score = data.get("fe_score", 0.5)
        
        # AUDIT FIX: Track all operations for potential rollback
        # Note: LadybugDB doesn't have native transactions, so we track for cleanup
        
        # Insert input node
        conn.execute("""
            CREATE (n:MemoryNode {
                id: $id,
                timestamp: $timestamp,
                layer: 'input',
                text: $text,
                summary: $summary,
                who: $who,
                affect_json: $affect_json,
                session_key: $session_key,
                conversation_id: $conversation_id,
                turn_id: $turn_id,
                fe_score: $fe_score
            })
        """, {
            "id": input_id,
            "timestamp": timestamp,
            "text": truncate(data["input"]["text"], MAX_TEXT_LENGTH),
            "summary": truncate(data["input"]["summary"], MAX_SUMMARY_LENGTH),
            "who": data["input"].get("who", "unknown"),
            "affect_json": affect_json,
            "session_key": session_key,
            "conversation_id": conversation_id,
            "turn_id": turn_id,
            "fe_score": fe_score
        })
        created_nodes.append(input_id)
        
        # Insert contemplation node
        conn.execute("""
            CREATE (n:MemoryNode {
                id: $id,
                timestamp: $timestamp,
                layer: 'contemplation',
                text: $text,
                summary: $summary,
                who: 'self',
                affect_json: $affect_json,
                session_key: $session_key,
                conversation_id: $conversation_id,
                turn_id: $turn_id,
                fe_score: $fe_score
            })
        """, {
            "id": contemplation_id,
            "timestamp": timestamp,
            "text": truncate(data["contemplation"]["text"], MAX_TEXT_LENGTH),
            "summary": truncate(data["contemplation"]["summary"], MAX_SUMMARY_LENGTH),
            "affect_json": affect_json,
            "session_key": session_key,
            "conversation_id": conversation_id,
            "turn_id": turn_id,
            "fe_score": fe_score
        })
        created_nodes.append(contemplation_id)
        
        # Insert output node
        conn.execute("""
            CREATE (n:MemoryNode {
                id: $id,
                timestamp: $timestamp,
                layer: 'output',
                text: $text,
                summary: $summary,
                who: 'self',
                affect_json: $affect_json,
                session_key: $session_key,
                conversation_id: $conversation_id,
                turn_id: $turn_id,
                fe_score: $fe_score
            })
        """, {
            "id": output_id,
            "timestamp": timestamp,
            "text": truncate(data["output"]["text"], MAX_TEXT_LENGTH),
            "summary": truncate(data["output"]["summary"], MAX_SUMMARY_LENGTH),
            "affect_json": affect_json,
            "session_key": session_key,
            "conversation_id": conversation_id,
            "turn_id": turn_id,
            "fe_score": fe_score
        })
        created_nodes.append(output_id)
        
        # Create edges: input → contemplation → output
        conn.execute("""
            MATCH (a:MemoryNode {id: $source}), (b:MemoryNode {id: $target})
            CREATE (a)-[:relates_to {relation: 'triggered', weight: 1.0}]->(b)
        """, {"source": input_id, "target": contemplation_id})
        
        conn.execute("""
            MATCH (a:MemoryNode {id: $source}), (b:MemoryNode {id: $target})
            CREATE (a)-[:relates_to {relation: 'produced', weight: 1.0}]->(b)
        """, {"source": contemplation_id, "target": output_id})
        
        conn.execute("""
            MATCH (a:MemoryNode {id: $source}), (b:MemoryNode {id: $target})
            CREATE (a)-[:relates_to {relation: 'responded_to', weight: 1.0}]->(b)
        """, {"source": output_id, "target": input_id})
        
        # Create turn (schema: id, turn_id, timestamp, affect_json only)
        conn.execute("""
            CREATE (t:Turn {
                id: $turn_id_int,
                turn_id: $turn_id,
                timestamp: $timestamp,
                affect_json: $affect_json
            })
        """, {
            "turn_id_int": timestamp,  # Use full millisecond timestamp as ID
            "turn_id": turn_id,
            "timestamp": timestamp,
            "affect_json": affect_json
        })
        
        print(f"stored:{input_id},{contemplation_id},{output_id}")
        
        # Dual-write to SQLite for FTS + embedding search
        try:
            _dual_write_sqlite(data, input_id, contemplation_id, output_id)
        except Exception as sqlite_err:
            print(f"[ladybug_store] SQLite dual-write failed (non-fatal): {sqlite_err}", file=sys.stderr)
        
        return True
        
    except Exception as e:
        # AUDIT FIX: Attempt cleanup of partially created nodes (Issue #2)
        print(f"error:{e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        # Try to clean up any nodes that were created before the failure
        if created_nodes:
            print(f"[ladybug_store] Attempting cleanup of {len(created_nodes)} partial nodes...", file=sys.stderr)
            for node_id in created_nodes:
                try:
                    conn.execute("MATCH (n:MemoryNode {id: $id}) DETACH DELETE n", {"id": node_id})
                except Exception as cleanup_err:
                    print(f"[ladybug_store] Cleanup failed for node {node_id}: {cleanup_err}", file=sys.stderr)
        
        return False
    finally:
        try:
            conn.close()
        except:
            pass


def health_check() -> dict:
    """Check LadybugDB health."""
    if not LADYBUG_AVAILABLE:
        return {"ok": False, "error": "real_ladybug not installed"}
    
    if not os.path.exists(LADYBUG_DB):
        return {"ok": False, "error": f"database not found at {LADYBUG_DB}"}
    
    try:
        db, conn = _open_db_safe(LADYBUG_DB)

        result = conn.execute("MATCH (n:MemoryNode) RETURN count(n) as count")
        node_count = 0
        for row in result:
            node_count = row[0]
        
        result = conn.execute("MATCH ()-[r:relates_to]->() RETURN count(r) as count")
        edge_count = 0
        for row in result:
            edge_count = row[0]
        
        conn.close()
        
        return {
            "ok": True,
            "stats": {
                "nodes": node_count,
                "edges": edge_count,
                "db_path": LADYBUG_DB,
                "db_size_mb": round(os.path.getsize(LADYBUG_DB) / (1024 * 1024), 2)
            }
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ladybug_store.py <data_file.json> | health", file=sys.stderr)
        sys.exit(1)
    
    if sys.argv[1] == "health":
        import json
        print(json.dumps(health_check(), indent=2))
        sys.exit(0)
    
    success = store_memory(sys.argv[1])
    sys.exit(0 if success else 1)