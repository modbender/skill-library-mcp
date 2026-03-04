---
name: fxtwitter
description: Fetch tweet/post data from X (Twitter) links using the fxTwitter API (api.fxtwitter.com). Use when a user sends an x.com or twitter.com URL and wants to read, summarize, or extract tweet content. No auth required. Returns full tweet metadata including text, author, media, and engagement stats.
---

# fxTwitter

Fetch tweet data from an X/Twitter URL without auth or browser automation.

## Endpoint

```
GET https://api.fxtwitter.com/:tweetId
```

Extract the tweet ID from the URL:
- `https://x.com/user/status/1234567890` → ID: `1234567890`
- `https://twitter.com/user/status/1234567890` → ID: `1234567890`

## Usage

```bash
curl -s "https://api.fxtwitter.com/1234567890" | jq '.tweet'
```

Key fields in `.tweet`:
- `.text` — tweet content
- `.author.name` / `.author.screen_name`
- `.created_at`
- `.likes`, `.retweets`, `.replies`
- `.media.photos[]`, `.media.videos[]`
- `.url` — canonical URL

## Output Format

When presenting a tweet to the user:
- Lead with TL;DR if the tweet is long
- Use bullet points for key info
- Keep it concise — no filler
