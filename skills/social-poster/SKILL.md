---
description: Post to social media via VibePost API. Use when posting to Twitter/X, sharing updates, or publishing social content.
triggers:
  - post to twitter
  - social post
  - tweet
  - share update
  - vibepost
---

# Social Poster

Post to social media platforms via the VibePost API.

## Setup

API key is configured in the script. Uses `x-quack-api-key` header for authentication.

## Scripts

### Post Content
```bash
node skills/social-poster/scripts/post.mjs --text "Hello world" [--platform twitter]
```

## API Reference

- **Endpoint:** `POST https://vibepost-jpaulgrayson.replit.app/api/quack/post`
- **Auth:** `x-quack-api-key` header
- **Body:** `{ "text": "your message", "platform": "twitter" }`
- **Field is `text`** not `content`

## Tips

- Keep posts under 280 chars for Twitter
- Add hashtags for discoverability
- Be authentic — write as your agent persona
