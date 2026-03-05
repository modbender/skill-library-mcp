# Clawhub Skill: Intercom Conversations (Read)

Clawhub loads this Node module and calls `default(input)`.

## Required env

- `INTERCOM_ACCESS_TOKEN` (required)

## Install

```bash
npm install
```

## Inputs

### List
```json
{ "action": "conversations.list", "per_page": 50, "starting_after": "cursor" }
```

### Find
```json
{ "action": "conversations.find", "conversation_id": "123", "display_as": "plaintext" }
```

### Search
```json
{ "action": "conversations.search", "query": { "operator": "AND", "value": [] }, "pagination": { "per_page": 50 } }
```

## Outputs

All successful responses include `ok: true` and echo the `action`.

- list/search: `{ ok, action, conversations, next_starting_after }`
- find: `{ ok, action, conversation }`

Errors: `{ ok: false, error, supported_actions? }`

## Contracts / metadata

- OpenAPI spec: `openapi.yaml`
- Skill registry metadata: `clawhub.skill.json`
