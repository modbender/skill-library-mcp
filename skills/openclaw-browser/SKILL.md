---
name: openclaw-browser
description: Browser automation via Chrome DevTools Protocol (CDP) for OpenClaw. Use when user needs to take screenshots of websites, automate browser actions, or interact with web pages programmatically. Triggers on: screenshot requests, browser automation, web page capture, CDP-based browser control.
---

# OpenClaw Browser

Browser automation for OpenClaw via Chrome DevTools Protocol.

## Prerequisites

Chrome must be installed and running with remote debugging enabled:

```bash
# Start Chrome with CDP (port 9222)
chrome --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0
```

## Quick Start

### Screenshot a Website

```bash
# Using the provided script
node ~/.openclaw/workspace/skills/openclaw-browser/scripts/screenshot.js https://example.com /tmp/output.png

# With custom viewport
node ~/.openclaw/workspace/skills/openclaw-browser/scripts/screenshot.js https://example.com /tmp/output.png --width=1920 --height=1080
```

### Full Page Screenshot

The script automatically captures full page content, not just viewport.

## How It Works

1. Connects to running Chrome via CDP (http://127.0.0.1:9222)
2. Creates new tab or uses existing one
3. Navigates to target URL
4. Waits for page load
5. Takes screenshot
6. Saves to specified path

## Common Issues

**Chrome not running:**
- Start Chrome with CDP flags first
- Verify with: `curl http://127.0.0.1:9222/json/version`

**Headless detection:**
- Some sites (Xiaohongshu, Taobao) detect headless browsers
- Solution: Use non-headless Chrome (visible window)
- This skill connects to existing Chrome, avoiding detection

**Permission errors:**
- Use `--no-sandbox` when starting Chrome if needed

## Script Reference

See [scripts/screenshot.js](scripts/screenshot.js) for the main automation script.

## Advanced Usage

For custom automation beyond screenshots, modify the script or use Puppeteer directly:

```javascript
const puppeteer = require('puppeteer');
const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9222' });
// ... custom actions
```
