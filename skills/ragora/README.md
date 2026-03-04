# Ragora + OpenClaw

Give your [OpenClaw](https://openclaw.ai) agent the ability to search, retrieve, and reason over [Ragora](https://ragora.app) knowledge bases — via MCP or REST API.

## What is this?

This repo ships a **Ragora skill file** (`ragora.md`) — a comprehensive guide that teaches AI agents how to:

- Authenticate with Ragora (API key setup, security rules, troubleshooting)
- Discover and understand knowledge base structure (collections, documents, chunks, versions, tags)
- Search via **MCP tools** or **REST API** with full request/response examples
- Run multi-step research workflows (cross-collection comparison, due diligence, versioned doc lookup)
- Handle errors, rate limits, and retries gracefully
- Format responses with proper source citations and confidence indicators
- Manage context window size with smart `top_k` tuning

It works with any MCP-compatible client — OpenClaw, Claude Desktop, Cursor, VS Code — and any HTTP-capable agent via the REST API.

## Prerequisites

- An [OpenClaw](https://openclaw.ai) instance (or any MCP-compatible AI client)
- A [Ragora](https://ragora.app) account
- A Ragora API key — create one from your [dashboard](https://app.ragora.app/settings/api-keys)

> API keys use the format `sk_live_<uuid>` and are shown **once** at creation. Copy and store it securely.

## Quick Start

### 1. Download the skill file

```bash
curl -O https://raw.githubusercontent.com/velarynai/ragora-openclaw/main/ragora.md
```

Or clone the repo:

```bash
git clone https://github.com/velarynai/ragora-openclaw.git
```

### 2. Configure the MCP connection

**YAML** (OpenClaw):

```yaml
name: ragora
type: http
url: https://mcp.ragora.app/mcp
headers:
  Authorization: Bearer ${RAGORA_API_KEY}
```

**JSON** (Claude Desktop / Cursor / VS Code):

```json
{
  "mcpServers": {
    "ragora": {
      "type": "http",
      "url": "https://mcp.ragora.app/mcp",
      "headers": {
        "Authorization": "Bearer ${RAGORA_API_KEY}"
      }
    }
  }
}
```

> Set `RAGORA_API_KEY` as an environment variable. Never hardcode keys in config files that may be committed to version control.

### 3. Verify the connection

Ask your agent to run:

```
discover_collections()
```

If it returns your collections, you're all set. If the result is empty, you may need to [access a knowledge base](https://ragora.app/marketplace) first.

## What's in the Skill File

The skill file covers everything an AI agent needs:

| Section | What it teaches |
|---------|----------------|
| **Core Concepts** | Collections, documents, chunks, versions, tags, filters, billing model |
| **Connection Setup** | MCP and REST API authentication, config examples for multiple clients |
| **MCP Tools Reference** | Static tools, dynamic per-collection tools, MCP prompts and resources |
| **REST API Reference** | Full endpoint docs with request/response schemas for all operations |
| **Error Codes** | HTTP status codes, error response format, and what the agent should do for each |
| **Rate Limiting** | Limits, retry strategy, exponential backoff, best practices |
| **Auth Troubleshooting** | Common auth failures with symptoms, causes, and fixes |
| **Core Workflow** | 5-step process: understand, discover, retrieve, synthesize, respond |
| **Multi-Step Examples** | Cross-collection research, vendor comparison, due diligence, versioned docs |
| **Query Patterns** | Task-specific query templates and refinement strategies |
| **Context Management** | `top_k` tuning guide, handling large/insufficient results |
| **Output Formatting** | Citation rules, confidence indicators, comparison tables |
| **Failure Handling** | Recovery actions for every failure type |

## Quick Reference

### MCP tools

| Tool | Description |
|------|-------------|
| `discover_collections()` | List all accessible knowledge bases |
| `search(query, top_k?)` | Search across all collections |
| `search_collection(collection_name, query, ...)` | Search a specific collection |
| `search_{slug}(query, top_k?, version?, ...)` | Dynamic per-collection search |
| `get_topic_{slug}(topic)` | Get topic info from a collection |
| `list_versions_{slug}()` | List doc versions for a collection |
| `check_balance()` | Check credit balance |

### REST API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/health` | Health check |
| `GET` | `/v1/collections` | List all collections |
| `POST` | `/v1/search` | Search across all collections |
| `POST` | `/v1/collections/{slug}/search` | Search a specific collection |
| `POST` | `/v1/collections/{slug}/topic` | Get topic from a collection |
| `GET` | `/v1/collections/{slug}/versions` | List versions |
| `GET` | `/v1/billing/balance` | Check credit balance |
| `GET` | `/v1/mcp/manifest` | List available MCP tools |
| `POST` | `/v1/mcp/execute` | Execute any MCP tool via REST |

All REST endpoints use base URL `https://api.ragora.app` and require `Authorization: Bearer <RAGORA_API_KEY>`.

## Security

- API keys are hashed (SHA-256 + bcrypt) — the raw value is only shown once at creation
- Each key scopes access to the owner's collections only
- The skill file instructs the agent to never expose API keys in outputs
- There is no test/sandbox mode; all keys are live (`sk_live_`)

## Billing

| Scenario | Cost |
|----------|------|
| Your own collections & subscriptions | Free |
| Pay-per-use marketplace products | Credits deducted per retrieval based on seller pricing |

Check your balance anytime with `check_balance()`. Top up credits at [app.ragora.app/settings/billing](https://app.ragora.app/settings/billing).

## Links

- [Ragora](https://ragora.app) — Knowledge base platform
- [Ragora Marketplace](https://ragora.app/marketplace) — Browse knowledge bases
- [Ragora Docs](https://ragora.app/docs) — Full documentation
- [OpenClaw](https://openclaw.ai) — Open-source autonomous AI agent

## License

[MIT](LICENSE)
