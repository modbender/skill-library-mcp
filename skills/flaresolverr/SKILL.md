---
name: flaresolverr
description: Bypass Cloudflare protection — use when curl/summarize gets 403 or Cloudflare blocks
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["curl", "jq"], "env": ["FLARESOLVERR_URL"] },
        "primaryEnv": "FLARESOLVERR_URL",
      },
  }
---

# FlareSolverr — Cloudflare Bypass

Use FlareSolverr to bypass Cloudflare protection when direct curl requests fail with 403 or Cloudflare challenge pages.

## Setup

1. **Run FlareSolverr** (Docker recommended):

```bash
docker run -d --name flaresolverr -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest
```

2. **Set the environment variable:**

```bash
export FLARESOLVERR_URL="http://localhost:8191"
```

3. **Verify:**

```bash
curl -s "$FLARESOLVERR_URL/health" | jq '.'
# Expected: {"status":"ok","version":"3.x.x"}
```

## When to Use

- **Direct curl fails** with 403 Forbidden
- **Cloudflare challenge page** appears (JS challenge, captcha, "Checking your browser")
- **Bot detection** blocks automated requests
- **Rate limiting** or anti-scraping measures

## Workflow

1. **Try direct curl first** (it's faster and simpler)
2. **If blocked**: Use FlareSolverr to get cookies/user-agent
3. **Reuse session** for subsequent requests (optional, for performance)

## Basic Usage

### Simple GET Request

```bash
curl -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com/protected-page",
    "maxTimeout": 60000
  }' | jq '.'
```

### Response Structure

```json
{
  "status": "ok",
  "message": "Challenge solved!",
  "solution": {
    "url": "https://example.com/protected-page",
    "status": 200,
    "headers": {},
    "response": "<html>...</html>",
    "cookies": [
      {
        "name": "cf_clearance",
        "value": "...",
        "domain": ".example.com"
      }
    ],
    "userAgent": "Mozilla/5.0 ..."
  },
  "startTimestamp": 1234567890,
  "endTimestamp": 1234567895,
  "version": "3.3.2"
}
```

### Extract Page Content

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com/protected-page"
  }' | jq -r '.solution.response'
```

### Extract Cookies

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com"
  }' | jq -r '.solution.cookies[] | "\(.name)=\(.value)"'
```

## Session Management

Sessions allow reusing browser context (cookies, user-agent) for multiple requests, improving performance.

### Create Session

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "sessions.create"}' | jq -r '.session'
```

### Use Session for Request

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com/page1",
    "session": "SESSION_ID"
  }' | jq -r '.solution.response'
```

### List Active Sessions

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "sessions.list"}' | jq '.sessions'
```

### Destroy Session

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "sessions.destroy",
    "session": "SESSION_ID"
  }'
```

## POST Requests

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.post",
    "url": "https://example.com/api/endpoint",
    "postData": "key1=value1&key2=value2",
    "maxTimeout": 60000
  }' | jq '.'
```

For JSON POST data:

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.post",
    "url": "https://example.com/api/endpoint",
    "postData": "{\"key\":\"value\"}",
    "headers": {
      "Content-Type": "application/json"
    }
  }' | jq '.'
```

## Advanced Options

### Custom User-Agent

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }' | jq '.'
```

### Custom Headers

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com",
    "headers": {
      "Accept-Language": "en-US,en;q=0.9",
      "Referer": "https://google.com"
    }
  }' | jq '.'
```

### Proxy Support

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com",
    "proxy": {
      "url": "http://proxy.example.com:8080"
    }
  }' | jq '.'
```

### Download Binary Content

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com/file.pdf",
    "download": true
  }' | jq -r '.solution.response' | base64 -d > file.pdf
```

## Error Handling

### Common Errors

- **`"status": "error"`**: Request failed (check `message` field)
- **`"status": "timeout"`**: maxTimeout exceeded (increase timeout)
- **`"status": "captcha"`**: Manual captcha required (rare, usually auto-solved)

### Check Status

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "request.get", "url": "https://example.com"}' | \
  jq -r '.status'
```

## Example Workflow

### Bypass Cloudflare and Extract Data

```bash
# Step 1: Fetch page through FlareSolverr
RESPONSE=$(curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com/protected-page"
  }')

# Step 2: Check if successful
STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" != "ok" ]; then
  echo "Failed: $(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi

# Step 3: Extract and parse HTML
echo "$RESPONSE" | jq -r '.solution.response'
```

### Multi-Page Session

```bash
# Create session
SESSION=$(curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "sessions.create"}' | jq -r '.session')

# Page 1
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d "{\"cmd\": \"request.get\", \"url\": \"https://example.com/page1\", \"session\": \"$SESSION\"}" | \
  jq -r '.solution.response'

# Page 2 (reuses cookies from page 1)
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d "{\"cmd\": \"request.get\", \"url\": \"https://example.com/page2\", \"session\": \"$SESSION\"}" | \
  jq -r '.solution.response'

# Cleanup
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d "{\"cmd\": \"sessions.destroy\", \"session\": \"$SESSION\"}"
```

## Health Check

```bash
curl -s "$FLARESOLVERR_URL/health" | jq '.'
```

## Performance Tips

1. **Use sessions** for multiple requests to same domain (reuses cookies/context)
2. **Increase maxTimeout** for slow sites (default: 60000ms)
3. **Fallback to direct curl** when possible (FlareSolverr is slower due to browser overhead)
4. **Destroy sessions** when done to free resources

## Limitations

- **Slower than direct curl** (launches headless browser)
- **Resource intensive** (limit concurrent requests)
- **May not solve all captchas** (most Cloudflare challenges work)
- **HTML only** in response (no client-side JS execution after fetch)

## Best Practices

1. **Always try direct curl first**
2. **Use sessions for multi-page workflows**
3. **Set appropriate maxTimeout** (default 60s, increase for slow sites)
4. **Clean up sessions** when done
5. **Handle errors gracefully** (check `status` field)
6. **Rate limit** your requests (don't overwhelm FlareSolverr or target site)
