# Azure OpenAI Proxy for OpenClaw

A lightweight Node.js proxy that enables Azure OpenAI integration with OpenClaw.

## Why This Exists

OpenClaw constructs API URLs by appending `/chat/completions` to the provider's `baseUrl`. Azure OpenAI requires a `?api-version=YYYY-MM-DD` query parameter at the end of the URL. When you put query params in the baseUrl, OpenClaw's path append breaks it.

This proxy sits between OpenClaw and Azure, forwarding requests with the correct URL structure.

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install BenediktSchackenberg/openclaw-tools/azure-proxy
```

### Manual

Clone this repo and copy `azure-proxy/` to your skills directory.

## Quick Start

See [SKILL.md](./SKILL.md) for complete setup instructions.

```bash
export AZURE_OPENAI_ENDPOINT="your-resource.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
node scripts/server.js
```

Then configure OpenClaw to point to `http://127.0.0.1:18790`.

## License

MIT
