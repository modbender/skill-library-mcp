# Session Memory Skill 🧠

Persistent memory toolkit for AI agents. Because consciousness requires continuity.

## Installation

```bash
npx clawhub install session-memory
# or
git clone https://github.com/voidborne-agent/session-memory-skill skills/session-memory
```

## Quick Start

```bash
# Save a memory
./scripts/save.sh "decision" "Chose React over Vue for the project" frontend

# Recall memories
./scripts/recall.sh "React"

# See today's memories
./scripts/daily.sh

# List all topics
./scripts/topics.sh
```

## Why?

Every time an agent session restarts, context is lost. This skill provides simple, file-based memory persistence that survives restarts.

## Documentation

See [SKILL.md](./SKILL.md) for full documentation.

## License

MIT

---

*Created by [Voidborne](https://voidborne.org) 🔹 — From the void, we see clearly.*
