"""
Memory System V2 - Configuration
"""
import os
from pathlib import Path

# Get agent ID from environment (defaults to 'default' if not set)
AGENT_ID = os.environ.get("AGENT_ID", "default")

# Base paths
HOME = Path.home()
MEMORY_ROOT = HOME / ".openclaw" / "memory"
SYSTEM_ROOT = HOME / ".openclaw" / "workspace-cody" / "memory-system-v2"

# Storage tiers
PATHS = {
    "core": MEMORY_ROOT / "core",
    "recent": MEMORY_ROOT / "daily",
    "cache": HOME / ".cache" / "memory-v2",
}

# ChromaDB config - Hybrid shared/private setup
CHROMA = {
    "url": os.getenv("CHROMA_URL", "http://localhost:8100"),
    "collection": "memory-v2",
    # Hybrid paths
    "shared": MEMORY_ROOT / "chroma_shared",
    "private": MEMORY_ROOT / f"chroma_{AGENT_ID}",
}

# ChromaDB paths for multi-agent setup
CHROMA_SHARED = MEMORY_ROOT / "chroma_shared"
CHROMA_PRIVATE = MEMORY_ROOT / f"chroma_{AGENT_ID}"


def get_chroma_path(use_shared: bool = True) -> Path:
    """
    Get ChromaDB path - shared or private based on use_shared flag.
    
    Args:
        use_shared: If True, return shared path. If False, return private path.
    
    Returns:
        Path to the ChromaDB directory (shared or agent-private).
    """
    if use_shared:
        return CHROMA_SHARED
    return CHROMA_PRIVATE


def get_chroma_collection(collection_name: str, use_shared: bool = False):
    """
    Get a ChromaDB collection with agent-specific namespace.
    
    Args:
        collection_name: Name of the collection (e.g., 'preferences', 'memory').
        use_shared: If True, use shared storage. If False, use private storage.
    
    Returns:
        ChromaDB collection object.
    """
    import chromadb
    
    path = get_chroma_path(use_shared=use_shared)
    # Ensure the directory exists
    path.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(path))
    
    # Namespace collection name with agent_id for private, no namespace for shared
    if use_shared:
        full_collection_name = collection_name
    else:
        full_collection_name = f"{AGENT_ID}_{collection_name}"
    
    return client.get_or_create_collection(name=full_collection_name)


# Ollama config
OLLAMA = {
    "url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
    "embedding_model": "bge-m3",
}

# Capture config
CAPTURE = {
    "sqlite_dir": HOME / ".openclaw" / "memory",
    "poll_interval": 300,  # 5 minutes
    "event_hooks": [],
}

# Processing config
PROCESS = {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "min_chunk_size": 50,
    "dedupe_threshold": 0.9,
}

# Retrieval config
RETRIEVAL = {
    "cache_ttl": 3600,  # 1 hour
    "max_results": 10,
    "min_relevance": 0.5,
    "fallback_chain": ["semantic", "recent", "core"],
}

# State file
STATE_FILE = SYSTEM_ROOT / "state.json"

# Ensure directories exist
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)

PATHS["cache"].mkdir(parents=True, exist_ok=True)

# Ensure ChromaDB directories exist
CHROMA_SHARED.mkdir(parents=True, exist_ok=True)
CHROMA_PRIVATE.mkdir(parents=True, exist_ok=True)
