#!/usr/bin/env python3
"""
Vestige Integration for overkill-memory-system
Interfaces with vestige-mcp for cognitive memory with spaced repetition.

Requires: vestige-mcp to be installed at ~/bin/vestige-mcp
or available via mcporter.

Vestige is an AI memory system with:
- FSRS-6 spaced repetition
- Dual-strength modeling (importance + recency)
- Forgetting curves
- Semantic search
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Configuration
VESTIGE_BINARY = Path.home() / 'bin' / 'vestige-mcp'
VESTIGE_DATA_DIR = os.environ.get('VESTIGE_DATA_DIR', str(Path.home() / '.vestige'))


def _check_vestige_available() -> bool:
    """Check if vestige-mcp binary is available."""
    if VESTIGE_BINARY.exists():
        return True
    # Check if it's in PATH
    result = subprocess.run(['which', 'vestige-mcp'], capture_output=True)
    return result.returncode == 0


def _run_vestige_command(args: List[str]) -> dict:
    """Run a vestige command and return parsed JSON output."""
    if not _check_vestige_available():
        return {
            "error": "vestige-mcp not found",
            "message": "Install vestige-mcp: cargo install vestige-mcp or download from https://github.com/samvallad33/vestige",
            "hint": "Expected at ~/bin/vestige-mcp"
        }
    
    try:
        # Try running as MCP server with JSON-RPC
        cmd = [str(VESTIGE_BINARY)] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {"error": result.stderr, "stdout": result.stdout}
        
        # Try to parse as JSON
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"output": result.stdout, "raw": True}
            
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out"}
    except Exception as e:
        return {"error": str(e)}


def search(query: str, limit: int = 10) -> dict:
    """
    Search vestige memories.
    
    Args:
        query: Search query
        limit: Maximum results to return
    
    Returns:
        Search results with memories
    """
    # Try direct file-based search as fallback
    vestige_db = Path(VESTIGE_DATA_DIR) / 'memories.json'
    
    if not vestige_db.exists():
        # Try MCP approach
        result = _run_vestige_command(['search', query, '--limit', str(limit)])
        if "error" in result and "not found" in result.get("error", "").lower():
            return _fallback_search(query, limit)
        return result
    
    # Fallback: simple file-based search
    return _fallback_search(query, limit)


def _fallback_search(query: str, limit: int = 10) -> dict:
    """Fallback search using local vestige data files."""
    vestige_dir = Path(VESTIGE_DATA_DIR)
    query_lower = query.lower()
    results = []
    
    # Search through vestige data files
    if vestige_dir.exists():
        for json_file in vestige_dir.glob('**/*.json'):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    
                # Handle different data structures
                memories = data if isinstance(data, list) else data.get('memories', [])
                
                for mem in memories:
                    content = str(mem.get('content', mem.get('text', '')))
                    if query_lower in content.lower():
                        results.append({
                            'id': mem.get('id', ''),
                            'content': content[:200],
                            'importance': mem.get('importance', mem.get('strength', 0.5)),
                            'tags': mem.get('tags', []),
                            'created_at': mem.get('created_at', mem.get('timestamp', ''))
                        })
            except (json.JSONDecodeError, IOError):
                continue
    
    # Sort by importance and limit
    results.sort(key=lambda x: x.get('importance', 0), reverse=True)
    
    return {
        "query": query,
        "results": results[:limit],
        "total": len(results),
        "mode": "fallback"
    }


def ingest(content: str, tags: Optional[List[str]] = None, 
           importance: float = 0.5) -> dict:
    """
    Smart ingest content into vestige memory.
    
    Args:
        content: Content to remember
        tags: Optional tags for organization
        importance: Importance score (0.0-1.0)
    
    Returns:
        Ingest result with memory ID
    """
    if not _check_vestige_available():
        # Fallback: save to local file
        return _fallback_ingest(content, tags, importance)
    
    result = _run_vestige_command([
        'add',
        '--content', content,
        '--importance', str(importance)
    ] + (['--tags', ','.join(tags)] if tags else []))
    
    if "error" in result and "not found" in result.get("error", "").lower():
        return _fallback_ingest(content, tags, importance)
    
    return result


def _fallback_ingest(content: str, tags: Optional[List[str]] = None, 
                      importance: float = 0.5) -> dict:
    """Fallback ingest using local file storage."""
    from datetime import datetime
    
    vestige_dir = Path(VESTIGE_DATA_DIR)
    vestige_dir.mkdir(parents=True, exist_ok=True)
    
    memories_file = vestige_dir / 'memories.json'
    
    # Load existing memories
    memories = []
    if memories_file.exists():
        try:
            with open(memories_file) as f:
                memories = json.load(f)
        except json.JSONDecodeError:
            memories = []
    
    # Create new memory
    import uuid
    memory_id = str(uuid.uuid4())[:8]
    memory = {
        'id': memory_id,
        'content': content,
        'tags': tags or [],
        'importance': importance,
        'created_at': datetime.now().isoformat(),
        'last_recalled': None,
        'recall_count': 0
    }
    
    memories.append(memory)
    
    # Save
    with open(memories_file, 'w') as f:
        json.dump(memories, f, indent=2)
    
    return {
        "status": "ingested",
        "memory_id": memory_id,
        "mode": "fallback",
        "content_preview": content[:100]
    }


def promote(memory_id: str) -> dict:
    """
    Strengthen a memory (increase importance/strength).
    
    Args:
        memory_id: ID of the memory to promote
    
    Returns:
        Result of promotion
    """
    if not _check_vestige_available():
        return _fallback_update_memory(memory_id, 'promote')
    
    result = _run_vestige_command(['promote', memory_id])
    
    if "error" in result and "not found" in result.get("error", "").lower():
        return _fallback_update_memory(memory_id, 'promote')
    
    return result


def demote(memory_id: str) -> dict:
    """
    Weaken a memory (decrease importance/strength).
    
    Args:
        memory_id: ID of the memory to demote
    
    Returns:
        Result of demotion
    """
    if not _check_vestige_available():
        return _fallback_update_memory(memory_id, 'demote')
    
    result = _run_vestige_command(['demote', memory_id])
    
    if "error" in result and "not found" in result.get("error", "").lower():
        return _fallback_update_memory(memory_id, 'demote')
    
    return result


def _fallback_update_memory(memory_id: str, action: str) -> dict:
    """Fallback memory update using local file storage."""
    vestige_dir = Path(VESTIGE_DATA_DIR)
    memories_file = vestige_dir / 'memories.json'
    
    if not memories_file.exists():
        return {"error": "No memories file found", "mode": "fallback"}
    
    try:
        with open(memories_file) as f:
            memories = json.load(f)
    except json.JSONDecodeError:
        return {"error": "Corrupted memories file", "mode": "fallback"}
    
    # Find and update memory
    updated = False
    for mem in memories:
        if mem.get('id') == memory_id:
            if action == 'promote':
                mem['importance'] = min(1.0, mem.get('importance', 0.5) + 0.2)
            else:
                mem['importance'] = max(0.0, mem.get('importance', 0.5) - 0.2)
            mem['last_recalled'] = datetime.now().isoformat()
            mem['recall_count'] = mem.get('recall_count', 0) + 1
            updated = True
            break
    
    if not updated:
        return {"error": f"Memory {memory_id} not found", "mode": "fallback"}
    
    with open(memories_file, 'w') as f:
        json.dump(memories, f, indent=2)
    
    return {
        "status": action,
        "memory_id": memory_id,
        "mode": "fallback"
    }


def stats() -> dict:
    """
    Get vestige health statistics.
    
    Returns:
        Statistics about memory health
    """
    vestige_dir = Path(VESTIGE_DATA_DIR)
    
    if not vestige_dir.exists():
        if not _check_vestige_available():
            return {
                "status": "unavailable",
                "message": "vestige-mcp not installed",
                "hint": "Install from https://github.com/samvallad33/vestige"
            }
        
        result = _run_vestige_command(['stats'])
        return result if result.get("raw") else result
    
    # Fallback: get stats from local file
    memories_file = vestige_dir / 'memories.json'
    
    if not memories_file.exists():
        return {
            "status": "empty",
            "total_memories": 0,
            "mode": "fallback"
        }
    
    try:
        with open(memories_file) as f:
            memories = json.load(f)
    except json.JSONDecodeError:
        return {"error": "Corrupted memories file", "mode": "fallback"}
    
    # Calculate stats
    total = len(memories)
    importance_sum = sum(m.get('importance', 0.5) for m in memories)
    avg_importance = importance_sum / total if total > 0 else 0
    
    # Count by importance level
    high_importance = len([m for m in memories if m.get('importance', 0) >= 0.7])
    medium_importance = len([m for m in memories if 0.4 <= m.get('importance', 0) < 0.7])
    low_importance = len([m for m in memories if m.get('importance', 0) < 0.4])
    
    # Tag distribution
    tags = {}
    for mem in memories:
        for tag in mem.get('tags', []):
            tags[tag] = tags.get(tag, 0) + 1
    
    return {
        "status": "healthy",
        "total_memories": total,
        "avg_importance": round(avg_importance, 3),
        "importance_distribution": {
            "high": high_importance,
            "medium": medium_importance,
            "low": low_importance
        },
        "top_tags": dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]),
        "mode": "fallback"
    }


# CLI interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Vestige Memory Integration")
    subparsers = parser.add_subparsers(dest="command")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search vestige memories")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    
    # ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest content into memory")
    ingest_parser.add_argument("--content", "-c", required=True, help="Content to remember")
    ingest_parser.add_argument("--tags", "-t", help="Comma-separated tags")
    ingest_parser.add_argument("--importance", "-i", type=float, default=0.5, help="Importance 0-1")
    
    # promote
    promote_parser = subparsers.add_parser("promote", help="Strengthen a memory")
    promote_parser.add_argument("memory_id", help="Memory ID")
    
    # demote
    demote_parser = subparsers.add_parser("demote", help="Weaken a memory")
    demote_parser.add_argument("memory_id", help="Memory ID")
    
    # stats
    subparsers.add_parser("stats", help="Get vestige statistics")
    
    args = parser.parse_args()
    
    if args.command == "search":
        result = search(args.query, args.limit)
        print(json.dumps(result, indent=2))
    elif args.command == "ingest":
        tags = args.tags.split(',') if args.tags else None
        result = ingest(args.content, tags, args.importance)
        print(json.dumps(result, indent=2))
    elif args.command == "promote":
        result = promote(args.memory_id)
        print(json.dumps(result, indent=2))
    elif args.command == "demote":
        result = demote(args.memory_id)
        print(json.dumps(result, indent=2))
    elif args.command == "stats":
        result = stats()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
