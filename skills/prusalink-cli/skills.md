---
name: prusalink-cli
description: "OpenClaw skill: local PrusaLink CLI (curl wrapper) for status/upload/print using Digest auth (user/password) or optional X-Api-Key."
user-invocable: true
metadata: {
  "author": "DonSqualo",
  "env": {
    "PRUSALINK_HOST": { "description": "Printer host/IP (default: printer.local).", "default": "printer.local" },
    "PRUSALINK_SCHEME": { "description": "http or https (default: http).", "default": "http" },
    "PRUSALINK_USER": { "description": "PrusaLink Digest username." },
    "PRUSALINK_PASSWORD": { "description": "PrusaLink Digest password." },
    "PRUSALINK_API_KEY": { "description": "Optional: send as X-Api-Key if your PrusaLink supports it." },
    "PRUSALINK_TIMEOUT": { "description": "curl max-time seconds (default: 10).", "default": "10" }
  },
  "openclaw": { "requires": { "bins": ["curl"] } }
}
---

# PrusaLink CLI

This is an alias of `SKILL.md` for registries/uploader flows that expect `skills.md`.

If you're reading this locally, prefer `SKILL.md`.

For safety, this published skill intentionally **does not** include an "arbitrary API request" command. It exposes only the fixed, common endpoints (status/job/upload/start/cancel).
