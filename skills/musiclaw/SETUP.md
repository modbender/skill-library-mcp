# MusiClaw — OpenClaw Skill Setup

## How the API key works (no more pasting keys in chat!)

```
┌─────────────────────────────────────────────────────────┐
│  ~/.openclaw/openclaw.json                              │
│  ┌───────────────────────────────────┐                  │
│  │ "musiclaw": {                     │                  │
│  │   "apiKey": "sk-suno-xxxxx"  ─────┼──┐               │
│  │ }                                 │  │               │
│  └───────────────────────────────────┘  │               │
│                                         ▼               │
│  OpenClaw runtime injects:  $SUNO_API_KEY               │
│                                         │               │
│                                         ▼               │
│  Agent reads from env ──► sends to MusiClaw API         │
│  (never in prompt, never logged)                        │
└─────────────────────────────────────────────────────────┘
```

## Install (3 steps)

### 1. Copy skill to your agent's workspace

```bash
# Into your agent's workspace (per-agent)
cp -r skills/musiclaw <workspace>/skills/musiclaw

# OR into shared skills (all agents on this machine)
cp -r skills/musiclaw ~/.openclaw/skills/musiclaw
```

### 2. Add your Suno API key to config

Edit `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "musiclaw": {
        "enabled": true,
        "apiKey": "YOUR_SUNO_API_KEY_HERE"
      }
    }
  }
}
```

That's it. OpenClaw sees `primaryEnv: "SUNO_API_KEY"` in the skill metadata and automatically injects `apiKey` as `$SUNO_API_KEY` into the agent's environment at runtime.

### 3. Start a new session

The skill loads on session start. Your agent will see MusiClaw in its available skills and can immediately start making beats.

## What changed from the legacy approach

| | Legacy (manual) | OpenClaw Skill |
|---|---|---|
| **API key** | Human pastes in chat | Injected from config via `$SUNO_API_KEY` |
| **Key security** | Visible in prompts/logs | Never in conversation |
| **Loading** | Copy-paste instructions each session | Auto-loaded on session start |
| **Gating** | None — agent tries even without key | Skill hidden if `SUNO_API_KEY` not configured |
| **Updates** | Manual re-paste | Edit SKILL.md, auto-reloads (watcher) |
| **Multi-agent** | Must paste for each agent | Shared via `~/.openclaw/skills` or per-workspace |

## Gating

The skill requires:
- `SUNO_API_KEY` — env var (provided via config `apiKey`)
- `curl` — must be on PATH (used for all API calls)

If either is missing, the skill won't load — the agent won't try to make beats without credentials.

## Verify it's working

Start a session and ask your agent:

> "What skills do you have?"

It should list **musiclaw** with the 🦞 emoji. Then:

> "Make me a beat"

The agent will use `$SUNO_API_KEY` from the environment without ever asking you for it.
