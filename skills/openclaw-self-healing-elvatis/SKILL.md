---
name: openclaw-self-healing-elvatis
description: OpenClaw plugin that applies guardrails and auto-fixes reversible failures (rate limits, disconnects, stuck session pins).
---

# openclaw-self-healing-elvatis

Self-healing extension for OpenClaw.

## What it does

- Detects common reversible failures (rate limits, auth errors, stuck session model pins)
- Applies guardrails (e.g. avoid breaking config)
- Can auto-recover WhatsApp disconnects (when enabled)

## Install

```bash
clawhub install openclaw-self-healing-elvatis
```

## Notes

Keep repository content public-safe (no private identifiers).
