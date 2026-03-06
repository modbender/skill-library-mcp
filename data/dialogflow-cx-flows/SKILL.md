---
name: dialogflow-cx-flows
description: Manage flows and pages in Google Dialogflow CX via REST API. Use for creating and organizing conversation paths within agents. Supports v3beta1 API.
---

# Dialogflow CX Flows

Manage flows and pages in Google Dialogflow CX via REST API for organizing conversation paths.

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

### List Flows
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/flows" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create Flow
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/flows" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Booking Flow",
    "description": "Handles flight booking conversations"
  }'
```

### List Pages
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/flows/${FLOW_ID}/pages" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create Page
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/flows/${FLOW_ID}/pages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Collect Destination",
    "entryFulfillment": {
      "messages": [
        {
          "text": {
            "text": ["Where would you like to fly?"]
          }
        }
      ]
    }
  }'
```

## Key Resources

| Resource | Description |
|----------|-------------|
| **Flows** | Conversation paths within an agent |
| **Pages** | States within a flow |
| **Transition Routes** | Routing logic between pages |
| **Versions** | Immutable snapshots of flows |

## Quick Reference

For detailed API reference:
- **Flows & Pages**: See [references/flows.md](references/flows.md)

## Scripts

- `scripts/flows.py` — CLI wrapper for flows and pages operations

### Usage
```bash
python scripts/flows.py list-flows --agent AGENT_NAME
python scripts/flows.py list-pages --flow FLOW_NAME
python scripts/flows.py get-flow --flow FLOW_NAME
python scripts/flows.py get-page --page PAGE_NAME
```

## Tips

- Every agent has a default "Default Start Flow"
- Pages represent conversation states
- Use transition routes to move between pages based on intents or conditions
- Train flows after making changes to update NLU
