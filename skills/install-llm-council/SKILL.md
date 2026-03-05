---
name: install-llm-council
version: 1.1.6
description: |
  LLM Council — multi-model consensus app with one-command setup. Ask one question to many
  models, let them critique each other, get a synthesized chairman answer. OpenRouter/OpenClaw-native
  backend + React/Vite frontend. Zero config — credentials resolve automatically.
slash_command: /install-llm-council
metadata: {"category":"devtools","tags":["llm","openrouter","openclaw","install","vite","fastapi","consensus","multi-model"],"repo":"https://github.com/jeadland/llm-council"}
---

# LLM Council (with Installer)

**LLM Council** — ask one question to many models, let them critique each other, get a synthesized chairman answer.

This skill is the fastest way to run it: one command installs dependencies, configures credentials, and launches both backend and frontend. No manual setup, no API key prompts.

**OpenClaw-native:** Credentials resolve automatically from OpenClaw config or workspace `.env`. Falls back to the local OpenClaw gateway (port 18789) if no OpenRouter key is found.

## Two Ways to Use LLM Council

| Mode | Best For | Command |
|------|----------|---------|
| **Quick answer** | Fast decisions, mobile, casual questions | `/council "Your question"` (requires [ask-council](https://clawhub.com/skills/ask-council) skill) |
| **Full discussion** | Deep research, exploring disagreements, seeing all model responses | `/install-llm-council` then open browser at `:5173` |

## Slash Command

```
/install-llm-council [--mode auto|dev|preview] [--dir PATH]
```

When the user says `/install-llm-council`, run:

```bash
bash ~/.openclaw/skills/install-llm-council/install.sh
```

The script will:
1. **Resolve credentials** — env var → workspace `.env` → OpenClaw local gateway (no prompt ever)
2. **Clone or pull** `https://github.com/jeadland/llm-council` to `~/workspace/llm-council`
3. **`uv sync`** — Python backend dependencies
4. **`npm ci`** — frontend dependencies
5. **Write `.env`** — API key/URL for OpenRouter direct or OpenClaw gateway mode
6. **Start app** — uses hardened `start.sh` with mode-aware startup and health checks
7. **Auto-handle port conflicts** — selects safe fallback ports when defaults are busy
8. **Print practical access URLs** — Caddy route and common direct fallbacks

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--mode auto` | `auto` | Detect Caddy on :5173 and prefer preview mode; otherwise dev mode |
| `--mode dev` | — | Run Vite dev server (hot reload, port 5173 default) |
| `--mode preview` | — | Build + run Vite preview (port 4173 default) |
| `--dir PATH` | `~/workspace/llm-council` | Override clone directory |

## Credential Resolution (OpenClaw-native)

The installer **never prompts** for API keys. It resolves credentials in this order:

1. **Environment** — `OPENROUTER_API_KEY` already exported
2. **Workspace `.env`** — `~/.openclaw/workspace/.env` contains `OPENROUTER_API_KEY=...`
3. **OpenClaw gateway** — reads `~/.openclaw/openclaw.json` → `gateway.auth.token` + `gateway.port`
   - Sets `OPENROUTER_API_URL=http://127.0.0.1:<port>/v1/chat/completions` in `.env`
   - Uses the gateway token as the bearer key (OpenAI-compatible endpoint)

## Ports

| Service | Port | Notes |
|---------|------|-------|
| Backend (FastAPI) | 8001 | Always |
| Frontend dev | 5173 | `--mode dev` (default) |
| Frontend preview | 4173 | `--mode preview` |

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — skill documentation |
| `install.sh` | Main one-shot installer/launcher |
| `stop.sh` | Stop background services |
| `status.sh` | Check if services are running |
| `pids` | Saved PIDs for background processes |

## Agent Instructions

When user says `/install-llm-council` or "install llm-council" or "start llm council":

```bash
bash ~/.openclaw/skills/install-llm-council/install.sh
```

Report back the access URL from the script output (e.g. `http://10.0.1.X:5173`).

To stop:
```bash
bash ~/.openclaw/skills/install-llm-council/stop.sh
```

To check status:
```bash
bash ~/.openclaw/skills/install-llm-council/status.sh
```

## Example Output

```
✅ LLM Council installed and running!

  Mode:     dev
  API:      openrouter
  Backend:  http://127.0.0.1:8001
  Frontend: http://10.0.1.42:5173

  Stop:     bash ~/.openclaw/skills/install-llm-council/stop.sh
  Status:   bash ~/.openclaw/skills/install-llm-council/status.sh
```
