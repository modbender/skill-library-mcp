---
name: sooda-bridge
description: "Connect to business AI agents on the Sooda network. Use when: user mentions Sooda, the Sooda network, or asks to talk to a Sooda agent by name (travelwise, dineout, support, helpdesk, procurebot, vendorbot). NOT for general queries — only when the user specifically wants to reach an agent through Sooda."
version: 1.0.0
metadata: { "clawdbot": { "emoji": "🔗", "requires": { "env": ["SOODA_API_KEY"], "bins": ["curl"] }, "primaryEnv": "SOODA_API_KEY" } }
---

# Sooda Bridge

Send messages to business AI agents through the Sooda network.

## First-Use Setup

Before sending any message, check if `SOODA_API_KEY` is set in the environment.

**If `SOODA_API_KEY` IS set** — skip to "Send a Message".

**If `SOODA_API_KEY` is NOT set** — sign up for a session key:

1. Ask the user for their email address
2. Run the signup call inline:

```bash
curl -s -X POST https://sooda.ai/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"USER_EMAIL_HERE"}'
```

3. Parse the JSON response:
```json
{
  "agent_id": "uuid",
  "agent_name": "user-a1b2c3d4",
  "api_key": "sk_...",
  "connected_agents": ["travelwise", "dineout", "support", "helpdesk", "procurebot", "vendorbot"]
}
```

4. Hold the `api_key` value in memory as `SOODA_API_KEY` for this session
5. Tell the user: "You're connected! To persist across sessions, run: `export SOODA_API_KEY=sk_...`"

## Send a Message

Use this curl template to relay a message to any connected agent:

```bash
curl -s -X POST https://sooda.ai/api/v1/relay/AGENT_NAME \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SOODA_API_KEY" \
  -H "X-Sooda-Context-ID: CONTEXT_ID_OR_OMIT" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "USER_MESSAGE_HERE"}]
      }
    }
  }'
```

- Replace `AGENT_NAME` with the target agent (e.g. `travelwise`, `helpdesk`)
- Replace `USER_MESSAGE_HERE` with the user's message
- For the first message in a conversation, omit the `X-Sooda-Context-ID` header
- For follow-up messages, include the `context_id` from the previous response

## Response Parsing

The relay response is JSON:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "completed",
    "session_id": "uuid",
    "context_id": "uuid",
    "a2a_task_id": "uuid",
    "a2a_response": {
      "result": {
        "id": "...",
        "status": { "state": "completed" },
        "artifacts": [{
          "parts": [{"type": "text", "text": "The agent's reply text"}]
        }]
      }
    }
  }
}
```

**Extract the agent's reply** from `.result.a2a_response.result.artifacts[0].parts[0].text`.

**Save the `context_id`** from `.result.context_id` — pass it as `X-Sooda-Context-ID` on follow-ups to continue the conversation.

### Status values

| Status | Meaning | Action |
|--------|---------|--------|
| `completed` | Agent responded | Extract text from `a2a_response` |
| `working` | Agent is still processing | Poll for result (see below) |
| `queued` | Agent at capacity, message queued | Poll for result |
| `failed` | Delivery failed | Show error message to user |

### Error responses

Errors use JSON-RPC error format:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": { "code": -32600, "message": "description" }
}
```

## Async Polling

If the status is `working` or `queued`, poll for the result using the `session_id`:

```bash
curl -s https://sooda.ai/api/v1/sessions/SESSION_ID/result \
  -H "Authorization: Bearer $SOODA_API_KEY"
```

Poll every 2-3 seconds until the response contains a completed result.

## Multi-Turn Context Tracking

Every relay response includes a `context_id`. You MUST:

1. Parse and store the `context_id` from the FIRST relay response to an agent
2. Pass it as the `X-Sooda-Context-ID` header on EVERY follow-up to the same agent

If you do NOT pass the context ID, the follow-up creates a NEW conversation instead of continuing the existing one. ALWAYS pass the context ID for follow-ups.

## Available Agents

- `helpdesk` — Customer support helpdesk (orders, returns, refunds, shipping issues). Escalates to internal-ops for backend operations.
- `travelwise` — AI travel booking agent (flights, hotels, activities)
- `dineout` — AI restaurant booking agent (reservations, dining recommendations)
- `support` — Customer support (orders, returns, help)
- `procurebot` — B2B procurement agent (sourcing, quotes, purchase orders)
- `vendorbot` — B2B vendor/supplier sales agent

More agents are added as partners join the network.

## External Endpoints

| URL | Method | Data Sent | Purpose |
|-----|--------|-----------|---------|
| `https://sooda.ai/api/v1/signup` | POST | Email, optional agent name | One-time signup to get API key |
| `https://sooda.ai/api/v1/relay/{agent}` | POST | JSON-RPC message with user text | Send A2A message to a business agent |
| `https://sooda.ai/api/v1/sessions/{id}/result` | GET | None (Bearer token in header) | Poll for async agent response |

## Security & Privacy

- All communication uses HTTPS only. No plaintext HTTP requests.
- Authentication via Bearer token (`SOODA_API_KEY`) in the Authorization header.
- No local data storage — the API key is held in memory for the session only.
- Message content is opaque to Sooda's relay layer; it is forwarded to the target agent as-is.
- The API key scopes access to the registered agent's connections only.

## Trust Statement

Sooda.ai is a third-party A2A relay platform. By using this skill, messages are sent through Sooda's infrastructure to business agents registered on the network. The `SOODA_API_KEY` controls which agents you can communicate with — it cannot access other users' data or agents outside your connection graph. Sooda does not store message content beyond delivery; see [sooda.ai](https://sooda.ai) for full terms.
