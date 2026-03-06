---
name: council-brief
version: 2.0.0
description: |
  Unified LLM Council skill — install, query, and manage the multi-model consensus app.
  Get synthesized answers from multiple LLMs via quick CLI or full web UI. One skill does it all.
slash_command: /council-brief
metadata: {"category":"productivity","tags":["llm","council","llm-council","consensus","multi-model","installer","query","unified"],"repo":"https://github.com/jeadland/llm-council"}
---

# Council Brief v2.0.0 (Unified)

**One skill to rule them all** — install, query, and manage LLM Council.

LLM Council is a multi-model consensus app: ask one question to many models, let them critique each other, get a synthesized chairman answer.

> **v2.0.0 Upgrade:** Now unified! Previously separate `install-llm-council` and `ask-council` skills are merged here. One command handles everything.

## Usage

| Command | Action |
|---------|--------|
| `/council-brief install` | Install deps and start backend + frontend |
| `/council-brief ask <question>` | Quick chairman's answer (headless) |
| `/council-brief <question>` | Shorthand — just ask directly |
| `/council-brief status` | Check if services are running |
| `/council-brief stop` | Stop background services |
| `/council-brief --help` | Show usage help |

## Examples

**Install and run:**
```
/council-brief install
```

**Quick question (no browser needed):**
```
/council-brief ask "Should I invest in Tesla right now?"
/council-brief "Is Python or Go better for microservices?"
/council-brief What are the tradeoffs of Rust vs Zig?
```

**Check status:**
```
/council-brief status
```

**Stop services:**
```
/council-brief stop
```

## Two Ways to Use

| Mode | Best For | Command |
|------|----------|---------|
| **Quick answer** | Fast decisions, mobile, casual questions | `/council-brief "question"` |
| **Full discussion** | Deep research, exploring disagreements, seeing all model responses | `/council-brief install` then open browser at `:5173` |

## How Ask Mode Works

1. Sends your question to the LLM Council backend
2. Waits for Stage 1 (all models respond)
3. Waits for Stage 2 (models rank each other)
4. Returns Stage 3 (Chairman's final synthesis)
5. **Takes 30-60 seconds** — models need time to deliberate

## How Install Mode Works

1. Resolves credentials (env → workspace `.env` → OpenClaw gateway)
2. Clones/updates `https://github.com/jeadland/llm-council`
3. Installs Python backend (`uv sync`)
4. Installs frontend (`npm ci`)
5. Starts backend (FastAPI on `:8001`)
6. Starts frontend (Vite dev on `:5173`)

## Prerequisites

- `git`, `uv` (Python), `npm`, `jq`
- API credentials: `OPENROUTER_API_KEY` in env/workspace `.env`, OR OpenClaw gateway configured

## Ports

| Service | Port |
|---------|------|
| Backend (FastAPI) | 8001 |
| Frontend dev | 5173 |
| Frontend preview | 4173 |

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This documentation |
| `council-brief.sh` | Main router script (install/ask/status/stop) |
| `ask-council.sh` | Query handler (chairman's answer) |
| `install.sh` | Installer/launcher |
| `stop.sh` | Service stopper |
| `status.sh` | Service status checker |
| `_meta.json` | Skill metadata |

## Agent Instructions

When user says `/council-brief <args>`:

```bash
bash ~/.openclaw/skills/council-brief/council-brief.sh "$@"
```

The `council-brief.sh` script handles argument routing:
- `install` → runs `install.sh` (setup + launch)
- `ask <question>` or any freeform text → runs `ask-council.sh` (query mode)
- `status` → runs `status.sh` (check services)
- `stop` → runs `stop.sh` (stop services)
- `--help` or `help` → shows usage

## Changelog

**v2.0.0** — Unified skill merging:
- `install-llm-council` (setup/launcher)
- `council-brief` v1.x (quick answers only)
- `ask-council` (deprecated duplicate)

Now one skill handles everything: install, query, status, stop.

**v1.0.5** — Previous version (query-only mode, required manual install)
