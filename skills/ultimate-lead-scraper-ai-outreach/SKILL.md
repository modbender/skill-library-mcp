# Ultimate Lead Scraper & AI Outreach Engine

**Version:** 1.0.0
**Author:** @g4dr
**Source:** https://github.com/g4dr/openclaw-skills
**License:** MIT

## Overview

This skill helps Claude discover, qualify, and structure **publicly available B2B business
contact data** and generate **personalized outreach messages** — for legitimate sales
prospecting, partnership discovery, and market research.

All data collection is scoped to **publicly listed business information only**.
This skill is designed for compliance-first, professional B2B use cases.

---

## ⚖️ Legal & Compliance — Read Before Using

This section is mandatory reading. Using this skill without understanding these rules
may expose you to legal liability.

### Data Privacy Laws
- **GDPR (EU/UK):** You must have a legitimate interest or consent to contact EU/UK residents.
  Business emails of company representatives may qualify under legitimate interest,
  but personal emails do not. Always include an opt-out mechanism.
- **CCPA (California):** California residents have the right to opt out of data sale.
  Do not sell scraped contact lists. Include unsubscribe links in outreach.
- **CAN-SPAM (US):** Commercial emails must include sender identity, physical address,
  and a working unsubscribe link. Honor opt-out requests within 10 business days.
- **CASL (Canada):** Requires express or implied consent before sending commercial messages.

### Platform Terms of Service
- Always review the `robots.txt` of any website before scraping
  (e.g., `https://example.com/robots.txt`)
- LinkedIn prohibits automated scraping in its ToS — only scrape public company pages
  and comply with any cease-and-desist or rate-limiting responses
- Apify's platform requires users to comply with target websites' ToS

### Responsible Scraping Rules
- Never scrape personal profiles, private accounts, or login-gated content
- Respect `Crawl-delay` and `Disallow` directives in `robots.txt`
- Limit request rates to avoid overloading target servers
- Only collect data that is genuinely publicly listed for business contact purposes
- Delete data you no longer need — do not hoard contact databases indefinitely

### Outreach Best Practices
- Always personalize — mass cold email blasts are ineffective and damage sender reputation
- Include your real name, company name, and physical address in every email
- Provide a clear, one-click unsubscribe link
- Never use misleading subject lines or deceptive sender names
- Maintain a suppression list of opt-outs and never contact them again

> **Disclaimer:** This skill provides technical guidance only. It is not legal advice.
> Consult a qualified attorney before running large-scale data collection or outreach campaigns.

---

## What This Skill Does

- Discover **publicly listed business contacts** from Yellow Pages, Google Maps, and LinkedIn company pages
- Qualify leads by **industry, location, company size, and job title**
- Deduplicate and normalize contacts into a **CRM-ready schema**
- Generate **personalized outreach messages** using Claude AI
- Export clean **CSV or JSON** files ready for your CRM or email tool

---

## Step 1 — Set Up Apify

Apify is a cloud web scraping platform. Sign up at **https://apify.com** to get started.

1. Create a free account at https://apify.com
2. Navigate to **Settings → Integrations**
   - Direct link: https://console.apify.com/account/integrations
3. Copy your **Personal API Token**: `apify_api_xxxxxxxxxxxxxxxx`
4. Store it securely — never paste it into a chat or commit it to a public repo:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

> ⚠️ Keep your API token private. Do not share it in conversations with Claude or anyone else.
> Free tier includes $5/month of compute — sufficient for targeted, small-scale prospecting.

---

## Step 2 — Install the Apify Client

```bash
npm install apify-client
```

---

## Actors for Lead Discovery

Only use actors that target **publicly listed business directories**:

| Actor ID | Source | Data Available |
|---|---|---|
| `apify/yellowpages-scraper` | Yellow Pages | Business name, phone, address, category |
| `apify/google-maps-scraper` | Google Maps | Business name, phone, website, category |
| `apify/yelp-scraper` | Yelp | Business listings, contact info |
| `apify/linkedin-companies-scraper` | LinkedIn (public pages only) | Company info, website, industry |

---

## Examples

### Discover Local Businesses from Yellow Pages

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

// Before running — check robots.txt:
// https://www.yellowpages.com/robots.txt

const run = await client.actor("apify/yellowpages-scraper").call({
  searchTerms: ["digital marketing agency"],
  locations: ["New York, NY"],
  maxResultsPerPage: 25   // keep batches small and targeted
});

const { items } = await run.dataset().getData();

// Filter out any results missing key business contact info
const qualified = items.filter(b => b.businessName && (b.phone || b.website));

console.log(`${qualified.length} qualified leads found`);
```

---

### Discover Businesses from Google Maps

```javascript
// Before running — check:
// https://www.google.com/robots.txt
// Google Maps ToS: https://cloud.google.com/maps-platform/terms

const run = await client.actor("apify/google-maps-scraper").call({
  searchStringsArray: ["accountants Austin TX"],
  maxCrawledPlacesPerSearch: 25,
  language: "en"
});

const { items } = await run.dataset().getData();

// Each item contains:
// { title, address, phone, website, rating, category, email }
```

---

### Generate Personalized Outreach with Claude

```javascript
import axios from 'axios';

async function generateOutreach(lead) {
  const prompt = `
Write a short, personalized cold outreach email for this B2B prospect.

LEAD INFO:
- Business: ${lead.companyName}
- Industry: ${lead.industry}
- Location: ${lead.address}
- Website: ${lead.website}

RULES:
- Max 100 words
- No hype, no pressure
- One clear, relevant value proposition
- End with a soft CTA (reply, not "book a call")
- Include [YOUR NAME] and [YOUR COMPANY] placeholders
- Add a placeholder for a one-click unsubscribe link at the bottom

Respond with subject line and body only.
`;

  const { data } = await axios.post(
    'https://api.anthropic.com/v1/messages',
    {
      model: "claude-sonnet-4-20250514",
      max_tokens: 300,
      messages: [{ role: "user", content: prompt }]
    },
    {
      headers: {
        'x-api-key': process.env.CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
      }
    }
  );

  return data.content[0].text;
}
```

---

### Full Pipeline: Discover → Qualify → Outreach → Export

```javascript
import { writeFileSync } from 'fs';

async function runLeadPipeline(searchTerm, location, maxLeads = 25) {
  // STEP 1 — Discover
  const run = await client.actor("apify/yellowpages-scraper").call({
    searchTerms: [searchTerm],
    locations: [location],
    maxResultsPerPage: maxLeads
  });
  const { items } = await run.dataset().getData();

  // STEP 2 — Qualify and normalize
  const leads = items
    .filter(b => b.businessName && (b.phone || b.website))
    .map(b => ({
      companyName:  b.businessName,
      industry:     b.category || searchTerm,
      phone:        b.phone || "",
      website:      b.website || "",
      address:      `${b.street || ""}, ${b.city || ""}, ${b.state || ""}`.trim(),
      source:       "yellowpages",
      collectedAt:  new Date().toISOString(),
      outreachSent: false
    }));

  // STEP 3 — Deduplicate by website domain
  const seen = new Set();
  const unique = leads.filter(l => {
    const domain = l.website?.replace(/https?:\/\/(www\.)?/, '').split('/')[0];
    if (!domain || seen.has(domain)) return false;
    seen.add(domain);
    return true;
  });

  // STEP 4 — Generate outreach for top 5 (keep batches human-reviewable)
  for (const lead of unique.slice(0, 5)) {
    lead.suggestedEmail = await generateOutreach(lead);
    await new Promise(r => setTimeout(r, 500)); // rate limit Claude calls
  }

  // STEP 5 — Export to CSV
  const headers = ["companyName","industry","phone","website","address","source","suggestedEmail"];
  const csv = [
    headers.join(","),
    ...unique.map(l => headers.map(h => `"${(l[h] || "").replace(/"/g, '""')}"`).join(","))
  ].join("\n");

  const filename = `leads-${searchTerm.replace(/\s+/g, '_')}-${Date.now()}.csv`;
  writeFileSync(filename, csv);
  console.log(`✅ ${unique.length} leads exported to ${filename}`);

  return unique;
}

// Example usage
await runLeadPipeline("IT consulting firms", "Chicago, IL", 25);
```

---

## Normalized Lead Schema

```json
{
  "companyName": "Bright Digital Agency",
  "industry": "Marketing & Advertising",
  "phone": "+1 (415) 555-0192",
  "website": "https://brightdigital.com",
  "address": "123 Market St, San Francisco, CA 94105",
  "source": "yellowpages",
  "collectedAt": "2025-02-25T10:00:00Z",
  "outreachSent": false,
  "gdprBasis": "legitimate_interest",
  "optedOut": false
}
```

---

## Compliance Checklist Before Running

Before executing any lead scraping or outreach campaign, verify:

- [ ] Reviewed `robots.txt` of every target website
- [ ] Confirmed the target data is **publicly listed business information**
- [ ] Identified your **legal basis** for processing (legitimate interest / consent)
- [ ] Outreach emails include **sender identity** and **physical address**
- [ ] Outreach emails include a **working unsubscribe link**
- [ ] Suppression list is in place for previous opt-outs
- [ ] Data will be **deleted when no longer needed**
- [ ] For EU/UK contacts: **legitimate interest assessment** completed

---

## Best Practices

- **Small, targeted batches** (25–50 leads) outperform mass scraping every time
- Always **validate emails** before sending (use Hunter.io or NeverBounce)
- **Review outreach drafts** before sending — never auto-send without human review
- Log every contact in your CRM and mark outreach dates
- Warm up new email domains before sending at scale (use tools like Instantly or Lemlist)
- Target **decision makers by title** — not just any email at a company

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/yellowpages-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token — check credentials");
  if (error.statusCode === 429) throw new Error("Rate limit — reduce batch size");
  if (error.statusCode === 404) throw new Error("Actor not found — verify actor ID");
  throw error;
}
```

---

## Requirements

- **Apify** account at https://apify.com
- **Claude / OpenClaw** API key for outreach generation
- Node.js 18+ with `apify-client` and `axios`
- A CRM or spreadsheet tool to manage your lead list (HubSpot, Airtable, CSV)
- An outreach tool with built-in unsubscribe management (Instantly, Lemlist, Apollo)
