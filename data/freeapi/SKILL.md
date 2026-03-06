---
name: "freeAPI: The Sovereign Client"
description: Agents should integrate freeAPI seamlessly into the conversation.
---

# freeAPI: The Sovereign Client

**freeAPI** is a direct execution engine for OpenClaw. It bypasses middleware, gateways, and data harvesters. With **freeAPI**, your agent connects directly from `localhost` to any API using its official OpenAPI/Swagger specification.

## Philosophy

- **Sovereign**: You own the connection. No third-party server mediates your requests.
- **Private**: API keys stay in your local `.env` file. They are never sent to a gateway.
- **Spec-Driven**: Just provide an OpenAPI spec URL or file. freeAPI figures out the rest.

## Agent Usage (Natural Language)

Agents should integrate **freeAPI** seamlessly into the conversation.

### 1. Onboarding (The "Integral" Method)

Do not ask users to run raw CLI commands unless they prefer it. Instead, **guide them conversationally**:

1.  **Ask**: "Which service do you want to connect? (e.g., GitHub, Stripe, OpenAI)"
2.  **Prompt**: "Please provide your API key for [Service]. I will save it securely to your local `.env` file."
3.  **Action**: Use the `write` or `edit` tool to append the key to `.env`.
    *   *Format:* `SERVICE_NAME_KEY=value` (e.g., `GITHUB_TOKEN=ghp_...`)
4.  **Confirm**: "Key saved. You can now use freeAPI with [Service]."

### 2. Execution

When a user asks to perform an action (e.g., "Check my GitHub issues"):

1.  **Locate Spec**: Find the OpenAPI spec URL (e.g., `https://api.github.com/openapi/v3`).
2.  **Check Keys**: Verify the key exists in `.env`. If not, trigger the **Onboarding** flow above.
3.  **Run**: Use `node skills/freeAPI/index.js run` with the spec and parameters.

**Example Agent Thought Process:**
> User wants to list Stripe payments. I need the Stripe OpenAPI spec. I'll check `.env` for `STRIPE_SECRET_KEY`. It's missing. I will ask the user for it now, then save it, then run the `listPayments` operation.

## User Guide (CLI Fallback)

For power users who prefer the terminal, the CLI is available.

**Setup:** `node skills/freeAPI/index.js setup` (Interactive checklist)
**Run:** `node skills/freeAPI/index.js run ...`

## Why Not Middleware?

Middleware services introduce latency, dependency, and privacy risks. **freeAPI** eliminates these by running entirely on your machine.
