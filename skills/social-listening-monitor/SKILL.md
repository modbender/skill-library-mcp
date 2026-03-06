---
name: Social Listening & Brand Reputation Monitor Skill
description: "This skill builds a real-time brand reputation monitoring system
  that: 1. Apify scrapes Twitter/X, Reddit, forums, and news sites for every
  mention of your brand 2. Claude (OpenClaw) analyzes senti..."
---

# Social Listening & Brand Reputation Monitor Skill

## Overview

This skill builds a **real-time brand reputation monitoring system** that:
1. **Apify** scrapes Twitter/X, Reddit, forums, and news sites for every mention of your brand
2. **Claude (OpenClaw)** analyzes sentiment, detects crises, and classifies each mention
3. **Alerts** fire instantly to Slack, Telegram, or email when reputation risk is detected

The result: you know what people are saying about your brand the moment they say it —
and you can respond before it becomes a crisis.

> 🔗 Apify: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- Monitor **Twitter/X, Reddit, forums, and news** for brand mentions in real-time
- Perform **sentiment analysis** on every mention (positive / negative / neutral)
- Detect **crisis signals** — sudden spikes in negative mentions
- Track **competitor mentions** for comparative reputation benchmarking
- Score **reputation health** over time with a rolling dashboard score
- **Alert immediately** on Slack/Telegram when a crisis threshold is crossed
- Generate **weekly reputation reports** with trends and actionable insights
- Distinguish **genuine complaints** from spam or bot activity

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│           SOCIAL LISTENING & REPUTATION MONITOR                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LAYER 1 — MENTION SCRAPING (Apify)                      │   │
│  │  Twitter/X │ Reddit │ Hacker News │ Google News           │   │
│  │  Trustpilot │ G2 │ App Store │ Niche Forums               │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────▼──────────────────────────────┐   │
│  │  LAYER 2 — REPUTATION ANALYSIS ENGINE (Claude)           │   │
│  │                                                          │   │
│  │  • Sentiment Classifier   → pos / neg / neutral + score  │   │
│  │  • Crisis Detector        → spike in neg mentions        │   │
│  │  • Topic Categorizer      → product | support | pr | etc │   │
│  │  • Influence Scorer       → who is talking (reach)       │   │
│  │  • Response Generator     → suggested reply drafts       │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────▼──────────────────────────────┐   │
│  │  LAYER 3 — ALERTS & REPORTING                            │   │
│  │  Slack │ Telegram │ Email │ Dashboard │ Weekly Report     │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
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

### Slack Webhook (optional)
1. Go to **api.slack.com/apps** → Create App → Incoming Webhooks
2. Copy the webhook URL:
   ```bash
   export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
   ```

### Telegram Bot (optional)
```bash
export TELEGRAM_BOT_TOKEN=123456789:AABBccDDeeFFggHH
export TELEGRAM_CHAT_ID=-1001234567890
```

---

## Step 2 — Install Dependencies

```bash
npm install apify-client axios node-cron dotenv
```

---

## Configuration — Define Your Brand

```javascript
// config.js
export const BRAND_CONFIG = {
  brandName: "YourBrand",
  keywords: [
    "YourBrand",
    "YourBrand.com",
    "@YourBrandHandle",
    "#YourBrand",
    "your brand common misspelling"
  ],
  competitors: ["CompetitorA", "CompetitorB"],
  crisisThreshold: {
    negativeSpike: 5,       // alert if 5+ negative mentions in one scan
    sentimentDrop: 20,      // alert if sentiment score drops 20 points
    viralThreshold: 1000    // alert if a negative post hits 1000+ engagements
  },
  language: "en",
  timezone: "America/New_York"
};
```

---

## Layer 1 — Multi-Platform Mention Scraper (Apify)

### Scrape Twitter/X Mentions

```javascript
import ApifyClient from 'apify-client';
import { BRAND_CONFIG } from './config.js';

const apify = new ApifyClient({ token: process.env.APIFY_TOKEN });

async function scrapeTwitterMentions() {
  console.log("🐦 Scraping Twitter/X mentions...");

  const run = await apify.actor("apify/twitter-scraper").call({
    searchTerms: BRAND_CONFIG.keywords,
    maxTweets: 100,
    addUserInfo: true,
    startUrls: [],
    languageFilter: BRAND_CONFIG.language
  });

  const { items } = await run.dataset().getData();

  return items.map(t => ({
    source:      "twitter",
    id:          t.id,
    text:        t.fullText || t.text,
    author:      t.author?.userName,
    authorName:  t.author?.name,
    followers:   t.author?.followers || 0,
    verified:    t.author?.isVerified || false,
    likes:       t.likeCount || 0,
    retweets:    t.retweetCount || 0,
    replies:     t.replyCount || 0,
    engagements: (t.likeCount || 0) + (t.retweetCount || 0) * 2 + (t.replyCount || 0),
    url:         t.url,
    createdAt:   t.createdAt,
    scrapedAt:   new Date().toISOString()
  }));
}
```

---

### Scrape Reddit Mentions

```javascript
async function scrapeRedditMentions() {
  console.log("👽 Scraping Reddit mentions...");

  const searchQueries = BRAND_CONFIG.keywords.map(k =>
    apify.actor("apify/reddit-search-scraper").call({
      queries: [k],
      maxItems: 30,
      sort: "new"
    }).then(run => run.dataset().getData())
      .then(d => d.items)
  );

  const results = await Promise.all(searchQueries);

  return results.flat().map(p => ({
    source:      "reddit",
    id:          p.id,
    text:        p.title + " " + (p.selftext || ""),
    title:       p.title,
    author:      p.author,
    subreddit:   p.subreddit,
    score:       p.score,
    comments:    p.numComments,
    upvoteRatio: p.upvoteRatio,
    engagements: p.score + p.numComments * 2,
    url:         p.url,
    createdAt:   new Date(p.created * 1000).toISOString(),
    scrapedAt:   new Date().toISOString()
  }));
}
```

---

### Scrape News & Review Platforms

```javascript
async function scrapeNewsAndReviews() {
  console.log("📰 Scraping news and reviews...");

  const brandQuery = BRAND_CONFIG.brandName;

  const [news, trustpilot, hackerNews] = await Promise.all([

    // Google News
    apify.actor("apify/google-search-scraper").call({
      queries: [`"${brandQuery}" news`],
      maxPagesPerQuery: 2,
      resultsPerPage: 20,
      dateRange: "pastWeek"
    }).then(run => run.dataset().getData())
      .then(d => d.items.map(r => ({
        source:    "google_news",
        text:      r.title + " " + r.snippet,
        title:     r.title,
        url:       r.url,
        createdAt: r.date || new Date().toISOString(),
        scrapedAt: new Date().toISOString()
      }))),

    // Trustpilot reviews
    apify.actor("apify/trustpilot-scraper").call({
      startUrls: [{ url: `https://www.trustpilot.com/review/${brandQuery.toLowerCase()}.com` }],
      maxReviews: 50,
      filterScore: [1, 2, 3]   // focus on negative/neutral
    }).then(run => run.dataset().getData())
      .then(d => d.items.map(r => ({
        source:    "trustpilot",
        text:      r.reviewBody,
        title:     r.reviewTitle,
        rating:    r.ratingValue,
        author:    r.author,
        url:       r.url,
        createdAt: r.datePublished,
        scrapedAt: new Date().toISOString()
      }))).catch(() => []),  // graceful fail if brand not on Trustpilot

    // Hacker News
    apify.actor("apify/hacker-news-scraper").call({
      searchQuery: brandQuery,
      maxItems: 20,
      type: "story"
    }).then(run => run.dataset().getData())
      .then(d => d.items.map(r => ({
        source:    "hacker_news",
        text:      r.title + " " + (r.text || ""),
        title:     r.title,
        author:    r.by,
        score:     r.score,
        comments:  r.descendants,
        url:       r.url || `https://news.ycombinator.com/item?id=${r.id}`,
        createdAt: new Date(r.time * 1000).toISOString(),
        scrapedAt: new Date().toISOString()
      }))).catch(() => [])

  ]);

  return [...news, ...trustpilot, ...hackerNews];
}
```

---

### Aggregate All Mentions

```javascript
async function scrapeAllMentions() {
  const [twitter, reddit, newsReviews] = await Promise.all([
    scrapeTwitterMentions(),
    scrapeRedditMentions(),
    scrapeNewsAndReviews()
  ]);

  const all = [...twitter, ...reddit, ...newsReviews];

  // Deduplicate by URL
  const seen = new Set();
  return all.filter(m => {
    if (seen.has(m.url)) return false;
    seen.add(m.url);
    return true;
  });
}
```

---

## Layer 2 — Reputation Analysis Engine (Claude)

### Sentiment Classifier

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

async function analyzeSentiment(mentions) {
  const prompt = `
You are a brand reputation analyst. Analyze each mention and classify it.

BRAND: ${BRAND_CONFIG.brandName}

MENTIONS TO ANALYZE:
${JSON.stringify(mentions.slice(0, 30), null, 2)}

Respond ONLY in this JSON format:
{
  "analyzedMentions": [
    {
      "id": "mention id or url",
      "sentiment": "positive | negative | neutral | mixed",
      "sentimentScore": 7,
      "confidenceLevel": "high | medium | low",
      "emotionalTone": "angry | frustrated | disappointed | happy | excited | neutral | sarcastic",
      "category": "product_feedback | customer_support | pr_crisis | competitor_comparison | spam | praise | question | bug_report",
      "urgency": "critical | high | medium | low",
      "isInfluencer": true,
      "requiresResponse": true,
      "suggestedResponseTone": "apologetic | informative | appreciative | ignore",
      "keyTopics": ["topic1", "topic2"],
      "isCrisisSignal": false,
      "summary": "one-line summary of what was said"
    }
  ],
  "batchSentiment": {
    "positive": 0,
    "negative": 0,
    "neutral": 0,
    "mixed": 0,
    "overallScore": 65,
    "trend": "improving | declining | stable"
  },
  "crisisSignals": [
    {
      "signal": "description of the risk",
      "severity": "critical | high | medium",
      "source": "platform",
      "url": "url of the post",
      "recommendedAction": "what to do right now"
    }
  ],
  "topComplaintsThisRound": ["complaint 1", "complaint 2"],
  "topPraisesThisRound": ["praise 1", "praise 2"]
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

### Crisis Detector

```javascript
// Rolling sentiment history (use Redis/DB in production)
const sentimentHistory = [];

function detectCrisis(analysis) {
  const crisisAlerts = [];
  const batch = analysis.batchSentiment;
  const signals = analysis.crisisSignals || [];

  // Track history
  sentimentHistory.push({
    score: batch.overallScore,
    negative: batch.negative,
    timestamp: new Date().toISOString()
  });

  const prev = sentimentHistory[sentimentHistory.length - 2];

  // CRISIS TRIGGER 1 — Spike in negative mentions
  if (batch.negative >= BRAND_CONFIG.crisisThreshold.negativeSpike) {
    crisisAlerts.push({
      type: "negative_spike",
      severity: "critical",
      message: `🚨 ${batch.negative} negative mentions detected in this scan`,
      threshold: BRAND_CONFIG.crisisThreshold.negativeSpike,
      current: batch.negative
    });
  }

  // CRISIS TRIGGER 2 — Sentiment score drop
  if (prev && (prev.score - batch.overallScore) >= BRAND_CONFIG.crisisThreshold.sentimentDrop) {
    crisisAlerts.push({
      type: "sentiment_drop",
      severity: "high",
      message: `📉 Sentiment dropped from ${prev.score} to ${batch.overallScore} (-${prev.score - batch.overallScore} pts)`,
      previousScore: prev.score,
      currentScore: batch.overallScore
    });
  }

  // CRISIS TRIGGER 3 — High-engagement negative post
  const viralNegative = analysis.analyzedMentions?.filter(m =>
    m.sentiment === "negative" &&
    m.urgency === "critical"
  ) || [];

  if (viralNegative.length > 0) {
    crisisAlerts.push({
      type: "viral_negative",
      severity: "high",
      message: `🔥 ${viralNegative.length} high-urgency negative mention(s) detected`,
      mentions: viralNegative.map(m => m.id)
    });
  }

  // Add explicit crisis signals from Claude
  signals.forEach(signal => {
    if (signal.severity === "critical" || signal.severity === "high") {
      crisisAlerts.push({ ...signal, type: "claude_signal" });
    }
  });

  return crisisAlerts;
}
```

---

### Response Suggestion Generator

```javascript
async function generateResponseSuggestions(urgentMentions) {
  if (urgentMentions.length === 0) return [];

  const prompt = `
You are a brand communications expert. Write response suggestions for these urgent mentions.
Be empathetic, on-brand, and action-oriented. Never defensive.

BRAND: ${BRAND_CONFIG.brandName}

URGENT MENTIONS REQUIRING RESPONSE:
${JSON.stringify(urgentMentions.slice(0, 5), null, 2)}

Respond ONLY in this JSON format:
{
  "suggestions": [
    {
      "mentionId": "id or url",
      "platform": "twitter | reddit | etc",
      "originalText": "what they said (summarized)",
      "sentiment": "negative | mixed",
      "responseOptions": [
        {
          "tone": "apologetic",
          "response": "full suggested response text",
          "bestFor": "when the issue is your fault"
        },
        {
          "tone": "informative",
          "response": "full suggested response text",
          "bestFor": "when it is a misunderstanding"
        }
      ],
      "doNotDo": "what to avoid saying in this specific case",
      "priority": "respond within 1h | 4h | 24h"
    }
  ]
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

## Layer 3 — Alerts & Reporting

### Slack Alert Publisher

```javascript
async function sendSlackAlert(crisisAlerts, analysis, responses) {
  const isCrisis = crisisAlerts.some(a => a.severity === "critical");
  const color = isCrisis ? "#FF0000" : "#FFA500";
  const icon = isCrisis ? "🚨" : "⚠️";

  const payload = {
    attachments: [{
      color,
      blocks: [
        {
          type: "header",
          text: { type: "plain_text", text: `${icon} Brand Alert: ${BRAND_CONFIG.brandName}` }
        },
        {
          type: "section",
          fields: [
            { type: "mrkdwn", text: `*Sentiment Score:*\n${analysis.batchSentiment.overallScore}/100` },
            { type: "mrkdwn", text: `*Trend:*\n${analysis.batchSentiment.trend}` },
            { type: "mrkdwn", text: `*Negative Mentions:*\n${analysis.batchSentiment.negative}` },
            { type: "mrkdwn", text: `*Requires Response:*\n${responses?.suggestions?.length || 0} mentions` }
          ]
        },
        ...crisisAlerts.map(alert => ({
          type: "section",
          text: {
            type: "mrkdwn",
            text: `*${alert.severity?.toUpperCase()}:* ${alert.message}\n${alert.recommendedAction || ""}`
          }
        })),
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `*Top Complaints:*\n${analysis.topComplaintsThisRound?.map(c => `• ${c}`).join('\n') || "None"}`
          }
        }
      ]
    }]
  };

  await axios.post(process.env.SLACK_WEBHOOK_URL, payload);
}
```

---

### Telegram Crisis Alert

```javascript
async function sendTelegramAlert(crisisAlerts, analysis) {
  const severity = crisisAlerts[0]?.severity || "medium";
  const icon = severity === "critical" ? "🚨🚨🚨" : "⚠️";

  const message = `
${icon} *BRAND ALERT: ${BRAND_CONFIG.brandName}*

📊 *Reputation Score:* ${analysis.batchSentiment.overallScore}/100 (${analysis.batchSentiment.trend})
😡 *Negative:* ${analysis.batchSentiment.negative} | 😊 *Positive:* ${analysis.batchSentiment.positive}

*🔴 Crisis Signals:*
${crisisAlerts.map(a => `• [${a.severity?.toUpperCase()}] ${a.message}`).join('\n')}

*📢 Top Complaints:*
${analysis.topComplaintsThisRound?.slice(0, 3).map(c => `• ${c}`).join('\n') || "• None"}

*✅ Top Praises:*
${analysis.topPraisesThisRound?.slice(0, 2).map(p => `• ${p}`).join('\n') || "• None"}

⏰ ${new Date().toLocaleString()}
`.trim();

  await axios.post(
    `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`,
    {
      chat_id: process.env.TELEGRAM_CHAT_ID,
      text: message,
      parse_mode: "Markdown"
    }
  );
}
```

---

### Weekly Reputation Report

```javascript
function generateWeeklyReport(weekData) {
  const avgScore = Math.round(
    weekData.reduce((sum, d) => sum + d.score, 0) / weekData.length
  );
  const totalMentions = weekData.reduce((sum, d) => sum + d.mentions, 0);
  const totalNegative = weekData.reduce((sum, d) => sum + d.negative, 0);
  const date = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  return `# 📣 Weekly Reputation Report — ${BRAND_CONFIG.brandName}
**Week ending:** ${date}

---

## 📊 At a Glance

| Metric | Value |
|---|---|
| Reputation Score | ${avgScore}/100 |
| Total Mentions | ${totalMentions} |
| Negative Mentions | ${totalNegative} (${Math.round(totalNegative/totalMentions*100)}%) |
| Crisis Events | ${weekData.filter(d => d.hadCrisis).length} |
| Trend | ${avgScore >= 70 ? "✅ Healthy" : avgScore >= 50 ? "⚠️ Watch" : "🚨 At Risk"} |

---

## 📈 Day-by-Day Sentiment

${weekData.map(d =>
  `**${d.date}** — Score: ${d.score}/100 | Mentions: ${d.mentions} | Neg: ${d.negative}`
).join('\n')}

---

## 🔴 Top Complaints This Week
${weekData.flatMap(d => d.complaints || []).slice(0, 8).map(c => `- ${c}`).join('\n')}

---

## 🟢 Top Praises This Week
${weekData.flatMap(d => d.praises || []).slice(0, 5).map(p => `- ${p}`).join('\n')}

---

## 💡 Recommended Actions
1. Address top recurring complaint systematically — not just one-by-one
2. Amplify positive mentions by engaging with brand advocates
3. Monitor competitor sentiment for positioning opportunities

---
*Generated by Social Listening Bot • Powered by Apify + Claude*
`;
}
```

---

## Master Orchestrator — Full Pipeline

```javascript
import cron from 'node-cron';
import { writeFileSync } from 'fs';

async function runSocialListening() {
  console.log(`\n👂 Social Listening scan — ${new Date().toISOString()}`);

  try {
    // STEP 1 — Scrape all platforms
    console.log("[1/5] Scraping mentions...");
    const mentions = await scrapeAllMentions();
    console.log(`  ✅ ${mentions.length} mentions collected`);

    if (mentions.length === 0) {
      console.log("  ℹ️  No new mentions found");
      return;
    }

    // STEP 2 — Analyze sentiment
    console.log("[2/5] Analyzing sentiment with Claude...");
    const analysis = await analyzeSentiment(mentions);
    const score = analysis.batchSentiment.overallScore;
    console.log(`  ✅ Score: ${score}/100 | Neg: ${analysis.batchSentiment.negative} | Trend: ${analysis.batchSentiment.trend}`);

    // STEP 3 — Detect crisis
    console.log("[3/5] Checking for crisis signals...");
    const crisisAlerts = detectCrisis(analysis);
    console.log(`  ✅ ${crisisAlerts.length} crisis signal(s) detected`);

    // STEP 4 — Generate response suggestions for urgent mentions
    const urgentMentions = analysis.analyzedMentions?.filter(m =>
      m.requiresResponse && (m.urgency === "critical" || m.urgency === "high")
    ) || [];
    let responses = { suggestions: [] };

    if (urgentMentions.length > 0) {
      console.log(`[4/5] Generating ${urgentMentions.length} response suggestions...`);
      responses = await generateResponseSuggestions(urgentMentions);
      console.log(`  ✅ ${responses.suggestions?.length} response drafts ready`);
    }

    // STEP 5 — Send alerts if needed
    if (crisisAlerts.length > 0) {
      console.log("[5/5] Sending crisis alerts...");
      if (process.env.SLACK_WEBHOOK_URL) {
        await sendSlackAlert(crisisAlerts, analysis, responses);
      }
      if (process.env.TELEGRAM_BOT_TOKEN) {
        await sendTelegramAlert(crisisAlerts, analysis);
      }
      console.log("  ✅ Alerts sent");
    } else {
      console.log("[5/5] No alerts needed — reputation looks healthy");
    }

    // Save report
    const report = {
      scannedAt: new Date().toISOString(),
      mentionsFound: mentions.length,
      sentimentScore: score,
      trend: analysis.batchSentiment.trend,
      crisisAlerts,
      topComplaints: analysis.topComplaintsThisRound,
      topPraises: analysis.topPraisesThisRound,
      responseSuggestions: responses.suggestions
    };

    writeFileSync(`./reputation-log-${Date.now()}.json`, JSON.stringify(report, null, 2));
    return report;

  } catch (err) {
    console.error("Listening error:", err.message);
  }
}

// Scan every hour
cron.schedule('0 * * * *', runSocialListening);

// Run immediately on startup
runSocialListening();
```

---

## Environment Variables

```bash
# .env
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# Alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
TELEGRAM_BOT_TOKEN=123456789:AABBccDDeeFFggHH
TELEGRAM_CHAT_ID=-1001234567890

# Optional
ALERT_EMAIL=team@yourbrand.com
```

---

## Normalized Mention Schema

```json
{
  "source": "twitter",
  "text": "Just tried YourBrand and honestly it is broken...",
  "author": "user123",
  "followers": 12400,
  "engagements": 847,
  "sentiment": "negative",
  "sentimentScore": 2,
  "emotionalTone": "frustrated",
  "category": "product_feedback",
  "urgency": "high",
  "requiresResponse": true,
  "isCrisisSignal": false,
  "keyTopics": ["bug", "login", "performance"],
  "url": "https://twitter.com/user123/status/xxx",
  "createdAt": "2025-02-25T09:00:00Z"
}
```

---

## Best Practices

- Scan every **30–60 minutes** for real-time monitoring, **every 4 hours** for standard tracking
- Always monitor **competitor brand names** in parallel for benchmarking opportunities
- Set `crisisThreshold.negativeSpike` based on your **normal daily volume** — not a fixed number
- Flag and ignore **spam/bot mentions** — Claude's `confidenceLevel` field helps filter these
- Route `critical` alerts to **on-call Slack/phone**, `high` alerts to the team channel
- Use the **response suggestions** as drafts only — always have a human review before posting
- Archive all mention logs for **quarterly trend analysis** and PR reporting

---

## Error Handling

```javascript
try {
  const mentions = await scrapeAllMentions();
  return mentions;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token");
  if (error.statusCode === 429) throw new Error("Rate limit hit — space out scraping intervals");
  if (error.message.includes("TELEGRAM")) throw new Error("Telegram config error — check token and chat ID");
  throw error;
}
```

---

## Requirements

- **Apify** account → https://www.apify.com/?fpr=dx06p
- **Claude / OpenClaw** API key
- Node.js 18+ with `apify-client`, `axios`, `node-cron`
- **Slack** workspace and/or **Telegram** bot for alerts
- Optional: Redis for persistent sentiment history and trend tracking across restarts
