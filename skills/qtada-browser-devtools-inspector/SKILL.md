---
name: browser-devtools-inspector
description: "Inspect browser DevTools (Console, Network, Performance) for
  debugging frontend applications. Use when: (1) checking console errors or
  warnings, (2) analyzing failed API requests or CORS issues, (3) investigating
  slow page loads or network performance, (4) debugging JavaScript errors, (5)
  inspecting HTTP request/response headers, (6) monitoring API endpoints during
  page load, or (7) troubleshooting frontend issues with real browser data."
---


# Browser DevTools Inspector

Capture and analyze browser DevTools data (Console, Network, Performance) to debug frontend applications and diagnose issues.

## Quick Start

### Capture Console Logs

```bash
node scripts/capture_console.js <url> [--filter=error]
```

Filters: `all`, `log`, `warn`, `error`, `info`

**Example:**
```bash
# Check for errors on storefront
node scripts/capture_console.js http://localhost:5177 --filter=error
```

### Capture Network Requests

```bash
node scripts/capture_network.js <url> [--filter=failed] [--type=xhr]
```

Filters: `all`, `failed`, `slow`  
Types: `all`, `xhr`, `fetch`, `script`, `stylesheet`, `image`

**Example:**
```bash
# Find failed API requests
node scripts/capture_network.js http://localhost:5177 --filter=failed --type=xhr

# Check CORS issues
node scripts/check_cors.js http://localhost:5177
```

### Analyze Performance

```bash
node scripts/analyze_performance.js <url>
```

Reports:
- Page load time
- Time to First Byte (TTFB)
- DOM Content Loaded
- Resource loading times
- Slowest resources

---

## Common Workflows

### Debug Console Errors

```bash
# 1. Capture all console output
node scripts/capture_console.js http://localhost:5177

# 2. Filter errors only
node scripts/capture_console.js http://localhost:5177 --filter=error

# 3. Review output for:
#    - JavaScript errors
#    - Failed network requests
#    - Uncaught exceptions
#    - React/Vue warnings
```

### Diagnose API Failures

```bash
# 1. Capture network requests
node scripts/capture_network.js http://localhost:5177 --type=xhr

# 2. Check for CORS
node scripts/check_cors.js http://localhost:5177

# 3. Review output for:
#    - 404 Not Found errors
#    - 401 Unauthorized
#    - 500 Server errors
#    - CORS policy blocks
#    - Network timeouts
```

### Analyze Performance Issues

```bash
# 1. Run performance analysis
node scripts/analyze_performance.js http://localhost:5177

# 2. Review metrics:
#    - Load time > 3s = slow
#    - TTFB > 1s = backend issue
#    - Large resources (>1MB)
#    - Blocking scripts

# 3. Identify bottlenecks and optimize
```

### Check for CORS Issues

```bash
# Quick CORS check
node scripts/check_cors.js http://localhost:5177

# Output includes:
# - Missing CORS headers
# - Invalid Access-Control-Allow-Origin
# - Blocked requests
# - Preflight failures
```

---

## Output Format

All scripts output structured JSON for easy parsing:

### Console Output
```json
{
  "url": "http://localhost:5177",
  "timestamp": "2026-03-02T02:15:00Z",
  "logs": [
    {
      "level": "error",
      "message": "Failed to load resource: net::ERR_FAILED",
      "source": "http://localhost:8000/api/vendors",
      "lineNumber": 42
    }
  ],
  "summary": {
    "total": 15,
    "errors": 3,
    "warnings": 2,
    "logs": 10
  }
}
```

### Network Output
```json
{
  "url": "http://localhost:5177",
  "timestamp": "2026-03-02T02:15:00Z",
  "requests": [
    {
      "url": "http://localhost:8000/api/products",
      "method": "GET",
      "status": 200,
      "statusText": "OK",
      "type": "xhr",
      "size": 53167,
      "time": 26234,
      "headers": {
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      }
    }
  ],
  "summary": {
    "total": 42,
    "failed": 2,
    "slow": 5,
    "totalSize": 2456789,
    "totalTime": 8234
  }
}
```

---

## Advanced Usage

### Filter by URL Pattern
```bash
# Only capture requests to /api/*
node scripts/capture_network.js http://localhost:5177 --pattern="/api/*"
```

### Export Results
```bash
# Save to file
node scripts/capture_console.js http://localhost:5177 > console-output.json
node scripts/capture_network.js http://localhost:5177 > network-output.json
```

### Combine with Other Tools
```bash
# Parse with jq
node scripts/capture_network.js http://localhost:5177 | jq '.requests[] | select(.status >= 400)'

# Count errors
node scripts/capture_console.js http://localhost:5177 | jq '.summary.errors'
```

---

## Requirements

- Node.js 14+
- Puppeteer (auto-installed on first run)
- Chrome/Chromium browser

**Installation:**
```bash
cd scripts
npm install
```

---

## References

- **DevTools Protocol**: See `references/devtools-api.md` for full CDP reference
- **Common Issues**: See `references/common-issues.md` for troubleshooting patterns

---

## Tips

1. **Run locally first** - Test on localhost before production URLs
2. **Filter aggressively** - Use `--filter=error` to reduce noise
3. **Check CORS early** - CORS issues are common in development
4. **Monitor slow requests** - API calls >1s need optimization
5. **Save outputs** - Redirect to files for later analysis

---

## Troubleshooting

### Script Won't Run
```bash
# Install dependencies
cd scripts
npm install puppeteer
```

### No Output
```bash
# Check if page loads
node scripts/capture_console.js <url> --verbose
```

### Browser Not Found
```bash
# Set Chrome path (Windows)
set PUPPETEER_EXECUTABLE_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

---

## Examples

### Real-World Use Cases

**Example 1: Debug ThreeU Storefront**
```bash
# Check console errors
node scripts/capture_console.js http://localhost:5177 --filter=error

# Find failed API calls
node scripts/capture_network.js http://localhost:5177 --filter=failed

# Check CORS
node scripts/check_cors.js http://localhost:5177
```

**Example 2: Analyze SuperAdmin Performance**
```bash
# Full performance report
node scripts/analyze_performance.js http://localhost:5179

# Find slow API endpoints
node scripts/capture_network.js http://localhost:5179 --filter=slow --type=xhr
```

**Example 3: Monitor Production Issues**
```bash
# Capture all errors
node scripts/capture_console.js https://storefront.threeu.app --filter=error > prod-errors.json

# Check for 404s
node scripts/capture_network.js https://storefront.threeu.app --filter=failed > prod-404s.json
```
