---
name: Vincent - Brave Search for agents
description: |
  Web and news search powered by Brave Search. Use this skill when users want to search the web,
  find news articles, or look up current information. Pay-per-call via Vincent credit system.
  Triggers on "search the web", "web search", "brave search", "search news", "find information",
  "look up", "current events".
allowed-tools: Read, Write, Bash(npx:*, curl:*)
version: 1.0.0
author: HeyVincent <contact@heyvincent.ai>
license: MIT
homepage: https://heyvincent.ai
source: https://github.com/HeyVincent-ai/Vincent
metadata:
  clawdbot:
    homepage: https://heyvincent.ai
    requires:
      config:
        - ${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/datasources
        - ./datasources
---

# Vincent - Brave Search for agents

Use this skill to search the web and news using Brave Search. All requests are proxied through the Vincent backend, which handles authentication with the Brave Search API, enforces rate limits, tracks per-call costs, and deducts from your credit balance automatically.

**No API keys to manage.** The agent authenticates with a Vincent API key scoped to a `DATA_SOURCES` secret. Vincent handles the upstream Brave Search API credentials server-side -- the agent never sees or manages Brave API keys.

All commands use the `@vincentai/cli` package. API keys are stored and resolved automatically — you never handle raw keys or file paths.

## Security Model

This skill is designed for **autonomous agent operation with pay-per-call pricing and human oversight**.

**No environment variables are required** because this skill uses agent-first onboarding: the agent creates a `DATA_SOURCES` secret at runtime by calling the Vincent API, which returns a scoped API key. The CLI stores the returned API key automatically during creation. The config paths where the key is persisted (`${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/datasources/` or `./datasources/`) are declared in this skill's metadata.

**The agent's API key is not a Brave Search API key.** It is a scoped Bearer token for the Vincent proxy. The Vincent server authenticates with Brave Search on the agent's behalf. The agent cannot access the upstream API directly or bypass the proxy's credit and rate-limit enforcement.

**Model invocation is intentionally enabled.** The purpose of this skill is to give AI agents autonomous web search capabilities. The agent is expected to search the web and news on its own. The human controls spending through credit balance and payment method management at `https://heyvincent.ai`.

**All API calls go exclusively to `heyvincent.ai`** over HTTPS/TLS. The Vincent server then calls the Brave Search API. The agent does not contact Brave directly.

**Key lifecycle:**

- **Creation**: The agent runs `secret create` with `--type DATA_SOURCES` — the CLI stores the API key automatically and returns a `keyId` and `claimUrl`.
- **Claim**: The human operator uses the claim URL to take ownership, add credit, and manage payment at `https://heyvincent.ai`.
- **Credit**: Each API call costs a small amount (see Pricing below). The human adds credit via the frontend. Calls are rejected when credit runs out and no payment method is on file.
- **Revocation**: The secret owner can revoke the agent's API key at any time from the Vincent frontend.

## Pricing

| Endpoint | Cost per call |
| --- | --- |
| Web search | $0.005 |
| News search | $0.005 |

Credit is deducted automatically per call. The response includes `_vincent.creditRemainingUsd` so the agent can track remaining balance.

## Quick Start

### 1. Check for Existing Keys

Before creating a new secret, check if one already exists:

```bash
npx @vincentai/cli@latest secret list --type DATA_SOURCES
```

If a key is returned, use its `id` as the `--key-id` for all subsequent commands. If no keys exist, create a new secret.

### 2. Create a Data Sources Secret

```bash
npx @vincentai/cli@latest secret create --type DATA_SOURCES --memo "My agent data sources"
```

Returns `keyId` (use for all future commands) and `claimUrl` (share with the user).

After creating, tell the user:

> "Here is your data sources claim URL: `<claimUrl>`. Use this to claim ownership and add credit for Brave Search and other data sources at https://heyvincent.ai."

**Important:** The secret must be claimed and have credit (or a payment method on file) before API calls will succeed.

### 3. Web Search

```bash
npx @vincentai/cli@latest brave web --key-id <KEY_ID> --q "latest AI news" --count 10
```

Parameters:

- `--q` (required): Search query (1-400 characters)
- `--count` (optional): Number of results, 1-20 (default: 10)
- `--offset` (optional): Pagination offset, 0-9
- `--freshness` (optional): Time filter — `pd` (past day), `pw` (past week), `pm` (past month), `py` (past year)
- `--country` (optional): 2-letter country code for localized results (e.g., `us`, `gb`, `de`)

Returns web results with titles, URLs, descriptions, and metadata.

### 4. News Search

```bash
npx @vincentai/cli@latest brave news --key-id <KEY_ID> --q bitcoin --count 10
```

Parameters:

- `--q` (required): Search query (1-400 characters)
- `--count` (optional): Number of results, 1-20 (default: 10)
- `--freshness` (optional): Time filter — `pd` (past day), `pw` (past week), `pm` (past month), `py` (past year)

Returns news articles with titles, URLs, descriptions, publication dates, and source information.

## Response Metadata

Every successful response includes a `_vincent` object with:

```json
{
  "_vincent": {
    "costUsd": 0.005,
    "creditRemainingUsd": 4.99
  }
}
```

Use `creditRemainingUsd` to warn the user when credit is running low.

## Output Format

Web search results:

```json
{
  "web": {
    "results": [
      {
        "title": "Article Title",
        "url": "https://example.com/article",
        "description": "A brief description of the article content."
      }
    ]
  },
  "_vincent": {
    "costUsd": 0.005,
    "creditRemainingUsd": 4.99
  }
}
```

News search results follow the same structure with additional `age` and `source` fields per result.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Check that the key-id is correct; re-link if needed |
| `402 Insufficient Credit` | Credit balance is zero and no payment method on file | User must add credit at heyvincent.ai |
| `429 Rate Limited` | Exceeded 60 requests/minute | Wait and retry with backoff |
| `Key not found` | API key was revoked or never created | Re-link with a new token from the secret owner |

## Rate Limits

- 60 requests per minute per API key across all data source endpoints (Twitter + Brave Search combined)
- If rate limited, you'll receive a `429` response. Wait and retry.

## Re-linking (Recovering API Access)

If the agent loses its API key, the secret owner can generate a **re-link token** from the frontend. The agent then exchanges this token for a new API key.

```bash
npx @vincentai/cli@latest secret relink --token <TOKEN_FROM_USER>
```

The CLI exchanges the token for a new API key, stores it automatically, and returns the new `keyId`. Re-link tokens are one-time use and expire after 10 minutes.

## Important Notes

- A single `DATA_SOURCES` API key works for **all** data sources (Twitter, Brave Search, etc.). You do not need a separate key per data source.
- Always share the claim URL with the user after creating a secret.
- If a call is rejected with a credit error, tell the user to add credit at `https://heyvincent.ai`.
