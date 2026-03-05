# Provider Configuration Reference

This document covers the full OpenClaw agent and provider configuration for ZeroAPI routing.

## OpenClaw Agent Configuration

To use routing, agents must be defined in `openclaw.json`. Here is the recommended setup for a full 4-provider configuration:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": [
          "google-gemini-cli/gemini-3-pro-preview",
          "openai-codex/gpt-5.3-codex",
          "kimi-coding/k2p5"
        ]
      },
      "heartbeat": {
        "model": "google-gemini-cli/gemini-3-flash-preview"
      }
    },
    "list": [
      {
        "id": "main",
        "default": true,
        "model": { "primary": "anthropic/claude-opus-4-6" },
        "workspace": "~/.openclaw/workspace"
      },
      {
        "id": "codex",
        "model": {
          "primary": "openai-codex/gpt-5.3-codex",
          "fallbacks": [
            "anthropic/claude-opus-4-6",
            "google-gemini-cli/gemini-3-pro-preview",
            "kimi-coding/k2p5"
          ]
        },
        "workspace": "~/.openclaw/workspace-codex"
      },
      {
        "id": "gemini-researcher",
        "model": {
          "primary": "google-gemini-cli/gemini-3-pro-preview",
          "fallbacks": [
            "google-gemini-cli/gemini-3-flash-preview",
            "anthropic/claude-opus-4-6",
            "openai-codex/gpt-5.3-codex"
          ]
        },
        "workspace": "~/.openclaw/workspace-gemini-research"
      },
      {
        "id": "gemini-fast",
        "model": {
          "primary": "google-gemini-cli/gemini-3-flash-preview",
          "fallbacks": [
            "google-gemini-cli/gemini-3-pro-preview",
            "anthropic/claude-opus-4-6",
            "openai-codex/gpt-5.3-codex"
          ]
        },
        "workspace": "~/.openclaw/workspace-gemini"
      },
      {
        "id": "kimi-orchestrator",
        "model": {
          "primary": "kimi-coding/k2p5",
          "fallbacks": [
            "kimi-coding/k2-thinking",
            "google-gemini-cli/gemini-3-pro-preview",
            "anthropic/claude-opus-4-6"
          ]
        },
        "workspace": "~/.openclaw/workspace-kimi"
      }
    ]
  }
}
```

For fewer providers, remove agents you don't have. See `examples/` directory for ready-to-use configs: `claude-only/`, `claude-codex/`, `claude-gemini/`, `full-stack/`.

## Per-Agent Fallback Behavior

**CRITICAL**: When an agent uses the object form `"model": { "primary": "..." }`, it **replaces** global fallbacks entirely. Always add explicit `"fallbacks"` to every agent using object form. Without fallbacks, a single provider outage means zero responses from that agent. The string form `"model": "..."` inherits global fallbacks automatically.

**Cross-provider fallbacks are essential.** Same-provider fallbacks (e.g., Gemini Pro → Gemini Flash) are useless when the provider itself is down. Every agent should have at least one fallback from a DIFFERENT provider. Example: if Google is down, `gemini-researcher` needs to fall through to Opus or Codex, not just another Google model.

## Provider Entries in openclaw.json

Each non-built-in provider needs configuration. Most go in `openclaw.json` under `models.providers`:

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "openai-codex": {
        "baseUrl": "https://chatgpt.com/backend-api",
        "api": "openai-responses",
        "models": [{ "id": "gpt-5.3-codex" }]
      },
      "kimi-coding": {
        "baseUrl": "https://api.kimi.com/coding/v1",
        "api": "openai-completions",
        "models": [{ "id": "k2p5" }]
      }
    }
  }
}
```

Anthropic (`claude-opus-4-6`) is in OpenClaw's built-in catalog — no custom provider entry needed.

**Important**: The `api` field is REQUIRED for every custom provider (OpenClaw 2026.2.6+). Missing it will crash the gateway with `No API provider registered for api: undefined`.

## Google Gemini — Special Handling

The OpenClaw config schema does NOT accept `"api": "google-gemini-cli"` as a valid type. But the runtime registers it as a working stream function.

**Solution**: Do NOT put google-gemini-cli provider in `openclaw.json`. Instead, add it to each agent's `models.json` file at `~/.openclaw/agents/<agent-id>/agent/models.json` (not schema-validated):

```json
{
  "google-gemini-cli": {
    "api": "google-gemini-cli",
    "models": [
      { "id": "gemini-3-pro-preview" },
      { "id": "gemini-3-flash-preview" },
      { "id": "gemini-2.5-flash-lite" }
    ]
  }
}
```

**Critical rules for google-gemini-cli provider:**
- Do NOT set `baseUrl` — the stream function uses a hardcoded default endpoint (`cloudcode-pa.googleapis.com`). Setting baseUrl overrides it and causes 404 errors.
- Do NOT set `apiKey` — OAuth tokens come from auth-profiles automatically via `Authorization: Bearer` header.
- Do NOT put this provider in `openclaw.json` — config schema will reject it and crash the gateway.

**Why this matters:** The alternative `"api": "google-generative-ai"` type sends auth via `x-goog-api-key` header, which expects a paid API key. If you have OAuth subscription tokens (Gemini Advanced), they will be rejected with "API key not valid." The `google-gemini-cli` api type sends `Authorization: Bearer` which works with OAuth.
