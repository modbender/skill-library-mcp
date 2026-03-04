---
name: dialogflow-cx-nlu
description: Manage intents and entity types in Google Dialogflow CX via REST API. Use for creating, updating, and managing natural language understanding components. Supports v3beta1 API.
---

# Dialogflow CX NLU

Manage intents and entity types in Google Dialogflow CX via REST API for natural language understanding.

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

### List Intents
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/intents" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create Intent
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/intents" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Book Flight",
    "trainingPhrases": [
      {
        "parts": [{"text": "I want to book a flight"}],
        "repeatCount": 1
      }
    ]
  }'
```

### List Entity Types
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/entityTypes" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create Entity Type
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/entityTypes" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Cities",
    "kind": "KIND_LIST",
    "entities": [
      {"value": "New York"},
      {"value": "Los Angeles"}
    ]
  }'
```

## Key Resources

| Resource | Description |
|----------|-------------|
| **Intents** | Classify user utterances and extract parameters |
| **Entity Types** | Define structured data extraction patterns |

## Quick Reference

For detailed API reference:
- **Intents**: See [references/intents.md](references/intents.md)
- **Entity Types**: See [references/entities.md](references/entities.md)

## Scripts

- `scripts/nlu.py` — CLI wrapper for intents and entity types operations

### Usage
```bash
python scripts/nlu.py list-intents --agent AGENT_NAME
python scripts/nlu.py create-intent --agent AGENT_NAME --intent "Book Flight" --phrases "book a flight,I want to fly"
python scripts/nlu.py list-entities --agent AGENT_NAME
python scripts/nlu.py create-entity --agent AGENT_NAME --name "Cities" --values "New York,Los Angeles"
```

## Tips

- Use training phrases that cover various ways users might express the intent
- Entity types can be system (built-in) or custom
- Use KIND_MAP for entities with synonyms, KIND_LIST for simple lists
