#!/usr/bin/env python3
"""
NIMA Embedding Index Builder
=============================

Pre-computes nearest neighbor indices for all embeddings.
Enables instant semantic search without decoding vectors.

Run: python3 build_embedding_index.py [--incremental]

Options:
  --incremental  Add only new embeddings since last build
  --full         Rebuild entire index (default)

Output: ~/.nima/memory/embedding_index.npy

Cron (recommended): Run at 3 AM daily
  0 3 * * * python3 ~/.openclaw/extensions/nima-recall-live/build_embedding_index.py --incremental

Author: NIMA Core Team
Date: 2026-02-14
"""

import sqlite3
import os
import json
import struct
import numpy as np
from datetime import datetime, timedelta
import argparse

DB_PATH = os.path.expanduser("~/.nima/memory/graph.sqlite")
INDEX_PATH = os.path.expanduser("~/.nima/memory/embedding_index.npy")
META_PATH = os.path.expanduser("~/.nima/memory/embedding_index_meta.json")

def decode_vector(blob):
    """Unpack embedding from BLOB."""
    if not blob:
        return None
    n = len(blob) // 4
    return np.array(struct.unpack(f'{n}f', blob), dtype=np.float32)

def cosine_similarity_matrix(query_vec, embedding_matrix):
    """Compute cosine similarity between query and all embeddings."""
    if embedding_matrix is None or len(embedding_matrix) == 0:
        return np.array([])
    
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
    norms = np.linalg.norm(embedding_matrix, axis=1, keepdims=True) + 1e-8
    normalized = embedding_matrix / norms
    return np.dot(normalized, query_norm)

def load_existing_index():
    """Load existing index and metadata."""
    try:
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            matrix = np.load(INDEX_PATH)
            with open(META_PATH, 'r') as f:
                meta = json.load(f)
            return matrix, meta
    except Exception as e:
        print(f"[build_index] Could not load existing index: {e}")
    return None, None

def build_index(incremental=False):
    """Build or update embedding index."""
    print(f"Building embedding index (incremental={incremental})...")
    
    db = sqlite3.connect(DB_PATH)
    
    # Get existing index if incremental
    existing_matrix = None
    existing_meta = None
    existing_ids = set()
    
    if incremental:
        existing_matrix, existing_meta = load_existing_index()
        if existing_meta:
            existing_ids = set(e['id'] for e in existing_meta.get('entries', []))
            print(f"Existing index: {len(existing_ids)} embeddings")
    
    # Get embeddings from last 180 days
    min_timestamp = int((datetime.now() - timedelta(days=180)).timestamp() * 1000)
    
    if incremental and existing_matrix is not None:
        # Only get new embeddings
        cursor = db.execute("""
            SELECT id, turn_id, embedding, timestamp
            FROM memory_nodes
            WHERE embedding IS NOT NULL
            AND timestamp >= ?
            AND id NOT IN ({})
            ORDER BY timestamp DESC
        """.format(','.join(map(str, existing_ids)) if existing_ids else '0'), (min_timestamp,))
    else:
        # Full rebuild
        cursor = db.execute("""
            SELECT id, turn_id, embedding, timestamp
            FROM memory_nodes
            WHERE embedding IS NOT NULL
            AND timestamp >= ?
            ORDER BY timestamp DESC
        """, (min_timestamp,))
    
    rows = cursor.fetchall()
    db.close()
    
    print(f"Found {len(rows)} new embeddings")
    
    if len(rows) == 0 and existing_matrix is not None:
        print("No new embeddings, index up to date!")
        return
    
    # Decode new embeddings
    new_embeddings = []
    new_metadata = []
    
    for row in rows:
        node_id, turn_id, blob, timestamp = row
        vec = decode_vector(blob)
        if vec is not None:
            new_embeddings.append(vec)
            new_metadata.append({
                'id': node_id,
                'turn_id': turn_id,
                'timestamp': timestamp,
                'idx': len(new_embeddings) - 1
            })
    
    if len(new_embeddings) == 0:
        print("No valid new embeddings to add")
        return
    
    new_matrix = np.array(new_embeddings, dtype=np.float32)
    
    # Merge with existing if incremental
    if incremental and existing_matrix is not None:
        # Update indices in new metadata
        base_idx = len(existing_meta.get('entries', []))
        for m in new_metadata:
            m['idx'] = base_idx + m['idx']
        
        # Concatenate matrices
        embedding_matrix = np.vstack([existing_matrix, new_matrix])
        metadata = existing_meta.get('entries', []) + new_metadata
        print(f"Merged: {len(existing_meta.get('entries', []))} + {len(new_metadata)} = {len(metadata)} embeddings")
    else:
        embedding_matrix = new_matrix
        metadata = new_metadata
        print(f"Built fresh index: {len(metadata)} embeddings")
    
    print(f"Embedding matrix shape: {embedding_matrix.shape}")
    
    # Save
    np.save(INDEX_PATH, embedding_matrix)
    print(f"Saved embedding matrix to {INDEX_PATH}")
    
    with open(META_PATH, 'w') as f:
        json.dump({
            'created': datetime.now().isoformat(),
            'count': len(metadata),
            'embedding_dim': embedding_matrix.shape[1],
            'entries': metadata
        }, f)
    print(f"Saved metadata to {META_PATH}")
    
    # Test
    print("\nTesting search...")
    query_idx = 0
    query_vec = embedding_matrix[query_idx]
    similarities = cosine_similarity_matrix(query_vec, embedding_matrix)
    top_k = np.argsort(similarities)[-5:][::-1]
    print(f"Query: turn_id={metadata[query_idx]['turn_id'][:30]}...")
    print(f"Top 5 similar:")
    for idx in top_k:
        print(f"  {metadata[idx]['turn_id'][:30]}... sim={similarities[idx]:.3f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build NIMA embedding index')
    parser.add_argument('--incremental', action='store_true', help='Add only new embeddings')
    parser.add_argument('--full', action='store_true', help='Rebuild entire index')
    args = parser.parse_args()
    
    build_index(incremental=args.incremental and not args.full)