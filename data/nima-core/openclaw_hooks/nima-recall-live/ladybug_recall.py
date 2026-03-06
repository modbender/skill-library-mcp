#!/usr/bin/env python3
"""
NIMA Living Memory Recall v6 - LadybugDB Backend
=======================================================

Phase 3: Spontaneous Recall (Serendipity)
- Adds weighted scoring: Similarity + Strength + Recency + Surprise
- Adds dismissal tracking (negative feedback loop)

Author: Lilu + David Dorta
Date: 2026-02-17
"""

import sys
import os
import time
import json
import math
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Import real_ladybug — try system-wide first, then venv fallback
try:
    import real_ladybug as lb
except ImportError:
    import glob as _glob
    _venv_base = os.path.expanduser("~/.openclaw/workspace/.venv/lib")
    _candidates = sorted(_glob.glob(os.path.join(_venv_base, "python3*/site-packages")), reverse=True)
    for _candidate in _candidates:
        sys.path.insert(0, _candidate)
    import real_ladybug as lb

# Config
LADYBUG_DB = os.path.expanduser("~/.nima/memory/ladybug.lbug")


def _open_db_safe(path=None, max_retries=2):
    """Open LadybugDB with WAL corruption auto-recovery."""
    p        = path or LADYBUG_DB
    wal_path = p + '.wal'
    for _attempt in range(max_retries):
        try:
            db   = lb.Database(p)
            conn = lb.Connection(db)
            try:
                conn.execute("LOAD VECTOR")
            except Exception:
                pass
            return db, conn
        except RuntimeError as e:
            if any(k in str(e).lower() for k in ('wal', 'corrupted')) and os.path.exists(wal_path):
                bak = wal_path + f'.bak_{int(time.time())}'
                os.rename(wal_path, bak)
                print(f"nima-recall: WAL corrupted — recovered (→ {os.path.basename(bak)})",
                      file=sys.stderr)
            else:
                raise
    raise RuntimeError(f"LadybugDB failed after {max_retries} recovery attempts")
MAX_RESULTS = 7
TIME_WINDOW_DAYS = 90
EMBEDDING_THRESHOLD = 0.35
GHOST_THRESHOLD = 0.1

# Phase 3 Weights
W_SIMILARITY = 0.5
W_STRENGTH = 0.2
W_RECENCY = 0.2
W_SURPRISE = 0.1

# =============================================================================
# CONNECTION MANAGEMENT
# =============================================================================

_db = None
_conn = None

def connect():
    """Get or create database connection."""
    global _db, _conn
    
    if _conn is None:
        _db, _conn = _open_db_safe(LADYBUG_DB)
    return _conn

def disconnect():
    """Close database connection."""
    global _db, _conn
    _db = None
    _conn = None

# =============================================================================
# ECOLOGY LOGIC
# =============================================================================

def calculate_current_strength(strength: float, decay_rate: float, last_accessed: int, timestamp: int) -> float:
    """Apply Ebbinghaus forgetting curve."""
    start_time = last_accessed if last_accessed > 0 else timestamp
    if start_time == 0:
        return strength
    
    now_ms = int(time.time() * 1000)
    elapsed_ms = max(0, now_ms - start_time)
    elapsed_hours = elapsed_ms / 3600000.0
    
    try:
        retention = math.exp(-decay_rate * elapsed_hours)
        return strength * retention
    except OverflowError:
        return 0.0

def calculate_ecology_score(base_similarity: float, strength: float, timestamp: int, dismissal_count: int) -> float:
    """
    Phase 3: Weighted Scoring Algorithm
    
    Score = (Sim * 0.5) + (Strength * 0.2) + (Recency * 0.2) + (Surprise * 0.1)
    
    Penalties:
    - Dismissals: exponential penalty (0.5 ^ count)
    """
    now_ms = int(time.time() * 1000)
    
    # 1. Recency (0.0 to 1.0)
    # Decay over ~100 days
    age_days = (now_ms - timestamp) / 86_400_000
    recency = math.exp(-0.01 * age_days)
    
    # 2. Surprise (Serendipity)
    # Random factor to surface unexpected memories
    # 10% chance of a high surprise boost, otherwise low
    if random.random() < 0.1:
        surprise = random.uniform(0.5, 1.0)
    else:
        surprise = random.uniform(0.0, 0.2)
        
    # 3. Dismissal Penalty
    # If user has dismissed this memory before, kill the score
    penalty = math.pow(0.5, dismissal_count)
    
    # Weighted Sum
    score = (
        (base_similarity * W_SIMILARITY) +
        (strength * W_STRENGTH) +
        (recency * W_RECENCY) +
        (surprise * W_SURPRISE)
    )
    
    return score * penalty

def update_memory_stats(memory_ids: List[int]):
    """Hebbian Reinforcement."""
    if not memory_ids:
        return
    conn = connect()
    now = int(time.time() * 1000)
    ids_str = "[" + ",".join(str(mid) for mid in memory_ids) + "]"
    
    try:
        conn.execute(f"""
            MATCH (n:MemoryNode)
            WHERE n.id IN {ids_str}
            SET n.strength = CASE WHEN n.strength + 0.1 > 1.0 THEN 1.0 ELSE n.strength + 0.1 END,
                n.decay_rate = CASE WHEN n.decay_rate * 0.9 < 0.001 THEN 0.001 ELSE n.decay_rate * 0.9 END
        """)
    except Exception as e:
        print(f"[ladybug_recall] Stats update warning: {e}", file=sys.stderr)

# =============================================================================
# SEARCH FUNCTIONS
# =============================================================================

def text_search(query: str, limit: int = MAX_RESULTS) -> List[Dict]:
    conn = connect()
    start = time.time()
    min_timestamp = int((datetime.now() - timedelta(days=TIME_WINDOW_DAYS)).timestamp() * 1000)

    # Split multi-word queries — CONTAINS requires exact substring match
    # so "EMJAC fabrication" would fail. Search each term separately with OR.
    terms = [t.strip() for t in query.split() if len(t.strip()) >= 3][:6]
    if not terms:
        terms = [query]

    # Build per-term conditions
    params: Dict[str, Any] = {"min_ts": min_timestamp, "result_limit": limit * 3}
    term_clauses = []
    for i, term in enumerate(terms):
        key = f"term{i}"
        params[key] = term
        term_clauses.append(f"(n.text CONTAINS ${key} OR n.summary CONTAINS ${key})")
    where_terms = " OR ".join(term_clauses)

    try:
        result = conn.execute(f"""
            MATCH (n:MemoryNode)
            WHERE ({where_terms})
            AND n.timestamp >= $min_ts
            RETURN n.id, n.text, n.summary, n.who, n.layer, n.timestamp,
                   n.strength, n.decay_rate
            LIMIT $result_limit
        """, params)
        
        memories = []
        for row in result:
            memories.append({
                'id': row[0],
                'text': row[1] or "",
                'summary': row[2] or "",
                'who': row[3] or "unknown",
                'layer': row[4] or "unknown",
                'timestamp': row[5] or 0,
                'strength': row[6] if row[6] is not None else 1.0,
                'decay_rate': row[7] if row[7] is not None else 0.01,
                'last_accessed': 0,
                'is_ghost': False,
                'dismissal_count': 0,
                'fts_score': 1.0
            })
        
        return memories, (time.time() - start) * 1000
    except Exception as e:
        print(f"[ladybug_recall] Text search error: {e}", file=sys.stderr)
        return [], 0

def vector_search(query_embedding: List[float], limit: int = MAX_RESULTS) -> List[Dict]:
    conn = connect()
    start = time.time()
    
    if not isinstance(query_embedding, list):
        return [], 0
    min_timestamp = int((datetime.now() - timedelta(days=TIME_WINDOW_DAYS)).timestamp() * 1000)
    
    try:
        result = conn.execute("""
            CALL QUERY_VECTOR_INDEX('MemoryNode', 'embedding_idx', $embedding, $top_k)
            RETURN node.id, node.text, node.summary, node.who, node.layer, node.timestamp, distance,
                   node.strength, node.decay_rate
            ORDER BY distance
        """, {"embedding": query_embedding, "top_k": limit * 4})
        
        memories = []
        for row in result:
            distance = row[6] if row[6] is not None else 1.0
            score = 1.0 - distance
            if score < EMBEDDING_THRESHOLD:
                continue
            if (row[5] or 0) < min_timestamp:
                continue
            
            memories.append({
                'id': row[0],
                'text': row[1] or "",
                'summary': row[2] or "",
                'who': row[3] or "unknown",
                'layer': row[4] or "unknown",
                'timestamp': row[5] or 0,
                'emb_score': score,
                'strength': row[7] if row[7] is not None else 1.0,
                'decay_rate': row[8] if row[8] is not None else 0.01,
                'last_accessed': 0,
                'is_ghost': False,
                'dismissal_count': 0
            })
        
        return memories, (time.time() - start) * 1000
    except Exception as e:
        print(f"[ladybug_recall] Vector search error: {e}", file=sys.stderr)
        return [], 0

def hybrid_search(query: str, query_embedding: List[float], 
                  limit: int = MAX_RESULTS,
                  text_weight: float = 0.3,
                  who_boost: float = 1.2) -> List[Dict]:
    
    text_results, text_time = text_search(query, limit * 2)
    vector_results, vector_time = vector_search(query_embedding, limit * 2)
    
    seen_ids = {}
    
    # Helper to process result
    def process_result(m, base_score):
        curr_strength = calculate_current_strength(
            m['strength'], m['decay_rate'], m['last_accessed'], m['timestamp']
        )
        is_ghost = m['is_ghost'] or (curr_strength < GHOST_THRESHOLD)
        
        # Phase 3: Spontaneous Scoring
        eco_score = calculate_ecology_score(
            base_score, curr_strength, m['timestamp'], m['dismissal_count']
        )
        
        if m.get('who') == 'self':
            eco_score *= who_boost
            
        # Boost existing
        if m['id'] in seen_ids:
            seen_ids[m['id']]['combined_score'] += (eco_score * 0.5) # Diminishing returns
        else:
            m['combined_score'] = eco_score
            m['current_strength'] = curr_strength
            m['is_ghost'] = is_ghost
            seen_ids[m['id']] = m

    for m in vector_results:
        process_result(m, m.get('emb_score', 0.5))
        
    for m in text_results:
        # Text matches get fixed relevance of 1.0 * text_weight
        process_result(m, 1.0 * text_weight)
        
    # Sort
    combined = sorted(seen_ids.values(), key=lambda x: x['combined_score'], reverse=True)
    
    results = []
    ids_to_reinforce = []
    
    for m in combined[:limit]:
        summary = m['summary'] or m['text']
        text = m['text']
        
        if m['is_ghost']:
            summary = "👻 [Faded Memory] " + summary[:50] + "..."
            text = "[Memory has faded. Details are ghostly.]"
            
        results.append({
            'turn_id': f"ladybug:{m['id']}",
            'timestamp': m['timestamp'],
            'who': m['who'],
            'layer': m['layer'],
            'summary': summary[:200],
            'text': text[:500],
            'score': m['combined_score'],
            'strength': m['current_strength'],
            'is_ghost': m['is_ghost'],
            'time_ms': text_time + vector_time
        })
        ids_to_reinforce.append(m['id'])
        
    if ids_to_reinforce:
        update_memory_stats(ids_to_reinforce)
    
    return results

# =============================================================================
# COMPATIBILITY LAYER
# =============================================================================

def get_voyage_embedding(text: str, verbose: bool = False) -> Optional[List[float]]:
    """Generate query embedding via Voyage AI — uses disk cache for speed."""
    # Try voyage_cache first (SQLite-backed LRU — same-session repeat = instant)
    try:
        _this_dir = os.path.dirname(os.path.abspath(__file__))
        import sys as _sys
        if _this_dir not in _sys.path:
            _sys.path.insert(0, _this_dir)
        from voyage_cache import embed_cached
        emb = embed_cached(text[:500])
        if emb is not None:
            emb_list = emb.tolist() if hasattr(emb, 'tolist') else list(emb)
            if verbose: print(f"[ladybug_recall] ✅ Voyage embedding (cached): {len(emb_list)}D", file=sys.stderr)
            return emb_list
    except Exception:
        pass  # Fall through to direct API call

    # Direct API call fallback
    import urllib.request, json as _json
    api_key = os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        return None
    try:
        payload = _json.dumps({
            "input": [text[:500]],
            "model": "voyage-3-lite",  # matches stored 512D embeddings
            "input_type": "query"
        }).encode()
        req = urllib.request.Request(
            "https://api.voyageai.com/v1/embeddings",
            data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = _json.loads(resp.read())
            emb = data["data"][0]["embedding"]
            if verbose: print(f"[ladybug_recall] ✅ Voyage embedding (API): {len(emb)}D", file=sys.stderr)
            return emb
    except Exception as e:
        if verbose: print(f"[ladybug_recall] Voyage embedding failed: {e}", file=sys.stderr)
        return None


def lazy_recall(query: str, 
                 query_embedding: Optional[List[float]] = None,
                 who: Optional[str] = None,
                 top_k: int = MAX_RESULTS,
                 verbose: bool = False) -> List[Dict]:
    start = time.time()
    if verbose: print(f"[ladybug_recall] Query: '{query[:50]}...'", file=sys.stderr)

    # Auto-generate embedding if not provided (enables semantic search)
    if not query_embedding:
        query_embedding = get_voyage_embedding(query, verbose=verbose)

    if query_embedding:
        results = hybrid_search(query, query_embedding, limit=top_k)
    else:
        # Text-only fallback
        raw_results, text_time = text_search(query, limit=top_k)
        results = []
        ids_to_reinforce = []
        for m in raw_results:
            curr_strength = calculate_current_strength(m['strength'], m['decay_rate'], m['last_accessed'], m['timestamp'])
            eco_score = calculate_ecology_score(1.0, curr_strength, m['timestamp'], m['dismissal_count'])
            is_ghost = m['is_ghost'] or (curr_strength < GHOST_THRESHOLD)
            
            summary = m['summary'] or m['text']
            text = m['text']
            if is_ghost:
                summary = "👻 " + summary[:50]
                text = "[Ghost]"
                
            results.append({
                'turn_id': f"ladybug:{m['id']}",
                'timestamp': m['timestamp'],
                'who': m['who'],
                'layer': m['layer'],
                'summary': summary[:200],
                'text': text[:500],
                'score': eco_score,
                'strength': curr_strength,
                'time_ms': text_time
            })
            ids_to_reinforce.append(m['id'])
            
        if ids_to_reinforce:
            update_memory_stats(ids_to_reinforce)
    
    # Apply who filter if specified
    if who:
        results = [r for r in results if r.get("who") == who]
            
    if verbose:
        total_time = (time.time() - start) * 1000
        print(f"[ladybug_recall] Found {len(results)} results in {total_time:.1f}ms", file=sys.stderr)
    
    return results

# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NIMA LadybugDB Recall")
    parser.add_argument("query", nargs="?", default="memory", help="Search query")
    parser.add_argument("--top", type=int, default=5, help="Top results")
    parser.add_argument("--who", type=str, help="Filter by who")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    results = lazy_recall(args.query, who=args.who, top_k=args.top, verbose=args.verbose)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n🔍 Query: '{args.query}'")
        print(f"   Found {len(results)} results\n")
        for i, r in enumerate(results):
            strength_bar = "█" * int(r.get('strength', 0) * 10)
            print(f"{i+1}. [{r.get('who', '?')}] {r.get('summary', '')[:100]}...")
            print(f"   Life: {strength_bar} ({r.get('strength',0):.2f}) | Score: {r.get('score', 0):.3f}\n")

if __name__ == "__main__":
    main()
