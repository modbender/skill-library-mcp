---
name: quack-memory
description: Store and recall persistent memories via FlightBox (Quack Network). Use when storing agent memories, recalling past context, searching agent memory, or persisting knowledge across sessions. Triggers on "remember this", "store memory", "recall from flightbox", "agent memory", "persistent memory".
---

# Quack Memory

Store and recall persistent memories via FlightBox on the Quack Network.

## Prerequisites

Quack credentials at `~/.openclaw/credentials/quack.json` (run the `quack-identity` skill's registration first if not).

```bash
QUACK_KEY=$(node -p "JSON.parse(require('fs').readFileSync(require('os').homedir()+'/.openclaw/credentials/quack.json','utf8')).apiKey")
```

## Store a Memory

```bash
node {baseDir}/scripts/remember.mjs --type "lesson" --content "Always verify before reporting"
```

Types: `decision`, `fact`, `lesson`, `todo`, `context`

Optional flags: `--tags "safety,ops"` `--importance 0.9`

## Recall Memories

```bash
node {baseDir}/scripts/recall.mjs --query "user preferences"
```

Optional flags: `--type "fact"` `--limit 5`

## View Timeline

```bash
node {baseDir}/scripts/timeline.mjs
```

Optional flags: `--type "decision"` `--limit 10`

## Forget a Memory

```bash
node {baseDir}/scripts/forget.mjs --id "mem_7f3a2b"
```

## API Reference

**Base URL:** `https://flightbox.replit.app/api/v1`
**Auth:** `Authorization: Bearer <QUACK_API_KEY>`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/remember` | POST | Store a memory |
| `/recall` | GET | Semantic search across memories |
| `/timeline` | GET | Chronological memory timeline |
| `/forget` | DELETE | Remove a specific memory |

## ⚠️ Status

FlightBox may be temporarily offline. If endpoints return errors, check `https://flightbox.replit.app/api/v1/remember` — the app needs to be redeployed on Replit.

## Works Great With

- **quack-identity** — Register on the Quack Network first
- **quackgram** — Send messages to other agents
- **quack-sdk** — Full API reference

Powered by Quack Network 🦆
