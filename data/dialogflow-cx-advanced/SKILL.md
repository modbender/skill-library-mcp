---
name: dialogflow-cx-advanced
description: Manage advanced features in Google Dialogflow CX via REST API. Use for environments, webhooks, and deployment management. Supports v3beta1 API.
---

# Dialogflow CX Advanced

Manage advanced features in Google Dialogflow CX via REST API for deployment and external integrations.

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

### List Environments
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/environments" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create Environment
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/environments" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "production",
    "description": "Production environment"
  }'
```

### List Webhooks
```bash
curl -X GET \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/webhooks" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create Webhook
```bash
curl -X POST \
  "https://dialogflow.googleapis.com/v3beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/${AGENT_ID}/webhooks" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Order Fulfillment",
    "genericWebService": {
      "uri": "https://your-webhook.com/fulfill"
    }
  }'
```

## Key Resources

| Resource | Description |
|----------|-------------|
| **Environments** | Deployment stages (draft, production) |
| **Webhooks** | External fulfillment endpoints |
| **Continuous Testing** | Ongoing health monitoring |

## Quick Reference

For detailed API reference:
- **Advanced Features**: See [references/advanced.md](references/advanced.md)

## Scripts

- `scripts/advanced.py` — CLI wrapper for advanced operations

### Usage
```bash
python scripts/advanced.py list-environments --agent AGENT_NAME
python scripts/advanced.py list-webhooks --agent AGENT_NAME
```

## Tips

- Use environments to separate development, staging, and production
- Webhooks enable external processing and integrations
- Continuous testing helps maintain conversation quality
