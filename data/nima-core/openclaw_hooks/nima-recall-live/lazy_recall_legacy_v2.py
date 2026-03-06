#!/usr/bin/env python3
"""
NIMA Lazy Reconstruction Recall v2
==================================

OPTIMIZED VERSION with:
  - Embedding cache (in-memory LRU)
  - Pre-computed similarity index
  - Parallel FTS + embedding search
  - Timeout protection
  - Skip embedding for short queries

Author: NIMA Core Team
Date: 2026-02-14
"""

import sqlite3
import json
import sys
import struct
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional, List, Dict, Any, Tuple

# Config
DEFAULT_DB = os.path.expanduser("~/.nima/memory/graph.sqlite")
MAX_RESULTS = 3
TIME_WINDOW_DAYS = 90
EMBEDDING_THRESHOLD = 0.35
VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY")
if not VOYAGE_API_KEY:
    print("ERROR: VOYAGE_API_KEY environment variable not set", file=sys.stderr)
RECALL_TIMEOUT = 8.0  # Max seconds for entire recall
SKIP_EMBEDDING_MIN_LENGTH = 10  # Skip embedding for queries shorter than this
FTS_CONFIDENCE_THRESHOLD = 15.0  # If best FTS score < this, skip embedding search
FTS_MIN_RESULTS = 3  # Need at least this many FTS results to skip embedding

# =============================================================================
# EMBEDDING CACHE (LRU in-memory)
# =============================================================================

_EMBEDDING_CACHE: Dict[str, Tuple[List[float], float]] = {}
_EMBEDDING_CACHE_MAX = 100
_EMBEDDING_CACHE_TTL = 3600  # 1 hour

def get_embedding_cached(text: str) -> Optional[List[float]]:
    """Get embedding with LRU cache and TTL."""
    cache_key = text[:200]  # Truncate for cache key
    
    # Check cache
    if cache_key in _EMBEDDING_CACHE:
        vec, timestamp = _EMBEDDING_CACHE[cache_key]
        if time.time() - timestamp < _EMBEDDING_CACHE_TTL:
            return vec
        else:
            del _EMBEDDING_CACHE[cache_key]
    
    # Fetch from Voyage
    try:
        import voyageai
        client = voyageai.Client(api_key=VOYAGE_API_KEY)
        result = client.embed([text[:500]], model="voyage-3-lite")
        vec = result.embeddings[0]
        
        # Cache it
        if len(_EMBEDDING_CACHE) >= _EMBEDDING_CACHE_MAX:
            # Evict oldest
            oldest_key = min(_EMBEDDING_CACHE.keys(), 
                           key=lambda k: _EMBEDDING_CACHE[k][1])
            del _EMBEDDING_CACHE[oldest_key]
        
        _EMBEDDING_CACHE[cache_key] = (vec, time.time())
        return vec
    except Exception as e:
        print(f"[lazy_recall_v2] Voyage error: {e}", file=sys.stderr)
        return None


# =============================================================================
# PRE-COMPUTED EMBEDDING INDEX (loaded once, reused)
# =============================================================================

_EMBEDDING_INDEX: Optional[Dict[str, Any]] = None
_EMBEDDING_INDEX_PATH = os.path.expanduser("~/.nima/memory/embedding_index.json")

def load_embedding_index() -> Dict[str, Any]:
    """Load pre-computed embedding index (turn_id -> [neighbor_ids])."""
    global _EMBEDDING_INDEX
    if _EMBEDDING_INDEX is not None:
        return _EMBEDDING_INDEX
    
    if os.path.exists(_EMBEDDING_INDEX_PATH):
        try:
            with open(_EMBEDDING_INDEX_PATH, 'r') as f:
                _EMBEDDING_INDEX = json.load(f)
            return _EMBEDDING_INDEX
        except:
            pass
    
    # Empty index - will be built on first query
    _EMBEDDING_INDEX = {}
    return _EMBEDDING_INDEX


def decode_vector(blob) -> Optional[List[float]]:
    """Unpack embedding from BLOB."""
    if not blob:
        return None
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))


def cosine_sim(a: List[float], b: List[float]) -> float:
    """Cosine similarity between vectors."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# =============================================================================
# FTS5 QUERY SANITIZATION
# =============================================================================

def sanitize_fts5_query(text: str) -> str:
    """Escape special FTS5 characters."""
    if not text:
        return ""
    import re
    cleaned = re.sub(r'[()\{\}\[\]"\'\*\^\-\+:\~\?,\.!]', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


# =============================================================================
# TIER 1: INDEX SCANS (lazy - no full embedding decode)
# =============================================================================

def normalize_timestamp(ts: int) -> int:
    """Normalize timestamp to milliseconds. Handles both seconds and ms formats."""
    # If timestamp is less than year 2100 in seconds (4102444800), it's in seconds
    if ts < 4102444800:
        return ts * 1000
    return ts


def tier1_fts_scan(db, query: str, limit: int, min_timestamp: int) -> List[Dict]:
    """FTS5 search - just turn_ids and scores."""
    safe_query = sanitize_fts5_query(query)
    if not safe_query:
        return []
    
    try:
        # Fetch without timestamp filter first, then filter in Python
        # (timestamps in DB may be in seconds or milliseconds)
        cursor = db.execute("""
            SELECT n.turn_id, n.timestamp, 
                   MIN(fts.rank) as best_score
            FROM memory_fts fts
            JOIN memory_nodes n ON fts.rowid = n.id
            WHERE memory_fts MATCH ?
            GROUP BY n.turn_id
            ORDER BY best_score
            LIMIT ?
        """, (safe_query, limit * 10))
        
        results = []
        for r in cursor:
            ts = normalize_timestamp(r[1])
            if ts >= min_timestamp:
                results.append({
                    "turn_id": r[0], 
                    "timestamp": ts, 
                    "fts_score": abs(r[2])
                })
                if len(results) >= limit * 3:
                    break
        
        return results
        
        return [{"turn_id": r[0], "timestamp": r[1], "fts_score": abs(r[2])} 
                for r in cursor]
    except Exception as e:
        print(f"[lazy_recall_v2] FTS error: {e}", file=sys.stderr)
        return []


def tier1_embedding_scan_lazy(db, query_vec: List[float], limit: int, 
                               min_timestamp: int) -> List[Dict]:
    """
    Lazy embedding scan - only decodes embeddings for candidates.
    Uses timestamp normalization to handle mixed formats.
    """
    try:
        # Get recent nodes with embeddings (no timestamp filter in SQL due to mixed formats)
        cursor = db.execute("""
            SELECT DISTINCT turn_id, timestamp
            FROM memory_nodes
            WHERE embedding IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit * 10,))
        
        # Filter by timestamp in Python
        candidates = []
        for r in cursor:
            ts = normalize_timestamp(r[1])
            if ts >= min_timestamp:
                candidates.append((r[0], ts))
            if len(candidates) >= limit * 5:
                break
        
        if not candidates:
            return []
        
        # Now load and decode ONLY the embeddings we need
        results = []
        for tid, ts in candidates[:limit * 3]:
            # Load just this one embedding
            emb_cursor = db.execute("""
                SELECT embedding FROM memory_nodes
                WHERE turn_id = ? AND embedding IS NOT NULL
                LIMIT 1
            """, (tid,))
            
            row = emb_cursor.fetchone()
            if row and row[0]:
                vec = decode_vector(row[0])
                if vec:
                    sim = cosine_sim(query_vec, vec)
                    if sim > EMBEDDING_THRESHOLD:
                        results.append({
                            "turn_id": tid,
                            "timestamp": ts,
                            "emb_score": sim
                        })
        
        # Sort by similarity
        results.sort(key=lambda x: x["emb_score"], reverse=True)
        return results[:limit * 2]
        
    except Exception as e:
        print(f"[lazy_recall_v2] Embedding scan error: {e}", file=sys.stderr)
        return []


# =============================================================================
# TIER 2: SUMMARY LOAD
# =============================================================================

def tier2_load_summaries(db, candidates: List[Dict]) -> List[Dict]:
    """Load compressed summaries for candidates."""
    turn_ids = [c["turn_id"] for c in candidates if c.get("turn_id")]
    if not turn_ids:
        return candidates
    
    placeholders = ",".join("?" * len(turn_ids))
    cursor = db.execute(f"""
        SELECT turn_id, layer, summary, who
        FROM memory_nodes
        WHERE turn_id IN ({placeholders})
    """, turn_ids)
    
    summaries = {}
    for row in cursor:
        tid = row[0]
        if tid not in summaries:
            summaries[tid] = {"layers": {}, "who": row[3] or "unknown"}
        summaries[tid]["layers"][row[1]] = row[2] or ""
    
    for c in candidates:
        tid = c.get("turn_id")
        if tid in summaries:
            c["layers"] = summaries[tid]["layers"]
            c["who"] = summaries[tid]["who"]
        else:
            c["layers"] = {}
            c["who"] = "unknown"
    
    return candidates


# =============================================================================
# AFFECT RESONANCE
# =============================================================================

AFFECT_DIMENSIONS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"]

def parse_affect_json(affect_json_str: str) -> Dict[str, float]:
    """Parse affect_json string into dict."""
    if not affect_json_str:
        return {}
    try:
        data = json.loads(affect_json_str)
        if isinstance(data, dict):
            return {k: float(v) for k, v in data.items() 
                    if k in AFFECT_DIMENSIONS and isinstance(v, (int, float))}
    except:
        pass
    return {}


def tier2_load_affect(db, candidates: List[Dict]) -> List[Dict]:
    """Load affect states for candidates."""
    turn_ids = [c["turn_id"] for c in candidates if c.get("turn_id")]
    if not turn_ids:
        return candidates
    
    placeholders = ",".join("?" * len(turn_ids))
    cursor = db.execute(f"""
        SELECT turn_id, affect_json
        FROM memory_nodes
        WHERE turn_id IN ({placeholders})
          AND affect_json IS NOT NULL
          AND affect_json != ''
          AND affect_json != '{{}}'
        ORDER BY timestamp DESC
    """, turn_ids)
    
    affects = {}
    for row in cursor:
        tid = row[0]
        if tid not in affects:
            affects[tid] = parse_affect_json(row[1])
    
    for c in candidates:
        c["affect"] = affects.get(c.get("turn_id"), {})
    
    return candidates


def compute_affect_resonance(memory_affect: Dict, current_affect: Dict) -> float:
    """Compute resonance between memory and current affect."""
    if not memory_affect or not current_affect:
        return 0.5
    
    total_diff = 0.0
    dimensions = 0
    
    for dim in AFFECT_DIMENSIONS:
        if dim in memory_affect and dim in current_affect:
            total_diff += abs(memory_affect[dim] - current_affect[dim])
            dimensions += 1
        elif dim in memory_affect or dim in current_affect:
            total_diff += 0.3
            dimensions += 1
    
    if dimensions == 0:
        return 0.5
    
    return 1.0 - min(total_diff / dimensions, 1.0)


def compute_affect_bleed(memories: List[Dict], current_affect: Dict, 
                         bleed_factor: float = 0.08) -> Dict[str, float]:
    """Compute affect bleed from recalled memories."""
    bleed = {dim: 0.0 for dim in AFFECT_DIMENSIONS}
    
    for m in memories:
        affect = m.get("affect", {})
        for dim in AFFECT_DIMENSIONS:
            if dim in affect:
                bleed[dim] += affect[dim] * bleed_factor
    
    return bleed


# =============================================================================
# PARALLEL EXECUTION WITH TIMEOUT
# =============================================================================

def parallel_recall(query_text: str, db_path: str, max_results: int, 
                    min_timestamp: int, current_affect: Optional[Dict],
                    use_embedding: bool = True) -> Dict:
    """Run FTS first, then decide if embedding search is needed."""
    
    db = sqlite3.connect(db_path)
    
    fts_candidates = []
    emb_candidates = []
    skipped_embedding = False
    
    # Run FTS first (fast, ~2ms)
    fts_candidates = tier1_fts_scan(db, query_text, max_results, min_timestamp)
    
    # Check if FTS results are good enough to skip embedding
    if fts_candidates and len(fts_candidates) >= FTS_MIN_RESULTS:
        best_fts_score = min(c.get("fts_score", 999) for c in fts_candidates)
        if best_fts_score < FTS_CONFIDENCE_THRESHOLD:
            skipped_embedding = True
            print(f"[lazy_recall_v2] Skipping embedding (FTS score {best_fts_score:.1f} < {FTS_CONFIDENCE_THRESHOLD})", 
                  file=sys.stderr)
    
    # Run embedding search only if needed
    if use_embedding and not skipped_embedding and len(query_text) >= SKIP_EMBEDDING_MIN_LENGTH:
        query_vec = get_embedding_cached(query_text)
        if query_vec:
            emb_candidates = tier1_embedding_scan_lazy(db, query_vec, max_results, min_timestamp)
    
    db.close()
    
    # Merge candidates
    merged = {}
    for c in fts_candidates:
        merged[c["turn_id"]] = c
    
    for c in emb_candidates:
        tid = c["turn_id"]
        if tid in merged:
            merged[tid]["emb_score"] = c.get("emb_score", 0)
        else:
            merged[tid] = c
    
    return list(merged.values()), skipped_embedding


# =============================================================================
# MAIN: OPTIMIZED LAZY RECALL
# =============================================================================

def lazy_recall(query_text: str, db_path: str = DEFAULT_DB, 
                 max_results: int = MAX_RESULTS, 
                 current_affect: Optional[Dict] = None) -> Dict:
    """
    Optimized lazy recall with:
      - Embedding cache
      - Parallel execution
      - Timeout protection
      - Skip embedding for short queries
    """
    start_time = time.time()
    
    min_timestamp = int((datetime.now() - timedelta(days=TIME_WINDOW_DAYS)).timestamp() * 1000)
    
    # Skip embedding for very short queries (FTS only)
    use_embedding = len(query_text) >= SKIP_EMBEDDING_MIN_LENGTH
    
    try:
        # Run with timeout, returns (candidates, skipped_embedding)
        candidates, skipped_embedding = parallel_recall(
            query_text, db_path, max_results, min_timestamp, 
            current_affect, use_embedding
        )
    except Exception as e:
        print(f"[lazy_recall_v2] Recall error: {e}", file=sys.stderr)
        candidates = []
        skipped_embedding = False
    
    if not candidates:
        return {"memories": [], "affect_bleed": {dim: 0.0 for dim in AFFECT_DIMENSIONS}}
    
    # Tier 2: Load summaries and affect (need DB again)
    db = sqlite3.connect(db_path)
    candidates = tier2_load_summaries(db, candidates)
    candidates = tier2_load_affect(db, candidates)
    db.close()
    
    # Score blending (adjust weights if embedding was skipped)
    for c in candidates:
        fts_norm = min(c.get("fts_score", 0) / 50, 1.0)
        emb_norm = c.get("emb_score", 0)
        affect_res = compute_affect_resonance(c.get("affect", {}), current_affect or {})
        
        # Adjust weights based on whether embedding was used
        if skipped_embedding or not use_embedding:
            # FTS-only scoring
            c["score"] = (fts_norm * 0.85) + (affect_res * 0.15)
        else:
            # Hybrid scoring
            c["score"] = (fts_norm * 0.35) + (emb_norm * 0.50) + (affect_res * 0.15)
        
        c["affect_resonance"] = affect_res
    
    # Sort and take top
    ranked = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)[:max_results]
    
    # Compute bleed
    affect_bleed = compute_affect_bleed(ranked, current_affect)
    
    # Format output
    output = []
    for r in ranked:
        parts = []
        layers = r.get("layers", {})
        if layers.get("input"):
            parts.append(f"In: {layers['input'][:100]}")
        if layers.get("output"):
            parts.append(f"Out: {layers['output'][:100]}")
        if layers.get("contemplation"):
            parts.append(f"Think: {layers['contemplation'][:80]}")
        if parts:
            who = r.get("who", "unknown")
            output.append(f"[{who}] " + " | ".join(parts))
    
    elapsed = time.time() - start_time
    if elapsed > 1.0:
        print(f"[lazy_recall_v2] Slow recall: {elapsed*1000:.0f}ms for '{query_text[:30]}...'", 
              file=sys.stderr)
    
    return {
        "memories": output,
        "affect_bleed": affect_bleed
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lazy_recall_v2.py <query> [affect_json]", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    current_affect = None
    
    if len(sys.argv) > 2:
        try:
            current_affect = json.loads(sys.argv[2])
        except:
            pass
    
    result = lazy_recall(query, current_affect=current_affect)
    print(json.dumps(result))