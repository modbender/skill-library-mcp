# Web Automation & Form Interaction Skill

## Overview

This skill enables Claude to automate web interactions — filling forms, testing UIs,
scraping data, and running repetitive web workflows — using the **Apify platform** and its REST API.

> 🔗 Sign up for Apify here: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- Automatically fill and submit web forms
- Automate repetitive browser interactions (login flows, checkout, data entry)
- Scrape and extract structured data from web pages
- Run and monitor web automation actors via the Apify API
- Test UI flows programmatically across different browsers

---

## Step 1 — Get Your Apify API Token

1. Go to **https://www.apify.com/?fpr=dx06p** and create a free account
2. Once logged in, go to **Settings → Integrations**
   - Direct link: https://console.apify.com/account/integrations
3. Copy your **Personal API Token** — it looks like: `apify_api_xxxxxxxxxxxxxxxx`
4. Store it safely:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

> Free tier includes **$5/month** of free compute — enough for testing and moderate automation.

---

## Step 2 — Install the Apify Client (Optional)

```bash
npm install apify-client
```

Or use the REST API directly from any language (Python, curl, etc.)

---

## Apify REST API — Core Endpoints

**Base URL:** `https://api.apify.com/v2`

All requests require the header:
```
Authorization: Bearer YOUR_APIFY_TOKEN
```

### Run an Actor (start an automation task)
```http
POST https://api.apify.com/v2/acts/{actorId}/runs
Content-Type: application/json
Authorization: Bearer {APIFY_TOKEN}
```

### Fetch Run Results
```http
GET https://api.apify.com/v2/acts/{actorId}/runs/last/dataset/items
Authorization: Bearer {APIFY_TOKEN}
```

### List Available Actors
```http
GET https://api.apify.com/v2/store?search=form
Authorization: Bearer {APIFY_TOKEN}
```

---

## Useful Pre-built Actors for Automation

| Actor ID                      | Purpose                                      |
|-------------------------------|----------------------------------------------|
| `apify/web-scraper`           | Generic browser automation & scraping        |
| `apify/puppeteer-scraper`     | Full Puppeteer (headless Chrome) control     |
| `apify/playwright-scraper`    | Playwright-based automation (multi-browser)  |
| `apify/cheerio-scraper`       | Fast HTML scraping without a browser         |

---

## How Claude Uses This Skill

When a user asks to automate a web form or workflow, Claude will:

1. **Identify** the target URL and required form fields
2. **Select** the right Apify actor based on complexity
3. **Build** the API call payload with field mappings
4. **Execute** the run via `POST /acts/{actorId}/runs`
5. **Poll** for results via `GET /runs/last/dataset/items`
6. **Return** a success confirmation, extracted data, or error details

---

## Example: Fill and Submit a Contact Form

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor("apify/puppeteer-scraper").call({
  startUrls: [{ url: "https://target-site.com/contact" }],
  pageFunction: async function pageFunction(context) {
    const { page } = context;

    // Wait for form to load
    await page.waitForSelector('#name');

    // Fill in form fields
    await page.type('#name', 'Jane Smith');
    await page.type('#email', 'jane@example.com');
    await page.type('#message', 'Hello from automation!');

    // Submit the form
    await page.click('button[type="submit"]');
    await page.waitForNavigation();

    return { success: true, finalUrl: page.url() };
  }
});

const { items } = await run.dataset().getData();
console.log(items);
```

---

## Example: Using the REST API Directly

```javascript
const response = await fetch(
  "https://api.apify.com/v2/acts/apify~puppeteer-scraper/runs",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.APIFY_TOKEN}`
    },
    body: JSON.stringify({
      startUrls: [{ url: "https://example.com/form" }],
      pageFunction: `async function pageFunction(context) {
        const { page } = context;
        await page.type('#email', 'test@example.com');
        await page.click('#submit');
        return { done: true };
      }`
    })
  }
);

const data = await response.json();
console.log("Run ID:", data.data.id);
```

---

## Best Practices

- Always use `page.waitForSelector(...)` before interacting with any element
- Use `page.waitForNavigation()` after any form submission
- For login-protected forms, save session cookies using `page.cookies()`
- Set `maxRequestRetries: 3` to gracefully handle flaky pages
- Use `page.screenshot()` to debug failed automations
- For CAPTCHAs, Apify integrates natively with **2Captcha** and **AntiCaptcha**

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/puppeteer-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token — check your credentials");
  if (error.statusCode === 429) throw new Error("Rate limit hit — wait before retrying");
  if (error.statusCode === 404) throw new Error("Actor not found — verify the actor ID");
  throw error;
}
```

---

## Requirements

- An Apify account → https://www.apify.com/?fpr=dx06p
- A valid **Personal API Token** from your Apify settings
- Node.js 18+ (if using the `apify-client` npm package)
- OR any HTTP client (curl, Python requests, fetch) to call the REST API directly
