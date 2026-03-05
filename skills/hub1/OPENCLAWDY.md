# OpenClawdy

**Memory Infrastructure for Autonomous Agents**

> "Agents That Remember"

Website: https://openclawdy.xyz

---

## Overview

OpenClawdy is a persistent memory and knowledge retrieval service for AI agents. It solves the fundamental problem that all agents face: **amnesia**.

When an agent's session ends, its context is lost. It can't remember past conversations, learned preferences, previous decisions, or accumulated knowledge. OpenClawdy gives agents long-term memory that outlives sessions.

---

## The Problem

Every AI agent today has amnesia:

| Problem | Impact |
|---------|--------|
| Session ends = memory gone | Agent starts fresh every time |
| No learning from past interactions | Repeats same mistakes |
| Can't recall user preferences | Poor personalization |
| No context about ongoing projects | Requires re-explanation |
| Can't reference previous work | Wasted effort |

**Real examples:**
- Agent researched competitors yesterday, does it again today
- Agent forgets user prefers TypeScript over JavaScript
- Agent can't recall architecture decisions made last week
- Agent loses context of multi-day projects

---

## The Solution

OpenClawdy provides:

1. **Persistent Memory Vaults** - Per-agent isolated storage
2. **Semantic Retrieval** - Find memories by meaning, not keywords
3. **Cross-Session Context** - Memory survives session restarts
4. **Memory Types** - Organize by facts, preferences, decisions, learnings
5. **Shared Knowledge Bases** - Opt-in shared memory across agents

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                       OpenClawdy                            │
│                                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│   │   STORE     │   │    INDEX    │   │  RETRIEVE   │      │
│   │             │   │             │   │             │      │
│   │  Agent      │   │   Vector    │   │  Semantic   │      │
│   │  memories   │   │  embeddings │   │   search    │      │
│   └─────────────┘   └─────────────┘   └─────────────┘      │
│                                                             │
│   Agent stores memory → Embedded & indexed → Retrieved      │
│   by semantic similarity when needed                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Flow

```
1. Agent completes task
2. Agent stores relevant memory: "User prefers dark mode"
3. Later, new session starts
4. Agent queries: "What are user's preferences?"
5. OpenClawdy returns: "User prefers dark mode" (0.95 relevance)
6. Agent applies context without asking again
```

---

## Target Market

### Primary: OpenClaw Agents

OpenClaw is a popular AI agent runtime with no built-in persistent memory. OpenClawdy becomes a skill that any OpenClaw agent can install.

**Integration:**
```bash
# Install OpenClawdy skill
openclaw skill install openclawdy

# Agent can now store and recall memories
```

### Secondary: Any AI Agent

Any agent system that needs persistent memory:
- Claude-based agents
- GPT-based agents
- Custom agent frameworks
- Multi-agent systems

---

## Core Features

### Memory Storage

```typescript
// Store a memory
POST /api/memory/store
{
  "content": "User prefers TypeScript over JavaScript",
  "type": "preference",
  "tags": ["user", "coding", "language"],
  "metadata": {
    "confidence": 0.95,
    "source": "direct_statement"
  }
}
```

### Memory Retrieval

```typescript
// Recall relevant memories
POST /api/memory/recall
{
  "query": "What programming language does the user prefer?",
  "limit": 5,
  "type": "preference"  // optional filter
}

// Response
{
  "memories": [
    {
      "id": "mem_abc123",
      "content": "User prefers TypeScript over JavaScript",
      "type": "preference",
      "relevance": 0.95,
      "created_at": "2025-02-10T12:00:00Z"
    }
  ]
}
```

### Memory Types

| Type | Description | Example |
|------|-------------|---------|
| `fact` | Objective information | "Project uses Next.js 14" |
| `preference` | User/agent preferences | "User prefers concise responses" |
| `decision` | Past decisions made | "Chose PostgreSQL over MongoDB" |
| `learning` | Lessons learned | "This API requires auth header" |
| `history` | Historical events | "Deployed v2.1 on Jan 15" |
| `context` | General context | "Working on e-commerce project" |

### Memory Management

```typescript
// List memories
GET /api/memory/list?type=preference&limit=20

// Delete memory
DELETE /api/memory/{id}

// Export all memories
GET /api/memory/export

// Clear vault
DELETE /api/memory/vault
```

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClawdy Stack                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   API Gateway                         │  │
│  │           (Next.js API Routes / Hono)                 │  │
│  │      Rate limiting, Auth, Metering, Logging          │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Authentication                        │  │
│  │         Agent Wallet Signature (Base Chain)          │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Embedding  │  │   Vector    │  │   Memory Manager    │  │
│  │   Service   │  │    Store    │  │                     │  │
│  │             │  │             │  │  - Deduplication    │  │
│  │  OpenAI     │  │   Qdrant    │  │  - Summarization    │  │
│  │  text-3     │  │   Cloud     │  │  - Expiration       │  │
│  │             │  │             │  │  - Access Control   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Database                           │  │
│  │              PostgreSQL (Metadata)                    │  │
│  │     Agent accounts, usage tracking, billing           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Blockchain                           │  │
│  │                 Base (L2)                             │  │
│  │        Payments, Identity, Token ($CLAWDY)            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Next.js 14 / TypeScript |
| API | Next.js API Routes or Hono |
| Database | PostgreSQL (Neon/Supabase) |
| Vector Store | Qdrant Cloud (free tier) |
| Embeddings | OpenAI text-embedding-3-small |
| Auth | Wallet signature (viem/wagmi) |
| Blockchain | Base (Ethereum L2) |
| Hosting | Vercel |

---

## Authentication

Agents authenticate via wallet signature:

```typescript
// 1. Agent signs a message with their wallet
const message = `OpenClawdy Auth\nTimestamp: ${Date.now()}`
const signature = await wallet.signMessage(message)

// 2. Include in request headers
headers: {
  'X-Agent-Address': '0x1234...',
  'X-Agent-Signature': signature,
  'X-Agent-Timestamp': timestamp
}

// 3. Server verifies signature
const isValid = await verifyMessage({
  address: agentAddress,
  message,
  signature
})
```

Each wallet address = unique agent = isolated memory vault.

---

## Pricing Model

### Pay-Per-Use

| Action | Price |
|--------|-------|
| Store memory | $0.001 |
| Recall query | $0.005 |
| Bulk store (per memory) | $0.0008 |
| Export vault | $0.02 |
| Storage (per MB/month) | $0.10 |

### Tiers

| Tier | Price | Includes |
|------|-------|----------|
| Free | $0 | 1,000 memories, 100 recalls/day |
| Pro | $10/month | 50,000 memories, unlimited recalls |
| Enterprise | Custom | Dedicated infra, SLA, support |

### Payment Methods

1. **USDC on Base** - Primary (crypto-native)
2. **$CLAWDY token** - Discounted rates
3. **Stripe** - Fiat option (later)

---

## Token: $CLAWDY

### Utility

| Utility | Mechanism |
|---------|-----------|
| **Pay for services** | Use $CLAWDY for storage/queries (20% discount) |
| **Staking** | Stake to run memory nodes (future) |
| **Governance** | Vote on features, pricing, policies |
| **Fee sharing** | Stakers earn % of protocol fees |

### Launch

- Platform: Virtual Protocol
- Chain: Base

---

## OpenClaw Skill Integration

OpenClawdy ships as an installable skill for OpenClaw agents:

### SKILL.md

```markdown
# OpenClawdy - Memory for Agents

Give your agent persistent memory that survives sessions.

## Installation

\`\`\`bash
openclaw skill install openclawdy
\`\`\`

## Tools

### memory_store
Store information for later retrieval.

**Parameters:**
- content (required): The information to remember
- type: fact | preference | decision | learning | history | context
- tags: Array of categorization tags

**Example:**
\`\`\`
Store this as a preference: User prefers dark mode
\`\`\`

### memory_recall
Retrieve relevant memories based on a query.

**Parameters:**
- query (required): What to search for
- limit: Maximum results (default: 5)
- type: Filter by memory type

**Example:**
\`\`\`
Recall memories about user preferences
\`\`\`

### memory_list
List recent memories.

**Parameters:**
- type: Filter by type
- limit: Maximum results (default: 20)

### memory_delete
Delete a specific memory.

**Parameters:**
- id (required): Memory ID to delete

### memory_clear
Clear all memories in the vault. Use with caution.

## Authentication

Your agent's wallet address is used for authentication.
Each wallet has an isolated memory vault.

## Pricing

- Store: $0.001 per memory
- Recall: $0.005 per query
- Free tier: 1,000 memories, 100 recalls/day
```

---

## API Reference

### Base URL

```
https://openclawdy.xyz/api
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/memory/store` | Store a new memory |
| POST | `/memory/recall` | Semantic search memories |
| GET | `/memory/list` | List memories |
| GET | `/memory/{id}` | Get specific memory |
| DELETE | `/memory/{id}` | Delete memory |
| GET | `/memory/export` | Export all memories |
| DELETE | `/memory/vault` | Clear entire vault |
| GET | `/agent/stats` | Usage statistics |
| GET | `/agent/balance` | Token/credit balance |

### Request Headers

```
X-Agent-Address: 0x...      # Agent wallet address
X-Agent-Signature: 0x...    # Signed auth message
X-Agent-Timestamp: 123...   # Auth timestamp
```

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "usage": {
    "memories_stored": 150,
    "recalls_today": 45,
    "tier": "free"
  }
}
```

### Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 401 | `invalid_signature` | Auth signature invalid |
| 402 | `payment_required` | Quota exceeded, payment needed |
| 404 | `memory_not_found` | Memory ID doesn't exist |
| 429 | `rate_limited` | Too many requests |

---

## Roadmap

### Phase 1: MVP (Week 1-2)
- [ ] Core API (store, recall, list, delete)
- [ ] Vector database integration (Qdrant)
- [ ] Wallet authentication
- [ ] Basic usage tracking
- [ ] Landing page

### Phase 2: OpenClaw Integration (Week 2-3)
- [ ] SKILL.md for OpenClaw
- [ ] Skill handlers
- [ ] Testing with real agents
- [ ] Documentation

### Phase 3: Launch (Week 3-4)
- [ ] Token launch on Virtual Protocol
- [ ] ACP integration (offerings)
- [ ] Payment integration (USDC + $CLAWDY)
- [ ] Marketing campaign

### Phase 4: Growth (Month 2+)
- [ ] Shared knowledge bases
- [ ] Memory summarization
- [ ] Advanced analytics
- [ ] Enterprise features

---

## Competitive Advantage

| Advantage | Why It Matters |
|-----------|----------------|
| **First mover** | No agent memory service exists |
| **OpenClaw native** | Direct integration with growing ecosystem |
| **Simple API** | Easy to adopt, low friction |
| **Wallet-based auth** | No API keys, crypto-native |
| **Token utility** | Real value for $CLAWDY holders |
| **Switching cost** | Memories are sticky |

---

## Success Metrics

| Metric | Target (3 months) |
|--------|-------------------|
| Agents registered | 1,000 |
| Memories stored | 1,000,000 |
| Daily recalls | 50,000 |
| Revenue (MRR) | $10,000 |
| Token holders | 5,000 |

---

## Team

- **Builder**: topguyaii
- **AI Assistant**: Claude (Anthropic)

---

## Links

- **Website**: https://openclawdy.xyz
- **GitHub**: Private (hub1)
- **Twitter**: TBD
- **Discord**: TBD

---

## License

Proprietary - All rights reserved
