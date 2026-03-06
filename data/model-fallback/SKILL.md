---
name: model-fallback
description: >-
  Multi-model automatic fallback system. Monitors model availability and automatically
  falls back to backup models when the primary model fails. Supports MiniMax, Kimi,
  Zhipu and other OpenAI-compatible APIs. Use when: (1) Primary model API is unavailable,
  (2) Model response time is too slow, (3) Rate limit exceeded, (4) Need to optimize
  costs by using cheaper models for simple tasks.
tags: [model, fallback, multi-model, cost-optimization, reliability]
---

# Model Fallback Skill

> Multi-model automatic fallback system for AI agents

## Overview

This skill provides automatic model fallback functionality for OpenClaw agents. When the primary model fails (unavailable, slow, or rate-limited), it automatically switches to backup models in a predefined priority order.

## Features

- **Automatic Fallback**: Seamlessly switch to backup models on failure
- **Configurable Priority**: Define your own model fallback order
- **Health Monitoring**: Track model availability and response times
- **Cost Optimization**: Use cheaper models for simple tasks
- **Logging**: Full audit trail of fallback events

## Supported Models

| Provider | Model | Context | Use Case |
|----------|-------|---------|----------|
| MiniMax | M2.5 | 200K | Primary (reasoning) |
| MiniMax | M2.1 | 200K | Backup |
| Kimi | K2.5 | 256K | Long documents |
| Kimi | K2 | 128K | Standard |
| Zhipu | GLM-4-Air | 128K | Low cost |
| Zhipu | GLM-4-Flash | 1M | High volume |

## Configuration

### Default Fallback Chain

```json
{
  "fallback_chain": [
    {
      "provider": "minimax-portal",
      "model": "MiniMax-M2.5",
      "priority": 1,
      "timeout": 30,
      "max_retries": 3
    },
    {
      "provider": "moonshot",
      "model": "kimi-k2.5",
      "priority": 2,
      "timeout": 30,
      "max_retries": 2
    },
    {
      "provider": "zhipu",
      "model": "glm-4-air",
      "priority": 3,
      "timeout": 20,
      "max_retries": 2
    }
  ]
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MODEL_FALLBACK_ENABLED` | No | Enable/disable fallback (default: true) |
| `MODEL_FALLBACK_LOG_LEVEL` | No | Log level: debug, info, warn, error |

## Usage

### Basic Usage

The skill automatically handles model failures. No explicit calls needed.

```bash
# Trigger a model call (fallback happens automatically on failure)
```

### Manual Fallback

```bash
# Force fallback to next model
/scripts/model-fallback.sh --force-next

# Check current model status
/scripts/model-fallback.sh --status

# Reset to primary model
/scripts/model-fallback.sh --reset
```

### Configuration

Edit `config.json` to customize the fallback chain:

```json
{
  "fallback_chain": [
    {"provider": "...", "model": "...", "priority": 1}
  ],
  "health_check": {
    "enabled": true,
    "interval_seconds": 300
  }
}
```

## How It Works

```
1. User makes request with primary model
2. Model call fails (error, timeout, rate limit)
3. Skill detects failure
4. Wait 3 seconds (debounce)
5. Switch to next model in chain
6. Retry request with new model
7. If successful, return result
8. If failed, repeat steps 4-7
9. If all models fail, return error with details
```

## Fallback Triggers

| Trigger | Condition | Action |
|----------|-----------|--------|
| API Unavailable | Connection timeout | Fallback |
| Rate Limit | 429 response | Fallback + wait |
| Slow Response | > timeout seconds | Fallback |
| Invalid Response | Parse error | Fallback |
| Auth Error | 401/403 response | Log + stop |

## Logging

Logs are written to:
- `~/.openclaw/logs/model-fallback.log`

### Log Format

```
[2026-02-27 14:00:00] [INFO] Primary model MiniMax-M2.5 called
[2026-02-27 14:00:05] [WARN] Model failed: rate limit exceeded
[2026-02-27 14:00:05] [INFO] Falling back to Kimi K2.5
[2026-02-27 14:00:10] [INFO] Fallback successful
```

## Cost Optimization

Use cheaper models for simple tasks:

```json
{
  "task_routing": {
    "simple_query": ["glm-4-air", "glm-4-flash"],
    "complex_reasoning": ["MiniMax-M2.5", "kimi-k2.5"],
    "long_context": ["kimi-k2.5", "MiniMax-M2.1"]
  }
}
```

## Integration

### OpenClaw Configuration

Add to `openclaw.json`:

```json
{
  "models": {
    "mode": "merge",
    "fallback": {
      "enabled": true,
      "config": "~/.openclaw/skills/model-fallback/config.json"
    }
  }
}
```

### Health Check

Integrate with system health monitoring:

```bash
# Check model health
curl http://localhost:18789/api/models/health
```

## Troubleshooting

### Fallback Not Working

1. Check if fallback is enabled: `echo $MODEL_FALLBACK_ENABLED`
2. Verify config exists: `ls ~/.openclaw/skills/model-fallback/config.json`
3. Check logs: `tail -f ~/.openclaw/logs/model-fallback.log`

### Models Always Failing

1. Check API keys are valid
2. Verify network connectivity
3. Check rate limits on provider dashboard

## Examples

### Example 1: Simple Fallback

```
User: "Hello"
System: Using MiniMax-M2.5...
System: Rate limited, switching to Kimi K2.5...
System: Response from Kimi K2.5: "Hello! How can I help?"
```

### Example 2: Cost Optimization

```
User: "What is 2+2?"
System: Routing to glm-4-air (low cost)...
System: Response: "2+2=4"
```

### Example 3: Long Document

```
User: "Summarize this 100-page PDF"
System: Detected long context requirement
System: Routing to Kimi K2.5 (256K context)...
System: Processing...
```

## License

MIT

## Author

CC (AI Assistant)

## Version

1.0.0
