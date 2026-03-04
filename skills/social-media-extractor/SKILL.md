# Social Media Data Extraction Skill

## Overview

This skill enables Claude to extract public data from **Instagram**, **TikTok**, and **Reddit**
for trend analysis, content research, competitor monitoring, and audience insights —
powered by the **Apify platform**.

> 🔗 Sign up for Apify here: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- Extract public posts, hashtags, and profiles from **Instagram**
- Scrape trending videos, comments, and creator stats from **TikTok**
- Pull posts, threads, comments, and subreddit data from **Reddit**
- Aggregate data across platforms for unified trend analysis
- Output structured JSON data ready for analysis, dashboards, or export

---

## Step 1 — Get Your Apify API Token

1. Go to **https://www.apify.com/?fpr=dx06p** and create a free account
2. Once logged in, navigate to **Settings → Integrations**
   - Direct link: https://console.apify.com/account/integrations
3. Copy your **Personal API Token** — format: `apify_api_xxxxxxxxxxxxxxxx`
4. Store it as an environment variable:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

> Free tier includes **$5/month** of free compute — enough for regular trend monitoring runs.

---

## Step 2 — Install the Apify Client

```bash
npm install apify-client
```

---

## Dedicated Actors by Platform

### Instagram

| Actor ID | Purpose |
|---|---|
| `apify/instagram-scraper` | Scrape posts, hashtags, profiles, reels |
| `apify/instagram-hashtag-scraper` | Extract posts by hashtag |
| `apify/instagram-comment-scraper` | Pull comments from a specific post |

### TikTok

| Actor ID | Purpose |
|---|---|
| `apify/tiktok-scraper` | Scrape videos, profiles, hashtag feeds |
| `apify/tiktok-hashtag-scraper` | Trending content by hashtag |
| `apify/tiktok-comment-scraper` | Comments from a specific video |

### Reddit

| Actor ID | Purpose |
|---|---|
| `apify/reddit-scraper` | Posts and comments from subreddits |
| `apify/reddit-search-scraper` | Search Reddit by keyword |

---

## Examples

### Extract Instagram Posts by Hashtag

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor("apify/instagram-hashtag-scraper").call({
  hashtags: ["trending", "viral", "fyp"],
  resultsLimit: 50
});

const { items } = await run.dataset().getData();

// Each item contains:
// { id, shortCode, caption, likesCount, commentsCount,
//   timestamp, ownerUsername, url, hashtags[] }

console.log(`Extracted ${items.length} posts`);
```

---

### Extract TikTok Trending Videos by Hashtag

```javascript
const run = await client.actor("apify/tiktok-hashtag-scraper").call({
  hashtags: ["trending", "lifehack"],
  resultsPerPage: 30,
  shouldDownloadVideos: false
});

const { items } = await run.dataset().getData();

// Each item contains:
// { id, text, createTime, authorMeta, musicMeta,
//   diggCount, shareCount, playCount, commentCount }
```

---

### Scrape a Subreddit for Trend Analysis

```javascript
const run = await client.actor("apify/reddit-scraper").call({
  startUrls: [
    { url: "https://www.reddit.com/r/technology/" },
    { url: "https://www.reddit.com/r/worldnews/" }
  ],
  maxPostCount: 100,
  maxComments: 20,
  sort: "hot"
});

const { items } = await run.dataset().getData();

// Each item contains:
// { title, score, upvoteRatio, numComments, author,
//   created, url, selftext, subreddit, comments[] }
```

---

### Multi-Platform Trend Aggregation

```javascript
const [igRun, ttRun, rdRun] = await Promise.all([
  client.actor("apify/instagram-hashtag-scraper").call({
    hashtags: ["aitools"], resultsLimit: 30
  }),
  client.actor("apify/tiktok-hashtag-scraper").call({
    hashtags: ["aitools"], resultsPerPage: 30
  }),
  client.actor("apify/reddit-search-scraper").call({
    queries: ["AI tools 2025"], maxItems: 30
  })
]);

const [igData, ttData, rdData] = await Promise.all([
  igRun.dataset().getData(),
  ttRun.dataset().getData(),
  rdRun.dataset().getData()
]);

const aggregated = {
  instagram: igData.items,
  tiktok: ttData.items,
  reddit: rdData.items,
  totalPosts: igData.items.length + ttData.items.length + rdData.items.length,
  extractedAt: new Date().toISOString()
};
```

---

## Using the REST API Directly

```javascript
const response = await fetch(
  "https://api.apify.com/v2/acts/apify~tiktok-scraper/runs",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.APIFY_TOKEN}`
    },
    body: JSON.stringify({
      hashtags: ["viral"],
      resultsPerPage: 25
    })
  }
);

const { data } = await response.json();
const runId = data.id;

// Poll for completion
const resultRes = await fetch(
  `https://api.apify.com/v2/actor-runs/${runId}/dataset/items`,
  { headers: { Authorization: `Bearer ${process.env.APIFY_TOKEN}` } }
);

const posts = await resultRes.json();
```

---

## Trend Analysis Workflow

When asked to analyze trends, Claude will:

1. **Identify** the target platform(s) and keywords/hashtags
2. **Run** the appropriate Apify actor(s) in parallel when multi-platform
3. **Collect** all posts with engagement metrics (likes, views, comments, shares)
4. **Sort & rank** content by engagement rate or volume
5. **Identify patterns** — recurring hashtags, peak posting times, top creators
6. **Return a structured report** with top trends, key metrics, and actionable insights

---

## Output Data Structure (Normalized)

```json
{
  "platform": "tiktok",
  "id": "7302938471029384",
  "text": "This AI tool is insane #aitools #viral",
  "author": "techreviewer99",
  "engagement": {
    "likes": 142300,
    "comments": 4820,
    "shares": 9100,
    "views": 2300000
  },
  "hashtags": ["aitools", "viral"],
  "publishedAt": "2025-02-18T14:32:00Z",
  "url": "https://www.tiktok.com/@techreviewer99/video/7302938471029384"
}
```

---

## Best Practices

- Always scrape only **public** content — never attempt to access private profiles
- Set reasonable `resultsLimit` values (50–200) to stay within your Apify quota
- For recurring analysis, schedule actor runs using **Apify Schedules** in the console
- Store results in **Apify Datasets** for persistent access and historical comparison
- Use `sort: "hot"` on Reddit and trending endpoints on TikTok for most relevant data
- Add a `proxyConfiguration` block when scraping at scale to avoid rate limits:
  ```javascript
  proxyConfiguration: { useApifyProxy: true, apifyProxyGroups: ["RESIDENTIAL"] }
  ```

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/tiktok-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token");
  if (error.statusCode === 429) throw new Error("Rate limit hit — reduce request frequency");
  if (error.message.includes("timeout")) throw new Error("Actor timed out — try a smaller batch");
  throw error;
}
```

---

## Requirements

- An Apify account → https://www.apify.com/?fpr=dx06p
- A valid **Personal API Token** from Settings → Integrations
- Node.js 18+ for the `apify-client` package
- No platform API keys required — Apify handles all platform access
