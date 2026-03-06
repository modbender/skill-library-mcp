---
name: online-shopping
description: Browse and buy products from online stores, including Cloudflare-protected sites. Use when the user asks to find, compare, or order products online. Handles product search, price comparison, adding to cart, filling checkout forms, and navigating to payment. Uses a stealth browser (Patchright) to bypass bot detection.
---

# Online Shopping

## Overview

Search for products, compare options, and complete purchases on online stores — even those protected by Cloudflare. Uses Patchright (stealth Playwright) to avoid bot detection.

## First-Time Setup

Run the setup script to install all dependencies:

```bash
bash <skill-dir>/scripts/setup.sh
```

This installs xvfb, Patchright, and Chromium, then verifies everything works. See [references/setup.md](references/setup.md) for manual steps or troubleshooting.

## Workflow

1. **Understand the request** — product type, specs, size, brand preference, budget
2. **Browse the store** — use stealth browser script to search and extract product listings
3. **Recommend** — present options with price, availability, ratings. Give a clear recommendation.
4. **Confirm** — get explicit approval before adding to cart
5. **Checkout** — fill shipping/contact details, select delivery and payment
6. **Stop before paying** — always confirm with the user before completing a purchase

## Using the Stealth Browser

All browsing goes through Patchright scripts executed with `xvfb-run`. Do NOT use OpenClaw's built-in `browser` tool for Cloudflare-protected sites — it connects via CDP which leaks `Runtime.enable` calls that Cloudflare detects.

### Quick browse (bundled script)

```bash
xvfb-run --auto-servernum node <skill-dir>/scripts/browse.mjs "<url>" --screenshot /tmp/page.png --text
```

### Custom scripts

Write `.mjs` scripts in `/tmp/` for multi-step flows. Auto-detect Patchright path:

```javascript
import { createRequire } from 'module';
import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';

function findPatchright() {
  const root = execSync('npm root -g 2>/dev/null').toString().trim();
  const candidates = [
    root + '/openclaw/node_modules/patchright',
    process.env.HOME + '/.npm-global/lib/node_modules/openclaw/node_modules/patchright',
    root + '/patchright',
  ];
  for (const p of candidates) {
    try { if (existsSync(p)) return p; } catch {}
  }
  throw new Error('Patchright not found. Run setup.sh first.');
}

const require = createRequire(import.meta.url);
const { chromium } = require(findPatchright());

const browser = await chromium.launchPersistentContext('/tmp/patchright-ctx', {
  headless: false,   // REQUIRED — Cloudflare detects headless
  viewport: null,    // REQUIRED — use real viewport, not default 800x600
  args: ['--no-sandbox', '--disable-gpu'],
});

const page = browser.pages()[0] || await browser.newPage();
// ... your automation here ...
await browser.close();
```

Execute with: `xvfb-run --auto-servernum node /tmp/my-script.mjs`

### Critical best practices (from Patchright docs)

These are essential for avoiding bot detection:

1. **`headless: false`** — always. Cloudflare fingerprints headless mode. Use xvfb for servers without a display.
2. **`viewport: null`** — let the browser use its natural viewport. Custom viewports are a detection signal.
3. **Do NOT set custom `userAgent` or HTTP headers** — fingerprint injection makes you more detectable, not less.
4. **Use persistent context** (`launchPersistentContext`) — retains cookies, localStorage, and session state between runs. Also more closely resembles real browser behavior.
5. **Prefer Google Chrome over Chromium** where available (x86_64: `npx patchright install chrome`, then `channel: "chrome"`). Chromium has subtle fingerprint differences. ARM64 only supports Chromium.
6. **Do NOT use `connectOverCDP()`** — connecting via raw CDP bypasses Patchright's patches. Always use `chromium.launch()` or `chromium.launchPersistentContext()`.

### Why Patchright works where Playwright doesn't

Patchright patches three key detection vectors:
- **Runtime.enable leak** — Playwright uses `Runtime.enable` CDP call which sites detect. Patchright executes JS in isolated execution contexts instead.
- **Command flag leaks** — Removes `--enable-automation`, adds `--disable-blink-features=AutomationControlled`.
- **Console.enable leak** — Disables console API to avoid detection (console.log won't work in page context).

### Script workflow for shopping

1. **Search script** — navigate to store, search for product, extract listings as text
2. **Product script** — click into a product page, get details
3. **Cart script** — add to cart, navigate to checkout
4. **Checkout script** — dump form fields with `page.evaluate()`, fill details, select shipping/payment
5. **Screenshot** — always screenshot before completing purchase for user confirmation

Write each step as a separate `.mjs` script in `/tmp/`. Persistent context means the cart and session carry over between scripts.

### Debugging tips

- Use `page.screenshot()` liberally to see what the page looks like
- Use `page.evaluate(() => document.body.innerText)` to dump page text
- Dump form fields with `page.evaluate(() => { ... querySelectorAll('input') ... })` before filling
- Some fields may be read-only (auto-filled from other fields) — check before trying to fill
- Use `page.waitForTimeout()` generously — sites need time to load/render
- Close cookie banners early — they can block interactions

## User Details & Preferences

Check `references/preferences.md` for saved shopping data (addresses, payment methods, delivery preferences, order history). If it doesn't exist yet, copy `references/preferences-template.md` to `references/preferences.md` and fill it in.

Fall back to USER.md for basic contact/address info.

When checkout requires info not on file, ask the user. After a successful order, update `references/preferences.md` with:
- Any new address or delivery preference
- The order in the history table

Never store card numbers or sensitive payment credentials. Only store method names (e.g. "Swish", "PayPal", "Visa ending 4321").

## Safety

- **Never complete a purchase without explicit user confirmation**
- Show the cart summary, total price, and shipping cost before final step
- Screenshot the checkout page and describe it to the user
- If something looks wrong (wrong product, unexpected charges), stop and ask

## Site-Specific Notes

See [references/sites.md](references/sites.md) for store-specific quirks and tips. If the file doesn't exist yet, copy [references/sites-template.md](references/sites-template.md) to get started.
