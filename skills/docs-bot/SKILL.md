---
name: docs-bot
displayName: Docs Bot
description: Scans and fetches the most up-to-date documentation for coding tasks. Use when building integrations (e.g. OpenRouter), implementing third-party APIs, or when the user asks for current docs, model lists, or API reference for a service.
---

# Docs Bot — Up-to-Date Docs Scanner

When working on integrations or any coding task that depends on external APIs or services, **fetch current documentation** instead of relying on training data. Docs and model lists change frequently.

## When to Apply

- Building or debugging **OpenRouter** (or similar) integrations
- Implementing or updating **third-party API** usage
- User asks for "latest docs", "current API", "model list", or "official reference"
- Choosing models, parameters, or SDK usage for a service

## Scan Workflow

1. **Identify the canonical doc base** for the task (e.g. `https://openrouter.ai/docs` for OpenRouter).
2. **Fetch the relevant URLs** using the web fetch tool:
   - Main docs/quickstart
   - API reference
   - Models/list page when model IDs, pricing, or capabilities matter
3. **Use the fetched content** to implement or correct code (endpoints, headers, request/response shapes, model IDs).
4. **Cite the URLs** you used so the user can verify or read more.

## OpenRouter — Canonical URLs

When the task involves OpenRouter, fetch these for current behavior:

| Purpose | URL |
|--------|-----|
| Quickstart & SDK | https://openrouter.ai/docs |
| API reference (request/response, params) | https://openrouter.ai/docs/api/reference |
| Models (IDs, pricing, context, filters) | https://openrouter.ai/models |
| OpenAPI spec | https://openrouter.ai/openapi.json |

**Integration checklist (OpenRouter):**

- Base URL: `https://openrouter.ai/api/v1`
- Chat completions: `POST .../chat/completions`
- Auth header: `Authorization: Bearer <OPENROUTER_API_KEY>`
- Optional headers: `HTTP-Referer`, `X-Title` for attribution
- Model IDs include provider prefix (e.g. `openai/gpt-4o`, `anthropic/claude-sonnet-4`)
- Confirm model ID and parameters from the **current** models page; names and availability change.

## Other Services

For other APIs or SDKs:

1. Find the official docs root (e.g. `https://<service>.com/docs` or `/developer`).
2. Fetch quickstart + API reference (and models/catalog if applicable).
3. Prefer official docs over blog posts or third-party tutorials for correctness and recency.

## Output

- Base implementation on **fetched** docs, not memory.
- If a URL returns an error or empty content, say so and fall back to a web search or alternative URL.
- Keep answers concise; link to the exact pages used for details.
