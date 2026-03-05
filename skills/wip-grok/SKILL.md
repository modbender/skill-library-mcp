---
name: wip-grok
version: 1.0.2
description: xAI Grok API. Search the web, search X, generate images, generate video.
homepage: https://github.com/wipcomputer/wip-grok
metadata:
  category: search,media
  api_base: https://api.x.ai/v1
  capabilities:
    - api
    - web-search
    - x-search
    - image-generation
    - image-editing
    - video-generation
  dependencies: []
  interface: REST
openclaw:
  emoji: "🔍"
  install:
    env:
      - XAI_API_KEY
author:
  name: Parker Todd Brooks
---

# wip-grok

xAI Grok API. Sensor (search) + Actuator (generate). All xAI functions in one tool.

## When to Use This Skill

### Sensor: Search

**Use search_web for:**
- Current information from websites, news, documentation
- Real-time data (stock prices, weather, recent events)
- Finding information from specific domains
- Verifying current facts

**Use search_x for:**
- What people are saying on X/Twitter about a topic
- Trending discussions and social sentiment
- Real-time reactions to events
- Posts from specific X handles/users

### Actuator: Generate

**Use generate_image for:**
- Creating images from text descriptions
- Generating multiple variations of a concept
- Creating images with specific aspect ratios

**Use edit_image for:**
- Modifying existing images with natural language
- Style transfer, color changes, adding/removing elements
- Combining up to 3 source images

**Use generate_video for:**
- Creating short video clips (1-15 seconds)
- Animating still images (image-to-video)
- Text-to-video generation

### Do NOT Use For

- Fetching a specific X post by URL (use wip-x fetch_post instead)
- Posting tweets (use wip-x post_tweet)
- Reading bookmarks (use wip-x get_bookmarks)
- Historical facts that won't change
- Mathematical calculations

## API Reference

### search_web(options)

```javascript
const result = await search_web({ query: "latest news about AI" });
// result: { content, citations, usage, raw_response }
```

Options: query (required), model, allowed_domains (max 5), excluded_domains (max 5), enable_image_understanding

### search_x(options)

```javascript
const result = await search_x({ query: "AI thoughts", allowed_x_handles: ["elonmusk"] });
```

Options: query (required), model, allowed_x_handles (max 10), excluded_x_handles (max 10), from_date, to_date, enable_image_understanding, enable_video_understanding

### generate_image(options)

```javascript
const result = await generate_image({ prompt: "a red cube", n: 1, aspect_ratio: "1:1" });
// result: { images: [{ url, revised_prompt }] }
```

Options: prompt (required), model, n (1-10), response_format ("url"|"b64_json"), aspect_ratio

Cost: $0.02 per image. URLs are temporary ... download promptly.

### edit_image(options)

```javascript
const result = await edit_image({ prompt: "make it blue", image: "https://..." });
```

Options: prompt (required), image (required, URL or file path or base64), model, n, response_format

Cost: $0.022 per image (input + output).

### generate_video(options)

```javascript
const { request_id } = await generate_video({ prompt: "sunset timelapse", duration: 10 });
const result = await wait_for_video({ request_id });
// result: { status: "completed", url: "https://..." }
```

Options: prompt (required), model, duration (1-15 sec), resolution ("480p"|"720p"), aspect_ratio, image (seed image URL)

Cost: $0.05/sec at 480p, $0.07/sec at 720p. URLs are temporary.

### poll_video(options) / wait_for_video(options)

Poll or wait for async video generation. wait_for_video is a convenience wrapper that polls until complete or timeout.

## Troubleshooting

### "XAI_API_KEY not found"
Set via environment or 1Password: `op://Agent Secrets/X API/api key`

### Slow search responses
Grok reasoning models can take 30-60+ seconds. This is normal.

### Temporary URLs
Image and video URLs expire. Download or process them immediately after receiving.

## API Documentation

- Web Search: https://docs.x.ai/developers/tools/web-search
- X Search: https://docs.x.ai/developers/tools/x-search
- Image Generation: https://docs.x.ai/docs/guides/image-generations
- Video Generation: https://docs.x.ai/docs/guides/video-generations
