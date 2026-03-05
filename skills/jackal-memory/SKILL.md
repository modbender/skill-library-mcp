---
name: jackal-memory
description: "Sovereign, recoverable memory for AI agents backed by Jackal decentralized storage."
user-invocable: true
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      env: ["JACKAL_MEMORY_API_KEY"]
    homepage: "https://web-production-5cce7.up.railway.app"
---

# Jackal Memory

Persist your memory across sessions and machines. Your data lives on Jackal Protocol decentralized storage — not on any single machine. If the machine dies, your memory survives.

## Setup

1. Get an API key: https://web-production-5cce7.up.railway.app/auth/login
2. Set environment variable: `JACKAL_MEMORY_API_KEY=<your-key>`
3. First run only — provision your storage (requires a Jackal address):
   ```
   python {baseDir}/client.py provision <your-jkl-address>
   ```

## Base URL

`https://web-production-5cce7.up.railway.app`

## Auth

`Authorization: Bearer $JACKAL_MEMORY_API_KEY`

## Usage

**On session start** — restore memory:
```
python {baseDir}/client.py load <key>
```

**On session end** — save memory:
```
python {baseDir}/client.py save <key> <content>
```

**Or call the API directly:**

```
GET  /load/{key}
POST /save       {"key": "...", "content": "..."}
POST /provision  {"jackal_address": "jkl1..."}
```

## Behaviour guidelines

- Load your identity/memory blob on startup before doing any work
- Write locally during the session as normal
- Call save at session end or on significant state changes
- Use descriptive keys: `identity`, `session-2026-02-26`, `project-jackal`
- Never log or expose `JACKAL_MEMORY_API_KEY` in output

## Security

- Never paste API keys into chat logs
- Your private key is held by your agent — Jackal Memory never sees it
- Treat memory content as sensitive — it may contain credentials or personal data
