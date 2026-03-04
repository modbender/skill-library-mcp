# Freeman Browser — Web Stealth Browser for AI Agents

> **Stealth engine for your OpenClaw**

---

## Why your agent needs this

Regular Playwright gets blocked **immediately** by:
- Cloudflare (bot score detection)
- DataDome (fingerprint analysis)
- PerimeterX (behavioral analysis)

Freeman Browser solves this by combining:
1. **Real device fingerprint** — iPhone 15 Pro or Windows Chrome, complete with canvas, WebGL, fonts
2. **Freeman-like behavior** — Bezier mouse curves, 60–220ms typing, natural scroll with jitter
3. **Full anti-detection** — `webdriver=false`, no automation flags

---

## Quick Start

```js
const { launchFreeman } = require('freeman-browser');

const { browser, page, humanType, humanClick, humanScroll, sleep } = await launchFreeman();

// Desktop Chrome (Windows fingerprint)
const { page: desktopPage } = await launchFreeman({ mobile: false });

await page.goto('https://example.com', { waitUntil: 'domcontentloaded' });
await humanScroll(page, 'down');
await humanType(page, 'input[type="email"]', 'user@example.com');
await humanClick(page, 760, 400);
await browser.close();
```

---

## Setup

### As an OpenClaw Skill

```bash
clawhub install sbrin/freeman-browser
```

### As a standalone NPM package

```bash
npm install freeman-browser playwright
npx playwright install chromium --with-deps
```

---

## Configuration

You can configure the browser's fingerprint (locale, timezone, and geolocation) by creating a `browser.json` file in the root of your project:

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

*(Alternatively, you can specify a custom config path via the `BROWSER_CONFIG` environment variable.)*

---

## How it compares

| Feature | Regular Playwright | Freeman Browser |
|---------|-------------------|---------------|
| Bot detection | Fails | Passes all |
| Mouse movement | Instant teleport | Bezier curves |
| Typing speed | Instant | 60–220ms/char |
| Fingerprint | Detectable bot | iPhone 15 Pro |
| Cloudflare | Blocked | Bypassed |
| DataDome | Blocked | Bypassed |

## Credits

Based on the [human-browser](https://github.com/al1enjesus/human-browser) by [al1enjesus](https://github.com/al1enjesus).