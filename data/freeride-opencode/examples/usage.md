# Usage Examples

## Example 1: Initial Setup

**User Request:**
> "I want to configure my OpenClaw to use free models from OpenCode Zen"

**Response:**
I'll configure optimal free model fallbacks for you:

```bash
# Apply the configuration
openclaw config.patch --raw '{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "opencode/kimi-k2.5-free",
          "opencode/glm-4.7-free",
          "opencode/gpt-5-nano"
        ]
      },
      "models": {
        "opencode/minimax-m2.1-free": { "alias": "MiniMax M2.1" },
        "opencode/kimi-k2.5-free": { "alias": "Kimi K2.5" },
        "opencode/glm-4.7-free": {},
        "opencode/gpt-5-nano": {}
      }
    }
  }
}'
```

## Example 2: Optimizing for Subtasks

**User Request:**
> "My subtasks are slow and expensive. How can I use a cheaper model?"

**Response:**
Let's switch subtasks to GPT 5 Nano for faster, cheaper processing:

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "model": "opencode/gpt-5-nano"
      }
    }
  }
}
```

**Apply:**
```bash
openclaw config.patch --raw '{"agents":{"defaults":{"subagents":{"model":"opencode/gpt-5-nano"}}}}'
```

## Example 3: Reducing Heartbeat Costs

**User Request:**
> "I have heartbeat running every 5 minutes and it's costing too much"

**Response:**
Let's use GPT 5 Nano for heartbeat and increase interval to 30 minutes:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "model": "opencode/gpt-5-nano"
      }
    }
  }
}
```

## Example 4: Custom Fallback Chain

**User Request:**
> "I want to prioritize Kimi over MiniMax as my primary"

**Response:**
Here's the configuration with Kimi as primary:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/kimi-k2.5-free",
        "fallbacks": [
          "opencode/minimax-m2.1-free",
          "opencode/glm-4.7-free"
        ]
      }
    }
  }
}
```

## Example 5: Adding a New Fallback

**User Request:**
> "How do I add another model to my fallback chain?"

**Response:**
Just add it to the fallbacks array:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "opencode/kimi-k2.5-free",
          "opencode/glm-4.7-free",
          "opencode/gpt-5-nano",
          "opencode/new-model-free"  // New fallback
        ]
      }
    }
  }
}
```

## Example 6: Checking Current Configuration

**User Request:**
> "What models am I currently using?"

**Response:**
Let me check your configuration:

```bash
openclaw config.get | jq '.agents.defaults.model'
```

**Output:**
```json
{
  "primary": "opencode/minimax-m2.1-free",
  "fallbacks": [
    "opencode/kimi-k2.5-free",
    "opencode/glm-4.7-free",
    "opencode/gpt-5-nano"
  ]
}
```

## Example 7: Switching from OpenRouter FreeRide

**User Request:**
> "I'm coming from the OpenRouter FreeRide skill. How do I switch?"

**Response:**
Your OpenRouter config:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallbacks": ["openrouter/free:free"]
      }
    }
  }
}
```

Switch to OpenCode Zen:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "opencode/kimi-k2.5-free",
          "opencode/glm-4.7-free",
          "opencode/gpt-5-nano"
        ]
      }
    }
  }
}
```

**Benefits:**
- No separate API key needed
- More free model options
- Direct provider access
- Better fallbacks

## Example 8: Troubleshooting Rate Limits

**User Request:**
> "I'm hitting rate limits on all my fallbacks"

**Response:**
Let's add more fallbacks and check availability:

```bash
# Check available free models
opencode models | grep -E "opencode/.*-free"
```

**Expand fallback chain:**
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "opencode/kimi-k2.5-free",
          "opencode/glm-4.7-free",
          "opencode/gpt-5-nano",
          "openrouter/free:free"  // Fallback to OpenRouter
        ]
      }
    }
  }
}
```

## Example 9: Performance Testing

**User Request:**
> "I want to test which free model is fastest for simple tasks"

**Response:**
Let's benchmark the models:

```bash
# Test each model
echo "Testing MiniMax M2.1..."
time opencode run "What is 2+2?" --model opencode/minimax-m2.1-free

echo "Testing Kimi K2.5..."
time opencode run "What is 2+2?" --model opencode/kimi-k2.5-free

echo "Testing GPT 5 Nano..."
time opencode run "What is 2+2?" --model opencode/gpt-5-nano
```

## Example 10: Complete Production Configuration

**User Request:**
> "Give me a production-ready configuration"

**Response:**
Here's a complete, optimized configuration:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "opencode/kimi-k2.5-free",
          "opencode/glm-4.7-free",
          "opencode/gpt-5-nano"
        ]
      },
      "models": {
        "opencode/minimax-m2.1-free": { "alias": "MiniMax M2.1" },
        "opencode/kimi-k2.5-free": { "alias": "Kimi K2.5" },
        "opencode/glm-4.7-free": { "alias": "GLM 4.7" },
        "opencode/gpt-5-nano": { "alias": "GPT Nano" }
      },
      "heartbeat": {
        "every": "30m",
        "model": "opencode/gpt-5-nano"
      },
      "subagents": {
        "model": "opencode/kimi-k2.5-free"
      },
      "maxConcurrent": 4,
      "compaction": {
        "mode": "safeguard"
      }
    }
  }
}
```

**Features:**
- Best free model as primary
- Three fallback options
- Cheap heartbeat (30 min interval)
- Balanced subtasks model
- Aliases for all models
- Concurrency limits
- Context compaction enabled
