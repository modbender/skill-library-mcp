# Overkill Memory System - Quick Start

A neuroscience-inspired 6-tier memory architecture for OpenClaw agents.

## Quick Start

### 1. Initialize

```bash
cd ~/.openclaw/workspace-cody/skills/overkill-memory-system
python3 cli.py init
```

### 2. Add Your First Memory

```bash
python3 cli.py add "Starting my memory system journey!"
```

### 3. Search Memories

```bash
python3 cli.py search "memory system"
```

## Common Commands

| Command | Description |
|---------|-------------|
| `python3 cli.py init` | Initialize memory system |
| `python3 cli.py add "text"` | Add a memory |
| `python3 cli.py search "query"` | Search memories |
| `python3 cli.py session new` | Start new session |
| `python3 cli.py session end` | End session (flush WAL) |
| `python3 cli.py brain state` | View emotional state |
| `python3 cli.py daily "note"` | Add daily note |
| `python3 cli.py diary "entry"` | Add diary entry |
| `python3 cli.py stats` | Show memory statistics |

## The 6 Tiers

1. **HOT** - Session state (current context)
2. **WARM** - Daily notes (24-48h)
3. **TEMP** - Cache (minutes-hours)
4. **COLD** - Core memory (weeks-months)
5. **ARCHIVE** - Diary (months-years)
6. **COLD-STORAGE** - Git-Notes (indefinite)

## Environment Setup

```bash
cp .env.example .env
# Edit .env with your ChromaDB/Ollama settings (optional)
```

## Need Help?

See `SKILL.md` for complete documentation.
