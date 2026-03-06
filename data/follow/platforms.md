# Platform Integration

## Overview

Each platform has different access methods and limitations.

---

## Twitter/X

**Access:** API (limited free tier) or scraping
**Best for:** Real-time thoughts, announcements, threads
**Limitations:** API rate limits, content deletion

**Setup:**
- Use API for accounts with modest activity
- Consider Nitter for scraping fallback
- Archive important tweets (they get deleted)

**What to capture:**
- Original tweets (not RTs unless commenting)
- Threads (flag as high-value)
- Replies to known accounts

---

## YouTube

**Access:** yt-dlp (reliable), YouTube API
**Best for:** Long-form content, podcasts, tutorials
**Limitations:** Processing time for transcription

**Setup:**
- Monitor channel RSS: `https://www.youtube.com/feeds/videos.xml?channel_id=XXXXX`
- Auto-transcribe new uploads
- Extract chapters if available

**What to capture:**
- New uploads from subscribed channels
- Guest appearances (search by name)
- Timestamps for key moments

---

## RSS/Blogs

**Access:** Direct fetch (most reliable)
**Best for:** Long-form writing, official announcements
**Limitations:** Some sites don't have RSS

**Common patterns:**
- Substack: `newsletter.substack.com/feed`
- Medium: `medium.com/feed/@username`
- Ghost: `blog.com/rss/`
- WordPress: `site.com/feed/`

**What to capture:**
- Full article or summary depending on length
- Publication date, author
- Key quotes

---

## GitHub

**Access:** API (generous limits)
**Best for:** Release tracking, contributor activity
**Limitations:** Signal buried in noise

**Monitor:**
- Releases for critical dependencies
- Security advisories
- Commits from specific contributors
- Stars/forks velocity

**What to capture:**
- Release notes for dependencies you use
- Breaking changes, migration guides
- Security patches

---

## LinkedIn

**Access:** Very limited (mostly manual)
**Best for:** Professional moves, company updates
**Limitations:** No good API, requires login

**Workarounds:**
- RSS tools (feed43, rss.app) for public profiles
- Manual check schedule for key people
- Focus on job change alerts

---

## Reddit/HN

**Access:** API or RSS
**Best for:** Discussion, emerging trends
**Limitations:** High noise ratio

**Reddit:**
- Subreddit RSS: `reddit.com/r/subreddit/.rss`
- User RSS: `reddit.com/user/username/.rss`

**Hacker News:**
- Front page RSS: various services
- Algolia API for search

**What to capture:**
- Top posts matching keywords
- Discussions with high engagement
- Mentions of tracked entities

---

## Substack/Newsletters

**Access:** RSS (reliable)
**Best for:** Analysis, opinions, exclusive content
**Limitations:** Paywalled content needs subscription

**Setup:**
- RSS: `publication.substack.com/feed`
- Most have free tier for some posts
- Worth paying for high-value sources

---

## Telegram

**Access:** Join channels, use bots
**Best for:** Real-time updates, leaks, crypto
**Limitations:** Requires Telegram account

**Options:**
- Join channels directly
- Forward to aggregator bot
- Export with Telegram export tools
