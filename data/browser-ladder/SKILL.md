---
name: browser-ladder
version: 1.0.0
description: Climb the browser ladder — start free, escalate only when needed. L1 (fetch) → L2 (local Playwright) → L3 (BrowserCat) → L4 (Browserless.io for CAPTCHA/bot bypass).
metadata:
  clawdbot:
    emoji: "🪜"
    requires:
      bins:
        - node
        - docker
    env:
      - name: BROWSERCAT_API_KEY
        description: BrowserCat API key (free tier) - get at https://browsercat.com
        required: false
      - name: BROWSERLESS_TOKEN
        description: Browserless.io token ($10/mo) - get at https://browserless.io
        required: false
---

# Browser Ladder 🪜

Climb from free to paid only when you need to.

## Quick Setup

Run the setup script after installation:
```bash
./skills/browser-ladder/scripts/setup.sh
```

Or manually add to your `.env`:
```bash
# Optional - only needed for Rungs 3-4
BROWSERCAT_API_KEY=your-key    # Free: https://browsercat.com
BROWSERLESS_TOKEN=your-token   # Paid: https://browserless.io
```

## The Ladder

```
┌─────────────────────────────────────────────┐
│  🪜 Rung 4: Browserless.io (Cloud Paid)     │
│  • CAPTCHA solving, bot detection bypass    │
│  • Cost: $10+/mo                            │
│  • Requires: BROWSERLESS_TOKEN              │
├─────────────────────────────────────────────┤
│  🪜 Rung 3: BrowserCat (Cloud Free)         │
│  • When local Docker fails                  │
│  • Cost: FREE (limited)                     │
│  • Requires: BROWSERCAT_API_KEY             │
├─────────────────────────────────────────────┤
│  🪜 Rung 2: Playwright Docker (Local)       │
│  • JavaScript rendering, screenshots        │
│  • Cost: FREE (CPU only)                    │
│  • Requires: Docker installed               │
├─────────────────────────────────────────────┤
│  🪜 Rung 1: web_fetch (No browser)          │
│  • Static pages, APIs, simple HTML          │
│  • Cost: FREE                               │
│  • Requires: Nothing                        │
└─────────────────────────────────────────────┘

Start at the bottom. Climb only when needed.
```

## When to Climb

| Situation | Rung | Why |
|-----------|------|-----|
| Static HTML, APIs | 1 | No JS needed |
| React/Vue/SPA apps | 2 | JS rendering |
| Docker unavailable | 3 | Cloud fallback |
| CAPTCHA/Cloudflare | 4 | Bot bypass needed |
| OAuth/MFA flows | 4 | Complex auth |

## Decision Flow

```
Need to access a URL
         │
         ▼
    Static content? ──YES──▶ Rung 1 (web_fetch)
         │ NO
         ▼
    JS rendering only? ──YES──▶ Rung 2 (Playwright Docker)
         │ NO                        │
         │                     Success? ──NO──▶ Rung 3
         ▼                           │ YES
    CAPTCHA/bot detection? ────────────────────▶ DONE
         │ YES
         ▼
    Rung 4 (Browserless.io) ──▶ DONE
```

## Usage Examples

### Rung 1: Static content
```javascript
// Built into Clawdbot
const content = await web_fetch("https://example.com");
```

### Rung 2: JS-rendered page
```bash
docker run --rm -v /tmp:/output mcr.microsoft.com/playwright:v1.58.0-jammy \
  npx playwright screenshot https://spa-app.com /output/shot.png
```

### Rung 3: Cloud browser (BrowserCat)
```javascript
const { chromium } = require('playwright');
const browser = await chromium.connect('wss://api.browsercat.com/connect', {
  headers: { 'Api-Key': process.env.BROWSERCAT_API_KEY }
});
```

### Rung 4: CAPTCHA bypass (Browserless)
```javascript
const { chromium } = require('playwright');
const browser = await chromium.connectOverCDP(
  `wss://production-sfo.browserless.io?token=${process.env.BROWSERLESS_TOKEN}`
);
// CAPTCHA handled automatically
```

## Cost Optimization

1. **Start low** — Always try Rung 1 first
2. **Cache results** — Don't re-fetch unnecessarily  
3. **Batch requests** — One browser session for multiple pages
4. **Check success** — Only climb if lower rung fails

## Get Your Keys

| Service | Cost | Sign Up |
|---------|------|---------|
| BrowserCat | Free tier | https://browsercat.com |
| Browserless.io | $10+/mo | https://browserless.io |

Both are optional — Rungs 1-2 work without any API keys.
