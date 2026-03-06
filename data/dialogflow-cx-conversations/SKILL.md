---
name: dialogflow-cx-conversations
description: Manage conversations and sessions in Google Dialogflow CX via REST API. Use for testing intents, handling user interactions, and managing conversation state. Supports v3beta1 API.
---

# Dialogflow CX Conversations

Manage conversations and sessions in Google Dialogflow CX via REST API for testing and interaction handling.

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

### Detect Intent
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/sessions/${SESSION_ID}:detectIntent" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "queryInput": {
      "text": {
        "text": "Hello"
      },
      "languageCode": "en"
    }
  }'
```

### Match Intent (no state change)
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/sessions/${SESSION_ID}:matchIntent" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "queryInput": {
      "text": {
        "text": "Hello"
      },
      "languageCode": "en"
    }
  }'
```

### Create Test Case
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/testCases" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Greeting Test",
    "testCaseConversationTurns": [
      {
        "userInput": {
          "input": {
            "text": {
              "text": "Hi"
            }
          }
        },
        "virtualAgentOutput": {
          "textResponses": [
            {
              "text": ["Hello!"]
            }
          ]
        }
      }
    ]
  }'
```

## Key Resources

| Resource | Description |
|----------|-------------|
| **Sessions** | Conversation instances with state |
| **Detect Intent** | Process user input and get responses |
| **Test Cases** | Automated conversation testing |

## Quick Reference

For detailed API reference:
- **Conversations & Testing**: See [references/conversations.md](references/conversations.md)

## Scripts

- `scripts/conversations.py` — CLI wrapper for conversation operations

### Usage
```bash
python scripts/conversations.py detect-intent --agent AGENT_NAME --text "Hello"
python scripts/conversations.py match-intent --agent AGENT_NAME --text "Hello"
```

## Tips

- Session IDs can be any unique string (e.g., UUID)
- Use detectIntent for full conversation flow, matchIntent for testing without state changes
- Test cases help validate conversation logic before deployment
