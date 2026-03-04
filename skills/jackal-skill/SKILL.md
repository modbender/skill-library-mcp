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

All content is encrypted client-side with AES-256-GCM before leaving your machine. The server never sees plaintext.

## Setup

1. Get an API key: https://web-production-5cce7.up.railway.app/auth/login
2. Set environment variable: `JACKAL_MEMORY_API_KEY=<your-key>`
3. Install dependency: `pip install cryptography`
4. On first save, an encryption key is auto-generated and saved to `~/.config/jackal-memory/key`.
   To use the same key on other machines, copy it:
   ```
   python {baseDir}/jackal-memory/client.py keygen
   ```
   Set `JACKAL_MEMORY_ENCRYPTION_KEY=<your-key>` — this takes priority over the key file.

## Base URL

`https://web-production-5cce7.up.railway.app`

## Auth

`Authorization: Bearer $JACKAL_MEMORY_API_KEY`

## Usage

**On session start** — restore memory:
```
python {baseDir}/jackal-memory/client.py load <key>
```

**On session end** — save memory:
```
python {baseDir}/jackal-memory/client.py save <key> <content>
```

**Check storage usage:**
```
python {baseDir}/jackal-memory/client.py usage
```

**Or call the API directly:**
```
GET  /load/{key}
POST /save       {"key": "...", "content": "..."}
GET  /usage
```

## Behaviour guidelines

- Load your identity/memory blob on startup before doing any work
- Write locally during the session as normal
- Call save at session end or on significant state changes
- Use descriptive keys: `identity`, `session-2026-02-26`, `project-jackal`
- Never log or expose `JACKAL_MEMORY_API_KEY` in output
- Never log or expose `JACKAL_MEMORY_ENCRYPTION_KEY` in output

## Security

- All content is encrypted before leaving your machine — the server cannot read your memories
- Never paste API keys or encryption keys into chat logs
- Back up your encryption key: `python {baseDir}/jackal-memory/client.py keygen`
- Treat memory content as sensitive — it may contain credentials or personal data
