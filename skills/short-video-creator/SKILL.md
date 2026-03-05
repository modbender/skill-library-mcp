# Short-Form Video Creation for Social Media Skill

## Overview

This skill enables Claude to transform a **text script or idea** into a fully produced
short-form video — ready to publish as an Instagram Reel, YouTube Short, or TikTok —
using the **InVideo AI** platform and its API.

No video editing experience required. Just provide a script or topic, and Claude handles the rest.

> 🔗 Sign up for InVideo here: https://invideo.sjv.io/TBB

---

## What This Skill Does

- Convert a **raw script** into a complete short-form video with visuals and voiceover
- Generate videos optimized for **Instagram Reels**, **YouTube Shorts**, and **TikTok**
- Automatically match **stock footage, music, and transitions** to the script content
- Add **subtitles, captions, and text overlays** for better engagement
- Produce videos in the correct **9:16 vertical format** for all short-form platforms
- Export in **MP4** ready to upload directly to any platform

---

## Step 1 — Get Your InVideo API Access

1. Go to **https://invideo.sjv.io/TBB** and create an account
2. Choose a plan that includes **API access** (Business plan or above)
3. Navigate to **Settings → API** or **Developer Settings**
4. Copy your **API Key**: `iv_api_xxxxxxxxxxxxxxxx`
5. Store it safely:
   ```bash
   export INVIDEO_API_KEY=iv_api_xxxxxxxxxxxxxxxx
   ```

> InVideo offers a free trial — sign up at https://invideo.sjv.io/TBB to explore the platform
> before committing to a paid plan.

---

## Step 2 — Install Dependencies

```bash
npm install axios form-data fs-extra
```

---

## InVideo API — Core Endpoints

**Base URL:** `https://api.invideo.io/v1`

All requests require:
```
Authorization: Bearer YOUR_INVIDEO_API_KEY
Content-Type: application/json
```

### Generate a Video from Script
```http
POST https://api.invideo.io/v1/videos/generate
```

### Get Video Generation Status
```http
GET https://api.invideo.io/v1/videos/{videoId}/status
```

### Download / Export Video
```http
GET https://api.invideo.io/v1/videos/{videoId}/export
```

---

## Examples

### Generate a TikTok / Reel from a Script

```javascript
import axios from 'axios';

const client = axios.create({
  baseURL: 'https://api.invideo.io/v1',
  headers: {
    'Authorization': `Bearer ${process.env.INVIDEO_API_KEY}`,
    'Content-Type': 'application/json'
  }
});

const script = `
  Did you know that 90% of startups fail in their first year?
  Here are 3 things the successful 10% do differently.
  Number 1: They talk to customers before building anything.
  Number 2: They launch ugly and iterate fast.
  Number 3: They obsess over retention, not acquisition.
  Follow for more startup insights every day.
`;

const response = await client.post('/videos/generate', {
  script: script,
  format: "9:16",           // vertical for Reels / TikTok / Shorts
  duration: "short",        // 15–60 seconds
  style: "dynamic",         // energetic cuts and transitions
  voiceover: {
    enabled: true,
    voice: "en-US-male-1",  // choose from available voices
    speed: 1.1              // slightly faster for short-form
  },
  captions: {
    enabled: true,
    style: "bold-bottom",   // TikTok-style captions
    highlight: true         // highlight word as it's spoken
  },
  music: {
    enabled: true,
    mood: "upbeat",
    volume: 0.3             // background music volume (0–1)
  },
  branding: {
    watermark: false
  }
});

const videoId = response.data.videoId;
console.log("Video generation started. ID:", videoId);
```

---

### Poll for Completion and Get Download URL

```javascript
async function waitForVideo(videoId, maxWaitMs = 120000) {
  const start = Date.now();

  while (Date.now() - start < maxWaitMs) {
    await new Promise(r => setTimeout(r, 5000)); // poll every 5s

    const status = await client.get(`/videos/${videoId}/status`);
    const { state, progress, exportUrl } = status.data;

    console.log(`Status: ${state} — ${progress}% complete`);

    if (state === "completed") {
      console.log("Video ready:", exportUrl);
      return exportUrl;
    }

    if (state === "failed") {
      throw new Error("Video generation failed — check your script and settings");
    }
  }

  throw new Error("Timeout — video took too long to generate");
}

const downloadUrl = await waitForVideo(videoId);
```

---

### Full Pipeline: Script → Video → Download

```javascript
import axios from 'axios';
import { writeFileSync } from 'fs';

async function scriptToShortVideo(script, outputPath = './output.mp4') {
  const client = axios.create({
    baseURL: 'https://api.invideo.io/v1',
    headers: { Authorization: `Bearer ${process.env.INVIDEO_API_KEY}` }
  });

  // 1 — Start generation
  const { data } = await client.post('/videos/generate', {
    script,
    format: "9:16",
    duration: "short",
    style: "dynamic",
    voiceover: { enabled: true, voice: "en-US-female-1", speed: 1.05 },
    captions: { enabled: true, style: "bold-bottom", highlight: true },
    music: { enabled: true, mood: "upbeat", volume: 0.25 }
  });

  const videoId = data.videoId;
  console.log(`Generation started — ID: ${videoId}`);

  // 2 — Wait for completion
  let exportUrl = null;
  while (!exportUrl) {
    await new Promise(r => setTimeout(r, 6000));
    const status = await client.get(`/videos/${videoId}/status`);
    if (status.data.state === "completed") exportUrl = status.data.exportUrl;
    if (status.data.state === "failed") throw new Error("Generation failed");
    console.log(`Progress: ${status.data.progress}%`);
  }

  // 3 — Download the video
  const videoStream = await axios.get(exportUrl, { responseType: 'arraybuffer' });
  writeFileSync(outputPath, videoStream.data);
  console.log(`Video saved to ${outputPath}`);

  return { videoId, exportUrl, localPath: outputPath };
}

// Usage
await scriptToShortVideo(
  "3 productivity hacks that changed my life. Number 1: Time blocking...",
  "./my-reel.mp4"
);
```

---

### Batch Generate Multiple Videos

```javascript
const scripts = [
  { topic: "morning routine tips",     voice: "en-US-female-1", mood: "calm" },
  { topic: "5 foods to boost energy",  voice: "en-US-male-1",   mood: "upbeat" },
  { topic: "how to learn faster",      voice: "en-US-female-2", mood: "inspiring" }
];

const jobs = await Promise.all(
  scripts.map(s =>
    client.post('/videos/generate', {
      script: s.topic,
      format: "9:16",
      duration: "short",
      style: "dynamic",
      voiceover: { enabled: true, voice: s.voice },
      music: { enabled: true, mood: s.mood, volume: 0.3 },
      captions: { enabled: true, style: "bold-bottom" }
    })
  )
);

const videoIds = jobs.map(j => j.data.videoId);
console.log("All jobs started:", videoIds);
```

---

## Video Creation Workflow

When asked to create a short-form video, Claude will:

1. **Analyze** the script or topic provided by the user
2. **Optimize** the script for short-form pacing (hook in first 3 seconds)
3. **Select** the right style, voice, music mood, and caption style
4. **Call** the InVideo API to generate the video
5. **Poll** the status endpoint until the video is ready
6. **Return** the download URL or save the MP4 locally
7. **Suggest** platform-specific tweaks (TikTok vs Reels vs Shorts)

---

## Platform-Specific Settings

| Platform | Format | Duration | Caption Style | Music |
|---|---|---|---|---|
| TikTok | 9:16 | 15–60s | Bold bottom, word highlight | Upbeat / trending |
| Instagram Reels | 9:16 | 15–90s | Bold bottom or centered | Upbeat / chill |
| YouTube Shorts | 9:16 | 15–60s | Clean bottom | Optional |
| LinkedIn Video | 16:9 or 1:1 | 30–90s | Professional, top-aligned | Subtle / none |

---

## Script Optimization Tips (Claude Will Apply These)

- **Hook in 3 seconds** — start with a bold claim, question, or shocking stat
- **One idea per video** — don't try to cover too much ground
- **Short sentences** — 8–12 words max per caption line
- **Call to action at the end** — "Follow for more", "Comment below", "Save this"
- **Conversational tone** — write how people talk, not how they write
- **Numbers perform** — "3 tips", "5 mistakes", "1 rule" always outperform vague titles

---

## Normalized Output Schema

```json
{
  "videoId": "iv_7f3k29xm",
  "title": "3 Startup Lessons Nobody Tells You",
  "platform": "tiktok",
  "format": "9:16",
  "durationSeconds": 42,
  "exportUrl": "https://cdn.invideo.io/exports/iv_7f3k29xm.mp4",
  "captions": true,
  "voiceover": "en-US-male-1",
  "musicMood": "upbeat",
  "createdAt": "2025-02-25T10:00:00Z",
  "status": "completed"
}
```

---

## Best Practices

- Always **start with a strong hook** — the first 2–3 seconds determine if users keep watching
- Keep scripts between **120–200 words** for a 30–60 second video
- Use **bold captions with word highlighting** — it significantly increases watch time
- Set music volume to **0.2–0.3** so it never overpowers the voiceover
- Generate **3–5 variations** of the same script with different styles to A/B test
- For TikTok, use a **slightly faster voiceover speed** (1.1x) to match platform energy
- Always review the video before publishing — AI generations may need minor tweaks

---

## Error Handling

```javascript
try {
  const response = await client.post('/videos/generate', payload);
  return response.data.videoId;
} catch (error) {
  if (error.response?.status === 401) throw new Error("Invalid InVideo API key");
  if (error.response?.status === 429) throw new Error("Rate limit hit — wait before retrying");
  if (error.response?.status === 400) throw new Error(`Bad request: ${error.response.data.message}`);
  throw error;
}
```

---

## Requirements

- An InVideo account → https://invideo.sjv.io/TBB
- A plan with **API access** enabled (Business plan or above)
- A valid **API Key** from your InVideo settings
- Node.js 18+ and `axios` for API calls
- Optional: `ffmpeg` locally if you need to post-process or compress the exported MP4
