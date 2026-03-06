# Memphis Schemas

Block structures, chain formats, and data models.

---

## 1. Chain Structure

**Location:** `~/.memphis/chains/<name>/`

**Format:** JSONL (JSON Lines)

**File naming:** `<index>.json` (zero-padded 6 digits)

**Example:**
```
~/.memphis/chains/
├── journal/
│   ├── 000000.json
│   ├── 000001.json
│   └── 000002.json
├── decision/
│   └── 000000.json
├── ask/
│   └── 000000.json
└── summary/
    └── 000000.json
```

---

## 2. Block Types

### 2.1 Journal Block

**Type:** `journal`

**Schema:**
```json
{
  "type": "journal",
  "text": "string",
  "tags": ["string"],
  "timestamp": "ISO8601",
  "hash": "sha256",
  "prevHash": "sha256|null"
}
```

**Fields:**
- `type` — always "journal"
- `text` — journal content
- `tags` — tag array
- `timestamp` — creation time
- `hash` — block hash
- `prevHash` — previous block hash (chain link)

**Example:**
```json
{
  "type": "journal",
  "text": "Prefer concise responses, avoid fluff",
  "tags": ["preferences", "communication"],
  "timestamp": "2026-03-01T10:00:00Z",
  "hash": "a1b2c3d4...",
  "prevHash": "z9y8x7w6..."
}
```

---

### 2.2 Decision Block

**Type:** `decision`

**Schema:**
```json
{
  "type": "decision",
  "title": "string",
  "choice": "string",
  "options": ["string"],
  "reasoning": "string",
  "tags": ["string"],
  "timestamp": "ISO8601",
  "hash": "sha256",
  "prevHash": "sha256|null",
  "id": "number",
  "status": "active|superseded|contradicted|stale",
  "supersedes": "number|null"
}
```

**Fields:**
- `title` — decision title
- `choice` — chosen option
- `options` — all options considered
- `reasoning` — why this choice
- `id` — sequential decision ID
- `status` — current status
- `supersedes` — previous decision ID if replaced

**Status values:**
- `active` — current decision
- `superseded` — replaced by newer decision
- `contradicted` — proven wrong
- `stale` — outdated but not replaced

**Example:**
```json
{
  "type": "decision",
  "title": "Memory Strategy",
  "choice": "Local-first + IPFS sync",
  "options": ["cloud", "local", "hybrid"],
  "reasoning": "Privacy + resilience",
  "tags": ["philosophy", "memory"],
  "timestamp": "2026-03-01T10:00:00Z",
  "hash": "e5f6g7h8...",
  "prevHash": "d4c3b2a1...",
  "id": 1,
  "status": "active",
  "supersedes": null
}
```

---

### 2.3 Ask Block

**Type:** `ask`

**Schema:**
```json
{
  "type": "ask",
  "question": "string",
  "answer": "string",
  "context": ["block-hash"],
  "provider": "string",
  "model": "string",
  "timestamp": "ISO8601",
  "hash": "sha256",
  "prevHash": "sha256|null"
}
```

**Fields:**
- `question` — user query
- `answer` — LLM response
- `context` — block hashes used for context
- `provider` — LLM provider name
- `model` — model name

**Example:**
```json
{
  "type": "ask",
  "question": "What are my preferences?",
  "answer": "Based on your journal...",
  "context": ["a1b2c3d4", "e5f6g7h8"],
  "provider": "ollama",
  "model": "qwen2.5:3b",
  "timestamp": "2026-03-01T10:00:00Z",
  "hash": "i9j0k1l2...",
  "prevHash": "h8g7f6e5..."
}
```

---

### 2.4 Summary Block

**Type:** `summary`

**Schema:**
```json
{
  "type": "summary",
  "sourceChain": "string",
  "sourceRange": {
    "start": "number",
    "end": "number"
  },
  "summary": "string",
  "themes": ["string"],
  "keyDecisions": ["number"],
  "timestamp": "ISO8601",
  "hash": "sha256",
  "prevHash": "sha256|null"
}
```

**Fields:**
- `sourceChain` — chain being summarized
- `sourceRange` — block range summarized
- `summary` — condensed text
- `themes` — extracted themes
- `keyDecisions` — decision IDs included

**Example:**
```json
{
  "type": "summary",
  "sourceChain": "journal",
  "sourceRange": {"start": 0, "end": 49},
  "summary": "User prefers local-first...",
  "themes": ["privacy", "resilience", "performance"],
  "keyDecisions": [1, 3, 5],
  "timestamp": "2026-03-01T10:00:00Z",
  "hash": "m3n4o5p6...",
  "prevHash": "l2k1j0i9..."
}
```

---

### 2.5 Reflection Block

**Type:** `reflection`

**Schema:**
```json
{
  "type": "reflection",
  "mode": "daily|weekly|deep",
  "period": {
    "start": "ISO8601",
    "end": "ISO8601"
  },
  "insights": [
    {
      "type": "tag_frequency|theme|decision_pattern|graph_cluster|stale|contradiction|opportunity",
      "description": "string",
      "data": "object"
    }
  ],
  "timestamp": "ISO8601",
  "hash": "sha256",
  "prevHash": "sha256|null"
}
```

**Insight types:**
- `tag_frequency` — most used tags
- `theme` — extracted themes
- `decision_pattern` — decision trends
- `graph_cluster` — knowledge graph clusters
- `stale` — outdated decisions
- `contradiction` — conflicting decisions
- `opportunity` — improvement opportunities

**Example:**
```json
{
  "type": "reflection",
  "mode": "daily",
  "period": {
    "start": "2026-03-01T00:00:00Z",
    "end": "2026-03-01T23:59:59Z"
  },
  "insights": [
    {
      "type": "tag_frequency",
      "description": "Most used tags: session (15), journal (12)",
      "data": {"session": 15, "journal": 12}
    },
    {
      "type": "stale",
      "description": "Decision #2 is stale (>30 days)",
      "data": {"decisionId": 2, "daysOld": 45}
    }
  ],
  "timestamp": "2026-03-01T18:00:00Z",
  "hash": "q7r8s9t0...",
  "prevHash": "p6o5n4m3..."
}
```

---

### 2.6 Trade Block

**Type:** `trade`

**Schema:**
```json
{
  "type": "trade",
  "manifest": {
    "version": "string",
    "offerId": "uuid",
    "sender": {
      "did": "string",
      "signature": "string"
    },
    "recipient": {
      "did": "string"
    },
    "blocks": [
      {
        "chain": "string",
        "range": {"start": "number", "end": "number"},
        "hashes": ["sha256"]
      }
    ],
    "ttl": "ISO8601-duration",
    "timestamp": "ISO8601",
    "signature": "string"
  },
  "status": "pending|accepted|rejected|expired",
  "timestamp": "ISO8601",
  "hash": "sha256"
}
```

---

## 3. Embedding Index

**Location:** `~/.memphis/embeddings/<chain>.json`

**Schema:**
```json
{
  "chain": "string",
  "model": "string",
  "blocks": [
    {
      "index": "number",
      "hash": "sha256",
      "embedding": ["number"],
      "timestamp": "ISO8601"
    }
  ]
}
```

**Fields:**
- `embedding` — vector (dimension depends on model)
- `model` — embedding model (e.g., `nomic-embed-text`)

**Example:**
```json
{
  "chain": "journal",
  "model": "nomic-embed-text",
  "blocks": [
    {
      "index": 0,
      "hash": "a1b2c3d4",
      "embedding": [0.123, -0.456, ...],
      "timestamp": "2026-03-01T10:00:00Z"
    }
  ]
}
```

---

## 4. Knowledge Graph

**Location:** `~/.memphis/graph/`

### 4.1 Nodes

**File:** `nodes.jsonl`

**Schema:**
```json
{
  "id": "string",
  "type": "block|concept|tag",
  "label": "string",
  "chain": "string|null",
  "blockIndex": "number|null",
  "data": "object"
}
```

**Example:**
```json
{"id": "journal:0", "type": "block", "label": "Identity block", "chain": "journal", "blockIndex": 0}
{"id": "privacy", "type": "concept", "label": "Privacy principle"}
```

---

### 4.2 Edges

**File:** `edges.jsonl`

**Schema:**
```json
{
  "source": "node-id",
  "target": "node-id",
  "type": "semantic|tag|ref",
  "weight": "number",
  "data": "object"
}
```

**Edge types:**
- `semantic` — similarity (cosine > 0.7)
- `tag` — shared tag
- `ref` — explicit reference

**Example:**
```json
{"source": "journal:0", "target": "journal:5", "type": "semantic", "weight": 0.85}
{"source": "journal:0", "target": "privacy", "type": "tag", "weight": 1.0}
```

---

## 5. Network Chain

**Location:** `~/.memphis/network-chain.jsonl`

**Purpose:** Track IPFS pins for share-sync.

**Schema:**
```json
{
  "cid": "string",
  "sourceAgent": "string",
  "timestamp": "ISO8601",
  "size": "number",
  "blocks": ["sha256"],
  "ttl": "ISO8601-duration"
}
```

**Example:**
```json
{
  "cid": "QmXyz...",
  "sourceAgent": "watra",
  "timestamp": "2026-03-01T10:00:00Z",
  "size": 2048,
  "blocks": ["a1b2c3d4"],
  "ttl": "P7D"
}
```

---

## 6. Config Schema

**Location:** `~/.memphis/config.yaml`

**Structure:**
```yaml
providers:
  <name>:
    url: string
    model: string
    role: primary|fallback
    api_key: string (optional, prefer vault)

embeddings:
  backend: ollama|openai
  model: string
  url: string (optional)

integrations:
  pinata:
    jwt: string (or env PINATA_JWT)
    apiKey: string
    apiSecret: string

security:
  workspaceGuard: boolean
  allowUnsafeOperations: boolean

autosummary:
  enabled: boolean
  threshold: number
  triggerBlocks: number

daemon:
  collectors: [git, shell, file]
  interval: number (ms)
```

---

## 7. Vault Structure

**Location:** `~/.memphis/vault.enc`

**Format:** Encrypted JSON

**Decrypted schema:**
```json
{
  "version": "1.0",
  "secrets": {
    "<key>": {
      "value": "string",
      "created": "ISO8601",
      "updated": "ISO8601"
    }
  },
  "metadata": {
    "created": "ISO8601",
    "seedHash": "sha256"
  }
}
```

---

## 8. Hash Chain Integrity

**Linking:**
- Each block contains `hash` (current) and `prevHash` (previous)
- First block: `prevHash: null`
- Tampering breaks chain (verify fails)

**Hash algorithm:**
```
hash = sha256(JSON.stringify(block))
```

**Verification:**
```bash
memphis verify --chain journal
```

---

## 9. Block Size Limits

**Soft limit:** 2KB per block

**Hard limit:** 10KB per block

**Share-sync limit:** 2KB (larger blocks skipped)

**Recommendation:** Split large content across multiple blocks.

---

## 10. Timestamp Format

**ISO 8601:** `YYYY-MM-DDTHH:mm:ssZ`

**Example:** `2026-03-01T10:30:45Z`

**Timezone:** UTC (store), Local (display)

---

## Summary

- **Chains:** JSONL files in `~/.memphis/chains/<name>/`
- **Blocks:** Immutable, hash-linked JSON objects
- **Types:** journal, decision, ask, summary, reflection, trade
- **Embeddings:** Vector index per chain
- **Graph:** nodes.jsonl + edges.jsonl
- **Network:** Track IPFS pins
- **Config:** YAML in `~/.memphis/config.yaml`
- **Vault:** Encrypted secrets

---

All data is local-first, human-readable JSON, and cryptographically linked.
