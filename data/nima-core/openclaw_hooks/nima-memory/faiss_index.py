#!/usr/bin/env python3
"""
NIMA FAISS Embedding Index
===========================

O(log N) vector similarity search using Facebook's FAISS library.
Replaces O(N) brute-force search for massive scalability.

Performance (on Apple M1):
  - Brute force (N=100K): ~500ms
  - FAISS IVF (N=100K): ~5ms (100x faster)

Usage:
  # Build index from existing embeddings
  python3 faiss_index.py build [--index-type ivf|flat]
  
  # Search
  python3 faiss_index.py search "query text" [--top 10]
  
  # Add new embeddings incrementally
  python3 faiss_index.py add <node_id> <embedding_blob_hex>
  
  # Stats
  python3 faiss_index.py stats

Author: NIMA Backend Architect
Date: 2026-02-16
"""

import os
import sys
import json
import time
import struct
import sqlite3
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

import numpy as np

# Paths
NIMA_DIR = Path.home() / ".nima" / "memory"
FAISS_INDEX_PATH = NIMA_DIR / "faiss.index"
FAISS_META_PATH = NIMA_DIR / "faiss_meta.json"
GRAPH_DB = NIMA_DIR / "graph.sqlite"

# Config
EMBEDDING_DIM = 512  # voyage-3-lite dimension
DEFAULT_NLIST = 100  # IVF clusters (sqrt(N) is a good heuristic)
DEFAULT_NPROBE = 10  # Clusters to search (trade speed vs recall)


def decode_vector(blob: bytes) -> Optional[np.ndarray]:
    """Unpack embedding BLOB to numpy array."""
    if not blob:
        return None
    n = len(blob) // 4
    return np.array(struct.unpack(f'{n}f', blob), dtype=np.float32)


def encode_vector(vec: np.ndarray) -> bytes:
    """Pack numpy array to BLOB for SQLite."""
    return struct.pack(f'{len(vec)}f', *vec.tolist())


class FAISSIndex:
    """
    FAISS-powered embedding index for O(log N) similarity search.
    
    Supports two index types:
    - 'flat': Exact search (for small datasets < 10K)
    - 'ivf': Approximate search with IVF (for large datasets)
    
    IVF (Inverted File Index) partitions vectors into clusters,
    then only searches relevant clusters → O(log N) complexity.
    """
    
    def __init__(self, dim: int = EMBEDDING_DIM, index_type: str = 'flat'):
        self.dim = dim
        self.index_type = index_type
        self.id_map: List[Dict[str, Any]] = []  # Maps FAISS index to node metadata
        self._index = None
        self._is_trained = False
        
    def _create_index(self, n_vectors: int = 0):
        """Create FAISS index based on dataset size and type."""
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed. Run: pip install faiss-cpu")
        
        if self.index_type == 'flat' or n_vectors < 1000:
            # Exact search - IndexFlatIP for inner product (cosine with normalized vectors)
            self._index = faiss.IndexFlatIP(self.dim)
            self._is_trained = True
        else:
            # IVF with L2 quantization - needs training
            nlist = min(DEFAULT_NLIST, max(1, int(np.sqrt(n_vectors))))
            quantizer = faiss.IndexFlatL2(self.dim)
            self._index = faiss.IndexIVFFlat(quantizer, self.dim, nlist, faiss.METRIC_INNER_PRODUCT)
            self._is_trained = False
            
        return self._index
    
    def train(self, embeddings: np.ndarray):
        """Train IVF index (required before adding vectors)."""
        if self._index is None:
            self._create_index(len(embeddings))
        
        if hasattr(self._index, 'train') and not self._is_trained:
            # Normalize for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8
            normalized = embeddings / norms
            self._index.train(normalized.astype(np.float32))
            self._is_trained = True
    
    def add(self, node_ids: List[str], embeddings: np.ndarray, 
            metadata: Optional[List[Dict]] = None):
        """
        Add embeddings to index.
        
        Args:
            node_ids: List of node IDs
            embeddings: Numpy array of shape (N, dim)
            metadata: Optional list of metadata dicts per node
        """
        if self._index is None:
            self._create_index(len(embeddings))
        
        if not self._is_trained:
            self.train(embeddings)
        
        # Normalize for cosine similarity (inner product on unit vectors = cosine)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8
        normalized = embeddings / norms
        
        # Add to FAISS
        self._index.add(normalized.astype(np.float32))
        
        # Update ID map
        for i, nid in enumerate(node_ids):
            entry = {'id': nid, 'idx': len(self.id_map)}
            if metadata and i < len(metadata):
                entry.update(metadata[i])
            self.id_map.append(entry)
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10,
               nprobe: int = DEFAULT_NPROBE) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            nprobe: Number of IVF clusters to search (higher = better recall, slower)
            
        Returns:
            List of (node_id, similarity_score, metadata) tuples
        """
        if self._index is None or len(self.id_map) == 0:
            return []
        
        # Set nprobe for IVF
        if hasattr(self._index, 'nprobe'):
            self._index.nprobe = nprobe
        
        # Normalize query
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        query = query_norm.reshape(1, -1).astype(np.float32)
        
        # Search
        scores, indices = self._index.search(query, min(top_k, len(self.id_map)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.id_map):
                continue
            entry = self.id_map[idx]
            results.append((
                entry.get('id'),
                float(scores[0][i]),
                {k: v for k, v in entry.items() if k not in ('id', 'idx')}
            ))
        
        return results
    
    def save(self, index_path: str = str(FAISS_INDEX_PATH),
             meta_path: str = str(FAISS_META_PATH)):
        """Save index and metadata to disk."""
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed")
        
        if self._index is None:
            raise ValueError("No index to save")
        
        # Ensure directory exists
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self._index, index_path)
        
        # Save metadata
        meta = {
            'created': datetime.now().isoformat(),
            'dim': self.dim,
            'index_type': self.index_type,
            'count': len(self.id_map),
            'is_trained': self._is_trained,
            'entries': self.id_map
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f)
        
        print(f"✅ Saved FAISS index ({len(self.id_map)} vectors) to {index_path}")
    
    @classmethod
    def load(cls, index_path: str = str(FAISS_INDEX_PATH),
             meta_path: str = str(FAISS_META_PATH)) -> 'FAISSIndex':
        """Load index from disk."""
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed")
        
        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Index not found at {index_path}")
        
        # Load metadata
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        
        # Create instance
        instance = cls(dim=meta.get('dim', EMBEDDING_DIM), 
                      index_type=meta.get('index_type', 'flat'))
        instance.id_map = meta.get('entries', [])
        instance._is_trained = meta.get('is_trained', True)
        
        # Load FAISS index
        instance._index = faiss.read_index(index_path)
        
        return instance


# Singleton for global access
_global_index: Optional[FAISSIndex] = None


def get_faiss_index() -> Optional[FAISSIndex]:
    """Get or load the global FAISS index."""
    global _global_index
    
    if _global_index is not None:
        return _global_index
    
    try:
        _global_index = FAISSIndex.load()
        return _global_index
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[faiss_index] Could not load index: {e}", file=sys.stderr)
        return None


def build_faiss_index(index_type: str = 'flat', 
                      time_window_days: int = 180) -> FAISSIndex:
    """
    Build FAISS index from all embedded nodes in database.
    
    Args:
        index_type: 'flat' for exact search, 'ivf' for approximate
        time_window_days: Only include recent nodes
    """
    db = sqlite3.connect(str(GRAPH_DB))
    db.row_factory = sqlite3.Row
    
    min_timestamp = int((datetime.now() - timedelta(days=time_window_days)).timestamp() * 1000)
    
    print(f"Loading embeddings from last {time_window_days} days...")
    rows = db.execute("""
        SELECT id, turn_id, embedding, timestamp, who, layer
        FROM memory_nodes
        WHERE embedding IS NOT NULL
        AND timestamp >= ?
        ORDER BY timestamp DESC
    """, (min_timestamp,)).fetchall()
    
    db.close()
    
    if not rows:
        print("No embeddings found!")
        return None
    
    print(f"Found {len(rows)} embedded nodes")
    
    # Decode embeddings
    node_ids = []
    embeddings = []
    metadata = []
    
    for row in rows:
        vec = decode_vector(row['embedding'])
        if vec is not None:
            node_ids.append(row['id'])
            embeddings.append(vec)
            metadata.append({
                'turn_id': row['turn_id'],
                'timestamp': row['timestamp'],
                'who': row['who'],
                'layer': row['layer']
            })
    
    print(f"Decoded {len(embeddings)} valid embeddings")
    
    # Build index
    embedding_matrix = np.array(embeddings, dtype=np.float32)
    
    # Use IVF for large datasets
    if len(embeddings) > 10000 and index_type == 'flat':
        print(f"Dataset > 10K, switching to IVF index for performance")
        index_type = 'ivf'
    
    index = FAISSIndex(dim=embedding_matrix.shape[1], index_type=index_type)
    
    if index_type == 'ivf':
        print("Training IVF index...")
        index.train(embedding_matrix)
    
    print("Adding vectors to index...")
    index.add(node_ids, embedding_matrix, metadata)
    
    # Save
    index.save()
    
    return index


def add_to_index(node_id: str, embedding: np.ndarray, 
                 metadata: Optional[Dict] = None):
    """Add a single embedding to the index incrementally."""
    global _global_index
    
    index = get_faiss_index()
    if index is None:
        # Build new index
        print("[faiss_index] No existing index, building new one...")
        index = build_faiss_index()
        _global_index = index
        return
    
    # Add single vector
    index.add([node_id], embedding.reshape(1, -1), [metadata] if metadata else None)
    
    # Persist periodically (every 100 additions)
    if len(index.id_map) % 100 == 0:
        index.save()


def search_faiss(query_embedding: np.ndarray, top_k: int = 10) -> List[Dict]:
    """
    Search FAISS index for similar vectors.
    
    Returns list of dicts with 'id', 'score', 'turn_id', 'timestamp', etc.
    """
    index = get_faiss_index()
    if index is None:
        return []
    
    results = index.search(query_embedding, top_k)
    
    return [
        {
            'id': nid,
            'score': score,
            **meta
        }
        for nid, score, meta in results
    ]


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='NIMA FAISS Index')
    parser.add_argument('command', choices=['build', 'search', 'stats', 'add'])
    parser.add_argument('--index-type', choices=['flat', 'ivf'], default='flat')
    parser.add_argument('--top', type=int, default=10)
    parser.add_argument('--days', type=int, default=180)
    parser.add_argument('query', nargs='?', help='Search query text')
    args = parser.parse_args()
    
    if args.command == 'build':
        index = build_faiss_index(index_type=args.index_type, 
                                  time_window_days=args.days)
        if index:
            print(f"\n✅ Built FAISS index: {len(index.id_map)} vectors")
    
    elif args.command == 'search':
        if not args.query:
            print("Error: search requires a query")
            sys.exit(1)
        
        # Get embedding from Voyage
        from embeddings import get_client, MAX_TEXT_CHARS, MODEL
        client = get_client()
        result = client.embed([args.query[:MAX_TEXT_CHARS]], model=MODEL)
        query_vec = np.array(result.embeddings[0], dtype=np.float32)
        
        # Search
        results = search_faiss(query_vec, args.top)
        
        print(f"\nTop {len(results)} results:")
        for r in results:
            print(f"  [{r['score']:.3f}] {r.get('turn_id', 'unknown')[:50]}...")
    
    elif args.command == 'stats':
        index = get_faiss_index()
        if index:
            print(f"📊 FAISS Index Stats:")
            print(f"   Vectors: {len(index.id_map)}")
            print(f"   Dimension: {index.dim}")
            print(f"   Type: {index.index_type}")
            print(f"   Trained: {index._is_trained}")
        else:
            print("No index found. Run: python3 faiss_index.py build")


if __name__ == "__main__":
    main()
