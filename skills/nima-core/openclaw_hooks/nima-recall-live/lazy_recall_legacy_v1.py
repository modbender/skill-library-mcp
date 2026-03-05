#!/usr/bin/env python3
"""
NIMA Lazy Reconstruction Recall
================================

Three-tier memory loading:
  Layer 1: Index scan (turn_id + score only)
  Layer 2: Summary load (10-20 token summaries)
  Layer 3: Full decode (complete text - only top 2-3)

Optimizations:
  - Embedding cache (pre-computed neighbor index)
  - Timestamp filtering (last 90 days default)
  - Tiered loading to minimize context usage

Author: NIMA Core Team
Date: 2026-02-14
"""

import sqlite3
import json
import sys
import struct
import os
from datetime import datetime, timedelta

# Config
DEFAULT_DB = os.path.expanduser("~/.nima/memory/graph.sqlite")
MAX_RESULTS = 3
TIME_WINDOW_DAYS = 90  # Only search recent memories
EMBEDDING_THRESHOLD = 0.35
VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY")
if not VOYAGE_API_KEY:
    print("ERROR: VOYAGE_API_KEY environment variable not set", file=sys.stderr)


def decode_vector(blob):
    """Unpack embedding from BLOB."""
    if not blob:
        return None
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))


def cosine_sim(a, b):
    """Cosine similarity between vectors."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def sanitize_fts5_query(text):
    """
    Escape special FTS5 characters to prevent syntax errors.
    FTS5 special chars: ( ) { } [ ] " ' * ^ - + : ~ ? , . !
    Returns a safe query string.
    """
    if not text:
        return ""
    
    # Remove or escape problematic characters
    # Keep alphanumeric, spaces, and basic punctuation
    import re
    # Replace special FTS5 operators with space
    cleaned = re.sub(r'[()\{\}\[\]"\'\*\^\-\+:\~\?,\.!]', ' ', text)
    # Collapse multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def get_embedding(text):
    """Get Voyage embedding for text."""
    import voyageai
    client = voyageai.Client(api_key=VOYAGE_API_KEY)
    result = client.embed([text[:500]], model="voyage-3-lite")
    return result.embeddings[0]


# =============================================================================
# TIER 1: INDEX SCAN - Returns turn_ids + scores only
# =============================================================================

def tier1_fts_scan(db, query, limit, min_timestamp):
    """FTS5 search for candidate turn_ids. No text loading."""
    # Sanitize query for FTS5 (escape special characters)
    safe_query = sanitize_fts5_query(query)
    if not safe_query:
        return []
    
    cursor = db.execute("""
        SELECT n.turn_id, n.timestamp, 
               MIN(fts.rank) as best_score
        FROM memory_fts fts
        JOIN memory_nodes n ON fts.rowid = n.id
        WHERE memory_fts MATCH ?
          AND n.timestamp >= ?
        GROUP BY n.turn_id
        ORDER BY best_score
        LIMIT ?
    """, (safe_query, min_timestamp, limit * 3))
    
    results = []
    for row in cursor:
        results.append({
            "turn_id": row[0],
            "timestamp": row[1],
            "fts_score": abs(row[2])
        })
    return results


def tier1_embedding_scan(db, query_vec, limit, min_timestamp):
    """Semantic search over embeddings. Only loads embeddings, not text."""
    # Only load recent embeddings
    cursor = db.execute("""
        SELECT id, turn_id, embedding, timestamp
        FROM memory_nodes
        WHERE embedding IS NOT NULL
          AND timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 500
    """, (min_timestamp,))
    
    scored = []
    for row in cursor:
        vec = decode_vector(row[2])
        if vec:
            sim = cosine_sim(query_vec, vec)
            if sim > EMBEDDING_THRESHOLD:
                scored.append({
                    "turn_id": row[1],
                    "timestamp": row[3],
                    "emb_score": sim
                })
    
    # Sort by similarity and dedupe by turn_id
    scored.sort(key=lambda x: x["emb_score"], reverse=True)
    seen = set()
    deduped = []
    for s in scored:
        if s["turn_id"] not in seen:
            seen.add(s["turn_id"])
            deduped.append(s)
            if len(deduped) >= limit * 3:
                break
    
    return deduped


# =============================================================================
# TIER 2: SUMMARY LOAD - Load summaries for candidates
# =============================================================================

def tier2_load_summaries(db, candidates):
    """Load compressed summaries for candidate turn_ids."""
    turn_ids = [c["turn_id"] for c in candidates if c.get("turn_id")]
    if not turn_ids:
        return candidates
    
    placeholders = ",".join("?" * len(turn_ids))
    cursor = db.execute(f"""
        SELECT turn_id, layer, summary, who
        FROM memory_nodes
        WHERE turn_id IN ({placeholders})
    """, turn_ids)
    
    # Group by turn_id
    summaries = {}
    for row in cursor:
        tid = row[0]
        if tid not in summaries:
            summaries[tid] = {"layers": {}, "who": row[3] or "unknown"}
        summaries[tid]["layers"][row[1]] = row[2] or ""
    
    # Merge into candidates
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
# TIER 3: FULL DECODE - Load complete text (only for top results)
# =============================================================================

def tier3_full_decode(db, top_candidates, max_full=2):
    """Fully reconstruct top N memories. Expensive - use sparingly."""
    for c in top_candidates[:max_full]:
        tid = c.get("turn_id")
        if not tid:
            continue
        
        cursor = db.execute("""
            SELECT layer, text, who
            FROM memory_nodes
            WHERE turn_id = ?
        """, (tid,))
        
        c["full_text"] = {}
        for row in cursor:
            layer = row[0]
            c["full_text"][layer] = {
                "text": row[1][:500] if row[1] else "",
                "who": row[2] or "unknown"
            }
    
    return top_candidates


# =============================================================================
# AFFECT RESONANCE & BLEED
# =============================================================================

# Valid affect dimensions
AFFECT_DIMENSIONS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"]

def parse_affect_json(affect_json_str):
    """Parse affect_json string into dict."""
    if not affect_json_str:
        return {}
    try:
        data = json.loads(affect_json_str)
        if isinstance(data, dict):
            return {k: float(v) for k, v in data.items() 
                    if k in AFFECT_DIMENSIONS and isinstance(v, (int, float))}
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return {}


def tier2_load_affect(db, candidates):
    """Load affect states for candidate turn_ids."""
    turn_ids = [c["turn_id"] for c in candidates if c.get("turn_id")]
    if not turn_ids:
        return candidates
    
    placeholders = ",".join("?" * len(turn_ids))
    # Get the most recent affect for each turn (from any layer)
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
        if tid not in affects:  # Only first (most recent) per turn
            affects[tid] = parse_affect_json(row[1])
    
    # Merge into candidates
    for c in candidates:
        tid = c.get("turn_id")
        c["affect"] = affects.get(tid, {})
    
    return candidates


def compute_affect_resonance(memory_affect, current_affect):
    """
    Compute resonance score between memory affect and current affect.
    Higher score = more similar feeling state.
    Returns 0.0 to 1.0.
    """
    if not memory_affect or not current_affect:
        return 0.5  # Neutral if unknown
    
    # Compute similarity for shared dimensions
    total_diff = 0.0
    dimensions = 0
    
    for dim in AFFECT_DIMENSIONS:
        if dim in memory_affect and dim in current_affect:
            diff = abs(memory_affect[dim] - current_affect[dim])
            total_diff += diff
            dimensions += 1
        elif dim in memory_affect or dim in current_affect:
            # One has it, other doesn't - moderate difference
            total_diff += 0.3
            dimensions += 1
    
    if dimensions == 0:
        return 0.5
    
    avg_diff = total_diff / dimensions
    # Convert to similarity (0 diff = 1.0, 1.0 diff = 0.0)
    resonance = 1.0 - min(avg_diff, 1.0)
    return resonance


def compute_affect_bleed(memories, current_affect, bleed_factor=0.08):
    """
    Compute how recalled memories should bleed into current affect.
    Returns the affect delta to apply.
    """
    bleed = {dim: 0.0 for dim in AFFECT_DIMENSIONS}
    
    for m in memories:
        affect = m.get("affect", {})
        for dim in AFFECT_DIMENSIONS:
            if dim in affect:
                # Bleed is proportional to the memory's affect intensity
                # and the resonance (similar feelings transfer more)
                bleed[dim] += affect[dim] * bleed_factor
    
    return bleed


# =============================================================================
# MAIN: LAZY RECALL PIPELINE
# =============================================================================

def lazy_recall(query_text, db_path=DEFAULT_DB, max_results=MAX_RESULTS, current_affect=None):
    """
    Three-tier lazy recall with affect resonance:
      1. Index scan → candidate turn_ids
      2. Summary load → compressed context
      3. Affect resonance → score by feeling similarity
      4. Clean output → content only, no affect tags
      5. Affect bleed → returns affect deltas too
    
    Returns: (memories, affect_bleed)
    """
    # Calculate time window
    min_timestamp = int((datetime.now() - timedelta(days=TIME_WINDOW_DAYS)).timestamp() * 1000)
    
    db = sqlite3.connect(db_path)
    
    # Tier 1: Index scan
    fts_candidates = tier1_fts_scan(db, query_text, max_results, min_timestamp)
    
    # Get embedding for semantic search
    query_vec = get_embedding(query_text)
    emb_candidates = tier1_embedding_scan(db, query_vec, max_results, min_timestamp)
    
    # Merge candidates by turn_id
    merged = {}
    for c in fts_candidates:
        tid = c["turn_id"]
        merged[tid] = c
    
    for c in emb_candidates:
        tid = c["turn_id"]
        if tid in merged:
            merged[tid]["emb_score"] = c.get("emb_score", 0)
        else:
            merged[tid] = c
    
    # Tier 2: Load summaries AND affect states
    merged_list = list(merged.values())
    merged_list = tier2_load_summaries(db, merged_list)
    merged_list = tier2_load_affect(db, merged_list)
    
    # Blend scores: 35% FTS5 + 50% semantic + 15% affect resonance
    for c in merged_list:
        fts_norm = min(c.get("fts_score", 0) / 50, 1.0)
        emb_norm = c.get("emb_score", 0)
        
        # Affect resonance - how similar does this memory feel?
        affect_res = compute_affect_resonance(c.get("affect", {}), current_affect or {})
        
        # Weighted blend
        c["score"] = (fts_norm * 0.35) + (emb_norm * 0.50) + (affect_res * 0.15)
        c["affect_resonance"] = affect_res
    
    # Sort and take top results
    ranked = sorted(merged_list, key=lambda x: x.get("score", 0), reverse=True)[:max_results]
    
    db.close()
    
    # Compute affect bleed from recalled memories
    affect_bleed = compute_affect_bleed(ranked, current_affect)
    
    # Format CLEAN output (no affect tags)
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
    
    # Return both memories and affect bleed
    return {
        "memories": output,
        "affect_bleed": affect_bleed
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lazy_recall.py <query> [affect_json]", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    current_affect = None
    
    # Parse current affect if provided
    if len(sys.argv) > 2:
        try:
            current_affect = json.loads(sys.argv[2])
        except:
            pass
    
    result = lazy_recall(query, current_affect=current_affect)
    print(json.dumps(result))


def apply_affect_bleed(bleed, affect_state_path):
    """
    Apply affect bleed to the current affect state file.
    Modifies the affect state in place.
    
    This is the integration point - recalled memories actually
    change how I feel now.
    """
    if not bleed or not affect_state_path or not os.path.exists(affect_state_path):
        return False
    
    try:
        with open(affect_state_path, 'r') as f:
            state = json.load(f)
        
        if 'current' not in state:
            state['current'] = {}
        if 'named' not in state['current']:
            state['current']['named'] = {}
        
        named = state['current']['named']
        
        # Apply bleed to each dimension
        for dim in AFFECT_DIMENSIONS:
            if dim in bleed:
                current = named.get(dim, 0.1)
                # Apply bleed and clamp to valid range
                new_val = max(0.08, min(0.92, current + bleed[dim]))
                named[dim] = new_val
        
        # Write back
        with open(affect_state_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Failed to apply affect bleed: {e}", file=sys.stderr)
        return False