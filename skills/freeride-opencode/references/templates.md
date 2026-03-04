# Configuration Templates

## Minimal Template (Just Fallbacks)

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "openrouter/arcee-ai/trinity-large-preview:free",
          "opencode/kimi-k2.5-free"
        ]
      }
    }
  }
}
```

## Complete Template (All Optimizations)

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "openrouter/arcee-ai/trinity-large-preview:free",
          "opencode/kimi-k2.5-free"
        ]
      },
      "models": {
        "opencode/minimax-m2.1-free": { "alias": "MiniMax M2.1" },
        "openrouter/arcee-ai/trinity-large-preview:free": { "alias": "Trinity Large" },
        "opencode/kimi-k2.5-free": { "alias": "Kimi K2.5" },
        "opencode/glm-4.7-free": { "alias": "GLM 4.7" }
      },
      "heartbeat": {
        "every": "30m",
        "model": "opencode/glm-4.7-free"
      },
      "subagents": {
        "model": "opencode/kimi-k2.5-free"
      }
    }
  }
}
```

## Cost-Optimized Template (Cheapest First)

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/glm-4.7-free",
        "fallbacks": [
          "openrouter/arcee-ai/trinity-large-preview:free",
          "opencode/kimi-k2.5-free"
        ]
      },
      "heartbeat": {
        "model": "opencode/glm-4.7-free"
      },
      "subagents": {
        "model": "opencode/kimi-k2.5-free"
      }
    }
  }
}
```

## Performance-Optimized Template (Best First)

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "openrouter/arcee-ai/trinity-large-preview:free"
        ]
      },
      "heartbeat": {
        "model": "opencode/glm-4.7-free"
      },
      "subagents": {
        "model": "opencode/kimi-k2.5-free"
      }
    }
  }
}
```

## Subagent-Only Template

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "model": "opencode/kimi-k2.5-free"
      }
    }
  }
}
```

## Cron-Specific Template

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/glm-4.7-free",
        "fallbacks": [
          "opencode/kimi-k2.5-free"
        ]
      }
    }
  }
}
```

## Applying Templates

> **⚠️ Prerequisites:** Ensure you have both API keys configured before applying templates:
> - OpenCode Zen API key (for `opencode/*` models)
> - OpenRouter API key (for `openrouter/*` models - Trinity Large)
>
> Without both keys, fallbacks will fail when switching providers.

### Via CLI

```bash
openclaw config.patch --raw '{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": ["openrouter/arcee-ai/trinity-large-preview:free", "opencode/kimi-k2.5-free"]
      }
    }
  }
}'
```

### Via Gateway API

```bash
openclaw gateway call config.patch --params '{
  "raw": "{\"agents\":{\"defaults\":{\"model\":{\"primary\":\"opencode/minimax-m2.1-free\",\"fallbacks\":[\"openrouter/arcee-ai/trinity-large-preview:free\",\"opencode/kimi-k2.5-free\"]}}}}"
}'
```

### Manual Edit

Edit `~/.openclaw/openclaw.json` directly, then run:

```bash
openclaw gateway restart
```

## Verifying Configuration

After applying:

```bash
# Check model configuration
openclaw config.get | jq '.agents.defaults.model'

# List available models
opencode models | grep -E "opencode/.*-free"

# Test fallback
opencode run "Hello" --model opencode/minimax-m2.1-free
```

## Resetting to Defaults

To remove FreeRide configuration and return to defaults:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5"
      }
    }
  }
}
```
