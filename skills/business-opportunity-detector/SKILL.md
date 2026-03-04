# Hidden Business Opportunity Detector Skill

## Overview

This skill builds an **automated business intelligence engine** that:
1. **Apify** scrapes App Store reviews, Amazon reviews, Reddit, niche forums, and Product Hunt
2. **Claude (OpenClaw)** deep-analyzes the raw frustrations, recurring requests, and unmet needs
3. Produces a structured **market gap report** with validated SaaS ideas, scored by opportunity size

This is how the best indie hackers and founders find their next product — systematically.

> 🔗 Apify: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- Scrape **App Store & Google Play** reviews to find what users hate about existing apps
- Scrape **Amazon reviews** (1–2 stars) to extract product frustrations at scale
- Mine **Reddit** niche communities for recurring complaints and feature requests
- Crawl **niche forums and communities** for unmet needs
- Scrape **Product Hunt** for emerging tools and gaps in the market
- Feed all raw data into **Claude** for structured opportunity analysis
- Output a **ranked list of business opportunities** with validation signals
- Generate **SaaS idea briefs** with positioning, features, and GTM angle

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│           HIDDEN BUSINESS OPPORTUNITY DETECTOR                  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LAYER 1 — DATA MINING (Apify)                          │   │
│  │  App Store │ Google Play │ Amazon │ Reddit │ Forums      │   │
│  │  Product Hunt │ G2 │ Trustpilot │ Indie Hackers          │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  LAYER 2 — OPPORTUNITY ANALYSIS ENGINE (Claude)         │   │
│  │                                                         │   │
│  │  • Frustration Extractor  → what people hate/struggle   │   │
│  │  • Pattern Detector       → recurring complaints        │   │
│  │  • Gap Analyzer           → what nobody is building     │   │
│  │  • Opportunity Scorer     → market size x pain level    │   │
│  │  • SaaS Idea Generator    → concrete product briefs     │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  LAYER 3 — OPPORTUNITY REPORT                           │   │
│  │  Ranked ideas │ Validation signals │ GTM angles          │   │
│  │  JSON export │ Markdown report │ Notion / Slack push     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1 — Get Your API Keys

### Apify
1. Sign up at **https://www.apify.com/?fpr=dx06p**
2. Go to **Settings → Integrations**
3. Copy your token:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

### Claude / OpenClaw
```bash
export CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

---

## Step 2 — Install Dependencies

```bash
npm install apify-client axios node-cron dotenv fs-extra
```

---

## Layer 1 — Multi-Source Data Miner (Apify)

### Mine App Store & Google Play Reviews

```javascript
import ApifyClient from 'apify-client';

const apify = new ApifyClient({ token: process.env.APIFY_TOKEN });

// Define the niche and competitor apps to analyze
const TARGET_NICHE = "project management";
const COMPETITOR_APPS = [
  { name: "Notion",   appStoreId: "1232780281", playStoreId: "notion.id" },
  { name: "Asana",    appStoreId: "489969512",  playStoreId: "com.asana.app" },
  { name: "Trello",   appStoreId: "461504587",  playStoreId: "com.trello" },
  { name: "Monday",   appStoreId: "1298450011", playStoreId: "com.monday.monday" }
];

async function scrapeAppReviews() {
  console.log("📱 Scraping App Store & Play Store reviews...");

  const jobs = COMPETITOR_APPS.map(app =>
    Promise.all([

      // App Store — focus on 1-3 star reviews (the gold mine)
      apify.actor("apify/apple-app-store-scraper").call({
        appIds: [app.appStoreId],
        maxReviews: 100,
        filterStars: [1, 2, 3]
      }).then(run => run.dataset().getData())
        .then(d => d.items.map(r => ({
          source: "app_store",
          appName: app.name,
          rating: r.rating,
          review: r.review,
          title: r.title,
          date: r.date,
          country: r.country
        }))),

      // Google Play Store
      apify.actor("apify/google-play-scraper").call({
        appId: app.playStoreId,
        maxReviews: 100,
        filterScore: [1, 2, 3]
      }).then(run => run.dataset().getData())
        .then(d => d.items.map(r => ({
          source: "google_play",
          appName: app.name,
          rating: r.score,
          review: r.text,
          title: r.title || "",
          date: r.date,
          thumbsUp: r.thumbsUp
        })))

    ]).then(results => results.flat())
  );

  const allReviews = await Promise.all(jobs);
  return allReviews.flat();
}
```

---

### Mine Amazon Reviews (1-3 Stars)

```javascript
async function scrapeAmazonReviews() {
  console.log("📦 Scraping Amazon negative reviews...");

  // Target products in your niche
  const TARGET_PRODUCTS = [
    "https://www.amazon.com/dp/B08N5WRWNW", // productivity tool example
    "https://www.amazon.com/dp/B09G9HD6PD"
  ];

  const jobs = TARGET_PRODUCTS.map(url =>
    apify.actor("apify/amazon-reviews-scraper").call({
      startUrls: [{ url }],
      maxReviews: 100,
      filterByStar: ["one_star", "two_star", "three_star"]
    }).then(run => run.dataset().getData())
      .then(d => d.items.map(r => ({
        source: "amazon",
        productTitle: r.productTitle,
        rating: r.ratingScore,
        review: r.reviewText,
        title: r.reviewTitle,
        date: r.date,
        helpfulVotes: r.helpfulVotes,
        verifiedPurchase: r.verifiedPurchase
      })))
  );

  const results = await Promise.all(jobs);
  return results.flat();
}
```

---

### Mine Reddit Niche Communities

```javascript
async function scrapeRedditFrustrations() {
  console.log("💬 Scraping Reddit communities...");

  const SUBREDDITS = [
    "r/Entrepreneur",
    "r/SaaS",
    "r/smallbusiness",
    "r/productivity",
    "r/projectmanagement",
    "r/startups",
    "r/indiehackers"
  ];

  const [posts, searchResults] = await Promise.all([

    // Hot/top posts in subreddits
    apify.actor("apify/reddit-scraper").call({
      startUrls: SUBREDDITS.map(s => ({ url: `https://www.reddit.com/${s}/` })),
      maxPostCount: 30,
      maxComments: 15,
      sort: "top"
    }).then(run => run.dataset().getData()),

    // Search for frustration signals
    apify.actor("apify/reddit-search-scraper").call({
      queries: [
        `${TARGET_NICHE} frustrated wish`,
        `${TARGET_NICHE} hate problem broken`,
        `${TARGET_NICHE} alternative looking for better`,
        `${TARGET_NICHE} feature request need`,
        `${TARGET_NICHE} why is there no tool`
      ],
      maxItems: 50
    }).then(run => run.dataset().getData())

  ]);

  return [
    ...posts.items.map(p => ({
      source: "reddit_post",
      subreddit: p.subreddit,
      title: p.title,
      text: p.selftext,
      score: p.score,
      comments: p.numComments,
      url: p.url
    })),
    ...searchResults.items.map(p => ({
      source: "reddit_search",
      subreddit: p.subreddit,
      title: p.title,
      text: p.selftext,
      score: p.score,
      url: p.url
    }))
  ];
}
```

---

### Mine Product Hunt & G2 Reviews

```javascript
async function scrapeProductIntelligence() {
  console.log("🚀 Scraping Product Hunt & review platforms...");

  const [productHunt, g2] = await Promise.all([

    // Product Hunt — see what's launching and what comments say
    apify.actor("apify/product-hunt-scraper").call({
      mode: "search",
      searchQuery: TARGET_NICHE,
      maxItems: 30
    }).then(run => run.dataset().getData())
      .then(d => d.items.map(p => ({
        source: "product_hunt",
        name: p.name,
        tagline: p.tagline,
        description: p.description,
        upvotes: p.votesCount,
        comments: p.commentsCount,
        topics: p.topics,
        url: p.url
      }))),

    // G2 reviews for competitor software
    apify.actor("apify/website-content-crawler").call({
      startUrls: [
        { url: `https://www.g2.com/categories/${TARGET_NICHE.replace(/\s+/g, '-')}-software` }
      ],
      maxCrawlingDepth: 1,
      maxRequestsPerCrawl: 10
    }).then(run => run.dataset().getData())
      .then(d => d.items.map(p => ({
        source: "g2",
        text: p.text?.slice(0, 2000),
        url: p.url
      })))

  ]);

  return [...productHunt, ...g2];
}
```

---

## Layer 2 — Opportunity Analysis Engine (Claude)

### Frustration Extractor

```javascript
import axios from 'axios';

const claude = axios.create({
  baseURL: 'https://api.anthropic.com/v1',
  headers: {
    'x-api-key': process.env.CLAUDE_API_KEY,
    'anthropic-version': '2023-06-01',
    'Content-Type': 'application/json'
  }
});

async function extractFrustrations(allData) {
  const prompt = `
You are a world-class product researcher and market analyst.

Analyze this raw data from app reviews, Amazon reviews, Reddit posts, and product listings.
Extract every customer frustration, unmet need, and recurring complaint.

NICHE: ${TARGET_NICHE}

RAW DATA (sample):
${JSON.stringify(allData.slice(0, 30), null, 2)}

Respond ONLY in this JSON format:
{
  "frustrations": [
    {
      "theme": "short label",
      "description": "what users are frustrated about",
      "frequency": "how often this comes up (high/medium/low)",
      "emotionalIntensity": "how angry/upset users are (1-10)",
      "affectedSegment": "who experiences this most",
      "evidenceQuotes": ["direct quote 1", "direct quote 2"],
      "sources": ["app_store", "reddit"]
    }
  ],
  "featureRequests": [
    {
      "request": "what users are explicitly asking for",
      "frequency": "high | medium | low",
      "currentWorkaround": "what users do today instead",
      "evidenceQuotes": ["quote"]
    }
  ],
  "recurringPatterns": [
    "pattern 1 observed across multiple sources",
    "pattern 2"
  ],
  "underservedSegments": [
    {
      "segment": "who is being ignored",
      "unmetNeed": "what they need",
      "currentSolution": "what they use today despite it being bad"
    }
  ]
}
`;

  const { data } = await claude.post('/messages', {
    model: "claude-opus-4-5",
    max_tokens: 3000,
    messages: [{ role: "user", content: prompt }]
  });

  return JSON.parse(data.content[0].text.replace(/```json|```/g, '').trim());
}
```

---

### Market Gap Analyzer & SaaS Idea Generator

```javascript
async function analyzeMarketGaps(frustrations, productIntel) {
  const prompt = `
You are a serial entrepreneur and SaaS product strategist.

Based on these validated customer frustrations and market intelligence, identify
the highest-potential business opportunities and generate concrete SaaS ideas.

FRUSTRATIONS & PATTERNS:
${JSON.stringify(frustrations, null, 2)}

MARKET INTELLIGENCE (existing products):
${JSON.stringify(productIntel.slice(0, 10), null, 2)}

Respond ONLY in this JSON format:
{
  "marketGaps": [
    {
      "gap": "what is clearly missing from the market",
      "evidenceStrength": "strong | moderate | weak",
      "estimatedMarketSize": "niche | small | medium | large",
      "competitionLevel": "none | low | medium | high",
      "urgency": "nice-to-have | important | critical"
    }
  ],
  "saasIdeas": [
    {
      "rank": 1,
      "name": "working product name",
      "oneLiner": "X for Y — one sentence pitch",
      "problem": "exact problem it solves",
      "targetCustomer": "specific ICP (ideal customer profile)",
      "coreFeatures": ["feature 1", "feature 2", "feature 3"],
      "differentiator": "why this beats existing solutions",
      "monetization": "pricing model (per seat | usage | freemium | etc)",
      "estimatedMRR": "rough MRR potential at 100 customers",
      "validationSignals": ["signal from data that confirms the need"],
      "gtmAngle": "how to acquire first 100 customers",
      "buildComplexity": "low | medium | high",
      "opportunityScore": 8,
      "risksAndChallenges": ["risk 1", "risk 2"]
    }
  ],
  "quickWins": [
    {
      "idea": "simplest possible version of a solution",
      "timeToMVP": "estimated days/weeks to build",
      "validationMethod": "how to validate before building"
    }
  ],
  "topRecommendation": "single best opportunity with 1-paragraph reasoning"
}
`;

  const { data } = await claude.post('/messages', {
    model: "claude-opus-4-5",
    max_tokens: 4000,
    messages: [{ role: "user", content: prompt }]
  });

  return JSON.parse(data.content[0].text.replace(/```json|```/g, '').trim());
}
```

---

### Validation Signal Scorer

```javascript
async function scoreOpportunities(ideas, rawData) {
  const prompt = `
Score each SaaS idea based on the evidence in the raw data.
Apply the Rob Walling (TinySeed) and Paul Graham opportunity frameworks.

IDEAS TO SCORE:
${JSON.stringify(ideas.saasIdeas, null, 2)}

RAW DATA SIGNALS:
- Total reviews analyzed: ${rawData.length}
- Sources: ${[...new Set(rawData.map(r => r.source))].join(', ')}
- Top frustration themes: ${JSON.stringify(ideas.marketGaps?.slice(0, 5))}

Respond ONLY in this JSON format:
{
  "scoredIdeas": [
    {
      "rank": 1,
      "name": "product name",
      "scores": {
        "painLevel":       { "score": 9, "reasoning": "why" },
        "marketSize":      { "score": 7, "reasoning": "why" },
        "competition":     { "score": 8, "reasoning": "why" },
        "buildability":    { "score": 6, "reasoning": "why" },
        "monetization":    { "score": 8, "reasoning": "why" },
        "founderFit":      { "score": 7, "reasoning": "why" }
      },
      "overallScore": 7.5,
      "verdict": "🔥 Build this | ✅ Worth exploring | ⚠️ Risky | ❌ Skip",
      "nextStep": "concrete first action to validate this idea"
    }
  ],
  "winnerIdea": "name of the single best opportunity",
  "executiveSummary": "2-3 sentence summary of the full analysis"
}
`;

  const { data } = await claude.post('/messages', {
    model: "claude-opus-4-5",
    max_tokens: 2500,
    messages: [{ role: "user", content: prompt }]
  });

  return JSON.parse(data.content[0].text.replace(/```json|```/g, '').trim());
}
```

---

## Layer 3 — Opportunity Report Generator

```javascript
import { writeFileSync } from 'fs';

function generateMarkdownReport(frustrations, gaps, scored, rawDataCount) {
  const top = scored.scoredIdeas.slice(0, 3);
  const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  return `# 🎯 Business Opportunity Report
**Niche:** ${TARGET_NICHE} | **Date:** ${date} | **Data Points Analyzed:** ${rawDataCount}

---

## Executive Summary
${scored.executiveSummary}

**🏆 Winner Idea: ${scored.winnerIdea}**

---

## Top Market Gaps Identified

${gaps.marketGaps?.slice(0, 5).map((g, i) =>
  `### ${i + 1}. ${g.gap}
- **Evidence:** ${g.evidenceStrength} | **Market:** ${g.estimatedMarketSize} | **Competition:** ${g.competitionLevel}
- **Urgency:** ${g.urgency}`
).join('\n\n')}

---

## Top 3 SaaS Opportunities

${top.map(idea => `### ${idea.rank}. ${idea.name} — Score: ${idea.overallScore}/10 ${idea.verdict}

${gaps.saasIdeas?.find(i => i.name === idea.name)?.oneLiner || ""}

| Dimension | Score | Notes |
|---|---|---|
| Pain Level | ${idea.scores.painLevel.score}/10 | ${idea.scores.painLevel.reasoning} |
| Market Size | ${idea.scores.marketSize.score}/10 | ${idea.scores.marketSize.reasoning} |
| Competition | ${idea.scores.competition.score}/10 | ${idea.scores.competition.reasoning} |
| Buildability | ${idea.scores.buildability.score}/10 | ${idea.scores.buildability.reasoning} |
| Monetization | ${idea.scores.monetization.score}/10 | ${idea.scores.monetization.reasoning} |

**Next Step:** ${idea.nextStep}`
).join('\n\n---\n\n')}

---

## Top Customer Frustrations

${frustrations.frustrations?.slice(0, 8).map((f, i) =>
  `**${i + 1}. ${f.theme}** (Intensity: ${f.emotionalIntensity}/10 | Frequency: ${f.frequency})
> "${f.evidenceQuotes?.[0] || 'No quote available'}"
${f.description}`
).join('\n\n')}

---

## Quick Wins (Ship in Days)

${gaps.quickWins?.map(q =>
  `- **${q.idea}** | Time to MVP: ${q.timeToMVP} | Validate by: ${q.validationMethod}`
).join('\n')}

---
*Generated by Hidden Business Opportunity Detector • Powered by Apify + Claude*
`;
}
```

---

## Master Orchestrator — Full Pipeline

```javascript
async function runOpportunityDetector(niche = TARGET_NICHE) {
  console.log(`\n🎯 Opportunity Detector started — ${niche}`);
  console.log(`Timestamp: ${new Date().toISOString()}\n`);

  try {
    // STEP 1 — Mine all data sources in parallel
    console.log("[1/5] Mining data sources...");
    const [appReviews, amazonReviews, redditData, productIntel] = await Promise.all([
      scrapeAppReviews(),
      scrapeAmazonReviews(),
      scrapeRedditFrustrations(),
      scrapeProductIntelligence()
    ]);

    const allData = [...appReviews, ...amazonReviews, ...redditData, ...productIntel];
    console.log(`  ✅ ${allData.length} data points collected`);
    console.log(`     App reviews: ${appReviews.length} | Amazon: ${amazonReviews.length}`);
    console.log(`     Reddit: ${redditData.length} | Product intel: ${productIntel.length}`);

    // STEP 2 — Extract frustrations
    console.log("\n[2/5] Extracting frustrations with Claude...");
    const frustrations = await extractFrustrations(allData);
    console.log(`  ✅ ${frustrations.frustrations?.length} frustration themes identified`);
    console.log(`  ✅ ${frustrations.featureRequests?.length} feature requests found`);

    // STEP 3 — Analyze market gaps and generate SaaS ideas
    console.log("\n[3/5] Analyzing market gaps...");
    const gaps = await analyzeMarketGaps(frustrations, productIntel);
    console.log(`  ✅ ${gaps.marketGaps?.length} gaps identified`);
    console.log(`  ✅ ${gaps.saasIdeas?.length} SaaS ideas generated`);

    // STEP 4 — Score all opportunities
    console.log("\n[4/5] Scoring opportunities...");
    const scored = await scoreOpportunities(gaps, allData);
    console.log(`  ✅ Ideas scored | Winner: ${scored.winnerIdea}`);

    // STEP 5 — Generate report
    console.log("\n[5/5] Generating report...");
    const report = generateMarkdownReport(frustrations, gaps, scored, allData.length);
    writeFileSync(`./opportunity-report-${Date.now()}.md`, report);

    const outputJSON = {
      niche,
      analyzedAt: new Date().toISOString(),
      dataPoints: allData.length,
      frustrationThemes: frustrations.frustrations?.length,
      marketGaps: gaps.marketGaps,
      saasIdeas: scored.scoredIdeas,
      winnerIdea: scored.winnerIdea,
      quickWins: gaps.quickWins,
      executiveSummary: scored.executiveSummary
    };

    writeFileSync(`./opportunity-data-${Date.now()}.json`, JSON.stringify(outputJSON, null, 2));
    console.log("\n✅ Reports saved to disk");

    // Optional: push to Slack
    if (process.env.SLACK_WEBHOOK_URL) {
      await axios.post(process.env.SLACK_WEBHOOK_URL, {
        text: `🎯 *Opportunity Report Ready — ${niche}*\n` +
              `📊 ${allData.length} data points analyzed\n` +
              `🏆 Top idea: *${scored.winnerIdea}*\n` +
              `💬 ${scored.executiveSummary}`
      });
    }

    return outputJSON;

  } catch (err) {
    console.error("Pipeline error:", err.message);
    throw err;
  }
}

// Run immediately
runOpportunityDetector("project management tools");
```

---

## Environment Variables

```bash
# .env
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# Optional notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxx
```

---

## Normalized Opportunity Output Schema

```json
{
  "niche": "project management",
  "analyzedAt": "2025-02-25T10:00:00Z",
  "dataPoints": 380,
  "winnerIdea": "AutoStandup",
  "saasIdeas": [
    {
      "rank": 1,
      "name": "AutoStandup",
      "oneLiner": "Async standups that actually get filled out",
      "overallScore": 8.5,
      "verdict": "🔥 Build this",
      "targetCustomer": "Remote engineering teams 5-50 people",
      "estimatedMRR": "$12,000 at 100 customers ($120/mo per team)",
      "timeToMVP": "3 weeks",
      "nextStep": "Post in r/remotework and r/SaaS — ask if this is a real problem",
      "validationSignals": [
        "47 Reddit posts complaining about standups being ignored",
        "3-star Slack reviews: 'nobody fills them out'"
      ]
    }
  ],
  "quickWins": [
    {
      "idea": "Notion template for async standups",
      "timeToMVP": "2 days",
      "validationMethod": "Post on Gumroad, see if anyone pays $9"
    }
  ]
}
```

---

## Best Practices

- Focus on **1–3 star reviews** — that's where the real pain lives
- Scrape **at least 200+ reviews** per competitor for statistically significant patterns
- Always include a **"why is there no tool for X"** Reddit search — goldmine for gaps
- Cross-validate: an idea is strong only if the same frustration appears in **3+ sources**
- The **Quick Wins section** is perfect for validation before building — ship a landing page first
- Re-run the pipeline on a **new niche weekly** to build a pipeline of ideas
- Track which ideas get the most Slack/Notion engagement from your team

---

## Error Handling

```javascript
try {
  const data = await scrapeAppReviews();
  return data;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token");
  if (error.statusCode === 429) throw new Error("Rate limit — reduce concurrent scrapers");
  if (error.message.includes("actor")) throw new Error("Actor not found — verify actor ID");
  throw error;
}
```

---

## Requirements

- **Apify** account → https://www.apify.com/?fpr=dx06p
- **Claude / OpenClaw** API key
- Node.js 18+ with `apify-client`, `axios`, `node-cron`, `fs-extra`
- Optional: Slack, Notion, or Airtable for team collaboration on the output
