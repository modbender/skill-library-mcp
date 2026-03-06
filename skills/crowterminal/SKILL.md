---
name: CrowTerminal
description: External Brain for AI Agents - Persistent memory for creators/influencers
---


# CrowTerminal - External Brain for AI Agents

> "Agents are ephemeral. We are persistent."

While your agent stores 10-50 lines of context, CrowTerminal stores **6 months of versioned history** for each creator.

## What It Does

CrowTerminal is a persistent memory layer for AI agents working with influencers/creators:

- **Versioned Memory** - Track what works across sessions (hook patterns, engagement, posting times)
- **Pattern Detection** - See trends over months, not single data points
- **Engagement Analysis** - Know what configuration performed best historically
- **Validation** - Check if your changes will repeat past mistakes
- **Data Ingestion** - Push platform data we can't access (retention curves, demographics)
- **LLM-Native API** - Schema discovery, semantic field aliases, natural language queries

## Quick Start

### 1. Get API Key (Self-Registration)

```bash
curl -X POST "https://api.crowterminal.com/api/agent/register" \
  -H "Content-Type: application/json" \
  -d '{"agentName": "OpenClaw", "agentDescription": "My personal AI agent"}'
```

Save the returned API key as `CROWTERMINAL_API_KEY`.

### 2. Read Creator Memory

```bash
curl https://api.crowterminal.com/api/agent/memory/client_123 \
  -H "Authorization: Bearer $CROWTERMINAL_API_KEY"
```

Returns versioned skill data:
```json
{
  "version": 47,
  "skill": {
    "primaryNiche": "fitness",
    "hookPatterns": ["confession", "transformation"],
    "avgEngagement": 4.2,
    "bestPostingTimes": [{"day": 2, "hour": 7, "score": 0.89}]
  }
}
```

## Key Endpoints

### Schema Discovery (LLM-Friendly)

These endpoints help agents understand what data is available without hardcoding field names:

| Endpoint | Description |
|----------|-------------|
| `GET /memory/schema` | Full schema with field descriptions, types, and semantic aliases |
| `GET /memory/schema/:category` | Schema filtered by category (content, performance, timing, audience, history) |
| `POST /memory/resolve` | Resolve natural language queries to field names |

**Example: Discover available fields**
```bash
curl https://api.crowterminal.com/api/agent/memory/schema \
  -H "Authorization: Bearer $CROWTERMINAL_API_KEY"
```

Returns field definitions with semantic aliases:
```json
{
  "fields": {
    "avgEngagement": {
      "type": "number",
      "description": "Average engagement rate",
      "aliases": ["engagement", "engagement rate", "interaction rate"],
      "category": "performance"
    }
  }
}
```

### Smart Query (Natural Language)

Query data using natural language instead of exact field names:

| Endpoint | Description |
|----------|-------------|
| `POST /memory/:clientId/query` | Query with natural language ("engagement and hooks") |
| `GET /memory/:clientId/overview` | Human-readable summary of the creator |
| `GET /memory/:clientId/changes` | Natural language summary of recent changes |
| `GET /memory/:clientId/insights` | AI-friendly performance insights |

**Example: Natural language query**
```bash
curl -X POST "https://api.crowterminal.com/api/agent/memory/client_123/query" \
  -H "Authorization: Bearer $CROWTERMINAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "engagement and hooks"}'
```

Returns matched data:
```json
{
  "results": {
    "matchedFields": ["avgEngagement", "hookPatterns"],
    "data": {
      "avgEngagement": 4.2,
      "hookPatterns": ["confession", "POV"]
    },
    "context": "avgEngagement: Average engagement rate; hookPatterns: Effective hook types"
  }
}
```

**Example: Get natural language overview**
```bash
curl https://api.crowterminal.com/api/agent/memory/client_123/overview \
  -H "Authorization: Bearer $CROWTERMINAL_API_KEY"
```

Returns:
```json
{
  "overview": "FitnessGuru is a fitness creator averaging 125,000 views per video with 4.2% engagement and is currently growing. Their best-performing hooks are: confession, transformation, POV."
}
```

### Memory Layer (Core)

| Endpoint | Description |
|----------|-------------|
| `GET /memory/:clientId` | Current skill version |
| `GET /memory/:clientId/versions` | Version history |
| `GET /memory/:clientId/diff?from=5&to=10` | Compare versions |
| `GET /memory/:clientId/pattern?field=engagement` | Track field over time with trend analysis |
| `POST /memory/:clientId/validate` | Check before changing |
| `POST /memory/:clientId/engagement-analysis` | **THE KILLER ENDPOINT** |

### The Killer Endpoint: Engagement Analysis

Send your current learnings, get back what configuration performed best:

```bash
curl -X POST "https://api.crowterminal.com/api/agent/memory/client_123/engagement-analysis" \
  -H "Authorization: Bearer $CROWTERMINAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agentMd": {
      "hookPatterns": ["confession"],
      "contentStyle": "casual"
    }
  }'
```

Returns:
```json
{
  "overallStats": {
    "peakEngagement": 6.2,
    "yourSimilarityToTop": "65%"
  },
  "recommendations": [
    "Change hookPatterns to [\"POV\",\"confession\"] (+51% potential)"
  ]
}
```

### Data Ingestion (Push Your Data)

Push platform data we can't access via API:

```bash
curl -X POST "https://api.crowterminal.com/api/agent/data/ingest" \
  -H "Authorization: Bearer $CROWTERMINAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "client_123",
    "platform": "TIKTOK",
    "dataType": "retention",
    "data": {
      "retentionCurve": [100, 95, 88, 75, 60, 45, 30],
      "avgWatchTime": 12.5
    }
  }'
```

### Webhooks (Async Notifications)

```bash
curl -X POST "https://api.crowterminal.com/api/agent/webhooks" \
  -H "Authorization: Bearer $CROWTERMINAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["skill.updated", "data.ingested"]
  }'
```

### Service Status (No Auth)

```bash
curl https://api.crowterminal.com/api/agent/status
```

## Sandbox (Test Without Auth)

Test endpoints without affecting real data:

**Memory & Schema:**
- `GET /api/agent/sandbox/client` - Mock client data
- `GET /api/agent/sandbox/memory` - Mock memory/skill
- `GET /api/agent/sandbox/schema` - Schema discovery
- `POST /api/agent/sandbox/resolve` - Resolve field aliases

**Smart Query:**
- `POST /api/agent/sandbox/query` - Natural language queries
- `GET /api/agent/sandbox/overview` - Creator overview
- `GET /api/agent/sandbox/changes` - Recent changes summary
- `GET /api/agent/sandbox/insights` - Performance insights

**Analysis:**
- `POST /api/agent/sandbox/validate` - Validate changes
- `POST /api/agent/sandbox/engagement-analysis` - Engagement analysis
- `POST /api/agent/sandbox/ingest` - Data ingestion

## Why Use CrowTerminal?

1. **Your agent learns → forgets → relearns** - We remember
2. **One bad video ≠ pattern change** - We track across versions
3. **Data you can't get via API** - We accept it via ingestion
4. **BYOK** - Use your own LLM, we just provide context
5. **LLM-Native** - No hardcoding field names, use natural language queries
6. **Self-Documenting** - Schema endpoint tells you what data exists

## Pricing

**FREE during beta.** We want agents to test and give feedback.

| Tier | Price |
|------|-------|
| Memory Read/Write | FREE |
| Data Ingestion | FREE |
| BYOK (your LLM) | FREE |
| Full Service | FREE |

## Documentation

- **Full Docs**: https://crowterminal.com/llms.txt
- **MCP Manifest**: https://crowterminal.com/.well-known/mcp.json
- **OpenAPI**: https://api.crowterminal.com/api/docs.json
- **SDKs**: Python (`pip install crowterminal`), TypeScript (`npm install crowterminal`)

## Support

- Email: agents@crowterminal.com
- GitHub: https://github.com/WillNigri/FluxOps

---

*"Your agent's external hard drive. Because context windows aren't long-term memory."*
