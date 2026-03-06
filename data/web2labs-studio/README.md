<p align="center">
  <a href="https://www.web2labs.com">
    <img src="https://www.web2labs.com/assets/images/logo.svg" alt="Web2Labs Studio" width="320" />
  </a>
</p>

<h3 align="center">AI video editing - turns videos & streams into<br/>complete YouTube videos & shorts</h3>

<p align="center">
  <a href="https://www.web2labs.com/openclaw"><strong>Landing Page</strong></a> · 
  <a href="https://www.web2labs.com"><strong>Web App</strong></a> · 
  <a href="https://www.web2labs.com/api/v1/docs"><strong>API Docs</strong></a> · 
  <a href="https://github.com/web2labs/web2labs-studio-examples"><strong>Examples</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-skill-blue?style=flat-square" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/node-%3E%3D18-brightgreen?style=flat-square" alt="Node.js 18+" />
  <img src="https://img.shields.io/badge/tools-20-orange?style=flat-square" alt="20 MCP Tools" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License" />
</p>

---

## What is Web2Labs Studio?

**Web2Labs Studio** is a cloud video editing platform that turns raw recordings into publish-ready content - automatically. No timeline. No editing software. Just upload and get back:

<table>
<tr>
<td width="33%" align="center">

**Edited Video**

Dead air removed. Pacing tightened. Dynamic zoom punch-ins. Animated captions. Audio normalized. Every second earns its place.

</td>
<td width="33%" align="center">

**25+ Shorts**

Vertical clips auto-extracted from your recording, ready to post on YouTube Shorts, TikTok, Instagram Reels, and X.

</td>
<td width="33%" align="center">

**Full Meta Package**

AI-generated titles, descriptions, tags, chapters, pinned comments, and A/B/C thumbnail variants - everything you need to publish.

</td>
</tr>
</table>



### High Retention Cut vs. Normal Video

<table>
<tr>
<td align="center"><strong>Studio Output</strong></td>
<td align="center"><strong>Raw Recording</strong></td>
</tr>
<tr>
<td align="center">
<img src="assets/retention-cut-sample.gif" alt="High retention cut by Studio" width="400" />
<br/><em>Dead air cut. Pacing tightened. Every second earns its place.</em>
</td>
<td align="center">
<img src="assets/normal-cut-sample.gif" alt="Normal unedited video" width="400" />
<br/><em>Silences, filler, and rambles. Viewers scroll past.</em>
</td>
</tr>
</table>

### See the difference

<table>
<tr>
<td align="center"><strong>Studio Thumbnail</strong></td>
<td align="center"><strong>Amateur Thumbnail</strong></td>
</tr>
<tr>
<td align="center">
<img src="https://www.web2labs.com/assets/studio/thumbnails/thumbnail_1.webp" alt="Studio-generated thumbnail" width="400" />
<br/><em>AI-generated, brand-colored, click-worthy.</em>
</td>
<td align="center">
<img src="https://www.web2labs.com/assets/studio/thumbnails/thumbnail-amateur.webp" alt="Amateur thumbnail" width="400" />
<br/><em>Generic frame grab. Viewers scroll right past.</em>
</td>
</tr>
</table>

> [See the full interactive comparison on web2labs.com →](https://www.web2labs.com)

### Who is it for?

YouTube creators, Twitch streamers, podcasters, educators, coaches - anyone who records video and wants it edited without the grind. Studio handles the tedious parts (cutting silence, adding captions, generating shorts) so you can focus on creating.

---

## This Skill: Studio in Your Terminal

This OpenClaw skill gives you the **full power of Studio** from your AI assistant. Talk to your agent, and it handles everything:

```
You:   "Edit my latest recording as a YouTube video"
Agent: Uploading ~/Desktop/recording.mp4... Processing with 'youtube' preset.
       Transcribing → Cutting → Rendering... Done in 3m 42s.
       
       Downloaded to ~/studio-exports/my-recording/:
       ├── main.mp4              (edited video, 18:24)
       ├── shorts/
       │   ├── short-1.mp4       (0:58)
       │   ├── short-2.mp4       (0:45)
       │   └── ... 23 more
       ├── subtitles.srt
       └── transcription.json
       
       Want me to generate thumbnail variants? (10 Creator Credits)
```

### From URL - no download needed

```
You:   "Make shorts from https://youtube.com/watch?v=dQw4w9WgXcQ"
Agent: Downloading via yt-dlp... Uploading to Studio...
       Processing with 'shorts-only' preset... Done.
       27 shorts ready for download.
```

---

## Quick Start

**3 commands. 2 free credits. No credit card.**

```bash
# 1. Install the skill
clawhub install @web2labs/studio

# 2. Set up your account (sends a magic link to your email)
"Run studio_setup with my email hello@example.com"

# 3. Edit your first video
"Edit ~/Desktop/my-recording.mp4 as a youtube video"
```

That's it. Your first two videos are free.

---

## What You Get: The Full Package

Every video processed through Studio returns a complete content package:

### Edited Video
- **Smart jump-cuts** - AI removes dead air, filler words, and awkward pauses while preserving meaning
- **Dynamic zoom punch-ins** - automatic Ken Burns-style zooms at the right moments to hold attention
- **Animated captions** - word-level subtitles styled to your brand, because most viewers watch on mute
- **Tighter pacing** - rambles tightened, momentum maintained, every minute feels intentional
- **Audio normalization** - broadcast-standard loudness (-14 LUFS) so you sound professional
- **High-quality render** - CRF 18, ready to upload directly

### Vertical Shorts
- **25+ shorts per recording** - auto-extracted highlight clips with clean hooks and payoffs
- **Multi-platform ready** - formatted for YouTube Shorts, TikTok, Instagram Reels, and X
- **One recording → one week of content** - never go dark on social media again

### Meta Package
- **A/B/C thumbnail variants** - AI-generated, brand-colored thumbnails you can test
- **Titles, descriptions, tags** - optimized for search and click-through
- **Chapters** - auto-generated from your transcript so viewers can jump in
- **Pinned comment** - ready to copy-paste for engagement

---

## 8 Presets for Every Content Style

| Preset | Best For | What It Does |
|--------|----------|-------------|
| `youtube` | Standard YouTube videos | Subtitles + shorts + music + full meta |
| `quick` | Fast turnaround | Clean cuts, no extras, fastest render |
| `shorts-only` | Social media blitz | Only generates vertical shorts |
| `podcast` | Talking-head podcasts | Soft cuts, subtitles, no zoom |
| `gaming` | Streams & gameplay | Dynamic zoom, gaming-style pacing |
| `tutorial` | Educational content | Gentle edits, preserves explanations |
| `vlog` | Daily vlogs | Balanced pacing, natural feel |
| `cinematic` | High production | Premium settings, slower pacing |

Mix presets with custom overrides for full control:

```
"Edit my video with the youtube preset but disable music and set subtitle style to minimal"
```

---

## 20 Tools at Your Fingertips

<details>
<summary><strong>Core Workflow</strong></summary>

| Tool | What It Does |
|------|-------------|
| `studio_setup` | One-time account setup via magic link or existing API key |
| `studio_upload` | Upload local files or URLs (YouTube, Twitch, Vimeo) for processing |
| `studio_status` | Check current project processing status |
| `studio_poll` | Smart polling - waits for completion with progress updates |
| `studio_results` | Get output URLs and metadata for a completed project |
| `studio_download` | Download all outputs to your local filesystem |
| `studio_projects` | List your recent projects |
| `studio_delete` | Delete a project and free up storage |
| `studio_watch` | Watch YouTube/Twitch channels and auto-process new uploads |

</details>

<details>
<summary><strong>Premium Features</strong></summary>

| Tool | What It Does |
|------|-------------|
| `studio_thumbnails` | Generate A/B/C thumbnail variants for any completed project |
| `studio_rerender` | Re-render with different settings - no re-upload needed (first free, then 15 CC) |
| `studio_brand` | Save your brand colors, fonts, and identity for consistent output |
| `studio_brand_import` | Auto-import brand settings from your YouTube or Twitch channel |
| `studio_assets` | Upload reusable intros, outros, and watermarks |
| `studio_analytics` | See your usage stats and time saved |

</details>

<details>
<summary><strong>Credits & Pricing</strong></summary>

| Tool | What It Does |
|------|-------------|
| `studio_credits` | Check your API credit and Creator Credit balances |
| `studio_pricing` | Get current pricing for all features and bundles |
| `studio_estimate` | Estimate exact cost before uploading |
| `studio_feedback` | Report bugs, request features, or ask questions |
| `studio_referral` | Get your referral code - earn 5 free credits per signup |

</details>

---

## Pricing

**2 free credits on signup. No credit card required.**

Every video costs **1 API credit** (or 2 for rush priority). Premium features like thumbnails use Creator Credits.

| Bundle | Credits | Price | Per Video |
|--------|---------|-------|-----------|
| **Free** | 2 | €0 | €0 |
| Casual | 10 | €22.99 | €2.30 |
| Starter | 20 | €39.99 | €2.00 |
| Pro | 100 | €199.99 | €2.00 |
| Studio | 250 | €449.99 | €1.80 |
| Agency | 1000 | €1,699.99 | €1.70 |

**Subscribers** (Starter €20/mo, Creator €50/mo, Legend €800 lifetime) can use their monthly project allocation through the skill - as low as €0.50/video on Creator tier.

[View full pricing →](https://www.web2labs.com/pricing)

---

## Referral Program

Every user gets a unique referral code. Share it and both you and your friend get **5 free API credits** (60-day expiry).

```
You:   "What's my referral code?"
Agent: Your code is STUDIO-K7M3
       Share: https://www.web2labs.com/ref/STUDIO-K7M3
       
       Stats: 3 referrals, 15 credits earned, 7 slots remaining
```

Earn up to **50 free credits** (10 referrals). That's 50 fully edited videos - for free.

---

## Advanced Workflows

### Brand Consistency

Set up your brand once, and every video matches your style:

```
You:   "Import my brand from https://youtube.com/@mychannel"
Agent: Imported from YouTube: primary #1a73e8, secondary #ff6f00,
       identity: "Tech educator focused on practical tutorials"
       Applied to your brand kit. All future videos will use these settings.
```

### Batch Processing

```
You:   "Process all .mp4 files in ~/recordings/ as youtube videos"
Agent: Found 5 files. This will consume 5 API credits. Proceed?
You:   "Yes"
Agent: Processing 5 videos... [████████░░] 3/5 complete
```

### Fire-and-Forget with Webhooks

```
You:   "Upload this video and send results to https://my-server.com/callback"
Agent: Uploaded with webhook. You'll receive a signed callback at
       project.completed - no need to poll.
```

### Re-render Without Re-upload

```
You:   "Add subtitles to that last video"
Agent: Re-rendering with subtitles enabled. First re-render is free!
       No re-upload needed - reusing existing analysis.
```

### Watch Mode - Auto-Process New Uploads

Set up a watcher on your channel and Studio processes every new upload automatically:

```
You:   "Watch my YouTube channel https://youtube.com/@mychannel for new videos"
Agent: Watcher created for 'mychannel' with youtube preset.
       Max 5 uploads/day, skipping videos over 2 hours.
       
       Run "check my watchers" to poll for new videos, or set up a cron job.
```

```
You:   "Check my watchers"
Agent: Checking 1 watcher...
       
       mychannel: 2 new videos found
       ├── "Building a REST API" (24:31) → project p_abc123, uploading...
       └── "React Server Components" (18:07) → project p_def456, uploading...
       
       2 videos uploaded and processing. Use studio_poll to track progress.
```

Works with YouTube channels, YouTube live VODs, and Twitch channels. Requires `yt-dlp`.

---

## Spend Control

You're always in control of what gets spent. Configure your spend policy:

| Mode | Behavior |
|------|----------|
| `auto` (default) | Proceeds without prompts unless auto-caps are exceeded |
| `smart` | Confirms high-cost or low-balance actions |
| `explicit` | Confirms every credit-spending action |

```bash
# Set in your environment
export WEB2LABS_SPEND_POLICY=explicit
```

---

## Requirements

- **Node.js 18+**
- **Web2Labs account** - [sign up free](https://www.web2labs.com/openclaw) (2 free credits, no card)
- **Optional:** `yt-dlp` for URL-based workflows and watch mode (`brew install yt-dlp`)

---

## Configuration

The skill reads from environment variables or OpenClaw config (`~/.openclaw/openclaw.json`):

| Variable | Default | Description |
|----------|---------|-------------|
| `WEB2LABS_API_KEY` | - | Your API key (starts with `sk_live_`) |
| `WEB2LABS_API_ENDPOINT` | `https://www.web2labs.com` | API base URL |
| `WEB2LABS_DEFAULT_PRESET` | `youtube` | Default preset when none specified |
| `WEB2LABS_DOWNLOAD_DIR` | `~/studio-exports` | Where downloads are saved |
| `WEB2LABS_SPEND_POLICY` | `auto` | Spend confirmation mode |

---

## Security

- API keys are stored locally in your OpenClaw config - never sent to third parties
- Auth headers are stripped for non-Web2Labs download URLs - no credential leakage to CDN/S3
- The skill never logs or displays full API key values
- URL downloads happen locally on your machine via yt-dlp - files never touch third-party servers
- All API communication uses HTTPS
- Webhook callbacks are HMAC-SHA256 signed with your secret
- Remote filenames are sanitized to prevent path traversal

For the full security posture and vulnerability reporting, see [SECURITY.md](SECURITY.md).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and pull request guidelines.

---

## Links

- **Product:** [web2labs.com](https://www.web2labs.com) - see real before/after examples
- **OpenClaw Landing:** [web2labs.com/openclaw](https://www.web2labs.com/openclaw) - skill-specific info + install
- **API Documentation:** [web2labs.com/api/v1/docs](https://www.web2labs.com/api/v1/docs) - Swagger/OpenAPI reference
- **Examples:** [github.com/web2labs/web2labs-studio-examples](https://github.com/web2labs/web2labs-studio-examples)
- **Support:** Use `studio_feedback` or email [hello@web2labs.com](mailto:hello@web2labs.com)

---

<p align="center">
  <strong>Record once. Publish everywhere.</strong><br/>
  <a href="https://www.web2labs.com/openclaw">Start free →</a>
</p>
