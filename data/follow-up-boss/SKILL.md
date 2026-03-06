---
name: follow-up-boss
description: CLI for interacting with the Follow Up Boss API. Manage people, notes, tasks, events, deals, webhooks, and more.
---

# Follow Up Boss (CLI)

CLI for interacting with the Follow Up Boss API.

## Setup

1. **Get API Key**: Follow Up Boss → Admin → API → Create API Key

2. **Set Environment Variable**:
```bash
export FUB_API_KEY="fka_xxxxxxxxxxxx"
```

## CLI Usage

```bash
node fub.js <command> [options]
```

## Commands

| Command | Description |
|---------|-------------|
| `me` | Current user info |
| `people [query]` | List/search people |
| `person <id>` | Get person details |
| `people create <json>` | Create person via /events (triggers automations) |
| `people update <id> <json>` | Update a person |
| `notes <personId>` | Get notes for a person |
| `notes create <json>` | Create a note |
| `tasks [query]` | List tasks |
| `tasks create <json>` | Create a task |
| `tasks complete <id>` | Complete a task |
| `events [query]` | List events |
| `events create <json>` | Create event (for lead intake) |
| `pipelines` | Get pipelines |
| `deals [query]` | List deals |
| `deals create <json>` | Create a deal |
| `textmessages <personId>` | Get text messages for a person |
| `textmessages create <json>` | Log a text (NOT sent - recorded only!) |
| `emails <personId>` | Get emails for a person |
| `emails create <json>` | Log an email (NOT sent - recorded only!) |
| `calls <personId>` | Get calls for a person |
| `calls create <json>` | Log a call |
| `webhooks` | List webhooks |
| `webhooks create <json>` | Create webhook |
| `webhooks delete <id>` | Delete webhook |
| `sources` | Get lead sources |
| `users` | Get users/agents |
| `search <query>` | Global search |

## Examples

```bash
# List people
node fub.js people "limit=10"

# Get person
node fub.js person 123

# Create a lead (triggers automations!)
node fub.js events create '{"source":"Website","system":{"name":"John Doe","email":"john@test.com","phone":"5551234567"}}'

# Add a note
node fub.js notes create '{"personId":123,"body":"Called - left voicemail"}'

# Create task
node fub.js tasks create '{"personId":123,"body":"Follow up","dueDate":"2026-02-20"}'

# Complete task
node fub.js tasks complete 456

# Log a text (NOT sent - recorded!)
node fub.js textmessages create '{"personId":123,"body":"Hey!","direction":"outbound"}'

# Log a call
node fub.js calls create '{"personId":123,"direction":"outbound","outcome":"voicemail"}'

# Search
node fub.js search "john"
```

## Important Notes

- **Text/Email Logging**: The API can log texts and emails but cannot actually send them. Use FUB's built-in texting or integrations like SendHub for sending.
- **Rate Limits**: GET /events: 20 req/10 sec, All else: 250 req/10 sec
