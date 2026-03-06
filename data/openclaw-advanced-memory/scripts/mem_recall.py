#!/usr/bin/env python3
"""
mem-recall: Unified search across warm (recent) and cold (curated) memory tiers.
Searches both collections, ranks by relevance + recency, returns structured results.

Usage:
    python3 mem_recall.py "what did we decide about pricing"
    python3 mem_recall.py "pricing" --date 2026-02-15
    python3 mem_recall.py "Bryan minecraft" --category person
    python3 mem_recall.py "Guardian deployment" --tier cold --limit 10
"""

import argparse
import json
import os
import sys
import math
from datetime import datetime, timezone, timedelta
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embeddings import get_embedding

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
WARM_COLLECTION = "watts_warm"
COLD_COLLECTION = "watts_cold"

# Recency decay: halve relevance score every N days
RECENCY_HALF_LIFE_DAYS = 30


def recency_boost(timestamp: float, half_life_days: float = RECENCY_HALF_LIFE_DAYS) -> float:
    """Calculate recency boost factor (1.0 = now, decays over time)."""
    now = datetime.now(timezone.utc).timestamp()
    age_days = (now - timestamp) / 86400
    if age_days < 0:
        age_days = 0
    return math.exp(-0.693 * age_days / half_life_days)


def search_warm(client: QdrantClient, query_vector: list[float], 
                limit: int = 10, date_filter: str = None) -> list[dict]:
    """Search warm (recent) memories."""
    filters = []
    if date_filter:
        filters.append(FieldCondition(key="date", match=MatchValue(value=date_filter)))
    
    search_filter = Filter(must=filters) if filters else None
    
    results = client.query_points(
        collection_name=WARM_COLLECTION,
        query=query_vector,
        query_filter=search_filter,
        limit=limit,
        with_payload=True,
    ).points
    
    memories = []
    for result in results:
        ts = result.payload.get("timestamp", 0)
        boost = recency_boost(ts)
        
        memories.append({
            "tier": "warm",
            "text": result.payload.get("text", ""),
            "date": result.payload.get("date", ""),
            "channel": result.payload.get("channel", ""),
            "session_id": result.payload.get("session_id", ""),
            "score": result.score,
            "boosted_score": result.score * (1 + boost * 0.5),
            "timestamp": ts,
        })
    
    return memories


def search_cold(client: QdrantClient, query_vector: list[float],
                limit: int = 10, date_filter: str = None,
                category_filter: str = None, project_filter: str = None,
                person_filter: str = None) -> list[dict]:
    """Search cold (curated) memories."""
    filters = []
    if date_filter:
        filters.append(FieldCondition(key="date", match=MatchValue(value=date_filter)))
    if category_filter:
        filters.append(FieldCondition(key="categories", match=MatchValue(value=category_filter)))
    if project_filter:
        filters.append(FieldCondition(key="project", match=MatchValue(value=project_filter)))
    if person_filter:
        filters.append(FieldCondition(key="people", match=MatchValue(value=person_filter)))
    
    search_filter = Filter(must=filters) if filters else None
    
    results = client.query_points(
        collection_name=COLD_COLLECTION,
        query=query_vector,
        query_filter=search_filter,
        limit=limit,
        with_payload=True,
    ).points
    
    memories = []
    for result in results:
        ts = result.payload.get("timestamp", 0)
        boost = recency_boost(ts)
        
        # Importance bonus
        imp = result.payload.get("importance", "medium")
        imp_bonus = {"high": 0.15, "medium": 0.05, "low": 0.0}.get(imp, 0.05)
        
        memories.append({
            "tier": "cold",
            "gem": result.payload.get("gem", ""),
            "context": result.payload.get("context", ""),
            "date": result.payload.get("date", ""),
            "categories": result.payload.get("categories", []),
            "project": result.payload.get("project"),
            "people": result.payload.get("people", []),
            "importance": imp,
            "confidence": result.payload.get("confidence", 0.8),
            "score": result.score,
            "boosted_score": result.score * (1 + boost * 0.3) + imp_bonus,
            "timestamp": ts,
        })
    
    return memories


def unified_search(query: str, limit: int = 10, tier: str = "both",
                   date_filter: str = None, category_filter: str = None,
                   project_filter: str = None, person_filter: str = None) -> list[dict]:
    """Search across both memory tiers, return ranked results."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    query_vector = get_embedding(query)
    
    results = []
    
    if tier in ("both", "warm"):
        warm = search_warm(client, query_vector, limit=limit, date_filter=date_filter)
        results.extend(warm)
    
    if tier in ("both", "cold"):
        cold = search_cold(client, query_vector, limit=limit,
                          date_filter=date_filter, category_filter=category_filter,
                          project_filter=project_filter, person_filter=person_filter)
        results.extend(cold)
    
    # Sort by boosted score
    results.sort(key=lambda r: r["boosted_score"], reverse=True)
    
    return results[:limit]


def format_result(mem: dict, verbose: bool = False) -> str:
    """Format a single memory result for display."""
    tier = mem["tier"]
    score = mem["boosted_score"]
    date = mem.get("date", "?")
    
    if tier == "cold":
        gem = mem.get("gem", "")
        ctx = mem.get("context", "")
        cats = ", ".join(mem.get("categories", []))
        imp = mem.get("importance", "?")
        project = mem.get("project", "")
        people = ", ".join(mem.get("people", []))
        
        line = f"  🧊 [{score:.3f}] [{date}] [{imp}] {gem}"
        if verbose:
            if ctx:
                line += f"\n     Context: {ctx}"
            if cats:
                line += f"\n     Tags: {cats}"
            if project:
                line += f" | Project: {project}"
            if people:
                line += f" | People: {people}"
        return line
    else:
        text = mem.get("text", "")[:200]
        channel = mem.get("channel", "?")
        
        line = f"  🔥 [{score:.3f}] [{date}] [{channel}] {text}"
        return line


def main():
    parser = argparse.ArgumentParser(description="Search Watts memory")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    parser.add_argument("--tier", choices=["both", "warm", "cold"], default="both")
    parser.add_argument("--date", "-d", help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--project", "-p", help="Filter by project")
    parser.add_argument("--person", help="Filter by person")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    print(f"🔍 Searching: \"{args.query}\"")
    if args.tier != "both":
        print(f"   Tier: {args.tier}")
    
    results = unified_search(
        query=args.query,
        limit=args.limit,
        tier=args.tier,
        date_filter=args.date,
        category_filter=args.category,
        project_filter=args.project,
        person_filter=args.person,
    )
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
        return
    
    if not results:
        print("  No memories found.")
        return
    
    warm_count = sum(1 for r in results if r["tier"] == "warm")
    cold_count = sum(1 for r in results if r["tier"] == "cold")
    print(f"   Found: {len(results)} results ({cold_count} curated 🧊, {warm_count} recent 🔥)\n")
    
    for mem in results:
        print(format_result(mem, verbose=args.verbose))


if __name__ == "__main__":
    main()
