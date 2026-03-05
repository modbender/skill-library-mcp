#!/usr/bin/env python3
"""
Setup Qdrant collections for Watts Memory V2.
Creates watts_warm (mid-term) and watts_cold (long-term curated) collections.
Preserves existing watts_memories as archive.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, 
    PayloadSchemaType,
)

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBEDDING_DIM = 1024  # snowflake-arctic-embed2

def setup():
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # --- watts_warm: mid-term session dumps (7-day retention) ---
    if not client.collection_exists("watts_warm"):
        client.create_collection(
            collection_name="watts_warm",
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        # Create payload indexes for fast filtering
        client.create_payload_index("watts_warm", "date", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_warm", "session_id", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_warm", "channel", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_warm", "timestamp", PayloadSchemaType.FLOAT)
        print("✅ Created watts_warm collection")
    else:
        print("ℹ️  watts_warm already exists")

    # --- watts_cold: long-term curated gems ---
    if not client.collection_exists("watts_cold"):
        client.create_collection(
            collection_name="watts_cold",
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        # Create payload indexes
        client.create_payload_index("watts_cold", "date", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_cold", "categories", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_cold", "project", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_cold", "people", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_cold", "importance", PayloadSchemaType.KEYWORD)
        client.create_payload_index("watts_cold", "timestamp", PayloadSchemaType.FLOAT)
        print("✅ Created watts_cold collection")
    else:
        print("ℹ️  watts_cold already exists")

    # Show status of all memory collections
    print("\n📊 Memory Collections:")
    for name in ["watts_memories", "watts_warm", "watts_cold"]:
        if client.collection_exists(name):
            info = client.get_collection(name)
            print(f"  {name}: {info.points_count} points ({info.status})")
        else:
            print(f"  {name}: not found")

if __name__ == "__main__":
    setup()
