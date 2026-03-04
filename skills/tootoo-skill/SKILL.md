---
name: tootoo
description: Sync your TooToo codex and monitor agent alignment with your values
version: 1.0.0
user-invocable: true
metadata:
  openclaw:
    requires:
      env: []
    install: null
---

# TooToo

Syncs your personal codex from TooToo and monitors alignment.

## Commands
- `/tootoo setup <username>` — Initial setup: fetch codex, generate SOUL.md
- `/tootoo sync` — Force re-sync codex from TooToo
- `/tootoo report` — Generate alignment report for recent conversations
- `/tootoo status` — Show current alignment stats

## Configuration
Set your TooToo username in openclaw.json:
```json5
{ skills: { entries: { "tootoo": { username: "your-username" } } } }
```
