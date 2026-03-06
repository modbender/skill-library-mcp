---
name: dialogflow-cx-agents
description: Manage agents in Google Dialogflow CX via REST API. Use for creating, listing, updating, and deleting chatbot agents. Supports v3beta1 API.
---

# Dialogflow CX Agents

Manage Google Dialogflow CX agents via REST API.

## Prerequisites

- Google Cloud project with Dialogflow CX API enabled
- Service account or OAuth credentials with Dialogflow API access
- `gcloud` CLI authenticated OR bearer token

## Authentication

### Option 1: gcloud CLI (recommended)
```bash
gcloud auth application-default login
TOKEN=$(gcloud auth print-access-token)
```

### Option 2: Service Account
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
TOKEN=$(gcloud auth application-default print-access-token)
```

## API Base URL

```
https://dialogflow.googleapis.com/v3beta1
```

Regional endpoints available:
- `https://{region}-dialogflow.googleapis.com` (e.g., `us-central1`, `europe-west1`)

## Common Operations

### List Agents
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create Agent
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "My Agent",
    "defaultLanguageCode": "en",
    "timeZone": "Asia/Kolkata"
  }'
```

### Get Agent
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Update Agent
```bash
curl -X PATCH \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Updated Agent Name"
  }'
```

### Delete Agent
```bash
curl -X DELETE \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
```

## Key Resources

| Resource | Description |
|----------|-------------|
| **Agents** | Top-level container for flows, intents, entity types |

## Quick Reference

For detailed API reference:
- **Agents**: See [references/agents.md](references/agents.md)

## Scripts

- `scripts/agents.py` — CLI wrapper for agent management operations

### Usage
```bash
python scripts/agents.py list --project PROJECT_ID --location LOCATION
python scripts/agents.py create --project PROJECT_ID --location LOCATION --name "My Agent"
python scripts/agents.py get --project PROJECT_ID --location LOCATION --agent AGENT_ID
python scripts/agents.py update --agent AGENT_NAME --name "New Name"
python scripts/agents.py delete --agent AGENT_NAME
```

## Tips

- Use `locations/global` for multi-region agents
- Agent IDs are generated automatically on creation