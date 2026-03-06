---
name: zhipu-search
description: Use Zhipu (智谱) web search API for searching the internet. Use when user asks for web search, latest news, or needs current information.
allowed-tools: Bash(curl:*) Bash(jq:*)
env:
  - ZHIPU_API_KEY
---

# Zhipu Web Search

Use Zhipu's web search API to search the internet.

## ⚠️ Security Requirements

**This skill requires `ZHIPU_API_KEY` environment variable to be set before use.**

### Security Best Practices:

1. **DO NOT store API keys in ~/.bashrc** - keys can be leaked
2. **DO NOT source shell configuration files** - prevents arbitrary code execution  
3. **Set environment variable directly** when running the script
4. **Be aware** API key will be visible in process list (ps aux)

## Setup

```bash
# Set API key as environment variable
export ZHIPU_API_KEY="your_api_key"
```

**Get your API key from:** https://www.bigmodel.cn/usercenter/proj-mgmt/apikeys

## Usage

### Quick Search

```bash
export ZHIPU_API_KEY="your_key"

curl -s -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4-flash",
    "messages": [{"role": "user", "content": "搜索: YOUR_QUERY"}],
    "tools": [{"type": "web_search", "web_search": {"search_query": "YOUR_QUERY"}}]
  }' | jq -r '.choices[0].message.content'
```

### Using the Script

```bash
export ZHIPU_API_KEY="your_key"
./search.sh "搜索内容"
```

## Security Analysis

### ✅ What's Safe:
- No sourcing of ~/.bashrc or shell config files
- Uses jq for JSON escaping (prevents injection)
- Uses HTTPS with TLS 1.2+
- API key via environment variable (not hardcoded)
- Proper error handling - sensitive info not leaked
- Input validation (query length limit)
- Generic error messages (no path/file hints)

### ⚠️ Considerations:
- **Process list visibility**: API key visible in `ps aux`
  - Use in trusted environments only
- **Endpoint**: `https://open.bigmodel.cn` (official Zhipu API)

## Safety Features

| Feature | Implementation |
|---------|----------------|
| JSON escaping | jq --arg prevents injection |
| Input validation | Query length ≤500 chars |
| TLS | Force TLS 1.2+ |
| Error handling | Generic messages, no leaks |
| Timeout | 30 second curl timeout |

## When to Use

- User says "search for", "look up", "find information about"
- User asks "what's the latest news about"
- User needs current information from the web

## API Endpoint

**Official:** `https://open.bigmodel.cn/api/paas/v4/chat/completions`
