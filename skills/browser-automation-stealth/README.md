# Browser Automation Stealth

**Value Proposition**: Anti-bot evasion Playwright wrapper. Evade detection, manage cookies, rotate headers, handle captchas. Silent, headless, undetectable.

## Problem Solved
- Websites blocking bot automation
- Captcha & anti-bot detection
- Headers/fingerprint inconsistency
- Rate limiting on web scraping
- Session management complexity

## Use Cases
- Web scraping at scale (undetected)
- Automated testing on protected sites
- Data collection for market research
- Competitive intelligence gathering
- Automated form submission (compliant)
- Screenshot automation without detection

## Quick Start

```bash
npm install browser-automation-stealth
# or
python -m pip install browser-automation-stealth
```

```javascript
const { StealthBrowser } = require('browser-automation-stealth');

const browser = new StealthBrowser({
  headless: true,
  stealth: 'aggressive'  // evasion level
});

const page = await browser.newPage();
await page.goto('https://example.com');
await page.screenshot({ path: 'example.png' });
await browser.close();
```

## Features
✅ Playwright wrapper with stealth defaults
✅ Anti-detection mechanisms (fingerprint randomization)
✅ Header rotation (100+ user-agents)
✅ Proxy support (SOCKS5, HTTP)
✅ Cookie jar management
✅ Captcha bypass (integration-ready)
✅ Rate limiting aware
✅ Screenshot/PDF generation
✅ Form automation
✅ Cookie/session persistence

## Installation

### Node.js
```bash
npm install browser-automation-stealth
```

### Python
```bash
pip install browser-automation-stealth
```

### Requirements
- Playwright (auto-installed)
- Chrome/Chromium (downloaded automatically)

## Configuration

```javascript
const browser = new StealthBrowser({
  headless: true,
  stealth: 'aggressive',  // 'low', 'medium', 'aggressive'
  proxy: 'socks5://proxy:1080',
  userAgent: 'random',  // or provide custom
  timeout: 30000,
  retries: 3,
  captchaBypass: true,
  headerRotation: true
});
```

## Example Code

### Basic Page Scraping
```javascript
const { StealthBrowser } = require('browser-automation-stealth');

async function scrapeNews() {
  const browser = new StealthBrowser();
  const page = await browser.newPage();
  
  await page.goto('https://news.example.com', { waitUntil: 'networkidle' });
  
  const articles = await page.evaluate(() => {
    return document.querySelectorAll('article').map(el => ({
      title: el.querySelector('h2')?.innerText,
      url: el.querySelector('a')?.href
    }));
  });
  
  await browser.close();
  return articles;
}

scrapeNews().then(console.log);
```

### Form Automation (No Detection)
```javascript
const browser = new StealthBrowser({
  stealth: 'aggressive',
  headerRotation: true
});

const page = await browser.newPage();
await page.goto('https://form.example.com');

// Fill form stealthily
await page.type('#username', 'user@example.com', { delay: 50 });  // Human-like typing
await page.type('#password', 'secret', { delay: 40 });
await page.click('#submit');
await page.waitForNavigation();

const result = await page.title();
console.log('Form submitted:', result);
```

### Screenshot with Rotating IPs
```javascript
const browser = new StealthBrowser({
  proxy: 'http://proxy-rotator:8080',
  stealth: 'medium'
});

const pages = [
  'https://example.com/page1',
  'https://example.com/page2',
  'https://example.com/page3'
];

for (const url of pages) {
  const page = await browser.newPage();
  await page.goto(url);
  await page.screenshot({ path: `${url.split('/').pop()}.png` });
}

await browser.close();
```

### Cookie Management
```javascript
const browser = new StealthBrowser();
const page = await browser.newPage();

// Load saved cookies
await page.context().addCookies(require('./cookies.json'));

await page.goto('https://authenticated-site.com');
const content = await page.content();

// Save cookies for next session
const cookies = await page.context().cookies();
require('fs').writeFileSync('cookies.json', JSON.stringify(cookies));
```

## Anti-Detection Features

| Feature | Description |
|---------|-------------|
| **Fingerprint Randomization** | Randomize canvas, WebGL, screen properties |
| **Header Rotation** | 100+ realistic user-agents |
| **Proxy Support** | SOCKS5 & HTTP proxies |
| **Timing Variance** | Random delays mimicking human behavior |
| **Captcha Bypass** | 2Captcha/AntiCaptcha integration |
| **Device Emulation** | Emulate real devices (iPhone, Android, etc.) |

## API Reference

### `StealthBrowser(options)`
Create a new stealth browser instance.
- `headless` (boolean): Run in headless mode (default: true)
- `stealth` (string): 'low', 'medium', 'aggressive'
- `proxy` (string): Proxy URL
- `timeout` (number): Navigation timeout in ms
- `captchaBypass` (boolean): Enable captcha solving

### `newPage()`
Create a new page. Returns `Promise<Page>`

### `goto(url, options)`
Navigate to URL with stealth headers.

### `screenshot(options)`
Take screenshot without detection.

## Troubleshooting

**Getting "Failed to launch browser"?**
→ Run `npx playwright install`

**Still being detected?**
→ Try `stealth: 'aggressive'` and add a proxy

**Captcha still blocking?**
→ Enable `captchaBypass: true` and set API key

## Support
📧 support@midas-skills.com
🔗 Docs: https://docs.midas-skills.com/browser-automation-stealth

---

**Want pro version + updates?** [Buy bundle on Gumroad](https://gumroad.com/midas-skills)
