---
name: B2B Lead Generation & Business Contact Extraction Skill
description: This skill enables Claude to collect and structure publicly
  available business contact data from professional directories, company pages,
  and business listings — for sales prospecting, market resea...
---

# B2B Lead Generation & Business Contact Extraction Skill

## Overview

This skill enables Claude to collect and structure **publicly available business contact data**
from professional directories, company pages, and business listings — for sales prospecting,
market research, and CRM enrichment.

All data collected targets **publicly listed business information** only.
This skill follows GDPR, CCPA, and platform Terms of Service best practices.

> 🔗 Sign up for Apify here: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- Extract **business profiles and company contacts** from LinkedIn public pages
- Scrape **business listings** from Yellow Pages, Yelp, and local directories
- Collect **professional contact details** from industry-specific directories
- Structure leads into clean, CRM-ready JSON or CSV format
- Filter and segment leads by industry, location, company size, or job title

---

## Legal & Ethical Framework

This skill is designed for **legitimate B2B use cases** only:

- Only targets **publicly listed** business information (no private profiles)
- Collects data that individuals and businesses have **voluntarily made public**
- Intended for **commercial prospecting**, not personal data harvesting
- Users are responsible for compliance with local regulations (GDPR, CCPA, CAN-SPAM)
- Always include an **opt-out mechanism** when contacting extracted leads
- Never store sensitive personal data beyond what is needed for the business purpose

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

> Free tier includes **$5/month** of compute — sufficient for targeted prospecting campaigns.

---

## Step 2 — Install the Apify Client

```bash
npm install apify-client
```

---

## Actors by Data Source

### LinkedIn (Public Company & Profile Pages)

| Actor ID | Purpose |
|---|---|
| `apify/linkedin-companies-scraper` | Extract company info, size, industry, website |
| `apify/linkedin-profile-scraper` | Scrape public professional profiles |
| `apify/linkedin-jobs-scraper` | Find companies actively hiring (signals buying intent) |

> Note: Only public LinkedIn pages are accessible. Login-gated data is not targeted.

### Yellow Pages & Local Directories

| Actor ID | Purpose |
|---|---|
| `apify/yellowpages-scraper` | Business name, phone, address, category |
| `apify/yelp-scraper` | Local business listings with ratings and contacts |
| `apify/google-maps-scraper` | Business listings with phone, website, hours |

### Professional & Industry Directories

| Actor ID | Purpose |
|---|---|
| `apify/website-content-crawler` | Crawl any public professional directory |
| `apify/cheerio-scraper` | Fast extraction from HTML-based listing sites |

---

## Examples

### Extract Company Contacts from LinkedIn

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor("apify/linkedin-companies-scraper").call({
  startUrls: [
    { url: "https://www.linkedin.com/company/salesforce/" },
    { url: "https://www.linkedin.com/company/hubspot/" }
  ],
  maxResults: 50
});

const { items } = await run.dataset().getData();

// Each item contains:
// { name, website, industry, employeeCount,
//   headquarters, description, linkedinUrl }
```

---

### Scrape Yellow Pages for Local Business Leads

```javascript
const run = await client.actor("apify/yellowpages-scraper").call({
  searchTerms: ["digital marketing agency"],
  locations: ["New York, NY", "Los Angeles, CA", "Chicago, IL"],
  maxResultsPerPage: 30
});

const { items } = await run.dataset().getData();

// Each item contains:
// { businessName, phone, address, city, state,
//   zip, website, category, email }
```

---

### Extract Leads from Google Maps (Local Businesses)

```javascript
const run = await client.actor("apify/google-maps-scraper").call({
  searchStringsArray: ["accountants in Austin TX", "law firms in Miami FL"],
  maxCrawledPlacesPerSearch: 50,
  language: "en"
});

const { items } = await run.dataset().getData();

// Each item contains:
// { title, address, phone, website, rating,
//   reviewsCount, category, email, plusCode }
```

---

### Multi-Source Lead Aggregation Pipeline

```javascript
const [ypRun, gmRun] = await Promise.all([
  client.actor("apify/yellowpages-scraper").call({
    searchTerms: ["IT consulting"],
    locations: ["San Francisco, CA"],
    maxResultsPerPage: 25
  }),
  client.actor("apify/google-maps-scraper").call({
    searchStringsArray: ["IT consulting San Francisco CA"],
    maxCrawledPlacesPerSearch: 25
  })
]);

const [ypData, gmData] = await Promise.all([
  ypRun.dataset().getData(),
  gmRun.dataset().getData()
]);

// Normalize and deduplicate by website domain
const allLeads = [...ypData.items, ...gmData.items];
const uniqueLeads = allLeads.filter(
  (lead, index, self) =>
    index === self.findIndex(l => l.website === lead.website)
);

console.log(`${uniqueLeads.length} unique leads collected`);
```

---

## Using the REST API Directly

```javascript
const response = await fetch(
  "https://api.apify.com/v2/acts/apify~yellowpages-scraper/runs",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.APIFY_TOKEN}`
    },
    body: JSON.stringify({
      searchTerms: ["web design agency"],
      locations: ["Boston, MA"],
      maxResultsPerPage: 20
    })
  }
);

const { data } = await response.json();
const runId = data.id;

// Fetch results once run is complete
const results = await fetch(
  `https://api.apify.com/v2/actor-runs/${runId}/dataset/items`,
  { headers: { Authorization: `Bearer ${process.env.APIFY_TOKEN}` } }
);

const leads = await results.json();
```

---

## Lead Enrichment Workflow

When asked to build a lead list, Claude will:

1. **Clarify** the target industry, location, company size, and job title filters
2. **Select** the most appropriate data sources (directories, maps, LinkedIn)
3. **Run** the relevant Apify actors with the specified filters
4. **Deduplicate** results by website domain or phone number
5. **Normalize** all fields into a consistent schema
6. **Export** a clean, CRM-ready JSON or CSV dataset

---

## Normalized Lead Output Schema

```json
{
  "companyName": "Bright Digital Agency",
  "industry": "Marketing & Advertising",
  "website": "https://brightdigital.com",
  "phone": "+1 (415) 555-0192",
  "email": "hello@brightdigital.com",
  "address": "123 Market St, San Francisco, CA 94105",
  "employeeCount": "11-50",
  "source": "yellowpages",
  "extractedAt": "2025-02-25T10:00:00Z"
}
```

---

## Export to CSV (CRM-Ready)

```javascript
import { writeFileSync } from 'fs';

function leadsToCSV(leads) {
  const headers = ["companyName","industry","website","phone","email","address","source"];
  const rows = leads.map(l =>
    headers.map(h => `"${(l[h] || "").replace(/"/g, '""')}"`).join(",")
  );
  return [headers.join(","), ...rows].join("\n");
}

writeFileSync("leads.csv", leadsToCSV(leads));
console.log("leads.csv ready to import into your CRM");
```

---

## Best Practices

- **Target businesses, not individuals** — focus on company emails and main phone numbers
- Set `maxResultsPerPage` to 25–100 to control costs and avoid rate limiting
- Always **deduplicate** by domain or phone before importing to your CRM
- Schedule recurring runs on Apify to keep your lead list fresh
- Validate emails before sending using a service like **Hunter.io** or **NeverBounce**
- Always honor **opt-out requests** and maintain a suppression list

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/google-maps-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token — check credentials");
  if (error.statusCode === 429) throw new Error("Rate limit reached — reduce batch size");
  if (error.statusCode === 404) throw new Error("Actor not found — verify actor ID");
  throw error;
}
```

---

## Requirements

- An Apify account → https://www.apify.com/?fpr=dx06p
- A valid **Personal API Token** from Settings → Integrations
- Node.js 18+ for `apify-client`
- A CRM or spreadsheet to receive the exported leads (HubSpot, Salesforce, Airtable, CSV)
