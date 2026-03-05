#!/usr/bin/env python3
"""
mem-warm: Moves buffered turns from Redis into Qdrant watts_warm collection.
Runs via cron every 30 minutes. Chunks conversations into searchable blocks.

Each chunk = ~5-10 turns grouped by session, embedded as a single unit.
Warm memories auto-expire after 7 days (cleaned by mem-curate).
"""

import json
import os
import sys
import uuid
import redis
from datetime import datetime, timezone
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Add parent dir to path for shared modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embeddings import get_embedding, content_hash

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY = "mem:watts:turns"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
WARM_COLLECTION = "watts_warm"

# Chunk size: group turns into blocks for embedding
CHUNK_SIZE = 8  # turns per chunk
MAX_CHUNK_CHARS = 3000  # max chars per chunk text


def drain_redis(r: redis.Redis) -> list[dict]:
    """Atomically drain all turns from Redis buffer."""
    turns = []
    # Use pipeline to atomically get and clear
    pipe = r.pipeline()
    pipe.lrange(REDIS_KEY, 0, -1)
    pipe.delete(REDIS_KEY)
    results = pipe.execute()
    
    raw_turns = results[0]
    for raw in raw_turns:
        try:
            turns.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    
    return turns


def chunk_turns(turns: list[dict]) -> list[dict]:
    """Group turns into chunks by session, ready for embedding."""
    # Group by session_id
    sessions = {}
    for turn in turns:
        sid = turn.get("session_id", "unknown")
        if sid not in sessions:
            sessions[sid] = []
        sessions[sid].append(turn)
    
    chunks = []
    for session_id, session_turns in sessions.items():
        # Sort by timestamp
        session_turns.sort(key=lambda t: t.get("timestamp", ""))
        
        # Split into chunks of CHUNK_SIZE
        for i in range(0, len(session_turns), CHUNK_SIZE):
            batch = session_turns[i:i + CHUNK_SIZE]
            
            # Build chunk text
            lines = []
            for turn in batch:
                role = turn.get("role", "unknown")
                text = turn.get("text", "").strip()
                if text:
                    lines.append(f"[{role}] {text}")
            
            chunk_text = "\n".join(lines)
            if not chunk_text.strip():
                continue
            
            # Truncate if too long
            if len(chunk_text) > MAX_CHUNK_CHARS:
                chunk_text = chunk_text[:MAX_CHUNK_CHARS] + "..."
            
            # Get timestamp range
            timestamps = [t.get("timestamp", "") for t in batch if t.get("timestamp")]
            first_ts = min(timestamps) if timestamps else datetime.now(timezone.utc).isoformat()
            last_ts = max(timestamps) if timestamps else first_ts
            
            # Extract date
            try:
                date_str = first_ts[:10]
            except (IndexError, TypeError):
                date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            # Detect channel from session_id
            channel = "unknown"
            if "discord" in session_id:
                channel = "discord"
            elif "slack" in session_id:
                channel = "slack"
            elif "main" in session_id:
                channel = "main"
            elif "cron" in session_id:
                channel = "cron"
            
            chunks.append({
                "text": chunk_text,
                "session_id": session_id,
                "channel": channel,
                "date": date_str,
                "timestamp_start": first_ts,
                "timestamp_end": last_ts,
                "turn_count": len(batch),
                "content_hash": content_hash(chunk_text),
            })
    
    return chunks


def store_chunks(client: QdrantClient, chunks: list[dict]) -> int:
    """Embed and store chunks to Qdrant watts_warm."""
    points = []
    
    for chunk in chunks:
        try:
            vector = get_embedding(chunk["text"])
        except Exception as e:
            print(f"  ⚠️  Embedding failed: {e}", file=sys.stderr)
            continue
        
        # Parse timestamp for float index
        try:
            ts = datetime.fromisoformat(chunk["timestamp_start"].replace("Z", "+00:00"))
            ts_float = ts.timestamp()
        except (ValueError, AttributeError):
            ts_float = datetime.now(timezone.utc).timestamp()
        
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "text": chunk["text"],
                "session_id": chunk["session_id"],
                "channel": chunk["channel"],
                "date": chunk["date"],
                "timestamp": ts_float,
                "timestamp_start": chunk["timestamp_start"],
                "timestamp_end": chunk["timestamp_end"],
                "turn_count": chunk["turn_count"],
                "content_hash": chunk["content_hash"],
                "stored_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        points.append(point)
    
    if points:
        # Batch upsert
        batch_size = 50
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(collection_name=WARM_COLLECTION, points=batch)
    
    return len(points)


def main():
    print(f"⚡ mem-warm: Processing Redis buffer → Qdrant {WARM_COLLECTION}")
    
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # Check buffer size
    buffer_size = r.llen(REDIS_KEY)
    if buffer_size == 0:
        print("  No turns in buffer. Nothing to do.")
        return
    
    print(f"  Buffer: {buffer_size} turns")
    
    # Drain buffer
    turns = drain_redis(r)
    print(f"  Drained: {len(turns)} turns")
    
    # Chunk
    chunks = chunk_turns(turns)
    print(f"  Chunked: {len(chunks)} chunks")
    
    # Store
    stored = store_chunks(client, chunks)
    print(f"  Stored: {stored} chunks to {WARM_COLLECTION}")
    
    # Report
    info = client.get_collection(WARM_COLLECTION)
    print(f"  Collection total: {info.points_count} points")
    print("  ✅ Done")


if __name__ == "__main__":
    main()
