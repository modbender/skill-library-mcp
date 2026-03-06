# Boardroom model: OpenRouter + Claude Opus 4.6

The board of advisors (four personas) should run on a stronger model so their arguments and rebuttals are higher quality. Recommended: **Claude Opus 4.6 via OpenRouter**.

## OpenRouter model ID

- **Full ref (OpenClaw):** `openrouter/anthropic/claude-opus-4.6`
- **OpenRouter page:** https://openrouter.ai/anthropic/claude-opus-4.6

Requires `OPENROUTER_API_KEY` in the environment (get a key at https://openrouter.ai).

## Option A: Dedicated Boardroom agent

Add a second agent that uses Opus 4.6. When the user consults the board, they (or the system) use this agent so the entire deliberation runs on the better model.

```json5
{
  "env": { "OPENROUTER_API_KEY": "sk-or-..." },
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-sonnet-4" },
      "models": {
        "anthropic/claude-sonnet-4": {},
        "openrouter/anthropic/claude-opus-4.6": { "alias": "board" },
      },
    },
    "list": [
      { "id": "main", "default": true, "name": "Main" },
      {
        "id": "boardroom",
        "name": "Boardroom",
        "model": { "primary": "openrouter/anthropic/claude-opus-4.6" },
      },
    ],
  },
}
```

User selects the "Boardroom" agent when they want to consult the board, or the main agent can spawn a sub-agent with `agentId: "boardroom"` and the boardroom task.

## Option B: Subagent model override for board

If the main agent runs the boardroom skill and can spawn sub-agents, set the default subagent model to Opus 4.6 so that when the skill spawns a sub-agent to run the board, that sub-agent uses the stronger model:

```json5
{
  "env": { "OPENROUTER_API_KEY": "sk-or-..." },
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-sonnet-4" },
      "models": {
        "openrouter/anthropic/claude-opus-4.6": { "alias": "board" },
      },
      "subagents": {
        "model": "openrouter/anthropic/claude-opus-4.6",
      },
    },
  },
}
```

Then when the boardroom skill uses `sessions_spawn` to run the deliberation (e.g. one sub-agent for the full board process), that sub-agent will use Opus 4.6.

## Option C: Spawn with explicit model

When calling `sessions_spawn` for the boardroom task, pass the model explicitly:

- **model:** `openrouter/anthropic/claude-opus-4.6` (or alias `board` if configured in `agents.defaults.models`)

No need to change the default agent model; the board runs on Opus 4.6 only when the boardroom skill spawns a sub-agent with this model.

## OpenClaw Setup

Add `OPENROUTER_API_KEY` to your `.env` file, then ensure it is referenced in the OpenClaw config (or env) for the openclaw service. The config lives at `~/.openclaw/openclaw.json`. Merge the `agents` and `env` snippets above into that file (or use the OpenClaw gateway UI if available).
