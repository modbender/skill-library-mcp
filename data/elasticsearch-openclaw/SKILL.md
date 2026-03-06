---
name: elasticsearch-openclaw
description: >
  Read-only Elasticsearch 9.x reference for AI-orchestrated search and analytics.
  SECURITY: This skill provides documentation for read-only operations only (search,
  aggregations, analytics). No write/update/delete operations are included.
  Covers: (1) Semantic search with JINA embeddings via Elastic Inference API,
  (2) semantic_text field type with automatic embedding, (3) kNN vector search
  with dense_vector mappings, (4) Hybrid search combining BM25 + kNN with RRF,
  (5) Classic patterns: mappings, text/keyword fields, analyzers, boolean queries,
  aggregations, pagination, (6) Elasticsearch Python client 9.x — no body= parameter,
  keyword args, (7) Read-only API key creation with least-privilege scoping.
metadata:
  openclaw:
    emoji: 🔍
    requires:
      anyBins: ["python3"]
    os: ["linux", "darwin", "win32"]
    env:
      ELASTICSEARCH_URL: "Elasticsearch cluster URL (required)"
      ELASTICSEARCH_API_KEY: "Base64-encoded API key (required, secret)"
---

# Elasticsearch OpenClaw 🔍

Modern Elasticsearch 9.x patterns for AI-orchestrated applications.

## 🔒 Security Model: Read-Only by Design

This skill provides **documentation for read-only operations only**: search,
aggregations, and analytics. No write operations (indexing, updates, deletions)
are included or executed by the agent.

**Note:** This skill requires external credentials (Elasticsearch API key) to
function. ClawHub security scanners may flag this as "suspicious" — this is
expected for skills that integrate with external services. All code is
transparent markdown documentation. Review before granting credentials.

## Quick Start — Local Dev

For local Elasticsearch 9.x setup with Kibana, use the official start-local tool:
- Repository: https://github.com/elastic/start-local
- Documentation: https://www.elastic.co/start-local

Once running:
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Credentials: `elastic-start-local/.env`

## Auth — Always Use API Keys

```bash
# Test connection
curl -s "$ELASTICSEARCH_URL" -H "Authorization: ApiKey $ELASTICSEARCH_API_KEY"

# Python client 9.x
from elasticsearch import Elasticsearch
es = Elasticsearch(ES_URL, api_key=API_KEY)
```

## Reference Files

Load these only when needed — do not load all at once:

| File | Load when... |
|------|-------------|
| `references/semantic-search.md` | Setting up JINA, `semantic_text`, inference endpoint |
| `references/vector-search.md` | kNN queries, `dense_vector` mapping, hybrid search with RRF |
| `references/classic-patterns.md` | Mapping design, boolean queries, aggregations, pagination |
| `references/python-client-9.md` | Python `elasticsearch` 9.x — no `body=`, keyword args, type hints |

## When to Use Each Pattern

```
User asks about meaning / intent / "find products like X"
  → semantic_text + semantic query  →  references/semantic-search.md

User needs exact match + semantic combined
  → hybrid search (RRF)            →  references/vector-search.md

User asks about mapping, field types, analyzers, aggregations
  → classic patterns                →  references/classic-patterns.md

User uses Python elasticsearch library
  → always check                    →  references/python-client-9.md
```

## Security Best Practices

- Always use API keys over username/password
- Scope API keys to specific indices and minimal privileges
- For read-only OpenClaw access: `privileges: ["read", "view_index_metadata"]`
- Store credentials in `.env`, never hardcode in scripts
- `.env` always in `.gitignore`

```json
POST /_security/api_key
{
  "name": "openclaw-readonly",
  "role_descriptors": {
    "reader": {
      "indices": [{ "names": ["my-index"], "privileges": ["read"] }]
    }
  }
}

// Response:
{
  "id": "VuaCfGcBCdbkQm-e5aOx",
  "name": "openclaw-readonly",
  "api_key": "ui2lp2axTNmsyakw9tvNnw",
  "encoded": "VnVhQ2ZHY0JDZGJrUW0tZTVhT3g6dWkybHAyYXhUTm1zeWFrdzl0dk5udw=="
}
```

⚠️ Save the `encoded` field from the response immediately — it cannot be retrieved later.  
Add to: `~/.openclaw/workspace-[name]/.env` as `ELASTICSEARCH_API_KEY`
