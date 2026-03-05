---
name: azure-proxy
description: Enable Azure OpenAI integration with OpenClaw via a lightweight local proxy. Use when configuring Azure OpenAI as a model provider, when encountering 404 errors with Azure OpenAI in OpenClaw, or when needing to use Azure credits (e.g. Visual Studio subscription) with OpenClaw subagents. Solves the api-version query parameter issue that prevents direct Azure OpenAI integration.
---

# Azure OpenAI Proxy for OpenClaw

A lightweight Node.js proxy that bridges Azure OpenAI with OpenClaw.

## The Problem

OpenClaw constructs API URLs like this:
```javascript
const endpoint = `${baseUrl}/chat/completions`;
```

Azure OpenAI requires:
```
https://{resource}.openai.azure.com/openai/deployments/{model}/chat/completions?api-version=2025-01-01-preview
```

When `api-version` is in the baseUrl, OpenClaw's path append breaks it.

## Quick Setup

### 1. Configure and Run the Proxy

```bash
# Set your Azure details
export AZURE_OPENAI_ENDPOINT="your-resource.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
export AZURE_OPENAI_API_VERSION="2025-01-01-preview"

# Run the proxy
node scripts/server.js
```

### 2. Configure OpenClaw Provider

Add to `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "providers": {
      "azure-gpt4o": {
        "baseUrl": "http://127.0.0.1:18790",
        "apiKey": "YOUR_AZURE_API_KEY",
        "api": "openai-completions",
        "authHeader": false,
        "headers": {
          "api-key": "YOUR_AZURE_API_KEY"
        },
        "models": [
          { "id": "gpt-4o", "name": "GPT-4o (Azure)" }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "models": {
        "azure-gpt4o/gpt-4o": {}
      }
    }
  }
}
```

**Important:** Set `authHeader: false` — Azure uses `api-key` header, not Bearer tokens.

### 3. (Optional) Use for Subagents

Save Azure credits by routing automated tasks through Azure:

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "model": "azure-gpt4o/gpt-4o"
      }
    }
  }
}
```

## Run as systemd Service

Copy the template and configure:

```bash
mkdir -p ~/.config/systemd/user
cp scripts/azure-proxy.service ~/.config/systemd/user/

# Edit the service file with your Azure details
nano ~/.config/systemd/user/azure-proxy.service

# Enable and start
systemctl --user daemon-reload
systemctl --user enable azure-proxy
systemctl --user start azure-proxy
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_PROXY_PORT` | `18790` | Local proxy port |
| `AZURE_PROXY_BIND` | `127.0.0.1` | Bind address |
| `AZURE_OPENAI_ENDPOINT` | — | Azure resource hostname |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o` | Deployment name |
| `AZURE_OPENAI_API_VERSION` | `2025-01-01-preview` | API version |

## Health Check

```bash
curl http://localhost:18790/health
# {"status":"ok","deployment":"gpt-4o"}
```

## Troubleshooting

**404 Resource not found:** Check endpoint hostname and deployment name match Azure Portal.

**401 Unauthorized:** API key is wrong or expired.

**Content Filter Errors:** Azure has aggressive content filtering — some prompts that work on OpenAI may get blocked.
