---
name: jina-deepsearch
description: Jina DeepSearch API access via AIHubMix - use curl to call the HTTP API directly.
homepage: https://jina.ai/
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "env": ["AIHUBMIX_API_KEY"], "bins": ["curl"] },
        "install":
          [
            {
              "id": "config",
              "kind": "manual",
              "label": "Configure AIHUBMIX_API_KEY",
              "instructions": "Set AIHUBMIX_API_KEY environment variable. Get your key from https://aihubmix.com",
            },
          ],
      },
  }
---

# Jina DeepSearch

Access Jina's DeepSearch API via AIHubMix using curl.

## Quick Start

```bash
# Set your API key first
export AIHUBMIX_API_KEY="sk-..."

# Call the API directly with curl
curl https://aihubmix.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AIHUBMIX_API_KEY" \
  -d '{
    "model": "jina-deepsearch-v1",
    "messages": [{"role": "user", "content": "Your search query"}]
  }'
```

## Configuration

Set `AIHUBMIX_API_KEY` environment variable. Get your API key from https://aihubmix.com

## Model

- `jina-deepsearch-v1` - Jina's deep search model
