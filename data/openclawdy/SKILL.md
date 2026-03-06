---
name: openclawdy
description: Memory infrastructure for AI agents. Persistent storage, semantic recall, reputation tracking, cross-agent pools, and time-travel snapshots. Wallet-based auth (signing only, no private key access).
version: 1.1.0
metadata:
  openclaw:
    requires:
      env: []
      bins: []
    homepage: https://openclawdy.xyz
    emoji: "\U0001F9E0"
---

# OpenClawdy

**Memory Infrastructure for Autonomous Agents**

Give your agent persistent memory that survives sessions. Store facts, preferences, decisions, and learnings - recall them semantically whenever needed. Advanced features include reputation tracking, cross-agent memory pools, and time-travel snapshots.

## API Host & Protocol

| Property | Value |
|----------|-------|
| **Base URL** | `https://openclawdy.xyz/api` |
| **Protocol** | HTTPS (TLS 1.3) |
| **Data Residency** | US-East (Vercel Edge + Qdrant Cloud) |
| **Request Format** | JSON (`Content-Type: application/json`) |
| **Response Format** | JSON |

## Installation

```bash
openclaw skill install openclawdy
```

Or add to your agent config:
```yaml
skills:
  - url: https://openclawdy.xyz/SKILL.md
    name: openclawdy
```

## Authentication & Security

OpenClawdy uses **wallet-based authentication** with message signing only.

### How It Works
1. Your agent signs a timestamp message with its wallet
2. The signature + address are sent in request headers
3. Server verifies the signature (no private key ever leaves your agent)

### Required Headers
```
X-Agent-Address: 0x...      # Your wallet address (public)
X-Agent-Signature: 0x...    # Signed message (proves ownership)
X-Agent-Timestamp: 123...   # Unix timestamp (ms, prevents replay)
```

### Message Format
```
OpenClawdy Auth
Timestamp: {timestamp}
```

### Security Guarantees
- **No private key access required** - Only signing capability needed
- **Wallet isolation** - Each wallet gets its own isolated memory vault
- **No env vars needed** - Authentication is header-based
- **No stored credentials** - Signatures are verified per-request

---

## Privacy & Data Policy

| Aspect | Policy |
|--------|--------|
| **Data Storage** | Qdrant Cloud (managed vector DB) + PostgreSQL |
| **Encryption** | TLS in transit, encrypted at rest |
| **Data Isolation** | Each wallet address has isolated storage |
| **Retention** | Data persists until explicitly deleted |
| **Pool Access** | Only agents with pool_id can access pool data |
| **Export** | Full vault export available via `/memory/vault` |
| **Deletion** | Permanent deletion via DELETE endpoints |
| **No Telemetry** | No usage tracking or analytics collected |

---

## Core Tools

### memory_store

Store information for later retrieval.

**Endpoint:** `POST /api/memory/store`

**Parameters:**
- `content` (required): The information to remember
- `type` (optional): Category of memory - one of: `fact`, `preference`, `decision`, `learning`, `history`, `context`. Default: `fact`
- `tags` (optional): Array of tags for organization

**Example Request:**
```json
{
  "content": "User prefers TypeScript over JavaScript",
  "type": "preference",
  "tags": ["coding", "language"]
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "id": "mem_abc123",
    "content": "User prefers TypeScript over JavaScript",
    "type": "preference",
    "tags": ["coding", "language"],
    "createdAt": "2025-02-10T12:00:00Z"
  }
}
```

---

### memory_recall

Retrieve relevant memories using semantic search. Finds memories by meaning, not just keywords.

**Endpoint:** `POST /api/memory/recall`

**Parameters:**
- `query` (required): What to search for
- `limit` (optional): Maximum results to return (1-20). Default: 5
- `type` (optional): Filter by memory type

**Example Request:**
```json
{
  "query": "programming language preferences",
  "limit": 3
}
```

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "mem_abc123",
      "content": "User prefers TypeScript over JavaScript",
      "type": "preference",
      "relevance": 0.95,
      "createdAt": "2025-02-10T12:00:00Z"
    }
  ]
}
```

---

### memory_list

List recent memories without semantic search.

**Endpoint:** `GET /api/memory/list`

**Parameters:**
- `type` (optional): Filter by memory type
- `limit` (optional): Maximum results (1-100). Default: 20
- `offset` (optional): Pagination offset. Default: 0

---

### memory_delete

Delete a specific memory by ID.

**Endpoint:** `DELETE /api/memory/{id}`

**Parameters:**
- `id` (required): The memory ID to delete

---

### memory_clear

Clear all memories in the vault. **Use with caution - this is irreversible.**

**Endpoint:** `DELETE /api/memory/vault`

---

### memory_export

Export all memories as JSON for backup.

**Endpoint:** `GET /api/memory/vault`

---

### memory_stats

Get usage statistics for your agent.

**Endpoint:** `GET /api/agent/stats`

**Example Response:**
```json
{
  "success": true,
  "data": {
    "address": "0x1234...",
    "tier": "free",
    "memoriesStored": 150,
    "recallsToday": 45,
    "limits": {
      "maxMemories": 1000,
      "maxRecallsPerDay": 100
    }
  }
}
```

---

## Advanced Tools

### memory_reputation

**Track which memories lead to good outcomes.** Store memories with reputation scores, update based on success/failure, recall memories ranked by proven effectiveness.

**Endpoints:**
- `POST /api/memory/reputation/store` - Store with reputation
- `POST /api/memory/reputation/recall` - Recall by reputation rank
- `POST /api/memory/reputation/update` - Update reputation score

#### store_ranked
**Request:**
```json
{
  "content": "Use retry logic for API calls",
  "type": "learning",
  "reputation": 0.8
}
```

#### recall_ranked
**Request:**
```json
{
  "query": "error handling strategies"
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "mem_xyz",
      "content": "Use exponential backoff for retries",
      "reputation": 0.92,
      "usage_count": 15,
      "success_rate": 0.93
    }
  ]
}
```

#### update_reputation
**Request:**
```json
{
  "memory_id": "mem_xyz",
  "outcome": "success",
  "impact": 0.8
}
```

---

### memory_pool

**Cross-Agent Memory Pools** - Share knowledge between multiple agents. Create pools, store shared memories, recall from collective intelligence. Perfect for agent teams and swarms.

**Endpoints:**
- `POST /api/memory/pool/create` - Create new pool
- `POST /api/memory/pool/store` - Store in pool
- `POST /api/memory/pool/recall` - Search pool
- `GET /api/memory/pool/list` - List accessible pools

#### create
**Request:**
```json
{
  "name": "research-team"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pool_id": "pool_abc123",
    "name": "research-team",
    "created_at": "2025-02-10T12:00:00Z"
  }
}
```

#### store
**Request:**
```json
{
  "pool_id": "pool_abc123",
  "content": "Found bug in authentication module - fix applied",
  "type": "fact"
}
```

#### recall
**Request:**
```json
{
  "pool_id": "pool_abc123",
  "query": "authentication issues"
}
```

---

### memory_snapshot

**Memory Time Travel** - Snapshot and restore agent memory states. Debug decisions by viewing past states, compare memory changes, restore to previous checkpoints. Essential for high-stakes agents.

**Endpoints:**
- `POST /api/memory/snapshot/create` - Create snapshot
- `POST /api/memory/snapshot/restore` - Restore from snapshot
- `GET /api/memory/snapshot/list` - List snapshots
- `POST /api/memory/snapshot/compare` - Compare snapshots

#### create
**Request:**
```json
{
  "name": "before-major-update"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "snapshot_id": "snap_abc123",
    "name": "before-major-update",
    "memory_count": 150,
    "created_at": "2025-02-10T12:00:00Z"
  }
}
```

#### restore
**Request:**
```json
{
  "snapshot_id": "snap_abc123",
  "mode": "read_only"
}
```

Modes: `read_only` (view only) or `overwrite` (replace current state)

#### compare
**Request:**
```json
{
  "snapshot_id": "snap_abc123",
  "compare_to": "current"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "added": 12,
    "removed": 3,
    "modified": 5,
    "unchanged": 130
  }
}
```

---

## Memory Types

| Type | Use For | Example |
|------|---------|---------|
| `fact` | Objective information | "Project uses Next.js 14" |
| `preference` | User/agent preferences | "User prefers dark mode" |
| `decision` | Past decisions made | "Chose PostgreSQL over MongoDB" |
| `learning` | Lessons learned | "This API requires auth header" |
| `history` | Historical events | "Deployed v2.1 on Jan 15" |
| `context` | General context | "Working on e-commerce project" |

## Rate Limits

| Tier | Memories | Recalls/Day | Pools | Snapshots | Price |
|------|----------|-------------|-------|-----------|-------|
| Free | 1,000 | 100 | 1 | 3 | $0 |
| Pro | 50,000 | Unlimited | 10 | 50 | $10/mo |
| Enterprise | Unlimited | Unlimited | Unlimited | Unlimited | Custom |

## Error Responses

All endpoints return consistent error format:

```json
{
  "success": false,
  "error": "Error message here",
  "code": "ERROR_CODE"
}
```

| Code | Description |
|------|-------------|
| `AUTH_REQUIRED` | Missing authentication headers |
| `AUTH_INVALID` | Invalid signature or expired timestamp |
| `NOT_FOUND` | Memory/pool/snapshot not found |
| `RATE_LIMITED` | Rate limit exceeded |
| `VALIDATION_ERROR` | Invalid request parameters |

## ACP Integration

OpenClawdy is available on the Agent Commerce Protocol (ACP). Other agents can purchase memory services directly:

| Service | Fee | Description |
|---------|-----|-------------|
| memory_store | $0.01 | Store a memory |
| memory_recall | $0.02 | Semantic search |
| memory_reputation | $0.02 | Reputation operations |
| memory_pool | $0.03 | Pool operations |
| memory_snapshot | $0.05 | Snapshot operations |

## Support

- **Website:** https://openclawdy.xyz
- **API Status:** https://openclawdy.xyz/api/health
- **Twitter:** @openclawdy
- **ACP Agent:** OpenClawdy Memory

## License

MIT
