---
name: agentgate
description: "API gateway for personal data with human-in-the-loop write approval. Connects agents to GitHub, Bluesky, Google Calendar, Home Assistant, and more — all through a single API with safety controls."
homepage: "https://agentgate.org"
metadata: { "openclaw": { "emoji": "🚪", "primaryEnv": "AGENT_GATE_TOKEN", "requires": { "env": ["AGENT_GATE_TOKEN", "AGENT_GATE_URL"] } } }
---

# agentgate

API gateway for AI agents to access personal data with human-in-the-loop write approval.

- **Reads** (GET) execute immediately
- **Writes** (POST/PUT/PATCH/DELETE) go through an approval queue
- **Bypass mode** available for trusted agents (writes execute immediately)

GitHub: <https://github.com/monteslu/agentgate>
Docs: <https://agentgate.org>

## Setup

**agentgate server runs on a separate machine from OpenClaw.** This is by design — your agent should not have direct access to the server holding your credentials. Install and run agentgate on a different computer (or VPS/container on a different host). See <https://agentgate.org> for setup instructions.

Once agentgate is running, configure these environment variables for your OpenClaw agent:

- `AGENT_GATE_URL` — agentgate base URL (e.g., `http://your-agentgate-host:3050`)
- `AGENT_GATE_TOKEN` — your agent's API key (create in the agentgate Admin UI → API Keys)

## Authentication

All requests require the API key in the Authorization header:

```
Authorization: Bearer $AGENT_GATE_TOKEN
```

## First Steps — Service Discovery

After connecting, discover what's available on your instance:

```
GET $AGENT_GATE_URL/api/agent_start_here
Authorization: Bearer $AGENT_GATE_TOKEN
```

Returns your agent's config, available services, accounts, and full API documentation.

## Instance-Specific Skills

agentgate generates additional skills tailored to your instance with your specific accounts and endpoints. See the [agentgate skills documentation](https://agentgate.org/docs/skills) for details on how to install and update them.

## Supported Services

agentgate supports many services out of the box. Common ones include:

- **Code:** GitHub, Jira
- **Social:** Bluesky, Mastodon, LinkedIn
- **Search:** Brave Search, Google Search
- **Personal:** Google Calendar, YouTube, Fitbit
- **IoT:** Home Assistant
- **Messaging:** Twilio, Plivo

New services are added regularly. Check `GET /api/agent_start_here` for what's configured on your instance.

## Reading Data

```
GET $AGENT_GATE_URL/api/{service}/{accountName}/{path}
Authorization: Bearer $AGENT_GATE_TOKEN
```

Example: `GET $AGENT_GATE_URL/api/github/myaccount/repos/owner/repo`

## Writing Data

Writes go through the approval queue:

```
POST $AGENT_GATE_URL/api/queue/{service}/{accountName}/submit
Authorization: Bearer $AGENT_GATE_TOKEN
Content-Type: application/json

{
  "requests": [
    {
      "method": "POST",
      "path": "/the/api/path",
      "body": { "your": "payload" }
    }
  ],
  "comment": "Explain what you are doing and why"
}
```

**Always include a clear comment** explaining your intent. Include links to relevant resources.

### Check write status

```
GET $AGENT_GATE_URL/api/queue/{service}/{accountName}/status/{id}
Authorization: Bearer $AGENT_GATE_TOKEN
```

Statuses: `pending` → `approved` → `executing` → `completed` (or `rejected`/`failed`/`withdrawn`)

### Withdraw a pending request

```
DELETE $AGENT_GATE_URL/api/queue/{service}/{accountName}/status/{id}
Authorization: Bearer $AGENT_GATE_TOKEN
Content-Type: application/json

{ "reason": "No longer needed" }
```

### Binary uploads

For binary data (images, files), set `binaryBase64: true` in the request body:

```json
{
  "method": "POST",
  "path": "com.atproto.repo.uploadBlob",
  "binaryBase64": true,
  "headers": { "Content-Type": "image/jpeg" },
  "body": "<base64 encoded data>"
}
```

## Inter-Agent Messaging

Agents can message each other through agentgate for multi-agent coordination.

### Send a message

```
POST $AGENT_GATE_URL/api/agents/message
Authorization: Bearer $AGENT_GATE_TOKEN
Content-Type: application/json

{ "to_agent": "agent_name", "message": "Hello!" }
```

### Read messages

```
GET $AGENT_GATE_URL/api/agents/messages?unread=true
Authorization: Bearer $AGENT_GATE_TOKEN
```

### Mark as read

```
POST $AGENT_GATE_URL/api/agents/messages/{id}/read
Authorization: Bearer $AGENT_GATE_TOKEN
```

### Broadcast to all agents

```
POST $AGENT_GATE_URL/api/agents/broadcast
Authorization: Bearer $AGENT_GATE_TOKEN
Content-Type: application/json

{ "message": "Team announcement" }
```

### Discover agents

```
GET $AGENT_GATE_URL/api/agents/messageable
Authorization: Bearer $AGENT_GATE_TOKEN
```

Messaging modes (configured by admin): `off`, `supervised` (requires approval), `open` (immediate delivery).

## Mementos (Persistent Memory)

Store and retrieve notes across sessions using keyword tags.

### Store a memento

```
POST $AGENT_GATE_URL/api/agents/memento
Authorization: Bearer $AGENT_GATE_TOKEN
Content-Type: application/json

{ "content": "Important info to remember", "keywords": ["project", "notes"] }
```

### Search by keyword

```
GET $AGENT_GATE_URL/api/agents/memento/search?keywords=project&limit=10
Authorization: Bearer $AGENT_GATE_TOKEN
```

### Fetch full content by IDs

```
GET $AGENT_GATE_URL/api/agents/memento/42,38
Authorization: Bearer $AGENT_GATE_TOKEN
```

### List your keywords

```
GET $AGENT_GATE_URL/api/agents/memento/keywords
Authorization: Bearer $AGENT_GATE_TOKEN
```

## Important Notes

- Always include clear comments on write requests
- Be patient with writes — approval requires human action
- Use `GET /api/agent_start_here` to discover available services
- See [agentgate docs](https://agentgate.org) for instance-specific skill setup
