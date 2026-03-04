---
name: zhipu-image
description: Generate images using Zhipu AI's CogView model
allowed-tools: Bash(curl:*) Bash(jq:*)
env:
  - ZHIPU_API_KEY
---

# Zhipu Image Generation

Generate images using Zhipu AI's CogView model.

## ⚠️ Security Requirements

**This skill requires `ZHIPU_API_KEY` environment variable to be set before use.**

### Security Best Practices:

1. **DO NOT store API keys in ~/.bashrc** - keys can be leaked
2. **DO NOT source shell configuration files** - prevents arbitrary code execution
3. **Set environment variable directly** when running the script

## Setup

```bash
export ZHIPU_API_KEY="your_api_key"
```

**Get your API key from:** https://www.bigmodel.cn/usercenter/proj-mgmt/apikeys

## Usage

### Quick Example

```bash
export ZHIPU_API_KEY="your_key"

curl -s -X POST "https://open.bigmodel.cn/api/paas/v4/images/generations" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "cogview-4", "prompt": "your description"}'
```

### Using the Script

```bash
export ZHIPU_API_KEY="your_key"
./generate.sh "A beautiful Chinese girl in white dress"
```

## Security Analysis

### ✅ What's Safe:
- No sourcing of ~/.bashrc or shell config files
- Uses jq for JSON escaping (prevents injection)
- Uses HTTPS with TLS 1.2+
- API key via environment variable (not hardcoded)
- Input validation (prompt length limit)
- Generic error messages

### ⚠️ Considerations:
- **Process list visibility**: API key visible in `ps aux`
- Use in trusted environments only

## Safety Features

| Feature | Implementation |
|---------|----------------|
| JSON escaping | jq prevents injection |
| Input validation | Prompt length ≤1000 chars |
| TLS | Force TLS 1.2+ |
| Timeout | 60 second curl timeout |
| Error handling | Generic messages only |

## Model

Uses **CogView-4** model from Zhipu AI.

## API Endpoint

**Official:** `https://open.bigmodel.cn/api/paas/v4/images/generations`
