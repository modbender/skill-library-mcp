---
name: Video Ad Production Skill
description: This skill enables Claude to transform a text brief into a fully
  produced video advertisement — ready to run on Facebook Ads, Instagram Ads, or
  YouTube Ads — using the InVideo AI platform.
---

# Video Ad Production Skill

## Overview

This skill enables Claude to transform a **text brief** into a fully produced
video advertisement — ready to run on **Facebook Ads**, **Instagram Ads**, or **YouTube Ads** —
using the **InVideo AI** platform.

From a product description or campaign goal, Claude generates a complete ad video:
script, voiceover, visuals, captions, CTA, and platform-optimized export.

> 🔗 Sign up for InVideo here: https://invideo.sjv.io/TBB

---

## What This Skill Does

- Generate **video ads from a text brief** (product, audience, goal, tone)
- Produce ads in the correct format for **Facebook**, **Instagram**, and **YouTube**
- Write and optimize **ad scripts** with proven direct-response copywriting structures
- Add **voiceover, background music, captions, and call-to-action overlays**
- Export multiple **ad variations** for A/B testing
- Support multiple **aspect ratios**: 9:16 (Stories/Reels), 1:1 (Feed), 16:9 (YouTube)
- Localize ads into **multiple languages** with different voices

---

## Step 1 — Get Your InVideo API Access

1. Go to **https://invideo.sjv.io/TBB** and create an account
2. Choose a plan with **API access** (Business plan or above)
3. Navigate to **Settings → API / Developer Settings**
4. Copy your **API Key**: `iv_api_xxxxxxxxxxxxxxxx`
5. Store it as an environment variable:
   ```bash
   export INVIDEO_API_KEY=iv_api_xxxxxxxxxxxxxxxx
   ```

> Start with the free trial at https://invideo.sjv.io/TBB to test ad generation
> before scaling to paid production.

---

## Step 2 — Install Dependencies

```bash
npm install axios fs-extra
```

---

## InVideo API — Core Endpoints

**Base URL:** `https://api.invideo.io/v1`

All requests require:
```
Authorization: Bearer YOUR_INVIDEO_API_KEY
Content-Type: application/json
```

| Endpoint | Method | Purpose |
|---|---|---|
| `/videos/generate` | POST | Start video generation from a script or brief |
| `/videos/{id}/status` | GET | Poll generation progress |
| `/videos/{id}/export` | GET | Retrieve final download URL |
| `/scripts/generate` | POST | Generate an ad script from a brief (if supported) |

---

## Ad Script Structures (Claude Will Apply These)

Claude selects the right copywriting framework automatically based on the campaign goal:

| Framework | Best For | Structure |
|---|---|---|
| **AIDA** | Awareness campaigns | Attention → Interest → Desire → Action |
| **PAS** | Pain-point products | Problem → Agitate → Solution |
| **BAB** | Transformation products | Before → After → Bridge |
| **Hook + Proof + CTA** | Performance ads | Bold hook → Social proof → Offer + CTA |

---

## Examples

### Generate a Facebook Ad from a Brief

```javascript
import axios from 'axios';

const client = axios.create({
  baseURL: 'https://api.invideo.io/v1',
  headers: { Authorization: `Bearer ${process.env.INVIDEO_API_KEY}` }
});

// Define the ad brief
const brief = {
  product: "AI-powered meal planning app",
  targetAudience: "busy professionals aged 25–40",
  goal: "app installs",
  tone: "energetic and relatable",
  keyBenefit: "save 2 hours a week on meal prep",
  offer: "Free 14-day trial, no credit card required",
  callToAction: "Download free today"
};

// Claude-generated script based on the brief (PAS framework)
const script = `
  Tired of staring at the fridge every evening, clueless about dinner?
  That mental load of planning meals every single day is exhausting.
  Meet MealAI — the app that plans your entire week in 30 seconds.
  Personalized to your diet, your schedule, your grocery budget.
  Over 200,000 busy professionals already saved 2 hours a week.
  Try it completely free for 14 days. No credit card needed.
  Download MealAI today.
`;

const response = await client.post('/videos/generate', {
  script,
  format: "1:1",              // Square — best for Facebook/Instagram Feed
  duration: "short",          // 15–30 seconds optimal for paid ads
  style: "cinematic",         // polished, professional ad look
  voiceover: {
    enabled: true,
    voice: "en-US-female-1",
    speed: 1.05,
    tone: "energetic"
  },
  captions: {
    enabled: true,
    style: "bold-center",
    highlight: true,
    fontSize: "large"          // readable on mobile without sound
  },
  music: {
    enabled: true,
    mood: "upbeat",
    volume: 0.2
  },
  cta: {
    enabled: true,
    text: "Download Free Today",
    position: "bottom",
    style: "button"
  },
  branding: {
    watermark: false
  }
});

const videoId = response.data.videoId;
console.log("Ad generation started:", videoId);
```

---

### Generate Platform-Specific Ad Variants

```javascript
// Generate all 3 formats from the same script in parallel

const formats = [
  { name: "facebook_feed",    format: "1:1",   platform: "Facebook Feed" },
  { name: "instagram_story",  format: "9:16",  platform: "Instagram Story/Reels" },
  { name: "youtube_preroll",  format: "16:9",  platform: "YouTube Pre-roll" }
];

const jobs = await Promise.all(
  formats.map(f =>
    client.post('/videos/generate', {
      script,
      format: f.format,
      duration: f.format === "16:9" ? "medium" : "short",
      style: "cinematic",
      voiceover: { enabled: true, voice: "en-US-female-1", speed: 1.05 },
      captions: { enabled: true, style: "bold-bottom", highlight: true },
      music: { enabled: true, mood: "upbeat", volume: 0.2 },
      cta: { enabled: true, text: "Try Free Today", position: "bottom" }
    }).then(res => ({ ...f, videoId: res.data.videoId }))
  )
);

console.log("All ad variants started:");
jobs.forEach(j => console.log(`  [${j.platform}] ID: ${j.videoId}`));
```

---

### Poll All Variants Until Ready

```javascript
async function waitForAll(jobs) {
  const results = [];

  for (const job of jobs) {
    let exportUrl = null;

    while (!exportUrl) {
      await new Promise(r => setTimeout(r, 5000));
      const { data } = await client.get(`/videos/${job.videoId}/status`);

      console.log(`[${job.platform}] ${data.state} — ${data.progress}%`);

      if (data.state === "completed") exportUrl = data.exportUrl;
      if (data.state === "failed") throw new Error(`${job.platform} ad failed`);
    }

    results.push({ ...job, exportUrl });
  }

  return results;
}

const completedAds = await waitForAll(jobs);
completedAds.forEach(ad => {
  console.log(`✅ ${ad.platform}: ${ad.exportUrl}`);
});
```

---

### A/B Test: Generate 3 Hook Variations

```javascript
const hooks = [
  "Tired of wasting money on groceries you never eat?",
  "What if you could plan a full week of meals in 30 seconds?",
  "200,000 people just discovered the secret to stress-free meal prep."
];

const baseScript = (hook) => `
  ${hook}
  MealAI plans your entire week in seconds.
  Personalized meals. Automatic grocery list. Zero stress.
  Try free for 14 days — no credit card required.
  Download MealAI now.
`;

const abJobs = await Promise.all(
  hooks.map((hook, i) =>
    client.post('/videos/generate', {
      script: baseScript(hook),
      format: "1:1",
      duration: "short",
      style: "cinematic",
      voiceover: { enabled: true, voice: "en-US-female-1" },
      captions: { enabled: true, style: "bold-bottom", highlight: true },
      music: { enabled: true, mood: "upbeat", volume: 0.2 },
      cta: { enabled: true, text: "Download Free Today" }
    }).then(res => ({ variant: `Hook_${i + 1}`, hook, videoId: res.data.videoId }))
  )
);

console.log("A/B variants launched:", abJobs.map(j => j.variant));
```

---

## Full Brief-to-Ad Pipeline

When given an ad brief, Claude will:

1. **Extract** product, audience, goal, tone, benefit, offer, and CTA from the brief
2. **Choose** the right copywriting framework (AIDA, PAS, BAB, Hook+Proof+CTA)
3. **Write** a platform-optimized ad script (15–30s for social, up to 60s for YouTube)
4. **Select** format, style, voice, music mood, and caption style per platform
5. **Generate** all required format variants in parallel via InVideo API
6. **Poll** until all variants are ready
7. **Return** download URLs and a structured ad delivery report

---

## Platform Ad Specifications

| Platform | Format | Duration | Key Requirements |
|---|---|---|---|
| Facebook Feed | 1:1 or 16:9 | 15–30s | Captions mandatory (85% watched muted) |
| Instagram Feed | 1:1 | 15–30s | Hook in first 2s, strong visual |
| Instagram Stories | 9:16 | 15s | Full screen, bold captions, fast pace |
| Instagram Reels Ads | 9:16 | 15–30s | Native feel, no borders |
| YouTube Pre-roll | 16:9 | 15–30s | Skip button at 5s — hook must hit before |
| YouTube Bumper | 16:9 | 6s max | One message, one CTA only |
| TikTok Ads | 9:16 | 15–60s | Authentic tone, trending audio |

---

## Normalized Ad Output Schema

```json
{
  "campaignName": "MealAI — App Install Q1 2025",
  "variant": "Hook_1",
  "platform": "facebook_feed",
  "format": "1:1",
  "durationSeconds": 28,
  "scriptFramework": "PAS",
  "videoId": "iv_ad_9k2mx7",
  "exportUrl": "https://cdn.invideo.io/exports/iv_ad_9k2mx7.mp4",
  "cta": "Download Free Today",
  "voiceover": "en-US-female-1",
  "musicMood": "upbeat",
  "captionsEnabled": true,
  "createdAt": "2025-02-25T10:00:00Z",
  "status": "completed"
}
```

---

## Ad Copywriting Best Practices (Applied Automatically)

- **Hook in the first 2 seconds** — the scroll stops here or nowhere
- **Lead with the problem or benefit** — never with the brand name
- **One clear message per ad** — don't try to say everything at once
- **Always include social proof** — numbers, testimonials, or results
- **End with a specific, urgent CTA** — "Download free today" beats "Learn more"
- **Write for silent viewing** — assume 85% of viewers have sound off on Facebook
- **Match the platform energy** — polished for YouTube, raw and native for TikTok

---

## Error Handling

```javascript
try {
  const response = await client.post('/videos/generate', payload);
  return response.data.videoId;
} catch (error) {
  if (error.response?.status === 401) throw new Error("Invalid InVideo API key — check credentials");
  if (error.response?.status === 429) throw new Error("Rate limit hit — reduce concurrent generations");
  if (error.response?.status === 400) {
    throw new Error(`Invalid request: ${error.response.data.message}`);
  }
  throw error;
}
```

---

## Requirements

- An InVideo account → https://invideo.sjv.io/TBB
- A plan with **API access** (Business plan or above)
- A valid **API Key** from your InVideo settings
- Node.js 18+ and `axios`
- A paid ads account (Facebook Ads Manager, Google Ads) to deploy the generated videos
