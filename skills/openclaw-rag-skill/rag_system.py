#!/usr/bin/env python3
"""
OpenClaw RAG System - Core Library
Manages vector store, ingestion, and retrieval with ChromaDB
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class RAGSystem:
    """OpenClaw RAG System for knowledge retrieval"""

    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = "openclaw_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize RAG system

        Args:
            persist_directory: Where ChromaDB stores data
            collection_name: Name of the collection
            embedding_model: Embedding model name ( ChromaDB handles this)
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed. Run: pip3 install chromadb")

        self.collection_name = collection_name

        # Default to ~/.openclaw/data/rag if not specified
        if persist_directory is None:
            persist_directory = os.path.expanduser("~/.openclaw/data/rag")

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "created": datetime.now().isoformat(),
                "description": "OpenClaw knowledge base"
            }
        )

    def add_document(
        self,
        text: str,
        metadata: Dict,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the vector store

        Args:
            text: Document content
            metadata: Document metadata (type, source, date, etc.)
            doc_id: Optional document ID (auto-generated if not provided)

        Returns:
            Document ID
        """
        # Generate ID if not provided (include more context for uniqueness)
        if doc_id is None:
            unique_str = ":".join([
                metadata.get('type', 'unknown'),
                metadata.get('source', 'unknown'),
                metadata.get('date', datetime.now().isoformat()),
                str(metadata.get('chunk_index', '0')),  # Convert to string!
                text[:200]
            ])
            doc_id = hashlib.md5(unique_str.encode()).hexdigest()

        # Add to collection
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

        return doc_id

    def add_documents_batch(
        self,
        documents: List[Dict],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add multiple documents efficiently

        Args:
            documents: List of {"text": str, "metadata": dict, "id": optional} dicts
            batch_size: Number of documents to add per batch

        Returns:
            List of document IDs
        """
        all_ids = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            texts = [doc["text"] for doc in batch]
            metadatas = [doc["metadata"] for doc in batch]
            ids = [doc.get("id", hashlib.md5(
                f"{doc['metadata'].get('type', 'unknown')}:{doc['metadata'].get('source', 'unknown')}:{doc['metadata'].get('date', '')}:{str(doc['metadata'].get('chunk_index', '0'))}:{doc['text'][:100]}".encode()
            ).hexdigest()) for doc in batch]

            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            all_ids.extend(ids)
            print(f"✅ Added batch {i//batch_size + 1}: {len(ids)} documents")

        return all_ids

    def search(
        self,
        query: str,
        n_results: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for relevant documents

        Args:
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of {"text": str, "metadata": dict, "id": str, "score": float} dicts
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filters
        )

        # Format results
        formatted = []
        for i, doc_id in enumerate(results['ids'][0]):
            formatted.append({
                "id": doc_id,
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                # Note: ChromaDB doesn't return scores by default in query()
                # We'd need to use a different method or approximate
                "score": 1.0 - (i / len(results['ids'][0]))  # Simple approximation
            })

        return formatted

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"❌ Error deleting document {doc_id}: {e}")
            return False

    def delete_by_filter(self, filter_dict: Dict) -> int:
        """
        Delete documents by metadata filter

        Args:
            filter_dict: Filter criteria (e.g., {"source": "session-2026-02-10"})

        Returns:
            Number of documents deleted
        """
        # First, find matching IDs
        results = self.collection.get(where=filter_dict)

        if not results['ids']:
            return 0

        count = len(results['ids'])
        self.collection.delete(ids=results['ids'])

        print(f"✅ Deleted {count} documents matching filter")
        return count

    def get_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()

        # Get sample to understand metadata structure
        sample = self.collection.get(limit=10)

        # Count by source/type
        source_counts = {}
        type_counts = {}

        for metadata in sample['metadatas']:
            source = metadata.get('source', 'unknown')
            doc_type = metadata.get('type', 'unknown')

            source_counts[source] = source_counts.get(source, 0) + 1
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

        return {
            "total_documents": count,
            "collection_name": self.collection_name,
            "persist_directory": str(self.persist_directory),
            "source_distribution": source_counts,
            "type_distribution": type_counts
        }

    def reset_collection(self):
        """Delete all documents and reset the collection"""
        self.collection.delete(where={})
        print("✅ Collection reset - all documents deleted")

    def close(self):
        """Close the connection"""
        # ChromaDB PersistentClient doesn't need explicit close
        pass


def main():
    """Test the RAG system"""
    print("🚀 Testing OpenClaw RAG System...\n")

    # Initialize
    rag = RAGSystem()
    print(f"✅ Initialized RAG system")
    print(f"   Collection: {rag.collection_name}")
    print(f"   Storage: {rag.persist_directory}\n")

    # Add test document
    test_doc = {
        "text": "OpenClaw is a personal AI assistant with tools for automation, messaging, and infrastructure management. It supports Discord, Telegram, SMS via VoIP.ms, and more.",
        "metadata": {
            "type": "test",
            "source": "test-initialization",
            "date": datetime.now().isoformat()
        }
    }

    doc_id = rag.add_document(test_doc["text"], test_doc["metadata"])
    print(f"✅ Added test document: {doc_id}\n")

    # Search
    results = rag.search(
        query="What messaging platforms does OpenClaw support?",
        n_results=5
    )

    print("🔍 Search Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. [{result['metadata'].get('source', '?')}]")
        print(f"   {result['text'][:200]}...")

    # Stats
    stats = rag.get_stats()
    print(f"\n📊 Stats:")
    print(f"   Total documents: {stats['total_documents']}")


if __name__ == "__main__":
    main()