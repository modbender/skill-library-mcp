#!/usr/bin/env python3
"""
Auto-Retrieve: Pre-response memory injection hook.

Queries ChromaDB (vector search) and NetworkX (graph traversal) for a given
query and returns formatted context ready for system prompt injection.

Usage:
    # As CLI (for OpenClaw heartbeat/scripts):
    python3 vector_memory/auto_retrieve.py "query text here"
    
    # As module:
    from vector_memory.auto_retrieve import auto_retrieve
    context = auto_retrieve("query text here")

Returns formatted markdown block with:
- Top-k vector search results (semantic similarity)
- Related graph nodes and edges (relationship context)
- Memory system status (sync health)

This makes memory retrieval INFRASTRUCTURE-LEVEL, not agent-discretionary.
Inspired by: MemOS scheduler, LangGraph pre-model hooks, Mem0 auto-search.
"""

import os
import sys
import json
import hashlib
from datetime import datetime

# Resolve paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)
MEMORY_MD = os.path.join(WORKSPACE_DIR, "MEMORY.md")
GRAPH_PATH = os.path.join(SCRIPT_DIR, "memory_graph.json")
HEARTBEAT_PATH = os.path.join(WORKSPACE_DIR, "memory", "heartbeat-state.json")
CHROMA_DB_PATH = os.path.join(SCRIPT_DIR, "chroma_db")

# Add venv to path for imports
VENV_SITE = os.path.join(SCRIPT_DIR, "venv", "lib")
if os.path.exists(VENV_SITE):
    for d in os.listdir(VENV_SITE):
        sp = os.path.join(VENV_SITE, d, "site-packages")
        if os.path.isdir(sp) and sp not in sys.path:
            sys.path.insert(0, sp)


def get_memory_md_hash():
    """Get MD5 hash of MEMORY.md for sync checking."""
    try:
        with open(MEMORY_MD, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:12]
    except FileNotFoundError:
        return "missing"


def query_chromadb(query_text, n_results=5):
    """Semantic vector search via ChromaDB + SentenceTransformers."""
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection("memory_chunks")

        query_embedding = model.encode([query_text]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        entries = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                dist = results["distances"][0][i] if results["distances"] else None
                # Lower distance = more relevant (L2 distance)
                relevance = f"(dist: {dist:.3f})" if dist is not None else ""
                section = meta.get("section", "unknown")
                # Only include reasonably relevant results
                if dist is not None and dist > 2.0:
                    continue
                entries.append({
                    "section": section,
                    "snippet": doc[:300] + "..." if len(doc) > 300 else doc,
                    "relevance": relevance
                })

        return {
            "count": collection.count(),
            "results": entries
        }
    except Exception as e:
        return {"count": 0, "results": [], "error": str(e)}


def query_graph(query_text, max_nodes=10):
    """Traverse knowledge graph for related concepts."""
    try:
        import networkx as nx

        if not os.path.exists(GRAPH_PATH):
            return {"nodes": 0, "edges": 0, "related": [], "error": "graph not found"}

        with open(GRAPH_PATH, "r") as f:
            data = json.load(f)

        G = nx.node_link_graph(data)
        total_nodes = G.number_of_nodes()
        total_edges = G.number_of_edges()

        # Find nodes whose names match query keywords
        query_words = set(query_text.lower().split())
        matched_nodes = []
        for node in G.nodes():
            node_lower = node.lower()
            # Score by keyword overlap
            score = sum(1 for w in query_words if w in node_lower)
            if score > 0:
                matched_nodes.append((node, score))

        matched_nodes.sort(key=lambda x: -x[1])
        matched_nodes = matched_nodes[:max_nodes]

        # Get neighbors for matched nodes
        related = []
        for node, score in matched_nodes:
            neighbors = []
            for neighbor in G.neighbors(node):
                edge_data = G.get_edge_data(node, neighbor, default={})
                edge_type = edge_data.get("type", "related")
                neighbors.append(f"{neighbor} ({edge_type})")
            related.append({
                "node": node,
                "score": score,
                "neighbors": neighbors[:5]
            })

        return {
            "nodes": total_nodes,
            "edges": total_edges,
            "related": related
        }
    except Exception as e:
        return {"nodes": 0, "edges": 0, "related": [], "error": str(e)}


def get_sync_status():
    """Check memory sync health."""
    current_hash = get_memory_md_hash()
    
    try:
        with open(HEARTBEAT_PATH, "r") as f:
            state = json.load(f)
        sync = state.get("memorySync", {})
        stored_hash = sync.get("memoryMdHash")
        
        if stored_hash and stored_hash != current_hash:
            status = "OUT_OF_SYNC"
        else:
            status = sync.get("status", "unknown")
        
        return {
            "status": status,
            "memoryMdHash": current_hash,
            "storedHash": stored_hash,
            "lastSync": sync.get("lastSync", "never"),
            "chromadbChunks": sync.get("chromadbChunks", "?"),
            "graphNodes": sync.get("graphNodes", "?"),
            "graphEdges": sync.get("graphEdges", "?")
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "status": "unknown",
            "memoryMdHash": current_hash,
            "lastSync": "never"
        }


def update_sync_status(chromadb_count, graph_nodes, graph_edges):
    """Update heartbeat-state.json with current sync info."""
    try:
        try:
            with open(HEARTBEAT_PATH, "r") as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {"lastChecks": {}}
        
        state["memorySync"] = {
            "memoryMdHash": get_memory_md_hash(),
            "chromadbChunks": chromadb_count,
            "graphNodes": graph_nodes,
            "graphEdges": graph_edges,
            "lastSync": datetime.now().astimezone().isoformat(),
            "status": "synced"
        }
        
        with open(HEARTBEAT_PATH, "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass  # Non-critical


def auto_retrieve(query_text, n_results=5):
    """
    Main entry point: auto-retrieve memory context for a query.
    Returns formatted markdown ready for system prompt injection.
    """
    vector = query_chromadb(query_text, n_results)
    graph = query_graph(query_text)
    sync = get_sync_status()

    lines = []
    lines.append("## 🧠 Auto-Retrieved Memory Context")
    lines.append(f"**Query:** {query_text}")
    lines.append(f"**Sync Status:** {sync['status']} | MEMORY.md hash: {sync.get('memoryMdHash', '?')} | Last sync: {sync.get('lastSync', 'never')}")
    lines.append("")

    # Vector results
    lines.append(f"### Vector Search (ChromaDB — {vector.get('count', '?')} chunks indexed)")
    if vector.get("error"):
        lines.append(f"⚠️ Error: {vector['error']}")
    elif vector["results"]:
        for r in vector["results"]:
            lines.append(f"- **[{r['section']}]** {r['relevance']}")
            lines.append(f"  {r['snippet']}")
    else:
        lines.append("No relevant results found.")
    lines.append("")

    # Graph results
    lines.append(f"### Knowledge Graph (NetworkX — {graph.get('nodes', '?')} nodes, {graph.get('edges', '?')} edges)")
    if graph.get("error"):
        lines.append(f"⚠️ Error: {graph['error']}")
    elif graph["related"]:
        for r in graph["related"]:
            neighbors_str = ", ".join(r["neighbors"][:5]) if r["neighbors"] else "no direct neighbors"
            lines.append(f"- **{r['node']}** → {neighbors_str}")
    else:
        lines.append("No matching graph nodes found.")
    lines.append("")

    # Sync warning
    if sync["status"] == "OUT_OF_SYNC":
        lines.append("### ⚠️ MEMORY OUT OF SYNC")
        lines.append("MEMORY.md has changed since last index. Run: `vector_memory/venv/bin/python vector_memory/indexer.py`")
        lines.append("")

    return "\n".join(lines)


def format_compact(query_text, n_results=3):
    """
    Compact version for token-constrained contexts.
    Returns just the key facts, no formatting.
    """
    vector = query_chromadb(query_text, n_results)
    graph = query_graph(query_text, max_nodes=5)
    
    lines = []
    if vector["results"]:
        for r in vector["results"]:
            lines.append(f"[{r['section']}] {r['snippet'][:150]}")
    if graph["related"]:
        for r in graph["related"]:
            neighbors = ", ".join(r["neighbors"][:3])
            lines.append(f"Graph: {r['node']} → {neighbors}")
    
    return "\n".join(lines) if lines else "No relevant memories found."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 auto_retrieve.py 'query text'")
        print("       python3 auto_retrieve.py --compact 'query text'")
        print("       python3 auto_retrieve.py --status")
        sys.exit(1)

    if sys.argv[1] == "--status":
        sync = get_sync_status()
        vector = query_chromadb("test", 1)
        graph = query_graph("test", 1)
        print(f"Memory Sync Status: {sync['status']}")
        print(f"  MEMORY.md hash: {sync.get('memoryMdHash', '?')}")
        print(f"  ChromaDB chunks: {vector.get('count', '?')}")
        print(f"  Graph nodes: {graph.get('nodes', '?')}, edges: {graph.get('edges', '?')}")
        print(f"  Last sync: {sync.get('lastSync', 'never')}")
        # Update sync state
        update_sync_status(
            vector.get("count", 0),
            graph.get("nodes", 0),
            graph.get("edges", 0)
        )
        sys.exit(0)

    compact = False
    query = sys.argv[1]
    if query == "--compact":
        compact = True
        query = sys.argv[2] if len(sys.argv) > 2 else ""

    if compact:
        print(format_compact(query))
    else:
        print(auto_retrieve(query))
