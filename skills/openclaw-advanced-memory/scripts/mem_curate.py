#!/usr/bin/env python3
"""
mem-curate: Nightly curation of warm memories into cold (long-term) gems.
Uses an LLM (via Ollama on TrueNAS) to read warm memories and extract
structured gems for permanent storage.

Also cleans up warm memories older than 7 days.
Runs via cron at 2 AM daily.
"""

import json
import os
import sys
import uuid
import time
import requests
from datetime import datetime, timezone, timedelta
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, Range

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embeddings import get_embedding, content_hash

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
WARM_COLLECTION = "watts_warm"
COLD_COLLECTION = "watts_cold"

# LLM for curation — qwen2.5:7b on TrueNAS (CPU, always-on)
# Tested: 7b extracts more gems and fills metadata better than 14b
# Speed: ~65s per day's curation — runs at 2 AM so speed doesn't matter
OLLAMA_HOST = "http://localhost:11434"
CURATOR_MODEL = "qwen2.5:7b"

# Load curator prompt
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CURATOR_PROMPT_FILE = os.path.join(SCRIPT_DIR, "curator_prompt.md")

# Warm memory retention
WARM_RETENTION_DAYS = 7


def load_curator_prompt() -> str:
    """Load the curator system prompt."""
    with open(CURATOR_PROMPT_FILE) as f:
        return f.read()


def get_warm_memories_for_date(client: QdrantClient, date_str: str) -> list[dict]:
    """Get all warm memories for a specific date."""
    results = client.scroll(
        collection_name=WARM_COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="date",
                    match={"value": date_str},
                ),
            ]
        ),
        limit=500,
        with_payload=True,
        with_vectors=False,
    )
    return [point.payload for point in results[0]]


def build_transcript(memories: list[dict]) -> str:
    """Build a readable transcript from warm memories."""
    # Sort by timestamp
    memories.sort(key=lambda m: m.get("timestamp", 0))
    
    parts = []
    for mem in memories:
        session = mem.get("session_id", "unknown")
        channel = mem.get("channel", "unknown")
        text = mem.get("text", "")
        ts_start = mem.get("timestamp_start", "")
        
        header = f"[{ts_start} | {channel} | {session}]"
        parts.append(f"{header}\n{text}")
    
    return "\n\n---\n\n".join(parts)


def curate_with_llm(transcript: str, date_str: str) -> list[dict]:
    """Send transcript to LLM curator and get back gems."""
    system_prompt = load_curator_prompt()
    
    user_prompt = f"""Here is the full conversation transcript for {date_str}. 
Read it holistically and extract the valuable gems worth remembering long-term.

TRANSCRIPT:
{transcript[:30000]}

Return ONLY a JSON array of gems. No other text."""

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": CURATOR_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 4096,
                },
            },
            timeout=300,
        )
        resp.raise_for_status()
        
        content = resp.json()["message"]["content"]
        
        # Parse JSON from response (handle markdown code blocks)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        gems = json.loads(content)
        
        if not isinstance(gems, list):
            print(f"  ⚠️  LLM returned non-list: {type(gems)}", file=sys.stderr)
            return []
        
        return gems
        
    except requests.exceptions.Timeout:
        print("  ⚠️  LLM request timed out", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"  ⚠️  Failed to parse LLM response as JSON: {e}", file=sys.stderr)
        print(f"  Raw response: {content[:500]}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  ⚠️  LLM curation error: {e}", file=sys.stderr)
        return []


def store_gems(client: QdrantClient, gems: list[dict], date_str: str) -> int:
    """Embed and store curated gems to watts_cold."""
    points = []
    
    for gem in gems:
        gem_text = gem.get("gem", "")
        context = gem.get("context", "")
        
        if not gem_text:
            continue
        
        # Embed the gem + context together for better search
        embed_text = f"{gem_text}. {context}"
        
        try:
            vector = get_embedding(embed_text)
        except Exception as e:
            print(f"  ⚠️  Embedding failed for gem: {e}", file=sys.stderr)
            continue
        
        # Parse date to timestamp
        try:
            ts = datetime.strptime(gem.get("date", date_str), "%Y-%m-%d")
            ts_float = ts.replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            ts_float = datetime.now(timezone.utc).timestamp()
        
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "gem": gem_text,
                "context": context,
                "date": gem.get("date", date_str),
                "timestamp": ts_float,
                "categories": gem.get("categories", []),
                "project": gem.get("project"),
                "people": gem.get("people", []),
                "importance": gem.get("importance", "medium"),
                "confidence": gem.get("confidence", 0.8),
                "content_hash": content_hash(gem_text),
                "curated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        points.append(point)
    
    if points:
        client.upsert(collection_name=COLD_COLLECTION, points=points)
    
    return len(points)


def cleanup_old_warm(client: QdrantClient):
    """Remove warm memories older than retention period."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=WARM_RETENTION_DAYS)
    cutoff_ts = cutoff.timestamp()
    
    # Find old points
    old_points = client.scroll(
        collection_name=WARM_COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="timestamp",
                    range=Range(lt=cutoff_ts),
                ),
            ]
        ),
        limit=1000,
        with_payload=False,
        with_vectors=False,
    )
    
    point_ids = [point.id for point in old_points[0]]
    
    if point_ids:
        client.delete(
            collection_name=WARM_COLLECTION,
            points_selector=point_ids,
        )
        print(f"  🧹 Cleaned {len(point_ids)} warm memories older than {WARM_RETENTION_DAYS} days")
    else:
        print(f"  🧹 No warm memories to clean (all within {WARM_RETENTION_DAYS} days)")


def main():
    # Default to yesterday's date (since this runs at 2 AM)
    target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    
    print(f"⚡ mem-curate: Curating warm memories for {target_date}")
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # Get warm memories for target date
    memories = get_warm_memories_for_date(client, target_date)
    
    if not memories:
        print(f"  No warm memories found for {target_date}")
        # Still clean up old warm memories
        cleanup_old_warm(client)
        return
    
    print(f"  Found {len(memories)} warm memory chunks")
    
    # Build transcript
    transcript = build_transcript(memories)
    print(f"  Transcript: {len(transcript)} chars")
    
    # Curate with LLM
    print(f"  Curating with {CURATOR_MODEL}...")
    start = time.time()
    gems = curate_with_llm(transcript, target_date)
    elapsed = time.time() - start
    print(f"  Extracted {len(gems)} gems in {elapsed:.1f}s")
    
    if gems:
        # Store to cold collection
        stored = store_gems(client, gems, target_date)
        print(f"  Stored {stored} gems to {COLD_COLLECTION}")
        
        # Print gems for logging
        for gem in gems:
            imp = gem.get("importance", "?")
            cats = ", ".join(gem.get("categories", []))
            print(f"    [{imp}] [{cats}] {gem.get('gem', '')[:80]}")
    
    # Clean up old warm memories
    cleanup_old_warm(client)
    
    # Report totals
    warm_info = client.get_collection(WARM_COLLECTION)
    cold_info = client.get_collection(COLD_COLLECTION)
    print(f"\n  📊 watts_warm: {warm_info.points_count} | watts_cold: {cold_info.points_count}")
    print("  ✅ Curation complete")


if __name__ == "__main__":
    main()
