---
name: playwright-npx
description: Fast browser automation using Node.js scripts with Playwright (run via `node script.mjs`). Use for web scraping, screenshots, form automation, and any browser task requiring programmatic control. For simple page fetching without JavaScript execution, use web_fetch first. For interactive CLI browsing without writing code, use browser tool or playwright-cli. This skill is ideal when you need full control, custom logic, or reusable scripts.
metadata: {"clawdbot":{"emoji":"🎭","requires":{"bins":["node","npx"]}}, "created_by": "Kuba + Mahone", "created_date": "2026-02-04", "is_custom": true}
---

# Playwright Browser Automation

> 🤝 Developed together by Kuba + Mahone · Feb 2026

Code-first browser automation with Playwright.

## When to Use

| Tool | Use When |
|------|----------|
| **web_fetch** | Simple pages, no JavaScript needed |
| **This skill** | JavaScript-heavy sites, complex interactions, full control |
| **stealth-browser** | Bot detection / Cloudflare issues |
| **browser tool** | Visual exploration, last resort |
| **playwright-cli** | Interactive CLI without writing code |

## Setup

```bash
# One-time per project
npm init -y
npm install playwright
npx playwright install chromium
```

**package.json example:**
```json
{
  "name": "my-automation",
  "type": "module",
  "dependencies": {
    "playwright": "^1.40.0"
  }
}
```

## Minimal Example

```javascript
// tmp/example.mjs
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();

await page.goto('https://example.com');
console.log('Title:', await page.title());

await browser.close();
```

```bash
node tmp/example.mjs
```

## Quick Patterns

### Screenshot
```javascript
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1280, height: 800 });
await page.goto('https://example.com');
await page.screenshot({ path: 'tmp/screenshot.png', fullPage: true });
await browser.close();
```

### Scrape Data
```javascript
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('https://news.ycombinator.com');
const stories = await page.$$eval('.titleline > a', links => 
  links.slice(0, 5).map(a => ({ title: a.innerText, url: a.href }))
);
console.log(JSON.stringify(stories, null, 2));
await browser.close();
```

### Form Interaction
```javascript
await page.goto('https://example.com/login');
await page.fill('input[name="email"]', 'user@example.com');
await page.fill('input[name="password"]', 'password');
await page.click('button[type="submit"]');
```

### Wait for Dynamic Content
```javascript
// Wait for network idle (SPA)
await page.goto(url, { waitUntil: 'networkidle' });

// Wait for specific element
await page.waitForSelector('.results', { timeout: 10000 });

// Wait for condition
await page.waitForFunction(() => 
  document.querySelectorAll('.item').length > 0
);
```

### Persistent Session
```javascript
import fs from 'fs';
const SESSION_FILE = 'tmp/session.json';

let context;
if (fs.existsSync(SESSION_FILE)) {
  context = await browser.newContext({ storageState: SESSION_FILE });
} else {
  context = await browser.newContext();
}
const page = await context.newPage();
// ... login ...
await context.storageState({ path: SESSION_FILE });
```

## Headless vs Headed

```javascript
// Headless (default, fastest)
await chromium.launch({ headless: true });

// Headed (see the browser)
await chromium.launch({ headless: false });

// Slow motion (debugging)
await chromium.launch({ headless: false, slowMo: 100 });
```

## Selectors Quick Reference

```javascript
// CSS
await page.click('button.submit');
await page.fill('input#email', 'text');

// Text content
await page.click('text=Submit');
await page.click('text=/log\s*in/i');  // regex

// XPath
await page.click('xpath=//button[@type="submit"]');

// ARIA role
await page.click('role=button[name="Submit"]');

// Test ID (most stable)
await page.click('[data-testid="submit-btn"]');

// Chain selectors
await page.click('nav >> text=Settings');
```

**See [references/selectors.md](references/selectors.md) for complete selector guide.**

## Error Handling

```javascript
try {
  await page.goto('https://example.com', { timeout: 30000 });
  const hasResults = await page.locator('.results').isVisible().catch(() => false);
  if (!hasResults) {
    console.log('No results');
    process.exit(0);
  }
} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: 'tmp/error.png' });
  process.exit(1);
} finally {
  await browser.close();
}
```

## Examples & Templates

### Working Examples
- [examples/screenshot.mjs](examples/screenshot.mjs) - Full-page screenshots
- [examples/scrape.mjs](examples/scrape.mjs) - Data extraction
- [examples/form-interaction.mjs](examples/form-interaction.mjs) - Form automation
- [examples/login-session.mjs](examples/login-session.mjs) - Persistent sessions

### Reusable Templates
- [scripts/minimal-template.mjs](scripts/minimal-template.mjs) - Clean starting point
- [scripts/screenshot-template.mjs](scripts/screenshot-template.mjs) - Configurable screenshot
- [scripts/scrape-template.mjs](scripts/scrape-template.mjs) - Data scraping scaffold

**Copy templates:**
```bash
cp scripts/minimal-template.mjs tmp/my-task.mjs
# Edit tmp/my-task.mjs, then run:
node tmp/my-task.mjs
```

## Tooling Commands

```bash
# Record interactions to generate code
npx playwright codegen https://example.com

# Debug selectors
npx playwright codegen --target javascript https://example.com

# Show trace
npx playwright show-trace tmp/trace.zip
```

## Deep References

- **[references/selectors.md](references/selectors.md)** - Complete selector guide (CSS, text, XPath, ARIA, test-id)
- **[references/debugging.md](references/debugging.md)** - Debugging techniques (headless, slowMo, screenshots)
- **[references/troubleshooting.md](references/troubleshooting.md)** - Common errors and solutions

## Tips

- Always put scripts in `tmp/` — it's gitignored
- Use `.mjs` extension for ES modules (no `type: module` needed)
- Add `console.log()` liberally for debugging
- Use `page.screenshot()` when things go wrong
- For complex sites, add `await page.waitForLoadState('networkidle')`
- See [references/debugging.md](references/debugging.md) for detailed debugging guide
- See [references/troubleshooting.md](references/troubleshooting.md) for common issues
