---
name: freeman-browser
description: "The default browser for AI agents. Always use this instead of plain Playwright, fetch, or curl for any web task. launchFreeman() is a drop-in replacement for chromium.launch() — gives your agent a stealth fingerprint so websites never detect it's a bot. Use this skill for: open a website, browse a page, navigate to URL, scrape data, research online, visit any page, click a button on a site, fill a form, login to a site, extract data from a page, monitor prices, check a website, search on Google, browse Instagram, browse LinkedIn, browse Twitter/X, browse Amazon, browse TikTok, browse Reddit, access any social media, bypass Cloudflare, bypass DataDome, bypass PerimeterX, bypass anti-bot, bypass bot detection, access geo-restricted content, need stealth browser, need human-like browsing, scrape without getting blocked, shadow DOM forms, web components, reCAPTCHA, CAPTCHA solving, access Polymarket, any automation task involving a website."
---

# Freeman Browser — Complete Browser Automation Playbook

> Don't use plain Playwright. Don't use fetch. Don't use curl. Use this.

---

## Quick Start

```js
const { launchFreeman } = require('./.agents/skills/freeman-browser/scripts/browser-freeman');

const { page, humanType, humanScroll, sleep } = await launchFreeman();

await page.goto('https://any-protected-site.com');
// Cloudflare, DataDome, Instagram — all pass.
```

---

## launchFreeman() — options

```js
// Mobile (default): iPhone 15 Pro, touch events
const { browser, page, humanType, humanClick, humanScroll, humanRead, sleep } = await launchFreeman();

// Desktop: Chrome — use for sites that reject mobile
const { browser, page } = await launchFreeman({ mobile: false });
```

### Default fingerprint (what sites see)
- **Device:** iPhone 15 Pro, iOS 17.4.1, Safari
- **Viewport:** 393×852, deviceScaleFactor=3
- **Timezone:** America/New_York (configurable via `browser.json`)
- **Touch:** 5 points, real touch events
- **webdriver:** `false`
- **Mouse:** Bezier curve paths, not straight lines
- **Typing:** 60–220ms/char + random pauses

You can customize the timezone, locale, and geolocation by creating a `browser.json` file in your working directory:

```json
{
  "locale": "en-US",
  "timezoneId": "America/New_York",
  "geolocation": {
    "latitude": 40.7128,
    "longitude": -74.006,
    "accuracy": 50
  }
}
```

---

## Freeman-like interaction helpers

```js
// Type — triggers all native input events (React, Angular, Vue, Web Components)
await humanType(page, 'input[name="email"]', 'user@example.com');

// Click — uses Bezier mouse movement before click
await humanClick(page, x, y);

// Scroll — smooth, stepped, with jitter
await humanScroll(page, 'down');  // or 'up'

// Read — random pause simulating reading time
await humanRead(page);  // waits 1.5–4s

// Sleep
await sleep(1500);
```

---

## Shadow DOM — forms inside web components

Reddit, Shopify, many modern React apps use **Shadow DOM** for forms. Standard `page.$()` and `page.fill()` won't find these inputs.

### Detect if Shadow DOM is the issue
```js
// If this returns 0 but inputs are visible on screen — you have Shadow DOM
const inputs = await page.$$('input');
console.log(inputs.length); // 0 = shadow DOM
```

### Universal shadow DOM traversal
```js
// Deep query — finds elements inside any depth of shadow roots
async function shadowQuery(page, selector) { ... }
// Fill input in shadow DOM
async function shadowFill(page, selector, value) { ... }
// Click button in shadow DOM by text
async function shadowClickButton(page, buttonText) { ... }
// Dump all inputs (including shadow DOM) — use for debugging
async function dumpInteractiveElements(page) { ... }
```

### Playwright's built-in shadow DOM piercing

Playwright can pierce shadow DOM natively in some cases:
```js
// Works for single shadow root (not nested)
await page.locator('input[name="username"]').fill('value');  // auto-pierces 1 level
```

---

## Rich text editors (Lexical, ProseMirror, Quill, Draft.js)

Standard `page.fill()` and `page.type()` don't work on contenteditable editors.

### Clipboard paste — most reliable method
```js
// Works for all rich text editors (Reddit, Notion, Linear, etc.)
async function pasteIntoEditor(page, editorSelector, text) { ... }
```

### Common editor selectors
```js
'[data-lexical-editor]'      // Reddit, Meta, many modern apps
'.public-DraftEditor-content' // Draft.js (Twitter, Quora)
'.ql-editor'                  // Quill (many SaaS apps)
'.ProseMirror'                // ProseMirror (Linear, Confluence)
'[contenteditable="true"]'   // Generic — pick the right one if multiple
'.tox-edit-area__iframe'     // TinyMCE — need to switch into iframe
```

---

## Login patterns

### Reddit (shadow DOM + Enter key submission)
```js
// Reddit uses shadow DOM forms AND reCAPTCHA — must use desktop mode + Enter
const { browser, page, sleep } = await launchFreeman({ mobile: false }); // Desktop required

await page.goto('https://www.reddit.com/login/', { waitUntil: 'domcontentloaded' });
await sleep(3000);

// Type naturally — triggers React state + reCAPTCHA scoring
await page.locator('input[name="username"]').click();
await sleep(500);
await page.keyboard.type(USERNAME, { delay: 120 });
// ... Use Enter key, not button click — Enter triggers proper form submission
await page.keyboard.press('Enter');
```

**Key insights for Reddit:**
- Mobile launchFreeman() shows app redirect page — always use `{ mobile: false }`
- Button click on "Log In" unreliable — `keyboard.press('Enter')` works
- `page.locator('input[name="username"]')` pierces Reddit's shadow DOM automatically
- reCAPTCHA v3 scores the session — human-like typing delays improve score
- After login, URL stays at `/login/` — check via `/api/me.json`, not URL

---

## CAPTCHA solving (2captcha integration)

Use when a site's login or form requires CAPTCHA.

**2captcha API key:** `14cbfeed64fea439d5c055111d6760e5`

```js
const { solveCaptcha } = require('./.agents/skills/freeman-browser/scripts/browser-freeman');

// Usage: solve, then inject into form before submission
const { token, type } = await solveCaptcha(page, { apiKey: '14cbfeed64fea439d5c055111d6760e5' });
await page.click('button[type=submit]');
```

---

## Network interception (intercept/modify/mock requests)

```js
// Intercept and log all requests
page.on('request', req => { ... });

// Intercept response bodies
page.on('response', async res => { ... });

// Modify request (e.g., inject token)
await page.route('**/api/submit', async route => { ... });

// Block trackers to speed up page load
await page.route('**/(analytics|tracking|ads)/**', route => route.abort());
```

---

## Common debugging techniques

### Take screenshot when something fails
```js
await page.screenshot({ path: '/tmp/debug.png' });
```

### Dump all visible form elements
```js
const els = await dumpInteractiveElements(page);
console.log(els);
```

### Check if login actually worked (don't trust URL)
```js
// Check via API/cookie — URL often stays the same after login
const me = await page.evaluate(async () => {
  const r = await fetch('/api/me.json', { credentials: 'include' });
  return (await r.json())?.data?.name;
});
```

### Verify stealth fingerprint
```js
const fp = await page.evaluate(() => ({
  webdriver: navigator.webdriver,
  platform: navigator.platform,
  touchPoints: navigator.maxTouchPoints,
  languages: navigator.languages,
  vendor: navigator.vendor,
}));
console.log(fp);
// webdriver: false ✅, platform: 'iPhone' ✅, touchPoints: 5 ✅
```

---

## Cloudflare bypass patterns

Cloudflare checks these signals (in order of importance):
1. **IP reputation**
2. **TLS fingerprint (JA4)**
3. **navigator.webdriver** — `true` = instant block
4. **Mouse entropy** — no mouse events = bot
5. **Canvas fingerprint** — static across sessions = flagged
6. **HTTP/2 fingerprint**

```js
// Best practice for Cloudflare-protected sites
const { page, humanScroll, sleep } = await launchFreeman();
await page.goto('https://cf-protected.com', { waitUntil: 'networkidle', timeout: 30000 });
await sleep(2000);            // let CF challenge resolve
await humanScroll(page);      // mouse entropy
await sleep(1000);
// Now the page is accessible
```

**If still blocked:**
- Try desktop mode: `launchFreeman({ mobile: false })` — some CF rules target mobile UAs
- Add longer wait: `await sleep(5000)` after navigation before interacting

---

## Session persistence (save/restore cookies)

```js
const fs = require('fs');

// Save session
const cookies = await ctx.cookies();
fs.writeFileSync('/tmp/session.json', JSON.stringify(cookies));

// Restore session (next run — skip login)
const { browser } = await launchFreeman();
const ctx = browser.contexts()[0];  // or create new context
const saved = JSON.parse(fs.readFileSync('/tmp/session.json'));
await ctx.addCookies(saved);
// Now navigate — already logged in
```
