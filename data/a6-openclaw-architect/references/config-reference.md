# openclaw.json Configuration Reference

The main config file at `~/.openclaw/openclaw.json`. All settings are optional — OpenClaw uses sensible defaults.

## Top-Level Structure

```json
{
  "meta": {},
  "wizard": {},
  "diagnostics": {},
  "browser": {},
  "auth": {},
  "agents": {},
  "tools": {},
  "messages": {},
  "commands": {},
  "channels": {},
  "gateway": {},
  "skills": {},
  "plugins": {}
}
```

## agents.defaults — Model & Session Config

### Model Routing
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": [
          "openrouter/moonshotai/kimi-k2-thinking",
          "openrouter/deepseek/deepseek-v3.2"
        ]
      },
      "imageModel": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": ["openrouter/moonshotai/kimi-k2-thinking"]
      }
    }
  }
}
```

**Model ID format:**
- `anthropic/claude-*` — Direct Anthropic API (needs auth profile)
- `openrouter/*` — Via OpenRouter (needs OpenRouter API key)
- Provider prefix determines routing

### Per-Model Settings
```json
{
  "models": {
    "anthropic/claude-opus-4-6": {
      "alias": "opus",
      "params": {
        "cacheRetention": "long"
      }
    },
    "openrouter/anthropic/claude-sonnet-4": {}
  }
}
```

### Memory Search
```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "remote": {
      "baseUrl": "https://openrouter.ai/api/v1",
      "apiKey": "sk-or-v1-..."
    }
  }
}
```
Uses embeddings to search memory files. Provider "openai" works with OpenRouter's OpenAI-compatible API.

### Context Pruning
```json
{
  "contextPruning": {
    "mode": "cache-ttl",
    "ttl": "5m"
  }
}
```
Modes: `cache-ttl` (prune old cached content), `none`.

### Compaction
```json
{
  "compaction": {
    "mode": "safeguard",
    "memoryFlush": {
      "enabled": true,
      "softThresholdTokens": 4000,
      "prompt": "Scan conversation for unstored important info...",
      "systemPrompt": "Session nearing compaction..."
    }
  }
}
```
When context gets too large, compaction summarizes and continues. `memoryFlush` saves important info before compaction.

### Heartbeat
```json
{
  "heartbeat": {
    "every": "55m"
  }
}
```
Periodic agent wake-up for background tasks.

### Concurrency
```json
{
  "maxConcurrent": 4,
  "subagents": {
    "maxConcurrent": 8
  }
}
```

## channels — Chat Platform Config

### Telegram
```json
{
  "channels": {
    "telegram": {
      "botToken": "1234:ABCD...",
      "dmPolicy": "allowlist",
      "allowFrom": [5162552495],
      "groupPolicy": "allowlist",
      "streamMode": "partial"
    }
  }
}
```

- `dmPolicy` — `allowlist` (only listed users) or `open`
- `allowFrom` — Array of Telegram user IDs
- `groupPolicy` — `allowlist` or `open`
- `streamMode` — `partial` (edit messages as they stream) or `none`

## gateway — Server Config

```json
{
  "gateway": {
    "mode": "local",
    "controlUi": {
      "allowInsecureAuth": false
    },
    "auth": {
      "mode": "token",
      "token": "your-secret-token",
      "allowTailscale": true
    },
    "trustedProxies": ["172.18.0.0/16"]
  }
}
```

- `mode` — `local` (standard) or `hosted`
- `auth.allowTailscale` — Accept connections from Tailscale network without token
- `trustedProxies` — CIDR ranges for proxy headers (Docker network)

## tools — Tool Configuration

### Web Search
```json
{
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "perplexity",
        "perplexity": {
          "apiKey": "pplx-...",
          "baseUrl": "https://api.perplexity.ai",
          "model": "sonar"
        }
      }
    }
  }
}
```

### Media (Audio Transcription)
```json
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "maxChars": 10000,
        "models": [{
          "capabilities": ["audio"],
          "type": "cli",
          "command": "/path/to/transcribe.sh",
          "args": ["{{MediaPath}}"],
          "maxBytes": 26214400,
          "timeoutSeconds": 120
        }]
      }
    }
  }
}
```

## browser — Browser Automation

```json
{
  "browser": {
    "enabled": true,
    "executablePath": "/path/to/chrome",
    "headless": true,
    "noSandbox": true
  }
}
```

## skills — Skill-Specific Config

```json
{
  "skills": {
    "entries": {
      "agentmail": {
        "enabled": true,
        "env": {
          "AGENTMAIL_API_KEY": "am_..."
        }
      }
    }
  }
}
```

Per-skill environment variables and enable/disable flags.

## diagnostics — Observability

```json
{
  "diagnostics": {
    "enabled": true,
    "otel": {
      "enabled": true,
      "endpoint": "http://signoz-otel-collector:4318",
      "protocol": "http/protobuf",
      "serviceName": "openclaw-gateway",
      "traces": true,
      "metrics": true,
      "logs": true,
      "sampleRate": 1,
      "flushIntervalMs": 5000
    }
  }
}
```

## auth — API Credentials

```json
{
  "auth": {
    "profiles": {
      "anthropic:claude-code-feb-2-2026": {
        "provider": "anthropic",
        "mode": "token"
      }
    }
  }
}
```

## messages — Message Behavior

```json
{
  "messages": {
    "ackReactionScope": "group-mentions"
  }
}
```

## commands — Command System

```json
{
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true
  }
}
```

## CLI Config Commands

```bash
openclaw config get agents.defaults.model.primary
openclaw config set agents.defaults.model.primary "anthropic/claude-opus-4-6"
openclaw config unset diagnostics.otel.enabled
openclaw configure   # Interactive wizard
```
