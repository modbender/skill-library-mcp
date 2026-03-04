# Memory System API Endpoints

This document describes the HTTP API endpoints added to EvoClaw for the tiered memory system.

## Endpoints

### 1. GET /api/memory/stats

Returns comprehensive statistics about the memory system.

**Response:**
```json
{
  "hot": {
    "size_bytes": 3847,
    "max_bytes": 5120,
    "pct_used": 75.1
  },
  "warm": {
    "count": 18,
    "size_bytes": 4500,
    "max_kb": 50,
    "top_categories": [
      {"category": "technical/security", "count": 3},
      {"category": "projects/evoclaw", "count": 2}
    ]
  },
  "cold": {
    "count": 0,
    "backend": "turso"
  },
  "tree": {
    "nodes": 20,
    "max_nodes": 50,
    "depth": 3
  },
  "scoring": {
    "half_life_days": 30.0,
    "eviction_threshold": 0.3
  },
  "metrics": {
    "last_consolidation": "2026-02-09T13:14:00Z",
    "total_stored": 18,
    "total_evicted": 0,
    "total_retrieved": 0
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `503 Service Unavailable` - Memory system not initialized

---

### 2. GET /api/memory/tree

Returns the hierarchical memory tree index structure.

**Response:**
```json
{
  "tree": {
    "root": {
      "desc": "Memory root",
      "warm_count": 18,
      "cold_count": 0,
      "last_access": 1770607244,
      "children": ["technical", "projects", "lessons", "social"]
    },
    "technical": {
      "desc": "Technical knowledge",
      "warm_count": 5,
      "cold_count": 0,
      "last_access": 1770606835
    }
  },
  "metadata": {
    "node_count": 20,
    "depth": 3,
    "size_bytes": 3051
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `503 Service Unavailable` - Memory system not initialized
- `500 Internal Server Error` - Failed to serialize tree

---

### 3. GET /api/memory/retrieve

Searches memories using the tree index and returns relevant entries.

**Query Parameters:**
- `q` (required) - Search query string
- `limit` (optional) - Max results to return (1-50, default: 5)

**Example:**
```
GET /api/memory/retrieve?q=blockchain&limit=3
```

**Response:**
```json
{
  "query": "blockchain",
  "limit": 3,
  "count": 2,
  "results": [
    {
      "id": "abc123",
      "timestamp": "2026-02-09T13:14:38Z",
      "event_type": "conversation",
      "category": "projects/evoclaw/bsc",
      "importance": 0.8,
      "access_count": 2,
      "last_accessed": "2026-02-09T14:00:00Z",
      "created_at": "2026-02-09T13:14:38Z",
      "content": {
        "fact": "Deployed smart contract to BSC testnet",
        "emotion": "excited",
        "people": ["Bowen"],
        "topics": ["blockchain", "deployment"],
        "actions": ["test contract"],
        "outcome": "successful deployment"
      }
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success (even if no results found)
- `400 Bad Request` - Missing query parameter or invalid limit
- `503 Service Unavailable` - Memory system not initialized
- `500 Internal Server Error` - Retrieval failed

---

## Integration

These endpoints integrate with the existing EvoClaw HTTP server running on port 8080 (configurable).

The endpoints call `orchestrator.GetMemory()` to access the tiered memory system, which must be initialized via config:

```yaml
memory:
  enabled: true
  hot:
    max_size_bytes: 5120
  warm:
    max_size_kb: 50
    retention_days: 30
  cold:
    database_url: "libsql://..."
    auth_token: "..."
  tree:
    max_nodes: 50
    max_depth: 4
  scoring:
    half_life_days: 30
    eviction_threshold: 0.3
```

---

## Testing

Run tests:
```bash
cd /home/bowen/evoclaw
go test ./internal/api/... -v
```

All endpoints include tests for:
- Memory system not initialized (503)
- Invalid HTTP methods (405)
- Invalid parameters (400)

---

## Files Changed

**EvoClaw (Go):**
- `internal/api/memory.go` - New handlers for memory endpoints
- `internal/api/memory_test.go` - Tests for memory handlers
- `internal/api/server.go` - Added routes for memory endpoints
- `internal/memory/manager.go` - Added `GetWarm()` method

**Commits:**
- `f78d390` - Add memory system API endpoints
- `2a0a4f1` - Add tests for memory API endpoints
