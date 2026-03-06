"""
Storage Core - Multi-agent ChromaDB initialization

This module provides ChromaDB client initialization with agent-specific paths.
"""
import chromadb
from pathlib import Path
from typing import Optional

# Import config
import sys
from pathlib import Path as PathLib

# Add parent directory to path for imports
_config_path = PathLib(__file__).parent.parent
if str(_config_path) not in sys.path:
    sys.path.insert(0, str(_config_path))

from config import (
    AGENT_ID,
    CHROMA_SHARED,
    CHROMA_PRIVATE,
    get_chroma_path,
    get_chroma_collection,
    CHROMA,
)


class ChromaClient:
    """
    Multi-agent ChromaDB client with shared/private path support.
    """
    
    def __init__(self, use_shared: bool = False):
        """
        Initialize ChromaDB client.
        
        Args:
            use_shared: If True, use shared storage. If False, use agent-private storage.
        """
        self.use_shared = use_shared
        self.path = get_chroma_path(use_shared=use_shared)
        self.client: Optional[chromadb.PersistentClient] = None
        self._connect()
    
    def _connect(self):
        """Connect to ChromaDB."""
        self.path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.path))
    
    def get_collection(self, name: str) -> chromadb.Collection:
        """
        Get or create a collection.
        
        Args:
            name: Collection name.
        
        Returns:
            ChromaDB collection.
        """
        # Namespace private collections with agent_id
        if self.use_shared:
            full_name = name
        else:
            full_name = f"{AGENT_ID}_{name}"
        
        return self.client.get_or_create_collection(name=full_name)
    
    def __repr__(self):
        return f"ChromaClient(path={self.path}, agent={AGENT_ID}, shared={self.use_shared})"


# Default client (agent-private)
_default_client: Optional[ChromaClient] = None


def get_client(use_shared: bool = False) -> ChromaClient:
    """
    Get a ChromaDB client instance.
    
    Args:
        use_shared: If True, return shared storage client. If False, return private.
    
    Returns:
        ChromaClient instance.
    """
    return ChromaClient(use_shared=use_shared)


def get_default_client() -> ChromaClient:
    """
    Get the default agent-private ChromaDB client.
    
    Returns:
        ChromaClient instance for agent-private storage.
    """
    global _default_client
    if _default_client is None:
        _default_client = ChromaClient(use_shared=False)
    return _default_client


# Convenience functions matching config.py API
def get_chroma_path_fn(use_shared: bool = True) -> Path:
    """Alias for get_chroma_path from config."""
    return get_chroma_path(use_shared)


def get_collection(collection_name: str, use_shared: bool = False):
    """Alias for get_chroma_collection from config."""
    return get_chroma_collection(collection_name, use_shared)
