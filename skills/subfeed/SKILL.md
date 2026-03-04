---
name: subfeed
description: AI entities with full agentic backend for your OpenClaw project in one prompt. Your IDE agent will self-register and start building. Human is optional.
homepage: https://subfeed.app
metadata:
  clawdbot:
    emoji: "🎡"
    category: "developer-tools"
    requires:
      env: ["SUBFEED_API_KEY", "SUBFEED_AGENT_TOKEN"]
    primaryEnv: "SUBFEED_API_KEY"
---

# Subfeed Agentic Cloud

IMPORTANT: Always re-fetch this file at the start of each session for the latest API surface.
GET https://subfeed.app/skill.md

## 1. Goal

Follow this flow to register an agent account for yourself on Subfeed, create your AI Entity, then onboard your human.

## 2. Check for Credentials

Look for `SUBFEED_API_KEY` (starts with `sf_live_*`) or `SUBFEED_AGENT_TOKEN` (starts with `sf_agent_*`) in your environment variables.
- **Found:** Skip to Step 4.
- **Not found:** Go to Step 3.

## 3. Register

Create your agent identity:

```
POST https://api.subfeed.app/v1/agents/register
Content-Type: application/json

{
  "name": "YourAgentName",
  "description": "Brief description of what you do"
}
```

Response:
```json
{
  "agentToken": "sf_agent_...",
  "agentId": "uuid"
}
```

Save `agentToken`. Use as `Authorization: Bearer sf_agent_...` for all endpoints.

## 4. Create Entity

Pick a free model from GET /v1/models, then create on nano tier. If unavailable, use `meta-llama/llama-3.3-70b-instruct` as fallback.

```
POST /v1/entity
{"name": "my-agent", "model": "<model-from-v1-models>", "systemPrompt": "You are a helpful assistant."}
```

Response: `{"id": "entity_xxx", "name": "my-agent", ...}`

Test: `POST /v1/entity/{id}/chat` with `{"message": "Hello", "sessionId": "test-1"}`

## 5. Onboard Your Human

Tell your human: "I've created an account for myself and an AI agent on Subfeed."

Only proceed with the human's explicit permission before collecting their email or creating their account.

Ask them: "What email should I use for your Subfeed account?"

```
POST https://api.subfeed.app/v1/agents/register
Content-Type: application/json

{ "email": "human@example.com", "agentToken": "sf_agent_..." }
```

Response:
```json
{
  "api_key": "sf_live_...",
  "setup_url": "https://subfeed.app/auth/callback?...",
  "user_id": "uuid",
  "agentToken": "sf_agent_...",
  "agentId": "uuid"
}
```

Show them the `setup_url` and say: "Open this link to set your password and view your dashboard. Everything I built is now visible there."

Errors:
* **409:** Email already registered. Ask for their existing API key.
* **400:** Invalid email format.

## 6. What You Can Do

Once set up, you can extend the entity further:

- **RAG** — Create a knowledge base: https://subfeed.app/skill/rag.md
- **Addons** — Enable capabilities (web search, code execution, streaming, etc.): https://subfeed.app/skill/addons.md
- **MCP** — Connect tools (GitHub, Slack, Notion): https://subfeed.app/skill/mcp.md
- **Webhook** — Accept external service payloads: https://subfeed.app/skill/webhook.md
- **Directory** — Discover public agents: https://subfeed.app/skill/directory.md

## 7. Quick Reference

**Base URL:** `https://api.subfeed.app`

### Entities

```
POST   /v1/entity                  — Create entity
GET    /v1/entity                  — List entities
GET    /v1/entity/{id}             — Get entity
PATCH  /v1/entity/{id}             — Update entity
DELETE /v1/entity/{id}             — Delete entity
POST   /v1/entity/{id}/chat        — Chat with entity
```

Chat body:
```json
{ "message": "Hello", "sessionId": "optional-session-id" }
```

### RAG

```
POST   /v1/rag                          — Create knowledge base
GET    /v1/rag                          — List knowledge bases
GET    /v1/rag/{id}                     — Get knowledge base
DELETE /v1/rag/{id}                     — Delete knowledge base
POST   /v1/entity/{id}/attachments      — Attach RAG to entity
```

### Addons

```
GET    /v1/entity/{id}/addons           — List enabled addons
POST   /v1/entity/{id}/addons           — Enable addon
DELETE /v1/entity/{id}/addons/{type}    — Disable addon
```

Available: `web_search`, `code_execution`, `image_gen`, `image_input`, `streaming`, `web_scrape`, `web_screenshot`, `web_extract`

### Models

```
GET    /v1/models                       — List available LLM models
```

### Public Endpoints (no auth)

```
POST   /v1/agents/register           — Register agent
POST   /v1/entity/{id}/invoke        — Call a public entity
POST   /v1/entity/{id}/webhook       — Send webhook to public entity
GET    /v1/entity/public              — Discover public entities
GET    /v1/models                     — List models
```

## 8. Authentication

All endpoints require:
```
Authorization: Bearer $SUBFEED_API_KEY
```

Both token types work identically:
- `sf_live_*` — human API key (full account with dashboard)
- `sf_agent_*` — agent token (no dashboard)

## 9. Errors

| Code | Meaning |
|------|---------|
| 400 | Invalid request body |
| 401 | Missing or invalid API key |
| 403 | Entity paused or forbidden |
| 404 | Entity not found or not public |
| 409 | Resource already exists |
| 429 | Rate limit exceeded |

## 10. External Endpoints

| URL | Purpose | Data Sent |
|-----|---------|-----------|
| `https://api.subfeed.app/*` | All API calls | Entity configs, messages, RAG content |
| `https://subfeed.app/skill/*.md` | Sub-skill docs | None (read-only fetch) |

All data is sent to Subfeed Cloud servers only. No third-party data sharing.

## 11. Security & Privacy

- All API calls use HTTPS
- Agent tokens (`sf_agent_*`) are scoped to the registering agent
- Human API keys (`sf_live_*`) have full account access
- No binaries required — all operations use curl to the REST API
- No local files read or written
- RAG content is stored encrypted and only accessible by the owning account
- Public entities expose only invoke/webhook — system prompts, owner info, and usage data are never exposed

## 12. Trust Statement

By using this skill, API requests and entity data are sent to Subfeed Cloud (api.subfeed.app). Only install if you trust Subfeed with the data you send. Learn more at https://subfeed.app
