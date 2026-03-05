# Automated Content Generation Pipeline Skill

## Overview

This skill builds a **fully automated content factory** that runs 24/7:
1. **Apify** scrapes the most viral content across TikTok, Instagram, YouTube, and Reddit
2. **Claude (OpenClaw)** extracts the hooks, reverse-engineers why it went viral, generates scripts, captions, carousels, and threads
3. A **scheduler** batches all posts and queues them for auto-publishing

The result: a near fully-automated content channel that feeds itself.

> 🔗 Apify: https://www.apify.com/?fpr=dx06p

---

## What This Skill Does

- **Scrape** the top viral content across multiple platforms every few hours
- **Extract** the exact hooks, structures, and formats that made content go viral
- **Repurpose** viral content into original scripts, captions, carousels, and threads
- **Generate** a full weekly content calendar automatically
- **Batch and schedule** posts across platforms (Instagram, TikTok, LinkedIn, Twitter/X)
- **Track** which generated content performs best and feed that signal back into the pipeline
- Run **completely autonomously** once configured — minimal human input needed

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              AUTOMATED CONTENT GENERATION PIPELINE              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LAYER 1 — VIRAL CONTENT SCRAPING (Apify)               │   │
│  │  TikTok │ Instagram │ YouTube │ Reddit │ Twitter/X       │   │
│  │  Top posts by hashtag, views, engagement, shares        │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  LAYER 2 — AI CONTENT ENGINE (Claude / OpenClaw)        │   │
│  │                                                         │   │
│  │  • Hook Extractor     → why did this go viral?          │   │
│  │  • Script Generator   → original video scripts          │   │
│  │  • Caption Writer     → post captions + hashtags        │   │
│  │  • Carousel Builder   → slide-by-slide content          │   │
│  │  • Thread Writer      → Twitter/X and LinkedIn threads  │   │
│  │  • Calendar Planner   → weekly posting schedule         │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  LAYER 3 — SCHEDULED PUBLISHING                         │   │
│  │  Buffer │ Later │ Hootsuite │ Custom Webhook             │   │
│  │  Posts queued, timed, and published automatically       │   │
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
1. Get your API key from your OpenClaw or Anthropic account
2. Store it:
   ```bash
   export CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
   ```

---

## Step 2 — Install Dependencies

```bash
npm install apify-client axios node-cron dotenv
```

---

## Layer 1 — Viral Content Scraper (Apify)

```javascript
import ApifyClient from 'apify-client';

const apify = new ApifyClient({ token: process.env.APIFY_TOKEN });

// Define your niche and topics
const NICHE_TOPICS = [
  "productivity", "entrepreneurship", "ai tools",
  "personal finance", "self improvement", "marketing"
];

async function scrapeViralContent() {
  console.log("🔍 Scraping viral content...");

  const [tiktok, instagram, reddit] = await Promise.all([

    // TikTok — top videos by hashtag
    apify.actor("apify/tiktok-hashtag-scraper").call({
      hashtags: NICHE_TOPICS,
      resultsPerPage: 30,
      shouldDownloadVideos: false
    }).then(run => run.dataset().getData()),

    // Instagram — top posts by hashtag
    apify.actor("apify/instagram-hashtag-scraper").call({
      hashtags: NICHE_TOPICS,
      resultsLimit: 30
    }).then(run => run.dataset().getData()),

    // Reddit — hottest posts in relevant subreddits
    apify.actor("apify/reddit-scraper").call({
      startUrls: [
        { url: "https://www.reddit.com/r/Entrepreneur/" },
        { url: "https://www.reddit.com/r/productivity/" },
        { url: "https://www.reddit.com/r/personalfinance/" }
      ],
      maxPostCount: 20,
      sort: "hot"
    }).then(run => run.dataset().getData())

  ]);

  // Normalize all platforms to a common schema
  const normalized = [
    ...tiktok.items.map(p => ({
      platform: "tiktok",
      text: p.text,
      likes: p.diggCount,
      shares: p.shareCount,
      comments: p.commentCount,
      views: p.playCount,
      engagementScore: (p.diggCount + p.shareCount * 3 + p.commentCount * 2),
      url: p.webVideoUrl,
      author: p.authorMeta?.name
    })),
    ...instagram.items.map(p => ({
      platform: "instagram",
      text: p.caption,
      likes: p.likesCount,
      comments: p.commentsCount,
      engagementScore: (p.likesCount + p.commentsCount * 2),
      url: p.url,
      author: p.ownerUsername
    })),
    ...reddit.items.map(p => ({
      platform: "reddit",
      text: p.title + " " + (p.selftext || ""),
      likes: p.score,
      comments: p.numComments,
      engagementScore: (p.score + p.numComments * 3),
      url: p.url,
      author: p.author
    }))
  ];

  // Return top 20 by engagement score
  return normalized
    .sort((a, b) => b.engagementScore - a.engagementScore)
    .slice(0, 20);
}
```

---

## Layer 2 — AI Content Engine (Claude / OpenClaw)

### Hook Extractor

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

async function extractHooks(viralPosts) {
  const prompt = `
You are an expert viral content analyst.

Analyze these top-performing posts and extract the exact patterns that made them go viral.

VIRAL POSTS:
${JSON.stringify(viralPosts.slice(0, 10), null, 2)}

Respond ONLY in this JSON format, no preamble:
{
  "hookPatterns": [
    {
      "pattern": "pattern name",
      "template": "reusable template with [BRACKETS] for variables",
      "example": "real example from the data",
      "whyItWorks": "psychological reason this triggers engagement",
      "bestPlatforms": ["tiktok", "instagram"]
    }
  ],
  "commonStructures": [
    {
      "format": "format name (list | storytime | tutorial | controversy | etc)",
      "openingFormula": "how these posts start",
      "bodyFormula": "how they build",
      "closingFormula": "how they end / CTA",
      "avgEngagementBoost": "estimated % above average"
    }
  ],
  "topEmotions": ["curiosity", "surprise", "..."],
  "keyInsight": "single most important lesson from this batch of viral content"
}
`;

  const { data } = await claude.post('/messages', {
    model: "claude-opus-4-5",
    max_tokens: 2000,
    messages: [{ role: "user", content: prompt }]
  });

  return JSON.parse(data.content[0].text.replace(/```json|```/g, '').trim());
}
```

---

### Script Generator

```javascript
async function generateScripts(hookAnalysis, niche, count = 5) {
  const prompt = `
You are a viral content creator. Use these proven hook patterns to generate ${count} original video scripts.

NICHE: ${niche}
HOOK PATTERNS: ${JSON.stringify(hookAnalysis.hookPatterns, null, 2)}
BEST STRUCTURES: ${JSON.stringify(hookAnalysis.commonStructures, null, 2)}

Respond ONLY in this JSON format:
{
  "scripts": [
    {
      "id": 1,
      "title": "video title",
      "platform": "tiktok | instagram | youtube_shorts",
      "hookPattern": "which pattern was used",
      "hook": "opening line — first 3 seconds",
      "fullScript": "complete word-for-word script (120-180 words)",
      "estimatedDuration": "30s",
      "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
      "cta": "call to action",
      "thumbnailIdea": "thumbnail concept",
      "viralPotential": "high | medium",
      "bestPostTime": "morning | afternoon | evening"
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

### Caption & Post Writer

```javascript
async function generatePostCaptions(scripts) {
  const prompt = `
Transform these video scripts into platform-optimized social media captions.

SCRIPTS: ${JSON.stringify(scripts, null, 2)}

Respond ONLY in this JSON format:
{
  "posts": [
    {
      "scriptId": 1,
      "platforms": {
        "instagram": {
          "caption": "full caption with line breaks and emojis",
          "hashtags": ["#tag1", "#tag2"],
          "firstComment": "hashtags to put in first comment"
        },
        "tiktok": {
          "caption": "shorter, punchy tiktok caption",
          "hashtags": ["#fyp", "#tag2"]
        },
        "linkedin": {
          "caption": "professional angle of the same content, 150-200 words",
          "hashtags": ["#tag1"]
        },
        "twitter": {
          "thread": [
            "tweet 1 (hook)",
            "tweet 2",
            "tweet 3",
            "tweet 4 (CTA)"
          ]
        }
      }
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

### Weekly Content Calendar Builder

```javascript
async function buildContentCalendar(scripts, captions) {
  const today = new Date();
  const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];

  const prompt = `
Build a 7-day content calendar from these generated posts.
Maximize reach by distributing smartly across platforms and times.

AVAILABLE CONTENT:
Scripts: ${scripts.scripts.length} video scripts
Captions: ready for Instagram, TikTok, LinkedIn, Twitter

Today is ${today.toDateString()}.

Respond ONLY in this JSON format:
{
  "calendar": [
    {
      "day": "Monday",
      "date": "YYYY-MM-DD",
      "posts": [
        {
          "time": "08:00",
          "platform": "instagram",
          "contentType": "reel | carousel | story | post",
          "scriptId": 1,
          "caption": "caption preview",
          "hashtags": ["#tag1"],
          "status": "scheduled",
          "notes": "optional tip for this post"
        }
      ]
    }
  ],
  "weekSummary": {
    "totalPosts": 0,
    "platformBreakdown": { "instagram": 0, "tiktok": 0, "linkedin": 0, "twitter": 0 },
    "estimatedReach": "rough estimate",
    "bestDayToPost": "day name",
    "strategy": "brief summary of the week strategy"
  }
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

## Layer 3 — Scheduled Publisher

```javascript
async function publishToScheduler(calendar) {
  // Example: send to Buffer API
  const BUFFER_TOKEN = process.env.BUFFER_ACCESS_TOKEN;

  for (const day of calendar.calendar) {
    for (const post of day.posts) {
      const scheduledTime = new Date(`${day.date}T${post.time}:00`);

      if (BUFFER_TOKEN) {
        await axios.post(
          'https://api.bufferapp.com/1/updates/create.json',
          {
            text: post.caption,
            profile_ids: [process.env[`BUFFER_${post.platform.toUpperCase()}_ID`]],
            scheduled_at: scheduledTime.toISOString(),
            hashtags: post.hashtags.join(' ')
          },
          { headers: { Authorization: `Bearer ${BUFFER_TOKEN}` } }
        );
      }

      // Or push to your own webhook / CMS
      if (process.env.PUBLISH_WEBHOOK_URL) {
        await axios.post(process.env.PUBLISH_WEBHOOK_URL, {
          platform: post.platform,
          caption: post.caption,
          hashtags: post.hashtags,
          scheduledAt: scheduledTime.toISOString(),
          scriptId: post.scriptId
        });
      }

      console.log(`✅ Scheduled: [${post.platform}] ${day.date} ${post.time}`);
    }
  }
}
```

---

## Master Orchestrator — Full Automated Pipeline

```javascript
import cron from 'node-cron';

async function runContentPipeline(niche = "entrepreneurship") {
  console.log(`\n🏭 Content Pipeline started — ${new Date().toISOString()}`);
  const report = {};

  try {
    // STEP 1 — Scrape viral content
    console.log("\n[1/5] Scraping viral content with Apify...");
    const viralContent = await scrapeViralContent();
    report.postsScraped = viralContent.length;
    console.log(`  ✅ ${viralContent.length} viral posts collected`);

    // STEP 2 — Extract hooks and patterns
    console.log("\n[2/5] Extracting viral hooks with Claude...");
    const hookAnalysis = await extractHooks(viralContent);
    report.hookPatterns = hookAnalysis.hookPatterns.length;
    console.log(`  ✅ ${hookAnalysis.hookPatterns.length} hook patterns identified`);
    console.log(`  💡 Key insight: ${hookAnalysis.keyInsight}`);

    // STEP 3 — Generate scripts
    console.log("\n[3/5] Generating video scripts...");
    const scripts = await generateScripts(hookAnalysis, niche, 7);
    report.scriptsGenerated = scripts.scripts.length;
    console.log(`  ✅ ${scripts.scripts.length} scripts generated`);

    // STEP 4 — Write captions for all platforms
    console.log("\n[4/5] Writing multi-platform captions...");
    const captions = await generatePostCaptions(scripts.scripts);
    report.captionsWritten = captions.posts.length;
    console.log(`  ✅ Captions written for ${captions.posts.length} posts`);

    // STEP 5 — Build weekly calendar and schedule
    console.log("\n[5/5] Building content calendar and scheduling...");
    const calendar = await buildContentCalendar(scripts, captions);
    report.calendarBuilt = true;
    report.totalPostsScheduled = calendar.weekSummary.totalPosts;
    await publishToScheduler(calendar);
    console.log(`  ✅ ${calendar.weekSummary.totalPosts} posts scheduled for the week`);

    // Summary
    console.log("\n📊 PIPELINE COMPLETE:");
    console.log(`  • Viral posts scraped:   ${report.postsScraped}`);
    console.log(`  • Hook patterns found:   ${report.hookPatterns}`);
    console.log(`  • Scripts generated:     ${report.scriptsGenerated}`);
    console.log(`  • Posts scheduled:       ${report.totalPostsScheduled}`);
    console.log(`  • Best day this week:    ${calendar.weekSummary.bestDayToPost}`);
    console.log(`  • Strategy:              ${calendar.weekSummary.strategy}`);

    return { success: true, report, calendar };

  } catch (err) {
    console.error("Pipeline error:", err.message);
    throw err;
  }
}

// Run every Sunday at 8:00 AM — generates the full week ahead
cron.schedule('0 8 * * 0', () => {
  runContentPipeline("entrepreneurship");
});

// Run every morning at 6:00 AM for daily fresh content
cron.schedule('0 6 * * *', () => {
  runContentPipeline("productivity");
});

// Run immediately on startup
runContentPipeline("ai tools");
```

---

## Environment Variables

```bash
# .env
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# Publishing (optional — pick one or more)
BUFFER_ACCESS_TOKEN=your_buffer_token
BUFFER_INSTAGRAM_ID=your_ig_profile_id
BUFFER_TIKTOK_ID=your_tiktok_profile_id
BUFFER_LINKEDIN_ID=your_linkedin_profile_id
PUBLISH_WEBHOOK_URL=https://your-app.com/webhooks/publish

# Alerts (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
```

---

## Normalized Pipeline Output Schema

```json
{
  "runAt": "2025-02-25T06:00:00Z",
  "niche": "entrepreneurship",
  "postsScraped": 90,
  "hookPatterns": 6,
  "scriptsGenerated": 7,
  "totalPostsScheduled": 21,
  "calendar": {
    "Monday": [
      { "time": "08:00", "platform": "instagram", "type": "reel", "scriptId": 1 },
      { "time": "18:00", "platform": "tiktok",    "type": "video", "scriptId": 1 },
      { "time": "12:00", "platform": "linkedin",  "type": "post",  "scriptId": 2 }
    ]
  },
  "weekSummary": {
    "totalPosts": 21,
    "platformBreakdown": {
      "instagram": 7, "tiktok": 7, "linkedin": 4, "twitter": 3
    },
    "bestDayToPost": "Tuesday",
    "strategy": "Lead with curiosity hooks on TikTok early week, repurpose as LinkedIn insights mid-week, close with engagement posts on weekends"
  }
}
```

---

## Best Practices

- **Scrape wide, publish narrow** — collect 50+ viral posts, produce 5–7 pieces of original content
- **Never copy** — use viral posts as structural inspiration only, always generate original text
- Set `cron` to run on **Sunday evening** to pre-fill the full week ahead
- Use **3–5 niches max** to keep the content focused and the audience growing
- Track which posts actually perform and feed that back as additional context to Claude
- Combine with the **Trend Radar skill** to inject real-time trend data into the pipeline
- For maximum automation, connect the video scripts to **InVideo** (see Short Video Creator skill)

---

## Requirements

- **Apify** account → https://www.apify.com/?fpr=dx06p
- **Claude / OpenClaw** API key
- Node.js 18+ with `apify-client`, `axios`, `node-cron`
- Optional: Buffer, Later, or Hootsuite account for automated publishing
- Optional: InVideo account for auto video production from generated scripts
