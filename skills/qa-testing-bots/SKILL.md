# Automated QA Testing Bots Skill

## Overview

This skill enables Claude to build and run **automated QA testing bots** that simulate
real user journeys across websites and web applications — catching bugs, broken flows,
and regressions before your users do.

Powered by **Apify** with Puppeteer and Playwright under the hood.

> 🔗 Sign up for Apify here: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- Simulate complete **user journeys** (signup, login, checkout, form submission)
- Detect **broken links**, **404 errors**, and **failed redirects** across an entire site
- Validate **UI elements** — buttons, inputs, modals, dropdowns — are present and functional
- Run **regression tests** after deployments to catch newly introduced bugs
- Take **screenshots and video recordings** at each step for visual debugging
- Test across multiple **viewports** (desktop, tablet, mobile)
- Assert **response times** and flag pages that are too slow

---

## Step 1 — Get Your Apify API Token

1. Go to **https://www.apify.com/?fpr=dx06p** and create a free account
2. Navigate to **Settings → Integrations**
   - Direct link: https://console.apify.com/account/integrations
3. Copy your **Personal API Token**: `apify_api_xxxxxxxxxxxxxxxx`
4. Set it as an environment variable:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

---

## Step 2 — Install Dependencies

```bash
npm install apify-client
```

---

## Actors for QA Testing

| Actor ID | Best For |
|---|---|
| `apify/puppeteer-scraper` | Full browser automation, form testing, click flows |
| `apify/playwright-scraper` | Cross-browser testing (Chrome, Firefox, WebKit) |
| `apify/broken-links-checker` | Detect all 404s and broken links site-wide |
| `apify/website-content-crawler` | Crawl all pages and validate structure |

---

## Examples

### Test a Full User Registration Flow

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor("apify/puppeteer-scraper").call({
  startUrls: [{ url: "https://your-app.com/signup" }],
  pageFunction: async function pageFunction(context) {
    const { page } = context;
    const results = { steps: [], passed: true, errors: [] };

    try {
      // Step 1 — Page loads
      await page.waitForSelector('#signup-form', { timeout: 5000 });
      results.steps.push({ step: "Page loaded", status: "PASS" });

      // Step 2 — Fill registration form
      await page.type('#firstName', 'Test');
      await page.type('#lastName', 'User');
      await page.type('#email', `testuser+${Date.now()}@example.com`);
      await page.type('#password', 'SecurePass123!');
      results.steps.push({ step: "Form filled", status: "PASS" });

      // Step 3 — Submit
      await Promise.all([
        page.waitForNavigation({ timeout: 8000 }),
        page.click('button[type="submit"]')
      ]);
      results.steps.push({ step: "Form submitted", status: "PASS" });

      // Step 4 — Assert success redirect
      const currentUrl = page.url();
      if (!currentUrl.includes('/dashboard')) {
        throw new Error(`Expected /dashboard, got: ${currentUrl}`);
      }
      results.steps.push({ step: "Redirected to dashboard", status: "PASS" });

      // Step 5 — Screenshot proof
      await page.screenshot({ path: 'signup-success.png', fullPage: true });

    } catch (err) {
      results.passed = false;
      results.errors.push(err.message);
      await page.screenshot({ path: 'signup-error.png', fullPage: true });
    }

    return results;
  }
});

const { items } = await run.dataset().getData();
const report = items[0];

console.log(report.passed ? "✅ All steps passed" : "❌ Test failed");
report.steps.forEach(s => console.log(`  [${s.status}] ${s.step}`));
if (report.errors.length) console.log("Errors:", report.errors);
```

---

### Test a Complete E-Commerce Checkout Flow

```javascript
const run = await client.actor("apify/puppeteer-scraper").call({
  startUrls: [{ url: "https://your-shop.com/products/test-item" }],
  pageFunction: async function pageFunction(context) {
    const { page } = context;
    const journey = [];

    // 1 — Product page
    await page.waitForSelector('.add-to-cart');
    journey.push({ step: "Product page loaded", status: "PASS" });

    // 2 — Add to cart
    await page.click('.add-to-cart');
    await page.waitForSelector('.cart-count', { timeout: 3000 });
    const cartCount = await page.$eval('.cart-count', el => el.innerText);
    journey.push({
      step: "Item added to cart",
      status: cartCount > 0 ? "PASS" : "FAIL",
      value: cartCount
    });

    // 3 — Go to cart
    await page.click('.cart-icon');
    await page.waitForSelector('.cart-summary');
    journey.push({ step: "Cart page loaded", status: "PASS" });

    // 4 — Proceed to checkout
    await page.click('.proceed-to-checkout');
    await page.waitForSelector('#checkout-form');
    journey.push({ step: "Checkout page loaded", status: "PASS" });

    // 5 — Fill shipping info
    await page.type('#shipping-name', 'QA Test User');
    await page.type('#shipping-address', '123 Test Street');
    await page.type('#shipping-city', 'San Francisco');
    await page.type('#shipping-zip', '94105');
    journey.push({ step: "Shipping info filled", status: "PASS" });

    return { journey, allPassed: journey.every(s => s.status === "PASS") };
  }
});
```

---

### Detect All Broken Links Site-Wide

```javascript
const run = await client.actor("apify/broken-links-checker").call({
  startUrls: [{ url: "https://your-website.com" }],
  maxCrawlingDepth: 3,
  maxRequestsPerCrawl: 200
});

const { items } = await run.dataset().getData();

const broken = items.filter(link => link.statusCode >= 400);
console.log(`Found ${broken.length} broken links out of ${items.length} checked`);

broken.forEach(link => {
  console.log(`  [${link.statusCode}] ${link.url} — found on: ${link.referrer}`);
});
```

---

### Responsive Design Test — Multi-Viewport

```javascript
const viewports = [
  { name: "Desktop", width: 1440, height: 900 },
  { name: "Tablet",  width: 768,  height: 1024 },
  { name: "Mobile",  width: 375,  height: 812 }
];

const run = await client.actor("apify/puppeteer-scraper").call({
  startUrls: [{ url: "https://your-app.com" }],
  pageFunction: async function pageFunction(context) {
    const { page } = context;
    const results = [];

    const viewports = [
      { name: "Desktop", width: 1440, height: 900 },
      { name: "Tablet",  width: 768,  height: 1024 },
      { name: "Mobile",  width: 375,  height: 812 }
    ];

    for (const vp of viewports) {
      await page.setViewport({ width: vp.width, height: vp.height });
      await page.reload();

      const navVisible = await page.$('.navbar') !== null;
      const ctaVisible = await page.$('.cta-button') !== null;

      results.push({
        viewport: vp.name,
        resolution: `${vp.width}x${vp.height}`,
        navbarPresent: navVisible,
        ctaButtonPresent: ctaVisible,
        status: navVisible && ctaVisible ? "PASS" : "FAIL"
      });
    }

    return results;
  }
});
```

---

### Performance & Load Time Assertions

```javascript
const run = await client.actor("apify/puppeteer-scraper").call({
  startUrls: [{ url: "https://your-app.com" }],
  pageFunction: async function pageFunction(context) {
    const { page } = context;

    const startTime = Date.now();
    await page.waitForSelector('main');
    const loadTime = Date.now() - startTime;

    const metrics = await page.metrics();
    const perfEntries = await page.evaluate(() =>
      JSON.stringify(window.performance.timing)
    );
    const timing = JSON.parse(perfEntries);
    const ttfb = timing.responseStart - timing.navigationStart;
    const domReady = timing.domContentLoadedEventEnd - timing.navigationStart;

    return {
      url: page.url(),
      loadTimeMs: loadTime,
      ttfbMs: ttfb,
      domReadyMs: domReady,
      jsHeapUsedMB: (metrics.JSHeapUsedSize / 1024 / 1024).toFixed(2),
      passed: loadTime < 3000 && ttfb < 600,
      warnings: [
        loadTime > 3000 ? `Slow load: ${loadTime}ms (threshold: 3000ms)` : null,
        ttfb > 600 ? `High TTFB: ${ttfb}ms (threshold: 600ms)` : null
      ].filter(Boolean)
    };
  }
});
```

---

## QA Workflow — How Claude Uses This Skill

When asked to test a site or app, Claude will:

1. **Map** the user journeys to test (registration, login, checkout, search...)
2. **Build** a Puppeteer/Playwright test script for each journey
3. **Run** all tests in parallel via Apify actors
4. **Collect** pass/fail results, screenshots, and error messages
5. **Generate** a structured test report with step-by-step results
6. **Flag** failures with context — which step failed and why
7. **Optionally schedule** recurring runs after each deployment

---

## Normalized Test Report Schema

```json
{
  "testName": "User Registration Flow",
  "url": "https://your-app.com/signup",
  "passed": true,
  "duration": 4823,
  "steps": [
    { "step": "Page loaded",            "status": "PASS", "durationMs": 820 },
    { "step": "Form filled",            "status": "PASS", "durationMs": 310 },
    { "step": "Form submitted",         "status": "PASS", "durationMs": 2100 },
    { "step": "Redirected to dashboard","status": "PASS", "durationMs": 593 }
  ],
  "errors": [],
  "screenshotUrl": "https://api.apify.com/v2/key-value-stores/.../records/signup-success.png",
  "runAt": "2025-02-25T10:00:00Z"
}
```

---

## CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/qa.yml
name: Automated QA Tests

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run QA Tests via Apify
        run: |
          curl -X POST \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${{ secrets.APIFY_TOKEN }}" \
            -d '{"startUrls":[{"url":"${{ vars.STAGING_URL }}"}]}' \
            "https://api.apify.com/v2/acts/apify~puppeteer-scraper/runs"
```

---

## Best Practices

- Use **unique test emails** with `+timestamp` suffixes to avoid conflicts between runs
- Always take a **screenshot on failure** for instant visual debugging
- Set `timeout` on every `waitForSelector` — never let a test hang indefinitely
- Use **`waitForNavigation`** after any click that triggers a page load
- Test both the **happy path** and **edge cases** (empty fields, wrong passwords, network slow)
- Store all test artifacts (screenshots, reports) in **Apify Key-Value Store** for later review
- Integrate with **Slack or email webhooks** to get instant failure notifications

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/puppeteer-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token — check credentials");
  if (error.statusCode === 429) throw new Error("Rate limit hit — reduce parallel test runs");
  if (error.message.includes("timeout")) throw new Error("Test timed out — check if the app is reachable");
  throw error;
}
```

---

## Requirements

- An Apify account → https://www.apify.com/?fpr=dx06p
- A valid **Personal API Token** from Settings → Integrations
- Node.js 18+ for `apify-client`
- A staging or production URL to test against
- Optional: CI/CD pipeline (GitHub Actions, GitLab CI) for post-deployment triggering
