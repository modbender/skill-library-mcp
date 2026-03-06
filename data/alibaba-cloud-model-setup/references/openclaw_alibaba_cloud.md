# OpenClaw Alibaba Cloud Bailian Configuration

## Provider Name

**`bailian`** (not "balian" - typo fixed in v0.1.4)

## Base URLs

### Pay-As-You-Go (按量付费)

| Site | Region | Base URL |
|------|--------|----------|
| `cn` | China (Beijing) | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `intl` | International (Singapore) | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| `us` | US (Virginia) | `https://dashscope-us.aliyuncs.com/compatible-mode/v1` |

### Coding Plan (订阅制)

| Site | Region | Base URL |
|------|--------|----------|
| `cn` | China | `https://coding.dashscope.aliyuncs.com/v1` |
| `intl` | International | `https://coding-intl.dashscope.aliyuncs.com/v1` |

## Model Series

### Flagship 4 Series (Pay-As-You-Go & Coding Plan)

#### Qwen-Max (Best Performance)
| Model ID | Context Window | Max Tokens | Description |
|----------|---------------|------------|-------------|
| `qwen-max` | 262,144 | 65,536 | Latest best-performing model |
| `qwen-max-2025-01-25` | 262,144 | 65,536 | Previous generation Max |

#### Qwen-Plus (Balanced)
| Model ID | Context Window | Max Tokens | Description |
|----------|---------------|------------|-------------|
| `qwen-plus` | 1,000,000 | 65,536 | Latest balanced model |
| `qwen-plus-2025-01-15` | 1,000,000 | 65,536 | Previous generation Plus |

#### Qwen-Flash (Fast & Cost-Effective)
| Model ID | Context Window | Max Tokens | Description |
|----------|---------------|------------|-------------|
| `qwen-flash` | 1,000,000 | 65,536 | Latest fast model |
| `qwen-flash-2025-01-15` | 1,000,000 | 65,536 | Previous generation Flash |

#### Qwen-Coder (Code Specialist)
| Model ID | Context Window | Max Tokens | Description |
|----------|---------------|------------|-------------|
| `qwen3-coder-plus` | 1,000,000 | 65,536 | Best coding model |
| `qwen3-coder-next` | 262,144 | 65,536 | Next-gen coding model |
| `qwen2.5-coder-32b-instruct` | 256,000 | 65,536 | 32B code specialist |

### Latest Qwen Models (Available for All Users)

| Model ID | Context Window | Max Tokens | Description |
|----------|---------------|------------|-------------|
| `qwen3.5-plus` | 1,000,000 | 65,536 | Qwen3.5 Plus (latest flagship) |
| `qwen3-max-2026-01-23` | 262,144 | 65,536 | Qwen3 Max latest |

### Coding Plan Exclusive Models (Third-Party)

| Model ID | Context Window | Max Tokens | Provider |
|----------|---------------|------------|----------|
| `MiniMax-M2.5` | 204,800 | 131,072 | MiniMax |
| `glm-5` | 202,752 | 16,384 | 智谱 AI |
| `glm-4.7` | 202,752 | 16,384 | 智谱 AI |
| `kimi-k2.5` | 262,144 | 32,768 | 月之暗面 |

## Model Count Summary

| Plan Type | Total Models | Includes |
|-----------|-------------|----------|
| **Pay-As-You-Go** | 11 | Flagship 4 series (9) + Latest Qwen (2) |
| **Coding Plan** | 15 | Pay-As-You-Go (11) + Third-party exclusive (4) |

## Configuration Example

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "YOUR_API_KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "Qwen3.5 Plus",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
          // ... more models
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      },
      "models": {
        "bailian/qwen3.5-plus": {}
      }
    }
  }
}
```

## API Key Storage

### Environment Variable (Recommended)

```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

### Inline (Not Recommended)

Store directly in `openclaw.json`:

```json
{
  "models": {
    "providers": {
      "bailian": {
        "apiKey": "your-api-key-here"
      }
    }
  }
}
```

## Testing

After configuration, test with:

```bash
# Validate JSON
python3 -m json.tool ~/.openclaw/openclaw.json

# Restart Gateway
openclaw gateway restart

# Test in TUI
openclaw tui
/model qwen3.5-plus

# Test model call
Ask a simple question to verify the model works.
```

## Troubleshooting

### HTTP 401: Incorrect API key

- Verify API key is for the correct plan type (Pay-As-You-Go vs Coding Plan)
- Check API key matches the site (CN vs INTL vs US)
- Ensure no extra spaces in API key
- Verify subscription status in Bailian console

### Model not found

- Check `models.providers.bailian.models` array contains the model ID
- Verify model ID spelling (case-sensitive)
- For Coding Plan models, ensure you're using Coding Plan endpoint

### Gateway fails to start

- Check JSON syntax: `python3 -m json.tool ~/.openclaw/openclaw.json`
- Verify `models.mode` is set to `"merge"`
- Check backup file exists if config was overwritten

---

*Last updated: 2026-03-02*  
*Version: 0.1.4*  
*Models: Pay-As-You-Go 11, Coding Plan 15*
