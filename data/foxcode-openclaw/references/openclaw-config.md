# OpenClaw Configuration Reference

Complete configuration reference for OpenClaw with Foxcode integration.

## Configuration File Location

OpenClaw uses JSON/JSON5 configuration files. The default location is:

| Platform | Default Path |
|----------|--------------|
| macOS | `~/.openclaw/openclaw.json` |
| Linux | `~/.openclaw/openclaw.json` |
| Windows | `%APPDATA%\openclaw\openclaw.json` |

### Finding Your Config File

```bash
# macOS/Linux
ls ~/.openclaw/openclaw.json

# Or search for it
find ~ -name "openclaw.json" 2>/dev/null
```

---

## Configuration Schema

OpenClaw uses camelCase and a nested structure for model providers.

### Minimal Configuration

Add to your `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude",
        "apiKey": "sk-foxcode-your-token-here",
        "api": "anthropic-messages"
      }
    }
  }
}
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `models.providers` | object | Yes | Custom provider definitions |
| `models.providers.<id>.baseUrl` | string | Yes | Foxcode endpoint URL |
| `models.providers.<id>.apiKey` | string | Yes | Your Foxcode API token |
| `models.providers.<id>.api` | string | Yes | API adapter: `anthropic-messages` |
| `models.providers.<id>.models` | array | No | Model catalog with metadata |
| `agents.defaults.model` | string | No | Default model in format `provider/modelId` |

---

## Complete Configuration Examples

### Example 1: Basic Setup (Official Endpoint)

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude",
        "apiKey": "sk-foxcode-your-token-here",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "claude-sonnet-4-5-20251101",
            "name": "Claude Sonnet",
            "contextWindow": 200000,
            "maxTokens": 4096
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "foxcode/claude-sonnet-4-5-20251101"
    }
  }
}
```

### Example 2: With Multiple Models

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude",
        "apiKey": "sk-foxcode-your-token-here",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "claude-sonnet-4-5-20251101",
            "name": "Claude Sonnet",
            "contextWindow": 200000,
            "maxTokens": 4096
          },
          {
            "id": "claude-haiku-4-5-20251101",
            "name": "Claude Haiku",
            "contextWindow": 200000,
            "maxTokens": 4096
          },
          {
            "id": "claude-opus-4-5-20251101",
            "name": "Claude Opus",
            "contextWindow": 200000,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### Example 3: Cost-Optimized (Super Endpoint)

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude/super",
        "apiKey": "sk-foxcode-your-token-here",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "claude-sonnet-4-5-20251101",
            "name": "Claude Sonnet (Super)",
            "contextWindow": 200000,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### Example 4: Maximum Savings (Ultra Endpoint)

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude/ultra",
        "apiKey": "sk-foxcode-your-token-here",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "claude-haiku-4-5-20251101",
            "name": "Claude Haiku (Ultra)",
            "contextWindow": 200000,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### Example 5: Speed-Optimized (AWS Endpoint)

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude/aws",
        "apiKey": "sk-foxcode-your-token-here",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "claude-sonnet-4-5-20251101",
            "name": "Claude Sonnet (AWS)",
            "contextWindow": 200000,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### Example 6: Complex Tasks (AWS Thinking)

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude/droid",
        "apiKey": "sk-foxcode-your-token-here",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "claude-opus-4-5-20251101",
            "name": "Claude Opus (AWS Thinking)",
            "contextWindow": 200000,
            "maxTokens": 4096,
            "reasoning": true
          }
        ]
      }
    }
  }
}
```

---

## Model Reference

### Available Models

| Model ID | Context Window | Max Tokens | Best For |
|----------|----------------|------------|----------|
| `claude-opus-4-5-20251101` | 200,000 | 4096 | Complex reasoning, coding |
| `claude-sonnet-4-5-20251101` | 200,000 | 4096 | General tasks, daily use |
| `claude-haiku-4-5-20251101` | 200,000 | 4096 | Quick tasks, high volume |

### Model Selection Guide

| Task | Recommended Model |
|------|-------------------|
| Complex coding/debugging | claude-opus-4-5-20251101 |
| General development | claude-sonnet-4-5-20251101 |
| Quick questions | claude-haiku-4-5-20251101 |
| Documentation | claude-haiku-4-5-20251101 |
| Code review | claude-sonnet-4-5-20251101 |
| Architecture decisions | claude-opus-4-5-20251101 |

---

## Environment Variables

Use environment variables for better security:

### In Configuration

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "baseUrl": "https://code.newcli.com/claude",
        "apiKey": "${FOXCODE_API_TOKEN}",
        "api": "anthropic-messages"
      }
    }
  }
}
```

### Setting the Variable

```bash
# macOS/Linux
export FOXCODE_API_TOKEN="sk-foxcode-your-token"

# Add to ~/.zshrc or ~/.bashrc for persistence
echo 'export FOXCODE_API_TOKEN="sk-foxcode-your-token"' >> ~/.zshrc
```

---

## Per-Agent Configuration

Override provider settings per agent in `~/.openclaw/agents/<agentId>/agent/models.json`:

```json
{
  "models": {
    "providers": {
      "foxcode": {
        "apiKey": "different-token-for-this-agent"
      }
    }
  }
}
```

### Merge Behavior

- Non-empty values in agent `models.json` take precedence
- Empty or missing values fall back to main config
- Use `"mode": "replace"` to fully override instead of merge

---

## Configuration Validation

### Validate JSON Syntax

```bash
python3 -m json.tool ~/.openclaw/openclaw.json
```

### Validate with Script

```bash
python3 scripts/validate_config.py --config ~/.openclaw/openclaw.json
```

---

## Security Best Practices

### DO

- [ ] Use environment variables for API keys
- [ ] Set restrictive file permissions: `chmod 600 ~/.openclaw/openclaw.json`
- [ ] Rotate API tokens regularly
- [ ] Use separate tokens for different environments

### DON'T

- [ ] Never commit API keys to git
- [ ] Don't share configuration files containing tokens
- [ ] Avoid hardcoding tokens in scripts

### Secure Setup

```bash
# Set permissions
chmod 600 ~/.openclaw/openclaw.json

# Use env var for API key
export FOXCODE_API_TOKEN="sk-foxcode-your-token"
```

---

## Troubleshooting

### Config Not Loading

1. Verify file path: `ls -la ~/.openclaw/openclaw.json`
2. Check JSON syntax: `python3 -m json.tool ~/.openclaw/openclaw.json`
3. Check permissions: `ls -l ~/.openclaw/openclaw.json`
4. Restart OpenClaw after changes

### API Key Not Working

1. Verify token format: should start with `sk-`
2. Check token hasn't expired
3. Verify token in Foxcode dashboard: https://foxcode.rjj.cc/api-keys

### Endpoint Not Responding

1. Check status: `python3 scripts/check_status.py`
2. Verify URL spelling
3. Test connection with curl
