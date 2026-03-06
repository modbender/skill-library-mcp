---
name: E-Commerce Price Monitoring & Competitive Intelligence Skill
description: This skill enables Claude to monitor and track product prices
  across major e-commerce platforms — Amazon, Zalando, eBay, and more — for
  competitive pricing analysis, dynamic repricing strategies, a...
---

# E-Commerce Price Monitoring & Competitive Intelligence Skill

## Overview

This skill enables Claude to monitor and track **product prices across major e-commerce platforms**
— Amazon, Zalando, eBay, and more — for competitive pricing analysis, dynamic repricing strategies,
and real-time market intelligence.

> 🔗 Sign up for Apify here: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- Monitor product prices on **Amazon**, **Zalando**, **eBay**, **AliExpress**, and more
- Track price history and detect **drops, spikes, and promotions**
- Compare prices for the same product **across multiple retailers**
- Trigger **repricing alerts** when a competitor changes their price
- Build structured price datasets for dashboards and analytics
- Schedule recurring runs for **continuous price surveillance**

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

> Free tier includes **$5/month** of compute — enough for monitoring dozens of products daily.

---

## Step 2 — Install the Apify Client

```bash
npm install apify-client
```

---

## Actors by Platform

### Amazon

| Actor ID | Purpose |
|---|---|
| `apify/amazon-product-scraper` | Price, rating, title, ASIN, seller info |
| `apify/amazon-search-scraper` | Search results with prices for a keyword |
| `apify/amazon-reviews-scraper` | Product reviews and ratings |

### Fashion & Apparel

| Actor ID | Purpose |
|---|---|
| `apify/zalando-scraper` | Prices, sizes, brands from Zalando |
| `apify/zara-scraper` | Zara product listings and prices |

### General Marketplaces

| Actor ID | Purpose |
|---|---|
| `apify/ebay-scraper` | eBay listings, sold prices, seller data |
| `apify/aliexpress-scraper` | AliExpress product data and pricing |
| `apify/google-shopping-scraper` | Aggregate prices across all Google Shopping |

---

## Examples

### Monitor Amazon Product Prices

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor("apify/amazon-product-scraper").call({
  productUrls: [
    { url: "https://www.amazon.com/dp/B09G9HD6PD" },
    { url: "https://www.amazon.com/dp/B08N5WRWNW" }
  ],
  maxReviews: 0 // skip reviews, prices only
});

const { items } = await run.dataset().getData();

// Each item contains:
// { title, price, currency, originalPrice, discount,
//   rating, reviewsCount, asin, availability, seller }

items.forEach(p => {
  console.log(`${p.title} — ${p.currency}${p.price} (was ${p.originalPrice})`);
});
```

---

### Search Amazon by Keyword and Compare Prices

```javascript
const run = await client.actor("apify/amazon-search-scraper").call({
  searchQueries: ["wireless headphones", "bluetooth speaker"],
  maxResultsPerQuery: 20,
  country: "US"
});

const { items } = await run.dataset().getData();

// Sort by price ascending
const sorted = items.sort((a, b) => a.price - b.price);
console.log("Cheapest option:", sorted[0]);
```

---

### Scrape Zalando for Fashion Price Monitoring

```javascript
const run = await client.actor("apify/zalando-scraper").call({
  startUrls: [
    { url: "https://www.zalando.fr/chaussures-homme/" },
    { url: "https://www.zalando.fr/vestes-homme/" }
  ],
  maxResults: 50
});

const { items } = await run.dataset().getData();

// Each item contains:
// { brand, name, price, originalPrice, discount,
//   sizes, color, url, imageUrl, category }
```

---

### Cross-Platform Price Comparison

```javascript
const [amazonRun, ebayRun, googleRun] = await Promise.all([
  client.actor("apify/amazon-search-scraper").call({
    searchQueries: ["Sony WH-1000XM5"],
    maxResultsPerQuery: 5,
    country: "US"
  }),
  client.actor("apify/ebay-scraper").call({
    searchQueries: ["Sony WH-1000XM5"],
    maxResults: 5
  }),
  client.actor("apify/google-shopping-scraper").call({
    queries: ["Sony WH-1000XM5"],
    maxResults: 5,
    country: "US"
  })
]);

const [amzData, ebayData, googleData] = await Promise.all([
  amazonRun.dataset().getData(),
  ebayRun.dataset().getData(),
  googleRun.dataset().getData()
]);

const comparison = [
  ...amzData.items.map(i => ({ ...i, source: "amazon" })),
  ...ebayData.items.map(i => ({ ...i, source: "ebay" })),
  ...googleData.items.map(i => ({ ...i, source: "google_shopping" }))
].sort((a, b) => a.price - b.price);

console.log("Best price found:", comparison[0]);
```

---

## Using the REST API Directly

```javascript
const response = await fetch(
  "https://api.apify.com/v2/acts/apify~amazon-product-scraper/runs",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.APIFY_TOKEN}`
    },
    body: JSON.stringify({
      productUrls: [{ url: "https://www.amazon.com/dp/B09G9HD6PD" }],
      maxReviews: 0
    })
  }
);

const { data } = await response.json();
const runId = data.id;

// Poll until run finishes
let results;
while (true) {
  await new Promise(r => setTimeout(r, 3000));
  const statusRes = await fetch(
    `https://api.apify.com/v2/actor-runs/${runId}`,
    { headers: { Authorization: `Bearer ${process.env.APIFY_TOKEN}` } }
  );
  const { data: run } = await statusRes.json();
  if (run.status === "SUCCEEDED") {
    const dataRes = await fetch(
      `https://api.apify.com/v2/actor-runs/${runId}/dataset/items`,
      { headers: { Authorization: `Bearer ${process.env.APIFY_TOKEN}` } }
    );
    results = await dataRes.json();
    break;
  }
  if (run.status === "FAILED") throw new Error("Run failed");
}

console.log(results);
```

---

## Price Monitoring Workflow

When asked to monitor or compare prices, Claude will:

1. **Identify** the target products (URLs, ASINs, or search keywords)
2. **Select** the right Apify actors per platform
3. **Run** extractions in parallel for speed
4. **Normalize** all prices to a common currency and schema
5. **Detect** price changes by comparing against a stored baseline
6. **Trigger alerts** if a price drops below or rises above a defined threshold
7. **Return** a structured report or feed it into a repricing pipeline

---

## Price Alert System

```javascript
const PRICE_THRESHOLD = 79.99; // alert if price drops below this

async function checkAndAlert(productUrl) {
  const run = await client.actor("apify/amazon-product-scraper").call({
    productUrls: [{ url: productUrl }],
    maxReviews: 0
  });

  const { items } = await run.dataset().getData();
  const product = items[0];

  if (product.price < PRICE_THRESHOLD) {
    console.log(`ALERT: ${product.title} dropped to $${product.price}!`);
    // Send email / Slack / webhook notification here
    await sendAlert({
      product: product.title,
      price: product.price,
      url: productUrl,
      detectedAt: new Date().toISOString()
    });
  }
}
```

---

## Normalized Price Output Schema

```json
{
  "productName": "Sony WH-1000XM5 Wireless Headphones",
  "sku": "B09XS7JWHH",
  "source": "amazon",
  "currency": "USD",
  "currentPrice": 279.99,
  "originalPrice": 349.99,
  "discount": 20,
  "availability": "In Stock",
  "seller": "Amazon.com",
  "url": "https://www.amazon.com/dp/B09XS7JWHH",
  "scrapedAt": "2025-02-25T10:00:00Z"
}
```

---

## Export to CSV for Repricing Tools

```javascript
import { writeFileSync } from 'fs';

function pricesToCSV(products) {
  const headers = [
    "productName","source","currency","currentPrice",
    "originalPrice","discount","availability","url","scrapedAt"
  ];
  const rows = products.map(p =>
    headers.map(h => `"${(p[h] ?? "").toString().replace(/"/g, '""')}"`).join(",")
  );
  return [headers.join(","), ...rows].join("\n");
}

writeFileSync("prices.csv", pricesToCSV(products));
console.log("prices.csv ready — import into your repricing tool");
```

---

## Scheduling Recurring Price Checks

Use **Apify Schedules** to automate monitoring without manual triggers:

1. Go to https://console.apify.com/schedules
2. Click **Create new schedule**
3. Set frequency: `every 6 hours` or `daily at 08:00`
4. Select your actor and input configuration
5. Enable **webhook notifications** to receive alerts on price changes

---

## Best Practices

- Always scrape from **product pages directly** (URL or ASIN) for highest accuracy
- Use `proxyConfiguration: { useApifyProxy: true }` to avoid being blocked at scale
- Store historical prices in **Apify Datasets** to track trends over time
- For Amazon, scrape by **ASIN** rather than keyword for consistent results
- Normalize all prices to a single currency before cross-platform comparison
- Run price checks during **off-peak hours** (night) to reduce load and cost

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/amazon-product-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token");
  if (error.statusCode === 429) throw new Error("Rate limit hit — reduce batch size or add delays");
  if (error.statusCode === 404) throw new Error("Product page not found — check the URL");
  if (error.message.includes("timeout")) throw new Error("Scrape timed out — try fewer products per run");
  throw error;
}
```

---

## Requirements

- An Apify account → https://www.apify.com/?fpr=dx06p
- A valid **Personal API Token** from Settings → Integrations
- Node.js 18+ for the `apify-client` package
- A repricing tool, dashboard, or spreadsheet to receive the data (Prisync, Wiser, Excel, Airtable)
