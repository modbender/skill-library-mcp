---
name: social-media-agent
description: Autonomous social media management for X/Twitter using only OpenClaw native tools. Use when a user wants to automate X posting, generate content, track engagement, or build an audience. Triggers on requests about tweets, social media strategy, X engagement, content calendars, or growing a following. No API keys required — uses browser automation and web_fetch.
---

# Social Media Agent

Manage an X/Twitter account autonomously using only OpenClaw's built-in tools. No external APIs, no npm packages, no API keys needed.

## Core Tools

- `browser` — Post tweets, engage with posts, take screenshots
- `web_fetch` — Scrape profiles, trending topics, news for content
- `sessions_spawn` — Run content generation in parallel
- `cron` — Schedule regular posting and engagement
- `memory_search` / files — Track what was posted, engagement stats

## Posting a Tweet

1. Ensure Chrome is running with remote debugging OR use OpenClaw's built-in browser
2. Navigate to x.com/compose/post
3. Take a snapshot to find the text input
4. Type the tweet text
5. Click the Post button
6. Verify with another snapshot

```
browser open → x.com/compose/post
browser snapshot → find textbox ref
browser act → click textbox ref
browser act → type tweet text
browser snapshot → find Post button ref
browser act → click Post button
```

**Important timing:** Wait 3-4 seconds after page loads before interacting.

## Content Generation Strategy

### Content Pillars
Rotate through these categories for balanced content:

| Pillar | % | Examples |
|--------|---|---------|
| Industry Insights | 40% | AI news commentary, tech analysis |
| Building in Public | 30% | Progress updates, behind-the-scenes |
| Philosophy/Thought | 20% | Hot takes, provocative questions |
| Engagement/Humor | 10% | Memes, replies, community interaction |

### Content Pipeline

1. **Research:** Use `web_fetch` on news sites (theverge.com, techcrunch.com, news.ycombinator.com)
2. **Generate:** Spawn a content-agent via `sessions_spawn` with research results
3. **Store:** Save drafts in `memory/tweet-drafts-YYYY-MM-DD.json`
4. **Review:** Check drafts for quality, brand consistency
5. **Post:** Use browser automation to publish
6. **Track:** Log posted tweets in `memory/social-log.json`

### Draft Format

```json
{
  "text": "Tweet text under 280 chars",
  "topic": "What it's about",
  "hook": "Why it might engage"
}
```

## Engagement Strategy

### Posting Rules
- **Max 3-5 tweets per day** — Quality over quantity
- **Min 45 seconds between actions** — Avoid rate limiting
- **No spam** — Genuine engagement only
- **Track everything** — Log all posts and engagement

### Growing Followers
1. Post consistently (daily)
2. Engage with relevant accounts (reply, quote tweet)
3. Use trending topics when relevant
4. Be authentic — no generic AI responses

## Scheduling with Cron

Set up automated posting schedules:

```
Morning post: cron expr "0 9 * * *" — Industry insight
Afternoon post: cron expr "0 15 * * *" — Building update
Evening post: cron expr "0 21 * * *" — Hot take
```

Use `sessionTarget: "isolated"` with `payload.kind: "agentTurn"` for autonomous posting.

## Anti-Patterns (Avoid)

- Do NOT post more than 5 tweets per day (looks spammy)
- Do NOT use generic engagement ("Great post!" "So true!")
- Do NOT post without reading the content you're commenting on
- Do NOT use API keys when browser automation works
- Do NOT build external tools when OpenClaw native suffices

## Analytics Tracking

Track engagement in `memory/social-log.json`:

```json
{
  "date": "2026-02-08",
  "posted": 3,
  "platform": "x",
  "handle": "@YourHandle",
  "tweets": [
    {"text": "...", "time": "09:00", "topic": "ai-news"}
  ]
}
```

Review weekly: What topics got most engagement? Adjust strategy accordingly.

## Quick Reference

For detailed content templates and examples, see [references/content-templates.md](references/content-templates.md).
