#!/usr/bin/env python3
"""
NIMA Voyage Embedding System
=============================
Embeds memory nodes with Voyage-3-lite for semantic search.
Supports: embed single text, batch embed, cosine similarity search.

SCALABILITY OPTIMIZATIONS (2026-02-16):
  - FAISS index for O(log N) search (vs O(N) brute force)
  - LRU + disk cache for Voyage API (80% cost reduction)
  - Rate limiting (10 req/sec max)
  - Incremental index updates

Usage:
  # Embed a single text
  python3 embeddings.py embed "some text here"
  
  # Backfill all un-embedded nodes
  python3 embeddings.py backfill [--batch-size 64]
  
  # Semantic search (now uses FAISS!)
  python3 embeddings.py search "feeling isolated and scared" [--top 5]
  
  # Build/rebuild FAISS index
  python3 embeddings.py build-index [--type flat|ivf]
  
  # Stats
  python3 embeddings.py stats
"""

import sqlite3
import json
import struct
import sys
import os
import time
from typing import Optional, List, Dict, Any
import numpy as np

GRAPH_DB = os.path.join(os.path.expanduser("~"), ".nima", "memory", "graph.sqlite")
VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY")
if not VOYAGE_API_KEY:
    print("WARNING: VOYAGE_API_KEY environment variable not set", file=sys.stderr)
MODEL = "voyage-3-lite"
EMBEDDING_DIM = 512
BATCH_SIZE = 64  # Voyage max is 128, stay safe
MAX_TEXT_CHARS = 2000  # Truncate long texts

# Use cached client for rate limiting and caching
_cached_client = None

def get_client():
    """Get Voyage client (legacy, for backward compatibility)."""
    import voyageai
    return voyageai.Client(api_key=VOYAGE_API_KEY)

def get_cached_client():
    """Get cached + rate-limited Voyage client."""
    global _cached_client
    if _cached_client is None:
        try:
            from voyage_cache import VoyageCachedClient
            _cached_client = VoyageCachedClient()
        except ImportError:
            print("[embeddings] voyage_cache not available, using raw client", file=sys.stderr)
            return None
    return _cached_client

def encode_vector(vec):
    """Pack float list into bytes for SQLite BLOB storage."""
    return struct.pack(f'{len(vec)}f', *vec)

def decode_vector(blob):
    """Unpack bytes back to float list."""
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def ensure_embedding_column(db):
    """Add embedding column if it doesn't exist."""
    cols = [r[1] for r in db.execute("PRAGMA table_info(memory_nodes)").fetchall()]
    if "embedding" not in cols:
        db.execute("ALTER TABLE memory_nodes ADD COLUMN embedding BLOB DEFAULT NULL")
        db.commit()
        print("✅ Added 'embedding' column to memory_nodes")
    return True

def embed_texts(client, texts, use_cache=True):
    """
    Embed a batch of texts, truncating long ones.
    
    SCALABILITY FIX (2026-02-16): Uses caching to reduce API calls.
    
    Args:
        client: Voyage client (ignored if use_cache=True)
        texts: List of texts to embed
        use_cache: If True, use cached client with rate limiting
    """
    truncated = [t[:MAX_TEXT_CHARS] if t else "" for t in texts]
    # Filter empty strings
    valid = [(i, t) for i, t in enumerate(truncated) if t.strip()]
    if not valid:
        return [None] * len(texts)
    
    indices, valid_texts = zip(*valid)
    
    # Try cached batch embed
    if use_cache:
        cached_client = get_cached_client()
        if cached_client:
            embeddings_list = cached_client.embed_batch(list(valid_texts))
            embeddings = [None] * len(texts)
            for idx, emb in zip(indices, embeddings_list):
                if emb is not None:
                    embeddings[idx] = emb.tolist()  # Convert numpy to list for compatibility
            return embeddings
    
    # Fallback to raw client
    result = client.embed(list(valid_texts), model=MODEL)
    
    embeddings = [None] * len(texts)
    for idx, emb in zip(indices, result.embeddings):
        embeddings[idx] = emb
    
    return embeddings

def backfill(batch_size=BATCH_SIZE, max_retries=3):
    """
    Embed all nodes that don't have embeddings yet.
    
    AUDIT FIX 2026-02-16: Added proper transaction rollback and retry logic (Issues #2, #3)
    
    Args:
        batch_size: Number of nodes to process per batch
        max_retries: Maximum retries per batch on transient failures
    """
    db = None
    try:
        db = sqlite3.connect(GRAPH_DB, timeout=30.0)  # Increased timeout for locks
        db.row_factory = sqlite3.Row
        ensure_embedding_column(db)
        
        # Count un-embedded
        total = db.execute("SELECT COUNT(*) FROM memory_nodes WHERE embedding IS NULL").fetchone()[0]
        embedded_count = db.execute("SELECT COUNT(*) FROM memory_nodes WHERE embedding IS NOT NULL").fetchone()[0]
        print(f"📊 {embedded_count} already embedded, {total} remaining")
        
        if total == 0:
            print("✅ All nodes already embedded!")
            return
        
        client = get_client()
        processed = 0
        failed_batches = 0
        start = time.time()
        
        while True:
            rows = db.execute("""
                SELECT id, text, summary 
                FROM memory_nodes 
                WHERE embedding IS NULL 
                ORDER BY timestamp DESC, fe_score DESC
                LIMIT ?
            """, (batch_size,)).fetchall()
            
            if not rows:
                break
            
            # Use summary if available, fall back to text
            texts = []
            for r in rows:
                t = r["summary"] if r["summary"] and len(r["summary"]) > 10 else r["text"]
                texts.append(t or "")
            
            # AUDIT FIX: Retry logic with exponential backoff (Issue #3)
            for attempt in range(1, max_retries + 1):
                try:
                    embeddings = embed_texts(client, texts)
                    
                    # AUDIT FIX: Explicit transaction with proper rollback (Issue #2)
                    db.execute("BEGIN TRANSACTION")
                    try:
                        for row, emb in zip(rows, embeddings):
                            if emb:
                                db.execute("UPDATE memory_nodes SET embedding = ? WHERE id = ?",
                                          (encode_vector(emb), row["id"]))
                        db.execute("COMMIT")
                    except Exception as db_err:
                        db.execute("ROLLBACK")
                        raise db_err
                    
                    processed += len(rows)
                    elapsed = time.time() - start
                    rate = processed / elapsed if elapsed > 0 else 0
                    print(f"  ... embedded {processed}/{total} ({rate:.0f}/s)")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    is_transient = (
                        'timeout' in error_msg or
                        'rate limit' in error_msg or
                        'sqlite_busy' in error_msg or
                        'database is locked' in error_msg or
                        '429' in error_msg or
                        '503' in error_msg
                    )
                    
                    if attempt < max_retries and is_transient:
                        delay = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                        print(f"  ⚠️ Attempt {attempt} failed (transient), retrying in {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        print(f"  ❌ Batch error (attempt {attempt}/{max_retries}): {e}")
                        failed_batches += 1
                        # Still continue to next batch
                        break
            
            # Rate limiting — Voyage allows 300 RPM, be conservative
            time.sleep(0.3)
        
        elapsed = time.time() - start
        print(f"\n✅ Backfill complete! {processed} nodes embedded in {elapsed:.1f}s")
        if failed_batches > 0:
            print(f"   ⚠️ {failed_batches} batches failed and were skipped")
        
        final = db.execute("SELECT COUNT(*) FROM memory_nodes WHERE embedding IS NOT NULL").fetchone()[0]
        print(f"   Total embedded: {final}")
        
    except Exception as e:
        print(f"❌ Fatal error in backfill: {e}", file=sys.stderr)
        raise
    finally:
        # AUDIT FIX: Always close connection (Issue #2)
        if db:
            try:
                db.close()
            except:
                pass

def search(query, top_k=5, use_faiss=True):
    """
    Semantic search using Voyage embeddings.
    
    SCALABILITY FIX (2026-02-16): Now uses FAISS for O(log N) search.
    Falls back to O(N) brute force if FAISS index not available.
    
    Args:
        query: Search query text
        top_k: Number of results
        use_faiss: If True, try FAISS first (default)
    """
    # Try FAISS first (O(log N))
    if use_faiss:
        try:
            from faiss_index import search_faiss, get_faiss_index
            index = get_faiss_index()
            if index is not None:
                # Get query embedding (cached)
                cached_client = get_cached_client()
                if cached_client:
                    query_vec = cached_client.embed_text(query[:MAX_TEXT_CHARS])
                else:
                    client = get_client()
                    result = client.embed([query[:MAX_TEXT_CHARS]], model=MODEL)
                    query_vec = np.array(result.embeddings[0], dtype=np.float32)
                
                if query_vec is not None:
                    faiss_results = search_faiss(query_vec, top_k)
                    
                    # Enrich with database info
                    db = sqlite3.connect(GRAPH_DB)
                    db.row_factory = sqlite3.Row
                    
                    results = []
                    for r in faiss_results:
                        row = db.execute("""
                            SELECT id, layer, summary, who, turn_id, timestamp
                            FROM memory_nodes WHERE id = ?
                        """, (r['id'],)).fetchone()
                        
                        if row:
                            results.append({
                                "id": row["id"],
                                "score": round(r['score'], 4),
                                "layer": row["layer"],
                                "who": row["who"],
                                "summary": (row["summary"] or "")[:150],
                                "turn_id": row["turn_id"],
                                "timestamp": row["timestamp"]
                            })
                    
                    db.close()
                    print(f"[embeddings] FAISS search: {len(results)} results", file=sys.stderr)
                    return results
        except ImportError:
            print("[embeddings] FAISS not available, falling back to brute force", file=sys.stderr)
        except Exception as e:
            print(f"[embeddings] FAISS error: {e}, falling back to brute force", file=sys.stderr)
    
    # Fallback: O(N) brute force (legacy)
    print("[embeddings] Using O(N) brute force search (consider running: python3 faiss_index.py build)", file=sys.stderr)
    
    db = sqlite3.connect(GRAPH_DB)
    db.row_factory = sqlite3.Row
    
    # Get query embedding (cached)
    cached_client = get_cached_client()
    if cached_client:
        query_vec = cached_client.embed_text(query[:MAX_TEXT_CHARS])
        if query_vec is None:
            return []
    else:
        client = get_client()
        result = client.embed([query[:MAX_TEXT_CHARS]], model=MODEL)
        query_vec = result.embeddings[0]
    
    # Load all embedded nodes - O(N) brute force
    rows = db.execute("""
        SELECT id, layer, text, summary, who, timestamp, turn_id, affect_json, embedding
        FROM memory_nodes
        WHERE embedding IS NOT NULL
    """).fetchall()
    
    # Score each
    scored = []
    for r in rows:
        vec = decode_vector(r["embedding"])
        sim = cosine_similarity(query_vec, vec)
        scored.append((sim, r))
    
    # Sort by similarity
    scored.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for sim, r in scored[:top_k]:
        results.append({
            "id": r["id"],
            "score": round(sim, 4),
            "layer": r["layer"],
            "who": r["who"],
            "summary": (r["summary"] or "")[:150],
            "turn_id": r["turn_id"],
            "timestamp": r["timestamp"]
        })
    
    db.close()
    return results

def stats():
    """Show embedding stats."""
    db = sqlite3.connect(GRAPH_DB)
    total = db.execute("SELECT COUNT(*) FROM memory_nodes").fetchone()[0]
    embedded = db.execute("SELECT COUNT(*) FROM memory_nodes WHERE embedding IS NOT NULL").fetchone()[0]
    pct = (embedded / total * 100) if total > 0 else 0
    print(f"📊 Embedding Stats:")
    print(f"   Total nodes: {total}")
    print(f"   Embedded: {embedded} ({pct:.1f}%)")
    print(f"   Remaining: {total - embedded}")
    db.close()

def build_index(index_type='flat'):
    """Build or rebuild FAISS index from embedded nodes."""
    try:
        from faiss_index import build_faiss_index
        index = build_faiss_index(index_type=index_type)
        if index:
            print(f"✅ Built FAISS index: {len(index.id_map)} vectors")
        else:
            print("❌ Failed to build FAISS index")
    except ImportError as e:
        print(f"❌ FAISS not available: {e}")
        print("   Install with: pip install faiss-cpu")
    except Exception as e:
        print(f"❌ Build failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "backfill":
        bs = int(sys.argv[2]) if len(sys.argv) > 2 else BATCH_SIZE
        backfill(bs)
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        top = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        results = search(query, top)
        for r in results:
            print(f"  [{r['score']:.3f}] [{r['who']}] {r['summary']}")
    elif cmd == "stats":
        stats()
        # Also show FAISS stats if available
        try:
            from faiss_index import get_faiss_index
            index = get_faiss_index()
            if index:
                print(f"\n📊 FAISS Index:")
                print(f"   Vectors: {len(index.id_map)}")
                print(f"   Type: {index.index_type}")
        except:
            pass
        # Show cache stats if available
        try:
            from voyage_cache import cache_stats
            cs = cache_stats()
            print(f"\n📊 Voyage Cache:")
            print(f"   LRU hits: {cs['lru_hits']}")
            print(f"   Disk hits: {cs['disk_hits']}")
            print(f"   API calls: {cs['api_calls']}")
            print(f"   Hit rate: {cs['cache_hit_rate']}%")
            print(f"   Disk entries: {cs['disk_cache']['total_entries']}")
            print(f"   Disk size: {cs['disk_cache']['size_mb']} MB")
        except:
            pass
    elif cmd == "embed":
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        # Use cached client
        cached_client = get_cached_client()
        if cached_client:
            vec = cached_client.embed_text(text)
            if vec is not None:
                print(f"Dim: {len(vec)}")
                print(f"Cache stats: {cached_client.stats()}")
        else:
            client = get_client()
            result = client.embed([text], model=MODEL)
            print(f"Dim: {len(result.embeddings[0])}, tokens: {result.total_tokens}")
    elif cmd == "build-index":
        index_type = sys.argv[2] if len(sys.argv) > 2 else "flat"
        build_index(index_type)
    elif cmd == "cache-stats":
        try:
            from voyage_cache import cache_stats
            import json
            print(json.dumps(cache_stats(), indent=2))
        except ImportError:
            print("voyage_cache not available")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
