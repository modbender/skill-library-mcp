# Browser Automation v2

Enterprise-grade browser automation for OpenClaw with robust resource management.

## Features

- ✅ **Automatic tab cleanup** - No more tab accumulation
- ✅ **Timeout & retry** - Exponential backoff on network errors
- ✅ **Smart waiting** - `waitForLoadState`, `waitForSelector`
- ✅ **Concurrency lock** - Prevents profile conflicts
- ✅ **Structured logging** - DEBUG=1 for verbose output
- ✅ **Configurable** - Environment variables for timeout, retries, profile

## Files

- `browser-manager.v2.js` - Core manager class
- `search-google.js` - Google search with screenshot + PDF
- `fetch-summary.js` - Fetch page content (static or dynamic)
- `multi-pages.js` - Batch process multiple URLs
- `fill-form.js` - Auto-fill forms by field names

## Usage

```bash
# Set environment (optional)
export BROWSER_PROFILE=openclaw
export BROWSER_TIMEOUT=30000
export BROWSER_RETRIES=2
export DEBUG=1

cd ~/.openclaw/workspace/skills/browser-automation-v2

# Search Google
node search-google.js "OpenClaw automation"

# Batch process
node multi-pages.js "https://example.com" "https://github.com"

# Fill form
node fill-form.js "https://example.com/form" '{"email":"test@xx.com"}'
```

## Integration

Register as OpenClaw skill:
```bash
openclaw skills install ~/.openclaw/workspace/skills/browser-automation-v2
```

Or call directly from agent:
```
run search-google.js "query"
```

## Requirements

- OpenClaw v2026.2.15+
- Browser profile configured (default: `openclaw`)
- Gateway running

## Troubleshooting

- **Timeout errors**: Increase `BROWSER_TIMEOUT`
- **Profile locked**: Wait for other instance to finish
- **Element not found**: Use `snapshot --format ai` to debug refs

---

*Created: 2026-02-16*
*Version: 2.0.0*
*License: MIT*
