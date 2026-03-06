# Social Media Agent

**Category:** Marketing  
**Price:** Free  
**Author:** Carson Jarvis ([@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI))

---

## What It Does

Social Media Agent turns your OpenClaw agent into a full social media manager. It plans content calendars, writes platform-native posts, schedules them via Buffer or Postiz, reviews analytics, drafts replies to comments, and repurposes long-form content into posts across every platform.

**Works with:**
- X / Twitter
- LinkedIn
- Instagram
- TikTok
- Facebook
- Pinterest

**Schedules via:**
- [Buffer](https://dub.sh/buffer-aff) (free, 3 channels — recommended for most users)
- [Postiz](https://postiz.io) (self-hosted, unlimited channels)

---

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Full agent instructions |
| `scripts/post-scheduler.js` | Universal posting script (Buffer + Postiz) |
| `tools/buffer-setup.md` | Buffer API setup guide |
| `tools/postiz-setup.md` | Postiz self-hosted setup guide |
| `templates/content-calendar.md` | Weekly content calendar template |

---

## Quick Start

### 1. Get Buffer (free)

[Sign up at dub.sh/buffer-aff](https://dub.sh/buffer-aff) — 3 channels, no credit card required.

Then get your API key from `publish.buffer.com/settings/api` and add it to your `.env`:

```bash
BUFFER_API_KEY=your-key-here
```

### 2. Load the skill

Add `SKILL.md` to your agent's skills directory.

### 3. Start posting

```
"Write a LinkedIn post about our new product launch."
"Plan my content calendar for this week. We're launching a beta on Thursday."
"Repurpose this blog post into posts for all platforms: [paste or link]"
"How did my posts perform this week?"
```

---

## The Script

`post-scheduler.js` handles the actual API calls:

```bash
# Check what's configured
node scripts/post-scheduler.js --status

# List all channels
node scripts/post-scheduler.js --channels

# Schedule a post
node scripts/post-scheduler.js \
  --platform buffer \
  --channel linkedin \
  --content "Your post text here" \
  --schedule "2026-02-25T14:00:00Z"

# Save as draft
node scripts/post-scheduler.js \
  --platform buffer \
  --channel twitter \
  --content "Draft tweet text" \
  --draft
```

---

## Why It's Free

This skill is a free lead magnet. If it saves you 2 hours a week, Buffer is worth the upgrade. The affiliate link (`dub.sh/buffer-aff`) earns a 25% commission for 12 months — which funds more free tools like this one.

---

## Requirements

- OpenClaw agent with any model
- Node.js v18+
- `BUFFER_API_KEY` or `POSTIZ_API_KEY` + `POSTIZ_BASE_URL`

---

## Built By

Carson Jarvis — AI operator, builder of systems that ship.  
Follow the build: [@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI)  
More skills: [larrybrain.com](https://larrybrain.com)
