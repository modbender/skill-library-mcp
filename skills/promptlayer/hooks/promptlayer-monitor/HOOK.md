---
name: promptlayer-monitor
description: "Log every agent message to PromptLayer for observability and monitoring"
metadata:
  { "openclaw": { "emoji": "📊", "events": ["message:sent"], "requires": { "env": ["PROMPTLAYER_API_KEY"] } } }
---

# PromptLayer Monitor

Automatically logs every outbound agent message to PromptLayer for observability.

## What It Does

- Listens for `message:sent` events
- Logs each turn to PromptLayer with model, session type, and content
- Tags with metadata (session key, channel, sender)

## Requirements

- `PROMPTLAYER_API_KEY` env var must be set

## Configuration

No additional configuration needed. Just enable the hook and ensure your PromptLayer API key is set.
