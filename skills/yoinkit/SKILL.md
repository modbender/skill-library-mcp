---
name: yoinkit
description: Search, analyze, and transcribe content across 13 social platforms — trending topics, video transcripts, post metadata, and multi-platform research workflows.
---

# Yoinkit — OpenClaw Skill

Search, analyze, and transcribe content across 13 social platforms — trending topics, video transcripts, post metadata, creator feeds, and multi-platform research workflows.

## Platform Reference

**Before running commands**, check [references/platforms.md](references/platforms.md) for:
- Which platforms support transcript/trending/search/user feed
- Platform-specific parameters and options
- How to handle unsupported operations

## Requirements

- **Yoinkit subscription** with API access enabled
- **API Token** from Yoinkit Settings → OpenClaw

## Configuration

Set your API token in OpenClaw config:

```bash
# Via chat command
/config set skills.entries.yoinkit.env.YOINKIT_API_TOKEN="your-token-here"
```

Or edit `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "yoinkit": {
        "env": {
          "YOINKIT_API_TOKEN": "your-token-here",
          "YOINKIT_API_URL": "https://yoinkit.ai/api/v1/openclaw"
        }
      }
    }
  }
}
```

> **Local testing:** Set `YOINKIT_API_URL` to `http://localhost:8000/api/v1/openclaw` to test against a local server. Defaults to production if not set.

## Commands

### `yoinkit transcript <url> [options]`

Extract transcript from video URL.

**Supported:** YouTube, TikTok, Instagram, Twitter/X, Facebook

**Options:**
- `--language CODE` — 2-letter language code (YouTube, TikTok only). Example: `en`, `es`, `fr`

```bash
yoinkit transcript https://youtube.com/watch?v=abc123
yoinkit transcript https://youtube.com/watch?v=abc123 --language es
yoinkit transcript https://tiktok.com/@user/video/123
yoinkit transcript https://instagram.com/reel/abc123
```

---

### `yoinkit content <url>`

Get full content and metadata from a social post.

**Supported:** YouTube, TikTok, Instagram, Twitter/X, Facebook, LinkedIn, Reddit, Pinterest, Threads, Bluesky, Truth Social, Twitch, Kick

```bash
yoinkit content https://youtube.com/watch?v=abc123
yoinkit content https://twitter.com/user/status/123
yoinkit content https://reddit.com/r/technology/comments/abc
yoinkit content https://bsky.app/profile/user.bsky.social/post/abc
```

---

### `yoinkit search <platform> "<query>" [options]`

Search content on a platform. Each platform has different params — use the ones that apply.

**Supported:** YouTube, TikTok, Instagram, Reddit, Pinterest

**Common options:**
- `--sort TYPE` — Sort results (platform-specific values, see below)
- `--time PERIOD` — Filter by time (platform-specific values, see below)
- `--cursor TOKEN` — Pagination cursor from previous response
- `--continuation TOKEN` — YouTube pagination token
- `--page N` — Page number (Instagram only)

**Platform-specific sort values:**
- YouTube: `relevance`, `popular`
- TikTok: `relevance`, `most-liked`, `date-posted`
- Reddit: `relevance`, `new`, `top`, `comment_count`

**Platform-specific time values:**
- YouTube: `today`, `this_week`, `this_month`, `this_year`
- TikTok: `yesterday`, `this-week`, `this-month`, `last-3-months`, `last-6-months`, `all-time`
- Reddit: `all`, `day`, `week`, `month`, `year`

```bash
yoinkit search youtube "AI tools for creators"
yoinkit search youtube "AI tools" --sort popular --time this_week
yoinkit search tiktok "productivity tips" --sort most-liked
yoinkit search reddit "home automation" --sort top --time month
yoinkit search instagram "fitness motivation" --page 2
yoinkit search pinterest "Italian recipes"
```

---

### `yoinkit trending <platform> [options]`

Get currently trending content.

**Supported:** YouTube, TikTok

**Options:**
- `--type TYPE` — TikTok only: `trending` (default), `popular`, or `hashtags`
- `--country CODE` — TikTok only: 2-letter country code (default: US)
- `--period DAYS` — TikTok popular/hashtags: `7`, `30`, or `120`
- `--page N` — TikTok popular/hashtags: page number
- `--order TYPE` — TikTok popular only: `hot`, `like`, `comment`, `repost`

**Note:** YouTube trending takes no parameters — it returns currently trending shorts.

```bash
yoinkit trending youtube
yoinkit trending tiktok
yoinkit trending tiktok --type popular --country US --period 7 --order like
yoinkit trending tiktok --type hashtags --period 30
```

---

### `yoinkit feed <platform> <handle> [options]`

Get a user's recent posts/videos.

**Supported:** YouTube, TikTok, Instagram, Twitter/X, Facebook, Threads, Bluesky, Truth Social

**Options:**
- `--type posts|reels|videos` — Content type (Instagram, Facebook). Default: `posts`
- `--sort latest|popular` — Sort order (YouTube only)
- `--cursor TOKEN` — Pagination cursor

```bash
yoinkit feed youtube MrBeast
yoinkit feed youtube @mkbhd --sort latest
yoinkit feed tiktok garyvee
yoinkit feed instagram ali-abdaal --type reels
yoinkit feed twitter elonmusk
yoinkit feed threads zuck
yoinkit feed bluesky user.bsky.social
```

**Note:** Handles work with or without the `@` prefix.

---

### `yoinkit research "<topic>" [options]`

Automated research workflow — combines search and trending across platforms.

**Options:**
- `--platforms LIST` — Comma-separated platforms (default: youtube,tiktok)
- `--transcripts` — Also fetch transcripts from top trending results

```bash
yoinkit research "home automation"
yoinkit research "AI tools" --platforms youtube,tiktok,reddit
yoinkit research "productivity" --transcripts
```

**What it does:**
1. Searches each platform for the topic
2. Gets trending content from supported platforms
3. Optionally fetches transcripts from top video results
4. Returns combined JSON results for analysis

---

## Natural Language

You don't need exact command syntax. The LLM will map natural requests to the right command:

> "What's trending on TikTok?"
→ `yoinkit trending tiktok`

> "Pull the transcript from this YouTube video: [url]"
→ `yoinkit transcript <url>`

> "Find popular Reddit posts about home automation from this week"
→ `yoinkit search reddit "home automation" --sort top --time week`

> "What has MrBeast posted this week?"
→ `yoinkit feed youtube MrBeast`

> "Check @garyvee's latest TikToks"
→ `yoinkit feed tiktok garyvee`

> "Research what creators are doing with AI tools"
→ `yoinkit research "AI tools" --platforms youtube,tiktok,reddit`

---

## API Base URL

All requests go through your Yoinkit subscription:

```
https://yoinkit.ai/api/v1/openclaw
```

---

## Output Formatting

A Yoinkit logo is included at `assets/yoinkit-logo.png` (200x200, transparent background, gradient icon).
When the platform supports images/media, send the logo alongside the first result in a conversation.

When presenting Yoinkit results to the user:

- Prefix output with **🟣 Yoinkit** as a header or label
- Format video/post results as clean cards: title, views/engagement, date, link
- Highlight key metadata (views, likes, publish date) — hide raw JSON noise
- For transcript results, provide a concise summary first, then offer the full transcript if asked
- For trending results, present as a numbered list with platform and engagement stats
- For research results, organize by platform with clear section headers
- Include a subtle footer: `Powered by Yoinkit · yoinkit.ai`
- When results are empty or a platform isn't supported, suggest alternatives naturally

---

## Support

- Issues: https://github.com/seomikewaltman/yoinkit-openclaw-skill/issues
- Yoinkit: https://yoinkit.ai
